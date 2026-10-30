"""UDM uses default trust without weakening names, routes or other CA inputs."""

import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
spec = importlib.util.spec_from_file_location("udm_route_compiler", FRAMEWORK / "blueprints/compile.py")
compiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compiler)
sys.path.insert(0, str(FRAMEWORK / "proxmox/applications"))
import discovery
import foundation
import render


class UdmTransportTests(unittest.TestCase):
    def stack(self, changed=False):
        overlay = compiler.read(ROOT / "site.example.json")
        if changed:
            overlay["values"].update({
                "domains.udm_backend": "controller.changed.example.invalid",
                "domains.secondary": "changed.example.invalid",
            })
        packet = compiler.compile_stack(ROOT, overlay, [])["ingress"]
        return json.loads(packet["files"]["stack.json"])

    def staged(self, root):
        """Create disposable invented inputs; no real trust or handshake is tested."""
        stack = self.stack()
        certificate = "-----BEGIN CERTIFICATE-----\nsynthetic-public-fixture\n-----END CERTIFICATE-----\n"
        pve = root / "provider.pem"
        pve.write_text(certificate)
        pve.chmod(0o600)
        stack["foundation"]["pve_ca_file"] = str(pve)
        for name in stack["foundation"]["secret_files"]:
            path = root / (name + "-fixture")
            path.write_text("synthetic-retained-fixture")
            path.chmod(0o600)
            stack["foundation"]["secret_files"][name] = str(path)
        for name, row in stack["routing"]["transports"].items():
            if "ca_file" in row:
                path = root / (name + ".pem")
                path.write_text(certificate)
                path.chmod(0o600)
                row["ca_file"] = str(path)
        return stack

    def test_profile_keeps_explicit_udm_name_and_other_ca_inputs(self):
        profile = compiler.read(ROOT / "guests/ingress/profile.json")
        transports = profile["stack"]["routing"]["transports"]
        self.assertEqual(transports["udm"], {"server_name": "${domains.udm_backend}"})
        self.assertEqual({name for name, row in transports.items() if "ca_file" in row}, {"proxmox", "pegaprox", "nas"})

    def test_compiled_name_follows_central_binding_without_a_tls_bypass(self):
        for changed in (False, True):
            with self.subTest(central_values_changed=changed):
                stack = self.stack(changed)
                expected = "controller.changed.example.invalid" if changed else compiler.manifest(ROOT)["values"]["domains.udm_backend"]
                shared = discovery.shared(stack["routing"])
                self.assertEqual(shared["http"]["serversTransports"]["udm"], {"serverName": expected})
                self.assertNotIn("insecureSkipVerify", json.dumps(shared))
                route = stack["routing"]["routes"]["host"]
                self.assertEqual(route["transport"], "udm")
                self.assertEqual(route["middlewares"], ["security-headers", "management-clients"])
                self.assertEqual(shared["http"]["routers"]["host"]["middlewares"], ["security-headers@file", "management-clients@file"])

    def test_only_udm_root_ca_differs_from_the_previous_rendered_configuration(self):
        stack = self.stack()
        routing = stack["routing"]
        previous = copy.deepcopy(routing)
        previous["transports"]["udm"]["ca_file"] = "/usr/local/share/ca-certificates/homelab-udm.crt"
        previous_rendered = discovery.shared(previous)
        del previous_rendered["http"]["serversTransports"]["udm"]["rootCAs"]
        self.assertEqual(previous_rendered, discovery.shared(routing))
        # An alias still produces the same router when the CA override is omitted.
        previous["routes"]["host"]["aliases"] = ["router.example.invalid"]
        current = copy.deepcopy(previous)
        del current["transports"]["udm"]["ca_file"]
        rendered = discovery.shared(previous)
        del rendered["http"]["serversTransports"]["udm"]["rootCAs"]
        self.assertEqual(rendered, discovery.shared(current))

    def test_udm_has_no_ca_read_artifact_or_mount_and_other_ca_mounts_remain(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stack = self.staged(root)
            missing = root / "udm.pem"
            previous = copy.deepcopy(stack)
            previous["routing"]["transports"]["udm"]["ca_file"] = str(missing)
            self.assertFalse(missing.exists())
            self.assertIn(str(missing), foundation.source_files(previous))
            with self.assertRaises(FileNotFoundError):
                foundation.files(previous)
            self.assertNotIn(str(missing), foundation.source_files(stack))
            with patch.object(foundation, "read_private", wraps=foundation.read_private) as reader:
                artifacts = foundation.files(stack)
            self.assertNotIn(str(missing), [str(call.args[0]) for call in reader.call_args_list])
            paths = {row["path"] for row in artifacts}
            self.assertNotIn("route-udm.pem", paths)
            self.assertTrue({"route-proxmox.pem", "route-pegaprox.pem", "route-nas.pem", "pve-ca.pem"} <= paths)
            service = render.compose(stack)["services"]["traefik"]
            mounts = {row["target"]: row for row in service["volumes"]}
            self.assertNotIn(discovery.ca_path("udm"), mounts)
            for name in ("proxmox", "pegaprox", "nas"):
                self.assertIn(stack["routing"]["transports"][name]["ca_file"], foundation.source_files(stack))
                self.assertEqual(discovery.shared(stack["routing"])["http"]["serversTransports"][name]["rootCAs"], [discovery.ca_path(name)])
                self.assertTrue(mounts[discovery.ca_path(name)]["read_only"])
                self.assertFalse(mounts[discovery.ca_path(name)]["bind"]["create_host_path"])
            self.assertEqual(service["environment"]["SSL_CERT_FILE"], "/etc/ssl/certs/homelab-pve.pem")
            self.assertFalse(missing.exists())

    def test_other_missing_ca_files_and_invalid_tls_transports_still_fail(self):
        for name in ("proxmox", "pegaprox", "nas"):
            with self.subTest(missing_ca=name), tempfile.TemporaryDirectory() as directory:
                stack = self.staged(Path(directory))
                Path(stack["routing"]["transports"][name]["ca_file"]).unlink()
                with self.assertRaises(FileNotFoundError):
                    foundation.files(stack)
        for definition in (
            {"server_name": "synology"},
            {"server_name": "https://bad.invalid"},
            {"server_name": "controller.example.invalid", "insecureSkipVerify": True},
            {"server_name": "controller.example.invalid", "verify": False},
        ):
            with self.subTest(definition=definition), self.assertRaises(ValueError):
                discovery.validate_ingress({"transports": {"udm": definition}})
