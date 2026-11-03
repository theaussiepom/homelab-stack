"""Exercise database-tool network paths without contacting a guest or database."""

import importlib.util
import copy
import json
import os
import re
from pathlib import Path
import sys
import unittest
import yaml
from jinja2 import Environment

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
spec = importlib.util.spec_from_file_location("db_tools_compiler", FRAMEWORK / "blueprints/compile.py")
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
sys.path.insert(0, str(FRAMEWORK / "proxmox/applications"))
import render
import discovery
import cloudbeaver


class DatabaseToolsTests(unittest.TestCase):
    def configurations(self, overlay=None, disabled=None):
        packets = c.compile_stack(ROOT, overlay or c.read(ROOT / "site.example.json"), disabled or [])
        return {name: json.loads(packet["files"]["site.json"]) for name, packet in packets.items()}

    def test_cloudbeaver_publishes_only_the_authenticated_gateway(self):
        packet = c.compile_stack(ROOT, c.read(ROOT / "site.example.json"), [])["db-tools"]
        cfg = json.loads(packet["files"]["site.json"])
        stack = json.loads(packet["files"]["stack.json"])
        self.assertEqual(cfg["app"]["variant"], "cloudbeaver")
        self.assertEqual(stack["variant"], "cloudbeaver")
        self.assertEqual(set(cfg["app"]["service_health_checks"]), {"cloudbeaver"})
        self.assertEqual(cfg["app"]["endpoints"], {"cloudbeaver": {"web": "http://198.18.30.32:80"}})
        compose = render.compose(stack)
        self.assertEqual(set(compose["services"]), {"cloudbeaver", "auth_gateway"})
        server = compose["services"]["cloudbeaver"]
        gateway = compose["services"]["auth_gateway"]
        self.assertNotIn("ports", server)
        self.assertNotEqual(server.get("network_mode"), "host")
        self.assertEqual(server["user"], "8978:8978")
        self.assertEqual(gateway["user"], "65532:65532")
        self.assertEqual(len(gateway["ports"]), 1)
        self.assertTrue(gateway["ports"][0].startswith("198.18.30.32:80:"))
        self.assertIn("/srv/homelab/data/cloudbeaver", {mount["source"] for mount in server["volumes"]})
        self.assertEqual(stack["cloudbeaver"]["heap_mib"], 1024)
        self.assertEqual(sum(row["memory_mib"] for row in stack["services"].values()), 1664)
        self.assertEqual(stack["guest_memory_mib"], 2048)
        for name, service in compose["services"].items():
            with self.subTest(service=name):
                self.assertEqual(service["restart"], "always")
                self.assertNotIn("privileged", service)
                self.assertFalse(any("pgadmin" in mount["source"] for mount in service.get("volumes", [])))
                self.assertFalse(any("docker.sock" in mount["source"] for mount in service.get("volumes", [])))
        self.assertEqual(server["image"], "dbeaver/cloudbeaver:26.2.3@sha256:a537c60a7ca98d8d791c11c01172c1354e8dedfe222d04a54795ceeb32f12bbc")
        self.assertEqual(gateway["image"], "quay.io/oauth2-proxy/oauth2-proxy:v7.15.5@sha256:0d989b27d90d5e527fb2b045d864c4001c3104bdd763b3211b7e9ba2110380ea")

    def test_connection_metadata_follows_both_selected_backends_without_database_credentials(self):
        overlay = c.read(ROOT / "site.example.json")
        overlay["values"].update({"addresses.mariadb_backend": "198.18.32.124", "addresses.postgresql_backend": "198.18.31.123"})
        packet = c.compile_stack(ROOT, overlay, [])["db-tools"]
        cfg = json.loads(packet["files"]["site.json"])
        stack = json.loads(packet["files"]["stack.json"])
        self.assertEqual(cfg["app"]["service_connections"], {
            "cloudbeaver.postgresql": {"service": "postgresql.postgresql", "address": "backend"},
            "cloudbeaver.mariadb": {"service": "mariadb.mariadb", "address": "backend"},
        })
        for engine, host, port, database in (
            ("postgresql", "198.18.31.123", 5432, "postgres"),
            ("mariadb", "198.18.32.124", 3306, ""),
        ):
            with self.subTest(engine=engine):
                row = stack["cloudbeaver"]["connections"][engine]
                self.assertEqual(row["host"], host)
                self.assertEqual(row["port"], port)
                self.assertEqual(row["database"], database)
                fields = {"name", "driver", "database", "host", "port"}
                if engine == "postgresql":
                    fields.add("sslmode")
                    self.assertEqual(row["sslmode"], "prefer")
                self.assertEqual(set(row), fields)
        self.assertEqual(stack["foundation"]["oidc_issuer"], "https://service-6.example.invalid/application/o/pgadmin4/")
        self.assertEqual(stack["foundation"]["user_claim"], "preferred_username")
        self.assertEqual(set(stack["foundation"]["secret_files"]), {"oauth_client_secret"})
        checks = cfg["app"]["service_health_checks"]["cloudbeaver"]
        self.assertEqual(checks, cfg["app"]["health_checks"])
        self.assertEqual(checks[0]["argv"], ["python3", "/opt/homelab-app/cloudbeaver-runtime.py", "health", "--config", "/opt/homelab-app/runtime/cloudbeaver-public.json"])
        route = checks[-1]
        self.assertEqual(route["argv"][-1], "https://db.example.invalid/")
        self.assertEqual(route["expect"], "302")
        self.assertEqual(route["argv"][route["argv"].index("--resolve") + 1], "db.example.invalid:443:198.18.40.33")
        self.assertFalse({"--insecure", "-k", "--location", "-L"} & set(route["argv"]))
        play = yaml.safe_load((FRAMEWORK / "proxmox/applications/ansible/reconcile.yml").read_text())[0]
        task = next(row for row in play["tasks"] if row.get("loop") == "{{ app.health_checks }}")
        failed = Environment(autoescape=True).compile_expression(task["failed_when"])
        for result, expected in (({"rc": 0, "stdout": "302"}, False),
                                 ({"rc": 60, "stdout": "302"}, True),
                                 ({"rc": 28, "stdout": "302"}, True),
                                 ({"rc": 22, "stdout": "404"}, True),
                                 ({"rc": 0, "stdout": "301"}, True),
                                 ({"rc": 0, "stdout": "200"}, True)):
            with self.subTest(result=result):
                self.assertEqual(failed(ordinary_health=result, item=route), expected)

    def test_canonical_https_retry_budget_retains_tls_and_the_step_cap(self):
        overlay = c.read(ROOT / "site.example.json")
        overlay["values"].update({"domains.db_tools": "databases.example.invalid",
                                  "addresses.ingress_frontend": "198.18.40.133"})
        packets = c.compile_stack(ROOT, overlay, [])
        cfg = json.loads(packets["db-tools"]["files"]["site.json"])
        checks = cfg["app"]["health_checks"]
        self.assertEqual(checks, cfg["app"]["service_health_checks"]["cloudbeaver"])
        argv = checks[-1]["argv"]
        option = lambda name: int(argv[argv.index(name) + 1])
        self.assertEqual((option("--retry"), option("--retry-delay"),
                          option("--retry-max-time"), option("--max-time")),
                         (1200, 2, 2250, 15))
        self.assertGreaterEqual(option("--retry") * option("--retry-delay"), option("--retry-max-time"))
        self.assertEqual(argv[-1], "https://databases.example.invalid/")
        self.assertEqual(argv[argv.index("--resolve") + 1], "databases.example.invalid:443:198.18.40.133")
        self.assertFalse({"--insecure", "-k", "--location", "-L"} & set(argv))
        self.assertIn("--fail", argv)
        self.assertEqual(checks[-1]["expect"], "302")
        self.assertEqual(len(checks), 2)
        for unchanged in [json.loads(packets["music"]["files"]["site.json"])["app"]["health_checks"][-1]]:
            original = unchanged["argv"]
            self.assertEqual(original[original.index("--retry") + 1], "30")
            self.assertEqual(original[original.index("--retry-max-time") + 1], "180")
        workflow = yaml.safe_load((ROOT / ".github/workflows/guest-db-tools.yml").read_text())
        steps = [step for job in workflow["jobs"].values() for step in job["steps"]
                 if step.get("with", {}).get("phase") == "cloudbeaver"
                 and "/.github/actions/guest-phase@" in step.get("uses", "")]
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0]["timeout-minutes"], 45)
        self.assertLess(option("--retry-max-time") + option("--retry-delay") + option("--max-time"),
                        steps[0]["timeout-minutes"] * 60)

    def test_missing_database_firewall_or_wrong_driver_binding_refuses_compilation(self):
        for owner, direction in (("db-tools", "out"), ("mariadb", "in")):
            overlay = c.read(ROOT / "site.example.json")
            profile = c.read(ROOT / "guests" / owner / "profile.json")
            rules = profile["config"]["guest"]["rules"]
            overlay["guests"][owner] = {"config": {"guest": {"rules": [
                rule for rule in rules if not (rule["direction"] == direction and rule.get("port") == "3306")
            ]}}}
            with self.subTest(owner=owner), self.assertRaisesRegex(ValueError, "3306"):
                self.configurations(overlay)
        overlay = c.read(ROOT / "site.example.json")
        overlay["guests"]["db-tools"] = {"config": {"app": {"service_connections": {
            "cloudbeaver.postgresql": {"service": "mariadb.mariadb", "address": "backend"},
        }}}}
        with self.assertRaises(ValueError):
            self.configurations(overlay)

    def test_private_overrides_cannot_bypass_the_gateway_or_silently_change_tls(self):
        overrides = [
            {"stack": {"services": {"auth_gateway": {"environment": {"OAUTH2_PROXY_SKIP_AUTH_ROUTES": ".*"}}}}},
            {"stack": {"services": {"cloudbeaver": {"extra_mounts": [{"source": "/srv/homelab/data/pgadmin", "target": "/retained", "read_only": True}]}}}},
            {"config": {"app": {"variant": "pgadmin"}}},
            {"config": {"app": {"endpoints": {"cloudbeaver": {"web": "http://${addresses.pgadmin_backend}:8978"}}}}},
            {"stack": {"cloudbeaver": {"connections": {"postgresql": {"sslmode": "verify-full"}}}}},
        ]
        for override in overrides:
            overlay = c.read(ROOT / "site.example.json")
            overlay["guests"]["db-tools"] = override
            with self.subTest(override=override), self.assertRaises(ValueError):
                self.configurations(overlay)

    def test_legacy_web_hostname_redirects_before_login_without_redirecting_canonical(self):
        overlay = c.read(ROOT / "site.example.json")
        overlay["values"].update({
            "domains.db_tools": "databases.example.invalid",
            "domains.pgadmin": "old-databases.example.invalid",
        })
        packets = c.compile_stack(ROOT, overlay, [])
        cfg = json.loads(packets["db-tools"]["files"]["site.json"])
        routes = cfg["routes"]
        self.assertEqual(routes["db-tools"]["host"], "databases.example.invalid")
        self.assertEqual(routes["pgadmin-compat"]["host"], "old-databases.example.invalid")
        self.assertEqual(routes["db-tools"]["url"], routes["pgadmin-compat"]["url"])
        self.assertEqual(routes["db-tools"]["middlewares"], ["security-headers"])
        self.assertEqual(routes["pgadmin-compat"]["middlewares"], ["security-headers", "db-canonical"])
        shared = discovery.shared(json.loads(packets["ingress"]["files"]["stack.json"])["routing"])
        self.assertEqual(shared["http"]["middlewares"]["db-canonical"], {
            "redirectRegex": {"regex": "^https://[^/]+/(.*)",
                              "replacement": "https://databases.example.invalid/", "permanent": False}
        })
        redirect = shared["http"]["middlewares"]["db-canonical"]["redirectRegex"]
        for suffix in ("/", "/browser/", "/oauth2/callback?code=old&state=old",
                       "//external.example.invalid/path?next=https://external.example.invalid/",
                       "/%2f%2fexternal.example.invalid/?return_to=https%3A%2F%2Fexternal.example.invalid"):
            with self.subTest(suffix=suffix):
                self.assertEqual(re.sub(redirect["regex"], redirect["replacement"],
                                        "https://old-databases.example.invalid" + suffix),
                                 "https://databases.example.invalid/")
        labels = discovery.labels(cfg)
        self.assertEqual(labels["traefik.http.routers.db-tools.middlewares"], "security-headers@file")
        self.assertEqual(labels["traefik.http.routers.pgadmin-compat.middlewares"], "security-headers@file,db-canonical@file")
        self.assertEqual(labels["traefik.http.routers.db-tools.rule"], "Host(`databases.example.invalid`)")
        self.assertEqual(labels["traefik.http.routers.pgadmin-compat.rule"], "Host(`old-databases.example.invalid`)")

    def test_database_paths_use_separate_existing_bridges_and_exact_server_rules(self):
        overlay = c.read(ROOT / "site.example.json")
        overlay["values"].update({
            "addresses.db_tools_mariadb": "198.18.32.132",
            "addresses.mariadb_backend": "198.18.32.124",
            "addresses.pgadmin_postgresql": "198.18.31.132",
            "addresses.postgresql_backend": "198.18.31.123",
        })
        cfg = self.configurations(overlay)
        tools = cfg["db-tools"]["guest"]
        self.assertEqual(tools["vmid"], 202)
        self.assertEqual(tools["hostname"], "db-tools")
        self.assertEqual((tools["cpu"], tools["memory_mib"], tools["root_gib"]), (1, 2048, 4))
        self.assertEqual([nic["bridge"] for nic in tools["interfaces"]], ["vmbr0", "vmbr30", "vmbr31", "vmbr32"])
        self.assertEqual(tools["volumes"]["data"], {"path": "/srv/homelab", "size_gib": 2})
        for target, source, destination, port in (
            ("postgresql", "198.18.31.132", "198.18.31.123", 5432),
            ("mariadb", "198.18.32.132", "198.18.32.124", 3306),
        ):
            with self.subTest(target=target):
                self.assertEqual(c.connections.source_address(tools, destination), source)
                connection = c.connections.Connection("db-tools", target, source, destination, "tcp", port)
                self.assertTrue(c.connections.permits(tools["rules"], "out", connection))
                self.assertTrue(c.connections.permits(cfg[target]["guest"]["rules"], "in", connection))
                for changed in (
                    {"source_address": "198.18.25.32"},
                    {"target_address": destination.rsplit(".", 1)[0] + ".125"},
                    {"port": port + 1},
                    {"protocol": "udp"},
                ):
                    wrong = c.connections.Connection(**(connection.__dict__ | changed))
                    self.assertFalse(c.connections.permits(cfg[target]["guest"]["rules"], "in", wrong))

    def test_database_publications_use_only_the_existing_server_backends(self):
        overlay = c.read(ROOT / "site.example.json")
        overlay["values"].update({
            "hostnames.postgresql_database": "postgres.test.example.invalid",
            "hostnames.mariadb_database": "mariadb.test.example.invalid",
            "addresses.mariadb_backend": "198.18.32.124",
            "addresses.postgresql_backend": "198.18.31.123",
        })
        packets = c.compile_stack(ROOT, overlay, [])
        dns = json.loads(packets["dns"]["files"]["stack.json"])["dns_records"]
        for engine, host, address, port in (
            ("postgresql", "postgres.test.example.invalid", "198.18.31.123", 5432),
            ("mariadb", "mariadb.test.example.invalid", "198.18.32.124", 3306),
        ):
            with self.subTest(engine=engine):
                cfg = json.loads(packets[engine]["files"]["site.json"])
                self.assertEqual(cfg["app"]["published_services"], {engine: {
                    "hostname": host, "addresses": {"backend": address},
                    "dns_address": "backend", "protocol": "tcp", "port": port,
                }})
                self.assertEqual(dns[host], address)
                self.assertFalse(any(route["url"].endswith(":" + str(port)) for route in cfg.get("routes", {}).values()))

    def test_mariadb_client_identity_collision_refuses_compilation(self):
        for field, value in (
            ("addresses.db_tools_mariadb", c.read(ROOT / "site.example.json")["values"]["addresses.mariadb_backend"]),
            ("mac.db-tools.3", c.read(ROOT / "site.example.json")["values"]["mac.mariadb.1"]),
        ):
            overlay = c.read(ROOT / "site.example.json")
            overlay["values"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "network identity"):
                self.configurations(overlay)

    def test_explicit_endpoints_avoid_startup_discovery_and_preserve_authentication_controls(self):
        for example in ('site.example.json', 'examples/site.second.json'):
            overlay = c.read(ROOT / example)
            packet = c.compile_stack(ROOT, overlay, [])['db-tools']
            stack = json.loads(packet['files']['stack.json'])
            cfg = json.loads(packet['files']['site.json'])
            selected = stack['foundation']
            endpoints = selected['oidc_endpoints']
            for field in ('authorization', 'token', 'userinfo', 'jwks'):
                self.assertEqual(endpoints[field + '_url'], overlay['values']['identity.db_tools_' + field + '_url'])
            self.assertEqual(endpoints['signing_algorithms'], ['RS256'])
            # Compare only the intended explicit-metadata delta to the unchanged
            # discovery branch, with clearly invented in-memory key material.
            secret = b'synthetic fixture material ' * 2
            before = copy.deepcopy(selected)
            before.pop('oidc_endpoints')
            old_alpha, old_options = cloudbeaver.gateway(stack['cloudbeaver'], before, secret)
            alpha, options = cloudbeaver.gateway(stack['cloudbeaver'], selected, secret)
            provider = alpha['providers'][0]
            self.assertEqual(provider['oidcConfig']['skipDiscovery'], True)
            self.assertEqual(provider['oidcConfig']['issuerURL'], selected['oidc_issuer'])
            self.assertEqual(provider['oidcConfig']['jwksURL'], endpoints['jwks_url'])
            self.assertEqual(provider['oidcConfig']['enabledSigningAlgs'], ['RS256'])
            self.assertIs(provider['oidcConfig']['insecureSkipNonce'], False)
            self.assertEqual(provider['code_challenge_method'], 'S256')
            self.assertEqual(provider['scope'], 'openid email profile')
            for configured, field in [('loginURL','authorization'), ('redeemURL','token'), ('profileURL','userinfo')]:
                self.assertEqual(provider.pop(configured), endpoints[field + '_url'])
            for key in ('skipDiscovery','jwksURL','enabledSigningAlgs'):
                provider['oidcConfig'].pop(key)
            self.assertEqual(alpha, old_alpha)
            self.assertEqual(options, old_options)
            checks = cfg['app']['health_checks']
            self.assertEqual(checks, cfg['app']['service_health_checks']['cloudbeaver'])
            self.assertEqual(len(checks), 2)
            self.assertIn('cloudbeaver-runtime.py', checks[0]['argv'][1])
            self.assertEqual(checks[-1]['expect'], '302')
            self.assertNotIn('.well-known/openid-configuration', json.dumps(checks))
            self.assertNotIn(overlay['values']['domains.identity'], json.dumps(checks))

    def test_identity_can_be_disabled_for_first_install_and_updates_without_changing_cloud_packets(self):
        overlay = c.read(ROOT / 'site.example.json')
        baseline = c.compile_stack(ROOT, overlay, [])
        for disabled in (['identity'], ['identity','automation']):
            with self.subTest(disabled=disabled):
                selected = c.compile_stack(ROOT, overlay, disabled)
                self.assertFalse(selected['identity']['enabled'])
                self.assertTrue(selected['db-tools']['enabled'])
                self.assertEqual(selected['db-tools']['files'], baseline['db-tools']['files'])
                self.assertTrue(selected['postgresql']['enabled'])
                self.assertTrue(selected['mariadb']['enabled'])
                self.assertTrue(selected['ingress']['enabled'])
        for prerequisite in ('postgresql','mariadb','ingress'):
            with self.subTest(prerequisite=prerequisite), self.assertRaisesRegex(ValueError, 'prerequisite'):
                c.compile_stack(ROOT, overlay, [prerequisite])

    def test_tools_remain_an_independent_leaf_with_both_database_dependencies(self):
        manifest = c.manifest(ROOT)
        self.assertEqual(manifest["guests"]["db-tools"]["depends_on"], ["postgresql", "mariadb", "ingress"])
        workflow = yaml.safe_load((ROOT / ".github/workflows/deploy.yml").read_text())
        self.assertEqual(workflow["jobs"]["db-tools"]["name"], "CloudBeaver")
        self.assertEqual(workflow["jobs"]["db-tools"]["needs"], ["selection", "postgresql", "mariadb", "ingress"])
        packets = c.compile_stack(ROOT, c.read(ROOT / "site.example.json"), ["db-tools"])
        self.assertFalse(packets["db-tools"]["enabled"])
        self.assertTrue(packets["mariadb"]["enabled"])
        self.assertTrue(packets["postgresql"]["enabled"])
        disabled = ["mariadb", "bitwarden", "automation", "music"]
        with self.assertRaisesRegex(ValueError, "prerequisite"):
            c.compile_stack(ROOT, c.read(ROOT / "site.example.json"), disabled)
        packets = c.compile_stack(ROOT, c.read(ROOT / "site.example.json"), [*disabled, "db-tools"])
        self.assertFalse(packets["mariadb"]["enabled"])
        self.assertFalse(packets["db-tools"]["enabled"])
        self.assertTrue(packets["zigbee2mqtt"]["enabled"])


if __name__ == "__main__":
    unittest.main()
