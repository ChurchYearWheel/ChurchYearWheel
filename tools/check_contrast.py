"""List any color whose text color is not the more readable of black and white.

    python3 tools/check_contrast.py

Reads data/colors.csv and every tradition's colors.csv, and reports each color
whose `text` has less contrast with its `fill` (WCAG contrast ratio) than the
other of black and white would.
"""

if __name__ == "__main__":
    import _cli
    _cli.check(__doc__, 0)
import csv
import glob


def luminance(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    hi, lo = sorted([luminance(a), luminance(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


bad = 0
for path in ["data/colors.csv"] + sorted(glob.glob("data/*/colors.csv")):
    for line in open(path, encoding="utf-8"):
        if line.startswith(("#", '"#', "name,")):
            continue
        row = next(csv.reader([line]))
        if len(row) < 3 or not row[1].startswith("#") or not row[2].startswith("#"):
            continue
        best = "#000000" if contrast(row[1], "#000000") >= contrast(row[1], "#ffffff") else "#ffffff"
        if row[2].lower() != best:
            bad += 1
            print(f"{path}: {row[0]} {row[1]} has text {row[2]} "
                  f"({contrast(row[1], row[2]):.1f}:1); {best} gives {contrast(row[1], best):.1f}:1")
print(f"{bad} color(s) could be more readable")
