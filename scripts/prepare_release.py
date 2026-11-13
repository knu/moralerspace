"""Extract manually maintained release notes and package a complete font build."""

import argparse
import configparser
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from markdown_it import MarkdownIt

VARIANTS = ("", "HW", "JPDOC", "HWJPDOC", "NFM", "HWNFM", "JPDOCNFM", "HWJPDOCNFM")
FAMILIES = ("Neon", "Argon", "Xenon", "Radon", "Krypton")
STYLES = ("Regular", "Bold", "Italic", "BoldItalic")


def release_notes(markdown: str, version: str) -> str:
    tokens = MarkdownIt().parse(markdown)
    headings = [
        (token.map, tokens[index + 1].content)
        for index, token in enumerate(tokens)
        if token.type == "heading_open" and token.level == 0 and token.tag == "h2"
    ]
    matches = [span for span, title in headings if title == version.removeprefix("v")]
    if len(matches) != 1:
        raise ValueError(f"expected one CHANGELOG section for {version}")
    span = matches[0]
    # A release section ends at the next top-level H1 or H2, not an H3 subsection.
    start = span[1]
    end = len(markdown.splitlines())
    for token in tokens:
        if (
            token.type == "heading_open"
            and token.level == 0
            and token.tag in ("h1", "h2")
            and token.map[0] >= start
        ):
            end = token.map[0]
            break
    notes = "\n".join(markdown.splitlines()[start:end]).strip()
    if not notes:
        raise ValueError(f"empty CHANGELOG section for {version}")
    return notes + "\n"


def package_fonts(build: Path, output: Path, name: str, version: str) -> None:
    manifests = {}
    for variant in VARIANTS:
        directory = build / f"{name}{variant}_{version}"
        expected = {
            f"{name}{family}{variant}-{style}.ttf"
            for family in FAMILIES
            for style in STYLES
        }
        if not directory.is_dir() or {p.name for p in directory.iterdir()} != expected:
            raise ValueError(f"incomplete font build: {directory}")
        manifests[directory] = sorted(directory.iterdir())
    output.mkdir(parents=True, exist_ok=True)
    for directory, fonts in manifests.items():
        with ZipFile(output / f"{directory.name}.zip", "w", ZIP_DEFLATED) as archive:
            for path in fonts:
                archive.write(path, f"{directory.name}/{path.name}")
            archive.write("LICENSE", f"{directory.name}/LICENSE")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("output", type=Path)
    parser.add_argument("--build", type=Path)
    args = parser.parse_args()
    settings = configparser.ConfigParser()
    settings.read("build.ini", encoding="utf-8")
    version = settings["DEFAULT"]["VERSION"]
    if not re.fullmatch(r"v\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", args.tag):
        parser.error(f"invalid version tag: {args.tag}")
    if args.tag != version:
        parser.error(f"tag {args.tag} does not match build.ini VERSION {version}")
    try:
        notes = release_notes(Path("CHANGELOG.md").read_text(encoding="utf-8"), version)
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "release-notes.md").write_text(notes, encoding="utf-8")
        if args.build:
            package_fonts(
                args.build, args.output, settings["DEFAULT"]["FONT_NAME"], version
            )
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
