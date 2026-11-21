#!/usr/bin/env python3
"""
Check that lib/links.py makes the same links as the web page (page.js:
plainCitation, bibleUrl, readingLinks, feastUrl, bibleDefault).

    python web/verify_links.py                       # every church's readings and feasts
    python web/verify_links.py --church elca --church roman

Every reading in each church's readings is linked for both sites, in the
church's own Bible version and in two others (one Bible.com carries, one it
does not), and every feast name, with and without a transfer note, through the
tradition's feast_link pattern.  The functions are taken out of web/page.js
as they stand and run under Node, so the page itself is what is checked.

Needs Node.js (https://nodejs.org) and an up-to-date web/data.json
(python web/export_data.py).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

import lectionary as L          # noqa: E402
import links                    # noqa: E402
import traditions as T          # noqa: E402

PAGE_PARTS = ("BIBLE_VERSIONS", "BIBLE_LANGS", "bibleAllowed", "YOUVERSION", "NOT_AT_BIBLE_GATEWAY",
              "APOCRYPHA", "APOCRYPHA_AT_BIBLE_GATEWAY", "APOCRYPHA_AT_YOUVERSION", "USFM", "HEBREW_NUMBERED", "PSALM_HEADING",
              "CONCORD_SITE", "CONCORD_DOCS", "CONCORD_PAGES", "romanValue", "concordPage", "concordUrl",
              "VERSE_SHIFTS", "numberingBooks", "englishVerse", "englishCitation", "verseNumbering",
              "bibleDefault", "plainCitation", "bibleUrl", "readingParts", "readingLinks", "readingChoices", "groupCitation",
              "groupUrl", "wordToWorshipUrl", "HYMNARY_ORDER", "hymnaryUrl", "feastUrl", "feastUrlFor")


def page_source(names=PAGE_PARTS) -> str:
    """The named consts and functions of web/page.js, as written there."""
    src = (HERE / "page.js").read_text(encoding="utf-8")
    out = []
    for name in names:
        m = re.search(rf"^(const {name} = |function {name}\()", src, re.M)
        if not m:
            sys.exit(f"✗ web/page.js has no {name}")
        if m.group(1).startswith("function"):
            end = src.index("\n}\n", m.start()) + 3
        else:
            # Up to the bracket that closes the one the value opens with.
            i = src.index("=", m.start()) + 1
            while src[i] in " \n":
                i += 1
            if src[i] in "'\"/":
                # A string or a regular expression: the line it ends.
                out.append(src[m.start():src.index(";\n", i) + 1])
                continue
            depth, j, quote = 0, i, None
            while True:
                c = src[j]
                if quote:
                    quote = None if c == quote else quote
                elif c in "'\"":
                    quote = c
                elif c in "[{":
                    depth += 1
                elif c in "]}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            end = src.index(";", j) + 1
        out.append(src[m.start():end])
    return "\n".join(out)


# The page's surroundings, stubbed: the version and site menus, a link
# element, the page's chosen Bible versions (none: every one) and the tradition
# the wheel shows.
HARNESS = r"""
const CY = require(process.argv[1]).ChurchYear;
const DATA = require(process.argv[2]);
let BIBLES = [];
const bibleBox = { value: '' }, siteBox = { value: '' };
const bibleLinks = true;                 // a page with Bible links (--links)
const document = { createElement: () => ({}) };
let CURRENT = null;
const currentTradition = () => CURRENT;
const traditionOf = key => CY.findTradition(DATA, key);
// The citations as written in English: the book names in the church's own
// language are only what the page shows (page.js: localCite), not the links.
const localCite = text => text;
%s
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = {
  defaults: cases.defaults.map(k => bibleDefault(k)),
  plain: cases.readings.map(plainCitation),
  readings: [],
  feasts: [],
};
// The defaults on pages that offer only some versions (page_bibles).
out.limited = cases.bibleSets.map(set => { BIBLES = set; return cases.defaults.map(k => bibleDefault(k)); });
BIBLES = [];
out.numbered = cases.numbered.map(([key, r, version]) => {
  CURRENT = key; bibleBox.value = version; siteBox.value = 'biblegateway';
  return readingLinks(r).map(p => typeof p === 'string' ? [p, null] : [p.textContent, p.href]);
});
CURRENT = 'elca';   // a church cited in the English numbering
for (const [version, site] of cases.choices) {
  bibleBox.value = version; siteBox.value = site;
  out.readings.push(cases.readings.map(r => readingLinks(r).map(p => typeof p === 'string' ? [p, null] : [p.textContent, p.href])));
}
out.groups = cases.groups.map(([key, rs, v]) => {
  CURRENT = key; const n = verseNumbering();
  return [groupUrl(rs, v, n), wordToWorshipUrl(rs, n), hymnaryUrl(rs, 'lsb2006', n)];
});
for (const [key, name, link] of cases.feasts) { CURRENT = key; out.feasts.push(feastUrl(name, link)); }
process.stdout.write(JSON.stringify(out));
"""


# Citations no church's readings have yet, linked all the same: the Book of
# Concord, and the Apocrypha in every way it is named.
EXTRA_READINGS = [
    "Augsburg Confession XX 1–8", "Augsburg Confession XXVIII", "Augsburg Confession, Preface 1–5",
    "Apology IV 1–20", "Apology of the Augsburg Confession XXIV", "Apology XXVI",
    "Smalcald Articles III VIII 1–13", "Smalcald Articles II", "Smalcald Articles I",
    "Treatise 1–10", "Small Catechism, Baptism", "Small Catechism IV", "Small Catechism, Lord’s Prayer",
    "Large Catechism III 1–10", "Large Catechism, Baptism", "Large Catechism, Short Preface 1–6",
    "Formula of Concord, Solid Declaration II 1–10", "Formula of Concord Epitome VII", "Epitome XI",
    "Nicene Creed", "Athanasian Creed 1–20", "Augsburg Confession IV or Romans 3:21–28",
    "Smalcald Articles, Preface 1–15", "Smalcald Articles 1:1–2/2:7", "Smalcald Articles 3/3:19–29",
    "Treatise 60–72", "Apology, Preface; 1; 2:1–14", "Apology 4:183–230", "Apology 12:125–147",
    "Apology 7/8:42–50; 9; 10", "Formula of Concord, Solid Declaration, Summary Formulation 9–20",
    "Formula of Concord, Solid Declaration 9; 10:1–9", "Catalog of Testimonies 9–10; Conclusion",
    "Catalog of Testimonies, Preface", "Preface to the Book of Concord (Triglot Concordia, pp. 7–9)",
    "Augsburg Confession 28; Conclusion", "Augsburg Confession 14–19",
    "Sirach 51:1–12", "Ecclesiasticus 44:1–15", "Wisdom of Solomon 1", "Bel and the Dragon 1–22",
    "1 Maccabees 14:1–27a", "Additions to Esther", "Prayer of Manasseh", "Greek Esther (the Additions to Esther)",
    "Letter of Jeremiah 1–29 (Baruch 6)", "Song of the Three Young Men 1–27", "Wisdom of Solomon 3:1–9", "2 Maccabees 12:38–45",
    "Tobit 8:4–8", "Song of the Three Young Men 29–34", "1 Esdras 4:34–40", "Baruch 3:9–15, 32–4:4",
]


def cases(keys: list[str]) -> dict:
    readings, feasts, seen = set(EXTRA_READINGS), [], set()
    for key in keys:
        t = T.find_tradition(L.DATA, key)
        source = T.Source(L.DATA, t)
        readings |= {r["reading"] for r in L.source_readings(source) if r.get("reading")}
        for f in source.feasts:
            for name in {f.get("name", ""), f.get("full_name", "")} - {""}:
                for text in (name, name + " (transferred from 03-25)"):
                    if (key, text, f.get("link", "")) not in seen:
                        seen.add((key, text, f.get("link", "")))
                        feasts.append([key, text, f.get("link", "")])
    defaults = sorted({links.bible_default(T.tradition_settings(L.DATA, T.find_tradition(L.DATA, k)))
                       for k in keys})
    choices = [[v, s] for v in sorted(set(defaults) | {"ESV", "EHV"})
               for s in ("biblegateway", "youversion")]
    # The churches that cite the Hebrew numbering: their readings in their own
    # version, in ESV and in NABRE (which numbers the Hebrew way too).
    numbered = []
    for key in keys:
        s = T.tradition_settings(L.DATA, T.find_tradition(L.DATA, key))
        if links.numbering_books(s.get("verse_numbering", "")):
            own = sorted({r["reading"] for r in L.source_readings(T.Source(L.DATA, T.find_tradition(L.DATA, key)))
                          if r.get("reading")})
            for v in sorted({links.bible_default(s), "ESV", "NABRE", "TB"}):
                numbered += [[key, r, v] for r in own]
    # Each set of readings as the page opens it together, in the church's own
    # version and in ESV, and at Word to Worship.
    groups = []
    for key in keys:
        s = T.tradition_settings(L.DATA, T.find_tradition(L.DATA, key))
        sets: dict = {}
        for r in L.source_readings(T.Source(L.DATA, T.find_tradition(L.DATA, key))):
            if r.get("reading"):
                k = tuple(r.get(c, "") for c in ("_file", "day", "offset", "when", "cycle", "variant", "title"))
                sets.setdefault(k, []).append(r["reading"])
        for rs in sets.values():
            for v in sorted({links.bible_default(s), "ESV"}):
                groups.append([key, rs, v])
    for v in ("ESV", "NRSVUE", "TB"):
        groups.append([keys[0], ["Sirach 51:1–12", "Psalm 45:10–15", "Matthew 25:1–13"], v])
        groups.append([keys[0], ["Augsburg Confession XX 1–8", "Romans 3:21–28"], v])
        groups.append([keys[0], ["Apology 4:117–146"], v])
        groups.append([keys[0], ["Sirach 1"], v])
        groups.append([keys[0], ["Jonah 1:1–4:11", "Prayer of Manasseh"], v])
    return {"defaults": keys, "readings": sorted(readings), "feasts": feasts,
            "choices": choices, "numbered": numbered, "bibleSets": BIBLE_SETS, "groups": groups}


# Pages that offer only some versions (page_bibles), as the page keeps them.
BIBLE_SETS = [["english"], ["de"], ["esv", "kjv", "ehv"], ["nkjv"], ["own"],
              ["english", "luth1545"], ["sv", "no"]]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().split("\n\n")[0])
    p.add_argument("--church", action="append", default=[], metavar="KEY",
                   help="a church's key (repeatable; default: every church)")
    a = p.parse_args(argv)
    node = shutil.which("node") or shutil.which("nodejs")
    if not node:
        sys.exit("✗ Node.js is needed: install it from https://nodejs.org")
    keys = a.church or [t.key for t in T.load_registry(L.DATA)]
    try:
        want = cases(keys)
    except ValueError as exc:
        sys.exit(f"✗ {str(exc).split(';')[0]}; `python lectionary.py --list` shows them all")
    run = subprocess.run([node, "-e", HARNESS % page_source(), str(HERE / "church_year.js"),
                          str(HERE / "data.json")], input=json.dumps(want), capture_output=True,
                         text=True, encoding="utf-8")
    if run.returncode:
        sys.exit(f"✗ node: {run.stderr.strip()[:600]}")
    js = json.loads(run.stdout)

    known: dict = {}

    def settings(key):
        if key not in known:
            known[key] = T.tradition_settings(L.DATA, T.find_tradition(L.DATA, key))
        return known[key]

    py = {
        "defaults": [links.bible_default(settings(k)) for k in keys],
        "limited": [[links.bible_default(settings(k), b) for k in keys] for b in BIBLE_SETS],
        "plain": [links.plain_citation(r) for r in want["readings"]],
        "readings": [[[list(part) for part in links.reading_links(r, v, s)] for r in want["readings"]]
                     for v, s in want["choices"]],
        "feasts": [links.feast_url(name, link, settings(key).get("feast_link", ""))
                   for key, name, link in want["feasts"]],
        "numbered": [[list(part) for part in links.reading_links(
            r, v, "biblegateway", links.numbering_books(settings(key).get("verse_numbering", "")))]
            for key, r, v in want["numbered"]],
        "groups": [[links.group_url(rs, v, links.numbering_books(settings(key).get("verse_numbering", ""))),
                    links.word_to_worship_url(rs, links.numbering_books(settings(key).get("verse_numbering", ""))),
                    links.hymnary_url(rs, "lsb2006", links.numbering_books(settings(key).get("verse_numbering", "")))]
                   for key, rs, v in want["groups"]],
    }
    bad = 0
    for part in ("defaults", "limited", "plain", "readings", "feasts", "numbered", "groups"):
        a_, b_ = py[part], js[part]
        if part == "readings":
            diffs = [(f"{want['choices'][i]} {want['readings'][j]!r}", x[j], y[j])
                     for i, (x, y) in enumerate(zip(a_, b_)) for j in range(len(x)) if x[j] != y[j]]
            count = len(want["readings"]) * len(want["choices"])
        else:
            label = {"defaults": keys, "limited": [" ".join(b) for b in BIBLE_SETS],
                     "plain": want["readings"],
                     "feasts": [f"{k}: {n}" for k, n, _ in want["feasts"]],
                     "numbered": [f"{k} {v}: {r}" for k, r, v in want["numbered"]],
                     "groups": [f"{k} {v}: {'; '.join(rs)}" for k, rs, v in want["groups"]]}[part]
            diffs = [(label[i], x, y) for i, (x, y) in enumerate(zip(a_, b_)) if x != y]
            count = len(a_)
        if len(a_) != len(b_):
            diffs.append(("count", len(a_), len(b_)))
        if diffs:
            bad += 1
            print(f"✗ {part}: {len(diffs)} of {count} differ")
            for what, x, y in diffs[:5]:
                print(f"    {what}\n      python {x}\n      page   {y}")
        else:
            print(f"✓ {part}: {count} identical")
    print(f"{len(keys)} churches, {len(want['readings'])} readings, "
          f"{len(want['feasts'])} feast names")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
