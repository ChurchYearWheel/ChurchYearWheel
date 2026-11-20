# Tools

Scripts for maintaining the calendar. None of them is needed to draw it.
Each prints its usage with `-h`.

## In use

| script | what it does | when to run it |
| --- | --- | --- |
| `publish.py` | builds the web page and publishes it to a here.now site as its index.html (`--site SLUG`, `--add` more files, `--no-page` for only the `--add` files, `--password` / `--no-password`, `--dry-run`); the API key comes from `HERENOW_API_KEY` or `~/.herenow/credentials` | to update the preview site |
| `provenance.py` | writes `docs/provenance.md` from `docs/provenance.csv`; `--check` only checks the CSV | after editing `docs/provenance.csv` |
| `font_widths.py` | writes `lib/font_widths.py`: the widths of the letters beyond ASCII that the calendars use (accented, Cyrillic, typographic quotes), read from the Liberation fonts with fontTools, so that names in them are fitted to their cells at their true width | after adding a calendar whose names use letters not yet in the table |
| `check_contrast.py` | lists any color whose text color is not the more readable of black and white | after adding or changing a color in any `colors.csv` |
| `clean_svg.py` | tidies a Wikimedia Commons SVG for use as center artwork: drops editor-only content, prefixes its ids, rounds coordinates | when adding artwork from Commons |
| `_cli.py` | the `-h` handling and argument check the scripts share | not run by itself |

The checks of the renderers themselves (`verify.py`, `verify_bc.py`,
`verify_readings.py`, `verify_links.py`, `verify_lists.py`, `verify_pages.py`) are in `web/`; see the README.

The scripts that redraw the church emblems kept for private use (`make_roundels.py`
and the `trace_*.py` tracers) are kept with those pictures in
`artwork/church-emblems/tools/`, and are not published.
