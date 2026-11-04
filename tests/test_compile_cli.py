"""The authored library examples reach the real component packet CLI offline."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()


class CompilerCLITests(unittest.TestCase):
    def test_default_and_empty_disable_nothing_while_named_guests_are_excluded(self):
        for arguments, guest, expected in (
            ([], "resolver", True),
            (["--disabled", ""], "resolver", True),
            (["--disabled", "[]"], "resolver", True),
            (["--disabled", '["resolver"]'], "resolver", False),
        ):
            with self.subTest(
                arguments=arguments
            ), tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / "packet.json"
                result = self.command(
                    "--guest", guest, "--output", str(output), *arguments
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIs(json.loads(output.read_text())["enabled"], expected)

    def command(self, *args):
        return subprocess.run(
            [
                sys.executable,
                str(FRAMEWORK / "blueprints/compile.py"),
                "--stack",
                str(ROOT),
                "--site",
                str(ROOT / "site.example.yaml"),
                *args,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_check_and_packet_output_are_offline_and_exclusive(self):
        for example in ("site.example.yaml", "examples/site.second.yaml"):
            with self.subTest(example=example):
                result = subprocess.run(
                    [sys.executable, str(FRAMEWORK / "blueprints/compile.py"),
                     "--stack", str(ROOT), "--site", str(ROOT / example), "--check"],
                    capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "packet.json"
            result = self.command("--guest", "resolver", "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads(output.read_text())
            self.assertEqual(packet["schema"], "homelab-component-guest-deployment-v1")
            self.assertEqual(packet["guest"], "resolver")
            self.assertTrue(packet["enabled"])
            self.assertEqual(set(packet), {"schema", "guest", "enabled", "identity", "files"})
            runtime = json.loads(packet["files"]["component-runtime.json"])
            self.assertEqual(set(runtime["applications"]), {"recursive_dns"})
            self.assertEqual(runtime["applications"]["recursive_dns"]["adapter"], "unbound")
            before = output.read_bytes()
            self.assertNotEqual(
                self.command("--guest", "resolver", "--output", str(output)).returncode, 0
            )
            self.assertEqual(output.read_bytes(), before)
            for args in (
                [],
                ["--guest", "resolver", "--output", str(Path(tmp) / "other"), "--admit"],
                [
                    "--guest",
                    "resolver",
                    "--output",
                    str(Path(tmp) / "other"),
                    "--admit",
                    "--disabled",
                    '["resolver"]',
                ],
            ):
                result = self.command(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((Path(tmp) / "other").exists())
        result = self.command("--check", "--enabled", "[]")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments", result.stderr)
