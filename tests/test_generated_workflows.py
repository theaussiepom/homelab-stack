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

    def test_named_secrets_survive_reusable_edges_and_remain_guest_scoped(self):
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

        def forward(job, names, supplied):
            self.assertEqual(set(job["secrets"]), set(names))
            result = {}
            for name, expression in job["secrets"].items():
                self.assertEqual(expression, "${{ secrets." + name + " }}")
                result[name] = supplied.get(name, "")
            return result

        directory = ROOT / ".github/workflows"
        deploy = load(directory / "deploy.yml")
        phase = load(directory / "phase.yml")
        framework = load(FRAMEWORK / ".github/workflows/guest-phase.yml")
        self.assertEqual(declarations(deploy), generic)
        self.assertEqual(declarations(phase), generic)
        self.assertEqual(declarations(framework), generic)
        self.assertEqual(deploy["permissions"], {"contents": "read"})
        self.assertNotIn("secrets", deploy["jobs"]["selection"])
        final = framework["jobs"]["run"]
        self.assertEqual(final["environment"], "${{ inputs.environment_name }}")
        reconcile = next(step for step in final["steps"] if step.get("name") == "Reconcile this phase")
        owners = {name: guest for guest, row in applications.items() for name in row}
        application_bindings = []
        for expression in reconcile["env"].values():
            if "secrets." not in expression:
                continue
            match = re.fullmatch(r"\$\{\{ inputs\.guest == '([a-z-]+)' && secrets\.([A-Z_]+) \|\| '' \}\}", expression)
            self.assertIsNotNone(match, expression)
            owner, name = match.groups()
            self.assertEqual(owner, owners[name])
            application_bindings.append((owner, name))
        self.assertEqual(sorted(name for _, name in application_bindings), sorted(owners))
        declared = json.loads((ROOT / "stack.json").read_text())["guests"]
        for guest in declared:
            with self.subTest(guest=guest):
                selected = {**common, **applications.get(guest, {})}
                workflow = load(directory / ("guest-" + guest + ".yml"))
                self.assertEqual(declarations(workflow), selected)
                self.assertEqual(workflow["permissions"], {"contents": "read"})
                caller = deploy["jobs"][guest]
                self.assertEqual(caller["uses"], "./.github/workflows/guest-" + guest + ".yml")
                guest_values = forward(caller, selected, available)
                for job in workflow["jobs"].values():
                    self.assertEqual(job["uses"], "./.github/workflows/phase.yml")
                    self.assertEqual(job["with"]["guest"], guest)
                    phase_values = forward(job, selected, guest_values)
                    final_values = forward(phase["jobs"]["run"], generic, phase_values)
                    self.assertEqual(final_values, {name: available[name] if name in selected else "" for name in generic})
                    for owner, name in application_bindings:
                        actual = final_values.get(name, "") if guest == owner else ""
                        self.assertEqual(actual, available[name] if name in applications.get(guest, {}) else "")
                    # Optional SMTP may be absent throughout the whole chain.
                    without_smtp = dict(available)
                    without_smtp.pop("FOUNDATION_AUTHENTIK_SMTP_PASSWORD")
                    sparse = forward(caller, selected, without_smtp)
                    sparse = forward(job, selected, sparse)
                    sparse = forward(phase["jobs"]["run"], generic, sparse)
                    self.assertEqual(sparse["FOUNDATION_AUTHENTIK_SMTP_PASSWORD"], "")

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
