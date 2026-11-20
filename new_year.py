#!/usr/bin/env python3
"""
Build the dated CSVs for a church year, in any of the traditions under data/.

Five of the data files depend on where Easter falls and have to be rebuilt
each year: `sundays_seasons.csv`, `season_periods.csv`, `broad_seasons.csv`,
`halves.csv` and `year_feasts.csv`.  Easter moves across five weeks of the
calendar, so this is not a matter of shifting last year's dates — the number
of Sundays after Epiphany and after Pentecost changes, rows appear and
disappear, every ordinal is renumbered, and in the Roman calendar a solemnity
that lands on a Sunday of Lent moves to the Monday.  Doing that by hand is
where mistakes creep in, and a wrong-but-well-formed year draws perfectly
happily.

    python new_year.py 2026                 # writes ./data_2026, copying ./data
    python new_year.py 2026 --out 2027data
    python new_year.py 2026 --out data --force      # overwrite in place
    python new_year.py 2026 --dry-run               # just show the dates
    python new_year.py 2026 --lectionary roman --subcalendar united_states

The year given is the year the church year begins: 2026 means the year that
runs from Advent 2026 into November 2027 (or, for a tradition whose year
starts elsewhere, from its first day in 2026).

The rules for each tradition live in its folder under data/ -- see
docs/traditions.md.  Everything that is not date-dependent — the shared
colors, rings and styles, and the tradition's folder — is copied from the
source directory, and `config.csv` is copied with only its dates, the
tradition and `output_filename` rewritten.  Your settings are preserved.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import sys
from pathlib import Path
from typing import Iterator, Optional

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "lib"))

from calendars import (CivilDate, PASCHALIONS, RECKONINGS, GREGORIAN,  # noqa: E402
                       Reckoning)
import traditions as T  # noqa: E402
from traditions import ORDINALS, FEAST_DETAIL  # noqa: E402,F401

DATA = HERE / "data"

# Shared files that carry no dates and are copied across untouched.
STATIC_FILES = [
    "colors.csv", "month_names.csv", "rings.csv", "text_styles.csv",
    "month_overrides.csv", "traditions.csv", "artwork.csv", "icons.csv",
    "season_art.csv",
]

SUNDAY = 6
THURSDAY = 3


# --------------------------------------------------------------------------
# The movable dates
# --------------------------------------------------------------------------

def easter(year: int, paschalion="gregorian") -> int:
    """Easter as a day, by whichever computus was asked for."""
    rule = PASCHALIONS[paschalion] if isinstance(paschalion, str) else paschalion
    return rule(year)


def _weekday(z: int) -> int:
    """Monday 0 ... Sunday 6, from the unbroken line of days."""
    return (z + 3) % 7


def advent_sunday(year: int, reckoning: Reckoning = GREGORIAN) -> int:
    """First Sunday in Advent: the fourth Sunday before Christmas."""
    christmas = reckoning.to_day(year, 12, 25)
    return christmas - (_weekday(christmas) + 1) - 21


def year_start(year: int, lectionary: str = "lcms-three-year",
               calendar: str = "gregorian", data_dir: Path = DATA) -> int:
    """The first day of a tradition's church year that begins in `year`."""
    tradition = T.find_tradition(data_dir, lectionary)
    settings = T.tradition_settings(data_dir, tradition)
    ctx = T.Context(RECKONINGS[calendar], "gregorian", year, tradition.variant,
                    False, settings)
    return ctx.eval(settings.get("year_start") or "sun<12-25-21")


def sundays(first: int, last: int) -> Iterator[int]:
    """Every Sunday from `first` through `last`, inclusive."""
    day = first + (SUNDAY - _weekday(first)) % 7
    while day <= last:
        yield day
        day += 7


def nth_weekday(year: int, month: int, weekday: int, count: int,
                reckoning: Reckoning = GREGORIAN) -> int:
    """The `count`-th `weekday` of a month (1 = the first one)."""
    first = reckoning.to_day(year, month, 1)
    return first + (weekday - _weekday(first)) % 7 + 7 * (count - 1)


class ChurchYear:
    """One church year of one tradition: its span, its Easter, and its rows.

    A thin handle over `traditions.Year`, which does the work.  The Latin
    names change the titles, so the rows are worked out for whichever setting
    of them is asked for, and kept.
    """

    def __init__(self, advent_year: int, lectionary: str = "lcms-three-year",
                 calendar: str = "gregorian", paschalion: str = "",
                 data_dir: Path = DATA, subcalendars=(),
                 settings: Optional[dict] = None) -> None:
        calendar = calendar or "gregorian"
        if calendar not in RECKONINGS:
            raise ValueError(f"calendar must be one of {tuple(RECKONINGS)}")
        if paschalion and paschalion not in PASCHALIONS:
            raise ValueError(f"paschalion must be one of {tuple(PASCHALIONS)}")
        self.data_dir = Path(data_dir)
        self._asked = (calendar, paschalion)
        self.tradition = T.find_tradition(self.data_dir, lectionary)
        self.lectionary = self.tradition.key
        self.subcalendars = [s for s in subcalendars if s]
        self.settings = dict(settings or read_defaults(self.data_dir)["raw"])
        self.source = T.Source(self.data_dir, self.tradition, self.subcalendars)
        self.advent_year = self.year = advent_year
        self._years: dict[bool, T.Year] = {}
        base = self.resolve(False)
        self.calendar = base.calendar
        self.paschalion = base.paschalion
        self.paschalion_named = base.paschalion_named
        self.reckoning = base.reckoning
        self.start, self.end = base.start, base.end
        self.next_advent = base.next_start
        self.easter = base.easter
        self.one_year = self.tradition.variant == "one-year"
        self.latin_available = T._truthy(self.source.settings.get("latin_names_available", ""))

    def resolve(self, latin: bool) -> T.Year:
        latin = bool(latin)
        if latin not in self._years:
            self._years[latin] = T.Year(self.source, self.year, self._asked[0],
                                        self._asked[1], latin, self.settings)
        return self._years[latin]

    def iso(self, day: int) -> str:
        """A day written out in this year's calendar."""
        return self.reckoning.isoformat(day)

    def on(self, day: int) -> CivilDate:
        return CivilDate(self.reckoning, day)

    @property
    def days(self) -> int:
        return self.end - self.start + 1

    @property
    def weeks(self) -> int:
        return (self.days + 6) // 7

    @property
    def label(self) -> str:
        return T.year_label(self.year)




# --------------------------------------------------------------------------
# The dated rows
# --------------------------------------------------------------------------

def season_periods(cy: ChurchYear) -> list[tuple[str, int, int, str]]:
    return [(p["name"], p["start"], p["end"], p["season"])
            for p in cy.resolve(False).periods]


def broad_seasons(cy: ChurchYear, rule: str = "auto") -> list[tuple[str, int, int]]:
    return [(p["name"], p["start"], p["end"]) for p in _with_rule(cy, rule).broad]


def halves(cy: ChurchYear, rule: str = "auto") -> list[tuple[str, int, int, str, str]]:
    return [(p["name"], p["start"], p["end"], p["subtitle"], p["scale"])
            for p in _with_rule(cy, rule).halves]


FESTIVAL_HALF_ENDS = ("auto", "pentecost-eve", "pentecost-week", "trinity-week")


def _with_rule(cy: ChurchYear, rule: str) -> T.Year:
    if rule in ("", None, cy.settings.get("festival_half_end", "auto")):
        return cy.resolve(False)
    settings = dict(cy.settings)
    settings["festival_half_end"] = rule
    return T.Year(cy.source, cy.year, cy._asked[0], cy._asked[1], False, settings)


# --------------------------------------------------------------------------
# Writing
# --------------------------------------------------------------------------

def _write(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def _same_file(a: Path, b: Path) -> bool:
    try:
        return a.exists() and b.exists() and a.resolve() == b.resolve()
    except OSError:
        return False


def write_year(cy: ChurchYear, source: Path, out: Path, latin: bool = False,
               feast_detail: str = "all", copy_folders: bool = True) -> None:
    """Write one year's dated CSVs and config.csv into `out`, with the static
    files and every tradition's folder.  `copy_folders=False` leaves out the
    folders, for a folder that already has them (colors.py writes year after
    year into one scratch folder and copies them once)."""
    out.mkdir(parents=True, exist_ok=True)
    year = cy.resolve(latin)

    _write(out / "sundays_seasons.csv", T.SUNDAYS_HEADER, year.sundays_rows())

    _write(out / "season_periods.csv",
           ["name", "start_date", "end_date", "season", "color"],
           [[p["name"], cy.iso(p["start"]), cy.iso(p["end"]), p["season"], p["color"]]
            for p in year.periods])

    _write(out / "broad_seasons.csv",
           ["name", "start_date", "end_date"],
           [[p["name"], cy.iso(p["start"]), cy.iso(p["end"])] for p in year.broad])

    _write(out / "halves.csv",
           ["name", "start_date", "end_date", "subtitle", "scale"],
           [[p["name"], cy.iso(p["start"]), cy.iso(p["end"]), p["subtitle"], p["scale"]]
            for p in year.halves])

    _write(out / "year_feasts.csv", T.FEASTS_HEADER, year.feast_rows())

    for name in STATIC_FILES:
        origin, destination = source / name, out / name
        if not origin.exists():
            continue
        if _same_file(origin, destination):
            continue          # regenerating in place; it is already there
        shutil.copy(origin, destination)
    # Every tradition's folder goes along, so the year folder can be switched
    # to another tradition without reaching back to the source; and the
    # artwork, which config.csv names by key.
    if copy_folders and not _same_file(source, out):
        for tradition in T.load_registry(source):
            folder = source / tradition.folder
            if tradition.folder and folder.is_dir():
                shutil.copytree(folder, out / tradition.folder, dirs_exist_ok=True)

    # Keep every tuned setting; rewrite only what depends on the year.
    # Read in full before writing: in place, these are the same file.
    config = (source / "config.csv").read_text(encoding="utf-8-sig").splitlines()
    wanted = {
        "church_year_start": cy.iso(cy.start),
        "church_year_end": cy.iso(cy.end),
        "output_filename": f"church_year_{cy.label}_calendar.svg",
        "feast_detail": feast_detail,
        "calendar": cy.calendar,
        "paschalion": _paschalion_cell(cy),
        "lectionary": cy.lectionary,
        "latin_names": "TRUE" if latin else "FALSE",
        "subcalendars": " ".join(cy.subcalendars),
    }
    seen = set()
    rewritten = []
    for line in config:
        key = line.split(",", 1)[0]
        if key in wanted and not line.startswith(("#", '"#')):
            line = f"{key},{wanted[key]}"
            seen.add(key)
        rewritten.append(line)
    for key in ("lectionary", "latin_names", "calendar", "paschalion",
                "feast_detail", "subcalendars"):
        if key not in seen:
            rewritten.append(f"{key},{wanted[key]}")
    (out / "config.csv").write_text("\n".join(rewritten) + "\n", encoding="utf-8")


def _paschalion_cell(cy: "ChurchYear") -> str:
    """What to write back for `paschalion` in config.csv.

    Blank means "follow the calendar", and writing the resolved value back in
    its place would quietly destroy that: generate one Gregorian year and
    every later `--calendar julian` would keep a Gregorian Easter, because the
    config now pins one.  So a paschalion that was inferred is written back as
    the blank it came from, and only one the caller actually named is kept.
    """
    return cy.paschalion if cy.paschalion_named else ""


def use_utf8_output() -> None:
    """Keep the ✓ and ✗ in our messages from crashing the run.

    Those characters cannot be encoded by a C/POSIX locale or a legacy Windows
    code page, and Python raises UnicodeEncodeError rather than printing —
    which turns a successful run into a traceback the moment output is
    redirected to a file, as it is under cron or in a container.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:      # not a reconfigurable stream; nothing to do
            pass


def read_defaults(source: Path) -> dict:
    """The tradition, Latin names, calendar and so on from the source config.csv."""
    found = {"lectionary": "lcms-three-year", "latin_names": False,
             "calendar": "gregorian", "paschalion": "",
             "feast_detail": "all", "festival_half_end": "auto",
             "subcalendars": [], "raw": {}}
    path = Path(source) / "config.csv"
    if not path.exists():
        return found
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith(("#", '"#')) or "," not in line:
            continue
        key, _, value = line.partition(",")
        key, value = key.strip(), value.strip()
        found["raw"][key] = value
        if key == "lectionary" and value:
            found["lectionary"] = value.lower()
        elif key == "latin_names":
            found["latin_names"] = value.upper() in ("TRUE", "1", "YES", "Y", "ON")
        elif key == "calendar" and value in RECKONINGS:
            found["calendar"] = value
        elif key == "paschalion" and value in PASCHALIONS:
            found["paschalion"] = value
        elif key == "feast_detail" and value in FEAST_DETAIL:
            found["feast_detail"] = value
        elif key == "festival_half_end" and value in FESTIVAL_HALF_ENDS:
            found["festival_half_end"] = value
        elif key == "subcalendars":
            found["subcalendars"] = value.replace(",", " ").split()
    return found


# Which rows the overview reads its dates from, by the id the rules give them.
OVERVIEW_IDS = [
    ("christmas", ["christmas"]),
    ("epiphany", ["epiphany"]),
    ("transfiguration", ["transfiguration"]),
    ("septuagesima", ["septuagesima"]),
    ("ash_wednesday", ["ash_wednesday"]),
    ("palm_sunday", ["palm_sunday"]),
    ("good_friday", ["good_friday"]),
    ("easter", ["easter"]),
    ("ascension", ["ascension"]),
    ("pentecost", ["pentecost"]),
    ("trinity", ["trinity"]),
    ("reformation_observed", ["reformation", "reformation_day"]),
    ("all_saints_observed", ["all_saints", "all_saints_day"]),
    ("thanksgiving", ["thanksgiving"]),
    ("last_sunday", ["last_sunday", "christ_the_king"]),
]


def overview(cy: ChurchYear, latin: bool = False) -> dict:
    """The year at a glance: its movable dates and how many Sundays it holds.

    `describe` prints from this and `colors.py --overview` writes it as a
    row, so the screen and the file cannot come to disagree about what a year
    contains.  A date the tradition does not keep is left blank, so a file
    mixing traditions still has one fixed header.
    """
    year = cy.resolve(latin)
    by_id: dict[str, int] = {}
    for r in year.principal:
        if r["id"] and r["title"] and r["id"] not in by_id:
            by_id[r["id"]] = r["day"]
    out = {"church_year": cy.label, "lectionary": cy.lectionary,
           "calendar": cy.calendar, "paschalion": cy.paschalion,
           "advent_1": cy.iso(cy.start)}
    for column, ids in OVERVIEW_IDS:
        day = next((by_id[i] for i in ids if i in by_id), None)
        if column == "easter":
            day = cy.easter
        out[column] = cy.iso(day) if day is not None else ""
    out["end"] = cy.iso(cy.end)
    # Counted from the titles, for any tradition that names its Sundays so; a
    # count the tradition has no Sundays for is left blank.  Sundays after the
    # Epiphany resumed in November (the 1962 Missal) are not the season's.
    def count(phrase: str, before: Optional[int] = None):
        n = sum(1 for r in year.principal if r["title"] and phrase in r["title"]
                and (before is None or r["day"] < before))
        return n or ""
    out["sundays_after_epiphany"] = count("Sunday after Epiphany", cy.easter) \
        or count("Sunday after the Epiphany", cy.easter)
    out["sundays_after_pentecost"] = count("Sunday after Pentecost")
    out["sundays_after_trinity"] = count("Sunday after Trinity")
    out["days"] = cy.days
    out["weeks"] = cy.weeks
    return out


def overview_columns() -> list[str]:
    """The overview's column names, in order, taken from the thing itself."""
    return list(overview(ChurchYear(2025, "lcms-three-year")).keys())


def describe(cy: ChurchYear, latin: bool = False) -> None:
    year = cy.resolve(latin)
    glance = overview(cy, latin)
    reckoning = cy.reckoning.label
    extra = f", {cy.paschalion} Easter" if cy.paschalion != cy.calendar else ""
    uses_latin = latin and cy.latin_available
    print(f"Church year {cy.label}: {cy.iso(cy.start)} to {cy.iso(cy.end)} "
          f"({cy.days} days, {cy.weeks} weeks, {cy.tradition.label}"
          f"{', Latin names' if uses_latin else ''})")
    if cy.subcalendars:
        print(f"  {'With':20} {', '.join(cy.subcalendars)}")
    print(f"  {'Calendar':20} {reckoning}{extra}")
    names = {"ash_wednesday": "Ash Wednesday", "transfiguration": "Transfiguration",
             "ascension": "Ascension", "pentecost": "Pentecost",
             "reformation_observed": "Reformation", "all_saints_observed": "All Saints",
             "thanksgiving": "Thanksgiving", "last_sunday": "Last Sunday"}
    print(f"  {'Easter':20} {cy.iso(cy.easter)}  ({cy.on(cy.easter).strftime('%A')})")
    for column, label in names.items():
        if glance.get(column):
            day = cy.reckoning.parse(glance[column])
            print(f"  {label:20} {glance[column]}  ({cy.on(day).strftime('%A')})")
    if glance.get("septuagesima"):
        print(f"  {'Pre-Lent':20} from {glance['septuagesima']}")
    counts = [f"{glance[k]} after {name}" for k, name in
              (("sundays_after_epiphany", "Epiphany"), ("sundays_after_pentecost", "Pentecost"),
               ("sundays_after_trinity", "Trinity")) if glance[k] != ""]
    if counts:
        print(f"  {'Sundays':20} {', '.join(counts)}")
    print(f"  {'Rows written':20} {sum(1 for r in year.principal if r['title'])} principal days, "
          f"{len(year.feasts)} commemorations")


def draw_year(data_dir: Path, out_dir: Path, advent_year: int,
              no_png: bool = False, no_html: bool = False) -> int:
    """Draw the year that was just written, in whatever forms are wanted.

    Each drawing script is called in-process rather than through a subprocess,
    so a missing dependency or a bad row is reported here rather than as a
    return code from somewhere else.  A failure to draw does not undo the CSVs,
    which are already written and correct: it is reported and the run carries
    on to whatever else was asked for.
    """
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    problems = 0
    label = T.year_label(advent_year)

    print()
    try:
        import church_year_image
        argv = ["--data", str(data_dir), "--out", str(out_dir) + os.sep]
        if no_png:
            argv.append("--no-png")
        church_year_image.main(argv)
    except SystemExit as exc:          # church_year_image.py exits on a data problem
        if exc.code:
            print(f"  ✗ the drawing failed: {exc.code}", file=sys.stderr)
            problems += 1
    except Exception as exc:
        print(f"  ✗ could not draw: {exc}", file=sys.stderr)
        problems += 1

    if not no_html:
        try:
            import church_year
            church_year.main(["--data", str(data_dir), "--year", str(advent_year),
                              "--out", str(out_dir / f"church_year_{label}.html")])
        except SystemExit as exc:
            if exc.code:
                print(f"  ✗ the HTML failed: {exc.code}", file=sys.stderr)
                problems += 1
        except Exception as exc:
            print(f"  ✗ could not build the HTML: {exc}", file=sys.stderr)
            problems += 1

    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the dated CSVs for a church year.")
    parser.add_argument("year", type=int,
                        help="the year the church year begins "
                             "(2026 = Advent 2026 into Nov 2027)")
    parser.add_argument("--from", dest="source", default="data", type=Path,
                        help="directory to copy the undated files from (default: ./data)")
    parser.add_argument("--out", default=None, type=Path,
                        help="directory to write (default: ./data_<year>)")
    parser.add_argument("--force", action="store_true",
                        help="allow writing into a directory that already exists")
    parser.add_argument("--feasts", choices=FEAST_DETAIL, default=None,
                        help="how much of the feasts the drawing uses "
                             "(default: the feast_detail setting in config.csv)")
    parser.add_argument("--calendar", choices=tuple(RECKONINGS), default=None,
                        help="which calendar to reckon the dates in "
                             "(default: the tradition's own, e.g. revised-julian for the "
                             "Orthodox, else the calendar setting in config.csv)")
    parser.add_argument("--paschalion", choices=tuple(PASCHALIONS), default=None,
                        help="which rule finds Easter (default: follows the calendar)")
    parser.add_argument("--lectionary", default=None, metavar="KEY",
                        help="which tradition: a key from data/traditions.csv, such as "
                             "lcms-three-year, lcms-one-year or roman "
                             "(default: the lectionary setting in config.csv)")
    parser.add_argument("--subcalendar", action="append", default=None, metavar="KEY",
                        help="lay a national, religious or other calendar over the "
                             "tradition's own (repeatable; see its subcalendars.csv)")
    parser.add_argument("--latin-names", dest="latin", action="store_true", default=None,
                        help="LCMS one-year series: append the Sunday's Latin name, "
                             "e.g. 'Third Sunday in Lent (Oculi)'")
    parser.add_argument("--no-latin-names", dest="latin", action="store_false",
                        help="plain titles")
    parser.add_argument("--draw", action="store_true",
                        help="also draw the year once the CSVs are written "
                             "(SVG and PNG, and the interactive HTML)")
    parser.add_argument("--images-out", default=None, type=Path, metavar="DIR",
                        help="where --draw puts what it makes (default: beside the CSVs)")
    parser.add_argument("--no-png", action="store_true",
                        help="--draw: skip the PNG, which is the slow part")
    parser.add_argument("--no-html", action="store_true",
                        help="--draw: skip the interactive HTML")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the dates without writing anything")
    args = parser.parse_args(argv)
    use_utf8_output()

    if not args.source.is_dir():
        sys.exit(f"✗ Source directory not found: {args.source}")
    defaults = read_defaults(args.source)
    lectionary = (args.lectionary or defaults["lectionary"]).strip().lower()
    subcalendars = (defaults["subcalendars"] if args.subcalendar is None
                    else args.subcalendar)

    # A tradition that keeps its own calendar (the Orthodox, on the Revised
    # Julian) brings it along unless one is asked for, as the page does.
    try:
        own = T.tradition_settings(args.source, T.find_tradition(args.source, lectionary))
    except ValueError:
        sys.exit(f"\u2717 No tradition '{lectionary}'; "
                 "python3 church_year.py --list-churches lists them")
    latin = T.latin_names_wanted(args.latin, own, defaults["latin_names"])
    try:
        cy = ChurchYear(args.year, lectionary,
                        args.calendar or own.get("calendar") or defaults["calendar"],
                        args.paschalion or defaults["paschalion"],
                        args.source, subcalendars, defaults["raw"])
    except ValueError as exc:
        sys.exit(f"✗ {exc}")
    describe(cy, latin)
    if args.dry_run:
        return 0

    out = args.out or Path(f"data_{args.year}")
    if out.exists() and not args.force:
        sys.exit(f"✗ {out} already exists — pass --force to write into it")

    in_place = _same_file(args.source, out)
    write_year(cy, args.source, out, latin, args.feasts or defaults["feast_detail"])
    print(f"\n✓ Wrote {out.resolve()}{os.sep}")
    if in_place:
        print("  (in place: the dated files were rewritten, the rest left alone)")
    if not args.draw:
        print(f"  Check it, then draw with:  python church_year_image.py --data {out}")
        return 0
    return draw_year(out, args.images_out or out, args.year, args.no_png, args.no_html)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # Piped into head, less or similar and the reader closed early.  Point
        # stdout at the void so the interpreter's final flush stays quiet too.
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        raise SystemExit(0)
