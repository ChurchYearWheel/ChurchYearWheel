#!/usr/bin/env python3
"""
The Bible readings of a church year, for one church: a list to print, keep or
import, the same readings the web page shows under each day's name.

    python lectionary.py elca 2025                 # 2025-26, as CSV on the screen
    python lectionary.py lcms-three-year 2026 -o lsb_2026-27.csv
    python lectionary.py episcopal 2025 -o readings.md --links
    python lectionary.py lcms-elhb-one-year 2027 -o elhb.ics   # for a calendar app
    python lectionary.py elca --from 2025 --to 2027 -o .       # three years, default name
    python lectionary.py elca 2025 --from 2026-03-01 --to 2026-04-30
    python lectionary.py lcms-three-year 2025 --feasts principal --readings -daily
    python lectionary.py --list                    # the churches, and which have readings

The year is the one the church year begins in (2025 = Advent 2025 to the eve
of Advent 2026); --from and --to take church years or dates.  Formats: csv
(one row per reading), html (a page to print), ics (iCalendar: one all-day
event per day, its readings in the description), json and md (Markdown, day
by day).  --links opens each citation at Bible Gateway or Bible.com in
--bible's version, as the page does.  --readings keeps some kinds of set
(day, feasts, dated, daily, office) as the page's Readings boxes do, and --feasts
leaves off the readings of the feasts the page's Feasts menu leaves off.

The readings come from the tradition's own data/<folder>/readings.csv and the
shared lectionaries in data/readings/ its `readings` setting names (--data
names another folder of rules than ./data); how those files are written is in
docs/traditions.md.  The page works the same out in
web/church_year.js (readingsIndex), and web/verify_readings.py checks that
the two agree; web/verify_links.py does the same for the links.
"""

from __future__ import annotations

import csv
import html
import re
import sys
import unicodedata
from pathlib import Path
from typing import Optional

# The shared modules (calendars.py, traditions.py, listing.py, links.py) live in lib/.
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import traditions as T
import listing as out
import links as bible

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

# What each kind of reading is called, unless the tradition renames it
# (church_year.js: READING_LABELS).
READING_LABELS = {
    "ot": "Old Testament", "ot2": "Old Testament", "ot_opt": "Old Testament (additional)",
    "psalm": "Psalm", "psalm_morning": "Psalm (morning)", "psalm_evening": "Psalm (evening)",
    "epistle": "Epistle", "gospel": "Gospel", "nt": "New Testament",
    "nt_opt": "New Testament (additional)", "introit": "Introit", "gradual": "Gradual", "verse": "Verse",
    "procession": "Procession", "morning": "Morning", "evening": "Evening",
    "first": "First Lesson", "second": "Second Lesson",
    "ot_s": "Old Testament (semicontinuous)", "psalm_s": "Psalm (semicontinuous)",
    "ot_c": "Old Testament (complementary)", "psalm_c": "Psalm (complementary)",
    "nt_gospel": "New Testament (Gospels)", "nt_epistle": "New Testament (Epistles)",
    "sermon": "Sermon Text", "story": "Story Text", "lesson": "Lesson", "apocrypha": "Apocrypha",
    "confessions": "Lutheran Confessions",
}

# Words of the date language that are not row ids.
RULE_WORDS = ("easter", "prev_easter", "start", "end", "next_start", "half_end")

# The kinds of set a day's readings fall into, in the order the web page's
# Readings boxes list them (church_year.js: READING_CATEGORIES): the day's
# own propers; a feast's or festival's; another day kept by its date or a
# date rule that the calendar has no row for (Ember and Rogation Days,
# Thanksgiving and national days, the Byzantine Saturdays before and after a
# feast); a daily or weekday lectionary; the additional readings a daily
# lectionary offers beside its own (LSB's, printed in italics, for reading
# more of the Bible); a table of psalms for daily prayer (LSB's, morning and
# evening by season and weekday); a plan of Bible reading kept by the calendar year
# rather than the church year (Reading the Word of God); and the lessons of
# the Office (Morning and Evening Prayer, Matins, a second or third service).
READING_CATEGORIES = ("day", "feasts", "dated", "daily", "additional", "psalms", "plan", "office")
OFFICE_TITLE = re.compile(r"\b(Morning|Evening) Prayer\b|\bLessons\b|\bMatins\b|\bVespers\b|\bMidnight Office\b|\bCompline\b"
                          r"|\bEvensong\b|\b(Second|Third) Service\b")
DAILY_TITLE = re.compile(r"\bDaily\b")
ADDITIONAL_TITLE = re.compile(r"\bAdditional Readings?\b")
PSALMS_TITLE = re.compile(r"^Psalms\b")
# A shared reading plan (data/readings/plan-*.csv): its rows are keyed
# `plan:N`, the Nth day of the calendar year that none of its other rows
# (its festivals) take, and its `cycle` is the year a cycle was first read.
PLAN_FILE = re.compile(r"^plan-")
PLAN_KEY = re.compile(r"plan:(\d+)")
# A shared lectionary of this name is a daily or weekday one throughout.
DAILY_FILE = re.compile(r"-(daily|weekday)$")
# A title of a day kept by its date rather than a saint's or a feast's: a
# set of one keyed to a month and day is not taken for a feast's.
DATED_TITLE = re.compile(r"\b(Ember|Rogation|Independence|Dominion|Remembrance|National|Founders)\b"
                         r"|\bThanksgiving Day\b|\bNew Year's Day\b|Gedenkens|Samefolkets"
                         r"|^\d+\. mai$|Nyttårsaften")
# A day named by the feast it comes before or after ("Saturday before
# Theophany") is not that feast's day.
RELATIVE_TITLE = re.compile(r"^(Saturday|Sunday) (before|after) ")
# Words that say nothing about which saint or feast a title names.
FEAST_STOP = frozenset((
    "st sts ss saint saints the of and day a an in on to for our lord apostle apostles "
    "evangelist martyr martyrs bishop blessed virgin feast festival holy jesus christ "
    "der die des tag und von").split())


def _int(value: str, default: int = 0) -> int:
    value = (value or "").strip()
    return int(value) if re.fullmatch(r"[+-]?\d+", value) else default


def reading_rows(path: Path) -> list[dict]:
    """A readings.csv (web/export_data.py: reading_rows).  Its #comment lines
    (plain, or quoted so that a spreadsheet keeps them in one cell) are dropped
    before the CSV is read, so they may hold commas and quotes."""
    if not path.exists():
        return []
    lines = [line for line in path.read_text(encoding="utf-8-sig").splitlines()
             if line.strip() and not line.lstrip().startswith(("#", '"#'))]
    rows = []
    for raw in csv.DictReader(lines):
        row = {(k or "").strip(): (v or "").strip() for k, v in raw.items() if k is not None}
        if row.get("kind") == "omit" or (row.get("day") and row.get("reading")):
            rows.append(row)
    return rows


def source_readings(source: T.Source) -> list[dict]:
    """The folder's own rows, then the shared lectionaries it names, less the
    shared rows its `omit` rows drop and with its `=kind` rows swapped in
    (church_year.js: Source)."""
    v = source.tradition.variant
    own = [r for r in reading_rows(source.folder / "readings.csv")
           if T.variant_matches(r.get("variant", ""), v)]
    names = [n for n in re.split(r"[\s,]+", source.settings.get("readings", "") or "") if n]
    shared = [reading_rows(source.data_dir / "readings" / f"{n}.csv") for n in names]
    omits = [r for r in own if r.get("kind") == "omit"]

    def dropped(r: dict) -> bool:
        for o in omits:
            day, cyc = o.get("day", ""), o.get("cycle", "")
            kinds = (o.get("reading", "") or "").split()
            if (o.get("title", "") == r.get("title", "")
                    and (not day or (day == r.get("day", "")
                                     and _int(o.get("offset")) == _int(r.get("offset"))))
                    and (not cyc or cyc == r.get("cycle", ""))
                    and (not kinds or r.get("kind", "") in kinds)):
                return True
        return False

    def key(r: dict, kind: str) -> tuple:
        return (r.get("day", ""), _int(r.get("offset")), r.get("cycle", ""), r.get("title", ""), kind)

    swaps: dict[tuple, list[dict]] = {}
    for r in own:
        kind = r.get("kind", "")
        if kind.startswith("="):
            swaps.setdefault(key(r, kind[1:]), []).append(r)

    def swapped(r: dict) -> dict:
        waiting = swaps.get(key(r, r.get("kind", "")))
        return dict(r, reading=waiting.pop(0)["reading"]) if waiting else r

    out = [r for r in own if r.get("kind") != "omit" and not r.get("kind", "").startswith("=")]
    for name, rows in zip(names, shared):
        # `_file` names the shared lectionary a row came from (a daily one
        # puts its sets among the daily readings).
        out += [dict(swapped(r), _file=name) for r in rows
                if T.variant_matches(r.get("variant", ""), v) and not dropped(r)]
    return out


def feast_shown(level: str, detail: str) -> bool:
    """Whether the Feasts setting `detail` keeps a feast of this level on the
    wheel (church_year.js: feastShown)."""
    if detail == "none":
        return False
    if detail == "principal":
        return level == "principal"
    if detail == "festivals":
        return level in ("principal", "festival")
    return True


def _title_words(text: str) -> set[str]:
    text = re.sub(r"[\u0300-\u036f]", "", unicodedata.normalize("NFKD", text or "")).lower()
    return {w for w in re.findall(r"[a-z0-9]+", text) if len(w) > 1 and w not in FEAST_STOP}


# The hours of the Office in the order of the day: a day's sets of the Office
# are listed by the hour they are read at, Matins before Vespers and Compline
# last, whatever order the file has them in (church_year.js: OFFICE_HOURS).
OFFICE_HOURS = [
    (re.compile(r"\b(Midnight|Nocturns?)\b"), 0),
    (re.compile(r"\b(Matins|Mattins|Lauds|Orthros|Morning)\b"), 1),
    (re.compile(r"\b(Prime|Terce|Sext|None|Midday|Noonday)\b"), 2),
    (re.compile(r"\b(Vespers|Evening|Evensong)\b"), 4),
    (re.compile(r"\bCompline\b"), 5),
]


def office_hour(group: dict) -> int:
    """Where a set falls in the day: an Office's by its hour, the rest at 3."""
    if group.get("category") != "office":
        return 3
    for pattern, hour in OFFICE_HOURS:
        if pattern.search(group["title"]):
            return hour
    return 3


def same_feast(title: str, name: str) -> bool:
    """Whether a set's title names this feast: they share a word that is not
    a saint's or a feast's common one ("St. Andrew, Apostle" and "St. Andrew";
    "Martinstag" and "Martin von Tours").  What follows a ": " in the title
    is the service ("All Saints' Day: Second Service") (church_year.js: sameFeast)."""
    a, b = _title_words(title.split(": ")[0]), _title_words(name)
    return any(x == y or (len(x) >= 5 and len(y) >= 5 and (x in y or y in x))
               for x in a for y in b)


class ReadingInfo:
    """What a folder's readings are tied to, worked out once for each Source
    (church_year.js: readingInfo): the days.csv ids and titles, and the
    feasts.csv ids and names by date -- every subcalendar's too, chosen or
    not, so that a feast left off with its calendar takes its readings."""

    def __init__(self, source: T.Source) -> None:
        v = source.tradition.variant
        self.day_ids = {r.get("id", "") for r in source.days if r.get("id")}
        self.day_titles = [r.get("title", "") for r in source.days if r.get("title")]
        feasts = list(source.feasts)
        for entry in source.subcalendar_list:
            feasts += [r for r in T.read_rows(source.folder / entry.get("file", ""))
                       if T.variant_matches(r.get("variant", ""), v)
                       and not (r.get("title") or r.get("from"))]
        self.feast_ids = {r.get("id", "") for r in feasts if r.get("id")}
        self.by_date: dict[str, list[str]] = {}
        for r in feasts:
            if r.get("date") and r.get("name"):
                self.by_date.setdefault(r["date"].strip(), []).append(r["name"])
        self.feast_names = [n for names in self.by_date.values() for n in names]
        self._day_words = [_title_words(t) for t in self.day_titles]
        # The days.csv titles of every variant of the folder: one that keeps
        # another language's names may read a sibling's English sets.
        self.folder_day_titles = [r.get("title", "") for r in T.read_rows(source.folder / "days.csv")
                                  if r.get("title")]
        # The days and offsets the day's own (untitled) propers are keyed to:
        # a titled set beside them is another of that day's ("Christmas Dawn
        # (Proper II)", "Three-year series").
        rows = source_readings(source)
        self.untitled = {(r.get("day", "").strip(), _int(r.get("offset")))
                         for r in rows if not r.get("title")}
        # The titles of sets keyed to a days.csv day: a heading of the day's
        # propers ("Three-year series"), wherever it is keyed.
        self.day_set_titles = {r.get("title", "") for r in rows if r.get("title")
                               and r.get("day", "").strip().split(":")[0] in self.day_ids}
        self._tied: dict[tuple, list[str]] = {}
        self._category: dict[tuple, str] = {}

    def is_feast_id(self, key: str) -> bool:
        return (re.fullmatch(r"[A-Za-z_]\w*", key) is not None and key not in self.day_ids
                and key in self.feast_ids)

    def tied(self, key: str, title: str) -> list[str]:
        """The feasts a titled set keyed to a date (not a feast's id) belongs
        to: those of its title kept on that same date."""
        k = (key, title)
        if k not in self._tied:
            self._tied[k] = ([n for n in self.by_date.get(key, []) if same_feast(title, n)]
                             if title else [])
        return self._tied[k]

    def names_day(self, title: str) -> bool:
        """Whether a title names one of the calendar's days.csv days: in the
        same words, or (unless it is a day before or after one) sharing one."""
        words = _title_words(title.split(": ")[0])
        if any(words == w for w in self._day_words):
            return True
        return (not RELATIVE_TITLE.search(title)
                and any(same_feast(title, t) for t in self.day_titles))

    def category(self, row: dict) -> str:
        key, title, file = row.get("day", "").strip(), row.get("title", ""), row.get("_file", "")
        offset = _int(row.get("offset"))
        k = (key, offset, title, file)
        if k not in self._category:
            m = re.fullmatch(r"([A-Za-z_]\w*)(?::\d+)?", key)
            relative = RELATIVE_TITLE.search(title) is not None
            if PLAN_FILE.search(file):
                cat = "plan"
            elif OFFICE_TITLE.search(title):
                cat = "office"
            elif ADDITIONAL_TITLE.search(title):
                cat = "additional"
            elif PSALMS_TITLE.search(title):
                cat = "psalms"
            elif DAILY_TITLE.search(title) or DAILY_FILE.search(file):
                cat = "daily"
            elif self.is_feast_id(key) or (title and self.tied(key, title)):
                cat = "feasts"
            elif not title or (m and m.group(1).lower() not in RULE_WORDS):
                cat = "day"
            elif ((key, offset) in self.untitled or title in self.day_set_titles
                  or self.names_day(title)):
                cat = "day"
            elif DATED_TITLE.search(title):
                cat = "dated"
            elif re.fullmatch(r"\d\d-\d\d", key):
                cat = "feasts"
            elif not relative and any(same_feast(title, n) for n in self.feast_names):
                cat = "feasts"
            elif not relative and any(same_feast(title, t) for t in self.folder_day_titles):
                cat = "day"
            else:
                cat = "dated"
            self._category[k] = cat
        return self._category[k]


def reading_info(source: T.Source) -> ReadingInfo:
    info = getattr(source, "_reading_info", None)
    if info is None:
        info = source._reading_info = ReadingInfo(source)
    return info


def categories(source: T.Source) -> list[str]:
    """The kinds of set this church's readings have, in READING_CATEGORIES order."""
    info = reading_info(source)
    found = {info.category(r) for r in source_readings(source)}
    return [c for c in READING_CATEGORIES if c in found]


def parse_categories(text: str) -> list[str]:
    """--readings (and the page's `readings=` link): `none`; `all`; the kinds
    to keep (`day,feasts`); or the kinds to leave out (`-daily,-office`)
    (page.js: readingKindsFrom)."""
    text = (text or "").strip().lower()
    if text in ("0", "false", "no", "off", "none"):
        return []
    if text in ("", "1", "true", "yes", "on", "all"):
        return list(READING_CATEGORIES)
    words = [w.strip() for w in text.split(",") if w.strip()]
    unknown = [w for w in words if w.lstrip("-") not in READING_CATEGORIES]
    if unknown:
        raise ValueError(f"no kind of reading '{unknown[0]}' (the kinds: "
                         f"{', '.join(READING_CATEGORIES)})")
    if any(w.startswith("-") for w in words):
        off = {w.lstrip("-") for w in words}
        return [c for c in READING_CATEGORIES if c not in off]
    return [c for c in READING_CATEGORIES if c in words]


def readings_index(year: T.Year, rows: list[dict],
                   detail: str = "") -> dict[int, list[dict]]:
    """Every day's readings: day -> [{title, category, items: [{kind, label,
    reading}]}] (church_year.js: readingsIndex).  A feast the wheel does not
    show that day -- left off by `detail` (the Feasts setting: all, festivals,
    principal or none; config.csv's feast_detail when blank), outranked,
    moved, or of a calendar not laid over it -- takes its readings with it."""
    out: dict[int, list[dict]] = {}
    if not rows:
        return out
    ctx = year.ctx
    cfg = year.settings
    psalter = str(cfg.get("psalter", "") or "").strip()
    detail = (detail or str(cfg.get("feast_detail", "") or "all")).strip().lower()
    if detail not in T.FEAST_DETAIL:
        detail = "all"
    info = reading_info(year.source)
    shown = [f for f in year.feasts if feast_shown(f.get("level", ""), detail)]
    shown_names: dict[int, list[str]] = {}
    for f in shown:
        shown_names.setdefault(f["day"], []).append(str(f.get("name") or ""))
    day_titles: dict[int, list[str]] = {}
    for e in year.principal:
        if e.get("title"):
            day_titles.setdefault(e["day"], []).append(str(e["title"]))
    labels = dict(READING_LABELS)
    for part in str(cfg.get("reading_labels", "") or "").split(";"):
        i = part.find("=")
        if i > 0:
            labels[part[:i].strip()] = part[i + 1:].strip()
    cycles: set[str] = set()
    for part in str(cfg.get("reading_cycle", "") or "").split(";"):
        words = part.split()
        if len(words) == 1 and words[0].lower() == "abc":
            cycles.add("ABC"[(year.year - 2025) % 3])
        elif len(words) == 1 and words[0].lower() == "year":
            cycles.add(str(year.year))
        elif len(words) > 2 and re.fullmatch(r"-?\d+", words[-1]):
            names = [w.upper() for w in words[:-1]]
            cycles.add(names[(year.year - int(words[-1])) % len(names)])
    by_id: dict[str, list[dict]] = {}
    for e in year.principal:
        if e.get("id"):
            by_id.setdefault(e["id"], []).append(e)
    # A feasts.csv row may be named too, on the day it is kept (after any
    # transfer), when no days.csv row has that id -- and only while the wheel
    # shows it.
    feast_id: dict[str, list[dict]] = {}
    for f in shown:
        if f.get("id"):
            feast_id.setdefault(f["id"], []).append(
                {"day": f["day"], "title": str(f.get("name") or "")})

    rot = str(cfg.get("reading_rotate", "") or "").strip().split()
    # The run's id, and any other rows that take a Sunday of it (TLH's
    # Transfiguration on the last Sunday after the Epiphany): "after_epiphany|transfiguration".
    rot_ids = rot[0].split("|") if rot else [""]
    rot_id = rot_ids[0]
    rot_total = _int(rot[1]) if len(rot) > 1 else 0
    rot_title = " ".join(rot[2:])
    rot_day: dict[int, dict] = {}
    if rot_id and rot_total:
        sundays = sorted((e for i in rot_ids for e in by_id.get(i, [])), key=lambda e: e["day"])
        n = len(sundays)
        kept = list(range(1, rot_total + 1))
        if n < rot_total:
            s = year.year % rot_total
            omit = {(s + i) % rot_total + 1 for i in range(rot_total - n)}
            kept = [w for w in kept if w not in omit]
        for j, w in enumerate(kept):
            if j < len(sundays):
                rot_day[w] = sundays[j]

    memo: dict[str, list] = {}

    def days_of(key: str) -> list:
        if key in memo:
            return memo[key]
        days: list = []
        m = re.fullmatch(r"([A-Za-z_]\w*)(?::(\d+))?", key)
        md = re.fullmatch(r"(\d\d)-(\d\d)", key)
        if m and m.group(1).lower() not in RULE_WORDS:
            n = None if m.group(2) is None else int(m.group(2))
            days = [(e["day"], str(e.get("title") or "").split("\n")[0])
                    for e in by_id.get(m.group(1), []) if n is None or e.get("number") == n]
            if not days and n is None:
                days = [(e["day"], e["title"].split("\n")[0]) for e in feast_id.get(m.group(1), [])]
        elif md:
            # A month and day may fall twice in a church year that starts late.
            month, dom = int(md.group(1)), int(md.group(2))
            for y in range(ctx.year_of(year.start), ctx.year_of(year.end) + 1):
                if year.reckoning.valid(y, month, dom):
                    days.append((year.reckoning.to_day(y, month, dom), ""))
        else:
            try:
                days = [(ctx.eval(key), "")]
            except Exception:
                days = []
        memo[key] = days
        return days

    # A reading plan (PLAN_FILE) is kept by the calendar year.  Its cycles
    # are the years they were first read, taken in turn; its rows keyed by a
    # date rule are its festivals, and `plan:N` is the Nth day of the year
    # that none of them takes.  A set past the year's plan days (a cycle
    # written for a leap year, read in a common one) is read on the last.
    plans: dict[str, dict] = {}
    for row in rows:
        f = row.get("_file", "")
        if PLAN_FILE.search(f):
            plan = plans.setdefault(f, {"cycles": set(), "fixed": {}})
            c = row.get("cycle", "").strip()
            if re.fullmatch(r"-?\d+", c):
                plan["cycles"].add(int(c))
            key = row.get("day", "").strip()
            if not PLAN_KEY.fullmatch(key):
                plan["fixed"].setdefault(c, set()).add(key)

    def plan_cycle(f: str, y: int) -> str:
        known = sorted(plans[f]["cycles"])
        return next((str(c) for c in known if (y - c) % len(known) == 0), "")

    plan_memo: dict[tuple, list[int]] = {}

    def plan_days(f: str, y: int) -> list[int]:
        """The plan days of calendar year y, in order."""
        k = (f, y)
        if k not in plan_memo:
            rk = year.reckoning
            first, last = rk.to_day(y, 1, 1), rk.to_day(y + 1, 1, 1) - 1
            taken: set[int] = set()
            for key in plans[f]["fixed"].get(plan_cycle(f, y), ()):
                md = re.fullmatch(r"(\d\d)-(\d\d)", key)
                if md:
                    if rk.valid(y, int(md.group(1)), int(md.group(2))):
                        taken.add(rk.to_day(y, int(md.group(1)), int(md.group(2))))
                    continue
                # A rule of the church year: the two that share this calendar year.
                for cy in (y - 1, y):
                    try:
                        z = year.context(cy).eval(key)
                    except Exception:
                        continue
                    if first <= z <= last:
                        taken.add(z)
            plan_memo[k] = [z for z in range(first, last + 1) if z not in taken]
        return plan_memo[k]

    civil_years = range(ctx.year_of(year.start), ctx.year_of(year.end) + 1)

    found: dict[int, list[dict]] = {}
    for row in rows:
        f = row.get("_file", "")
        plan = f if f in plans else ""
        want = row.get("cycle", "").strip().upper()
        if want and not plan and want not in cycles:
            continue
        offset = _int(row.get("offset"))
        category = info.category(row)
        # A set keyed to a date under a feast's name is that feast's: it is
        # read only where the wheel shows the feast (or the day's own title
        # names it), so Ember days, weekdays and the day's propers stay.
        tied = (info.tied(row.get("day", "").strip(), row.get("title", ""))
                if category not in ("daily", "psalms", "plan") else [])
        pm = PLAN_KEY.fullmatch(row.get("day", "").strip()) if plan else None
        if pm:
            n = int(pm.group(1))
            keyed = []
            for y in civil_years:
                days = plan_days(plan, y)
                if 0 < n <= len(days):
                    keyed.append((days[n - 1], ""))
                elif n > len(days) and days:
                    keyed.append((days[-1], ""))
        else:
            keyed = days_of(row.get("day", "").strip())
        if plan and want:
            keyed = [(b, nm) for b, nm in keyed if plan_cycle(plan, ctx.year_of(b + offset)) == want]
        if rot_id and row.get("title", "") == rot_title and offset > 0:
            m = re.fullmatch(re.escape(rot_id) + r":(\d+)", row.get("day", "").strip())
            if m:
                e = rot_day.get(int(m.group(1)))
                keyed = [(e["day"], str(e.get("title") or "").split("\n")[0])] if e else []
        for base, name in keyed:
            if tied and not any(n in tied for n in shown_names.get(base, [])) \
                    and not any(same_feast(row.get("title", ""), t) for t in day_titles.get(base, [])):
                continue
            day = base + offset
            if day < year.start or day > year.end:
                continue
            try:
                ok = ctx.holds(row.get("when", ""), day)
            except Exception:
                ok = False
            if not ok:
                continue
            own = not row.get("title", "")
            title = row.get("title", "") or ("" if offset else name)
            groups = found.setdefault(day, [])
            group = next((g for g in groups if g["title"] == title and g["own"] == own), None)
            if group is None:
                group = {"title": title, "own": own, "category": category, "items": []}
                groups.append(group)
            kind = row.get("kind", "")
            item = {"kind": kind, "label": labels.get(kind, kind), "reading": row.get("reading", "")}
            # A hymn's list and service (data/readings/lsb-hymns.csv).
            for k in ("service", "source"):
                if row.get(k):
                    item[k] = row[k]
            # The church's own psalms cited in its Prayer Book psalter's
            # verses (`psalter`): `cite` is the citation in the English ones,
            # for the links.
            if psalter and not row.get("_file") and "Psalm" in item["reading"]:
                cited = bible.psalter_citation(item["reading"], psalter)
                if cited != item["reading"]:
                    item["cite"] = cited
            group["items"].append(item)

    rank: dict[str, int] = {}
    for i, part in enumerate(str(cfg.get("reading_order", "") or "").split("|")):
        for k in part.split():
            rank[k] = i
    if rank:
        for groups in found.values():
            for g in groups:
                slots = [i for i, it in enumerate(g["items"]) if it["kind"] in rank]
                picked = sorted((g["items"][i] for i in slots), key=lambda it: rank[it["kind"]])
                for s, it in zip(slots, picked):
                    g["items"][s] = it
    # The hymns of a set (`reading_hymns`) are not readings: they go apart, as
    # its `hymns`, and a set of hymns alone is left out.
    hymn_kinds = hymns_of(cfg)

    def shaped(g: dict) -> dict:
        items = [it for it in g["items"] if it["kind"] not in hymn_kinds]
        hymns = [it for it in g["items"] if it["kind"] in hymn_kinds]
        out = {"title": g["title"], "category": g["category"], "items": items}
        if hymns:
            out["hymns"] = hymns
        return out

    for day, groups in found.items():
        ordered = sorted(enumerate(groups), key=lambda p: (-int(p[1]["own"]), office_hour(p[1]), p[0]))
        sets = [shaped(g) for _, g in ordered]
        sets = [g for g in sets if g["items"]]
        if sets:
            out[day] = sets
    return out



# ---------------------------------------------------------------------------
# A year of one church
# ---------------------------------------------------------------------------

def church_year(key: str, advent_year: int, data_dir: Path = DATA, *, subcalendars=(),
                calendar: str = "", paschalion: str = "",
                latin: bool = False, feasts: str = "") -> tuple[T.Year, dict]:
    year = out.year_of(key, advent_year, data_dir, subcalendars, calendar, paschalion, latin)
    return year, readings_index(year, source_readings(year.source), feasts)


def day_names(year: T.Year, detail: str = "all") -> dict[int, list[str]]:
    """What each day is called: its principal day, then the commemorations
    the Feasts setting `detail` keeps."""
    names: dict[int, list[str]] = {}
    for e in year.principal:
        if e.get("title"):
            names.setdefault(e["day"], []).append(" ".join(e["title"].split("\n")))
    for f in year.feasts:
        if not feast_shown(f.get("level", ""), detail):
            continue
        text = f.get("full_name") or f.get("name")
        if text and text not in names.get(f["day"], []):
            names.setdefault(f["day"], []).append(text)
    return names


def hymns_of(cfg: dict) -> set[str]:
    """The kinds that are hymns sung with a set, not readings (`reading_hymns`)."""
    return set(str(cfg.get("reading_hymns", "") or "").replace(",", " ").split())


def propers_of(cfg: dict) -> set[str]:
    """The kinds that are parts of the service rather than readings (`reading_propers`)."""
    return set(str(cfg.get("reading_propers", "") or "").replace(",", " ").split())


def split_propers(items: list[dict], propers: set[str]) -> tuple[list[dict], list[dict]]:
    """A set's readings, and its parts of the service (church_year.js: splitPropers)."""
    return ([it for it in items if it["kind"] not in propers],
            [it for it in items if it["kind"] in propers])


def plain(item: dict) -> dict:
    """A reading as the formats write it, without its link citation."""
    return {k: v for k, v in item.items() if k != "cite"}


def records(year: T.Year, index: dict, start: Optional[str], end: Optional[str],
            kinds=READING_CATEGORIES, site: str = "none", version: str = "ESV",
            feasts: str = "all", with_propers: bool = True) -> list[dict]:
    """Each day's readings of the kinds asked for (READING_CATEGORIES), as the
    formats write them.  With a site, each reading also has `links`: its
    parts, and where each opens.  A set's parts of the service
    (`reading_propers`: an Introit, a Gradual ...) come apart from its
    readings, as `propers`, unless `with_propers` is false; the set's link
    opens only its readings."""
    names = day_names(year, feasts)
    numbering = bible.numbering_books(year.settings.get("verse_numbering", ""))
    own = propers_of(year.settings)

    def item(it: dict) -> dict:
        return (dict(plain(it), links=bible.reading_links(it["reading"], version, site, numbering, it.get("cite")))
                if site != "none" else plain(it))

    def link(items: list[dict]) -> dict:
        return {"link": bible.group_url([it.get("cite", it["reading"]) for it in items], version, numbering)} \
            if site != "none" and items else {}

    def one(s: dict, title: str) -> dict:
        readings, parts = split_propers(s["items"], own)
        if not with_propers:
            parts = []
        out = {"title": title, **link(readings or parts), "readings": [item(it) for it in readings]}
        if parts:
            out["propers"] = [item(it) for it in parts]
            if site != "none" and readings:
                out["propers_link"] = link(parts)["link"]
        return out

    recs = []
    for day in sorted(index):
        fields = out.day_fields(day, year.reckoning)
        if (start and fields["date"] < start) or (end and fields["date"] > end):
            continue
        sets = [s for s in index[day] if s["category"] in kinds]
        if not with_propers:
            sets = [s for s in sets if any(it["kind"] not in own for it in s["items"])]
        if not sets:
            continue
        # A day's own propers have no title of their own: they carry its name.
        first = (names.get(day) or [""])[0]
        recs.append(dict(fields, church_year=year.label, names=names.get(day, []),
                         sets=[one(s, s["title"] or (first if len(sets) > 1 else "")) for s in sets]))
    return recs


# ---------------------------------------------------------------------------
# Writing it out
# ---------------------------------------------------------------------------

def _urls(it: dict) -> list[str]:
    return [url for _, url in it.get("links", []) if url]


def as_csv(recs: list[dict], span: bool, linked: bool, **_) -> str:
    own = out.has_own_dates(recs)
    header = ((["church_year"] if span else []) + ["date", "weekday"] + (["own_date"] if own else [])
              + ["day", "set", "kind", "label", "reading"] + (["url"] if linked else []))
    rows = []
    for r in recs:
        for s in r["sets"]:
            for it in s["readings"] + s.get("propers", []):
                rows.append(([r["church_year"]] if span else []) + [r["date"], r["weekday"]]
                            + ([r.get("own_date", "")] if own else [])
                            + [" / ".join(r["names"]), s["title"], it["kind"], it["label"],
                               it["reading"]]
                            + ([" ".join(_urls(it))] if linked else []))
    return out.csv_text(header, rows)


def as_json(recs: list[dict], heading: str, key: str, linked: bool, version: str, **_) -> str:
    days = []
    for r in recs:
        sets = []
        for s in r["sets"]:
            items = []
            for it in s["readings"]:
                item = {k: it[k] for k in ("kind", "label", "reading")}
                if linked:
                    item["urls"] = _urls(it)
                items.append(item)
            parts = [{k: it[k] for k in ("kind", "label", "reading")} | ({"urls": _urls(it)} if linked else {})
                     for it in s.get("propers", [])]
            sets.append({"title": s["title"], **({"url": s["link"]} if "link" in s else {}),
                         "readings": items,
                         **({"propers": parts} if parts else {}),
                         **({"propers_url": s["propers_link"]} if "propers_link" in s else {})})
        day = {k: r[k] for k in ("date", "weekday", "own_date", "names") if k in r}
        day["sets"] = sets
        days.append(day)
    return out.json_text({"title": heading, "church": key,
                          **({"bible": version} if linked else {}), "days": days})


def _set_heading(s: dict) -> str:
    return s["title"] or "Readings"


# What a set's parts of the service (reading_propers) are headed.
PROPERS = "Propers"


def _notes(linked: bool, site: str, version: str) -> list[str]:
    where = {"biblegateway": "Bible Gateway", "youversion": "Bible.com"}.get(site, "")
    return ([f"Each reading opens at {where} in the {version}; each heading opens its set's "
             "readings together at Bible Gateway (its propers apart)."] if linked else [])


def as_md(recs: list[dict], heading: str, calendar: str, linked: bool, site: str,
          version: str, **_) -> str:
    body = []
    for r in recs:
        body += [f"## {out.md_escape(out.long_date(r, calendar))}"
                 + (f" — {out.md_escape(' / '.join(r['names']))}" if r["names"] else ""), ""]
        for s in r["sets"]:
            if s["title"] or len(r["sets"]) > 1:
                body += [f"**{out.md_escape(_set_heading(s))}**", ""]
            line = lambda it: (f"- {out.md_escape(it['label'])}: "
                               + ("".join(out.md_link(t, u) for t, u in it["links"]) if linked
                                  else out.md_escape(it["reading"])))
            body += [line(it) for it in s["readings"]] + [""]
            if s.get("propers"):
                head = out.md_link(PROPERS, s["propers_link"]) if "propers_link" in s else PROPERS
                body += [f"*{head}*", ""] + [line(it) for it in s["propers"]] + [""]
    return out.md_page(heading, _notes(linked, site, version), body, "lectionary.py")


def as_html(recs: list[dict], heading: str, calendar: str, linked: bool, site: str,
            version: str, **_) -> str:
    e = html.escape
    body = []
    for r in recs:
        body.append(f"<h2>{e(out.long_date(r, calendar))}"
                    + (f" — {e(' / '.join(r['names']))}" if r["names"] else "") + "</h2>")
        for s in r["sets"]:
            if linked:
                # The heading opens the set's readings together at Bible Gateway.
                body.append(f"<h3>{out.html_link(s['title'] or 'Readings', s['link'])}</h3>")
            elif s["title"] or len(r["sets"]) > 1:
                body.append(f"<h3>{e(_set_heading(s))}</h3>")
            def table(items: list[dict], cls: str) -> str:
                return f'<table class="{cls}">' + "".join(
                    f"<tr><td>{e(it['label'])}</td><td>"
                    + ("".join(out.html_link(t, u) for t, u in it["links"]) if linked
                       else e(it["reading"])) + "</td></tr>"
                    for it in items) + "</table>"
            if s["readings"]:
                body.append(table(s["readings"], "readings"))
            if s.get("propers"):
                body.append("<h4>" + (out.html_link(PROPERS, s["propers_link"]) if "propers_link" in s
                                      else e(PROPERS)) + "</h4>")
                body.append(table(s["propers"], "readings propers"))
    return out.html_page(heading, _notes(linked, site, version), body, "lectionary.py")


def as_ics(recs: list[dict], heading: str, key: str, **_) -> str:
    stamp = out.ics_stamp(recs[0]["date"]) if recs else "20000101T000000Z"
    events = []
    for r in recs:
        body = []
        for s in r["sets"]:
            if s["title"] or len(r["sets"]) > 1:
                body.append(_set_heading(s) + ":")
            for it in s["readings"]:
                body.append(f"{it['label']}: {it['reading']}")
                body += _urls(it)
            if s.get("propers"):
                body.append(PROPERS + ":")
                for it in s["propers"]:
                    body.append(f"{it['label']}: {it['reading']}")
                    body += _urls(it)
        events.append(out.ics_event(f"{key}-{r['date'].replace('-', '')}@churchyearwheel",
                                    r["date"], stamp, " / ".join(r["names"]) or "Readings",
                                    "\n".join(body)))
    return out.ics_calendar(heading, "lectionary.py", events)


FORMATS = {"csv": as_csv, "html": as_html, "ics": as_ics, "json": as_json, "md": as_md}


def main(argv: Optional[list[str]] = None) -> int:
    out.use_utf8_output()
    p = out.parser(__doc__.split("\n\nThe readings come")[0])
    out.add_church(p)
    out.add_span(p)
    out.add_output(p, FORMATS)
    p.add_argument("--links", nargs="?", const="biblegateway", default="none",
                   choices=bible.SITES,
                   help="link each citation to Bible Gateway or Bible.com, as the page "
                        "does (default: none; --links alone: biblegateway)")
    p.add_argument("--no-links", dest="links", action="store_const", const="none",
                   help="plain citations (the default)")
    p.add_argument("--bible", choices=bible.VERSION_CODES, metavar="VERSION",
                   help="the version the links open in: " + ", ".join(bible.VERSION_CODES)
                        + " (default: the church's own, else ESV; within config.csv's "
                        "page_bibles, as on the web page)")
    p.add_argument("--readings", metavar="KINDS", default=None,
                   help="the kinds of readings to list, as the web page's Readings boxes "
                        "choose them: day (the day's propers), feasts (a feast's or "
                        "festival's), dated (other days kept by date: Ember and Rogation "
                        "Days, Thanksgiving and national days ...), daily (a daily or "
                        "weekday lectionary), additional (a daily lectionary's additional "
                        "readings), psalms (a table of psalms for daily prayer: LSB's), plan (a Bible "
                        "reading plan kept by the calendar year), "
                        "office (Morning and Evening Prayer, Matins ...): the ones to keep "
                        "(day,feasts) or to leave out (-daily,-office); default: all")
    p.add_argument("--no-daily", action="store_true",
                   help="leave out daily lectionaries, their additional readings, psalm tables, "
                        "reading plans and the Office's lessons "
                        "(--readings -daily,-additional,-psalms,-plan,-office)")
    p.add_argument("--no-propers", dest="propers", action="store_false",
                   help="leave out the parts of the service the church lists with its readings "
                        "(tradition.csv reading_propers: LCMS Introit, Gradual and Verse), for a "
                        "lector's list of the readings alone")
    out.add_feasts(p, T.FEAST_DETAIL)
    out.add_data(p)
    out.add_year_options(p)
    # `--readings -daily` would read as an option of its own: keep it with --readings.
    argv = list(sys.argv[1:] if argv is None else argv)
    for i in range(len(argv) - 1):
        if argv[i] == "--readings" and argv[i + 1].startswith("-") and argv[i + 1] != "--":
            argv[i:i + 2] = [f"--readings={argv[i + 1]}"]
            break
    a = p.parse_args(argv)
    data = out.data_dir(p, a)

    if a.list:
        return out.list_churches(lambda t: "" if source_readings(T.Source(data, t))
                                 else "   (no readings yet)", data)
    fmt = out.output_format(p, a, FORMATS)
    try:
        kinds = parse_categories(a.readings or "")
    except ValueError as exc:
        p.error(f"--readings: {exc}")
    if a.no_daily:
        kinds = [k for k in kinds if k not in ("daily", "additional", "psalms", "plan", "office")]
    defaults = out.config_defaults(data)
    feasts = a.feasts or defaults["feast_detail"]
    key, named = out.church_and_year(p, a, defaults)
    try:
        tradition = T.find_tradition(data, key)
    except ValueError as exc:
        return out.unknown_church(exc, "lectionary.py")
    own = T.tradition_settings(data, tradition)
    latin = T.latin_names_wanted(a.latin, own, defaults["latin_names"])
    # The versions config.csv's page_bibles lets the web page offer: the links
    # here open in the one the page would, and --bible keeps within them.
    bibles = bible.page_bibles(defaults["raw"].get("page_bibles", ""))
    page_version = bible.bible_default(own, bibles)
    if a.bible and (not bible.bible_allowed(a.bible, bibles)
                    or (bibles[:1] == ["own"] and a.bible != page_version)):
        p.error(f"--bible {a.bible}: config.csv's page_bibles ({' '.join(bibles)}) "
                f"does not offer it")
    version = a.bible or page_version
    years: dict[int, tuple] = {}

    def build(y: int) -> tuple:
        if y not in years:
            years[y] = church_year(key, y, data,
                                   subcalendars=out.subcalendars(a, named, defaults),
                                   calendar=a.calendar or "", paschalion=a.paschalion or "",
                                   latin=latin, feasts=feasts)
        return years[y]

    def bounds(y: int) -> tuple[str, str]:
        year = build(y)[0]
        return out.day_fields(year.start)["date"], out.day_fields(year.end)["date"]

    try:
        first, last, start, end = out.span(p, a, defaults["year"], bounds)
    except ValueError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 2
    recs = []
    for y in range(first, last + 1):
        year, index = build(y)
        if not index:
            print(f"✗ {year.tradition.label} has no readings yet", file=sys.stderr)
            return 1
        recs += records(year, index, start, end, kinds, a.links, version, feasts, a.propers)
    heading = out.heading(year.tradition.label, "readings", first, last)
    text = FORMATS[fmt](recs, heading=heading, key=year.tradition.key, span=first != last,
                        linked=a.links != "none", site=a.links, version=version,
                        calendar=year.calendar)
    return out.write(text, a.output, out.default_name(key if named else None, first, last,
                                                       "readings", fmt), f"{len(recs)} days")


if __name__ == "__main__":
    out.run(main)
