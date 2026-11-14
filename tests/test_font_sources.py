"""Check source pinning, safe extraction, and download cache failures."""

import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import font_sources


class FontSourcesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.manifest = self.directory / "versions.ini"
        self.manifest.write_bytes(
            (font_sources.source_directory() / "versions.ini").read_bytes()
        )

    def test_pins_select_the_correct_upstream_files(self) -> None:
        versions = font_sources.read_versions(self.manifest)
        versions["releases"]["ibm-plex-sans-jp"] = "4.0.0"
        versions["revisions"]["stick"] = "a" * 40
        sources = font_sources.source_urls(versions)
        self.assertIn(
            "%40ibm%2Fplex-sans-jp%404.0.0/",
            sources["ibm-plex-sans-jp/IBMPlexSansJP-Text.ttf"],
        )
        self.assertIn("/" + "a" * 40 + "/", sources["stick/Stick-Regular.ttf"])
        self.assertIn(
            "fonts/NerdFonts/Monaspace%20Argon/MonaspaceArgonNF-Regular.otf",
            sources["monaspace/MonaspaceArgon-Regular.otf"],
        )

    def test_invalid_or_missing_pins_fail(self) -> None:
        original = self.manifest.read_text()
        revision = font_sources.read_versions(self.manifest)["revisions"]["stick"]
        for replacement in ("", "stick = master\n", "stick = ../other\n"):
            with self.subTest(replacement=replacement):
                self.manifest.write_text(
                    original.replace(
                        f"stick = {revision}\n",
                        replacement,
                    )
                )
                with self.assertRaises(ValueError):
                    font_sources.read_versions(self.manifest)

    def test_cache_changes_when_a_pin_changes(self) -> None:
        (self.directory / "ideographic_space.sfd").write_text("sample")
        with patch.object(
            font_sources, "source_directory", return_value=self.directory
        ):
            before = font_sources.prepared_directory()
            version = font_sources.read_versions(self.manifest)["releases"][
                "nerd-fonts"
            ]
            self.manifest.write_text(
                self.manifest.read_text().replace(
                    f"nerd-fonts = {version}", "nerd-fonts = v0.0.0"
                )
            )
            self.assertNotEqual(font_sources.prepared_directory(), before)

    def test_download_reuses_complete_files_and_discards_partial_files(self) -> None:
        def response(data: bytes, length: int) -> io.BytesIO:
            result = io.BytesIO(data)
            result.headers = {"Content-Length": str(length)}
            return result

        with patch.object(font_sources, "CACHE", self.directory):
            with patch.object(
                font_sources, "urlopen", return_value=response(b"font", 4)
            ):
                path = font_sources.download("https://example.com/font")
                self.assertEqual(path.read_bytes(), b"font")
            with patch.object(font_sources, "urlopen") as request:
                self.assertEqual(
                    font_sources.download("https://example.com/font"), path
                )
                request.assert_not_called()
            with (
                patch.object(font_sources, "urlopen", return_value=response(b"bad", 4)),
                self.assertRaisesRegex(ValueError, "incomplete download"),
            ):
                font_sources.download("https://example.com/other")
            self.assertEqual(list((self.directory / "downloads").iterdir()), [path])

    def test_symbols_archive_only_extracts_required_files(self) -> None:
        archive = self.directory / "symbols.zip"
        with ZipFile(archive, "w") as file:
            file.writestr("SymbolsNerdFont-Regular.ttf", b"font")
            file.writestr("LICENSE", "sample license")
            file.writestr("../outside", "unwanted")
        output = self.directory / "symbols"
        font_sources.unpack_symbols(archive, output)
        self.assertEqual(
            {path.name for path in output.iterdir()},
            {"SymbolsNerdFont-Regular.ttf", "LICENSE"},
        )
        self.assertFalse((self.directory / "outside").exists())


if __name__ == "__main__":
    unittest.main()
