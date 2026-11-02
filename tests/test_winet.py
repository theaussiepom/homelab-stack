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

    def test_tagged_radio_interfaces_use_the_declared_physical_uplinks(self):
        # Reference host inventory: management and service/IoT trunks are separate.
        carried = {"vmbr0": {15, 25}, "vmbr1": {20, 30, 40, 100, 107}}
        cfg = json.loads(self.packet()["files"]["site.json"])
        for nic in cfg["guest"]["interfaces"]:
            if nic.get("vlan") is not None:
                self.assertIn(nic["vlan"], carried[nic["bridge"]])
        self.assertEqual([n["bridge"] for n in cfg["guest"]["interfaces"]],
                         ["vmbr0", "vmbr30", "vmbr1"])

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

    def test_health_assertion_cannot_accept_unhealthy_as_healthy(self):
        cfg = json.loads(self.packet()["files"]["site.json"])
        check = cfg["app"]["service_health_checks"]["winet"][0]
        self.assertEqual(check["argv"][:2], ["python3", "-c"])
        self.assertNotIn("{{", check["argv"][2])
        self.assertEqual(check["expect"], '"healthy": true')

    def test_actual_ansible_extra_vars_run_the_health_check_without_templating(self):
        import subprocess
        import tempfile
        import yaml
        check = json.loads(self.packet()["files"]["site.json"])["app"]["service_health_checks"]["winet"][0]
        task = next(t for t in yaml.safe_load((FRAMEWORK / "proxmox/applications/ansible/reconcile.yml").read_text())[0]["tasks"]
                    if t["name"] == "Check this service after reconciliation")
        ansible = Path(sys.executable).with_name("ansible-playbook")
        self.assertTrue(ansible.is_file(), "Install the selected framework's pinned test requirements")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "bin"
            binary.mkdir()
            called, inspection = root / "called", root / "inspection.json"
            fake = binary / "docker"
            fake.write_text("#!" + sys.executable + "\nimport json,sys\nfrom pathlib import Path\n"
                            + "assert sys.argv[1:]==['inspect','--type=container','homelab-zigbee2mqtt-winet-1']\n"
                            + "Path(" + repr(str(called)) + ").write_text('called')\n"
                            + "print(Path(" + repr(str(inspection)) + ").read_text())\n")
            fake.chmod(0o700)
            play = root / "play.json"
            play.write_text(json.dumps([{"hosts": "localhost", "connection": "local", "gather_facts": False,
                                         "environment": {"PATH": str(binary) + os.pathsep + os.environ["PATH"]},
                                         "tasks": [task]}]))
            extra = root / "extra.json"
            extra.write_text(json.dumps({"app": {"health_checks": [check]}}))
            for state, expected in (({"Running": True, "Health": {"Status": "healthy"}}, 0),
                                    ({"Running": True, "Health": {"Status": "unhealthy"}}, 2),
                                    ({"Running": False, "Health": {"Status": "healthy"}}, 2),
                                    ({"Running": True}, 2)):
                inspection.write_text(json.dumps([{"State": state}]))
                called.unlink(missing_ok=True)
                result = subprocess.run([str(ansible), "-i", "localhost,", "--extra-vars", "@" + str(extra), str(play)],
                                        capture_output=True, text=True, timeout=30,
                                        env=dict(os.environ, ANSIBLE_LOCAL_TEMP=str(root / "ansible")))
                with self.subTest(state=state):
                    self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                    self.assertTrue(called.is_file(), "Health must reach Docker rather than fail in Jinja")

    def test_iot_interface_has_no_gateway_or_inbound_grant(self):
        cfg = json.loads(self.packet()["files"]["site.json"])
        iot = cfg["guest"]["interfaces"][2]
        self.assertEqual(iot, {"role": "iot", "bridge": "vmbr1", "vlan": 107,
                               "mac": "02:00:0a:02:00:01", "ipv4": "198.19.107.246/24", "ipv6": "manual"})
        self.assertEqual(sum(bool(n.get("gateway")) for n in cfg["guest"]["interfaces"]), 1)
        rule = next(r for r in cfg["guest"]["rules"] if r["comment"] == "WiNet encrypted inverter telemetry only")
        self.assertEqual({k:rule[k] for k in ("source", "destination", "proto", "port", "direction")},
                         {"source": "198.19.107.246/32", "destination": "198.19.107.23/32",
                          "proto": "tcp", "port": "443", "direction": "out"})
        self.assertEqual(rule["interface"], "net2")

    def test_package_egress_cannot_bypass_the_iot_endpoint_even_with_spoofed_source(self):
        import connections
        cfg = json.loads(self.packet()["files"]["site.json"])
        rules = cfg["guest"]["rules"]
        for source, destination, interface, port, expected in (
            ("198.19.107.246", "198.19.107.23", "net2", 443, True),
            ("198.19.107.246", "198.19.107.24", "net2", 443, False),
            ("198.19.107.246", "198.19.107.23", "net2", 80, False),
            ("198.19.107.246", "198.19.107.23", "net2", 8082, False),
            ("198.18.25.22", "198.19.107.24", "net2", 443, False),
            ("198.18.25.22", "203.0.113.10", "net0", 443, True),
            ("198.18.25.22", "203.0.113.10", "net2", 443, False),
            ("198.19.107.246", "203.0.113.10", "net0", 443, False),
            ("198.18.30.22", "198.18.30.21", "net1", 1883, True),
        ):
            flow = connections.Connection("zigbee2mqtt", None, source, destination, "tcp", port)
            with self.subTest(source=source, destination=destination, interface=interface, port=port):
                self.assertEqual(connections.permits(rules, "out", flow, interface), expected)

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
