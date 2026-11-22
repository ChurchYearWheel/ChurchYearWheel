# Changelog

## 2026-11 (138) — the page is church_year.py; published by GitHub Pages

### Added

- **The page in the reader's language.** Its buttons, menus, settings and
  their notes come in 18 languages besides English (`data/ui/<code>.csv`):
  the browser's first language the page has, unless Settings > Language
  chooses another or *Match the church* (the church's language, changing
  with the church). The calendar's own names, dates and readings stay in the
  church's language; an English calendar's dates follow the page's language.
  Make a page, Edit the data and the Download window are translated too, and
  the lists it downloads as HTML, Markdown and iCalendar take the page's
  language for their headings, notes, column names and dates (CSV and JSON
  keep their English field names; in English every list is still the
  scripts' own). Make a page has a Language choice (`--language`,
  `page_language` in config.csv): the browser's, the church's or one
  language, until the reader picks another. The keys (T, F, W ...) are the
  same in every language.
- **The User Guide in the same 18 languages** (`docs/user-guide.<code>.md`),
  its settings and buttons named as the page names them in each; the English
  guide stays the reference and links to them. Help opens the guide in the
  page's language when there is one (`guides` in data.json), otherwise the
  English one. The guide now says where T, F and W come from.
- **Readings in the church's language.** The page's readings say
  "Readings", each kind ("Epistle", "Gospel", Hungary's "Prophecy" ...) and
  the "or" between choices in the church's language ("Čítania: Žalm 110
  alebo Žalm 47 · Epištola ..."; `reading_...` in `data/languages/`).
  Verses after a chapter in parentheses now take the church's mark too
  ("Lukas 11,(1–4) 5–13").
- **Months, dates and Bible books in each church's language.** A church's
  `language` (tradition.csv; files in `data/languages/`) puts the wheel's
  month ring and dates in it ("29 de noviembre de 2026", "2026. november
  29.", "29 листопада 2026 р."), the page's date line too, and the Bible book
  names in the page's readings ("Römer 13,11–14", "Mateo 21:1–9"). Set for the
  25 churches whose calendars are not in English, in 18 languages; the book
  names for the 15 whose churches have readings. The readings stay in English
  in the data, so the links, verse numbering and searches are unchanged; the
  printed lists (lectionary.py and the page's Lists) are still in English.
- **The header's color words** in the church's language too ("Adviento ·
  morado", "Semana Santa · blanco (o escarlata o violeta)"): `color_...` and
  `or` in each language file. Settings → Colors still names them in English.
  The words follow the churches' documents where found: Swedish and Norwegian
  in the neuter their churches use ("vitt", "hvitt", "gyllent"), Danish
  "gylden", German as capitalized nouns ("Violett"); a church's own words go
  in its new `color_labels` setting (the IEAB's "azul escuro").
- **Colors from church documents.** The IEAB's Advent is violet or dark blue,
  and its Good Friday black or red, from the IEAB's *Calendário Eclesiástico*
  (2025) (Good Friday was no color, uncited). The Church of Norway's Good
  Friday adds black as the alternative to violet, as its 2010 color rule
  allows.
- **The Iglesia Evangélica Luterana en España (IELE)**, Lutheran → IELE: the
  one-year series of Lutheran Service Book in Spanish, from the IELE's
  *Calendario Litúrgico de la Iglesia, Serie Anual* (2025–26). Spanish day,
  feast and reading names, the Latin Sunday names, and the calendar's colors
  (rose Gaudete, white Holy Saturday, red Pentecost Monday and Tuesday). The
  readings and propers are LSB's, which the calendar matches set for set; LSB's
  daily lectionary is left out. The Bible menu adds the **Reina-Valera 1995**
  (Spanish), the IELE's own.

### Changed

- **The scripts are renamed**, now that the web page is what most people use:
  `church_year.py` builds the web page (it was `church_year_web.py`), and
  `church_year_image.py` draws the wheel as an SVG and PNG (it was
  `church_year.py`). Their options are unchanged. A command or settings file
  that names `church_year_web.py` still reads back into Make a page and
  `--settings`.
- **The README** opens with a picture of the page and three paths: *Using
  the calendar* (the live page and the user guide, with links to its
  sections), *Running it yourself* (the scripts) and *Changing or adding a
  church* (the documentation and the checks).

### Added

- **`.github/workflows/pages.yml`** builds the page and publishes it with
  GitHub Pages on every push to `main`, after checking that the browser's
  drawing still matches the Python one. Turn it on under Settings → Pages →
  Source: GitHub Actions.
- **A Help button** beside Feedback, in the wheel's bottom left corner, opens
  the user guide on GitHub in a new tab. `--help-link URL` (`config.csv`:
  `page_help`) points it elsewhere, and `none` leaves it off; Make a page has
  a *Help link* field for it.
- **The page opens magnified 3×** on the day it opens on (`config.csv`:
  `page_zoom,3`); `--zoom 1` or `zoom=1` in a link shows the whole wheel.
- **Copy embed code**, under Share in the settings (All view), copies one line
  of HTML, an iframe, that shows the page inside a page of another website,
  with the settings on screen, opening on the day it is read. The user guide
  (*Showing the wheel on your own website*) and docs/web-page.md (*In another
  page*) explain it beside the fragment, whose Make a page box is now *To
  paste into another page's HTML*, with a note saying what the file is for.
- **LSB's psalm table: the General weeks begin again at Week 1** in each
  season that uses them, where they had been counted on from Advent: in
  Epiphany the week of 7 January is Week 1, and after Pentecost Holy Trinity
  begins Week 1. So Holy Trinity 2026 has Week 1's Psalm 103, and the weeks
  after it follow on. The data's note on the Easter table now says it runs to
  the Saturday after Pentecost, as the data has it.
- **The README is titled *Church Year Wheel*.**
- **Leftovers dropped before publishing:** `tools/history/`, the one-off
  scripts that first built the data folders (the notes that pointed to them
  now say so); and the scripts and sources for the pictures kept for private
  use moved into `artwork/church-emblems/`, which is not published.
- **README:** the count of Anglican books was wrong ("Seventeen"); it now
  names fourteen other Anglican prayer books besides the Episcopal Church's,
  and the two calendars from books of the same tradition (*Divine Worship* and
  the Western Rite Orthodox book). It and the user guide say the page opens
  magnified on today, and that `0` shows the whole wheel.
- **The calendar feeds carry the project's name:** `PRODID:-//Church Year
  Wheel//…//EN`, and every event's UID ends `@churchyearwheel`, the same for
  the colors, the feasts and the readings, from Python and from the page
  (they were `church-year-calendar`, and `church-year` for the readings).
- **The Pages workflow uses the actions' Node 24 versions** (checkout v6,
  configure-pages v6, upload-pages-artifact v5, deploy-pages v5), so GitHub no
  longer warns that Node.js 20 is deprecated.
- **The gold band round the center pictures** now has its black lines at its
  edges: the outer line lies at the very edge of the picture, where a thin
  sliver of gold showed beyond it under the month ring, and both lines are
  drawn over the picture so nothing inside reaches across them.
- `.gitignore` leaves out what is built: `church_year.html`, `web/data.json`
  and the workflow's `_site/`.

### Fixed

- **T, F and W on any keyboard.** On a layout that types another alphabet
  there (Cyrillic, Greek ...), the key in their place works.
- README: the churches of Slovakia, Hungary and Spain are no longer joined
  with "and" to the HKBP and GKLI.

## 2026-11 (137) — 2026-27 the scripts' year; the seasons' pictures last

### Changed

- **The scripts' year is 2026-27** (`new_year.py 2026 --out data --force`):
  the dated files under `data/` (`sundays_seasons.csv`, `season_periods.csv`,
  `broad_seasons.csv`, `halves.csv`, `year_feasts.csv`) and `config.csv`'s
  `church_year_start` (2026-11-29), `church_year_end` (2027-11-27) and
  `output_filename`. `church_year.py` with no year now draws
  `church_year_2026-27_calendar.svg`, which replaces the 2025-26 drawing. The
  web page needed nothing: it opens on the church year of the day it is opened.
- **Artwork** (Settings, and Make a page's menu and *Pictures kept*): the
  pictures A to Z, then the seasons' own pictures at the foot in the order of
  the church year, Advent's four wreaths to Pentecost's dove, as
  `season_art.csv` first names them.
- "Church year" is never hyphenated: the README's title (*Circular church
  year calendar*), the user guide's, and the footer of the Download lists
  (*... from the church year calendar's data*).

## 2026-11 (136) — Simple settings; repainting from Python; artwork ready to publish

### Added

- **A license.** The code is under MIT No Attribution (`LICENSE`) and the
  data, artwork and documentation under CC0 1.0 (`LICENSE-CC0.txt`): free for
  any use, no credit needed. The README's License section says so, and that the
  lectionaries and calendars remain their publishers'.

- **Arrow keys go on into the next year**, a box in Settings (All). Checked,
  the arrow keys (a day, a week, or with Shift a month) draw the next year's
  wheel at the end of the church year, or the last; unchecked, as the page
  opens, they go round the year on the wheel as before. A page is built
  either way with `--arrows-next-year` or `--arrows-same-year` (`config.csv`:
  `page_arrows_next_year`), which Make a page offers too, and a link carries
  a reader's choice as `arrows=1`.

- **Settings: Simple or All.** The panel opens on the handful of settings most
  often changed (year, church, feasts, Bible, how the readings are shown,
  Copy link, Print, Download); **All** shows the rest under headings (Calendar
  and names, Readings, The wheel, Under the wheel, Rings). The choice is kept
  in the browser. Nothing was removed.
- **Artwork: By season.** An Artwork choice, off unless chosen, that changes
  the picture in the middle with the day: the wreath in Advent (a candle more
  lit each week: `season_art.csv`'s `week` column), the manger at
  Christmas, the star and crowns in Epiphany, the cross and thorns in Lent,
  three crosses in Holy Week, the empty tomb at Easter, the dove at Pentecost,
  and the church's own picture in the seasons that have none. Ten new
  pictures (CC0, `tools/make_emblems.py`); `data/season_art.csv` says which
  season shows which, for every church or for one. **Make a page** offers it
  as the picture a page opens on (`church_year_web.py --art season`), and a
  link carries it (`art=season`). A wheel saved from the page holds the
  season's picture of the day chosen; `church_year.py --art-date 2026-12-25`
  draws the same from Python, and without a date the church's own stays.
  `web/verify.py --art-date` checks the two renderers agree.
- `church_year.py --color-changes`: the wheel repainted from Python exactly as
  the page's Colors menu repaints it (the same words a link's `colors=`
  carries). `web/verify.py --color-changes` checks the two renderers agree.
- `church_year.py --png-background`, as the page's Download offers.
- **A full set of center artwork drawn for the project**
  (`tools/make_emblems.py`), each filling the middle with color like a
  stained-glass roundel in a gold ring: a new Luther rose (a double rose with
  pointed petals, offered beside the Commons drawing), a Chi-Rho, a Celtic
  cross on a hill, a Canterbury cross, the burning bush, a Moravian star,
  and the chalice and host (the Roman and Ambrosian calendars; the IHS
  roundel is gone). The Orthodox, Armenian, Syriac, Coptic and
  Ethiopian crosses are set in gold on sunbursts of their own colors.

### Changed

- **The Luther rose is the project's own drawing.** The rose drawn for this
  project (`artwork/Luther_Rose.svg`, CC0) took the place of the one from
  Wikimedia Commons as every Lutheran church's picture, under the same key,
  `lutherrose`, so links, settings and pages already made keep working. The
  Commons file and the separate `luther_rose` choice are gone. With it went
  the only default picture whose license asked for credit and share-alike.
- **The last picture whose license asked for credit is set aside**
  (`artwork/church-emblems/`, not published). Every picture the project
  publishes is now its own (CC0) or in the public domain, and none needs a
  credit.
- **The readings list has no scroll bar** while it is closed. A set with a
  Propers line was a pixel or two taller than its two lines (the small space
  the line stands off by), so some browsers drew a scroll bar beside it, as
  on Christmas Day; the list now allows for that space.
- **Three season pictures redrawn in part.** Lent's crown of thorns is two
  briars wound over and under one another with thorns of uneven length and
  lean, where it was a ring of even teeth; Christmas has a sky of scattered
  stars of several sizes; and Epiphany's three crowns stand apart.
- **Advent's candles stand round the wreath**, where they stood in a row
  across the middle: one at each side and two at the back, evenly apart, lit
  round the back from the left. The wreath has berries at the back as well.
- A credit for a picture drawn for this project reads "Luther rose, drawn for
  this project", not "by drawn for this project".
- **Pentecost's dove** was redrawn from a wider look at doves in church
  windows: a fanned tail, the body's sides shown over the wings, a rounder
  head, and wings that hang low and round, rise to one point leaning in, and
  come back to the shoulder in feathers.

- **Church emblems are no longer published.** They moved to
  `artwork/church-emblems/` (ignored by git) and out of `data/artwork.csv`;
  their churches' wheels carry
  the project's own roundels or the Luther rose. The Reformed churches open on
  the burning bush. The page is about
  215 KB smaller.
- **Readings in columns, opened:** both columns read from the left, a set's
  later lines hang in under its name, and "less" sits at the foot on the
  right (it sat in the middle of the bar).
- The **Slide** setting shows only while the readings are in columns.

### Fixed

- **LSB one-year: Christmas Midnight is on 24 December**, when the service
  begins, as the three-year series already had it (it was listed on the 25th).
- **Zooming all the way out no longer jumps.** With the wheel pushed to one
  side, a pinch or the mouse wheel held its place down to the last step and
  then snapped to the middle. The view is now drawn back to the middle as the
  wheel shrinks (page.js: clampPan).
- **Settings on a phone:** the panel was as wide as its row of Share buttons,
  so every menu ran off the right side of the screen. The buttons wrap and
  the panel keeps to the screen.
- **Dark theme:** the date box's calendar mark, the menus and the scroll bars
  follow it (`color-scheme`).
- Resizing the window lays the readings out once a frame, not once an event.

## 2026-11 (135) — Ambrosian saints on the wheel; a quieter page

### Added

- **Ambrosian Rite:** the 26 saints' feasts that have readings of their own
  (the Apostles and Evangelists, St Lawrence, St Mary Magdalene, St Benedict,
  St Martin, Sant'Anatalo and the rest) are on the wheel, in the lower half of
  their cell: red for the apostles, evangelists and martyrs, white for the
  others, as GCatholic's Common Ambrosian Calendar gives them. A Sunday, the
  Ascension, Corpus Domini, Holy Week and the Easter octave take the day
  instead, and their readings go with them. 16 December's commemoration is
  named on weekdays too.
- `--local-art` (`page_local_art`, and a box in **Make a page**): the page
  looks for a picture beside it (`center.svg` ...) only when asked.

### Changed

- **A page no longer looks for `center.svg` beside it unless it was made to**
  (`--local-art`), so opening it logs no "file not found" in the browser's
  console. A page that should offer a picture beside it is made with the box
  ticked or with `page_local_art` set to `TRUE`.

## 2026-11 (134) — Printing the week

### Added

- **Week → Print:** the week by itself on paper: the church and year, the
  week, then each day with its full date, its names, color and season, and its
  readings (the kinds the Readings boxes show), the links printed as plain
  text and the hymn and song marks left off. A day is never split between two
  pages. The Week window opens again after printing.

### Fixed

- **Ambrosian Rite:** in a year whose fifth week of Advent runs past 16
  December (2026: 14–19 December), its weekdays from the 17th listed that
  week's readings as well as the ferie prenatalizie, which replace them.

## 2026-11 (133) — Plain tables from Make a page

### Added

- **Make a page:** a **Packed** box. Off, the page it makes carries its tables
  as plain JSON (`--no-compress`), about three times the size, for reading
  the page's source or for a browser older than 2023. It starts as the page's
  own tables are, and the command and saved settings carry it.

## 2026-11 (132) — Find a day, the Week list, a smaller page

### Added

- **Find a day** in the bar (or `F`): type a Sunday's, a season's or a feast's
  name, or part of it, and pick the day; the wheel goes to it in the year it
  shows. Case and accents do not matter; names beginning with what you typed
  come first.
- **Week** (or `W`): the chosen day's week in a list, each day with its names,
  color, season and readings (with their links and marks), a week at a time.
  On a phone, where the wheel's cells are small, it is the easy way to read
  them. On a narrow screen the zoom slider gives up its place to these two
  (the buttons, the menu and pinching still zoom).

### Changed

- **The page is about a third of the size** (about 2 MB rather than 6): its
  tables are packed (gzip, then base64) and unpacked as it opens. A page made
  with **Make a page** is packed the same way. `church_year_web.py
  --no-compress` writes them as plain JSON. The page needs a browser from
  2023 or later to unpack them.

### Fixed

- The table of keys in the user guide was broken in two by a paragraph.

## 2026-11 (131) — A review

### Fixed

- **Feast links:** 26 saints' days in the Anglican, Episcopal, ELCA, RCL World
  and Ukrainian Lutheran feasts had a Wikipedia address with a comma in it
  written unquoted, so the link stopped at the comma (St Richard of
  Chichester opened the page on *Richard*). The addresses are quoted.
- `docs/provenance.md` is written again from the CSV (v202 left the Ambrosian
  readings out of it).
- A doubled space in a Morning Prayer psalm (*Psalms 3 (4), 5*).
- American spelling in the comments and tools (toward, center, gray).
- Code no longer used is gone: an unused import, variables and a function
  (`new_year.principal_days`), and a helper defined twice in two tracing
  tools.

### Changed

- `web/verify.py` draws several years at once (`-j`, one per processor by
  default), each with a Node process that reads the tables once
  (`web/render_one.js --serve`): the full check of every tradition takes
  a fraction of the time it did.

## 2026-11 (130) — The Ambrosian readings

### Added

- **Ambrosian Rite:** the readings of the *Lezionario Ambrosiano*, from the
  Archdiocese of Milan's Ordo of its three books: Sundays and feasts in the
  three years A, B, C, every weekday in the two years I and II, the Sunday
  Gospel of the Resurrection, Lent's vigil readings and the Christmas vigil,
  with the Canto al Vangelo listed with the propers. The saints' days and
  feasts kept by the date (40 days) from the Archdiocese's readings of each
  day. Checked against those daily readings from 2012 to 2026.

### Fixed

- **Ambrosian Rite:** when 29 August is a Sunday it is the Sunday before the
  Martyrdom (2021: the Sundays after the Martyrdom were counted one too many).

## 2026-11 (129) — The propers apart from the readings

### Changed

- **LCMS and LCC:** the Introit, Gradual and Verse come on a line of their own
  after each set's readings, headed **Propers**, which opens them together at
  Bible Gateway; the set's own heading (**Readings**) opens only the
  readings, the page a lector prints. Each line has its own Hymn search and
  song search marks. A **Propers** box in Settings (and
  `propers=0` in a link) leaves them out, of Download's lists too.
- **Readings lists** (`lectionary.py`, Download): the propers listed after each
  set's readings under *Propers*, with a link of their own; `--no-propers`
  leaves them out. A set without a title of its own is headed *Readings*
  (before, *Propers*).

### Added

- `reading_propers` in `tradition.csv`: the kinds a church lists as parts of
  the service rather than readings.

## 2026-11 (128) — Edit the data on the page

### Added

- **Edit the data…** (under Share): change the chosen day's names, colors
  and readings, add a feast or a set of readings on a date, add a new kind of
  reading with its name, rename and reorder the kinds of reading, and change
  the season colors and what each color looks like. The wheel shows each
  change at once; the changes are kept in the browser, undone file by file or
  all at once, and written into a page Make a page makes.
- **Download changed files:** a `.zip` of the data files the changes make,
  in the project's `data` layout, for `church_year.py` and the other scripts.
  Each file comes back as it was but for the rows changed, comments and all.
- `church_year_web.py --no-edit` / `--edit` and `page_edit` in `config.csv`;
  Make a page's Edit the data… box.
- `web/verify_edits.py`: every file written back unchanged, and a page with
  changes the same as the page the scripts make from the downloaded files.

### Changed

- **LCMS and LCC:** each set lists the Introit first and the Gradual and Verse
  between the Epistle and the Gospel, as the Divine Service has them (before,
  after the Gospel).

## 2026-11 (127) — Pictures of your own for chosen churches; LSB introits

### Added

- **LCMS and LCC (Lutheran Service Book): Introit, Gradual and Verse** for
  the Sundays and festivals of the three-year series and the one-year
  series, from the LSB Altar Book's Propers of the Day (about 390
  citations, the introits with their antiphons' sources). Days whose
  citations the photographs did not show clearly have none yet.
- **Hymns the Altar Book names** in its rites: at the imposition of ashes
  (419), the procession with palms (442), before the Passion (440), on Good
  Friday (440, 450, and Tenebrae's office hymns), and the Vigil of Easter's
  canticles, as hymn marks on those days.

- **Make a page: more than one picture of your own.** Each picture added has
  its own card (preview, size, credit, license, Remove) and a list of the
  page's churches, tradition by tradition, to make it their own picture:
  *The tradition's own* then shows it for them. Another picture can be added
  for other churches; a church has one.
- **Pictures kept** (Make a page): untick one of the churches' own pictures
  to leave it out of the page. A church left with no picture is named, so one
  of yours can be given it; otherwise its middle is empty.
- Bible links leave out "Liturgical Text" and a half-verse letter standing
  alone ("4a, c").
- `church_year_web.py --own-art "FILE|churches=...|credit=...|author=...|license=...|license-url=...|source=...|attribution=...|scale=..."`
  (again for each picture) and `--drop-art KEYS`, as Make a page writes them.

### Changed

- `--art-credit`, `--art-scale`, `--art-author`, `--art-license`,
  `--art-license-url`, `--art-source` and `--art-attribution` of
  `church_year_web.py` are fields of `--own-art`. `church_year.py` keeps its
  own `--art-credit` and `--art-scale`.

### Fixed

- **The tradition's own** on a page made with a picture of your own showed
  that picture still; it shows each church's own (or the one of yours given
  it), the picture of yours only when chosen.

## 2026-11 (126) — Slide speed; enlarged artwork kept in the middle

### Added

- **Slide** (Settings, with Readings shown as Columns): Off, Quick, Medium
  or Slow for the sets' slide between the columns; kept in the browser.

### Fixed

- **Artwork enlarged past the circle** (Size above 1, `--art-scale`,
  `center_svg_scale`): cut to the middle's circle, on the page, in Make a
  page's preview and in the drawings, instead of covering the rings around
  it. A photo was already cut to a circle, but one that grew with it.

## 2026-11 (125) — A slower slide

### Changed

- **Readings shown as columns**: the slide when **▾ more** or **▴ less** is
  clicked takes 0.7 seconds instead of a quarter of one, each set moving from
  where its text stood (before, the sets that crossed to the left column
  barely moved) and passing over the columns' edges rather than being cut
  off by them.

## 2026-11 (124) — Readings in columns; your own artwork's credit

### Changed

- **Readings shown as columns**: the sets stay on the right under the day's
  name, as many as fit; **▾ more** opens the box and the sets slide into
  two columns, read left then right, instead of the later ones starting on
  the left. A reading's label and citation ("Epistle Romans 13:11–14") stay
  on one line when they fit, in tabs and columns alike.

### Added

- **Make a page, a picture of your own**: a preview of the picture in the
  middle of the wheel (with the ring around it, so its size can be checked),
  and beside the credit its artist or owner, a license or copyright notice,
  links to the license and the source, and whether the credit must be shown
  (`--art-author`, `--art-license`, `--art-license-url`, `--art-source`,
  `--art-attribution`).

## 2026-11 (123) — Ruthenian Sundays after Theophany; Divine Worship 2027

### Added

- **Divine Worship**: the weekday Masses and the Daily Office (psalms and
  lessons at Morning and Evening Prayer, First Evensong) for all of 2027,
  from the Ordinariate's Ordo for 2026-27, and the Conversion of St Paul,
  Sts Philip and James, St Matthias and St Luke, which had no readings.
- **Byzantine Catholic (Ruthenian)**: the Sundays between the Sunday after
  Theophany and Zacchaeus have their readings, counted back from Zacchaeus as
  the ByzCath lectionary directs: the Sunday before it the 31st after
  Pentecost (Luke 18:35–43), then the 30th (Luke 18:18–27) and the 29th
  (Luke 17:12–19).

## 2026-11 (122) — More Divine Worship psalms

### Added

- **Divine Worship**: psalms for more Sundays from the Ordinariate's online
  archive of Ordos (2022-2027): the 31st Sunday in Ordinary Time of Year A,
  and the 4th, 13th, 24th, 31st and 32nd of Year C. Year B now follows the
  Ordo for 2026-27, the current year (the 12th Sunday's psalm gains verse 8),
  and Year C's the 2025 Ordo with 2022's for the days it lacks. Still without
  a psalm: Year A 7th-10th, Year B 7th-9th, Year C 7th and 9th-12th Sundays
  in Ordinary Time, which no Ordo of those years reaches.

## 2026-11 (121) — Divine Worship Year B and C psalms

### Added

- **Divine Worship**: the Coverdale psalms of Years B and C at Mass, from
  the Ordinariate's Ordos for 2023-24 and 2024-25, for every Sunday and holy
  day those years reach, with the Ordos' own citations where they differ
  from the Roman Lectionary's (Mark 1:21b–28, 1 John 5:1–7, Isaiah 50:5–9a,
  Sirach 27:4–7, Acts 5:27b–32, the order of the options on the Holy Family,
  the Baptism, the Ascension and Pentecost). The psalm now
  follows the Lesson in every Divine Worship set.
- **LCMS**: the Commission on Worship's Lectionary Summaries (three-year,
  one-year, feasts) checked too; they agree with the readings given.

## 2026-11 (120) — LCMS readings checked; BCP 1962 lesser days

### Changed

- **LCMS (LSB three-year and one-year)**: every Sunday and festival
  checked against the Commission on Worship's Church Year Calendars for
  2024-25, 2025-26 and 2026-27. They agree, psalms included, except Easter
  Day in Series C (now Psalm 16, the calendars' psalm; the old one was the
  Sunrise service's) and Proper 9 in Series C (Psalm 66:1–7). Where the
  calendars differ from Lutheran Service Book itself, the book is kept; the
  calendars' misprints are listed in docs/source-errors.csv.
- **LCMS one-year**: the First Sunday after the Epiphany's own readings now
  show beside the Baptism of Our Lord, as LSB gives them, instead of being
  hidden behind it.

### Added

- **BCP 1962 (Canada)**: the black-letter days have Epistles and Gospels
  (with the Introit and psalm Between the Lections) from the book's
  Supplementary Collects, Epistles, and Gospels: Of the Blessed Virgin Mary,
  a Martyr, a Bishop, a Missionary, a Virgin or Matron, a Doctor, Any Saint,
  and Founders and Benefactors, each day taking the one its Calendar entry
  describes; St Joseph, the Name of Jesus, the Beheading of St John the
  Baptist and Holy Cross Day take the Epistle and Gospel the book names.

## 2026-11 (119) — Episcopal Daily Office Lectionary

### Added

- **Episcopal (BCP 1979)**: the Prayer Book's Daily Office Lectionary in its
  two years: every day's morning and evening psalms and three lessons, the
  Evening Prayer of the Eves, Morning and Evening Prayer in Holy Week and on
  Easter Day, the weeks after Pentecost by their Propers, Judith in place of
  Esther as the book allows, and the Holy Days at both offices with their
  Eves. Seven misprints in the table are corrected (docs/source-errors.csv).

## 2026-11 (118) — Prayer Book psalm links

### Fixed

- **BCP 1928, REC 2005, BCP 1962 and BCP 1979**: their own psalm citations
  are in their psalters' verses; the links now open the same verses in
  English Bibles, from verse tables of each psalter (the American Coverdale
  of 1928 and REC, the Canadian 1962 and the Episcopal 1979) as for ACNA.
- BCP 1928 and REC 2005 lists of psalms after a part of a psalm are written
  with a semicolon ("Psalms 21:1–6; 24"), so their links open both psalms
  rather than a verse 24 of Psalm 21.

## 2026-11 (117) — Trackpad scrolling and zooming

### Fixed

- **Trackpads** (Apple's Magic Trackpad and Magic Mouse above all): a
  two-finger swipe now pans the magnified wheel in both directions instead of
  zooming it, and a pinch zooms smoothly in step with the fingers. Before,
  every one of the many small wheel events a trackpad sends zoomed a fixed
  18 per cent (a sideways swipe zoomed out), each restarting the zoom's
  easing. The wheel's movement is now measured and applied once a frame;
  Safari's pinch gestures are handled too. A mouse wheel still zooms a step
  per notch.

## 2026-11 (116) — REC 2005 readings

### Added

- **REC 2005** (Reformed Episcopal Church): the Epistles and Gospels and the
  book's Table of Psalms and Lessons for Morning and Evening Prayer: every
  Sunday's sets, every weekday, the Ember Days, the fixed holy days (Eve,
  Morning and Evening), Independence Day, Thanksgiving Day and the End of the
  Year.

## 2026-11 (115) — ACNA psalm links

### Fixed

- **ACNA 2019**: its psalms are cited in its Prayer Book psalter's verses
  (Psalm 33:17–21 is 33:18–22 in an English Bible); their links now open the
  same verses at Bible Gateway and Bible.com, from a verse table of the 66
  psalms its psalter divides differently (docs/versification.md).

## 2026-11 (114) — Syriac Orthodox corrections

### Fixed

- **Syriac Orthodox**: four misprinted citations in Scripture Readings settled
  from the Archdiocese's Epistle lectionary and the Patriarchate's Old
  Testament readings: Zechariah 7:1–14 (Sunday of the Leper), Isaiah 15:1–9
  (Easter Monday), 1 Corinthians 7:25–34 (22nd Sunday after Easter) and
  2 Timothy 2:15–26 (the Presentation).

## 2026-10 (113) — The Syriac Orthodox lectionary

### Added

- **Syriac Orthodox readings** for the whole year, from the Archdiocese of
  the Syriac Orthodox Church in the Eastern USA's Scripture Readings
  (Qeryone men kthobo qadisho, 2000): each Sunday's and feast's Old
  Testament lessons, Acts or Catholic Epistle, Pauline Epistle and Gospels;
  the weekdays of the Fast of Nineveh and the Great Fast; Holy Week's
  Evening and Morning Prayer, Midnight Office and hours; Naheere, the
  Blessing of the Branches and of the Water, the Washing of the Feet, the
  Service of Peace and Pentecost's Kneeling Service.

## 2026-10 (112) — ACNA's own lectionary

### Changed

- **ACNA 2019** reads its Prayer Book's Sunday, Holy Day, and
  Commemoration Lectionary instead of the plain Revised Common Lectionary:
  Years A, B and C, the three Christmas and Easter services, Holy Week and
  Easter Week, World Mission Sunday, the holy days, the Ember and Rogation
  Days, Thanksgiving (both countries), Canada Day, Independence Day,
  Memorial and Remembrance Days.

## 2026-10 (111) — The Malankara and Maronite lectionaries

### Added

- **Malankara Orthodox Syrian Church readings** for the whole year, from
  St. George Indian Orthodox Church, Melbourne's Lectionary Guide: each
  Sunday's and feast's Gospels at Vespers and Matins, the Old Testament
  lessons before the Holy Qurbana and its Acts or Catholic Epistle, Pauline
  Epistle and Gospel; the weekdays of the Great Fast and the Fast of
  Nineveh; Holy Week's Midnight Office and hours; the Service of the Fire at
  Christmas, the Blessing of the Water at Denho, the Washing of the Feet and
  Pentecost's Kneeling Service.
- **Maronite readings**: the Epistle and Gospel of every Sunday and weekday
  from the Consecration of the Church to the Sundays of the Cross, and of the
  calendar's feasts, from the Eparchy of Our Lady of Lebanon's Ordo.
- The Midnight Office and Compline count as the Office.

## 2026-10 (110) — From the LSB Altar Book; page fixes

### Added

- **LSB**: the psalms the online sources lacked, from the Altar Book (St.
  Thomas, St. Joseph, the Annunciation, St. Philip and St. James, the
  Visitation, the Nativity of St. John the Baptist, St. Mary Magdalene,
  St. James of Jerusalem, Monday to Wednesday of Holy Week, Holy Saturday,
  Easter Monday to Wednesday) and the Vigil of Easter's twelve readings
  with the psalm or canticle after each.

### Changed

- A day's Office is listed in the order of the day: Matins (or Morning
  Prayer) before Vespers (or Evening Prayer), Compline last.
- The page's header gives the day's name the room beside the controls,
  wrapping it there rather than dropping it under them.

### Fixed

- On a phone the readings and their tabs ran off the side of the screen;
  they wrap now.

## 2026-10 (109) — BCP 1928 Morning and Evening Prayer

### Added

- **BCP 1928 Office lessons**: the Table of Psalms and Lessons for the
  Christian Year (the 1943 lectionary, as printed in 1945) for every day,
  with the Sundays' alternative sets, the three weeks before Advent, the
  autumnal Ember Days, the fixed holy days' Eve, Morning and Evening
  Prayer, Independence Day, Thanksgiving Day and the End of the Year.

## 2026-10 (108) — Armenian and Assyrian readings

### Added

- **Assyrian Church of the East**: the Sundays' and the Lord's feasts'
  readings (two lessons, the Apostle and the Gospel) from
  the Archdiocese of Australia's lectionary, on the days they name.
- **Armenian readings** for every day from Advent 2025 to 6 January 2027,
  from the Armenian Prelacy's monthly calendars: the day's readings, the
  services of Christmas Eve, Holy Week and Easter, and Eastertide's four
  Gospels read through morning, midday, evening and dismissal.

## 2026-10 (107) — The Coptic Katameros

### Added

- **Coptic readings** for every day of the year, from the Katameros as the
  katameros-api project keeps it: the Vespers and Matins psalm and Gospel and
  the Liturgy's Pauline and Catholic Epistles, Acts, psalm and Gospel, by
  Coptic date on weekdays and by month on Sundays, with Great Lent's and the
  Fifty Days' own, the feasts (the Nativity and its Paramoun, Theophany and
  its Paramoun, the Cross, the Annunciation ...), the Fast of Nineveh and the
  hours of Pascha in Holy Week.
- `when` conditions may have alternatives: `date lt easter-69 or date gt
  easter+49`, each joined by `and`.

## 2026-10 (106) — The Church in Wales's daily lectionary for 2025-26

### Added

- **Church in Wales**, from its Year A booklet (Advent 2025 to Kingdom
  2026): the Second and Third Services on Sundays and principal holy days,
  and the Daily Eucharist and Morning and Evening Prayer on the other days,
  with Evening Prayer on the eves of holy days.

## 2026-10 (105) — Divine Worship's weekdays and Daily Office for 2025-26

### Added

- **Divine Worship**, from the Ordinariate's Ordo for Advent 2025 to
  Christmastide 2026: the weekday Masses' first reading and Gospel, and the
  Daily Office's psalms and first and second lessons at Morning and Evening
  Prayer (with First Evensong on the eves of Sundays and holy days), for
  every day from Advent Sunday 2025 to 31 December 2026.

## 2026-10 (104) — BCP 1962's Table of Lessons

### Added

- **BCP 1962's Table of Lessons for Morning and Evening Prayer**, from the
  book (pp. xvi–xlvii): both years' first and second lessons for every day
  of the year, Year I when Advent Sunday falls in an even year; the
  holy days' First Evensong, Morning and Evening Prayer lessons; and, for
  the 21st to 26th Sundays after Trinity, the book's other first lessons
  "in place of the Lessons from the Apocrypha". Twelve misprints are
  corrected and listed in docs/source-errors.csv.
- Two new kinds of reading, `first` and `second` (First Lesson, Second
  Lesson).

### Fixed

- LW: the 7th Sunday after Pentecost C psalm (Psalm 19) and the
  Annunciation's Gospel (Luke 1:26–38), checked against the printed book.

## 2026-10 (103) — LW's readings from Lutheran Worship itself

### Added

- **LW's one-year series**, from the book's Propers of the Day (pp. 10–122):
  every Sunday and festival, with its psalm, as its own set "One-Year
  Series" beside the year's three-year set; Easter Day's three sets and the
  Day of Pentecost's two; the Vespers readings of Easter Eve, Easter Evening,
  Pentecost Eve and Pentecost Evening.
- Readings for days that had none: New Year's Eve, the Commemoration of the
  Faithful Departed, Martin Luther, C. F. W. Walther and the Presentation of
  the Augsburg Confession (LW's Commemoration of the Doctors of the Church).

### Fixed

- **LW's three-year series now follows LW itself** rather than the LCMS's
  LSB/LW comparison chart, which often gave LSB's verses and left many psalms
  and readings out: about 120 readings change (Advent 1 A Matthew 24:37–44, not
  24:36–44 ...) and the missing psalms, epistles and Old Testament readings are
  filled. The Christmas services follow the book: Christmas Dawn is Isaiah 52,
  Psalm 2, Hebrews 1 and John 1; Christmas Day Isaiah 62, Psalm 98, Titus 3 and
  Luke 2.

## 2026-10 (102) — LSB's own topical index for the hymn marks

### Changed

- **The LSB hymn marks follow the book's Topical Index of Hymns and Songs**
  (pp. 993–997): each section ("Advent, 331–357") now lists the other hymns
  the index adds to it as well (The Bridegroom soon will call us, Come, Thou
  bright and Morning Star ...), and Reformation and Holy Cross Day list the
  index's hymns instead of searching Hymnary.org.

### Added

- Hymn marks for the index's topics for Baptism of Our Lord, Palm Sunday,
  Maundy (Holy) Thursday, Good Friday, the Presentation of Our Lord and St.
  Michael and All Angels; the first lines of the 42 hymns this adds to
  `data/hymnals/LSB2006.csv`, as the index prints them.
- A hymn mark's tooltip gives the number of hymns rather than their numbers.

### Checked

- Against the printed Pew Edition: the three-year, one-year, feast and
  occasion readings (pp. xiv–xxiii) and the commemorations (pp. xi–xiii) match;
  every Daily Lectionary reading kept as an additional reading is in italics on
  pp. 299–304, and none is missing, so that split is no longer inferred.

## 2026-10 (101) — Sourced gaps filled

### Added

- **Ethiopian:** Gizret, the Circumcision (6 Tir), and Megabit Meskel, the
  finding of the Cross (10 Megabit), from Mahibere Kidusan.
- **Methodist Church in Britain:** the Fourth Sunday in Lent "or Mothering
  Sunday", the Fifth "First Sunday of the Passion", Palm Sunday as the "Sixth
  Sunday in Lent: Second Sunday of the Passion", and Remembrance Sunday (the
  second Sunday in November), from the 2025–26 lectionary and the Church's
  special Sundays.
- **Reformed (RCA):** Reformation Sunday (the Sunday before 31 October, unless
  31 October is a Sunday) and Reformation Day, from the RCA's observances.
- **Maronite:** All Saints (1 November), a holy day of obligation.
- **Roman:** the optional Masses of the third, fourth and fifth weeks of Lent
  (Lect. 236, 243, 250), a second set on each weekday of those weeks.
- **Roman 1962:** the Vigil of the Ascension (Rogation Wednesday). Rogation
  Tuesday has no propers of its own and keeps the Sunday's.

### Fixed

- provenance.csv: the WELS festivals, listed since they were added, are now
  marked sourced.

## 2026-10 (100) — Hymn marks for the other hymnals' topics

### Added

- **Days get hymn marks from the topics of every hymnal the page offers,**
  not only Lutheran Service Book: Christian Worship (2021), Together in Song,
  Singing the Faith, the Moravian Book of Worship, Church Hymnary 4, the
  United Methodist Hymnal, Glory to God, Lift Up Your Hearts, the Evangelical
  Lutheran Hymnary, Worship (4th ed.), Ancient and Modern (2013), Complete
  Anglican Hymns Old and New, Common Praise (2000 and 1998) and the New English
  Hymnal. Each folder's new `hymn_topics.csv` names the seasons and days in
  the hymnal's own words: every Sunday in Ordinary Time (Worship), every
  Sunday and Proper of Common Worship (Ancient and Modern, Common Praise,
  Complete Anglican Hymns under Year A, B or C), the historic series'
  Sundays (Evangelical Lutheran Hymnary), the saints' days (New English
  Hymnal, Common Praise 1998), Aldersgate (UMH) and the Moravian festivals.
- `hymn_topics.csv` takes `when` (a condition, as readings.csv's: the Propers
  by date) and `subtopic`; `{abc}` in either is the lectionary year.

### Changed

- **A topic mark opens Hymnary.org's list for that topic**
  (`hymnary.org/browse/topics/<code>?subject1=...`) rather than a search of
  its words, which also matched other topics sharing them.

## 2026-10 (99) — Names that ran out of their cells on phones

### Fixed

- **Each line on the wheel carries the width it was fitted at**
  (`textLength`, with `lengthAdjust="spacingAndGlyphs"`), so a browser
  without Times New Roman or Arial draws it to that width rather than its
  own: on Android, whose Noto Serif is about a tenth wider, "Johannes von
  Staupitz" ran over the sides of its cell. Small capitals drawn as two sizes
  of capitals carry it run by run. Where the fonts are there, as on most
  computers, nothing changes.
- church_year.py adds floats one by one, as the browser does, where a
  coordinate is a sum (`_plain_sum`): Python 3.12's compensated `sum()` left
  the last digit of three 1962 Roman wheels' small capitals unlike the page's.

## 2026-10 (98) — A day's hymns by the sections of the hymnal

### Added

- **The day's hymn marks list the hymnal's own sections.** Hymnary.org can
  search neither a range of hymn numbers nor (for Lutheran Service Book) the
  seasons, so a `hymn_topics.csv` row may now give a section of the hymnal's
  contents by its numbers (`advent,,LSB2006,Advent,331-357`): its mark opens
  a window listing the section's hymns with their first lines, each opening
  its page at Hymnary.org. The first lines are in `data/hymnals/LSB2006.csv`
  (from Hymnary.org's listing of the hymnal). LSB's contents (pp. v–vi) now
  give every Sunday and principal day of Advent, Christmas, the Epiphany, the
  Transfiguration, Lent, Holy Week, Easter, the Ascension, Pentecost and the
  Holy Trinity its section, the last three Sundays End Times, the festivals
  Feasts and Festivals, New Year's Eve and Day New Year; Holy Baptism,
  Baptismal Life, Confession and Absolution, the Lord's Supper, the Word of
  God, the Church Militant and Triumphant, Mission and Witness, Harvest and
  Thanksgiving and Nation and National Songs where they suit. Hymnary's
  topics remain for Reformation and Holy Cross Day, which have no section.

## 2026-10 (97) — Hymn marks for the day; Hymnary results in hymn order

### Added

- **A hymn mark after the day's name** for each topic of the hymnal's index
  at Hymnary.org that suits the day, before the season ("Nineteenth Sunday
  after Pentecost · St. Michael and All Angels ♪ — Season After Pentecost"):
  the hymnal's hymns on that topic, in hymn-number order. The topics are
  matched to days in a folder's new `hymn_topics.csv` (`day,variant,hymnal,
  topic`), keyed as readings.csv is. Lutheran Service Book's (the LCMS and
  LCC calendars), from hymnary.org/browse/topics/LSB2006: the festivals
  (Feasts and Festivals; the Presentation, Holy Cross Day and St. Michael
  and All Angels their own), the Baptism of Our Lord (and Baptismal Life),
  Ash Wednesday, Maundy Thursday (and the Lord's Supper), Reformation (and
  the Word of God), All Saints (Church Triumphant), Thanksgiving (Harvest and
  Thanksgiving; Nation and National Songs); and, as Hymnary has no topics
  for the seasons, Sundays by theme: the Epiphany and its Sundays (Mission
  and Witness), Lent (Confession and Absolution), Sexagesima (the Word of
  God) and the last three Sundays of the year (End Times).

### Changed

- Hymnary.org searches list their hymns in the hymnal's order
  (`&sort=hymnalNumber&order=asc`).

## 2026-10 (96) — The first day's date on two lines

### Changed

- The year's first day, when its date does not fit on one line even at the
  smallest size, breaks it after the comma ("September 11," / "2026", the
  Coptic and Ethiopian New Year in 2026) instead of leaving the year out; the
  cell gives the second line its room, and the two lines are fitted to the
  width at each one's radius (church_year.py `_date_label_fit`,
  church_year.js `dateLabelFit`).

## 2026-10 (95) — Names that ran to the edge of their cells; no hymn search on the Apocrypha

### Fixed

- **Letters beyond ASCII are measured at their true width.** The wheel's
  measurer knew only ASCII and took every other letter as half an em, so a
  line of wide capitals or Cyrillic ("PYHÄINPÄIVÄ", "NAGYCSÜTÖRTÖK",
  "РІЗДВО ХРИСТОВЕ") was fitted to a cell it then ran out of, by up to 3
  units. `lib/font_widths.py`, written by `tools/font_widths.py` from the
  Liberation fonts (metric-compatible with Times New Roman and Arial), gives
  the width of each of the 214 such characters the calendars use; the
  typographic apostrophe, once half an em, is now its own third. Measured in
  the browser over every church for 2024–2026, no name now comes within 1.5
  units of its cell's sides.
- **The first day's label gives up its year rather than run out of its
  cell**: "September 11, 2026", the Coptic and Ethiopian New Year, did not
  fit even at its smallest size and overran by a unit; it now reads
  "September 11".
- **The chosen day's frame sits on the cell's outline** (5 units of white
  under 2.5 of black, half on each side) rather than outside it, so it no
  longer covers the ends of long names in the cells beside it (Johannes von
  Staupitz, the day before the Sunday after him).
- **Hymn search leaves out the Apocrypha**, as Word to Worship does: a set
  of only Apocrypha readings has no hymn mark.

## 2026-10 (94) — The hymnal a page opens on; Hymn search for the 1962 calendar

### Added

- Make a page has a **Hymnal** menu (each church's first, or one of the
  hymnals of the churches on the page that have several), written as
  `church_year_web.py --hymnal CODE`; the page then opens every church that
  has that hymnal on it. A code no church on the page offers is an error.
- Hymn search for the 1962 Roman calendar (Worship, 4th ed., WORS2011).
- docs/adding-a-church.md: which Readings box a set goes under, the Apocrypha
  and Book of Concord citations, and a new step 8 for a church's extras on the
  page: weekday names, Hymn search (finding a hymnal's code and how many of
  its hymns Hymnary has indexed by scripture; several hymnals), feast links,
  Latin names, the Bible version.

## 2026-10 (93) — A Hymnal menu; the ELS and Roman hymnals

### Added

- **A Hymnal menu** in Settings for a church with several hymnals at
  Hymnary.org (`hymnary_hymnal` codes separated by spaces, their names by
  `|`), newest first, the first opening; a link keeps a choice (`hymnal=`).
  The Church of England's calendars (Common Worship, BCP 1662) offer Ancient
  and Modern (2013, AM2013), Complete Anglican Hymns Old and New (2000,
  CAH2000), Common Praise (2000, CPAM2000) and the New English Hymnal (1986,
  NEH1985).
- Hymn search for the ELS (Evangelical Lutheran Hymnary, 1996, ELH1996),
  though few of its hymns have their scripture at Hymnary.org yet, and the
  General Roman Calendar (Worship, 4th ed., 2011, WORS2011).

## 2026-10 (92) — Hymn search for more churches

### Added

- **Hymn search for twelve more calendars**, each with its hymnal's code and
  name in `tradition.csv` (`hymnary_hymnal`, `hymnary_hymnal_name`, the
  name in the mark's title): the LCMS One-year and the LCC (Lutheran Service
  Book), WELS (Christian Worship: Hymnal, 2021), the LCA (Together in Song,
  1999), the United Methodist Church (The United Methodist Hymnal, 1989), the
  Methodist Church in Britain (Singing the Faith, 2011), the Moravian Church
  (Moravian Book of Worship, 1995), the PC(USA) (Glory to God, 2013), the RCA
  and CRC (Lift Up Your Hearts, 2013), the Church of Scotland (Church
  Hymnary, 4th ed., 2005), the Anglican Church of Canada (Common Praise,
  1998) and the Church of England (Common Praise, 2000, Hymns Ancient and
  Modern). Each has several hundred hymns indexed by scripture at
  Hymnary.org. Lutheran Worship (1982), Evangelical Lutheran Worship, the
  Evangelical Lutheran Hymnary and the Hymnal 1982 are there but with only a
  few dozen so indexed, and TLH and the ELHB with none, so they are left out.

## 2026-10 (91) — Hymn search at Hymnary.org; a thicker line where the year begins

### Added

- **Hymn search**: after each set of readings, a hymnal mark (a book with a
  note on its cover) opens Hymnary.org's hymns on those readings in the
  church's hymnal: `scripture:` the set's readings, every choice of each,
  with hyphens, then `hymnalNumber:lsb2006 in:instance`. For now the LCMS
  Three-year, Lutheran Service Book (2006) (`tradition.csv` `hymnary_hymnal`).
  Settings has a *Hymn search* box; Make a page and `church_year_web.py
  --hymnary` / `page_hymnary` take on, off or none, as for Word to Worship;
  a link keeps `hymns=`. `links.py`: `hymnary_url`; `page.js`: `hymnaryUrl`.
- Word to Worship's search is now called *Contemporary song search*, its mark
  (the circled note) titled for contemporary worship songs, so the two read
  apart.
- **A thicker line where the year begins** (`year_line`, width
  `year_line_width`, 4): where the year's last week meets its first, across
  the day cells and the season, half and month rings, so the weeks on either
  side read as a year apart. A box in Settings (`yearline=` in a link),
  Make a page's *The wheel*, `--year-line` / `--no-year-line` for
  `church_year_web.py` and `church_year.py`.

## 2026-10 (90) — Make a page: the churches folded, the file name by the button

### Changed

- Make a page's *Churches it offers* opens folded to one line with its count
  ("68 of 68"); click it for the buttons and the list. The window opens at
  its top.
- The file name stands beside *Make the page* and *Close*.

## 2026-10 (89) — Make a page regrouped; the Bible it opens in is on its menu

### Changed

- **Make a page's window is regrouped**: *It opens* (the church, calendars,
  year and zoom), *The wheel* (Feasts, Latin names, rings, colors, text on
  mid-tone colors, artwork), *Readings and links* (the kinds of readings,
  tabs or columns, links, the Bible menu, then the Bible it opens in, Open in,
  Song search), *Settings it shows* (calendar, Easter, artwork, dark text on
  reds) and *Buttons it shows* (Download…, Make a page…). With no readings
  left, the reading settings leave the window.
- **The Bible a page opens in must be on its Bible menu.** Make a page offers
  only the versions the Bible menu chosen offers (none but each church's own
  when the menu is each church's own), and a version taken off the menu goes
  back to each church's own; a pasted command that asks for one not on its
  menu says so. `church_year_web.py --bible-default` stops with an error when
  the version is not on `--bible`'s menu, where before the page quietly
  opened in another.

## 2026-10 (88) — Smaller pages: only the readings asked for, packed

### Changed

- **`--readings` (and `page_readings`, Make a page's Readings boxes) now says
  which sets the page carries**, not only which boxes start checked: the
  readings of the other kinds are left out of the page, with their boxes.
  `--readings day` gives a one-church LCMS page of about 530 KB, where v158's
  was 1.25 MB with the Reading plan, the psalm table and the additional
  readings it never offered checked. A page with no readings left has no
  Readings section. Make a page offers only the kinds its page carries.
- **The readings are packed** in `data.json` and the page: each lectionary's
  columns, every distinct cell once, and each row as the indexes of its cells
  (`export_data.py`: `pack_rows`; `church_year.js`: `readingRows`). The same
  page with every set is 740 KB rather than 1.25 MB, and `data.json` 3.9 MB
  rather than 7.3 MB.
- The tables are written into the page as UTF-8 rather than with `\u`
  escapes (en dashes, accented names).

## 2026-10 (87) — A feast kept on a Sunday no longer names the week

### Changed

- **The weekdays after a Sunday a fixed-date feast takes are named from the
  Sunday it displaced**: the Tuesday after Reformation Day (observed) is
  "Tuesday after the Twenty-first Sunday after Pentecost", not "Tuesday after
  Reformation Day"; the same for All Saints' Day observed, Reformation Sunday
  (ELCA, ELS, WELS), All Saints' Sunday (Episcopal), St. Michael and All
  Angels (ELS), and the Coptic, Armenian and Syriac saints' days and feasts of
  the Cross that take a Sunday. Christmas, the Epiphany and the feasts of
  their season (the Holy Family, the Baptism) still name their weeks, as do
  the movable Sundays with names of their own (the Transfiguration, the Last
  Sunday of the Church Year). In the Orthodox and Byzantine Catholic calendars,
  which count the weeks, every Sunday leaves the week its number: "Tuesday of
  the Twenty-first Week after Pentecost" after the Sunday of the Holy Fathers.

## 2026-10 (86) — Readings under tabs; weekdays named from their Sundays

### Added

- **Readings under tabs** (now the default): a row of the sets' names (the
  day's propers, Daily lectionary, Additional, Psalms, Reading plan ...) with
  the chosen one's readings under it; the tab chosen stays chosen from day to
  day. Settings has *Readings shown as: Tabs / Columns* (the two columns of
  v156). `--readings-layout` / `page_readings_layout`: tabs, columns, or both
  (`tabs,columns`, the default, or `columns,tabs`), the first opening and the
  other offered in Settings; Make a page has the same choice, and its command
  and pasted settings carry it. The link keeps a choice away from the
  default (`layout=columns`).
- **A weekday without a name of its own is named from its Sunday**, after the
  date: "Tuesday after the Sixth Sunday after Pentecost" (the LCMS, the other
  Lutheran and the Anglican calendars), "Wednesday of Laetare" where the
  one-year series' Latin names are on; "Tuesday of the Sixth Week of Easter",
  "of the Thirteenth Week in Ordinary Time" (the Roman calendar) and "of the
  Fifth Week after Pentecost" (the Orthodox and Byzantine Catholic). A Sunday
  named by a feast kept on it gives "Tuesday after Reformation Day". Not for
  the calendars whose names are not in English (tradition.csv
  `weekday_titles`: after, week or none).

## 2026-10 (85) — Readings in two columns, a "more" button, Feedback in the corner

### Changed

- **The day's readings use both sides of the bar**: the sets stand on the right
  under the day's name as before, and when they need more than its three
  lines the later ones move to a column on the left, under the church's name,
  split where the two columns come out most even. A column with more below
  fades at its foot.
- **"▾ N more"** appears when the sets still do not all fit (most often on a
  phone, where they stay in one column): it opens the box to show them all,
  up to half the screen, and "▴ less" closes it. The wheel takes the room
  that is left.
- **The Feedback button moved to the bottom left corner**, across from the (i),
  freeing the bar's left side.

## 2026-10 (84) — No Bible Gateway or song links for the Book of Concord

### Changed

- **A set of Book of Concord readings has no Bible Gateway link**, since Bible
  Gateway lacks them (a set with Bible readings too opens those alone), and
  **the Song search mark leaves out the Apocrypha and the Book of Concord**,
  which Word to Worship (Protestant canon only) does not know; a set of only
  those has no mark. links.py and page.js alike.
- On 14 September the Additional readings set keeps both LSB's Jonah and the
  draft's Prayer of Manasseh.

## 2026-10 (83) — Additional readings from the Apocrypha and the Confessions; Book of Concord paragraph links; the psalm weeks from Advent

### Added

- **The draft Daily Lectionary's own additional readings** (LSB-Daily-Lectionary.pdf,
  "with Additional Readings from the Apocrypha, the Lutheran Confessions, and
  the Catalog of Testimonies") fill the *Additional readings* set on the days
  LSB gives none: 172 from the Apocrypha (kind `apocrypha`) and 147 from the
  Book of Concord and the Catalog of Testimonies (kind `confessions`, "Lutheran
  Confessions"). Abbreviations spelled out; Baruch 6 given as the Letter of
  Jeremiah and the "Apocr. parts of Esther" as Greek Esther, the names Bible
  Gateway's RSV knows them by. Where the draft puts Hosea and Jonah a day
  before LSB (12–13 September), LSB's dates are kept.
- A book of the Apocrypha cited whole ("Prayer of Manasseh") is linked.

### Changed

- **Book of Concord links go to bookofconcord.org, at the paragraph**: its
  pages have an anchor for every paragraph (`#ap-iv-0117`), which CPH's site
  lacks. Citations by article and paragraph ("Apology 4:117–146", "Augsburg
  Confession XX 1–8"), by part and article for the Smalcald Articles
  ("3/3:19–29"), by paragraph for the Treatise and the prefaces. The Apology's
  IV 122–400 and XII 98–178, which the site puts on pages of their own, and
  its articles numbered on from the one before (IX is 51–53 there), are
  mapped to the site's numbers; every anchor the readings use was checked to
  exist.
- **The General weeks of LSB's psalm table are counted from the First Sunday
  in Advent** through the whole church year, instead of starting again on
  7 January and at Holy Trinity.

## 2026-10 (82) — A Bible reading plan, LSB's additional readings and psalm table, Loehe's saints, Apocrypha and Book of Concord links

### Added

- **Reading the Word of God**, the three-year daily Bible reading plan of
  Lutheran Church–Canada, the LCMS and the North American Lutheran Church
  (`data/readings/plan-rwg.csv`), for every LCMS calendar and both LCC series,
  under a new Readings box, *Bible reading plan* (`--readings plan`). It is
  kept by the calendar year: rows keyed `plan:N` fall on the Nth day of the
  year that none of the plan's fourteen festivals takes, and its cycles (2018,
  2019, 2020, republished for 2021–2023) are read in turn. The engine gives
  the three printed calendars back day for day; the leap-year case the
  calendars never meet is inferred and noted in the file. Four slips of the
  print corrected (docs/source-errors.csv). lectionary.py and church_year.js
  alike (`Year.context`: a neighboring church year's rules, for the plan's
  festivals in the calendar year two church years share).
- **LSB's additional readings are their own set**, *Daily Lectionary:
  Additional Reading*, with their own box, *Additional readings*
  (`--readings additional`), instead of "(additional)" lines within the Daily
  Lectionary. The draft LSB Daily Lectionary the data were checked against
  (St. John's, Austin) is the one named in lsb.csv; its OT/NT columns were
  compared with the final text before, and the split of the italic readings
  rests on that comparison.
- **Wilhelm Loehe's calendars of saints**: *Loehe Martyrologium (1868)* and
  *Loehe Kirchenbuch (1859)* in the LCMS's hymnal menu (`data/LCMS/Loehe`),
  from Benjamin T. G. Mayes's translations: a name or more for every day, the
  1859 book's Epistles and Gospels for its feasts (a `lesson` where it prints
  a third citation), on the historic one-year calendar (ELHB's days and
  seasons). Links as for the LCMS: CPH where LSB keeps the saint (38 or 39 names),
  else a Wikipedia article (the Lutheran, Anglican and 1954 Roman calendars
  of saints; 78 and 91 names), else a Wikipedia search for the name and its place.
- **Book of Concord links**: a reading citing the Confessions ("Augsburg
  Confession XX 1–8", "Apology IV", "Smalcald Articles III VIII", "Small
  Catechism, Baptism", "Formula of Concord, Solid Declaration II", the
  creeds) opens at its article on CPH's bookofconcord.cph.org, which has a
  page for every article (bookofconcord.org names its pages by topic,
  irregularly; neither links paragraphs). No calendar has such readings yet;
  verify_links.py checks a set of them.

- **LSB's table of psalms** (p. 304) under its own box, *Psalm table*
  (`--readings psalms`), as the set *Psalms for Daily Prayer*: a morning psalm
  and two evening psalms for every day, from the weekday tables of Advent
  (to 23 December), Lent (to Holy Saturday), Easter (to the Tuesday after
  Pentecost) and the four General weeks (the season of Epiphany from 7
  January, and the Time of the Church from Holy Trinity), with the Christmas
  days by date (24 December to 6 January, until now within the Daily
  Lectionary). LSB leaves the turn of the General weeks open ("may be
  repeated as often as necessary"); they are read in turn, Week 1 from the
  week of 7 January and again from Holy Trinity.

### Fixed

- **Readings from the Apocrypha opened nothing** in the ESV and most other
  versions (Bible Gateway: "No results found"). They now open in the RSV at
  Bible Gateway, whose Apocrypha the ESV's (in CPH's Lutheran Edition, not
  online) revises, and in the NRSVUE at Bible.com, which has no RSV
  Apocrypha; a set with one opens in the RSV. Versions that have them (NRSVUE,
  NRSVA, RSV, NABRE, CEB, RSVCE, DRA) open as chosen. links.py and page.js
  alike.

## 2026-10 (81) — One size for every name on the seasons ring

### Changed

- **The seasons ring's names are all one size** (`ring_label_uniform`,
  config.csv, `seasons`): the largest at which every name on the ring fits,
  spilling past short seasons where it must, rather than each shrinking by
  itself. LCMS, ELCA, Roman, Common Worship and the rest keep 24 points every
  year; the Orthodox ring takes 18.75 throughout, every year from 2024 to
  2030. A sliver of a season named elsewhere on the ring is still left
  unlabeled. church_year.js the same; `web/verify.py` identical.

## 2026-10 (80) — Seasons ring: larger type, and short seasons spill over

### Changed

- **The seasons ring's names are larger:** 24 points, up from 18 (rings.csv),
  above the months ring's 18.
- **A short season's name runs past its arc** into the free ring beside it
  instead of shrinking (`ring_label_spill`, config.csv, on). The Orthodox
  Apostles' Fast, often a week or less, now has the full 24 points in most
  years (it was 6 or 7 in late-Easter years; 15.5 in 2026-27, when it is one
  day); the Dormition Fast and the Exaltation of the Cross went from 10 and
  12 to 24, the Transfiguration from 16 to 18.5. The same helps every
  church's short seasons. A label stays half its size clear of the others,
  keeps its own arc's middle under it, and never crosses the year's ends.
- **A one-day sliver of a season named elsewhere on the ring** (the Sunday
  "After Pentecost" before the Apostles' Fast) is left unlabeled rather than
  turned across the ring at 6 points.
- church_year.js does the same; `web/verify.py` finds the drawings identical
  (132 years, every church; 1990-2075 for both LCMS series).

## 2026-10 (79) — provenance.md fits the screen

### Fixed

- **docs/provenance.md's tables ran off the side** in Markdown readers
  (Markdown Monster, MarkText, Obsidian) wherever a source was a long web
  address, which no reader can wrap: 47 sections, from the Anglican and
  Lutheran books to the Orthodox churches. `tools/provenance.py` now writes
  each address as a link named by its site (`[calendar.lcms.org/…](…)`), so
  the address is still there to click but the column can wrap.
  `docs/provenance.csv` keeps the full addresses.
- One long run of color changes in docs/data-files.md's table is split at
  its commas.

## 2026-10 (78) — WELS feast links: CPH first too

### Changed

- **WELS** (Christian Worship 2021, three-year and one-year) links its feasts
  and festivals as the LCMS calendars do: CPH's post for the day first (all
  of them, the Name of Jesus, the Visitation and St. James the Elder
  included, which had no link), then a Wikipedia article (Thanksgiving Day),
  then a search. St. James of Jerusalem no longer opens Wikipedia's "James"
  disambiguation page.

## 2026-10 (77) — LCMS feast links: CPH first

### Changed

- **The LCMS calendars link Concordia Publishing House first,** then a
  Wikipedia article, then a Wikipedia search.
  - **Lutheran Service Book:** its 35 feasts and festivals (the apostles and
    evangelists, the Annunciation, the Visitation, Holy Cross, Reformation,
    All Saints and the rest) now open CPH's post for the day, from its Feasts
    and Festivals index, as its 81 commemorations already opened CPH's
    commemoration pages. All 116 rows link CPH. ELS and LCC, which keep
    LSB's list, the same.
  - **Lutheran Worship, The Lutheran Hymnal, the Evangelical Lutheran
    Hymn-Book:** CPH for every day LSB keeps (St. Laurence too, and the
    feasts under their older names); a Wikipedia article for the rest (the
    Faithful Departed in Lutheran Worship). No satucket.com links.

## 2026-10 (76) — Feast links for the Anglican, Episcopal and Lutheran calendars

### Added

- **A page about each commemoration** in the other calendars too, in place of
  a Wikipedia search: 1,840 more rows across 15 feasts files.
  - **Episcopal Church:** satucket.com's biographies (its calendar page, as saved
    from satucket.com), else Wikipedia: 163 of 184 rows.
  - **Church of England, Church in Wales, Anglican Church of Canada,
    Scottish Episcopal Church:** the article each church's Wikipedia calendar
    of saints links; a prayer book looks first in its own church's calendar,
    then the others'. ACNA, BCP 1928 and REC look first in satucket.com.
  - **Lutheran** (ELCA, LCMS hymnals, ELS, LCC, WELS, the world Lutheran and
    Ukrainian calendars): Wikipedia's Lutheran calendar of saints, then
    satucket.com. Rows that already had a link keep it.
  - Matched by name, on the date or as the only one of that name, as the
    Catholic links are. Links to general articles (England, Martyr,
    Reformation) are left out. The Brazilian and Portuguese books' names are
    mostly in Portuguese and keep the search; so do the Armenian feasts,
    whose dates move.

## 2026-10 (75) — Catholic feasts link to Loyola Press and Franciscan Media

### Added

- **A page about each Catholic celebration.** A commemoration's name on the
  Roman calendars opened a Wikipedia search, which did not always find it.
  It now opens the saint's or feast's page at Loyola Press (*Saints Stories
  for All Ages*), else Franciscan Media (*Saint of the Day*), from a `link`
  column in the Roman feasts files.
  - **General Roman Calendar:** 219 of its 222 rows (184 Loyola Press, 35
    Franciscan Media). St. Pancras, Our Lady of Loreto and the Immaculate
    Heart have no page at either and keep the Wikipedia search.
  - **The 1962 calendar, national, religious-order and ordinariate
    calendars:** 256 more rows, where Loyola Press or Franciscan Media has
    the same saint (matched by name, on its date or as the only one of that
    name; a choice such as "St. Pius V or St. Peter Chanel" is left alone).
  - A national row that keeps a General Roman Calendar id for another
    celebration (Our Lady of Nuria in Andorra, the Exaltation of the Cross on
    3 May in Mexico and four other countries) does not inherit the other's
    page: it gets its own, or none (`-`).

## 2026-10 (74) — Download: up to 101 years

### Changed

- **Download** makes files for up to 101 church years at a time (it was 50),
  so a whole century with both ends, 2000-01 to 2100-01, comes in one go.
  The four lists over 101 years take a few seconds (13 MB zipped); the wheel
  as SVG and PNG at 5,000 pixels takes about a minute and a half and some
  510 MB, so the window says how large a run of PNGs will be and that a
  narrower PNG is smaller.

## 2026-10 (73) — Make a page: settings back in, and HKBP in the Terjemahan Baru

### Added

- **A command back into Make a page:** paste a `church_year_web.py` command
  under *The same page from Python* and *Set the window from it*: every choice
  is set as the script reads the command (short option names, `--opt=value`,
  quotes, lines continued with `\` or `^`), and what it leaves out as
  `config.csv` says. Anything it cannot use is named; a command that would
  fail leaves the window as it was.
- **Save settings… and Load settings…:** the command as a small text file
  with a note of what it is; loading sets the window from it. **Copy** puts
  the command on the clipboard.
- **`church_year_web.py --settings FILE`** reads such a file; options after
  it win.
- `web/verify_pages.py` pastes each case's command into a fresh window and
  finds it sets the same command again.

### Changed

- **HKBP** opens in the Alkitab Terjemahan Baru: its online almanac prints
  its Indonesian texts from the TB and names it.

## 2026-10 (72) — GKLI in the Alkitab Terjemahan Baru

### Added

- **The Alkitab Terjemahan Baru (TB)**, the Indonesian Bible Society's
  translation, in the Bible menu under Indonesian. GKLI opens in it: the
  Almanak GKLI 2026 quotes its Indonesian verses word for word (Yes 41:13,
  48:17; Yer 4:27, checked against Bible.com's TB).
  - Bible Gateway does not carry TB, so its readings open at Bible.com
    whichever site Open in names, and a set's heading opens nothing (Bible.com
    shows one passage at a time). `lib/links.py` does the same
    (`NOT_AT_BIBLE_GATEWAY`), so the lists agree.

### Fixed

- `web/verify_links.py` ran short of the `--links` setting from (71); it
  checks TB links too now.

## 2026-10 (71) — A page without links

### Added

- **`--links`** (`page_links` in `config.csv`): `all` (the default), `none`,
  or `bible` and `feasts`. Without `bible` the readings and set headings are
  plain text, the Bible and Open in settings leave the page, and Download's
  readings list has no *with links*; without `feasts` the commemorations'
  names are plain text and the feasts list has no *with links*.
- **Make a page:** *Links* under Settings it shows: to the Bible and about the
  feasts, either, or none. Without Bible links the window drops its Bible,
  Open in and Bible menu choices; choosing none sets Song search to none
  (it is a link too), which can be set back. `web/verify_pages.py` makes pages
  with none and with feast links only.

## 2026-10 (70) — A page without Download or Make a page

### Added

- **`--no-download` and `--no-make-page`** (`page_download` and
  `page_make_page` in `config.csv`, TRUE unless set) leave Download… and
  Make a page… off the page; `--download` and `--make-page` put them back over
  `config.csv`.
- **Make a page** has both under *Settings it shows*, starting as this page
  has them; the command line names them when they differ from `config.csv`.
  `web/verify_pages.py` makes pages without each.

## 2026-10 (69) — Colors church by church

### Added

- **A color change for one church:** `lutheran:wels-one-year:RED-c00000`
  (its tradition, then its key) changes that church's red alone, and wins over
  its tradition's change, which wins over every church's. Links,
  `--color-changes` and `page_colors` (which check the church is on the page
  and in that tradition) and the Colors window all take it.
- **Make a page's colors:** *Change them* for all the churches together,
  tradition by tradition, or church by church (each church under its
  tradition, after the tradition's own row of changes). It starts as fine as
  the changes already made; changes a coarser choice does not show are kept
  and counted, with a button to put them back. Each color offers its own
  shades first, then every other church's on the page.

## 2026-10 (68) — Colors by tradition

### Added

- **A color change for one tradition:** `lutheran:PURPLE-7a1f7a` changes
  purple for the Lutheran churches only, and wins over a change for every
  church (`PURPLE-7a1f7a`). It works in a link's `colors=`, in
  `--color-changes` and `page_colors` (which say so when a tradition is not
  on the page), and in the Colors window, which changes the tradition's color
  where it already has a change of its own.
- **Make a page's color list** has a section for every church and one to open
  for each tradition ticked. Each color has a picker and swatches to click:
  the tradition's own shades first, then the other traditions' (pointing at
  one names whose it is); × puts it back.
- **web/verify_pages.py** carries tradition changes through the window, the
  command line and the made page.

## 2026-10 (67) — Make a page: a list of colors to change

### Changed

- **Make a page:** *Colors* is now a list to open, not just a text box: a
  swatch for each day color the ticked churches use, for outside the year,
  and for each ring and its words, starting from the changes on screen.
  - A change is made by name, as `--color-changes` makes it, so it reaches
    every church on the page with that color; beside each name are the
    churches' own shades (pointing at one names whose it is).
  - **×** puts a color back; the line under the list keeps the changes as
    text, to paste in from a link or copy out.

## 2026-10 (66) — Make a page: a + to open each tradition

### Changed

- **Make a page:** each tradition in the churches list has a + (− when open),
  and clicking the + or the name opens and closes it; only the box ticks.
  Its churches start one step further in, so the tree reads at a glance.
- The church it opens on stays the church on screen when it is ticked again
  after None.

## 2026-10 (65) — Download: the year at a glance

### Added

- **The year at a glance** in the Download window's lists: the overview
  `colors.py --overview` writes, one row a year with its movable dates and
  how many Sundays it holds, in CSV, HTML, JSON or Markdown (as CSV when
  iCalendar is the format chosen, since it has no calendar form).
  - **web/listings.js** ports `new_year.py`'s `overview`.
  - **web/verify_lists.py** adds 80 overview cases (one year and ten, the
    four formats, ten churches), all identical to the script's, and takes
    `--list` to check one kind of list.

## 2026-10 (64) — Make a page: every church and every option

### Changed

- **Make a page…** now has every option `church_year_web.py` has, each
  starting as the page is now.
  - **Churches:** a box for each church, series and hymnal, under its
    tradition and church, with All, This tradition, This church, Only this
    one and None to start from.
  - **It opens:** the church, calendars, year, zoom, Feasts, Latin names,
    text on mid-tone colors, Readings boxes, Bible, Open in, Song search,
    rings, changed colors and artwork, each its own choice; *As this page
    opens* puts them back to the page's own.
  - **A picture of your own** (SVG, PNG, JPEG, GIF or WebP) with its credit
    and size, carried in as `--art FILE` carries it.
  - **Bible menu:** any languages and versions, as `--bible` takes them.
  - **File name** (`-o`), and *The same page from Python*: the command line
    for what the window is set to.
- **web/verify_pages.py** sets the window six ways (two pictures of your own
  among them), runs the command line it shows, and finds the tables and
  markup the same; each made page makes the same page again.

## 2026-10 (63) — Make a page: a page like this one, made from the page

### Added

- **Make a page…** under Share writes a page like the one it is on, without
  Python, as `church_year_web.py` builds it.
  - **Churches:** every church on the page, its tradition, its church (every
    series and hymnal), or only the one shown (`--churches`).
  - **Opens:** with the settings on screen (church, calendars, Feasts, Latin
    names, Readings boxes, Bible, Open in, Song search, rings, colors, artwork,
    zoom) and on the year shown, or not.
  - **Shows:** the Calendar, Easter, Artwork and Dark text on reds settings
    (`--show`, `--fixed`); the Bible menu (`--bible`); the lines under the
    wheel (`--footer`); a feedback link (`--feedback`); with or without the
    `<html>` wrapper (`--fragment`).
  - **web/verify_pages.py** makes four pages in a browser and builds them
    with the script: tables and markup are the same, and a made page makes
    the same page again.

### Fixed

- The Download and Make a page windows no longer grow past a phone's width
  when a menu choice is long.

## 2026-10 (62) — Download: the readings, colors and feasts lists from the page

### Added

- **Lists in the Download window.** It also makes the three lists the scripts
  write — Readings (lectionary.py), Colors (colors.py) and Feasts (feasts.py)
  — in CSV, HTML, iCalendar, JSON or Markdown, over the years chosen.
  - **Settings:** the lists follow the page's own settings: the church and
    its calendars, Latin names, the Feasts setting, the Readings boxes, and
    the Bible and Open in for the links.
  - **Options:** readings with links; colors for Sundays and principal days,
    every named day or every day, with or without the other colors; feasts
    with the major days and with links.
  - **web/listings.js** is the port, function by function, of the three
    scripts' writers and of lib/listing.py.
  - **web/verify_lists.py** runs 870 cases (10 churches, one year and two, the
    five formats, the options) through both and finds every file identical,
    byte for byte.

### Fixed

- colors.py's JSON and iCalendar named the Easter reckoning from config.csv
  rather than the one the year was worked out by. A church with its own
  `paschalion_default` (the Coptic, Ethiopian and Syriac Orthodox churches'
  and the Ukrainian Lutheran Church's Julian Easter) was listed as "gregorian" and its calendar feed's event ids
  had no "-julian-easter". The dates were right.

## 2026-10 (61) — Download: the wheel as SVG and PNG from the page

### Added

- **Download…** behind the gear (under Share), the first part of making
  files on the page with nothing to install.
  - **What it saves:** the wheel as SVG and/or PNG, for the year on the
    wheel or a run of up to 50 church years, with every setting behind the
    gear.
  - **SVG:** byte for byte the file church_year.py writes, since both come
    from the same drawing (`CY.renderDocument`).
  - **PNG:** made in the browser at the width asked for (config.csv's
    `png_width`, 5000), on a clear or white background.
  - **Names:** files are named as church_year.py names them; more than one
    come in a .zip.
  - **Your own picture:** a `center.svg` (or other picture) beside the page
    goes into the files when the page is served from a web server.

### Fixed

- The Download window fits a phone's width: the background menu no longer
  stretches it, and the PNG's width and background are on a line of their own.

## 2026-10 (60) — a set's readings together; hymn and song search; keys go round the year

### Added

- **Sets open together:** on the page, each set's name (*Readings*, *Daily
  Lectionary*, a feast's name …) opens all its readings together at Bible
  Gateway, every choice of each (both A and B of "A or B"). lectionary.py's HTML (each set's
  heading) and JSON (each set's `url`) do the same with `--links`.
- **Song search:** a small ♫ mark after each set searches Word to
  Worship (wordtoworship.com) for worship songs on its readings.
  - It has a *Song search* box in the settings and a link's
    `songs=1|0`.
  - `church_year_web.py --word-to-worship on|off|none` (`page_word_to_worship`)
    sets it: off opens with the box unchecked, and none leaves out the box
    and the marks.
- web/verify_links.py checks the set links and the search links against
  lib/links.py: 67,276 cases, identical.

### Changed

- **Arrow keys:** they go round the church year on the wheel. A week or a
  month past the last week comes back in at the first, and the other way.
  The ◀ ▶ buttons and Page Up / Page Down still go on into the next or
  previous year.

## 2026-10 (59) — the WELS one-year series

### Added

- **WELS One-year** (`wels-one-year`): Christian Worship 2021's historic
  series. The WELS now has a Lectionary menu, *One-year* and *Three-year*,
  as the LCMS does.
  - **Readings:** from the Wartburg Project, with the Psalm of the Day from
    the hymnal's Psalm Appointments.
  - **Latin names:** the Sundays' Latin names (Ad Te Levavi, Invocavit,
    Misericordia Domini, Exaudi…) are shown by default for the one-year
    series only.
  - **Calendar:** the Transfiguration comes before Septuagesima,
    Sexagesima and Quinquagesima. The Sundays after Pentecost are counted
    after Trinity, and there is no Baptism of Our Lord.
  - **Reformation and All Saints:** named on their Sundays beside the
    Sunday after Trinity, which keeps its readings.
  - **Last Sunday:** the Last Sunday of the Church Year has only its psalm,
    because the Wartburg Project lists no readings for it.

### Changed

- The WELS three-year calendar's key is now `wels-three-year` (was `wels`).
- **Keys on the page:**
  - ← and → step a week round the wheel.
  - ↑ and ↓ step a day, as the ◀ ▶ buttons do.
  - Shift with any arrow still steps a month.
  - Ctrl+arrow and Option+arrow no longer do anything on the page; they are
    left to the browser and the system.

## 2026-10 (58) — the WELS Psalm of the Day

### Added

- WELS (Christian Worship 2021): the Psalm of the Day for every Sunday and
  festival of the three-year series, the minor festivals, New Year's Eve
  and Thanksgiving. They come from the hymnal's Psalm Appointments table
  (pp. xxxi–xxxiv). Advent 1's alternative psalm goes with its alternative
  readings, and the Last Sunday's with Christ the King. Psalm 119A–E are
  given the verses of Christian Worship: Psalter's settings of those
  numbers.

## 2026-10 (57) — the rest of the Byzantine services

### Added

- Eastern Orthodox, UGCC and Ruthenian: the other lessons of the services,
  from the OCA's daily lectionary, under *Office lessons*.
  - **Vespers:** the lessons for the great feasts, fixed and movable (Palm
    Sunday, Mid-Pentecost, the Ascension, the Fathers, Pentecost, All
    Saints), and for 56 saints and feasts of the Menaion. Each is listed on
    the feast's own day; Vespers is sung the evening before.
  - **The eves of the Nativity and Theophany:** the Royal Hours, the
    Vespers lessons and the Great Blessing of Water. The Blessing is listed
    on Theophany too.
  - **Holy Week:** Great Thursday's Sixth Hour and Washing of the Feet,
    Great Friday's Royal Hours, and the fifteen lessons of Great Saturday's
    Vespers.
  - **Composite lessons:** the OCA's composite lessons are given by chapter,
    marked "(selected verses)", because the OCA does not print their verses.

## 2026-10 (56) — the Roman Proper of Saints

### Added

- Roman: the Proper of Saints from the US Lectionary, in
  data/readings/roman-saints.csv, keyed by the feasts' ids.
  - **Feasts:** every feast roman.csv lacked, including St. Stephen, St.
    John and the Holy Innocents on 26–28 December.
  - **Memorials:** those the Lectionary gives proper readings for, such as
    the Holy Name, Barnabas, Martha, Mary and Lazarus, Our Lady of Sorrows
    and the Guardian Angels.
  - **United States:** Our Lady of Guadalupe as a feast with its own
    readings.
  - **Source:** Felix Just's table, checked against the USCCB on 21 days.
    Two citations follow the USCCB (docs/source-errors.csv).
  - **Not included:** memorials whose readings all come from the Commons,
    and Sts. Joachim and Anne.

## 2026-10 (55) — the Gospels of Matins

### Added

- Eastern Orthodox, UGCC and Ruthenian: the Gospel of Matins, as the OCA's
  daily lectionary gives it, under *Office lessons*.
  - **Sundays:** the eleven Resurrection Gospels in turn, from All Saints'
    Sunday to the fifth Sunday of Lent, and those the Pentecostarion
    appoints.
  - **Movable days:** Palm Sunday, Holy Week (the Twelve Passion Gospels
    on Great Friday), the Ascension and Pentecost.
  - **Great Feasts:** the Twelve Great Feasts. When one falls on a Sunday,
    its Gospel is read in place of the Sunday's.
  - **Saints and feasts:** 52 from the Menaion, none on a Sunday (when the
    Resurrection Gospel is read), on the Ascension, or in Holy and Bright
    Weeks.
  - **Checks:** the Sunday rule was checked against the OCA for every Sunday
    of 2025-26, and against the great feasts that fell on Sundays from 2022
    to 2030.

## 2026-10 (54) — shorter JSON; lists A to Z; Feedback lower

### Changed

- The JSON the listings write is much shorter: each year and each day is one
  line, a day no longer repeats its church year (its date gives it), and
  colors.py gives the settings all the years share (calendar, Easter,
  calendars laid over, Latin names, feast level) once at the top, leaving each
  year its church year, start and end.
- `--list` (lectionary.py, colors.py, feasts.py, church_year.py) lists each
  tradition's churches alphabetically by name, as the page's menus do.
- The page's Feedback button sits a little lower under the gear, so it is not
  clicked by mistake on the way to Settings.
- The page's series menu (the LCMS's Lectionary: One-year, Three-year) is
  alphabetical too; a hymnal still opens on its first series.
- The page's Bible menu groups the versions by language: English first, then
  Danish, Finnish, German and the rest by language name, each A to Z by
  abbreviation. A page offering only one language shows no group headings.

## 2026-10 (53) — a zoom menu; 0 goes back; quiet days

### Changed

- The magnification beside the slider is a menu, 1× to 6× by halves (a zoom
  in between, from the mouse wheel or a pinch, is shown as an extra entry).
- `0` shows the whole wheel and, pressed again, returns to the zoom it left
  (the first time on a page built with `--zoom`, to that).
- A day with no readings of the kinds checked leaves the readings box blank,
  rather than saying so.

## 2026-10 (52) — a week or a month at a key

### Added

- The page's keys: Ctrl+← / Ctrl+→ step a week (Option+arrow on a Mac,
  where Ctrl+arrow switches desktops), Shift+← / Shift+→ a month back or on,
  to the same weekday of the same week (the third Sunday to the third Sunday;
  a fifth the month lacks becomes its last), into the next or previous church
  year as needed.
- ↑ and ↓ step as ← and → do (↑ back, ↓ on), with Ctrl and Shift too.

## 2026-10 (51) — church_year_web.py takes the other scripts' options

### Added

- church_year_web.py: `--church KEY`, `--subcalendar KEY` (repeatable, or
  `none`), `--feasts`, `--latin-names` / `--no-latin-names`, `--mid-text` and
  `--bible-default VERSION` set what the page opens with, as config.csv's
  `lectionary`, `subcalendars`, `feast_detail`, `latin_names` and `mid_text`
  do (each wins over its line); `-o/--output` and `--list` as in the other
  scripts (`--out` and `--list-churches` still work).

### Changed

- church_year_web.py's `--colors` is `--color-changes`, so as not to clash
  with the listings' `--colors all|primary`.

## 2026-10 (50) — which readings a page shows at first

### Added

- church_year_web.py `--readings KINDS` (config.csv `page_readings`): the
  Readings boxes checked when the page opens (`all`, `none`, `day,feasts`,
  `-daily,-office` ...). Reset settings returns to them, and a link writes
  `readings=` only when the boxes differ from them (`readings=all` when every
  box is checked on a page that opens with fewer).
- And for the rest of the gear that had no default of its own:
  `--hide RINGS` (`page_hide`), `--color-changes CHANGES` (`page_colors`, as a link's
  `colors=`) and `--bible-site` (`page_bible_site`). Links write `hide=none` /
  `colors=none` when a page opening with some is shown with none; Reset colors
  goes back to the page's own colors.

## 2026-10 (49) — publishing to here.now

### Added

- tools/publish.py: builds the web page and publishes it to a here.now site
  in one step (`python tools/publish.py --site crisp-nimbus-6xz9`), as its
  index.html, with any `--add` files beside it; unchanged files are not sent
  again, and the version before stays in the site's Versions panel.
  `--password` sets or changes the site's password (asked for, not echoed),
  `--no-password` removes it, `--dry-run` only lists the files. The API key
  is read from `HERENOW_API_KEY` or `~/.herenow/credentials`; only Python's
  standard library is used.
- tools/publish.py `--no-page`: publish only the `--add` files, with no
  index.html built or uploaded.

## 2026-10 (48) — a Feedback link

### Added

- The web page has a **Feedback** link under the gear (church_year_web.py
  `--feedback URL`, config.csv `page_feedback`, set to the project's Tally
  form). It opens the form in a new tab with the day on screen: the page's
  link to it, the date and the church (`link=`, `date=`, `church=`, or
  `{link}`, `{date}`, `{church}` placed in the address; a `mailto:` address
  gets them in the message). No address, no link; it is left off a print.
- The Feedback link is a small button hanging under the gear, so the bar
  keeps its height and the readout beside it does not move; on a phone it sits
  beside the gear.

## 2026-10 (47) — a page that opens zoomed in

### Added

- church_year_web.py `--zoom N` (config.csv `page_zoom`): the page opens at
  that magnification, 1 to 6, centered on the day it opens on. A link's own
  `zoom=` wins, and a link writes the zoom only when it differs from the
  page's own.

## 2026-10 (46) — a picture beside the page; dated readings; old year folders no longer read

### Added

- The web page looks for `center.svg` (or `center.png`, `.jpg`, `.jpeg`,
  `.webp`, `.gif`) in the folder it was opened from. When there is one it is
  offered in the Artwork menu as "center.svg (beside this page)" and the page
  opens on it, cut to the center circle (`art=local` in a link; a link naming
  other artwork wins; `--fixed artwork` turns it off). Nothing is uploaded.
- A fifth Readings box, *Other dated days* (`dated`): the readings of days the
  calendar does not name, kept by a date or a date rule — the Ember and
  Rogation Days of BCP 1928 and 1962, Dominion Day, Thanksgiving where the
  calendar has no such day, the RCL's New Year's Day, Norway's national days,
  the German days of remembrance, the ELS Founders' Day, and the Byzantine
  Saturdays before and after the Exaltation, the Nativity and Theophany. It
  shows only for a church that has such sets; `readings=-dated` in a link,
  `lectionary.py --readings -dated`.

### Changed

- A set keyed beside the day's own propers ("Christmas Dawn (Proper II)") is
  the day's; Wales's St David and Common Worship's Corpus Christi count as
  feasts.

### Removed

- Year folders made by older versions of new_year.py are no longer read
  (folders without traditions.csv or a tradition's folder, or with
  `feasts_festivals_commemorations.csv`, no year_feasts.csv or no halves.csv);
  remake such a year with new_year.py. feasts.csv no longer takes
  `lectionary` for its `variant` column, and a year_feasts.csv row with a
  blank `level` counts as `all`. church_year.py, new_year.py and
  export_data.py stop with a clear message when traditions.csv or a
  tradition's folder is missing.

## 2026-10 (45) — church_year.py's command line; your own artwork; readings by kind; data/LCMS/LSB; old names removed

### Added

- church_year.py takes a church and a year like the other scripts
  (`church_year.py roman 2027`), and `--from/--to` (a wheel a year), `--list`,
  `--calendar`, `--paschalion`, `--subcalendar`, `--latin-names`, `--feasts`,
  `--art KEY|FILE` (with `--art-credit`, `--art-scale`), `--credit`,
  `--mid-text` and `--hide RING`, and `-o/--output` (a file or a folder). A
  year is drawn from a scratch copy: config.csv is not rewritten, and the
  drawing is the one new_year.py and church_year.py would have made. With no
  options it draws `./data` as before. A named church writes
  `KEY_YYYY-YY_calendar.svg`.
- Your own picture in the middle: `--art`, or config.csv's `center_svg`, takes
  an .svg, .png, .jpg, .gif or .webp file, looked for in the current folder,
  then the project folder. A photo is cut to the center circle; it has no
  credit unless `--art-credit` (`center_svg_credit`) gives one.
  church_year_web.py `--art FILE` puts it in the page's Artwork menu and opens
  on it. `center_svg,none` now leaves the middle empty.
- The page's Readings box is a group: the day's propers, feasts and festivals,
  the daily lectionary and Office lessons, each of which can be turned off;
  only the kinds a church has are shown. The link writes `readings=none`,
  `readings=day,feasts` or `readings=-daily,-office`. lectionary.py has
  `--readings` to match (`--no-daily` is now `--readings -daily,-office`).

### Changed

- The web page leaves out the Calendar and Easter settings unless it is built
  with `--show calendar,easter` (config.csv `page_show`); each church keeps its
  own.
- A feast the wheel does not show (left off by the Feasts setting, outranked,
  moved, or from a calendar not laid over) has its readings left off too, on
  the page and in lectionary.py, which now takes `--feasts`. Readings keyed to
  a date that is not a feast's (Ember days, weekdays, Christmas Day) stay.
- The LCMS's Lutheran Service Book files are in data/LCMS/LSB, beside LW, TLH
  and ELHB.

### Removed

- The names kept only for old links and commands: the keys `three-year`,
  `one-year`, `anglican-tec-1979`, `lcms-lw-three-year` and
  `lcms-lw-one-year` (traditions.csv no longer has rows outside the menus);
  feasts.py's `--great-days` and `great_days_exclude`; the old LCMS series
  names in colors.py's iCalendar UIDs (an LCMS feed imported before will add
  its events again rather than update them).

## 2026-10 (44) — tidier CSV files

### Changed

- The data files' comments that hold a comma are in double quotes, so a
  spreadsheet shows each in one cell instead of splitting it across columns
  (600 lines in 64 files). Every reader skips a comment either way; the
  calendars are unchanged.
- traditions.csv: the old names kept for links (`lcms-lw-three-year`,
  `lcms-lw-one-year`, `anglican-tec-1979`) are grouped at the end under a
  comment saying what they are for.

## 2026-10 (43) — "major days"

### Changed

- feasts.py: the great days are now the **major days**: `--major-days`
  (`--no-major-days`), level `major day`, and the tradition setting
  `major_days_exclude`. The old names (`--great-days`, `great_days_exclude`)
  still work.

## 2026-10 (42) — a Colors menu

### Added

- The page's settings have a **Colors…** button under the Rings. It lists the
  colors on the wheel this year (the days' colors the year uses, the cells
  outside the year, and each ring's fill and words) with a swatch to change
  each. The wheel is redrawn with the new colors, a day's text turns black or
  white if it would no longer read, and the changes go into the page's link
  (`colors=`); Reset colors and Reset settings put them back. The data files
  and church_year.py are unchanged by it (docs/web-page.md, and the user
  guide: the Colors window, Esc, and `colors=` in links).

## 2026-10 (41) — ring labels in every renderer; option order; NIV for LW

### Fixed

- A ring label with a subtitle ("FESTIVAL HALF: About the Savior") is two
  runs that meet at one measured point along the arc, instead of two tspans
  of one centered run, which some PNG rasterizers anchored one by one, off
  center and overlapping the next label. The SVG looks as before.
- colors.py and feasts.py html: a color with its swatch ("blue (or violet)")
  no longer wraps.
- church_year.py --report: a name a day's title already carries (All Saints'
  Day on its Sunday) is listed as drawn once, not as a label needing
  attention.

### Changed

- Options that set how much to include list the most first (`--feasts all,
  festivals, principal, none`; `--days all, named, principal, sundays`);
  options that are only a choice stay alphabetical (`--png-renderer`,
  verify.py `--calendar`).
- LCMS (LW): links open in the NIV.

## 2026-10 (40) — daily readings: Roman weekdays and the Byzantine weekdays and saints; the Church in Wales and Divine Worship calendars

### Added

- Roman: the weekday Mass readings (data/readings/roman-weekday.csv) for
  Advent with 17–24 December, Christmas Time, Lent, Easter weeks 2–7 and
  Ordinary Time weeks 1–34, Year I and II (Year II from Advent 2025), from
  Felix Just's tables of the US Lectionary. Thirteen citations the tables
  were read wrongly for are corrected (listed in the file). Not yet: the
  Proper of Saints and 26–28 December.
- Eastern Orthodox, UGCC and Ruthenian: the Liturgy Epistle and Gospel of
  every weekday, as rules (the Triodion and Pentecostarion by Pascha; the
  weeks after Pentecost, with the Lukan jump and the counting back from
  Zacchaeus), and the readings of 70 saints and feasts of the Menaion and the
  movable Saturdays, from the OCA's monthly lectionaries; checked against
  790 of 792 weekdays. The OCA's American saints are for the OCA only.

### Changed

- Church in Wales: the calendar of *The New Calendar and the Collects* (2003),
  the one its lectionary booklets follow, from Advent 2003 (`year ge 2003`):
  Sundays of Epiphany to the Presentation, Sundays before Lent, of Lent and of
  Easter, after Trinity to the Last Sunday after Trinity (Bible Sunday), and the
  Kingdom season from All Saints (Second and Third Sundays of the Kingdom,
  Christ the King – the Fourth Sunday of the Kingdom); Thomas on 3 July, the
  Visit of the Virgin Mary to Elizabeth on 31 May, Thanksgiving for Holy
  Communion, and the newer commemorations, with the booklet's names. The 1984
  Prayer Book's year (Septuagesima, Thomas 21 December, the Visitation 2 July)
  holds for earlier years. The Church in Wales readings now fall on days the
  wheel names.
- Divine Worship: the calendar follows *Divine Worship: The Missal* and its
  Table of Liturgical Days (`precedence,roman`). The Sundays are "of Advent",
  "of Christmas" and "of Easter" (the Second to the Seventh, with Good
  Shepherd and Rogation Sunday; no "Sunday after Ascension Day"), and the
  Sunday after 6 January is the Baptism of the Lord. All Saints and the feasts
  of the Lord replace a green Sunday, with its readings; saints' feasts and
  memorials on a Sunday, in Holy Week or the Easter octave are omitted; an
  impeded solemnity is transferred (the Annunciation in Holy Week to the
  Monday after the Second Sunday of Easter, St Joseph to the Saturday before
  Palm Sunday). The Missal's full names (Passion Sunday, Septuagesima "or the
  Third Sunday before Lent", Whitsunday, Christ the King) are in the readout.
  The Sundays of Easter of Years B and C now have the Lectionary's readings.
  The Epiphany stays on 6 January and Corpus Christi on Thursday, as in the
  Missal's universal calendar; the Ordinariate of the Chair of St Peter moves
  both to Sunday and keeps the Chair of St Peter as its Solemnity of Title.

## 2026-10 (39) — readings for Divine Worship, the Church in Wales and the 1962 Missal; the 1928 and 1962 books checked

### Added

- Roman 1962: the propers of the Mass under the rubrics of 1960 (Introit,
  Lessons, Epistle, Gradual, Gospel) for every Sunday, the temporal feasts,
  the Ember days, every weekday of Lent, Holy Week (1955 Ordo), the Easter and
  Pentecost octaves, Rogation Monday and the I-III class feasts, from Divinum
  Officium. Links open in the Douay-Rheims; the Vulgate psalm numbers are given
  the Hebrew way and translated in links, as for the modern Roman calendar.
- Divine Worship (the Personal Ordinariates): the Sunday and holy-day Mass
  readings. They are the Roman Lectionary's, now shared
  (`data/readings/roman.csv`, `readings,roman`), with the citations of the
  Ordinariate's Ordo for 2025-26 put in where they differ: its Coverdale
  psalms, the RSV-2CE's numbering and half verses, Year A and Advent and
  Christmas of Year B; also the Chair of St Peter, Our Lady of Walsingham and
  the saints' feasts with proper readings. Years B and C have the Lectionary's
  Lessons, Epistles and Gospels but no psalm, and no Sundays after Easter yet.
- Church in Wales: the Principal Service readings, as the Revised Common
  Lectionary with the Church in Wales changes (Epiphany 4, the Second Sunday
  before Lent, Trinity Sunday, the Kingdom Sundays, the holy days, Mothering
  Sunday, Bible Sunday), its holy days moved as the booklets move them, and
  22 Welsh saints, from the Year A (2025-26) and Year B booklets and Book Two.
- BCP 1962: the Ember and Rogation Days (with the book's second sets: Peace in
  the World, Missionary Work, Unity, Labour and Industry, the Fruits of the
  Earth), Wednesday to Saturday in Easter week, Whitsunday's second service,
  Dominion Day (1 July), All Souls and Founders and Benefactors.

### Changed

- BCP 1962: every set checked against the book (the anglican.ca PDF). Trinity
  7's Gospel ends at Mark 8:9 and Trinity 20's Epistle at Ephesians 5:21 (the
  Society's chart had 8:10 and 5:20); SS Simon and Jude has Revelation 21:10–14
  or Jude 1–4; Christmas, Easter Day and St Peter and St Paul have each set's
  own psalms; the Second Sunday after Christmas takes the Octave Day's
  propers, as the book directs; Thanksgiving's Old Testament reading is the
  book's own. The book's misprints are in docs/source-errors.csv.
- BCP 1928: every set checked against the book's Propers; no changes.
- The Roman Lectionary moved from `data/Roman/readings.csv` to
  `data/readings/roman.csv`; the Roman calendar's readings are unchanged.

## 2026-10 (38) — readings for the BCP 1928 and the Canadian BCP 1962

### Added

- BCP 1928 (Episcopal Church): the Epistles and Gospels for the Sundays, holy
  days, Holy Week, Easter and Whitsun weeks, the Ember and Rogation Days,
  Independence Day and Thanksgiving Day, with the second propers for
  Christmas, Easter Day and Whitsunday, from the book's text (episcopalnet.org,
  justus.anglican.org). The 25th and 26th Sundays after Trinity follow the
  1928 rubric (the Sunday next before Advent counted last).
- BCP 1962 (Anglican Church of Canada): the Epistles and Gospels and the
  book's Introit and "between the Lections" psalms for the Sundays, holy days,
  Holy Week, Easter and Whitsun weeks and Thanksgiving Day, with the Prayer
  Book Society of Canada's supplement of Old Testament lessons, labeled as the
  Society's. Links open in the KJV.

### Fixed

- BCP 1662: the Gospel of the Sunday after Christmas is Matthew 1:18–25 (not
  1:18–21) and that of St Philip and St James John 14:1–14 (not 14:1–4).

## 2026-10 (37) — Latvia's verses; page_bibles for files; a faster colors.py

### Changed

- Latvia: the nine citations its source prints in the English numbering (as
  the RCL gives them) are given in the Latvian Bible's, and Latvia's links
  translate (`verse_numbering,hebrew`), so the Bible and the links agree; the
  six that fit neither numbering are as printed (docs/source-errors.csv).
- lectionary.py `--links` opens in the version the web page would: within
  config.csv's `page_bibles` (with `page_bibles,english` a German church's
  links open in ESV, not the Luther Bible), and a `--bible` the page would not
  offer is refused. web/verify_links.py checks the defaults under such limits.
- colors.py writes year after year into one scratch folder, copying the
  traditions' folders once: a hundred years in a few seconds instead of half a
  minute, with the same output.
- The Moravian Church's center picture changed.

## 2026-10 (36) — the churches' own verse numbers, translated in links; feasts.py great days

### Changed

- Readings are cited again in the numbering each church's Bible uses: the
  Hebrew one (psalm headings counted, Malachi in three chapters) for the EKD,
  Poland, Norway, Denmark, Finland, Estonia, Iceland and Hungary, in the Psalms
  for Sweden, Slovakia and the HKBP, and as printed for Latvia. A
  `verse_numbering` setting names it, and the Bible links translate it, so
  Bible Gateway and Bible.com open at the same verses (the NABRE, numbered the
  Hebrew way there too, is not translated). The Roman readings say
  `verse_numbering,hebrew` as well, so a version other than the NABRE opens
  right. ELHB's 1 Kings 22:52 stays 22:51 (the LCMS's Bibles number it so).
- Only a day whose two colors are both its own (the day before's above, the
  day after's below: Christmas Eve, Holy Saturday) splits its name over them;
  Reformation Day observed keeps its name on the red again.

### Added

- feasts.py `--great-days`: also the year's great days, each principal day
  days.csv sets on a date of its own (Christmas, the Epiphany, Easter, the
  Ascension, Pentecost, Trinity, Reformation, All Saints ...), not the Sundays
  of a season's run or of a named sequence (Sexagesima, Exaudi, the Sundays of
  the Triodion ...; a tradition can name more in `great_days_exclude`); level
  `great day`, before the day's feasts; with `--feasts none`, the great days
  alone. Off by default.
- lectionary.py and feasts.py take `--data`, the folder of rules, as colors.py
  does; `--list` follows it in all three.
- docs/summaries.md is now docs/listings.md.

## 2026-10 (35) — colors.py and feasts.py; English verse numbers; names over two colors

### Added

- `feasts.py`: a church's feast days for a year, as the wheel places them
  (transfers included), with `--feasts`, `--colors` and `--links` to read
  about each; CSV, HTML, iCalendar, JSON or Markdown.
- `lectionary.py --links [biblegateway|youversion]` and `--bible VERSION` link
  each citation as the page does; it also takes year spans, `--subcalendar`,
  `--calendar`, `--paschalion` and the Latin names.
- `lib/listing.py` (what the three listing scripts share), `lib/links.py` (the
  page's links in Python) and `web/verify_links.py` (the two compared).
- docs/versification.md: the Hebrew and English verse numberings, and what the
  calendar does with them.

### Changed

- `year_summary.py` is now `colors.py`: church and year as arguments,
  `--from`/`--to` as years or dates, csv, html (with color swatches), ics, json
  or md, `--days all|named|principal|sundays`, `--colors primary|all` (the
  colors allowed and the lower half's), `--overview`. It writes to the screen
  unless given `-o`; the color files are no longer kept in the package.
- `calendars.py` and `traditions.py` are in `lib/` with the other shared modules.
- Every citation is in the English verse numbering that current Bibles and
  Bible sites use. The EKD, Poland, Norway, Denmark, Finland, Estonia, Iceland
  and Hungary (and the psalms of Sweden, Slovakia and HKBP, and Latvia's
  plainly Hebrew-numbered citations) were printed in the Hebrew numbering,
  correct for the Bibles they followed; docs/source-errors.csv notes each.
  The Roman readings keep the NABRE's numbering, which the links open in.
- A day of two colors with only its own name (Christmas Eve, Holy Saturday,
  Maundy Thursday where it has two, Reformation Day observed) puts its first
  words on the upper color and the rest on the lower, each in that color's
  text color; Advent 4 on Christmas Eve gives each name its color.
- README: the lists start with capitals; the scripts and lib/ are listed.

## 2026-10 (34) — Poland from its own 2018 order; ELHB 1 Kings 22:51

### Changed

- Poland's readings now come from its own order (Nowe perykopy liturgiczne
  2018 and its table, liturgika.pl) instead of being shared with the EKD:
  89 of 103 days were the same; the rest now follow the Polish text (psalm
  alternatives, the Augsburg Confession's Nehemiah 7:72c, Stephen's sermon
  text, Matthias' series order, and others). The Transfiguration (6 August)
  and the miners' service (4 December) are added. Two misprints in the Polish
  documents are recorded in docs/source-errors.csv.
- ELHB, Friday after Trinity 11, evening: 1 Kings 22:51 (the book's 22:52 is
  the German/Hebrew verse count; the link missed the verse).

## 2026-10 (33) — Bible versions per page; Poland's own days; Byzantine feasts on Sunday

### Added

- `--bible` (`page_bibles` in config.csv): the Bible versions a page offers:
  one version (no menu), a list, a language (`english`, `de` ...) or `own`
  (each church's own, no menu).
- Poland: its fixed days (apostles, evangelists, Mary, the Augsburg Confession,
  Michael, Martin, Nicholas, All Saints, Pamiątka Umarłych on 1 November),
  named as the church's 2018 table of pericopes (liturgika.pl) names them,
  with their readings; the German-titled sets are now Pasterka i Jutrznia,
  Wielkanoc rezurekcja (on Easter morning), Pamiątka Umarłych and Izrael
  (Luke 19:41-49, as the Polish table has it).

### Changed

- Eastern Orthodox and Byzantine Catholic: the Nativity and Theophany take
  the place of a Sunday they fall on (the Sundays are still counted past
  them); in the Ruthenian calendar Zacchaeus Sunday gives way to Theophany
  (6 January 2008).
- The Roman Catholic and Divine Worship series menu is now **Missal**, so it
  is no longer a second "Calendar".

## 2026-10 (32) — an audit of the whole project

### Fixed

- Readings cut short by an unquoted comma: LSB Easter Wednesday (Acts 3:13-15,
  17-19, both series) and Pentecost Monday (Acts 10:34a, 42-48); the same in a
  provenance note and a source-errors note. `tools/provenance.py --check` now
  catches a row with more fields than its header.
- Precedence (Roman, Common Worship): a moved feast no longer lands on a day
  another feast keeps on its own date. Common Worship 2022 and 2033: George on
  Tuesday 26 April, Mark on the Monday (as the 2022 CW lectionary had it); 2000:
  George 2 May, Mark 3 May, Philip and James on 1 May. Roman 1962, 2011: the
  Precious Blood moves to 4 July and the Visitation keeps 2 July.
- Common Worship: the red of the Kingdom season starts on All Saints' Day, not
  on Bible Sunday a week earlier.
- GKLI: eight LSB Daily Lectionary rows that had lost their title no longer
  double the New Year's Eve and New Year's Day readings.
- Poland: readings for the 5th Sunday before Lent and the 24th Sunday after
  Trinity (the EKD's); the EKD's saints' days, which Poland's calendar does
  not keep, no longer put German-titled readings on unnamed days.
- WELS: the minor festivals its lectionaries give readings for are now in its
  calendar (CW 2021 from 2021-22, the CW 1993 ones before); two CW 2021
  titles lost a stray " ::".
- A repeated Hebrews 8 in the RCL daily readings (Year B).
- Reading links: optional verses, "1:1-6 (7-12)", are now part of the passage
  searched.
- `--churches` pages carry only the lectionaries their churches read (a
  one-church page is about 510 KB instead of 2 MB).
- A link naming an unknown ring in `hide=` is ignored; `--fixed artwork`
  keeps each church's own picture even when config.csv names one.
- `tools/provenance.py -h` prints its usage instead of writing the page;
  `tools/clean_svg.py` asks for its three arguments.
- En dashes in LW and ELHB citations; "Savior" in three names; "Song of
  Solomon" in Latvia's readings; a broken comment in Orthodox feasts.csv;
  227 full names that only repeated the name left blank.
- Docs: the missing link parameters (reds, help, credit), --footer and
  --fragment in the user guide, page sizes, the README file index,
  verify_readings.py, flags that had no mention, `elhb` examples (the key is
  lcms-elhb-one-year), American spelling.
- The 2025-26 drawing and summary regenerated.

## 2026-10 (31) — leave out the Dark text on reds box

### Added

- `--fixed reds` (`page_fixed` in config.csv) leaves the Dark text on reds
  box out of a page; the reds stay as config.csv's `mid_text` sets them, and a
  link's `reds` is ignored.

## 2026-10 (30) — the Baptism (observed); WELS psalms inferred

### Added

- Common Worship: when the Epiphany is kept on Sunday 7 or 8 January, the
  Baptism of Christ is shown on the Monday, "(observed)", with its readings.
- WELS (CW 1993) Year A Pentecost 21-24: Psalms inferred (23, 96, 1, 43) and
  marked so.

## 2026-10 (29) — Common Worship's optional Sundays

### Added

- Common Worship: the Epiphany and Candlemas are also shown on the Sunday the
  Rules allow, as "(observed)", with their readings; All Saints' Sunday is now
  white in its lower half like them.

## 2026-10 (28) — Common Worship's transfers; WELS Pentecost 24 A

### Added

- Common Worship keeps the Rules' precedence: Festivals move off the Sundays
  of Advent, Lent and Eastertide, Principal Feasts and Holy Days (Holy Week
  and Easter Week to the Monday after Easter 2), with their readings; Lesser
  Festivals and Commemorations on Sundays and Festivals are left out.
- WELS (CW 1993) Year A Pentecost 24: readings inferred, and titled so.

### Changed

- Common Worship: when 6 January is a Sunday the Baptism of Christ is the
  Second Sunday of Epiphany and the numbers after it follow.
- WELS: Advent 1 A (Matthew 24:36-44) and Lent 4 C (Luke 15:11b-32)
  confirmed by the maintainer.

## 2026-10 (27) — Common Worship from the Church of England; WELS Christian Worship (1993)

### Added

- Common Worship: the Principal, Second and Third Service lectionary and the
  Daily Eucharistic Lectionary (`cofe-cw`, `cofe-cw-weekday`); the Calendar
  rebuilt from the Church of England's own page, with its four levels
  (Principal Feasts, Festivals, Lesser Festivals in roman, Commemorations in
  italics) and the Accession of Charles III or Elizabeth II by year.
- WELS before 2021–22: Christian Worship (1993), with its End Time Sundays
  (Reformation, Last Judgment, Saints Triumphant, Christ the King), its colors,
  its three-year lectionary with the Psalm of the Day (`cw93`) and the
  supplemental lectionary of Christian Worship Supplement (`cw93-supp`).
- TLH: the Matins and Vespers psalms of the Table of Lessons (pp. 159-160).

### Changed

- Common Worship colors from the Rules: Good Friday red (hangings removed),
  blue as Advent's option, the Lent array, rose on Advent 3 and Lent 4, red or
  green from All Saints to Advent, and All Souls purple (or black or white).
- TLH: Quinquagesima Tuesday morning is Luke 6:43-49 and the Saturday of
  Trinity 21 morning Ephesians 5:22-33, as checked by the maintainer.
- Reading links leave out notes in words ("first part"), the "Canticle:"
  label and "-end" (the whole chapter).
- The CW 1993 sources' differences, and a misprint in the Year A PCWR
  (Revelation 19:1-19 for 19:1-9), are in docs/source-errors.csv.

## 2026-10 (26) — TLH's daily lessons and psalms; LCMS calendar charts

### Added

- TLH (pp. 161-166): the Lessons for Morning and Evening, the Psalms for the
  Sundays, Feasts and Festivals, and the Psalter over thirty-one days (with
  its rules for thirty-day months and the end of February).
- `reading_rotate` takes more than one id (`after_epiphany|transfiguration`),
  so TLH's Transfiguration Sunday keeps its week of lessons.
- LSB psalms for St. Timothy, St. Mary, St. Luke, the 2 July Visitation and
  the Series B and C Easter Sunrise, from the LCMS Church Year Calendars.

### Changed

- TLH Wednesday of Holy Week stays Luke 22:1-23:43 (the propers and the
  passage); the Table of Lessons' 23:42 is recorded as a misprint, with TLH's
  other misprints and the LCMS charts' inconsistent Reformation Gospel order,
  in docs/source-errors.csv.
- The 31 May Visitation readings are now the three-year series' only.

## 2026-10 (25) — checked against LSB, LW and TLH; Catholic icons; a user guide

### Added

- docs/user-guide.md: every control, key and gesture of the web page, links,
  printing and pages made for one church.
- `--fixed calendar,easter,artwork` (`page_fixed` in config.csv) leaves those
  settings out of a page and keeps each church's own; links naming them are
  ignored.
- Icons for holy days of obligation, fasting and abstinence on the other
  Catholic calendars, each by its own law: Roman 1962 (the 1983 Code),
  Ukrainian Greek Catholic, Byzantine (Ruthenian), Maronite, Ambrosian and
  Divine Worship (see docs/traditions.md, Icons). `icon_when` now also works
  in days.csv rows.
- LSB: Monday to Wednesday in Holy Week and Holy Saturday (three-year), Easter
  Monday to Wednesday and Pentecost Eve to Tuesday (both series) and the
  one-year Visitation on 2 July, from the book.
- TLH: the Table of Lessons' Old Testament lessons and Second Series of
  Epistles and Gospels; full names of the minor festivals.
- LW: full names of the minor festivals.
- docs/source-errors.csv, shown in docs/provenance.md as "Errors found in
  sources": misprints found in sources and what the calendar uses instead.

### Changed

- Checked against photographs of Lutheran Service Book (pp. x-xxiii),
  Lutheran Worship (pp. 8-9, 295-299) and The Lutheran Hymnal (pp. 3,
  159-161). Corrected: LSB C Proper 14 Gospel Luke 12:22-34 (35-40); one-year
  Trinity 12 Romans 10:9-16; Tuesday in Holy Week Mark 14:1-15:47; LW daily
  lectionary 23 January, 9 April and 9 October. LSB Maundy Thursday white
  (scarlet or violet named); LW Advent purple (or blue), Ash Wednesday black
  (or purple), Holy Week scarlet (or purple), Maundy Thursday scarlet (or
  white), Easter Day white (or gold).
- The one-year Visitation readings no longer show on 31 May.
- Conditions: `variant eq a|b` documented.

## 2026-10 (24) — first colors with their options; dated color changes; fixes from the sources

### Added

- A color can name the options its source permits after semicolons
  (`PURPLE; royal blue`): the first is drawn, the others are named in the
  page readout ("purple (or royal blue)").
- No color (`NONE`) is drawn as white hatched with gray and read "no color";
  any `colors.csv` fill written `#ground/#line` is hatched.
- `year` conditions (`year ge 2011`) in `when`, so a church's change of use
  applies from the year it was made, the older use before it.
- tools/README.md: an index of the tools.

### Changed

- Church in Wales: the 2011 color scheme from the 2011–12 year, the 1984
  colors before.
- The fixes in docs/provenance-review.md marked applied there: Armenian,
  Ethiopian, Coptic, West Syriac, Assyrian, Byzantine, Anglican Church of
  Canada, Episcopal, ELCA (and the Emanuel Nine), LCA, Iceland, Finland,
  Estonia and the United Methodist Church, each with the first-listed color
  and its options named. LSB's black Ash Wednesday stays: a published book
  is preferred to a website.
- data/LW, data/TLH and data/ELHB are now data/LCMS/LW, data/LCMS/TLH and
  data/LCMS/ELHB, and data/Roman1962 is data/Roman/1962: a church's other
  books sit in its folder.
- The one-time builders (`stage*.py`) and their source texts moved to
  tools/history; they are kept as a record and are not to be rerun.
- The Bible menu lists the versions alphabetically.

## 2026-10 (23) — sources for the uncited data and colors

### Changed

- docs/provenance.csv: sources found for most of the uncited days, feasts,
  names and colors (church calendars, lectionaries and service books online:
  the Church in Wales, the Episcopal Church, the USCCB, the 1960 rubrics,
  the Pittsburgh Archeparchy, the UGCC, the OCA, the Armenian Prelacy,
  copticchurch.net, the EOTC, Syriac Orthodox and Malankara dioceses, the
  Assyrian Church of the East, the LCMS, ELCA, WELS and LCA, Kirkemøtet,
  kirkkovuosikalenteri.fi, kirkjan.is, the UMC Book of Worship, the
  Methodist Church in Britain and the RCA); 3 rows remain uncited.
- docs/provenance-review.md: the places where the calendars' data disagree
  with those sources, each with a suggested fix, for review.

## 2026-10 (22) — a record of sources, gaps and guesses

### Added

- docs/provenance.csv: one row per claim about where a calendar's days,
  feasts, colors, names, readings or art come from, with its status
  (sourced, partial, inferred, uncited, guess, missing), source and notes;
  tools/provenance.py checks it and writes docs/provenance.md, which shows
  the same rows by church and aspect, as the open items by aspect, and by
  church.

## 2026-10 (21) — the Byzantine readings

### Added

- Eastern Orthodox, Ukrainian Greek Catholic and Ruthenian Byzantine
  Catholic: the Epistle and Gospel of the Divine Liturgy for every Sunday,
  the days of the Triodion and Pentecostarion (with the Old Testament
  lessons of Holy Week and the Matins readings of Holy Saturday), the
  special Sundays (before and after the Exaltation, the Fathers, the
  Forefathers, before and after the Nativity and Theophany) and the great
  feasts, as the OCA's monthly lectionaries give them.  The Sundays after
  Pentecost are rules (the Epistle by the Sunday's number, the Gospel by the
  number and then by the weeks of Luke after the Exaltation), checked
  against all 567 ordinary Sundays of 2024-2046; the Sundays between
  Theophany and Zacchaeus follow the OCA's order year by year to 2045-46
  (not yet for the Ruthenian calendar, whose Pascha is the Gregorian).

## 2026-10 (20) — BCP 1662 and the RCL Anglican churches

### Added

- BCP 1662 (and the IARB's LOC 1662): the Epistle and Gospel of every
  Sunday, holy day and weekday of Holy Week and of Easter and Whitsun weeks,
  from the Church of England's text of the Prayer Book; the Second Sunday
  after Christmas has the Circumcision's, a 25th or 26th Sunday after
  Trinity the Epiphany Sundays' that were left out, as the rubrics direct.
- ACNA 2019, IEAB 2015, IAB 2021, IECB 1987, LOCb 2008, the Igreja Lusitana
  and REB 2027 read the Revised Common Lectionary (ACNA with the US
  Thanksgiving Day).
- The Portuguese-speaking churches' readings open the Almeida Revista e
  Corrigida (ARC), a new choice in the Bible menu.

## 2026-10 (19) — the Roman Lectionary

### Added

- Roman Catholic: the Lectionary for Mass (USA, 1998/2002), Years A, B and
  C: every Sunday, Christmas (the Vigil and the three Masses), Holy Family,
  Mary Mother of God, Epiphany, the Baptism, Ash Wednesday, Palm Sunday
  (with the Gospel at the procession), Holy Week, the Triduum and the
  seven readings of the Easter Vigil, the Octave of Easter, Ascension,
  Pentecost and its Vigil, Trinity, Corpus Christi, the Sacred Heart and
  the solemnities and feasts that can fall on a Sunday, with their Vigil
  Masses (from Felix Just's tables at catholic-resources.org).  Links open
  the NABRE.

### Changed

- readings.csv: a row may name a feasts.csv id, so a feast's readings
  follow it when it is transferred (the Immaculate Conception on
  9 December 2024).

## 2026-10 (18) — Tanzania 2014-2018

### Added

- Tanzania (ELCT/KKKT): the psalm, readings and sermon text of each Sunday
  and feast from the Kalenda ya Biblia of 2014 (elct.org, by the Wayback
  Machine) to 2018: the church years beginning in Advent 2013 to 2017.
- ELCT: Whit Monday (Jumatatu ya Pentekoste) and the World Day of Prayer
  (Siku ya Maombi ya Dunia, the first Friday in March, violet), both kept
  in the Kalenda.

## 2026-10 (17) — readings for Hungary, Estonia, Slovakia, Latvia, GKLI, HKBP and Tanzania

### Added

- Hungary: the old-church pericope order the church took up in Advent 2023,
  a Gospel, Epistle and Prophecy for every Sunday and feast, the same each
  year ("Óegyházi perikóparend", garainyh.hu); links open the Károli Bible.
- Estonia: the EELK reads the Church of Finland's three series (as its day
  posts at e-kirik.eelk.ee show for 2026), mapped to the Estonian days; the
  Reformation texts on the 22nd Sunday after Pentecost; Harvest
  Thanksgiving's own texts for the second series.
- GKLI: Lutheran Service Book's three-year series, which its "Leksionari
  GKLI" (gkli.org) and Almanak GKLI 2026 follow, set on the GKLI's own days
  (Septuagesima to Estomihi take the Epiphany Sundays falling on them); the
  second days of Christmas, Easter and Pentecost from the almanac.
- HKBP: the Epistel and Evangelium (the sermon text) of every Sunday and
  feast in 2025 and 2026, from the church's online almanac (hkbp.or.id),
  which chooses new texts each year.
- Slovakia: the old-church lessons (Gospel, Epistle, psalm) of the ECAV's
  Agenda of 1996, "Perikopy".
- Latvia: the one-year series and the church's three-year series (Year A
  from Advent 2025), with the Palm Sunday procession Gospel, gathered from
  the daily "Dieva Vārds" pages at lelb.lv, Advent 2017 to November 2026.
- Tanzania (ELCT/KKKT): the psalm, readings and sermon text of 2018, from
  the church's Kalenda.

### Changed

- `reading_cycle,year`: a row's cycle is the year its church year begins,
  for a church that chooses its texts year by year.
- `lectionary.py --list` groups the churches by tradition and leaves out
  the old names kept only for links (`lcms-lw-one-year` ...).
- docs/adding-a-church.md: how to add a church's readings, to a new church
  or one already here, and to read a lectionary shared with others.

### Fixed

- EKD: the Last Sunday after Epiphany falls on 2 February when that is a
  Sunday (2025, 2030), as kirchenjahr-evangelisch.de has it; the 5th Sunday
  before Passiontide and the 24th Sunday after Trinity have their texts
  (from the EKHN's liturgischer-wegweiser.de).
- Iceland: the 2nd Sunday after Christmas has its series B texts
  (kirkjan.is).

## 2026-10 (16) — readings for the Lutheran churches of Europe

### Added

- EKD and Austria: the Perikopenordnung of 2018, the week's psalm, Old
  Testament reading, Epistle and Gospel and the sermon text in its six
  series (from kirchenjahr-evangelisch.de); the Lutheran Church in Poland
  reads the same order.
- Church of Sweden: Den svenska evangelieboken, three series and the four
  Passion series (evangelieboken.se).
- Church of Norway: Bibeltekster for kirkeåret, three series and the story
  texts (bibel.no).
- Church of Denmark: the two text series of the Alterbog (denfriebibel.dk).
- Church of Finland: the psalm and three series of the Kirkkokäsikirja
  (kirkkovuosikalenteri.fi).
- Church of Iceland: the three text series A-C (kirkjan.is); a few rare
  Sundays the site never gave are left without readings.
- Bible versions for them: Luther 1545, Schlachter 2000, Svenska Folkbibeln
  2015, Det Norsk Bibelselskap 1930, Dette er Biblen på dansk (1933),
  Raamattu 1933/38, the Icelandic Bible, Hungarian Károli and the Ukrainian
  Bible, each church opening in its own language.

### Changed

- `reading_cycle` takes any series and the year it starts, and several side
  by side (docs/traditions.md); new kinds of reading `sermon` (Sermon Text)
  and `story` (Story Text).

## 2026-10 (15) — ELS, LCC and WELS readings

### Added

- ELS: the three-year and historic one-year series and the saints' days,
  from the ELS's own calendars ("ELS 3-year", "ELS Historic", "ELS Saint
  Days"); the few days they never reached come from Lutheran Service Book,
  and three evident misprints are corrected (listed in data/ELS/readings.csv).
- Lutheran Church–Canada: Lutheran Service Book's readings, now shared with
  the LCMS as `data/readings/lsb.csv`; Thanksgiving falls on Canada's day.
- WELS: Christian Worship (2021), Years A, B and C, the minor festivals, New
  Year's Eve and Thanksgiving, from the Wartburg Project (no psalms there).
  The readings are called First Reading and Second Reading, as in the book.

### Changed

- The Bible menu gives each version's full name: "ESV (English Standard
  Version)".
- **Open in** starts on Bible.com on a phone or tablet (its app opens when
  installed) and on Bible Gateway on a computer.
- LSB's Thanksgiving readings serve the one-year series too.

## 2026-10 (14) — links to the readings and the saints

### Added

- `lectionary.py`: one church's readings for a year as CSV, JSON, Markdown,
  a printable HTML page or an iCalendar feed (`python lectionary.py elca
  2025 -o readings.csv`; `--list` names the churches). It works the readings
  out the way the page does, and `web/verify_readings.py` checks that they
  agree.
- ELCA: the readings of Evangelical Lutheran Worship where they differ from
  the RCL, checked against the ELCA's yearly lists: the lesser festivals'
  own readings, the twelve readings of the Easter Vigil, New Year's Eve, the
  Vigil of Pentecost, the week after Easter, Reformation Day; Easter Day's
  and Lent 2 A's Gospels; the complementary series first after Pentecost,
  and the daily readings following it alone.
- Episcopal Church: the psalms in the Prayer Book's numbering (canticles
  given as their texts), the Prayer Book's First and Second Sundays after
  Christmas, the Major Feasts and Holy Cross Day, the days of Easter Week and
  the Vigil of Pentecost, from the Lectionary Page.
- readings.csv: rows of kind `omit` drop rows of a shared lectionary, `=kind`
  rows replace one in place, and the `reading_order` setting reorders kinds
  (see docs/traditions.md).

- Each reading's citation opens the passage at Bible Gateway or Bible.com
  (chosen behind the gear as **Open in**); on a phone or tablet it opens in
  that site's app when installed. **Bible** chooses the translation; each
  church starts on its own (LCMS ESV, WELS EHV, ELCA NRSVUE, TLH and ELHB KJV
  ...), ESV otherwise. Links carry `bible=` and `bibleat=`.
- A saint's or festival's name in the readout is a link: for the LSB calendars (and
  the ELS and LCC) to Concordia Publishing House's page on each
  commemoration, otherwise to Wikipedia. The LSB calendars show each day's
  whole name (St. James of Jerusalem, Brother of Jesus and Martyr; Johann
  Walter, Kantor), where the cell has room only for the short one.
- LSB Daily Lectionary: the optional readings of 1 September–26 November,
  checked against LSB p. 302.
- RCL Daily Readings for every week, the missing ones from
  liturgical-calendar.com.

### Changed

- ELHB: corrected misprints (Exodus 1:8–22, Ezekiel 37:1–14, 1 Corinthians
  11:21–32, Isaiah 40:1–5 for St. John the Baptist and 11:1–5 for the
  Visitation); the Morning and Evening lessons after the Epiphany follow the
  book's rubric for short years, leaving out a different week each year.
- A reading that runs from one book into the next is written "1 Kings 22:52 –
  2 Kings 1:17".
- The instructions and the artwork credit under the wheel are off by default
  (`page_footer,none`).

## 2026-10 (13) — the Revised Common Lectionary

### Added

- Readings for the churches of the Revised Common Lectionary: the Episcopal
  Church, the ELCA, the United Methodist Church, the PC(USA), the Reformed
  churches, the Methodist Church in Britain, the Moravian Church in America,
  the Church of Scotland and the LCA. Years A, B and C from the Vanderbilt
  Divinity Library, with both series of Old Testament readings after
  Pentecost (Track 1 and Track 2 for the Episcopal Church).
- The RCL Daily Readings on weekdays, for the same churches.
- `data/readings/`: lectionaries that several calendars share, named by a
  tradition's `readings` setting.

## 2026-10 (12) — the day's readings

### Added

- The page lists the chosen day's Bible readings under its name, for the LCMS
  hymnals: the day's propers, those of a festival kept on it, and the daily
  lectionary, each set on a line of its own. A **Readings** box behind the
  gear turns them off (`readings=0` in a link).
  - **LSB**: the three-year series (Years A, B, C), the one-year series, the
    feasts and festivals and the Daily Lectionary.
  - **LW**: the three-year series, minor festivals and Daily Lectionary.
  - **TLH**: the Epistles and Gospels of every Sunday, festival and minor
    festival.
  - **ELHB**: the Epistles and Gospels, the two Old Testament lessons (from
    the Historical and the Poetical Books) and two New Testament lessons for
    each Sunday and festival, and the Table of Lessons for Morning and Evening.
- `readings.csv` in a tradition folder, with the settings `reading_cycle` and
  `reading_labels` (docs/traditions.md).

## 2026-10 (11) — the Moravian Church's picture

### Changed

- The Moravian Church's center picture redrawn.

## 2026-10 (10) — Back and Forward, a guide to adding a church

### Added

- The browser's **Back** and **Forward** go through the changes made on the
  page: each change of settings and each day picked is a step; stepping day by
  day with the arrows only updates the current one.
- [docs/adding-a-church.md](docs/adding-a-church.md), a step-by-step guide,
  and `docs/example-church/`, a small working calendar to copy.

### Changed

- The Rings menu lists the rings as they lie on the wheel, outermost first
  (the day cells after the seasons).
- Iceland, Denmark and Finland are listed under their churches' own English
  names: the Evangelical Lutheran Church of Iceland, in Denmark, of Finland.
- `artwork/CREDITS.md` notes which pictures need permission before the
  project is published.

### Fixed

- Printing with the instructions turned off put the artwork credit nearer the
  wheel than with them on (an empty line was printed above it); it now sits
  the same distance below the wheel either way.

## 2026-10 (9) — books named in the Church menu

### Changed

- A church with a single prayer book or calendar, which has no menu after it,
  shows that book in the Church menu: "Church in Wales (BCP 1984)", "Igreja
  Lusitana (Portugal, LOC 1991)". The `series` of the single-book Anglican
  churches name their books (BCP 2019, LOC 2015, ...) rather than a year.

## 2026-10 (8) — the Evangelical Lutheran Hymn-Book; sourced colors

### Added

- **ELHB (1912)** in the Hymnal menu: the *Evangelical Lutheran Hymn-Book*,
  the LCMS's first English hymnal, one-year (`lcms-elhb-one-year`).

### Changed

- A Lectionary (or Prayer book, Calendar) menu with a single entry is left
  out: LW (`lcms-lw`; its one calendar serves both its lectionaries), TLH, the
  ELHB, and the churches with one prayer book. Returning to LSB brings back
  the series last chosen. `lcms-lw-three-year` still works in links.
- TLH and the ELHB, which print no colors, take the *Common Service Book*'s
  (1917): white through the Epiphany season and the Trinity octave, green
  from Septuagesima to Ash Wednesday, violet Maundy Thursday, red All Saints'.

## 2026-10 (7) — the LCMS hymnals

### Added

- A **Hymnal** menu for the LCMS: *Lutheran Service Book* (2006, as before),
  *Lutheran Worship* (1982, three-year, with its own colors and minor
  festivals) and *The Lutheran Hymnal* (1941, one-year, Latin names on).
  Keys `lcms-lw-three-year` and `lcms-tlh-one-year`; the folders are written
  by `tools/stage8_lcms_hymnals.py`.

### Changed

- The series menu of the LCMS, ELS and LCC is named **Lectionary**; the LSB
  headings read "LCMS Three-year (LSB)" and "LCMS One-year (LSB)".

## 2026-10 (6) — Latin names by default, and a review

### Changed

- **LCMS One-year** (and the ELS and LCC One-year, the same series) opens with
  the Sundays' Latin names: a new tradition.csv setting, `latin_names_default`,
  read by the page, `new_year.py` and `year_summary.py` (which gains
  `--no-latin-names`).
- The dry run's "Sundays" line counts the Sundays after the Epiphany, Pentecost
  or Trinity for every tradition that names them so, not only the two LCMS
  series; the 1962 Missal's resumed November Sundays are no longer counted with
  the Epiphany's.
- Year labels in file names and messages are right outside 1000–9998
  (`6-5BC`, `1BC-1`, `9999-10000`) rather than `-5-` or `9999-000`.
- Headings "BCP 1979 (Episcopal Church)" and "BCP 1984 (Church in Wales)",
  book then church like the others; the Diocese Anglicana do Recife and the
  Malankara Orthodox Syrian Church under their own names.
- The EKD is listed as "EKD (Evangelische Kirche in Deutschland)", abbreviation
  first like the LCMS, ELCA and WELS.
- "Lutheran Church–Canada" with its en dash throughout; the HKBP's label
  matches its church name.

### Fixed

- **Reset settings** cleared the gear's dot only when it also redrew the wheel;
  with only the Under-the-wheel boxes changed the dot stayed.
- A link opened on a page already showing (a changed address, Back/Forward)
  now sets everything it leaves out back to its default instead of keeping the
  settings in hand; Back and Forward could also fail to move the wheel.
- ◀ ▶ and links stop at the first and last years the page draws; a link with
  settings but no day keeps its `zoom`; PageDown from Advent Sunday lands on
  the next Advent Sunday.
- `church_year_web.py --churches` kept "the tradition's own" artwork only by
  chance: a page of several churches opened every one of them on the first
  kept picture.  `--list-churches` now lists what `--churches` keeps.
- `center_svg` naming a file (as older config.csv files do) draws the same
  picture, at its artwork.csv scale, in the page as in church_year.py.
- An unknown `--lectionary` gives a one-line message instead of a traceback.
- Tanzania (ELCT): the Sunday between 2 and 5 January is named (the second
  Sunday after Christmas).
- Ambrosian: a Sunday on 24 December (when Christmas is a Monday) is the
  Domenica prenatalizia.
- The settings panel lines its controls up on a phone; printing from dark mode
  prints the church's name dark.
- The tools in `tools/` answer `--help` and say which arguments they need
  (`stage2.py --help` used to make a folder called `--help`).
- Stale mentions of the Chi-Rho, papal emblem and "Lectionary menu" removed.

## 2026-10 (5) — more artwork, footer boxes, mid-tone text

### Changed

- `traditions.csv` lists each tradition's churches by approximate size, largest
  first, so each tradition opens on its largest church (Lutheran: LCMS
  Three-year, then One-year; Oriental Orthodox now opens on the Ethiopian).
  The Church of England opens on Common Worship, and the ELS and LCC on their
  Three-year series.

### Added

- **Under the wheel** boxes in the settings panel: instructions and notes, and
  the artwork credit (with the **i** when a license requires it). Links keep
  them (`help=0`, `credit=0`).
- **Dark text on reds** in the panel (`mid_text` = `dark-reds`): black on the
  mid-tone reds (LCMS, Roman, Presbyterian), which read about as well with
  black as with white; `mid_text` can also be `dark` or `light` for every
  mid-tone color.
- Center pictures for the Moravian and British Methodist churches.
- The **IHS Christogram** in a sunburst is the Roman, 1962 and Ambrosian
  calendars' artwork, in place of the Chi-Rho.

## 2026-10 (4) — artwork, footer and single-church pages

### Added

- **`--churches`** (or `page_churches`): a page with only the churches named,
  by key, tradition or `lcms-*` prefix; menus with one choice are hidden.
  `--list-churches` lists the keys.
- **`--footer`** (or `page_footer`): `full`, `credit` or `none`. With `none`, a
  license that requires credit keeps a small **i** button that opens it.
- `tools/check_contrast.py` lists any color whose text is not the more
  readable of black and white.

### Changed

- **Artwork:** new center pictures for the Reformed and Episcopal churches,
  and a Chi-Rho with Alpha and Omega for the Roman, 1962 and Ambrosian
  calendars (also standing in for the Moravian and British Methodist, which
  showed the Luther rose by mistake). The crucifix, the papal emblem, the
  burning bush and the plain shields are gone.
- The **Orthodox cross**'s slanted foot has its ends cut upright.
- The middle of the wheel is **white** under every picture, in light and dark
  mode (it showed the page's background).
- Pictures are credited in `artwork.csv` by what their licenses require.
- Black text on the Presbyterian green and the Reformed red, which read
  better than white.

## 2026-10 (3) — menus and artwork

### Changed

- **Menus:** the Lectionary menu is replaced by **Tradition** (Anglican,
  Catholic, Church of the East, Lutheran, Methodist, Moravian, Oriental
  Orthodox, Orthodox, Reformed and Presbyterian) and **Church**, with a third
  menu for a church's series or prayer books (LCMS One-year and Three-year;
  the Church of England's 1662 and Common Worship). `traditions.csv` gains
  `tradition`, `church`, `series` and `series_menu` in place of the group
  columns. The Ordinariates' Divine Worship is under Catholic and the Western
  Rite Orthodox book under Orthodox. Old links and keys still work.
- **Artwork** is sized so each picture fits inside the month ring: its
  farthest point reaches 92% of the way, and the round seals fill the circle.
- The **artwork credit** has a line of its own under the instructions.
- Center pictures for the Presbyterian Church (U.S.A.) and the Church of
  Scotland.
- The **Halves** ring is **Parts of the year** in the Rings menu: it holds two
  halves for most churches but three to five parts for the Ambrosian, Syriac,
  Maronite and Assyrian years. Its key (`halves`, as in `hide=halves`) is unchanged.
- The **heading** is on two lines, the year above and the church below, in a
  set width so the controls beside it no longer move; the **gear** is at the
  far left. WELS is "(CW 2021)" and a few long names are shorter.
- The **settings gear** is a solid drawn icon rather than a text character, so
  it is as bold on every computer (the character was thin on Windows).

### Fixed

- The settings panel no longer shows scroll bars on a normal screen (it was
  capped at 34rem tall, and the vertical scroll bar then forced a horizontal
  one); on a short screen it scrolls up and down only.
- A link that changes only the settings (no date) now redraws the wheel.

## 2026-10 (2) — more churches

### Added

- **ELS One-year and Three-year** (Evangelical Lutheran Synod), from the
  synod's own calendars and its printed *ELS Liturgical Calendar* (2023–24),
  with its colors: the Baptism on Quinquagesima, the Transfiguration when
  there are three Sundays after the Epiphany, Michaelmas on a Sunday, the
  Third-Last, Second-Last and Last Sundays; gold for Christmas and Easter,
  rose for Gaudete and Laetare.
- **LCC One-year and Three-year** (Lutheran Church-Canada), with Canadian
  Thanksgiving; **WELS** (Christian Worship 2021).
- Lutheran (worldwide): **Austria** (the German calendar), **Tanzania (KKKT)**
  from its 2018 calendar with colors, and **Australia and New Zealand (LCA)**.
- **Methodist Church in Britain**, **Church of Scotland** and **Moravian Church
  in America**.
- **Ukrainian Greek Catholic** and **Byzantine Catholic (Ruthenian)** churches,
  as variants of the Orthodox year.
- **Ambrosian Rite**, **Maronite Catholic Church** and **Assyrian Church of the
  East**, each a folder of its own.

### Changed

- **HKBP** rebuilt from the church's own almanac (hkbp.or.id): Batak names and
  the almanac's colors (Good Friday blue; Septuagesima to Invocavit green);
  Reformation Day is a feast on 31 October, no longer a Sunday.
- **Estonia:** Holy Innocents, Candlemas, St John's Day, Michaelmas,
  Reformation Day and All Souls take over the Sunday they fall on.

## 2026-10 — the 1962 Roman calendar and more Lutheran churches

### Added

- **Roman Catholic 1962 (Extraordinary Form):** the General Roman Calendar of
  1960 with the 1962 Missal: Septuagesima, the octaves, Ember and Rogation
  days, the Sundays after Pentecost and the 1960 classes of feasts, ranked
  by the same precedence rules as the modern calendar. See
  [docs/traditions.md](docs/traditions.md#the-roman-calendar-of-1962).
- **Lutheran (worldwide)**, with a **Church** menu: the churches of Germany
  (OGTL 2018), Poland, Slovakia, Hungary, Estonia, Latvia and Iceland, the
  HKBP of Indonesia and the Malagasy Lutheran Church, each in its own
  language. See
  [docs/traditions.md](docs/traditions.md#lutheran-churches-worldwide).
- Titles can number in Roman numerals: `{roman}` and `{roman2}`.
- Estonia's Sundays named as the church's own calendar posts name them
  (*Advendiaja*, *Jõuluaja 1./2. pühapäev*, *Ülestõusmisaja*); Good Friday in
  black for Estonia, violet for Iceland (its more common use); Mission Day red
  in Iceland.
- **GKLI (Gereja Kristen Luther Indonesia)**, from its Almanak 2026 with its
  altar colors.
- Iceland: Reformation Day is also marked on the last Sunday in October, beneath
  that Sunday's own name, with red in the lower half.
- A single day's `first` may be a date, numbering the Sunday it takes over
  (`first=easter+56`).

### Fixed

- Small capitals of "ß" (which capitalizes to two letters) no longer stop a
  wheel from being drawn.

## 2026-10 — the Orthodox churches

### Added

- **Eastern Orthodox:** the Byzantine year from the Indiction on 1 September,
  with the Triodion, the Pentecostarion, the Twelve Great Feasts and the
  Slavic colors. It opens on the Revised Julian calendar with the Orthodox
  Pascha; choose the Julian calendar for the Old Calendar churches. See
  [docs/traditions.md](docs/traditions.md#the-eastern-orthodox-churches).
- **Ukrainian Lutheran Church:** Advent to Christ the King, Byzantine in
  between, in Ukrainian.
- **Oriental Orthodox**, with a **Church** menu: the Armenian Apostolic,
  Coptic Orthodox, Ethiopian and Eritrean Tewahedo, Syriac Orthodox and
  Malankara churches. See
  [docs/traditions.md](docs/traditions.md#the-oriental-orthodox-churches).
- Artwork:
  - the Orthodox three-bar cross;
  - the Armenian cross;
  - the West Syriac cross;
  - a Coptic and an Ethiopian cross drawn for the project.
- The date language can name a day in another calendar: `julian(12-25)`,
  `coptic(04-29)`, `ethiopian(05-11)`. `prev_easter` gives the Easter before
  the year began, and a run's `first` can be a date, to number the Sundays by
  the weeks since it.
- A tradition's `calendar` setting chooses the calendar it opens in, in
  `new_year.py` and `year_summary.py` as on the page.

### Changed

- **Ukrainian Lutheran Church** rebuilt from its own calendar and service book:
  a year from Advent to Christ the King, Byzantine in between, in Ukrainian,
  with its saints on the Revised Julian calendar and its colors. See
  [docs/traditions.md](docs/traditions.md#the-ukrainian-lutheran-church).
- Where a year starts or ends partway through a week (the Orthodox, Coptic
  and Ethiopian years), the rings are closed over the empty cells in their
  gray instead of leaving a notch (`year_seam_fill`).
- The Armenian year begins on the Sunday nearest 25 November, as the
  Armenian Church's own calendar gives it. The Coptic Sundays of Lent start
  with the Preparation Sunday. More Syriac, Coptic and Ethiopian days.

### Fixed

- A year made in another calendar than its tradition's own is drawn in the
  calendar it was made in.

## 2026-10 — more Anglican books, and the Nordic Lutheran churches

### Added

- **Ten more Anglican prayer books** in the Prayer book menu. See
  [docs/traditions.md](docs/traditions.md#the-anglican-prayer-books).
  - Church in Wales 1984.
  - *Divine Worship* 2021.
  - Proposed BCP 2025 (Western Rite Orthodox, with Orthodox Easter).
  - Seven Portuguese-language books from Brazil and Portugal.
- **Lutheran (Nordic)**, with a **Church** menu: the Church of Sweden, the
  Church of Norway, the Evangelical Lutheran Church in Denmark and the
  Evangelical Lutheran Church of Finland. Each is named in its own language,
  with its own moved feasts and colors. See
  [docs/traditions.md](docs/traditions.md#the-nordic-lutheran-churches).

### Fixed

- Norway keeps the Annunciation on the Sunday Mar 22–28 (the 5th Sunday in
  Lent when that is Palm Sunday or Easter), and now has its Day of Repentance
  and Prayer. Sweden drops Apostles' Day when it falls on St John the
  Baptist's Sunday.

## 2026-10 — the Episcopal, Lutheran, Methodist, Presbyterian, Reformed and Anglican calendars

### Added

- **Five churches of the Revised Common Lectionary**, each with its own names,
  colors and days. See
  [docs/traditions.md](docs/traditions.md#the-churches-of-the-revised-common-lectionary).
  - **Episcopal Church (BCP 1979):** blue Advent, red Holy Week, the Prayer
    Book's Holy Days and the lesser feasts, and Propers on the Sundays after
    Pentecost.
  - **ELCA (*Evangelical Lutheran Worship*):** lesser festivals,
    commemorations and lectionary numbers.
  - **United Methodist Church:** its special Sundays.
  - **Presbyterian Church (U.S.A.):** colors from its planning calendars,
    and its special offerings.
  - **Reformed:** colors from the RCA's calendar, with the Christian Reformed
    Church's Canadian special days as a calendar to lay over it.
- **Anglican**, with a **Prayer book** menu: ACNA 2019, BCP 1662, BCP 1928,
  BCP 1962 (Canada), Common Worship, REC 2005 and TEC 1979. Each has its own
  structure (Septuagesima and the Sundays after Trinity in the historic books;
  Common Worship's Sundays before Lent and before Advent) and its own holy days
  and commemorations.
- Artwork for each church, with credits. The ELCA uses the Luther rose.
- Runs of Sundays can be numbered toward their end (`count` = `before`: Fourth,
  Third, Second Sunday before Advent) and can carry a second number
  (`first2`/`count2`, `{number2}`), which gives each Sunday after Pentecost its
  Proper.

## 2026-10 — traditions, the Roman Catholic calendar, artwork

### Added

- **Traditions.** Each church's year is now a folder of rules under `data/`
  (`data/LCMS`, `data/Roman`), and the Lectionary menu lists them from
  `data/traditions.csv`: **LCMS One-year**, **LCMS Three-year** and **Roman
  Catholic (General Roman Calendar)**. Principal days, seasons and cycles are
  written in a small date language (`easter+49`, `sun<12-25-21`, `thu#4:11`)
  rather than in code, so a tradition can be added without programming. Both
  renderers read the same rules, and every LCMS drawing is byte-for-byte what
  it was. See [docs/traditions.md](docs/traditions.md).
- **The General Roman Calendar**: every solemnity, feast, memorial and
  optional memorial, each shown by a short name in its cell ("St. Isidore")
  with the full title in the page's readout. Colors and seasons follow the
  Roman Missal, with rose on Gaudete and Laetare Sundays and split cells for
  Christmas Eve, Holy Thursday and Holy Saturday. Precedence follows the Table
  of Liturgical Days. Impeded solemnities are transferred (the Immaculate
  Conception to 9 December in 2024; Saint Joseph before Palm Sunday in 2008 and
  2035). Memorials in Lent and late Advent become commemorations, and a Sunday
  gives way to a feast of the Lord or a solemnity.
- **National, institutional and personal-jurisdiction calendars** for the
  Roman calendar: 81 countries and regions, 37 religious institutes and
  societies, and the two Anglican-use ordinariates. Each has its own menu, and
  any combination can be laid over the General Roman Calendar
  (`--subcalendar`, `subcalendars` in `config.csv`, `sub=` in page links).
  Holy days of obligation follow each country's norms. In the United States,
  for example, the obligation is lifted from 1 January, 15 August and
  1 November when they fall on a Saturday or a Monday.
- **Icons**: a chalice and host marks a holy day of obligation, a bowl a day of
  fasting, a fish a day of abstinence (`data/icons.csv`, sized by `icon_size`).
- **Artwork menu.** The middle of the wheel can hold any picture listed in
  `data/artwork.csv`. `center_svg,auto` (the new default) picks each
  tradition's own: the Luther rose for the LCMS series, a crucifix for the
  Roman calendar. The emblem of the Holy See is also offered. Pictures are
  centered in the circle, and `scale` in `artwork.csv` can inset one.
  Each picture's title, author, license and source are listed, and the page
  shows the credit for the one in use, on screen and in print.
- **The artwork credit is drawn on the wheel** when its license asks for credit
  wherever it is shown, as the Luther rose's CC BY-SA does. It is two small
  lines in the lower-left corner. `artwork_credit` in `config.csv`: `auto`
  (the default), `always` or `none`.
- A **None** level in the Feasts menu and in `--feasts`: only the principal
  days, with no saints' days.
- `year_summary.py` takes any tradition's key and `--subcalendar`. The Roman
  listing includes weekday solemnities, and the calendar feed is named after
  the tradition. LCMS feeds keep their event IDs, so a feed imported before
  updates rather than duplicating.

### Changed

- The center artwork moved from `center.svg` to `artwork/Lutherrose.svg`, its
  name on Wikimedia Commons. A year folder made before this change, whose
  `config.csv` still names `center.svg`, draws exactly as before.
- The LCMS files moved into `data/LCMS/`. The menu reads **LCMS One-year** and
  **LCMS Three-year**, and the Latin names box appears only for LCMS One-year.
  The keys `one-year` and `three-year` still work everywhere.
- The menus of names (traditions, the added calendars, artwork) are in
  alphabetical order. Menus of levels, such as Feasts, keep their natural
  order.
- `year_summary.py` gives every day one color, the top of its cell, for
  choosing paraments. `--all-labels` used to add a split cell's lower color
  (`RED/WHITE`).
- `new_year.py` writes the year's commemorations to `year_feasts.csv`, already
  dated, with each one's level, rank and icon.

## 2026-09 — precedence, phones, embedding

### Changed

- **When a saint's day falls on a day that outranks it, the cell is split:
  the greater day keeps the top and the feast's color covers the lower half.**
  The Annunciation had turned Palm Sunday white in 2029 and 2040, a Sunday in
  Lent white in 2057, and a weekday of Holy Week white in 2043, 2054 and 2059;
  Palm Sunday 2029 is now scarlet over white. A day outranks a feast anywhere in
  Holy Week and Easter week, on a Sunday or named day in Advent, Lent or Easter,
  and on a day the Sundays file gives a color of its own (Pentecost over the
  Visitation, red over white). Elsewhere nothing changes: a feast with a
  `color_override` still colors the whole cell, on an ordinary Sunday or a plain
  weekday. Two new settings, `feast_yield_seasons` and `feast_yield_every_day`,
  say where; both renderers follow them. See
  [docs/liturgy.md](docs/liturgy.md#when-a-saints-day-falls-on-a-greater-day),
  which also explains displaced feasts.
- **PageDown now goes a year on and PageUp a year back**, as in a date picker,
  and both keep the date instead of jumping to Advent Sunday.
- **The address says `date=today` while the wheel is on today**, so a bookmark
  or a reload opens on the current day rather than the day it was saved.
  **Copy link** still writes the date out.
- The Lectionary menu lists One-year before Three-year. The default is still
  whatever `config.csv` names.
- Red cells carry white text (5.0:1 contrast) instead of black (4.2:1).
- The calendar feed's event IDs are made from the date and the lectionary, not
  the title, so a renamed day or `--all-labels` updates the imported event
  instead of adding a copy. Feeds made before this change will duplicate once.
- A `png_filename` of its own lands beside the SVG rather than in the folder the
  command was run from.
- The built-in fallback for `text_orientation` is `tangential`, matching what
  `config.csv` ships.

### Added

- **Checks on the year itself.** `church_year.py` warns when the year does not
  start on the week's first day, is not 364 or 371 days long, or when
  `sundays_seasons.csv` or `season_periods.csv` have nothing in the year — the
  mark of dates changed in `config.csv` without running `new_year.py`, which
  used to draw a blank white wheel and report that every label fitted.
- A misspelled setting suggests the one meant (`colour_split_max` → did you mean
  `color_split_max`?), and a feast date that cannot be read, or a day that does
  not exist, is reported with the row's name.
- The readout is announced to screen readers as the day changes, and the day
  arrows have spoken names. The wheel itself can take the keyboard focus.

### Fixed

- **The settings panel opened off the left edge of a phone's screen**, hiding
  every setting but the dropdown arrows. It now opens from the gear at every
  width and stays on screen.
- **Printing in landscape spilled over three pages.** It now fits one page on
  Letter or A4, either way round.
- **The page took the browser's own shortcuts:** Ctrl/Cmd with + / − / 0
  (page zoom) and Alt+← (Back). Keys held with Ctrl, Cmd or Alt are now left
  alone, as is typing in a text box.
- **`--fragment` broke the page it was put in.** Its styles applied to the whole
  page (every picture stretched to full width, the page stopped scrolling) and
  it drew into the page's first `<svg>`. Everything is now scoped to `.cy-app`;
  embedded, the wheel leaves the page's title, address, scrolling and keyboard
  alone. Alone in a page skeleton it still behaves as the full page.
- **A link with `hide=days` crashed the page** to a blank wheel, and
  `hide=center` hid the artwork the menu says cannot be hidden. Both are now
  ignored.
- The page's data is escaped so nothing in `center.svg` can close its script
  early.
- Data: "Nicea" is now "Nicaea".
- Tidied: an unused import and variable, and type hints in `new_year.py` that
  named `date` where the values are day numbers.

## 2026-09 — one web page, links, print, calendar feed

### Changed

- **One web page.** The fixed-year page is gone. `church_year_live.py` is now
  `church_year_web.py`, it writes `church_year.html`, and its support files
  live in `web/` rather than `live/`. `new_year.py --draw` builds the page from
  the year folder's own settings and names it `church_year_<year>.html`.
- **Where the festival half ends** now follows the lectionary. The new
  `festival_half_end` setting defaults to `auto`: through Trinity week in the
  one-year series (the non-festival half begins with the First Sunday after
  Trinity) and through Pentecost week in the three-year series (it begins with
  The Holy Trinity). `pentecost-eve` restores the old boundary. The EASTER cycle
  label ends with the festival half.
- **PNG renderer.** `config.csv` ships with `png_renderer,auto` instead of a pin
  on Inkscape, and `auto` now tries Inkscape, rsvg-convert, resvg and Chrome
  before CairoSVG, which is the weakest on this drawing's text.
- **README split up.** The README is now an overview; the detail moved to
  `docs/`, and this changelog took over the "What changed" section.

### Added

- **Links to a day.** The web page keeps its address up to date
  (`#date=2026-12-25&lectionary=one-year&zoom=2.5` and so on), opens on
  whatever a link describes, and has a **Copy link** button behind the gear.
- **Pinch to zoom** on touch screens, about the point between the fingers, with
  panning in the same gesture.
- **Reset settings** behind the gear puts the lectionary, calendar, Easter
  rule, feasts, Latin names and rings back to what `config.csv` asks for,
  keeping the day on the wheel. It is grayed out while nothing has changed.
- **Print layout.** Printing the page gives the whole wheel, the right way up,
  at 1x and in color, on one page, with a **Print** button behind the gear.
- **Calendar feed.** `year_summary.py --format ics` writes an iCalendar file
  for Google, Apple or Outlook calendars, for one year or a span. Julian
  years are converted to Gregorian dates.
- `config.csv` now lists the four settings it was missing: `color_split_max`,
  `color_split_gain`, `ring_subtitle_ratio` and `ring_subtitle_separator` (the
  last quoted so its trailing space survives).

### Fixed

- **The page's Easter picker ignored a blank `paschalion`.** The exported
  settings carried the resolved rule, so the picker opened on "Western" and
  switching the page to the Julian calendar kept a Western Easter. It now
  opens on "With the calendar", as `config.csv` asks.
- **The readout left the season blank** for one-year days whose color row
  carries no ring label (the weeks after Easter). It now names the season the
  ring shows.
- **The console said labels were tight** when the only report item was a
  repeated name drawn once. Repeats and tight labels are now counted apart.
- `web/data.json` is also rebuilt when `center.svg`, `church_year.py` or the
  exporter changes, not only a CSV, and no longer depends on the folder the
  script is run from.
- Two headings in the README rendered as giant text (a `---` straight under a
  paragraph); the Pre-Lent example showed `PURPLE` where the data and the text
  said green; the script table said four scripts and listed five.
- Data: "Fredrick the Wise" is now "Frederick the Wise", and "Circumcision &
  Name of Jesus" is "Circumcision and Name of Jesus", matching its eve.

## Earlier

- **Auto-fitting replaces the manual overrides.** Every label is measured with
  real font metrics (Adobe core-font advance widths, which is what "serif" and
  "sans-serif" resolve to in browsers and drawing programs), then sized and
  wrapped to fit its wedge. The `font_size_override`, `max_chars_override` and
  `vertical_offset` columns are still read and still win when filled in, but
  every one of them has been emptied in the shipped CSVs; the layout no longer
  needs them. Nothing drops below 8 pt in the current year's data.
- **All day-cell text keeps one orientation.** Labels run tangentially, the
  way they always have. The fitter can turn a label radially instead, but that
  is switched off (`text_orientation,tangential`) — turning individual cells
  looked inconsistent against their neighbors. Set `text_orientation,auto` if
  you ever want to see it. Ring labels curve along their arc as before.
- **Labels keep clear of the day number.** The number occupies the leading top
  corner of each cell; a label that would run into it is dropped below it and
  refitted. `day_number_gap` controls the clearance.
- **PNG as well as SVG.** Both are written by default, from the same drawing.
- **Rings are data.** `rings.csv` defines every concentric band — order,
  radii, fill, label source, font. Add, remove, reorder or disable a ring
  without touching the script.
- **Other fixes.** Several commemorations may now share one date (they stack
  in the cell instead of the last one silently winning). A missing
  `center.svg` warns instead of crashing. `#`-prefixed comment rows and blank
  rows are ignored in every CSV. Unknown settings and unknown color names are
  reported by name instead of failing silently or with a traceback. `lxml` is
  no longer required.
