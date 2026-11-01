"""Deploy the published upstream image beside the preserved radio, not a new guest."""
import copy
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
sys.path.insert(0, str(FRAMEWORK / "blueprints"))
sys.path.insert(0, str(FRAMEWORK / "proxmox/applications"))
import compile as compiler
import guest_contract
import render
import workflows


class WinetStackTests(unittest.TestCase):
    def packet(self, overlay=None):
        return compiler.compile_stack(ROOT, overlay or compiler.read(ROOT / "site.example.json"), [])["zigbee2mqtt"]

    def test_one_guest_two_services_with_exact_public_image_and_private_configuration(self):
        packet = self.packet()
        cfg = json.loads(packet["files"]["site.json"])
        stack = json.loads(packet["files"]["stack.json"])
        self.assertEqual(cfg["guest"]["vmid"], 209)
        self.assertEqual(cfg["guest"]["hostname"], "radio")
        self.assertEqual(cfg["guest"]["memory_mib"], 1024)
        self.assertEqual(guest_contract.phases(cfg), ["preparation", "zigbee2mqtt", "winet"])
        self.assertEqual(stack["services"]["winet"]["image"],
                         "ghcr.io/theaussiepom/winet-extractor@sha256:82c6b886967995f0a3cfe6fb5e20eeef70d10aa525d5bd824064eb272e1ce51a")
        self.assertEqual(stack["services"]["winet"]["extra_hosts"],
                         stack["services"]["zigbee2mqtt"]["extra_hosts"])
        self.assertEqual(stack["winet"]["mqtt_server"], stack["zigbee"]["mqtt_server"])
        compose = render.compose(stack)
        self.assertEqual(set(compose["services"]), {"zigbee2mqtt", "winet"})
        self.assertEqual(compose["services"]["winet"]["volumes"][0]["target"], "/data/options.json")
        self.assertTrue(compose["services"]["winet"]["volumes"][0]["read_only"])
        self.assertNotIn("devices", compose["services"]["winet"])
        self.assertNotIn("ports", compose["services"]["winet"])
        self.assertFalse(cfg["app"]["exclusive_writer_confirmed"])
        self.assertEqual(len(workflows.models(ROOT)["guest-zigbee2mqtt.yml"]["jobs"]), 1)

    def test_iot_interface_has_no_gateway_or_inbound_grant(self):
        cfg = json.loads(self.packet()["files"]["site.json"])
        iot = cfg["guest"]["interfaces"][2]
        self.assertEqual(iot, {"role": "iot", "bridge": "vmbr0", "vlan": 107,
                               "mac": "02:00:0a:02:00:01", "ipv4": "198.19.107.246/24", "ipv6": "manual"})
        self.assertEqual(sum(bool(n.get("gateway")) for n in cfg["guest"]["interfaces"]), 1)
        rule = next(r for r in cfg["guest"]["rules"] if r["comment"] == "WiNet encrypted inverter telemetry only")
        self.assertEqual({k:rule[k] for k in ("source", "destination", "proto", "port", "direction")},
                         {"source": "198.19.107.246/32", "destination": "198.19.107.23/32",
                          "proto": "tcp", "port": "443", "direction": "out"})

    def test_private_overlay_cannot_schedule_an_unconfigured_optional_phase(self):
        import tempfile
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "stack"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            profile = root / "guests/zigbee2mqtt/profile.json"
            value = json.loads(profile.read_text())
            value["config"]["app"]["service_health_checks"].pop("winet")
            profile.write_text(json.dumps(value))
            overlay = compiler.read(root / "site.example.json")
            overlay["guests"]["zigbee2mqtt"] = {"config": {"app": {"service_health_checks": {"winet": [{}]}}}}
            with self.assertRaisesRegex(ValueError, "shared profile"):
                compiler.compile_stack(root, overlay, [])

    def test_service_cannot_be_unlabelled_or_hidden_in_the_radio_phase(self):
        packet = self.packet()
        cfg = json.loads(packet["files"]["site.json"])
        stack = json.loads(packet["files"]["stack.json"])
        cfg["app"]["service_health_checks"].pop("winet")
        with self.assertRaisesRegex(ValueError, "every radio application"):
            guest_contract.validate(cfg, stack)


if __name__ == "__main__":
    unittest.main()
