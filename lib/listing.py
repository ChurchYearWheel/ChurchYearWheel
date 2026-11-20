"""
What the listing scripts share: colors.py, feasts.py and lectionary.py take
the same arguments for the same things and write the same five formats the
same way.

    church year      a key from data/traditions.csv and the year the church
                     year begins in; both default to config.csv's
    --from/--to      a church year (2025) or a date (2026-03-01), either end
    -f/--format      csv, html, ics, json or md; else -o's extension, else csv
    -o/--output      a file, or a folder for the default name; else the screen
    --data           the folder of rules, ./data unless named

The dates listed are Gregorian, as a diary or calendar app names them; a church
year kept in another calendar adds its own date beside them (own_date).
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Callable, Iterable, Optional, Sequence

import traditions as T
from calendars import GREGORIAN, PASCHALIONS, RECKONINGS

HERE = Path(__file__).resolve().parent.parent
DATA = HERE / "data"

FORMATS = ("csv", "html", "ics", "json", "md")
WEEKDAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December")


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------

def use_utf8_output() -> None:
    """Keep the ✓ and ✗ in our messages, and the names, from crashing a run
    whose output is redirected under a C/POSIX locale or a Windows code page."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def run(main: Callable[[], int]) -> None:
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # Piped into head, less or similar and the reader closed early.  Point
        # stdout at the void so the interpreter's final flush stays quiet too.
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        raise SystemExit(0)


def config_defaults(data_dir: Path = DATA) -> dict:
    """config.csv's tradition, year, Latin names, calendar and feast detail."""
    from new_year import read_defaults
    found = read_defaults(data_dir)
    start = str(found["raw"].get("church_year_start", "") or "")
    found["year"] = int(start[:4]) if re.match(r"\d{4}-", start) else date.today().year
    return found


# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------

def parser(description: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description=description.strip(),
                                   formatter_class=argparse.RawDescriptionHelpFormatter)


def add_church(p: argparse.ArgumentParser) -> None:
    p.add_argument("church", nargs="?",
                   help="a key from data/traditions.csv (see --list; default: config.csv's lectionary)")
    p.add_argument("year", nargs="?", type=int,
                   help="the year the church year begins in (default: config.csv's)")


def add_span(p: argparse.ArgumentParser) -> None:
    p.add_argument("--from", dest="start", metavar="WHEN",
                   help="first church year (YYYY) or first date (YYYY-MM-DD)")
    p.add_argument("--to", dest="end", metavar="WHEN",
                   help="last church year (YYYY) or last date (YYYY-MM-DD)")


def add_year_options(p: argparse.ArgumentParser, latin: bool = True) -> None:
    p.add_argument("--subcalendar", action="append", default=None, metavar="KEY",
                   help="lay this calendar over the church's own, e.g. united_states "
                        "or jesuits (repeatable; 'none' for none; default: config.csv's "
                        "subcalendars, for its own church)")
    p.add_argument("--calendar", choices=sorted(RECKONINGS),
                   help="the calendar the year is kept in (default: the church's own)")
    p.add_argument("--paschalion", choices=sorted(PASCHALIONS),
                   help="the Easter reckoning (default: follows the calendar)")
    if latin:
        p.add_argument("--latin-names", dest="latin", action="store_true", default=None,
                       help="one-year series: add each Sunday's Latin name "
                            "(default: the church's own, as the page does)")
        p.add_argument("--no-latin-names", dest="latin", action="store_false",
                       help="plain titles")


def add_feasts(p: argparse.ArgumentParser, choices: Sequence[str]) -> None:
    p.add_argument("--feasts", choices=tuple(choices),   # most to fewest
                   help="how many feasts: all; festivals, those that color their "
                        "day or its lower half; " + ("principal, those whose color "
                        "replaces the season's; or none" if "none" in choices else
                        "or principal, those whose color replaces the season's")
                        + " (default: config.csv's feast_detail)")


def add_colors(p: argparse.ArgumentParser) -> None:
    p.add_argument("--colors", choices=("all", "primary"), default="primary",
                   help="primary: the one color of the day (default); all: also the "
                        "others the church allows and the lower half's color")


def add_data(p: argparse.ArgumentParser,
             text: str = "the folder of rules: traditions.csv, config.csv and the "
                         "churches' folders (default: ./data)") -> None:
    p.add_argument("--data", type=Path, default=None, metavar="DIR", help=text)


def data_dir(p: argparse.ArgumentParser, a: argparse.Namespace) -> Path:
    """--data's folder, else ./data; one that is not there stops the run."""
    folder = a.data or DATA
    if not folder.is_dir():
        p.error(f"no folder {folder}")
    return folder


def add_output(p: argparse.ArgumentParser, formats: Sequence[str] = FORMATS) -> None:
    p.add_argument("-f", "--format", choices=sorted(formats),
                   help="default: from -o's extension, else csv")
    p.add_argument("-o", "--output", metavar="PATH",
                   help="file to write, or a folder to write the default name into "
                        "(default: the screen)")
    p.add_argument("--list", action="store_true", help="list the churches and stop")


def church_and_year(p: argparse.ArgumentParser, a: argparse.Namespace,
                    defaults: dict) -> tuple[str, bool]:
    """The church's key, and whether it was named.  `feasts.py 2026` is a year."""
    if a.church is not None and a.year is None and re.fullmatch(r"-?\d+", a.church):
        a.church, a.year = None, int(a.church)
    named = a.church is not None
    return (a.church or defaults["lectionary"]).strip().lower(), named


def subcalendars(a: argparse.Namespace, named: bool, defaults: dict) -> list[str]:
    """--subcalendar's, 'none' for none; else config.csv's, for config.csv's own church."""
    if a.subcalendar is not None:
        return [k for k in a.subcalendar if k.lower() != "none"]
    return [] if named else list(defaults["subcalendars"])


def year_of(key: str, advent_year: int, data_dir: Path = DATA, subcalendars=(),
            calendar: str = "", paschalion: str = "", latin: bool = False) -> T.Year:
    """One church year of one church, worked out from its rules."""
    from new_year import read_defaults
    source = T.Source(data_dir, T.find_tradition(data_dir, key), subcalendars)
    return T.Year(source, advent_year, calendar, paschalion, latin,
                  settings=read_defaults(data_dir)["raw"])


def _when(p: argparse.ArgumentParser, text: Optional[str], flag: str):
    if text is None:
        return None
    text = text.strip()
    if re.fullmatch(r"-?\d{1,6}", text):
        return int(text)
    if re.fullmatch(r"\d{4}-\d\d-\d\d", text):
        try:
            date.fromisoformat(text)
        except ValueError:
            p.error(f"{flag} {text}: no such date")
        return text
    p.error(f"{flag} takes a year (2025) or a date (2025-11-30), not '{text}'")


def span(p: argparse.ArgumentParser, a: argparse.Namespace, default_year: int,
         bounds: Callable[[int], tuple[str, str]]) -> tuple[int, int, Optional[str], Optional[str]]:
    """The first and last church years, and the first and last dates, asked for.

    `bounds(year)` gives a church year's first and last Gregorian dates, so a
    date can be placed in the church year that holds it.
    """
    lo, hi = _when(p, a.start, "--from"), _when(p, a.end, "--to")
    if a.year is not None and isinstance(lo, int):
        p.error("give the year or --from YEAR, not both")

    def holding(iso: str) -> int:
        y = int(iso[:4])
        return y if iso >= bounds(y)[0] else y - 1

    first = (a.year if a.year is not None else lo if isinstance(lo, int)
             else holding(lo) if lo else default_year)
    last = hi if isinstance(hi, int) else holding(hi) if hi else first
    if last < first:
        p.error(f"--to {a.end} is before {T.year_label(first)}")
    return first, last, (lo if isinstance(lo, str) else None), (hi if isinstance(hi, str) else None)


def output_format(p: argparse.ArgumentParser, a: argparse.Namespace,
                  formats: Sequence[str] = FORMATS) -> str:
    fmt = a.format or (Path(a.output).suffix.lstrip(".").lower() if a.output else "") or "csv"
    fmt = {"markdown": "md", "htm": "html", "ical": "ics"}.get(fmt, fmt)
    if fmt not in formats:
        p.error(f"unknown format '{fmt}'; choose from {', '.join(sorted(formats))}")
    return fmt


def list_churches(note: Callable[[T.Tradition], str] = lambda t: "",
                  data_dir: Path = DATA) -> int:
    """The churches the page's menus offer: the traditions, and the churches in
    each, alphabetically (by name, as the menus list them)."""
    groups: dict[str, list] = {}
    for t in T.load_registry(data_dir):
        groups.setdefault(t.tradition, []).append(t)
    for tradition in sorted(groups):
        print(tradition)
        for t in sorted(groups[tradition], key=lambda t: t.label.casefold()):
            print(f"  {t.key:34} {t.label}{note(t)}")
    return 0


def unknown_church(exc: Exception, script: str) -> int:
    print(f"✗ {str(exc).split(';')[0]}; `python {script} --list` shows them all", file=sys.stderr)
    return 2


# ---------------------------------------------------------------------------
# Naming and writing
# ---------------------------------------------------------------------------

def span_label(first: int, last: int) -> str:
    """2025-26 for a year, 2025-2035 for a span."""
    return T.year_label(first) if first == last else f"{first}-{last}"


def heading(label: str, what: str, first: int, last: int) -> str:
    """ELCA: readings for 2025-26, or for 2025-26 to 2034-35."""
    years = T.year_label(first) + ("" if first == last else f" to {T.year_label(last)}")
    return f"{label}: {what} for {years}"


def default_name(key: Optional[str], first: int, last: int, kind: str, fmt: str) -> str:
    """church_year_2025-26_colors.csv for config.csv's church, else elca_2025-26_readings.md."""
    return f"{key or 'church_year'}_{span_label(first, last)}_{kind}.{fmt}"


def write(text: str, output: Optional[str], name: str, count: str) -> int:
    """To the screen, or to -o: a file, or a folder (existing, or written with
    a trailing slash) to put the default name in."""
    if not output:
        sys.stdout.write(text)
        return 0
    target = Path(output)
    if target.is_dir() or output.endswith(("/", "\\")):
        target = target / name
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        # newline="" keeps the CRLF line endings an .ics needs on every platform.
        with open(target, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
    except OSError as exc:
        print(f"✗ Could not write {target}: {exc}", file=sys.stderr)
        return 1
    print(f"✓ Wrote {target}  ({count})", file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# Days
# ---------------------------------------------------------------------------

def day_number(day) -> int:
    """A datetime.date or CivilDate as a day on the unbroken line."""
    if hasattr(day, "day_number"):
        return day.day_number
    return GREGORIAN.to_day(day.year, day.month, day.day)


def day_fields(z: int, reckoning=GREGORIAN) -> dict:
    """date (Gregorian), weekday and, in another calendar, own_date."""
    out = {"date": GREGORIAN.isoformat(z), "weekday": WEEKDAY_NAMES[T.weekday(z)]}
    own = reckoning.isoformat(z)
    if own != out["date"]:
        out["own_date"] = own
    return out


def has_own_dates(records: Iterable[dict]) -> bool:
    return any("own_date" in r for r in records)


def long_date(r: dict, calendar: str = "") -> str:
    """Sunday, November 30, 2025; in another calendar, its own date after it."""
    y, m, d = (int(x) for x in re.match(r"([+-]?\d+)-(\d\d)-(\d\d)$", r["date"]).groups())
    text = f"{r['weekday']}, {MONTH_NAMES[m - 1]} {d}, {y}"
    if r.get("own_date"):
        text += f" ({r['own_date']}" + (f" {calendar.replace('-', ' ').title()})" if calendar else ")")
    return text


# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

def split_color(text: str) -> tuple[str, list[str]]:
    """"PURPLE; blue" -> ("PURPLE", ["blue"]): the color drawn, then the others allowed."""
    first, _, rest = (text or "").partition(";")
    return first.strip().upper(), [a.strip() for a in rest.split(";") if a.strip()]


def color_text(name: str, alt: Sequence[str], every: bool) -> str:
    """The color as data writes it: BLUE, or with --colors all BLUE; violet."""
    return "; ".join([name] + list(alt)) if every and name else name


def color_words(name: str, alt: Sequence[str] = ()) -> str:
    """"purple (or blue)"; NONE is "no color" (page.js: colorWords)."""
    def say(c):
        return "no color" if c.lower() == "none" else c.lower().replace("_", " ")
    others = [say(a) for a in alt]
    return say(name) + (" (or " + " or ".join(others) + ")" if others else "")


def css_paint(fill: str) -> str:
    """A colors.csv fill as CSS paints it: "#ffffff/#bfbfbf" is the hatch of no
    color (page.js: cssPaint)."""
    ground, _, line = (fill or "").partition("/")
    if not line:
        return fill or ""
    return (f"repeating-linear-gradient(45deg, {line.strip()} 0 1.5px, "
            f"{ground.strip()} 1.5px 5px)")


def palette(source: T.Source) -> dict[str, str]:
    """Color name -> fill, the shared colors.csv under the church's own."""
    out = {}
    for path in (source.data_dir / "colors.csv", source.folder / "colors.csv"):
        for row in T.read_rows(path):
            if row.get("name"):
                out[row["name"].upper()] = row.get("fill", "")
    return out


# RFC 7986 COLOR takes a CSS color name.  Few clients show it, but those that
# do can tint the event with the day's liturgical color.
CSS_COLOR = {"BLUE": "blue", "WHITE": "white", "GREEN": "green",
             "PURPLE": "purple", "SCARLET": "crimson", "BLACK": "black",
             "RED": "red", "GOLD": "gold", "ROSE": "pink", "VIOLET": "violet"}


# ---------------------------------------------------------------------------
# The formats
# ---------------------------------------------------------------------------

def csv_text(header: Sequence[str], rows: Iterable[Sequence]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def json_text(payload) -> str:
    """JSON a person can read too: the top level a key a line, and each entry of
    a list of records (the years, the days) on a line of its own."""
    one = lambda v: json.dumps(v, ensure_ascii=False, separators=(", ", ": "))
    if not isinstance(payload, dict):
        return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    lines = []
    for k, v in payload.items():
        if isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
            body = ",\n".join("    " + one(x) for x in v)
            lines.append(f"  {one(k)}: [\n{body}\n  ]")
        else:
            lines.append(f"  {one(k)}: {one(v)}")
    return "{\n" + ",\n".join(lines) + "\n}\n"


def md_escape(text: str) -> str:
    return re.sub(r"([\\`*_\[\]<>|])", r"\\\1", str(text))


def md_link(text: str, url: Optional[str]) -> str:
    return f"[{md_escape(text)}](<{url}>)" if url else md_escape(text)


def md_table(header: Sequence[str], rows: Iterable[Sequence[str]]) -> list[str]:
    """Cells already escaped (they may hold links)."""
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(str(c).replace("\n", " ") for c in row) + " |" for row in rows]
    return lines + [""]


def footer(script: str) -> str:
    return f"Made by {script} from the church year calendar's data."


def md_page(title: str, notes: Sequence[str], body: list[str], script: str) -> str:
    lines = [f"# {md_escape(title)}", ""]
    if notes:
        lines += ["  \n".join(md_escape(n) for n in notes), ""]
    lines += body
    lines += ["---", "", md_escape(footer(script)), ""]
    return "\n".join(lines)


HTML_STYLE = (
    "body{font:15px/1.4 Georgia,serif;max-width:46em;margin:2em auto;padding:0 1em;"
    "color:#111;background:#fff}"
    "h2{font-size:1.05em;margin:1.4em 0 .2em}h3{font-size:.95em;margin:.4em 0 0;font-style:italic;"
    "font-weight:normal}p.note{color:#555;margin:.2em 0}footer{color:#555;font-size:.85em;"
    "margin-top:2em;border-top:1px solid #ccc;padding-top:.4em}"
    "table{border-collapse:collapse}td,th{padding:0 .8em 0 0;vertical-align:top;text-align:left}"
    "table.readings td:first-child{color:#555;white-space:nowrap}"
    "table.list{width:100%}table.list th{border-bottom:1px solid #999;font-size:.9em}"
    "table.list td{border-bottom:1px solid #e4e4e4;padding:.15em .8em .15em 0}"
    "td.date,td.color{white-space:nowrap}"
    ".sw{display:inline-block;width:.85em;height:.85em;border:1px solid #888;"
    "vertical-align:-.08em;margin-right:.35em;-webkit-print-color-adjust:exact;"
    "print-color-adjust:exact}"
    "a{color:#1a4f8b}@media print{h2{break-after:avoid}a{color:inherit;text-decoration:none}"
    "tr{break-inside:avoid}}"
)


def html_link(text: str, url: Optional[str]) -> str:
    e = html.escape
    return f'<a href="{e(url)}">{e(text)}</a>' if url else e(text)


def html_swatch(fill: str) -> str:
    return f'<span class="sw" style="background:{html.escape(css_paint(fill))}"></span>' if fill else ""


def html_table(header: Sequence[str], rows: Iterable[Sequence[str]], cls: str = "list") -> str:
    """Cells already escaped (they may hold links and swatches); a first
    column of dates, and a color with its swatch, do not wrap."""
    out = [f'<table class="{cls}">', "<tr>" + "".join(f"<th>{html.escape(h)}</th>" for h in header) + "</tr>"]
    for row in rows:
        out.append("<tr>" + "".join(f'<td class="date">{c}</td>' if i == 0 else
                                     f'<td class="color">{c}</td>' if c.startswith('<span class="sw"') else
                                     f"<td>{c}</td>" for i, c in enumerate(row)) + "</tr>")
    out.append("</table>")
    return "\n".join(out)


def html_page(title: str, notes: Sequence[str], body: list[str], script: str) -> str:
    e = html.escape
    out = ["<!doctype html>", '<html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           f"<title>{e(title)}</title>", f"<style>{HTML_STYLE}</style>",
           f"</head><body><h1>{e(title)}</h1>"]
    out += [f'<p class="note">{e(n)}</p>' for n in notes]
    out += body
    out.append(f"<footer>{e(footer(script))}</footer>")
    out.append("</body></html>")
    return "\n".join(out) + "\n"


# -- iCalendar ----------------------------------------------------------------
# An all-day event per day, marked free rather than busy, that Google
# Calendar, Apple Calendar and Outlook all import.  Each script makes its UIDs
# from the date and the church, not from the day's name, so importing a
# regenerated file updates the events already there instead of adding copies.
# DTSTAMP is taken from the year rather than the clock, so the same year always
# makes the same file.

def ics_text(text: str) -> str:
    return (text.replace("\\", "\\\\").replace(";", "\\;")
                .replace(",", "\\,").replace("\n", "\\n"))


def ics_fold(line: str) -> list[str]:
    """Split a content line at 75 octets, as RFC 5545 asks, without cutting a character."""
    out, current = [], ""
    for ch in line:
        limit = 75 if not out else 74          # continuation lines lose one to the space
        if len((current + ch).encode("utf-8")) > limit:
            out.append(current)
            current = ch
        else:
            current += ch
    out.append(current)
    return [out[0]] + [" " + part for part in out[1:]]


def ics_event(uid: str, day: str, stamp: str, summary: str, description: str = "",
              extra: Sequence[str] = ()) -> list[str]:
    """`day` is a Gregorian ISO date; `extra` are further properties, as written."""
    g = date.fromisoformat(day)
    return (["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{stamp}",
             f"DTSTART;VALUE=DATE:{g.strftime('%Y%m%d')}",
             f"DTEND;VALUE=DATE:{(g + timedelta(days=1)).strftime('%Y%m%d')}",
             f"SUMMARY:{ics_text(summary)}"]
            + ([f"DESCRIPTION:{ics_text(description)}"] if description else [])
            + list(extra) + ["TRANSP:TRANSPARENT", "END:VEVENT"])


def ics_stamp(first_day: str) -> str:
    return date.fromisoformat(first_day).strftime("%Y%m%dT000000Z")


def ics_calendar(name: str, script: str, events: Iterable[list[str]]) -> str:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0",
             f"PRODID:-//Church Year Wheel//{script}//EN",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
             f"X-WR-CALNAME:{ics_text(name)}", f"NAME:{ics_text(name)}"]
    for event in events:
        lines += event
    lines.append("END:VCALENDAR")
    return "\r\n".join(part for line in lines for part in ics_fold(line)) + "\r\n"
