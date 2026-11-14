"""Generate the bold and dehinted Japanese source fonts."""

import argparse
from pathlib import Path

import fontforge
from ttfautohint import ttfautohint


def prepare_derived_fonts(directory: Path) -> None:
    for subdirectory, family, style, width in (
        ("kiwimaru", "KiwiMaru", "Medium", 35),
        ("stick", "Stick", "Regular", 38),
    ):
        path = directory / subdirectory
        font = fontforge.open(str(path / f"{family}-{style}.ttf"))
        try:
            for glyph in font.glyphs():
                if glyph.isWorthOutputting():
                    glyph.stroke(
                        "circular", width, removeinternal=True, removeoverlap="none"
                    )
                    glyph.removeOverlap()
            font.generate(str(path / f"{family}-Bold.ttf"))
        finally:
            font.close()
    for style in ("Medium", "Bold"):
        path = directory / "kiwimaru"
        ttfautohint(
            in_file=str(path / f"KiwiMaru-{style}.ttf"),
            out_file=str(path / f"KiwiMaru-{style}_dehint.ttf"),
            dehint=True,
            no_info=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    prepare_derived_fonts(args.directory)


if __name__ == "__main__":
    main()
