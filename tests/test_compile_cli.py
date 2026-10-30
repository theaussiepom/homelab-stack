"""Compiler and credential CLIs exercise the same current catalogues offline."""

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
            ([], "dns", True),
            (["--disabled", ""], "dns", True),
            (["--disabled", "[]"], "dns", True),
            (["--disabled", '["zigbee2mqtt"]'], "zigbee2mqtt", False),
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
                str(ROOT / "site.example.json"),
                *args,
            ],
            capture_output=True,
            text=True,
        )

    def test_check_and_packet_output_are_offline_and_exclusive(self):
        self.assertEqual(self.command("--check").returncode, 0)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "packet.json"
            result = self.command("--guest", "dns", "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads(output.read_text())
            self.assertTrue(packet["enabled"])
            before = output.read_bytes()
            self.assertNotEqual(
                self.command("--guest", "dns", "--output", str(output)).returncode, 0
            )
            self.assertEqual(output.read_bytes(), before)
            for args in (
                [],
                ["--guest", "dns", "--output", str(Path(tmp) / "other"), "--admit"],
                [
                    "--guest",
                    "dns",
                    "--output",
                    str(Path(tmp) / "other"),
                    "--admit",
                    "--disabled",
                    '["dns"]',
                ],
            ):
                result = self.command(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((Path(tmp) / "other").exists())
        result = self.command("--check", "--enabled", "[]")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments", result.stderr)
