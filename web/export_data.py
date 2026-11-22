#!/usr/bin/env python3
"""
Freeze everything the browser needs into JSON.

The browser renderer has to agree with `church_year_image.py` exactly, so it is given
the same tables rather than its own copy of them: the font metrics, the parsed
settings (for each tradition, with its own settings laid over config.csv),
the colors, styles and rings, every tradition's rules and feasts and the
calendars that can be laid over them, the icons, and the artwork for the
middle.  Everything is read through `church_year_image.py`'s and `traditions.py`'s
own loaders, so a change to a CSV reaches the browser the next time this runs.

    python web/export_data.py                    # ./data  -> web/data.json
    python web/export_data.py --data years/2026
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import church_year_image as cy  # noqa: E402
import traditions as T  # noqa: E402


def font_metrics() -> dict:
    return {
        "first": cy._FIRST_CODE,
        "default": cy._DEFAULT_WIDTH,
        "faces": {k: list(v) for k, v in cy._FONT_METRICS.items()},
        "extra": {k: {str(c): w for c, w in v.items()} for k, v in cy._FONT_EXTRA.items()},
    }


def settings_dict(settings: cy.Settings) -> dict:
    """Every setting, as its parsed value.  Dates go out as ISO strings."""
    out = {}
    for name in cy.SETTING_SPEC:
        value = getattr(settings, name)
        out[name] = value.isoformat() if hasattr(value, "isoformat") else value
    # A blank paschalion means "follow the calendar".  Exporting the resolved
    # rule instead opened the page's Easter picker on "Western", so switching
    # the page to the Julian calendar kept a Western Easter.
    out["paschalion"] = settings._values.get("paschalion_as_written", out["paschalion"])
    return out


def svg_artwork(path: Path) -> dict:
    """A picture's children (or embedded image) and its own size, ready to be
    scaled into the middle; church_year_image.py draws from the same markup."""
    return cy.artwork_markup(path)


def own_artwork(path: Path, credit: str = "", scale: str = "", author: str = "",
                license: str = "", license_url: str = "", source_url: str = "",
                attribution: str = "") -> tuple[str, dict]:
    """A picture of the user's own (config.csv's center_svg naming a file, or
    church_year.py --art FILE), frozen like an artwork.csv entry under
    the key file:<name>.  It carries no credit unless one is given; a credit
    (title, author or license) must be shown unless `attribution` is
    optional."""
    row = cy.own_art_row(path, credit, scale)
    art = svg_artwork(path)
    value = cy.own_art_scale(row["scale"])
    author, license = (author or "").strip(), (license or "").strip()
    credited = bool(row["title"] or author or license)
    art.update({"label": row["label"], "title": row["title"], "author": author, "license": license,
                "licenseUrl": (license_url or "").strip(), "sourceUrl": (source_url or "").strip(),
                "changes": "",
                "attribution": "required" if credited and (attribution or "required") == "required" else "",
                "scale": "" if value == 1.0 else repr(value), "own": True})
    return row["key"], art


def use_artwork(out: dict, key: str) -> None:
    """Open the page on this artwork.  Only the opening choice: "The
    tradition's own" stays each church's own picture."""
    out["defaultArt"] = key
    out["configRaw"] = dict(out.get("configRaw") or {}, center_svg=key)


def style_dict(style: cy.TextStyle) -> dict:
    return {
        "name": style.name, "fontFamily": style.font_family,
        "fontSize": style.font_size, "fontWeight": style.font_weight,
        "fontStyle": style.font_style, "fontVariant": style.font_variant,
        "minFontSize": style.min_font_size, "maxLines": style.max_lines,
        "orientation": style.orientation, "fill": style.fill,
    }


def ring_dict(ring: cy.Ring) -> dict:
    return {
        "order": ring.order, "key": ring.key, "kind": ring.kind,
        "rInner": ring.r_inner, "rOuter": ring.r_outer, "fill": ring.fill,
        "stroke": ring.stroke, "strokeWidth": ring.stroke_width,
        "source": ring.source, "fontSize": ring.font_size,
        "fontFamily": ring.font_family, "fontWeight": ring.font_weight,
        "textColor": ring.text_color, "labelMode": ring.label_mode,
        "innerBorderColor": ring.inner_border_color,
        "innerBorderWidth": ring.inner_border_width, "enabled": ring.enabled,
    }


def month_overrides(data_dir: Path) -> dict:
    found = cy.Calendar._load_month_overrides(data_dir / "month_overrides.csv")
    return {
        "fontSize": {str(k): v for k, v in found["font_size"].items()},
        "vertical": {str(k): v for k, v in found["vertical"].items()},
        "horizontal": {str(k): v for k, v in found["horizontal"].items()},
        "firstDayVertical": found["first_day_vertical"],
    }


def compact(rows: list[dict]) -> list[dict]:
    """Rows without their blank cells, which the browser reads as blank anyway."""
    return [{k: v for k, v in row.items() if v != ""} for row in rows]


def pack_rows(rows: list[dict]) -> dict:
    """A table of readings as the page keeps it (church_year.js: packRows):
    its columns in the order they first appear, every distinct cell once in
    `strings`, and each row as the indexes of its cells, less trailing blanks.
    A lectionary repeats its titles, kinds and cycles on every row, so this is
    about a third the size of the rows written out."""
    cols: list[str] = []
    for row in rows:
        cols += [k for k in row if k not in cols]
    strings: dict[str, int] = {}
    packed = []
    for row in rows:
        cells = [row.get(c, "") for c in cols]
        while cells and cells[-1] == "":
            cells.pop()
        packed.append([strings.setdefault(v, len(strings)) for v in cells])
    return {"cols": cols, "strings": list(strings), "rows": packed}


def unpack_rows(table: dict) -> list[dict]:
    """pack_rows undone: each row's cells by column, blank ones left out."""
    cols, strings = table["cols"], table["strings"]
    return [{cols[i]: strings[x] for i, x in enumerate(row) if strings[x] != ""}
            for row in table["rows"]]


def reading_rows(path: Path) -> list[dict]:
    """readings.csv: its #comment lines are dropped before the CSV is read, so
    the sources named in them may hold commas and quotes freely."""
    if not path.exists():
        return []
    import csv
    lines = [l for l in path.read_text(encoding="utf-8-sig").splitlines()
             if l.strip() and not l.lstrip().startswith(("#", '"#'))]
    rows = []
    for raw in csv.DictReader(lines):
        row = {(k or "").strip(): (v or "").strip() for k, v in raw.items() if k is not None}
        # (an `omit` row may leave its day or its kinds blank)
        if row.get("kind") == "omit" or (row.get("day") and row.get("reading")):
            rows.append(row)
    return rows


def folder_tables(data_dir: Path, folder: str) -> dict:
    """A tradition folder's rules, as written; the browser filters by variant."""
    base = data_dir / folder
    subs = []
    for entry in T.read_rows(base / "subcalendars.csv"):
        if not entry.get("key"):
            continue
        subs.append({"menu": entry.get("menu", ""), "menuLabel": entry.get("menu_label", ""),
                     "key": entry["key"], "label": entry.get("label", "") or entry["key"],
                     "include": entry.get("include", ""), "file": entry.get("file", ""),
                     "rows": compact(T.read_rows(base / entry.get("file", "")))})
    return {
        "settings": compact(T.read_rows(base / "tradition.csv")),
        "days": compact(T.read_rows(base / "days.csv")),
        "periods": compact(T.read_rows(base / "periods.csv")),
        "feasts": compact(T.read_rows(base / "feasts.csv")),
        "subcalendars": subs,
        "readings": pack_rows(compact(reading_rows(base / "readings.csv"))),
        # Hymnal topics matched to days, for the page's hymn marks by the day's name.
        "hymnTopics": compact(T.read_rows(base / "hymn_topics.csv")),
        # The folder's colors and season colors as written, for the page's
        # editor (the drawing reads them from profiles).
        "colors": compact(T.read_rows(base / "colors.csv")),
        "seasons": compact(T.read_rows(base / "seasons.csv")),
    }


def csv_layouts(data_dir: Path, out: dict) -> dict:
    """The layout of every file behind the page's tables (lib/csvlayout.py),
    by its path under data/, so the page can write an edited file back."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
    import csvlayout
    found = {}

    def add(rel: str, kind: str = "rows") -> None:
        path = data_dir / rel
        if path.is_file():
            found[rel] = csvlayout.layout(path, kind)

    add("colors.csv")
    for folder, tables in out["folders"].items():
        for name in ("tradition", "days", "periods", "feasts", "hymn_topics", "colors", "seasons"):
            add(f"{folder}/{name}.csv")
        add(f"{folder}/readings.csv", "readings")
        for sub in tables["subcalendars"]:
            if sub.get("file"):
                add(f"{folder}/{sub['file']}")
    for name in out["sharedReadings"]:
        add(f"readings/{name}.csv", "readings")
    return found


def ui_words(path: Path) -> dict:
    """data/ui/<code>.csv: the page's English words (key) and this language's (value)."""
    out = {}
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(r for r in f if not r.startswith('"#') and not r.startswith("#")):
            if row.get("english") and row.get("translation"):
                out[row["english"]] = row["translation"]
    return out


def language_dict(lang: cy.Language) -> dict:
    return {"months": [lang.months[i] for i in range(1, 13)],
            "dateMonths": [lang.date_months[i] for i in range(1, 13)],
            "monthDay": lang.month_day, "fullDate": lang.full_date,
            "chapterVerse": lang.chapter_verse, "books": lang.books,
            "colors": lang.colors, "or": lang.or_word,
            "readings": lang.readings, "name": lang.name}


def profile(data_dir: Path, tradition: T.Tradition) -> dict:
    """What drawing this tradition needs besides its rules: settings, colors, styles."""
    folder = T.folder_path(data_dir, tradition)
    overlay = T.tradition_settings(data_dir, tradition)
    settings = cy.load_settings(data_dir / "config.csv", overlay)
    colors = cy.load_colors(data_dir / "colors.csv", folder / "colors.csv")
    season_colors = cy.load_season_colors(folder / "seasons.csv", colors)
    styles = cy.load_text_styles(data_dir / "text_styles.csv", folder / "text_styles.csv")
    return {
        "settings": settings_dict(settings),
        "colors": {k: {"name": v.name, "fill": v.fill, "text": v.text} for k, v in colors.items()},
        "seasonColors": {k: v.name + ("; " + v.alt if v.alt else "")
                         for k, v in season_colors.items()},
        "styles": {k: style_dict(v) for k, v in styles.items()},
        "art": (overlay.get("center_art", "") or "lutherrose").lower(),
    }


def artwork(data_dir: Path, calendar: "cy.Calendar") -> tuple[dict, list[str]]:
    out, order = {}, []
    for row in calendar.artwork_rows():
        key = cy._cell(row, "key").lower()
        path = calendar.resolve_asset(cy._cell(row, "file"))
        if path is None:
            print(f"  ! artwork '{key}': {cy._cell(row, 'file')} not found; left out",
                  file=sys.stderr)
            continue
        art = svg_artwork(path)
        for column, name in (("label", "label"), ("title", "title"), ("author", "author"),
                             ("license", "license"), ("license_url", "licenseUrl"),
                             ("source_url", "sourceUrl"), ("changes", "changes"),
                             ("attribution", "attribution"), ("scale", "scale")):
            art[name] = cy._cell(row, column)
        out[key] = art
        order.append(key)
    return out, order


class _Shared:
    """Just enough of a Calendar to find files and read artwork.csv."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    artwork_rows = cy.Calendar.artwork_rows
    resolve_asset = cy.Calendar.resolve_asset


def build(data_dir: Path) -> dict:
    raw = cy.read_config(data_dir / "config.csv")
    registry = T.load_registry(data_dir)
    default = (raw.get("lectionary") or "lcms-three-year").strip().lower()
    if default not in {t.key for t in registry}:
        default = registry[0].key
    base = cy.load_settings(data_dir / "config.csv")
    shared = _Shared(data_dir)
    art, order = artwork(data_dir, shared)
    # config.csv may name the artwork by its file, as older ones did; the page
    # knows artwork only by its artwork.csv key, so the file becomes its key.
    named = (raw.get("center_svg") or "").strip()
    if named and named.lower() not in ("auto", "none") and named.lower() not in art:
        for row in shared.artwork_rows():
            if cy._cell(row, "file") == named and cy._cell(row, "key").lower() in art:
                raw = dict(raw, center_svg=cy._cell(row, "key").lower())
                break
        else:
            # A picture of the user's own, frozen into the page beside the others.
            path = cy.resolve_art_file(named, data_dir) if cy.is_art_file(named) else None
            try:
                key, entry = own_artwork(path, base.center_svg_credit, base.center_svg_scale)
            except Exception as exc:
                if path is not None:
                    print(f"  ! center_svg '{named}' could not be read ({exc})", file=sys.stderr)
                print(f"  ! center_svg '{named}' is not in artwork.csv; the page shows "
                      "each tradition's own artwork instead", file=sys.stderr)
            else:
                art[key] = entry
                order.append(key)
                raw = dict(raw, center_svg=key)
    folders = {}
    for tradition in registry:
        if tradition.folder and tradition.folder not in folders:
            folders[tradition.folder] = folder_tables(data_dir, tradition.folder)
    out = {
        "metrics": font_metrics(),
        "sansHints": list(cy.TextMeasurer.SANS_HINTS),
        "configRaw": raw,
        "settings": settings_dict(base),
        "rings": [ring_dict(r) for r in cy.close_ring_gaps(cy.load_rings(data_dir / "rings.csv"))],
        "monthNames": {str(k): v for k, v in cy.load_month_names(data_dir / "month_names.csv").items()},
        # The churches' languages: the wheel's months and dates, the page's
        # Bible book names (church_year.js: languageOf).
        "languages": {code: language_dict(cy.load_language(data_dir, code))
                      for code in ["en"] + sorted(p.stem for p in (data_dir / "languages").glob("*.csv"))},
        # The page's own words in other languages (data/ui/<code>.csv: the
        # English words and theirs; page.js: T and the Language setting).
        "ui": {p.stem: ui_words(p) for p in sorted((data_dir / "ui").glob("*.csv"))},
        "monthOverrides": month_overrides(data_dir),
        # Which picture a season shows when the middle follows the season.
        "seasonArt": [{"season": season, "art": art, "church": church, "week": week}
                      for season, art, church, week in cy.load_season_art(data_dir / "season_art.csv")],
        "traditions": [t.as_dict() for t in registry],
        "folders": folders,
        # Lectionaries that several calendars share (data/readings/*.csv),
        # named by a tradition's `readings` setting.
        "sharedReadings": {p.stem: pack_rows(compact(reading_rows(p)))
                           for p in sorted((data_dir / "readings").glob("*.csv"))},
        "profiles": {t.key: profile(data_dir, t) for t in registry},
        # Hymnals' first lines by number (data/hymnals/<code>.csv), for the
        # page's list of a hymn_topics.csv section.
        "hymnals": {p.stem: {r["number"]: r.get("first_line", "") for r in T.read_rows(p)}
                    for p in sorted((data_dir / "hymnals").glob("*.csv"))},
        "icons": {k: {"label": v["label"], "path": v["path"]}
                  for k, v in cy.load_icon_defs(data_dir / "icons.csv").items()},
        "artwork": art,
        "artworkOrder": order,
        # The palette as written (colors.csv), for the page's editor.
        "colorRows": compact(T.read_rows(data_dir / "colors.csv")),
        "defaultTradition": default,
        "defaultSubcalendars": (raw.get("subcalendars") or "").replace(",", " ").split(),
        "defaultArt": (raw.get("center_svg") or "auto").strip(),
    }
    # How each file behind the tables is laid out, so the page can write it back.
    out["csv"] = csv_layouts(data_dir, out)
    # A file renamed to its key above is renamed for every tradition too.
    if named and raw.get("center_svg") != named:
        out["settings"]["center_svg"] = raw["center_svg"]
        for p in out["profiles"].values():
            if p["settings"].get("center_svg") == named:
                p["settings"]["center_svg"] = raw["center_svg"]
    return out


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Freeze the year-independent calendar data as JSON.")
    parser.add_argument("--data", default="data", type=Path,
                        help="directory holding the CSV files (default: ./data)")
    parser.add_argument("--out", default=None, type=Path,
                        help="output JSON (default: web/data.json)")
    args = parser.parse_args(argv)
    cy.use_utf8_output()

    if not args.data.is_dir():
        sys.exit(f"✗ Data directory not found: {args.data}")

    out_path = args.out or Path(__file__).resolve().parent / "data.json"
    payload = build(args.data)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, separators=(",", ":"), sort_keys=True),
                        encoding="utf-8")
    feasts = sum(len(f["feasts"]) for f in payload["folders"].values())
    print(f"✓ Wrote {out_path.resolve()}  "
          f"({out_path.stat().st_size / 1024:.0f} KB, {len(payload['traditions'])} "
          f"traditions, {feasts} feasts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
