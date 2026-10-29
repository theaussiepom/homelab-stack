"""Real compiled packets materialize privately without target execution."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
APPS = FRAMEWORK / "proxmox/applications"
sys.path.insert(0, str(APPS))
import deployment_inputs as inputs
from secret_contract import BINDINGS


class InputMaterializationTests(unittest.TestCase):
    def test_compiled_foundation_packet_materializes_existing_secrets_once(self):
        spec = importlib.util.spec_from_file_location(
            "entrypoint_compiler", APPS.parents[1] / "blueprints/compile.py"
        )
        compiler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(compiler)
        stack = ROOT
        for kind in ("identity", "db-tools"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                packet = compiler.compile_stack(
                    stack, compiler.read(stack / "site.example.json"), []
                )[kind]
                self.assertTrue(packet["enabled"])
                cfg = json.loads(packet["files"]["site.json"])
                value = json.loads(packet["files"]["stack.json"])
                destination = root / "inputs" / kind / packet["identity"]
                cfg["app"]["exclusive_writer_confirmed"] = True
                cfg["app"]["stack_config"] = str(destination / "stack.json")
                value["foundation"]["secret_files"] = {
                    key: str(destination / b.filename)
                    for key, b in BINDINGS[kind].items()
                }
                packet["files"]["site.json"] = json.dumps(cfg)
                packet["files"]["stack.json"] = json.dumps(value)
                source = root / "packet.json"
                source.write_text(json.dumps(packet))
                environment = {
                    b.environment: "synthetic-retained-" + key
                    for key, b in BINDINGS[kind].items()
                    if b.environment
                }
                selected, path = inputs.prepare(source, root / "inputs", environment)
                self.assertEqual(
                    selected["app"]["stack_config"], str(path.parent / "stack.json")
                )
                for key, binding in BINDINGS[kind].items():
                    self.assertEqual(
                        (path.parent / binding.filename).read_text(),
                        environment[binding.environment],
                    )
                    self.assertEqual(
                        (path.parent / binding.filename).stat().st_mode & 0o777, 0o600
                    )
                before = {p.name: p.read_bytes() for p in path.parent.iterdir()}
                inputs.prepare(source, root / "inputs", environment)
                self.assertEqual(
                    before, {p.name: p.read_bytes() for p in path.parent.iterdir()}
                )

    def test_automation_archives_are_checked_before_reusing_prepared_inputs(self):
        spec = importlib.util.spec_from_file_location(
            "archive_packet_compiler", APPS.parents[1] / "blueprints/compile.py"
        )
        compiler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(compiler)
        stack = ROOT
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet = compiler.compile_stack(
                stack, compiler.read(stack / "site.example.json"), []
            )["automation"]
            self.assertTrue(packet["enabled"])
            cfg = json.loads(packet["files"]["site.json"])
            value = json.loads(packet["files"]["stack.json"])
            cfg["app"]["exclusive_writer_confirmed"] = True
            cfg["app"]["stack_config"] = str(
                root / "inputs/automation" / packet["identity"] / "stack.json"
            )
            archives = []
            for name, service in value["services"].items():
                if "archive" in service:
                    archive = root / (name + ".tar")
                    archive.write_bytes(b"synthetic verified archive")
                    archives.append(archive)
                    service["archive"] = str(archive)
                    service["archive_sha256"] = hashlib.sha256(
                        archive.read_bytes()
                    ).hexdigest()
            packet["files"]["site.json"] = json.dumps(cfg)
            packet["files"]["stack.json"] = json.dumps(value)
            source = root / "packet.json"
            source.write_text(json.dumps(packet))
            environment = {"NODE_RED_API_TOKEN": "synthetic-retained-token"}
            _, site = inputs.prepare(source, root / "inputs", environment)
            prepared = json.loads((site.parent / "stack.json").read_text())
            self.assertEqual(
                prepared["services"]["node_red"]["environment"]["NODE_RED_API_TOKEN"],
                environment["NODE_RED_API_TOKEN"],
            )
            before = {p.name: p.read_bytes() for p in site.parent.iterdir()}
            archives[0].write_bytes(b"different content")
            with self.assertRaisesRegex(ValueError, "image archive"):
                inputs.prepare(source, root / "inputs", environment)
            self.assertEqual(
                before, {p.name: p.read_bytes() for p in site.parent.iterdir()}
            )
