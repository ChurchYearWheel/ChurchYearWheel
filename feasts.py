#!/usr/bin/env python3
"""
The feast days of a church year, for one church: its festivals, saints' days
and commemorations, on the days the calendar keeps them that year.

    python feasts.py roman 2025                    # 2025-26, as CSV on the screen
    python feasts.py lcms-three-year 2025 --feasts festivals -o feasts.md
    python feasts.py episcopal 2025 -o feasts.html --links
    python feasts.py roman 2026 --subcalendar united_states -o roman.ics
    python feasts.py elca --from 2025 --to 2030 --feasts principal
    python feasts.py lcms-three-year 2025 --major-days -o year.ics   # with Christmas, Easter ...
    python feasts.py elca 2025 --major-days --feasts none           # the major days alone
    python feasts.py --list                        # the churches, and how many feasts each keeps

The year is the one the church year begins in (2025 = Advent 2025 to the eve
of Advent 2026); --from and --to take church years or dates.  Formats: csv,
html (a page to print), ics (iCalendar: one all-day event per day), json and
md (Markdown).  --feasts picks how many, as it does for the drawing; --links
adds where to read about each, as the page's readout links it; --major-days
adds the year's major days, Christmas, Easter, Pentecost and the like.


The feasts are the church's feasts.csv (and any --subcalendar's), placed in
the year exactly as the wheel and the page place them: moved where the
tradition's rules transfer them, left out where they give way, and without a
commemoration that only repeats the day's own name.  The Sundays and the major
days of the seasons are days.csv's, and colors.py lists them.

--major-days adds those major days: each principal day days.csv sets on a date
of its own (a `date` row with a title -- Christmas, the Epiphany, Ash
Wednesday, Easter, the Ascension, Pentecost, Trinity, a Reformation or All
Saints' Sunday), not the numbered Sundays of a season's run (`from`/`to`).
Each comes before the day's feasts, at level "major day"; --feasts does not
thin them, and --feasts none leaves them alone.

Each feast's level is principal (its color replaces the season's), festival
(it colors the lower half of its day) or commemoration; its color is its own,
blank where it takes the day's (a major day's, the season's).
"""

from __future__ import annotations

import html
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import traditions as T  # noqa: E402
import listing as out  # noqa: E402
import links  # noqa: E402

DATA = out.DATA

# The levels --feasts keeps, and what each is called in the listing.
KEEPS = {"none": (), "principal": ("principal",), "festivals": ("principal", "festival"),
         "all": ("principal", "festival", "all")}
LEVEL_NAMES = {"principal": "principal", "festival": "festival", "all": "commemoration"}
MAJOR_DAY = "major day"


# Sundays some churches date one by one that are Sundays of a sequence rather
# than celebrations of their own: Pre-Lent and Lent by their Latin names, the
# Sundays after Christmas or before Advent, the Byzantine and Syriac Sundays
# named for their Gospels.  A tradition can name more (or other) ids in its
# `major_days_exclude` setting.
ORDINARY_SUNDAYS = set("""
after_christmas after_christmas_1 after_christmas_2 after_new_year after_octave after_nativity
after_theophany after_exaltation before_exaltation before_nativity before_theophany after_ascension
after_all_saints septuagesima sexagesima quinquagesima estomihi shrove_sunday invocavit lent1
laetare judica gaudete rogate exaudi low_sunday new_sunday first_sunday octave_sunday
third_last third_last_sunday second_last second_last_sunday penultimate last_sunday
next_before_lent next_before_advent fathers_first fathers_fourth fathers_seventh forefathers
holy_fathers zacchaeus publican prodigal meatfare forgiveness orthodoxy palamas climacus
mary_of_egypt myrrhbearers paralytic samaritan blind blind_man bent_woman canaanite leper
hemorrhaging sower steward fifty_3 fifty_4 fifty_5 fifty_6 green_sunday red_sunday
""".split())


def major_days(year: T.Year) -> list[dict]:
    """The principal days of the year days.csv dates one by one and titles:
    the celebrations in their own right, not the Sundays of a run, nor the
    Sundays of a sequence some churches date one by one (ORDINARY_SUNDAYS)."""
    extra = set(str(year.settings.get("major_days_exclude") or "").split())
    skip = ORDINARY_SUNDAYS | extra
    return [e for e in year.principal
            if e.get("single") and e.get("title") and e.get("id") not in skip]


def flat(text: str) -> str:
    return " ".join(str(text or "").split())


def records(year: T.Year, detail: str, start: Optional[str], end: Optional[str],
            every_color: bool, with_links: bool, major: bool = False) -> list[dict]:
    """The year's feasts, and with `major` its major days, in order, as the
    formats write them."""
    keep = KEEPS[detail]
    pattern = year.source.settings.get("feast_link", "")
    dedupe = T._truthy(year.settings.get("deduplicate_day_labels", "TRUE") or "TRUE")
    titles: dict[int, set] = {}
    for e in year.principal:
        if e.get("title"):
            titles.setdefault(e["day"], set()).add(flat(e["title"]).lower())
    recs = []
    if major:
        for e in major_days(year):
            fields = out.day_fields(e["day"], year.reckoning)
            if (start and fields["date"] < start) or (end and fields["date"] > end):
                continue
            # The title's first line; what follows is a note or the Latin name.
            name = flat(e["title"].split("\n")[0])
            full = flat(e["full_name"] or e["title"])
            rec = dict(fields, church_year=year.label, name=name, full_name=full,
                       level=MAJOR_DAY)
            # The top of its cell: a lower half of its own (Christmas Eve's) is not its color.
            color, alt = out.split_color(e["color"])
            rec.update(color=color, alternatives=alt if every_color else [])
            if with_links:
                rec["url"] = links.feast_url(name, "", pattern)
            recs.append((e["day"], -1, rec))
    for f in sorted(year.feasts, key=lambda f: (f["day"], f["order"])):
        if f["level"] not in keep:
            continue
        if dedupe and flat(f["name"]).lower() in titles.get(f["day"], ()):
            continue          # the day's own title already says it
        fields = out.day_fields(f["day"], year.reckoning)
        if (start and fields["date"] < start) or (end and fields["date"] > end):
            continue
        full = flat(f["full_name"] or f["name"])
        moved = f.get("transferred_from")
        rec = dict(fields, church_year=year.label, name=flat(f["name"]), full_name=full,
                   level=LEVEL_NAMES[f["level"]])
        name, alt = out.split_color(f["color"] or f["bottom"])
        rec.update(color=name, alternatives=alt if every_color else [])
        if moved is not None:
            rec["transferred_from"] = out.day_fields(moved)["date"]
            m, d = year.reckoning.from_day(moved)[1:]
            note = f" (transferred from {m:02d}-{d:02d})"      # as the page names it
        else:
            note = ""
        if with_links:
            rec["url"] = links.feast_url(full + note, f.get("link", ""), pattern)
        recs.append((f["day"], f["order"], rec))
    # A major day comes before the feasts kept on it.
    return [rec for _, _, rec in sorted(recs, key=lambda t: t[:2])]


# ---------------------------------------------------------------------------
# Writing it out
# ---------------------------------------------------------------------------

def _moved(r: dict) -> str:
    if not r.get("transferred_from"):
        return ""
    y, m, d = r["transferred_from"].split("-")
    return f" (transferred from {out.MONTH_NAMES[int(m) - 1]} {int(d)})"


def as_csv(recs: list[dict], span: bool, every: bool, linked: bool, **_) -> str:
    own = out.has_own_dates(recs)
    header = ((["church_year"] if span else []) + ["date", "weekday"] + (["own_date"] if own else [])
              + ["name", "full_name", "level", "color", "transferred_from"]
              + (["url"] if linked else []))
    rows = [([r["church_year"]] if span else []) + [r["date"], r["weekday"]]
            + ([r.get("own_date", "")] if own else [])
            + [r["name"], r["full_name"], r["level"],
               out.color_text(r["color"], r["alternatives"], every), r.get("transferred_from", "")]
            + ([r["url"]] if linked else []) for r in recs]
    return out.csv_text(header, rows)


def as_json(recs: list[dict], heading: str, key: str, every: bool, **_) -> str:
    keys = ["date", "weekday", "own_date", "name", "full_name", "level", "color"] \
        + (["alternatives"] if every else []) + ["transferred_from", "url"]
    return out.json_text({"title": heading, "church": key,
                          "feasts": [{k: r[k] for k in keys if k in r} for r in recs]})


def _notes(detail: str, major: bool = False) -> list[str]:
    return ({"none": [],
             "principal": ["Principal feasts only: those whose color replaces the season's."],
             "festivals": ["Festivals: the feasts that color their day or its lower half."],
             "all": []}[detail]
            + (["With the major days: the principal days set on dates of their own, "
                "Christmas, Easter, Pentecost and the like; a blank color is the season's."]
               if major else []))


def _rows(recs, calendar, cell_name, cell_color):
    return [[out.long_date(r, calendar), cell_name(r), r["level"], cell_color(r)] for r in recs]


def as_md(recs: list[dict], heading: str, calendar: str, detail: str, major: bool,
          **_) -> str:
    rows = _rows(recs, calendar,
                 lambda r: out.md_link(r["full_name"], r.get("url")) + out.md_escape(_moved(r)),
                 lambda r: out.color_words(r["color"], r["alternatives"]) if r["color"] else "")
    return out.md_page(heading, _notes(detail, major),
                       out.md_table(["Date", "Feast", "Level", "Color"], rows), "feasts.py")


def as_html(recs: list[dict], heading: str, calendar: str, detail: str, major: bool,
            fills: dict, **_) -> str:
    e = html.escape
    rows = _rows(recs, calendar,
                 lambda r: out.html_link(r["full_name"], r.get("url")) + e(_moved(r)),
                 lambda r: (out.html_swatch(fills.get(r["color"], "")) + e(out.color_words(
                     r["color"], r["alternatives"]))) if r["color"] else "")
    return out.html_page(heading, _notes(detail, major),
                         [out.html_table(["Date", "Feast", "Level", "Color"], rows)], "feasts.py")


def as_ics(recs: list[dict], heading: str, key: str, **_) -> str:
    stamp = out.ics_stamp(recs[0]["date"]) if recs else "20000101T000000Z"
    by_day: dict[str, list[dict]] = {}
    for r in recs:
        by_day.setdefault(r["date"], []).append(r)
    events = []
    for day, feasts in by_day.items():
        body = []
        for r in feasts:
            color = out.color_words(r["color"], r["alternatives"]) if r["color"] else ""
            body.append(r["full_name"] + _moved(r) + f" ({r['level']}" + (f", {color})" if color else ")"))
            if r.get("url"):
                body.append(r["url"])
        first = next((r["color"] for r in feasts if r["color"]), "")
        events.append(out.ics_event(
            f"{day}-{key}-feasts@churchyearwheel", day, stamp,
            " / ".join(r["name"] for r in feasts), "\n".join(body),
            [f"COLOR:{out.CSS_COLOR[first]}"] if first in out.CSS_COLOR else []))
    return out.ics_calendar(heading, "feasts.py", events)


FORMATS = {"csv": as_csv, "html": as_html, "ics": as_ics, "json": as_json, "md": as_md}


def main(argv: Optional[list[str]] = None) -> int:
    out.use_utf8_output()
    p = out.parser(__doc__.split("\n\n\n")[0])
    out.add_church(p)
    out.add_span(p)
    out.add_output(p, FORMATS)
    out.add_feasts(p, ("all", "festivals", "principal", "none"))
    p.add_argument("--major-days", action="store_true",
                   help="also the year's major days: the principal days days.csv sets on "
                        "dates of their own (Christmas, Easter, Pentecost ...), not the "
                        "Sundays of a season; level 'major day'")
    p.add_argument("--no-major-days", dest="major_days", action="store_false",
                   help="feasts.csv's feasts only (the default)")
    out.add_colors(p)
    p.add_argument("--links", action="store_true",
                   help="add where to read about each feast: its own link, the "
                        "church's feast_link, else a Wikipedia search, as the page does")
    p.add_argument("--no-links", dest="links", action="store_false",
                   help="no links (the default)")
    out.add_data(p)
    out.add_year_options(p, latin=False)
    a = p.parse_args(argv)
    data = out.data_dir(p, a)

    if a.list:
        def count(t: T.Tradition) -> str:
            n = len(T.Source(data, t).feasts)
            return f"   ({n} feasts)" if n else "   (no feasts)"
        return out.list_churches(count, data)
    if a.feasts == "none" and not a.major_days:
        p.error("--feasts none lists nothing without --major-days")
    fmt = out.output_format(p, a, FORMATS)
    defaults = out.config_defaults(data)
    key, named = out.church_and_year(p, a, defaults)
    try:
        T.find_tradition(data, key)
    except ValueError as exc:
        return out.unknown_church(exc, "feasts.py")
    # config.csv's feast_detail none is the drawing's: it leaves the list whole.
    detail = a.feasts or (defaults["feast_detail"] if defaults["feast_detail"] in KEEPS
                          and defaults["feast_detail"] != "none" else "all")
    years: dict[int, T.Year] = {}

    def build(y: int) -> T.Year:
        if y not in years:
            years[y] = out.year_of(key, y, data, out.subcalendars(a, named, defaults),
                                   a.calendar or "", a.paschalion or "")
        return years[y]

    def bounds(y: int) -> tuple:
        year = build(y)
        return out.day_fields(year.start)["date"], out.day_fields(year.end)["date"]

    try:
        first, last, start, end = out.span(p, a, defaults["year"], bounds)
        recs = []
        for y in range(first, last + 1):
            recs += records(build(y), detail, start, end, a.colors == "all", a.links,
                            a.major_days)
    except ValueError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 2
    year = years[first]
    heading = out.heading(year.tradition.label,
                          "feasts and major days" if a.major_days else "feasts", first, last)
    text = FORMATS[fmt](recs, heading=heading, key=year.tradition.key, span=first != last,
                        every=a.colors == "all", linked=a.links, detail=detail,
                        major=a.major_days,
                        calendar=year.calendar, fills=out.palette(year.source))
    return out.write(text, a.output, out.default_name(key if named else None, first, last,
                                                       "feasts", fmt),
                     f"{len(recs)} {'days' if a.major_days else 'feasts'}")


if __name__ == "__main__":
    out.run(main)
