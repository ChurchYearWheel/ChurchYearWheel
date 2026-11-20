"""
The calendar arithmetic again, in plain integers.

`church_year_image.py` and `new_year.py` reach for `datetime.date`, which stops at
1 January of AD 1 and so cannot speak for a year before that.  The browser can,
because its dates are day counts rather than a library type.  These few
functions are the same arithmetic with nothing underneath it, so they go as far
as the browser does and can be used to check it there.

This is a reference for the tests, not a second calendar: nothing in the
package draws with it.
"""

from __future__ import annotations


def days_from_civil(y: int, m: int, d: int) -> int:
    """Days from 1970-01-01 in the proleptic Gregorian calendar (Hinnant)."""
    y -= m <= 2
    # Plain floor division, not the guarded form the C++ original uses: that
    # guard exists because C++ truncates toward zero, and Python's // already
    # floors.  Transcribing it makes 400 years come to 146098 days below year 1.
    era = y // 400
    yoe = y - era * 400                                   # [0, 399]
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def civil_from_days(z: int) -> tuple[int, int, int]:
    z += 719468
    era = z // 146097
    doe = z - era * 146097                                # [0, 146096]
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    y = yoe + era * 400
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + (3 if mp < 10 else -9)
    return (y + (m <= 2), m, d)


def weekday(z: int) -> int:
    """Python's convention: Monday 0 ... Sunday 6.  1970-01-01 was a Thursday."""
    return (z + 3) % 7


def easter(year: int) -> int:
    """Gregorian Easter as a day count, for any year at all.

    Before 1583 this is the modern rule extrapolated backwards, not a record of
    anything observed.
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
    return days_from_civil(year, month, day + 1)


def advent_sunday(year: int) -> int:
    """First Sunday in Advent: the fourth Sunday before Christmas."""
    christmas = days_from_civil(year, 12, 25)
    return christmas - (weekday(christmas) + 1) - 21


def iso(z: int) -> str:
    """ISO 8601, in the expanded form outside the four-digit years."""
    y, m, d = civil_from_days(z)
    if 1 <= y <= 9999:
        year = f"{y:04d}"
    else:
        year = ("-" if y < 0 else "+") + f"{abs(y):06d}"
    return f"{year}-{m:02d}-{d:02d}"
