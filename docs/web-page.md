# The wheel in a browser

`church_year.py` writes one self-contained HTML file that carries the
renderer itself: type any year and the wheel is drawn for it on the spot, in
about 50 ms. One file of about 2 MB covers every year there will ever be,
with no year list to keep up to date, no server and no network access. Copy it
to a phone, attach it to an email, or put it on a shared drive and it still
works.

```
python church_year.py                        # -> church_year.html
python church_year.py -o wheel.html
python church_year.py -o pages/              # into a folder
python church_year.py --year 2030            # open on a different year
python church_year.py --data years/2026      # take the settings from a year folder
python church_year.py --fragment             # no <html>/<body>, to put in another page
```

It opens on whichever church year contains today, turned so the week holding
the chosen day sits at the top — where the tangential text reads upright —
while the Luther rose in the middle stays still and level. The day itself is
outlined, and the readout names it, its title or titles, its season and its
color. A saint's or festival's name is a link to a page about them (for the
LCMS calendars, Concordia Publishing House's page on each commemoration;
otherwise Wikipedia), and each reading's citation opens the passage in the
Bible version chosen behind the gear. Under it, for a calendar that has them, are the day's Bible readings:
its propers, those of a festival kept on it, and the daily lectionary, each
on a line of its own (a box three lines tall, so the wheel does not change
size from day to day; a day with more scrolls inside it). A feast's readings
follow the feast: one the wheel does not show that day -- left off by the
Feasts menu, outranked, moved to another day, or of a calendar not laid over
it -- is not listed either. The turn is animated over about two-thirds of a second and honors
`prefers-reduced-motion`.

The bar keeps only what you reach for while looking at the wheel — the date,
the day arrows, **Today**, and the magnifier — and everything that is set once
and then left alone lives behind the **gear**:

The panel opens on **Simple**: the year, the church (with its hymnal, lectionary and any calendars laid over it), Feasts, Bible, how the readings are shown, Reset settings, Copy link, Print and Download. **All** adds the rest under headings: the calendar and Latin names, the kinds of reading and the searches, the artwork, rings and colors, what stands under the wheel, Make a page and Edit the data. Nothing is switched off by Simple, only put away, and the choice is kept in the browser.

| in the bar | to |
| --- | --- |
| the date box | go to any date, in any year |
| `←` / `→` | a week back / on |
| `↑` / `↓` or the arrows | step a day |
| `Shift` + an arrow key | a month back / on, to the same weekday of the same week (the third Sunday to the third Sunday; a fifth the month lacks becomes its last) |
| | the arrow keys go round the church year on the wheel: past its last week to its first, and back; the ◀ ▶ buttons and `PageUp` / `PageDown` go on into the next or previous year. With **Arrow keys go on into the next year** checked in Settings the arrow keys go on too, into the next year's wheel and back into the last |
| `PageDown` / `PageUp` | a church year on / back, keeping the date (29 February becomes the 28th, and a date near Advent is held inside the year asked for) |
| **Today** or `T` | jump back |
| **Find a day** or `F` | type a Sunday's, a season's or a feast's name (any part of it, in any case, accents or none) and pick it from the list, or press Enter for the first: the wheel goes to that day in the year it shows. The names that begin with what you typed come first |
| **Week** or `W` | the chosen day's week, Sunday to Saturday, in a list: each day's names, color and season, and its readings (the kinds the Readings boxes show) with their links. ◀ ▶ step a week; a day's date chooses it on the wheel. Easier to read on a phone than the wheel's cells. **Print** prints the week alone: the church and year, the week, and each day with its full date, names, color and readings, the links as plain text, a day never split between pages |
| the slider, the 1×–6× menu beside it, `+` / `-`, the mouse wheel, or pinching | read a cell close up (the menu steps by halves, and shows a zoom in between while the wheel or a pinch has left one) |
| dragging | move around while magnified |
| `0` | go back to the whole wheel; pressed again, back to the zoom it left (the first time, the page's own `--zoom`) |

Keys held with Ctrl, Cmd or Alt are left to the browser, so Ctrl + and Ctrl −
still enlarge the whole page and Alt+← still goes Back.

| behind the gear | to |
| --- | --- |
| Year | draw another church year by the year it begins in (its Advent year) rather than by a date |
| Tradition, Church | the family of churches and the church (a menu with one choice is hidden) |
| Hymnal, Prayer book, Lectionary, Calendar | the church's book or series, when it has more than one |
| National calendar, Religious order, Personal jurisdiction | shown for the Roman calendar: lay a country's, a religious order's or an ordinariate's calendar over it, in any combination |
| Calendar | Gregorian, Julian (Old Calendar), Revised Julian (New Calendar); only with `--show calendar` |
| Easter | move the paschalion on its own: with the calendar, Western, Eastern; only with `--show easter` |
| Feasts | all, festivals only, principal days only, or none |
| Latin names | shown for the one-year series (LCMS One-year, TLH and ELHB, LCC and ELS One-year) and Roman 1962: name the Sundays from their Introits |
| Readings | shown for a calendar with readings (most churches now; `python lectionary.py --list` marks those with none yet): which of the day's Bible readings to list under its name, a box for each kind the church's lectionary has -- *The day's propers* (its Sunday, holy day or season, with any other service appointed for it, such as the Easter Vigil), *Feasts and festivals* (a saint's day or festival, while the wheel shows it), *Other dated days* (a day the calendar does not name, kept by its date or a date rule: the prayer books' Ember and Rogation Days, Thanksgiving Day where it is no day of the calendar, New Year's Day, Dominion Day, Norway's 1 and 17 May and Samefolkets dag, the German days of remembrance, the Byzantine Saturdays before and after the Exaltation, the Nativity and Theophany), *Daily lectionary* (a daily or weekday lectionary: LSB's Daily Lectionary, the RCL's Daily Readings, the Roman weekday Masses, TLH's Daily Psalter), *Additional readings* (the additional readings a daily lectionary offers beside its own, for reading more of the Bible: LSB's, printed in italics, as their own set, Daily Lectionary: Additional Reading), *Psalm table* (LSB's psalms for daily prayer, a morning and two evening psalms for each day by season and weekday, as the set Psalms for Daily Prayer), *Bible reading plan* (Reading the Word of God, the three-year plan of the LCC, LCMS and NALC, kept by the calendar year: Old Testament, psalm and New Testament for each day, its own readings on fourteen festivals) and *Office lessons* (Morning and Evening Prayer, Matins, Common Worship's second and third services, TLH's and the ELHB's Morning and Evening Lessons). All are on by default; with every one off the readings are hidden. Shown as tabs (the default: a row of the sets' names, the chosen one's readings under it, the same tab kept from day to day) or columns (the sets on the right under the day's name, three lines tall), chosen under *Readings shown as* when the page offers both (`--readings-layout`). More than fits and a **▾ n more** button opens the box (up to half the screen): the first sets slide over to a column on the left and the later ones fill the right, split where the two come out most even (one column on a phone); **▴ less** closes it, and it stays open from day to day until closed. *Slide* sets how fast the sets move between the columns (Off, Quick, Medium, Slow), kept in the reader's browser |
| Bible | the translation a reading opens in: each church starts on its own (LCMS ESV, WELS EHV, ELCA and Episcopal NRSVUE, United Methodist CEB, Roman Catholic NABRE, TLH and the ELHB KJV ...), ESV where it names none |
| Open in | Bible Gateway or Bible.com (YouVersion). On a phone or tablet the link opens in that site's app when it is installed. A version only one site carries opens there whichever is chosen: Bible.com lacks most of the non-English ones, and Bible Gateway lacks the Indonesian Terjemahan Baru (whose sets' headings then open nothing, since Bible.com shows one passage at a time). A reading from the Apocrypha (Sirach, Wisdom, Tobit, Baruch, the Maccabees ...), which the ESV and most others leave out, opens in a version that has it: the RSV at Bible Gateway (the ESV's Apocrypha, used in CPH's Lutheran Edition, revises the RSV's and is not online), the NRSVUE at Bible.com (which has no RSV Apocrypha); a set with one opens in the RSV. The NRSVUE, NRSVA, RSV, NABRE, CEB, RSVCE and DRA open as chosen. A reading from the Book of Concord ("Augsburg Confession XX 1–8", "Apology 4:117–146", "Smalcald Articles 3/3:1–18", "Treatise 12–21", "Small Catechism, Baptism", "Formula of Concord, Solid Declaration 2:1–7") opens at its first paragraph on bookofconcord.org, whose pages have an anchor for every paragraph (#ap-iv-0117); the Catalog of Testimonies and the Preface to the Book of Concord open at their section. A set's name opens its readings together at Bible Gateway without its Book of Concord readings, which Bible Gateway lacks, and a set of only those has no such link; the Song search mark leaves out the Apocrypha and the Book of Concord too |
| Arrow keys go on into the next year | unchecked (as the page opens, unless built with `--arrows-next-year` or `page_arrows_next_year` set to `TRUE`), the arrow keys go round the year on the wheel, a week's step keeping its weekday; checked, a step past the year's end draws the next church year, or the last |
| Thicker line where the year begins | a wider line (`year_line_width`, 4) where the year's last week meets its first, across the day cells and the rings beside them (`year_line`, `--year-line`) |
| Propers | a church whose sets hold parts of the service as well as readings (`tradition.csv` `reading_propers`; the LCMS and LCC: the Introit, Gradual and Verse) lists those on a line of their own after the readings, headed *Propers*, which opens them together, with Hymn search and song search marks of their own; the set's own heading and marks are its readings', and the heading opens only them, the page a lector prints. Unticked, the page and its Download lists leave them out |
| Hymn search | a hymnal mark after each set of readings: Hymnary.org's hymns on them in the church's hymnal (`tradition.csv` `hymnary_hymnal`; the LCMS Three-year: `lsb2006`, Lutheran Service Book), the readings joined with semicolons and the verses with hyphens, as Hymnary's scripture index writes them; the Apocrypha and the Book of Concord are left out, and a set of only those has no mark |
| Contemporary song search | a circled-note mark after each set: Word to Worship's contemporary worship songs on its readings |
| Dark text on reds | black lettering on the mid-tone reds (see below) |
| Artwork | the picture in the middle: the tradition's own; **By season**, which changes it with the day chosen (the wreath in Advent, the manger at Christmas, the star and crowns in Epiphany, the cross and thorns in Lent, three crosses in Holy Week, the empty tomb at Easter, the dove at Pentecost) and keeps the church's own in the seasons that have none (`season_art.csv`); any in `artwork.csv` (A to Z, then the seasons' own pictures at the foot of the menu in the order of the church year, Advent to Pentecost, as `season_art.csv` names them), or your own picture when the page was made with one (`--art FILE`); on a page made with `--local-art` (or `page_local_art`), a `center.svg` (or `center.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`) in the page's own folder is found when the page opens, offered as "center.svg (beside this page)" and shown unless a link or `page_fixed` says otherwise (`art=local` in a link) |
| Under the wheel | the instructions and notes, and the artwork's credit |
| Rings | which rings to draw |
| Colors… | the colors on the wheel this year, the days' and each ring's, any of which can be changed (see below) |
| Reset settings | put all of the above back to what `config.csv` asks for, keeping the day and the magnification |
| Copy link | copy a link that opens on this day with these settings |
| Copy embed code | (All) copy a line of HTML, an `<iframe>`, that shows this page inside a page of another website, with these settings, opening on the day it is read (see [In another page](#in-another-page)) |
| Print | print the whole wheel on one page |
| Make a page… | a page like this one to put on a website, for every church here or only some, opening with these settings (see [Making a page from the page](#making-a-page-from-the-page)) |
| Download… | the wheel as SVG and PNG files (the same SVG `church_year_image.py` writes) and the readings, colors and feasts lists and the year at a glance (the files `lectionary.py`, `colors.py`, `colors.py --overview` and `feasts.py` write), for this year or up to 101 years, several in a .zip |

The gear carries a dot when any of those is set away from what `config.csv`
asked for, so a wheel that is not in its default state says so without having
to be opened. The Year box is left out of that reckoning: moving through the
years is what the wheel is for, and a dot that is always lit says nothing. **Reset settings** is available only while the dot is lit.

The date box takes **any** date, not just one from the year on the wheel: give
it a date from another year and the wheel is redrawn for that year, with the
Year box behind the gear following along. Stepping past 1 Advent or the Last Sunday rolls
into the neighboring year the same way.

There is no ambiguity to trip over here, which is worth saying because it looks
like there should be. Advent Sunday to Advent Sunday is always a whole number
of weeks — 364 days, or 371 in a long year such as 2027-28 — so the church
years tile the calendar exactly, with no gap and no overlap, and every date
names precisely one of them. (Checked by brute force over 73,050 consecutive
dates, 1950 to 2150: every one belongs to exactly one church year.)

The one thing that really does appear twice is a *commemoration* in a 371-day
year: 2027-28 runs from 28 November 2027 to 2 December 2028 and so contains 30
November twice over, which is why St Andrew can be drawn at both ends. That is
what the `feast_repeat` setting is for, and it concerns labels rather than
which year a date belongs to.

## Links to a day

The page keeps its address up to date as you move, so the address bar always
holds a link to what is on screen. **Copy link** behind the gear puts it on the
clipboard. Opening the link opens the page on that day, with the same settings
and magnification.

While the wheel is on today the address says `date=today` rather than the
date, so a bookmark, or a reload next week, opens on whatever day it is then.
Step to any other day and the address names it. **Copy link** always writes the
date out, so a link you send opens on the day you were looking at:

```
church_year.html#date=2026-12-25
church_year.html#date=2027-04-18&lectionary=lcms-one-year&latin=1&zoom=2.5
church_year.html#date=2026-03-19&lectionary=roman&sub=united_states,jesuits
church_year.html#date=2026-12-25&calendar=julian&easter=calendar
church_year.html#year=2030                  an Advent year, opening on its first day
church_year.html#2026-12-25                 a bare date works too
church_year.html#date=today                 whatever day it is when opened
```

| key | values |
| --- | --- |
| `date` | a date in the wheel's calendar, `YYYY-MM-DD` (years BC as `-003000-12-03`), or `today` |
| `year` | an Advent year, used when there is no `date` |
| `lectionary` | a key from `traditions.csv`: `lcms-three-year`, `lcms-one-year`, `roman` |
| `sub` | the calendars laid over it, comma separated: `sub=england,dominicans`; `sub=none` for none |
| `art` | the artwork: `auto` (each church's own), `none`, a key from `artwork.csv`, or `file:NAME` for a picture of your own the page was made with |
| `calendar` | `gregorian`, `julian`, `revised-julian` |
| `easter` | `calendar` (follow the calendar), `gregorian`, `julian` |
| `feasts` | `all`, `festivals`, `principal`, `none` |
| `reds` | `dark` or `set`: the Dark text on reds box checked or not |
| `latin` | `1` or `0` |
| `readings` | the kinds of readings listed, when not all: `none` (`0` too), the kinds shown (`day,feasts`) or the kinds left out (`-daily,-office`), of `day`, `feasts`, `dated`, `daily` and `office`; the page writes whichever is shorter |
| `bible` | a Bible version: `ESV`, `EHV`, `KJV`, `NKJV`, `NIV`, `NRSVUE` ... |
| `bibleat` | `biblegateway` or `youversion` |
| `songs` | `1` or `0`: the Word to Worship marks on or off |
| `propers` | `0`: the parts of the service (Introit, Gradual, Verse) left out of the readings |
| `arrows` | `1` or `0`: the arrow keys go on into the next year, or round the year on the wheel |
| `help` | `1` or `0`: the instructions and notes under the wheel |
| `credit` | `1` or `0`: the artwork credit under the wheel |
| `hide` | ring keys from `rings.csv`, comma separated: `hide=halves,seasons` (the day cells and the artwork cannot be hidden) |
| `colors` | colors changed in the Colors menu, comma separated: a color's name and its new fill (`PURPLE-7a1f7a`), a ring's fill (`ring.halves-e6c3f7`) or its words (`text.halves-000000`), and the cells outside the year (`empty-f0f0f0`) |
| `zoom` | 1 to 6 (left out when it is the page's own, `--zoom` / `page_zoom`, 1 unless set) |

Only settings that differ from `config.csv` are written into the link, so an
ordinary link stays short and follows the file if its defaults change later.
Anything the page does not recognize is ignored rather than breaking it.

The browser's **Back** and **Forward** buttons go through the changes made on
the page: each change of a setting, and each day picked (clicked, typed in the
date box, Today, or a new year typed in), is a step of its own. Stepping day
by day with the arrows or keys, and magnifying, only update the current step,
so Back does not crawl through every day passed on the way.

A link is only as reachable as the file: for someone else to open it, the HTML
has to be somewhere they can reach — a church website, a shared drive — with
the part from `#` onward added to that address.

## On a phone

Pinching magnifies about the point between your fingers and carries it with
them, so pinching and moving at once zooms and pans in one gesture, the way a
map does. One finger drags while magnified; a tap picks the day under it. The
page never scrolls, so the wheel claims every touch on it rather than letting
the browser zoom the whole page. The hint line under the wheel switches its
wording for touch screens. On a narrow screen the zoom slider is left out (the
buttons, the menu and pinching still zoom), so **Find a day** and **Week** share
its row; **Week** lists the chosen day's week with its readings, larger than
the wheel's cells can show them.

## In another page

There are two ways to show the wheel inside a page of another website, a
parish's, say.

**An iframe** is the simple one. Once the page is on a website (the project's
own at <https://churchyearwheel.github.io/ChurchYearWheel/>, or a copy of your
own), one line of HTML shows it, in a website builder's "embed" or "custom
HTML" block or in a page's own HTML:

```html
<iframe src="https://churchyearwheel.github.io/ChurchYearWheel/" title="Church year calendar" style="width:100%;height:90vh;border:0" allow="clipboard-write"></iframe>
```

**Copy embed code**, under Share in the settings (All), copies that line for
the page in front of you, with the settings on screen: the church, the
feasts, the Bible and the rest, and the magnification. It leaves the day out,
so the wheel opens on the day it is read. Change `height` to suit the page.
The page inside the frame is the page itself, so it updates when its website
does; there is nothing to copy again.

**A fragment** puts the wheel itself into your page, for those who edit
their site's HTML and want the wheel to be part of the page rather than in a
frame. `--fragment` (in Make a page, *To paste into another page's HTML*)
writes the page without its `<html>`, `<head>` and `<body>`: open the file in
a text editor and paste its contents where the wheel should go. It is about
2 MB, which some website builders' blocks will not take.

```
python church_year.py --fragment -o wheel-fragment.html
```

Everything the wheel brings is scoped to its own box, `.cy-app`: its styles do
not touch the host page's buttons, pictures or scrolling, and it finds its own
drawing rather than the first picture on the page. It then behaves as a guest:

- it keeps to a box one screen tall; give `.cy-app` a height of your own in the
  host's stylesheet to change that;
- the keys work while the wheel has the focus — click it, or Tab to it — rather
  than anywhere on the page;
- rolling the mouse wheel scrolls the page, and Ctrl with the wheel (or a
  trackpad pinch) magnifies; on a phone one finger scrolls the page until the
  wheel is magnified;
- it leaves the page's title and address alone. It still opens on a link's
  `#date=…`, and **Copy link** still gives the host page's address with the
  day added.

### Making a page from the page

**Make a page…** under Share writes such a page without Python: the page
copies itself, as `church_year.py` would build it with the options the
window stands for, and saves it as one HTML file. The window has every one of
the script's options, and each starts as the page is now; *As this page opens*
puts It opens, The wheel and Readings and links back to what the page itself opens with.

| In the window | `church_year.py` |
|---|---|
| Churches it offers: a box for each church, series and hymnal, under its tradition and church, with All, This tradition, This church, Only this one and None to start from | `--churches` |
| It opens on: the church | `--church` |
| The calendars laid over it | `--subcalendar` |
| On the year beginning in Advent | `--year` |
| Zoom | `--zoom` |
| The wheel: Feasts | `--feasts` |
| Latin names: each church's own, off or on | `--latin-names`, `--no-latin-names` |
| Rings | `--hide` |
| Colors: each day color the ticked churches use, for all the churches together, tradition by tradition or church by church (their own shades and the others' as swatches to choose), outside the year, and each ring and its words; or as text | `--color-changes` |
| Text on mid-tone colors | `--mid-text` |
| Thicker line where the year begins | `--year-line`, `--no-year-line` |
| Artwork: the picture the page opens on (the tradition's own, By season, none, a picture the churches have, or one of yours); the churches' pictures kept; pictures of your own, each on a card with a preview in the middle of the wheel, its size, credit, artist or owner, license or copyright notice, links to the license and the source, whether the credit must be shown, the churches it is the own picture of, and Remove | `--art`, `--own-art`, `--drop-art` |
| Readings and links: Readings (the kinds the page carries) | `--readings` |
| Readings shown as: tabs or columns, or both | `--readings-layout` |
| Links: to the Bible and about the feasts, either, or none (without Bible links, the Bible settings leave the window) | `--links` |
| Bible menu: every version, these (languages and versions), or none (each church's own) | `--bible` |
| Bible: each church's own or one version on the Bible menu | `--bible-default` |
| Open in | `--bible-site` |
| Hymn search: on, off or none | `--hymnary` |
| Hymnal: each church's first, or one of those of the churches with several | `--hymnal` |
| Contemporary song search: on, off or none | `--word-to-worship` |
| Settings it shows: Calendar, Easter, Artwork, Dark text on reds | `--show`, `--fixed` |
| Buttons it shows: Download…, Make a page…, Edit the data… | `--no-download`, `--no-make-page`, `--no-edit` |
| Arrow keys go on into the next year | `--arrows-next-year`, `--arrows-same-year` |
| A picture beside the page (center.svg…) | `--local-art` |
| Under the wheel | `--footer` |
| Help link | `--help-link` |
| Feedback link | `--feedback` |
| To paste into another page's HTML | `--fragment` |
| Packed, about a third of the size (on unless this page's own tables are plain) | off: `--no-compress` |
| File name | `-o` |

*The same page from Python* shows the command line for what the window is
set to (leaving out what `config.csv` already says), to keep or to run.
It works the other way too: paste a command into the box below it (one copied
there before, or written for the script) and *Set the window from it* sets
every choice as the script would read it, the options it leaves out as
`config.csv` says. *Save settings…* saves the command as a small text file
(`church_year_settings.txt`, after the page's file name), and *Load
settings…* sets the window from one. The script reads the same file:
`python church_year.py --settings church_year_settings.txt`, with any
options given after it winning. A picture of your own is named in the
command but not carried, so it is chosen again after loading (its card says
so), unless the page already carries it. The
page it makes is the page that command makes, table for table and element for
element (`web/verify_pages.py` checks this), and it can make pages in turn.

It can offer only the churches it has itself: a page made with `--churches`
makes pages from those. `--data` (a folder of CSVs, such as a year made by
`new_year.py`) needs the script. A picture of your own put beside the page
(`center.svg`) is not read from there; choose it as *a picture of your own*
to carry it inside the new page.

### Only your church

A church's own site need not offer every other church. `--churches` (or
`page_churches` in `config.csv`) names the ones to keep, by key, by
tradition, or by a key prefix ending in `*`:

```
python church_year.py --list                              # the keys
python church_year.py --churches lcms-*                   # the LCMS: every hymnal and lectionary
python church_year.py --churches presbyterian
python church_year.py --churches Lutheran,episcopal
```

The page then carries only those churches (and is much smaller: about 510 KB
for one), offers only their artwork, and hides a menu that would have one
choice in it: a page made with `--churches lcms-one-year,lcms-three-year`
shows no Tradition, Church or Hymnal menu, only the Lectionary.

`--fixed` (or `page_fixed` in `config.csv`) also leaves out settings a
church's own site has no use for, keeping each church's own value:
`calendar`, `easter`, `artwork` and `reds` (the Dark text on reds box,
which then stays as config.csv's `mid_text` sets it), separated by spaces or
commas. A link that names one of them is then ignored for it.

`--readings KINDS` (or `page_readings` in `config.csv`) sets which kinds of
set the page carries: `all` (the default), `none`, the kinds to keep
(`--readings day,feasts`) or the kinds to leave out
(`--readings=-daily,-office`, with the `=` since the value starts with a
dash), of `day`, `feasts`, `dated`, `daily`, `additional`, `psalms`, `plan`
and `office`. The readings of the others are not put in the page at all, so
it has no box for them and is smaller: `--readings day` leaves a one-church
LCMS page about 530 KB rather than 740 KB. Make a page's Readings boxes do the
same, and offer only the kinds the page itself carries.

In the page the readings are packed (`export_data.py`: `pack_rows`): each
lectionary's columns, every distinct cell once, and each row as the indexes
of its cells, about a third the size of the rows written out.

The page can open with other settings of the gear's too, each with its
`config.csv` line: `--hide halves,seasons` (`page_hide`) turns rings off,
`--color-changes PURPLE-7a1f7a,ring.gold-c9a227` (`page_colors`, written as a link's
`colors=`) changes colors, and `--bible-site youversion` (`page_bible_site`)
sets where readings open. `--hymnary off` (`page_hymnary`) does the same for the Hymn search box, and `--hymnal CPAM2000` opens every church that has that hymnal among several on it. `--year-line` (`year_line`) opens with the thicker line where the year begins. `--word-to-worship off` (`page_word_to_worship`)
opens with the Contemporary song search box unchecked, and `none` leaves the box
and its marks off the page. And as the other scripts take them, `--church KEY`
(the church it opens on; `lectionary`), `--subcalendar KEY` (repeatable;
`subcalendars`), `--feasts all|festivals|principal|none` (`feast_detail`),
`--latin-names` / `--no-latin-names` (for every church; otherwise each
church's own, then `latin_names`), `--mid-text dark-reds` and the rest
(`mid_text`), and `--bible-default VERSION` (every church opens in it where
the page offers it; otherwise each church's own). As with the readings, Reset settings (and Reset
colors) go back to them, and a link records `hide=` or `colors=` only when
they differ (`hide=none`, `colors=none` for none at all). The rest already
have theirs: the church (`lectionary`), the calendars laid over it
(`subcalendars`), Feasts (`feast_detail`), Dark text on reds (`mid_text`),
Latin names (`latin_names`), Bible (each church's own, within `page_bibles`),
Artwork (`center_svg`), Under the wheel (`page_footer`) and the zoom
(`page_zoom`).

`--help-link URL` (or `page_help` in `config.csv`) puts a **Help** button in
the bottom left corner that opens that page in a new tab. The project's
`config.csv` names the user guide as GitHub shows it, so a copy hosted
anywhere links to it; `--help-link none`, or a blank `page_help`, leaves the
button off, and another address (your own instructions, say) replaces it.

`--feedback URL` (or `page_feedback` in `config.csv`) puts a **Feedback**
link in the bottom left corner that opens that form in a new tab. The day on screen goes
with it: the page's link to it (which reopens the same day, church and
settings), the date and the church, added to the address as `link=`, `date=`
and `church=` (for a Tally form, hidden fields of those names). An address
can instead place them itself with `{link}`, `{date}` and `{church}` (a Google
Forms pre-filled link, say), and a `mailto:` address gets them in the
message. `--feedback none`, or a blank `page_feedback`, leaves the link off.

`--links` (or `page_links`) chooses the page's links: `bible` (each reading
opens in a Bible, and a set's heading opens them all), `feasts` (each
commemoration's name opens a page about it), both (`all`, the default) or
`none`. Without `bible` the readings are plain text and the page has no Bible
or Open in setting; Download's lists then come without links too. The
Word to Worship mark is its own setting (`--word-to-worship none`).

`--no-download`, `--no-make-page` and `--no-edit` (or `page_download`,
`page_make_page` and `page_edit` set to `FALSE` in `config.csv`) leave
**Download…**, **Make a page…** and **Edit the data…** off the page's Share
row, for a site that should offer only the wheel itself. `--download`,
`--make-page` and `--edit` put them back over `config.csv`.

`--local-art` (or `page_local_art` set to `TRUE`) has the page look, as it
opens, for a picture beside it — `center.svg`, then `center.png`, `.jpg`,
`.jpeg`, `.webp` and `.gif` — and offer the first it finds in the middle. It is
off unless asked for: each name it tries and does not find is a "file not
found" in the browser's console, and a page that is not looking asks for no
files at all. `--no-local-art` turns it off over `config.csv`.

`--zoom N` (or `page_zoom` in `config.csv`) makes the page open magnified,
1 (the whole wheel, the default) to 6, centered on the day it opens on. A
link's own `zoom=` wins, the `0` key and Reset zoom still show the whole
wheel, and a link records the zoom only when it differs from the page's own.

The Calendar and Easter settings are left out of every page unless asked for
with `--show` (or `page_show` in `config.csv`): `calendar`, `easter` or both.
Most readers keep their church's own calendar and Easter, and the two menus
mostly invite the wrong one; a page about calendars can still offer them.

```
python church_year.py --churches lcms-one-year,lcms-three-year --fixed artwork,reds
python church_year.py --show calendar,easter
```

`--own-art` freezes a picture of your own into the page — an `.svg`, `.png`,
`.jpg`, `.gif` or `.webp` file, found from the current folder, then the
project folder (a photo as an embedded image, cut to the circle). It is listed
in the **Artwork** menu by its file name, and given more after `|`, each
`NAME=VALUE`:

| | |
|---|---|
| `churches=` | the churches (keys, commas between) it is the own picture of: *The tradition's own* shows it for them instead of theirs. A church has one; the last named wins |
| `credit=` | its title or a line of credit, shown under the wheel as the credit of `artwork.csv`'s pictures is. A picture carries no credit unless given one |
| `author=` | the artist or owner |
| `license=` | a license such as CC BY 4.0, or a copyright notice such as "© 2026 St. Mark's, used by permission" |
| `license-url=`, `source=` | links for the license's name and the credit |
| `attribution=` | `required` (the default): a credit is shown under the wheel, or behind a small (i) when the footer is off; `optional` leaves it to the footer setting |
| `scale=` | its size in the circle: 1 fills it, `0.9` leaves a margin; a picture enlarged past the circle (above 1) is cut to it, off the rings around it |

`--own-art` may be given again for more pictures, each for other churches.
`--drop-art` leaves the churches' own pictures named (keys from
`artwork.csv`, commas between) out of the page; a church whose picture is
dropped has none unless one of yours is its own, and Make a page lists such
churches under the pictures kept.

`--art` (or `center_svg` in `config.csv`) sets the artwork the page opens
on: `auto` (*The tradition's own*: each church's own picture, or the one of
yours given it), `none`, a key, or a picture's file (one `--own-art` named, or
added as one with no credit). Choosing *The tradition's own* on the page always
shows each church's own, whatever the page opened on. `center_svg_credit`
and `center_svg_scale` credit and size a picture `center_svg` names. Make a page
shows each picture of yours on a card: a small preview of it in the middle of
the wheel, the next ring around it (so a picture too large or too small for
the circle shows before the page is made), its credit and size, the churches
it is the own picture of, and **Remove**. The wheel is drawn exactly as
`church_year_image.py --art` draws it (see
[rendering.md](rendering.md#the-picture-in-the-middle)).

```
python church_year.py --own-art "my_cross.png|credit=Photo: J. Smith" --art my_cross.png
python church_year.py --churches lutheran --own-art "seal.png|churches=lcms-one-year,lcms-three-year" --drop-art lutherrose --art auto
python church_year.py --churches presbyterian --art season
```

A photo adds its own size to the page, so a few hundred pixels across is
plenty.

`--bible` (or `page_bibles` in `config.csv`) sets the Bible versions the
**Bible** menu offers, separated by spaces or commas:

- one version (`--bible NKJV`): every reading opens in it, and the menu is left
  out;
- several (`--bible ESV,KJV,EHV`): only those are listed;
- a language (`--bible english`, or `de`, `sv`, `no`, `da`, `fi`, `is`, `hu`,
  `uk`, `pt`): only that language's versions, and languages and versions can
  be mixed (`--bible english,LUTH1545`);
- `own`: each church's own version, and no menu.

A church whose own version is not offered opens in the first one named (ESV
if it is offered, for a language). A link naming a version the page does not
offer is ignored.

```
python church_year.py --churches lcms-three-year --bible ESV,NKJV,KJV,EHV
```

### The lines under the wheel

The panel's **Under the wheel** boxes turn the instructions and notes and the
artwork's credit on and off; with the credit off, artwork whose license
requires credit keeps a small **i** that opens it. `--footer` (or
`page_footer` in `config.csv`) sets where the boxes start:

| Value | Shows |
|---|---|
| `full` (default) | the instructions, the notes and the artwork's credit |
| `credit` | the artwork's credit only |
| `none` | nothing (both boxes off) |

With `none`, artwork whose license requires credit (`attribution` =
`required` in `artwork.csv`; none of the project's own pictures does, but one
you add may) keeps a small
**i** button in the corner that opens its credit, and the credit is still
printed. A church's own emblem (`attribution` = `owner`) is credited to the
church; a church showing its own emblem may leave the credit off entirely. Set
`artwork_credit` to `none` as well to keep it out of a drawing made by
`church_year_image.py`.

A page that holds nothing but the fragment — a host that supplies only the
skeleton — is recognized as the wheel's own, and the wheel fills it, takes the
keyboard and keeps the address up to date exactly as the full page does.

## Printing

Printing (the **Print** button, or the browser's own Print) gives the whole
wheel on one page with its heading above it: the right way up as drawn in the
SVG, at 1x whatever the magnification on screen, without the highlight or the
controls, and in color — the page asks the browser to keep background colors,
which most otherwise drop. Landscape or portrait both work, on Letter or A4;
the wheel fits the shorter side. The artwork's credit is printed beneath the
wheel. For a large print or a poster, the PNG from `church_year_image.py` is
the better source; it carries the credit in its lower-left corner when the
artwork's license asks for one (`artwork_credit`).

## Editing the data

**Edit the data…** (under Share) changes the tables the page draws from, the
rows of the files in `data/`, and shows the change on the wheel at once:

- **This day:** the names and colors of what falls on the chosen day (a feast's
  name, full name, link and color; a Sunday's name, which for a run of days is
  its pattern, `{ordinal} Sunday in Advent`), a feast of your own on the
  date, and the day's readings set by set: a reading's kind and text changed,
  a reading removed or added, and a set of readings of your own on the date.
  A reading's kind is one the church has or a new one: its key (`tract`) and
  the name the page gives it (Tract), kept in `reading_labels`.
- **Kinds of reading:** the names the church gives its kinds of reading and
  the order a set lists them in (`reading_labels` and `reading_order` in its
  `tradition.csv`).
- **Seasons:** the seasons' colors (`seasons.csv`) and the colors of periods
  that have their own (`periods.csv`).
- **Colors:** what each color looks like, its fill and its text, for the
  tradition (its own `colors.csv`, started if it has none) or every church
  (`data/colors.csv`), and new colors.
- **Changes:** what has changed, file by file, each undone on its own or all
  at once.

Each change names the file it is in, and says when that file is read by more
churches than the one on screen (a shared lectionary such as
`readings/lsb.csv`, or a folder of several churches): the change is theirs too.

The changes are kept in the browser, for the page where it is (moved or
renamed, it starts again without them), and **Make a page…** writes them into
the page it makes, whose tables then have them for good (it can be edited and
made again in turn). **Download changed files** gives a `.zip` of the files the
changes make, laid out as the project's `data` folder: put its `data` folder
over the project's own and `church_year_image.py`, the listing scripts and
`church_year.py` read the changes as if the files had been edited by hand.
A file is written back as it was, comments, blank lines and spelling and all,
with only the changed rows written anew, so a comparison of the two shows just
the changes. A page made from one with changes keeps the list of files it
changed, and downloads those files too.

A page made with `--churches` or `--readings` carries only some of a
lectionary's rows; their files cannot be written back from it, and the editor
says so: edit those on a page with the whole file. `web/verify_edits.py`
checks that every file comes back unchanged, and that a page with changes of
every kind, made in the browser, is the page `church_year.py` makes from
the files it downloads.

## Text on mid-tone colors

Some colors -- the LCMS red, green and blue, the Roman red and violet -- read
about as well with black text as with white (both reach 3:1). The panel's
**Dark text on reds** box puts black on the reds among them (the LCMS, Roman
and Presbyterian reds) and leaves the rest as each church's `colors.csv` set
them. `mid_text` in `config.csv` makes a choice the default, for the page and
for drawings made by `church_year_image.py`: `as-set`, `dark-reds`, or `dark` or
`light` for every mid-tone color (`church_year_image.py --mid-text` for one
drawing). `tools/check_contrast.py` lists the colors
whose set text is not the more readable of the two.

## Which rings to draw

`rings.csv` says what rings exist and its `enabled` column switches them off for
good. The interactive page adds a **Rings** menu that turns them on and off as
you look, without touching the file — useful for seeing the wheel stripped back
to its day cells. The menu lists the rings as they lie on the wheel, outermost
first. The day cells and the artwork in the middle are listed but
cannot be switched off; they are the drawing rather than decoration.
`church_year_image.py --hide halves --hide seasons` draws the same wheel as the page
with those rings off (`hide=halves,seasons`).

Either way, **a ring that is off leaves no gap**. Everything outside it slides
inward to close the space, and what is left is stretched back out to fill the
room — so turning a ring off gives its space to the rings that remain rather
than shrinking the drawing.

Two kinds of ring are held at their own size rather than stretched, because
stretching them would read as the thing itself having changed:

- the **artwork in the middle**, which is a drawing and not a band. Grow it and
  the picture looks bigger, and whatever used to touch it stands off at a
  distance.
- a plain **`band`**, which is usually a border. Grow it and the wheel looks to
  have gained a much heavier rim — dropping both the halves and the seasons
  would otherwise have taken the gold band from 40 units thick to 47.

So the rings that move are the ones between those fixed pieces, and each such
stretch is closed on its own. Dropping the month ring leaves the center at 330
and brings the day cells in to meet it, 380-900 becoming 330-891.3, with the
gold band untouched at 1010-1050. Dropping the halves and the seasons together
runs the day cells all the way out to the band, 389.6-1010.

A band that is itself switched off stops being fixed, and its room is shared out
like any other gap — so the wheel does grow into the rim when the rim is the
thing you dropped. With every ring on none of this changes anything, which is
what keeps the ordinary output identical.

A ring's `inner_border` is drawn wholly inside it, rather than as a stroke
straddling its inner edge. A straddling stroke lays half its width over
whatever is inside the ring, and that half survives or not depending on whether
a later ring happens to paint over it — so the gold band's black border looked
twice as thick the moment the ring below it was switched off, without anything
having moved. Inside the band it is the same thickness whatever its neighbors
do, and `inner_border_width` is simply what you see: it reads `7.5` where it
used to read `15`, for the same drawing.

## Changing the colors

**Colors…**, under the Rings, opens a list of the colors on the wheel this
year: each color the days are painted in (the tradition's palette, only those
the year uses, the lower halves included), the cells outside the year, and
each ring's fill and, where the ring is labeled, its words.  Clicking a swatch
picks a new color and the wheel is redrawn with it.  A day's text keeps its
color while it still reads at 4.5:1 on the new fill; otherwise it turns black
or white, whichever reads better.  The changes belong to this page: they are
written into its link (`colors=`), so a copied link carries them, and Reset
colors or Reset settings puts them back.  They do not change the data files;
`church_year_image.py --color-changes` draws the same repainted wheel from Python
(`web/verify.py --color-changes` checks the two agree), and to change a color
for good, edit `colors.csv` (or a tradition's own) and `rings.csv`.

A day color can be changed for every church (`PURPLE-7a1f7a`), for one
tradition (`lutheran:PURPLE-7a1f7a`: the tradition's name in lower case, its
spaces as hyphens, `church-of-the-east`) or for one church
(`lutheran:wels-one-year:PURPLE-7a1f7a`: its tradition, then its key). The
nearer change wins: a church's over its tradition's, a tradition's over every
church's. The Colors window changes the color where this church's is already
changed (its own, its tradition's, or else every church's). Make a page's
color list sets any of them: *Change them* for all the churches together,
tradition by tradition, or church by church, each color with its own shades
and every other church's on the page to choose from.

## Reading a cell close up

The wheel holds 364 cells, so at a whole-wheel view the commemorations are
small. Magnification runs from 1x to 6x — enough that a cell fills a good part
of the screen and its text reads at a glance.

**What it is anchored on depends on how you ask**, which is the part worth
knowing:

- **Rolling the mouse** magnifies about the cursor and pins whatever is under
  it, the way a map behaves. Measured drift over six notches, from 1x to 2.7x,
  at three different places on the wheel: **zero**.
- **Pinching** on a touch screen does the same about the point between your
  fingers, and moving the fingers pans at the same time.
- **A trackpad** sends wheel events too, but many small ones a second (with
  momentum after the fingers lift) and in both axes. A two-finger swipe pans
  the magnified wheel; a pinch (a wheel event with Ctrl held in Chrome, Edge
  and Firefox, gesture events in Safari) magnifies in step with the fingers.
  The wheel's movement is measured rather than counted (a mouse notch of 100
  pixels is still one 18 per cent step), gathered and applied once a frame
  without the easing, and settled on the nearest 0.05 when the gesture stops.
- **The slider and the `+` / `-` keys** magnify about the chosen day instead,
  since that is the thing you asked to look at. The wheel has already turned it
  to the top, so it sits on the vertical line above the center at whichever
  radius its band occupies; the point is drawn in toward the middle of the
  view as magnification rises, arriving smoothly rather than jumping.
- **Picking a day** — by click, arrow key or the date box — brings it into view
  at whatever magnification is set.

The drawing surface fills the whole stage, not just the square the wheel
occupies. At 1x that makes no visible difference — the circle is fitted inside
and centered, letterboxed by whatever the window's shape leaves over — but once
magnified the drawing spreads into that margin rather than being cut off at the
edge of a square. On a 1920-wide window the surface is 1888 x 961 where the
wheel itself is 961 across, so roughly twice the area is in use when zoomed.

Dragging pans, but only once the pointer has moved four pixels: a press that
stays put is still a click, and clicking still picks the day underneath.
Panning is bounded so that whatever sits at the middle of the view is always
somewhere on the drawing, which makes it hard to get lost. `0` returns to the
whole wheel.

Clicking keeps working at every magnification and after panning — checked by
computing where a given day's cell ought to be on screen, clicking exactly
there, and confirming the page selects that day: 23 cells at 1x, 2.5x, 4x and
6x, all exact, plus a click after a drag.

## How big the wheel is drawn

The page is exactly one screen tall, and the wheel takes whatever the header
and the hint line leave behind — so the whole circle is visible without
scrolling, maximized or not.

That is worth saying because the obvious way to size it is wrong. Sizing the
wheel from the viewport directly, as `92vmin`, measures the window and ignores
the header sitting above it, so the bottom of the wheel falls off the screen by
however tall the header happens to be. It cost 100 to 230 pixels at every
desktop size, and more when the controls wrapped onto a second row.

Instead the page is a flex column: header, wheel, hint. The wheel is given an
intrinsic size in the markup and scaled down like an image to fit both the
width and the height it is allowed, keeping its square. On a window under about
620 pixels tall the instruction line hides itself, since it costs more than it
is worth there.

Roughly what you get:

| window | wheel |
| --- | --- |
| 1920 x 1080 | 961 px |
| 1440 x 900 | 737 px |
| 1280 x 800 | 637 px |
| 900 x 650 | 491 px |

## What "Today" means

The browser's own local date — `getFullYear`, `getMonth`, `getDate`, which are
the local getters, not the UTC ones. Nothing in the page reads UTC for this.
(The one UTC in the file is in the date wording, where a proxy date is built and
formatted in UTC so that the label cannot be dragged across a day boundary by
the reader's time zone. It is display only.)

Tested against a fixed clock: at 11 pm on a Sunday in New York, the page
opens on that Sunday and stays on it when Today is pressed.

If the page disagrees with the clock on your wall, the machine's date is not
the one you are reading. The two usual causes are a remote or virtual session,
which takes its time zone from the host rather than from the machine in front
of you, and a browser set to report UTC to scripts — Firefox does exactly that
under `privacy.resistFingerprinting`, and several privacy extensions do too.

The Today button's tooltip names the day it will go to, so you can hover it and
see at once whether the browser agrees with you.

## What is inside

```
web/church_year.js     the renderer, ported from church_year_image.py
web/page.js            the controls, rotation, highlight, zoom and links
web/style.css          the page's own styling, print layout included
web/data.json          the frozen tables (font metrics, colors, rings, ...)
web/export_data.py     rebuilds data.json from ./data
web/verify.py          checks the port against church_year_image.py
web/verify_bc.py       checks the years datetime.date cannot reach
web/verify_readings.py checks the page's readings against lectionary.py
web/verify_links.py    checks the page's Bible and feast links against lib/links.py
web/listings.js        the Download window's lists, ported from lectionary.py, colors.py and feasts.py
web/verify_lists.py    checks those lists against the scripts, byte for byte
web/verify_pages.py    checks Make a page against church_year.py (needs Playwright)
web/proleptic.py       the calendar arithmetic in plain integers, for tests
web/render_one.js      draws one year under Node, for verify.py
web/dates_one.js       lists one span's dates under Node, for verify_bc.py
```

In the page the tables are packed — gzip, then base64 — which makes them
about a fifth of their size (the page is about 2 MB rather than 6); the page
unpacks them as it opens, which any browser from 2023 on can do.
`--no-compress` writes them as plain JSON instead, for reading the page's
source or for an older browser. **Make a page** does the same with its
**Packed** box: on, the new page's tables are packed; off, they are plain
(`--no-compress`). It starts as this page's own are.

Everything that does not depend on the year — the font metrics, the parsed
settings, the colors, styles, rings and commemorations, the artwork for the
middle — is frozen into `web/data.json` by `web/export_data.py`, which reads
it through `church_year_image.py`'s own loaders. You do not normally run it yourself:
`church_year.py` and `web/verify.py` rebuild `data.json` whenever it is
missing or older than any CSV under `data/`, any SVG in `artwork/` (or the
picture of your own `center_svg` names), `church_year_image.py`, `lib/traditions.py`
or the exporter. `python web/export_data.py` does it by hand.

Given `--data` pointing at a folder of CSVs instead — a year made by
`new_year.py`, say — `church_year.py` builds the tables straight from that
folder, so its lectionary, calendar and colors reach the page without touching
`web/data.json`. That is what `new_year.py --draw` does.

The dates are not frozen: the browser works them out itself, computus and all,
which is what lets it draw a year nobody has generated CSVs for.

## Keeping the two renderers honest

A second implementation of the same drawing can drift from the first — a fix
made in `church_year_image.py` and not in `web/church_year.js` gives a calendar that
is wrong only in the browser, and only for some years. So they are checked
against each other:

```
python web/verify.py                      # 20 years, both LCMS series
python web/verify.py --from 1990 --to 2075
python web/verify.py --lectionary lcms-one-year --latin-names
python web/verify.py --lectionary all     # every tradition
python web/verify.py --lectionary roman --subcalendar each   # every Roman calendar in turn
python web/verify.py --calendar all       # every calendar and paschalion pair
python web/verify.py --keep /tmp/drift    # save any pair that disagreed
python web/verify.py -j 1                 # one year at a time
```

Each year is drawn both ways and the markup compared, as many years at once
as the computer has processors (`-j`), each with one Node process that reads
the tables once (`web/render_one.js --serve`). The two are expected to
match **byte for byte** — the JavaScript reproduces Python's number formatting
deliberately, down to rounding a value that lands exactly halfway to the nearer
even digit, which is what Python does and `toFixed` does not. Anything less
than an exact match is reported.

As it stands, 1990 through 2075 agree exactly: 172 years across both
lectionaries, plus 86 more with the Latin names on, and 192 more sweeping all
six calendar-and-paschalion pairings. Run it after changing
either renderer. It needs Node; nothing else.

The page's links are kept the same way. `lectionary.py` and `feasts.py` make
the links the readout makes, through `lib/links.py`, a port of `page.js`'s
`plainCitation`, `bibleUrl`, `readingLinks`, `feastUrl` and `bibleDefault`.
`web/verify_links.py` takes those functions out of `page.js` as they stand,
runs them under Node over every reading and feast name in the data, for both
sites and several Bible versions, and compares them with the Python. Run it
after changing either.

```
python web/verify_links.py                # every church
python web/verify_links.py --church elca  # one
```

**Make a page** is checked against `church_year.py` by
`web/verify_pages.py`, which makes pages in a browser (Playwright, under
Node), builds the same pages with the script, and compares their tables as
data and their markup as the browser reads it. A made page is made again from
itself and compared too.

```
python web/verify_pages.py
```

## Caveats

Tested in headless Chromium only. It uses `transform-box: view-box`,
`replaceChildren`, `DOMParser` and `adoptNode` — all current across Chrome,
Edge, Firefox and Safari, but not in Internet Explorer or a browser more than a
few years old. Links need nothing more; the Copy link button uses the
clipboard API where it can and falls back to the older copy command where it
cannot.

Drawing a year takes about 50 ms on a laptop and perhaps three times that on an
older phone — quick enough to feel immediate, but it is real work, not a
pre-drawn picture being shown.
