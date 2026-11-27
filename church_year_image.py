#!/usr/bin/env python3
"""
The church year wheel as a still image: an SVG, and a PNG beside it.  (The
interactive web page is church_year.py's.)

    python church_year_image.py                         # ./data's year, as config.csv says
    python church_year_image.py roman 2027              # roman_2027-28_calendar.svg
    python church_year_image.py 2026 -o wheels/         # config.csv's church, Advent 2026
    python church_year_image.py elca --from 2025 --to 2030 -o wheels/   # six years
    python church_year_image.py --art my_cross.png --art-credit "Photo: J. Smith"
    python church_year_image.py --hide halves --hide seasons --mid-text dark-reds
    python church_year_image.py --list                  # the churches' keys

With no church, no year and no year option (--from, --to, --calendar,
--paschalion, --subcalendar, --latin-names) it draws the year folder --data
names (./data) as it stands, hand edits included.  Named, or given a year, it
works the year out from the rules exactly as new_year.py does, in a scratch
folder, and draws that: config.csv is never rewritten.  The other options lay
settings over config.csv for this drawing only.


Everything that can reasonably be data lives in CSV files under the data
directory: dates, names, colors, ring geometry, fonts, and layout numbers.
The script itself only contains logic.

Text is auto-fitted: each label is measured with real font metrics and the
size / wrapping / orientation (tangential vs radial) are chosen so the text
fits its wedge. Per-entry overrides in the CSVs still win when present, so
they remain available as an escape hatch.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path

# The modules the scripts share (calendars.py, traditions.py) live in lib/.
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from calendars import (CivilDate, PASCHALIONS, RECKONINGS, GREGORIAN,
                       days_between as _days_between)
from itertools import count
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Optional, Sequence

# ============================================================================
# FONT METRICS
# ============================================================================
# Advance widths in 1/1000 em for ASCII 32..126, taken from the Adobe core
# font metrics (Times / Helvetica).  These are the fallbacks browsers and
# drawing programs use for the generic "serif" / "sans-serif" families, so
# they predict rendered width well.  If your viewer uses noticeably wider or
# narrower fonts, nudge `text_width_fudge` in config.csv.

_FONT_METRICS_RAW: dict[str, str] = {
    "serif|normal|normal":
        "250,333,408,500,500,833,778,333,333,333,500,564,250,333,250,278,500,500,500,500,500,500,500,500,500,500,278,278,564,564,564,444,921,722,667,667,722,611,556,722,722,333,389,722,611,889,722,722,556,722,667,556,611,722,722,944,722,722,611,333,278,333,469,500,333,444,500,444,500,444,333,500,500,278,278,500,278,778,500,500,500,500,333,389,278,500,500,722,500,500,444,480,200,480,541",
    "serif|bold|normal":
        "250,333,555,500,500,1000,833,333,333,333,500,570,250,333,250,278,500,500,500,500,500,500,500,500,500,500,333,333,570,570,570,500,930,722,667,722,722,667,611,778,778,389,500,778,667,944,722,778,611,778,722,556,667,722,722,1000,722,722,667,333,278,333,581,500,333,500,556,444,556,444,333,500,556,278,333,556,278,833,556,500,556,556,444,389,333,556,500,722,500,500,444,394,220,394,520",
    "serif|normal|italic":
        "250,333,420,500,500,833,778,333,333,333,500,675,250,333,250,278,500,500,500,500,500,500,500,500,500,500,333,333,675,675,675,500,920,611,611,667,722,611,611,722,722,333,444,667,556,833,667,722,611,722,611,500,556,722,611,833,611,556,556,389,278,389,422,500,333,500,500,444,500,444,278,500,500,278,278,444,278,722,500,500,500,500,389,389,278,500,444,667,444,444,389,400,275,400,541",
    "serif|bold|italic":
        "250,389,555,500,500,833,778,333,333,333,500,570,250,333,250,278,500,500,500,500,500,500,500,500,500,500,333,333,570,570,570,500,832,667,667,667,722,667,667,722,778,389,500,667,611,889,722,722,611,722,667,556,611,722,667,889,667,611,611,333,278,333,570,500,333,500,500,444,500,444,333,500,556,278,278,500,278,778,556,500,500,500,389,389,278,556,444,667,500,444,389,348,220,348,570",
    "sans|normal|normal":
        "278,278,355,556,556,889,667,222,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,278,278,584,584,584,556,1015,667,667,722,722,667,611,778,722,278,500,667,556,833,722,778,667,778,722,667,611,722,667,944,667,667,611,278,278,278,469,556,222,556,556,500,556,556,278,556,556,222,222,500,222,833,556,556,556,556,333,500,278,556,500,722,500,500,500,334,260,334,584",
    "sans|bold|normal":
        "278,333,474,556,556,889,722,278,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,333,333,584,584,584,611,975,722,722,722,722,667,611,778,722,278,556,722,611,833,722,778,667,778,722,667,611,722,667,944,667,667,611,333,278,333,584,556,278,556,611,556,611,556,333,611,611,278,278,556,278,889,611,611,611,611,389,556,333,611,556,778,556,556,500,389,280,389,584",
    "sans|normal|italic":
        "278,278,355,556,556,889,667,222,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,278,278,584,584,584,556,1015,667,667,722,722,667,611,778,722,278,500,667,556,833,722,778,667,778,722,667,611,722,667,944,667,667,611,278,278,278,469,556,222,556,556,500,556,556,278,556,556,222,222,500,222,833,556,556,556,556,333,500,278,556,500,722,500,500,500,334,260,334,584",
    "sans|bold|italic":
        "278,333,474,556,556,889,722,278,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,333,333,584,584,584,611,975,722,722,722,722,667,611,778,722,278,556,722,611,833,722,778,667,778,722,667,611,722,667,944,667,667,611,333,278,333,584,556,278,556,611,556,611,556,333,611,611,278,278,556,278,889,611,611,611,611,389,556,333,611,556,778,556,556,500,389,280,389,584",
}
_FIRST_CODE = 32
_LAST_CODE = 126
_DEFAULT_WIDTH = 500


def _build_metrics() -> dict[str, tuple[int, ...]]:
    return {k: tuple(int(x) for x in v.split(","))
            for k, v in _FONT_METRICS_RAW.items()}


_FONT_METRICS = _build_metrics()

# Past ASCII: the letters the calendars use, read from the Liberation fonts by
# tools/font_widths.py (church_year.js: TextMeasurer.extra).
from font_widths import EXTRA_WIDTHS as _EXTRA_RAW  # noqa: E402
_FONT_EXTRA = {k: {int(c): int(w) for c, w in (p.split(":") for p in v.split(","))}
               for k, v in _EXTRA_RAW.items()}


# The step from one line of a two-line date label to the next, in font sizes.
DATE_LINE_HEIGHT = 1.15


def _plain_sum(values) -> float:
    """Floats added one by one, left to right, as church_year.js adds them.
    The built-in sum() compensates for rounding since Python 3.12, which can
    leave the last digit of a coordinate different from the browser's."""
    total = 0.0
    for v in values:
        total += v
    return total


class TextMeasurer:
    """Measures rendered text width using core-font advance widths."""

    def __init__(self, fudge: float = 1.0, small_caps_ratio: float = 0.8) -> None:
        self.fudge = fudge
        self.small_caps_ratio = small_caps_ratio
        self._cache: dict[tuple, float] = {}

    SANS_HINTS = ("sans", "arial", "helvetica", "verdana", "tahoma", "calibri",
                  "segoe", "roboto", "futura", "gill", "franklin", "avenir",
                  "lato", "open sans", "noto sans", "liberation sans", "dejavu sans")

    @classmethod
    def _face_key(cls, family: str, weight: str, style: str) -> str:
        """Pick the metric table.  `family` is the role (serif / sans-serif)."""
        name = (family or "").strip().lower()
        fam = "sans" if any(hint in name for hint in cls.SANS_HINTS) else "serif"
        try:
            bold = float(weight) >= 600
        except (TypeError, ValueError):
            bold = str(weight).strip().lower() in ("bold", "bolder", "800", "900")
        italic = str(style).strip().lower() in ("italic", "oblique")
        return f"{fam}|{'bold' if bold else 'normal'}|{'italic' if italic else 'normal'}"

    def _char_widths(self, family: str, weight: str, style: str) -> tuple[int, ...]:
        return _FONT_METRICS.get(self._face_key(family, weight, style),
                                 _FONT_METRICS["serif|normal|normal"])

    def width(self, text: str, size: float, family: str = "serif",
              weight: str = "normal", style: str = "normal",
              variant: str = "normal") -> float:
        """Return the rendered width of `text` in user units."""
        if not text:
            return 0.0
        key = (text, size, family, weight, style, variant)
        hit = self._cache.get(key)
        if hit is not None:
            return hit
        widths = self._char_widths(family, weight, style)
        extra = _FONT_EXTRA.get(self._face_key(family, weight, style), _FONT_EXTRA["serif|normal|normal"])
        small_caps = str(variant).strip().lower() == "small-caps"
        total = 0.0
        for raw in text:
            glyphs, scale = raw, 1.0
            if small_caps and raw.islower():
                glyphs = raw.upper()        # may be two letters: "ß" -> "SS"
                scale = self.small_caps_ratio
            for ch in glyphs:
                code = ord(ch)
                if _FIRST_CODE <= code <= _LAST_CODE:
                    w = widths[code - _FIRST_CODE]
                else:
                    w = extra.get(code, _DEFAULT_WIDTH)
                total += w * scale
        result = total / 1000.0 * size * self.fudge
        self._cache[key] = result
        return result


# ============================================================================
# SETTINGS
# ============================================================================

# How much of the feasts CSV to draw.  The file holds three kinds of row: those
# that set the day's color outright, those that only color the lower half of
# the cell, and those that carry no color at all.
FEAST_DETAIL = ("all", "festivals", "principal", "none")


def _as_bool(v: Any) -> bool:
    return str(v).strip().lower() in ("1", "true", "yes", "y", "on")


def _as_date(v: Any) -> str:
    """Left as text: which calendar it is written in is itself a setting.

    Settings.__init__ turns these into dates once the whole file is parsed and
    `calendar` is known.
    """
    return str(v).strip()


def _as_str(v: Any) -> str:
    return str(v).strip()


def _as_text(v: Any) -> str:
    """A string kept exactly as written, spaces and all (quote it in the CSV)."""
    return str(v)


def _as_keys(v: Any) -> list[str]:
    """Season keys, separated by spaces or commas: `ADVENT LENT HOLY_WEEK`."""
    return [k.upper() for k in str(v).replace(",", " ").split()]


# Where the Sundays and principal days outrank the saints' days.  Kept as
# settings rather than written into the logic, because the season keys are the
# user's own (seasons.csv).
DEFAULT_FEAST_YIELD = ["ADVENT", "LENT", "HOLY_WEEK", "EASTER", "POST_EASTER",
                       "PRE_PENTECOST"]
DEFAULT_FEAST_EVERY_DAY = ["HOLY_WEEK"]


# Settings whose surrounding spaces are part of the value.
_KEEP_SPACES = {"ring_subtitle_separator"}


# name -> (parser, default, help)
#
# These are only the FALLBACKS.  Any row present in data/config.csv overrides
# the value here, and the shipped config.csv lists every setting, so editing
# this table has no effect until you delete or blank the matching config row.
SETTING_SPEC: dict[str, tuple[Callable[[Any], Any], Any, str]] = {
    # --- required-ish -------------------------------------------------------
    "church_year_start":            (_as_date, None, "First day of the church year (YYYY-MM-DD)"),
    "church_year_end":              (_as_date, None, "Last day of the church year (YYYY-MM-DD)"),
    "output_filename":              (_as_str, "church_year_calendar.svg", "SVG file to write"),
    "center_svg":                   (_as_str, "auto", "Artwork for the middle: auto (the tradition's own), a key from artwork.csv, none, or a picture of your own (.svg, .png, .jpg, .gif or .webp; found from the current folder, then the project folder)"),
    "center_svg_credit":            (_as_text, "", "A picture of your own (center_svg naming a file): the credit drawn with it, as artwork_credit says; blank for none"),
    "center_svg_scale":             (_as_str, "", "A picture of your own: its size inside the circle (blank = 1, filling its width or height; 0.9 leaves a margin)"),
    "artwork_credit":               (_as_str, "auto", "Credit the middle's artwork in the drawing's lower-left corner: auto (when artwork.csv's attribution is required or owner), always, or none"),
    "mid_text":                     (_as_str, "as-set", "Text on mid-tone colors -- those on which both black and white text reach 3:1 contrast: as-set (colors.csv's choice), dark (black), light (white) or dark-reds (black on the reds only)"),
    "page_footer":                  (_as_str, "full", "The web page's lines under the wheel: full (instructions, notes and the artwork's credit), credit (the credit only), or none (nothing; a small (i) still opens the credit of artwork whose license requires it)"),
    "page_bibles":                  (_as_str, "", "The Bible versions the web page offers: version codes (ESV, KJV ...), languages (english, de, sv ...) or own (each church's own, no menu); one version hides the menu; blank for all"),
    "page_fixed":                   (_as_str, "", "Settings the web page leaves out, keeping each church's own: calendar, easter, artwork, reds (the Dark text on reds box), separated by spaces or commas; blank for none"),
    "page_show":                    (_as_str, "", "Settings the web page leaves out unless named here: calendar, easter"),
    "page_zoom":                    (_as_str, "", "The magnification the web page opens at, 1 to 6 (blank: 1, the whole wheel)"),
    "page_readings":                (_as_str, "", "The kinds of set of readings the web page carries and offers (the others are left out of it): all, none, day,feasts or -daily,-office (blank: all)"),
    "page_hide":                    (_as_str, "", "Rings the web page opens with turned off: rings.csv keys separated by commas"),
    "page_colors":                  (_as_str, "", "Colors the web page opens with changed: PURPLE-7a1f7a,lutheran:WHITE-fffff0,ring.halves-e6c3f7 ... as a link's colors="),
    "page_hymnary":                 (_as_str, "", "The web page's Hymnary.org marks (hymns in the church's hymnal for each set of readings, where tradition.csv names it in hymnary_hymnal): on, off (the box unchecked) or none (no box; blank: on)"),
    "page_word_to_worship":         (_as_str, "", "The web page's Word to Worship marks (contemporary worship songs for each set of readings): on, off (the box unchecked) or none (no box; blank: on)"),
    "page_readings_layout":         (_as_str, "", "How the web page shows the day's readings when there are several sets: tabs, columns, or both comma-separated (the first opening, the other in Settings; blank: tabs,columns)"),
    "page_bible_site":              (_as_str, "", "Where the web page's readings open at first: biblegateway or youversion (blank: by device)"),
    "page_help":                    (_as_str, "", "The page the web page's Help button opens (https://), such as the user guide; blank for no button"),
    "page_feedback":                (_as_str, "", "The form the web page's Feedback link opens (https:// or mailto:); blank for no link"),
    "page_links":                   (_as_str, "", "The web page's links: all, none, or bible (the readings) and feasts (the commemorations' pages), separated by commas (blank: all)"),
    "page_download":                (_as_bool, True, "Whether the web page offers Download... (the wheel as SVG and PNG, and its lists)"),
    "page_make_page":               (_as_bool, True, "Whether the web page offers Make a page... (a page like itself, made in the browser)"),
    "page_edit":                    (_as_bool, True, "Whether the web page offers Edit the data... (changes to its titles, colors and readings, kept in the browser, and the changed files to download)"),
    "page_arrows_next_year":        (_as_bool, False, "Whether the web page's arrow keys go on into the next church year (and back into the last) at the year's end; off, they go round the year on the wheel. The page's Settings has a box for it"),
    "page_local_art":               (_as_bool, False, "Whether the web page looks for a picture beside it (center.svg, .png, .jpg, .jpeg, .webp, .gif) to offer in the middle; off, it asks for no files, so the browser logs no missing ones"),
    "page_churches":                (_as_str, "", "The churches the web page offers: blank for all, or keys, tradition names or key prefixes ending in * (lcms-*), separated by spaces or commas"),
    "ring_subtitle_ratio":          (float, 0.78, "Size of a ring label's trailing subtitle, as a fraction of the label"),
    "ring_subtitle_separator":      (_as_text, ": ", "What joins a ring label to its subtitle"),
    "festival_half_end":            (_as_str, "auto", "Where the festival half ends: auto (one-year: the Saturday after Trinity; three-year: the Saturday after Pentecost), pentecost-eve, pentecost-week or trinity-week (read by new_year.py)"),
    "feast_detail":                 (_as_str, "all", "How much of the feasts to draw: all, festivals (principal and festival rows), principal (principal rows only), or none"),
    "calendar":                     (_as_str, "gregorian", "Which calendar the dates are reckoned in: gregorian, julian or revised-julian"),
    "paschalion":                   (_as_str, "", "Which rule finds Easter: gregorian or julian (blank follows the calendar)"),
    "lectionary":                   (_as_str, "lcms-three-year", "Which tradition this year follows: a key from traditions.csv, such as lcms-three-year, roman, episcopal or anglican-bcp-1662 (new_year.py reads it)"),
    "subcalendars":                 (_as_str, "", "Extra calendars laid over the tradition's own, by key from its subcalendars.csv, separated by spaces (read by new_year.py)"),
    "latin_names_default":        (_as_str, "", "A tradition's own default for latin_names (tradition.csv; LCMS One-year: TRUE)"),
    "readings":                   (_as_str, "", "Shared readings files from data/readings/ this tradition uses, by name: rcl rcl-us (page only)"),
    "bible_version":              (_as_str, "", "The Bible version the page's reading links open by default for this tradition (ESV when blank; page only)"),
    "feast_link":                 (_as_str, "", "Where the page links a commemoration's name when feasts.csv gives no link: a URL with {name} (Wikipedia search when blank; page only)"),
    "reading_rotate":             (_as_str, "", "readings.csv: run id, its full number of weeks, and the title of rows whose weeks rotate when the run is short (ELHB; page only)"),
    "reading_cycle":              (_as_str, "", "readings.csv: abc = three-year series, Year A beginning Advent 2025, 2028 ... (page only)"),
    "hymnary_hymnal":             (_as_str, "", "Hymnary.org's code for the church's hymnal (lsb2006): the web page's Hymn search looks in it for hymns on each set of readings (page only)"),
    "hymnary_hymnal_name":        (_as_str, "", "That hymnal's name, for the Hymn search mark's title (Lutheran Service Book (2006)) (page only)"),
    "color_labels":               (_as_str, "", "The church's own words for its colors in the page's header, where they differ from its language's (data/languages): purple=morado; scarlet=rojo; none=sin color"),
    "language":                   (_as_str, "en", "The church's language, by code (data/languages/<code>.csv): the month ring and the dates on the wheel in it, and on the page the date line and the Bible book names"),
    "weekday_titles":             (_as_str, "", "How the web page names a weekday that has no name of its own, from the Sunday before it: after (blank; Tuesday after the Sixth Sunday after Pentecost, Wednesday of Laetare) or week (Tuesday of the Sixth Week after Pentecost) (page only)"),
    "reading_order":              (_as_str, "", "readings: groups of kinds (split by |) put in this order within each set, the others staying put (ELCA: complementary series first; page only)"),
    "reading_labels":             (_as_str, "", "readings.csv: the page's names for reading kinds, as kind=Name; kind=Name (page only)"),
    "reading_hymns":              (_as_str, "", "readings: the kinds that are hymns sung with a set rather than readings (LCMS: hymn_lsb hymn_entrance hymn_day ...; data/readings/lsb-hymns.csv): kept apart from the readings, and listed under Hymns by the page's Hymn search (page only)"),
    "hymn_credits":               (_as_str, "", "Who prepared each list of hymns (reading_hymns), as source=who, separated by | (page only)"),
    "reading_propers":            (_as_str, "", "readings: the kinds that are parts of the service, sung or said, rather than readings (LCMS: introit gradual verse): listed apart after each set's readings, and left out of the links that open its readings together (page and lectionary.py)"),
    "latin_names":                (_as_bool, False, "LCMS one-year series: append the Sunday's Latin name to its title (read by new_year.py)"),
    "deduplicate_day_labels":       (_as_bool, True, "Drop a commemoration whose name repeats the day's own title"),
    "feast_yield_seasons":          (_as_keys, DEFAULT_FEAST_YIELD, "Seasons whose Sundays and named days outrank a feast: the day keeps the top of the cell and the feast's color takes the lower half ('none' turns this off)"),
    "feast_yield_every_day":        (_as_keys, DEFAULT_FEAST_EVERY_DAY, "Seasons in which every day, and every day of the week after (Easter week), outranks a feast in the same way ('none' turns this off)"),
    "feast_repeat":                 (_as_str, "all", "When a 53-week year contains a MM-DD date twice, place it: all / first / last"),
    "png_output":                   (_as_bool, True, "Also write a PNG beside the SVG"),
    "png_filename":                 (_as_str, "", "PNG file to write, in the SVG's folder unless the path is absolute; blank = the SVG's name with a .png suffix"),
    "png_width":                    (int, 5000, "PNG width in pixels; height follows the canvas aspect"),
    "png_background":               (_as_str, "none", "PNG background; 'none' for transparency"),
    "png_renderer":                 (_as_str, "auto", "Which rasterizer to use: auto, cairosvg, rsvg-convert, inkscape, resvg or chrome"),

    # --- canvas -------------------------------------------------------------
    "width":                        (int, 2100, "Canvas width in user units"),
    "height":                       (int, 2100, "Canvas height in user units"),
    "background_fill":              (_as_str, "none", "Canvas background fill"),
    "start_angle":                  (float, 180.0, "Angle (deg) where the first week begins; 180 = 9 o'clock"),

    # --- week ring ----------------------------------------------------------
    "day_bands":                    (int, 7, "Rows per weekly wedge (7 = Sun..Sat)"),
    "week_starts_on":               (int, 6, "Python weekday that starts a week (6 = Sunday)"),
    "day_stroke":                   (_as_str, "#000000", "Outline color of day cells"),
    "day_stroke_width":             (float, 0.4, "Outline width of day cells"),
    "empty_cell_fill":              (_as_str, "#f0f0f0", "Fill for padding cells at the end of the year"),
    "empty_cell_stroke":            (_as_str, "#c0c0c0", "Outline for padding cells"),
    "year_line":                    (_as_bool, False, "Draw the line where the year ends and begins (between its last week and its first) wider, to show that the weeks on either side are a year apart"),
    "year_line_width":              (float, 4.0, "Width of that line when year_line is on"),
    "year_seam_fill":               (_as_str, "auto", "Fill for the rings over the padding cells where a year starts or ends partway through a week (the Orthodox 1 September): auto (empty_cell_fill), a color, or none to leave the gap"),
    "icon_size":                    (float, 9.0, "Height of a day's icons (holy day of obligation, fasting), in user units"),
    "icon_gap":                     (float, 1.5, "Space between two icons, and between the icons and the text above them"),

    # --- fonts --------------------------------------------------------------
    "font_family_serif":            (_as_str, "Times New Roman, Liberation Serif, Nimbus Roman, Times, serif", "Font stack used wherever a style says 'serif'"),
    "font_family_sans":             (_as_str, "Arial, Liberation Sans, Nimbus Sans, Helvetica, sans-serif", "Font stack used wherever a style says 'sans-serif'"),
    "line_height_factor":           (float, 1.0, "Line spacing as a multiple of font size"),
    "text_width_fudge":             (float, 1.0, "Global width correction if your fonts run wide/narrow"),
    "small_caps_ratio":             (float, 0.8, "Size of small-caps lowercase relative to caps"),
    "small_caps_synthetic":         (_as_bool, True, "Draw small caps as real caps at two sizes instead of relying on font-variant (renderers often ignore font-variant)"),

    # --- day cell layout ----------------------------------------------------
    "day_number_vertical_ratio":    (float, 0.18, "Day number position from the outer edge, as a share of band height"),
    "day_number_horizontal_ratio":  (float, 0.05, "Day number position from the leading edge, as a share of wedge span"),
    "cell_padding":                 (float, 1.5, "Blank margin inside each day cell, in user units"),
    "text_fill_ratio":              (float, 0.94, "Share of the available width a line of text may use"),
    "radial_clearance":             (float, 0.74, "Share of cell width usable by radial text (keeps clear of the day number)"),
    "day_number_gap":               (float, 2.5, "Clear space kept between the day number and any label beside it"),
    "top_label_reserve":            (float, 0.34, "Most of the band a cell's month/year label may take"),
    "color_split_max":              (float, 0.70, "Most of a cell the upper color may take when a commemoration recolors the foot"),
    "color_split_gain":             (float, 0.15, "How much better the worse-off label must do before that break moves off center"),
    "split_share_min":              (float, 0.34, "Smallest share of a cell given to one of two stacked labels"),
    "split_share_max":              (float, 0.66, "Largest share of a cell given to one of two stacked labels"),

    # --- auto-fit -----------------------------------------------------------
    "autofit":                      (_as_bool, True, "Shrink/wrap/rotate text automatically to fit its cell"),
    "autofit_allow_grow":           (_as_bool, False, "Let text grow past the style's font_size when there is room"),
    "autofit_max_scale":            (float, 1.0, "Ceiling on growth, as a multiple of the style font_size"),
    "autofit_step":                 (float, 0.25, "Font-size granularity used while fitting"),
    "text_orientation":             (_as_str, "tangential", "Day-cell text direction: tangential | radial | auto"),
    "radial_min_line_saving":       (int, 2, "Lines a label must save before it is turned radial (0 = turn it whenever radial wraps better)"),

    # --- ring labels --------------------------------------------------------
    "curved_text_vertical_offset":  (float, -0.35, "Curved ring labels shift, as a multiple of font size"),
    "ring_label_arc_usage":         (float, 0.95, "Share of a ring segment's arc a curved label may use"),
    "ring_label_autofit":           (_as_bool, True, "Shrink ring labels that do not fit their arc"),
    "ring_label_radial_fallback":   (_as_bool, True, "Turn a ring label across the ring when the arc is too short"),
    "ring_label_min_font_size":     (float, 6.0, "Never shrink a ring label below this"),
    "ring_label_hide_if_unfit":     (_as_bool, False, "Drop a ring label that still does not fit instead of overflowing"),
    "ring_label_uniform":           (_as_str, "seasons", "Rings (rings.csv keys) whose labels all take one size: the largest at which every one fits, spilling past short arcs"),
    "ring_label_spill":             (_as_bool, True, "Let a short segment's label run past its arc into free ring on either side, rather than shrink"),
    "month_label_largest_only":     (_as_bool, True, "Label only the longest run of each month (avoids duplicates at the year seam)"),

    # --- reporting ----------------------------------------------------------
    "warn_below_font_size":         (float, 6.0, "Report labels that had to shrink below this size"),
}


class Settings:
    """Typed access to config.csv with documented defaults."""

    def __init__(self, raw: dict[str, str]) -> None:
        self._raw = raw
        self._values: dict[str, Any] = {}
        unknown = sorted(set(raw) - set(SETTING_SPEC))
        for name in unknown:
            import difflib
            near = difflib.get_close_matches(name, list(SETTING_SPEC), n=1)
            hint = f" (did you mean '{near[0]}'?)" if near else ""
            print(f"  ! config.csv: unknown setting '{name}' ignored{hint}", file=sys.stderr)
        for name, (parser, default, _doc) in SETTING_SPEC.items():
            text = raw.get(name, "")
            if text is None or str(text).strip() == "":
                self._values[name] = default
                continue
            try:
                self._values[name] = parser(text)
            except Exception as exc:
                print(f"  ! config.csv: bad value for '{name}' ({text!r}): {exc}; "
                      f"using default {default!r}", file=sys.stderr)
                self._values[name] = default

        self._resolve_calendar()
        self._resolve_feasts()

    def _resolve_feasts(self) -> None:
        wanted = str(self._values.get("feast_detail", "all")).strip().lower()
        if wanted not in FEAST_DETAIL:
            print(f"  ! config.csv: feast_detail '{wanted}' is not one of "
                  f"{', '.join(FEAST_DETAIL)}; using all", file=sys.stderr)
            wanted = "all"
        self._values["feast_detail"] = wanted

    def _resolve_calendar(self) -> None:
        """Settle which calendar the dates are in, now that they are all read."""
        wanted = str(self._values.get("calendar", "gregorian")).strip().lower()
        reckoning = RECKONINGS.get(wanted)
        if reckoning is None:
            print(f"  ! config.csv: calendar '{wanted}' is not one of "
                  f"{', '.join(RECKONINGS)}; using gregorian", file=sys.stderr)
            reckoning = GREGORIAN
        self._values["reckoning"] = reckoning

        rule = str(self._values.get("paschalion", "")).strip().lower()
        # Kept as written, so the browser page can tell "follow the calendar"
        # from an explicit choice; everything else uses the resolved rule.
        self._values["paschalion_as_written"] = rule if rule in PASCHALIONS else ""
        if not rule:
            # A Julian calendar with a Gregorian Easter is nobody's practice, so
            # the paschalion follows the calendar unless it is set outright.
            rule = "gregorian" if reckoning is GREGORIAN else "julian"
        if rule not in PASCHALIONS:
            print(f"  ! config.csv: paschalion '{rule}' is not one of "
                  f"{', '.join(PASCHALIONS)}; using gregorian", file=sys.stderr)
            rule = "gregorian"
        self._values["paschalion"] = rule
        self._values["easter_of"] = PASCHALIONS[rule]

        for key in ("church_year_start", "church_year_end"):
            text = self._values.get(key)
            if isinstance(text, str):
                try:
                    self._values[key] = CivilDate.parse(reckoning, text)
                except Exception as exc:
                    sys.exit(f"\u2717 config.csv: {key} '{text}' is not a date "
                             f"in the {reckoning.label} calendar ({exc})")

    def __getattr__(self, name: str) -> Any:
        try:
            return self._values[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    @property
    def cx(self) -> float:
        return self._values["width"] / 2.0

    @property
    def cy(self) -> float:
        return self._values["height"] / 2.0


# ============================================================================
# DATA MODEL
# ============================================================================

@dataclass(frozen=True)
class LiturgicalColor:
    """A liturgical color: what the cell is filled with, and what text on it looks like.
    `alt` holds the other colors a source allows ("violet; gold"), for the page's readout."""
    name: str
    fill: str
    text: str
    alt: str = ""


@dataclass(frozen=True)
class TextStyle:
    """A named text appearance, loaded from text_styles.csv."""
    name: str
    font_family: str = "serif"
    font_size: float = 10.0
    font_weight: str = "normal"
    font_style: str = "normal"
    font_variant: str = "normal"
    min_font_size: float = 5.0
    max_lines: int = 6
    orientation: str = "auto"       # auto | tangential | radial
    fill: str = ""                  # blank = use the cell's text color

    @property
    def metric_family(self) -> str:
        """The role used to choose a metric table — never the rendered stack.

        `font_family` here is what text_styles.csv says: usually the role
        'serif' or 'sans-serif'.  config.csv turns that into a real font stack
        for the SVG, but measurement must key off the role, or naming a
        concrete face like 'Arial' would silently measure it as a serif.
        """
        return self.font_family

    def resolved_family(self, settings: "Settings") -> str:
        key = self.font_family.strip().lower()
        if key in ("serif", "font_family_serif"):
            return settings.font_family_serif
        if key in ("sans", "sans-serif", "font_family_sans"):
            return settings.font_family_sans
        return self.font_family


@dataclass(frozen=True)
class SeasonPeriod:
    """A stretch of the year that colors its days, labels the ring, or both.

    The two do not always want the same boundaries.  The one-year series names
    Pentecost from the Ascension onward, while the days themselves stay white
    until Pentecost has actually come -- so a row with no `season` labels the
    ring and colors nothing, and a row with no `name` colors its days and puts
    nothing on the ring.
    """
    name: str
    start_date: date
    end_date: date
    season: str
    color: Optional[LiturgicalColor] = None


@dataclass
class RingLabel:
    """One ring label, sized but not yet drawn, so a ring can settle them all."""
    text: str
    subtitle: str
    style: "TextStyle"
    angle_start: float
    angle_end: float
    size: float
    width: Any            # width(at_size) -> user units, name and subtitle together
    metric: str
    full: float = 0.0     # the size it would have with room enough
    spill: bool = False   # runs past its own arc into free ring beside it
    center: float = 0.0   # where a spilled label is centered
    hidden: bool = False  # a sliver left unlabeled


@dataclass(frozen=True)
class BroadSeason:
    name: str
    start_date: date
    end_date: date
    subtitle: str = ""      # set in italics after the name, when there is one
    scale: float = 1.0      # this label's size against the ring's own
    scale_is_subtitle: bool = False   # or: the size a subtitle would be drawn at


@dataclass(frozen=True)
class DayEntry:
    """One label on one day, from sundays_seasons.csv or the feasts CSV."""
    text: str
    color_override: Optional[LiturgicalColor] = None
    color_override_bottom: Optional[LiturgicalColor] = None
    font_size_override: Optional[float] = None
    max_chars_override: Optional[int] = None
    vertical_offset: float = 0.0
    style_override: str = ""
    icon: str = ""                  # icon keys from icons.csv, space separated
    full_name: str = ""             # the whole name, for readouts; the cell uses `text`


@dataclass(frozen=True)
class Ring:
    """One concentric ring, from rings.csv.  `order` is also the drawing order."""
    order: int
    key: str
    kind: str                    # center | days | segments | months | band
    r_inner: float
    r_outer: float
    fill: str = "none"
    stroke: str = "none"
    stroke_width: float = 0.0
    source: str = ""             # segments/months: which dataset supplies the labels
    font_size: float = 18.0
    font_family: str = "sans-serif"
    font_weight: str = "bold"
    text_color: str = "#000000"
    label_mode: str = "auto"     # curve | radial | auto | none
    inner_border_color: str = ""
    inner_border_width: float = 0.0
    enabled: bool = True

    @property
    def r_mid(self) -> float:
        return (self.r_inner + self.r_outer) / 2.0

    @property
    def thickness(self) -> float:
        return self.r_outer - self.r_inner


# ============================================================================
# CSV LOADING
# ============================================================================

def _cell(row: dict, key: str) -> str:
    value = row.get(key)
    return value.strip() if isinstance(value, str) else ""


def _opt_float(row: dict, key: str) -> Optional[float]:
    text = _cell(row, key)
    return float(text) if text else None


def _opt_int(row: dict, key: str) -> Optional[int]:
    text = _cell(row, key)
    return int(text) if text else None


def _float_or(row: dict, key: str, default: float) -> float:
    value = _opt_float(row, key)
    return default if value is None else value


def _str_or(row: dict, key: str, default: str) -> str:
    return _cell(row, key) or default


def read_rows(path: Path, required: bool = True) -> list[dict]:
    """Read a CSV into a list of dicts.  Blank rows and #comment rows are skipped."""
    if not path.exists():
        if required:
            sys.exit(f"✗ Required file not found: {path}")
        return []
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            rows = []
            for row in csv.DictReader(handle):
                if row is None:
                    continue
                first = next(iter(row.values()), "") or ""
                if first.strip().startswith("#"):
                    continue
                if not any((v or "").strip() for v in row.values()):
                    continue
                rows.append(row)
            return rows
    except Exception as exc:
        sys.exit(f"✗ Error reading {path}: {exc}")


def read_config(path: Path) -> dict[str, str]:
    raw = {}
    for row in read_rows(path):
        name = _cell(row, "setting")
        if name:
            raw[name] = (row.get("value") or "") if name in _KEEP_SPACES else _cell(row, "value")
    return raw


def load_settings(path: Path, overlay: Optional[dict[str, str]] = None,
                  overrides: Optional[dict[str, str]] = None) -> Settings:
    """config.csv, with the tradition's own settings laid over it.

    A tradition's tradition.csv may carry settings of its own that the drawing
    does not read (its year_start, say); only the ones config.csv could also
    hold are laid over it here.  `overrides` (the command line's --art,
    --mid-text ...) go over both, without config.csv being written.
    """
    raw = read_config(path)
    for name, value in (overlay or {}).items():
        if name in SETTING_SPEC:
            raw[name] = value
    for name, value in (overrides or {}).items():
        raw[name] = value
    missing = [k for k in ("church_year_start", "church_year_end") if not raw.get(k)]
    if missing:
        sys.exit(f"✗ config.csv is missing: {', '.join(missing)}")
    return Settings(raw)


def _luminance(color: str) -> float:
    """WCAG relative luminance of a #rrggbb color."""
    h = color.strip().lstrip("#")
    if len(h) != 6:
        return 1.0
    out = 0.0
    for weight, i in ((0.2126, 0), (0.7152, 2), (0.0722, 4)):
        c = int(h[i:i + 2], 16) / 255.0
        c = c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        out += weight * c
    return out


def is_mid_tone(fill: str) -> bool:
    """A fill on which black and white text both reach 3:1, so either reads."""
    lum = _luminance(fill)
    return (lum + 0.05) / 0.05 >= 3.0 and 1.05 / (lum + 0.05) >= 3.0


def is_red(fill: str) -> bool:
    """A strong red: hue within 20 degrees of red, and well saturated."""
    h = fill.strip().lstrip("#")
    if len(h) != 6:
        return False
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    hi, lo = max(r, g, b), min(r, g, b)
    if hi == 0 or (hi - lo) / hi < 0.5 or r != hi:
        return False
    hue = 60.0 * (g - b) / (hi - lo)               # -60..60 when red is highest
    return -20.0 <= hue <= 20.0


def with_mid_text(colors: dict[str, LiturgicalColor], rule: str) -> dict[str, LiturgicalColor]:
    """Colors with the text on mid-tone fills set by mid_text: dark, light, or
    dark-reds (black on the mid-tone reds only)."""
    rule = (rule or "as-set").strip().lower()
    if rule not in ("dark", "light", "dark-reds"):
        return colors
    text = "#ffffff" if rule == "light" else "#000000"
    def wanted(c: LiturgicalColor) -> bool:
        return is_mid_tone(c.fill) and (rule != "dark-reds" or is_red(c.fill))
    return {k: (LiturgicalColor(c.name, c.fill, text) if wanted(c) else c)
            for k, c in colors.items()}


def _contrast(a: str, b: str) -> float:
    """The contrast ratio of two #rrggbb colors."""
    x, y = _luminance(a), _luminance(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)


def readable_text(fill: str) -> str:
    """Black or white, whichever reads better on a fill."""
    lum = _luminance(fill)
    return "#000000" if (lum + 0.05) / 0.05 >= 1.05 / (lum + 0.05) else "#ffffff"


def with_overrides(colors: dict[str, LiturgicalColor],
                   fills: dict[str, str]) -> dict[str, LiturgicalColor]:
    """Colors with some fills replaced (--color-changes; church_year.js:
    withOverrides).  The text keeps its color while it still reads (4.5:1);
    otherwise it turns black or white, whichever reads better."""
    out = dict(colors)
    # A fill may be stripes (#ffffff/#bfbfbf, a day with no color appointed);
    # NAME.TEXT is the color of a day's words, which then stays as chosen.
    for name, fill in fills.items():
        c = out.get(name)
        if c is None or name.endswith(".TEXT"):
            continue
        parts = fill.split("/")
        text = c.text if all(_contrast(p, c.text) >= 4.5 for p in parts) else readable_text(parts[0])
        out[name] = replace(c, fill=fill.lower(), text=text)
    for name, text in fills.items():
        if name.endswith(".TEXT") and name[:-5] in out:
            out[name[:-5]] = replace(out[name[:-5]], text=text.lower())
    return out


@dataclass(frozen=True)
class ColorChanges:
    """Colors changed for one drawing, as the page's Colors menu changes them
    and a link's colors= writes them (--color-changes)."""
    days: dict            # color name -> #rrggbb, for the church being drawn
    rings: dict           # ring key -> fill
    ring_text: dict       # ring key -> text color
    empty: str = ""       # the cells outside the year


def _hex6(value: str) -> str:
    v = value.strip().lower()
    if re.fullmatch(r"[0-9a-f]{3}", v):
        v = "".join(ch * 2 for ch in v)
    return "#" + v if re.fullmatch(r"[0-9a-f]{6}", v) else ""


def parse_color_changes(spec: str, church: str = "", family: str = "") -> ColorChanges:
    """--color-changes for one church: PURPLE-7a1f7a (every church),
    lutheran:WHITE-fffff0 (a tradition's, which wins), lutheran:wels-one-year:RED-c00000
    (a church's, which wins again), ring.halves-e6c3f7, text.halves-000000,
    empty-f0f0f0; a day's fill may be stripes (NONE-ffffff/bfbfbf), and
    PURPLE.text-ffffff (with the same tradition: and church: prefixes) is
    the color of its words.  `church` is the key being drawn and `family` its tradition
    (traditions.csv); changes for other churches are passed over, as the page
    does.  Raises ValueError for an item that is not NAME-rrggbb."""
    def trad_slug(name: str) -> str:
        return re.sub(r"\s+", "-", (name or "").strip().lower())
    every: dict = {}
    by_tradition: dict = {}
    by_church: dict = {}
    rings: dict = {}
    ring_text: dict = {}
    empty = ""
    for item in (w.strip() for w in (spec or "").split(",")):
        if not item or item.lower() == "none":
            continue
        key, _, raw = item.rpartition("-")
        # Stripes (NONE-ffffff/bfbfbf) for a day's fill.
        parts = [_hex6(p) for p in raw.split("/")]
        value = "/".join(parts) if all(parts) and (len(parts) == 1 or "." not in key and key != "empty") else ""
        if not key or not value:
            raise ValueError(f"'{item}' is not NAME-rrggbb (PURPLE-7a1f7a, lutheran:WHITE-fffff0, "
                             "ring.halves-e6c3f7, text.halves-000000, empty-f0f0f0)")
        if key == "empty":
            empty = value
        elif key.startswith("ring."):
            rings[key[5:]] = value
        elif key.startswith("text."):
            ring_text[key[5:]] = value
        elif ":" in key:
            parts = key.split(":")
            if trad_slug(parts[0]) != trad_slug(family):
                continue
            if len(parts) == 3:
                if parts[1].strip().lower() == church.lower():
                    by_church[parts[2].strip().upper()] = value
            else:
                by_tradition[parts[1].strip().upper()] = value
        else:
            every[key.strip().upper()] = value
    return ColorChanges({**every, **by_tradition, **by_church}, rings, ring_text, empty)


def load_colors(path: Path, *more: Path) -> dict[str, LiturgicalColor]:
    """The palette, and any further files laid over it (a tradition's own colors)."""
    colors: dict[str, LiturgicalColor] = {}
    for row in read_rows(path) + [r for extra in more for r in read_rows(extra, required=False)]:
        name = _cell(row, "name").upper()
        if not name:
            continue
        colors[name] = LiturgicalColor(
            name=name,
            fill=_str_or(row, "fill", "#ffffff"),
            text=_str_or(row, "text", "#000000"),
        )
    if not colors:
        sys.exit("✗ colors.csv defined no colors")
    return colors


def make_color_lookup(colors: dict[str, LiturgicalColor], where: str):
    def lookup(name: str) -> Optional[LiturgicalColor]:
        # "PURPLE; blue": the first color is drawn; the others a source allows
        # are only named (the page's readout says "purple (or blue)").  Not "|",
        # which picks a run's value by its number in days.csv.
        first, _, rest = (name or "").partition(";")
        key = first.strip().upper()
        if not key:
            return None
        if key not in colors:
            print(f"  ! {where}: unknown color '{first.strip()}' (see colors.csv)", file=sys.stderr)
            return None
        alt = "; ".join(a.strip() for a in rest.split(";") if a.strip())
        return replace(colors[key], alt=alt) if alt else colors[key]
    return lookup


def load_season_colors(path: Path, colors: dict[str, LiturgicalColor]) -> dict[str, LiturgicalColor]:
    lookup = make_color_lookup(colors, "seasons.csv")
    mapping: dict[str, LiturgicalColor] = {}
    for row in read_rows(path):
        name = _cell(row, "season").upper()
        color = lookup(_cell(row, "color"))
        if name and color:
            mapping[name] = color
    return mapping


def load_month_names(path: Path) -> dict[int, str]:
    names = {}
    for row in read_rows(path, required=False):
        try:
            names[int(_cell(row, "month"))] = _cell(row, "name")
        except ValueError:
            continue
    if not names:
        names = {i: n for i, n in enumerate(
            ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"], start=1)}
    return names


ENGLISH_MONTH_DAY = "{month} {day}"
ENGLISH_FULL_DATE = "{month} {day},|{year}"


@dataclass
class Language:
    """A church's language, as the wheel writes dates in it (data/languages/<code>.csv;
    English from month_names.csv): the month ring's names, the names in a
    date, and the patterns for a day ({day} {month}) and for the year's first
    day, whose | marks where it may break onto a second line."""
    code: str
    months: dict[int, str]
    date_months: dict[int, str]
    month_day: str = ENGLISH_MONTH_DAY
    full_date: str = ENGLISH_FULL_DATE
    chapter_verse: str = ":"
    books: dict[str, str] = field(default_factory=dict)
    colors: dict[str, str] = field(default_factory=dict)   # "purple" -> "morado" (the page's header)
    or_word: str = "or"
    readings: dict[str, str] = field(default_factory=dict)  # "Gospel" -> "Evangelio" (the page's readings)
    name: str = "English"                                    # the language in its own words ("Español")

    def day_text(self, month: int, day: int) -> str:
        """church_year.js: Language.dayText."""
        return (self.month_day.replace("{month}", self.date_months.get(month, str(month)))
                .replace("{day}", str(day)))

    def full_text(self, month: int, day: int, year: str) -> str:
        """church_year.js: Language.fullText.  Keeps the | break mark."""
        return (self.full_date.replace("{month}", self.date_months.get(month, str(month)))
                .replace("{day}", str(day)).replace("{year}", year))


def load_language(data_dir: Path, code: str) -> Language:
    """data/languages/<code>.csv, what it leaves out in English (church_year.js: languageOf)."""
    english = load_month_names(data_dir / "month_names.csv")
    code = (code or "en").strip().lower() or "en"
    values = {}
    if code != "en":
        path = data_dir / "languages" / f"{code}.csv"
        if not path.exists():
            print(f"  ! language '{code}': no {path}; the wheel writes dates in English", file=sys.stderr)
        for row in read_rows(path, required=False):
            key = _cell(row, "key")
            if key:
                values[key] = _cell(row, "value")

    def twelve(key: str, fallback: dict[int, str]) -> dict[int, str]:
        names = [n.strip() for n in values.get(key, "").split("|")]
        return {i + 1: n for i, n in enumerate(names)} if len(names) == 12 and all(names) else dict(fallback)
    months = twelve("months", english)
    return Language(
        code=code, months=months, date_months=twelve("date_months", months),
        month_day=values.get("month_day") or ENGLISH_MONTH_DAY,
        full_date=values.get("full_date") or ENGLISH_FULL_DATE,
        chapter_verse=values.get("chapter_verse") or ":",
        books={k: v for k, v in values.items() if re.fullmatch(r"[1-4]?[A-Z]{2,3}", k) and v},
        colors={k[6:].replace("_", " "): v for k, v in values.items() if k.startswith("color_") and v},
        or_word=values.get("or") or "or",
        readings={k[8:]: v for k, v in values.items() if k.startswith("reading_") and v},
        name=values.get("name") or "English")


def load_text_styles(path: Path, *more: Path) -> dict[str, TextStyle]:
    styles: dict[str, TextStyle] = {}
    for row in read_rows(path) + [r for extra in more for r in read_rows(extra, required=False)]:
        name = _cell(row, "style")
        if not name:
            continue
        styles[name] = TextStyle(
            name=name,
            font_family=_str_or(row, "font_family", "serif"),
            font_size=_float_or(row, "font_size", 10.0),
            font_weight=_str_or(row, "font_weight", "normal"),
            font_style=_str_or(row, "font_style", "normal"),
            font_variant=_str_or(row, "font_variant", "normal"),
            min_font_size=_float_or(row, "min_font_size", 5.0),
            max_lines=int(_float_or(row, "max_lines", 6)),
            orientation=_str_or(row, "orientation", "auto"),
            fill=_cell(row, "fill"),
        )
    for required in ("day_number", "month_day_label", "first_day_label",
                     "sunday_title", "weekday_title", "feast"):
        if required not in styles:
            sys.exit(f"✗ text_styles.csv is missing the '{required}' style")
    return styles


def load_rings(path: Path) -> list[Ring]:
    rings = []
    for row in read_rows(path):
        key = _cell(row, "key")
        if not key:
            continue
        enabled = _cell(row, "enabled")
        rings.append(Ring(
            order=int(_float_or(row, "order", len(rings) + 1)),
            key=key,
            kind=_str_or(row, "kind", "band").lower(),
            r_inner=_float_or(row, "r_inner", 0.0),
            r_outer=_float_or(row, "r_outer", 0.0),
            fill=_str_or(row, "fill", "none"),
            stroke=_str_or(row, "stroke", "none"),
            stroke_width=_float_or(row, "stroke_width", 0.0),
            source=_cell(row, "source"),
            font_size=_float_or(row, "font_size", 18.0),
            font_family=_str_or(row, "font_family", "sans-serif"),
            font_weight=_str_or(row, "font_weight", "bold"),
            text_color=_str_or(row, "text_color", "#000000"),
            label_mode=_str_or(row, "label_mode", "auto").lower(),
            inner_border_color=_cell(row, "inner_border_color"),
            inner_border_width=_float_or(row, "inner_border_width", 0.0),
            enabled=_as_bool(enabled) if enabled else True,
        ))
    rings.sort(key=lambda r: r.order)
    if not any(r.kind == "days" and r.enabled for r in rings):
        sys.exit("✗ rings.csv needs a row with kind=days (the week ring)")
    return rings


def close_ring_gaps(rings: list[Ring]) -> list[Ring]:
    """Pull the remaining rings together over the space a disabled one leaves.

    A ring switched off would otherwise leave a blank annulus where it used to
    be.  Everything outside the gap slides inward to close it, and the bands
    are then stretched back out to fill the room, so turning a ring off gives
    its space to the rings that are left rather than shrinking the drawing.

    Two kinds of ring are held at their own size rather than stretched, because
    stretching them would read as the thing itself having changed:

    * the artwork in the middle, which is a drawing rather than a band — grow
      it and the picture looks bigger, and the ring that used to touch it
      stands off at a distance;
    * a plain ``band``, which is usually a border — grow it and the wheel looks
      to have gained a much heavier rim, which is what dropping both the halves
      and the seasons used to do to the gold one.

    So the rings that move are the ones between those fixed pieces, and each
    such stretch is closed and stretched on its own.  A band that is itself
    switched off stops being fixed, and its room is then shared out like any
    other gap — which is what lets the wheel grow into the rim when the rim is
    the thing that was dropped.

    With every ring enabled this changes nothing, which is what keeps the
    ordinary output identical.
    """
    gaps = sorted((r.r_inner, r.r_outer) for r in rings if not r.enabled)
    if not gaps:
        return rings
    edge = max((r.r_outer for r in rings), default=0.0)
    fixed = sorted((r.r_inner, r.r_outer) for r in rings
                   if r.enabled and r.kind in ("center", "band"))

    # What the fixed rings leave between them: the stretches that may move.
    free: list[tuple[float, float]] = []
    lower = 0.0
    for inner, outer in fixed:
        if inner > lower:
            free.append((lower, inner))
        lower = max(lower, outer)
    if lower < edge:
        free.append((lower, edge))

    moves = []
    for lower, upper in free:
        inside = [(max(lower, a), min(upper, b)) for a, b in gaps
                  if min(upper, b) > max(lower, a)]
        lost = _plain_sum(b - a for a, b in inside)
        if not inside or upper - lower <= lost:
            continue
        moves.append((lower, upper, (upper - lower) / (upper - lower - lost), inside))
    if not moves:
        return rings

    def pulled(radius: float) -> float:
        for lower, upper, factor, inside in moves:
            if lower <= radius <= upper:
                below = _plain_sum(min(radius, b) - a for a, b in inside if radius > a)
                return lower + (radius - lower - below) * factor
        return radius

    return [replace(ring, r_inner=pulled(ring.r_inner),
                    r_outer=pulled(ring.r_outer))
            for ring in rings if ring.enabled]


def load_season_periods(path: Path, colors: dict[str, LiturgicalColor],
                        season_colors: dict[str, LiturgicalColor],
                        reckoning=GREGORIAN) -> list[SeasonPeriod]:
    lookup = make_color_lookup(colors, "season_periods.csv")
    _as_date = lambda text: CivilDate.parse(reckoning, text)
    periods = []
    for row in read_rows(path):
        season = _cell(row, "season").upper()
        color = lookup(_cell(row, "color")) or season_colors.get(season)
        # No season at all means the row is there to label the ring, not to
        # color anything, so there is nothing missing to complain about.
        if color is None and season:
            print(f"  ! season_periods.csv: no color for season '{season}'; "
                  f"add it to seasons.csv", file=sys.stderr)
        periods.append(SeasonPeriod(
            name=_cell(row, "name"),
            start_date=_as_date(_cell(row, "start_date")),
            end_date=_as_date(_cell(row, "end_date")),
            season=season,
            color=color,
        ))
    return periods


def load_season_art(path: Path) -> list[tuple[str, str, str, int]]:
    """season_art.csv: which picture a season shows when the middle follows the
    season (--art-date, the page's "By season"), as (season, art, church, week)
    rows.

    `season` is a season's name as the wheel gives it ("Advent") or its word in
    season_periods.csv ("ADVENT"); `church` is one church's key, or blank for
    every church; `week` is the week of the season the picture comes in with
    (1 is its first seven days), or blank for the whole season.  A row with no
    `art` leaves the church's own picture."""
    out = []
    for row in read_rows(path, required=False):
        if not _cell(row, "season"):
            continue
        week = _cell(row, "week")
        out.append((_cell(row, "season"), _cell(row, "art").lower(), _cell(row, "church").lower(),
                    int(week) if week.isdigit() else 0))
    return out


def season_art(rows: list[tuple[str, str, str, int]], known: set, church: str,
               name: str, word: str, week: int = 1) -> str:
    """The picture a season shows in a week of it, or '' for the church's own
    (church_year.js: seasonArt).  A church's own rows win, by name and then by
    word; then every church's, by word and then by name.  Of the rows found,
    the one for the latest week that has come: four rows for Advent's weeks 1
    to 4 light a candle a week, and the fourth stays for any days after.
    `known`: the artwork.csv keys there are."""
    def find(who: str, what: str):
        if not what:
            return None
        found = [r for r in rows if r[2] == who and r[0] == what and r[3] <= week]
        return max(found, key=lambda r: r[3]) if found else None
    row = find(church, name) or find(church, word) or find("", word) or find("", name)
    return row[1] if row and row[1] in known else ""


def load_broad_seasons(path: Path, reckoning=GREGORIAN) -> list[BroadSeason]:
    _as_date = lambda text: CivilDate.parse(reckoning, text)

    def _scale(row: dict) -> tuple[float, bool]:
        """A number, or the word "subtitle" for whatever size subtitles are.

        Naming it rather than repeating 0.78 keeps a nested label in step with
        the subtitles beside it when ring_subtitle_ratio is changed.
        """
        text = _cell(row, "scale").strip()
        if text.lower() == "subtitle":
            return 1.0, True
        try:
            return (float(text) if text else 1.0), False
        except ValueError:
            return 1.0, False

    rows = []
    for row in read_rows(path):
        scale, as_subtitle = _scale(row)
        rows.append(BroadSeason(
            name=_cell(row, "name"),
            start_date=_as_date(_cell(row, "start_date")),
            end_date=_as_date(_cell(row, "end_date")),
            subtitle=_cell(row, "subtitle"),
            scale=scale,
            scale_is_subtitle=as_subtitle,
        ))
    return rows


def _entry_from_row(row: dict, text: str, lookup) -> DayEntry:
    return DayEntry(
        text=text,
        color_override=lookup(_cell(row, "color_override")),
        color_override_bottom=lookup(_cell(row, "color_override_bottom")),
        font_size_override=_opt_float(row, "font_size_override"),
        max_chars_override=_opt_int(row, "max_chars_override"),
        vertical_offset=_float_or(row, "vertical_offset", 0.0),
        style_override=_cell(row, "style"),
        icon=_cell(row, "icon"),
        full_name=_cell(row, "full_name"),
    )


def _expand_dates(text: str, start: CivilDate, end: CivilDate) -> list[CivilDate]:
    """Accept YYYY-MM-DD, or MM-DD which is placed in whichever year is in range."""
    text = text.strip()
    reckoning = start.reckoning
    parts = text.lstrip("+-").split("-")
    if len(parts) == 3:
        try:
            day = CivilDate.parse(reckoning, text)
        except Exception:
            raise ValueError(f"unrecognized date {text!r}") from None
        return [day] if start <= day <= end else []
    if len(parts) == 2:
        try:
            month, day_of_month = int(parts[0]), int(parts[1])
        except ValueError:
            raise ValueError(f"unrecognized date {text!r}") from None
        # 2000 was a leap year in all three calendars, so this lets 29 February
        # through and stops 30 February or a thirteenth month.
        if not reckoning.valid(2000, month, day_of_month):
            raise ValueError(f"no such day as {text!r}")
        found = []
        for year in range(start.year, end.year + 1):
            # A 29 February that this calendar does not have simply is not there.
            if not reckoning.valid(year, month, day_of_month):
                continue
            candidate = CivilDate.of(reckoning, year, month, day_of_month)
            if start <= candidate <= end:
                found.append(candidate)
        return found
    raise ValueError(f"unrecognized date {text!r}")


def feast_level(row: dict) -> str:
    """principal, festival or all: the least a Feasts setting must allow to show it.

    The dated year file says so in its `level` column (new_year.py fills it
    in); a row left blank there is shown only when everything is.
    """
    level = _cell(row, "level").lower()
    return level if level in ("principal", "festival") else "all"


def feast_shown(row: dict, detail: str) -> bool:
    if detail == "none":
        return False
    level = feast_level(row)
    if detail == "principal":
        return level == "principal"
    if detail == "festivals":
        return level in ("principal", "festival")
    return True


def load_icon_defs(path: Path) -> dict[str, dict]:
    """icons.csv: each icon's name, what it means, and its outline in a 100 x 100 box."""
    defs = {}
    for row in read_rows(path, required=False):
        key = _cell(row, "key")
        if key and _cell(row, "path"):
            defs[key] = {"key": key, "label": _cell(row, "label"), "path": _cell(row, "path")}
    return defs


def load_icons(paths: Iterable[Path], start: CivilDate, end: CivilDate,
               detail: str = "all") -> dict[CivilDate, list[str]]:
    """Every icon a day carries, from its principal rows and its feasts, in order.

    A principal row may carry nothing but an icon (the Fridays of Lent), and a
    feast's icon goes with it when the Feasts setting leaves the feast out.
    """
    icons: dict[CivilDate, list[str]] = {}
    for index, path in enumerate(paths):
        for row in read_rows(path, required=False):
            keys = _cell(row, "icon").split()
            if not keys or not _cell(row, "date"):
                continue
            if index > 0 and detail != "all" and not feast_shown(row, detail):
                continue
            try:
                days = _expand_dates(_cell(row, "date"), start, end)
            except ValueError:
                continue
            for day in days:
                have = icons.setdefault(day, [])
                for key in keys:
                    if key not in have:
                        have.append(key)
    return icons


def load_day_entries(path: Path, colors: dict[str, LiturgicalColor],
                     start: date, end: date, text_column: str,
                     required: bool = True,
                     repeat: str = "all",
                     detail: str = "all") -> dict[date, list[DayEntry]]:
    """Load a dated-label CSV.  Several rows may share a date; all are kept.

    A church year is 364 days most years but 371 in some (2027-28, 2033-34),
    and in those a MM-DD row near the seam falls inside the range twice — St.
    Andrew on 30 November at both ends, say.  `repeat` decides what to do.
    """
    lookup = make_color_lookup(colors, path.name)
    entries: dict[date, list[DayEntry]] = {}
    for row in read_rows(path, required=required):
        text = _cell(row, text_column)
        raw_date = _cell(row, "date")
        if not text or not raw_date:
            continue
        # A row may be left out by how much of the file was asked for.
        if detail != "all" and not feast_shown(row, detail):
            continue
        try:
            days = _expand_dates(raw_date, start, end)
        except ValueError as exc:
            print(f"  ! {path.name}: {exc} ({text}); row skipped", file=sys.stderr)
            continue
        mode = (repeat or "all").strip().lower()
        if len(days) > 1 and mode in ("first", "last"):
            days = days[:1] if mode == "first" else days[-1:]
        for day in days:
            entries.setdefault(day, []).append(_entry_from_row(row, text, lookup))
    return entries


# ============================================================================
# GEOMETRY
# ============================================================================

def polar_to_cartesian(cx: float, cy: float, r: float, angle_deg: float) -> tuple[float, float]:
    """Polar -> Cartesian.  0 deg points right; angles increase clockwise (SVG y is down)."""
    rad = math.radians(angle_deg)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def arc_span(angle_start: float, angle_end: float) -> float:
    """Angular width in degrees, coping with wrap past 360."""
    return (360 - angle_start) + angle_end if angle_end < angle_start else angle_end - angle_start


@dataclass(frozen=True)
class Wedge:
    """The annular sector a label has to live in."""
    r_inner: float
    r_outer: float
    angle_start: float
    angle_end: float

    @property
    def angle_mid(self) -> float:
        return (self.angle_start + self.angle_end) / 2.0

    @property
    def angle_span(self) -> float:
        return arc_span(self.angle_start, self.angle_end)

    @property
    def radial_extent(self) -> float:
        return self.r_outer - self.r_inner

    @property
    def r_mid(self) -> float:
        return (self.r_inner + self.r_outer) / 2.0

    def chord_at(self, r: float) -> float:
        """Width of a straight tangential line at radius r that stays inside the wedge."""
        return max(0.0, 2.0 * r * math.tan(math.radians(self.angle_span) / 2.0))


# ============================================================================
# TEXT FITTING
# ============================================================================

TANGENTIAL = "tangential"
RADIAL = "radial"


@dataclass
class FittedText:
    lines: list[str]
    size: float
    orientation: str
    line_height: float
    r_center: float
    overflow: bool = False

    @property
    def block_thickness(self) -> float:
        """Extent of the block in the direction lines stack."""
        return self.line_height * len(self.lines)


def wrap_to_width(paragraphs: Sequence[str], max_width: float, style: TextStyle,
                  size: float, family: str, measurer: TextMeasurer,
                  max_chars: Optional[int] = None) -> list[str]:
    """Greedy word wrap by rendered width (optionally also capped by character count)."""
    lines: list[str] = []
    for paragraph in paragraphs:
        words = paragraph.split()
        if not words:
            continue
        current: list[str] = []
        for word in words:
            candidate = " ".join(current + [word])
            too_wide = measurer.width(candidate, size, family, style.font_weight,
                                      style.font_style, style.font_variant) > max_width
            too_long = max_chars is not None and len(candidate) > max_chars
            if current and (too_wide or too_long):
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines.append(" ".join(current))
    return lines or [""]


def balance_lines(paragraphs: Sequence[str], max_width: float, style: TextStyle,
                  size: float, family: str, measurer: TextMeasurer,
                  max_chars: Optional[int]) -> list[str]:
    """Wrap into the same number of lines but as evenly as possible.

    Plain greedy wrapping leaves a short last line ("Twenty-first Sunday after /
    Pentecost").  Squeezing the width down as far as it will go without adding a
    line produces a tidier, more centered block.
    """
    baseline = wrap_to_width(paragraphs, max_width, style, size, family, measurer, max_chars)
    target = len(baseline)
    if target <= 1:
        return baseline
    low, high, best = 0.0, max_width, baseline
    for _ in range(12):
        mid = (low + high) / 2.0
        trial = wrap_to_width(paragraphs, mid, style, size, family, measurer, max_chars)
        if len(trial) <= target:
            best, high = trial, mid
        else:
            low = mid
    return best


def _widest(lines: Sequence[str], style: TextStyle, size: float, family: str,
            measurer: TextMeasurer) -> float:
    return max((measurer.width(line, size, family, style.font_weight,
                               style.font_style, style.font_variant)
                for line in lines), default=0.0)


class TextFitter:
    """Chooses font size, wrapping and orientation so a label fits its wedge."""

    def __init__(self, settings: Settings, measurer: TextMeasurer) -> None:
        self.settings = settings
        self.measurer = measurer

    def _candidate_sizes(self, style: TextStyle, pinned: Optional[float]) -> list[float]:
        cfg = self.settings
        if pinned is not None:
            return [pinned]
        top = style.font_size * (cfg.autofit_max_scale if cfg.autofit_allow_grow else 1.0)
        if not cfg.autofit:
            return [top]
        step = max(0.05, cfg.autofit_step)
        floor = min(style.min_font_size, top)
        sizes, value = [], top
        while value >= floor - 1e-9:
            sizes.append(round(value, 3))
            value -= step
        if not sizes or abs(sizes[-1] - floor) > 1e-9:
            sizes.append(round(floor, 3))
        return sizes

    def _try_tangential(self, paragraphs, style, family, size, wedge, r_center,
                        max_chars, width_budget) -> Optional[FittedText]:
        cfg = self.settings
        pad = cfg.cell_padding
        line_height = size * cfg.line_height_factor
        height_budget = wedge.radial_extent - 2 * pad
        if height_budget < line_height:
            return None
        lines, count_guess = [""], 1
        for _ in range(8):
            # The innermost line is the narrowest, so measure there.
            r_ref = r_center - (count_guess - 1) * line_height / 2.0
            available = wedge.chord_at(max(r_ref, 1.0)) * width_budget - 2 * pad
            if available <= 0:
                return None
            lines = balance_lines(paragraphs, available, style, size, family,
                                  self.measurer, max_chars)
            if len(lines) == count_guess:
                break
            count_guess = len(lines)
        if len(lines) > style.max_lines:
            return None
        r_ref = r_center - (len(lines) - 1) * line_height / 2.0
        available = wedge.chord_at(max(r_ref, 1.0)) * width_budget - 2 * pad
        if _widest(lines, style, size, family, self.measurer) > available:
            return None
        if line_height * len(lines) > height_budget:
            return None
        return FittedText(lines, size, TANGENTIAL, line_height, r_center)

    def _try_radial(self, paragraphs, style, family, size, wedge, r_center,
                    max_chars, width_budget) -> Optional[FittedText]:
        cfg = self.settings
        pad = cfg.cell_padding
        line_height = size * cfg.line_height_factor
        available = wedge.radial_extent - 2 * pad
        if available <= 0:
            return None
        lines = balance_lines(paragraphs, available, style, size, family,
                              self.measurer, max_chars)
        if len(lines) > style.max_lines:
            return None
        if _widest(lines, style, size, family, self.measurer) > available:
            return None
        stack_budget = wedge.chord_at(r_center) * width_budget * cfg.radial_clearance - 2 * pad
        if line_height * len(lines) > stack_budget:
            return None
        return FittedText(lines, size, RADIAL, line_height, r_center)

    def fit(self, paragraphs: Sequence[str], style: TextStyle, wedge: Wedge,
            pinned_size: Optional[float] = None, max_chars: Optional[int] = None,
            r_center: Optional[float] = None,
            orientation: Optional[str] = None) -> FittedText:
        """Return the best fit; falls back to the minimum size with overflow flagged."""
        cfg = self.settings
        family = style.metric_family
        center = wedge.r_mid if r_center is None else r_center
        width_budget = cfg.text_fill_ratio

        wanted = (orientation or style.orientation or "auto").lower()
        if cfg.text_orientation.lower() != "auto" and wanted == "auto":
            wanted = cfg.text_orientation.lower()
        allow_tangential = wanted in ("auto", TANGENTIAL)
        allow_radial = wanted in ("auto", RADIAL)

        best: Optional[FittedText] = None
        for size in self._candidate_sizes(style, pinned_size):
            options = []
            if allow_tangential:
                options.append(self._try_tangential(paragraphs, style, family, size,
                                                    wedge, center, max_chars, width_budget))
            if allow_radial:
                options.append(self._try_radial(paragraphs, style, family, size,
                                                wedge, center, max_chars, width_budget))
            found = [o for o in options if o is not None]
            if not found:
                continue
            flat = next((f for f in found if f.orientation == TANGENTIAL), None)
            spoke = next((f for f in found if f.orientation == RADIAL), None)
            if flat is None:
                best = spoke
            elif spoke is None:
                best = flat
            else:
                # Both work at this size.  Turning a label radial only pays off if
                # it saves real wrapping, so keep it flat unless the gain is clear.
                saving = len(flat.lines) - len(spoke.lines)
                best = spoke if saving >= cfg.radial_min_line_saving else flat
            break

        if best is not None:
            return best

        # Nothing fits: fall back to the smallest allowed size and let it overflow.
        size = pinned_size if pinned_size is not None else style.min_font_size
        line_height = size * cfg.line_height_factor
        if allow_radial and not allow_tangential:
            available = wedge.radial_extent - 2 * cfg.cell_padding
        else:
            available = max(1.0, wedge.chord_at(center) * width_budget - 2 * cfg.cell_padding)
        lines = balance_lines(paragraphs, max(available, 1.0), style, size, family,
                              self.measurer, max_chars)
        chosen = RADIAL if (allow_radial and not allow_tangential) else TANGENTIAL
        return FittedText(lines, size, chosen, line_height, center, overflow=True)


# ============================================================================
# SVG OUTPUT
# ============================================================================

def by_author(author: str) -> str:
    """How a credit goes on to its author: " by NAME" for a name, and ", drawn
    for this project" for a phrase, which begins in lower case."""
    if not author:
        return ""
    return (", " if author[:1].islower() else " by ") + author


def credit_lines(row: dict) -> list[str]:
    """The artwork credit as two short lines: what and by whom; license and source."""
    title = _cell(row, "title") or _cell(row, "label") or _cell(row, "key")
    author = _cell(row, "author")
    first = f"Center artwork: {title}" + by_author(author)
    source = _cell(row, "source_url")
    for prefix in ("https://", "http://"):
        if source.startswith(prefix):
            source = source[len(prefix):]
    second = " · ".join(part for part in (_cell(row, "license"), source) if part)
    changes = _cell(row, "changes")
    if changes and changes.lower() != "none":
        second += f" · {changes}"
    return [first, second] if second else [first]


def xml_escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace('"', "&quot;").replace("'", "&apos;"))


class SVGBuilder:
    """Accumulates SVG markup."""

    def __init__(self, settings: Settings, measurer: TextMeasurer) -> None:
        self.settings = settings
        self.measurer = measurer
        self.parts: list[str] = []
        # Per document, not per process: as a class attribute this counter made
        # the arc ids depend on how many calendars had been drawn before, so
        # drawing two years in one run gave the second one ids starting at 180.
        self._path_ids = count(1)
        self._clip_ids = count(1)
        self.patterns: set[str] = set()

    # -- plumbing ------------------------------------------------------------

    def write(self, markup: str) -> None:
        self.parts.append(markup)

    def content(self) -> str:
        return "".join(self.parts)

    def open_document(self) -> None:
        cfg = self.settings
        self.write(
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{cfg.width}" height="{cfg.height}" '
            f'viewBox="0 0 {cfg.width} {cfg.height}">\n'
            f'<rect x="0" y="0" width="{cfg.width}" height="{cfg.height}" '
            f'fill="{cfg.background_fill}" />\n'
        )

    def close_document(self) -> None:
        self.write("</svg>\n")

    def add_credit(self, lines: list[str]) -> None:
        """Small lines of text in the lower-left corner, clear of the wheel."""
        cfg = self.settings
        size, step, x = 12, 16, 16
        bottom = cfg.height - 16
        self.write(f'<g font-family="{xml_escape(cfg.font_family_sans)}" font-size="{size}" '
                   f'fill="#555555">\n')
        for i, line in enumerate(lines):
            y = bottom - (len(lines) - 1 - i) * step
            self.write(f'<text x="{x}" y="{y}">{xml_escape(line)}</text>\n')
        self.write('</g>\n')

    # -- shapes --------------------------------------------------------------

    def _annulus_path(self, r_inner: float, r_outer: float,
                      angle_start: float, angle_end: float) -> str:
        cfg = self.settings
        large_arc = 1 if (angle_end - angle_start) > 180 else 0
        x1o, y1o = polar_to_cartesian(cfg.cx, cfg.cy, r_outer, angle_start)
        x2o, y2o = polar_to_cartesian(cfg.cx, cfg.cy, r_outer, angle_end)
        x2i, y2i = polar_to_cartesian(cfg.cx, cfg.cy, r_inner, angle_end)
        x1i, y1i = polar_to_cartesian(cfg.cx, cfg.cy, r_inner, angle_start)
        return (f"M {x1o:.2f},{y1o:.2f} "
                f"A {r_outer:.2f},{r_outer:.2f} 0 {large_arc} 1 {x2o:.2f},{y2o:.2f} "
                f"L {x2i:.2f},{y2i:.2f} "
                f"A {r_inner:.2f},{r_inner:.2f} 0 {large_arc} 0 {x1i:.2f},{y1i:.2f} Z")

    def add_sector(self, r_inner: float, r_outer: float, angle_start: float,
                   angle_end: float, fill: str, stroke: str = "none",
                   stroke_width: float = 0.0) -> None:
        path = self._annulus_path(r_inner, r_outer, angle_start, angle_end)
        self.write(f'<path d="{path}" fill="{self.paint(fill)}" stroke="{stroke}" '
                   f'stroke-width="{stroke_width}" />\n')

    def add_radial_line(self, r_inner: float, r_outer: float, angle: float,
                        stroke: str, stroke_width: float) -> None:
        """A line across a ring at one angle: where the year ends and begins
        (year_line) (church_year.js: SVGBuilder.addRadialLine)."""
        x1, y1 = polar_to_cartesian(self.settings.cx, self.settings.cy, r_inner, angle)
        x2, y2 = polar_to_cartesian(self.settings.cx, self.settings.cy, r_outer, angle)
        self.write(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                   f'stroke="{stroke}" stroke-width="{stroke_width}" />\n')

    def split_colors(self, start: int, r_inner: float, r_split: float, r_outer: float,
                     angle_start: float, angle_end: float, top_fill: str,
                     bottom_fill: str) -> None:
        """Recolor what was written since `start` for a two-color cell: the
        part above `r_split` keeps `top_fill`, the part below takes
        `bottom_fill`, so one label centered on the whole cell reads on both
        colors (church_year.js: SVGBuilder.splitColors)."""
        drawn = "".join(self.parts[start:])
        del self.parts[start:]
        if not drawn or top_fill == bottom_fill:
            self.write(drawn)
            return
        n = next(self._clip_ids)
        upper = self._annulus_path(r_split, r_outer, angle_start, angle_end)
        lower = self._annulus_path(r_inner, r_split, angle_start, angle_end)
        self.write(f'<defs><clipPath id="clip{n}a"><path d="{upper}" /></clipPath>'
                   f'<clipPath id="clip{n}b"><path d="{lower}" /></clipPath></defs>\n')
        self.write(f'<g clip-path="url(#clip{n}a)">\n{drawn}</g>\n')
        # The copy reuses the arcs the first one defined.
        copy = re.sub(r"<defs>.*?</defs>\n?", "", drawn, flags=re.S)
        copy = copy.replace(f'fill="{top_fill}"', f'fill="{bottom_fill}"')
        self.write(f'<g clip-path="url(#clip{n}b)">\n{copy}</g>\n')

    def paint(self, fill: str) -> str:
        """A fill as SVG paints it.  "#ffffff/#bfbfbf" (colors.csv) is a hatch:
        the second color in fine diagonal lines over the first -- no color, the
        hangings removed (church_year.js: SVGBuilder.paint)."""
        if "/" not in fill:
            return fill
        ground, line = (s.strip() for s in fill.split("/", 1))
        pid = "hatch-" + (ground + line).replace("#", "")
        if pid not in self.patterns:
            self.patterns.add(pid)
            self.write(f'<defs><pattern id="{pid}" width="6" height="6" '
                       f'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                       f'<rect width="6" height="6" fill="{ground}" />'
                       f'<line x1="0" y1="0" x2="0" y2="6" stroke="{line}" stroke-width="1.5" />'
                       f'</pattern></defs>\n')
        return f"url(#{pid})"

    def add_icon(self, icon: dict, x: float, y: float, rotation: float,
                 size: float, fill: str) -> None:
        """An icon from icons.csv, drawn in its 100 x 100 box at `size` units."""
        self.write(
            f'<path transform="translate({x:.2f},{y:.2f}) rotate({rotation:.2f}) '
            f'scale({size / 100.0:g}) translate(-50,-50)" d="{icon["path"]}" '
            f'fill="{fill}" fill-rule="evenodd" />\n')

    def add_circle_stroke(self, radius: float, color: str, width: float) -> None:
        cfg = self.settings
        self.write(f'<circle cx="{cfg.cx}" cy="{cfg.cy}" r="{radius:.2f}" fill="none" '
                   f'stroke="{color}" stroke-width="{width}" />\n')

    # -- text ----------------------------------------------------------------

    @staticmethod
    def _small_caps_runs(text: str) -> list[tuple[str, bool, bool]]:
        """Split text into (chunk, is_reduced, is_space) runs for small caps.

        Characters that were lower case become capitals drawn at a reduced
        size; everything else keeps its own case and full size.  Spaces are
        kept in runs of their own and never merged into a letter run: each run
        is drawn at an absolute x, and XML strips leading whitespace from an
        element, so a run beginning with a space would have its first letter
        pulled back onto the previous word ("OUR LORD" set as "OURL ORD").
        """
        runs: list[tuple[str, bool, bool]] = []
        for char in text:
            space = char.isspace()
            reduced = char.islower()
            glyph = char.upper() if reduced else char
            if runs and runs[-1][1] == reduced and runs[-1][2] == space:
                runs[-1] = (runs[-1][0] + glyph, reduced, space)
            else:
                runs.append((glyph, reduced, space))
        return runs

    def _text_element(self, content: str, x: float, y: float, style: TextStyle,
                      size: float, fill: str) -> str:
        cfg = self.settings
        family = style.resolved_family(cfg)
        small_caps = str(style.font_variant).strip().lower() == "small-caps"
        synthesise = small_caps and cfg.small_caps_synthetic

        attrs = [f'x="{x:.2f}"', f'y="{y:.2f}"', f'font-family="{family}"',
                 f'font-size="{size:g}"']
        if style.font_weight and style.font_weight != "normal":
            attrs.append(f'font-weight="{style.font_weight}"')
        if style.font_style and style.font_style != "normal":
            attrs.append(f'font-style="{style.font_style}"')
        # Synthesised runs carry their own absolute x, so each is its own text
        # chunk and must anchor at its start.
        attrs.append(f'text-anchor="{"start" if synthesise else "middle"}"')
        attrs.append('dominant-baseline="middle"')
        attrs.append(f'fill="{fill}"')

        if synthesise:
            body = self._small_caps_body(content, x, size, style)
        else:
            if style.font_variant and style.font_variant != "normal":
                attrs.append(f'style="font-variant: {style.font_variant}"')
            attrs.append(self._text_length(content, size, style, style.font_style,
                                           style.font_variant))
            body = xml_escape(content)

        return f'  <text {" ".join(attrs)}>{body}</text>\n'

    def _text_length(self, content: str, size: float, style: TextStyle,
                     font_style: str, variant: str = "normal") -> str:
        """The width the line was fitted at, as the line's own length: a
        browser without Times New Roman or Arial (a phone's Noto Serif is a
        tenth wider) draws it to that width rather than past its cell
        (church_year.js: SVGBuilder.textLength)."""
        width = self.measurer.width(content, size, style.metric_family, style.font_weight,
                                    font_style, variant)
        return f'textLength="{width:.2f}" lengthAdjust="spacingAndGlyphs"'

    def _small_caps_body(self, content: str, x: float, size: float,
                         style: TextStyle) -> str:
        """Small caps as capitals at two sizes, each run placed at an exact x.

        Letting the runs flow (tspans with no x) is what the SVG spec intends,
        but renderers disagree about it — CairoSVG re-applies the parent's x to
        every tspan, which stacks the whole line on top of its first letter.
        Measuring each run and writing its x removes the question entirely.
        """
        reduced = size * self.settings.small_caps_ratio
        runs = [(chunk, reduced if is_reduced else size, is_space)
                for chunk, is_reduced, is_space in self._small_caps_runs(content)]

        def advance(chunk: str, run_size: float) -> float:
            return self.measurer.width(chunk, run_size, style.metric_family,
                                       style.font_weight, style.font_style)

        total = _plain_sum(advance(chunk, run_size) for chunk, run_size, _ in runs)
        cursor = x - total / 2.0
        parts = []
        for chunk, run_size, is_space in runs:
            # Spaces only move the pen along; drawing them would leave every
            # following x one space adrift wherever a renderer strips them.
            if not is_space:
                parts.append(f'<tspan x="{cursor:.2f}" font-size="{run_size:g}" '
                             f'textLength="{advance(chunk, run_size):.2f}" '
                             f'lengthAdjust="spacingAndGlyphs">{xml_escape(chunk)}</tspan>')
            cursor += advance(chunk, run_size)
        return "".join(parts)

    def add_fitted_text(self, fitted: FittedText, style: TextStyle, wedge: Wedge,
                        fill: str, radial_shift: float = 0.0) -> None:
        """Draw a fitted block, centered on its wedge's mid angle.

        Tangential blocks stack their lines inward; radial blocks run outward
        from the center of the wheel and stack their lines sideways.
        """
        if not fitted.lines:
            return
        cfg = self.settings
        radius = fitted.r_center - radial_shift
        if fitted.orientation == RADIAL:
            anchor_x, anchor_y = polar_to_cartesian(cfg.cx, cfg.cy, radius, wedge.angle_mid)
            rotation = wedge.angle_mid
        else:
            anchor_x, anchor_y = polar_to_cartesian(cfg.cx, cfg.cy, radius, wedge.angle_mid)
            rotation = wedge.angle_mid + 90.0

        total = fitted.line_height * len(fitted.lines)
        start = -(total - fitted.line_height) / 2.0
        self.write(f'<g transform="translate({anchor_x:.2f},{anchor_y:.2f}) '
                   f'rotate({rotation:.2f})">\n')
        for index, line in enumerate(fitted.lines):
            self.write(self._text_element(line, 0.0, start + index * fitted.line_height,
                                          style, fitted.size, fill))
        self.write("</g>\n")

    def add_anchored_text(self, text: str, x: float, y: float, rotation: float,
                          style: TextStyle, size: float, fill: str,
                          anchor: str = "middle") -> None:
        """A single line placed at an exact point (day numbers, month labels)."""
        cfg = self.settings
        family = style.resolved_family(cfg)
        baseline = ' dominant-baseline="middle"' if anchor == "middle" else ""
        self.write(
            f'<g transform="translate({x:.2f},{y:.2f}) rotate({rotation:.2f})">\n'
            f'  <text x="0" y="0" font-family="{family}" font-size="{size:g}" '
            f'font-weight="{style.font_weight}" text-anchor="{anchor}"{baseline} '
            f'fill="{fill}" {self._text_length(text, size, style, "normal")}>'
            f'{xml_escape(text)}</text>\n'
            f'</g>\n')

    def add_curved_label(self, text: str, angle_start: float, angle_end: float,
                         radius: float, size: float, family: str,
                         weight: str, color: str, metric_family: str = "serif",
                         subtitle: str = "") -> None:
        """A label bent along a ring, optionally with a smaller trailing part.

        With a subtitle the two sit on one baseline at two sizes, as two runs
        that meet at one point along the arc (see below).
        """
        cfg = self.settings
        path_id = f"arc{next(self._path_ids)}"
        adjusted = radius + size * cfg.curved_text_vertical_offset
        large_arc = 1 if (angle_end - angle_start) > 180 else 0
        x_start, y_start = polar_to_cartesian(cfg.cx, cfg.cy, adjusted, angle_start)
        x_end, y_end = polar_to_cartesian(cfg.cx, cfg.cy, adjusted, angle_end)
        self.write(
            f'<defs><path id="{path_id}" d="M {x_start:.2f},{y_start:.2f} '
            f'A {adjusted:.2f},{adjusted:.2f} 0 {large_arc} 1 {x_end:.2f},{y_end:.2f}" />'
            f'</defs>\n')

        attrs = (f'font-family="{family}" font-size="{size:g}" '
                 f'font-weight="{weight}" fill="{color}"')
        if not subtitle:
            self.write(f'<text {attrs} text-anchor="middle" xml:space="preserve">'
                       f'<textPath href="#{path_id}" xlink:href="#{path_id}" '
                       f'startOffset="50%" text-anchor="middle">{xml_escape(text)}'
                       f'</textPath></text>\n')
            return

        # The name and the subtitle sit on one baseline at two sizes.  Each is a
        # run of its own, the name ending and the subtitle beginning at one point
        # along the arc: renderers disagree about how a tspan advances inside a
        # textPath (CairoSVG anchors every tspan by itself, stacking the two), but
        # none disagree about an anchor at an offset written down in user units.
        # The metrics only place that point, so if a 900-weight face is wider
        # than they say, the label sits a little off center; the two parts never
        # meet.
        small = size * cfg.ring_subtitle_ratio
        sep = cfg.ring_subtitle_separator
        name = text + sep.rstrip()
        gap = self.measurer.width(sep[len(sep.rstrip()):], size, metric_family, weight)
        w_name = self.measurer.width(name, size, metric_family, weight)
        w_sub = self.measurer.width(subtitle, small, metric_family, "normal", "italic")
        length = math.radians(angle_end - angle_start) * adjusted
        joint = length / 2.0 + (w_name - gap - w_sub) / 2.0
        self.write(
            f'<text {attrs} text-anchor="end" xml:space="preserve">'
            f'<textPath href="#{path_id}" xlink:href="#{path_id}" '
            f'startOffset="{joint:.2f}" text-anchor="end">{xml_escape(name)}</textPath></text>\n'
            f'<text font-family="{family}" font-size="{small:g}" font-style="italic" '
            f'font-weight="normal" fill="{color}" text-anchor="start" xml:space="preserve">'
            f'<textPath href="#{path_id}" xlink:href="#{path_id}" '
            f'startOffset="{joint + gap:.2f}" text-anchor="start">{xml_escape(subtitle)}'
            f'</textPath></text>\n')

    # -- center artwork ------------------------------------------------------

    def add_center_artwork(self, svg_path: Path, radius: float, clip: float = 0.0) -> None:
        """Scale a picture (an SVG, or a PNG, JPEG, GIF or WebP) to fill the
        middle of the wheel.  A picture enlarged past the middle's circle
        (`radius` above `clip`) is cut to that circle, so it does not cover
        the rings around it."""
        cfg = self.settings
        try:
            art = artwork_markup(svg_path)
        except Exception as exc:
            print(f"  ! center artwork {svg_path} could not be read ({exc}); "
                  f"leaving the middle blank", file=sys.stderr)
            return
        orig_w, orig_h, min_x, min_y = art["w"], art["h"], art["x"], art["y"]

        size = radius * 2.0
        scale = size / max(orig_w, orig_h)
        # Centered on its own width and height, so a picture taller than it is
        # wide (a cross with a long foot) sits in the middle rather than
        # against the left of the circle.  A square picture lands where it
        # always did.
        x_pos = cfg.cx - orig_w * scale / 2.0 - min_x * scale
        y_pos = cfg.cy - orig_h * scale / 2.0 - min_y * scale

        cut = clip > 0 and radius > clip
        if cut:
            self.write(f'<clipPath id="cy-center-clip"><circle cx="{cfg.cx:.2f}" cy="{cfg.cy:.2f}" '
                       f'r="{clip:.2f}" /></clipPath>\n<g clip-path="url(#cy-center-clip)">\n')
        self.write(f'<g transform="translate({x_pos:.2f},{y_pos:.2f}) scale({scale:.6f})">\n')
        self.write(art["body"])
        self.write("\n</g>\n")
        if cut:
            self.write("</g>\n")


# ============================================================================
# CENTER ARTWORK FILES
# ============================================================================
# The middle holds an artwork.csv picture, or one of the user's own: an SVG,
# whose drawing is copied in, or a photo or scan, which is embedded whole as a
# data: URI so the SVG stays one file.  web/export_data.py freezes the same
# markup for the browser, so the two renderers cannot disagree about it.

RASTER_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".gif": "image/gif", ".webp": "image/webp"}
ART_SUFFIXES = (".svg",) + tuple(RASTER_TYPES)
OWN_ART_CLIP = "cy-own-art-clip"


def is_art_file(name: str) -> bool:
    """Whether a center_svg / --art value names a picture file rather than a key."""
    return Path(str(name).strip()).suffix.lower() in ART_SUFFIXES


def resolve_art_file(name: str, data_dir: Optional[Path] = None) -> Optional[Path]:
    """A picture of the user's own: an absolute path, or one found from the
    current folder, then the project folder (this script's), then the data
    folder and the folder above it, as center_svg files always were."""
    candidate = Path(str(name).strip()).expanduser()
    if candidate.is_absolute():
        return candidate if candidate.is_file() else None
    bases = [Path.cwd(), Path(__file__).resolve().parent]
    if data_dir is not None:
        bases += [Path(data_dir), Path(data_dir).parent]
    for base in bases:
        found = base / candidate
        if found.is_file():
            return found.resolve()
    return None


def raster_size(path: Path) -> tuple[int, int]:
    """A PNG's, JPEG's, GIF's or WebP's width and height in pixels, read from
    its header (Pillow, when it is installed, for anything unusual)."""
    import struct
    data = path.read_bytes()
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", data[16:24])
        if data[:6] in (b"GIF87a", b"GIF89a"):
            return struct.unpack("<HH", data[6:10])
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            kind = data[12:16]
            if kind == b"VP8 ":
                w, h = struct.unpack("<HH", data[26:30])
                return w & 0x3FFF, h & 0x3FFF
            if kind == b"VP8L":
                bits = int.from_bytes(data[21:25], "little")
                return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
            if kind == b"VP8X":
                return (int.from_bytes(data[24:27], "little") + 1,
                        int.from_bytes(data[27:30], "little") + 1)
        if data[:2] == b"\xff\xd8":
            i = 2
            while i + 9 < len(data):
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7 or marker == 0xFF:
                    i += 1 if marker == 0xFF else 2
                    continue
                length = struct.unpack(">H", data[i + 2:i + 4])[0]
                if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    return w, h
                i += 2 + length
    except struct.error:
        pass
    try:
        from PIL import Image
        with Image.open(path) as image:
            return image.size
    except ImportError:
        raise ValueError("its size could not be read (pip install pillow)") from None


def artwork_markup(path: Path) -> dict:
    """A picture's own box (x, y, w, h) and the markup that draws it inside it.

    An SVG gives its children and its viewBox.  A raster image is one <image>
    of its pixel size, cut to the circle the middle of the wheel is, so a
    square photo comes out round instead of covering the month ring.
    """
    path = Path(path)
    mime = RASTER_TYPES.get(path.suffix.lower())
    if mime:
        import base64
        w, h = raster_size(path)
        if not (w and h):
            raise ValueError("it has no size")
        uri = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")
        body = (f'<clipPath id="{OWN_ART_CLIP}"><circle cx="{w / 2:g}" cy="{h / 2:g}" '
                f'r="{max(w, h) / 2:g}" /></clipPath>'
                f'<image x="0" y="0" width="{w}" height="{h}" clip-path="url(#{OWN_ART_CLIP})" '
                f'xlink:href="{uri}" />')
        return {"x": 0.0, "y": 0.0, "w": float(w), "h": float(h), "body": body}

    import xml.etree.ElementTree as ET
    root = ET.parse(path).getroot()
    box = root.get("viewBox")
    x = y = 0.0
    if box:
        x, y, w, h = (float(v) for v in box.replace(",", " ").split())
    else:
        def num(value: str, fallback: float) -> float:
            digits = "".join(c for c in value if c.isdigit() or c == ".")
            return float(digits) if digits else fallback
        w = num(root.get("width", "100"), 100.0)
        h = num(root.get("height", "100"), 100.0)
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    body = "".join(ET.tostring(child, encoding="unicode") for child in root)
    return {"x": x, "y": y, "w": w, "h": h, "body": body}


def own_art_scale(text: str) -> float:
    """center_svg_scale: blank, nonsense or not above 0 is 1."""
    try:
        value = float(str(text or "").strip() or 1.0)
    except ValueError:
        return 1.0
    return value if value > 0 and math.isfinite(value) else 1.0


def own_art_row(path: Path, credit: str, scale: str) -> dict:
    """A picture of the user's own, as an artwork.csv row would describe it:
    named by its file, and credited only if a credit is given."""
    credit = (credit or "").strip()
    return {"key": own_art_key(path), "label": Path(path).name, "title": credit,
            "attribution": "required" if credit else "", "scale": str(scale or "").strip(),
            "own": "true"}


def own_art_key(path: Path) -> str:
    """The key the page knows a picture of the user's own by: file:<name>."""
    return "file:" + Path(path).name.lower()


# ============================================================================
# PNG EXPORT
# ============================================================================
# The SVG is the master.  A PNG is rasterized from it with whatever tool is on
# the machine, tried best-first.  Install any one of these for exact output:
#   pip install cairosvg           librsvg (rsvg-convert)           Inkscape
# Chrome/Edge is used as a last resort; it works, but see _render_with_chrome.

PNG_BACKENDS_HELP = """\
  To export PNG, install any one of:
    * cairosvg      pip install cairosvg
    * rsvg-convert  apt install librsvg2-bin  /  brew install librsvg
    * Inkscape      https://inkscape.org
    * Google Chrome (already installed on most machines)"""


# Homebrew, MacPorts and snap install here, and these are not always on PATH —
# a launchd or cron job gets a much barer PATH than a terminal does.
EXTRA_TOOL_DIRS = ("/opt/homebrew/bin", "/usr/local/bin", "/opt/local/bin",
                   "/snap/bin")


def _which(*names: str) -> Optional[str]:
    import shutil
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    for name in names:
        for folder in EXTRA_TOOL_DIRS:
            candidate = Path(folder) / name
            if candidate.is_file():
                return str(candidate)
    return None


def _find_chrome() -> Optional[str]:
    """Chrome and Edge, including Windows per-user installs.

    On Windows, Chrome is very often installed for the current user only, under
    %LOCALAPPDATA%, and is not on PATH in either case.
    """
    import os
    env = os.environ.get("CHROME_PATH") or os.environ.get("CHROME")
    if env and Path(env).exists():
        return env
    found = _which("google-chrome", "google-chrome-stable", "chrome", "chromium",
                   "chromium-browser", "microsoft-edge", "msedge")
    if found:
        return found

    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    roots = [os.environ.get("PROGRAMFILES", r"C:\Program Files"),
             os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
             os.environ.get("LOCALAPPDATA", "")]
    tails = [r"Google\Chrome\Application\chrome.exe",
             r"Google\Chrome Beta\Application\chrome.exe",
             r"Chromium\Application\chrome.exe",
             r"Microsoft\Edge\Application\msedge.exe"]
    for root in roots:
        if root:
            candidates += [str(Path(root) / tail) for tail in tails]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


def _find_inkscape() -> Optional[str]:
    """Inkscape's Windows installer does not add it to PATH, so look for it."""
    import os
    env = os.environ.get("INKSCAPE_PATH")
    if env and Path(env).exists():
        return env
    found = _which("inkscape", "inkscape.com")
    if found:
        return found
    for candidate in (
        r"C:\Program Files\Inkscape\bin\inkscape.exe",
        r"C:\Program Files\Inkscape\inkscape.exe",
        r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe",
        r"C:\Program Files (x86)\Inkscape\inkscape.exe",
        "/Applications/Inkscape.app/Contents/MacOS/inkscape",
    ):
        if Path(candidate).exists():
            return candidate
    return None


# Why the last external renderer failed, for the error message.
_LAST_RUN_ERROR: str = ""


def _run(command: list[str], timeout: int = 300) -> bool:
    global _LAST_RUN_ERROR
    import subprocess
    try:
        done = subprocess.run(command, capture_output=True, timeout=timeout)
    except FileNotFoundError:
        _LAST_RUN_ERROR = f"{command[0]} could not be started"
        return False
    except Exception as exc:
        _LAST_RUN_ERROR = f"{type(exc).__name__}: {exc}"
        return False
    if done.returncode == 0:
        _LAST_RUN_ERROR = ""
        return True
    detail = (done.stderr or done.stdout or b"").decode("utf-8", "replace").strip()
    tail = detail.splitlines()[-1] if detail else "no output"
    _LAST_RUN_ERROR = f"exit code {done.returncode}: {tail}"
    return False


def _png_size(path: Path) -> Optional[tuple[int, int]]:
    """Width and height straight out of the PNG header, no image library needed."""
    import struct
    try:
        with open(path, "rb") as handle:
            header = handle.read(24)
        if header[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        return struct.unpack(">II", header[16:24])
    except Exception:
        return None


def _render_with_cairosvg(svg: Path, png: Path, width: int, height: int,
                          background: str) -> bool:
    try:
        import cairosvg
    except ImportError:
        return False
    try:
        cairosvg.svg2png(url=str(svg), write_to=str(png),
                         output_width=width, output_height=height)
        return png.exists()
    except Exception as exc:
        print(f"  ! cairosvg failed: {exc}", file=sys.stderr)
        return False


def _render_with_rsvg(svg: Path, png: Path, width: int, height: int,
                      background: str) -> bool:
    tool = _which("rsvg-convert")
    if not tool:
        return False
    return _run([tool, "-w", str(width), "-h", str(height),
                 "-o", str(png), str(svg)]) and png.exists()


def _render_with_inkscape(svg: Path, png: Path, width: int, height: int,
                          background: str) -> bool:
    tool = _find_inkscape()
    if not tool:
        return False
    solid = bool(background) and background != "none"

    modern = [tool, "--export-type=png", f"--export-filename={png}",
              f"--export-width={width}", f"--export-height={height}"]
    modern += ([f"--export-background={background}", "--export-background-opacity=1"]
               if solid else ["--export-background-opacity=0"])
    if _run(modern + [str(svg)]) and png.exists():
        return True

    # Inkscape 0.92 and earlier took a different flag set.
    legacy = [tool, "-z", "-e", str(png), "-w", str(width), "-h", str(height)]
    legacy += ["-b", background, "-y", "1.0"] if solid else ["-y", "0.0"]
    return _run(legacy + [str(svg)]) and png.exists()


def _render_with_resvg(svg: Path, png: Path, width: int, height: int,
                       background: str) -> bool:
    tool = _which("resvg")
    if not tool:
        return False
    return _run([tool, "-w", str(width), "-h", str(height),
                 str(svg), str(png)]) and png.exists()


def _chrome_viewport_offset(chrome: str, probe: int = 800) -> int:
    """How much of the window Chrome's headless screenshot cannot draw into.

    A headless screenshot is the size of the *window*, but Chrome only paints
    into the window minus its frame.  Sizing the window to the artwork
    therefore loses a strip off the bottom.  Ask a page how tall its viewport
    really is, and make the window that much taller.
    """
    import re
    import subprocess
    import tempfile
    page = "<!doctype html><script>document.title='VP'+window.innerHeight+'PV'</script>"
    with tempfile.TemporaryDirectory() as folder:
        probe_file = Path(folder) / "probe.html"
        probe_file.write_text(page, encoding="utf-8")
        try:
            done = subprocess.run(
                [chrome, "--headless", "--disable-gpu", "--no-sandbox",
                 "--hide-scrollbars", "--force-device-scale-factor=1",
                 f"--window-size={probe},{probe}", "--virtual-time-budget=2000",
                 "--dump-dom", probe_file.as_uri()],
                capture_output=True, timeout=90)
        except Exception:
            return 100
    match = re.search(rb"VP(\d+)PV", done.stdout or b"")
    if not match:
        return 100
    inner = int(match.group(1))
    return max(0, probe - inner) if 0 < inner <= probe else 100


def _crop_bottom(png: Path, height: int) -> bool:
    try:
        from PIL import Image
    except ImportError:
        return False
    try:
        with Image.open(png) as image:
            if image.height <= height:
                return True
            image.crop((0, 0, image.width, height)).save(png)
        return True
    except Exception:
        return False


def _render_with_chrome(svg: Path, png: Path, width: int, height: int,
                        background: str) -> bool:
    """Last resort.  Accurate, but a screenshot is the window, not the page."""
    import tempfile
    chrome = _find_chrome()
    if not chrome:
        return False
    offset = _chrome_viewport_offset(chrome)
    fill = background if background and background != "none" else "transparent"
    with tempfile.TemporaryDirectory() as folder:
        page = Path(folder) / "page.html"
        page.write_text(
            "<!doctype html><meta charset='utf-8'>"
            f"<style>html,body{{margin:0;padding:0;background:{fill};overflow:hidden}}"
            f"img{{display:block;width:{width}px;height:{height}px}}</style>"
            f"<img src='{svg.resolve().as_uri()}'>", encoding="utf-8")
        # A separate profile: without it, an already-running Chrome makes the
        # headless call hand off to the live instance and exit without drawing.
        profile = Path(folder) / "profile"
        command = [chrome, "--headless", "--disable-gpu", "--no-sandbox",
                   "--hide-scrollbars", "--force-device-scale-factor=1",
                   f"--user-data-dir={profile}", "--no-first-run",
                   f"--window-size={width},{height + offset}",
                   "--virtual-time-budget=15000",
                   f"--screenshot={png}", page.as_uri()]
        if fill == "transparent":
            command.insert(1, "--default-background-color=00000000")
        if not _run(command) or not png.exists():
            return False
    size = _png_size(png)
    if size and size[1] > height and not _crop_bottom(png, height):
        print(f"  ! Chrome returned a {size[0]}x{size[1]} image instead of "
              f"{width}x{height}; the artwork is complete but there is a blank "
              f"strip below it. Install Pillow (pip install pillow) or one of "
              f"the renderers listed by --help to get an exact size.",
              file=sys.stderr)
    return True


# The order `auto` tries them in.  CairoSVG comes last on purpose: it is the
# easiest to install but the weakest on this drawing's text (it ignores font
# stacks, does not advance <tspan> runs and drops font-variant), so it is only
# taken when nothing better is on the machine.
PNG_BACKENDS: list[tuple[str, Callable]] = [
    ("inkscape", _render_with_inkscape),
    ("rsvg-convert", _render_with_rsvg),
    ("resvg", _render_with_resvg),
    ("Chrome", _render_with_chrome),
    ("cairosvg", _render_with_cairosvg),
]


def _cairosvg_location() -> Optional[str]:
    try:
        import cairosvg
    except ImportError:
        return None
    return getattr(cairosvg, "__file__", "installed")


# One place that knows where each renderer lives, used by both the error
# message and --list-renderers.
RENDERER_LOCATIONS: dict[str, Callable[[], Optional[str]]] = {
    "cairosvg": _cairosvg_location,
    "rsvg-convert": lambda: _which("rsvg-convert"),
    "inkscape": _find_inkscape,
    "resvg": lambda: _which("resvg"),
    "chrome": _find_chrome,
}


def report_renderers() -> None:
    """Say which rasterizers this machine has, and where they were found."""
    print("PNG renderers on this machine:")
    for name, locate in RENDERER_LOCATIONS.items():
        where = locate()
        mark = "*" if where else "-"
        print(f"  {mark} {name:14} {where or 'not found'}")
    try:
        from PIL import Image  # noqa: F401
        print("  * Pillow         installed (used to trim Chrome's screenshot)")
    except ImportError:
        print("  - Pillow         not installed  (pip install pillow)")
    print("\nSet png_renderer in config.csv, or pass --png-renderer, to pin one.")


def write_png(svg_markup: str, png_path: Path, settings: Settings,
              width: int, background: str, renderer: str = "auto") -> bool:
    """Rasterize the calendar to PNG.  Returns True if a file was written."""
    import tempfile

    height = max(1, int(round(width * settings.height / settings.width)))

    wanted = (renderer or "auto").strip().lower()
    if wanted in ("", "auto"):
        chosen = PNG_BACKENDS
    else:
        chosen = [b for b in PNG_BACKENDS if b[0].lower() == wanted]
        if not chosen:
            names = ", ".join(name for name, _ in PNG_BACKENDS)
            print(f"  ! png_renderer '{renderer}' is not one of: auto, {names}",
                  file=sys.stderr)
            return False

    # Paint the background into a throwaway copy so every backend agrees.
    markup = svg_markup
    if background and background != "none":
        markup = markup.replace(f'fill="{settings.background_fill}" />',
                                f'fill="{background}" />', 1)

    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder) / "calendar.svg"
        source.write_text(markup, encoding="utf-8")
        for name, backend in chosen:
            if backend(source, png_path, width, height, background):
                print(f"✓ Wrote {png_path.resolve()} ({width}x{height}, via {name})")
                return True

    if wanted not in ("", "auto"):
        found = RENDERER_LOCATIONS.get(wanted, lambda: None)()
        if found is None:
            print(f"  ! png_renderer '{renderer}' was not found on this machine, "
                  f"so no PNG was written.", file=sys.stderr)
        else:
            print(f"  ! png_renderer '{renderer}' was found at {found} but failed, "
                  f"so no PNG was written.", file=sys.stderr)
            if _LAST_RUN_ERROR:
                print(f"    {_LAST_RUN_ERROR}", file=sys.stderr)
        others = [name for name, locate in RENDERER_LOCATIONS.items()
                  if name != wanted and locate()]
        if others:
            print(f"    Available here instead: {', '.join(others)} — set "
                  f"png_renderer in config.csv, or pass --png-renderer.",
                  file=sys.stderr)
            return False
    else:
        print("  ! No PNG renderer was found, so only the SVG was written.",
              file=sys.stderr)
    print("    Run  python church_year_image.py --list-renderers  to see what is here.",
          file=sys.stderr)
    print(PNG_BACKENDS_HELP, file=sys.stderr)
    return False


# ============================================================================
# CALENDAR MODEL
# ============================================================================

def days_between(start: CivilDate, end: CivilDate) -> Iterator[CivilDate]:
    return _days_between(start, end)


def group_into_weeks(days: Iterable[date], week_starts_on: int,
                     bands: int = 7) -> list[list[Optional[date]]]:
    """The days in weeks, each week a row of `bands` cells.

    A year that does not begin on the first day of a week -- the Orthodox year
    begins on 1 September, whatever day that is -- starts partway through its
    first week, so that week is padded with empty cells in front, and each day
    keeps the band its weekday belongs to.  The last week is padded after.
    """
    weeks: list[list[Optional[date]]] = []
    current: list[Optional[date]] = []
    for day in days:
        if day.weekday() == week_starts_on and current:
            weeks.append(current)
            current = []
        if not current and not weeks and bands == 7:
            current = [None] * ((day.weekday() - week_starts_on) % 7)
        current.append(day)
    if current:
        weeks.append(current)
    return [week + [None] * (bands - len(week)) if len(week) < bands else week
            for week in weeks]


@dataclass
class Warning_:
    day: Optional[date]
    where: str
    message: str


class Calendar:
    """Everything loaded from the data directory, plus the derived geometry."""

    def __init__(self, data_dir: Path, overrides: Optional[dict[str, str]] = None,
                 hide: Iterable[str] = (), color_changes: str = "",
                 art_date: str = "") -> None:
        """`overrides`: settings laid over config.csv for this drawing only (the
        command line's --art, --mid-text ...).  `hide`: rings.csv keys to leave
        out, as the page's hide= does; the day cells and the center stay.
        `color_changes`: colors repainted for this drawing, as the page's Colors
        menu and a link's colors= do (parse_color_changes).  `art_date`: a day
        (2026-12-25) whose season's picture the middle holds, where
        season_art.csv gives that season one, as the page's "By season" does."""
        import traditions
        self.data_dir = data_dir
        raw = read_config(data_dir / "config.csv")
        try:
            self.tradition = traditions.find_tradition(
                data_dir, raw.get("lectionary") or "lcms-three-year")
            # The tradition's own files, over the shared ones.
            self.folder = traditions.folder_path(data_dir, self.tradition)
        except ValueError as exc:
            sys.exit(f"✗ config.csv: {exc}")
        self.tradition_settings = traditions.tradition_settings(data_dir, self.tradition)
        try:
            changes = parse_color_changes(color_changes, self.tradition.key,
                                          self.tradition.tradition)
        except ValueError as exc:
            sys.exit(f"✗ --color-changes: {exc}")
        if changes.empty:
            overrides = {**(overrides or {}), "empty_cell_fill": changes.empty}
        # A tradition's own calendar (the Orthodox Revised Julian) is only where
        # new_year.py starts: the year folder's config.csv says which calendar
        # this year was actually made in, and that is the one to draw.
        self.settings = load_settings(
            data_dir / "config.csv",
            {k: v for k, v in self.tradition_settings.items() if k != "calendar"},
            overrides)
        cfg = self.settings
        self.colors = with_overrides(
            with_mid_text(load_colors(data_dir / "colors.csv", self.folder / "colors.csv"),
                          cfg.mid_text),
            changes.days)
        self.season_colors = load_season_colors(self.folder / "seasons.csv", self.colors)
        self.language = load_language(data_dir, cfg.language)
        self.month_names = self.language.months
        self.styles = load_text_styles(data_dir / "text_styles.csv",
                                       self.folder / "text_styles.csv")
        hidden = {k.lower() for k in hide}
        self.rings = close_ring_gaps([
            replace(r, enabled=False) if (r.key.lower() in hidden
                                          and r.kind not in ("days", "center")) else r
            for r in load_rings(data_dir / "rings.csv")])
        if changes.rings or changes.ring_text:
            self.rings = [
                replace(r, **({"fill": changes.rings[r.key]} if r.key in changes.rings else {}),
                        **({"text_color": changes.ring_text[r.key]} if r.key in changes.ring_text else {}))
                for r in self.rings]
        self.season_periods = load_season_periods(
            data_dir / "season_periods.csv", self.colors, self.season_colors,
            cfg.reckoning)
        self.season_art_rows = load_season_art(data_dir / "season_art.csv")
        self.season_art_key = ""
        if art_date:
            try:
                wanted = CivilDate.parse(cfg.reckoning, art_date.strip())
            except ValueError as exc:
                sys.exit(f"✗ --art-date: '{art_date}' is not a date like 2026-12-25 ({exc})")
            self.season_art_key = self.season_art_on(wanted)
        self.broad_seasons = load_broad_seasons(data_dir / "broad_seasons.csv",
                                                cfg.reckoning)
        self.halves = load_broad_seasons(data_dir / "halves.csv", cfg.reckoning)
        self.titles = load_day_entries(
            data_dir / "sundays_seasons.csv", self.colors,
            cfg.church_year_start, cfg.church_year_end, "title", required=False,
            repeat=cfg.feast_repeat)
        # The year's commemorations, dated by new_year.py.
        self.feasts_file = data_dir / "year_feasts.csv"
        self.feasts = load_day_entries(
            self.feasts_file, self.colors,
            cfg.church_year_start, cfg.church_year_end, "name", required=False,
            repeat=cfg.feast_repeat,
            detail=cfg.feast_detail)
        self.icons = load_icons([data_dir / "sundays_seasons.csv", self.feasts_file],
                                cfg.church_year_start, cfg.church_year_end,
                                cfg.feast_detail)
        self.month_overrides = self._load_month_overrides(data_dir / "month_overrides.csv")
        self.icon_defs = load_icon_defs(data_dir / "icons.csv")

        self.default_color = (self.season_colors.get("DEFAULT")
                              or next(iter(self.colors.values())))

        self._every_day_yields = self._find_every_day_yields()
        self._check_year()

        self.days = list(days_between(cfg.church_year_start, cfg.church_year_end))
        self.weeks = group_into_weeks(self.days, cfg.week_starts_on, cfg.day_bands)
        self.angle_per_week = 360.0 / len(self.weeks)

        self.measurer = TextMeasurer(cfg.text_width_fudge, cfg.small_caps_ratio)
        self.fitter = TextFitter(cfg, self.measurer)
        self.warnings: list[Warning_] = []

    def reload_feasts(self) -> None:
        """Re-read the feasts CSV after `feast_detail` has been changed.

        A command-line flag settles after the settings are parsed, so the file
        has already been read once by then; this is how the flag takes effect
        without the settings having to know about the command line.
        """
        cfg = self.settings
        self.feasts = load_day_entries(
            self.feasts_file, self.colors,
            cfg.church_year_start, cfg.church_year_end, "name", required=False,
            repeat=cfg.feast_repeat,
            detail=cfg.feast_detail)
        self.icons = load_icons([self.data_dir / "sundays_seasons.csv", self.feasts_file],
                                cfg.church_year_start, cfg.church_year_end,
                                cfg.feast_detail)

    # -- sanity --------------------------------------------------------------

    def _check_year(self) -> None:
        """Say so when the year's dates and its dated files do not fit together.

        A wrong-but-well-formed year draws perfectly happily: change the two
        dates in config.csv without running new_year.py and the wheel comes out
        white with no Sundays on it, and a fit report saying every label fits.
        These are warnings rather than errors, so a deliberate odd span still
        draws.
        """
        cfg = self.settings
        start, end = cfg.church_year_start, cfg.church_year_end
        span = end.day_number - start.day_number + 1
        say = lambda text: print(f"  ! {text}", file=sys.stderr)

        # A tradition whose year starts on a fixed date (the Orthodox 1
        # September) begins partway through a week by design.
        weekly = (self.tradition_settings.get("year_start", "sun<12-25-21") or "").startswith("sun")
        if weekly and start.weekday() != cfg.week_starts_on:
            say(f"config.csv: church_year_start {start} is a {start.strftime('%A')}, "
                f"so the first wedge is short; a church year starts on Advent Sunday")
        if weekly and span not in (364, 371):
            say(f"config.csv: {start} to {end} is {span} days; a church year is "
                f"364 or 371 (52 or 53 weeks). Run new_year.py to get both dates right")

        hint = "were the dates in config.csv changed without running new_year.py?"
        rows = [row for row in read_rows(self.data_dir / "sundays_seasons.csv", required=False)
                if _cell(row, "title") and _cell(row, "date")]
        outside = 0
        for row in rows:
            try:
                if not _expand_dates(_cell(row, "date"), start, end):
                    outside += 1
            except ValueError:
                pass                      # reported when the file was loaded
        if rows and outside == len(rows):
            say(f"sundays_seasons.csv: none of its {len(rows)} rows fall between "
                f"{start} and {end}, so no Sunday is named; {hint}")
        elif outside:
            say(f"sundays_seasons.csv: {outside} of {len(rows)} rows fall outside "
                f"{start} to {end} and are not drawn")

        colored = [p for p in self.season_periods if p.color is not None]
        if colored and not any(p.start_date <= end and p.end_date >= start
                               for p in colored):
            say(f"season_periods.csv: no season falls between {start} and {end}, "
                f"so every day is drawn in the DEFAULT color; {hint}")

    # -- overrides -----------------------------------------------------------

    @staticmethod
    def _load_month_overrides(path: Path) -> dict[str, dict]:
        result = {"font_size": {}, "vertical": {}, "horizontal": {},
                  "first_day_vertical": 0.0}
        for row in read_rows(path, required=False):
            key = _cell(row, "month").lower()
            if key == "first_day":
                result["first_day_vertical"] = _float_or(row, "vertical_offset", 0.0)
                continue
            try:
                month = int(key)
            except ValueError:
                continue
            for column, bucket in (("font_size_override", "font_size"),
                                   ("vertical_offset", "vertical"),
                                   ("horizontal_offset", "horizontal")):
                value = _opt_float(row, column)
                if value is not None:
                    result[bucket][month] = value
        return result

    # -- lookups -------------------------------------------------------------

    def season_art_on(self, day: date) -> str:
        """The picture a day's season shows (season_art), or '' for the church's own."""
        within = [p for p in self.season_periods if p.start_date <= day <= p.end_date]
        named = next((p for p in within if p.name), None)
        colored = next((p for p in within if p.season), None)
        known = {_cell(row, "key").lower() for row in self.artwork_rows()}
        # The week of the season: its first seven days are week 1.
        whole = named or colored
        week = (day.day_number - whole.start_date.day_number) // 7 + 1 if whole else 1
        return season_art(self.season_art_rows, known, self.tradition.key,
                          named.name if named else "", colored.season if colored else "", week)

    def season_for(self, day: date) -> Optional[SeasonPeriod]:
        """The colored period a day falls in; label-only rows are not one."""
        for period in self.season_periods:
            if period.color and period.start_date <= day <= period.end_date:
                return period
        return None

    # -- precedence ----------------------------------------------------------
    #
    # When a saint's day falls on a day that outranks it, the higher day keeps
    # the top of the cell and the feast's color takes the lower half.  Left to
    # itself the Annunciation's white replaced the scarlet of Palm Sunday (2029,
    # 2040) and the violet of a Sunday in Lent (2057).  A day outranks a feast:
    #
    #   * anywhere in Holy Week and the week after it, Easter week
    #     (`feast_yield_every_day`), Palm Sunday and Easter Day included;
    #   * on a Sunday, or any other day the Sundays file names -- Christmas Eve,
    #     Ash Wednesday, the Ascension -- in Advent, Lent or Easter
    #     (`feast_yield_seasons`);
    #   * on any day the Sundays file gives a color of its own: Pentecost,
    #     Trinity, the Transfiguration.
    #
    # Everywhere else a feast colors its day as it always has: the whole cell for
    # a `color_override` -- an ordinary Sunday included, whose title still sits
    # on top -- or the lower half for a `color_override_bottom`.  The names are
    # written in every case.

    def _find_every_day_yields(self) -> set[int]:
        seasons = set(self.settings.feast_yield_every_day)
        days: set[int] = set()
        for period in self.season_periods:
            if period.season and period.season in seasons:
                # The season itself and the seven days after it: Easter week.
                days.update(range(period.start_date.day_number,
                                  period.end_date.day_number + 8))
        return days

    def feast_outranked(self, day: date) -> bool:
        """True when the day outranks its feasts, which then take only the foot."""
        if day.day_number in self._every_day_yields:
            return True
        titles = self.titles.get(day, [])
        if any(entry.color_override for entry in titles):
            return True
        period = self.season_for(day)
        return (period is not None
                and period.season in self.settings.feast_yield_seasons
                and (day.weekday() == 6 or bool(titles)))

    def color_for(self, day: date) -> LiturgicalColor:
        for entry in self.titles.get(day, []):
            if entry.color_override:
                return entry.color_override
        if not self.feast_outranked(day):
            for entry in self.feasts.get(day, []):
                if entry.color_override:
                    return entry.color_override
        period = self.season_for(day)
        if period and period.color:
            return period.color
        return self.default_color

    def bottom_color_for(self, day: date) -> Optional[LiturgicalColor]:
        # A day's own split (Christmas Eve, Holy Saturday, a Reformation Day
        # observed on the Sunday before) is part of the day, and comes first.
        for entry in self.titles.get(day, []):
            if entry.color_override_bottom:
                return entry.color_override_bottom
        feasts = self.feasts.get(day, [])
        for entry in feasts:
            if entry.color_override_bottom:
                return entry.color_override_bottom
        if self.feast_outranked(day):
            # A feast that would color the whole cell yields the top to the day
            # and takes the lower half: the Annunciation on Palm Sunday.
            for entry in feasts:
                if entry.color_override:
                    return entry.color_override
        return None

    # -- segment geometry ----------------------------------------------------

    def _day_angle(self, week_index: int, day_index: int) -> float:
        return (self.settings.start_angle + week_index * self.angle_per_week
                + (day_index / self.settings.day_bands) * self.angle_per_week)

    def year_seams(self) -> list[tuple[float, float]]:
        """The arcs of the padding cells where a year starts or ends partway
        through a week, so the rings can be closed over them."""
        if not self.weeks:
            return []
        start = self.settings.start_angle
        full = start + len(self.weeks) * self.angle_per_week
        seams = []
        lead = next((i for i, d in enumerate(self.weeks[0]) if d is not None), 0)
        if lead:
            seams.append((start, self._day_angle(0, lead)))
        filled = sum(1 for day in self.weeks[-1] if day is not None)
        if filled < len(self.weeks[-1]):
            seams.append((self._day_angle(len(self.weeks) - 1, filled), full))
        return seams

    def month_segments(self) -> list[tuple[int, float, float]]:
        """Angular runs of each calendar month, cut at the exact day of change."""
        segments: list[tuple[int, float, float]] = []
        current_month: Optional[int] = None
        segment_start = self.settings.start_angle
        for week_index, week in enumerate(self.weeks):
            for day_index, day in enumerate(week):
                if day is None:
                    continue
                angle = self._day_angle(week_index, day_index)
                if current_month is None:
                    current_month, segment_start = day.month, angle
                elif day.month != current_month:
                    segments.append((current_month, segment_start, angle))
                    current_month, segment_start = day.month, angle
        if current_month is not None:
            # The last month runs to the end of the last day; when the year
            # ends partway through a week, that is short of the full circle.
            filled = sum(1 for day in self.weeks[-1] if day is not None)
            end = (self.settings.start_angle + len(self.weeks) * self.angle_per_week
                   if filled == len(self.weeks[-1]) else
                   self._day_angle(len(self.weeks) - 1, filled))
            segments.append((current_month, segment_start, end))
        return segments

    def _period_segments(self, periods: Sequence[Any]) -> list[tuple[Any, float, float]]:
        """One angular run per dated period, from its first day to the end of its last."""
        day_width = self.angle_per_week / self.settings.day_bands
        positions: dict[date, float] = {}
        for week_index, week in enumerate(self.weeks):
            for day_index, day in enumerate(week):
                if day is not None:
                    positions[day] = self._day_angle(week_index, day_index)
        segments = []
        for period in periods:
            covered = [positions[d] for d in self.days
                       if period.start_date <= d <= period.end_date and d in positions]
            if covered:
                segments.append((period, min(covered), max(covered) + day_width))
        return segments

    def season_segments(self) -> list[tuple[SeasonPeriod, float, float]]:
        """The periods that label the ring; color-only rows are not among them."""
        return self._period_segments([p for p in self.season_periods if p.name])

    def broad_segments(self) -> list[tuple[BroadSeason, float, float]]:
        return self._period_segments(self.broad_seasons)

    def segments_for_source(self, source: str) -> list[tuple[Any, float, float]]:
        if source == "months":
            return [(m, a, b) for m, a, b in self.month_segments()]
        if source == "season_periods":
            return self.season_segments()
        if source == "broad_seasons":
            return self.broad_segments()
        if source == "halves":
            return self._period_segments(self.halves)
        print(f"  ! rings.csv: unknown source '{source}'", file=sys.stderr)
        return []

    def label_for_segment(self, source: str, item: Any) -> str:
        if source == "months":
            return self.month_names.get(item, str(item))
        return getattr(item, "name", str(item))

    def artwork_rows(self) -> list[dict]:
        """artwork.csv: the pictures the middle of the wheel can hold."""
        return [row for row in read_rows(self.data_dir / "artwork.csv", required=False)
                if _cell(row, "key")]

    def center_artwork_key(self) -> str:
        """Which artwork.csv entry the middle holds, or '' for a file named outright.

        `auto` asks the tradition, whose tradition.csv names its own
        (`center_art`); an older config.csv that names a file keeps working.
        A season's own picture (--art-date) comes before either.
        """
        if self.season_art_key:
            return self.season_art_key
        name = (self.settings.center_svg or "").strip()
        if name.lower() in ("auto", "season"):      # by season, on a day without a picture
            name = "auto"
        if name.lower() == "auto":
            name = self.tradition_settings.get("center_art", "") or "lutherrose"
        rows = self.artwork_rows()
        keys = {_cell(row, "key").lower() for row in rows}
        if name.lower() in keys:
            return name.lower()
        # A file named outright that artwork.csv lists is that entry, scale and all.
        for row in rows:
            if name and _cell(row, "file") == name:
                return _cell(row, "key").lower()
        return ""

    def center_artwork_file(self) -> str:
        name = (self.settings.center_svg or "").strip()
        if not self.season_art_key and (not name or name.lower() == "none"):
            return ""
        key = self.center_artwork_key()
        if key:
            for row in self.artwork_rows():
                if _cell(row, "key").lower() == key:
                    return _cell(row, "file")
        if name.lower() != "auto" and self.own_artwork_path() is not None:
            return name
        # `auto` naming artwork this folder does not have, or a file that is not
        # there: the tradition's own, then the first there is, then the Luther
        # rose shipped with the scripts.
        rows = self.artwork_rows()
        own = (self.tradition_settings.get("center_art", "") or "").lower()
        for row in rows:
            if _cell(row, "key").lower() == own:
                return _cell(row, "file")
        return _cell(rows[0], "file") if rows else "artwork/Luther_Rose.svg"

    def center_artwork_row(self) -> Optional[dict]:
        """The artwork.csv entry for what the middle holds, if it is one; for a
        picture of the user's own, a row like one, if a credit was given."""
        name = self.center_artwork_file()
        if not name:
            return None
        key = self.center_artwork_key()
        for row in self.artwork_rows():
            if (key and _cell(row, "key").lower() == key) or _cell(row, "file") == name:
                return row
        own = self.own_artwork_path()
        if own is not None and (self.settings.center_svg_credit or "").strip():
            return own_art_row(own, self.settings.center_svg_credit,
                               self.settings.center_svg_scale)
        return None

    def own_artwork_path(self) -> Optional[Path]:
        """The picture of the user's own center_svg names, when it names one:
        a file artwork.csv does not list, found from the current folder, then
        the project folder (see resolve_art_file)."""
        name = (self.settings.center_svg or "").strip()
        if not name or name.lower() in ("auto", "none") or self.center_artwork_key():
            return None
        return resolve_art_file(name, self.data_dir)

    def resolve_asset(self, name: str) -> Optional[Path]:
        """Find a file named in config.csv: absolute, or beside the data dir / script."""
        candidate = Path(name)
        if candidate.is_absolute():
            return candidate if candidate.exists() else None
        for base in (self.data_dir, self.data_dir.parent, Path.cwd(),
                     Path(__file__).resolve().parent):
            found = base / candidate
            if found.exists():
                return found
        return None

    def warn(self, day: Optional[date], where: str, message: str) -> None:
        self.warnings.append(Warning_(day, where, message))


# ============================================================================
# RENDERING
# ============================================================================

class Renderer:
    def __init__(self, calendar: Calendar) -> None:
        self.cal = calendar
        self.cfg = calendar.settings
        self.svg = SVGBuilder(self.cfg, calendar.measurer)

    # -- rings ---------------------------------------------------------------

    def render_rings(self) -> list[tuple[Ring, str]]:
        """Draw each ring, keeping its markup separately.

        The web version needs the rings apart from one another: everything but
        the center artwork turns when the wheel turns.
        """
        pieces: list[tuple[Ring, str]] = []
        for ring in self.cal.rings:
            if not ring.enabled:
                continue
            mark = len(self.svg.parts)
            if ring.kind == "days":
                self._render_week_ring(ring)
            elif ring.kind in ("segments", "months"):
                self._render_segment_ring(ring)
            elif ring.kind == "band":
                self._render_band_ring(ring)
            elif ring.kind == "center":
                self._render_center(ring)
            else:
                print(f"  ! rings.csv: unknown kind '{ring.kind}' for '{ring.key}'",
                      file=sys.stderr)
            if self.cfg.year_line and ring.kind in ("days", "segments", "months"):
                self.svg.add_radial_line(ring.r_inner, ring.r_outer, self.cfg.start_angle,
                                         self.cfg.day_stroke, self.cfg.year_line_width)
            pieces.append((ring, "".join(self.svg.parts[mark:])))
        return pieces

    def render(self) -> str:
        self.svg.open_document()
        self.render_rings()
        self._render_credit()
        self.svg.close_document()
        return self.svg.content()

    def _render_band_ring(self, ring: Ring) -> None:
        if ring.fill and ring.fill != "none":
            self.svg.add_circle_stroke(ring.r_mid, ring.fill, ring.thickness)
        if ring.inner_border_color and ring.inner_border_width:
            # Drawn wholly inside the band rather than straddling its inner
            # edge.  A straddling stroke puts half its width over whatever is
            # inside the ring, and that half survives or not depending on
            # whether a later ring paints over it -- so the border looked twice
            # as thick the moment the ring below it was switched off.  Inside
            # the band it is the same thickness whatever its neighbors do, and
            # the width is simply what you see.
            width = min(ring.inner_border_width, ring.thickness)
            self.svg.add_circle_stroke(ring.r_inner + width / 2.0,
                                       ring.inner_border_color, width)

    def _render_credit(self) -> None:
        """The artwork's title, author, license and source, small, in a corner.

        A license such as CC BY-SA asks for this wherever the picture is shown,
        and a drawing printed or passed on leaves the web page's credit behind.
        """
        mode = (self.cal.settings.artwork_credit or "auto").strip().lower()
        center = next((r for r in self.cal.rings if r.kind == "center" and r.enabled), None)
        if mode == "none" or center is None:
            return
        row = self.cal.center_artwork_row()
        if row is None:
            return
        if mode != "always" and _cell(row, "attribution").lower() not in ("required", "owner", "yes", "true"):
            return
        self.svg.add_credit(credit_lines(row))

    def _render_center(self, ring: Ring) -> None:
        # A ground for the picture (rings.csv's `fill`): white, so a picture
        # that does not fill the circle sits on white in every color scheme.
        if ring.fill and ring.fill != "none":
            self.svg.add_circle_stroke(ring.r_outer / 2.0, ring.fill, ring.r_outer)
        name = self.cal.center_artwork_file()
        if not name:
            return
        own = self.cal.own_artwork_path()
        if own is not None:
            # A picture of the user's own: center_svg_scale sizes it.
            self.svg.add_center_artwork(own, ring.r_outer
                                        * own_art_scale(self.cfg.center_svg_scale), ring.r_outer)
            return
        path = self.cal.resolve_asset(name)
        if path is None:
            print(f"  ! center artwork '{name}' not found; leaving the middle blank",
                  file=sys.stderr)
            return
        # artwork.csv's `scale` insets a picture that would otherwise touch the
        # ring around it; blank is 1, filling the circle's width or height.
        row = self.cal.center_artwork_row()
        try:
            scale = float(_cell(row, "scale")) if row and _cell(row, "scale") else 1.0
        except ValueError:
            scale = 1.0
        self.svg.add_center_artwork(path, ring.r_outer * scale, ring.r_outer)

    def _render_segment_ring(self, ring: Ring) -> None:
        source = ring.source or ("months" if ring.kind == "months" else "")
        segments = self.cal.segments_for_source(source)
        painted: list[tuple[float, float]] = []
        for _item, angle_start, angle_end in segments:
            # A source may nest one span inside another — CHRISTMAS inside the
            # festival half — so that both can be labeled on one ring.  Only
            # the covering span is painted; a second wedge over the same arc
            # would show up the moment the ring is given a stroke.
            if any(a <= angle_start and angle_end <= b for a, b in painted):
                continue
            painted.append((angle_start, angle_end))
            self.svg.add_sector(ring.r_inner, ring.r_outer, angle_start, angle_end,
                                ring.fill, ring.stroke, ring.stroke_width)
        # Where the year begins or ends partway through a week, the rings
        # would stop short and leave a notch; close it in the padding color.
        seam = (self.cfg.year_seam_fill or "auto").strip()
        if seam.lower() == "auto":
            seam = self.cfg.empty_cell_fill
        if seam and seam.lower() != "none":
            for angle_start, angle_end in self.cal.year_seams():
                self.svg.add_sector(ring.r_inner, ring.r_outer, angle_start, angle_end,
                                    seam, ring.stroke, ring.stroke_width)
        if ring.label_mode == "none":
            return
        labeled = segments
        if source == "months" and self.cfg.month_label_largest_only:
            widest: dict[Any, tuple] = {}
            for item, angle_start, angle_end in segments:
                span = arc_span(angle_start, angle_end)
                if item not in widest or span > widest[item][3]:
                    widest[item] = (item, angle_start, angle_end, span)
            labeled = [(i, a, b) for i, a, b, _s in widest.values()]
        plans = [self._plan_ring_label(ring, self.cal.label_for_segment(source, item),
                                       angle_start, angle_end,
                                       getattr(item, "subtitle", ""),
                                       self._label_scale(item))
                 for item, angle_start, angle_end in labeled]
        self._settle_ring_labels(ring, plans)
        if not self._uniform_ring_labels(ring, plans):
            self._spill_ring_labels(ring, plans)
        for plan in plans:
            self._draw_ring_label(ring, plan)

    @staticmethod
    def _label_scale(item: Any) -> float:
        """A nested label's size against its ring's, or 0.0 for "the subtitle's"."""
        if getattr(item, "scale_is_subtitle", False):
            return 0.0
        return float(getattr(item, "scale", 1.0) or 1.0)

    def _plan_ring_label(self, ring: Ring, text: str, angle_start: float,
                         angle_end: float, subtitle: str = "",
                         scale: float = 1.0) -> "RingLabel":
        """Choose a size for one ring label, against its own arc alone."""
        cfg = self.cfg
        measurer = self.cal.measurer
        style = TextStyle(name=f"ring:{ring.key}", font_family=ring.font_family,
                          font_size=ring.font_size, font_weight=ring.font_weight,
                          min_font_size=cfg.ring_label_min_font_size, max_lines=3,
                          orientation=RADIAL)
        metric = style.metric_family
        span = arc_span(angle_start, angle_end)
        radius = ring.r_mid
        factor = cfg.ring_subtitle_ratio if scale == 0.0 else scale

        def full_width(at_size: float) -> float:
            """The label and its subtitle together, since both share the arc."""
            if not subtitle:
                return measurer.width(text, at_size, metric, ring.font_weight)
            # The subtitle is set in italics at regular weight, so it is
            # measured that way; measuring it as the name would over-book the
            # arc and shrink the pair further than it needs to go.
            return (measurer.width(text + cfg.ring_subtitle_separator, at_size,
                                   metric, ring.font_weight)
                    + measurer.width(subtitle, at_size * cfg.ring_subtitle_ratio,
                                     metric, "normal", "italic"))

        size = ring.font_size * factor
        if ring.label_mode in ("curve", "auto") and cfg.ring_label_autofit:
            budget = math.radians(span) * radius * cfg.ring_label_arc_usage
            while size > cfg.ring_label_min_font_size:
                if full_width(size) <= budget:
                    break
                size -= max(0.25, cfg.autofit_step)
        return RingLabel(text=text, subtitle=subtitle, style=style,
                         angle_start=angle_start, angle_end=angle_end,
                         size=size, width=full_width, metric=metric,
                         full=ring.font_size * factor)

    def _settle_ring_labels(self, ring: Ring, plans: list["RingLabel"]) -> None:
        """Shrink labels that would run into one another on the same ring.

        Segments that sit side by side never collide, because each label is
        already held inside its own arc.  Nested segments are the reason this
        exists: FESTIVAL HALF spans the arcs CHRISTMAS and EASTER divide
        between them, so all three are centered inside the same stretch of ring.
        The narrower span speaks first — it has nowhere else to go — and the
        wider one gives way until it clears, which in an ordinary year costs it
        nothing, because the gap between the two cycle names is far wider than
        the half's own label.
        """
        if len(plans) < 2 or ring.label_mode == "radial":
            return
        cfg = self.cfg
        radius = ring.r_mid
        step = max(0.25, cfg.autofit_step)

        def extent(plan: "RingLabel") -> tuple[float, float]:
            middle = plan.angle_start + arc_span(plan.angle_start, plan.angle_end) / 2.0
            reach = math.degrees(plan.width(plan.size) / 2.0 / radius)
            return middle - reach, middle + reach

        claimed: list[tuple[float, float]] = []
        for plan in sorted(plans, key=lambda p: arc_span(p.angle_start, p.angle_end)):
            while plan.size > cfg.ring_label_min_font_size:
                low, high = extent(plan)
                if not any(low < b and a < high for a, b in claimed):
                    break
                plan.size -= step
            claimed.append(extent(plan))

    def _uniform_ring_labels(self, ring: Ring, plans: list["RingLabel"]) -> bool:
        """One size for every label on the ring (`ring_label_uniform`).

        The largest size, from the ring's own down, at which every label fits:
        along its arc, or past a short arc into the free ring beside it (as
        `_spill_ring_labels` places them), each half its size clear of the
        next.  A sliver of a name the ring shows elsewhere is left unlabeled,
        as there.  False when the ring does not ask for it, or nothing fits
        even at the smallest size, and the labels are sized one by one.
        """
        cfg = self.cfg
        if (ring.key not in str(cfg.ring_label_uniform or "").replace(",", " ").split()
                or not cfg.ring_label_autofit or ring.label_mode not in ("auto", "curve")):
            return False
        live = [p for p in plans if p.text]
        if not live or not ring.font_size:
            return False
        radius = ring.r_mid
        step = max(0.25, cfg.autofit_step)
        smallest = cfg.ring_label_min_font_size
        low = min(p.angle_start for p in plans)
        high = max(p.angle_start + arc_span(p.angle_start, p.angle_end) for p in plans)
        middle = {id(p): p.angle_start + arc_span(p.angle_start, p.angle_end) / 2.0 for p in live}
        factor = {id(p): p.full / ring.font_size for p in live}

        def reach(plan: "RingLabel", size: float) -> float:
            return math.degrees(plan.width(size) / 2.0 / radius)

        def own_arc(plan: "RingLabel", size: float) -> bool:
            budget = math.radians(arc_span(plan.angle_start, plan.angle_end)) * radius * cfg.ring_label_arc_usage
            return plan.width(size) <= budget

        slivers = [p for p in live if not own_arc(p, smallest * factor[id(p)]) and any(
            o is not p and o.text == p.text and own_arc(o, smallest * factor[id(o)]) for o in live)]
        rest = [p for p in live if p not in slivers]

        def attempt(base: float):
            size = {id(p): base * factor[id(p)] for p in rest}
            center: dict[int, float] = {}

            def taken(other: "RingLabel") -> tuple[float, float]:
                s = size[id(other)]
                if id(other) in center or own_arc(other, s):
                    c = center.get(id(other), middle[id(other)])
                    r = reach(other, s)
                    return c - r, c + r
                return other.angle_start, other.angle_start + arc_span(other.angle_start, other.angle_end)

            for plan in sorted(rest, key=lambda p: arc_span(p.angle_start, p.angle_end)):
                mid, s = middle[id(plan)], size[id(plan)]
                left, right = low, high
                for other in rest:
                    if other is plan:
                        continue
                    c, d = taken(other)
                    if d <= mid:
                        left = max(left, d)
                    elif c >= mid:
                        right = min(right, c)
                    else:
                        return None
                r = reach(plan, s)
                pad = math.degrees(s / 2.0 / radius)
                lo, hi = left + pad + r, right - pad - r
                if lo > hi:
                    return None
                at = min(max(mid, lo), hi)
                if abs(at - mid) > r:
                    return None
                center[id(plan)] = at
            return size, center

        base = ring.font_size
        while base >= smallest - 1e-9:
            found = attempt(base)
            if found:
                size, center = found
                for plan in rest:
                    plan.size = size[id(plan)]
                    plan.center = center[id(plan)]
                    plan.spill = (not own_arc(plan, plan.size)
                                  or abs(plan.center - middle[id(plan)]) > 1e-9)
                for plan in slivers:
                    plan.hidden = True
                return True
            base -= step
        return False

    def _spill_ring_labels(self, ring: Ring, plans: list["RingLabel"]) -> None:
        """Give a label shrunk by a short arc the free ring on either side.

        A short season between long ones (the Apostles' Fast between the
        weeks after Pentecost) has room beside it: its neighbors' labels sit
        in the middle of their own long arcs.  The shortest arcs go first.  A
        label takes the free stretch of ring around its arc's middle (up to the
        next label, half its size clear of it, and never past the year's start
        or end), keeps its arc's middle under it, sits as near centered on its
        arc as that allows, and grows back toward its ring's size, or from a
        turn across the ring to a curve along it.
        """
        cfg = self.cfg
        if (not cfg.ring_label_spill or not cfg.ring_label_autofit or not plans
                or ring.label_mode not in ("auto", "curve")):
            return
        radius = ring.r_mid
        step = max(0.25, cfg.autofit_step)
        low = min(p.angle_start for p in plans)
        high = max(p.angle_start + arc_span(p.angle_start, p.angle_end) for p in plans)
        middle = {id(p): p.angle_start + arc_span(p.angle_start, p.angle_end) / 2.0 for p in plans}
        center: dict[int, float] = {}

        def reach(plan: "RingLabel", size: float) -> float:
            return math.degrees(plan.width(size) / 2.0 / radius)

        def own_arc(plan: "RingLabel", size: float) -> bool:
            budget = math.radians(arc_span(plan.angle_start, plan.angle_end)) * radius * cfg.ring_label_arc_usage
            return plan.width(size) <= budget

        def taken(other: "RingLabel") -> tuple[float, float]:
            if other.spill or own_arc(other, other.size):
                c = center.get(id(other), middle[id(other)])
                r = reach(other, other.size)
                return c - r, c + r
            return other.angle_start, other.angle_start + arc_span(other.angle_start, other.angle_end)

        def place(plan: "RingLabel", size: float):
            """Where the label goes at this size, or None if it does not fit."""
            mid = middle[id(plan)]
            left, right = low, high
            for other in plans:
                if other is plan or not other.text:
                    continue
                c, d = taken(other)
                if d <= mid:
                    left = max(left, d)
                elif c >= mid:
                    right = min(right, c)
                else:
                    return None           # another label already covers this arc's middle
            r = reach(plan, size)
            pad = math.degrees(size / 2.0 / radius)
            lo, hi = left + pad + r, right - pad - r
            if lo > hi:
                return None
            at = min(max(mid, lo), hi)
            return at if abs(at - mid) <= r else None

        for plan in sorted(plans, key=lambda p: arc_span(p.angle_start, p.angle_end)):
            if not plan.text or plan.size >= plan.full:
                continue
            at = place(plan, plan.size)
            if at is None:
                continue                  # no room: it stays as it was
            size = plan.size
            while size + step <= plan.full + 1e-9:
                nxt = place(plan, size + step)
                if nxt is None:
                    break
                size, at = size + step, nxt
            if size > plan.size or not own_arc(plan, plan.size):
                plan.size = size
                plan.spill = True
                plan.center = at
                center[id(plan)] = at
        # A sliver that could only turn across the ring, of a name the ring
        # reads elsewhere (the one Sunday "After Pentecost" before the
        # Apostles' Fast), is left unlabeled rather than crowd its neighbors.
        for plan in plans:
            if plan.text and not plan.spill and not own_arc(plan, plan.size) and any(
                    other is not plan and other.text == plan.text
                    and (other.spill or own_arc(other, other.size)) for other in plans):
                plan.hidden = True

    def _draw_ring_label(self, ring: Ring, plan: "RingLabel") -> None:
        """Curve the label along the ring; turn it across the ring if the arc is too short."""
        if not plan.text or plan.hidden:
            return
        cfg = self.cfg
        style = plan.style
        family = style.resolved_family(cfg)
        span = arc_span(plan.angle_start, plan.angle_end)
        radius = ring.r_mid
        budget = math.radians(span) * radius * cfg.ring_label_arc_usage
        fits = plan.width(plan.size) <= budget

        if plan.spill:
            # Past its own arc: a path as long as the label, where it was placed.
            reach = math.degrees(plan.width(plan.size) / 2.0 / radius) / cfg.ring_label_arc_usage
            self.svg.add_curved_label(plan.text, plan.center - reach, plan.center + reach,
                                      radius, plan.size, family, ring.font_weight,
                                      ring.text_color, plan.metric, plan.subtitle)
            return
        if ring.label_mode == "curve" or (fits and ring.label_mode != "radial"):
            self.svg.add_curved_label(plan.text, plan.angle_start, plan.angle_end,
                                      radius, plan.size, family, ring.font_weight,
                                      ring.text_color, plan.metric, plan.subtitle)
            if not fits:
                self.cal.warn(None, f"ring:{ring.key}",
                              f"'{plan.text}' overflows its arc even at {plan.size:g}pt")
            return

        wedge = Wedge(ring.r_inner, ring.r_outer, plan.angle_start, plan.angle_end)
        fitted = self.cal.fitter.fit([plan.text], style, wedge, orientation=RADIAL)
        if fitted.overflow and cfg.ring_label_hide_if_unfit:
            self.cal.warn(None, f"ring:{ring.key}", f"'{plan.text}' dropped: no room")
            return
        if fitted.overflow:
            self.cal.warn(None, f"ring:{ring.key}",
                          f"'{plan.text}' turned radial and still tight at {fitted.size:g}pt")
        self.svg.add_fitted_text(fitted, style, wedge, ring.text_color)

    # -- week ring -----------------------------------------------------------

    def _render_week_ring(self, ring: Ring) -> None:
        bands = self.cfg.day_bands
        band_height = (ring.r_outer - ring.r_inner) / bands
        for week_index, week in enumerate(self.cal.weeks):
            angle_start = self.cfg.start_angle + week_index * self.cal.angle_per_week
            angle_end = angle_start + self.cal.angle_per_week
            padded = list(week) + [None] * (bands - len(week))
            for band_index, day in enumerate(padded):
                r_outer = ring.r_outer - band_index * band_height
                wedge = Wedge(r_outer - band_height, r_outer, angle_start, angle_end)
                self._render_day(day, wedge)

    def _number_guard(self, day: date, wedge: Wedge) -> Optional[tuple[float, float]]:
        """Space the day number occupies, as (inner radius, half-width the text must stay inside).

        The number sits in the leading top corner of the cell.  Labels are
        centered, so a label only clears it if half its width stays inside the
        returned limit, or if it sits below the returned radius.
        """
        cfg = self.cfg
        style = self.cal.styles["day_number"]
        size = style.font_size
        text = str(day.day)
        width = self.cal.measurer.width(text, size, style.metric_family,
                                        style.font_weight, style.font_style)
        r_number = wedge.r_outer - cfg.day_number_vertical_ratio * wedge.radial_extent
        r_guard = r_number - 0.15 * size
        # Tangential position of the number's leading edge, measured from the cell center.
        offset_deg = (cfg.day_number_horizontal_ratio - 0.5) * wedge.angle_span
        start = r_number * math.tan(math.radians(offset_deg))
        limit = -(start + width + cfg.day_number_gap)
        return (r_guard, limit)

    def _collides_with_number(self, fitted: FittedText, guard: tuple[float, float],
                              style: TextStyle) -> bool:
        r_guard, limit = guard
        if fitted.orientation == RADIAL:
            # Radial lines run the depth of the cell, so they always reach the
            # number's row; only their sideways spread decides.
            return fitted.block_thickness / 2.0 > limit
        total = fitted.block_thickness
        top_radius = fitted.r_center + (total - fitted.line_height) / 2.0 + fitted.size * 0.4
        if top_radius <= r_guard:
            return False
        half = _widest(fitted.lines[:1], style, fitted.size, style.metric_family,
                       self.cal.measurer) / 2.0
        return half > limit

    def _render_day(self, day: Optional[date], wedge: Wedge) -> None:
        cfg = self.cfg
        cal = self.cal

        if day is None:
            self.svg.add_sector(wedge.r_inner, wedge.r_outer, wedge.angle_start,
                                wedge.angle_end, cfg.empty_cell_fill,
                                cfg.empty_cell_stroke, cfg.day_stroke_width)
            return

        color = cal.color_for(day)
        bottom = cal.bottom_color_for(day)
        if bottom is not None and bottom.fill == color.fill:
            # Both halves the same color: splitting would only draw a line
            # across an otherwise plain cell.
            bottom = None

        # The labels are settled before the cell is painted, because where the
        # color breaks depends on how much each of them has to say.
        titles = cal.titles.get(day, [])
        feasts = cal.feasts.get(day, [])

        if cfg.deduplicate_day_labels and titles and feasts:
            # A principal day and a commemoration can name the same thing — when
            # 31 October falls on a Sunday, Reformation Day is both.  Colors are
            # already settled above, so dropping the repeat only affects text.
            spoken = {" ".join(e.text.lower().split()) for e in titles}
            kept = [e for e in feasts
                    if " ".join(e.text.lower().split()) not in spoken]
            for dropped in [e for e in feasts if e not in kept]:
                cal.warn(day, "duplicate",
                         f"'{dropped.text}' also appears as the day's title; "
                         f"the commemoration was not drawn")
            feasts = kept

        # A day with icons keeps a strip along its inner edge for them, and the
        # labels are fitted in what is left above it.
        icons = cal.icons.get(day, [])
        tw = wedge
        if icons:
            tw = Wedge(wedge.r_inner + cfg.icon_size + cfg.icon_gap + cfg.cell_padding,
                       wedge.r_outer, wedge.angle_start, wedge.angle_end)

        r_split = (self._color_split(day, tw, titles, feasts)
                   if bottom is not None else wedge.r_mid)

        if bottom is not None:
            self.svg.add_sector(r_split, wedge.r_outer, wedge.angle_start, wedge.angle_end,
                                color.fill, cfg.day_stroke, cfg.day_stroke_width)
            self.svg.add_sector(wedge.r_inner, r_split, wedge.angle_start, wedge.angle_end,
                                bottom.fill, cfg.day_stroke, cfg.day_stroke_width)
        else:
            self.svg.add_sector(wedge.r_inner, wedge.r_outer, wedge.angle_start,
                                wedge.angle_end, color.fill, cfg.day_stroke,
                                cfg.day_stroke_width)

        text_color = color.text
        bottom_text_color = bottom.text if bottom is not None else text_color

        has_top_label = self._render_day_number(day, wedge, text_color)
        guard = None if has_top_label else self._number_guard(day, wedge)
        if icons:
            self._draw_icons(icons, wedge, bottom_text_color)

        if not titles and not feasts:
            return

        # Space available to the labels once the date line has taken its slice.
        body = tw
        if has_top_label:
            body = Wedge(tw.r_inner, wedge.r_outer - self._top_label_room(day, wedge),
                         wedge.angle_start, wedge.angle_end)
        elif guard is not None and titles and feasts:
            # Two labels have to share the cell, so keep both out of the date's row.
            body = Wedge(tw.r_inner, min(wedge.r_outer, guard[0]),
                         wedge.angle_start, wedge.angle_end)

        if titles and feasts:
            if bottom is not None:
                top_box = Wedge(max(r_split, body.r_inner), body.r_outer,
                                wedge.angle_start, wedge.angle_end)
                bottom_box = Wedge(tw.r_inner, min(r_split, body.r_outer),
                                   wedge.angle_start, wedge.angle_end)
            else:
                share = self._split_share(day, titles, feasts)
                cut = body.r_outer - share * body.radial_extent
                top_box = Wedge(cut, body.r_outer, wedge.angle_start, wedge.angle_end)
                bottom_box = Wedge(body.r_inner, cut, wedge.angle_start, wedge.angle_end)
            self._draw_entries(day, titles, top_box, text_color, is_title=True, guard=guard)
            self._draw_entries(day, feasts, bottom_box, bottom_text_color, is_title=False)
        elif titles and bottom is not None and self._spans_two_days(day, color, bottom) \
                and self._draw_title_halves(
                day, titles, body, r_split, text_color, bottom_text_color, guard):
            # The day's own name alone, on a day of two colors (Christmas Eve,
            # Holy Saturday: a late service already in the next season's): its
            # first words on the upper color, the rest on the lower.
            pass
        elif titles and bottom is not None and self._spans_two_days(day, color, bottom):
            # One word on a day of two colors: centered on the whole cell, each
            # part of it in the text color of the color behind it.
            start = len(self.svg.parts)
            self._draw_entries(day, titles, body, text_color, is_title=True, guard=guard)
            self.svg.split_colors(start, wedge.r_inner, r_split, wedge.r_outer,
                                  wedge.angle_start, wedge.angle_end,
                                  text_color, bottom_text_color)
        elif titles:
            # The name on the color of its own occasion, the upper part.
            box = body
            if bottom is not None:
                box = Wedge(max(r_split, body.r_inner), body.r_outer,
                            wedge.angle_start, wedge.angle_end)
            self._draw_entries(day, titles, box, text_color, is_title=True, guard=guard)
        else:
            # A commemoration alone sits on the color it brings, the lower part.
            box = body
            if bottom is not None:
                box = Wedge(body.r_inner, min(r_split, body.r_outer),
                            wedge.angle_start, wedge.angle_end)
            self._draw_entries(day, feasts, box, bottom_text_color, is_title=False, guard=guard)

    def _spans_two_days(self, day: date, color: LiturgicalColor,
                        bottom: LiturgicalColor) -> bool:
        """Whether a day's two colors are both its own: the day before's above
        and the day after's below, as on Christmas Eve and Holy Saturday, whose
        late services already belong to the feast.  Reformation Day observed,
        red over the Sunday's green, is the occasion's color over the season's."""
        if not hasattr(self, "_day_index"):
            self._day_index = {d: i for i, d in enumerate(self.cal.days)}
        i = self._day_index.get(day)
        days = self.cal.days
        if i is None or i == 0 or i + 1 >= len(days):
            return False
        return (self.cal.color_for(days[i - 1]).fill == color.fill
                and self.cal.color_for(days[i + 1]).fill == bottom.fill)

    def _draw_title_halves(self, day: date, titles: list[DayEntry], body: Wedge,
                           r_split: float, top_fill: str, bottom_fill: str,
                           guard: Optional[tuple[float, float]]) -> bool:
        """A day's name split over the two colors of its cell: the first words
        above the break, the rest below, at one size ("Christmas" / "Eve",
        "Holy" / "Saturday").  False when the name is a single word."""
        lines = [p for p in titles[0].text.split("\n") if p.strip()]
        if len(titles) > 1:
            # Two names (Advent 4 on Christmas Eve): one on each color.
            firsts, seconds = titles[:1], titles[1:]
            words = []
        elif len(lines) > 1:
            # A name already in lines: the first above, the rest below.
            firsts = [replace(titles[0], text=lines[0])]
            seconds = [replace(titles[0], text="\n".join(lines[1:]))]
            words = []
        else:
            words = " ".join(titles[0].text.split()).split()
            if len(words) < 2:
                return False
        # A note in parentheses, "(observed)", goes below; otherwise the break
        # that keeps the two lines nearest the same length.
        if words:
            k = next((i for i in range(1, len(words)) if words[i].startswith("(")), None)
            if k is None:
                k = min(range(1, len(words)),
                        key=lambda i: (max(len(" ".join(words[:i])), len(" ".join(words[i:]))), i))
            firsts = [replace(titles[0], text=" ".join(words[:k]))]
            seconds = [replace(titles[0], text=" ".join(words[k:]))]
        # The upper name stays out of the day number's row.
        top_outer = body.r_outer if guard is None else min(body.r_outer, guard[0])
        top_box = Wedge(max(r_split, body.r_inner), top_outer, body.angle_start, body.angle_end)
        foot_box = Wedge(body.r_inner, min(r_split, body.r_outer), body.angle_start, body.angle_end)
        if top_box.radial_extent <= 0 or foot_box.radial_extent <= 0:
            return False
        style = self._style_for(day, titles[0], is_title=True)
        size = min(self._fit_entries(firsts, style, top_box)[0].size,
                   self._fit_entries(seconds, style, foot_box)[0].size)
        self._draw_entries(day, [replace(e, font_size_override=size) for e in firsts], top_box,
                           top_fill, is_title=True, guard=guard)
        self._draw_entries(day, [replace(e, font_size_override=size) for e in seconds], foot_box,
                           bottom_fill, is_title=True)
        return True

    def _draw_icons(self, keys: list[str], wedge: Wedge, fill: str) -> None:
        """A day's icons, side by side and centered along the cell's inner edge.

        Each is drawn upright to the cell, as its text is, in the color the
        text on that part of the cell takes.  An icon icons.csv does not know
        is left out.
        """
        cfg = self.cfg
        known = [self.cal.icon_defs[k] for k in keys if k in self.cal.icon_defs]
        if not known:
            return
        size = cfg.icon_size
        radius = wedge.r_inner + cfg.cell_padding + size / 2.0
        total = len(known) * size + (len(known) - 1) * cfg.icon_gap
        for index, icon in enumerate(known):
            offset = -total / 2.0 + size / 2.0 + index * (size + cfg.icon_gap)
            # Written out rather than math.degrees, so the browser's arithmetic
            # matches step for step.
            angle = wedge.angle_mid + offset / radius * 180.0 / math.pi
            x, y = polar_to_cartesian(cfg.cx, cfg.cy, radius, angle)
            self.svg.add_icon(icon, x, y, wedge.angle_mid + 90.0, size, fill)

    def _split_share(self, day: date, titles: list[DayEntry],
                     feasts: list[DayEntry]) -> float:
        """How much of the cell the upper label gets, based on how much text each has."""
        cfg = self.cfg
        title_style = self._style_for(day, titles[0], is_title=True)
        feast_style = self._style_for(day, feasts[0], is_title=False)
        title_mass = sum(len(e.text) for e in titles) * title_style.font_size
        feast_mass = sum(len(e.text) for e in feasts) * feast_style.font_size
        total = title_mass + feast_mass
        if total <= 0:
            return 0.5
        return min(cfg.split_share_max, max(cfg.split_share_min, title_mass / total))

    def _style_for(self, day: date, entry: DayEntry, is_title: bool) -> TextStyle:
        styles = self.cal.styles
        if entry.style_override and entry.style_override in styles:
            return styles[entry.style_override]
        if not is_title:
            return styles["feast"]
        return styles["sunday_title" if day.weekday() == self.cfg.week_starts_on
                      else "weekday_title"]

    def _color_split(self, day: date, wedge: Wedge, titles: list[DayEntry],
                     feasts: list[DayEntry]) -> float:
        """Where the color changes in a cell whose commemoration recolors the foot.

        Half and half wherever that works, because a ring of cells all breaking
        at the same radius reads as a pattern and one breaking at a different
        radius each time reads as a mistake.  It stops working when the upper
        half has far more to say than the lower: Advent 1 on St. Andrew carries
        an opening date line and a Sunday title with its Latin name over a
        commemoration of two words, and half the cell is nothing like enough
        for the one while being twice what the other needs.

        So the two are fitted at a few positions and the line goes where the
        worse-off label comes closest to the size its style asks for -- but
        only if that is `color_split_gain` better than the middle manages.
        Nearly every split cell gains a little from a nudge, and taking every
        one of those would leave the wheel with no two breaks alike for the
        sake of a point of type; the threshold is what keeps the moves to the
        handful of cells that are genuinely squeezed.  `color_split_max` is as
        far as the line can go.
        """
        cfg = self.cfg
        middle = wedge.r_mid
        if not titles or not feasts or wedge.radial_extent <= 0:
            return middle

        body_outer = wedge.r_outer
        if self._has_top_label(day):
            body_outer -= self._top_label_room(day, wedge)
        else:
            guard = self._number_guard(day, wedge)
            if guard is not None:
                body_outer = min(body_outer, guard[0])
        if body_outer <= wedge.r_inner:
            return middle

        title_style = self._style_for(day, titles[0], is_title=True)
        feast_style = self._style_for(day, feasts[0], is_title=False)

        def share_of(radius: float) -> float:
            """How well both labels do with the break at this radius, worse one first."""
            top = Wedge(max(radius, wedge.r_inner), body_outer,
                        wedge.angle_start, wedge.angle_end)
            foot = Wedge(wedge.r_inner, min(radius, body_outer),
                         wedge.angle_start, wedge.angle_end)
            if top.radial_extent <= 0 or foot.radial_extent <= 0:
                return -1.0
            scores = []
            for entries, style, box in ((titles, title_style, top),
                                        (feasts, feast_style, foot)):
                fitted, _ = self._fit_entries(entries, style, box)
                scores.append(0.0 if fitted.overflow
                              else min(1.0, fitted.size / style.font_size))
            return min(scores)

        # Every candidate is judged against the middle, not against the one
        # before it, so a run of small improvements cannot creep past the
        # threshold a step at a time.
        centered = share_of(middle)
        best, best_score = middle, centered
        step = 0.05
        share = 0.5 + step
        while share <= cfg.color_split_max + 1e-9:
            radius = wedge.r_outer - share * wedge.radial_extent
            value = share_of(radius)
            if value >= centered + cfg.color_split_gain and value > best_score + 1e-9:
                best, best_score = radius, value
            share += step
        return best

    def _fit_entries(self, entries: list[DayEntry], style: TextStyle, box: Wedge):
        """Fit a cell's labels, and say which way the line breaks fell out.

        A line break written into a title is a preference, not a command.  The
        Latin names read better on a line of their own, but a crowded cell is
        better served by letting them flow on with the rest, so both are fitted
        and the break is kept only when it costs nothing.
        """
        pinned = next((e.font_size_override for e in entries
                       if e.font_size_override is not None), None)
        max_chars = next((e.max_chars_override for e in entries
                          if e.max_chars_override is not None), None)
        apart = [part for e in entries for part in e.text.split("\n") if part]
        flowed = [" ".join(e.text.split()) for e in entries]
        paragraphs = apart
        fitted = self.cal.fitter.fit(apart, style, box,
                                     pinned_size=pinned, max_chars=max_chars)
        if apart != flowed:
            together = self.cal.fitter.fit(flowed, style, box,
                                           pinned_size=pinned, max_chars=max_chars)
            if ((fitted.overflow and not together.overflow)
                    or together.size > fitted.size):
                fitted, paragraphs = together, flowed
        return fitted, paragraphs

    def _draw_entries(self, day: date, entries: list[DayEntry], box: Wedge,
                      fill: str, is_title: bool,
                      guard: Optional[tuple[float, float]] = None) -> None:
        if box.radial_extent <= 0:
            return
        style = self._style_for(day, entries[0], is_title=is_title)
        pinned = next((e.font_size_override for e in entries
                       if e.font_size_override is not None), None)
        max_chars = next((e.max_chars_override for e in entries
                          if e.max_chars_override is not None), None)
        shift = _plain_sum(e.vertical_offset for e in entries)
        fitted, paragraphs = self._fit_entries(entries, style, box)
        if guard is not None and self._collides_with_number(fitted, guard, style):
            # Drop the label clear of the day number and fit again in what is left.
            clear = Wedge(box.r_inner, min(box.r_outer, guard[0]),
                          box.angle_start, box.angle_end)
            if clear.radial_extent > 0:
                retry = self.cal.fitter.fit(paragraphs, style, clear,
                                            pinned_size=pinned, max_chars=max_chars)
                if not (retry.overflow and not fitted.overflow):
                    fitted, box = retry, clear
        if fitted.overflow:
            self.cal.warn(day, "title" if is_title else "feast",
                          f"'{' / '.join(paragraphs)}' does not fit "
                          f"(placed at {fitted.size:g}pt, {len(fitted.lines)} lines)")
        elif fitted.size < self.cfg.warn_below_font_size:
            self.cal.warn(day, "title" if is_title else "feast",
                          f"'{' / '.join(paragraphs)}' shrunk to {fitted.size:g}pt")
        self.svg.add_fitted_text(fitted, style, box, fill, radial_shift=shift)

    # -- the date line in each cell ------------------------------------------

    def _top_label_room(self, day: date, wedge: Wedge) -> float:
        """How deep a slice the date line at the top of a cell really needs.

        `top_label_reserve` is a share of the band, which is a fair proxy while
        the label has the whole cell to itself.  It stops being one as soon as
        something else has taken part of the cell: a day whose commemoration
        recolors the lower half leaves its title only the strip between the
        color line and this reserve, and a flat third of the band can be most
        of that strip.  Advent 1 falling on St. Andrew is the case that shows
        it -- the title had eleven units to work with and came out at 5.2pt.

        So the reserve is measured instead: where the line is drawn, plus half
        its own height and a padding.  `top_label_reserve` stays as the ceiling,
        so this only ever hands space back, never takes it.
        """
        cfg = self.cfg
        cal = self.cal
        band = wedge.radial_extent
        is_first = day == cal.settings.church_year_start
        style = cal.styles["first_day_label" if is_first else "month_day_label"]
        size = style.font_size
        if not is_first:
            size = cal.month_overrides["font_size"].get(day.month) or size
        drop = (cal.month_overrides["first_day_vertical"] if is_first
                else cal.month_overrides["vertical"].get(day.month, 0.0))
        if is_first:
            # The year's first day may take a second line ("September 11," /
            # "2026"); then the cell gives it the room, ceiling or not.
            r_label = wedge.r_outer - cfg.day_number_vertical_ratio * band - drop
            lines, fit = self._date_label_fit(self._first_day_text(day), style, wedge, r_label, None)
            if len(lines) > 1:
                return (cfg.day_number_vertical_ratio * band + drop
                        + (len(lines) - 1) * fit * DATE_LINE_HEIGHT + fit / 2.0 + cfg.cell_padding)
        needed = cfg.day_number_vertical_ratio * band + drop + size / 2.0 + cfg.cell_padding
        return min(cfg.top_label_reserve * band, max(0.0, needed))

    def _has_top_label(self, day: date) -> bool:
        """Whether this cell's date runs as a line across the top of it.

        The first day of the year and the first of each month do; every other
        day gets a bare number in the corner.  The cell has to know before it
        is painted, because where the color breaks depends on what room is
        left underneath the line.
        """
        return day == self.cal.settings.church_year_start or day.day == 1

    def _render_day_number(self, day: date, wedge: Wedge, fill: str) -> bool:
        """Draw the day number.  Returns True if it took the full width of the cell."""
        cfg = self.cfg
        cal = self.cal
        band_height = wedge.radial_extent
        r_label = wedge.r_outer - cfg.day_number_vertical_ratio * band_height
        is_first_day = day == cal.settings.church_year_start

        if is_first_day:
            style = cal.styles["first_day_label"]
            r_label -= cal.month_overrides["first_day_vertical"]
            self._centered_date_label(self._first_day_text(day), style, wedge, r_label, fill, None)
            return True

        if day.day == 1:
            style = cal.styles["month_day_label"]
            r_label -= cal.month_overrides["vertical"].get(day.month, 0.0)
            angle = wedge.angle_mid + cal.month_overrides["horizontal"].get(day.month, 0.0)
            text = cal.language.day_text(day.month, day.day)
            self._centered_date_label(text, style, wedge, r_label, fill,
                                      cal.month_overrides["font_size"].get(day.month),
                                      angle_override=angle)
            return True

        style = cal.styles["day_number"]
        angle = wedge.angle_start + cfg.day_number_horizontal_ratio * wedge.angle_span
        x, y = polar_to_cartesian(cfg.cx, cfg.cy, r_label, angle)
        self.svg.add_anchored_text(str(day.day), x, y, wedge.angle_mid + 90.0,
                                   style, style.font_size, fill, anchor="start")
        return False

    def _first_day_text(self, day: date) -> str:
        """The year's first day in the church's language, | where it may break."""
        return self.cal.language.full_text(day.month, day.day, str(day.year))

    def _date_label_fit(self, text: str, style: TextStyle, wedge: Wedge, radius: float,
                        pinned: Optional[float]) -> tuple[list[str], float]:
        """The lines and size of a 'January 1' style label: one line, shrunk
        if the wedge is too narrow for it; one that does not fit even at the
        style's smallest size breaks where its | marks onto a second line
        ("September 11," / "2026"), each line fitted to the width at its own
        radius (church_year.js: dateLabelFit)."""
        cfg = self.cfg
        whole = text.replace("|", " ")
        if pinned is not None or not cfg.autofit:
            return [whole], (pinned if pinned is not None else style.font_size)

        def fits(lines: list[str], size: float) -> bool:
            for i, line in enumerate(lines):
                r = radius - i * size * DATE_LINE_HEIGHT
                room = wedge.chord_at(r) * cfg.text_fill_ratio - 2 * cfg.cell_padding
                if self.cal.measurer.width(line, size, style.metric_family, style.font_weight,
                                           style.font_style) > room:
                    return False
            return True
        candidates = [[whole]]
        if "|" in text:
            head, tail = text.rsplit("|", 1)
            candidates.append([head.replace("|", " ").strip(), tail.strip()])
        for lines in candidates:
            size = style.font_size
            while size > style.min_font_size and not fits(lines, size):
                size -= max(0.05, cfg.autofit_step)
            if fits(lines, size):
                return lines, size
        return lines, size

    def _centered_date_label(self, text: str, style: TextStyle, wedge: Wedge,
                             radius: float, fill: str, pinned: Optional[float],
                             angle_override: Optional[float] = None) -> None:
        """A 'January 1' style label (_date_label_fit), its lines centered in
        the cell, the first at `radius` and the next below it."""
        cfg = self.cfg
        lines, size = self._date_label_fit(text, style, wedge, radius, pinned)
        angle = wedge.angle_mid if angle_override is None else angle_override
        for i, line in enumerate(lines):
            x, y = polar_to_cartesian(cfg.cx, cfg.cy, radius - i * size * DATE_LINE_HEIGHT, angle)
            self.svg.add_anchored_text(line, x, y, wedge.angle_mid + 90.0, style, size, fill)


# ============================================================================
# ENTRY POINT
# ============================================================================

def use_utf8_output() -> None:
    """Keep the ✓ and ✗ in our messages from crashing the run.

    Those characters cannot be encoded by a C/POSIX locale or a legacy Windows
    code page, and Python raises UnicodeEncodeError rather than printing —
    which turns a successful run into a traceback the moment output is
    redirected to a file, as it is under cron or in a container.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:      # not a reconfigurable stream; nothing to do
            pass


def resolve_output(given: Optional[str], configured: str) -> Path:
    """Work out where the SVG goes.

    `--out` may be a file (`images/2026.svg`) or a folder to drop the
    configured name into (`images`, `images/`, `.\\images\\`).  Path() strips
    trailing separators, so the raw string is what says which was meant.
    """
    default = Path(configured)
    if not given:
        return default
    target = Path(given)
    is_folder = (target.is_dir()
                 or given.endswith(("/", "\\"))
                 or target.suffix == "")
    return target / default.name if is_folder else target


def print_report(calendar: Calendar) -> None:
    """The labels that did not fit, then, as a note, the names a day already
    carried in its title (drawn once on purpose, not a problem)."""
    order = lambda w: (w.day or date.min, w.where)
    tight = sorted((w for w in calendar.warnings if w.where != "duplicate"), key=order)
    repeats = sorted((w for w in calendar.warnings if w.where == "duplicate"), key=order)
    if tight:
        print(f"  Fit report: {len(tight)} item(s) needed attention")
    else:
        print("  Fit report: every label fits its cell.")
    for item in tight:
        stamp = item.day.isoformat() if item.day else "     ring "
        print(f"    {stamp}  {item.where:<8}  {item.message}")
    if repeats:
        print(f"  Drawn once (the day's title already names it): {len(repeats)}")
        for item in repeats:
            print(f"    {item.day.isoformat()}  {item.message.split(' also appears')[0]}")


def apply_feasts(calendar, wanted):
    """Let --feasts override the config, once the calendar has been built."""
    if wanted:
        calendar.settings._values["feast_detail"] = wanted
        calendar.reload_feasts()
    return calendar


MID_TEXT = ("as-set", "dark", "dark-reds", "light")
ART_CREDIT = ("always", "auto", "none")


def _parse_args(argv: Optional[Sequence[str]]) -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    import listing as out
    p = out.parser(__doc__.split("\n\n\n")[0])
    out.add_church(p)
    p.add_argument("--from", dest="start", metavar="YEAR",
                   help="first church year to draw (YYYY), one wheel each")
    p.add_argument("--to", dest="end", metavar="YEAR",
                   help="last church year to draw (YYYY; default: --from's)")
    p.add_argument("-o", "--output", "--out", dest="out", default=None, metavar="PATH",
                   help="SVG file to write, or a folder to write it into: one that exists, "
                        "or any path ending in / or without a suffix (default: config.csv's "
                        "output_filename; for a church named, KEY_YYYY-YY_calendar.svg)")
    p.add_argument("--list", action="store_true", help="list the churches and stop")
    out.add_year_options(p)
    out.add_feasts(p, FEAST_DETAIL)
    p.add_argument("--art", default=None, metavar="KEY|FILE",
                   help="the picture in the middle: auto (the church's own), a key from "
                        "data/artwork.csv, none, or a picture of your own (.svg, .png, .jpg, "
                        ".jpeg, .gif or .webp; found from the current folder, then the "
                        "project folder) (default: config.csv's center_svg)")
    p.add_argument("--art-date", dest="art_date", default="", metavar="DATE",
                   help="draw the picture of this day's season in the middle (2026-12-25: the "
                        "manger), as the page's Artwork: By season does for the day chosen; "
                        "data/season_art.csv says which season shows which picture, and a day "
                        "in a season without one keeps the church's own (default: the church's own)")
    p.add_argument("--art-credit", default=None, metavar="TEXT",
                   help="your own picture's credit, drawn in the lower-left corner "
                        "(default: config.csv's center_svg_credit, or none)")
    p.add_argument("--art-scale", type=float, default=None, metavar="N",
                   help="your own picture's size in the circle: 1 fills it (default: "
                        "config.csv's center_svg_scale, or 1)")
    p.add_argument("--credit", choices=ART_CREDIT, default=None,
                   help="the artwork's credit in the corner: always, auto (when its "
                        "license asks for it, or a credit of your own is given) or none "
                        "(default: config.csv's artwork_credit)")
    p.add_argument("--mid-text", choices=MID_TEXT, default=None,
                   help="text on mid-tone colors, which read with black or white: as-set "
                        "(colors.csv's choice), dark (black), dark-reds (black on the reds "
                        "only) or light (white) (default: config.csv's mid_text)")
    p.add_argument("--year-line", dest="year_line", action="store_true", default=None,
                   help="a thicker line where the year ends and begins")
    p.add_argument("--no-year-line", dest="year_line", action="store_false",
                   help="without it (default: config.csv's year_line)")
    p.add_argument("--color-changes", dest="color_changes", default="", metavar="CHANGES",
                   help="colors repainted for this drawing, as the page's Colors menu does and "
                        "a link's colors= writes them: PURPLE-7a1f7a (every church), "
                        "lutheran:WHITE-fffff0 (one tradition's, which wins), "
                        "lutheran:wels-one-year:RED-c00000 (one church's, which wins again), "
                        "ring.halves-e6c3f7, text.halves-000000, empty-f0f0f0; text on a day "
                        "stays readable (it turns black or white if it would not)")
    p.add_argument("--hide", action="append", default=None, metavar="RING",
                   help="leave out a ring, by its key in data/rings.csv (gold, halves, "
                        "months, seasons ...), as the page's hide= does; repeatable, or "
                        "separated by commas")
    p.add_argument("--png", dest="png", action="store_true", default=None,
                   help="also write a PNG (default: whatever png_output says)")
    p.add_argument("--no-png", dest="png", action="store_false",
                   help="write only the SVG")
    p.add_argument("--png-width", type=int, default=None,
                   help="PNG width in pixels (default: png_width from config.csv)")
    p.add_argument("--png-background", default=None, metavar="COLOR",
                   help="the PNG's background: none (clear) or a color such as white or "
                        "#ffffff, as the page's Download offers (default: png_background "
                        "from config.csv)")
    p.add_argument("--png-renderer", default=None,
                   choices=["auto", "cairosvg", "chrome", "inkscape", "resvg",
                            "rsvg-convert"],
                   help="force one rasterizer (default: png_renderer from config.csv)")
    p.add_argument("--list-renderers", action="store_true",
                   help="show which PNG rasterizers this machine has, and exit")
    p.add_argument("--report", action="store_true",
                   help="list every label that had to shrink, wrap hard, or overflow")
    p.add_argument("--data", default="data", type=Path, metavar="DIR",
                   help="the folder of CSVs (default: ./data). With no church, year or "
                        "year option it is drawn as it stands, hand edits included; "
                        "otherwise it holds the rules the year is worked out from")
    return p, p.parse_args(argv)


def _overrides(p: argparse.ArgumentParser, a: argparse.Namespace,
               data_dir: Path) -> tuple[dict[str, str], list[str]]:
    """The settings the command line lays over config.csv, and the rings to hide."""
    overrides: dict[str, str] = {}
    if a.art is not None:
        name = a.art.strip()
        rows = [r for r in read_rows(data_dir / "artwork.csv", required=False) if _cell(r, "key")]
        keys = sorted(_cell(r, "key").lower() for r in rows)
        files = {_cell(r, "file"): _cell(r, "key").lower() for r in rows}
        if name.lower() in ("auto", "season", "none") or name.lower() in keys:
            # season: the church's own, which --art-date changes for a day's season.
            overrides["center_svg"] = name.lower()
        elif name in files:                 # artwork.csv's own file: that entry
            overrides["center_svg"] = files[name]
        elif is_art_file(name):
            found = resolve_art_file(name)
            if found is None:
                p.error(f"--art {name}: no such file here or in {Path(__file__).resolve().parent}")
            overrides["center_svg"] = str(found)
        else:
            p.error(f"--art {name}: not a picture file (.svg, .png, .jpg, .jpeg, .gif, "
                    f".webp) and not one of: auto, season, none, {', '.join(keys)}")
    if a.art_credit is not None:
        overrides["center_svg_credit"] = a.art_credit
    if a.art_scale is not None:
        if not (a.art_scale > 0 and math.isfinite(a.art_scale)):
            p.error("--art-scale must be above 0")
        overrides["center_svg_scale"] = repr(a.art_scale)
    if a.credit is not None:
        overrides["artwork_credit"] = a.credit
    if a.mid_text is not None:
        overrides["mid_text"] = a.mid_text
    if a.year_line is not None:
        overrides["year_line"] = a.year_line
    hide: list[str] = []
    if a.hide:
        rings = load_rings(data_dir / "rings.csv")
        movable = sorted(r.key for r in rings if r.kind not in ("days", "center"))
        fixed = {r.key for r in rings if r.kind in ("days", "center")}
        for word in (w.strip() for h in a.hide for w in h.split(",")):
            if not word or word.lower() == "none":
                continue
            if word in fixed:
                p.error(f"--hide {word}: the day cells and the center are the drawing "
                        f"itself; choose from {', '.join(movable)} (--art none empties the middle)")
            if word not in movable:
                p.error(f"--hide {word}: no such ring; choose from {', '.join(movable)}")
            hide.append(word)
    return overrides, hide


def _church_years(p: argparse.ArgumentParser, a: argparse.Namespace) -> Optional[tuple]:
    """The church and years asked for, or None to draw --data as it stands."""
    import listing as out
    import traditions as T
    asked = (a.church, a.year, a.start, a.end, a.calendar, a.paschalion,
             a.subcalendar, a.latin)
    if all(v is None for v in asked):
        return None
    defaults = out.config_defaults(a.data)
    key, named = out.church_and_year(p, a, defaults)
    try:
        tradition = T.find_tradition(a.data, key)
    except ValueError as exc:
        raise SystemExit(out.unknown_church(exc, "church_year_image.py"))

    def year_of(text: Optional[str], flag: str) -> Optional[int]:
        if text is None:
            return None
        if not re.fullmatch(r"-?\d{1,6}", text.strip()):
            p.error(f"{flag} takes a year the church year begins in (2025), not '{text}'")
        return int(text)
    lo, hi = year_of(a.start, "--from"), year_of(a.end, "--to")
    if a.year is not None and lo is not None:
        p.error("give the year or --from YEAR, not both")
    first = a.year if a.year is not None else lo if lo is not None else defaults["year"]
    last = hi if hi is not None else first
    if last < first:
        p.error(f"--to {a.end} is before {T.year_label(first)}")
    own = T.tradition_settings(a.data, tradition)
    return (tradition.key, named, first, last,
            a.calendar or own.get("calendar") or defaults["calendar"],
            a.paschalion or defaults["paschalion"],
            out.subcalendars(a, named, defaults),
            T.latin_names_wanted(a.latin, own, defaults["latin_names"]),
            a.feasts or defaults["feast_detail"])


def draw(calendar: Calendar, out_path: Path, args: argparse.Namespace,
         png_filename: str = "") -> None:
    """Draw one calendar to `out_path`, and its PNG if one is wanted."""
    print(f"Drawing {len(calendar.weeks)} weekly wedges "
          f"({calendar.settings.church_year_start} to {calendar.settings.church_year_end}) ...")
    markup = Renderer(calendar).render()
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(markup, encoding="utf-8")
    except OSError as exc:
        hint = ""
        if out_path.is_dir():
            hint = ("  (that is a folder — give a file name inside it, or pass "
                    "the folder with a trailing slash)")
        sys.exit(f"✗ Could not write {out_path}: {exc}{hint}")

    print(f"✓ Wrote {out_path.resolve()}")

    settings = calendar.settings
    want_png = settings.png_output if args.png is None else args.png
    if want_png:
        # A name of its own still goes beside the SVG, wherever --out put that,
        # rather than into whichever folder the command happened to run from.
        png_path = (out_path.parent / png_filename if png_filename
                    else out_path.with_suffix(".png"))
        write_png(markup, png_path, settings,
                  args.png_width or settings.png_width,
                  args.png_background or settings.png_background,
                  args.png_renderer or settings.png_renderer)

    if args.report:
        print_report(calendar)
    elif calendar.warnings:
        tight = sum(1 for w in calendar.warnings if w.where != "duplicate")
        repeats = len(calendar.warnings) - tight
        parts = []
        if tight:
            parts.append(f"{tight} label(s) are tight")
        if repeats:
            parts.append(f"{repeats} repeated name(s) were drawn once")
        print(f"  {'; '.join(parts)} — run with --report for details.")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser, args = _parse_args(argv)
    use_utf8_output()

    if args.list_renderers:
        report_renderers()
        return 0

    if not args.data.is_dir():
        sys.exit(f"✗ Data directory not found: {args.data}")

    if args.list:
        import listing as out
        return out.list_churches(data_dir=args.data)

    overrides, hide = _overrides(parser, args, args.data)
    asked = _church_years(parser, args)

    if asked is None:
        # The folder as it stands, exactly as before there were any options.
        print(f"Loading {args.data}/ ...")
        calendar = apply_feasts(Calendar(args.data, overrides, hide, args.color_changes, args.art_date), args.feasts)
        settings = calendar.settings
        draw(calendar, resolve_output(args.out, settings.output_filename), args,
             settings.png_filename)
        return 0

    # A church or year asked for: worked out from the rules into a scratch
    # folder, exactly as new_year.py writes it, and drawn from there.  config.csv
    # is not touched.  A picture config.csv names by a path relative to --data
    # is pinned first, since the scratch folder is somewhere else.
    import shutil
    import tempfile
    import new_year as ny
    import traditions as T
    key, named, first, last, calendar_name, paschalion, subs, latin, feasts = asked
    if "center_svg" not in overrides:
        configured = (read_config(args.data / "config.csv").get("center_svg") or "").strip()
        if is_art_file(configured):
            found = resolve_art_file(configured, args.data)
            if found is not None:
                overrides["center_svg"] = str(found)
    several = last > first
    if several and args.out and not (Path(args.out).is_dir() or args.out.endswith(("/", "\\"))
                                     or Path(args.out).suffix == ""):
        parser.error("several years are drawn into a folder: give -o a folder, not a file")
    scratch = Path(tempfile.mkdtemp(prefix="church-year-"))
    try:
        for year in range(first, last + 1):
            try:
                cy = ny.ChurchYear(year, key, calendar_name, paschalion, args.data, subs)
            except ValueError as exc:
                sys.exit(f"✗ {exc}")
            primed = (scratch / ".primed").exists()
            print(f"Working out {cy.tradition.label} {cy.label} from {args.data}/ ...")
            ny.write_year(cy, args.data, scratch, latin, feasts, copy_folders=not primed)
            (scratch / ".primed").touch()
            calendar = apply_feasts(Calendar(scratch, overrides, hide, args.color_changes, args.art_date), args.feasts)
            name = (f"{key}_{T.year_label(year)}_calendar.svg" if named
                    else calendar.settings.output_filename)
            draw(calendar, resolve_output(args.out, name), args)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # Piped into head, less or similar and the reader closed early.  Point
        # stdout at the void so the interpreter's final flush stays quiet too.
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        raise SystemExit(0)
