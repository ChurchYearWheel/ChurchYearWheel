#!/usr/bin/env python3
"""
Which calendar the dates are reckoned in, and which rule finds Easter.

These are two independent choices, and conflating them gets real practice
wrong:

  * The **reckoning** decides how a day is labeled — 1 January 2026 in the
    Julian calendar is 14 January in the Gregorian, because Julian leap years
    have no century rule and the two have drifted thirteen days apart.
  * The **paschalion** decides where Easter falls. The Julian computus is a
    different rule from the Gregorian one, which is why Orthodox Pascha is
    usually later: 5 May in 2024, 12 April in 2026, but the same day as the
    West in 2025.

Real practice mixes them. Western Christianity before 1582 was Julian in both.
Old Calendarist Orthodox churches still are. Most Orthodox churches today keep
fixed feasts on the Revised Julian calendar and Pascha on the Julian
paschalion — a combination a single setting could not express.

Underneath all of it the days themselves are one unbroken line, counted from
1 January 1970. A reckoning only says how to name a day on that line, so the
weekdays never shift: Advent Sunday is a Sunday whichever calendar is chosen.
"""

from __future__ import annotations

from typing import Iterator

# ---------------------------------------------------------------------------
# Reckonings
# ---------------------------------------------------------------------------

_MONTH_LENGTHS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


class Reckoning:
    """How a day on the line is named, and how a name finds its day."""

    name = "?"
    label = "?"

    def is_leap(self, year: int) -> bool:
        raise NotImplementedError

    def to_day(self, year: int, month: int, day: int) -> int:
        raise NotImplementedError

    def from_day(self, z: int) -> tuple[int, int, int]:
        raise NotImplementedError

    # -- shared helpers ------------------------------------------------------

    def days_in_month(self, year: int, month: int) -> int:
        if month == 2 and self.is_leap(year):
            return 29
        return _MONTH_LENGTHS[month - 1]

    def valid(self, year: int, month: int, day: int) -> bool:
        return 1 <= month <= 12 and 1 <= day <= self.days_in_month(year, month)

    def _month_day(self, year: int, day_of_year: int) -> tuple[int, int]:
        """Month and day from a 0-based day of the year."""
        for month in range(1, 13):
            length = self.days_in_month(year, month)
            if day_of_year < length:
                return month, day_of_year + 1
            day_of_year -= length
        raise ValueError("day of year out of range")

    def _from_day_by_search(self, z: int, days_per_year: float,
                            epoch_year: int, epoch_day: int) -> tuple[int, int, int]:
        """Estimate the year, then walk to it.  Two steps at the very most."""
        year = epoch_year + int((z - epoch_day) // days_per_year)
        while self.to_day(year, 1, 1) > z:
            year -= 1
        while self.to_day(year + 1, 1, 1) <= z:
            year += 1
        month, day = self._month_day(year, z - self.to_day(year, 1, 1))
        return year, month, day

    def isoformat(self, z: int) -> str:
        """ISO 8601, expanded outside the four-digit years."""
        year, month, day = self.from_day(z)
        if 1 <= year <= 9999:
            head = f"{year:04d}"
        else:
            head = ("-" if year < 0 else "+") + f"{abs(year):06d}"
        return f"{head}-{month:02d}-{day:02d}"

    def parse(self, text: str) -> int:
        """A day from an ISO date written in this reckoning."""
        text = text.strip()
        sign = 1
        if text[0] in "+-":
            sign = -1 if text[0] == "-" else 1
            text = text[1:]
        year, month, day = text.split("-")
        return self.to_day(sign * int(year), int(month), int(day))


class _Gregorian(Reckoning):
    """The civil calendar since 1582.  Leap years skip three centuries in four."""

    name = "gregorian"
    label = "Gregorian"

    def is_leap(self, year: int) -> bool:
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    # Howard Hinnant's closed form, transcribed with Python's flooring division
    # rather than the guards his C++ needs for truncation.
    def to_day(self, year: int, month: int, day: int) -> int:
        y = year - (month <= 2)
        era = y // 400
        yoe = y - era * 400
        doy = (153 * (month + (-3 if month > 2 else 9)) + 2) // 5 + day - 1
        doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
        return era * 146097 + doe - 719468

    def from_day(self, z: int) -> tuple[int, int, int]:
        z += 719468
        era = z // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        day = doy - (153 * mp + 2) // 5 + 1
        month = mp + (3 if mp < 10 else -9)
        return y + (month <= 2), month, day


class _Julian(Reckoning):
    """The calendar of the Roman world and of Christendom until 1582.

    A leap year every fourth year with no exception, which overshoots the solar
    year by about eleven minutes: enough to have drifted thirteen days by now.
    """

    name = "julian"
    label = "Julian"

    # Anchored on the changeover: Julian 4 October 1582 was followed directly by
    # Gregorian 15 October 1582, so Julian 5 October and Gregorian 15 October
    # 1582 name the same day.
    _OFFSET = -719470

    def is_leap(self, year: int) -> bool:
        return year % 4 == 0

    def to_day(self, year: int, month: int, day: int) -> int:
        y = year - (month <= 2)
        doy = (153 * (month + (-3 if month > 2 else 9)) + 2) // 5 + day - 1
        return 365 * y + y // 4 + doy + self._OFFSET

    def from_day(self, z: int) -> tuple[int, int, int]:
        return self._from_day_by_search(z, 365.25, 1970, self.to_day(1970, 1, 1))


class _RevisedJulian(Reckoning):
    """The Orthodox reform of 1923, used for fixed feasts by most of the East.

    A century is a leap year only when the year leaves 200 or 600 on division
    by 900, which tracks the solar year more closely than the Gregorian rule.
    It agrees with the Gregorian calendar from 1600 until 2800 and parts company
    on either side.
    """

    name = "revised-julian"
    label = "Revised Julian"

    _OFFSET = 0            # measured once below, against the Gregorian calendar
    _CYCLE_YEARS = 900
    # 900 years hold 225 fourth-years, less nine centuries, plus the two the
    # rule keeps: 218 leap days.
    _CYCLE_DAYS = 900 * 365 + 218

    def is_leap(self, year: int) -> bool:
        if year % 4 != 0:
            return False
        if year % 100 != 0:
            return True
        return year % 900 in (200, 600)

    def _leaps_before(self, year: int) -> int:
        """Leap days falling inside the March-shifted years [0, year).

        A shifted year runs March to February, so its leap day is the 29th of
        the *following* February: the count wanted is of leap years in [1,
        year], not of leap years below it.  The ordinary y // 4 - y // 100 form
        already means exactly that, which is easy to mistake for an off-by-one
        and then to "fix" in the wrong direction.
        """
        count = year // 4 - year // 100
        # Add back the centuries the rule keeps: those leaving 200 or 600 on
        # division by 900, counted up to and including `year`.
        for keep in (200, 600):
            if year >= keep:
                count += (year - keep) // self._CYCLE_YEARS + 1
        return count

    def to_day(self, year: int, month: int, day: int) -> int:
        y = year - (month <= 2)
        doy = (153 * (month + (-3 if month > 2 else 9)) + 2) // 5 + day - 1
        # Counted from 1 March of year 0, then shifted onto the common day line.
        return 365 * y + self._leaps_before(y) + doy + self._OFFSET

    def from_day(self, z: int) -> tuple[int, int, int]:
        return self._from_day_by_search(z, 365.2422, 1970, self.to_day(1970, 1, 1))


GREGORIAN = _Gregorian()
JULIAN = _Julian()
REVISED_JULIAN = _RevisedJulian()

# Anchored so the Revised Julian calendar lands on the Gregorian one through
# the years the reform was built to agree with.  Measured by asking the
# calendar itself where 1 January 2000 falls while its offset is still zero,
# rather than by repeating the formula here: a copy of it would go quietly
# stale the first time the original changed.
REVISED_JULIAN._OFFSET = (GREGORIAN.to_day(2000, 1, 1)
                          - REVISED_JULIAN.to_day(2000, 1, 1))

RECKONINGS = {r.name: r for r in (GREGORIAN, JULIAN, REVISED_JULIAN)}


# ---------------------------------------------------------------------------
# Paschalions
# ---------------------------------------------------------------------------

def gregorian_easter(year: int) -> int:
    """Easter by the Gregorian computus (the anonymous / Meeus-Jones-Butcher rule).

    Before 1583 this is the modern rule extrapolated backwards rather than a
    record of anything observed.
    """
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    el = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * el) // 451
    month, day = divmod(h + el - 7 * m + 114, 31)
    return GREGORIAN.to_day(year, month, day + 1)


def julian_easter(year: int) -> int:
    """Easter by the Julian computus, which the Orthodox churches keep.

    The rule names a date in the Julian calendar; the day it lands on is the
    same day whatever calendar the wheel is drawn in.
    """
    a = year % 4
    b = year % 7
    c = year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month, day = divmod(d + e + 114, 31)
    return JULIAN.to_day(year, month, day + 1)


PASCHALIONS = {"gregorian": gregorian_easter, "julian": julian_easter}


# ---------------------------------------------------------------------------
# The Alexandrian calendars
# ---------------------------------------------------------------------------
#
# The Coptic and Ethiopian churches keep their feasts by the old Egyptian
# year: twelve months of thirty days and a short thirteenth month of five,
# six in the year before a Julian leap year.  The two calendars are the same
# but for the era they count from.  They only name days for the rules here
# (coptic(04-29), ethiopian(01-17)); the wheel is still drawn in its own
# calendar, so a feast keeps the civil date its people know.

_JDN_1970 = 2440588
ALEXANDRIAN_EPOCHS = {"coptic": 1825030, "ethiopian": 1724221}


def alexandrian_to_day(calendar: str, year: int, month: int, day: int) -> int:
    epoch = ALEXANDRIAN_EPOCHS[calendar]
    return epoch + 365 * (year - 1) + year // 4 + 30 * (month - 1) + day - 1 - _JDN_1970


def alexandrian_year(calendar: str, z: int) -> int:
    return (4 * (z + _JDN_1970 - ALEXANDRIAN_EPOCHS[calendar]) + 1463) // 1461


def alexandrian_valid(year: int, month: int, day: int) -> bool:
    if day < 1:
        return False
    if 1 <= month <= 12:
        return day <= 30
    return month == 13 and day <= (6 if year % 4 == 3 else 5)


# ---------------------------------------------------------------------------
# A date that knows which calendar it is written in
# ---------------------------------------------------------------------------

class CivilDate:
    """A day on the line, named by a chosen reckoning.

    Stands in for `datetime.date` in the calendar code: the same attributes and
    the same arithmetic, but the naming follows whichever calendar was asked
    for.  The day itself is an integer, so comparing or subtracting two dates
    is exact whatever calendars they came from.
    """

    __slots__ = ("day_number", "reckoning", "_ymd")

    def __init__(self, reckoning: Reckoning, day_number: int) -> None:
        self.reckoning = reckoning
        self.day_number = day_number
        self._ymd = reckoning.from_day(day_number)

    # -- building ------------------------------------------------------------

    @classmethod
    def of(cls, reckoning: Reckoning, year: int, month: int, day: int) -> "CivilDate":
        return cls(reckoning, reckoning.to_day(year, month, day))

    @classmethod
    def parse(cls, reckoning: Reckoning, text: str) -> "CivilDate":
        return cls(reckoning, reckoning.parse(text))

    # -- reading -------------------------------------------------------------

    @property
    def year(self) -> int:
        return self._ymd[0]

    @property
    def month(self) -> int:
        return self._ymd[1]

    @property
    def day(self) -> int:
        return self._ymd[2]

    def weekday(self) -> int:
        """Monday 0 ... Sunday 6, as `datetime.date` counts.  1970-01-01 was a Thursday."""
        return (self.day_number + 3) % 7

    def isoformat(self) -> str:
        return self.reckoning.isoformat(self.day_number)

    def replace_reckoning(self, reckoning: Reckoning) -> "CivilDate":
        """The same day, named by another calendar."""
        return CivilDate(reckoning, self.day_number)

    # -- arithmetic ----------------------------------------------------------

    def plus(self, days: int) -> "CivilDate":
        return CivilDate(self.reckoning, self.day_number + days)

    def __add__(self, other):
        return self.plus(_as_days(other))

    def __sub__(self, other):
        if isinstance(other, CivilDate):
            import datetime
            return datetime.timedelta(days=self.day_number - other.day_number)
        return self.plus(-_as_days(other))

    def __eq__(self, other) -> bool:
        return isinstance(other, CivilDate) and self.day_number == other.day_number

    def __lt__(self, other) -> bool:
        return self.day_number < other.day_number

    def __le__(self, other) -> bool:
        return self.day_number <= other.day_number

    def __gt__(self, other) -> bool:
        return self.day_number > other.day_number

    def __ge__(self, other) -> bool:
        return self.day_number >= other.day_number

    def __hash__(self) -> int:
        return hash(self.day_number)

    def __str__(self) -> str:
        return self.isoformat()

    def __format__(self, spec: str) -> str:
        return format(self.isoformat(), spec)

    def __repr__(self) -> str:
        return f"CivilDate({self.reckoning.name}, {self.isoformat()})"

    def strftime(self, fmt: str) -> str:
        """Only for the weekday name in reports; the day is named by this calendar."""
        names = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                 "Saturday", "Sunday")
        return fmt.replace("%A", names[self.weekday()])


def _as_days(other) -> int:
    days = getattr(other, "days", None)
    if days is None:
        raise TypeError(f"cannot add {type(other).__name__} to a date")
    return days


def days_between(start: CivilDate, end: CivilDate) -> Iterator[CivilDate]:
    for z in range(start.day_number, end.day_number + 1):
        yield CivilDate(start.reckoning, z)
