"""PegaProx routing must agree with its TLS runtime and retain verified trust."""

from contextlib import redirect_stdout
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
spec = importlib.util.spec_from_file_location(
    "pegaprox_route_compiler", FRAMEWORK / "blueprints/compile.py"
)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
sys.path.insert(0, str(FRAMEWORK / "proxmox/applications"))
import discovery
import foundation
import pegaprox_health
import render


class PegaProxRouteTests(unittest.TestCase):
    def test_endpoint_notes_and_published_port_agree_with_actual_health_requests(self):
        for changed in (False, True):
            overlay = c.read(ROOT / "site.example.json")
            if changed:
                overlay["values"].update(
                    {
                        "addresses.pegaprox_management": "198.18.25.134",
                        "domains.secondary": "changed.example.invalid",
                    }
                )
            with self.subTest(central_values_changed=changed):
                packets = c.compile_stack(ROOT, overlay, [])
                packet = packets["pegaprox"]
                cfg = json.loads(packet["files"]["site.json"])
                stack = json.loads(packet["files"]["stack.json"])
                route = cfg["routes"]["pegaprox"]
                ingress = json.loads(packets["ingress"]["files"]["stack.json"])
                self.assertEqual(
                    ingress["routing"]["transports"]["pegaprox"]["server_name"],
                    route["host"],
                )
                endpoint = urlsplit(cfg["app"]["endpoints"]["pegaprox"]["web"])
                responses = []
                for status, body in (
                    (200, {"status": "ok", "version": "fixture"}),
                    (401, {"authenticated": False, "initialized": True}),
                ):
                    response = io.BytesIO(json.dumps(body).encode())
                    response.code = status
                    responses.append(response)
                output = io.StringIO()
                with (
                    patch("urllib.request.build_opener") as opener,
                    patch("ssl.SSLContext"),
                    redirect_stdout(output),
                ):
                    opener.return_value.open.side_effect = responses
                    exec(pegaprox_health.CONTAINER_CODE, {})
                self.assertEqual(
                    output.getvalue().strip(), "PegaProx verification passed"
                )
                probes = [
                    urlsplit(call.args[0].full_url)
                    for call in opener.return_value.open.call_args_list
                ]
                self.assertEqual(
                    [url.path for url in probes], ["/api/health", "/api/auth/check"]
                )
                for url in probes:
                    self.assertEqual(
                        (endpoint.scheme, endpoint.port), (url.scheme, url.port)
                    )
                self.assertEqual(endpoint.scheme, "https")
                self.assertEqual(endpoint.hostname, stack["bind_address"])
                self.assertEqual(route["url"], endpoint.geturl())
                self.assertEqual(
                    render.compose(stack)["services"]["pegaprox"]["ports"],
                    [f"{endpoint.hostname}:{endpoint.port}:{endpoint.port}/tcp"],
                )
                labels = discovery.labels(cfg)
                prefix = "traefik.http.services.pegaprox.loadbalancer"
                self.assertEqual(labels[prefix + ".server.url"], endpoint.geturl())
                self.assertEqual(labels[prefix + ".serverstransport"], "pegaprox@file")

    def test_transport_stages_required_public_trust_and_mounts_it_readonly(self):
        packets = c.compile_stack(ROOT, c.read(ROOT / "site.example.json"), [])
        guest = json.loads(packets["pegaprox"]["files"]["site.json"])
        stack = json.loads(packets["ingress"]["files"]["stack.json"])
        self.assertEqual(guest["routes"]["pegaprox"].get("transport"), "pegaprox")
        transport = stack["routing"]["transports"]["pegaprox"]
        self.assertEqual(
            transport,
            {
                "server_name": guest["routes"]["pegaprox"]["host"],
                "ca_file": "/usr/local/share/ca-certificates/homelab-pegaprox.crt",
            },
        )
        self.assertIn(transport["ca_file"], foundation.source_files(stack))
        self.assertEqual(
            discovery.shared(stack["routing"])["http"]["serversTransports"]["pegaprox"],
            {
                "serverName": transport["server_name"],
                "rootCAs": ["/etc/ssl/certs/route-pegaprox.pem"],
            },
        )
        mount = next(
            row
            for row in render.compose(stack)["services"]["traefik"]["volumes"]
            if row["target"] == "/etc/ssl/certs/route-pegaprox.pem"
        )
        self.assertTrue(mount["read_only"])
        self.assertFalse(mount["bind"]["create_host_path"])
        with tempfile.TemporaryDirectory() as tmp:
            staged = copy.deepcopy(stack)
            root = Path(tmp)
            # Exercise file staging with disposable inputs; this fixture does not
            # qualify any real certificate or perform a TLS handshake.
            public = "-----BEGIN CERTIFICATE-----\nsynthetic-public-fixture\n-----END CERTIFICATE-----\n"
            ca = root / "ca.pem"
            ca.write_text(public)
            ca.chmod(0o600)
            staged["foundation"]["pve_ca_file"] = str(ca)
            for key in staged["foundation"]["secret_files"]:
                path = root / key
                path.write_text("synthetic-retained-value")
                path.chmod(0o600)
                staged["foundation"]["secret_files"][key] = str(path)
            for row in staged["routing"]["transports"].values():
                row["ca_file"] = str(ca)
            selected = root / "pegaprox.pem"
            staged["routing"]["transports"]["pegaprox"]["ca_file"] = str(selected)
            with self.assertRaises(FileNotFoundError):
                foundation.files(staged)
            selected.write_text(public)
            selected.chmod(0o600)
            artifact = next(
                row
                for row in foundation.files(staged)
                if row["path"] == "route-pegaprox.pem"
            )
            self.assertEqual(
                artifact,
                {
                    "path": "route-pegaprox.pem",
                    "content": public,
                    "uid": 0,
                    "gid": 0,
                    "mode": "0400",
                },
            )


if __name__ == "__main__":
    unittest.main()
