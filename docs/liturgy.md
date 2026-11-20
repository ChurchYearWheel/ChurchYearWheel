# The church year: lectionaries, seasons and feasts

This page is about the LCMS calendar. The Roman Catholic calendar, and how any
tradition's rules are written, are in [traditions.md](traditions.md).

## How much of the feasts list to draw

The feasts CSV (`data/LCMS/LSB/feasts.csv`) holds three kinds of row, and
`feast_detail` says how many of them reach the wheel:

```
feast_detail,all         # all | festivals | principal | none
```

`none` leaves out every row, keeping only the Sundays and principal days. For
the Roman calendar, the levels follow rank instead: `principal` is the
solemnities and `festivals` adds the feasts.

| value | keeps | example of what goes |
| --- | --- | --- |
| `all` | every row — 116 days | — |
| `festivals` | the 35 rows that color their cell | J.K. Wilhelm Loehe, Basil the Great, Abraham |
| `principal` | the 9 rows with a `color_override` | St. Andrew, Reformation Day, Holy Cross Day |

The middle one is usually what is wanted for a less crowded wheel: it drops the
81 plain commemorations and keeps everything the LCMS page prints in bold,
including the apostles and evangelists, whose rows color only the lower half
of the cell through `color_override_bottom`. `principal` is the strict reading —
only days whose color replaces the season's — and it is a large cut, since
Reformation Day and the apostles are all `color_override_bottom` rows.

Every drawing script takes it as a flag, overriding the config for one run:

```
python church_year_image.py --feasts festivals
python church_year.py --feasts principal
python colors.py --feasts festivals
python new_year.py 2027 --feasts festivals --draw
```

`new_year.py` writes the choice into the year's `config.csv`, so later drawings
of that year follow it. In the interactive page it is a dropdown, and changing
it redraws on the spot — the page opens on whatever `config.csv` asked for.

Both renderers are checked against each other at all three levels:

```
python web/verify.py --feasts every
```

## When a saint's day falls on a greater day

The feasts file is by date, so now and then a saint's day lands on a day that
outranks it. Left alone, the feast's color won: the Annunciation's white
replaced the scarlet of Palm Sunday (2029, 2040), the violet of a Sunday in Lent
(2057) and the scarlet of weekdays in Holy Week (2043, 2054, 2059).

Now a conflict splits the cell: **the higher-ranking day keeps the top, and the
lower-ranking day's color covers the bottom half.** Palm Sunday 2029 is scarlet
over white, with *Palm Sunday* above and *Annunciation of Our Lord* below.

A day outranks a feast that falls on it when it is

| the day | e.g. |
| --- | --- |
| any day of Holy Week or Easter week, named or not | Palm Sunday + the Annunciation: scarlet over white; Easter Day + St. Mark: white over red |
| a Sunday in Advent, Lent or Easter | Advent 1 + St. Andrew: blue over red; Lent 3 + St. Joseph: violet over white |
| any other day the Sundays file names in those seasons | Ash Wednesday + St. Matthias: black over red; the Ascension + St. Philip and St. James: white over red |
| a day the Sundays file gives a color of its own | Pentecost + the Visitation: red over white; Trinity + St. Barnabas: white over red |

Everywhere else the feast colors the day as it always has. A row with a
`color_override` colors the **whole cell**: St. Michael on an ordinary Sunday
after Pentecost is all white, with the Sunday's title still on top, and the
Annunciation on an ordinary Lent weekday is all white. A row with only a
`color_override_bottom` colors the lower half under the season's color, as the
apostles always have.

The day's own split comes first: Christmas Eve, Holy Saturday and a Reformation
Day observed on the Sunday before 31 October already divide their cells, so a feast on one of those
keeps its name but not its color. Where the two colors are the same — the
Annunciation on Maundy Thursday, both white — the cell is simply left whole.

### Displaced feasts

A feast that falls on a greater day is *displaced*: it cannot be kept on its own
date, and churches usually move ("transfer") it to the next free day — for the
Annunciation, commonly the Monday after the Second Sunday of Easter. The wheel
moves nothing. It shows both on the actual date, as above, and leaves the
transfer to the parish; add a dated row to the feasts file if you want the
transferred day on the wheel too.

### The settings

Two settings in `config.csv` say where the rule applies, by the season keys in
`seasons.csv`:

```
feast_yield_seasons,ADVENT LENT HOLY_WEEK EASTER POST_EASTER PRE_PENTECOST
feast_yield_every_day,HOLY_WEEK
```

`feast_yield_seasons` holds the seasons whose Sundays and named days outrank a
feast. `feast_yield_every_day` holds the seasons in which every day does, and
every day of the week after — the week after Holy Week being Easter week. Set
either to `none` to turn it off. A day with a color of its own in the Sundays
file outranks a feast wherever it falls. Both renderers apply the same rule,
and `web/verify.py` checks them against each other.

## Pre-Lent, and its color

The one-year series keeps **Pre-Lent** — Septuagesima, Sexagesima and
Quinquagesima, the three Sundays before Ash Wednesday. The three-year series
has no such season: it descends from the 1969 Roman lectionary, which abolished
it, so those weeks are simply more Sundays after the Epiphany. That is also why
Transfiguration sits in different places in the two series — last Sunday after
the Epiphany in the one-year, immediately before Ash Wednesday in the
three-year.

Pre-Lent has its own row in `seasons.csv` rather than borrowing Epiphany's
color:

```
EPIPHANY,GREEN
PRE_LENT,GREEN
LENT,PURPLE
```

**Green**, on the authority of LSB's own "The Church Year: Sundays and Seasons"
page, which marks Septuagesima, Sexagesima and Quinquagesima **G**. Pre-Lent
keeps its own season row so the ring still labels it and so its color can be
changed on its own: for the historic violet, change that one row to
`PRE_LENT,PURPLE`. The browser page picks the change up the next time
`church_year.py` runs.

### The Latin names

The one-year series knows most Sundays by a Latin name taken from the first
word or two of that day's Introit: *Ad Te Levavi* is Psalm 25:1, *Laetare* is
Isaiah 66:10, *Quasimodo Geniti* is 1 Peter 2:2. Two of the sixteen are not
Introit incipits — *Palmarum* is simply Palm Sunday, and *Rogate* is from
*rogare*, "to ask", for the theme of prayer running through that day.

These are names, not propers. The propers are everything in the service that
changes with the day — Introit, Collect, Gradual, Epistle, Gospel, Verse,
Offertory, Communion — as against the Ordinary, which does not. The name is one
word lifted off the front of one of them.

A Latin name is written into the title after a line break, which the drawing
treats as a **preference rather than a command**: it keeps the name on a line
of its own where that costs nothing, and lets it flow on after the title where
the cell is too tight. Advent 1 in 2026-27 comes out as three lines at 9.7pt
with "(Ad Te Levavi)" on its own; in 2025-26, where the cell also carries the
year's opening date, it stays on one line as before.

## Which lectionary

The three-year and one-year series name the Sundays differently, and
`new_year.py` will build either:

```
python new_year.py 2026                                   # three-year (the default)
python new_year.py 2026 --lectionary lcms-one-year
python new_year.py 2026 --lectionary lcms-one-year --latin-names
```

The choice is also a setting — put `lectionary,lcms-one-year` in `config.csv` and
every later run of `new_year.py` from that folder follows it without the flag.
`--lectionary` overrides the setting for one run, and the generated year records
which series it used.

What changes in the one-year series:

| | three-year | one-year |
| --- | --- | --- |
| Sundays after Trinity | "Second Sunday after Pentecost" onward, counting Trinity as the first | "First Sunday after Trinity" onward |
| pre-Lent | none | Septuagesima, Sexagesima, Quinquagesima, and a Pre-Lent segment in the season ring (still green) |
| the Transfiguration | the Sunday before Ash Wednesday | the last Sunday after the Epiphany, before Septuagesima |
| the Visitation | 31 May | 2 July |
| Latin names | not used | optional: "Third Sunday in Lent (Oculi)" |

`latin_names,TRUE` (or `--latin-names`) appends the Latin name to the
Advent, Lent, Palm Sunday and Easter titles; `--no-latin-names` leaves it off
for one run. It costs nothing in layout — those
Sundays sit in the outer band, and the smallest label on the wheel is the same
either way — so it is worth generating both and comparing.

Rows in `data/LCMS/LSB/feasts.csv` (and in `days.csv` and `periods.csv` beside it)
may name a `variant`, `one-year` or `three-year`; a blank means both. That is
how the Visitation lands on the right date without you editing anything.

## Rolling over to the next year

`new_year.py` builds the three date-dependent files for any church year:

```
python new_year.py 2026                  # writes ./data_2026, copying ./data
python new_year.py 2026 --dry-run        # just print the dates
python new_year.py 2026 --draw           # and draw it: SVG, PNG and HTML
python new_year.py 2026 --draw --no-png  # skipping the slow part
python new_year.py 2026 --draw --no-html # no interactive page
python new_year.py 2026 --out years/2026 --draw --images-out images/
python new_year.py 2026 --out data --force   # regenerate in place
python church_year_image.py --data data_2026  # then draw it
```

The year given is the year Advent begins, so `2026` means Advent 2026 through
November 2027. It computes Easter and everything hanging off it, works out the
tradition's rules for that year, writes `sundays_seasons.csv`,
`season_periods.csv`, `broad_seasons.csv`, `halves.csv` and `year_feasts.csv`,
copies the undated files and the tradition folders across unchanged, and copies
`config.csv` with only its dates, `output_filename` and the tradition's choices
rewritten — every setting you have tuned is preserved.
It refuses to write into an existing directory without `--force`.

Pointing `--out` at the source folder regenerates in place: the three dated
files are rewritten, `config.csv` is updated, and the undated files are left
exactly as they are. Re-running it is harmless — the same year in produces the
same files out.

`--dry-run` prints what it worked out, which is worth a glance before drawing:

```
Church year 2027-28: 2027-11-28 to 2028-12-02 (371 days, 53 weeks)
  Easter               2028-04-16  (Sunday)
  Ash Wednesday        2028-03-01  (Wednesday)
  ...
  Sundays              6 after Epiphany, 24 after Pentecost
```

The conventions it applies: Advent 1 is the fourth Sunday before Christmas;
the Transfiguration is the Sunday before Ash Wednesday; the Ascension is the
Thursday forty days after Easter; Reformation Day is kept on the Sunday on or
before 31 October; All Saints' Day on the first Sunday in November;
Thanksgiving is the fourth Thursday in November. Those are rules in
`data/LCMS/LSB/days.csv`; change any of them there (the date language is in
[traditions.md](traditions.md)).

These were checked against eighteen published LCMS Church Year Calendars —
eight three-year (2017-18 to 2026-27) and ten one-year (2015-16 to 2026-27).
247 dates agree, 0 disagree, in both series.

All Saints' Day and Reformation Day both displace that Sunday's number, and
both are titled "(observed)" only when they have actually been moved. All
Saints is drawn white whatever the season, since a feast of that rank overrides
the green of the Sundays after Pentecost.

Each of the two also has a **fixed-date row** in the festivals file — 31 October
for Reformation Day, 1 November for All Saints' — so the day itself is marked
even in the years when the observance is kept on a different Sunday. In a year
where the feast falls on the Sunday anyway, the fixed row and the Sunday title
name the same thing on the same day, and `deduplicate_day_labels` drops the
repeat so the cell carries the name once. `--report` says when that happens:

```
2026-11-01  duplicate  'All Saints' Day' also appears as the day's title;
                       the commemoration was not drawn
```

Reformation Day is titled "Reformation Day (observed)" only when it has actually
been moved, and is then drawn red over green — the observance above the Sunday
after Pentecost it displaces. In a year where 31 October is itself a Sunday —
2027, for instance — it keeps its plain name and the whole cell is red, because
the festival and the Sunday are the same day. The commemorations file also
carries a `10-31` Reformation Day entry, so in those years the same name would
land on that cell twice; `deduplicate_day_labels` drops the commemoration and
says so in `--report`.

It was checked by regenerating 2025-26 and diffing against the hand-built
files — all three come out identical.

### The weeks after Easter

The one-year series divides them the way the historic calendar does, and
`season_periods.csv` follows it:

| label on the ring | from | to | days |
| --- | --- | --- | --- |
| Easter | Easter Day | the Saturday of Quasimodo Geniti week | 14 |
| Post-Easter | Misericordias Domini | the Saturday of Jubilate week | 14 |
| Pre-Pentecost | Cantate | the day before the Ascension | 11 |
| Pentecost | The Ascension of Our Lord | the day before Trinity | 17 |
| Trinity | The Holy Trinity | the Saturday after | 7 |
| Season After Trinity | First Sunday after Trinity | the Last Sunday | 175 |

Trinity week is named `Trinity` rather than `Post-Pentecost`, because the
season that follows it counts from Trinity and not from Pentecost — a week
called "Post-Pentecost" sitting between `Pentecost` and `Season After Trinity`
reads as though it belonged to the wrong one.

**The labels and the colors do not divide at the same places.** Pentecost is
named from the Ascension onward, but the days themselves stay white until
Pentecost has actually come. So a `season_periods.csv` row may do one job or
the other:

| the row has | it does |
| --- | --- |
| a `name` and a `season` | labels the ring and colors its days — the ordinary case |
| a `name`, no `season` | labels the ring, colors nothing |
| a `season`, no `name` | colors its days, puts nothing on the ring |

Which is how the weeks above are labeled while the cells keep the coloring
they have always had:

| colored | from | to |
| --- | --- | --- |
| `EASTER` white | Easter Day | the Saturday of Easter week |
| `POST_EASTER` white | Quasimodo Geniti | the day before the Ascension |
| `PRE_PENTECOST` white | the Ascension | the day before Pentecost |
| `PENTECOST` green | Pentecost | the Saturday of Pentecost week |

Only the one-year series needs the split; everywhere else a row still does
both jobs at once.

The three-year series still keeps one long green season, but Pentecost week is
now named ahead of it:

| season | from | to |
| --- | --- | --- |
| Easter | Easter Day | the day before Pentecost |
| Pentecost | Pentecost | the Saturday of Pentecost week |
| Season After Pentecost | The Holy Trinity | the Last Sunday |

A season called "Season After Pentecost" that began on Pentecost named a feast
the ring never showed. In this series Trinity Sunday is itself the First Sunday
after Pentecost, so the counted Sundays begin exactly where the season now
does, and Pentecost week takes the same seven days of arc that Holy Week does.

Each season has its own row in `seasons.csv`, so the colors are yours to
change. Nothing about the coloring moved with this: the weekday cells follow
LSB's page through the Easter weeks in white and stay green from Pentecost
onward, and the red of Pentecost and the white of The Holy Trinity are
overrides on those two days in `sundays_seasons.csv`, so the festivals are
colored without repainting the whole week around them. `POST_PENTECOST` is
still listed in `seasons.csv` alongside `TRINITY`, so a year folder generated
before this change keeps its green rather than falling back to the default.

### The halves, and the two cycles

The outer lavender ring carries four labels, and replaces the old
`THE TIME OF THE CHURCH` arc:

```
              CHRISTMAS   FESTIVAL HALF: ABOUT THE SAVIOR   EASTER
                        NON-FESTIVAL HALF: ABOUT THE CHURCH
```

`FESTIVAL HALF` runs from Advent to the end of Pentecost week (three-year) or
Trinity week (one-year) — see below — and `CHRISTMAS` and `EASTER` divide that
same stretch between them — so all three are nested on one
band. They do not collide because each label is centered on its own span: the
half's name takes the middle and the two cycle names sit out toward the ends,
where the half's name does not reach. Over 1,600 year-and-lectionary drawings
from 1600 to 2400 none of them has had to give way; if one ever does, the
narrower span keeps its size and the wider one shrinks until it clears.

#### Where the festival half ends

Sources do not agree, and the disagreement follows the lectionary:

- **Historic, one-year usage** counts the green Sundays *after Trinity*, and
  catechetical material written for it lists The Holy Trinity as the last of
  the festival days, with the non-festival half beginning at the First Sunday
  after Trinity.
- **Material written for the three-year series**, where Trinity Sunday is
  itself the First Sunday after Pentecost, begins the non-festival half — "the
  Season after Pentecost" — with the Festival of the Holy Trinity.
- A few sources end the festival half on the Day of Pentecost itself.

`festival_half_end` in `config.csv` chooses, and `new_year.py` writes the
dates into `halves.csv` (the browser page works them out the same way):

| value | the festival half ends | non-festival half begins |
| --- | --- | --- |
| `auto` *(shipped)* | one-year: `trinity-week`; three-year: `pentecost-week` | |
| `pentecost-eve` | the day before Pentecost | Pentecost |
| `pentecost-week` | the Saturday after Pentecost | The Holy Trinity |
| `trinity-week` | the Saturday after Trinity | the First Sunday after Trinity |

With `auto` the boundary lands exactly where each series' own season ring
already divides: at "Season After Pentecost" in the three-year wheel and at
"Season After Trinity" in the one-year. The `EASTER` cycle label ends wherever
the festival half does, so the two stay nested.

The rows come from `halves.csv`:

| column | means |
| --- | --- |
| `subtitle` | set in italics at regular weight after the name |
| `scale` | this label's size against the ring's own — a number, or the word `subtitle` for whatever size subtitles are |

`ring_subtitle_separator` in `config.csv` joins a name to its subtitle (`": "`
by default) and `ring_subtitle_ratio` sizes it against the name (0.78). The
name and the subtitle are two tspans of one text run rather than two runs
placed by measurement: a 900-weight face is wider than the metrics this package
carries for it, so an offset computed from those would set the subtitle inside
the name. Both are measured together for the arc fit, so the autofit steps down
on the whole label rather than on either part of it.

Where a source nests one span inside another this way, only the covering span is
painted; the nested ones contribute their labels alone, so giving the ring a
stroke does not draw lines across the middle of it.

`broad_seasons.csv` (`THE TIME OF CHRISTMAS` and the rest) is still generated
but no ring sources it, now that the cycle names live in `halves.csv`. Add a
`segments` row with `source,broad_seasons` if you want that wording back.
