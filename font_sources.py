"""Prepare the source fonts pinned by source_fonts/versions.ini."""

from __future__ import annotations

import configparser
import hashlib
import re
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from zipfile import ZipFile

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "build_sources"
FAMILIES = ("Neon", "Argon", "Xenon", "Radon", "Krypton")
STYLES = ("Regular", "Bold", "Italic", "BoldItalic")
RELEASES = {
    "monaspace",
    "ibm-plex-sans-jp",
    "source-han-serif",
    "hack",
    "nerd-fonts",
}
REVISIONS = {"kiwimaru", "stick"}


def source_directory() -> Path:
    settings = configparser.ConfigParser()
    settings.read(ROOT / "build.ini", encoding="utf-8")
    return ROOT / settings["DEFAULT"]["SOURCE_FONTS_DIR"]


def read_versions(path: Path) -> configparser.ConfigParser:
    versions = configparser.ConfigParser(interpolation=None)
    with path.open(encoding="utf-8") as file:
        versions.read_file(file)
    for section, keys, pattern in (
        ("releases", RELEASES, r"v?\d+(?:\.\d+){1,2}"),
        ("revisions", REVISIONS, r"[a-f0-9]{40}"),
    ):
        if section not in versions or set(versions[section]) != keys:
            raise ValueError(f"{path}: invalid {section} entries")
        for key, value in versions[section].items():
            if not re.fullmatch(pattern, value):
                raise ValueError(f"{path}: invalid {key} version")
    return versions


def prepared_directory() -> Path:
    digest = hashlib.sha256()
    for path in (
        source_directory() / "versions.ini",
        source_directory() / "ideographic_space.sfd",
        Path(__file__),
        ROOT / "make_bold.py",
    ):
        digest.update(path.read_bytes())
    return CACHE / digest.hexdigest()


def raw_url(repository: str, ref: str, path: str) -> str:
    return (
        f"https://raw.githubusercontent.com/{repository}/"
        f"{quote(ref, safe='')}/{quote(path, safe='/')}"
    )


def source_urls(versions: configparser.ConfigParser) -> dict[str, str]:
    releases = versions["releases"]
    revisions = versions["revisions"]
    sources = {}
    for family in FAMILIES:
        for style in STYLES:
            sources[f"monaspace/Monaspace{family}-{style}.otf"] = raw_url(
                "githubnext/monaspace",
                releases["monaspace"],
                f"fonts/NerdFonts/Monaspace {family}/Monaspace{family}NF-{style}.otf",
            )
    for style in ("Text", "Medium", "Bold"):
        sources[f"ibm-plex-sans-jp/IBMPlexSansJP-{style}.ttf"] = raw_url(
            "IBM/plex",
            f"@ibm/plex-sans-jp@{releases['ibm-plex-sans-jp']}",
            f"packages/plex-sans-jp/fonts/complete/ttf/hinted/IBMPlexSansJP-{style}.ttf",
        )
    for style in ("Regular", "Bold"):
        sources[f"source-han-serif/SourceHanSerifJP-{style}.otf"] = raw_url(
            "adobe-fonts/source-han-serif",
            f"{releases['source-han-serif']}R",
            f"SubsetOTF/JP/SourceHanSerifJP-{style}.otf",
        )
    for style in STYLES:
        sources[f"hack/Hack-{style}.ttf"] = raw_url(
            "source-foundry/Hack", releases["hack"], f"build/ttf/Hack-{style}.ttf"
        )
    for directory, repository, name in (
        ("kiwimaru", "Kiwi-KawagotoKajiru/Kiwi-Maru", "KiwiMaru-Medium.ttf"),
        ("stick", "fontworks-fonts/Stick", "Stick-Regular.ttf"),
    ):
        sources[f"{directory}/{name}"] = raw_url(
            repository, revisions[directory], f"fonts/ttf/{name}"
        )
    for directory, repository, ref, license_path in (
        ("monaspace", "githubnext/monaspace", releases["monaspace"], "LICENSE"),
        (
            "ibm-plex-sans-jp",
            "IBM/plex",
            f"@ibm/plex-sans-jp@{releases['ibm-plex-sans-jp']}",
            "packages/plex-sans-jp/LICENSE.txt",
        ),
        (
            "source-han-serif",
            "adobe-fonts/source-han-serif",
            f"{releases['source-han-serif']}R",
            "LICENSE.txt",
        ),
        ("hack", "source-foundry/Hack", releases["hack"], "LICENSE.md"),
        ("kiwimaru", "Kiwi-KawagotoKajiru/Kiwi-Maru", revisions["kiwimaru"], "OFL.txt"),
        ("stick", "fontworks-fonts/Stick", revisions["stick"], "OFL.txt"),
    ):
        sources[f"{directory}/LICENSE"] = raw_url(repository, ref, license_path)
    return sources


def download(url: str) -> Path:
    directory = CACHE / "downloads"
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / hashlib.sha256(url.encode()).hexdigest()
    if destination.is_file():
        return destination
    print(f"Downloading {url}", file=sys.stderr)
    request = Request(url, headers={"User-Agent": "Moralerspace font builder"})
    with tempfile.NamedTemporaryFile(dir=directory, delete=False) as file:
        temporary = Path(file.name)
        try:
            with urlopen(request, timeout=60) as response:
                shutil.copyfileobj(response, file)
                length = response.headers.get("Content-Length")
                if length is not None and file.tell() != int(length):
                    raise ValueError(f"incomplete download: {url}")
            file.close()
            temporary.replace(destination)
        except OSError as error:
            raise OSError(f"{url}: {error}") from error
        finally:
            temporary.unlink(missing_ok=True)
    return destination


def unpack_symbols(archive: Path, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive) as zip_file:
        for name in ("SymbolsNerdFont-Regular.ttf", "LICENSE"):
            with zip_file.open(name) as source, (directory / name).open("wb") as output:
                shutil.copyfileobj(source, output)


def prepare_fonts() -> Path:
    versions = read_versions(source_directory() / "versions.ini")
    destination = prepared_directory()
    if (destination / ".complete").is_file():
        return destination
    CACHE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=CACHE, prefix="prepare-") as temporary:
        staging = Path(temporary) / "fonts"
        staging.mkdir()
        sources = source_urls(versions)
        with ThreadPoolExecutor(max_workers=4) as executor:
            for (name, _), downloaded in zip(
                sources.items(), executor.map(download, sources.values())
            ):
                path = staging / name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(downloaded, path)
        version = versions["releases"]["nerd-fonts"]
        archive = download(
            "https://github.com/ryanoasis/nerd-fonts/releases/download/"
            f"{quote(version, safe='')}/NerdFontsSymbolsOnly.zip"
        )
        unpack_symbols(archive, staging / "nerd-fonts")
        for path in (*staging.rglob("*.ttf"), *staging.rglob("*.otf")):
            with TTFont(path) as font:
                if not font.getBestCmap():
                    raise ValueError(f"{path}: missing character map")
        from make_bold import prepare_derived_fonts

        prepare_derived_fonts(staging)
        for name in ("ideographic_space.sfd", "versions.ini"):
            shutil.copyfile(source_directory() / name, staging / name)
        (staging / ".complete").touch()
        try:
            staging.rename(destination)
        except OSError:
            if not (destination / ".complete").is_file():
                raise
    return destination


if __name__ == "__main__":
    try:
        print(prepare_fonts())
    except (OSError, ValueError) as error:
        sys.exit(f"font sources: {error}")
