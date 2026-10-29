"""Check the executable composition and actual workflow graph without targets."""

import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import unittest
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

    def guest(self, name, enabled, **options):
        return c.compile_stack(ROOT, self.overlay, enabled, **options)[name]

    def test_all_guest_packets_compile_deterministically_without_restore(self):
        for name in c.CATALOGUE:
            a = self.guest(name, [])
            self.assertEqual(a, self.guest(name, []))
            cfg = json.loads(a["files"]["site.json"])
            self.assertFalse(a["enabled"])
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
        self.assertEqual(set(deploy["jobs"]), set(manifest["guests"]))
        for name, row in manifest["guests"].items():
            job = deploy["jobs"][name]
            needs = job.get("needs", [])
            self.assertEqual(set(needs), set(row["depends_on"]))
            self.assertIn("private == true", job["if"])
            guest = workflow(ROOT / ".github/workflows" / ("guest-" + name + ".yml"))
            phases = [
                "infrastructure",
                "preparation",
                *c.CATALOGUE[name]["applications"],
            ]
            self.assertEqual(list(guest["jobs"]), phases)
            for n, p in enumerate(phases):
                self.assertEqual(guest["jobs"][p]["with"]["phase"], p)
                if n:
                    self.assertEqual(guest["jobs"][p]["needs"], phases[n - 1])
        c.workflow_selection(ROOT / ".github/workflows/phase.yml", "guest-phase.yml")

    def test_missing_prerequisites_disabled_selection_and_placeholder_images_cannot_admit(
        self,
    ):
        for name in c.CATALOGUE:
            with self.assertRaises(ValueError):
                self.guest(name, [], admit=True)
        manifest = c.manifest(ROOT)
        enabled = list(c.CATALOGUE)
        self.overlay["accepted"] = {
            name: row["prerequisites"] for name, row in manifest["guests"].items()
        }
        for name in ["automation", "bitwarden", "dns"]:
            with self.assertRaises(ValueError):
                self.guest(name, enabled, admit=True)

    def test_private_central_override_and_independent_guest_selection(self):
        self.overlay["values"]["addresses.pve"] = "192.0.2.10"
        a = self.guest("postgresql", ["dns", "postgresql"])
        cfg = json.loads(a["files"]["site.json"])
        self.assertEqual(cfg["site"]["api_endpoint"], "https://192.0.2.10:8006/")
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
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            if path.suffix in [".json", ".yml"]:
                self.assertIsNone(
                    re.search(r"\b(?:10\.77|192\.168)\.\d+\.\d+", path.read_text()),
                    str(path),
                )
        self.assertFalse(list(ROOT.rglob("*.tar")))
