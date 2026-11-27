# Using the church year wheel

*Also in: [Dansk](user-guide.da.md), [Deutsch](user-guide.de.md), [Eesti](user-guide.et.md), [Español](user-guide.es.md), [Bahasa Indonesia](user-guide.id.md), [Íslenska](user-guide.is.md), [Italiano](user-guide.it.md), [Kiswahili](user-guide.sw.md), [Latviešu](user-guide.lv.md), [Magyar](user-guide.hu.md), [Malagasy](user-guide.mg.md), [Norsk (bokmål)](user-guide.nb.md), [Polski](user-guide.pl.md), [Português](user-guide.pt.md), [Slovenčina](user-guide.sk.md), [Suomi](user-guide.fi.md), [Svenska](user-guide.sv.md), [Українська](user-guide.uk.md).*

How to use the web page (`church_year.html`): every control, key and gesture,
and how to share what you see. It works the same in any modern browser,
on a computer, tablet or phone, with no internet connection needed except
for the links that open a Bible passage or a saint's page.

## What you see

- **The wheel.** One church year, Advent (or the church's own New Year) to
  the last week before the next. Each cell is a day, colored with the day's
  liturgical color. A day with no color (Good Friday in many churches) is
  white with gray diagonal lines. Rings around the cells show the months, the
  seasons and the two halves of the year. The picture in the middle is the
  church's emblem.
- **The chosen day** is outlined and turned to the top, where its text reads
  upright. The page opens on today, magnified 3× on it; press `0`, or choose
  1× in the zoom menu, for the whole wheel.
- **The heading** names the church year and the church.
- **The readout** under the bar names the chosen day: its date, its title or
  titles, its season and its color. When the church allows another color, it
  is named too: "purple (or royal blue)". Small signs in a cell (a chalice, a
  bowl, a fish) mark a holy day of obligation, a fast day or a day of
  abstinence; the readout says which. A saint's or feast's name is a link to a
  page about them.
- **The readings**, for a church whose lectionary is included, are listed
  under the readout: the day's propers, a festival kept on it, and the daily
  lectionary. Each citation opens the passage in the Bible version you chose.
  A saint's day or festival the wheel does not show (see Feasts) has its
  readings left off too.

## The bar

| Control | What it does |
|---|---|
| ◀ and ▶ | the day before or after |
| the date box | go to any date, in any year; the wheel redraws for that year |
| **Today** | back to today |
| **Find a day** | type a Sunday's, a season's or a feast's name, or part of it, and pick the day from the list (Enter takes the first): the wheel goes to it in the year it shows |
| **Week** | the chosen day's week, Sunday to Saturday, in a list with each day's names, color and readings; ◀ ▶ step a week and a day's date chooses it, and **Print** prints the week by itself, ready to hand round. On a phone this is the easy way to read a day's readings and the days around it |
| − and + , the slider and the menu beside it | magnify the wheel, 1× to 6× (the menu by halves) |
| the gear | the settings (below) |
| **Help** (bottom left corner) | opens this guide in a new tab, in the page's language when the guide has been translated into it |
| **Feedback** (bottom left corner) | opens the feedback form in a new tab; the day, church and settings on screen are sent with it, so a report can be followed up exactly |

## Keys

The keys work whenever the page has the focus (click the wheel first if it
is set inside another web page).

| Key | What it does |
|---|---|
| ← → | a week back or on, round the wheel |
| ↑ ↓ | the day before or after |
| Shift+arrow | a month back or on, to the same weekday of the same week (the third Sunday to the third Sunday) |
| Page Up / Page Down | the same date a church year back or on |
| T | today |
| S | the coming Sunday (today, on a Sunday); a link with `date=sunday` opens on it too |
| F | Find a day: type a name |
| W | the Week list |
| + and − | magnify or shrink |
| 0 | the whole wheel again (1×, centered); pressed again, back to the zoom it left (or the page's own) |
| Esc | close the Colors window, then the settings |

T, S, F and W come from English (Today, Sunday, Find, Week) and are the same in every
language the page speaks. They work on any keyboard: on one that types
another alphabet there (Cyrillic, for example), the key in the T, S, F or W
place does.

The arrow keys stay in the church year on the wheel: past its last week they
come round to its first, and back from its first to its last, as the wheel
does. Page Up and Page Down, and the ◀ ▶ buttons at the ends of the year, go
on into the next or previous year. To have the arrow keys go on as well,
check **Arrow keys go on into the next year** in Settings (All).

Apart from those, keys held with Ctrl, Cmd or Alt belong to the browser, so
Ctrl + and Ctrl − still enlarge the whole page and Alt+← still goes Back.

## Mouse and touch

| Action | What it does |
|---|---|
| click or tap a cell | choose that day |
| roll the mouse wheel | magnify about the pointer; what is under it stays put |
| pinch (touch screen or trackpad) | magnify about your fingers, and move as you pinch; held past 1x or 6x it stretches a little and springs back |
| swipe two fingers on a trackpad | move around the magnified wheel |
| drag (when magnified) | move around the wheel |
| one-finger drag on a phone | move around when magnified |

Stepping past the first or last day of the year moves into the next or
previous church year.

## Settings (the gear)

The panel opens on **Simple**: the year, the church (with its hymnal, lectionary and any calendars laid over it), Feasts, Bible, how the readings are shown, Reset settings, Copy link, Print and Download. **All** adds the rest under headings: the calendar and Latin names, the kinds of reading and the searches, the artwork, rings and colors, what stands under the wheel, Make a page and Edit the data. Nothing is switched off by Simple, only put away, and the choice is kept in the browser.

The gear shows a dot when any setting differs from the page's defaults.

| Setting | What it does |
|---|---|
| Language | the language of the page's buttons, menus and settings: the browser's (the first of its languages the page has, English otherwise), the church's (Match the church), or one chosen; kept in the browser. A page made with Make a page can start in a language of its own (its Language choice), until the reader picks another. The calendar's own names, dates and readings stay in the church's language |
| Year | draw another church year by the year it begins in |
| Tradition, Church | the family of churches and the church (hidden when the page offers only one) |
| Hymnal, Prayer book, Lectionary, Calendar | the church's book or series, when it has more than one |
| National calendar, Religious order, Personal jurisdiction | for the Roman calendar: lay a country's, a religious order's or an ordinariate's calendar over it |
| Calendar | Gregorian, Julian (Old Calendar) or Revised Julian (New Calendar); only on a page built with `--show calendar` |
| Easter | date Easter with the calendar, by the Western rule or by the Eastern rule; only on a page built with `--show easter` |
| Feasts | all commemorations, festivals only, principal days only, or none |
| Arrow keys go on into the next year | whether the arrow keys leave the church year on the wheel at its end, or go round it (config.csv `page_arrows_next_year`) |
| Thicker line where the year begins | a wider line where the year's last week meets its first, which are a year apart (config.csv `year_line`, `year_line_width`) |
| Dark text on reds | black lettering on the mid-tone reds |
| Latin names | for the one-year series: name the Sundays by their Introits (Invocabit, Laetare ...) |
| Readings | which of the day's Bible readings to list: the day's propers, feasts and festivals, other dated days (Ember and Rogation Days, Thanksgiving, national days ...), the daily lectionary, its additional readings (LSB's italic ones), a psalm table (LSB's morning and evening psalms), a Bible reading plan (the LCMS's, LCC's and NALC's Reading the Word of God), the Office lessons (Morning and Evening Prayer ...); only the kinds the church has are offered, and with all of them off the readings are hidden. Each set's name (**Readings**, **Daily Lectionary** ...) opens all its readings together at Bible Gateway. With several sets they are shown under tabs, one set at a time (the tab chosen stays chosen from day to day), or, with **Readings shown as: Columns**, all together on the right under the day's name. If they do not fit, a **▾ more** button opens the box and the sets slide into two columns, read left then right (one column on a phone); **▴ less** closes it |
| Readings shown as | Tabs or Columns, as above (offered when the page has both) |
| Slide | how fast the sets slide between the columns when **▾ more** or **▴ less** is clicked: Off, Quick, Medium (the default) or Slow; kept in your browser, not in the link (offered with Columns; a computer set to reduce motion never slides) |
| Bible | the translation a citation opens in; each church starts on its own |
| Open in | Bible Gateway or Bible.com (YouVersion); on a phone, the site's app if installed |
| Suggested hymns | the hymns suggested for the day year by year (the LCMS and LCC: LCMS Worship's lists and the LSB Hymn of the Day), under a **Hymns** tab after the readings' tabs, or after the readings in Columns |
| Hymnal topics | the hymnal marks after the day's name, one for each section of the hymnal's index the day has (Advent, Reformation, a saint's day), which open its hymns |
| Hymn search | a small hymnal mark (a book with a note on its cover) after each set of readings that searches [Hymnary.org](https://hymnary.org) for the hymns on them in the church's hymnal; offered where the church's `tradition.csv` names its hymnal there (`hymnary_hymnal`): the LCMS and LCC (LSB) calendars, Lutheran Service Book; WELS, Christian Worship: Hymnal (2021); the LCA, Together in Song; the United Methodist Hymnal; Singing the Faith (Methodist Church in Britain); the Moravian Book of Worship; Glory to God (PC(USA)); Lift Up Your Hearts (RCA/CRC); Church Hymnary 4 (Church of Scotland); Common Praise (Anglican Church of Canada, 1998); the Evangelical Lutheran Hymnary (ELS); Worship, 4th ed. (Roman Catholic); and for the Church of England a choice of four (see Hymnal). The day's name is followed by a mark too for each topic of the hymnal's index at Hymnary.org that suits the day (LSB: Confession and Absolution in Lent, End Times at the end of the year ...; Worship: each Sunday in Ordinary Time; Ancient and Modern: each Sunday and Proper of Common Worship; the New English Hymnal: the saints' days ...), opening its hymns in hymn-number order. An Introit's antiphon is searched with its psalm. The LCMS and LCC calendars also list the hymns of each Sunday and festival under **Hymns**, after its readings: the year's list from LCMS Worship's Hymn Suggestions, each hymn after the part of the service it is for (Entrance, Hymn of the Day, Distribution, Closing ...), and the Hymn of the Day of the LSB Hymn Selection Guide when the list does not sing it; each number opens the hymn at Hymnary.org. Each year shows one list, its own year's or else the lists in turn; the hymnal mark after **Hymns** opens every year's list for the day, for planning On a Sunday that keeps a festival (Reformation, All Saints), the window holds the Sunday's lists and the festival's together. |
| Hymnal | which hymnal Hymn search looks in, for a church with several (the Church of England: Ancient and Modern, Complete Anglican Hymns Old and New, Common Praise, the New English Hymnal) |
| Contemporary song search | a small circled ♫ mark after each set of readings that searches [Word to Worship](https://wordtoworship.com) for contemporary worship songs on them. Word to Worship knows the Protestant canon only, so the Apocrypha and the Book of Concord are left out of its search, and a set of nothing else has no mark |
| Artwork | the picture in the middle: the church's own; **By season**, which changes it with the day you choose (a wreath in Advent, the manger at Christmas, the empty tomb at Easter ...) and shows the church's own in the seasons without a picture; another (A to Z, with the seasons' pictures last, Advent to Pentecost); or a picture of your own: one the page was made with, or, on a page made to look for one (Make a page: *A picture beside the page*), a file named `center.svg` (or `center.png`, `.jpg`, `.webp`, `.gif`) put in the same folder as the page, which the page then opens on |
| Under the wheel | show the instructions and notes, and the artwork's credit |
| **i** (under the wheel) | shown when the credit is off and the artwork's license requires credit; opens the credit |
| Rings | turn rings on and off; the others widen to fill the space |
| Colors… | the colors on the wheel this year, the days' and each ring's, any of which can be changed (below) |
| Reset settings | put every setting back to the page's defaults, keeping the day |
| Copy link | copy a link to exactly what is on screen |
| Copy embed code | (All) copy a line of HTML that shows this page inside a page of your own website, with these settings, opening on the day it is read |
| Print | print the whole wheel on one page |
| Download… | save the wheel (SVG, PNG) and lists of its readings, colors and feasts, for this year or a run of years (below) |

A page made for one church may leave some of these out (see "A page for
one church" below).

### Colors

**Colors…**, under the Rings, opens a window listing every color on the
wheel for the year shown:

- **Days**: each liturgical color the year uses (lower halves included),
  named as the church's palette names them, with its swatch and code
  (`#660066`), and **Outside the year**, the gray cells before and after the
  church year.
- **Rings**: each ring's fill, outermost first, and for a ring with words
  (Parts of the year, Seasons, Months) the color of its words.

Click a swatch to pick a new color; the wheel is redrawn with it, and the row
is marked as changed. If a day's text would no longer read well on the new
color, it turns black or white, whichever reads better. The changes are kept
in the page's address, so **Copy link** shares them and the gear shows its
dot. **Reset colors** (in the window) or **Reset settings** puts them back.
The changes belong to this page only; to change the colors a church's data
files give (and what `church_year_image.py` draws), edit `colors.csv` and
`rings.csv` (see [data-files.md](data-files.md)).

## Sharing a day: links

The address in the browser always describes what is on screen, so a bookmark
or a copied address reopens the same day with the same settings.
**Copy link** puts it on the clipboard. While the wheel is on today, the
address says `date=today`, so a bookmark opens on whatever day it is later.

Examples:

```
church_year.html#date=2026-12-25
church_year.html#date=2027-04-18&lectionary=lcms-one-year&latin=1&zoom=2.5
church_year.html#date=2026-03-19&lectionary=roman&sub=united_states
church_year.html#year=2030
church_year.html#date=today
church_year.html#date=sunday
church_year.html#2026-12-25
```

A bare date (or `today`, or `sunday`) after the `#` works as `date=` does. `date=sunday` is the coming Sunday, today when it is one, and the address keeps the word while the wheel stays on that Sunday.

| Part | Values |
|---|---|
| `date` | `YYYY-MM-DD`, or `today` |
| `year` | the year a church year begins in, when there is no `date` |
| `lectionary` | a church's key (`lcms-three-year`, `roman`, `episcopal` ...) |
| `sub` | calendars laid over the Roman one, comma separated, or `none` |
| `calendar` | `gregorian`, `julian`, `revised-julian` |
| `easter` | `calendar`, `gregorian`, `julian` |
| `feasts` | `all`, `festivals`, `principal`, `none` |
| `reds` | `dark` or `set`: the Dark text on reds box checked or not |
| `latin` | `1` or `0` |
| `readings` | `none` to hide them, or the kinds to show (`day,feasts`) or to leave out (`-daily,-office`): `day`, `feasts`, `dated`, `daily`, `additional`, `psalms`, `plan`, `office`; left out while all are shown |
| `bible` | a version: `ESV`, `KJV`, `NRSVUE` ... |
| `bibleat` | `biblegateway` or `youversion` |
| `songs` | `1` or `0`: the contemporary song search marks on or off |
| `hymns` | `1` or `0`: the Hymn search marks on or off |
| `suggest` | `0`: no suggested hymns (no Hymns tab) |
| `topics` | `0`: no hymnal topic marks after the day's name |
| `art` | `auto`, an artwork key, or `file:NAME` for your own picture |
| `arrows` | `1` or `0`: the arrow keys go on into the next year, or round the year on the wheel |
| `help` | `1` or `0`: the instructions and notes under the wheel |
| `credit` | `1` or `0`: the artwork credit under the wheel |
| `hide` | rings to hide, comma separated |
| `colors` | colors changed in the Colors window, comma separated: `PURPLE-7a1f7a` (a day color), `lutheran:PURPLE-7a1f7a` (a day color in one tradition only), `lutheran:wels-one-year:PURPLE-7a1f7a` (in one church only), `ring.halves-e6c3f7` (a ring), `text.halves-000000` (a ring's words), `empty-f0f0f0` (outside the year) |
| `zoom` | 1 to 6 |

The browser's Back and Forward buttons step through the days you picked and
the settings you changed.

## Downloading the wheel and its lists

**Download…** (behind the gear, under Share) saves files made in the browser,
with nothing to install, for the church year on the wheel or a run of up to 101:

- **The wheel as SVG**: the drawing itself, sharp at any size, the same file
  `church_year_image.py` writes for the same church, year and settings.
- **The wheel as PNG**: a picture of it, as many pixels wide as you ask
  (5,000 unless the page was made with another `png_width`), on a clear or
  white background.
- **Lists**, the files `lectionary.py`, `colors.py` and `feasts.py` write:
  - **Readings**: each day's, as the Readings boxes and the Feasts setting
    choose them; *with links*, each opens where Bible and Open in say, and
    each set's heading opens all of its readings together.
  - **Colors**: the Sundays and principal days (or every named day, or every
    day) and the color the wheel paints each; *other colors* adds the others
    the church allows and the lower half's color.
  - **Feasts**: the festivals, saints' days and commemorations the Feasts
    setting keeps, on the days they fall that year; *with major days* adds
    Christmas, Easter, Pentecost and the like, and *with links* where to read
    about each.
  - **The year at a glance**: one row a year, the overview `colors.py
    --overview` writes: Advent, Christmas, the Epiphany, Ash Wednesday,
    Easter, Pentecost and the other movable dates, and how many Sundays fall
    after the Epiphany and after Pentecost or Trinity. It has no iCalendar
    form; with that format chosen it comes as CSV.

  Each list comes in the format chosen: CSV (a spreadsheet), HTML (a page to
  print), iCalendar (.ics, to import into a calendar app), JSON or Markdown.
  The lists' headings, notes and dates are in the page's language; CSV and
  JSON keep their English field names.

Each file is named as the scripts name it
(`lcms-three-year_2025-26_calendar.svg`, `lcms-three-year_2025-26_readings.csv`),
and more than one come together in a .zip. Everything set behind the gear
goes into the files: the church and its calendars, Latin names, feasts,
readings, rings, colors and artwork. A picture of your own put beside the page
(`center.svg` ...) goes into the wheel too when the page is opened from a web
server; opened straight from a file, the browser does not let the page read
it, and the files leave it out (and say so).

## Correcting or adding to the data

**Edit the data…** (also under Share) changes what the page draws from: the
chosen day's names, colors and readings (a reading's kind and text, readings
removed or added, a new kind of reading with its name), a feast or a set of
readings of your own on a date, the names and order of the kinds of reading,
the season colors and what each color looks like. The wheel shows each change
at once. The changes stay in this browser for this page, can be undone file
by file, go into any page **Make a page…** makes from it, and **Download
changed files** gives the data files they change, to put over the project's
`data` folder so the Python scripts read them too (see
[web-page.md](web-page.md#editing-the-data)).

## Making a page like this one

**Make a page…** (also under Share) saves a copy of the page to put on your
own website or hand to someone, without running Python. Everything
`church_year.py` can be told is there, starting as the page is now:

- **Churches it offers** (folded to one line with its count; click it to open): a box for each church, series and hymnal, grouped by
  tradition and church, with buttons for all of them, the tradition or church
  shown, only the one shown, or none. Click a tradition's + (or its name) to open it;
  its box ticks every church in it.
- **It opens:** the church and calendars, the year, the zoom and the language. *As this
  page opens* sets this group and the next two back to what the page itself
  opens with.
- **The wheel:** Feasts, Latin names, the rings, the colors (every color the
  ticked churches use, changed for all the churches together, tradition by
  tradition or church by church, with each one's own shades and the others'
  as swatches to choose from), text on mid-tone colors and the artwork,
  including a picture of your own with its credit and size.
- **Readings and links:** which kinds of readings the page carries (the
  others are left out of it), tabs or columns, its links (to the Bible, about
  the feasts, either or none: with none, the readings are plain text and
  there is no Bible to choose), the Bible menu (every version, these, or each
  church's own), the Bible it opens in (only the versions on that menu are
  offered), where readings open, Hymn search and the hymnal it opens on (for churches with several), and Contemporary song search.
- **Settings it shows:** whether readers can change the calendar, Easter, the
  artwork and dark text on reds.
- **Buttons it shows:** Download…, Make a page… and Edit the data… of its own.
- **Under the wheel**, a **help link** (this guide, unless you give another
  page, or none), a **feedback link** and **to embed in another page** (no
  `<html>` wrapper); the **file name** is beside *Make the page*.

*The same page from Python* shows the command that makes the same page with
the script; paste one back to set the window from it, or use *Save settings…*
and *Load settings…* to keep a selection in a small file (which
`church_year.py --settings FILE` reads too) (see [web-page.md](web-page.md#making-a-page-from-the-page)).

## Printing

**Print** (or the browser's own Print) gives the whole wheel on one page, in
color, portrait or landscape, Letter or A4, without the controls. For a
poster, make a PNG with `church_year_image.py` instead (see the README): it takes
the same choices on its command line, such as `python church_year_image.py roman
2027 --hide halves --art my_cross.png`, without changing `config.csv`.

## A page for one church

Whoever builds the page can limit it to some churches and leave out settings
a congregation has no use for:

```
python church_year.py --churches lcms-one-year,lcms-three-year --fixed artwork,reds
```

A menu with only one choice is hidden on its own. The Calendar and Easter
settings are left out unless the page is built with `--show calendar,easter`
(or `page_show` in config.csv); each church then keeps its own. `--fixed`
hides the Artwork setting and the Dark text on reds box, and keeps each
church's own (for the reds, config.csv's `mid_text`). `--bible` limits
the Bible menu: one version (`--bible ESV`, no menu), a list
(`--bible ESV,KJV`), a language (`--bible english`) or `own` (each church's
own, no menu). The menu groups the versions by language, English first.
`--art my_cross.png` puts your own picture in the middle and
in the Artwork menu; `--own-art "my_cross.png|credit=...|churches=..."`
credits it and makes it the own picture of churches, and `--drop-art` leaves
the churches' own pictures out. `--readings day` (or
`page_readings`) keeps only those readings: the page leaves the other sets
out, and is smaller for it. `--zoom 2.5` (or `page_zoom`) makes the page open magnified on its day; a
link's own `zoom=` still wins, and `0` shows the whole wheel and, pressed again, goes back. `--language de`
(or `page_language`) makes the page start in German until the reader picks another language. `--footer full`,
`credit` or `none` sets the lines under the wheel, and `--fragment` leaves out
the `<html>`, `<head>` and `<body>` for pasting into another page. See
[web-page.md](web-page.md) for building and embedding the page.

### Showing the wheel on your own website

The simplest way needs no building at all: one line of HTML shows the page
inside a page of your website, in a website builder's "embed" or "custom
HTML" block:

```html
<iframe src="https://churchyearwheel.github.io/ChurchYearWheel/" title="Church year calendar" style="width:100%;height:90vh;border:0" allow="clipboard-write"></iframe>
```

To have it open with your church and settings, choose them, open the gear's
**All** view, and press **Copy embed code** under Share: it copies that line
with the settings on screen, for the page you are on. The wheel inside it
opens on the day it is read. To show a page made for your congregation
instead (Make a page), put that file on your website and use its address in
the line.

## Good to know

- Any year works, from thousands of years BC to far in the future; the page
  computes it on the spot.
- Some churches change a color or a day in a known year (the Church in
  Wales's colors in 2011, for example); the wheel follows the use of the year
  shown.
- Where each calendar's data come from, and what is still missing, is in
  [provenance.md](provenance.md).
