# The data files and settings

## The data files

| file | holds |
| --- | --- |
| `config.csv` | every layout, font and behavior number — see the table below |
| `colors.csv` | liturgical color names → fill color and the text color used on it |
| `seasons.csv` | season key → color name |
| `season_periods.csv` | the dated seasons: their ring labels, their day colors, or both |
| `broad_seasons.csv` | the `CHRISTMAS` and `EASTER` arcs — generated, but no ring sources it by default |
| `halves.csv` | the two halves with their subtitles, and the CHRISTMAS and EASTER cycles |
| `sundays_seasons.csv` | dated Sundays, festivals and principal days |
| `year_feasts.csv` | the year's commemorations, dated, with each one's level, rank and icons (written by `new_year.py`) |
| `month_overrides.csv` | optional nudges for individual month labels |
| `month_names.csv` | month number → printed name (English) |
| `ui/` | the page's own words (buttons, menus, settings and their notes) in other languages: `english,translation` rows, one file a language (`de.csv`); what a file leaves out stays English |
| `languages/` | each church language's month names, date patterns and Bible book names (below) |
| `rings.csv` | the concentric rings and their geometry |
| `text_styles.csv` | the named text appearances used in the day cells |
| `traditions.csv` | the Tradition, Church, Hymnal and Lectionary (or Prayer book, Calendar) menus: each calendar's key, label, place in the menus, folder and variant |
| `artwork.csv` | the pictures the middle can hold, with each one's author, license and source |
| `season_art.csv` | which picture each season shows when the artwork follows the season (below) |
| `icons.csv` | the small pictures a day can carry (holy day of obligation, fasting, abstinence) |
| `LCMS/`, `Roman/`, ... | each tradition's rules, feasts and colors — see [traditions.md](traditions.md). A church's other books or editions are folders inside its own: `Roman/1962` (the 1962 Missal) inside `Roman`; the LCMS folder holds only its hymnals, `LCMS/LSB` (Lutheran Service Book, both series) and `LCMS/LW`, `LCMS/TLH` and `LCMS/ELHB` (the older hymnals), and `LCMS/Loehe` (Wilhelm Loehe's calendars of saints, 1859 and 1868). Each is complete in itself, nothing is inherited from the folder around it; `Roman/national`, `Roman/institutional` and `Roman/personal` instead hold the calendars laid over the Roman one. |

The dated files (`sundays_seasons.csv`, `season_periods.csv`,
`broad_seasons.csv`, `halves.csv`, `year_feasts.csv`) are written by
`new_year.py` from the tradition's rules. Edit the rules in the tradition's
folder and regenerate, or edit a year's dated files by hand for that year alone.

### languages/

One file per language, named by its code (`es.csv`, `de.csv`, ...), which a
church names with the `language` setting in its `tradition.csv`. Rows are
`key,value`:

| key | what |
|---|---|
| `name` | the language's own name |
| `months` | the twelve names on the month ring, separated by `\|` |
| `date_months` | the twelve as a date writes them, where that differs (Polish *stycznia*, Finnish *tammikuuta*) |
| `month_day` | a day's date on the wheel: `{day} de {month}`, `{day}. {month}`, `{month} {day}.` |
| `full_date` | the year's first day: `{day} de {month}\| de {year}`, the `\|` where it may break onto a second line |
| `chapter_verse` | what the page writes between chapter and verse: `:` or `,` (with `,`, verses are listed with `.`: *Römer 13,11.12*) |
| `GEN`, `EXO`, ... | the Bible books' names, by USFM code, as the page shows them in a citation |
| `color_purple`, `color_white`, ... `color_none`, `or` | the page header's words for the day's color and its alternatives ("morado (o azul)"), by the color's name in lower case, spaces as `_`; `color_none` stands for "no color", `or` between a color and its alternatives |
| `reading_Readings`, `reading_Gospel`, ... | the page's words for its readings, by their English names: `reading_Readings` heads the list, the others name a kind of reading (`reading_Old Testament`, `reading_First Reading`, `reading_Prophecy` ...). A church's own `reading_labels` (in English) are put into its language the same way; `or` also stands between a reading's choices ("Lukáš 2,15–20 alebo Matúš 23,34–39") |

The words follow the churches' own documents where one was found: the Church of
Sweden's *vitt, grönt, rött*, the Church of Norway's 2010 color rule (*hvitt,
grønt, rødt, gyllent*), Danish *gylden*, German capitalized (*Violett, Weiß*).
A church whose own documents use another word sets `color_labels` in its
`tradition.csv`.

What a file leaves out stays English, and a church without a `language` is
English (`month_names.csv`, and `{month} {day}` and `{month} {day},|{year}`).
The colors keep their names everywhere else (colors.csv, the overrides, links
and settings); only the header's words change. The readings themselves stay in
English in the data: the Bible links, the verse
numbering and the hymn and song searches read them; only what the page shows
is translated. The book names follow each church's Bible (`source` is noted at
the top of each file) and are worth a check by a reader of the language.

### colors.csv

`name,fill,text` — `name` is what the other files refer to. `text` is the
color lettering takes when it sits on that fill. A fill written as two colors,
`#ffffff/#bfbfbf`, is drawn as a ground with diagonal lines: `NONE` (no color,
the stripped altar of Good Friday) is white hatched with gray, and the page
reads it as "no color".

Wherever a color is named (`seasons.csv`, the `color` columns of the rules,
`color_override`), it may carry the alternatives a source permits after
semicolons: `PURPLE; royal blue`. The first is the one drawn, the first the
source lists; the others are shown only in the page's readout, "purple (or
royal blue)". Alternatives need not be colors in `colors.csv`.

### seasons.csv

`season,color` — maps the `season` key used in `season_periods.csv` to a color
in `colors.csv`. `DEFAULT` is the fallback for a date no season covers.

### season_periods.csv

`name,start_date,end_date,season` plus an optional `color` column that
overrides the season's color for that period alone. `name` is what appears in
the season ring.

### sundays_seasons.csv and year_feasts.csv

Both take the same columns:

| column | meaning |
| --- | --- |
| `date` | `YYYY-MM-DD`, or `MM-DD` to place it in whichever year falls inside the church year |
| `title` / `name` | the text (`title` in the Sundays file, `name` in the commemorations file) |
| `color_override` | recolors the whole day |
| `color_override_bottom` | recolors the lower half of the day, splitting the cell — if it matches the upper half the cell is left whole, since the split would only draw a line |
| `style` | optional: use a named row from `text_styles.csv` instead of the automatic choice |
| `font_size_override` | pins the font size; auto-fit is skipped for this label |
| `max_chars_override` | hard character cap per line, on top of the width-based wrap |
| `vertical_offset` | nudges the label outward (positive) or inward (negative), in user units |
| `icon` | icon keys from `icons.csv`, separated by spaces |
| `full_name` | the whole title, shown in the web page's readout; the cell shows the short one |
| `link` | feasts.csv: a page about the saint or festival, opened by clicking the name in the readout (otherwise the tradition's `feast_link`, or a Wikipedia search) |
| `rank`, `level` | the Roman rank (1–13), and the Feasts level the row belongs to: `principal`, `festival` or `all` (blank counts as `all`) |

Color priority for a day: an override in the Sundays file, then one in the
commemorations file, then the season's color — except where a saint's day falls
on a day that outranks it (Holy Week and Easter week; a Sunday or named day in
Advent, Lent or Easter; a day with a color of its own in the Sundays file).
There the day keeps the top of the cell and the commemoration's color covers
the lower half. `feast_yield_seasons` and `feast_yield_every_day` below set
where; see [liturgy.md](liturgy.md#when-a-saints-day-falls-on-a-greater-day).

A date that cannot be read, or a day that does not exist (`02-30`, `13-01`), is
reported with the row's name and skipped; 29 February is simply absent in a
common year.

Several rows may share a date. They stack in the cell as separate paragraphs
and are fitted together.

### season_art.csv

Which picture the middle holds in each season, when the artwork is set to
follow the season: the web page's **Artwork: By season**, and
`church_year_image.py --art-date`. A day in a season with no row keeps the church's
own picture, so the seasons that are left out (the time after Pentecost, for
one) show it.

| column | meaning |
|---|---|
| `season` | a season's name as the wheel's ring and the readout give it (`Advent`), or its word in the season files (`ADVENT`), which is the same in every language |
| `art` | a key from `artwork.csv`; blank for the church's own picture |
| `church` | one church's key (`traditions.csv`), or blank for every church |
| `week` | the week of the season the picture comes in with (1 is the season's first seven days), or blank for the whole season |

A church's own row wins, by name and then by word; then the rows for every
church, by word and then by name. To give a season a different picture, or a
picture to a season that has none (Trinity, say), add the picture to
`artwork.csv` and a row here. A season may have several rows with a `week`:
the one for the latest week that has come is shown, which is how the Advent
wreath gains a lit candle each week (four rows, weeks 1 to 4). The pictures
that come with the project are drawn
by `tools/make_emblems.py`: the Advent wreath four times over, the manger, the star and three
crowns, the cross and crown of thorns, the three crosses, the empty tomb, and
the dove and flames.

### rings.csv

One row per concentric band. `order` is also the drawing order, inside to out
as shipped.

| column | meaning |
| --- | --- |
| `order` | draw order; lower is drawn first |
| `key` | a name for you; appears in the fit report |
| `kind` | `days` (the week ring), `segments` (a ring cut into dated runs), `band` (a plain filled ring), `center` (the artwork in the middle) |
| `r_inner`, `r_outer` | radii, in the same units as `width`/`height` |
| `fill`, `stroke`, `stroke_width` | the ring's own paint |
| `source` | for `segments`: `months`, `season_periods`, `broad_seasons` or `halves` |
| `font_size`, `font_family`, `font_weight`, `text_color` | the ring's labels |
| `label_mode` | `auto` (curve, turn radial only if the arc is far too short), `curve`, `radial`, `none` |
| `inner_border_color`, `inner_border_width` | a border drawn just inside the ring's inner edge; the width is what you see |
| `enabled` | `FALSE` skips the ring entirely |

Exactly one row must be `kind=days`.

### text_styles.csv

The appearance of each kind of label in a day cell. `font_size` is the *ceiling*
— auto-fit shrinks from there, never above it, unless `autofit_allow_grow` is on.

| style | used for |
| --- | --- |
| `day_number` | the plain number in the corner |
| `month_day_label` | the "October 1" line on the first of a month |
| `first_day_label` | the "November 30, 2025" line that opens the year |
| `sunday_title` | a Sundays-file entry falling on a Sunday |
| `weekday_title` | a Sundays-file entry falling on any other day |
| `feast` | a commemorations-file entry |

`orientation` may be `tangential` (as shipped), `radial`, or `auto` to let the
fitter choose per cell. `font_family` accepts `serif` or `sans-serif`, which
resolve through `font_family_serif` / `font_family_sans` in `config.csv`, or any
literal family name.

#### Cells that have too much to say

Two rules keep a crowded cell readable, and Advent 1 falling on St. Andrew is
the case that needed both. That day carries the opening date line, a Sunday
title with its Latin name, and a commemoration whose `color_override_bottom`
paints the lower half of the cell red — three things in one cell.

**The date line keeps only the depth it needs** — where it sits, plus half its
own height and a padding — with `top_label_reserve` as the ceiling rather than
the amount. A flat share of the band is a fair guess while the label has the
cell to itself and a poor one once something else has taken part of it. On that
day a third of the band left the title eleven units to work with, and it came
out at 5.2pt.

**The color may break off center** when the halves are badly matched. Half and
half is the rule everywhere it works, because a ring of cells all breaking at
the same radius reads as a pattern and one breaking at a different radius each
time reads as a mistake. So the two labels are fitted at 50/50, 55/45 and so on
up to `color_split_max`, and the break moves only if the worse-off label comes
out `color_split_gain` better somewhere else. That threshold is what keeps it
rare: nearly every split cell gains a little from a nudge, and taking all of
those would leave no two breaks alike for the sake of a point of type. With it,
about one cell in twelve moves — and they are the genuine collisions, Advent 1
on St. Andrew and the Easter Sundays on St. Philip and St. James.

Set `color_split_max,0.5` for a uniform half and half, or `0.60` to allow the
gentler moves but no more. The wheel picks the shallowest break that does the
job, so the three-year Advent 1 — a shorter title, no Latin name — takes 60/40
where the one-year with Latin names takes 70/30.

**A day whose two colors are both its own** (Christmas Eve and Holy Saturday,
whose late services already belong to the feast: the cell's upper color is the
day before's and its lower the day after's) splits its name over the two: the
first words on the upper color, the rest on the lower ("Christmas" / "Eve",
"Holy" / "Saturday"), at one size and each in the text color of the color
behind it. A note in parentheses goes below; two names (Advent 4 on Christmas
Eve) take one color each; a one-word name is centered on the whole cell, each
part of it in the color its background asks for. Where the cell also has a
commemoration, the name keeps the upper part. Any other day of two colors
(Reformation Day observed, red over the Sunday's green) keeps its name on the
color of its own occasion, the upper part.

Together the two rules take that cell's title from **5.2pt on one line to
9.45pt on three**, with St. Andrew still at its full size in the band below.
Across 2020-2070 in both lectionaries, they are the difference between eleven
titles shrunk below their style size and none.

## config.csv reference

**Change settings here, not in the script.** Each setting also has a default
inside `church_year_image.py` (the `SETTING_SPEC` table), but any row in
`config.csv` overrides it — and the shipped `config.csv` lists every setting,
so editing the script's table has no effect until you delete or blank the
matching row here. Unknown names are reported and ignored, so a typo will not
fail silently.


**The year and the output files**

| setting | default | what it does |
| --- | --- | --- |
| `church_year_start` | — | First day of the church year (YYYY-MM-DD) |
| `church_year_end` | — | Last day of the church year (YYYY-MM-DD) |
| `lectionary` | `lcms-three-year` | Which tradition this year follows: a key from `traditions.csv`, such as `lcms-three-year`, `roman`, `episcopal`, `elca`, `methodist`, `presbyterian`, `reformed` or `anglican-bcp-1662` (see [traditions.md](traditions.md); `three-year` and `one-year` still mean the LCMS series; read by new_year.py) |
| `subcalendars` | *(blank)* | Calendars laid over the tradition's own, by key from its `subcalendars.csv`, separated by spaces, e.g. `united_states jesuits` (read by new_year.py; a tradition's `latin_names_default` in its tradition.csv wins) |
| `latin_names` | FALSE | One-year series: append the Sunday's Latin name to its title (read by new_year.py; a tradition's `latin_names_default` in its tradition.csv wins) |
| `festival_half_end` | `auto` | Where the festival half ends: `auto` (one-year: the Saturday after Trinity; three-year: the Saturday after Pentecost), `pentecost-eve`, `pentecost-week` or `trinity-week` (read by new_year.py; see [liturgy.md](liturgy.md#where-the-festival-half-ends)) |
| `calendar` | `gregorian` | Which calendar the dates are reckoned in: gregorian, julian or revised-julian (see [calendars.md](calendars.md)) |
| `paschalion` | *(blank)* | Which rule finds Easter: gregorian or julian; blank follows the calendar |
| `feast_detail` | `all` | How much of the feasts to draw: all, festivals (only rows that color their cell; Roman: feasts and solemnities), principal (only rows with a color_override; Roman: solemnities), or none |
| `deduplicate_day_labels` | TRUE | Drop a commemoration whose name repeats the day's own title |
| `feast_repeat` | `all` | When a 53-week year contains a MM-DD date twice, place it: all / first / last |
| `feast_yield_seasons` | `ADVENT LENT HOLY_WEEK EASTER POST_EASTER PRE_PENTECOST` | Seasons whose Sundays and named days outrank a feast: the day keeps the top of the cell and the feast's color covers the lower half. `none` turns this off |
| `feast_yield_every_day` | `HOLY_WEEK` | Seasons in which every day, and every day of the week after (Easter week), outranks a feast in the same way. `none` turns this off |
| `output_filename` | `church_year_calendar.svg` | SVG file to write |
| `center_svg` | `auto` | Artwork for the middle: `auto` (the tradition's own), a key from `artwork.csv` (`lutherrose`, `canterbury_cross`, `celtic_cross`, `chi_rho`, `burning_bush`, `moravian_star`, `chalice` and the rest), `none`, or a picture of your own: an `.svg`, `.png`, `.jpg`, `.gif` or `.webp` file, found from the current folder, then the project folder (see docs/rendering.md) |
| `center_svg_credit` | (none) | A picture of your own: the credit drawn with it; blank for none |
| `center_svg_scale` | (1) | A picture of your own: its size in the circle; blank is 1, filling it |
| `artwork_credit` | `auto` | Credit the artwork in the drawing's lower-left corner: `auto` (when `artwork.csv`'s `attribution` is `required` or `owner`), `always`, or `none` |
| `mid_text` | `as-set` | Text on mid-tone colors (where black and white both reach 3:1): `as-set`, `dark-reds` (black on the reds only), `dark` or `light` |
| `page_footer` | `none` | The web page's lines under the wheel: `full`, `credit` (the artwork's credit only) or `none` (see docs/web-page.md) |
| `page_churches` | (all) | The churches the web page offers: keys, tradition names or `lcms-*` prefixes (see docs/web-page.md) |
| `page_bibles` | (all) | The Bible versions the web page offers: version codes (`ESV`, `KJV` ...), languages (`english`, `de`, `sv` ...) or `own` (each church's own, no menu); one version hides the menu; see docs/web-page.md |
| `page_fixed` | (none) | Settings the web page leaves out, keeping each church's own: `calendar`, `easter`, `artwork`, `reds` (the Dark text on reds box); see docs/web-page.md |
| `page_readings` | (all) | The kinds of set of readings the web page carries and offers, the others' readings left out of it: `all`, `none`, the kinds to keep (`day,feasts`) or to leave out (`-daily,-office`), of `day`, `feasts`, `dated`, `daily`, `additional`, `psalms`, `plan`, `office` |
| `page_hide` | (none) | Rings the web page opens with turned off, rings.csv keys separated by commas (`halves,seasons`); the day cells and the artwork cannot be |
| `page_colors` | (none) | Colors the web page opens with changed, written as a link's `colors=`, separated by commas: `PURPLE-7a1f7a`, `lutheran:WHITE-fffff0`, `ring.halves-e6c3f7`, `text.halves-000000`, `empty-f0f0f0` |
| `page_hymnary` | on | The web page's Hymnary.org marks, which search hymnary.org for the hymns on each set of readings in the church's hymnal (`tradition.csv` `hymnary_hymnal`): `on`, `off` (the box unchecked) or `none` (no box and no marks) |
| `page_word_to_worship` | on | The web page's Word to Worship marks, which search wordtoworship.com for contemporary worship songs on each set of readings: `on`, `off` (the box unchecked) or `none` (no box and no marks) |
| `page_readings_layout` | tabs,columns | How the web page shows the day's readings when there are several sets: `tabs` (one set at a time, under tabs) or `columns` (all of them on the right; **▾ more** opens the box and reads them across two columns, the first on the left). Both, comma-separated, offers the other in the Settings menu, the first opening |
| `page_bible_site` | (by device) | Where the web page's readings open at first: `biblegateway` or `youversion` (blank: Bible.com on a phone, Bible Gateway elsewhere) |
| `page_help` | (none) | The page the web page's **Help** button opens: the project's `config.csv` names the user guide on GitHub. Blank or `none` leaves the button off (`--help-link`) |
| `page_feedback` | (none) | The form the web page's **Feedback** link (under the gear) opens; the day's link, date and church are added as `link=`, `date=` and `church=` (or fill `{link}`, `{date}`, `{church}` in the address); a `mailto:` address gets them in the message; blank for no link |
| `page_links` | all | The web page's links: `all`, `none`, or `bible` (each reading opens in a Bible, and each set together) and `feasts` (each commemoration's page), separated by commas; without `bible` the page has no Bible or Open in setting; see docs/web-page.md |
| `page_download` | TRUE | Whether the web page offers **Download…** (the wheel as SVG and PNG, and its lists); see docs/web-page.md |
| `page_make_page` | TRUE | Whether the web page offers **Make a page…** (a page like itself, made in the browser); see docs/web-page.md |
| `page_arrows_next_year` | FALSE | Whether the web page's arrow keys go on into the next church year (and back into the last) at the year's end; `FALSE`, they go round the year on the wheel. The page's Settings has a box for it (`--arrows-next-year`, `--arrows-same-year`) |
| `page_local_art` | FALSE | Whether the web page looks for a picture beside it (`center.svg`, or `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`) to offer in the middle; off, it asks for no files beside it, so the browser logs none missing (`--local-art`) |
| `page_edit` | TRUE | Whether the web page offers **Edit the data…** (changes to its titles, colors and readings, kept in the browser, and the changed files to download); see docs/web-page.md |
| `page_language` | auto | The language of the web page's buttons, menus and settings until the reader chooses another: `auto` (the reader's browser), `church` (each church's own), `en`, or a language in `data/ui` (`de`, `es` ...) (`--language`) |
| `page_zoom` | 1 | The magnification the web page opens at, 1 (the whole wheel) to 6, centered on the day it opens on; a link's `zoom=` wins; see docs/web-page.md |
| `page_show` | (none) | Settings the web page leaves out unless named here: `calendar`, `easter`; see docs/web-page.md |
| `icon_size` | 9 | Height of a day's icons, in user units |
| `icon_gap` | 1.5 | Space between two icons, and between the icons and the text above them |
| `png_output` | TRUE | Also write a PNG beside the SVG |
| `png_filename` | *(blank)* | PNG file to write, in the SVG's folder unless the path is absolute; blank = the SVG's name with a .png suffix |
| `png_width` | `5000` | PNG width in pixels; height follows the canvas aspect |
| `png_background` | `none` | PNG background; 'none' for transparency |
| `png_renderer` | `auto` | Which rasterizer to use: auto, inkscape, rsvg-convert, resvg, chrome or cairosvg (auto tries them in that order) |

**Canvas**

| setting | default | what it does |
| --- | --- | --- |
| `width` | `2100` | Canvas width in user units |
| `height` | `2100` | Canvas height in user units |
| `background_fill` | `none` | Canvas background fill |
| `start_angle` | `180.0` | Angle (deg) where the first week begins; 180 = 9 o'clock |

**Week ring**

| setting | default | what it does |
| --- | --- | --- |
| `day_bands` | `7` | Rows per weekly wedge (7 = Sun..Sat) |
| `week_starts_on` | `6` | Python weekday that starts a week (6 = Sunday) |
| `day_stroke` | `#000000` | Outline color of day cells |
| `day_stroke_width` | `0.4` | Outline width of day cells |
| `empty_cell_fill` | `#f0f0f0` | Fill for padding cells at the end of the year |
| `empty_cell_stroke` | `#c0c0c0` | Outline for padding cells |
| `year_line` | `FALSE` | Draw the line where the year ends and begins (between its last week and its first) wider, across the day cells and the season, half and month rings, to show that the weeks on either side are a year apart; the page's *Thicker line where the year begins* box, `--year-line` |
| `year_line_width` | `4` | Its width (the day cells' outlines are 0.4) |
| `year_seam_fill` | `auto` | Fill for the rings over the padding cells, where a year starts or ends partway through a week (the Orthodox 1 September, the Coptic Nayrouz). `auto` uses `empty_cell_fill`; `none` leaves the rings open there |

**Fonts**

| setting | default | what it does |
| --- | --- | --- |
| `font_family_serif` | `Times New Roman, Liberation Serif, Nimbus Roman, Times, serif` | Font stack used wherever a style says 'serif' |
| `font_family_sans` | `Arial, Liberation Sans, Nimbus Sans, Helvetica, sans-serif` | Font stack used wherever a style says 'sans-serif' |
| `line_height_factor` | `1.0` | Line spacing as a multiple of font size |
| `text_width_fudge` | `1.0` | Global width correction if your fonts run wide/narrow |
| `small_caps_ratio` | `0.8` | Size of small-caps lowercase relative to caps |
| `small_caps_synthetic` | TRUE | Draw small caps as real caps at two sizes instead of relying on font-variant (renderers often ignore font-variant) |

**Day-cell layout**

| setting | default | what it does |
| --- | --- | --- |
| `day_number_vertical_ratio` | `0.18` | Day number position from the outer edge, as a share of band height |
| `day_number_horizontal_ratio` | `0.05` | Day number position from the leading edge, as a share of wedge span |
| `cell_padding` | `1.5` | Blank margin inside each day cell, in user units |
| `text_fill_ratio` | `0.94` | Share of the available width a line of text may use |
| `radial_clearance` | `0.74` | Share of cell width usable by radial text (keeps clear of the day number) |
| `day_number_gap` | `2.5` | Clear space kept between the day number and any label beside it |
| `top_label_reserve` | `0.34` | Most of the band a cell's month/year label may take; it takes only what it needs |
| `color_split_max` | `0.70` | Most of a cell the upper color may take when a commemoration recolors the foot |
| `color_split_gain` | `0.15` | How much better the worse-off label must do before that break moves off center |
| `split_share_min` | `0.34` | Smallest share of a cell given to one of two stacked labels |
| `split_share_max` | `0.66` | Largest share of a cell given to one of two stacked labels |

**Auto-fit**

| setting | default | what it does |
| --- | --- | --- |
| `autofit` | TRUE | Shrink/wrap/rotate text automatically to fit its cell |
| `autofit_allow_grow` | FALSE | Let text grow past the style's font_size when there is room |
| `autofit_max_scale` | `1.0` | Ceiling on growth, as a multiple of the style font_size |
| `autofit_step` | `0.25` | Font-size granularity used while fitting |
| `text_orientation` | `tangential` | Day-cell text direction: tangential  /  radial  /  auto |
| `radial_min_line_saving` | `2` | Lines a label must save before it is turned radial (0 = turn it whenever radial wraps better) |

**Ring labels**

| setting | default | what it does |
| --- | --- | --- |
| `curved_text_vertical_offset` | `-0.35` | Curved ring labels shift, as a multiple of font size |
| `ring_label_arc_usage` | `0.95` | Share of a ring segment's arc a curved label may use |
| `ring_label_autofit` | TRUE | Shrink ring labels that do not fit their arc |
| `ring_label_radial_fallback` | TRUE | Turn a ring label across the ring when the arc is too short |
| `ring_label_min_font_size` | `6.0` | Never shrink a ring label below this |
| `ring_label_hide_if_unfit` | FALSE | Drop a ring label that still does not fit instead of overflowing |
| `ring_label_uniform` | seasons | Rings (rings.csv keys, separated by spaces or commas) whose labels all take one size: the largest at which every one fits, spilling past short arcs where it must |
| `ring_label_spill` | TRUE | Let a short segment's label run past its arc into the free ring on either side (clear of every other label, within the year) rather than shrink or turn across the ring |
| `ring_subtitle_ratio` | `0.78` | Subtitle size as a share of the ring label it follows |
| `ring_subtitle_separator` | `": "` | What joins a ring label to its subtitle on the arc; quote it in config.csv so its spaces are kept |
| `month_label_largest_only` | TRUE | Label only the longest run of each month (avoids duplicates at the year seam) |

**Reporting**

| setting | default | what it does |
| --- | --- | --- |
| `warn_below_font_size` | `6.0` | Report labels that had to shrink below this size |
