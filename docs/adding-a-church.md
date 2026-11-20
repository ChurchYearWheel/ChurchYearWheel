# Adding a church

This is a step-by-step guide to adding another church's calendar to the wheel.
You need Python 3 (and Node.js for the last check). No programming is needed:
a calendar is a folder of small spreadsheet (CSV) files that describe its
year as rules, and the scripts work out every year from them.

[traditions.md](traditions.md) is the full reference; this page is the short
road through it. A complete working example is in
[docs/example-church/](example-church/): copy it and change it.

## 1. Gather the sources first

Before writing anything, find the church's own published calendar: its
prayer book or hymnal, its lectionary tables, or the calendar it publishes
each year. For each part of the year, note

- the names of the Sundays and principal days, exactly as the church writes
  them, in its own language;
- how the year begins and ends (Advent Sunday for most Western churches;
  1 September for the Orthodox);
- the liturgical colors, if the church gives them (where a source gives two
  colors for a day, this project uses the first);
- the saints' days and other dated commemorations it keeps.

Write down where each fact came from (book, edition, page or web address):
it goes in a comment in the files and in `docs/traditions.md`, so others can
check it. Calendars from two different years of a church's own publications
are a good test that the rules you write are right.

## 2. Make the folder

Copy `docs/example-church/` to `data/<YourFolder>/` (a short name without
spaces, such as `Moravian` or `ChurchOfX`). It holds five files:

| File | What it says |
|---|---|
| `tradition.csv` | settings: when the year starts, which artwork goes in the middle |
| `days.csv` | the Sundays and principal days, as date rules |
| `periods.csv` | the seasons (the colored ring and the colors of ordinary days) and the large parts of the year (the outer ring) |
| `seasons.csv` | the color of each season |
| `feasts.csv` | dated saints' days and commemorations |

Lines beginning with `#` are comments. A comment with a comma in it is put
in double quotes (`"# Sundays, feasts and fasts",,`), so that a spreadsheet
keeps it in one cell; a `"` inside it is written twice. Columns that a file does not need can
be left out; see the other folders under `data/` for every column in use.

### tradition.csv

```
setting,value
year_start,sun<12-25-21
center_art,lutherrose
```

`sun<12-25-21` is "the Sunday before Christmas, then three weeks back":
Advent Sunday. `center_art` names a picture from `data/artwork.csv`.

### days.csv

Each row is one day or one run of Sundays:

```
id,when,date,from,to,every,first,title,color,claims
christmas,,12-25,,,,,Christmas Day,WHITE,TRUE
easter,,easter,,,,,Easter Day,WHITE,TRUE
pentecost,,easter+49,,,,,Pentecost,RED,TRUE
after_pentecost,,,easter+63,end,sun,2,{ordinal} Sunday after Pentecost,,
```

- A single day has a `date`: a fixed date (`12-25`), a distance from Easter
  (`easter+49`), or another rule from the date language in traditions.md
  (`sun>01-06` is the Sunday after 6 January; `@epiphany` is another row's
  date, by its `id`).
- A run has `from`, `to` and `every` (`sun`) instead, and `first`, the number
  of its first Sunday. `{ordinal}` in the title becomes First, Second, ...;
  `{number}` and `{roman}` give 2 and II.
- `claims` = TRUE means the day takes the place of a Sunday in any run: the
  run skips it but keeps counting, so the numbers after it stay right.
- `color` colors the day's cell; leave it blank to take the season's color.
- `when` keeps a row only in some years: `date lt 12-31` (only if the date
  falls before 31 December), `date wd sun` (only when it falls on a Sunday).

### periods.csv

```
kind,name,start,end,season
season,Advent,start,12-24,ADVENT
season,Christmas,12-25,01-05,CHRISTMAS
half,CHRISTMAS,start,easter-47
half,EASTER,easter-46,easter+49
half,THE CHURCH,easter+50,end
```

`season` rows name the stretch on the season ring and give its days a color
(through `seasons.csv`). `half` rows are the large divisions on the outer
ring: two halves, or three "Times", or whatever the church uses.

### seasons.csv and feasts.csv

```
season,color
ADVENT,PURPLE
CHRISTMAS,WHITE
DEFAULT,WHITE
```

```
date,name,color_override,color_override_bottom
11-30,St. Andrew,,RED
03-25,The Annunciation,WHITE,
```

Color names come from `data/colors.csv` (WHITE, GREEN, PURPLE, BLUE, RED,
SCARLET, BLACK, ROSE, GOLD, ...); a folder can add its own in a
`colors.csv`. In `feasts.csv`, `color_override` colors the whole day (a
festival) and `color_override_bottom` the lower half of the cell (a lesser
day, which leaves the season's color above it).

## 3. Put it in the menus

Add a row to `data/traditions.csv`:

```
key,label,tradition,church,series,series_menu,folder,variant,book,book_menu
example-church,Example Church,Lutheran,Example Church,,,Example,,,
```

- `key`: the short name used in links and on the command line.
- `label`: the full name shown above the wheel.
- `tradition` and `church`: where it appears in the Tradition and Church
  menus. A new tradition name makes a new entry in the Tradition menu.
- `series` and `series_menu`: only when one church has more than one
  calendar (One-year and Three-year; two prayer books). Rows of the same
  church then share a folder and tell their rows apart with `variant` (see
  traditions.md).
- `folder`: the folder under `data/`. Another book or edition of a church
  that already has a folder goes inside it (`LCMS/TLH`, `Roman/1962`), as a
  complete folder of its own: nothing is inherited from the one around it.

Within a tradition, rows are ordered by the church's size, largest first;
the first row is the church the tradition opens on.

## 4. Look at it

```
python3 new_year.py 2026 --lectionary example-church --dry-run
python3 new_year.py 2026 --lectionary example-church --out test_2026 --draw
python3 colors.py example-church 2026
python3 feasts.py example-church 2026
```

The dry run lists the year's principal dates; the second command writes the
year's files and draws them (`test_2026/church_year_2026-27_calendar.svg`);
the last two list the year's colors and its feasts, where they fell, to
compare with the source.
Check several years, including one with an early Easter (2008, 2035) and one
with a late one (2011, 2038), and years when Christmas falls on a Sunday
(2022) and a Saturday (2027): those are where rules usually go wrong.

## 5. Carry it to the web page and check it

If the calendar's names use letters beyond ASCII that no other calendar
uses yet (another alphabet, a new accent), run `python3 tools/font_widths.py`
first, so the wheel measures them at their true width; letters it does not
know are taken as half an em, and a line of wide ones can run out of its
cell.


```
python3 web/export_data.py
python3 church_year.py
python3 web/verify.py --lectionary example-church
```

The page (`church_year.html`) now offers the church. `verify.py` draws twenty
years with both the Python and the browser renderers and checks they are
identical; it needs Node.js.

## 6. Artwork (optional)

To give the church its own picture in the middle, put an SVG in `artwork/`,
add a row to `data/artwork.csv` (with its author, license and source), add it
to `artwork/CREDITS.md`, and name its key as `center_art`. Use only pictures
whose license allows it: public domain, a Creative Commons license, or a
church's emblem used to identify its own calendar. A license that requires
credit is marked `attribution` = `required`, and the page then shows the
credit under the wheel.

## 7. Readings (optional)

The page can list each day's Bible readings under its name, and
`lectionary.py` turns them into a list for the year. They live in a sixth
file, `readings.csv`, in the church's folder; the wheel itself never shows
them, so they can be added at any time, now or long after the calendar.

### 7a. Gather the lectionary

As in step 1, find the church's own table of readings: a lectionary in its
prayer book or hymnal, a published yearly calendar, or a page the church
keeps. Note for each Sunday and feast which readings it gives (Old
Testament, Psalm, Epistle, Gospel, a sermon text ...) and, if the readings
change from year to year, how: a three-year series (Year A, B, C), some other
number of series, and which series a known year used (Advent 2025 began Year
A of the Revised Common Lectionary).

Two years of the church's own calendars are again the best test: their dates
should land on the same days your rows do.

### 7b. Write readings.csv

```
day,offset,when,cycle,variant,title,kind,reading
advent:1,,,A,,,ot,Isaiah 2:1–5
advent:1,,,A,,,psalm,Psalm 122
advent:1,,,A,,,epistle,Romans 13:11–14
advent:1,,,A,,,gospel,Matthew 24:36–44
christmas,,,,,,gospel,John 1:1–14
11-30,,,,,St. Andrew,gospel,John 1:35–42
```

- `day` is an `id` from your `days.csv`, with `:n` for the nth Sunday of a run
  (`advent:1`, `after_pentecost:12`: the number in the day's title), or a date
  rule (`11-30`, `easter-46`, `sun>=05-29`).
- `cycle` is the series the row belongs to (blank: every year); `title`
  blank means the day's own readings, a name (a saint's day, `Daily
  Lectionary`) lists them under that heading.
- `kind` names the reading: `ot`, `psalm`, `epistle`, `gospel`, `nt`, `sermon`
  ... Write book names in full and in English (`1 Corinthians 13:1–13`), with
  an en dash in ranges, "or" between alternatives, and optional verses in
  parentheses: the page turns them into links to an online Bible.
- Comment lines at the top say where the readings came from.

Then add the settings the readings need to `tradition.csv`:

```
reading_cycle,abc
bible_version,ESV
```

`reading_cycle,abc` makes Year A the year that begins in Advent 2025; another
series is written as its names and the year its first began (`I II III
2025`). `bible_version` is the version the links open in (ESV when left out);
`reading_labels` and `reading_order` rename and reorder the kinds. All of
them are in traditions.md under "readings.csv".

### 7c. A church that reads a lectionary already here

Several churches read the same lectionary: the Revised Common Lectionary,
Lutheran Service Book. Such a lectionary is written once, in
`data/readings/<name>.csv`, with its days as date rules, and each church that
reads it says so in its `tradition.csv`:

```
readings,rcl rcl-us
reading_cycle,abc
```

A church that keeps it with a few changes adds only those changes to its own
`readings.csv`: a row of kind `omit` drops the shared rows it replaces, and a
row of kind `=psalm` (or `=gospel` ...) puts another reading in a shared row's
place (traditions.md shows both). When a church's days have other names than
the shared file's, its rows can instead be made from the shared file by a
short script, as `data/LutheranWorld/readings.csv` does for the GKLI from
Lutheran Service Book.

### 7d. Adding readings to a church that is already here

The calendar needs no change: add `readings.csv` (or rows in it) to the
church's folder and the settings above to its `tradition.csv`. When several
churches share a folder as variants (`data/LutheranWorld`, `data/Nordic`,
`data/Anglican`), fill the `variant` column of each row and of each setting
with the church's variant, so the readings reach only that church.

### 7e. Check them

```
python3 web/export_data.py
python3 lectionary.py --list
python3 lectionary.py example-church 2025
python3 web/verify_readings.py
python3 web/verify_links.py --church example-church
```

`--list` shows which churches have readings; the third command lists the
year's readings for you to compare with the source (look for Sundays left
without any); `verify_readings.py` checks that the page and `lectionary.py`
agree, and `verify_links.py` that they link each citation alike. Then open the page, choose the church and look at a few days.

### 7f. Which box a set goes under

The page's Readings boxes (and `lectionary.py --readings`) sort each set by
its `title`, so choose titles that say what the set is:

| Title, or file | Box |
|---|---|
| blank, or a day of the calendar | Day |
| a saint's day or feast of `feasts.csv` | Feasts |
| an Ember, Rogation, Thanksgiving or national day | Other dated days |
| containing `Daily` (`Daily Lectionary`), or a shared file ending `-daily` | Daily |
| containing `Additional Reading` (`Daily Lectionary: Additional Reading`) | Additional |
| beginning `Psalms` (`Psalms for Daily Prayer`), a table of psalms | Psalm table |
| any row of a shared `data/readings/plan-<name>.csv` | Reading plan |
| containing Morning or Evening Prayer, Matins, Vespers, Evensong, Lessons | Office |

A Bible reading plan kept by the calendar year rather than the church year
goes in `data/readings/plan-<name>.csv`, its days keyed `plan:1`, `plan:2`
... and its `cycle` the year each cycle was first read; the churches that
use it add its name to their `readings` setting. traditions.md ("readings.csv")
gives the whole rule.

Readings from the Apocrypha are written with the book's English name
(`Sirach 44:1–15`, `Wisdom 3:1–9`, `1 Maccabees 2:15–28`, `Greek Esther`,
`Letter of Jeremiah`, `Prayer of Manasseh`), kind `apocrypha`; they open in
a version that has them (the RSV or NRSVUE). Readings from the Book of
Concord are written as the LSB draft lectionary cites them
(`Augsburg Confession XX 1–8`, `Apology 4:117–146`, `Small Catechism,
Baptism`), kind `confessions`, and open at that paragraph on
bookofconcord.org. Neither is sent to the hymn and song searches below.

## 8. The page's extras for a church (optional)

These are settings in `tradition.csv`; each is described in traditions.md
under "tradition.csv".

**Weekday names.** A weekday without a name of its own is named from the
Sunday before it. `weekday_titles` says how: blank (`after`, the Lutheran and
Anglican custom: "Tuesday after the Sixth Sunday after Pentecost"), `week`
(the Roman and Byzantine custom: "Tuesday of the Sixth Week after
Pentecost"), or `none` for a calendar whose names are not in English.

**Hymn search.** A hymnal mark after each set of readings searches
Hymnary.org for the hymns on them in the church's hymnal:

```
hymnary_hymnal,GG2013
hymnary_hymnal_name,Glory to God (2013)
```

The code is the end of the hymnal's address at Hymnary.org
(hymnary.org/hymnal/GG2013). The search only finds hymns Hymnary has
indexed by scripture, so check the hymnal first: open
`https://hymnary.org/search?qu=hymnalNumber:GG2013 in:instances&sort=scripture`
and read the count ("Showing 1 - 10 of 796"); a few hundred is good, a few
dozen finds little (it can still be named, for hymns indexed later). A church
with several hymnals names them all, newest first, codes separated by spaces
and names by `|`; the page's Settings then has a Hymnal menu, the first
opening, and Make a page and `church_year.py --hymnal` can open on
another:

```
hymnary_hymnal,AM2013 CAH2000 CPAM2000 NEH1985
hymnary_hymnal_name,Ancient and Modern (2013)|Complete Anglican Hymns Old and New (2000)|Common Praise (2000)|The New English Hymnal (1986)
```

A church that has none is left without the setting, and its sets have no
hymn mark.

A hymnal whose topics Hymnary.org indexes (hymnary.org/browse/topics/<code>)
can also give a day a hymn mark of its own, after its name: list the topics
that suit each day in the church's `hymn_topics.csv`
(`day,variant,when,hymnal,topic,subtopic,numbers`; traditions.md,
"hymn_topics.csv"), as `data/Anglican/hymn_topics.csv` does. Copy each topic
from the index's own topic list word for word (misspellings too: the list
answers only to its own words); a sub-topic goes in `subtopic`, and `{abc}`
stands for the lectionary year where the index files Sundays under Year A, B
or C. Open a few of the marks to check they list hymns.
Better still, where the hymnal's contents group its hymns by season, give a
day its section's numbers (`advent,,LSB2006,Advent,331-357`), and the other
hymns the book's topical index adds to the topic (`331-357 508-516 872`), and
the hymns' first lines in `data/hymnals/<code>.csv` (`number,first_line`;
Hymnary.org's page for the hymnal lists them, 100 to a page, and the index
prints those it adds): the mark then lists the hymns, each opening at
Hymnary.org. The contemporary song search (Word to Worship) needs no setting:
every set with Bible readings has its mark.

**Feast links.** A saint's name in the readout links to `feasts.csv`'s `link`
for it, else to `feast_link` (a URL with `{name}`), else to a Wikipedia
search.

**Latin names.** A one-year series that names its Sundays by their Introits
puts the names in `days.csv`'s `latin` column and sets
`latin_names_available,TRUE` (and `latin_names_default,TRUE` to open with
them).

**Bible version.** `bible_version` is the version readings open in (step 7b);
`verse_numbering` says which books the church cites in the Hebrew or
Vulgate numbering, so the links can translate them (docs/versification.md).

## 9. Document it

Add the church to the table at the top of `docs/traditions.md` and a
paragraph in the right section saying what the calendar contains and where it
comes from; add a line to `CHANGELOG.md`. Record its sources, and anything
missing or guessed, as rows of `docs/provenance.csv` (one row per claim:
church, aspect, status, detail, source, notes) and run
`python3 tools/provenance.py` to rewrite `docs/provenance.md`. If you are sending the change to the
project, say in your message which sources you used.
