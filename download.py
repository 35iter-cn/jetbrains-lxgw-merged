#!/usr/bin/env python3
"""Download source fonts for JetBrainsMono LXGW Merged."""

import argparse
import os
import shutil
import zipfile
from pathlib import Path

import requests

DEFAULT_JB_URL = "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/JetBrainsMono.zip"
DEFAULT_LXGW_URL = "https://github.com/lxgw/LxgwWenkaiGB/releases/download/v1.522/LXGWWenKaiMonoGB-Regular.ttf"


def download(url: str, dest: Path, chunk_size: int = 8192) -> None:
    """Download a file with progress."""
    print(f"Downloading {url} ...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
    print(f"Saved to {dest}")


def extract_jb_mono(zip_path: Path, dest_dir: Path) -> Path:
    """Extract JetBrainsMonoNerdFontMono-Regular.ttf from Nerd Fonts zip."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        target = None
        for name in zf.namelist():
            if name.endswith("JetBrainsMonoNerdFontMono-Regular.ttf"):
                target = name
                break
        if not target:
            raise FileNotFoundError("JetBrainsMonoNerdFontMono-Regular.ttf not found in zip")
        zf.extract(target, dest_dir)
        extracted = dest_dir / target
        final = dest_dir / "JetBrainsMonoNerdFontMono-Regular.ttf"
        shutil.move(extracted, final)
        # Clean up empty subdirectories
        subdir = extracted.parent
        while subdir != dest_dir:
            if subdir.exists() and not any(subdir.iterdir()):
                subdir.rmdir()
            subdir = subdir.parent
    print(f"Extracted JetBrainsMono NFM Regular to {final}")
    return final


def main():
    parser = argparse.ArgumentParser(description="Download font sources")
    parser.add_argument("--jb-url", default=DEFAULT_JB_URL, help="JetBrainsMono Nerd Fonts zip URL")
    parser.add_argument("--lxgw-url", default=DEFAULT_LXGW_URL, help="LXGW WenKai GB Mono Regular URL")
    parser.add_argument("--cache-dir", default=".cache", help="Directory to cache downloaded files")
    args = parser.parse_args()

    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    jb_zip = cache_dir / "JetBrainsMono.zip"
    if not jb_zip.exists():
        download(args.jb_url, jb_zip)
    else:
        print(f"Using cached {jb_zip}")

    jb_ttf = extract_jb_mono(jb_zip, cache_dir)

    lxgw_ttf = cache_dir / "LXGWWenKaiMonoGB-Regular.ttf"
    if not lxgw_ttf.exists():
        download(args.lxgw_url, lxgw_ttf)
    else:
        print(f"Using cached {lxgw_ttf}")

    print(f"\nSources ready:")
    print(f"  JB:  {jb_ttf}")
    print(f"  LXGW: {lxgw_ttf}")


if __name__ == "__main__":
    main()
