"""ACME discovery has scoped public DNS without changing guest DNS or TLS policy."""

import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
spec = importlib.util.spec_from_file_location("acme_resolver_compiler", FRAMEWORK / "blueprints/compile.py")
compiler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compiler)
sys.path.insert(0, str(FRAMEWORK / "proxmox/applications"))
import foundation
# The compiler adds its blueprint directory; keep this stack's test discovery first.
sys.path.insert(0, str(ROOT / "tests"))


class AcmeResolverTests(unittest.TestCase):
    def packet(self):
        return compiler.compile_stack(ROOT, compiler.read(ROOT / "site.example.json"), [])["ingress"]

    def test_acme_public_resolvers_have_only_exact_tcp_udp_dns_egress(self):
        packet = self.packet()
        cfg = json.loads(packet["files"]["site.json"])
        stack = json.loads(packet["files"]["stack.json"])
        values = compiler.manifest(ROOT)["values"]
        self.assertEqual(stack["foundation"]["acme_dns_resolvers"], ["1.1.1.1:53", "1.0.0.1:53"])
        self.assertEqual(cfg["guest"]["dns_servers"], [values["addresses.dns"], values["addresses.fallback_dns"]])
        rules = cfg["guest"]["rules"]
        selected = [r for r in rules if r.get("destination") in {"1.1.1.1/32", "1.0.0.1/32"}]
        self.assertEqual(selected, [{"direction": "out", "proto": proto, "port": "53", "comment": "ACME recursive DNS only", "destination": address + "/32"} for address in ["1.1.1.1", "1.0.0.1"] for proto in ["udp", "tcp"]])
        for address in ("1.1.1.1", "1.0.0.1", "9.9.9.9"):
            for proto in ("tcp", "udp"):
                connection = compiler.connections.Connection("ingress", "recursive-dns", values["addresses.ingress_frontend"], address, proto, 53)
                self.assertEqual(compiler.connections.permits(rules, "out", connection), address != "9.9.9.9")

    def test_static_tls_render_changes_only_acme_resolvers(self):
        stack = json.loads(self.packet()["files"]["stack.json"])
        previous = copy.deepcopy(stack)
        previous["foundation"]["acme_dns_resolvers"] = [compiler.manifest(ROOT)["values"]["addresses.dns"] + ":53"]
        with patch.object(foundation, "read_private", return_value="invented-source-fixture"):
            current_files = {r["path"]: r for r in foundation.files(stack)}
            previous_files = {r["path"]: r for r in foundation.files(previous)}
        current = json.loads(current_files["traefik.yml"]["content"])
        old = json.loads(previous_files["traefik.yml"]["content"])
        challenge = current["certificatesResolvers"]["letsencrypt"]["acme"]["dnsChallenge"]
        self.assertEqual(challenge, {"provider": "cloudflare", "resolvers": ["1.1.1.1:53", "1.0.0.1:53"], "propagation": {"disableANSChecks": True, "requireAllRNS": True}})
        old["certificatesResolvers"]["letsencrypt"]["acme"]["dnsChallenge"]["resolvers"] = challenge["resolvers"]
        self.assertEqual(current, old)
        current_files.pop("traefik.yml")
        previous_files.pop("traefik.yml")
        self.assertEqual(current_files, previous_files)


if __name__ == "__main__":
    unittest.main()
