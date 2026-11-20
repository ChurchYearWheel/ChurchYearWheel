#!/usr/bin/env python3
"""
The church traditions the wheel can draw, and how a year of one is worked out.

Every tradition is a folder under `data/` -- `data/LCMS/LSB`, `data/Roman`, ... --
holding what is particular to it:

    tradition.csv   its settings (anything config.csv can say, plus a few more)
    seasons.csv     season key -> color
    days.csv        the principal days: Sundays, festivals, fasts, as rules
    periods.csv     the seasons, the halves of the year and the cycles, as rules
    feasts.csv      the saints' days and other commemorations
    colors.csv      optional: colors of its own, over the shared palette
    text_styles.csv optional: styles of its own, over the shared ones
    subcalendars.csv  optional: extra calendars that can be laid over it
                      (national, religious-order and personal calendars)

`data/traditions.csv` lists what the Tradition, Church and Series menus offer.  A row names a
folder and, optionally, a variant within it: LCMS One-year and LCMS Three-year
are one folder whose rows say which series they belong to.

Nothing here draws.  `resolve()` turns a tradition and a year into the same
dated rows the rest of the package has always drawn from -- the Sundays and
principal days, the seasons, the halves, the commemorations -- and the browser
does exactly the same in `web/church_year.js`, which is checked against this
by `web/verify.py`.

The rules are written in a small date language, described in
docs/traditions.md.  In short:

    easter+49            Pentecost               12-25        Christmas
    sun<12-25-21         Advent Sunday           sun>=01-02   the Sunday on or after 2 January
    thu#4:11             the fourth Thursday of November
    mon#-1:05            the last Monday of May
    max(sun>01-06, @epiphany+1)                  @name        another row's date
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

from calendars import (ALEXANDRIAN_EPOCHS, PASCHALIONS, RECKONINGS, Reckoning,
                       alexandrian_to_day, alexandrian_valid, alexandrian_year)

ORDINALS = [
    "", "First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh",
    "Eighth", "Ninth", "Tenth", "Eleventh", "Twelfth", "Thirteenth",
    "Fourteenth", "Fifteenth", "Sixteenth", "Seventeenth", "Eighteenth",
    "Nineteenth", "Twentieth", "Twenty-first", "Twenty-second",
    "Twenty-third", "Twenty-fourth", "Twenty-fifth", "Twenty-sixth",
    "Twenty-seventh", "Twenty-eighth", "Twenty-ninth", "Thirtieth",
    "Thirty-first", "Thirty-second", "Thirty-third", "Thirty-fourth",
    "Thirty-fifth", "Thirty-sixth", "Thirty-seventh", "Thirty-eighth",
    "Thirty-ninth", "Fortieth",
]

WEEKDAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}

# How much of the feasts file to draw.
FEAST_DETAIL = ("all", "festivals", "principal", "none")

# The festival half can end in one of three places; see docs/liturgy.md.
HALF_ENDS = {"pentecost-eve": "easter+48", "pentecost-week": "easter+55",
             "trinity-week": "easter+62"}


def weekday(z: int) -> int:
    """Monday 0 ... Sunday 6, from the unbroken line of days."""
    return (z + 3) % 7


# ---------------------------------------------------------------------------
# Reading the files
# ---------------------------------------------------------------------------

def read_rows(path: Path) -> list[dict]:
    """A CSV as dicts with every cell stripped.  Blank and #comment rows are skipped."""
    if not path.exists():
        return []
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        for raw in csv.DictReader(handle):
            row = {(k or "").strip(): (v or "").strip() for k, v in raw.items()
                   if k is not None}
            values = list(row.values())
            if not any(values):
                continue
            if values and values[0].startswith("#"):
                continue
            rows.append(row)
    return rows



def latin_names_wanted(asked, own: dict, fallback: bool) -> bool:
    """Whether to add Latin names: as asked, else the tradition's own default
    (tradition.csv `latin_names_default`, e.g. LCMS One-year), else config.csv."""
    if asked is not None:
        return bool(asked)
    if str(own.get("latin_names_default", "")).strip():
        return _truthy(own["latin_names_default"])
    return bool(fallback)


def year_label(year: int) -> str:
    """A church year's short name, as in file names: 2026-27, 9999-10000, 6-5BC.

    The page names years the same way, written out (spanName in church_year.js).
    """
    if year >= 1 and year + 1 <= 9999:
        return f"{year}-{(year + 1) % 100:02d}"
    if year < 1 and year + 1 < 1:
        return f"{1 - year}-{-year}BC"
    if year == 0:
        return "1BC-1"
    return f"{year}-{year + 1}"

class Tradition:
    """One calendar the page offers: a tradition, a church and maybe a series."""

    def __init__(self, row: dict) -> None:
        self.key = row.get("key", "")
        self.label = row.get("label", "") or self.key
        self.tradition = row.get("tradition", "")
        self.church = row.get("church", "") or self.label
        self.series = row.get("series", "")
        self.series_menu = row.get("series_menu", "")
        self.folder = row.get("folder", "")
        self.variant = row.get("variant", "")
        self.book = row.get("book", "")
        self.book_menu = row.get("book_menu", "")

    def as_dict(self) -> dict:
        return {"key": self.key, "label": self.label, "tradition": self.tradition,
                "church": self.church, "series": self.series,
                "seriesMenu": self.series_menu,
                "book": self.book, "bookMenu": self.book_menu,
                "folder": self.folder, "variant": self.variant}


def load_registry(data_dir: Path) -> list[Tradition]:
    rows = read_rows(data_dir / "traditions.csv")
    return [Tradition(r) for r in rows if r.get("key")]


def find_tradition(data_dir: Path, key: str) -> Tradition:
    wanted = (key or "").strip().lower()
    registry = load_registry(data_dir)
    if not registry:
        raise ValueError(f"no traditions listed in {data_dir / 'traditions.csv'}")
    for tradition in registry:
        if tradition.key == wanted:
            return tradition
    raise ValueError(f"no tradition '{key}' in {data_dir / 'traditions.csv'}; "
                     f"choose from {', '.join(t.key for t in registry)}")


def variant_matches(cell: str, variant: str) -> bool:
    """A blank cell applies to every variant; otherwise a space-separated list."""
    cell = (cell or "").strip().lower()
    if not cell:
        return True
    return (variant or "").lower() in cell.replace(",", " ").split()


def folder_path(data_dir: Path, tradition: Tradition) -> Path:
    """Where the tradition's own files are: its folder, as traditions.csv names it."""
    candidate = data_dir / tradition.folder
    if not tradition.folder or not candidate.is_dir():
        raise ValueError(f"tradition '{tradition.key}' has no folder "
                         f"{candidate if tradition.folder else '(none named)'}")
    return candidate


def tradition_settings(data_dir: Path, tradition: Tradition) -> dict[str, str]:
    """The tradition's own settings, for its variant.  Later rows win."""
    out: dict[str, str] = {}
    folder = folder_path(data_dir, tradition)
    for row in read_rows(folder / "tradition.csv"):
        name = row.get("setting", "")
        if not name or not variant_matches(row.get("variant", ""), tradition.variant):
            continue
        out[name] = row.get("value", "")
    return out


class Source:
    """Everything a tradition's folder says, filtered to its variant."""

    def __init__(self, data_dir: Path, tradition: Tradition,
                 subcalendars: Iterable[str] = ()) -> None:
        self.data_dir = data_dir
        self.tradition = tradition
        self.folder = folder_path(data_dir, tradition)
        self.settings = tradition_settings(data_dir, tradition)
        v = tradition.variant
        self.days = [r for r in read_rows(self.folder / "days.csv")
                     if variant_matches(r.get("variant", ""), v)]
        self.periods = [r for r in read_rows(self.folder / "periods.csv")
                        if variant_matches(r.get("variant", ""), v)]
        self.feasts = [r for r in read_rows(self.folder / "feasts.csv")
                       if variant_matches(r.get("variant", ""), v)]
        self.subcalendar_list = read_rows(self.folder / "subcalendars.csv")
        self.chosen: list[str] = []
        for key in subcalendars:
            if key:
                self.apply_subcalendar(key)

    def apply_subcalendar(self, key: str) -> None:
        entry = next((s for s in self.subcalendar_list if s.get("key") == key), None)
        if entry is None:
            print(f"  ! no subcalendar '{key}' for {self.tradition.label}", file=sys.stderr)
            return
        if key in self.chosen:
            return
        for other in (entry.get("include", "") or "").split():
            self.apply_subcalendar(other)
        self.chosen.append(key)
        rows = [r for r in read_rows(self.folder / entry.get("file", ""))
                if variant_matches(r.get("variant", ""), self.tradition.variant)]
        merge_rows(self.days, self.feasts, rows, key)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def merge_rows(days: list[dict], feasts: list[dict], extra: list[dict],
               source: str) -> None:
    """Lay a subcalendar's rows over the tradition's own.

    A row whose `id` names an existing row changes that row: every cell it
    fills replaces the one there, and `action=remove` takes the row out.  A row
    with no id that falls on the same date as a feast of the same name also
    changes it rather than adding a second copy.  Anything else is added.
    """
    for row in extra:
        action = (row.get("action", "") or "").lower()
        target = None
        rid = row.get("id", "")
        if rid:
            for table in (days, feasts):
                for existing in table:
                    if existing.get("id", "") == rid:
                        target = (table, existing)
                        break
                if target:
                    break
        if target is None and not rid and row.get("date") and row.get("name"):
            for existing in feasts:
                if (existing.get("date", "") == row.get("date")
                        and slug(existing.get("name", "")) == slug(row.get("name", ""))):
                    target = (feasts, existing)
                    break
        if target is not None:
            table, existing = target
            if action == "remove":
                table.remove(existing)
                continue
            for k, v in row.items():
                if k in ("action",) or v == "":
                    continue
                existing[k] = "" if v == "-" else v
            existing["source"] = source
            continue
        if action == "remove":
            continue
        added = dict(row)
        added["source"] = source
        # A new principal day (a rule) or a new feast (a name).
        if added.get("title") or added.get("from"):
            days.append(added)
        else:
            feasts.append(added)


# ---------------------------------------------------------------------------
# The date language
# ---------------------------------------------------------------------------

# Words that name a date in another calendar: julian(12-25), coptic(04-29).
OTHER_CALENDARS = ("gregorian", "julian", "coptic", "ethiopian")

_TOKEN = re.compile(r"\s*(y-?\d+:\d\d-\d\d|\d\d-\d\d|@[A-Za-z_]\w*|[A-Za-z_]\w*"
                    r"|\d+|>=|<=|[<>+\-(),#:])")


def tokenize(text: str) -> list[str]:
    tokens, pos, text = [], 0, text.strip()
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if not m or m.end() == pos:
            raise ValueError(f"cannot read date rule {text!r} at {text[pos:]!r}")
        tokens.append(m.group(1))
        pos = m.end()
        while pos < len(text) and text[pos].isspace():
            pos += 1
    return tokens


class Context:
    """One church year of one tradition, as the rules see it."""

    def __init__(self, reckoning: Reckoning, paschalion: str, year: int,
                 variant: str, latin: bool, settings: dict,
                 subcalendars: Iterable[str] = ()) -> None:
        self.reckoning = reckoning
        self.paschalion = paschalion
        self.year = year
        self.variant = variant
        self.latin = latin
        self.settings = settings
        self.subcalendars = set(subcalendars)
        self.ids: dict[str, str] = {}          # id -> the rule that dates it
        self.memo: dict[str, int] = {}
        self.busy: set[str] = set()
        self.start: Optional[int] = None
        self.end: Optional[int] = None
        self.next_start: Optional[int] = None
        self._easter: Optional[int] = None

    # -- anchors ------------------------------------------------------------

    def year_of(self, z: int) -> int:
        return self.reckoning.from_day(z)[0]

    def easter(self) -> int:
        if self._easter is None:
            rule = PASCHALIONS[self.paschalion]
            y = self.year_of(self.start)
            day = rule(y)
            if day < self.start:
                day = rule(y + 1)
            self._easter = day
        return self._easter

    def month_day(self, month: int, day: int) -> int:
        """The first time this date comes round on or after the year's start."""
        if self.start is None:                 # working out the start itself
            return self.reckoning.to_day(self.year, month, day)
        y = self.year_of(self.start)
        for candidate in (y, y + 1, y + 2):
            if self.reckoning.valid(candidate, month, day):
                z = self.reckoning.to_day(candidate, month, day)
                if z >= self.start:
                    return z
        raise ValueError(f"no {month:02d}-{day:02d} after the start of the year")

    def prev_easter(self) -> int:
        """The last Easter before the year begins, for counting the Sundays
        after Pentecost into a year that starts in September."""
        rule = PASCHALIONS[self.paschalion]
        y = self.year_of(self.start)
        day = rule(y)
        while day >= self.start:
            y -= 1
            day = rule(y)
        return day

    def other_month_day(self, calendar: str, month: int, day: int) -> int:
        """The first `month-day` in another calendar on or after the year's
        start: julian(12-25), coptic(04-29), ethiopian(01-17)."""
        base = (self.start if self.start is not None
                else self.reckoning.to_day(self.year, 1, 1))
        if calendar in ALEXANDRIAN_EPOCHS:
            y = alexandrian_year(calendar, base)
            for candidate in (y, y + 1, y + 2):
                if alexandrian_valid(candidate, month, day):
                    z = alexandrian_to_day(calendar, candidate, month, day)
                    if z >= base:
                        return z
        else:
            reckoning = RECKONINGS[calendar]
            y = reckoning.from_day(base)[0]
            for candidate in (y, y + 1, y + 2):
                if reckoning.valid(candidate, month, day):
                    z = reckoning.to_day(candidate, month, day)
                    if z >= base:
                        return z
        raise ValueError(f"no {calendar} {month:02d}-{day:02d} after the start of the year")

    def month_start(self, month: int) -> tuple[int, int]:
        """The year of the first such month beginning on or after the start."""
        if self.start is None:
            return self.year, month
        y = self.year_of(self.start)
        for candidate in (y, y + 1):
            if self.reckoning.to_day(candidate, month, 1) >= self.start:
                return candidate, month
        return y + 1, month

    def ref(self, name: str) -> int:
        if name in self.memo:
            return self.memo[name]
        if name not in self.ids:
            raise ValueError(f"no row with id '{name}'")
        if name in self.busy:
            raise ValueError(f"row '{name}' is dated in terms of itself")
        self.busy.add(name)
        try:
            value = self.eval(self.ids[name])
        finally:
            self.busy.discard(name)
        self.memo[name] = value
        return value

    def half_end(self) -> int:
        rule = str(self.settings.get("festival_half_end", "auto") or "auto").strip().lower()
        if rule == "auto":
            rule = str(self.settings.get("festival_half_end_auto", "pentecost-week")
                       or "pentecost-week").strip().lower()
        return self.eval(HALF_ENDS.get(rule, rule))

    # -- expressions ----------------------------------------------------------

    def eval(self, text: str) -> int:
        tokens = tokenize(text)
        value, pos = self._additive(tokens, 0)
        if pos != len(tokens):
            raise ValueError(f"unexpected {tokens[pos]!r} in date rule {text!r}")
        return value

    def _additive(self, t: list[str], pos: int) -> tuple[int, int]:
        value, pos = self._primary(t, pos)
        while pos < len(t) and t[pos] in "+-" and pos + 1 < len(t) and t[pos + 1].isdigit():
            n = int(t[pos + 1])
            value = value + n if t[pos] == "+" else value - n
            pos += 2
        return value, pos

    def _primary(self, t: list[str], pos: int) -> tuple[int, int]:
        if pos >= len(t):
            raise ValueError("a date rule ended too soon")
        tok = t[pos]
        low = tok.lower()
        if tok == "(":
            value, pos = self._additive(t, pos + 1)
            if pos >= len(t) or t[pos] != ")":
                raise ValueError("missing ')' in a date rule")
            return value, pos + 1
        if low in ("max", "min") and pos + 1 < len(t) and t[pos + 1] == "(":
            a, p = self._additive(t, pos + 2)
            if p >= len(t) or t[p] != ",":
                raise ValueError(f"{low}() takes two dates")
            b, p = self._additive(t, p + 1)
            if p >= len(t) or t[p] != ")":
                raise ValueError(f"missing ')' after {low}()")
            return (max(a, b) if low == "max" else min(a, b)), p + 1
        if low in WEEKDAYS and pos + 1 < len(t):
            wd = WEEKDAYS[low]
            op = t[pos + 1]
            if op == "#":
                p = pos + 2
                sign = 1
                if p < len(t) and t[p] == "-":
                    sign, p = -1, p + 1
                count = sign * int(t[p])
                if t[p + 1] != ":":
                    raise ValueError("write the nth weekday as thu#4:11")
                month = int(t[p + 2])
                return self.nth_weekday(month, wd, count), p + 3
            if op in (">=", ">", "<=", "<"):
                base, p = self._primary(t, pos + 2)
                return self.weekday_from(base, wd, op), p
        if re.fullmatch(r"\d\d-\d\d", tok):
            return self.month_day(int(tok[:2]), int(tok[3:])), pos + 1
        if low in OTHER_CALENDARS and pos + 3 < len(t) and t[pos + 1] == "(" \
                and re.fullmatch(r"\d\d-\d\d", t[pos + 2]) and t[pos + 3] == ")":
            md = t[pos + 2]
            return self.other_month_day(low, int(md[:2]), int(md[3:])), pos + 4
        m = re.fullmatch(r"y(-?\d+):(\d\d)-(\d\d)", tok)
        if m:
            y = self.year_of(self.start) + int(m.group(1)) if self.start is not None \
                else self.year + int(m.group(1))
            return self.reckoning.to_day(y, int(m.group(2)), int(m.group(3))), pos + 1
        if tok.startswith("@"):
            return self.ref(tok[1:]), pos + 1
        if low == "easter":
            return self.easter(), pos + 1
        if low == "prev_easter":
            return self.prev_easter(), pos + 1
        if low == "start":
            return self.start, pos + 1
        if low == "end":
            return self.end, pos + 1
        if low == "next_start":
            return self.next_start, pos + 1
        if low == "half_end":
            return self.half_end(), pos + 1
        raise ValueError(f"unknown word {tok!r} in a date rule")

    @staticmethod
    def weekday_from(base: int, wd: int, op: str) -> int:
        if op == ">=":
            return base + (wd - weekday(base)) % 7
        if op == ">":
            return base + 1 + (wd - weekday(base + 1)) % 7
        if op == "<=":
            return base - (weekday(base) - wd) % 7
        return base - 1 - (weekday(base - 1) - wd) % 7        # "<"

    def nth_weekday(self, month: int, wd: int, count: int) -> int:
        y, m = self.month_start(month)
        if count > 0:
            first = self.reckoning.to_day(y, m, 1)
            return first + (wd - weekday(first)) % 7 + 7 * (count - 1)
        last = self.reckoning.to_day(y, m, self.reckoning.days_in_month(y, m))
        return last - (weekday(last) - wd) % 7 + 7 * (count + 1)

    # -- conditions -----------------------------------------------------------

    def holds(self, when: str, date: Optional[int] = None) -> bool:
        """Every clause of a `when` cell, separated by '&', must hold."""
        when = (when or "").strip()
        if not when:
            return True
        for clause in when.split("&"):
            # "A or B and C": the clause holds when any of its alternatives
            # does, each of them its conditions joined by "and".
            alts = re.split(r"\s+or\s+", clause.strip())
            if len(alts) > 1 or re.search(r"\s+and\s+", clause):
                if not any(all(self.holds(c, date) for c in re.split(r"\s+and\s+", a)) for a in alts):
                    return False
                continue
            words = clause.split()
            if not words:
                continue
            if len(words) == 1:
                flag = words[0].lower()
                negate = flag.startswith("!")
                flag = flag.lstrip("!")
                if flag == "latin":
                    ok = self.latin
                elif flag.startswith("sub:"):
                    ok = flag[4:] in self.subcalendars
                else:
                    raise ValueError(f"unknown condition {words[0]!r}")
                if ok == negate:
                    return False
                continue
            if len(words) != 3:
                raise ValueError(f"cannot read condition {clause.strip()!r}")
            left, op, right = words
            if left.lower() == "year":
                # The church year, by the calendar year it begins in: a rule
                # that took effect then (Wales's colors, `year ge 2011`).
                b = int(right)
                ok = {"eq": self.year == b, "ne": self.year != b, "lt": self.year < b,
                      "le": self.year <= b, "gt": self.year > b, "ge": self.year >= b}.get(op)
                if ok is None:
                    raise ValueError(f"unknown comparison {op!r}")
                if not ok:
                    return False
                continue
            if left.lower() == "variant":
                ok = (self.variant or "").lower() in right.lower().split("|")
                if (op == "eq") != ok:
                    return False
                continue
            if op in ("wd", "nwd"):
                day = date if left.lower() == "date" else self.eval(left)
                if day is None:
                    raise ValueError("'date' used where a row has none")
                names = right.lower().split("|")
                ok = any(WEEKDAYS.get(n) == weekday(day) for n in names)
                if (op == "wd") != ok:
                    return False
                continue
            a = date if left.lower() == "date" else self.eval(left)
            b = date if right.lower() == "date" else self.eval(right)
            if a is None or b is None:
                raise ValueError("'date' used where a row has none")
            ok = {"eq": a == b, "ne": a != b, "lt": a < b, "le": a <= b,
                  "gt": a > b, "ge": a >= b}.get(op)
            if ok is None:
                raise ValueError(f"unknown comparison {op!r}")
            if not ok:
                return False
        return True


# ---------------------------------------------------------------------------
# A year
# ---------------------------------------------------------------------------

def _pick(cell: str, index: int) -> str:
    """A cell may hold one value, or one per step of a sequence split by '|'."""
    if "|" not in (cell or ""):
        return cell or ""
    parts = cell.split("|")
    return parts[index] if index < len(parts) else ""


def _int(cell: str, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(cell) if cell not in (None, "") else default
    except ValueError:
        return default


def _first(ctx, cell, default):
    """A run's `first`: a number, or a date rule the days are counted in weeks
    from (`prev_easter+49`: the Sunday a week after Pentecost is 1)."""
    text = (cell or "").strip()
    if not text or re.fullmatch(r"[+-]?\d+", text):
        return _int(text, default), None
    return default, ctx.eval(text)


def _count(mode: str, first: int, index: int, length: int) -> int:
    """A run's number for its index-th day.

    Blank counts up from `first`.  `down` ends on `first`, counting up to it
    (the Roman 34th Sunday of Ordinary Time, Proper 29).  `before` ends on
    `first` counting down to it ("Fourth, Third, Second Sunday before Advent").
    """
    mode = (mode or "").strip().lower()
    if mode == "down":
        return first - (length - 1 - index)
    if mode == "before":
        return first + (length - 1 - index)
    return first + index


def _ordinal(number: int) -> str:
    return ORDINALS[number] if 0 <= number < len(ORDINALS) else f"{number}th"


def _roman(number: int) -> str:
    """Roman numerals, for churches that number their Sundays I, II, III..."""
    if number <= 0:
        return str(number)
    out = ""
    for value, letters in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
                           (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
                           (5, "V"), (4, "IV"), (1, "I")):
        while number >= value:
            out += letters
            number -= value
    return out


def _title(template: str, number: int, name: str, number2: Optional[int] = None) -> str:
    """Fill a title's placeholders.  `{number2}`/`{ordinal2}` are a run's second
    count (`first2`/`count2`): the Proper beside "Eighth Sunday after Pentecost".
    `{roman}`/`{roman2}` give the number in Roman numerals."""
    if number2 is not None:
        template = (template.replace("{ordinal2}", _ordinal(number2))
                            .replace("{roman2}", _roman(number2))
                            .replace("{number2}", str(number2)))
    return (template.replace("{ordinal}", _ordinal(number))
                    .replace("{roman}", _roman(number))
                    .replace("{number}", str(number))
                    .replace("{name}", name))


class Year:
    """A church year of one tradition, worked out from its rules."""

    def __init__(self, source: Source, year: int, calendar: str = "",
                 paschalion: str = "", latin: bool = False,
                 settings: Optional[dict] = None) -> None:
        cfg = dict(settings or {})
        cfg.update(source.settings)
        self.source = source
        self.tradition = source.tradition
        self.settings = cfg
        calendar = (calendar or cfg.get("calendar") or "gregorian").strip().lower()
        if calendar not in RECKONINGS:
            raise ValueError(f"calendar must be one of {tuple(RECKONINGS)}")
        self.paschalion_named = bool(paschalion)
        if not paschalion:
            paschalion = (cfg.get("paschalion_default") or
                          ("gregorian" if calendar == "gregorian" else "julian"))
        if paschalion not in PASCHALIONS:
            raise ValueError(f"paschalion must be one of {tuple(PASCHALIONS)}")
        self.calendar = calendar
        self.paschalion = paschalion
        self.reckoning = RECKONINGS[calendar]
        self.year = year
        self.latin = bool(latin) and _truthy(cfg.get("latin_names_available", ""))
        self.variant = source.tradition.variant

        self._contexts: dict[int, Context] = {}
        ctx = self.context(year)
        self.ctx = ctx
        self.start, self.end, self.next_start = ctx.start, ctx.end, ctx.next_start
        self.easter = ctx.easter()

        self.principal = self._principal_days()
        self.periods = self._periods("season")
        self.broad = self._periods("broad")
        self.halves = self._periods("half")
        self.feasts = self._feasts()
        if (cfg.get("precedence") or "").strip().lower() == "roman":
            self._roman_precedence()
        self.principal = [r for r in self.principal if not r.get("hidden")]

    def context(self, year: int) -> Context:
        """The rules' view of church year `year` of this tradition: this year's
        own, or a neighbor's (a reading plan counts its days through a whole
        calendar year, which two church years share)."""
        if year not in self._contexts:
            cfg, source = self.settings, self.source
            ctx = Context(self.reckoning, self.paschalion, year, self.variant, self.latin,
                          cfg, source.chosen)
            rule = cfg.get("year_start") or "sun<12-25-21"
            ctx.start = ctx.eval(rule)
            ahead = Context(self.reckoning, self.paschalion, year + 1, self.variant,
                            self.latin, cfg)
            ctx.next_start = ahead.eval(rule)
            ctx.end = ctx.next_start - 1
            for row in source.days:
                if row.get("id") and row.get("date"):
                    ctx.ids[row["id"]] = row["date"]
            for row in source.feasts:
                if row.get("id") and row.get("date") and row["id"] not in ctx.ids \
                        and not re.fullmatch(r"\d\d-\d\d", row["date"]):
                    ctx.ids[row["id"]] = row["date"]
            self._contexts[year] = ctx
        return self._contexts[year]

    # -- labels ---------------------------------------------------------------

    def iso(self, day: int) -> str:
        return self.reckoning.isoformat(day)

    @property
    def label(self) -> str:
        return year_label(self.year)

    # -- the principal days ---------------------------------------------------

    def _principal_days(self) -> list[dict]:
        ctx = self.ctx
        singles: list[tuple[dict, int]] = []
        for row in self.source.days:
            if row.get("date"):
                day = ctx.eval(row["date"])
                if ctx.holds(row.get("when", ""), day):
                    singles.append((row, day))
        claimed = {day for row, day in singles if _truthy(row.get("claims", ""))}

        out: list[dict] = []
        single_at = {id(row): day for row, day in singles}
        for row in self.source.days:
            if row.get("date"):
                if id(row) not in single_at:
                    continue
                day = single_at[id(row)]
                if self.start <= day <= self.end:
                    # A single day's `first` may be a date too: the number of
                    # the Sunday it takes over, counted in weeks from it.
                    first, since = _first(ctx, row.get("first"), 1)
                    number = (day - since) // 7 if since is not None else first
                    out.append(self._entry(row, day, 0, number, _int(row.get("first2"))))
                continue
            if not row.get("from"):
                continue
            if not ctx.holds(row.get("when", ""), None):
                continue
            first_day = ctx.eval(row["from"])
            last_day = ctx.eval(row["to"]) if row.get("to") else self.end
            every = (row.get("every") or "sun").strip().lower()
            if every in ("sunday", "sundays"):
                every = "sun"
            days = []
            if every == "day":
                days = list(range(first_day, last_day + 1))
            else:
                wanted = {WEEKDAYS[w] for w in every.replace(",", " ").split()}
                days = [d for d in range(first_day, last_day + 1) if weekday(d) in wanted]
            first, since = _first(ctx, row.get("first"), 1)
            first2, since2 = _first(ctx, row.get("first2"), None)
            for index, day in enumerate(days):
                if day in claimed or not (self.start <= day <= self.end):
                    continue
                number = ((day - since) // 7 if since is not None
                          else _count(row.get("count"), first, index, len(days)))
                number2 = ((day - since2) // 7 if since2 is not None
                           else None if first2 is None
                           else _count(row.get("count2"), first2, index, len(days)))
                out.append(self._entry(row, day, index, number, number2))
        out.sort(key=lambda r: r["day"])
        return out

    def _entry(self, row: dict, day: int, index: int, number: int,
               number2: Optional[int] = None) -> dict:
        name = _pick(row.get("names", ""), index)
        title = _title(row.get("title", ""), number, name, number2)
        note = _title(_pick(row.get("notes", ""), index), number, name, number2)
        if title and note:
            title = f"{title}\n({note})"
        latin = _pick(row.get("latin", ""), index)
        if title and self.latin and latin:
            title = f"{title}\n({latin})"
        full = row.get("full_name", "")
        full = _title(_pick(full, index), number, name, number2) if full else ""
        return {
            "day": day, "title": title,
            "color": _pick(row.get("color", ""), index).upper(),
            "bottom": _pick(row.get("color_bottom", ""), index).upper(),
            "style": _pick(row.get("style", ""), index),
            "icon": (_pick(row.get("icon", ""), index)
                     if not row.get("icon_when") or self.ctx.holds(row["icon_when"], day)
                     else ""),
            "full_name": full,
            "rank": _int(_pick(row.get("rank", ""), index)),
            "yield": _int(row.get("yield", "")),
            "id": row.get("id", ""), "number": number,
            # A day of its own (a `date` row), not one of a run's (`from`/`to`).
            "single": bool(row.get("date")),
        }

    # -- seasons, halves and cycles --------------------------------------------

    def _periods(self, kind: str) -> list[dict]:
        ctx = self.ctx
        out = []
        for row in self.source.periods:
            if (row.get("kind") or "season").strip().lower() != kind:
                continue
            if not ctx.holds(row.get("when", ""), None):
                continue
            a, b = ctx.eval(row["start"]), ctx.eval(row["end"])
            out.append({
                "name": row.get("name", ""), "start": a, "end": b,
                "season": (row.get("season") or "").upper(),
                "color": (row.get("color") or "").upper(),
                "subtitle": row.get("subtitle", ""), "scale": row.get("scale", ""),
                "rank_weekday": _int(row.get("rank_weekday", "")),
                "rank_sunday": _int(row.get("rank_sunday", "")),
            })
        return out

    # -- the feasts -----------------------------------------------------------

    def _feasts(self) -> list[dict]:
        ctx = self.ctx
        mode = str(self.settings.get("feast_repeat", "all") or "all").strip().lower()
        out = []
        for order, row in enumerate(self.source.feasts):
            text, raw = row.get("name", ""), row.get("date", "")
            if not text or not raw:
                continue
            days: list[int] = []
            m = re.fullmatch(r"(\d\d)-(\d\d)", raw)
            full = re.fullmatch(r"[+-]?\d{4,}-\d\d-\d\d", raw)
            if m:
                month, dom = int(m.group(1)), int(m.group(2))
                if not self.reckoning.valid(2000, month, dom):
                    print(f"  ! feasts: no such day as {raw!r} ({text}); row skipped",
                          file=sys.stderr)
                    continue
                y0, y1 = ctx.year_of(self.start), ctx.year_of(self.end)
                for y in range(y0, y1 + 1):
                    if not self.reckoning.valid(y, month, dom):
                        continue
                    z = self.reckoning.to_day(y, month, dom)
                    if self.start <= z <= self.end:
                        days.append(z)
            elif full:
                z = self.reckoning.parse(raw)
                if self.start <= z <= self.end:
                    days.append(z)
            else:
                try:
                    z = ctx.eval(raw)
                except ValueError as exc:
                    print(f"  ! feasts: {exc} ({text}); row skipped", file=sys.stderr)
                    continue
                if self.start <= z <= self.end:
                    days.append(z)
            if len(days) > 1 and mode in ("first", "last"):
                days = days[:1] if mode == "first" else days[-1:]
            for z in days:
                if not ctx.holds(row.get("when", ""), z):
                    continue
                icon = row.get("icon", "")
                if icon and row.get("icon_when") and not ctx.holds(row["icon_when"], z):
                    icon = ""
                out.append({
                    "day": z, "name": text, "full_name": row.get("full_name", ""),
                    "color": (row.get("color_override") or "").upper(),
                    "bottom": (row.get("color_override_bottom") or "").upper(),
                    "rank": _int(row.get("rank", "")),
                    "level": self._level(row),
                    "style": row.get("style", ""), "icon": icon,
                    "transfer": row.get("transfer", ""),
                    "font_size_override": row.get("font_size_override", ""),
                    "max_chars_override": row.get("max_chars_override", ""),
                    "vertical_offset": row.get("vertical_offset", ""),
                    "id": row.get("id", ""), "order": order,
                    "link": row.get("link", ""),
                })
        out.sort(key=lambda r: r["day"])
        return out

    def _level(self, row: dict) -> str:
        """principal, festival or all -- which Feasts setting still shows it."""
        given = (row.get("level") or "").strip().lower()
        if given in ("principal", "festival", "all"):
            return given
        rank = _int(row.get("rank", ""))
        top = _int(str(self.settings.get("principal_max_rank", "")), None)
        mid = _int(str(self.settings.get("festival_max_rank", "")), None)
        if rank is not None and top is not None and mid is not None:
            return "principal" if rank <= top else "festival" if rank <= mid else "all"
        if row.get("color_override"):
            return "principal"
        if row.get("color_override_bottom"):
            return "festival"
        return "all"

    # -- precedence, as the Roman Rite keeps it ----------------------------------

    def _temporal_rank(self, day: int) -> int:
        ranks = [r["rank"] for r in self.principal
                 if r["day"] == day and r["rank"] is not None and r["title"]]
        if ranks:
            return min(ranks)
        for p in self.periods:
            if p["season"] and p["start"] <= day <= p["end"]:
                wanted = p["rank_sunday"] if weekday(day) == 6 else p["rank_weekday"]
                if wanted is not None:
                    return wanted
        return 13

    def _roman_precedence(self) -> None:
        """Settle which celebrations are kept when two fall on one day.

        Follows the General Norms for the Liturgical Year and the Calendar and
        its Table of Liturgical Days, by rank (1 highest, 13 lowest):

          * the higher rank is celebrated;
          * a solemnity that is impeded moves to the nearest following day
            that is not ranked 1 to 8 (or wherever its own `transfer` says);
          * an obligatory memorial on a privileged weekday (rank 9: Lent,
            17-24 December, the Christmas octave) becomes a commemoration;
          * anything else impeded is omitted that year.
        """
        temporal = {}
        for day in range(self.start, self.end + 1):
            temporal[day] = self._temporal_rank(day)
        placed: dict[int, list[dict]] = {}
        kept: list[dict] = []
        pending = sorted(self.feasts, key=lambda f: (f["rank"] if f["rank"] is not None
                                                      else 12, f["day"], f["order"]))

        def best_placed(day: int) -> int:
            return min((f["rank"] for f in placed.get(day, [])), default=99)

        # A day a feast ranked 1 to 8 keeps on its own date is not free for a
        # moved one, even before that feast is placed (Common Worship 2022:
        # George, moved from Easter Week, goes to Tuesday 26 April, not onto
        # Mark on the Monday).
        owned = {f["day"] for f in self.feasts
                 if (f["rank"] if f["rank"] is not None else 12) <= 8
                 and (f["rank"] if f["rank"] is not None else 12) < temporal.get(f["day"], 13)}

        def free(day: int) -> bool:
            return temporal.get(day, 99) > 8 and best_placed(day) > 8 and day not in owned

        def place(feast: dict, day: int) -> None:
            feast["day"] = day
            placed.setdefault(day, []).append(feast)
            kept.append(feast)
            if (feast["rank"] or 99) < temporal.get(day, 99) and (feast["rank"] or 99) <= 8:
                for row in self.principal:
                    if (row["day"] == day and row["rank"] is not None
                            and row["rank"] > feast["rank"]
                            and _truthy(self.settings.get("hide_outranked_titles", ""))):
                        row["hidden"] = True

        for feast in pending:
            rank = feast["rank"] if feast["rank"] is not None else 12
            feast["rank"] = rank
            day = feast["day"]
            t = temporal.get(day, 13)
            p = best_placed(day)
            if p < rank:
                # Something higher is already kept here.
                if rank >= 10 and p >= 10 and (rank <= 11 or p >= 12):
                    place(feast, day)                 # memorials side by side
                elif rank <= 4:
                    self._transfer(feast, free, place)
                continue
            if rank < t:
                place(feast, day)
            elif rank <= 4:
                self._transfer(feast, free, place)
            elif rank >= 10 and t == 9:
                # An obligatory memorial on a privileged weekday: a commemoration.
                feast["rank"] = 12
                feast["level"] = "all"
                demoted = self.settings.get("commemoration_style", "")
                if demoted:
                    feast["style"] = demoted
                place(feast, day)
            # otherwise it is not kept this year
        kept.sort(key=lambda f: (f["day"], f["order"]))
        self.feasts = kept
        # Marks such as a Friday's abstinence give way to a solemnity.
        solemn = {d for d, fs in placed.items() if any(f["rank"] <= 4 for f in fs)}
        self.principal = [r for r in self.principal
                          if not (r.get("yield") is not None and r["day"] in solemn
                                  and any(f["rank"] <= r["yield"] for f in placed[r["day"]]))]

    def _transfer(self, feast: dict, free: Callable[[int], bool],
                  place: Callable[[dict, int], None]) -> None:
        day = feast["day"]
        target = None
        for clause in (feast.get("transfer") or "next").split(";"):
            clause = clause.strip()
            if not clause:
                continue
            if "=>" in clause:
                span, to = clause.split("=>", 1)
                a, b = (span.split("..", 1) + [""])[:2]
                lo = self.ctx.eval(a)
                hi = self.ctx.eval(b) if b else lo
                if lo <= day <= hi:
                    target = self.ctx.eval(to)
                    break
                continue
            if clause in ("next", "prev"):
                step = 1 if clause == "next" else -1
                d = day + step
                while self.start <= d <= self.end and not free(d):
                    d += step
                target = d
                break
            if clause == "none":
                return
        if target is None or not (self.start <= target <= self.end):
            return
        if target != day:
            feast["transferred_from"] = day
            # The obligation of a holy day stays with its date.
            feast["icon"] = " ".join(k for k in feast["icon"].split() if k != "obligation")
        place(feast, target)

    # -- the rows the drawing reads ----------------------------------------------

    def sundays_rows(self) -> list[list[str]]:
        """sundays_seasons.csv: every titled principal day, plus the marks."""
        return [[self.iso(r["day"]), r["title"], r["color"], r["bottom"], "", "", "",
                 r["style"], r["icon"], r["full_name"],
                 "" if r["rank"] is None else str(r["rank"])]
                for r in self.principal]

    def feast_rows(self) -> list[list[str]]:
        rows = []
        for f in self.feasts:
            full = f["full_name"]
            if f.get("transferred_from") is not None:
                moved = self.reckoning.from_day(f["transferred_from"])
                full = (full or f["name"]) + f" (transferred from {moved[1]:02d}-{moved[2]:02d})"
            rows.append([self.iso(f["day"]), f["name"], f["color"], f["bottom"],
                         f["font_size_override"], f["max_chars_override"],
                         f["vertical_offset"], f["style"], f["icon"], full,
                         "" if f["rank"] is None else str(f["rank"]), f["level"]])
        return rows


SUNDAYS_HEADER = ["date", "title", "color_override", "color_override_bottom",
                  "font_size_override", "max_chars_override", "vertical_offset",
                  "style", "icon", "full_name", "rank"]
FEASTS_HEADER = ["date", "name", "color_override", "color_override_bottom",
                 "font_size_override", "max_chars_override", "vertical_offset",
                 "style", "icon", "full_name", "rank", "level"]


def _truthy(value: Any) -> bool:
    return str(value).strip().upper() in ("TRUE", "1", "YES", "Y", "ON")
