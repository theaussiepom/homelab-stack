"""Exercise database-tool network paths without contacting a guest or database."""

import importlib.util
import json
import os
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
        failed = Environment().compile_expression(task["failed_when"])
        for result, expected in (({"rc": 0, "stdout": "302"}, False),
                                 ({"rc": 60, "stdout": "302"}, True),
                                 ({"rc": 22, "stdout": "404"}, True),
                                 ({"rc": 0, "stdout": "200"}, True)):
            with self.subTest(result=result):
                self.assertEqual(failed(ordinary_health=result, item=route), expected)

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
                              "replacement": "https://databases.example.invalid/$1", "permanent": True}
        })
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
            ("addresses.db_tools_mariadb", c.manifest(ROOT)["values"]["addresses.mariadb_backend"]),
            ("mac.db-tools.3", c.manifest(ROOT)["values"]["mac.mariadb.1"]),
        ):
            overlay = c.read(ROOT / "site.example.json")
            overlay["values"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "network identity"):
                self.configurations(overlay)

    def test_tools_remain_an_independent_leaf_with_both_database_dependencies(self):
        manifest = c.manifest(ROOT)
        self.assertEqual(manifest["guests"]["db-tools"]["depends_on"], ["postgresql", "mariadb", "ingress", "identity"])
        workflow = yaml.safe_load((ROOT / ".github/workflows/deploy.yml").read_text())
        self.assertEqual(workflow["jobs"]["db-tools"]["name"], "CloudBeaver")
        self.assertEqual(workflow["jobs"]["db-tools"]["needs"], ["selection", "postgresql", "mariadb", "ingress", "identity"])
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
