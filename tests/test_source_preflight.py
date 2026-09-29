"""Protect the source pin and scoped-cleanliness rules used for builds."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.source_preflight import inspect_component


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


class SourcePreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "fixture"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Lineage POC Test")
        git(self.repo, "config", "user.email", "lineage-poc-test@example.invalid")
        git(self.repo, "remote", "add", "origin", "https://example.invalid/fixture.git")
        app = self.repo / "sample-app"
        app.mkdir()
        (app / "input.txt").write_text("source\n", encoding="utf-8")
        git(self.repo, "add", "sample-app/input.txt")
        git(self.repo, "commit", "-qm", "fixture")
        self.component = {
            "name": "fixture",
            "role": "test-app",
            "local_path": "fixture",
            "source_scope": "sample-app",
        }
        self.pin = {
            "repository_url": "https://example.invalid/fixture.git",
            "commit": git(self.repo, "rev-parse", "HEAD"),
            "source_scope": "sample-app",
        }

    def inspect(self) -> dict[str, object]:
        return inspect_component(self.root, self.component, self.pin, None)

    def test_unrelated_untracked_file_does_not_dirty_source_scope(self) -> None:
        (self.repo / "unrelated.txt").write_text("notes\n", encoding="utf-8")

        result = self.inspect()

        self.assertEqual(result["state"], "clean")
        self.assertTrue(result["reproducible"])
        self.assertEqual(result["dirty_paths"], [])
        self.assertEqual(result["checkout_dirty_paths"], ["unrelated.txt"])

    def test_source_change_blocks_reproducibility(self) -> None:
        (self.repo / "sample-app" / "input.txt").write_text("changed\n", encoding="utf-8")

        result = self.inspect()

        self.assertEqual(result["state"], "dirty")
        self.assertFalse(result["reproducible"])
        self.assertEqual(result["dirty_paths"], ["sample-app/input.txt"])

    def test_commit_mismatch_blocks_reproducibility(self) -> None:
        self.pin["commit"] = "0" * 40

        result = self.inspect()

        self.assertEqual(result["state"], "mismatch")
        self.assertFalse(result["reproducible"])


if __name__ == "__main__":
    unittest.main()
