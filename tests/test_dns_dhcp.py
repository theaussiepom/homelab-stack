"""The DNS composition preserves DHCP while its reviewed endpoint stays concrete."""

import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
spec = importlib.util.spec_from_file_location("dns_dhcp_compiler", FRAMEWORK / "blueprints/compile.py")
compiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compiler)
sys.path.insert(0, str(FRAMEWORK / "proxmox/applications"))
import render


class DNSDHCPTests(unittest.TestCase):
    def compile_dns(self, overlay=None):
        """Compile only public source fixtures; no admission or target contact."""
        packets = compiler.compile_stack(
            ROOT, overlay or compiler.read(ROOT / "site.example.json"), []
        )
        packet = packets["dns"]
        return json.loads(packet["files"]["site.json"]), json.loads(packet["files"]["stack.json"])

    def test_dns_keeps_dhcp_and_a_concrete_application_endpoint(self):
        """DHCP controls allocation; endpoint metadata controls address validation."""
        cfg, stack = self.compile_dns()
        nic = cfg["guest"]["interfaces"][0]
        self.assertEqual(cfg["guest"]["vmid"], 6101)
        self.assertEqual(nic["ipv4"], "dhcp")
        self.assertEqual(nic["ipv4_endpoint"], "198.18.40.2/24")
        self.assertIsNone(nic["gateway"])
        self.assertEqual(cfg["app"]["address"], "198.18.40.2")
        self.assertEqual(cfg["app"]["endpoints"]["pihole"]["web"], "http://198.18.40.2:80")
        composed = render.compose(stack)
        self.assertEqual(composed["services"]["pihole"]["network_mode"], "host")
        self.assertEqual(composed["services"]["pihole"]["environment"]["FTLCONF_dhcp_active"], "false")
        self.assertEqual(
            composed["services"]["unbound"]["ports"],
            ["127.0.0.1:5335:53/tcp", "127.0.0.1:5335:53/udp"],
        )

    def test_reviewed_endpoint_overrides_keep_allocation_and_bindings_distinct(self):
        """A qualified synthetic address/prefix override never requests static allocation."""
        overlay = compiler.read(ROOT / "site.example.json")
        overlay["values"]["addresses.dns"] = "198.18.40.102"
        nic = copy.deepcopy(compiler.read(ROOT / "guests/dns/profile.json")["config"]["guest"]["interfaces"][0])
        nic["ipv4_endpoint"] = "${addresses.dns}/23"
        overlay["guests"]["dns"] = {"config": {"guest": {"interfaces": [nic]}}}
        cfg, stack = self.compile_dns(overlay)
        selected = cfg["guest"]["interfaces"][0]
        self.assertEqual(selected["ipv4"], "dhcp")
        self.assertEqual(selected["ipv4_endpoint"], "198.18.40.102/23")
        self.assertIsNone(selected["gateway"])
        self.assertEqual(cfg["app"]["address"], "198.18.40.102")
        self.assertEqual(cfg["app"]["endpoints"]["pihole"]["web"], "http://198.18.40.102:80")
        self.assertEqual(render.compose(stack)["services"]["pihole"]["network_mode"], "host")

    def test_missing_or_conflicting_dhcp_endpoint_is_a_visible_failure(self):
        """Missing metadata, a foreign endpoint and an explicit gateway fail closed."""
        base = compiler.read(ROOT / "guests/dns/profile.json")["config"]["guest"]["interfaces"][0]
        for mutation in ("missing", "invalid", "foreign", "gateway", "static_metadata"):
            with self.subTest(mutation=mutation):
                nic = copy.deepcopy(base)
                if mutation == "missing":
                    nic.pop("ipv4_endpoint")
                elif mutation == "invalid":
                    nic["ipv4_endpoint"] = "dhcp"
                elif mutation == "foreign":
                    nic["ipv4_endpoint"] = "198.18.40.103/24"
                elif mutation == "gateway":
                    nic["gateway"] = "${gateways.frontend}"
                else:
                    nic["ipv4"] = "${addresses.dns}/24"
                overlay = compiler.read(ROOT / "site.example.json")
                overlay["guests"]["dns"] = {"config": {"guest": {"interfaces": [nic]}}}
                with self.assertRaises(ValueError):
                    self.compile_dns(overlay)

    def test_other_guests_keep_static_interfaces_without_dhcp_metadata(self):
        """The source refinement changes only the commissioned DHCP guest."""
        packets = compiler.compile_stack(ROOT, compiler.read(ROOT / "site.example.json"), [])
        for name, packet in packets.items():
            if name == "dns":
                continue
            for nic in json.loads(packet["files"]["site.json"])["guest"]["interfaces"]:
                with self.subTest(guest=name, mac=nic["mac"]):
                    self.assertNotEqual(nic["ipv4"], "dhcp")
                    self.assertNotIn("ipv4_endpoint", nic)
