#!/usr/bin/env python3
"""Patch U+23F8 pause symbol into a target font using built-in glyph asset."""

from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen

CODEPOINT = 0x23F8
DEFAULT_GLYPH_NAME = "uni23F8"


def patch_font(target_path: str, glyph_asset_path: str, output_path: str, glyph_name: str = DEFAULT_GLYPH_NAME) -> None:
    """Insert built-in U+23F8 glyph into target font."""
    print(f"Patching U+23F8 into {target_path}")
    target = TTFont(target_path)
    src = TTFont(glyph_asset_path)

    src_cmap = src['cmap'].getBestCmap()
    if CODEPOINT not in src_cmap:
        raise ValueError(f"Glyph asset does not contain U+{CODEPOINT:04X}")

    src_glyph_name = src_cmap[CODEPOINT]
    src_glyph = src['glyf'][src_glyph_name]

    scale = target['head'].unitsPerEm / src['head'].unitsPerEm
    if scale != 1.0:
        print(f"Warning: UPM mismatch, scaling glyph by {scale}")

    pen = TTGlyphPen(None)
    transform_pen = TransformPen(pen, (scale, 0, 0, scale, 0, 0))
    src_glyph.draw(transform_pen, src['glyf'])
    new_glyph = pen.glyph()

    target['glyf'][glyph_name] = new_glyph
    src_width, src_lsb = src['hmtx'][src_glyph_name]
    target['hmtx'][glyph_name] = (int(round(src_width * scale)), int(round(src_lsb * scale)))

    updated = 0
    for table in target['cmap'].tables:
        if table.isUnicode():
            table.cmap[CODEPOINT] = glyph_name
            updated += 1

    target['maxp'].numGlyphs = len(target.getGlyphOrder())
    target.save(output_path)

    print(f"Saved patched font to {output_path}")
    print(f"  U+{CODEPOINT:04X} -> {glyph_name}, width={target['hmtx'][glyph_name][0]}")
    print(f"  Updated {updated} cmap table(s)")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: patch_u23f8.py <target-ttf> <glyph-asset-ttf> <output-ttf>")
        sys.exit(1)
    patch_font(sys.argv[1], sys.argv[2], sys.argv[3])
