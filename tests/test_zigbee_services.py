"""The active radio and its broker/DNS bindings are ordinary graph entities."""

import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab"))
sys.path.insert(0, str(FRAMEWORK / "blueprints"))
sys.path.insert(0, str(FRAMEWORK / "proxmox/applications"))
import compile as compiler
import workflows
import render


class ZigbeeServiceTests(unittest.TestCase):
    def packets(self, overlay=None):
        return compiler.compile_stack(
            ROOT, overlay or compiler.read(ROOT / "site.example.json"), []
        )

    def stack(self, packet):
        return json.loads(packet["files"]["stack.json"])

    def test_radio_deploys_active_through_infrastructure_preparation_and_application(
        self,
    ):
        packet = self.packets()["zigbee2mqtt"]
        cfg = json.loads(packet["files"]["site.json"])
        self.assertEqual(cfg["guest"]["vmid"], 209)
        self.assertTrue(cfg["guest"]["started"] and cfg["guest"]["start_on_boot"])
        self.assertFalse(
            {"usb_stage", "radio_cd_mode", "zigbee_first_start_approval"}
            & cfg["app"].keys()
        )
        document = render.compose(self.stack(packet))["services"]["zigbee2mqtt"]
        device = cfg["guest"]["serial_device"]["path"]
        self.assertEqual(document["restart"], "always")
        self.assertEqual(
            document["devices"],
            [f"{device}:{device}:rw"],
        )
        self.assertEqual(document["ports"], ["198.18.30.22:8099:8099/tcp"])
        self.assertNotIn("privileged", document)
        self.assertFalse(document["volumes"][0]["bind"]["create_host_path"])
        self.assertEqual(
            document["volumes"][1],
            {
                "type": "bind",
                "source": device,
                "target": "/dev/ttyACM0",
                "read_only": False,
                "bind": {"create_host_path": False},
            },
        )
        graph = workflows.models(ROOT)
        self.assertEqual(
            graph["deploy.yml"]["jobs"]["zigbee2mqtt"]["needs"],
            ["selection", "automation"],
        )
        self.assertEqual(
            list(graph["guest-zigbee2mqtt.yml"]["jobs"]),
            ["deploy"],
        )
        steps = graph["guest-zigbee2mqtt.yml"]["jobs"]["deploy"]["steps"]
        self.assertEqual([step["env"]["PHASE"] for step in steps[8::3]],
                         ["infrastructure", "preparation", "zigbee2mqtt"])

    def test_broker_definition_owns_dns_check_and_the_backend_radio_alias(self):
        overlay = compiler.read(ROOT / "site.example.json")
        overlay["values"].update(
            {
                "addresses.automation_frontend": "198.18.40.121",
                "addresses.automation_backend": "198.18.30.121",
            }
        )
        overlay["guests"]["automation"] = {
            "config": {
                "app": {
                    "published_services": {"mqtt": {"hostname": "bus.example.invalid"}}
                }
            }
        }
        packets = self.packets(overlay)
        dns = self.stack(packets["dns"])
        expected = {
            "bus.example.invalid": "198.18.40.121",
            **{
                host: "198.18.40.33"
                for host in (
                    "hass.service-9.example.invalid",
                    "host.service-9.example.invalid",
                    "influx.service-9.example.invalid",
                    "matter.service-7.example.invalid",
                    "nas.service-7.example.invalid",
                    "nas.service-9.example.invalid",
                    "pihole1.service-7.example.invalid",
                    "pihole2.service-7.example.invalid",
                    "prox.service-9.example.invalid",
                    "proxmox.service-9.example.invalid",
                    "service-1.example.invalid",
                    "service-2.example.invalid",
                    "service-3.example.invalid",
                    "service-4.example.invalid",
                    "service-5.example.invalid",
                    "service-6.example.invalid",
                    "thread.service-7.example.invalid",
                    "zigbee1.service-7.example.invalid",
                    "zigbee2.service-7.example.invalid",
                )
            },
        }
        self.assertEqual(dns["dns_records"], expected)
        checks = json.loads(packets["dns"]["files"]["site.json"])["app"][
            "service_health_checks"
        ]["pihole"]
        self.assertEqual(
            next(
                check
                for check in checks
                if check["name"] == "DNS service record bus.example.invalid"
            )["argv"][-2:],
            ["bus.example.invalid", "198.18.40.121"],
        )
        radio = self.stack(packets["zigbee2mqtt"])
        self.assertEqual(
            radio["zigbee"]["mqtt_server"], "mqtt://bus.example.invalid:1883"
        )
        self.assertEqual(
            radio["services"]["zigbee2mqtt"]["extra_hosts"],
            {"bus.example.invalid": "198.18.30.121"},
        )
        self.assertNotIn(
            "FTLCONF_dns_hosts",
            render.compose(dns)["services"]["pihole"]["environment"],
        )
        dns["services"]["pihole"]["environment"][
            "FTLCONF_dns_hosts"
        ] = "198.18.40.99 old.example"
        with self.assertRaisesRegex(ValueError, "writable"):
            render.compose(dns)

    def test_both_sides_of_the_mqtt_connection_require_explicit_firewall_rules(self):
        for guest, direction in (("zigbee2mqtt", "out"), ("automation", "in")):
            overlay = compiler.read(ROOT / "site.example.json")
            profile = compiler.read(ROOT / "guests" / guest / "profile.json")
            overlay["guests"][guest] = {
                "config": {
                    "guest": {
                        "rules": [
                            row
                            for row in profile["config"]["guest"]["rules"]
                            if not (
                                row["direction"] == direction
                                and row.get("port") == "1883"
                            )
                        ]
                    }
                }
            }
            with self.subTest(guest=guest), self.assertRaisesRegex(
                ValueError, guest + " " + direction + " firewall"
            ):
                self.packets(overlay)

    def test_zigbee_cannot_replace_prepared_configuration_through_runtime_overrides(
        self,
    ):
        for override in (
            {"environment": {"ZIGBEE2MQTT_CONFIG_ADVANCED_NETWORK_KEY": "GENERATE"}},
            {"extra_mounts": [{"source": "/tmp/other", "target": "/app/data"}]},
            {"command": ["fresh-network"]},
            {"entrypoint": ["other"]},
            {"user": "other"},
        ):
            stack = self.stack(self.packets()["zigbee2mqtt"])
            stack["services"]["zigbee2mqtt"].update(override)
            with self.subTest(override=override), self.assertRaisesRegex(
                ValueError, "Preserve Zigbee"
            ):
                render.compose(stack)
