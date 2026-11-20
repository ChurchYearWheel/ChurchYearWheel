#!/usr/bin/env python3
"""Write lib/font_widths.py: the advance widths, in thousandths of an em, of
every character beyond ASCII that the calendars' names use, in the eight faces
the wheel measures text with (church_year_image.py: TextMeasurer).

The widths are read from the Liberation fonts, which are metric-compatible
with Times New Roman and Arial: a letter is as wide in either.  ASCII is in
church_year_image.py's own table; without these, an accented capital or a Cyrillic
letter was taken as half an em, and a line of them ("PYHÄINPÄIVÄ",
"РІЗДВО ХРИСТОВЕ") could be fitted to a cell it then ran out of.

    python tools/font_widths.py [--fonts DIR]

Run it again when a calendar brings letters not yet in the table; characters
the table lacks are still taken as half an em.
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
FACES = {
    "serif|normal|normal": "LiberationSerif-Regular",
    "serif|bold|normal": "LiberationSerif-Bold",
    "serif|normal|italic": "LiberationSerif-Italic",
    "serif|bold|italic": "LiberationSerif-BoldItalic",
    "sans|normal|normal": "LiberationSans-Regular",
    "sans|bold|normal": "LiberationSans-Bold",
    "sans|normal|italic": "LiberationSans-Italic",
    "sans|bold|italic": "LiberationSans-BoldItalic",
}


def used_characters() -> set[str]:
    """Every character past ASCII in the CSV files under data/, with the
    capitals of the small letters (small capitals are drawn as capitals)."""
    chars = set()
    for path in (HERE / "data").rglob("*.csv"):
        chars |= {c for c in path.read_text(encoding="utf-8-sig") if ord(c) > 126}
    for c in list(chars):
        chars |= {u for u in c.upper() if ord(u) > 126}
    return chars


def main() -> int:
    from fontTools.ttLib import TTFont
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--fonts", default="/usr/share/fonts/truetype/liberation",
                   help="the folder holding the Liberation Serif and Sans .ttf files")
    a = p.parse_args()
    chars = sorted(used_characters())
    out = ['"""Advance widths beyond ASCII, in thousandths of an em, by face: written by',
           'tools/font_widths.py from the Liberation fonts (metric-compatible with Times',
           'New Roman and Arial).  Do not edit by hand."""', "", "EXTRA_WIDTHS = {"]
    for face, name in FACES.items():
        font = TTFont(Path(a.fonts) / f"{name}.ttf")
        cmap, hmtx, upm = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
        pairs = [f"{ord(c)}:{round(hmtx[cmap[ord(c)]][0] * 1000 / upm)}"
                 for c in chars if ord(c) in cmap]
        out.append(f'    "{face}":')
        line = '        "'
        for i, pair in enumerate(pairs):
            piece = pair + ("," if i < len(pairs) - 1 else "")
            if len(line) + len(piece) > 98:
                out.append(line + '"')
                line = '        "'
            line += piece
        out.append(line + '",')
    out.append("}")
    (HERE / "lib" / "font_widths.py").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"✓ lib/font_widths.py: {len(chars)} characters", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
