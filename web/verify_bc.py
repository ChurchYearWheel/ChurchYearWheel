#!/usr/bin/env python3
"""
Check the browser's dates where `datetime.date` cannot follow.

`web/verify.py` draws each year twice and compares the markup, which is the
strongest check there is — but it leans on `church_year_image.py`, and that leans on
`datetime.date`, which stops at 1 January AD 1.  The browser goes further back,
so below that year there is no second drawing to compare against.

What can still be checked is the arithmetic underneath, and that is what this
does: `web/proleptic.py` is the same calendar and computus written in plain
integers, with no date library beneath it, so it reaches wherever the browser
does.  The two are compared year by year.

    python web/verify_bc.py                  # 4000 BC to AD 1
    python web/verify_bc.py --from -9999 --to 1

`web/proleptic.py` is itself checked against `datetime` over every week of
AD 1 to 9999 before it is trusted here, so it is not a reference taken on faith.

Needs Node; nothing else.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "lib"))

import proleptic as P  # noqa: E402


def check_reference() -> int:
    """Agree with `datetime` everywhere `datetime` can speak, before going past it."""
    bad = 0
    start, first = P.days_from_civil(1, 1, 1), date(1, 1, 1)
    total = (date(9999, 12, 31) - first).days
    for offset in range(0, total, 7):
        day = first + timedelta(days=offset)
        if P.civil_from_days(start + offset) != (day.year, day.month, day.day):
            bad += 1
        elif P.weekday(start + offset) != day.weekday():
            bad += 1
        elif P.iso(start + offset) != day.isoformat():
            bad += 1
    print(f"  reference vs datetime: {total // 7} weeks of AD 1–9999, "
          f"{bad} mismatches")

    # 400 Gregorian years are 146097 days -- 20871 whole weeks -- at every point
    # of the calendar.  This is what broke when the reference was first written.
    steps = {P.days_from_civil(y + 400, 6, 15) - P.days_from_civil(y, 6, 15)
             for y in range(-9999, 9500)}
    ok = steps == {146097}
    print(f"  400-year step across BC and AD: {sorted(steps)} "
          f"{'✓' if ok else '✗'}")
    return bad + (0 if ok else 1)


def python_rows(first: int, last: int) -> list[str]:
    """The same church year dates the browser reports, from the reference."""
    rows = []
    for year in range(first, last + 1):
        start = P.advent_sunday(year)
        end = P.advent_sunday(year + 1) - 1
        easter = P.easter(year + 1)
        reformation_day = P.days_from_civil(year + 1, 10, 31)
        reformation = reformation_day - (P.weekday(reformation_day) + 1) % 7

        def nth(month: int, weekday: int, count: int) -> int:
            first_of = P.days_from_civil(year + 1, month, 1)
            return first_of + (weekday - P.weekday(first_of)) % 7 + 7 * (count - 1)

        rows.append(",".join([
            str(year), P.iso(start), P.iso(end), P.iso(easter),
            P.iso(easter - 46), P.iso(easter + 49), P.iso(reformation),
            P.iso(nth(11, 3, 4)), P.iso(nth(11, 6, 1)), str(end - start + 1),
        ]))
    return rows


# ---------------------------------------------------------------------------
# The drawing itself
# ---------------------------------------------------------------------------
# The dates can be checked against a reference, but the drawing cannot: there is
# no Python renderer below AD 1 to compare it with.  So it is checked against
# itself in a different year instead.
#
# 400 Gregorian years are exactly 146097 days, which is 20871 whole weeks, so a
# BC year and an AD year 400 apart share every weekday and every month length.
# Where their Easters coincide as well, the two church years are the same shape
# from end to end -- every cell is the same color, carries the same labels and
# sits at the same angle.  One of the pair is inside Python's reach, so the BC
# drawing can be compared against a Python drawing of its twin.
#
# Exactly one thing legitimately differs: the label on the year's first day,
# which prints the year itself.  That line is blanked on both sides; everything
# else has to match character for character.

FIRST_DAY_LABEL = re.compile(r'(<text\b[^>]*>)([A-Z][a-z]+ \d{1,2}, [^<]+)(</text>)')


def find_twins(wanted: int = 3, search_from: int = -3000) -> list[tuple[int, int]]:
    """BC/AD church year pairs of identical shape, one of each length if possible."""
    pairs, lengths = [], set()
    for bc in range(search_from, 0):
        for step in range(1, 30):
            ad = bc + 400 * step
            if not 1 <= ad <= 9990:
                continue
            if (P.civil_from_days(P.easter(bc + 1))[1:]
                    != P.civil_from_days(P.easter(ad + 1))[1:]):
                continue
            length = P.advent_sunday(bc + 1) - P.advent_sunday(bc)
            # Take both a 364-day year and a 371-day one; the long ones are
            # where a commemoration lands twice and the seam is hardest.
            if length in lengths and len(pairs) >= wanted:
                break
            lengths.add(length)
            pairs.append((bc, ad))
            break
        if len(pairs) >= wanted and len(lengths) > 1:
            break
    return pairs


def blank_year_label(markup: str) -> str:
    # The whole element goes, attributes included: "November 30, 3001 BC" is
    # wider than "November 30, 3400", so auto-fitting shrinks it to a different
    # size, and that size is part of the same legitimate difference.
    return FIRST_DAY_LABEL.sub("<text>FIRST-DAY-LABEL</text>", markup)


def compare_twins(node: str, pairs: list[tuple[int, int]], data: Path) -> int:
    """Draw each BC year in the browser and its AD twin in Python."""
    import shutil as _shutil
    import tempfile
    import church_year_image as cy_py
    import new_year as ny

    root = HERE.parent
    differ = 0
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for bc, ad in pairs:
            length = P.advent_sunday(bc + 1) - P.advent_sunday(bc)
            # The AD twin, drawn by church_year_image.py exactly as any year is.
            data_dir = work / "data"
            if data_dir.exists():
                _shutil.rmtree(data_dir)
            data_dir.mkdir(parents=True)
            ny.write_year(ny.ChurchYear(ad, "lcms-three-year"), root / "data", data_dir, False)
            reference = cy_py.Renderer(cy_py.Calendar(data_dir)).render()

            # The BC year, drawn by the browser renderer.
            out = work / "bc.svg"
            result = subprocess.run(
                [node, str(HERE / "render_one.js"), str(bc), "lcms-three-year", "0",
                 str(out), str(data)], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"  \u2717 Advent {bc}: node failed: {result.stderr.strip()}")
                differ += 1
                continue

            left = blank_year_label(reference)
            right = blank_year_label(out.read_text(encoding="utf-8"))
            label = (f"Advent {bc} ({1 - bc} BC) vs its twin Advent {ad}"
                     f", {length} days")
            if left == right:
                print(f"  \u2713 {label}: identical ({len(left) // 1024} KB)")
            else:
                differ += 1
                rows = [(a, b) for a, b in zip(left.split("\n"), right.split("\n"))
                        if a != b]
                print(f"  \u2717 {label}: {len(rows)} line(s) differ")
                for a, b in rows[:3]:
                    print(f"      AD twin: {a[:120]}\n      BC year: {b[:120]}")
    return differ


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the browser's dates below the reach of datetime.date.")
    parser.add_argument("--from", dest="start", type=int, default=-4000,
                        help="first Advent year (default: -4000, i.e. 4001 BC)")
    parser.add_argument("--to", dest="end", type=int, default=1,
                        help="last Advent year (default: 1)")
    parser.add_argument("--dates-only", action="store_true",
                        help="skip the twin-drawing comparison")
    parser.add_argument("--data", type=Path, default=HERE / "data.json",
                        help="the frozen tables (default: web/data.json)")
    args = parser.parse_args(argv)

    node = shutil.which("node") or shutil.which("nodejs")
    if node is None:
        sys.exit("✗ Node is needed to run the JavaScript side.")

    print("Checking the reference itself first:")
    if check_reference():
        sys.exit("✗ The reference disagrees with datetime; fix "
                 "web/proleptic.py before trusting anything below.")

    result = subprocess.run([node, str(HERE / "dates_one.js"),
                             str(args.start), str(args.end)],
                            capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"✗ node failed: {result.stderr.strip()}")

    browser = result.stdout.strip().split("\n")
    reference = python_rows(args.start, args.end)
    if len(browser) != len(reference):
        sys.exit(f"✗ {len(reference)} years expected, {len(browser)} returned")

    differ = [(r, b) for r, b in zip(reference, browser) if r != b]
    total = len(reference)
    span = f"{args.start} to {args.end}"
    print(f"\n  browser vs reference: {total} church years ({span}), "
          f"{total - len(differ)} identical, {len(differ)} differ")
    for r, b in differ[:10]:
        print(f"    reference {r}\n    browser   {b}")

    problems = len(differ)
    if args.dates_only:
        return 1 if problems else 0

    print("\nAnd the drawing, against its twin inside Python's reach:")
    pairs = find_twins()
    if not pairs:
        print("  ! no twin years found to compare against")
        return 1 if problems else 0
    problems += compare_twins(node, pairs, args.data)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
