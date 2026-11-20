# Calendars and Easter

## Which calendar

Two settings, because "Julian" is two independent choices and conflating them
gets real practice wrong:

```
calendar,julian          # gregorian | julian | revised-julian
paschalion,              # gregorian | julian  (blank follows the calendar)
```

The **calendar** decides how a day is named. Julian leap years have no century
rule, so the Julian calendar has drifted thirteen days: 1 January 2026 there is
14 January in the Gregorian, which is why Orthodox Christmas falls on 7 January.
The **paschalion** decides where Easter falls, and the Julian rule usually runs
later — 5 May in 2024, 12 April in 2026, but the same day as the West in 2025.

Leaving `paschalion` blank is the sensible default: a Julian calendar with a
Gregorian Easter is nobody's practice, so it follows the calendar.

All six pairings are reachable, and five of them are somebody's practice:

| calendar | paschalion | Christmas 2025 | Easter 2026 | who keeps it |
| --- | --- | --- | --- | --- |
| `gregorian` | `gregorian` | 25 Dec | 5 Apr | the LCMS and the West today |
| `gregorian` | `julian` | 25 Dec | 12 Apr | New Calendar practice stated in plain Gregorian terms |
| `julian` | `julian` | 7 Jan | 12 Apr | Western Christendom before 1582; Jerusalem, Russia, Serbia, Mount Athos; the Ukrainian Lutheran Church |
| `julian` | `gregorian` | 7 Jan | 5 Apr | nobody, as far as I know — available, not recommended |
| `revised-julian` | `julian` | 25 Dec | 12 Apr | Constantinople, Alexandria, Antioch, Greece, Cyprus, Romania, Poland, Bulgaria; the Ukrainian Greek-Catholic Church in Ukraine since 2023 |
| `revised-julian` | `gregorian` | 25 Dec | 5 Apr | the Orthodox Church of Finland |

The dates in that table are what the wheel actually draws, in Gregorian terms,
so a row can be checked against a published calendar directly. `revised-julian`
and `gregorian` name the same days from 1600 to 2800, so the two pairs that
share a paschalion are indistinguishable over any year you are likely to want;
they part company in 2800.

Underneath, the days are one unbroken line counted from 1 January 1970, and a
calendar only says how to name a day on it. **The weekdays never shift**, so
Advent Sunday is a Sunday and Ash Wednesday a Wednesday whichever calendar is
chosen — a useful thing to check if you ever doubt the arithmetic.

`new_year.py` takes the same two as flags, and writes them into the year's
`config.csv` so the drawing follows:

```
python new_year.py 2025 --calendar julian --out years/julian-2025
python new_year.py 2025 --calendar revised-julian --paschalion julian
```

The interactive page has a picker for each axis rather than one for the pairs,
which is what lets all six be reached: **Gregorian / Julian (Old Calendar) /
Revised Julian (New Calendar)** beside **Easter: with the calendar / Western /
Eastern**. Left on "with the calendar" the second picker does what a blank
`paschalion` does in `config.csv`, and both pickers open on whatever that file
asked for.

### Two honest caveats

Changing the reckoning makes the **dates** right for Julian use. The **content**
is still LSB's. For pre-1582 Western history that hangs together reasonably,
since the one-year series is roughly the historic Western lectionary. For
Orthodox use it does not: the Orthodox church year has a different shape
altogether — its own fasts, its own feasts, Sundays named by their Gospel — and
no choice of reckoning turns this wheel into one.

Coptic, Ethiopian and Hebrew calendars are deliberately absent for the same
reason. They are not alternative labelings of this church year; they belong to
different church years, and bolting this lectionary onto them would produce
something nobody uses.

### Revised Julian, in particular

A century is a leap year only when it leaves 200 or 600 on division by 900. That
makes it agree with the Gregorian calendar for exactly the 1200 years from March
1600 to February 2800, and part company by a day on either side.

That is verified rather than assumed, and `verify.py` now checks it on every
run, along with the other properties the calendars must have:

```
Gregorian against datetime: 117808 samples, 0 mismatches
Gregorian round-trip over 4400 years: 0 failures
Julian round-trip over 4400 years: 0 failures
Revised Julian round-trip over 4400 years: 0 failures
Revised Julian matches Gregorian 1600-03-01 to 2800-02-28: 438290 days, 0 disagreements
gregorian Easter is always a Sunday, 1583-2499: yes
julian Easter is always a Sunday, 1583-2499: yes
Western and Orthodox Pascha 2024-2027 as published: 4 of 4 agree
```

Each of those has been wrong at some point while this was written, which is why
they are checked rather than trusted. The leap count in particular is a trap:
the ordinary `y // 4 - y // 100` form already counts the leap days falling
inside the March-shifted years below `y`, not the leap years below `y`. Reading
it as an off-by-one and "correcting" it puts 2000 and 2400 a day out — far
enough from the present to go unnoticed.

## How far the page goes

Advent **10000 BC** to Advent **9998** — written in the Advent box as `-9999`
to `9998`, using astronomical year numbering where year 0 is 1 BC.

At the top, 9998 is the last church year whose final day still falls in a
four-digit year, which is as far as an ISO date, an HTML date box and Python's
`date` type will go. The computus itself would carry on indefinitely.

At the bottom there is no such wall, only meaning. The Gregorian calendar began
in October 1582, when Thursday the 4th was followed by Friday the 15th, and
**1582 is the first church year lying wholly inside it** — Advent 1581 would
have to cover those ten missing days. Easter 1583, the first computed by the
new rules, falls on 10 April, and the wheel puts it there.

Below 1582 the wheel is running the modern rules backwards over a calendar
nobody was keeping. That is a curiosity rather than a record, and **the page
says so**: a line under the wheel reads *"Before the Gregorian calendar — these
are the modern rules run backwards, not a record of what was kept."*

Two practical notes for the years before AD 1:

- Dates are shown with the era — *Sunday, November 30, 3001 BC* — and the
  heading reads *Church Year 3001–3000 BC*.
- A native date box cannot hold a year outside AD 1 to 9999; there is no value
  it would accept. So outside that it switches itself off rather than show a
  date that is not the one on the wheel. The Advent box, the arrow keys and
  clicking a cell all still work, and stepping across 1 January of AD 1 carries
  on without a stumble.

## Checking the years Python cannot reach

`verify.py` compares two drawings of the same year, which is the strongest check
available — but it leans on `church_year_image.py`, and that leans on `datetime.date`,
which stops at 1 January of AD 1. Below that there is no second drawing to
compare against, so `verify_bc.py` replaces it with two weaker checks that
together cover the same ground:

```
python web/verify_bc.py                      # 4000 BC to AD 1
python web/verify_bc.py --from -9999 --to 1
python web/verify_bc.py --dates-only
```

**The dates** are checked against `web/proleptic.py` — the same calendar and
computus written in plain integers, with no date library underneath, so it goes
wherever the browser goes. It is not taken on faith either: before it is used it
is checked against `datetime` over every week of AD 1 to 9999 (521,722 samples),
and against the invariant that 400 Gregorian years are exactly 146,097 days at
every point of the calendar, BC and AD alike.

**The drawing** is checked against itself in another year. 400 Gregorian years
are exactly 146,097 days — 20,871 whole weeks — so a BC year and an AD year 400
apart share every weekday and every month length. Where their Easters coincide
as well, the two church years are the same shape from end to end. One of the
pair is inside Python's reach, so the BC drawing can be compared against a
Python drawing of its twin:

```
✓ Advent -3000 (3001 BC) vs its twin Advent 3400, 364 days: identical (252 KB)
✓ Advent -2999 (3000 BC) vs its twin Advent 1001, 364 days: identical (251 KB)
✓ Advent -2998 (2999 BC) vs its twin Advent 2202, 364 days: identical (251 KB)
✓ Advent -2997 (2998 BC) vs its twin Advent 2203, 371 days: identical (257 KB)
```

Exactly one element legitimately differs — the label on the year's first day,
which prints the year itself — and it is blanked on both sides. Everything else
matches character for character, the long 371-day years included.

Current state: 4,002 church years from 4001 BC to AD 1 agree with the reference
exactly, and four twin drawings match. Above AD 1, `verify.py` still does the
full byte-for-byte job.
