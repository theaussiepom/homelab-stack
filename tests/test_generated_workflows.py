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
            "db-tools": ["infrastructure", "preparation", "pgadmin"],
            "automation": ["infrastructure", "preparation", "mqtt", "homeassistant", "node_red"],
            "bitwarden": ["infrastructure", "preparation", "bitwarden"],
            "pegaprox": ["infrastructure", "preparation", "pegaprox"],
            "zigbee2mqtt": ["infrastructure", "preparation", "zigbee2mqtt"],
        }
        labels = {"infrastructure": "Update container", "preparation": "Prepare service",
                  "unbound": "Deploy resolver", "pihole": "Deploy DNS", "mqtt": "Deploy MQTT",
                  "homeassistant": "Deploy Home Assistant", "node_red": "Deploy Node-RED"}
        setup_names = ["Check readiness", "Get settings", "Choose services", "Get services", "Choose tools", "Get tools"]
        directory = ROOT / ".github/workflows"
        framework = load(FRAMEWORK / ".github/workflows/guest-phase.yml")
        recipe = framework["jobs"]["run"]
        self.assertEqual({p.stem.removeprefix("guest-") for p in directory.glob("guest-*.yml")}, set(phases))
        total_jobs = total_phases = total_phase_commands = 0
        for guest, expected_phases in phases.items():
            with self.subTest(guest=guest):
                workflow = load(directory / ("guest-" + guest + ".yml"))
                self.assertEqual(list(workflow["jobs"]), ["deploy"])
                self.assertEqual(workflow["defaults"], framework["defaults"])
                self.assertEqual(workflow["defaults"], {"run": {"shell": "bash"}})
                self.assertEqual(workflow["on"]["workflow_call"]["inputs"]["disabled"]["default"], "[]")
                job = workflow["jobs"]["deploy"]
                self.assertEqual(set(job), {"name", "if", "environment", "runs-on", "timeout-minutes", "env", "steps"})
                self.assertEqual(job["name"], "Deploy")
                self.assertEqual(job["if"], "github.event.repository.private == true && github.event_name == 'push' && github.ref == 'refs/heads/main' && !contains(fromJSON(inputs.disabled || '[]'), '" + guest + "')")
                for key in ("environment", "runs-on", "timeout-minutes", "env"):
                    self.assertEqual(job[key], recipe[key])
                self.assertEqual(job["timeout-minutes"], "45")  # Whole-guest cap.
                self.assertEqual(len(job["steps"]), 6 + 3 * len(expected_phases))
                self.assertEqual([step["id"] for step in job["steps"] if "id" in step], ["stack", "framework"])
                for step in job["steps"]:
                    self.assertNotIn("if", step)
                    self.assertNotIn("continue-on-error", step)
                for before, after, name in zip(recipe["steps"][:6], job["steps"][:6], setup_names):
                    self.assertEqual(set(after), set(before) | {"name"})
                    self.assertEqual(after["name"], name)
                    for key in set(before) - {"name"}:
                        self.assertEqual(after[key], before[key])
                for index, phase in enumerate(expected_phases):
                    triple = job["steps"][6 + 3 * index:9 + 3 * index]
                    display = labels.get(phase, "Deploy service")
                    self.assertEqual([step["name"] for step in triple], ["Check inputs", "Load credentials", display])
                    for before, after in zip(recipe["steps"][6:], triple):
                        self.assertEqual(set(after), set(before))
                        self.assertEqual(after["run"], before["run"])
                        self.assertEqual(set(after["env"]), set(before["env"]))
                        self.assertEqual(after["env"]["GUEST"], guest)
                        self.assertEqual(after["env"]["PHASE"], phase)
                        total_phase_commands += 1
                    self.assertEqual(triple[0]["env"]["DISABLED"], "${{ inputs.disabled }}")
                    for secret in ("APPLICATION_SSH_KEY", "PROXMOX_APP_TOKEN"):
                        self.assertEqual(triple[1]["env"][secret], "${{ secrets." + secret + " }}")
                    total_phases += 1
                total_jobs += 1
        self.assertEqual((total_jobs, total_phases, total_phase_commands), (11, 36, 108))

    def test_named_secrets_remain_guest_scoped_inside_native_job_steps(self):
        common = {"APPLICATION_SSH_KEY": "true", "PROXMOX_APP_TOKEN": "true"}
        applications = {
            "automation": {"AUTOMATION_NODE_RED_API_TOKEN": "true"},
            "identity": {
                "FOUNDATION_AUTHENTIK_POSTGRES_PASSWORD": "true",
                "FOUNDATION_AUTHENTIK_SECRET_KEY": "true",
                "FOUNDATION_AUTHENTIK_SMTP_PASSWORD": "false",
            },
            "db-tools": {"FOUNDATION_PGADMIN_OAUTH_SECRET": "true"},
            "ingress": {"FOUNDATION_CLOUDFLARE_DNS_TOKEN": "true"},
        }
        generic = {**common, **{name: "false" for row in applications.values() for name in row}}
        available = {name: "invented-" + name for name in generic}

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
        # The uncalled anchor keeps the same explicit immutable selection contract.
        self.assertEqual(set(phase["jobs"]["run"]["secrets"]), set(generic))
        for name, expression in phase["jobs"]["run"]["secrets"].items():
            self.assertEqual(expression, "${{ secrets." + name + " }}")
        recipe = framework["jobs"]["run"]
        reconcile = recipe["steps"][-1]
        owners = {name: guest for guest, row in applications.items() for name in row}
        bindings = {}
        for variable, expression in reconcile["env"].items():
            if "secrets." not in expression:
                continue
            match = re.fullmatch(r"\$\{\{ inputs\.guest == '([a-z-]+)' && secrets\.([A-Z_]+) \|\| '' \}\}", expression)
            self.assertIsNotNone(match, expression)
            owner, name = match.groups()
            self.assertEqual(owner, owners[name])
            bindings[variable] = (owner, name)
        self.assertEqual(sorted(name for _, name in bindings.values()), sorted(owners))
        declared = json.loads((ROOT / "stack.json").read_text())["guests"]
        for guest in declared:
            with self.subTest(guest=guest):
                selected = {**common, **applications.get(guest, {})}
                workflow = load(directory / ("guest-" + guest + ".yml"))
                self.assertEqual(declarations(workflow), selected)
                self.assertEqual(workflow["permissions"], {"contents": "read"})
                caller = deploy["jobs"][guest]
                self.assertEqual(caller["uses"], "./.github/workflows/guest-" + guest + ".yml")
                self.assertEqual(set(caller["secrets"]), set(selected))
                for name, expression in caller["secrets"].items():
                    self.assertEqual(expression, "${{ secrets." + name + " }}")
                for job in workflow["jobs"].values():
                    self.assertNotIn("uses", job)
                    self.assertNotIn("secrets", job)
                    self.assertEqual(set(re.findall(r"secrets\.([A-Z_]+)", json.dumps(job))), set(selected))
                    self.assertEqual(set(job["env"]), {"HOMELAB_DEPLOYMENT_WORKFLOW"})
                    self.assertEqual(list(workflow["jobs"]), ["deploy"])
                    for index, step in enumerate(job["steps"]):
                        references = set(re.findall(r"secrets\.([A-Z_]+)", json.dumps(step)))
                        role = (index - 6) % 3
                        expected = set() if index < 6 or role == 0 else set(common) if role == 1 else set(applications.get(guest, {}))
                        self.assertEqual(references, expected)
                    for deployment in job["steps"][8::3]:
                        for variable, (owner, name) in bindings.items():
                            secret_expression = "secrets." + name if owner == guest else "''"
                            expected = "${{ '" + guest + "' == '" + owner + "' && " + secret_expression + " || '' }}"
                            self.assertEqual(deployment["env"][variable], expected)
                            observed = re.fullmatch(r"\$\{\{ '([a-z0-9-]+)' == '([a-z-]+)' && (?:secrets\.([A-Z_]+)|'') \|\| '' \}\}", deployment["env"][variable])
                            self.assertIsNotNone(observed)
                            for smtp_present in (True, False):
                                supplied = {key: available[key] for key in selected if smtp_present or key != "FOUNDATION_AUTHENTIK_SMTP_PASSWORD"}
                                inherited = {key: supplied.get(key, "") for key in generic}
                                old_value = inherited[name] if guest == owner else ""
                                new_value = supplied.get(observed[3], "") if observed[1] == observed[2] and observed[3] else ""
                                self.assertEqual(new_value, old_value)

    def test_actual_selection_preflight_validates_before_any_guest_can_be_skipped(self):
        deploy = yaml.safe_load((ROOT / ".github/workflows/deploy.yml").read_text())
        selection = deploy["jobs"]["selection"]
        self.assertIn("private == true", selection["if"])
        self.assertEqual(selection["runs-on"], "ubuntu-24.04")
        self.assertNotIn("secrets", selection)
        step = selection["steps"][0]
        dependencies = json.loads(step["env"]["DEPENDENCIES"])
        declared = json.loads((ROOT / "stack.json").read_text())["guests"]
        self.assertEqual(
            dependencies, {name: row["depends_on"] for name, row in declared.items()}
        )
        for name, row in declared.items():
            self.assertEqual(
                deploy["jobs"][name]["needs"], ["selection", *row["depends_on"]]
            )
        for disabled, accepted in [
            ("", True),
            ("[]", True),
            ('["zigbee2mqtt"]', True),
            (json.dumps(list(declared)), True),
            ('["dns"]', False),
            ('["identity"]', False),
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
                    ),
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                self.assertEqual(result.returncode == 0, accepted, result.stderr)
