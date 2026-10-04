"""End-to-end tests in disposable repositories; no network or user notebook access."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]


class LearningTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.repo = self.base / "sample project"
        self.repo.mkdir()
        self.notebook = self.base / "private notebook"
        shutil.copytree(SCRIPTS, self.repo / "scripts")
        self.env = dict(
            os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1"
        )
        self.run_command("git", "init", "-q")
        self.run_command("git", "config", "user.email", "test@example.invalid")
        self.run_command("git", "config", "user.name", "Learning test")
        self.run_command("git", "config", "commit.gpgsign", "false")

    def run_command(self, *command, expected=0, input=None):
        result = subprocess.run(
            command,
            cwd=self.repo,
            env=self.env,
            capture_output=True,
            text=True,
            input=input,
            check=False,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def learning(self, *args, **kwargs):
        return self.run_command(sys.executable, "scripts/learning.py", *args, **kwargs)

    def configure(self, *args):
        return self.learning(
            "setup", "--notebook", str(self.notebook), "--project", "sample", *args
        )

    def records(self):
        records = []
        for file in self.notebook.glob("products/sample/events/*.md"):
            records.append(
                json.loads(file.read_text().split("```json\n")[1].split("\n```")[0])
            )
        return records

    def test_setup_is_idempotent_and_preserves_written_notes(self):
        self.configure()
        (self.notebook / "direction.md").write_text("My actual goals")
        self.configure()
        self.assertEqual(
            (self.notebook / "direction.md").read_text(), "My actual goals"
        )

    def test_setup_registers_project_for_review(self):
        self.configure()
        registered = json.loads(
            (self.notebook / "products/sample/project.json").read_text()
        )
        self.assertEqual(Path(registered["path"]), self.repo.resolve())

    def test_commit_hook_records_once_without_capturing_file_contents(self):
        self.configure()
        (self.repo / "file.txt").write_text("Private contents must not enter the event")
        self.run_command("git", "add", "file.txt")
        self.run_command("git", "commit", "-qm", "Test commit")
        self.learning("record", "--kind", "commit")
        self.assertEqual(len(self.records()), 1)
        self.assertEqual(self.records()[0]["subject"], "Test commit")
        self.assertNotIn("Private contents", json.dumps(self.records()))

    def test_command_failure_is_preserved_and_recorded(self):
        self.configure()
        self.run_command(
            "sh",
            "scripts/with-learning.sh",
            "build",
            sys.executable,
            "-c",
            "raise SystemExit(7)",
            expected=7,
        )
        self.assertEqual(self.records()[0]["exit_code"], 7)
        self.assertEqual(self.records()[0]["kind"], "build")

    def test_unconfigured_wrapper_has_no_notebook_side_effects(self):
        self.run_command(
            "sh", "scripts/with-learning.sh", "check", sys.executable, "-c", "pass"
        )
        self.assertFalse(self.notebook.exists())

    def test_capture_failure_does_not_change_command_result(self):
        self.configure()
        (self.repo / "scripts/learning.py").unlink()
        self.run_command(
            "sh", "scripts/with-learning.sh", "check", sys.executable, "-c", "pass"
        )

    def test_existing_hook_is_not_overwritten(self):
        hook = self.repo / ".git/hooks/post-commit"
        hook.write_text("#!/bin/sh\n# existing hook\n")
        self.learning(
            "setup", "--notebook", str(self.notebook), "--project", "sample", expected=1
        )
        self.assertIn("existing hook", hook.read_text())
        self.configure("--no-hook")
        self.assertIn("existing hook", hook.read_text())

    def test_hooks_manager_requires_explicit_no_hook(self):
        self.run_command("git", "config", "core.hooksPath", ".custom-hooks")
        self.learning(
            "setup", "--notebook", str(self.notebook), "--project", "sample", expected=1
        )
        self.assertFalse(self.notebook.exists())
        self.configure("--no-hook")
        self.assertFalse((self.repo / ".custom-hooks/post-commit").exists())
        self.assertEqual(
            self.run_command("git", "config", "--get", "core.hooksPath").stdout.strip(),
            ".custom-hooks",
        )

    def test_commit_survives_capture_failure(self):
        self.configure()
        (self.repo / "scripts/learning.py").unlink()
        (self.repo / "file.txt").write_text("work to preserve")
        self.run_command("git", "add", "file.txt")
        result = self.run_command("git", "commit", "-qm", "Preserved commit")
        self.assertIn("Learning capture failed", result.stderr)
        self.assertEqual(
            self.run_command("git", "log", "-1", "--format=%s").stdout.strip(),
            "Preserved commit",
        )

    def test_notebook_cannot_be_inside_product_repo(self):
        self.learning(
            "setup",
            "--notebook",
            str(self.repo / "notes"),
            "--project",
            "sample",
            expected=1,
        )
        self.assertFalse((self.repo / "notes").exists())

    def test_project_id_cannot_escape_notebook(self):
        self.learning(
            "setup",
            "--notebook",
            str(self.notebook),
            "--project",
            "../escape",
            expected=1,
        )

    def test_deployment_requires_explicit_evidence(self):
        self.configure()
        self.learning("record", "--kind", "deployment", expected=1)
        self.assertEqual(self.records(), [])
        self.learning(
            "record",
            "--kind",
            "deployment",
            "--evidence",
            "https://example.invalid/releases/1",
        )
        self.assertEqual(self.records()[0]["kind"], "deployment")

    def test_notes_are_private_and_append_without_overwriting(self):
        self.configure()
        for _ in range(2):
            self.learning(
                "note",
                "--area",
                "product",
                input="Evidence: two interviews.\nLearning: still uncertain.",
            )
        notes = list(self.notebook.glob("products/sample/notes/*.md"))
        self.assertEqual(len(notes), 2)
        self.assertIn("two interviews", notes[0].read_text())
        self.assertFalse((self.repo / "notes").exists())


if __name__ == "__main__":
    unittest.main()
