#!/usr/bin/env python3
"""
Check that the page's lists (web/listings.js) are the files lectionary.py,
colors.py (its --overview too) and feasts.py write: byte for byte, in every format.

    python web/verify_lists.py                       # a spread of churches and options
    python web/verify_lists.py --church roman --church eastern-orthodox

Each case is run through the script (into a scratch folder) and through
listings.js under Node with the page's own link functions (taken from
web/page.js as they stand), and the two texts compared.

Needs Node.js (https://nodejs.org) and an up-to-date web/data.json
(python web/export_data.py).
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(HERE))

import colors as C              # noqa: E402
import feasts as F              # noqa: E402
import lectionary as L          # noqa: E402
import links                    # noqa: E402
import traditions as T          # noqa: E402
from verify_links import page_source  # noqa: E402

PARTS = ("BIBLE_VERSIONS", "BIBLE_LANGS", "bibleAllowed", "YOUVERSION", "NOT_AT_BIBLE_GATEWAY",
         "APOCRYPHA", "APOCRYPHA_AT_BIBLE_GATEWAY", "APOCRYPHA_AT_YOUVERSION", "USFM", "HEBREW_NUMBERED",
         "CONCORD_SITE", "CONCORD_DOCS", "CONCORD_PAGES", "romanValue", "concordPage", "concordUrl",
         "PSALM_HEADING", "VERSE_SHIFTS", "numberingBooks", "englishVerse", "englishCitation",
         "plainCitation", "bibleUrl", "readingParts", "readingChoices", "withAntiphons", "groupCitation", "groupUrl",
         "feastUrlFor")

HARNESS = r"""
const CY = require(process.argv[1]).ChurchYear;
const LISTS = require(process.argv[2]).ChurchYearLists;
const DATA = require(process.argv[3]);
let BIBLES = [];
%s
const links = { parts: readingParts, group: groupUrl, feast: feastUrlFor, numbering: numberingBooks };
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = cases.map(c => {
  try {
    const f = { readings: LISTS.readingsList, colors: LISTS.colorsList, feasts: LISTS.feastsList,
                overview: LISTS.overviewList }[c.list];
    return f(DATA, c.o, c.fmt, links).text;
  } catch (e) { return 'ERROR ' + (e && e.stack || e); }
});
process.stdout.write(JSON.stringify(out));
"""

CHURCHES = ["lcms-three-year", "lcms-one-year", "roman", "eastern-orthodox", "elca",
            "anglican-common-worship", "oriental-ethiopian", "wels-one-year", "episcopal",
            "lutheran-sweden"]


def cases_for(key: str) -> list[dict]:
    settings = T.tradition_settings(L.DATA, T.find_tradition(L.DATA, key))
    own = links.bible_default(settings)
    latin = T.latin_names_wanted(None, settings, False)
    subs = ["united_states"] if key == "roman" else []
    out = []
    # A church with no readings yet has no readings list (both refuse it).
    has_readings = bool(L.source_readings(T.Source(L.DATA, T.find_tradition(L.DATA, key))))
    for fmt in ("csv", "html", "ics", "json", "md"):
        for first, last in ((2025, 2025), (2025, 2026)):
            base = {"tradition": key, "first": first, "last": last, "subcalendars": subs,
                    "latinNames": latin}
            span = ["--from", str(first), "--to", str(last)]
            sub = sum((["--subcalendar", s] for s in subs), []) or ["--subcalendar", "none"]
            lat = ["--latin-names" if latin else "--no-latin-names"]
            for site, kinds in ((("none", None), ("biblegateway", ["day", "feasts"]),
                                 ("youversion", None)) if has_readings else ()):
                o = dict(base, feastDetail="all", site=site, version=own)
                argv = [key] + span + sub + lat + ["--feasts", "all", "--bible", own]
                if site != "none":
                    argv += ["--links", site]
                if kinds:
                    o["kinds"] = kinds
                    argv += ["--readings", ",".join(kinds)]
                out.append({"list": "readings", "fmt": fmt, "o": o, "argv": argv})
            # The readings alone, without the parts of the service (reading_propers).
            if has_readings and str(settings.get("reading_propers", "")).strip():
                o = dict(base, feastDetail="all", site="biblegateway", version=own, propers=False)
                argv = [key] + span + sub + lat + ["--feasts", "all", "--bible", own, "--links", "biblegateway",
                                                   "--no-propers"]
                out.append({"list": "readings", "fmt": fmt, "o": o, "argv": argv})
            for days, every, detail in (("principal", False, "all"), ("all", True, "festivals"),
                                        ("named", False, "principal")):
                o = dict(base, feastDetail=detail, days=days, every=every)
                argv = [key] + span + sub + lat + ["--days", days, "--feasts", detail,
                                                    "--colors", "all" if every else "primary"]
                out.append({"list": "colors", "fmt": fmt, "o": o, "argv": argv})
            for detail, major, every, linked in (("all", False, False, False),
                                                 ("festivals", True, True, True),
                                                 ("none", True, False, False)):
                o = dict(base, detail=detail, major=major, every=every, links=linked)
                argv = [key] + span + sub + ["--feasts", detail]
                argv += ["--major-days"] if major else []
                argv += ["--colors", "all"] if every else []
                argv += ["--links"] if linked else []
                out.append({"list": "feasts", "fmt": fmt, "o": o, "argv": argv})
        if fmt != "ics":                # the overview: one row a year, over a decade too
            for first, last in ((2025, 2025), (2025, 2034)):
                o = {"tradition": key, "first": first, "last": last, "subcalendars": subs,
                     "latinNames": latin, "feastDetail": "all"}
                argv = [key, "--from", str(first), "--to", str(last)]
                argv += sum((["--subcalendar", s] for s in subs), []) or ["--subcalendar", "none"]
                argv += ["--latin-names" if latin else "--no-latin-names", "--overview"]
                out.append({"list": "overview", "fmt": fmt, "o": o, "argv": argv})
    return out


def python_text(case: dict, folder: Path) -> str:
    script = {"readings": L, "colors": C, "feasts": F, "overview": C}[case["list"]]
    target = folder / f"out.{case['fmt']}"
    if target.exists():
        target.unlink()
    with contextlib.redirect_stderr(io.StringIO()):
        try:
            code = script.main(case["argv"] + ["-o", str(target)])
        except SystemExit as exc:
            code = exc.code
    if code:
        return f"ERROR exit {code}"
    if not target.exists():
        return "ERROR no file"
    with open(target, encoding="utf-8", newline="") as handle:     # an .ics keeps its CRLFs
        return handle.read()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().split("\n\n")[0])
    p.add_argument("--church", action="append", default=[], metavar="KEY")
    p.add_argument("--list", action="append", default=[], dest="lists",
                   choices=("readings", "colors", "feasts", "overview"), help="only these lists")
    a = p.parse_args(argv)
    node = shutil.which("node") or shutil.which("nodejs")
    if not node:
        sys.exit("✗ Node.js is needed: install it from https://nodejs.org")
    cases = [c for key in (a.church or CHURCHES) for c in cases_for(key)
             if not a.lists or c["list"] in a.lists]
    run = subprocess.run([node, "-e", HARNESS % page_source(PARTS), str(HERE / "church_year.js"),
                          str(HERE / "listings.js"), str(HERE / "data.json")],
                         input=json.dumps([{k: c[k] for k in ("list", "fmt", "o")} for c in cases]),
                         capture_output=True, text=True, encoding="utf-8")
    if run.returncode:
        sys.exit(f"✗ node: {run.stderr.strip()[:800]}")
    js = json.loads(run.stdout)
    bad = 0
    with tempfile.TemporaryDirectory(prefix="lists-") as tmp:
        for case, page in zip(cases, js):
            py = python_text(case, Path(tmp))
            if py != page:
                bad += 1
                if bad <= 12:
                    print(f"✗ {case['list']} {case['fmt']}: {' '.join(case['argv'])}")
                    pl, jl = py.splitlines(), page.splitlines()
                    for i, (x, y) in enumerate(zip(pl, jl)):
                        if x != y:
                            print(f"    line {i + 1}\n      python {x[:300]!r}\n      page   {y[:300]!r}")
                            break
                    else:
                        print(f"    lengths {len(pl)} / {len(jl)}: {(pl or [''])[-1][:200]!r} / {(jl or [''])[-1][:200]!r}")
    print(f"{'✓' if not bad else '✗'} {len(cases) - bad} of {len(cases)} lists identical")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
