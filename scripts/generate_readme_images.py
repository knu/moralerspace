"""Render README specimens from built fonts, without installing them."""

import argparse
import configparser
import math
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont, features
from PIL.PngImagePlugin import PngInfo

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {
    "Neon": "#ef78ef",
    "Argon": "#82e7ed",
    "Xenon": "#a0ef76",
    "Radon": "#ffbe67",
    "Krypton": "#a6a2ff",
}
SAMPLE = (
    "Lorem ipsumであのイーハトーヴォの世界が広がります。",
    "abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "1234567890 `~!@#$%^&*()-_=+[]{}\\|;:'\",.<>/?",
    "m__ w__  -> => != == === <= >=  // /* */",
)
ICONS = (0xF07B, 0xF015, 0xF120, 0xF121, 0xF013, 0xF09B)
BACKGROUND = "#242424"
FOREGROUND = "#eeeeee"
MUTED = "#aaaaaa"


def find_fonts(directory: Path, version: str) -> dict[str, Path]:
    paths = {}
    for family in (*FAMILIES, "ArgonNFM"):
        filename = f"Moralerspace{family}-Regular.ttf"
        matches = list(directory.rglob(filename))
        if len(matches) != 1:
            raise ValueError(f"expected one {filename}, found {len(matches)}")
        path = matches[0]
        with TTFont(path) as font:
            actual = font["name"].getDebugName(5) or ""
            if actual.split(";", 1)[0] != version:
                raise ValueError(f"{path.name}: expected {version}, found {actual}")
            required = set("".join(SAMPLE))
            if family in ("Argon", "ArgonNFM"):
                required.update(map(chr, ICONS))
            missing = {ord(char) for char in required} - font.getBestCmap().keys()
            if missing:
                raise ValueError(f"{path.name}: missing glyphs {sorted(missing)}")
        paths[family] = path
    return paths


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


def save_image(image: Image.Image, path: Path, version: str) -> None:
    metadata = PngInfo()
    metadata.add_text("Font version", version)
    metadata.add_text("Generator", "scripts/generate_readme_images.py")
    image.save(path, pnginfo=metadata, optimize=True)
    print(path)


def render_families(paths: dict[str, Path], output: Path, version: str) -> None:
    fonts = {family: load_font(paths[family], 34) for family in FAMILIES}
    labels = {family: load_font(paths[family], 48) for family in FAMILIES}
    padding = 56
    text_x = (
        padding
        + math.ceil(max(font.getlength(family) for family, font in labels.items()))
        + 48
    )
    text_width = math.ceil(
        max(font.getbbox(line)[2] for font in fonts.values() for line in SAMPLE)
    )
    ascent = max(font.getmetrics()[0] for font in fonts.values())
    line_height = max(sum(font.getmetrics()) for font in fonts.values()) + 4
    row_height = line_height * len(SAMPLE) + 44
    header_height = 136
    image = Image.new(
        "RGB",
        (
            text_x + text_width + padding,
            header_height + row_height * len(FAMILIES) + 12,
        ),
        BACKGROUND,
    )
    draw = ImageDraw.Draw(image)
    draw.text(
        (padding, 30),
        "Moralerspace Community Edition",
        font=load_font(paths["Argon"], 36),
        fill=FOREGROUND,
        anchor="lt",
    )
    draw.text(
        (padding, 82),
        f"{version} / Regular / Standard width",
        font=load_font(paths["Argon"], 22),
        fill=MUTED,
        anchor="lt",
    )
    for index, (family, color) in enumerate(FAMILIES.items()):
        top = header_height + index * row_height
        draw.text(
            (padding, top + line_height * 2),
            family,
            font=labels[family],
            fill=color,
            anchor="lm",
        )
        for number, line in enumerate(SAMPLE):
            draw.text(
                (text_x, top + ascent + number * line_height),
                line,
                font=fonts[family],
                fill=color,
                anchor="ls",
                features=["calt", "liga"],
            )
    save_image(image, output / "sample.png", version)


def render_icons(paths: dict[str, Path], output: Path, version: str) -> None:
    size = 72
    with TTFont(paths["Argon"]) as font:
        cmap = font.getBestCmap()
        advance = font["hmtx"][cmap[ord("0")]][0]
        cell_width = size * advance / font["head"].unitsPerEm
    for family in ("Argon", "ArgonNFM"):
        with TTFont(paths[family]) as font:
            if any(font["hmtx"][font.getBestCmap()[cp]][0] != advance for cp in ICONS):
                raise ValueError(f"{family}: icons must have a one-cell advance")
    label = load_font(paths["Argon"], 28)
    small = load_font(paths["Argon"], 20)
    first_x = 220
    column_width = math.ceil(cell_width * 3)
    image = Image.new(
        "RGB", (first_x + column_width * len(ICONS) + 40, 414), BACKGROUND
    )
    draw = ImageDraw.Draw(image)
    draw.text((48, 24), "Nerd Font icons", font=label, fill=FOREGROUND, anchor="lt")
    draw.text(
        (48, 66),
        f"Moralerspace Argon {version} / 1-cell advance",
        font=small,
        fill=MUTED,
        anchor="lt",
    )
    for column, codepoint in enumerate(ICONS):
        draw.text(
            (first_x + column * column_width, 108),
            f"U+{codepoint:04X}",
            font=small,
            fill=MUTED,
            anchor="lt",
        )
    for row, (title, family) in enumerate((("Default", "Argon"), ("NFM", "ArgonNFM"))):
        font = load_font(paths[family], size)
        ascent, descent = font.getmetrics()
        top = 142 + row * 120
        draw.text(
            (48, top + (ascent + descent) / 2),
            title,
            font=label,
            fill=FOREGROUND,
            anchor="lm",
        )
        for column, codepoint in enumerate(ICONS):
            left = first_x + column * column_width
            draw.rectangle(
                (left, top, left + 2 * cell_width, top + ascent + descent),
                outline="#555555",
            )
            draw.rectangle(
                (left, top, left + cell_width, top + ascent + descent),
                fill="#18384e",
                outline="#4ea1ee",
            )
            draw.text(
                (left, top + ascent),
                chr(codepoint),
                font=font,
                fill=FOREGROUND,
                anchor="ls",
            )
    draw.text(
        (48, 382),
        "Blue: one character cell. Gray: neighboring cell.",
        font=small,
        fill=MUTED,
        anchor="lt",
    )
    save_image(image, output / "nerd-font-width.png", version)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fonts", type=Path, help="directory containing built TTF files")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets")
    args = parser.parse_args()
    if not features.check_feature("raqm"):
        parser.error("Pillow requires RAQM support for OpenType shaping")
    settings = configparser.ConfigParser()
    settings.read(ROOT / "build.ini", encoding="utf-8")
    version = settings["DEFAULT"]["VERSION"]
    try:
        paths = find_fonts(args.fonts, version)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        render_families(paths, args.output_dir, version)
        render_icons(paths, args.output_dir, version)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
