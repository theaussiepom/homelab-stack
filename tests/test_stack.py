"""Check the executable composition and actual workflow graph without targets."""

import importlib.util
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
import unittest
from unittest.mock import patch
import yaml

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
spec = importlib.util.spec_from_file_location(
    "blueprint_compiler", FRAMEWORK / "blueprints/compile.py"
)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
sys.path.insert(0, str(FRAMEWORK / "proxmox/applications"))
import render


def workflow(path):
    # PyYAML's YAML 1.1 loader interprets `on` as True; only inspect jobs here.
    return yaml.safe_load(path.read_text())


class StackTests(unittest.TestCase):
    def setUp(self):
        self.overlay = c.read(ROOT / "site.example.json")

    def guest(self, name, disabled=None, **options):
        return c.compile_stack(ROOT, self.overlay, disabled, **options)[name]

    def test_all_docker_guests_inherit_always_restart(self):
        guests = set()
        for name, packet in c.compile_stack(ROOT, self.overlay, []).items():
            if "stack.json" not in packet["files"]:
                continue
            guests.add(name)
            stack = json.loads(packet["files"]["stack.json"])
            for service, cfg in render.compose(stack)["services"].items():
                with self.subTest(guest=name, service=service):
                    self.assertEqual(cfg["restart"], "always")
                    if "services" in stack:
                        self.assertNotIn("restart", stack["services"][service])
        self.assertEqual(
            guests,
            {
                "automation",
                "dns",
                "identity",
                "ingress",
                "db-tools",
                "bitwarden",
                "pegaprox",
                "zigbee2mqtt",
            },
        )

    def test_all_guest_packets_compile_deterministically_without_restore(self):
        for name in c.CATALOGUE:
            a = self.guest(name, [])
            self.assertEqual(a, self.guest(name, []))
            cfg = json.loads(a["files"]["site.json"])
            self.assertTrue(a["enabled"])
            self.assertNotIn("capture", cfg["app"])
            self.assertNotIn("ha_http", cfg["app"])
            self.assertEqual(
                cfg["deployment"]["capabilities"], c.CATALOGUE[name]["capabilities"]
            )
            self.assertEqual(cfg["guest"]["vmid"], cfg["app"]["vmid"])
            if "stack.json" in a["files"]:
                stack = json.loads(a["files"]["stack.json"])
                render.compose(stack)

    def test_actual_workflows_match_blueprint_phases_and_dependency_edges(self):
        manifest = c.manifest(ROOT)
        deploy = workflow(ROOT / ".github/workflows/deploy.yml")
        self.assertEqual(set(deploy["jobs"]), {"selection", *manifest["guests"]})
        for name, row in manifest["guests"].items():
            job = deploy["jobs"][name]
            needs = job.get("needs", [])
            self.assertEqual(needs, ["selection", *row["depends_on"]])
            self.assertIn("private == true", job["if"])
            guest = workflow(ROOT / ".github/workflows" / ("guest-" + name + ".yml"))
            phases = [
                "infrastructure",
                "preparation",
                *c.CATALOGUE[name]["applications"],
            ]
            self.assertEqual(list(guest["jobs"]), ["deploy"])
            steps = guest["jobs"]["deploy"]["steps"]
            self.assertEqual(len(steps), 6 + 3 * len(phases))
            self.assertEqual([step["env"]["PHASE"] for step in steps[8::3]], phases)
            self.assertEqual([step["env"]["GUEST"] for step in steps[8::3]], [name] * len(phases))
            self.assertNotIn("uses", guest["jobs"]["deploy"])
            self.assertNotIn("needs", guest["jobs"]["deploy"])
        c.workflow_selection(ROOT / ".github/workflows/phase.yml", "guest-phase.yml")

    def test_admission_still_requires_reviewed_private_inputs_and_active_guests(
        self,
    ):
        for name in c.CATALOGUE:
            with self.assertRaises(ValueError):
                self.guest(name, [], admit=True)
        manifest = c.manifest(ROOT)
        with self.assertRaisesRegex(ValueError, "disabled"):
            self.guest("dns", list(c.CATALOGUE), admit=True)
        self.overlay["accepted"] = {
            name: row["prerequisites"] for name, row in manifest["guests"].items()
        }
        for name in ["automation", "bitwarden", "dns"]:
            with self.assertRaises(ValueError):
                self.guest(name, [], admit=True)

    def test_private_central_override_and_independent_guest_selection(self):
        self.overlay["values"]["addresses.pve"] = "192.0.2.10"
        with self.assertRaisesRegex(ValueError, "private HTTP"):
            self.guest("postgresql")
        self.overlay["values"]["addresses.pve"] = "198.18.25.99"
        a = self.guest("postgresql")
        cfg = json.loads(a["files"]["site.json"])
        self.assertEqual(cfg["site"]["api_endpoint"], "https://198.18.25.99:8006/")
        self.assertTrue(a["enabled"])
        with self.assertRaises(ValueError):
            self.guest("automation", ["automation"])

    def test_commissioned_database_bridges_and_no_shared_backend_revival(self):
        for name, bridge in [
            ("postgresql", "vmbr31"),
            ("mariadb", "vmbr32"),
            ("influxdb", "vmbr33"),
        ]:
            cfg = json.loads(self.guest(name, [])["files"]["site.json"])
            self.assertIn(bridge, [n["bridge"] for n in cfg["guest"]["interfaces"]])
            self.assertNotIn(
                "vmbr30", [n["bridge"] for n in cfg["guest"]["interfaces"]]
            )

    def test_influx_health_probes_the_configured_listener_after_address_overrides(self):
        for address in (None, "198.18.33.126"):
            if address is not None:
                self.overlay["values"]["addresses.influxdb_backend"] = address
            packet = self.guest("influxdb", [])
            cfg = json.loads(packet["files"]["site.json"])
            listener = tomllib.loads(packet["files"]["config.toml"])[
                "http-bind-address"
            ]
            checks = {
                "guest": cfg["app"]["health_checks"],
                "application": cfg["app"]["service_health_checks"]["influxdb"],
            }
            for scope, selected in checks.items():
                with self.subTest(address=address, scope=scope):
                    probe = next(
                        row for row in selected if row["expect"] == "INFLUX_OK"
                    )
                    self.assertEqual(probe["argv"][:2], ["python3", "-c"])
                    output = io.StringIO()
                    response = io.BytesIO(b'{"status":"pass","version":"v2.7.12"}')
                    with patch(
                        "urllib.request.urlopen", return_value=response
                    ) as request:
                        with redirect_stdout(output):
                            exec(probe["argv"][2], {})
                        request.assert_called_once_with(
                            "http://" + listener + "/health", timeout=5
                        )
                    self.assertEqual(output.getvalue().strip(), "INFLUX_OK")

    def test_automation_and_bitwarden_use_final_database_memberships(self):
        for name, bridges in [
            ("automation", {"vmbr32", "vmbr33"}),
            ("bitwarden", {"vmbr32"}),
        ]:
            packet = self.guest(name, [])
            cfg = json.loads(packet["files"]["site.json"])
            self.assertTrue(
                bridges <= {n["bridge"] for n in cfg["guest"]["interfaces"]}
            )
        cfg = json.loads(self.guest("automation", [])["files"]["stack.json"])
        self.assertEqual(
            cfg["services"]["homeassistant"]["extra_hosts"]["mariadb.db_hass"],
            c.manifest(ROOT)["values"]["addresses.mariadb_backend"],
        )

    def test_migration_fields_and_vm_overrides_refuse(self):
        for override in [
            {"app": {"capture": {}}},
            {"app": {"ha_http": {}}},
            {"guest": {"platform": "vm"}},
        ]:
            self.overlay["guests"]["automation"] = {"config": override}
            with self.assertRaises(ValueError):
                self.guest("automation", [])

    def test_public_tree_contains_no_actual_networks_or_private_assets(self):
        # Inspect this repository's files, including untracked edits, without
        # descending into the framework checkout that hosted CI places under this checkout.
        names = subprocess.check_output(
            ["git", "-C", str(ROOT), "ls-files", "--cached", "--others",
             "--exclude-standard", "-z"], text=True,
        ).split("\0")
        for name in set(names) - {""}:
            path = ROOT / name
            if path.is_file() and path.suffix in {".json", ".yml", ".yaml", ".md", ".py", ".sh", ""}:
                self.assertIsNone(
                    re.search(
                        r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b",
                        path.read_text(),
                    ), str(path),
                )
        self.assertFalse(list(ROOT.rglob("*.tar")))

    def test_node_red_oidc_identity_is_a_private_central_value(self):
        self.overlay["values"]["identity.node_red_client"] = "selected-client-fixture"
        packet = self.guest("automation", [])
        stack = json.loads(packet["files"]["stack.json"])
        self.assertEqual(stack["node_red_oidc"]["client_id"], "selected-client-fixture")
        default = c.compile_stack(ROOT, c.read(ROOT / "site.example.json"), [])
        self.assertEqual(
            json.loads(default["automation"]["files"]["stack.json"])["node_red_oidc"]["client_id"],
            "example-node-red-client",
        )
