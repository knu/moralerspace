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
from fontTools.pens.recordingPen import DecomposingRecordingPen
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
    def native_powerline_metrics(cls, family: str, style: str) -> dict:
        source = Path(f"source_fonts/monaspace/Monaspace{family}-{style}.otf")
        with TTFont(source) as font:
            cmap = font.getBestCmap()
            return {
                codepoint: (
                    font["head"].unitsPerEm,
                    font["hmtx"][cmap[codepoint]][0],
                    cls.bounds(font, cmap[codepoint]),
                )
                for codepoint in (0xE0B0, 0xE0B2)
            }

    @classmethod
    @lru_cache(maxsize=1)
    def symbols_metrics(cls) -> dict:
        with TTFont("source_fonts/nerd-fonts/SymbolsNerdFont-Regular.ttf") as font:
            cmap = font.getBestCmap()
            return {
                codepoint: (
                    font["head"].unitsPerEm,
                    font["hmtx"][cmap[codepoint]][0],
                    cls.bounds(font, cmap[codepoint]),
                )
                for codepoint in (0xEB06, 0xEAF7, 0xF408, 0xE6B3)
            }

    def test_complete_build(self) -> None:
        expected = {
            f"Moralerspace{family}{variant}{nerd}-{style}.ttf"
            for family in ("Neon", "Argon", "Xenon", "Radon", "Krypton")
            for variant in ("", "HW", "JPDOC", "HWJPDOC")
            for nerd in ("", "NFM")
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
                reference = self.native_powerline_metrics(family, style)
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
                for codepoint, (
                    em,
                    advance,
                    original,
                ) in self.symbols_metrics().items():
                    name = cmap[codepoint]
                    self.assertEqual(font["hmtx"][name][0], half_width)
                    bounds = self.bounds(font, name)
                    if "NFM" in path.name:
                        x0, y0, x1, y1 = bounds
                        self.assertGreaterEqual(x0, -1)
                        self.assertLessEqual(x1, half_width + 1)
                        self.assertGreaterEqual(y0, font["hhea"].descent - 1)
                        self.assertLessEqual(y1, font["hhea"].ascent + 1)
                        self.assertAlmostEqual((x0 + x1) / 2, half_width / 2, delta=1)
                        self.assertAlmostEqual((y0 + y1) / 2, 350, delta=1)
                        self.assertAlmostEqual(
                            (x1 - x0) / (y1 - y0),
                            (original[2] - original[0]) / (original[3] - original[1]),
                            delta=0.01,
                        )
                    else:
                        scale = 1000 / em
                        shift = (
                            (half_width - advance * scale) / 2
                            if advance * scale < 600
                            else 0
                        )
                        expected = (
                            original[0] * scale + shift,
                            original[1] * scale,
                            original[2] * scale + shift,
                            original[3] * scale,
                        )
                        for actual, target in zip(bounds, expected):
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

    def test_nerd_coverage(self) -> None:
        with TTFont("source_fonts/nerd-fonts/SymbolsNerdFont-Regular.ttf") as source:
            symbols = set(source.getBestCmap())
        for path in self.paths:
            with self.subTest(font=path.name), TTFont(path) as font:
                cmap = font.getBestCmap()
                self.assertFalse(symbols - cmap.keys())

    def test_nfm_preserves_text_and_separators(self) -> None:
        paths = {path.name: path for path in self.paths}
        for path in self.paths:
            if "NFM" not in path.name:
                continue
            sibling = paths[path.name.replace("NFM-", "-")]
            with (
                self.subTest(font=path.name),
                TTFont(path) as mono,
                TTFont(sibling) as wide,
            ):
                self.assertEqual(set(mono.getBestCmap()), set(wide.getBestCmap()))
                glyph_sets = (mono.getGlyphSet(), wide.getGlyphSet())
                characters = "0Aa_αЖỹあ漢─↔\ue0b0\ue0b4\ue0b6" + "".join(
                    chr(codepoint)
                    for codepoint in range(0xE123, 0xE134)
                    if codepoint in wide.getBestCmap()
                )
                for char in characters:
                    outlines = []
                    for font, glyphs in zip((mono, wide), glyph_sets):
                        name = font.getBestCmap()[ord(char)]
                        pen = DecomposingRecordingPen(glyphs)
                        glyphs[name].draw(pen)
                        outlines.append((font["hmtx"][name], pen.value))
                    self.assertEqual(outlines[0], outlines[1], char)

    def test_nfm_all_icons_fit(self) -> None:
        with TTFont("source_fonts/nerd-fonts/SymbolsNerdFont-Regular.ttf") as source:
            symbols = set(source.getBestCmap())
        for variant in ("NFM", "HWNFM"):
            path = next(
                p
                for p in self.paths
                if p.name == f"MoralerspaceArgon{variant}-Regular.ttf"
            )
            with TTFont(path) as font:
                cmap = font.getBestCmap()
                glyphs = font.getGlyphSet()
                half_width = font["hmtx"][cmap[ord("0")]][0]
                for codepoint in symbols:
                    if 0xE0B0 <= codepoint <= 0xE0D7:
                        continue
                    name = cmap[codepoint]
                    pen = BoundsPen(glyphs)
                    glyphs[name].draw(pen)
                    bounds = pen.bounds
                    if bounds is None:
                        continue
                    with self.subTest(font=path.name, codepoint=hex(codepoint)):
                        self.assertEqual(font["hmtx"][name][0], half_width)
                        x0, y0, x1, y1 = bounds
                        self.assertGreaterEqual(x0, -1)
                        self.assertLessEqual(x1, half_width + 1)
                        self.assertGreaterEqual(y0, font["hhea"].descent - 1)
                        self.assertLessEqual(y1, font["hhea"].ascent + 1)

    def test_unique_variant_names(self) -> None:
        names = set()
        for path in self.paths:
            with TTFont(path) as font:
                postscript = font["name"].getDebugName(6)
                self.assertEqual(postscript, path.stem)
                self.assertNotIn(postscript, names)
                names.add(postscript)
                if "NFM" in path.name:
                    self.assertTrue(font["name"].getDebugName(1).endswith(" NFM"))

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
                icon_and_label = self.shape(path, "\uf408 X")
                logo = self.bounds(font, icon_and_label[0]["g"])
                self.assertGreaterEqual(logo[0], -1)
                self.assertLessEqual(logo[2], 2 * half_width + 1)
                self.assertEqual(icon_and_label[0]["ax"], half_width)


if __name__ == "__main__":
    if shutil.which("hb-shape") is None:
        sys.exit("hb-shape is required (HarfBuzz CLI)")
    if len(sys.argv) > 1:
        GeneratedFontsTest.directory = Path(sys.argv.pop(1))
    unittest.main()
