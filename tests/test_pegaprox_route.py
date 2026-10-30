"""Browser TLS stays automatic while managed PegaProx uses scoped proxy HTTP."""

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
spec = importlib.util.spec_from_file_location("pegaprox_route_compiler", FRAMEWORK / "blueprints/compile.py")
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
sys.path.insert(0, str(FRAMEWORK / "proxmox/applications"))
import discovery
import foundation
import pegaprox
import pegaprox_health
import render


class PegaProxRouteTests(unittest.TestCase):
    def test_endpoint_proxy_binding_and_actual_health_requests_agree(self):
        """Execute the real read-only health code with invented closed-setup replies."""
        for changed in (False, True):
            overlay = c.read(ROOT / "site.example.json")
            if changed:
                overlay["values"].update({
                    "addresses.pegaprox_management": "198.18.25.134",
                    "addresses.ingress_management": "198.18.25.133",
                    "domains.secondary": "changed.example.invalid",
                })
            with self.subTest(central_values_changed=changed):
                values = dict(c.manifest(ROOT)["values"], **overlay["values"])
                packets = c.compile_stack(ROOT, overlay, [])
                packet = packets["pegaprox"]
                cfg = json.loads(packet["files"]["site.json"])
                stack = json.loads(packet["files"]["stack.json"])
                route = cfg["routes"]["pegaprox"]
                endpoint = urlsplit(cfg["app"]["endpoints"]["pegaprox"]["web"])
                self.assertEqual(endpoint.scheme, "http")
                self.assertEqual(endpoint.port, 5000)
                self.assertEqual(endpoint.hostname, stack["bind_address"])
                self.assertEqual(route["url"], endpoint.geturl())
                self.assertNotIn("transport", route)
                self.assertEqual(stack["trusted_proxy"], values["addresses.ingress_management"] + "/32")
                service = render.compose(stack)["services"]["pegaprox"]
                self.assertEqual(service["ports"], [f"{endpoint.hostname}:5000:5000/tcp"])
                self.assertEqual(service["environment"]["PEGAPROX_BEHIND_PROXY"], "true")
                self.assertEqual(service["environment"]["PEGAPROX_HOST"], "0.0.0.0")
                self.assertEqual(service["environment"]["PEGAPROX_TRUSTED_PROXIES"], stack["trusted_proxy"])
                self.assertEqual(service["restart"], "always")
                self.assertTrue(service["read_only"])
                self.assertEqual(service["cap_drop"], ["ALL"])
                pegaprox.validate_deployment(cfg, stack)
                responses = []
                for status, body in ((200, {"status": "ok", "version": "fixture"}), (401, {"authenticated": False, "initialized": True})):
                    response = io.BytesIO(json.dumps(body).encode())
                    response.code = status
                    responses.append(response)
                output = io.StringIO()
                with patch("urllib.request.build_opener") as opener, patch("ssl.SSLContext") as tls, redirect_stdout(output):
                    opener.return_value.open.side_effect = responses
                    exec(pegaprox_health.CONTAINER_CODE, {})
                tls.assert_not_called()
                self.assertEqual(output.getvalue().strip(), "PegaProx verification passed")
                requests = [call.args[0] for call in opener.return_value.open.call_args_list]
                self.assertEqual([urlsplit(request.full_url).path for request in requests], ["/api/health", "/api/auth/check"])
                for request in requests:
                    url = urlsplit(request.full_url)
                    self.assertEqual((url.scheme, url.hostname, url.port), ("http", "127.0.0.1", 5000))
                    self.assertEqual(request.get_header("Origin"), "http://127.0.0.1:5000")
                labels = discovery.labels(cfg)
                prefix = "traefik.http.services.pegaprox.loadbalancer"
                self.assertEqual(labels[prefix + ".server.url"], endpoint.geturl())
                self.assertNotIn(prefix + ".serverstransport", labels)
                self.assertEqual(labels["traefik.http.routers.pegaprox.entrypoints"], "websecure")
                self.assertEqual(labels["traefik.http.routers.pegaprox.tls.certresolver"], "letsencrypt")

    def test_trusted_proxy_must_stay_a_single_admitted_ingress_endpoint(self):
        """A runtime proxy field cannot replace the guest's finite client policy."""
        packets = c.compile_stack(ROOT, c.read(ROOT / "site.example.json"), [])
        cfg = json.loads(packets["pegaprox"]["files"]["site.json"])
        stack = json.loads(packets["pegaprox"]["files"]["stack.json"])
        for bad in ("0.0.0.0/0", "198.18.25.0/24", "198.51.100.1/32", stack["bind_address"] + "/32", [stack["trusted_proxy"]]):
            with self.subTest(trusted_proxy=bad), self.assertRaises(ValueError):
                changed = copy.deepcopy(stack)
                changed["trusted_proxy"] = bad
                render.compose(changed)
        changed = copy.deepcopy(cfg)
        changed["guest"]["rules"] = [row for row in changed["guest"]["rules"] if not (row.get("direction") == "in" and row.get("port") == "5000" and row.get("source") == stack["trusted_proxy"])]
        with self.assertRaises(ValueError):
            pegaprox.validate_deployment(changed, stack)

    def test_nas_http_route_keeps_frontend_tls_aliases_and_narrow_egress(self):
        """Compile the qualified port while preserving browser routing and policy."""
        for changed in (False, True):
            overlay = c.read(ROOT / "site.example.json")
            if changed:
                overlay["values"].update({"addresses.nas": "198.18.25.102", "domains.secondary": "secondary.changed.example.invalid", "domains.primary": "primary.changed.example.invalid"})
            with self.subTest(central_values_changed=changed):
                values = dict(c.manifest(ROOT)["values"], **overlay["values"])
                packets = c.compile_stack(ROOT, overlay, [])
                ingress = json.loads(packets["ingress"]["files"]["stack.json"])
                cfg = json.loads(packets["ingress"]["files"]["site.json"])
                route = ingress["routing"]["routes"]["nas"]
                self.assertEqual(route["url"], "http://" + values["addresses.nas"] + ":31763")
                self.assertEqual(route["host"], "nas." + values["domains.secondary"])
                self.assertEqual(route["aliases"], ["nas." + values["domains.primary"]])
                self.assertEqual(route["middlewares"], ["security-headers", "management-clients"])
                self.assertNotIn("transport", route)
                shared = discovery.shared(ingress["routing"])
                router = shared["http"]["routers"]["nas"]
                self.assertEqual(router["entryPoints"], ["websecure"])
                self.assertEqual(router["tls"], {"certResolver": "letsencrypt"})
                self.assertNotIn("serversTransport", shared["http"]["services"]["nas"]["loadBalancer"])
                rules = [r for r in cfg["guest"]["rules"] if r.get("direction") == "out" and r.get("destination") == values["addresses.nas"] + "/32"]
                self.assertEqual(len(rules), 1)
                self.assertEqual((rules[0]["source"], rules[0]["port"], rules[0]["proto"]), (values["addresses.ingress_management"] + "/32", "31763", "tcp"))
        overlay = c.read(ROOT / "site.example.json")
        profile = c.read(ROOT / "guests/ingress/profile.json")
        overlay["guests"]["ingress"] = {"config": {"guest": {"rules": [r for r in profile["config"]["guest"]["rules"] if r.get("port") != "31763"]}}}
        with self.assertRaises(ValueError):
            c.compile_stack(ROOT, overlay, [])

    def test_no_backend_ca_lifecycle_is_staged_and_pve_trust_acme_are_preserved(self):
        """Render invented inputs; no real certificate, process or login is touched."""
        packets = c.compile_stack(ROOT, c.read(ROOT / "site.example.json"), [])
        ingress = json.loads(packets["ingress"]["files"]["stack.json"])
        self.assertEqual(set(ingress["routing"]["transports"]), {"udm", "proxmox"})
        self.assertEqual(ingress["routing"]["transports"]["udm"], {"server_name": c.manifest(ROOT)["values"]["domains.udm_backend"]})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            staged = copy.deepcopy(ingress)
            ca = root / "pve.pem"
            ca.write_text("-----BEGIN CERTIFICATE-----\nsynthetic-public-fixture\n-----END CERTIFICATE-----\n")
            ca.chmod(0o600)
            staged["foundation"]["pve_ca_file"] = str(ca)
            staged["routing"]["transports"]["proxmox"]["ca_file"] = str(ca)
            for key in staged["foundation"]["secret_files"]:
                path = root / key
                path.write_text("synthetic-retained-value")
                path.chmod(0o600)
                staged["foundation"]["secret_files"][key] = str(path)
            with patch.object(foundation, "read_private", wraps=foundation.read_private) as reader:
                artifacts = foundation.files(staged)
            self.assertTrue(all(Path(call.args[0]).name in {"pve.pem", *staged["foundation"]["secret_files"]} for call in reader.call_args_list))
            files = {row["path"]: row["content"] for row in artifacts}
            self.assertTrue({"route-proxmox.pem", "pve-ca.pem"} <= set(files))
            self.assertTrue({"route-pegaprox.pem", "route-nas.pem", "route-udm.pem"}.isdisjoint(files))
            static = json.loads(files["traefik.yml"])
            self.assertEqual(static["entryPoints"]["web"]["http"]["redirections"]["entryPoint"], {"to": "websecure", "scheme": "https"})
            acme = static["certificatesResolvers"]["letsencrypt"]["acme"]
            self.assertEqual(acme["storage"], "/var/traefik/certs/acme.json")
            self.assertEqual(acme["dnsChallenge"]["provider"], "cloudflare")
            self.assertEqual(static["providers"]["plugin"][foundation.PLUGIN]["apiValidateSSL"], "true")
            mounts = {r["target"]: r for r in render.compose(staged)["services"]["traefik"]["volumes"]}
            self.assertTrue({discovery.ca_path("pegaprox"), discovery.ca_path("nas"), discovery.ca_path("udm")}.isdisjoint(mounts))
            self.assertTrue(mounts[discovery.ca_path("proxmox")]["read_only"])
            ca.unlink()
            with self.assertRaises(FileNotFoundError):
                foundation.files(staged)


if __name__ == "__main__":
    unittest.main()
