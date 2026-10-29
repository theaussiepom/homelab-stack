"""Real compiled routes and resolver selections must have usable narrow policies."""

import importlib.util
import ipaddress
import json
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
spec = importlib.util.spec_from_file_location(
    "connection_compiler", FRAMEWORK / "blueprints/compile.py"
)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class ConnectionTests(unittest.TestCase):
    def configurations(self, overlay=None):
        packets = c.compile_stack(
            ROOT, overlay or c.read(ROOT / "site.example.json"), []
        )
        return {
            name: json.loads(packet["files"]["site.json"])
            for name, packet in packets.items()
        }

    def test_each_published_backend_has_a_narrow_proxy_egress_allowance(self):
        cfg = self.configurations()
        rules = cfg["ingress"]["guest"]["rules"]
        for name, port in (
            ("automation", 8123),
            ("automation", 1880),
            ("bitwarden", 8080),
        ):
            route = next(
                route
                for route in cfg[name]["app"]["discovery_routes"]
                if route["url"].endswith(":" + str(port))
            )
            destination = route["url"].removeprefix("http://").split(":")[0] + "/32"
            with self.subTest(guest=name, port=port):
                self.assertTrue(
                    any(
                        rule["direction"] == "out"
                        and rule["proto"] == "tcp"
                        and rule.get("destination") == destination
                        and str(port) in rule.get("port", "").split(",")
                        for rule in rules
                    ),
                    "Published backend has no narrow proxy egress allowance",
                )

    def test_dns_accepts_the_management_and_frontend_client_networks(self):
        cfg = self.configurations()
        values = c.manifest(ROOT)["values"]
        rules = cfg["dns"]["guest"]["rules"]
        for network in ("networks.management", "networks.frontend"):
            for proto in ("tcp", "udp"):
                with self.subTest(network=network, protocol=proto):
                    self.assertTrue(
                        any(
                            row["direction"] == "in"
                            and row["proto"] == proto
                            and row.get("port") == "53"
                            and ipaddress.ip_network(row["source"])
                            == ipaddress.ip_network(values[network] + "/24")
                            for row in rules
                        ),
                        "Declared DNS clients have no resolver ingress allowance",
                    )

    def test_removing_either_proxy_allowance_is_refused_during_compilation(self):
        for name, direction in (("ingress", "out"), ("automation", "in")):
            overlay = c.read(ROOT / "site.example.json")
            rules = c.read(ROOT / "guests" / name / "profile.json")["config"]["guest"][
                "rules"
            ]
            overlay["guests"][name] = {
                "config": {
                    "guest": {
                        "rules": [
                            row
                            for row in rules
                            if not (
                                row["direction"] == direction
                                and "8123" in row.get("port", "").split(",")
                            )
                        ]
                    }
                }
            }
            with (
                self.subTest(guest=name),
                self.assertRaisesRegex(
                    ValueError, name + " " + direction + " firewall"
                ),
            ):
                self.configurations(overlay)

    def test_dns_protocol_and_changed_service_ports_are_validated(self):
        overlay = c.read(ROOT / "site.example.json")
        rules = c.read(ROOT / "guests/dns/profile.json")["config"]["guest"]["rules"]
        overlay["guests"]["dns"] = {
            "config": {
                "guest": {
                    "rules": [
                        row
                        for row in rules
                        if not (row["direction"] == "in" and row["proto"] == "udp")
                    ]
                }
            }
        }
        with self.assertRaisesRegex(ValueError, "udp/53"):
            self.configurations(overlay)
        overlay = c.read(ROOT / "site.example.json")
        routes = c.read(ROOT / "guests/automation/profile.json")["config"]["app"][
            "discovery_routes"
        ]
        routes[0]["url"] = routes[0]["url"].replace(":8123", ":8124")
        overlay["guests"]["automation"] = {
            "config": {"app": {"discovery_routes": routes}}
        }
        with self.assertRaisesRegex(ValueError, "tcp/8124"):
            self.configurations(overlay)

    def test_central_endpoint_overrides_keep_routes_and_policies_consistent(self):
        overlay = c.read(ROOT / "site.example.json")
        overlay["values"]["addresses.bitwarden_backend"] = "198.18.30.39"
        cfg = self.configurations(overlay)
        self.assertEqual(
            cfg["bitwarden"]["app"]["discovery_routes"][0]["url"],
            "http://198.18.30.39:8080",
        )


if __name__ == "__main__":
    unittest.main()
