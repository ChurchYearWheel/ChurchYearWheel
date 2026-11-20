#!/usr/bin/env python3
"""Write docs/provenance.md from docs/provenance.csv.

docs/provenance.csv is the record of where each calendar's data come from:
one row per claim, with the churches it covers (traditions.csv keys, or
`all`), the aspect (days, feasts, colors, names, readings, art, other), its
status, what part, the source and notes.  This script checks the keys and
words and renders the same rows three ways: a table of churches by aspect,
the open items (gaps and guesses) by aspect, and every row by church.

    python3 tools/provenance.py            # write docs/provenance.md
    python3 tools/provenance.py --check    # only check the CSVs

docs/source-errors.csv lists mistakes found in the sources and what the
calendar uses instead; it is rendered as its own section.
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "docs" / "provenance.csv"
ERRORS = ROOT / "docs" / "source-errors.csv"
OUT = ROOT / "docs" / "provenance.md"

ASPECTS = ["days", "feasts", "colors", "names", "readings", "art", "other"]
# Worst first.
STATUSES = ["missing", "guess", "uncited", "inferred", "partial", "sourced"]
MARK = {"sourced": "✓", "partial": "◐", "inferred": "≈", "uncited": "?", "guess": "~", "missing": "✗"}
MEANING = {
    "sourced": "taken from the source named",
    "partial": "from the source named, with known pieces missing",
    "inferred": "worked out from a source's rules, or borrowed from a related church, rather than stated outright",
    "uncited": "stated as fact, but no source is named yet",
    "guess": "a choice or assumption made without a source",
    "missing": "not in the calendar yet",
}
OPEN = ["missing", "guess", "uncited", "partial"]


def traditions():
    out = []
    with open(ROOT / "data" / "traditions.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key = (r.get("key") or "").strip()
            if key and not key.startswith("#"):
                out.append((key, r.get("label", key), r.get("tradition", "")))
    return out


def load():
    with open(CSV, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_errors():
    """docs/source-errors.csv: mistakes found in a source, and what the calendar uses instead."""
    if not ERRORS.exists():
        return []
    with open(ERRORS, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check(rows, keys):
    bad = []
    for i, r in enumerate(rows, start=2):
        for k in r["church"].split():
            if k != "all" and k not in keys:
                bad.append(f"line {i}: unknown church {k!r}")
        if r["aspect"] not in ASPECTS:
            bad.append(f"line {i}: unknown aspect {r['aspect']!r}")
        if r["status"] not in STATUSES:
            bad.append(f"line {i}: unknown status {r['status']!r}")
        if r.get(None):
            bad.append(f"line {i}: more fields than the header (a comma that needs quotes?)")
    return bad


URL = re.compile(r"https?://[^\s<>\"]+")


def short_link(m):
    """A bare URL as a link named by its site, so a long address does not
    widen the table past the reader's screen: [site](address)."""
    url = m.group(0)
    tail = ""
    while url and (url[-1] in ".,;:" or (url[-1] == ")" and url.count("(") < url.count(")"))):
        url, tail = url[:-1], url[-1] + tail
    site = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
    path = url.split(site, 1)[-1].strip("/")
    name = site + ("/…" if path else "")
    return f"[{name}]({url.replace(' ', '%20').replace(')', '%29').replace('(', '%28')}){tail}"


def cell(text):
    text = str(text or "").replace("|", "\\|").replace("\n", " ").strip()
    return URL.sub(short_link, text)


def render(rows, trads, errors=()):
    label = {k: lab for k, lab, _ in trads}
    lines = ["# Sources, gaps and guesses", "",
             "Where each calendar's days, feasts, colors, names, readings and artwork come from, "
             "and what is still missing or guessed. **Edit `docs/provenance.csv`, then run "
             "`python3 tools/provenance.py`**; this page is written from it. Where the calendar's data "
             "disagree with a source, the item waits in [provenance-review.md](provenance-review.md).", "",
             "Each row of the CSV is one claim: `church` (one or more keys from `data/traditions.csv`, "
             "or `all`), `aspect`, `status`, `detail` (which part), `source` and `notes`. "
             "The status is one of:", ""]
    for s in reversed(STATUSES):
        lines.append(f"- {MARK[s]} **{s}**: {MEANING[s]}")
    lines += ["", "The comments at the head of each data file give the same sources in more detail; "
              "CHANGELOG.md says when each was added.", "",
              "## By church and aspect", "",
              "Each cell shows the statuses of that church's rows for the aspect, best first: "
              "✓✗ is a sourced aspect with a known gap; a blank is no row yet. Rows for all calendars "
              "(the color palette, the icons, the artwork credits) are left out of this table.", "",
              "| Church | " + " | ".join(a.capitalize() for a in ASPECTS) + " |",
              "|---|" + "---|" * len(ASPECTS)]
    for key, lab, _trad in trads:
        marks = []
        for a in ASPECTS:
            st = {r["status"] for r in rows if r["aspect"] == a and key in r["church"].split()}
            marks.append("".join(MARK[s] for s in reversed(STATUSES) if s in st))
        lines.append(f"| [{cell(lab)}](#{key}) | " + " | ".join(marks) + " |")
    lines += ["", "## Open items", "",
              "Everything that is missing, guessed, uncited or partial, by aspect.", ""]
    for a in ASPECTS:
        items = [r for r in rows if r["aspect"] == a and r["status"] in OPEN]
        if not items:
            continue
        lines += [f"### {a.capitalize()}", "", "| Church | Status | What | Notes |", "|---|---|---|---|"]
        items.sort(key=lambda r: (OPEN.index(r["status"]), r["church"]))
        for r in items:
            who = ", ".join(label.get(k, k) for k in r["church"].split())
            lines.append(f"| {cell(who)} | {MARK[r['status']]} {r['status']} | {cell(r['detail'])} | {cell(r['notes'])} |")
        lines.append("")
    if errors:
        lines += ["## Errors found in sources", "",
                  "Where a source misprints a reading or a date, the calendar uses the corrected text. "
                  "Each row names the source, what it has, what the calendar uses and why. "
                  "**Edit `docs/source-errors.csv`.** A published book is preferred to a website "
                  "unless the church has changed its use since the book was printed.", "",
                  "| Church | Source | What | Source has | Calendar uses | Basis |", "|---|---|---|---|---|---|"]
        for e in errors:
            who = ", ".join(label.get(k, k) for k in e["church"].split())
            lines.append(f"| {cell(who)} | {cell(e['source'])} | {cell(e['what'])} | {cell(e['source_has'])} | "
                         f"{cell(e['used'])} | {cell(e['basis'])} |")
        lines.append("")
    lines += ["## By church", ""]
    shared = [r for r in rows if r["church"].strip() == "all"]
    if shared:
        lines += ["### All calendars", ""] + table(shared) + [""]
    family = None
    for key, lab, trad in trads:
        if trad != family:
            family = trad
        mine = [r for r in rows if key in r["church"].split()]
        lines += [f'<a id="{key}"></a>', f"### {lab}", "", f"`{key}` · {trad}", ""]
        lines += (table(mine) if mine else ["No rows yet."]) + [""]
    return "\n".join(lines) + "\n"


def table(rows):
    out = ["| Aspect | Status | What | Source | Notes |", "|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (ASPECTS.index(r["aspect"]), STATUSES.index(r["status"]))):
        out.append(f"| {r['aspect']} | {MARK[r['status']]} {r['status']} | {cell(r['detail'])} | "
                   f"{cell(r['source'])} | {cell(r['notes'])} |")
    return out


def main(argv):
    if any(a in ("-h", "--help") for a in argv) or any(a != "--check" for a in argv):
        print((__doc__ or "").strip())
        return 0 if all(a in ("-h", "--help", "--check") for a in argv) else 2
    trads = traditions()
    rows = load()
    errors = load_errors()
    keys = {k for k, _, _ in trads}
    bad = check(rows, keys)
    bad += [f"source-errors.csv line {i}: unknown church {k!r}" for i, e in enumerate(errors, start=2)
            for k in e["church"].split() if k not in keys]
    bad += [f"source-errors.csv line {i}: more fields than the header (a comma that needs quotes?)"
            for i, e in enumerate(errors, start=2) if e.get(None)]
    if bad:
        print("\n".join(bad))
        return 1
    if "--check" in argv:
        print(f"✓ {len(rows)} rows, {len(errors)} source errors")
        return 0
    OUT.write_text(render(rows, trads, errors), encoding="utf-8")
    print(f"✓ Wrote {OUT.relative_to(ROOT)} ({len(rows)} rows, {len(trads)} churches)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
