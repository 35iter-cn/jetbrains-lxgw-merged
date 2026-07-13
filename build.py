#!/usr/bin/env python3
"""Build JetBrainsMono LXGW Merged font."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from download import DEFAULT_JB_URL, DEFAULT_LXGW_URL, download, extract_jb_mono
from merge import merge_fonts
from patch_u23f8 import patch_font


def main():
    parser = argparse.ArgumentParser(description="Build JetBrainsMono LXGW Merged font")
    parser.add_argument("--jb-url", default=DEFAULT_JB_URL, help="JetBrainsMono Nerd Fonts zip URL")
    parser.add_argument("--lxgw-url", default=DEFAULT_LXGW_URL, help="LXGW WenKai GB Mono Regular URL")
    parser.add_argument("--cache-dir", default=".cache", help="Directory to cache downloaded files")
    parser.add_argument("--dist-dir", default="dist", help="Output directory")
    parser.add_argument("--family-name", default="JetBrainsMono LXGW Merged", help="Output font family name")
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading, use cached files")
    args = parser.parse_args()

    cache_dir = Path(args.cache_dir)
    dist_dir = Path(args.dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)

    jb_zip = cache_dir / "JetBrainsMono.zip"
    jb_ttf = cache_dir / "JetBrainsMonoNerdFontMono-Regular.ttf"
    lxgw_ttf = cache_dir / "LXGWWenKaiMonoGB-Regular.ttf"

    if not args.skip_download:
        if not jb_zip.exists():
            download(args.jb_url, jb_zip)
        else:
            print(f"Using cached {jb_zip}")
        jb_ttf = extract_jb_mono(jb_zip, cache_dir)

        if not lxgw_ttf.exists():
            download(args.lxgw_url, lxgw_ttf)
        else:
            print(f"Using cached {lxgw_ttf}")
    else:
        if not jb_ttf.exists():
            raise FileNotFoundError(f"{jb_ttf} not found, run without --skip-download first")
        if not lxgw_ttf.exists():
            raise FileNotFoundError(f"{lxgw_ttf} not found, run without --skip-download first")

    merged_ttf = dist_dir / "JetBrainsMono-LXGW-Merged-merged.ttf"
    output_ttf = dist_dir / "JetBrainsMono-LXGW-Merged.ttf"

    glyph_assets = [
        ("u23f8-glyph.ttf", "U+23F8 pause (⏸) — Claude Code Plan mode"),
        ("u23f5-glyph.ttf", "U+23F5 play (⏵) — Claude Code Bypass mode"),
    ]
    for asset_name, description in glyph_assets:
        asset_path = Path(__file__).parent / "assets" / asset_name
        if not asset_path.exists():
            raise FileNotFoundError(f"Built-in glyph asset not found: {asset_path}  ({description})")

    merge_fonts(str(jb_ttf), str(lxgw_ttf), str(merged_ttf), family_name=args.family_name)

    # Apply all symbol patches in sequence, each reading the next intermediate file
    current = str(merged_ttf)
    for asset_name, description in glyph_assets:
        asset_path = Path(__file__).parent / "assets" / asset_name
        next_output = str(output_ttf)
        patch_font(current, str(asset_path), next_output)
        current = next_output

    # Clean up intermediate merged file
    merged_ttf.unlink(missing_ok=True)

    print(f"\nBuild complete: {output_ttf}")


if __name__ == "__main__":
    main()
