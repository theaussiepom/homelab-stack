"""Compiled guest definitions reach the real shared Ansible expressions safely.

All executable tasks below are local debug/assert/set_fact/stat actions. Package,
image, account and service mutations are never executed by these fixtures.
"""

import base64
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import yaml

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
spec = importlib.util.spec_from_file_location(
    "runtime_contract_compiler", FRAMEWORK / "blueprints/compile.py"
)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
sys.path.insert(0, str(FRAMEWORK / "proxmox/applications"))
import ansible_guest
import deployment_inputs
import private_io

ANSIBLE = str(Path(sys.executable).with_name("ansible-playbook"))
if not Path(ANSIBLE).is_file():
    ANSIBLE = shutil.which("ansible-playbook")
TASKS = FRAMEWORK / "proxmox/applications/ansible/tasks"


class CompositionIdentityTests(unittest.TestCase):
    def test_additional_private_data_binds_need_explicit_preparation(self):
        overlay = c.read(ROOT / "site.example.json")
        profile = c.read(ROOT / "guests/automation/profile.json")
        mounts = profile["stack"]["services"]["homeassistant"]["extra_mounts"]
        added = "/srv/homelab/data/additional-media"
        overlay["guests"]["automation"] = {
            "stack": {
                "services": {
                    "homeassistant": {
                        "extra_mounts": mounts
                        + [
                            {
                                "source": added,
                                "target": "/additional-media",
                                "read_only": True,
                            }
                        ]
                    }
                }
            }
        }
        with self.assertRaisesRegex(ValueError, "prepared path"):
            c.compile_stack(ROOT, overlay, [])
        overlay["guests"]["automation"]["config"] = {
            "app": {"required_paths": [{"path": added, "type": "directory"}]}
        }
        packet = c.compile_stack(ROOT, overlay, [])["automation"]
        required = json.loads(packet["files"]["site.json"])["app"]["required_paths"]
        self.assertIn({"path": added, "type": "directory"}, required)

    def test_colliding_guests_are_refused_before_any_packet_can_be_admitted(self):
        overlay = c.read(ROOT / "site.example.json")
        manifest = c.manifest(ROOT)
        blob = (
            struct.pack("!I", 11)
            + b"ssh-ed25519"
            + struct.pack("!I", 32)
            + b"\x01" * 32
        )
        overlay["common"]["ssh_public_keys"] = [
            "ssh-ed25519 " + base64.b64encode(blob).decode()
        ]
        for name in ("postgresql", "mariadb"):
            overlay["accepted"][name] = manifest["guests"][name]["prerequisites"]
            overlay["guests"][name] = {
                "config": {"guest": {"vmid": 880}, "app": {"vmid": 880}}
            }
        with self.assertRaisesRegex(ValueError, "identity"):
            c.compile_stack(ROOT, overlay, admit=True)


@unittest.skipUnless(ANSIBLE, "Runtime contract fixtures require local Ansible")
class RuntimeContractTests(unittest.TestCase):
    def test_changed_runtime_files_recreate_the_application_with_current_bind_mounts(
        self,
    ):
        tasks = yaml.safe_load((TASKS / "compose.yml").read_text())
        source = next(t for t in tasks if t["name"] == "Start exactly this guest stack")
        install = next(
            t
            for t in tasks
            if t["name"]
            == "Install only the selected service-readable foundation files"
        )
        for kind in ("identity", "ingress", "db-tools"):
            for changed in (True, False):
                with (
                    self.subTest(guest=kind, runtime_changed=changed),
                    tempfile.TemporaryDirectory() as directory,
                ):
                    root = Path(directory)
                    (root / "rendered").mkdir()
                    (root / "runtime").mkdir()
                    (root / "rendered/config").write_text("current")
                    prior = root / "runtime/config"
                    prior.write_text("before" if changed else "current")
                    prior.chmod(0o600)
                    copy_task = copy.deepcopy(install)
                    copy_task["ansible.builtin.copy"]["dest"] = str(
                        root / "runtime/{{ item.path }}"
                    )
                    task = {
                        "ansible.builtin.debug": {
                            "msg": source["ansible.builtin.command"]["argv"]
                        }
                    }
                    result = self.run_tasks(
                        root,
                        {
                            "app": {
                                "kind": kind,
                                "start_services": True,
                                "render_dir": str(root / "rendered"),
                            },
                            "stack": {"foundation": {}},
                            "foundation_runtime_files": [
                                {
                                    "path": "config",
                                    "uid": os.getuid(),
                                    "gid": os.getgid(),
                                    "mode": "0600",
                                }
                            ],
                        },
                        [copy_task, task],
                    )
                    self.assertEqual(
                        result.returncode, 0, result.stdout + result.stderr
                    )
                    self.assertEqual(
                        "--force-recreate" in result.stdout, changed, result.stdout
                    )
                    self.assertEqual(prior.read_text(), "current")

    def run_tasks(self, root, variables, tasks):
        play = root / "local-contract.json"
        play.write_text(
            json.dumps(
                [
                    {
                        "hosts": "localhost",
                        "connection": "local",
                        "gather_facts": False,
                        "vars": variables,
                        "tasks": tasks,
                    }
                ]
            )
        )
        return subprocess.run(
            [ANSIBLE, "-i", "localhost,", str(play)],
            capture_output=True,
            text=True,
            timeout=30,
            env=dict(
                os.environ,
                ANSIBLE_LOCAL_TEMP=str(root / "ansible-local"),
                ANSIBLE_REMOTE_TEMP=str(root / "ansible-remote"),
            ),
        )

    def packet(self, name):
        return c.compile_stack(ROOT, c.read(ROOT / "site.example.json"), [])[name]

    def phase_variables(self, root, name, phase, *, dhcp_endpoint=None):
        packet = self.packet(name)
        cfg = json.loads(packet["files"]["site.json"])
        runtime = json.loads(packet["files"]["stack.json"])
        cfg["app"]["stack_config"] = str(root / "stack.json")
        private_io.write_new(root / "stack.json", private_io.encoded(runtime))
        operation = root / "attempt"
        operation.mkdir(mode=0o700)

        def execution(command, environment, log):
            private_io.write_new(log, b"fixture : ok=1 changed=0\n")

        def pve_read(selected, path):
            self.assertIs(selected, cfg)
            prefix = f"/nodes/{cfg['site']['node']}/lxc/{cfg['guest']['vmid']}"
            if path == prefix + "/config":
                observed = {"hostname": cfg["guest"]["hostname"], "protection": 1, "unprivileged": 1}
                for index, nic in enumerate(cfg["guest"]["interfaces"]):
                    fields = f"name=eth{index},bridge={nic['bridge']},hwaddr={nic['mac']},ip={nic['ipv4']}"
                    if nic["vlan"] is not None:
                        fields += f",tag={nic['vlan']}"
                    observed[f"net{index}"] = fields
                return observed
            self.assertEqual(path, prefix + "/interfaces")
            return [
                {"hwaddr": nic["mac"], "inet": (
                    dhcp_endpoint or nic["ipv4_endpoint"]
                    if nic["ipv4"] == "dhcp" else nic["ipv4"]
                )}
                for nic in cfg["guest"]["interfaces"]
            ]

        with (
            patch.object(deployment_inputs, "binding", return_value={"reviewed": True}),
            patch.object(ansible_guest.proxmox_guest, "guest_trust"),
            patch.object(ansible_guest.proxmox_guest, "api_get", side_effect=pve_read) as provider_read,
            patch.object(ansible_guest, "quiet", side_effect=execution),
        ):
            ansible_guest.run_phase(
                cfg, root / "site.json", root, operation, {"reviewed": True}, phase
            )
        self.assertEqual(provider_read.call_count, 2 if name == "dns" else 0)
        variables = json.loads((operation / phase / "variables.json").read_text())
        return dict(variables, stack=runtime)

    def test_changed_dhcp_prefix_refuses_before_the_shared_runtime_task(self):
        """The compiled DNS guest exercises real admission against synthetic PVE reads."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "endpoint differs"):
                self.phase_variables(root, "dns", "unbound", dhcp_endpoint="198.18.40.2/25")
            self.assertEqual(list((root / "attempt").iterdir()), [])

    def test_compiled_runtime_shapes_reach_the_shared_image_task(self):
        source = next(
            t
            for t in yaml.safe_load((TASKS / "compose.yml").read_text())
            if t["name"] == "Load preserved custom images by verified archive"
        )
        for name, phase in [
            ("pegaprox", "pegaprox"),
            ("automation", "mqtt"),
            ("automation", "homeassistant"),
            ("automation", "node_red"),
            ("dns", "unbound"),
            ("identity", "authentik"),
        ]:
            with (
                self.subTest(guest=name, phase=phase),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                variables = self.phase_variables(root, name, phase)
                task = copy.deepcopy(source)
                task.pop("ansible.builtin.include_tasks")
                task["ansible.builtin.debug"] = {
                    "msg": "IMAGE_INPUT={{ image_input.key }}"
                }
                result = self.run_tasks(root, variables, [task])
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                if name == "automation":
                    if phase in {"homeassistant", "node_red"}:
                        self.assertIn("IMAGE_INPUT=" + phase, result.stdout)
                    else:
                        self.assertNotIn("IMAGE_INPUT=", result.stdout)
                    for other in {"mqtt", "homeassistant", "node_red"} - {phase}:
                        self.assertNotIn("IMAGE_INPUT=" + other, result.stdout)

    def test_each_required_startup_file_is_checked_before_runtime_changes(self):
        source = yaml.safe_load((TASKS / "guest-ready.yml").read_text())[1:3]
        for missing in ("ha-startup/mdns-route.sh", "node-red/config/settings.js"):
            with (
                self.subTest(missing=missing),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                app = json.loads(self.packet("automation")["files"]["site.json"])["app"]
                for row in app["required_paths"]:
                    relative = row["path"].removeprefix("/srv/homelab/data/")
                    path = root / "guest-data" / relative
                    row["path"] = str(path)
                    if relative == missing:
                        continue
                    if row["type"] == "directory":
                        path.mkdir(parents=True, exist_ok=True)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text("synthetic prepared file")
                result = self.run_tasks(root, {"app": app}, source)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(
                    "Complete separate data/configuration preparation first",
                    result.stdout,
                )
                absent = root / "guest-data" / missing
                absent.parent.mkdir(parents=True, exist_ok=True)
                absent.write_text("synthetic prepared startup file")
                result = self.run_tasks(root, {"app": app}, source)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_new_repository_indexes_are_refreshed_before_exact_packages(self):
        # Model the external APT contract: changing repositories invalidates the
        # available index; an explicit cache refresh must precede installation.
        def package_actions(path):
            result = []
            for task in yaml.safe_load(path.read_text()):
                if "ansible.builtin.import_tasks" in task:
                    result.extend(
                        package_actions(
                            path.parent / task["ansible.builtin.import_tasks"]
                        )
                    )
                elif "ansible.builtin.copy" in task and "sources.list.d" in task[
                    "ansible.builtin.copy"
                ].get("dest", ""):
                    result.append(
                        {
                            "name": task["name"],
                            "ansible.builtin.set_fact": {
                                "repository_index_ready": False
                            },
                        }
                    )
                elif "ansible.builtin.apt" in task:
                    args = task["ansible.builtin.apt"]
                    if args.get("update_cache") is True:
                        result.append(
                            {
                                "name": task["name"],
                                "ansible.builtin.set_fact": {
                                    "repository_index_ready": True
                                },
                            }
                        )
                    if "name" in args:
                        result.append(
                            {
                                "name": task["name"],
                                "ansible.builtin.assert": {
                                    "that": "repository_index_ready | default(false)",
                                    "fail_msg": "Exact packages require refreshed repository indexes",
                                },
                            }
                        )
            return result

        with tempfile.TemporaryDirectory() as directory:
            result = self.run_tasks(
                Path(directory), {}, package_actions(TASKS / "packages-install.yml")
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
