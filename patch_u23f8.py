#!/usr/bin/env python3
"""Patch Unicode symbols into a target font using built-in glyph assets.

Used by the build pipeline to add missing symbols like U+23F8 (⏸ pause,
Claude Code Plan mode indicator) and U+23F5 (⏵ play, Claude Code
Bypass Permissions indicator).

The codepoint and glyph name are read dynamically from the asset font,
so any single-glyph symbol TTF works.
"""

from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen


def patch_font(target_path: str, glyph_asset_path: str, output_path: str) -> None:
    """Insert a symbol glyph from an asset font into the target font.

    The codepoint and glyph name are read dynamically from the asset's
    cmap table (the first Unicode mapping found).
    """
    target = TTFont(target_path)
    src = TTFont(glyph_asset_path)

    src_cmap = src['cmap'].getBestCmap()
    if not src_cmap:
        raise ValueError(f"Glyph asset has no Unicode mappings: {glyph_asset_path}")

    # Pick the first codepoint from the asset
    codepoint = next(iter(src_cmap.keys()))
    glyph_name = src_cmap[codepoint]

    # Ensure glyph name is unique in the target
    target_glyph_name = glyph_name
    if target_glyph_name in target.getGlyphOrder():
        target_glyph_name = f"lxgw_{glyph_name}"

    print(f"Patching U+{codepoint:04X} ({chr(codepoint)}) from {glyph_asset_path} into {target_path}")

    src_glyph = src['glyf'][glyph_name]

    scale = target['head'].unitsPerEm / src['head'].unitsPerEm
    if scale != 1.0:
        print(f"  Scaling glyph by {scale} (target UPM={target['head'].unitsPerEm}, src UPM={src['head'].unitsPerEm})")

    pen = TTGlyphPen(None)
    transform_pen = TransformPen(pen, (scale, 0, 0, scale, 0, 0))
    src_glyph.draw(transform_pen, src['glyf'])
    new_glyph = pen.glyph()

    target['glyf'][target_glyph_name] = new_glyph
    src_width, src_lsb = src['hmtx'][glyph_name]
    target['hmtx'][target_glyph_name] = (int(round(src_width * scale)), int(round(src_lsb * scale)))

    updated = 0
    for table in target['cmap'].tables:
        if table.isUnicode():
            table.cmap[codepoint] = target_glyph_name
            updated += 1

    target['maxp'].numGlyphs = len(target.getGlyphOrder())
    target.save(output_path)

    print(f"  Saved patched font to {output_path}")
    print(f"  U+{codepoint:04X} -> '{target_glyph_name}', width={target['hmtx'][target_glyph_name][0]}")
    print(f"  Updated {updated} cmap table(s)")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: patch_u23f8.py <target-ttf> <glyph-asset-ttf> <output-ttf>")
        sys.exit(1)
    patch_font(sys.argv[1], sys.argv[2], sys.argv[3])
