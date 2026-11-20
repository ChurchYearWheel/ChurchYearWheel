"""The layout of a data CSV beyond its rows, so a page can write the file back
(page.js: csvText): its header line, its comment and blank lines and the rows
the reader skips (`notes`, each before the row it precedes), and those rows
whose own spelling a plain rewrite would change (`raw`).  A rewrite with no
edits gives the file back byte for byte (web/verify_edits.py checks this)."""

import csv
import io
from pathlib import Path


def cell_text(value: str) -> str:
    """One cell as the page writes it (page.js: csvCell): quoted only when it must be."""
    if any(c in value for c in ',"\n\r') or value != value.strip():
        return '"' + value.replace('"', '""') + '"'
    return value


def row_text(row: dict, cols: list) -> str:
    """A row as the page writes it (page.js: csvRow): every column, in the header's order."""
    return ",".join(cell_text(row.get(c, "")) for c in cols)


def _records(text: str):
    """(raw text, cells) of each CSV record, its lines as written."""
    lines = text.split("\n")
    reader = csv.reader(iter(lines))
    out, done = [], 0
    for cells in reader:
        out.append(("\n".join(lines[done:reader.line_num]), cells))
        done = reader.line_num
    return out


def layout(path: Path, kind: str) -> dict:
    """`kind` is "rows" (traditions.read_rows) or "readings" (export_data.reading_rows)."""
    text = path.read_text(encoding="utf-8")
    bom = text.startswith("﻿")
    if bom:
        text = text[1:]
    end = text.endswith("\n")
    body = text[:-1] if end else text
    if kind == "readings":
        lines = body.split("\n")
        recs = []
        for line in lines:
            if not line.strip() or line.lstrip().startswith(("#", '"#')):
                recs.append((line, None))
            else:
                recs.append((line, next(csv.reader(io.StringIO(line)), [])))
    else:
        recs = _records(body)
    # The header: the first line of the file (readings: the first that is not a comment).
    lead = []
    while kind == "readings" and recs and recs[0][1] is None:
        lead.append(recs.pop(0)[0])
    head_raw, header = recs.pop(0)
    cols = [(h or "").strip() for h in header]
    notes, raw, n = [], {}, 0
    for line in lead:
        notes.append([-1, line])
    for text_, cells in recs:
        row = None
        if cells is not None and cells:
            d = {}
            for k, v in zip(header, cells):
                d[(k or "").strip()] = (v or "").strip()
            for k in header[len(cells):]:
                d[(k or "").strip()] = ""
            values = list(d.values())
            if kind == "readings":
                if d.get("kind") == "omit" or (d.get("day") and d.get("reading")):
                    row = d
            elif any(values) and not values[0].startswith("#"):
                row = d
        if row is None:
            notes.append([n, text_])
            continue
        if row_text(row, cols) != text_:
            raw[str(n)] = text_
        n += 1
    out = {"head": head_raw, "cols": cols, "n": n}
    if notes:
        out["notes"] = notes
    if raw:
        out["raw"] = raw
    if bom:
        out["bom"] = True
    if not end:
        out["open"] = True
    return out


def write(lay: dict, rows: list) -> str:
    """The file again from its rows (page.js: csvText)."""
    lines = [n[1] for n in lay.get("notes", []) if n[0] == -1]
    lines.append(lay["head"])
    notes = {}
    for i, t in lay.get("notes", []):
        if i >= 0:
            notes.setdefault(i, []).append(t)
    raw = lay.get("raw", {})
    for i, row in enumerate(rows):
        lines += notes.get(i, [])
        lines.append(raw.get(str(i), row_text(row, lay["cols"])))
    lines += notes.get(len(rows), [])
    text = "\n".join(lines) + ("" if lay.get("open") else "\n")
    return ("﻿" if lay.get("bom") else "") + text
