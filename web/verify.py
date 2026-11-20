#!/usr/bin/env python3
"""
Check the browser renderer against the Python one, year by year.

`web/church_year.js` is a second implementation of the same drawing, so the
two can drift apart: a fix made here and not there produces a calendar that is
wrong only in the browser, and only for some years.  This draws each year both
ways and compares the markup.  The two are expected to agree exactly — the JS
reproduces Python's number formatting on purpose — so any difference at all is
reported rather than waved through.

    python web/verify.py                     # 20 years, both lectionaries
    python web/verify.py --from 2025 --to 2060
    python web/verify.py --lectionary lcms-one-year
    python web/verify.py --keep /tmp/drift   # keep the files that disagreed
    python web/verify.py --color-changes PURPLE-7a1f7a,ring.halves-e6c3f7   # repainted
    python web/verify.py --art-date 12-25    # the middle holding that day's season's picture
    python web/verify.py -j 1                # one year at a time

Needs Node to run the JavaScript side; nothing else.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

import church_year_image as cy  # noqa: E402
import new_year as ny         # noqa: E402


def node_available() -> Optional[str]:
    return shutil.which("node") or shutil.which("nodejs")


def check_calendars() -> int:
    """The calendar arithmetic itself, before any drawing is compared.

    These are properties the reckonings must have whatever else changes, and
    each one has been wrong at some point while this was written: the Revised
    Julian leap count off by one at 2000 and 2400, a C++ division guard
    transcribed into Python where it did not belong.  Checking them here means
    a future edit cannot break them quietly.
    """
    import calendars as cal
    from datetime import date, timedelta

    problems = 0

    # 1. Gregorian must be datetime, exactly, everywhere datetime can speak.
    start, first = cal.GREGORIAN.to_day(1, 1, 1), date(1, 1, 1)
    total = (date(9999, 12, 31) - first).days
    bad = sum(1 for offset in range(0, total, 31)
              if cal.GREGORIAN.isoformat(start + offset)
              != (first + timedelta(days=offset)).isoformat())
    problems += bad
    print(f"  Gregorian against datetime: {total // 31} samples, {bad} mismatches")

    # 2. Every reckoning must round-trip: a day named, then read back.
    for reckoning in cal.RECKONINGS.values():
        bad = 0
        for z in range(-800000, 800000, 997):
            y, m, d = reckoning.from_day(z)
            if reckoning.to_day(y, m, d) != z:
                bad += 1
        problems += bad
        print(f"  {reckoning.label} round-trip over 4400 years: {bad} failures")

    # 3. Revised Julian agrees with Gregorian for exactly the window it claims,
    #    and parts company by a day on either side of it.
    low = cal.GREGORIAN.to_day(1600, 3, 1)
    high = cal.GREGORIAN.to_day(2800, 2, 28)
    inside = sum(1 for z in range(low, high + 1)
                 if cal.REVISED_JULIAN.from_day(z) != cal.GREGORIAN.from_day(z))
    outside = [z for z in (low - 1, high + 1)
               if cal.REVISED_JULIAN.from_day(z) == cal.GREGORIAN.from_day(z)]
    problems += inside + len(outside)
    print(f"  Revised Julian matches Gregorian 1600-03-01 to 2800-02-28: "
          f"{high - low + 1} days, {inside} disagreements"
          f"{'' if not outside else '; but it also matches outside the window'}")

    # 4. Both paschalions must land on a Sunday, always.
    for name, rule in cal.PASCHALIONS.items():
        weekdays = {(rule(y) + 3) % 7 for y in range(1583, 2500)}
        ok = weekdays == {6}
        problems += 0 if ok else 1
        print(f"  {name} Easter is always a Sunday, 1583-2499: "
              f"{'yes' if ok else 'NO — ' + str(sorted(weekdays))}")

    # 5. And must agree with the dates the churches actually keep.
    published = {2024: ("2024-03-31", "2024-05-05"), 2025: ("2025-04-20", "2025-04-20"),
                 2026: ("2026-04-05", "2026-04-12"), 2027: ("2027-03-28", "2027-05-02")}
    wrong = []
    for year, (west, east) in published.items():
        got = (cal.GREGORIAN.isoformat(cal.gregorian_easter(year)),
               cal.GREGORIAN.isoformat(cal.julian_easter(year)))
        if got != (west, east):
            wrong.append((year, got, (west, east)))
    problems += len(wrong)
    print(f"  Western and Orthodox Pascha 2024-2027 as published: "
          f"{len(published) - len(wrong)} of {len(published)} agree")
    for year, got, want in wrong:
        print(f"    {year}: computed {got}, published {want}")

    return problems


def python_svg(advent_year: int, lectionary: str, latin: bool, work: Path,
               calendar: str = "gregorian", paschalion: str = "",
               feasts: str = "all", subcalendars: tuple = (), colors: str = "",
               art_date: str = "") -> str:
    """The reference: generate the year's CSVs, then draw them as usual."""
    data_dir = work / "data"
    if data_dir.exists():
        shutil.rmtree(data_dir)
    data_dir.mkdir(parents=True)
    year = ny.ChurchYear(advent_year, lectionary, calendar, paschalion,
                         ROOT / "data", subcalendars)
    ny.write_year(year, ROOT / "data", data_dir, latin, feasts)
    return cy.Renderer(cy.Calendar(data_dir, color_changes=colors, art_date=art_date)).render()


class JsRenderer:
    """web/render_one.js --serve: one Node process for every year, the tables read once."""

    def __init__(self, node: str, data_json: Path):
        self.proc = subprocess.Popen(
            [node, str(HERE / "render_one.js"), "--serve", str(data_json)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8")

    def svg(self, advent_year: int, lectionary: str, latin: bool, calendar: str = "gregorian",
            paschalion: str = "", feasts: str = "all", subcalendars: tuple = (),
            colors: Optional[dict] = None, art_date: str = "") -> str:
        ask = {"year": advent_year, "tradition": lectionary, "latin": latin, "calendar": calendar,
               "paschalion": paschalion, "feasts": feasts, "subcalendars": list(subcalendars)}
        if colors:
            ask["colorOverrides"] = colors
        if art_date:
            ask["artDate"] = art_date
        self.proc.stdin.write(json.dumps(ask) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("node stopped")
        answer = json.loads(line)
        if "error" in answer:
            raise RuntimeError(answer["error"].strip())
        return answer["svg"]

    def close(self) -> None:
        self.proc.stdin.close()
        self.proc.wait()


def first_difference(a: str, b: str) -> str:
    """Where the two diverge, as a line number and the two lines."""
    left, right = a.split("\n"), b.split("\n")
    for index in range(min(len(left), len(right))):
        if left[index] != right[index]:
            return (f"line {index + 1}\n"
                    f"      python: {left[index][:150]}\n"
                    f"      js:     {right[index][:150]}")
    return f"one is longer: python {len(left)} lines, js {len(right)} lines"


# Each process's own Node renderer and work folder (--jobs runs several).
_CHECK: tuple = ()
_WORKER: dict = {}


def _start_worker() -> None:
    node, data, _, _, tmp, _, _ = _CHECK
    _WORKER["js"] = JsRenderer(node, data)
    _WORKER["work"] = Path(tempfile.mkdtemp(dir=tmp))


def _compare(case: tuple) -> tuple:
    """(label, "same" | "differ" | "failed", detail, the pair when kept)."""
    label, advent_year, lectionary, calendar, paschalion, feasts, subs = case
    _, _, latin, keep, _, colors, art_day = _CHECK
    # --art-date 12-25: that day in this church year (November and December in the year it begins).
    art_date = ""
    if art_day:
        month = int(art_day.split("-")[0])
        art_date = f"{advent_year + (0 if month >= 11 else 1)}-{art_day}"
    try:
        reference = python_svg(advent_year, lectionary, latin, _WORKER["work"],
                               calendar, paschalion, feasts, subs, colors, art_date)
        candidate = _WORKER["js"].svg(advent_year, lectionary, latin,
                                      calendar, paschalion, feasts, subs,
                                      _page_colors(colors, lectionary), art_date)
    except Exception as exc:
        return label, "failed", f"could not render: {exc}", None
    if reference == candidate:
        return label, "same", str(len(reference) // 1024), None
    return label, "differ", first_difference(reference, candidate), (reference, candidate) if keep else None


def _page_colors(spec: str, lectionary: str) -> Optional[dict]:
    """--color-changes as the page hands them to its renderer for one church
    (page.js: drawOptions)."""
    if not spec:
        return None
    import traditions as T
    tradition = T.find_tradition(ROOT / "data", lectionary)
    c = cy.parse_color_changes(spec, tradition.key, tradition.tradition)
    return {"days": c.days, "rings": c.rings, "ringText": c.ring_text, "empty": c.empty}


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check web/church_year.js against church_year_image.py, year by year.")
    parser.add_argument("--art-date", dest="art_date", default="", metavar="MM-DD",
                        help="draw both with the picture of this day's season in the middle, as "
                             "church_year_image.py --art-date and the page's Artwork: By season do "
                             "(12-25, 03-20 ...: the day in each church year drawn)")
    parser.add_argument("--color-changes", dest="colors", default="", metavar="CHANGES",
                        help="draw both with colors repainted, as church_year_image.py --color-changes "
                             "and the page's Colors menu do (PURPLE-7a1f7a,ring.halves-e6c3f7 ...)")
    parser.add_argument("--from", dest="start", type=int, default=2025,
                        help="first Advent year to check (default: 2025)")
    parser.add_argument("--to", dest="end", type=int, default=2044,
                        help="last Advent year to check (default: 2044)")
    parser.add_argument("--lectionary", default="both", metavar="KEY",
                        help="which tradition to check: a key from data/traditions.csv, "
                             "'both' for the two LCMS series (the default), or 'all'")
    parser.add_argument("--subcalendar", action="append", default=[], metavar="KEY",
                        help="lay this calendar over the tradition's own (repeatable); "
                             "'each' checks every one the tradition offers in turn")
    parser.add_argument("--feasts",
                        choices=("all", "festivals", "principal", "none", "every"),
                        default="all",
                        help="how much of the feasts CSV to draw (default: all; "
                             "'every' sweeps all three levels)")
    parser.add_argument("--calendar",
                        choices=("all", "gregorian", "julian", "revised-julian"),
                        default="gregorian",
                        help="which reckoning to check (default: gregorian; "
                             "'all' sweeps every calendar and paschalion pair)")
    parser.add_argument("--latin-names", action="store_true",
                        help="also name the one-year Sundays by their introits")
    parser.add_argument("--keep", type=Path, default=None,
                        help="directory to save any disagreeing pair into")
    parser.add_argument("--jobs", "-j", type=int, default=os.cpu_count() or 1,
                        help="years drawn at once (default: one per processor)")
    parser.add_argument("--data", type=Path, default=HERE / "data.json",
                        help="the frozen tables (default: web/data.json)")
    args = parser.parse_args(argv)
    cy.use_utf8_output()

    node = node_available()
    if node is None:
        sys.exit("✗ Node is needed to run the JavaScript side; install it "
                 "from https://nodejs.org and run this again.")
    if args.data == HERE / "data.json":
        # A data.json older than the CSVs compares this year's Python against
        # last week's tables, which reads as a renderer bug and is not one.
        sys.path.insert(0, str(HERE.parent))
        from church_year import freshen      # noqa: E402
        freshen(args.data, HERE.parent / "data")
    elif not args.data.exists():
        sys.exit(f"✗ {args.data} not found — run: python web/export_data.py")

    print("The calendar arithmetic first:")
    if check_calendars():
        sys.exit("\u2717 The calendars themselves are wrong; fix calendars.py "
                 "before comparing any drawings.")
    print()

    import traditions as T
    registry = T.load_registry(ROOT / "data")
    if args.lectionary == "both":
        series = ["lcms-three-year", "lcms-one-year"]
    elif args.lectionary == "all":
        series = [t.key for t in registry]
    else:
        series = [args.lectionary.strip().lower()]
    def overlays(key: str) -> list[tuple]:
        if args.subcalendar == ["each"]:
            tradition = T.find_tradition(ROOT / "data", key)
            keys = [r["key"] for r in T.read_rows(T.folder_path(ROOT / "data", tradition)
                                                    / "subcalendars.csv") if r.get("key")]
            return [()] + [(k,) for k in keys]
        return [tuple(args.subcalendar)]
    # The paschalion follows the calendar unless it is named, so "all" sweeps
    # the pairs that mean something rather than every product of the two.
    if args.calendar == "all":
        pairs = [("gregorian", "gregorian"), ("gregorian", "julian"),
                 ("julian", "julian"), ("julian", "gregorian"),
                 ("revised-julian", "julian"), ("revised-julian", "gregorian")]
    else:
        pairs = [(args.calendar, "")]
    levels = (["all", "festivals", "principal", "none"] if args.feasts == "every"
              else [args.feasts])
    agree = differ = 0
    failures = []
    cases = []
    for calendar, paschalion in pairs:
        for feasts in levels:
            for lectionary in series:
                for subs in overlays(lectionary):
                    for advent_year in range(args.start, args.end + 1):
                        how = "" if len(pairs) == 1 else f" [{calendar}/{paschalion or calendar}]"
                        how += "" if len(levels) == 1 else f" [{feasts}]"
                        how += f" +{'+'.join(subs)}" if subs else ""
                        label = f"{T.year_label(advent_year)} {lectionary}{how}"
                        cases.append((label, advent_year, lectionary, calendar, paschalion, feasts, subs))

    jobs = max(1, min(args.jobs, len(cases)))
    global _CHECK
    tmp = tempfile.mkdtemp(prefix="verify-")
    _CHECK = (node, args.data, args.latin_names, bool(args.keep), tmp, args.colors, args.art_date)
    if jobs == 1:
        _start_worker()
        results = map(_compare, cases)
    else:
        import multiprocessing
        pool = multiprocessing.get_context("fork").Pool(jobs, initializer=_start_worker)
        results = pool.imap(_compare, cases, chunksize=4)
    for label, status, detail, pair in results:
        if status == "same":
            agree += 1
            print(f"  ✓ {label}  ({detail} KB identical)")
            continue
        differ += 1
        failures.append((label, detail))
        print(f"  ✗ {label}: {detail}")
        if pair and args.keep:
            args.keep.mkdir(parents=True, exist_ok=True)
            stem = label.replace(" ", "_")
            (args.keep / f"{stem}.python.svg").write_text(pair[0], encoding="utf-8")
            (args.keep / f"{stem}.js.svg").write_text(pair[1], encoding="utf-8")
    if jobs > 1:
        pool.close()
        pool.join()
    else:
        _WORKER["js"].close()
    shutil.rmtree(tmp, ignore_errors=True)

    total = agree + differ
    print(f"\n{agree} of {total} years identical, {differ} differ")
    if failures:
        print("\nThe browser renderer has drifted from church_year_image.py for:")
        for label, detail in failures:
            print(f"  {label}: {detail.splitlines()[0]}")
        print("\nFix web/church_year.js (or re-run web/export_data.py if a CSV "
              "changed), then run this again.")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        raise SystemExit(0)
