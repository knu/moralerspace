"""Validate a complete build with fontTools and the HarfBuzz CLI."""

import configparser
import json
import shutil
import subprocess
import sys
import unittest
from functools import lru_cache
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont


class GeneratedFontsTest(unittest.TestCase):
    directory = Path("build")

    @classmethod
    def setUpClass(cls) -> None:
        cls.paths = sorted(cls.directory.rglob("Moralerspace*.ttf"))
        if not cls.paths:
            raise RuntimeError(f"no generated fonts in {cls.directory}")
        cls.settings = configparser.ConfigParser()
        cls.settings.read("build.ini", encoding="utf-8")

    @staticmethod
    def bounds(font: TTFont, name: str) -> tuple:
        glyphs = font.getGlyphSet()
        pen = BoundsPen(glyphs)
        glyphs[name].draw(pen)
        return pen.bounds

    @staticmethod
    def shape(path: Path, text: str, features: str = "") -> list:
        result = subprocess.run(
            [
                "hb-shape",
                str(path),
                text,
                "--output-format=json",
                f"--features={features}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    @classmethod
    @lru_cache(maxsize=20)
    def native_nerd_metrics(cls, family: str, style: str) -> dict:
        source = Path(f"source_fonts/monaspace/Monaspace{family}-{style}.otf")
        with TTFont(source) as font:
            cmap = font.getBestCmap()
            return {
                codepoint: (
                    font["head"].unitsPerEm,
                    font["hmtx"][cmap[codepoint]][0],
                    cls.bounds(font, cmap[codepoint]),
                )
                for codepoint in (0xEB06, 0xEAF7, 0xF408, 0xE0B0, 0xE0B2)
            }

    def test_complete_build(self) -> None:
        expected = {
            f"Moralerspace{family}{variant}-{style}.ttf"
            for family in ("Neon", "Argon", "Xenon", "Radon", "Krypton")
            for variant in ("", "HW", "JPDOC", "HWJPDOC")
            for style in ("Regular", "Bold", "Italic", "BoldItalic")
        }
        self.assertCountEqual([path.name for path in self.paths], expected)

    def test_metrics_and_coverage(self) -> None:
        for path in self.paths:
            with self.subTest(font=path.name), TTFont(path) as font:
                cmap = font.getBestCmap()
                half_width = 525 if "HW" in path.name else 600
                full_width = 1050 if "HW" in path.name else 1000
                family = next(
                    family
                    for family in ("Neon", "Argon", "Xenon", "Radon", "Krypton")
                    if path.name.startswith(f"Moralerspace{family}")
                )
                style = path.stem.partition("-")[2]
                reference = self.native_nerd_metrics(family, style)
                self.assertEqual(font["head"].unitsPerEm, 1000)
                self.assertIn(
                    self.settings["DEFAULT"]["VERSION"], font["name"].getDebugName(5)
                )
                for char in "0αЖỹあ漢":
                    self.assertIn(ord(char), cmap)
                self.assertEqual(font["hmtx"][cmap[ord("0")]][0], half_width)
                self.assertEqual(font["hmtx"][cmap[ord("あ")]][0], full_width)
                self.assertEqual(font["post"].isFixedPitch, int("HW" in path.name))
                for char in "─│┼":
                    expected = full_width if "JPDOC" in path.name else half_width
                    self.assertEqual(font["hmtx"][cmap[ord(char)]][0], expected)
                if "JPDOC" not in path.name:
                    for codepoint in range(0x2500, 0x2580):
                        self.assertIn(codepoint, cmap)
                        self.assertEqual(font["hmtx"][cmap[codepoint]][0], half_width)
                for char in "↔⇐∴∵∽≒≦≧":
                    self.assertIn(ord(char), cmap)
                    if "JPDOC" in path.name:
                        self.assertEqual(font["hmtx"][cmap[ord(char)]][0], full_width)
                for codepoint in (0xEB06, 0xEAF7, 0xF408):
                    name = cmap[codepoint]
                    self.assertEqual(font["hmtx"][name][0], half_width)
                    em, advance, original = reference[codepoint]
                    y_scale = 1000 / em * (0.99 if "HW" in path.name else 1)
                    expected = (
                        original[0] * half_width / advance,
                        original[1] * y_scale,
                        original[2] * half_width / advance,
                        original[3] * y_scale,
                    )
                    for actual, target in zip(self.bounds(font, name), expected):
                        self.assertAlmostEqual(actual, target, delta=3)
                for codepoint in (0xE0B0, 0xE0B2):
                    name = cmap[codepoint]
                    self.assertEqual(font["hmtx"][name][0], half_width)
                    _, advance, original = reference[codepoint]
                    expected = (
                        original[0] * half_width / advance,
                        font["hhea"].descent,
                        original[2] * half_width / advance,
                        font["hhea"].ascent,
                    )
                    for actual, target in zip(self.bounds(font, name), expected):
                        self.assertAlmostEqual(actual, target, delta=3)

    def test_nerd_supplement(self) -> None:
        with TTFont("source_fonts/nerd-fonts/SymbolsNerdFont-Regular.ttf") as source:
            symbols = set(source.getBestCmap())
        for path in self.paths:
            with self.subTest(font=path.name), TTFont(path) as font:
                cmap = font.getBestCmap()
                self.assertFalse(symbols - cmap.keys())
                glyph = cmap[0xE6B3]
                half_width = 525 if "HW" in path.name else 600
                self.assertEqual(font["hmtx"][glyph][0], half_width)
                x0, y0, x1, y1 = self.bounds(font, glyph)
                self.assertGreaterEqual(x0, -1)
                self.assertLessEqual(x1, half_width + 1)
                self.assertAlmostEqual((y0 + y1) / 2, 350, delta=1)

    def test_underscore_healing(self) -> None:
        for path in self.paths:
            with TTFont(path) as font:
                for features in ("", "ss06"):
                    for text in ("a__", "m__", "w__"):
                        with self.subTest(font=path.name, text=text, features=features):
                            shaped = self.shape(path, text, features)
                            self.assertEqual(len(shaped), 3)
                            heights = []
                            for glyph in shaped[1:]:
                                _, bottom, _, top = self.bounds(font, glyph["g"])
                                heights.append(
                                    (bottom + glyph["dy"], top + glyph["dy"])
                                )
                            self.assertEqual(heights[0], heights[1])

    def test_xenon_japanese_coverage(self) -> None:
        for style in ("Regular", "Bold"):
            source = Path(f"source_fonts/source-han-serif/SourceHanSerifJP-{style}.otf")
            with TTFont(source) as font:
                japanese = {
                    codepoint
                    for codepoint in font.getBestCmap()
                    if 0x2E80 <= codepoint <= 0x9FFF
                    or 0xF900 <= codepoint <= 0xFAFF
                    or 0xFF00 <= codepoint <= 0xFFEF
                    or 0x20000 <= codepoint <= 0x2FFFF
                }
            for path in self.paths:
                if "Xenon" not in path.name or ("Bold" in path.name) != (
                    style == "Bold"
                ):
                    continue
                with self.subTest(font=path.name), TTFont(path) as font:
                    self.assertFalse(japanese - font.getBestCmap().keys())

    def test_programming_ligatures(self) -> None:
        text = "!= === ->"
        for path in self.paths:
            with self.subTest(font=path.name), TTFont(path) as font:
                shaped = self.shape(path, text, "ss01,ss03")
                names = {glyph["g"] for glyph in shaped}
                self.assertTrue(
                    {"exclam_equal", "equal_equal_equal", "hyphen_greater"} <= names
                )
                half_width = font["hmtx"][font.getBestCmap()[ord("0")]][0]
                self.assertEqual(
                    sum(glyph["ax"] for glyph in shaped), len(text) * half_width
                )

    def test_multilingual_shaping(self) -> None:
        for path in self.paths:
            with self.subTest(font=path.name):
                shaped = self.shape(path, "αβγ Жж ỹ 日本語")
                self.assertFalse(any(glyph["g"] == ".notdef" for glyph in shaped))

    def test_terminal_prompt(self) -> None:
        for path in self.paths:
            with self.subTest(font=path.name), TTFont(path) as font:
                text = (
                    "\ue0b0 \ueb06/\ueaf7/project \ue0b0\uf408 \ue0a0main\u2261 \ue0b0"
                )
                shaped = self.shape(path, text)
                half_width = font["hmtx"][font.getBestCmap()[ord("0")]][0]
                self.assertFalse(any(glyph["g"] == ".notdef" for glyph in shaped))
                expected = len(text) * half_width
                if "JPDOC" in path.name:
                    expected += (1050 if "HW" in path.name else 1000) - half_width
                self.assertEqual(sum(glyph["ax"] for glyph in shaped), expected)
                pair = self.shape(path, "\ue0b0\uf408")
                divider = self.bounds(font, pair[0]["g"])
                logo = self.bounds(font, pair[1]["g"])
                gap = (
                    pair[0]["ax"] + pair[1]["dx"] + logo[0] - pair[0]["dx"] - divider[2]
                )
                family = next(
                    family
                    for family in ("Neon", "Argon", "Xenon", "Radon", "Krypton")
                    if path.name.startswith(f"Moralerspace{family}")
                )
                reference = self.native_nerd_metrics(
                    family, path.stem.partition("-")[2]
                )
                _, advance, native_divider = reference[0xE0B0]
                _, _, native_logo = reference[0xF408]
                expected_gap = (
                    (advance + native_logo[0] - native_divider[2])
                    * half_width
                    / advance
                )
                self.assertAlmostEqual(gap, expected_gap, delta=3)


if __name__ == "__main__":
    if shutil.which("hb-shape") is None:
        sys.exit("hb-shape is required (HarfBuzz CLI)")
    if len(sys.argv) > 1:
        GeneratedFontsTest.directory = Path(sys.argv.pop(1))
    unittest.main()
