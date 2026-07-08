#!/usr/bin/env python3
"""Merge JetBrainsMono NFM Regular with LXGW WenKai GB Mono Regular."""

from fontTools.ttLib import TTFont


def merge_fonts(jb_path: str, lxgw_path: str, output_path: str, family_name: str = "JetBrainsMono LXGW Merged") -> None:
    """Merge LXGW CJK glyphs into JetBrainsMono base font."""
    print(f"Loading base font: {jb_path}")
    font = TTFont(jb_path)

    print(f"Loading CJK font: {lxgw_path}")
    lxgw = TTFont(lxgw_path)

    jb_cmap = font['cmap'].getBestCmap()
    lxgw_cmap = lxgw['cmap'].getBestCmap()
    jb_glyph_order = set(font.getGlyphOrder())

    imported = 0
    skipped = 0
    # Track mapping from LXGW glyph names to final names in merged font
    name_mapping = {}

    def copy_glyph(lxgw_gname: str) -> str:
        """Copy a glyph and its composite components recursively."""
        if lxgw_gname in name_mapping:
            return name_mapping[lxgw_gname]

        final_name = lxgw_gname
        if final_name in jb_glyph_order:
            final_name = f"lxgw_{lxgw_gname}"

        # Copy glyph and metrics
        font['glyf'][final_name] = lxgw['glyf'][lxgw_gname]
        font['hmtx'][final_name] = lxgw['hmtx'][lxgw_gname]
        jb_glyph_order.add(final_name)
        name_mapping[lxgw_gname] = final_name

        # Recursively copy composite components
        glyph = font['glyf'][final_name]
        if glyph.isComposite():
            for comp in glyph.components:
                comp_final_name = copy_glyph(comp.glyphName)
                comp.glyphName = comp_final_name

        return final_name

    for codepoint, lxgw_gname in lxgw_cmap.items():
        if codepoint > 0xFFFF:
            skipped += 1
            continue  # Skip non-BMP codepoints to avoid cmap format 4 overflow

        if codepoint in jb_cmap:
            skipped += 1
            continue  # JB already has this codepoint

        final_name = copy_glyph(lxgw_gname)

        # Update cmap for all unicode tables
        for table in font['cmap'].tables:
            if table.isUnicode():
                table.cmap[codepoint] = final_name

        imported += 1

    # Update maxp
    font['maxp'].numGlyphs = len(font.getGlyphOrder())

    # Set font names so DirectWrite can find the merged family
    full_name = f"{family_name} Regular"
    ps_name = f"{family_name.replace(' ', '')}-Regular"
    for record in font['name'].names:
        if record.nameID == 1:
            record.string = family_name
        elif record.nameID == 4:
            record.string = full_name
        elif record.nameID == 6:
            record.string = ps_name
        elif record.nameID == 16:
            record.string = family_name
        elif record.nameID == 17:
            record.string = "Regular"

    font.save(output_path)
    print(f"Saved merged font to {output_path}")
    print(f"  Imported glyphs: {imported}")
    print(f"  Skipped: {skipped}")
    print(f"  Total glyphs: {font['maxp'].numGlyphs}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: merge.py <jb-ttf> <lxgw-ttf> <output-ttf>")
        sys.exit(1)
    merge_fonts(sys.argv[1], sys.argv[2], sys.argv[3])
