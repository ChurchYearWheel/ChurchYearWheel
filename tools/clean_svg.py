"""Tidy a Commons SVG for use as center artwork.

Drops editor-only content (Inkscape/Sodipodi elements and attributes, RDF
metadata, comments), prefixes every id so it can't collide with the page's own,
and rounds coordinates to two decimals.  The drawing itself is unchanged.

    python clean_svg.py IN.svg OUT.svg PREFIX
"""

if __name__ == "__main__":
    import _cli
    _cli.check(__doc__, 3)
import re, sys
import xml.etree.ElementTree as ET

SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"
EDITOR = ("http://www.inkscape.org/namespaces/inkscape",
          "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
NUM = re.compile(r"(?<![#\w.])-?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")

def rnd(text):
    def fix(m):
        s = m.group(0)
        if "." not in s and "e" not in s.lower():
            return s
        v = round(float(s), 2)
        out = f"{v:.2f}".rstrip("0").rstrip(".")
        return "0" if out in ("-0", "") else out
    return NUM.sub(fix, text)

def main(src, dst, prefix):
    ET.register_namespace("", SVG)
    ET.register_namespace("xlink", XLINK)
    tree = ET.parse(src)
    root = tree.getroot()

    def editor(tag):
        return tag.startswith("{") and (tag[1:].split("}")[0] in EDITOR
                                        or tag == f"{{{SVG}}}metadata")
    for parent in list(root.iter()):
        for child in list(parent):
            if not isinstance(child.tag, str) or editor(child.tag):
                parent.remove(child)

    ids = {el.get("id") for el in root.iter() if el.get("id")}
    for el in root.iter():
        for name in list(el.attrib):
            if name.startswith("{") and name[1:].split("}")[0] in EDITOR:
                del el.attrib[name]
        for name, value in list(el.attrib.items()):
            if name == "id":
                value = prefix + value
            elif name in ("d", "points", "x", "y", "x1", "y1",
                          "x2", "y2", "cx", "cy", "r", "fx", "fy", "rx", "ry", "width",
                          "height", "stroke-width", "viewBox"):
                value = rnd(value)
            if "url(#" in value:
                value = re.sub(r"url\(#([^)]+)\)",
                               lambda m: f"url(#{prefix + m.group(1) if m.group(1) in ids else m.group(1)})",
                               value)
            if name in (f"{{{XLINK}}}href", "href") and value.startswith("#") and value[1:] in ids:
                value = "#" + prefix + value[1:]
            el.set(name, value)
    # Unused id attributes on groups and paths are just weight.
    used = set()
    text = ET.tostring(root, encoding="unicode")
    used.update(re.findall(r"url\(#([^)]+)\)", text))
    used.update(re.findall(r'href="#([^"]+)"', text))
    for el in root.iter():
        if el.get("id") and el.get("id") not in used:
            del el.attrib["id"]
    for el in root.iter():
        if el.text and not el.text.strip():
            el.text = None
        if el.tail and not el.tail.strip():
            el.tail = None
    body = ET.tostring(root, encoding="unicode")
    open(dst, "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n")
    print(dst, len(body.encode()))

main(*sys.argv[1:])
