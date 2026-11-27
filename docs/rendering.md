# Drawing, PNG export and fonts

## The command line

`python church_year_image.py` draws the year folder `--data` names (`./data`) as
`config.csv` describes it, hand edits included. Everything else is an option,
so drawing another church, year or look never means editing `config.csv`:

| option | what it does | `config.csv` setting it stands in for |
| --- | --- | --- |
| `church` `year` | another church (a key from `data/traditions.csv`; `--list` lists them) and the year its church year begins in; `church_year_image.py 2026` is a year | `lectionary`, `church_year_start`/`_end` |
| `--from YEAR` `--to YEAR` | one wheel for each church year in the span | |
| `--calendar`, `--paschalion`, `--subcalendar KEY` (repeatable), `--latin-names`/`--no-latin-names` | how the year is worked out, as in `new_year.py` | `calendar`, `paschalion`, `subcalendars`, `latin_names` |
| `--feasts all\|festivals\|principal\|none` | how many feasts | `feast_detail` |
| `--art KEY\|FILE` | the picture in the middle: `auto`, a key from `data/artwork.csv`, `none`, or a file of your own (below) | `center_svg` |
| `--art-date DATE` | the picture of that day's season in the middle (`2026-12-25`: the manger), as the page's Artwork: By season shows for the day chosen; `data/season_art.csv` says which season shows which, and a day in a season without one keeps the church's own | |
| `--art-credit TEXT`, `--art-scale N` | your own picture's credit and size | `center_svg_credit`, `center_svg_scale` |
| `--credit always\|auto\|none` | the artwork's credit in the corner | `artwork_credit` |
| `--mid-text as-set\|dark\|dark-reds\|light` | text on the mid-tone colors | `mid_text` |
| `--hide RING` (repeatable, or `gold,halves`) | leave a ring out, by its `rings.csv` key, as the page's `hide=` does; the others close over the gap. The day cells and the center stay | |
| `--color-changes CHANGES` | repaint colors for this drawing, as the page's Colors menu does and a link's `colors=` writes them: `PURPLE-7a1f7a` (every church), `lutheran:WHITE-fffff0` (a tradition), `lutheran:wels-one-year:RED-c00000` (a church), `PURPLE.text-ffffff` (a color's words, which then stay as chosen), `NONE-ffffff/bfbfbf` (stripes), `ring.halves-e6c3f7`, `text.halves-000000`, `empty-f0f0f0`. Text on a day stays readable | |
| `--png-background COLOR` | the PNG's background, `none` (clear) or a color, as the page's Download offers | `png_background` |
| `-o PATH` (`--output`, `--out`) | the SVG file, or a folder for the default name | `output_filename` |
| `--png`/`--no-png`, `--png-width`, `--png-renderer` | the PNG (below) | `png_output`, `png_width`, `png_renderer` |
| `--report` | every label that had to shrink, wrap hard or overflow | |

A church, a year or any of the year options (`--from`, `--to`, `--calendar`,
`--paschalion`, `--subcalendar`, `--latin-names`) means the year is worked out
from the rules in `--data` rather than drawn as it stands. It is written into a
scratch folder exactly as `new_year.py` writes a year folder — the same code,
the same copy of `config.csv` with your settings — and drawn from there, so
`church_year_image.py roman 2027` is byte for byte what `new_year.py 2027
--lectionary roman` and then `church_year_image.py --data data_2027` make, and
`config.csv` is never rewritten. Without a church named, the church and its
subcalendars are `config.csv`'s; named, the church's own calendar and Latin
names apply, as on the page and in the listing scripts.

The other options lay settings over `config.csv` (and the tradition's own) for
this run only. A church named writes `KEY_YYYY-YY_calendar.svg`; otherwise the
name is `output_filename` (`church_year_YYYY-YY_calendar.svg` for a year worked
out). `-o` takes a file, or a folder — one that exists, or any path ending in
`/` or without a suffix — to put that name in; a span of years needs a folder.
`png_filename` applies only to `./data` drawn as it stands, since a span of
years would write every PNG over the last.

## The picture in the middle

`center_svg` (or `--art`) names the picture: `auto`, the church's own
(`center_art` in its `tradition.csv`); a key from `data/artwork.csv`, which
carries the picture's size and credit; `none`; or a file of your own:

```
python church_year_image.py --art my_cross.svg
python church_year_image.py --art photo.jpg --art-credit "Photo: J. Smith" --art-scale 0.9
```

```
center_svg,my_cross.png
center_svg_credit,Drawn by the youth group
center_svg_scale,
```

A file name is looked for in the current folder, then the project folder (the
one `church_year_image.py` is in), then `data/` and the folder above it; a full path
works too. `.svg`, `.png`, `.jpg`/`.jpeg`, `.gif` and `.webp` are taken:

* **An SVG** has its drawing copied into the wheel, scaled so its `viewBox`
  (or `width` and `height`) fills the circle's width or height and centered.
* **A photo or scan** is embedded whole as a `data:` URI, so the SVG stays one
  file to pass on, at its pixel size, scaled the same way, and cut to the
  circle so a square picture comes out round instead of covering the month
  ring. Its size is read from the file itself; Pillow is used only for a file
  whose header the script cannot read. Large photos make large SVGs: a few
  hundred pixels across is plenty for the middle of the wheel.

Your picture carries no credit unless you give one (`--art-credit`,
`center_svg_credit`); given one, it is drawn in the lower-left corner as an
`artwork.csv` credit is (`artwork_credit`: `auto` and `always` draw it, `none`
does not). `center_svg_scale` (`--art-scale`) sizes it: blank is 1, filling the
circle, and 0.9 leaves a margin; above 1 the picture is cut to the circle,
so it does not cover the rings. A file that cannot be read leaves the middle
blank with a message. The pictures in `artwork.csv` draw exactly as before.

The web page takes the same: `center_svg` naming a file adds it to the page's
Artwork menu and opens on it, as does `church_year.py --art FILE` (see
[web-page.md](web-page.md)). `web/export_data.py` freezes the same markup
for the browser that `church_year_image.py` draws, so the two cannot disagree.

## PNG output

The SVG is the master; the PNG is rasterized from it. `config.csv` ships with
`png_renderer,auto`, which tries these in order and reports which one it used.
Set `png_renderer` (or `--png-renderer NAME`) to pin one instead:

| renderer | how to get it | notes |
| --- | --- | --- |
| **Inkscape** | inkscape.org | best all-round: exact size, full text support, no helpers needed |
| **rsvg-convert** | `apt install librsvg2-bin`, `brew install librsvg` | fast, exact |
| **resvg** | github.com/linebender/resvg | exact |
| **Chrome / Edge** | already installed on most machines | faithful, but see below |
| **cairosvg** | `pip install cairosvg` | easiest to install, weakest on text — tried last |

`python church_year_image.py --list-renderers` shows which of these your machine has
and where each was found, which is the quickest way to settle why a PNG looks
wrong.

A pinned renderer is a pin, not a preference: on a machine without it the run
writes the SVG, says so, and writes no PNG rather than quietly using something
else. `auto` always takes the best one present.

**Inkscape** renders the size you ask for exactly, needs no helper library, and
handles font stacks, positioned `<tspan>` runs and text on a path properly.

**Chrome** is equally faithful — it is a browser engine, so its PNG matches
what a browser shows — and it is what makes a PNG possible out of the box on
most machines. Headless Chrome screenshots are the size of the *window*, not
the page, and Chrome only paints into the window minus its frame, so sizing the
window to the artwork silently loses a strip off the bottom. The script asks
Chrome how tall its viewport really is, makes the window that much taller, and
trims the surplus with Pillow if it is installed. If Pillow is missing you
still get the complete artwork, just with a blank strip below it, and a message
saying so. Inkscape, rsvg-convert and resvg avoid that entirely.

**CairoSVG** comes last on purpose. It is the easiest to install, but it is weak
on exactly what this drawing leans on: it ignores CSS generic font families (so
`serif` silently becomes a default sans, wider than the metrics the layout was
measured with), it does not advance `<tspan>` runs, and it drops
`font-variant`. `auto` reaches it only when nothing else is available.

Neither Inkscape nor Chrome puts itself on `PATH` on Windows, so the script
also looks in the usual install locations — including `%LOCALAPPDATA%`, where
Chrome lands when it is installed for the current user rather than the whole
machine. Set `INKSCAPE_PATH` or `CHROME_PATH` if yours is somewhere else. Both
the Inkscape 1.x and 0.92 command-line forms are handled, and Chrome is run with
a throwaway profile so an already-open Chrome window cannot swallow the request.

If a pinned renderer does not work, the message says which case it is — not
found, or found at a given path and failed with the tool's own error — and lists
what else is available:

```
  ! png_renderer 'chrome' was found at C:\...\chrome.exe but failed, so no PNG was written.
    exit code 21: <whatever Chrome reported>
    Available here instead: inkscape, cairosvg — set png_renderer in config.csv
```

`png_background` in `config.csv` takes `none` for a transparent PNG or any CSS
color for a solid one. `png_width` sets the pixel width and the height follows
the canvas aspect; `--png-width` overrides it for a single run. As shipped the
PNG is 5000x5000 and transparent — roughly 240 dpi at 21 inches. The SVG's own
background is separate (`background_fill`) and stays `none`.

## Running on any machine

The scripts run the same on macOS, Linux and Windows. Paths are handled through
`pathlib` rather than by joining strings, the CSVs are written with explicit
UTF-8 and `\n` line endings whatever the platform, and console output is forced
to UTF-8 so the ✓ in these messages cannot crash a run under a C/POSIX locale or
a legacy Windows code page — which is what happens the moment output is
redirected to a file, as under cron or in a container.

The optional Python packages — CairoSVG, and Pillow for trimming Chrome's
screenshot — are imported lazily, inside `try`/`except`, and only for PNG
export. The other renderers are ordinary programs, not Python packages, so they
are installed with the system package manager rather than pip.

CairoSVG binds to the native Cairo library, which pip does not supply. That is
usually already present on Linux and macOS; if `import cairosvg` raises
`OSError: no library called "cairo-2" was found`, install it with
`apt install libcairo2` / `brew install cairo`, or leave CairoSVG out.

`--list-renderers` prints the resolved path of each renderer. The search covers
`PATH`, then the usual macOS app bundles (`/Applications/Inkscape.app/…`,
`/Applications/Google Chrome.app/…`), then `/opt/homebrew/bin`,
`/usr/local/bin`, `/opt/local/bin` and `/snap/bin` — because a launchd or cron
job gets a far barer `PATH` than a terminal does, and a Homebrew Inkscape would
otherwise look missing.

## Fonts

`config.csv` names real font stacks rather than the CSS generics `serif` and
`sans-serif`:

```
font_family_serif,"Times New Roman, Liberation Serif, Nimbus Roman, Times, serif"
font_family_sans,"Arial, Liberation Sans, Nimbus Sans, Helvetica, sans-serif"
```

This matters more than it looks. Auto-fit measures every label against built-in
Times and Helvetica advance widths, and the first four entries in each stack are
all metrically identical to those — Liberation and Nimbus were drawn as
metric-compatible replacements for Times New Roman and Arial. Name them and the
measurements are not an estimate but exact: measured against the real font
files, predicted widths came out within 0.1% across serif, italic, bold and
heavy sans.

Leaving the generics bare is what causes trouble. A generic is a *request*, and
a renderer that does not honor it substitutes something else — often a default
sans, which is wider than Times, so text measured to fit overflows its cell.
That is the classic "PNG text is wider than the SVG, and the serifs are gone".

`text_styles.csv` still says `serif` or `sans-serif`; those are **roles**, mapped
through the two settings above. Measurement keys off the role, never the
resolved stack, so naming a concrete face cannot confuse the metrics.

The shipped order suits Windows and macOS, where Times New Roman and Arial are
both present. On Linux they usually are not, and Inkscape, Chrome and every
other renderer that understands a font stack simply fall through to Liberation,
which is metrically identical — so the drawing is unchanged and there is nothing
to do. The exception is CairoSVG, which reads only the *first* name in a stack:
if you use it on Linux, put `Liberation Serif` and `Liberation Sans` first. `text_width_fudge`
scales every measurement at once if the face you end up with runs wide or narrow.

## Tuning notes

**Small caps.** `font-variant: small-caps` is widely ignored — CairoSVG drops
it, and it is lost in several SVG-to-raster and print paths, so the same file
can show small caps on screen and mixed case in an export. The script therefore
builds small caps itself, as ordinary capitals at two sizes
(`small_caps_ratio`, default `0.8`).

Each run is written with its own absolute `x` rather than being left to flow.
That is deliberate: renderers also disagree about `<tspan>` advance — CairoSVG
re-applies the parent's `x` to every tspan, which stacks a whole line on top of
its first letter. Spaces are not drawn at all; they only move the pen along.
XML strips leading whitespace from an element, so a run that began with a space
would have its first letter pulled back onto the previous word — Inkscape sets
`OUR LORD` as `OURL ORD` — while a run that never contains one cannot be
misplaced by any renderer. The cost is that a small-caps line in the SVG holds
`OURLORD` as separate runs, so text search and hand-editing in a drawing program
do not see the spaces; `small_caps_synthetic,FALSE` gives them back at the price
of renderer-dependent small caps. The trade-off is that those positions come from the built-in
font metrics, so if your `serif` font is much wider or narrower than Times the
letter spacing inside a small-caps line will look loose or tight; that is what
`text_width_fudge` corrects. `small_caps_synthetic,FALSE` reverts to plain
`font-variant` and lets the renderer decide.

**Text looks slightly too wide or too narrow.** The metrics assume Times and
Helvetica proportions. If your viewer substitutes something else, set
`text_width_fudge` a little above or below `1.0` and everything rescales
together.

**You want the old fixed layout back.** Set `autofit,FALSE`. Every label then
uses its style's `font_size` verbatim and wraps to the available width, and the
override columns are the only way to adjust anything — the behavior the
previous version had.

**A label is still tight.** Run with `--report`. Anything that had to shrink
below `warn_below_font_size`, or that could not be made to fit at all, is listed
with its date. Raise `warn_below_font_size` to see more.

**Labels crowd the day number.** Raise `day_number_gap`. To move the number
itself, use `day_number_vertical_ratio` (down from the outer edge) and
`day_number_horizontal_ratio` (in from the leading edge).

**You want to try rotated text after all.** Set `text_orientation,auto`. A label
is then turned radially only when that saves at least `radial_min_line_saving`
lines of wrapping (default 2), which in this year's data is one cell.

**A month name overflows its arc.** It shrinks automatically. If you would
rather it turn across the ring, set that ring's `label_mode` to `radial`; if you
would rather it disappear, set `ring_label_hide_if_unfit,TRUE`.

A short segment between long ones need not shrink: its label may run past
its own arc into the free ring on either side (`ring_label_spill`, on by
default). The shortest arcs go first; a label keeps its arc's middle under
it, sits as near centered as the room allows, stays half its size clear of
every other label, and never crosses the year's start or end. So the
Orthodox Apostles' Fast, often a week or less, keeps the ring's full size in
most years. A sliver too short even for that, whose name the ring shows
elsewhere (the one Sunday "After Pentecost" before the Apostles' Fast), is
left unlabeled rather than turned across the ring in tiny type.

The seasons ring sets all its names at one size (`ring_label_uniform`,
config.csv: `seasons`): the largest, from the ring's 24 points down, at which
every name fits, spilling past short seasons where it must. Most churches'
seasons keep 24 points; the Orthodox ring, with its short fasts and feasts
side by side, takes 18.75. Name other rings there to treat them the same, or
leave it blank to size each label by itself.

**Next year.** Run `new_year.py` (above) rather than editing dates by hand —
Easter moves five weeks across the calendar, so the count of Sundays after
Epiphany and after Pentecost changes and every ordinal is renumbered. The
commemorations file uses `MM-DD` and carries over unchanged.

Everything that depends on the shape of the year is worked out from those
dates, so no other file needs touching. The wheel divides 360° by however many
weeks the year holds, the month ring cuts itself at the real month boundaries,
and auto-fit re-flows the text for whatever wedge width results. Two things are
worth knowing:

* **53-week years.** Most church years are 364 days, but some are 371 —
  2027-28 and 2033-34 among them. The wedges are then about 2% narrower. Both
  render with no labels overflowing.
* **A commemoration can land twice.** In a 371-day year the span covers late
  November at both ends, so a `MM-DD` row near the seam falls inside the range
  twice — St. Andrew on 30 November 2027 *and* 30 November 2028. Both really do
  occur in that church year, so `feast_repeat,all` shows both; set it to
  `first` or `last` to keep only one.
