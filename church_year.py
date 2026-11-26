#!/usr/bin/env python3
"""
Build the interactive church year wheel that draws any year in the browser.

The page carries the renderer itself: type a year and the wheel is redrawn on
the spot.
The output is one self-contained HTML file of about 5.5 MB (about 510 KB for
one church), with no server, no network and no year list to keep up to date.

    python church_year.py                         # -> church_year.html
    python church_year.py -o wheel.html
    python church_year.py -o pages/              # into a folder
    python church_year.py --year 2030             # open on a different year
    python church_year.py --fragment              # no <html>/<body>, to put in another page
    python church_year.py --churches lcms-*       # offer only these churches
    python church_year.py --churches Lutheran,episcopal
    python church_year.py --list                  # the keys to choose from
    python church_year.py --footer none           # no lines under the wheel
    python church_year.py --churches lcms-one-year,lcms-three-year --fixed calendar,easter,artwork,reds
    python church_year.py --art my_cross.png      # your own picture, added to the Artwork menu
    python church_year.py --art celtic_cross          # open on this artwork

The drawing in the browser is a port of `church_year_image.py`, so the two can drift
apart.  `python web/verify.py` draws a long run of years both ways and
compares the markup; run it after changing either one.

The tables the browser draws from are frozen into web/data.json.  That file is
rebuilt automatically whenever it is missing or older than the CSVs in ./data,
so editing a CSV is enough; `python web/export_data.py` refreshes it by hand.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
WEB = HERE / "web"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "lib"))

from church_year_image import use_utf8_output, xml_escape  # noqa: E402
import traditions as T  # noqa: E402


def read(name: str) -> str:
    path = WEB / name
    if not path.exists():
        sys.exit(f"✗ {path} not found. The web/ folder holds the browser "
                 f"renderer; keep it beside this script.")
    return path.read_text(encoding="utf-8")


def advent_year_for(day: date, lectionary: str = "lcms-three-year",
                    data_dir: Path = HERE / "data") -> int:
    """The year whose church year contains this date: its Advent year, for most.

    Worked in day numbers, which is what new_year.year_start speaks now that
    the calendar is a choice rather than a given.
    """
    from calendars import GREGORIAN
    from new_year import year_start
    z = GREGORIAN.to_day(day.year, day.month, day.day)
    for candidate in (day.year, day.year - 1):
        try:
            if (year_start(candidate, lectionary, "gregorian", data_dir) <= z
                    < year_start(candidate + 1, lectionary, "gregorian", data_dir)):
                return candidate
        except ValueError:
            break
    return day.year


def bible_versions() -> dict:
    """The page's Bible versions, code -> language, as web/page.js lists them."""
    src = (HERE / "web" / "page.js").read_text(encoding="utf-8")
    block = src[src.index("const BIBLE_VERSIONS = ["):]
    block = block[:block.index("];")]
    return {c: lang for c, lang in re.findall(r"\['([A-Z0-9]+)', '[^']*', '([a-z]+)'\]", block)}


def bible_choice(spec: str) -> list:
    """--bible / page_bibles: version codes, languages (english, de, ...), or own."""
    words = [w.strip() for w in spec.replace(",", " ").split() if w.strip()]
    if not words:
        return []
    known = bible_versions()
    langs = set(known.values()) | {"english"}
    out = []
    for w in words:
        if w.lower() == "own":
            if len(words) > 1:
                sys.exit("✗ page_bibles: 'own' stands alone (each church's own version, no menu)")
            return ["own"]
        if w.upper() in known:
            out.append(w.upper())
        elif w.lower() in langs:
            out.append(w.lower())
        else:
            sys.exit(f"✗ page_bibles: no Bible version or language '{w}'; "
                     f"choose from own, english, {', '.join(sorted(langs - {'english'}))}, {', '.join(known)}")
    return out


def bible_allowed(bibles: list, code: str) -> bool:
    """Whether a page with this Bible menu (bible_choice) offers this version:
    every version, those named and those of the languages named, or none
    (each church's own) (page.js: pageBibleFit)."""
    if not bibles:
        return True
    if bibles == ["own"]:
        return False
    lang = bible_versions().get(code)
    return code in bibles or (lang is not None and lang in {"en" if b == "english" else b for b in bibles})


# Settings a page can leave out (--fixed / page_fixed), keeping each church's own.
FIXABLE = ("calendar", "easter", "artwork", "reds")
# Left out unless asked for (--show / page_show): most readers keep their
# church's own calendar and Easter, and the two menus only invite a wrong one.
HIDDEN_UNLESS_SHOWN = ("calendar", "easter")


def select_churches(data: dict, spec: str) -> dict:
    """Keep only the churches `spec` names: keys (lcms-one-year), tradition
    names (Lutheran), or key prefixes ending in * (lcms-*), separated by
    spaces or commas.  The page then carries only their folders and artwork,
    and hides a menu with nothing to choose."""
    words = [w.strip() for w in spec.replace(",", " ").split() if w.strip()]
    if not words:
        return data
    keep = []
    for w in words:
        lw = w.lower()
        hits = [t for t in data["traditions"]
                if t["key"] == lw
                or (lw.endswith("*") and t["key"].startswith(lw[:-1]))
                or (t.get("tradition") or "").lower() == lw]
        if not hits:
            sys.exit(f"✗ --churches: no church '{w}'. See --list.")
        keep += [t for t in hits if t not in keep]
    keys = {t["key"] for t in keep}
    out = dict(data)
    out["traditions"] = [t for t in data["traditions"] if t["key"] in keys]
    out["profiles"] = {k: v for k, v in data["profiles"].items() if k in keys}
    folders = {t["folder"] for t in out["traditions"]}
    out["folders"] = {k: v for k, v in data["folders"].items() if k in folders}
    arts = {p.get("art") for p in out["profiles"].values()} - {None, ""}
    # A picture of the user's own (center_svg naming a file) stays whatever the churches.
    arts |= {k for k, v in data["artwork"].items() if v.get("own")}
    # The seasons' pictures these churches show with Artwork: By season.
    arts |= {r["art"] for r in data.get("seasonArt", [])
             if r["art"] and (not r["church"] or r["church"] in keys)}
    out["artwork"] = {k: v for k, v in data["artwork"].items() if k in arts}
    out["artworkOrder"] = [k for k in data["artworkOrder"] if k in arts]
    # "auto" (each church's own artwork) stays; a fixed picture that is gone
    # gives way to the first one kept.
    if out.get("defaultArt") not in arts | {"auto", "season", ""}:
        out["defaultArt"] = next(iter(out["artworkOrder"]), "")
    # Only the shared lectionaries the kept churches read (their `readings`
    # setting, in their folder or config.csv).
    variants = {t.get("variant") or "" for t in out["traditions"]}
    names = set(str((data.get("settings") or {}).get("readings") or "").split())
    for f in folders:
        for s in data["folders"][f].get("settings") or []:
            if s.get("setting") != "readings":
                continue
            v = set(str(s.get("variant") or "").split())
            if not v or v & variants:
                names |= set(str(s.get("value") or "").split())
    out["sharedReadings"] = {k: v for k, v in (data.get("sharedReadings") or {}).items() if k in names}
    out["csv"] = kept_layouts(data, out)
    if data["defaultTradition"] not in keys:
        out["defaultTradition"] = out["traditions"][0]["key"]
    return out


def file_owner(data: dict, path: str) -> str:
    """The folder whose file `path` (under data/) is: the longest that holds it;
    readings/NAME for a shared lectionary, blank for the palette."""
    if path.startswith("readings/"):
        return path
    owners = [f for f in data["folders"] if path.startswith(f + "/")]
    return max(owners, key=len) if owners else ""


def kept_layouts(data: dict, out: dict) -> dict:
    """The file layouts (export_data.csv_layouts) of the tables `out` still
    carries whole (church_year.js: keptLayouts): a folder dropped takes its
    files, a lectionary pruned or dropped takes its own."""
    kept = {}
    for path, lay in (data.get("csv") or {}).items():
        owner = file_owner(data, path)
        if owner.startswith("readings/"):
            name = owner[len("readings/"):-len(".csv")]
            old, new = (data.get("sharedReadings") or {}).get(name), (out.get("sharedReadings") or {}).get(name)
            if new is None or len(new["rows"]) != len(old["rows"]):
                continue
        elif owner:
            if owner not in out["folders"]:
                continue
            if path == owner + "/readings.csv" and \
                    len(out["folders"][owner]["readings"]["rows"]) != len(data["folders"][owner]["readings"]["rows"]):
                continue
        kept[path] = lay
    return kept


def prune_readings(data: dict, kinds: list[str], data_dir: Path = HERE / "data") -> dict:
    """--readings: the tables with only the readings of these kinds of set
    that some church on the page has, whatever subcalendar it is drawn with
    (church_year.js: pruneReadings).  A folder's `omit` and `=kind` rows stay;
    a shared lectionary left with nothing goes."""
    from lectionary import READING_CATEGORIES, reading_info, source_readings, _int
    sys.path.insert(0, str(WEB))
    from export_data import pack_rows, unpack_rows
    if all(c in kinds for c in READING_CATEGORIES):
        return data

    def key(file: str, r: dict) -> tuple:
        return (file, r.get("day", "").strip(), _int(r.get("offset")), r.get("title", ""))

    keep = set()
    for t in data["traditions"]:
        tradition = T.find_tradition(data_dir, t["key"])
        subs = [e["key"] for e in data["folders"][t["folder"]].get("subcalendars") or []]
        for chosen in [[]] + [[k] for k in subs]:
            source = T.Source(data_dir, tradition, chosen)
            info = reading_info(source)
            keep |= {key(r.get("_file", ""), r) for r in source_readings(source)
                     if info.category(r) in kinds}
    out = dict(data)
    out["sharedReadings"] = {}
    for name, table in (data.get("sharedReadings") or {}).items():
        rows = [r for r in unpack_rows(table) if key(name, r) in keep]
        if rows:
            out["sharedReadings"][name] = pack_rows(rows)
    out["folders"] = {}
    for f, tables in data["folders"].items():
        rows = [r for r in unpack_rows(tables["readings"])
                if r.get("kind", "") == "omit" or r.get("kind", "").startswith("=")
                or key("", r) in keep]
        out["folders"][f] = dict(tables, readings=pack_rows(rows))
    out["csv"] = kept_layouts(data, out)
    return out


OWN_ART_FIELDS = ("churches", "credit", "author", "license", "license-url", "source", "scale", "attribution")


def own_art_spec(spec: str) -> tuple[str, dict]:
    """--own-art FILE|name=value|...: the picture's file and its fields."""
    parts = [p.strip() for p in spec.split("|")]
    name, fields = parts[0], {}
    for part in parts[1:]:
        if not part:
            continue
        key, eq, value = part.partition("=")
        key = key.strip().lower()
        if not eq or key not in OWN_ART_FIELDS:
            sys.exit(f"✗ --own-art {name}: '{part}' is not one of "
                     + ", ".join(f + "=..." for f in OWN_ART_FIELDS))
        fields[key] = value.strip()
    if not name:
        sys.exit("✗ --own-art needs a picture file")
    return name, fields


def choose_artwork(data: dict, args: argparse.Namespace) -> None:
    """The pictures for the middle of the wheel.  --own-art freezes pictures of
    the user's own into the page (its Artwork menu lists each), each the own
    picture of the churches its churches= names; --drop-art leaves pictures
    the churches have out of the page, a church whose picture is dropped
    keeping none unless one of the user's is its own; --art is the picture
    the page opens on: auto (each church's own), none, a key, or a file
    (added as a picture of the user's own if --own-art did not)."""
    sys.path.insert(0, str(WEB))
    import export_data
    import church_year_image as cy
    churches = {t["key"] for t in data["traditions"]}

    def add(name: str, fields: dict) -> str:
        if not cy.is_art_file(name):
            sys.exit(f"✗ {name}: not a picture file (.svg, .png, .jpg, .jpeg, .gif, .webp)")
        path = cy.resolve_art_file(name)
        if path is None:
            sys.exit(f"✗ {name}: no such file here or in {HERE}")
        scale = fields.get("scale", "")
        if scale:
            try:
                ok = float(scale) > 0
            except ValueError:
                ok = False
            if not ok:
                sys.exit(f"✗ --own-art {name}: scale must be a number above 0")
        attribution = fields.get("attribution", "").lower()
        if attribution not in ("", "required", "optional"):
            sys.exit(f"✗ --own-art {name}: attribution is required or optional")
        try:
            key, entry = export_data.own_artwork(
                path, fields.get("credit", ""), scale, author=fields.get("author", ""),
                license=fields.get("license", ""), license_url=fields.get("license-url", ""),
                source_url=fields.get("source", ""), attribution=attribution)
        except Exception as exc:
            sys.exit(f"✗ {name} could not be read: {exc}")
        data["artwork"][key] = entry
        if key not in data["artworkOrder"]:
            data["artworkOrder"].append(key)
        size = len(entry["body"]) / 1024
        if size > 2048:
            print(f"  ! {path.name} adds {size / 1024:.1f} MB to the page; a smaller "
                  "picture would load faster", file=sys.stderr)
        return key

    assigned = set()
    for spec in args.own_art or []:
        name, fields = own_art_spec(spec)
        key = add(name, fields)
        for c in [w.strip().lower() for w in fields.get("churches", "").replace(",", " ").split()]:
            if c not in churches:
                sys.exit(f"✗ --own-art {name}: no church '{c}' on this page. See --list-churches.")
            profile = data["profiles"][c]
            profile.setdefault("churchArt", profile.get("art", ""))   # its own, should it be given back
            profile["art"] = key
            assigned.add(c)
    for word in (args.drop_art or "").replace(",", " ").split():
        key = word.strip().lower()
        if key not in data["artwork"] or data["artwork"][key].get("own"):
            sys.exit(f"✗ --drop-art: '{word}' is not one of the churches' pictures here: "
                     + ", ".join(k for k in data["artworkOrder"] if not data["artwork"][k].get("own")))
        del data["artwork"][key]
        data["artworkOrder"] = [k for k in data["artworkOrder"] if k != key]
        for c, p in data["profiles"].items():
            if p.get("art") == key and c not in assigned:
                p["art"] = "none"
    if args.art is None:
        if data.get("defaultArt") not in data["artwork"] and data.get("defaultArt") not in ("auto", "season", "none", ""):
            data["defaultArt"] = "auto"
        return
    name = args.art.strip()
    low = name.lower()
    if low in ("auto", "season", "none") or low in data["artwork"]:
        export_data.use_artwork(data, low)
        return
    if cy.is_art_file(name) and "file:" + Path(name).name.lower() in data["artwork"]:
        export_data.use_artwork(data, "file:" + Path(name).name.lower())
        return
    if not cy.is_art_file(name):
        sys.exit(f"✗ --art {name}: not a picture file (.svg, .png, .jpg, .jpeg, .gif, .webp) "
                 f"and not one of: auto, season, none, {', '.join(sorted(data['artworkOrder']))}")
    export_data.use_artwork(data, add(name, {}))


def list_churches(data: dict) -> None:
    for t in sorted(data["traditions"],
                    key=lambda t: (t["tradition"], t["church"], t.get("book", ""),
                                   t.get("series", ""))):
        place = " / ".join(x for x in (t["tradition"], t["church"], t.get("book"),
                                       t.get("series")) if x)
        print(f"  {t['key']:32} {place}")


def build(data: dict, fragment: bool = False, compress: bool = True) -> str:
    # The page retitles its own tab as the reader moves between years; this is
    # the name the file keeps, so it stays put.
    title = "Church Year Wheel"
    width = data["settings"]["width"]
    height = data["settings"]["height"]
    cx, cy = width / 2.0, height / 2.0

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        # The element fills the stage; the viewBox is fitted inside it and
        # centered, so the wheel keeps its shape whatever the window's is.
        f'viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet" '
        f'role="img" '
        f'aria-label="The church year as a wheel">\n'
        f'<g id="zoom">\n'
        f'<g id="rotor">\n<g id="art"></g>\n'
        f'<path id="hiUnder" class="hi-under" d="" />\n'
        f'<path id="hiOver" class="hi-over" d="" />\n'
        f'</g>\n<g id="center"></g>\n</g>\n</svg>\n'
    )

    tables = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    if compress:
        # Packed (gzip, then base64) the tables are about a fifth of the size;
        # the page unpacks them when it opens (page.js).  mtime=0 gives the
        # same bytes for the same tables.
        packed = gzip.compress(tables.encode("utf-8"), compresslevel=9, mtime=0)
        tables = '"' + base64.b64encode(packed).decode("ascii") + '"'
    else:
        # The tables go into a <script>, so a "</" anywhere in them (the center
        # artwork is someone's SVG) must not be able to close it early.
        tables = tables.replace("</", "<\\/")

    body = f"""<style>
{read('style.css')}
.cy-app {{ --ox: {cx}px; --oy: {cy}px; --ar: {width} / {height}; }}
</style>

<div class="cy-app">
<div class="bar">
  <div class="gearcol">
  <details id="settings" class="menu">
    <summary id="gear" title="Settings" aria-label="Settings"><svg viewBox="0 0 24 24" class="icon" aria-hidden="true" focusable="false"><path fill="currentColor" fill-rule="evenodd" d="M8.71 4.05 L10.19 3.59 L10.19 1.15 L13.81 1.15 L13.81 3.59 L15.29 4.05 L16.66 4.78 L18.40 3.05 L20.95 5.60 L19.22 7.34 L19.95 8.71 L20.41 10.19 L22.85 10.19 L22.85 13.81 L20.41 13.81 L19.95 15.29 L19.22 16.66 L20.95 18.40 L18.40 20.95 L16.66 19.22 L15.29 19.95 L13.81 20.41 L13.81 22.85 L10.19 22.85 L10.19 20.41 L8.71 19.95 L7.34 19.22 L5.60 20.95 L3.05 18.40 L4.78 16.66 L4.05 15.29 L3.59 13.81 L1.15 13.81 L1.15 10.19 L3.59 10.19 L4.05 8.71 L4.78 7.34 L3.05 5.60 L5.60 3.05 L7.34 4.78Z M15.2 12a3.2 3.2 0 1 0 -6.4 0a3.2 3.2 0 1 0 6.4 0Z"/></svg></summary>
    <div class="panel">
      <div class="viewrow"><span id="viewLabel">Settings</span><span class="seg" role="group" aria-labelledby="viewLabel"><button type="button" data-view="simple" aria-pressed="true" title="The settings most often changed: the year, the church, the feasts, the Bible and how the readings are shown">Simple</button><button type="button" data-view="all" aria-pressed="false" title="Every setting: the calendar, the kinds of reading, the searches, the artwork, the rings and colors, and making a page or editing the data">All</button></span></div>
      <label id="uiRow" title="The language of the page's buttons, menus and settings. The calendar's names, dates and readings stay in the church's language.">Language
        <select id="uiLanguage"></select></label>
      <label title="The year the church year begins in: Advent for most traditions, September for the Eastern Orthodox">Year
        <input type="number" id="yearBox" min="-9999" max="9998" step="1"></label>
      <label id="tradRow" title="The family of churches">Tradition
        <select id="tradition"></select></label>
      <label id="churchRow" title="Which church's calendar the wheel follows">Church
        <select id="church"></select></label>
      <label id="bookRow" hidden><span id="bookLabel">Hymnal</span>
        <select id="book"></select></label>
      <label id="seriesRow" hidden><span id="seriesLabel">Series</span>
        <select id="series"></select></label>
      <div id="subRows" class="rows"></div>
      <label title="All: every commemoration. Festivals: the festivals and feasts (in the Roman calendar, solemnities and feasts). Principal: only the principal days (solemnities). None: the saints' days are left off.">Feasts
        <select id="feasts">
          <option value="all">All</option>
          <option value="festivals">Festivals</option>
          <option value="principal">Principal only</option>
          <option value="none">None</option>
        </select></label>
      <label id="bibleRow" title="The translation the readings open in. Each church starts on the one it uses (ESV where it names none).">Bible
        <select id="bibleVersion"></select></label>
      <label id="layoutRow" title="How the day's readings are shown when there are several sets: one at a time under tabs, or all of them in columns (on the right, and across two columns when opened with more)">Readings shown as
        <select id="readingsLayout"><option value="tabs">Tabs</option><option value="columns">Columns</option></select></label>
      <label class="adv" id="slideRow" title="How fast the sets slide between the columns when more or less is clicked (kept in this browser)" hidden>Slide
        <select id="slideSpeed"><option value="0">Off</option><option value="350">Quick</option><option value="700">Medium</option><option value="1200">Slow</option></select></label>
      <div class="head adv">Calendar and names</div>
      <label class="adv" id="calRow" title="Which calendar the dates are reckoned in">Calendar
        <select id="calendar">
          <option value="gregorian">Gregorian</option>
          <option value="julian">Julian (Old Calendar)</option>
          <option value="revised-julian">Revised Julian (New Calendar)</option>
        </select></label>
      <label class="adv" id="easterRow" title="How Easter is dated, which is a separate question from how the days are named. Left to follow the calendar, a Gregorian wheel keeps Western Easter and the other two keep the Eastern one.">Easter
        <select id="paschalion">
          <option value="">With the calendar</option>
          <option value="gregorian">Western</option>
          <option value="julian">Eastern</option>
        </select></label>
      <label class="adv check" id="latinRow" title="Name the one-year Sundays as the historic calendar does, from the first words of the day's Introit: Ad Te Levavi, Laetare, Quasimodo Geniti"><input type="checkbox" id="latin"> Latin names</label>
      <div class="adv group" id="readingsRow" title="List the day's Bible readings under its name. Each kind can be left out; only the kinds this church's lectionary has are offered.">Readings
        <label class="site" id="bibleSiteRow" title="Where a reading opens. On a phone or tablet either one opens in its own app when the app is installed, and in the browser otherwise.">Open in
        <select id="bibleSite">
          <option value="biblegateway">Bible Gateway</option>
          <option value="youversion">Bible.com (YouVersion)</option>
        </select></label>
        <label title="The lessons of the day's own propers: its Sunday, holy day or season, and any other service its book appoints for it"><input type="checkbox" data-reading="day" checked> The day's propers</label>
        <label title="The lessons of a saint's day or festival, listed only while the wheel shows it (see Feasts)"><input type="checkbox" data-reading="feasts" checked> Feasts and festivals</label>
        <label title="The lessons of a day the calendar does not name, kept by its date or a date rule: Ember and Rogation Days, Thanksgiving, New Year's and national days, the Saturdays before and after a feast"><input type="checkbox" data-reading="dated" checked> Other dated days</label>
        <label title="The hymnal's or prayer book's daily or weekday lectionary"><input type="checkbox" data-reading="daily" checked> Daily lectionary</label>
        <label title="The additional readings a daily lectionary offers beside its own, for reading more of the Bible (Lutheran Service Book prints them in italics)"><input type="checkbox" data-reading="additional" checked> Additional readings</label>
        <label title="A table of psalms for daily prayer, morning and evening, by season and weekday (Lutheran Service Book, p. 304)"><input type="checkbox" data-reading="psalms" checked> Psalm table</label>
        <label title="A plan of daily Bible reading kept by the calendar year: Reading the Word of God (LCMS, LCC and NALC), through the Old Testament in three years and the Psalms and New Testament twice"><input type="checkbox" data-reading="plan" checked> Bible reading plan</label>
        <label title="The lessons of the Office: Morning and Evening Prayer, Matins, a second or third service"><input type="checkbox" data-reading="office" checked> Office lessons</label>
        <label id="propersRow" title="The parts of the service the church lists with each day's readings (an Introit, a Gradual and a Verse), on a line of their own after them; a set's heading opens only its readings together" hidden><input type="checkbox" id="propers" checked> <span id="propersName">Propers</span></label></div>
      <div class="head adv" id="musicHead">Music</div>
      <label class="adv check" id="suggestRow" title="The hymns suggested for the day, year by year, under a Hymns tab (or after the readings), with the Hymn of the Day"><input type="checkbox" id="suggest" checked> Suggested hymns</label>
      <label class="adv check" id="topicsRow" title="After the day's name, a hymnal mark for each section of the hymnal's index the day has (Advent, Reformation, a saint), opening its hymns"><input type="checkbox" id="hymnTopics" checked> Hymnal topics</label>
      <label class="adv check" id="hymnsRow" title="A hymnal mark after each set of readings that searches Hymnary.org for the hymns on them in this church's hymnal"><input type="checkbox" id="hymns" checked> Hymn search</label>
      <label class="adv" id="hymnalRow" title="The hymnal Hymn search and Hymnal topics look in, where the church has several" hidden>Hymnal
        <select id="hymnal"></select></label>
      <label class="adv check" id="w2wRow" title="A circled note after each set of readings that searches Word to Worship (wordtoworship.com) for contemporary worship songs on them"><input type="checkbox" id="w2w" checked> Contemporary song search</label>
      <div class="head adv">The wheel</div>
      <label class="adv" id="artRow" title="The picture in the middle of the wheel. Each tradition has its own; any of them can be chosen. By season changes it with the day chosen: the wreath in Advent, the manger at Christmas, the empty tomb at Easter, and the church's own picture in the seasons that have none.">Artwork
        <select id="artwork"></select></label>
      <label class="adv check" id="yearLineRow" title="A thicker line where the year's last week meets its first, which are a year apart"><input type="checkbox" id="yearLine"> Thicker line where the year begins</label>
      <label class="adv check" id="arrowsRow" title="Checked: at the end of the church year the arrow keys go on into the next year's wheel, and back into the last. Unchecked: they go round the year on the wheel, from its last week to its first. Page Up and Page Down and the &#9664; &#9654; buttons always go on."><input type="checkbox" id="arrowsOn"> Arrow keys go on into the next year</label>
      <label class="adv check" id="redsRow" title="The reds in the middle of the range (the LCMS, Roman and Presbyterian reds) read about as well with black text as with white. Checked: black on them."><input type="checkbox" id="darkReds"> Dark text on reds</label>
      <div class="adv group">Under the wheel
        <label title="How to use the wheel, the calendar's notes and how long it took to draw"><input type="checkbox" id="showHelp"> Instructions and notes</label>
        <label title="Who made the picture in the middle, and its license. When it is off and the license asks for credit, a small i button keeps it a click away."><input type="checkbox" id="showCredit"> Artwork credit</label></div>
      <div class="adv group">Rings<div id="ringList"></div>
        <button type="button" id="colorsBtn" class="reset" aria-haspopup="dialog"
                title="The colors the days and the rings are painted in, each of which can be changed for this page">Colors&#8230;</button>
        <dialog id="colorDialog" class="colors" aria-labelledby="colorHead">
          <form method="dialog">
            <h2 id="colorHead">Colors</h2>
            <p class="note">The colors on the wheel this year. Click a swatch to change it; the change is kept in the page's link. Text on a day stays readable: it turns black or white if it would not.</p>
            <div class="group">Days<div id="dayColors" class="swatches"></div></div>
            <div class="group">Rings<div id="ringColors" class="swatches"></div></div>
            <div class="actions">
              <button type="button" id="colorsReset" title="Put every color back to the page's own">Reset colors</button>
              <button value="close">Close</button>
            </div>
          </form>
        </dialog></div>
      <button type="button" id="resetBtn" class="reset"
              title="Put every setting here back to what config.csv asks for, keeping the day on the wheel">Reset settings</button>
      <div class="group">Share
        <div class="actions">
          <button type="button" id="copyLink" title="Copy a link that opens on this day, with these settings">Copy link</button>
          <button type="button" id="embedBtn" class="adv" title="Copy a line of HTML that shows this page inside a page of your own website (an iframe), opening on the day it is read, with these settings">Copy embed code</button>
          <button type="button" id="printBtn" title="Print the whole wheel on one page">Print</button>
          <button type="button" id="pageBtn" class="adv" aria-haspopup="dialog" title="Make a page like this one, for your own website: the churches it offers, the settings it opens with and which it shows">Make a page&#8230;</button>
          <button type="button" id="filesBtn" aria-haspopup="dialog" title="Download the wheel (SVG, PNG) and lists of its readings, colors and feasts, for this year or a run of years">Download&#8230;</button>
          <button type="button" id="editBtn" class="adv" aria-haspopup="dialog" title="Add to or correct the days' names and colors, the readings, the kinds of reading and the season colors: kept in this browser and in a page made from this one, and the changed data files to download for the Python scripts">Edit the data&#8230;</button>
        </div>
        <dialog id="editDialog" class="colors files edit" aria-labelledby="editHead">
          <form method="dialog">
            <h2 id="editHead" tabindex="-1">Edit the data</h2>
            <p class="note">Changes show on the wheel at once and are kept in this browser for this page; Make a page writes them into the page it makes. <b>Download changed files</b> gives the data files they change, to put over the project&#8217;s own for the Python scripts.</p>
            <div class="row quick tabs" role="tablist" id="editTabs"><button type="button" role="tab" data-tab="day">This day</button><button type="button" role="tab" data-tab="kinds">Kinds of reading</button><button type="button" role="tab" data-tab="seasons">Seasons</button><button type="button" role="tab" data-tab="colors">Colors</button><button type="button" role="tab" data-tab="changes">Changes</button></div>
            <div id="editBody"></div>
            <p class="text" id="editStatus" role="status"></p>
            <div class="actions">
              <button type="button" id="editExport" title="A .zip of the data files the changes make, laid out as the project's data folder">Download changed files</button>
              <button value="close">Close</button>
            </div>
          </form>
        </dialog>
        <dialog id="filesDialog" class="colors files" aria-labelledby="filesHead">
          <form method="dialog">
            <h2 id="filesHead">Download</h2>
            <p class="note">The wheel and its lists as they are here, with these settings: the church, calendars, feasts, readings, rings, colors and artwork.</p>
            <div class="group">Years
              <div class="row"><label>From <input type="number" id="filesFrom" step="1"></label>
                <label>to <input type="number" id="filesTo" step="1"></label></div>
              <p class="text" id="filesYears"></p></div>
            <div class="group">The wheel
              <label class="check"><input type="checkbox" id="filesSvg" checked> SVG (a drawing, sharp at any size)</label>
              <label class="check"><input type="checkbox" id="filesPng" checked> PNG (a picture)</label>
              <div class="row sub"><label><input type="number" id="filesWidth" min="500" max="16000" step="100" value="5000"> pixels wide</label>
                <label>Background <select id="filesBack"><option value="none">clear</option><option value="#ffffff">white</option></select></label></div></div>
            <div class="group">Lists
              <label class="check" id="listReadingsRow" title="Each day's readings, as the Readings boxes and the Feasts setting choose them"><input type="checkbox" id="listReadings"> Readings</label>
              <div class="row sub" id="listReadingsOpts"><label class="check" title="Each reading opens where Open in and Bible say; each set's heading opens all its readings"><input type="checkbox" id="listLinks"> with links</label></div>
              <label class="check" title="The Sundays and principal days (or every day) with the color the wheel paints them"><input type="checkbox" id="listColors"> Colors</label>
              <div class="row sub"><label>Days <select id="listDays"><option value="sundays">Sundays</option><option value="principal" selected>Sundays and principal days</option><option value="named">every named day</option><option value="all">every day</option></select></label>
                <label class="check" title="The other colors the church allows, and the lower half's where the wheel splits a cell (in the feasts list too)"><input type="checkbox" id="listEvery"> other colors</label></div>
              <label class="check" title="The festivals, saints' days and commemorations the Feasts setting keeps, on the days they fall"><input type="checkbox" id="listFeasts"> Feasts</label>
              <div class="row sub"><label class="check" title="Also Christmas, Easter, Pentecost and the other principal days on dates of their own"><input type="checkbox" id="listMajor"> with major days</label>
                <label class="check" title="Where to read about each, as the readout links it"><input type="checkbox" id="listFeastLinks"> with links</label></div>
              <label class="check" title="One row a year: Advent, Christmas, Ash Wednesday, Easter, Pentecost and the other movable dates, and how many Sundays after the Epiphany and Pentecost or Trinity (colors.py --overview). It has no iCalendar form, so with that format it comes as CSV."><input type="checkbox" id="listOverview"> The year at a glance</label>
              <div class="row"><label>Format <select id="listFormat"><option value="csv">CSV (spreadsheet)</option><option value="html">HTML (to print)</option><option value="ics">iCalendar (.ics)</option><option value="json">JSON</option><option value="md">Markdown</option></select></label></div></div>
            <p class="text" id="filesStatus" role="status"></p>
            <div class="actions">
              <button type="button" id="filesMake">Download</button>
              <button value="close">Close</button>
            </div>
          </form>
        </dialog>
        <dialog id="pageDialog" class="colors files page" aria-labelledby="pageHead">
          <form method="dialog">
            <h2 id="pageHead" tabindex="-1">Make a page</h2>
            <p class="note">A page like this one, in one HTML file to put on a website or open from a folder: the page church_year.py makes with the same options (below). Each choice starts as the page is now.</p>
            <details class="group churches" id="pageChurchesBox"><summary><span class="twisty" aria-hidden="true"></span><span class="name">Churches it offers</span> <span class="text" id="pageCount"></span></summary>
              <div class="row quick" id="pageQuick"><button type="button" data-pick="all">All</button><button type="button" data-pick="tradition">This tradition</button><button type="button" data-pick="church">This church</button><button type="button" data-pick="one">Only this one</button><button type="button" data-pick="none">None</button></div>
              <div class="tree" id="pageTree"></div></details>
            <div class="group">It opens
              <div class="row quick"><button type="button" id="pageNow" title="The church, calendars and settings on screen now">As on screen</button><button type="button" id="pageOwn" title="What this page opens with">As this page opens</button></div>
              <label title="--church">On <select id="pageChurch"></select></label>
              <div id="pageSubs"></div>
              <label class="check" title="--year (otherwise the church year that holds the day it is opened)"><input type="checkbox" id="pageYear"> <span>On the year beginning in Advent</span> <input type="number" id="pageYearNum" step="1"></label>
              <label title="--zoom: 1 (the whole wheel) to 6">Zoom <input type="number" id="pageZoom" min="1" max="6" step="0.1"></label>
              <label title="--language: the language of the page's buttons, menus and settings until the reader chooses another (Settings > Language)">Language <select id="pageUiLang"></select></label>
            </div>
            <div class="group">The wheel
              <label title="--feasts">Feasts <select id="pageFeasts"><option value="all">All</option><option value="festivals">Festivals</option><option value="principal">Principal only</option><option value="none">None</option></select></label>
              <label title="--latin-names, --no-latin-names">Latin names <select id="pageLatin"><option value="">Each church's own</option><option value="off">Off</option><option value="on">On</option></select></label>
              <div class="row" id="pageRings" title="--hide">Rings</div>
              <details class="tree colorsBox" id="pageColorsBox" title="--color-changes"><summary><span class="twisty" aria-hidden="true"></span><span class="name">Colors</span><span class="n" id="pageColorsN"></span></summary>
                <label class="mode">Change them <select id="pageColorMode"><option value="all">for all the churches together</option><option value="tradition">tradition by tradition</option><option value="church">church by church</option></select></label>
                <p class="text">A color changed for a tradition wins over every church&#8217;s, and one changed for a church wins over its tradition&#8217;s. Click a swatch to use that shade: its own come first, then the other churches&#8217; on this page. Point at one to see whose it is; &#215; puts a color back.</p>
                <div class="swatches" id="pageColorRows"></div>
                <label title="As a link's colors= writes them: PURPLE-7a1f7a,lutheran:WHITE-fffff0,ring.halves-e6c3f7,text.halves-000000,empty-f0f0f0">As text <input type="text" id="pageColors" placeholder="none" spellcheck="false"></label></details>
              <label title="--mid-text">Text on mid-tone colors <select id="pageMid"><option value="as-set">As each color sets it</option><option value="dark">Dark</option><option value="dark-reds">Dark on reds</option><option value="light">Light</option></select></label>
              <label class="check" title="--year-line, --no-year-line"><input type="checkbox" id="pageYearLine"> Thicker line where the year begins</label>
              <label title="--art: the picture the page opens on. By season: the picture of the chosen day's season, and the church's own in a season without one">Artwork <select id="pageArtwork"></select></label>
              <div class="row sub artkeep" id="pageArtKeep" title="--drop-art: untick a picture to leave it out of the page">Pictures kept</div>
              <p class="text artnone" id="pageArtNone" hidden></p>
              <div id="pageOwnArts"></div>
              <label class="addart" title="--own-art: a picture of your own, for the churches you choose"><span>Add a picture of your own&#8230;</span> <input type="file" id="pageArtFile" accept=".svg,.png,.jpg,.jpeg,.gif,.webp"></label></div>
            <div class="group" id="pageReadingsGroup">Readings and links
              <div class="row" id="pageReadings" title="--readings">Readings
                <label class="check"><input type="checkbox" value="day"> Day</label>
                <label class="check"><input type="checkbox" value="feasts"> Feasts</label>
                <label class="check"><input type="checkbox" value="dated"> Other dated days</label>
                <label class="check"><input type="checkbox" value="daily"> Daily</label>
                <label class="check"><input type="checkbox" value="additional"> Additional</label>
                <label class="check"><input type="checkbox" value="psalms"> Psalm table</label>
                <label class="check"><input type="checkbox" value="plan"> Reading plan</label>
                <label class="check"><input type="checkbox" value="office"> Office</label></div>
              <label title="--readings-layout">Readings shown as <select id="pageLayout"><option value="tabs,columns">Tabs, or columns in Settings</option><option value="columns,tabs">Columns, or tabs in Settings</option><option value="tabs">Tabs only</option><option value="columns">Columns only</option></select></label>
              <label title="--links">Links <select id="pageLinks"><option value="all">To the Bible and about the feasts</option><option value="bible">To the Bible only</option><option value="feasts">About the feasts only</option><option value="none">None (plain text)</option></select></label>
              <label title="--bible">Bible menu <select id="pageBibles"><option value="all">Every version</option><option value="some">These:</option><option value="own">None (each church's own version)</option></select></label>
              <div class="tree" id="pageBibleList" hidden></div>
              <label title="--bible-default">Bible <select id="pageBible"></select></label>
              <label title="--bible-site">Open in <select id="pageSite"><option value="biblegateway">Bible Gateway</option><option value="youversion">Bible.com</option><option value="">Bible.com on a phone, Bible Gateway elsewhere</option></select></label>
              <label title="--hymnary">Hymn search <select id="pageHymns"><option value="on">On</option><option value="off">Off (the box unchecked)</option><option value="none">None (no box and no marks)</option></select></label>
              <label title="--hymnal">Hymnal <select id="pageHymnal"></select></label>
              <label title="--word-to-worship">Contemporary song search <select id="pageW2w"><option value="on">On</option><option value="off">Off (the box unchecked)</option><option value="none">None (no box and no marks)</option></select></label>
            </div>
            <div class="group">Settings it shows
              <label class="check" title="--show calendar"><input type="checkbox" id="pageCal"> Calendar (Gregorian, Julian, Revised Julian)</label>
              <label class="check" title="--show easter"><input type="checkbox" id="pageEaster"> Easter (Western or Eastern)</label>
              <label class="check" title="--fixed artwork"><input type="checkbox" id="pageArt"> Artwork</label>
              <label class="check" title="--fixed reds"><input type="checkbox" id="pageReds"> Dark text on reds</label></div>
            <div class="group">Buttons it shows
              <label class="check" title="--no-download: the wheel as SVG and PNG, and its lists"><input type="checkbox" id="pageDownload"> Download&#8230;</label>
              <label class="check" title="--no-make-page: a page like itself, as this window makes"><input type="checkbox" id="pageMakePage"> Make a page&#8230;</label>
              <label class="check" title="--no-edit: changes to the titles, colors and readings, kept in the reader's browser, and the changed files to download"><input type="checkbox" id="pageEdit"> Edit the data&#8230;</label>
              <label class="check" title="--arrows-next-year, --arrows-same-year: whether the arrow keys go on into the next church year at the year's end, or round the year on the wheel (a box in the page's Settings changes it)"><input type="checkbox" id="pageArrows"> Arrow keys go on into the next year</label>
              <label class="check" title="--local-art: look for center.svg (or .png, .jpg ...) beside the page when it opens and offer it in the middle. Off, the page asks for no files beside it"><input type="checkbox" id="pageLocalArt"> A picture beside the page (center.svg&#8230;)</label>
            </div>
            <div class="group">Under the wheel
              <select id="pageFooter" title="--footer"><option value="full">Instructions, notes and credit</option><option value="credit">The artwork's credit only</option><option value="none">Nothing</option></select></div>
            <div class="group">Help link
              <input type="url" id="pageHelp" title="--help-link: the page the Help button opens, the user guide unless changed" placeholder="https://… (blank: none)"></div>
            <div class="group">Feedback link
              <input type="url" id="pageFeedback" title="--feedback" placeholder="https://… (blank: none)"></div>
            <label class="check" title="--fragment: no &lt;html&gt;, &lt;head&gt; or &lt;body&gt;, to paste into a page of your own"><input type="checkbox" id="pageFragment"> To paste into another page&#8217;s HTML</label>
              <p class="note" id="pageFragmentNote">Not a whole page: its contents go into your own page&#8217;s HTML. To show a page that is already on a website, <b>Copy embed code</b> under Share is simpler.</p>
            <label class="check" title="--no-compress when off: the tables as plain JSON, about three times the size, to read in the page's source or for a browser older than 2023"><input type="checkbox" id="pageCompress" checked> Packed, about a third of the size</label>
            <details class="cmd"><summary>The same page from Python; save or load these settings</summary><code id="pageCmd"></code>
              <div class="row quick"><button type="button" id="pageCmdCopy" title="Copy the command, to make this page with the script or to set this window from it later">Copy</button><button type="button" id="pageCmdSave" title="Save these settings as a small text file (the command), to load here again later">Save settings&#8230;</button><button type="button" id="pageCmdLoad" title="Set the window from a settings file saved here before">Load settings&#8230;</button><input type="file" id="pageCmdFile" accept=".txt,text/plain" hidden></div>
              <label for="pageCmdIn">Set the window from a command: paste one copied here before (or written for church_year.py)</label>
              <textarea id="pageCmdIn" rows="3" spellcheck="false" placeholder="python church_year.py --churches lcms-* --church lcms-one-year …"></textarea>
              <div class="row quick"><button type="button" id="pageCmdUse">Set the window from it</button></div>
              <p class="text" id="pageCmdNote" role="status"></p></details>
            <p class="text" id="pageStatus" role="status"></p>
            <div class="actions">
              <label title="-o">File name <input type="text" id="pageName" spellcheck="false"></label>
              <button type="button" id="pageMake">Make the page</button>
              <button value="close">Close</button>
            </div>
          </form>
        </dialog></div>
    </div>
  </details>
  </div>
  <h1 id="heading"><span id="headYear">Church Year</span><span id="headChurch"></span></h1>
  <button id="prev" class="step" title="Previous day (up arrow; left arrow: a week, Shift: a month)" aria-label="Previous day">&#9664;</button>
  <input type="date" id="pick" aria-label="Choose a date">
  <button id="next" class="step" title="Next day (down arrow; right arrow: a week, Shift: a month)" aria-label="Next day">&#9654;</button>
  <button id="now" title="Jump to today (T)">Today</button>
  <span class="find"><input type="search" id="find" placeholder="Find a day" autocomplete="off" spellcheck="false"
    aria-label="Find a day by its name" aria-controls="findList" aria-expanded="false"
    title="Type a Sunday's, a season's or a feast's name and pick it: the wheel goes to that day in the year shown (F)"><ul
    id="findList" class="findlist" role="listbox" aria-label="Days with that name" hidden></ul></span>
  <button id="weekBtn" type="button" aria-haspopup="dialog" title="The chosen day's week in a list: each day's names, color and readings (W)">Week</button>
  <span class="zoom">
    <button id="out" class="step" title="Zoom out (\u2212)" aria-label="Zoom out">&#8722;</button>
    <input type="range" id="mag" min="100" max="600" step="10" value="100"
           aria-label="Zoom">
    <button id="in" class="step" title="Zoom in (+)" aria-label="Zoom in">+</button>
    <select id="magOut" aria-label="Magnification" title="Magnification: 1&#215; (the whole wheel) to 6&#215;"></select>
  </span>
  <div class="readout" aria-live="polite">
    <div class="when" id="when"></div>
    <div class="what"><span class="swatch" id="dot"></span><span id="what"></span></div>
  </div>
  <div class="readings" id="readings" aria-live="polite" hidden></div>
  <dialog id="hymnsDialog" class="colors hymnlist" aria-labelledby="hymnsHead">
    <form method="dialog">
      <h2 id="hymnsHead"></h2>
      <p class="note" id="hymnsNote"></p>
      <ul id="hymnsList"></ul>
      <div class="actions"><button value="close">Close</button></div>
    </form>
  </dialog>
  <dialog id="weekDialog" class="colors week" aria-labelledby="weekHead">
    <form method="dialog">
      <div class="weekhead"><button type="button" id="weekPrev" class="step" title="The week before" aria-label="The week before">&#9664;</button>
      <h2 id="weekHead" tabindex="-1"></h2>
      <button type="button" id="weekNext" class="step" title="The week after" aria-label="The week after">&#9654;</button></div>
      <ol id="weekList"></ol>
      <div class="actions"><button type="button" id="weekPrint" title="Print this week's days and readings, a page or two to hand round">Print</button>
      <button value="close">Close</button></div>
    </form>
  </dialog>
</div>

<div class="stage" tabindex="0" aria-label="The church year wheel: left and right arrow keys step a week, up and down a day">
{svg}</div>

<p class="hint" id="hint"><span class="mouse">Type any year and the wheel is drawn for it. Click a
cell, use the arrow keys, or pick a date.</span><span class="touch">Tap a cell,
pinch to zoom, or pick a date.</span>
<span class="note" id="note"></span><span class="note timing" id="timing"></span>
<button type="button" id="infoBtn" class="info" hidden
aria-label="About the artwork" title="About the artwork" aria-expanded="false">i</button>
<span class="note credit" id="credit"></span></p>
<div class="corner"><a id="help" class="feedback" target="_blank" rel="noopener" hidden
   role="button" title="How to use this page: every control, key and setting">Help</a><a id="feedback" class="feedback" target="_blank" rel="noopener" hidden
   role="button" title="Send feedback about this page: the day, church and settings on screen go with it">Feedback</a></div>

<script>window.CHURCH_YEAR_DATA = {tables};</script>
<script>
{read('church_year.js')}
</script>
<script>
{read('listings.js')}
</script>
<script>
{read('page.js')}
</script>
</div>
"""

    if fragment:
        # A host that supplies its own <head> still needs the page's name; a
        # <title> here is hoisted out of the body by every browser.
        return f"<title>{xml_escape(title)}</title>\n" + body
    return (f"""<!doctype html>
<html lang="en" class="cy-page">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{xml_escape(title)}</title>
</head>
<body>
{body}</body>
</html>
""")


def freshen(data_json: Path, data_dir: Path = HERE / "data") -> None:
    """Rebuild web/data.json when it is missing or older than what it is built from.

    The frozen tables are a build product of data/ (plus the center artwork and
    the loaders in church_year_image.py), so leaving them to be regenerated by hand is
    a standing chance to draw last week's calendar.
    """
    sources = list(data_dir.rglob("*.csv"))
    sources += list((HERE / "artwork").glob("*.svg"))
    sources += [HERE / "church_year_image.py", HERE / "lib" / "traditions.py", HERE / "lib" / "calendars.py", WEB / "export_data.py"]
    # A picture of the user's own that config.csv names is frozen in too.
    from church_year_image import read_config, is_art_file, resolve_art_file
    named = (read_config(data_dir / "config.csv").get("center_svg") or "").strip() \
        if (data_dir / "config.csv").exists() else ""
    if is_art_file(named):
        sources += [f for f in [resolve_art_file(named, data_dir)] if f is not None]
    newest = max((f.stat().st_mtime for f in sources if f.exists()), default=0.0)
    if data_json.exists() and data_json.stat().st_mtime >= newest:
        return
    why = "is missing" if not data_json.exists() else "is out of date"
    print(f"  {data_json.name} {why} — rebuilding it ...")
    result = subprocess.run([sys.executable, str(WEB / "export_data.py"),
                             "--data", str(data_dir), "--out", str(data_json)],
                            capture_output=True, text=True)
    if result.returncode != 0 or not data_json.exists():
        sys.exit(result.stderr.strip()
                 or f"✗ could not build {data_json} — run: python web/export_data.py")


def load_tables(source: Path) -> dict:
    """The frozen tables, from web/data.json or straight from a folder of CSVs.

    Given a folder — a year made by new_year.py, say — the tables are built in
    memory from that folder's own settings, so its lectionary, calendar and
    colors reach the page without touching web/data.json.
    """
    if source.is_dir():
        sys.path.insert(0, str(WEB))
        import export_data
        return export_data.build(source)
    if source == WEB / "data.json":
        freshen(source)
    elif not source.exists():
        sys.exit(f"✗ {source} not found — run: python web/export_data.py")
    return json.loads(source.read_text(encoding="utf-8"))


def settings_file_args(argv: list[str]) -> list[str]:
    """argv with --settings FILE replaced by the options the file's command
    gives (Make a page's Save settings), put first so that the rest win."""
    import shlex
    out, before = [], []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--settings" or a.startswith("--settings="):
            name = a.split("=", 1)[1] if "=" in a else (argv[i + 1] if i + 1 < len(argv) else "")
            i += 1 if "=" in a else 2
            path = Path(name)
            if not name or not path.is_file():
                sys.exit(f"✗ --settings: no such file '{name}'")
            text = "\n".join(l for l in path.read_text(encoding="utf-8-sig").splitlines()
                              if not l.lstrip().startswith("#"))
            text = re.sub(r"[\\^]\r?\n", " ", text)          # lines continued (sh, cmd)
            words = shlex.split(text)
            at = next((k for k, w in enumerate(words) if re.search(r"church_year(_web)?(\.py)?$", w, re.I)), None)  # church_year_web.py was its old name
            words = words[at + 1:] if at is not None else words
            while words and not words[0].startswith("-"):
                words.pop(0)
            if "--settings" in words:
                sys.exit("✗ --settings: a settings file cannot name another")
            before += words
            continue
        out.append(a)
        i += 1
    return before + out


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the interactive wheel that draws any year in the browser.")
    parser.add_argument("--data", default=WEB / "data.json", type=Path,
                        help="the frozen tables (default: web/data.json), or a "
                             "folder of CSVs to build them from")
    parser.add_argument("-o", "--output", "--out", dest="out", default=None,
                        help="output HTML file, or a folder to write it into "
                             "(default: church_year.html)")
    parser.add_argument("--year", type=int, default=None,
                        help="Advent year to open on (default: whichever contains today)")
    parser.add_argument("--language", default=None, metavar="CODE",
                        help="the language of the page's buttons, menus and settings until the reader "
                             "chooses another: auto (the reader's browser), church (each church's own), "
                             "en, or a language in data/ui (de, es ...) (default: config.csv's "
                             "page_language, or auto)")
    parser.add_argument("--zoom", default=None, metavar="N",
                        help="the magnification the page opens at, 1 (the whole wheel) to 6, "
                             "centered on the day it opens on (default: config.csv's page_zoom, or 1)")
    parser.add_argument("--readings", default=None, metavar="KINDS",
                        help="the kinds of set of readings the page carries and offers: all, none, the kinds "
                             "to keep (day,feasts) or to leave out (--readings=-daily,-office), of day, "
                             "feasts, dated, daily, additional, psalms, plan and office; the others' readings "
                             "are not in the page (default: config.csv's page_readings, or all)")
    parser.add_argument("--church", default=None, metavar="KEY",
                        help="the church the page opens on, a key from data/traditions.csv "
                             "(default: config.csv's lectionary)")
    parser.add_argument("--subcalendar", action="append", default=None, metavar="KEY",
                        help="a calendar laid over the church's when the page opens (repeatable; "
                             "none for none; default: config.csv's subcalendars)")
    parser.add_argument("--feasts", choices=("all", "festivals", "principal", "none"), default=None,
                        help="the Feasts setting the page opens with (default: config.csv's feast_detail)")
    parser.add_argument("--latin-names", dest="latin", action="store_true", default=None,
                        help="open with Latin names on, for every church that has them")
    parser.add_argument("--no-latin-names", dest="latin", action="store_false",
                        help="open with Latin names off (default: each church's own, else config.csv's latin_names)")
    parser.add_argument("--year-line", dest="year_line", action="store_true", default=None,
                        help="open with the thicker line where the year ends and begins")
    parser.add_argument("--no-year-line", dest="year_line", action="store_false",
                        help="open without it (default: config.csv's year_line)")
    parser.add_argument("--mid-text", choices=("as-set", "dark", "dark-reds", "light"), default=None,
                        help="text on mid-tone colors; dark-reds opens with Dark text on reds checked "
                             "(default: config.csv's mid_text)")
    parser.add_argument("--bible-default", default=None, metavar="VERSION",
                        help="the Bible version every church opens in, when the page offers it "
                             "(default: each church's own; see --bible to limit the menu)")
    parser.add_argument("--hide", default=None, metavar="RINGS",
                        help="rings the page opens with turned off, rings.csv keys separated by commas "
                             "(gold, halves, seasons, months ...; default: config.csv's page_hide, or none)")
    parser.add_argument("--color-changes", dest="colors", default=None, metavar="CHANGES",
                        help="colors the page opens with changed, as a link's colors= writes them: "
                             "PURPLE-7a1f7a (every church), lutheran:WHITE-fffff0 (one tradition's, "
                             "which wins), lutheran:wels-one-year:RED-c00000 (one church's, which wins "
                             "again), ring.halves-e6c3f7, text.halves-000000, empty-f0f0f0 "
                             "(default: config.csv's page_colors, or none)")
    parser.add_argument("--bible-site", choices=["biblegateway", "youversion"], default=None,
                        help="where readings open at first: Bible Gateway or Bible.com (default: "
                             "config.csv's page_bible_site, else Bible.com on a phone and Bible Gateway elsewhere)")
    parser.add_argument("--word-to-worship", choices=["on", "off", "none"], default=None,
                        help="the mark after each set of readings that searches Word to Worship "
                             "for contemporary worship songs: on, off (the settings box unchecked) or none "
                             "(no box and no marks) (default: config.csv's page_word_to_worship, else on)")
    parser.add_argument("--hymnary", choices=["on", "off", "none"], default=None,
                        help="the mark after each set of readings that searches Hymnary.org for "
                             "hymns on them in the church's hymnal (tradition.csv hymnary_hymnal): on, "
                             "off (the settings box unchecked) or none (no box and no marks) "
                             "(default: config.csv's page_hymnary, else on)")
    parser.add_argument("--hymnal", default=None, metavar="CODE",
                        help="the hymnal Hymn search opens on, for each church that has it among "
                             "several (tradition.csv hymnary_hymnal: AM2013, CPAM2000 ...; default: "
                             "each church's first)")
    parser.add_argument("--readings-layout", default=None, metavar="LAYOUTS",
                        help="how the day's readings are shown when there are several sets: tabs "
                             "(one set at a time) or columns (all of them, the later ones on the "
                             "left); both, comma-separated, offers the other in Settings, the first "
                             "opening (default: config.csv's page_readings_layout, else tabs,columns)")
    parser.add_argument("--help-link", dest="help_link", default=None, metavar="URL",
                        help="the page the page's Help button opens, such as the user guide; none for "
                             "no button (default: config.csv's page_help, or none)")
    parser.add_argument("--feedback", default=None, metavar="URL",
                        help="the form the page's Feedback link opens; the day's link, date and "
                             "church are added as link=, date= and church= (or fill {link}, {date} "
                             "and {church} in URL); none for no link (default: config.csv's "
                             "page_feedback, or none)")
    parser.add_argument("--links", default=None, metavar="KINDS",
                        help="the links the page has: all, none, or bible (each reading opens in a Bible, "
                             "and each set together) and feasts (each commemoration's page), separated by "
                             "commas; without bible there is no Bible or Open in setting (default: "
                             "config.csv's page_links, or all)")
    parser.add_argument("--download", dest="download", action="store_true", default=None,
                        help="offer Download... (the default: config.csv's page_download, else on)")
    parser.add_argument("--no-download", dest="download", action="store_false",
                        help="leave Download... (the wheel as SVG and PNG, and its lists) off the page")
    parser.add_argument("--make-page", dest="make_page", action="store_true", default=None,
                        help="offer Make a page... (the default: config.csv's page_make_page, else on)")
    parser.add_argument("--no-make-page", dest="make_page", action="store_false",
                        help="leave Make a page... (a page like this one, made in the browser) off the page")
    parser.add_argument("--edit", dest="edit", action="store_true", default=None,
                        help="offer Edit the data... (the default: config.csv's page_edit, else on)")
    parser.add_argument("--arrows-next-year", dest="arrows_next_year", action="store_true", default=None,
                        help="open with the arrow keys going on into the next church year (and back into "
                             "the last) at the year's end (the default: config.csv's page_arrows_next_year, else off)")
    parser.add_argument("--arrows-same-year", dest="arrows_next_year", action="store_false",
                        help="open with the arrow keys going round the year on the wheel, from its last "
                             "week to its first, over config.csv")
    parser.add_argument("--local-art", dest="local_art", action="store_true", default=None,
                        help="look for a picture beside the page (center.svg, .png, .jpg ...) to offer in the "
                             "middle (the default: config.csv's page_local_art, else off)")
    parser.add_argument("--no-local-art", dest="local_art", action="store_false",
                        help="do not look for a picture beside the page")
    parser.add_argument("--no-edit", dest="edit", action="store_false",
                        help="leave Edit the data... (changes to the titles, colors and readings, "
                             "and the changed files) off the page")
    parser.add_argument("--no-compress", dest="compress", action="store_false",
                        help="write the tables as plain JSON in the page rather than packed "
                             "(gzip and base64, about a fifth of the size)")
    parser.add_argument("--fragment", action="store_true",
                        help="omit the <html>/<body> wrapper, for embedding in a page")
    parser.add_argument("--churches", default=None,
                        help="offer only these churches: keys, tradition names or "
                             "key prefixes ending in * (default: config.csv's "
                             "page_churches, or all)")
    parser.add_argument("--list", "--list-churches", dest="list_churches", action="store_true",
                        help="list the churches' keys and stop")
    parser.add_argument("--fixed", default=None, metavar="SETTINGS",
                        help="leave these settings out of the page and keep each church's own: "
                             "calendar, easter, artwork, reds (the Dark text on reds box), separated by spaces or commas "
                             "(default: config.csv's page_fixed, or none)")
    parser.add_argument("--show", default=None, metavar="SETTINGS",
                        help="offer these settings, which a page leaves out unless asked: "
                             "calendar (Gregorian, Julian, Revised Julian) and easter "
                             "(Western or Eastern), separated by spaces or commas "
                             "(default: config.csv's page_show, or neither)")
    parser.add_argument("--bible", default=None, metavar="VERSIONS",
                        help="the Bible versions the page offers: version codes (ESV, KJV ...), languages "
                             "(english, de, sv ...) or own (each church's own, no menu); one version hides "
                             "the menu (default: config.csv's page_bibles, or all)")
    parser.add_argument("--footer", choices=["full", "credit", "none"], default=None,
                        help="the lines under the wheel (default: config.csv's page_footer, or full)")
    parser.add_argument("--art", default=None, metavar="KEY|FILE",
                        help="the artwork the page opens on: auto (each church's own), season (the "
                             "picture of the chosen day's season, data/season_art.csv, and the "
                             "church's own in a season without one), none, a key "
                             "from data/artwork.csv, or a picture of your own (.svg, .png, .jpg, "
                             ".jpeg, .gif or .webp; found from the current folder, then the "
                             "project folder): one --own-art gives, or else added to the Artwork "
                             "menu as it is (default: config.csv's center_svg)")
    parser.add_argument("--own-art", action="append", default=None, metavar="FILE|FIELD=VALUE|...",
                        help="a picture of your own, frozen into the page and listed in its Artwork menu "
                             "(repeatable).  After the file, |-separated: churches=KEY,KEY (the churches it "
                             "is the own picture of), credit=, author=, license= (a license or a copyright "
                             "notice), license-url=, source=, scale= (1 fills the circle), attribution= "
                             "(required, the default when there is a credit: always shown; or optional)")
    parser.add_argument("--drop-art", default=None, metavar="KEYS",
                        help="the churches' pictures to leave out of the page (artwork.csv keys, comma-"
                             "separated); a church whose picture is dropped has none, unless --own-art gives "
                             "it one")
    parser.add_argument("--settings", default=None, metavar="FILE",
                        help="read the options from a settings file saved by the page's Make a page "
                             "(its command, # lines being notes); options given here as well win")
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--settings" in argv or any(a.startswith("--settings=") for a in argv):
        argv = settings_file_args(argv)
    args = parser.parse_args(argv)
    use_utf8_output()

    data = load_tables(args.data)
    raw = data.get("configRaw", {})
    keys = [t["key"] for t in data["traditions"] if t.get("tradition")]
    if args.church is not None:
        key = args.church.strip().lower()
        if key not in keys:
            sys.exit(f"✗ --church: no church '{args.church}' (python church_year.py --list shows them)")
        data["defaultTradition"] = key
    if args.subcalendar is not None:
        subs = [w.strip() for s in args.subcalendar for w in s.replace(",", " ").split() if w.strip()]
        subs = [] if subs == ["none"] else subs
        known = {s.get("key") for f in data["folders"].values() for s in (f.get("subcalendars") or [])}
        bad = [s for s in subs if s not in known]
        if bad:
            sys.exit(f"✗ --subcalendar: no calendar {', '.join(bad)} to lay over a church")
        data["defaultSubcalendars"] = subs
    if args.feasts:
        data["settings"]["feast_detail"] = args.feasts
    if args.mid_text:
        data["settings"]["mid_text"] = args.mid_text
    if args.latin is not None:
        data["latinDefault"] = bool(args.latin)
    if args.year_line is not None:
        data["settings"]["year_line"] = bool(args.year_line)
    if args.bible_default:
        code = args.bible_default.strip().upper()
        if code not in bible_versions():
            sys.exit(f"✗ --bible-default: no version '{args.bible_default}'; choose from {', '.join(sorted(bible_versions()))}")
        data["bibleDefault"] = code
    spec = args.churches if args.churches is not None else str(raw.get("page_churches") or "")
    data = select_churches(data, spec)
    if args.list_churches:              # the churches this page would offer
        list_churches(data)
        return 0
    footer = (args.footer or str(raw.get("page_footer") or "full")).strip().lower()
    if footer not in ("full", "credit", "none"):
        sys.exit(f"✗ page_footer must be full, credit or none (not '{footer}')")
    data["footer"] = footer
    fixed = (args.fixed if args.fixed is not None else str(raw.get("page_fixed") or ""))
    fixed = [w.strip().lower() for w in fixed.replace(",", " ").split() if w.strip()]
    fixed = ["artwork" if w == "art" else w for w in fixed]
    bad = [w for w in fixed if w not in FIXABLE]
    if bad:
        sys.exit(f"✗ page_fixed: {', '.join(bad)} cannot be fixed; choose from {', '.join(FIXABLE)}")
    show = (args.show if args.show is not None else str(raw.get("page_show") or ""))
    show = [w.strip().lower() for w in show.replace(",", " ").split() if w.strip()]
    bad = [w for w in show if w not in HIDDEN_UNLESS_SHOWN]
    if bad:
        sys.exit(f"✗ page_show: {', '.join(bad)} is always offered or unknown; "
                 f"choose from {', '.join(HIDDEN_UNLESS_SHOWN)}")
    fixed += [w for w in HIDDEN_UNLESS_SHOWN if w not in show and w not in fixed]
    data["fixed"] = fixed
    data["bibles"] = bible_choice(args.bible if args.bible is not None else str(raw.get("page_bibles") or ""))
    if data.get("bibleDefault") and not bible_allowed(data["bibles"], data["bibleDefault"]):
        menu = ",".join(data["bibles"])
        sys.exit(f"✗ --bible-default: {data['bibleDefault']} is not on the Bible menu (--bible {menu}); "
                 + ("with each church's own version there is none to choose; --bible "
                    f"{data['bibleDefault']} opens every church in it" if data["bibles"] == ["own"]
                    else "add it there, or leave --bible-default out"))
    choose_artwork(data, args)
    if args.year is not None:
        data["openOn"] = args.year
    readings = args.readings if args.readings is not None else str(raw.get("page_readings") or "")
    if readings.strip():
        from lectionary import READING_CATEGORIES, parse_categories
        try:
            kinds = parse_categories(readings)
        except ValueError as exc:
            sys.exit(f"✗ page_readings: {exc}")
        if list(kinds) != list(READING_CATEGORIES):
            data["readingsDefault"] = list(kinds)
            # Only those sets come along.
            data = prune_readings(data, list(kinds), args.data if args.data.is_dir() else HERE / "data")
    hide = args.hide if args.hide is not None else str(raw.get("page_hide") or "")
    hide = [w.strip() for w in hide.replace(" ", ",").split(",") if w.strip()]
    if hide:
        rings = {r["key"]: r for r in data.get("rings", [])}
        bad = [k for k in hide if k not in rings or rings[k].get("kind") in ("days", "center")]
        if bad:
            ok = ", ".join(k for k, r in rings.items() if r.get("kind") not in ("days", "center"))
            sys.exit(f"✗ page_hide: {', '.join(bad)} cannot be hidden; choose from {ok}")
        data["hiddenDefault"] = hide
    colors = (args.colors if args.colors is not None else str(raw.get("page_colors") or "")).strip()
    if colors:
        for item in colors.split(","):
            key, _, value = item.strip().rpartition("-")
            if not key or not re.fullmatch(r"[0-9a-fA-F]{6}|[0-9a-fA-F]{3}", value):
                sys.exit(f"✗ page_colors: '{item}' is not NAME-rrggbb (PURPLE-7a1f7a, lutheran:WHITE-fffff0, "
                         "ring.halves-e6c3f7, text.halves-000000, empty-f0f0f0)")
        slug = lambda t: re.sub(r"\s+", "-", (t.get("tradition") or "").strip().lower())
        trads = {slug(t) for t in data["traditions"]}
        for item in colors.split(","):
            scope = item.strip().rpartition("-")[0].split(":")
            if len(scope) > 1 and re.sub(r"\s+", "-", scope[0].strip().lower()) not in trads:
                sys.exit(f"✗ page_colors: '{item.strip()}' names no tradition on this page; "
                         f"choose from {', '.join(sorted(trads))}")
            if len(scope) > 2 and not any(t["key"] == scope[1].strip().lower()
                                          and slug(t) == re.sub(r"\s+", "-", scope[0].strip().lower())
                                          for t in data["traditions"]):
                sys.exit(f"✗ page_colors: '{item.strip()}' names no {scope[0]} church on this page "
                         "(tradition:church-key:COLOR-rrggbb)")
        data["colorsDefault"] = colors
    site = (args.bible_site or str(raw.get("page_bible_site") or "")).strip().lower()
    if site:
        if site not in ("biblegateway", "youversion"):
            sys.exit(f"✗ page_bible_site must be biblegateway or youversion (not '{site}')")
        data["bibleSite"] = site
    layout = (args.readings_layout or str(raw.get("page_readings_layout") or "")).strip().lower()
    if layout:
        words = [w for w in re.split(r"[\s,]+", layout) if w]
        if not words or any(w not in ("tabs", "columns") for w in words) or len(set(words)) != len(words):
            sys.exit(f"✗ page_readings_layout must be tabs, columns, tabs,columns or columns,tabs (not '{layout}')")
        if words != ["tabs", "columns"]:
            data["readingsLayout"] = words
    hymns = (args.hymnary or str(raw.get("page_hymnary") or "")).strip().lower()
    if hymns:
        if hymns not in ("on", "off", "none"):
            sys.exit(f"✗ page_hymnary must be on, off or none (not '{hymns}')")
        if hymns != "on":
            data["hymnary"] = hymns
    if args.hymnal:
        offered = []
        csv_dir = args.data if args.data.is_dir() else HERE / "data"
        for t in data["traditions"]:
            setting = T.tradition_settings(csv_dir, T.find_tradition(csv_dir, t["key"])).get("hymnary_hymnal")
            codes = str(setting or "").split()
            if len(codes) > 1:
                offered += [c for c in codes if c not in offered]
        hit = next((c for c in offered if c.lower() == args.hymnal.strip().lower()), None)
        if hit is None:
            sys.exit(f"✗ --hymnal: no church on this page offers '{args.hymnal}' among several hymnals"
                     + (f"; choose from {', '.join(offered)}" if offered else ""))
        data["hymnalDefault"] = hit
    w2w = (args.word_to_worship or str(raw.get("page_word_to_worship") or "")).strip().lower()
    if w2w:
        if w2w not in ("on", "off", "none"):
            sys.exit(f"✗ page_word_to_worship must be on, off or none (not '{w2w}')")
        if w2w != "on":
            data["wordToWorship"] = w2w
    help_link = (args.help_link if args.help_link is not None else str(raw.get("page_help") or "")).strip()
    if help_link and help_link.lower() != "none":
        if not re.match(r"^https?:", help_link, re.I):
            sys.exit(f"✗ page_help must be an https:// address, not '{help_link}'")
        data["help"] = help_link
    feedback = (args.feedback if args.feedback is not None else str(raw.get("page_feedback") or "")).strip()
    if feedback and feedback.lower() != "none":
        if not re.match(r"^(https?:|mailto:)", feedback, re.I):
            sys.exit(f"✗ page_feedback must be an https:// (or mailto:) address, not '{feedback}'")
        data["feedback"] = feedback
    links = (args.links if args.links is not None else str(raw.get("page_links") or "")).strip().lower()
    kinds = [w for w in links.replace(",", " ").split() if w]
    if kinds and kinds != ["all"]:
        bad = [w for w in kinds if w not in ("bible", "feasts", "none")]
        if bad or ("none" in kinds and len(kinds) > 1):
            sys.exit(f"✗ page_links: all, none, or bible and feasts (not '{links}')")
        if set(kinds) != {"bible", "feasts"}:
            data["links"] = [k for k in ("bible", "feasts") if k in kinds]
    for arg, setting, field in (("download", "page_download", "noDownload"),
                                ("make_page", "page_make_page", "noMakePage"),
                                ("edit", "page_edit", "noEdit")):
        wanted = getattr(args, arg)
        if wanted is None:
            text = str(raw.get(setting) or "").strip()
            if text and text.lower() not in ("true", "false", "1", "0", "yes", "no", "on", "off", "y", "n"):
                sys.exit(f"✗ {setting} must be TRUE or FALSE (not '{text}')")
            wanted = not text or text.lower() in ("true", "1", "yes", "on", "y")
        if not wanted:
            data[field] = True
    arrows = args.arrows_next_year
    if arrows is None:
        text = str(raw.get("page_arrows_next_year") or "").strip()
        if text and text.lower() not in ("true", "false", "1", "0", "yes", "no", "on", "off", "y", "n"):
            sys.exit(f"✗ page_arrows_next_year must be TRUE or FALSE (not '{text}')")
        arrows = text.lower() in ("true", "1", "yes", "on", "y")
    if arrows:
        data["arrowsNext"] = True
    local = args.local_art
    if local is None:
        text = str(raw.get("page_local_art") or "").strip()
        if text and text.lower() not in ("true", "false", "1", "0", "yes", "no", "on", "off", "y", "n"):
            sys.exit(f"✗ page_local_art must be TRUE or FALSE (not '{text}')")
        local = text.lower() in ("true", "1", "yes", "on", "y")
    if local:
        data["localArt"] = True
    ui = (args.language if args.language is not None else str(raw.get("page_language") or "")).strip().lower() or "auto"
    ui_codes = ["auto", "church", "en"] + sorted(data.get("ui", {}))
    if ui not in ui_codes:
        sys.exit(f"✗ page_language must be one of {', '.join(ui_codes)} (not '{ui}')")
    if ui != "auto":
        data["uiLanguage"] = ui
    zoom = args.zoom if args.zoom is not None else str(raw.get("page_zoom") or "").strip()
    if zoom not in (None, ""):
        try:
            z = float(zoom)
        except ValueError:
            sys.exit(f"✗ page_zoom must be a number from 1 to 6 (not '{zoom}')")
        if not 1 <= z <= 6:
            sys.exit(f"✗ page_zoom must be from 1 to 6 (not {z:g})")
        if z != 1:
            data["openZoom"] = z
    html = build(data, args.fragment, args.compress)

    default = Path("church_year.html")
    if args.out:
        target = Path(args.out)
        is_folder = (target.is_dir() or args.out.endswith(("/", "\\"))
                     or target.suffix == "")
        out_path = target / default.name if is_folder else target
    else:
        out_path = default

    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
    except OSError as exc:
        sys.exit(f"✗ Could not write {out_path}: {exc}")

    opening = (args.year if args.year is not None
               else advent_year_for(date.today(), data.get("defaultTradition", "lcms-three-year")))
    print(f"✓ Wrote {out_path.resolve()}  ({len(html) / 1024:.0f} KB, "
          f"any year, opening on {T.year_label(opening)})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        raise SystemExit(0)
