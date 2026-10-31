"""The admin VPN addition stays narrow and preserves existing route/TLS policy."""

import importlib.util
import ipaddress
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
spec = importlib.util.spec_from_file_location("management_client_compiler", FRAMEWORK / "blueprints/compile.py")
compiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compiler)
sys.path.insert(0, str(FRAMEWORK / "proxmox/applications"))
import discovery
# The compiler adds its blueprint directory; keep this stack's test discovery first.
sys.path.insert(0, str(ROOT / "tests"))


class ManagementClientTests(unittest.TestCase):
    def test_private_vpn_binding_preserves_existing_ranges_and_rejects_adjacent_subnets(self):
        for vpn_base in ("198.18.10.0", "198.19.9.0"):
            with self.subTest(vpn_base=vpn_base):
                overlay = compiler.read(ROOT / "site.example.json")
                overlay["values"]["networks.admin_vpn"] = vpn_base
                packet = compiler.compile_stack(ROOT, overlay, [])["ingress"]
                stack = json.loads(packet["files"]["stack.json"])
                cfg = json.loads(packet["files"]["site.json"])
                frontend = stack["foundation"]["bind_address"]
                shared = discovery.shared(stack["routing"])
                policy = shared["http"]["middlewares"]["management-clients"]
                values = compiler.manifest(ROOT)["values"]
                expected = [values["networks.policy_15"] + "/24", values["networks.management"] + "/24", vpn_base + "/28"]
                self.assertEqual(policy, {"ipAllowList": {"sourceRange": expected}})
                networks = [ipaddress.IPv4Network(value) for value in policy["ipAllowList"]["sourceRange"]]
                vpn = ipaddress.IPv4Network(vpn_base + "/28")
                for address in vpn:
                    self.assertTrue(any(address in network for network in networks))
                    for port in (80, 443):
                        connection = compiler.connections.Connection("vpn", "ingress", str(address), frontend, "tcp", port)
                        self.assertTrue(compiler.connections.permits(cfg["guest"]["rules"], "in", connection))
                for address in (vpn.network_address - 1, vpn.broadcast_address + 1, vpn.network_address + 255):
                    self.assertFalse(any(address in network for network in networks))
                    connection = compiler.connections.Connection("vpn", "ingress", str(address), frontend, "tcp", 443)
                    self.assertFalse(compiler.connections.permits(cfg["guest"]["rules"], "in", connection))
                for protocol, port, destination in (("tcp", 22, frontend), ("tcp", 53, frontend), ("udp", 443, frontend), ("tcp", 443, str(ipaddress.IPv4Address(frontend) + 1))):
                    connection = compiler.connections.Connection("vpn", "ingress", str(vpn.network_address + 1), destination, protocol, port)
                    self.assertFalse(compiler.connections.permits(cfg["guest"]["rules"], "in", connection))
                for network in networks[:2]:
                    self.assertTrue(any(network.network_address + 1 in permitted for permitted in networks))

    def test_management_routes_keep_middleware_order_and_verified_backend_policies(self):
        packet = compiler.compile_stack(ROOT, compiler.read(ROOT / "site.example.json"), [])["ingress"]
        stack = json.loads(packet["files"]["stack.json"])
        shared = discovery.shared(stack["routing"])
        selected = {name for name, route in stack["routing"]["routes"].items() if "management-clients" in route.get("middlewares", [])}
        self.assertEqual(selected, {"host", "nas", "proxmox"})
        for name in selected:
            with self.subTest(route=name):
                router = shared["http"]["routers"][name]
                self.assertEqual(router["middlewares"], ["security-headers@file", "management-clients@file"])
                self.assertEqual(router["entryPoints"], ["websecure"])
                self.assertEqual(router["tls"], {"certResolver": "letsencrypt"})
        self.assertEqual(shared["http"]["serversTransports"]["udm"], {"serverName": compiler.manifest(ROOT)["values"]["domains.udm_backend"]})
        self.assertEqual(shared["http"]["serversTransports"]["proxmox"], {"rootCAs": [discovery.ca_path("proxmox")]})
        self.assertNotIn("serversTransport", shared["http"]["services"]["nas"]["loadBalancer"])
        self.assertEqual(shared["http"]["middlewares"]["security-headers"], {"headers": {"contentTypeNosniff": True}})


if __name__ == "__main__":
    unittest.main()
