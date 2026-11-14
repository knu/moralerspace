"""Build representative fonts for pull-request checks."""

import argparse
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from font_sources import prepare_fonts

CASES = (
    ("Argon", "Regular", "", ()),
    ("Argon", "Regular", "HW", ("--half-width",)),
    ("Argon", "Regular", "NFM", ("--nerd-font-mono",)),
    ("Argon", "Regular", "HWNFM", ("--half-width", "--nerd-font-mono")),
    ("Xenon", "Regular", "", ()),
    ("Radon", "Bold", "", ()),
    ("Krypton", "Bold", "", ()),
)


def build_case(case: tuple, environment: dict) -> None:
    family, style, variant, flags = case
    subprocess.run(
        [
            sys.executable,
            "fontforge_script.py",
            "--do-not-delete-build-dir",
            "--family",
            family,
            "--style",
            style,
            *flags,
        ],
        cwd=ROOT,
        env=environment,
        check=True,
    )
    subprocess.run(
        [sys.executable, "fonttools_script.py", f"{variant}-", "--family", family],
        cwd=ROOT,
        env=environment,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "build/smoke")
    args = parser.parse_args()
    directory = args.output_dir.resolve()
    if directory.exists() and any(directory.iterdir()):
        parser.error(f"output directory is not empty: {directory}")
    directory.mkdir(parents=True, exist_ok=True)
    sources = prepare_fonts()
    environment = {**os.environ, "MORALERSPACE_BUILD_DIR": str(directory)}
    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(lambda case: build_case(case, environment), CASES))
    shutil.copyfile(sources / "versions.ini", directory / "source-versions.ini")
    print(directory)


if __name__ == "__main__":
    main()
