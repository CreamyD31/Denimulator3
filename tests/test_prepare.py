"""Exercise patch safety against real temporary Git repositories, without network."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "prepare", Path(__file__).resolve().parents[1] / "scripts" / "prepare.py")
prepare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare)


class PrepareTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "source"
        self.source.mkdir()
        self.git("init", "-q")
        self.git("config", "core.autocrlf", "false")
        self.file = self.source / "name.txt"
        # These are Git patch fixtures: use exact LF bytes even on Windows.
        # Text-mode writes translate LF to CRLF on that platform.
        self.file.write_bytes(b"Azahar\n")
        self.git("add", ".")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                 "commit", "-qm", "Fixture")
        self.commit = self.git("rev-parse", "HEAD").decode().strip()
        self.file.write_bytes(b"Denimulator3\n")
        self.patch = Path(self.temp.name) / "branding.patch"
        self.patch.write_bytes(self.git("diff", "--binary"))
        self.git("restore", "name.txt")
        for name, value in (("COMMIT", self.commit), ("PATCH", self.patch)):
            mock = patch.object(prepare, name, value)
            mock.start()
            self.addCleanup(mock.stop)

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.source), *args])

    def test_apply_and_repeat(self):
        prepare.apply_branding(self.source)
        prepare.apply_branding(self.source)
        self.assertEqual(self.file.read_text(), "Denimulator3\n")

    def test_foreign_changes_preserved(self):
        self.file.write_bytes(b"User changes\n")
        with self.assertRaisesRegex(RuntimeError, "other local changes"):
            prepare.apply_branding(self.source)
        self.assertEqual(self.file.read_text(), "User changes\n")

    def test_windows_patch_line_endings(self):
        self.patch.write_bytes(self.patch.read_bytes().replace(b"\n", b"\r\n"))
        prepare.apply_branding(self.source)
        prepare.apply_branding(self.source)
        self.assertEqual(self.file.read_bytes(), b"Denimulator3\n")

    def test_wrong_revision_rejected(self):
        with patch.object(prepare, "COMMIT", "0" * 40):
            with self.assertRaisesRegex(RuntimeError, "Unexpected upstream HEAD"):
                prepare.apply_branding(self.source)
        self.assertEqual(self.file.read_text(), "Azahar\n")

    def test_untracked_file_preserved(self):
        extra = self.source / "notes.txt"
        extra.write_bytes(b"Keep me\n")
        prepare.apply_branding(self.source)
        self.assertEqual(extra.read_text(), "Keep me\n")

    def test_existing_non_repository_rejected(self):
        other = Path(self.temp.name) / "other"
        other.mkdir()
        with self.assertRaisesRegex(RuntimeError, "not a Git checkout"):
            prepare.prepare(other, submodules=False)


if __name__ == "__main__":
    unittest.main()
