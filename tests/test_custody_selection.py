"""Keep actual stack exclusions separate from completed-group provenance."""

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
spec = importlib.util.spec_from_file_location(
    "custody_selection_compiler", FRAMEWORK / "blueprints/compile.py"
)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class CustodySelectionTests(unittest.TestCase):
    def custody_overlay(self):
        """Invent source bindings; these proofs deliberately claim no native acceptance."""
        overlay = c.read(ROOT / "site.example.json")
        packets = c.compile_stack(ROOT, overlay, [])
        catalogue = '{"fixture":"catalogue", "literal":"${inputs} ${domains.primary}"}\n'
        overlay["values"]["custody.catalogue"] = catalogue
        for engine, roles in (
            ("postgresql", ("postgresql", "identity", "db-tools")),
            ("mariadb", ("mariadb",)),
        ):
            digest = lambda label: hashlib.sha256(("synthetic-" + label).encode()).hexdigest()
            acceptance = json.dumps({"fixture": engine, "literal": "${inputs}"}) + "\n"
            overlay["values"]["custody." + engine + "_acceptance"] = acceptance
            cfgs = {name: json.loads(packets[name]["files"]["site.json"]) for name in roles}
            paths = cfgs[engine]["paths"]
            request = digest(engine + "-request")
            group = {
                "directory": "database-network-cutover-" + engine + "-example",
                "schema": "homelab-postgresql-cutover-v1" if engine == "postgresql" else "homelab-database-server-cutover-v1",
                "operation": engine + "-example",
                "records": {"request.json": request, "claim.json": request, "complete.json": digest(engine + "-complete")},
                "catalogue": {"file": "custody-catalogue.json", "sha256": hashlib.sha256(catalogue.encode()).hexdigest()},
                "acceptance": {"file": "custody-acceptance.json", "sha256": hashlib.sha256(acceptance.encode()).hexdigest()},
                "recovery": {"mount": paths["backup_mount"], "directory": paths["backup_directory"], "source": paths["backup_source"]},
                "members": {
                    role: {
                        "vmid": cfg["guest"]["vmid"], "node": cfg["site"]["node"],
                        "installed_site": "/srv/example-installed/" + role + ".json",
                        "overlay": {"directory": "database-network-apply-" + digest(role + "-review"), "sha256": digest(role + "-overlay")},
                        "initial_state_sha256": digest(role + "-initial-state"),
                        "initial_ordinary": None if role == engine else {
                            "operation": "ordinary-100-1", "sha256": digest(role + "-old-receipt"), "source_sha256": digest(role + "-old-source"),
                        },
                    } for role, cfg in cfgs.items()
                },
            }
            for role in roles:
                overlay["guests"][role] = {"config": {
                    "coordinated_custody": {"schema": "homelab-coordinated-custody-v1", "group": copy.deepcopy(group)},
                    "paths": {"coordinated_custody_inputs": "${inputs}"},
                }}
        return overlay

    def test_selected_proofs_are_literal_and_disabled_members_retain_complete_source(self):
        """Compile actual profiles with both synthetic groups and valid exclusions."""
        overlay = self.custody_overlay()
        for disabled in ([], ["db-tools"], ["identity", "db-tools", "automation", "zigbee2mqtt"]):
            with self.subTest(disabled=disabled):
                packets = c.compile_stack(ROOT, overlay, disabled)
                self.assertEqual(len(packets), 11)
                for role in ("postgresql", "identity", "db-tools", "mariadb"):
                    packet = packets[role]
                    cfg = json.loads(packet["files"]["site.json"])
                    selected = overlay["guests"][role]["config"]["coordinated_custody"]
                    self.assertEqual(cfg["coordinated_custody"], selected)
                    self.assertEqual(cfg["paths"]["coordinated_custody_inputs"], "/var/lib/homelab-inputs/ordinary/" + role + "/" + packet["identity"])
                    self.assertEqual(packet["enabled"], role not in disabled)
                    engine = "mariadb" if role == "mariadb" else "postgresql"
                    self.assertEqual(packet["files"]["custody-catalogue.json"], overlay["values"]["custody.catalogue"])
                    self.assertEqual(packet["files"]["custody-acceptance.json"], overlay["values"]["custody." + engine + "_acceptance"])
                    self.assertIn("${inputs}", packet["files"]["custody-catalogue.json"])
                    self.assertIn("${domains.primary}", packet["files"]["custody-catalogue.json"])
                for role in set(packets) - {"postgresql", "identity", "db-tools", "mariadb"}:
                    self.assertNotIn("coordinated_custody", json.loads(packets[role]["files"]["site.json"]))
                self.assertEqual(overlay["accepted"], {})

    def test_source_preserves_separately_pinned_initial_receipt_serializations(self):
        """Keep both raw starting pins through real profiles, including a disabled leaf."""
        overlay = self.custody_overlay()
        expected = {}
        for engine, roles in (("postgresql", ("postgresql", "identity", "db-tools")), ("mariadb", ("mariadb",))):
            group = overlay["guests"][engine]["config"]["coordinated_custody"]["group"]
            self.assertEqual(group["directory"], "database-network-cutover-" + group["operation"])
            for role, member in group["members"].items():
                source_hash = hashlib.sha256(("synthetic-source-" + role).encode()).hexdigest()
                record = {"status": "passed", "binding": {"vmid": member["vmid"], "source_sha256": source_hash},
                          "state_sha256": member["initial_state_sha256"], "result": {"fixture": role}}
                canonical = (json.dumps(record, indent=2) + "\n").encode()
                immutable = (json.dumps(record, sort_keys=True, indent=2) + "\n").encode()
                self.assertNotEqual(canonical, immutable)
                expected[role] = {"operation": "ordinary-100-1", "sha256": hashlib.sha256(canonical).hexdigest(),
                                  "immutable_sha256": hashlib.sha256(immutable).hexdigest(), "source_sha256": source_hash}
                member["initial_ordinary"] = expected[role]
            for role in roles:
                overlay["guests"][role]["config"]["coordinated_custody"]["group"] = copy.deepcopy(group)
        packets = c.compile_stack(ROOT, overlay, ["db-tools"])
        for role, initial in expected.items():
            cfg = json.loads(packets[role]["files"]["site.json"])
            for member_role, member in cfg["coordinated_custody"]["group"]["members"].items():
                self.assertEqual(member["initial_ordinary"], expected[member_role])
            self.assertEqual(cfg["coordinated_custody"]["group"]["members"][role]["initial_ordinary"], initial)
        self.assertFalse(packets["db-tools"]["enabled"])
        self.assertEqual(overlay["accepted"], {})

    def test_disabled_member_is_never_a_missing_or_conflicting_custody_waiver(self):
        """Real source closure must refuse before any runtime packet is available."""
        original = self.custody_overlay()
        refusals = {
            "missing-copy": "Configured group provenance copies must agree, including disabled members",
            "different-group": "Configured group provenance copies must agree, including disabled members",
            "wrong-vmid": "A custody selection belongs only to its exact guest and role",
            "altered-proof": "Preserve exact custody source proof bytes during resolution",
            "wrong-proof-name": "Bind the complete immutable custody source inputs",
            "unknown-waiver": "Use closed coordinated custody fields",
            "old-mariadb-directory": "Bind the exact existing group directory",
            "invalid-immutable-hash": "Pin an exact coordinated evidence digest",
            "unknown-receipt-field": "Use closed coordinated custody fields",
        }
        for case, message in refusals.items():
            changed = copy.deepcopy(original)
            config = changed["guests"]["db-tools"]["config"]
            group = config["coordinated_custody"]["group"]
            if case == "missing-copy":
                changed["guests"].pop("db-tools")
            elif case == "different-group":
                group["records"]["request.json"] = group["records"]["claim.json"] = "f" * 64
            elif case == "wrong-vmid":
                for role in ("postgresql", "identity", "db-tools"):
                    changed["guests"][role]["config"]["coordinated_custody"]["group"]["members"]["db-tools"]["vmid"] = 1202
            elif case == "altered-proof":
                changed["values"]["custody.catalogue"] += " "
            elif case == "wrong-proof-name":
                group["catalogue"]["file"] = "missing-catalogue.json"
            elif case == "unknown-waiver":
                for role in ("postgresql", "identity", "db-tools"):
                    changed["guests"][role]["config"]["coordinated_custody"]["completed_release"] = True
            elif case == "old-mariadb-directory":
                changed["guests"]["mariadb"]["config"]["coordinated_custody"]["group"]["directory"] = "database-server-cutover-mariadb-example"
            elif case == "invalid-immutable-hash":
                group["members"]["db-tools"]["initial_ordinary"]["immutable_sha256"] = "invalid"
            else:
                group["members"]["db-tools"]["initial_ordinary"]["canonical_sha256"] = "f" * 64
            if case in ("wrong-proof-name", "invalid-immutable-hash", "unknown-receipt-field"):
                for role in ("postgresql", "identity", "db-tools"):
                    changed["guests"][role]["config"]["coordinated_custody"]["group"] = copy.deepcopy(group)
            with self.subTest(case=case), self.assertRaisesRegex(ValueError, "^" + message + "$"):
                c.compile_stack(ROOT, changed, ["db-tools"])

    def test_valid_exclusions_keep_all_configured_guests_and_actual_dependencies(self):
        """Excluding a valid leaf must not force its job or remove its source."""
        configured = {
            "dns", "ingress", "postgresql", "mariadb", "influxdb", "identity",
            "db-tools", "automation", "bitwarden", "pegaprox", "zigbee2mqtt",
        }
        for disabled in (
            [],
            ["db-tools"],
            ["identity", "db-tools", "automation", "zigbee2mqtt"],
            ["pegaprox"],
            ["bitwarden"],
        ):
            with self.subTest(disabled=disabled):
                packets = c.compile_stack(ROOT, c.read(ROOT / "site.example.json"), disabled)
                self.assertEqual(set(packets), configured)
                self.assertEqual(
                    {name for name, packet in packets.items() if packet["enabled"]},
                    configured - set(disabled),
                )
                for name, packet in packets.items():
                    cfg = json.loads(packet["files"]["site.json"])
                    self.assertEqual(packet["kind"], name)
                    self.assertNotIn("coordinated_custody", cfg)

    def test_exclusions_cannot_leave_actual_consumers_without_prerequisites(self):
        """Group membership must not create a bypass of the existing guest DAG."""
        for disabled in (
            ["identity"],
            ["identity", "db-tools"],
            ["identity", "automation"],
            ["identity", "db-tools", "automation"],
            ["dns"],
        ):
            with self.subTest(disabled=disabled), self.assertRaisesRegex(
                ValueError, "Cannot disable a prerequisite"
            ):
                c.compile_stack(ROOT, c.read(ROOT / "site.example.json"), disabled)


if __name__ == "__main__":
    unittest.main()
