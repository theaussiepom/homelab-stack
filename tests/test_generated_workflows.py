"""CI uses the same generator check as local development; it never repairs drift."""

import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
GENERATOR = FRAMEWORK / "blueprints/workflows.py"


def generate(stack, check=False):
    return subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--stack",
            str(stack),
            *(["--check"] if check else []),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )


class GeneratedWorkflowTests(unittest.TestCase):
    def test_checked_in_workflows_match_the_selected_catalogue_and_composition(self):
        result = generate(ROOT, check=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_check_detects_guest_and_phase_drift_without_writing_and_repairs_it(self):
        for changed in ("guest-mariadb.yml", "phase.yml"):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                workflows = root / ".github/workflows"
                workflows.mkdir(parents=True)
                shutil.copyfile(ROOT / "stack.json", root / "stack.json")
                for source in (ROOT / ".github/workflows").glob("*.yml"):
                    shutil.copyfile(source, workflows / source.name)
                profile = root / "guests/zigbee2mqtt/profile.yaml"
                profile.parent.mkdir(parents=True)
                shutil.copyfile(ROOT / "guests/zigbee2mqtt/profile.yaml", profile)
                # Generation owns phase structure, preserving its deliberate pin.
                phase = (workflows / "phase.yml").read_bytes()
                ci_names = ("validate-stack.yml", "review-pr-dependencies.yml", "scan-python-security.yml")
                ci = {name: (workflows / name).read_bytes() for name in ci_names}
                path = workflows / changed
                if changed == "phase.yml":
                    document = yaml.safe_load(path.read_text())
                    del document["on"]["workflow_call"]["secrets"]["APPLICATION_SSH_KEY"]
                    del document["jobs"]["run"]["secrets"]["APPLICATION_SSH_KEY"]
                    path.write_text(yaml.safe_dump(document, sort_keys=False))
                else:
                    path.write_bytes(path.read_bytes() + b"\n# unintended manual edit\n")
                before = {p.name: p.read_bytes() for p in workflows.iterdir()}
                result = generate(root, check=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(changed, result.stdout + result.stderr)
                self.assertEqual(
                    before, {p.name: p.read_bytes() for p in workflows.iterdir()}
                )
                result = generate(root)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(generate(root, check=True).returncode, 0)
                self.assertEqual((workflows / "phase.yml").read_bytes(), phase)
                self.assertEqual({name: (workflows / name).read_bytes() for name in ci_names}, ci)

    def test_one_guest_job_preserves_all_ordered_phase_commands_and_policies(self):
        def load(path):
            return yaml.load(path.read_text(), Loader=yaml.BaseLoader)

        phases = {
            "dns": ["infrastructure", "preparation", "unbound", "pihole"],
            "ingress": ["infrastructure", "preparation", "traefik"],
            "postgresql": ["infrastructure", "preparation", "postgresql"],
            "mariadb": ["infrastructure", "preparation", "mariadb"],
            "influxdb": ["infrastructure", "preparation", "influxdb"],
            "identity": ["infrastructure", "preparation", "authentik"],
            "db-tools": ["infrastructure", "preparation", "cloudbeaver"],
            "automation": ["infrastructure", "preparation", "homeassistant", "node_red"],
            "bitwarden": ["infrastructure", "preparation", "bitwarden"],
            "pegaprox": ["infrastructure", "preparation", "pegaprox"],
            "zigbee2mqtt": ["infrastructure", "preparation", "zigbee2mqtt", "winet"],
            "monitoring": ["infrastructure", "preparation", "zabbix"],
            "music": ["infrastructure", "preparation", "music_assistant"],
            "mqtt": ["infrastructure", "preparation", "mqtt", "mqtt_explorer"],
        }
        labels = {"infrastructure": "Infrastructure", "preparation": "Prepare",
                  "unbound": "Unbound", "pihole": "Pi-hole", "traefik": "Traefik",
                  "postgresql": "PostgreSQL", "mariadb": "MariaDB", "influxdb": "InfluxDB",
                  "authentik": "Authentik", "cloudbeaver": "CloudBeaver", "homeassistant": "Home Assistant",
                  "node_red": "Node-RED", "bitwarden": "Bitwarden", "pegaprox": "PegaProx",
                  "zigbee2mqtt": "Zigbee2MQTT", "winet": "WiNet", "zabbix": "Zabbix",
                  "music_assistant": "Music Assistant", "mqtt": "MQTT", "mqtt_explorer": "MQTT Explorer", "zabbix-agent": "Zabbix agent"}
        directory = ROOT / ".github/workflows"
        framework = load(FRAMEWORK / ".github/workflows/guest-phase.yml")
        recipe = framework["jobs"]["run"]
        pin = load(directory / "phase.yml")["jobs"]["run"]["uses"]
        repository, revision = pin.split("/.github/workflows/guest-phase.yml@")
        self.assertEqual({p.stem.removeprefix("guest-") for p in directory.glob("guest-*.yml")}, set(phases))
        total_phases = 0
        for guest, applications in phases.items():
            expected_phases = [*applications, "zabbix-agent"]
            with self.subTest(guest=guest):
                workflow = load(directory / ("guest-" + guest + ".yml"))
                self.assertEqual(list(workflow["jobs"]), ["deploy"])
                self.assertEqual(workflow["defaults"], framework["defaults"])
                self.assertEqual(workflow["on"]["workflow_call"]["inputs"]["disabled"]["default"], "[]")
                job = workflow["jobs"]["deploy"]
                self.assertEqual(job["name"], workflow["name"])
                self.assertEqual(set(job), {"name", "if", "environment", "runs-on", "timeout-minutes", "env", "steps"})
                self.assertEqual(job["if"], "github.event.repository.private == true && github.event_name == 'push' && github.ref == 'refs/heads/main' && !contains(fromJSON(inputs.disabled || '[]'), '" + guest + "')")
                for key in ("environment", "runs-on", "env"):
                    self.assertEqual(job[key], recipe[key])
                self.assertEqual(recipe["timeout-minutes"], "45")
                self.assertEqual(int(job["timeout-minutes"]), 45 * len(expected_phases))
                self.assertEqual(len(job["steps"]), 1 + len(expected_phases))
                self.assertEqual(job["steps"][0], {"name": "Setup", "uses": repository + "/.github/actions/guest-setup@" + revision, "timeout-minutes": "45"})
                for step, phase in zip(job["steps"][1:], expected_phases):
                    self.assertEqual(set(step), {"name", "uses", "timeout-minutes", "with"})
                    self.assertEqual(step["name"], labels[phase])
                    self.assertEqual(step["uses"], repository + "/.github/actions/guest-phase@" + revision)
                    self.assertEqual(step["timeout-minutes"], "45")
                    self.assertEqual({key: step["with"][key] for key in ("guest", "phase", "disabled")},
                                     {"guest": guest, "phase": phase, "disabled": "${{ inputs.disabled }}"})
                    self.assertNotIn("continue-on-error", step)
                    self.assertNotIn("if", step)
                total_phases += len(expected_phases)
        self.assertEqual(total_phases, 60)
        # Consolidation is presentation only: run bytes and each separate environment
        # remain the original guarded leaf. The guard/compiler never receives secrets.
        setup = load(FRAMEWORK / ".github/actions/guest-setup/action.yml")["runs"]["steps"]
        self.assertEqual(len(setup), 7)
        self.assertEqual([s['name'] for s in setup if s['name'] == 'Prepare config'], ['Prepare config'])
        self.assertIn('framework-source/requirements.lock.txt', setup[-1]['run'])
        self.assertIn('--require-hashes --no-deps', setup[-1]['run'])
        for original, shared in zip(recipe["steps"][:7], setup):
            for key in set(original) - {"name"}:
                self.assertEqual(shared[key], original[key])
            self.assertNotIn("env", shared)
        phase_steps = load(FRAMEWORK / ".github/actions/guest-phase/action.yml")["runs"]["steps"]
        self.assertEqual([s["name"] for s in phase_steps], ["Check readiness", "Check inputs", "Load credentials", "Deploy"])
        for original, shared in zip([recipe["steps"][0], *recipe["steps"][7:]], phase_steps):
            self.assertEqual(shared["run"], original["run"])
            self.assertEqual(shared["shell"], "bash")
            expected = {key: value.replace("secrets.", "inputs.") for key, value in original.get("env", {}).items()}
            self.assertEqual(shared.get("env", {}), expected)
        self.assertEqual(set(phase_steps[1]["env"]), {"GUEST", "PHASE", "DISABLED"})
        self.assertNotIn("APPLICATION_SSH_KEY", phase_steps[1]["env"])
        self.assertNotIn("PROXMOX_APP_TOKEN", phase_steps[3]["env"])

    def test_named_secrets_remain_guest_scoped_inside_shared_phase_steps(self):
        common = {"APPLICATION_SSH_KEY": "true", "PROXMOX_APP_TOKEN": "true"}
        applications = {
            "automation": {"AUTOMATION_NODE_RED_API_TOKEN": "true"},
            "identity": {"FOUNDATION_AUTHENTIK_POSTGRES_PASSWORD": "true",
                         "FOUNDATION_AUTHENTIK_SECRET_KEY": "true", "FOUNDATION_AUTHENTIK_SMTP_PASSWORD": "false"},
            "db-tools": {"FOUNDATION_PGADMIN_OAUTH_SECRET": "true"},
            "ingress": {"FOUNDATION_CLOUDFLARE_DNS_TOKEN": "true"},
        }
        generic = {**common, **{name: "false" for row in applications.values() for name in row}}
        def load(path):
            return yaml.load(path.read_text(), Loader=yaml.BaseLoader)
        def declarations(document):
            return {name: row["required"] for name, row in document["on"]["workflow_call"]["secrets"].items()}
        directory = ROOT / ".github/workflows"
        deploy = load(directory / "deploy.yml")
        phase = load(directory / "phase.yml")
        framework = load(FRAMEWORK / ".github/workflows/guest-phase.yml")
        for document in (deploy, phase, framework):
            self.assertEqual(declarations(document), generic)
            self.assertEqual(document["permissions"], {"contents": "read"})
        self.assertNotIn("secrets", deploy["jobs"]["selection"])
        self.assertEqual(phase["jobs"]["run"]["secrets"], {name: "${{ secrets." + name + " }}" for name in generic})
        shared = load(FRAMEWORK / ".github/actions/guest-phase/action.yml")
        self.assertEqual({name: shared["inputs"][name]["required"] for name in generic}, generic)
        self.assertNotIn("secrets.", json.dumps(shared))
        owner_by_secret = {name: guest for guest, row in applications.items() for name in row}
        credential_step, deployment_step = shared["runs"]["steps"][2:]
        self.assertEqual(set(credential_step["env"]), {"GUEST", "PHASE", *common})
        for name in common:
            self.assertEqual(credential_step["env"][name], "${{ inputs." + name + " }}")
        application_expressions = {key: value for key, value in deployment_step["env"].items() if key not in {"GUEST", "PHASE"}}
        for value in application_expressions.values():
            match = re.fullmatch(r"\$\{\{ inputs\.guest == '([a-z-]+)' && inputs\.([A-Z_]+) \|\| '' \}\}", value)
            self.assertIsNotNone(match, value)
            self.assertEqual(owner_by_secret[match[2]], match[1])
        declared = json.loads((ROOT / "stack.json").read_text())["guests"]
        for guest in declared:
            selected = {**common, **applications.get(guest, {})}
            workflow = load(directory / ("guest-" + guest + ".yml"))
            self.assertEqual(declarations(workflow), selected)
            caller = deploy["jobs"][guest]
            self.assertEqual(caller["secrets"], {name: "${{ secrets." + name + " }}" for name in selected})
            job = workflow["jobs"]["deploy"]
            self.assertNotIn("secrets", job)
            self.assertEqual(set(job["env"]), {"HOMELAB_DEPLOYMENT_WORKFLOW"})
            self.assertNotIn("secrets.", json.dumps(job["steps"][0]))
            for step in job["steps"][1:]:
                self.assertNotIn("env", step)
                self.assertEqual(set(step["with"]), {"guest", "phase", "disabled", *selected})
                self.assertEqual(set(re.findall(r"secrets\.([A-Z_]+)", json.dumps(step))), set(selected))
                for name in selected:
                    self.assertEqual(step["with"][name], "${{ secrets." + name + " }}")
                # An absent optional SMTP input stays empty, and unowned inputs never
                # become available to the guard/compiler or another guest's deploy.
                for smtp_present in (True, False):
                    supplied = {name: "invented-" + name for name in selected if smtp_present or name != "FOUNDATION_AUTHENTIK_SMTP_PASSWORD"}
                    for value in application_expressions.values():
                        match = re.fullmatch(r"\$\{\{ inputs\.guest == '([a-z-]+)' && inputs\.([A-Z_]+) \|\| '' \}\}", value)
                        actual = supplied.get(match[2], "") if guest == match[1] else ""
                        self.assertEqual(actual, supplied.get(match[2], "") if owner_by_secret[match[2]] == guest else "")

    def test_actual_selection_preflight_validates_before_any_guest_can_be_skipped(self):
        deploy = yaml.safe_load((ROOT / ".github/workflows/deploy.yml").read_text())
        selection = deploy["jobs"]["selection"]
        self.assertIn("private == true", selection["if"])
        self.assertEqual(selection["runs-on"], "ubuntu-24.04")
        self.assertNotIn("secrets", selection)
        step = next(s for s in selection["steps"] if s.get("id") == "selection")
        preparation = [s for s in selection['steps'] if s.get('name') == 'Prepare config']
        self.assertEqual(len(preparation), 1)
        self.assertLess(selection['steps'].index(preparation[0]), selection['steps'].index(step))
        self.assertNotIn('secrets.', json.dumps(preparation[0]))
        self.assertIn('framework-source/requirements.lock.txt', preparation[0]['run'])
        self.assertIn('--require-hashes --no-deps', preparation[0]['run'])
        self.assertEqual(selection["steps"][0]["uses"], "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1")
        dependencies = json.loads(step["env"]["DEPENDENCIES"])
        declared = json.loads((ROOT / "stack.json").read_text())["guests"]
        self.assertEqual(
            dependencies, {name: row["depends_on"] for name, row in declared.items()}
        )
        for name, row in declared.items():
            self.assertEqual(
                deploy["jobs"][name]["needs"], ["selection", *row["depends_on"]]
            )
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        selection_root = Path(directory.name)
        (selection_root / 'site.yaml').write_text((ROOT / 'site.example.yaml').read_text())
        parser = selection_root / 'framework-source/blueprints/authored_config.py'
        parser.parent.mkdir(parents=True)
        shutil.copyfile(FRAMEWORK / 'blueprints/authored_config.py', parser)
        for disabled, accepted in [
            ("", True),
            ("[]", True),
            ('["zigbee2mqtt"]', True),
            ('["automation"]', True),
            (json.dumps(list(declared)), True),
            ('["dns"]', False),
            ('["ingress"]', False),
            ('["identity"]', True),
            ('["identity","db-tools"]', True),
            ('["identity","automation"]', True),
            ('["ingress","identity","db-tools","bitwarden","monitoring","music"]', True),
            ('["mariadb"]', False),
            ('["influxdb"]', False),
            ('["mqtt"]', False),
            ('["not-a-guest"]', False),
            ('["zigbee2mqtt", "zigbee2mqtt"]', False),
            ('[1]', False),
            ('{}', False),
            ('null', False),
            ('invalid-json', False),
        ]:
            with self.subTest(disabled=disabled):
                result = subprocess.run(
                    ["sh", "-eu", "-c", step["run"]],
                    env=dict(
                        os.environ,
                        DISABLED=disabled,
                        DEPENDENCIES=step["env"]["DEPENDENCIES"],
                        GITHUB_OUTPUT=os.devnull,
                        # CI's preceding Prepare config step supplies this exact
                        # interpreter role; this test environment already uses
                        # the selected framework's hash-pinned requirements.
                        HOMELAB_CONFIG_PYTHON=sys.executable,
                    ),
                    cwd=selection_root,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                self.assertEqual(result.returncode == 0, accepted, result.stderr)
