"""Check release notes boundaries and complete ZIP manifests."""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

spec = importlib.util.spec_from_file_location(
    "prepare_release",
    Path(__file__).resolve().parents[1] / "scripts/prepare_release.py",
)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseNotesTest(unittest.TestCase):
    def test_extracts_only_version_section(self) -> None:
        markdown = (
            "# Changelog\n\n## Unreleased\n\nLater.\n\n## 2.1.0\n\n"
            "- Fixed.\n\n### Details\n\n```markdown\n## 0.0.0\n```\n\n"
            "## 2.0.0\n\nEarlier.\n"
        )
        self.assertEqual(
            release.release_notes(markdown, "v2.1.0"),
            "- Fixed.\n\n### Details\n\n```markdown\n## 0.0.0\n```\n",
        )

    def test_rejects_missing_duplicate_and_empty_sections(self) -> None:
        for markdown in (
            "## 2.0.0\n\nEarlier.\n",
            "## 2.1.0\n\nFirst.\n\n## 2.1.0\n\nSecond.\n",
            "## 2.1.0\n\n## 2.0.0\n\nEarlier.\n",
            "```\n## 2.1.0\n```\n",
            "# 2.1.0\n\nWrong heading level.\n",
        ):
            with self.subTest(markdown=markdown), self.assertRaises(ValueError):
                release.release_notes(markdown, "v2.1.0")

    def test_cli_checks_tag_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "release"
            for tag in ("v0.0.0", "invalid"):
                result = subprocess.run(
                    [sys.executable, str(spec.origin), tag, str(output)],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                with self.subTest(tag=tag):
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("error:", result.stderr)
                    self.assertFalse(output.exists())


class PackageFontsTest(unittest.TestCase):
    def test_packages_all_variants_and_rejects_incomplete_build(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build = root / "build"
            output = root / "release"
            for variant in release.VARIANTS:
                directory = build / f"Moralerspace{variant}_v2.1.0"
                directory.mkdir(parents=True)
                for family in release.FAMILIES:
                    for style in release.STYLES:
                        (
                            directory / f"Moralerspace{family}{variant}-{style}.ttf"
                        ).touch()
            release.package_fonts(build, output, "Moralerspace", "v2.1.0")
            archives = sorted(output.glob("*.zip"))
            self.assertEqual(len(archives), 8)
            for path in archives:
                with ZipFile(path) as archive:
                    self.assertEqual(len(archive.namelist()), 21)
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(
                        archive.read(f"{path.stem}/LICENSE"),
                        Path("LICENSE").read_bytes(),
                    )
            next(build.rglob("*.ttf")).unlink()
            with self.assertRaisesRegex(ValueError, "incomplete font build"):
                release.package_fonts(
                    build, root / "incomplete", "Moralerspace", "v2.1.0"
                )
            self.assertFalse((root / "incomplete").exists())


if __name__ == "__main__":
    unittest.main()
