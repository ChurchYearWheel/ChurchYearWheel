#!/usr/bin/env python3
"""
The liturgical colors of a church year: each Sunday and principal day (or
every day), its name, and the color the wheel paints it.

    python colors.py                               # ./data's year, as CSV on the screen
    python colors.py -o .                          # ./church_year_2025-26_colors.csv
    python colors.py elca 2025 -o colors.html      # a page to print, with swatches
    python colors.py lcms-one-year 2026 -o lsb.ics # for a calendar app
    python colors.py episcopal 2025 --colors all   # with the others allowed and lower halves
    python colors.py roman 2025 --days all --subcalendar united_states
    python colors.py --from 2025 --to 2035 --overview   # Easter and the rest, year by year

The year is the one the church year begins in (2025 = Advent 2025 to the eve
of Advent 2026); --from and --to take church years or dates.  Formats: csv,
html (a page to print, with color swatches), ics (iCalendar: one all-day
event per day), json and md (Markdown).


With no church and no year it lists the year folder --data names (./data) as
it stands, hand edits included, exactly as church_year_image.py draws it.  Named,
or given a year, it generates each year from the rules, so none has to have
been built first; --data is then where the rules are.

The color is resolved exactly as church_year_image.py resolves it -- an override on
the day if there is one, otherwise the color of the season -- so the list and
the drawing can never disagree.  It is the top of the day's cell: the color of
the day itself, which the paraments are chosen by.  --colors all adds the
others the church allows ("BLUE; violet") and, where the wheel splits the
cell (Christmas Eve, an apostle's day on a Sunday), the lower half's color.

--days picks the days: sundays; principal (the default: the Sundays and the
weekdays with a name of their own -- Christmas, Ash Wednesday, Good Friday,
the Ascension -- and the solemnities); named (also every day with a festival
or commemoration, as many as --feasts allows); or all, every day of the year.
"""

from __future__ import annotations

import atexit
import html
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

import new_year as ny  # noqa: E402
from church_year_image import Calendar, apply_feasts  # noqa: E402
import listing as out  # noqa: E402
import traditions as T  # noqa: E402

DAYS = ("all", "named", "principal", "sundays")


# ---------------------------------------------------------------------------
# The days
# ---------------------------------------------------------------------------

def flat(text: str) -> str:
    return " ".join(text.split())      # the soft break is for the drawing


def _others(alt: str) -> list[str]:
    """"violet; gold" -> ["violet", "gold"]: the colors a source allows besides the one drawn."""
    return [c.strip() for c in (alt or "").split(";") if c.strip()]


def records(calendar: Calendar, days: str = "principal", start: Optional[str] = None,
            end: Optional[str] = None) -> list[dict]:
    """Each day worth listing, in date order: its date, names and colors."""
    settings = calendar.settings
    label = T.year_label(settings.church_year_start.year)
    recs = []
    for day in calendar.days:
        is_sunday = day.weekday() == settings.week_starts_on
        titled = bool(calendar.titles.get(day))
        feasted = bool(calendar.feasts.get(day))
        # A tradition that ranks its days (the Roman) marks its greatest with
        # the solemnity style; those are principal days even midweek.
        solemn = [flat(e.text) for e in calendar.feasts.get(day, [])
                  if e.style_override == "solemnity"]
        wanted = (days == "all" or is_sunday
                  or (days == "named" and (titled or feasted))
                  or (days == "principal" and (titled or solemn)))
        if not wanted:
            continue
        fields = out.day_fields(out.day_number(day), settings.reckoning)
        if (start and fields["date"] < start) or (end and fields["date"] > end):
            continue

        # A day's own titles, then its solemnities; a day with no title of
        # its own is named by its feasts, as are all days when they are asked for.
        labels = [flat(e.text) for e in calendar.titles.get(day, [])]
        if days in ("all", "named") or not labels:
            labels += [flat(e.text) for e in calendar.feasts.get(day, [])]
        else:
            labels += solemn

        # The top of the cell, and the lower half where the wheel splits it.
        # A split into the same color is not drawn, so it is not listed.
        top = calendar.color_for(day)
        lower = calendar.bottom_color_for(day)
        if lower is not None and lower.fill == top.fill:
            lower = None
        recs.append(dict(fields, church_year=label, titles=labels,
                         color=top.name, alternatives=_others(top.alt), fill=top.fill,
                         lower_color=lower.name if lower else "",
                         lower_alternatives=_others(lower.alt) if lower else [],
                         lower_fill=lower.fill if lower else ""))
    return recs


def year_details(calendar: Calendar, cy=None) -> dict:
    """Which lectionary and calendar produced the year, so a program reading
    the JSON does not have to guess.  With the generated year `cy`, the Easter
    reckoning it was worked out by (a church's own paschalion_default)."""
    s = calendar.settings
    return {"church_year": T.year_label(s.church_year_start.year),
            "start": out.day_fields(out.day_number(s.church_year_start))["date"],
            "end": out.day_fields(out.day_number(s.church_year_end))["date"],
            "lectionary": s.lectionary, "calendar": s.calendar,
            "paschalion": cy.paschalion if cy is not None else s.paschalion,
            "subcalendars": (s.subcalendars or "").replace(",", " ").split(),
            "latin_names": bool(s.latin_names), "feast_detail": s.feast_detail}


def build_year(advent_year: int, source: Path, lectionary: str, calendar: str,
               paschalion: str, latin: bool, feasts: Optional[str], subcalendars=(),
               scratch: Optional[Path] = None):
    """One year, generated into a scratch folder and loaded from it.

    A year that is asked for need not have a folder, so it is written out and
    read back through exactly the path `new_year.py` and `church_year_image.py`
    already take.  Reimplementing the colors here would eventually disagree
    with the drawing; this cannot.  Given a `scratch` folder that already
    holds the traditions' folders (from an earlier year of the same run), only
    the year's own files are written into it, which is most of the time a
    long span takes; what is read back is the same.
    """
    cy = ny.ChurchYear(advent_year, lectionary, calendar, paschalion,
                       data_dir=source, subcalendars=subcalendars)
    if scratch is not None:
        primed = (scratch / ".primed").exists()
        ny.write_year(cy, source, scratch, latin, feasts or "all", copy_folders=not primed)
        (scratch / ".primed").touch()
        return cy, apply_feasts(Calendar(scratch), feasts)
    with tempfile.TemporaryDirectory() as folder:
        ny.write_year(cy, source, Path(folder), latin, feasts or "all")
        return cy, apply_feasts(Calendar(Path(folder)), feasts)


# ---------------------------------------------------------------------------
# Writing it out
# ---------------------------------------------------------------------------

def as_csv(recs: list[dict], span: bool, every: bool, **_) -> str:
    own = out.has_own_dates(recs)
    header = ((["church_year"] if span else []) + ["date", "weekday"] + (["own_date"] if own else [])
              + ["title", "color"] + (["lower_color"] if every else []))
    rows = [([r["church_year"]] if span else []) + [r["date"], r["weekday"]]
            + ([r.get("own_date", "")] if own else [])
            + [" / ".join(r["titles"]), out.color_text(r["color"], r["alternatives"], every)]
            + ([out.color_text(r["lower_color"], r["lower_alternatives"], True)] if every else [])
            for r in recs]
    return out.csv_text(header, rows)


def as_json(recs: list[dict], heading: str, key: str, every: bool, years: list, **_) -> str:
    """The settings every year shares once at the top; each year only its span
    (and whatever else differs between them); each day without its year, which
    its date already gives."""
    own = ("church_year", "start", "end")
    shared = {k: v for k, v in (years[0].items() if years else ())
              if k not in own and all(y.get(k) == v for y in years)}
    if shared.get("lectionary") == key:
        del shared["lectionary"]
    keys = ["date", "weekday", "own_date", "titles", "color"] + (
        ["alternatives", "lower_color", "lower_alternatives"] if every else [])
    return out.json_text({"title": heading, "church": key, **shared,
                          "years": [{k: v for k, v in y.items()
                                     if k not in shared and not (k == "lectionary" and v == key)}
                                    for y in years],
                          "days": [{k: r[k] for k in keys if k in r} for r in recs]})


def _notes(every: bool) -> list[str]:
    return (["Each color is the day's own, the top of its cell on the wheel; "
             "the others the church allows follow in parentheses, and the lower half's "
             "is given where the wheel splits the cell."] if every else
            ["Each color is the day's own, the top of its cell on the wheel."])


def _header(every: bool) -> list[str]:
    return ["Date", "Day", "Color"] + (["Lower half"] if every else [])


def _words(r: dict, every: bool, lower: bool = False) -> str:
    if lower:
        return out.color_words(r["lower_color"], r["lower_alternatives"]) if r["lower_color"] else ""
    return out.color_words(r["color"], r["alternatives"] if every else [])


def _sections(recs: list[dict]) -> list[tuple[str, list[dict]]]:
    """One table per church year."""
    groups: dict[str, list[dict]] = {}
    for r in recs:
        groups.setdefault(r["church_year"], []).append(r)
    return list(groups.items())


def as_md(recs: list[dict], heading: str, every: bool, calendar: str, **_) -> str:
    body = []
    sections = _sections(recs)
    for label, rows in sections:
        if len(sections) > 1:
            body += [f"## {label}", ""]
        body += out.md_table(_header(every), (
            [out.md_escape(out.long_date(r, calendar)), out.md_escape(" / ".join(r["titles"])),
             out.md_escape(_words(r, every))] + ([out.md_escape(_words(r, every, True))] if every else [])
            for r in rows))
    return out.md_page(heading, _notes(every), body, "colors.py")


def as_html(recs: list[dict], heading: str, every: bool, calendar: str, **_) -> str:
    e = html.escape
    body = []
    sections = _sections(recs)
    for label, rows in sections:
        if len(sections) > 1:
            body.append(f"<h2>{e(label)}</h2>")
        body.append(out.html_table(_header(every), (
            [e(out.long_date(r, calendar)), e(" / ".join(r["titles"])),
             out.html_swatch(r["fill"]) + e(_words(r, every))]
            + ([(out.html_swatch(r["lower_fill"]) + e(_words(r, every, True))) if r["lower_color"]
                else ""] if every else [])
            for r in rows)))
    return out.html_page(heading, _notes(every), body, "colors.py")


def ics_series(calendar: Calendar, cy=None) -> str:
    """What a feed's UIDs are made from besides the date: the lectionary, any
    calendars laid over it, and the calendar and Easter when they are not the
    usual ones."""
    s = calendar.settings
    paschalion = cy.paschalion if cy is not None else s.paschalion
    series = s.lectionary
    subs = (s.subcalendars or "").replace(",", " ").split()
    if subs:
        series += "+" + "+".join(subs)
    if s.calendar != "gregorian":
        series += f"-{s.calendar}"
    natural = "gregorian" if s.calendar == "gregorian" else "julian"
    if paschalion != natural:
        series += f"-{paschalion}-easter"
    return series


def as_ics(recs: list[dict], heading: str, every: bool, series: dict, years: list, **_) -> str:
    stamps = {y["church_year"]: out.ics_stamp(y["start"]) for y in years}
    events = []
    for r in recs:
        stamp = stamps[r["church_year"]]
        words = "Liturgical color: " + _words(r, every).capitalize()
        if every and r["lower_color"]:
            words += "; lower half " + _words(r, every, True)
        names = [r["color"]] + ([r["lower_color"]] if every and r["lower_color"] else [])
        events.append(out.ics_event(
            f"{r['date']}-{series[r['church_year']]}@churchyearwheel", r["date"], stamp,
            " / ".join(r["titles"]) or r["weekday"], words,
            # Commas separate the categories, so each is escaped on its own.
            ["CATEGORIES:" + ",".join(out.ics_text(c) for c in names)]
            + ([f"COLOR:{out.CSS_COLOR[r['color']]}"] if r["color"] in out.CSS_COLOR else [])))
    return out.ics_calendar(heading, "colors.py", events)


FORMATS = {"csv": as_csv, "html": as_html, "ics": as_ics, "json": as_json, "md": as_md}


# -- the overview ----------------------------------------------------------

def overview_text(fmt: str, rows: list[dict], heading: str) -> str:
    columns = ny.overview_columns()
    if fmt == "csv":
        return out.csv_text(columns, ([g[k] for k in columns] for g in rows))
    if fmt == "json":
        return out.json_text({"title": heading, "years": rows})
    cells = [[str(g[k]) for k in columns] for g in rows]
    if fmt == "md":
        return out.md_page(heading, [], out.md_table(columns, ([out.md_escape(c) for c in row]
                                                               for row in cells)), "colors.py")
    return out.html_page(heading, [], [out.html_table(columns, ([html.escape(c) for c in row]
                                                                for row in cells))], "colors.py")


# ---------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    out.use_utf8_output()
    p = out.parser(__doc__.split("\n\n\n")[0])
    out.add_church(p)
    out.add_span(p)
    out.add_output(p, FORMATS)
    p.add_argument("--days", choices=DAYS, default="principal",
                   help="all (every day), named (the principal days and every "
                        "festival and commemoration), principal (the default: the "
                        "Sundays and the days with a name of their own) or sundays")
    out.add_feasts(p, T.FEAST_DETAIL)
    out.add_colors(p)
    p.add_argument("--overview", action="store_true",
                   help="instead of the days, one row per year: its movable dates "
                        "and how many Sundays it holds (csv, html, json or md)")
    out.add_data(p, "with no church or year, the year folder to list as it stands; "
                    "otherwise the folder of rules (default: ./data)")
    out.add_year_options(p)
    a = p.parse_args(argv)

    data = out.data_dir(p, a)
    if a.list:
        return out.list_churches(data_dir=data)
    fmt = out.output_format(p, a, FORMATS)
    every = a.colors == "all"
    folder_mode = (a.church is None and a.year is None and a.start is None and a.end is None
                   and not a.overview)

    if folder_mode:
        for name in ("subcalendar", "calendar", "paschalion", "latin"):
            if getattr(a, name) is not None:
                p.error(f"--{name.replace('_', '-')} changes how a year is generated; name a "
                        "church or a year (a year folder is listed as it stands)")
        calendar = apply_feasts(Calendar(data), a.feasts)
        recs = records(calendar, a.days)
        label = calendar.tradition.label if getattr(calendar, "tradition", None) else ""
        first = last = calendar.settings.church_year_start.year
        heading = out.heading(label or calendar.settings.lectionary, "colors", first, last)
        text = FORMATS[fmt](recs, heading=heading, key=calendar.settings.lectionary,
                            span=False, every=every, years=[year_details(calendar)],
                            series={recs[0]["church_year"]: ics_series(calendar)} if recs else {},
                            calendar=calendar.settings.calendar)
        return out.write(text, a.output, out.default_name(None, first, last, "colors", fmt),
                         f"{len(recs)} days")

    defaults = out.config_defaults(data)
    key, named = out.church_and_year(p, a, defaults)
    try:
        tradition = T.find_tradition(data, key)
    except ValueError as exc:
        return out.unknown_church(exc, "colors.py")
    own = T.tradition_settings(data, tradition)
    calendar_name = a.calendar or own.get("calendar") or defaults["calendar"]
    paschalion = a.paschalion or defaults["paschalion"]
    latin = T.latin_names_wanted(a.latin, own, defaults["latin_names"])
    feasts = a.feasts or defaults["feast_detail"]
    subs = out.subcalendars(a, named, defaults)
    years: dict[int, tuple] = {}
    # One scratch folder for the whole run: the traditions' folders are copied
    # into it once, and each year writes only its own files.
    scratch = Path(tempfile.mkdtemp(prefix="colors-"))
    atexit.register(shutil.rmtree, scratch, True)

    def build(y: int) -> tuple:
        if y not in years:
            years[y] = build_year(y, data, key, calendar_name, paschalion, latin, feasts, subs,
                                  scratch=scratch)
        return years[y]

    def bounds(y: int) -> tuple:
        cy = build(y)[0]
        return out.day_fields(cy.start)["date"], out.day_fields(cy.end)["date"]

    try:
        first, last, start, end = out.span(p, a, defaults["year"], bounds)
    except ValueError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 2
    name = out.default_name(key if named else None, first, last,
                            "overview" if a.overview else "colors", fmt)

    if a.overview:
        if fmt == "ics":
            p.error("the overview is one row per year, not a list of days: it has no ics form")
        rows = [ny.overview(ny.ChurchYear(y, key, calendar_name, paschalion, data_dir=data,
                                          subcalendars=subs), latin)
                for y in range(first, last + 1)]
        heading = out.heading(tradition.label, "the year at a glance", first, last)
        return out.write(overview_text(fmt, rows, heading), a.output, name, f"{len(rows)} years")

    recs, details, series = [], [], {}
    for y in range(first, last + 1):
        cy, calendar = build(y)
        recs += records(calendar, a.days, start, end)
        details.append(year_details(calendar, cy))
        series[T.year_label(y)] = ics_series(calendar, cy)
    heading = out.heading(tradition.label, "colors", first, last)
    text = FORMATS[fmt](recs, heading=heading, key=key, span=first != last, every=every,
                        years=details, series=series, calendar=calendar_name)
    return out.write(text, a.output, name, f"{len(recs)} days")


if __name__ == "__main__":
    out.run(main)
