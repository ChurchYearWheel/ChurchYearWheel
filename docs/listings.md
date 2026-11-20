# Listing a year: colors, feasts and readings

Three scripts list a church year as a table, a page to print or a calendar
feed, without the drawing:

| script | lists |
| --- | --- |
| `colors.py` | each Sunday and principal day (or every day), its name and its liturgical color; or, with `--overview`, each year's movable dates |
| `feasts.py` | the feasts: festivals, saints' days and commemorations, on the days the year keeps them; with `--major-days`, also Christmas, Easter, Pentecost and the year's other major days |
| `lectionary.py` | the Bible readings of each day |

They take the same arguments for the same things and write the same five
formats the same way, so what is said here of one holds for all three.

```
python colors.py elca 2025                       # 2025-26, as CSV on the screen
python feasts.py roman 2026 -o feasts.html       # a page to print
python lectionary.py episcopal 2025 -o readings.md --links
python colors.py lcms-one-year 2025 -o lsb.ics   # a calendar feed to import
python feasts.py --list                          # the churches
```

## What they share

**The church and the year.** The church is a key from `data/traditions.csv`
(`--list` shows them) and the year is the one the church year begins in:
`2025` is Advent 2025 to the eve of Advent 2026. Both may be left out, and are
then `config.csv`'s `lectionary` and year; a lone number is the year
(`feasts.py 2026`).

**`--from` and `--to`** take a church year or a date, at either end:

```
python lectionary.py elca --from 2025 --to 2027           # three church years
python feasts.py elca 2025 --from 2026-03-01 --to 2026-04-30   # part of one
python colors.py roman --from 2026-12-01 --to 2027-01-31  # across two
```

A date is placed in the church year that holds it. A span of years gives
one listing with a `church_year` column in front (the JSON leaves it to the
date; colors.py's lists the years, each with its start and end).

**`-f`/`--format`**: `csv`, `html`, `ics`, `json` or `md`. Without it the
format follows `-o`'s extension, else CSV.

**`-o`/`--output`**: the file to write. A folder (one that exists, or a name
ending in `/`) takes the default name: `elca_2025-26_readings.md`, or
`church_year_2026-27_colors.csv` when no church was named. Without `-o` the
listing goes to the screen.

**The year's options**, as `new_year.py` takes them: `--subcalendar KEY`
lays a national or religious-order calendar over the church's own (repeatable;
`none` for none), `--calendar` and `--paschalion` keep the year in another
calendar or with another Easter, and `--latin-names`/`--no-latin-names` add
or leave out the one-year series' Latin names (colors.py and lectionary.py;
the default is the church's own, as on the page).

**`--feasts`** says how many feasts, as it does for the drawing: `all`;
`festivals`, those that color their day or its lower half; `principal`, those
whose color replaces the season's (colors.py also takes `none`, and feasts.py
with `--major-days`). The default is `config.csv`'s `feast_detail`.

**`--data`** names the folder of rules, `./data` unless given:
`traditions.csv`, `config.csv` and the churches' folders. colors.py with no
church and no year lists it as a year folder instead (below).

**`--colors`**: `primary`, the one color of the day, or `all`, which adds
the others the church allows and, in colors.py, the lower half's color (see
below).

**The dates are Gregorian**, as a diary or calendar app names them. A year
kept in another calendar adds an `own_date` column (a field in the JSON) with
the date as that calendar names it, which is what the wheel shows: Christmas
on a Julian wheel is listed on 7 January, with `own_date` 12-25.

### The formats

- **csv**: one row per day (per reading in lectionary.py, per feast in
  feasts.py), for a spreadsheet.
- **json**: the same, with lists kept as lists, under a `title` and the
  church's key; each year and each day on a line of its own. colors.py's
  gives the settings all its years share (`calendar`, `paschalion`,
  `subcalendars`, `latin_names`, `feast_detail`) once at the top.
- **md**: a Markdown page, and **html** a self-contained page to print: a
  title, a note on what is listed, a table (day by day in lectionary.py),
  and a footer naming the script. colors.py's and feasts.py's pages show a
  swatch of each color.
- **ics**: an iCalendar file of all-day events, one per day, marked *free*
  rather than busy, that Google Calendar, Apple Calendar and Outlook all
  import; see [the calendar feed](#a-calendar-feed-to-import).

## colors.py: the colors of the year

```
python colors.py                                # ./data's year, as CSV
python colors.py -o .                           # ./church_year_2026-27_colors.csv
python colors.py episcopal 2025 --colors all -o colors.html
python colors.py roman 2025 --days all --subcalendar united_states
python colors.py lcms-one-year --from 2025 --to 2035 -o lsb.ics
```

```
date,weekday,title,color
2025-11-30,Sunday,First Sunday in Advent,BLUE
2025-12-24,Wednesday,Christmas Eve,BLUE
2025-12-25,Thursday,Nativity of Our Lord,WHITE
2026-02-18,Wednesday,Ash Wednesday,BLACK
```

The color comes from the same code that paints the wheel, so the table and
the drawing cannot drift apart. It is the top of the day's cell: the color of
the day itself, for choosing paraments and vestments.

`--colors all` adds what the wheel's readout says beside it: the other colors
the church allows, written as the data writes them (`BLUE; violet`), and,
where the wheel splits a cell (Christmas Eve, an apostle's day on a Sunday),
the lower half's color in a `lower_color` column. The JSON keeps them apart:
`color`, `alternatives`, `lower_color`, `lower_alternatives`.

```
date,weekday,title,color,lower_color
2025-11-30,Sunday,First Sunday of Advent,PURPLE; royal blue,RED
2025-12-24,Wednesday,Christmas Eve,PURPLE; royal blue,WHITE
```

`--days` picks the days:

| `--days` | lists |
| --- | --- |
| `sundays` | the Sundays |
| `principal` | the Sundays and the weekdays with a name of their own: Christmas Eve and Day, the Epiphany, Ash Wednesday, Maundy Thursday, Good Friday, Holy Saturday, the Ascension, Thanksgiving; and, in the Roman calendar, the solemnities (the default) |
| `named` | also every day with a festival or commemoration, as many as `--feasts` allows |
| `all` | every day of the year |

With no church and no year, colors.py lists the year folder `--data` names
(`./data`) as it stands, hand edits included, exactly as `church_year_image.py`
draws it; `-o .` then writes `church_year_2026-27_colors.csv` beside the
drawing (not kept in the package; make it when you want it). Named, or given a year, it **generates** each year from the
rules, so none of them has to have been built first, and `--data` is where
the rules are. A hundred years takes a few seconds: the traditions are copied into one
scratch folder once, and each year writes only its own files.

### The overview

`--overview` answers the other question a span asks: not "what falls on this
day" but "when is Easter over the next decade". It writes one row per year
instead of the days (CSV, HTML, JSON or Markdown):

```
python colors.py --from 2025 --to 2035 --overview
python colors.py roman --from 2025 --to 2100 --overview -o easter.csv
```

```
church_year  advent_1    ash_wednesday  easter      pentecost   last_sunday  days
2025-26      2025-11-30  2026-02-18     2026-04-05  2026-05-24  2026-11-22   364
2026-27      2026-11-29  2027-02-10     2027-03-28  2027-05-16  2027-11-21   364
2027-28      2027-11-28  2028-03-01     2028-04-16  2028-06-04  2028-11-26   371
```

Twenty-six columns in all: the lectionary, calendar and paschalion that built
the year; Advent 1, Christmas, the Epiphany, the Transfiguration, Septuagesima
(one-year only), Ash Wednesday, Palm Sunday, Good Friday, Easter, the
Ascension, Pentecost, Trinity, the observed Reformation and All Saints,
Thanksgiving, the Last Sunday and the year's end; the count of Sundays after
the Epiphany and after Pentecost or Trinity; and the length in days and weeks.
A date the tradition does not keep is left blank, so a file is readable with
one fixed header either way. `new_year.py`'s own summary prints from that
same function, so the screen and the file cannot come to disagree about what
a year holds. The page's Download window makes the same file (*The year at a
glance*), and `web/verify_lists.py` checks it against this one.

## feasts.py: the feast days

```
python feasts.py roman 2025
python feasts.py lcms-three-year 2025 --feasts festivals -o feasts.md
python feasts.py episcopal 2025 --links -o feasts.html
python feasts.py roman 2026 --subcalendar united_states -o roman.ics
```

```
date,weekday,name,full_name,level,color,transferred_from
2027-03-19,Friday,St. Joseph,"Saint Joseph, Spouse of the Blessed Virgin Mary",principal,WHITE,
2027-04-05,Monday,Annunciation of the Lord,The Annunciation of the Lord,principal,WHITE,2027-03-25
```

The feasts are the church's `feasts.csv` (and any `--subcalendar`'s), placed
in the year exactly as the wheel and the page place them: moved where the
tradition's rules transfer them (`transferred_from` gives the date they left),
left out where they give way, and without a commemoration that only repeats
the day's own name. The Sundays and the major days of the seasons are
`days.csv`'s, and colors.py lists them.

Each feast's **level** is `principal` (its color replaces the season's),
`festival` (it colors the lower half of its day) or `commemoration`; its
**color** is its own, blank where it takes the day's.

`--major-days` adds those major days to the feasts: each principal day the
church's `days.csv` sets on a date of its own (a `date` row with a title), such
as Christmas, the Epiphany, Ash Wednesday, Good Friday, Easter, the Ascension,
Pentecost, Trinity, a Reformation or All Saints' Sunday or Christ the King;
not the numbered Sundays of a season, which are runs (`from`/`to`), nor the
Sundays of a named sequence some churches date one by one (Sexagesima,
Estomihi, Exaudi, the Sunday next before Lent, the Sundays of the Triodion and
others; feasts.py's ORDINARY_SUNDAYS lists them, and a tradition can add ids in
its `major_days_exclude` setting). Their
**level** is `major day`; each comes before the feasts kept on its day, and
its **color** is the top of its cell, blank where it keeps the season's.
`--feasts` does not thin them, and `--feasts none` lists them alone. It is off
unless asked for, so a listing or feed made before stays the same.

```
python feasts.py lcms-three-year 2025 --major-days -o year.ics
python feasts.py roman 2025 --major-days --feasts none
```

```
date,weekday,name,full_name,level,color,transferred_from
2025-12-24,Wednesday,Christmas Eve,Christmas Eve,major day,,
2025-12-25,Thursday,Nativity of Our Lord,Nativity of Our Lord,major day,,
2025-12-26,Friday,St. Stephen,"St. Stephen, Martyr",festival,RED,
```

`--links` adds where to read about each feast, as the page's readout links
its name: the row's own `link`, else the tradition's `feast_link` pattern,
else a Wikipedia search. CSV and JSON get a `url`; Markdown and HTML make the
name a link; the calendar feed puts it in the description.

## lectionary.py: the readings

```
python lectionary.py --list                          # the churches, and which have readings
python lectionary.py lcms-three-year 2026            # 2026-27 as CSV, on the screen
python lectionary.py episcopal 2025 -o readings.md --links
python lectionary.py lcms-elhb-one-year 2027 -o elhb.ics --no-daily
python lectionary.py elca 2025 --from 2026-03-01 --to 2026-04-30
python lectionary.py lcms-three-year 2025 --feasts principal --readings -daily
```

The CSV has one row per reading: the date, the day's names, the set (a
day's own propers, or a feast's, or the daily lessons), the kind of reading
and the citation.

`--readings` chooses the kinds of set, as the web page's Readings boxes do:
`day` (the day's own propers), `feasts` (a saint's day or festival), `dated`
(another day kept by its date or a date rule that the calendar does not name:
Ember and Rogation Days, Thanksgiving, New Year's and national days, the
Byzantine Saturdays before and after a feast), `daily` (a daily or weekday
lectionary), `additional` (a daily lectionary's additional readings: LSB's
italic ones), `psalms` (a table of psalms for daily prayer: LSB's), `plan` (a Bible reading plan kept by the calendar year: Reading
the Word of God) and `office` (Morning and Evening Prayer,
Matins, a second or third service, Morning and Evening Lessons); name the
ones to keep (`--readings day,feasts`) or the ones to leave out (`--readings
-daily,-office`). `--no-daily` is `--readings -daily,-additional,-psalms,-plan,-office`.

A church whose sets hold parts of the service besides readings
(`reading_propers`: the LCMS's and LCC's Introit, Gradual and Verse) has them
listed apart, under *Propers*, after each set's readings, and with `--links` a
set's heading opens only its readings. `--no-propers` leaves them out: a
lector's list, which `--format html --links` makes printable, each heading
opening that day's readings at Bible Gateway.

`--feasts` (all, festivals, principal, none; default: config.csv's
`feast_detail`) works as the page's Feasts menu: a feast it leaves off has
its readings left off too, and so does one outranked, moved to another day,
or of a calendar not laid over the church's own (`--subcalendar`). A set
belongs to a feast when it is keyed to the feast's id, or to its date under
its name ("St. Andrew, Apostle" on `11-30`); sets keyed to a date that are
not a feast's (Ember days, weekdays, Christmas Day's propers) stay.

`--links` links each citation as the page does: at Bible Gateway
(`--links`, or `--links biblegateway`) or Bible.com (`--links youversion`,
which opens in the YouVersion app where it is installed; a version Bible.com
does not carry opens at Bible Gateway). Each alternative in "A or B" is a link
of its own. In HTML each set's heading, and in JSON each set's `url`, opens
the whole set together at Bible Gateway, as the page's set names do. `--bible` names the version (ESV, KJV, NRSVUE ...; `-h` lists
them); the default is the church's own `bible_version`, else ESV, as on the web
page, and like the page it keeps within config.csv's `page_bibles`: with
`page_bibles,english` a German church's links open in ESV, as its page does,
not in the Luther Bible, and a `--bible` the page would not offer is refused.
A church that cites the Hebrew verse numbering (`verse_numbering`) has its
citations translated for an English-numbered version, as the page does
(docs/versification.md). CSV gets a
`url` column (several, separated by spaces, for "A or B"), JSON a `urls`
list, Markdown and HTML a link on each citation, and the calendar feed the
addresses in each event's description.

The links are off unless asked for. A file outlives the screen it was made
on: a printed page has no use for them, the CSV and JSON stay as they were,
and the page's own choice between the two sites follows the device it is
opened on, which a file cannot know.

The readings come from the tradition's own `readings.csv` and the shared
lectionaries in `data/readings/` its `readings` setting names; how those files
are written is in [traditions.md](traditions.md). `web/verify_readings.py`
checks that the page gives every church the same readings, and
`web/verify_links.py` that `lib/links.py` makes the same links as the page,
for every reading and feast in the data.

The page's **Download…** window makes these same three lists, in the same five
formats, in the browser (`web/listings.js`), with the page's settings: the
Readings boxes, Feasts, Latin names, Bible and Open in. `web/verify_lists.py`
checks that its files are the scripts' files, byte for byte, across a spread
of churches, years and options.

## A calendar feed to import

`-f ics` (or `-o something.ics`) writes an iCalendar file, which Google
Calendar, Apple Calendar and Outlook all import, so the year appears beside
everything else in your diary:

```
python colors.py -f ics -o church.ics                     # this year's Sundays and festivals
python colors.py --from 2025 --to 2030 -o church.ics      # several years in one feed
python feasts.py roman 2025 --feasts festivals -o feasts.ics
python lectionary.py elca 2025 --links -o readings.ics
```

Each listed day becomes one all-day event marked *free* rather than busy.
The calendar is named after the listing, such as *LCMS Three-year (LSB):
colors for 2025-26*.

- **colors.py**: the event's title is the day's name or names; its
  description and category are the liturgical color, and clients that
  understand the RFC 7986 `COLOR` property tint it to match.
- **feasts.py**: the title is the day's feasts (with `--major-days`, its
  major day first); the description gives each one's full name, level and
  color, and with `--links` where to read about it.
- **lectionary.py**: the title is the day's names; the description lists
  the readings, and with `--links` each one's address.

Some things worth knowing:

- **Re-importing updates rather than duplicates.** Each event's ID is made
  from its date and the church, not from its title, so importing a
  regenerated file replaces the events already there, even after a day is
  renamed. colors.py's IDs also name any calendars laid over the church's
  own, and the calendar and Easter when they are not the usual ones. The three
  scripts' IDs differ, so their feeds can share one calendar. The file for a
  given year is the same byte for byte every time it is made.
- **Julian wheels are converted.** Calendar apps read every date as
  Gregorian, so a Julian or Revised Julian year is written in Gregorian dates,
  as every listing is: Christmas on a Julian wheel arrives on 7 January.
- **Subscribing** rather than importing needs the file on a web server; point
  the calendar app's "subscribe by URL" at it and regenerate the file once a
  year.
