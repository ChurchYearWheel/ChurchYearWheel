# Church emblems (not published)

The logos and seals in this folder belong to the churches they name. Their
published terms reserve them to the church's own bodies, ask outsiders for
permission, or forbid redrawing, or (the compass rose and the Episcopal
shield) are simply the church's own mark (see "Before publishing the project" in
`../CREDITS.md`), so they are **not part of the published project**:
`.gitignore` leaves out everything in this folder but this note, the pictures
are not in `data/artwork.csv`, and no page built from the project carries
them.

One picture here is not a church's emblem: **Calvin's seal**
(`Calvin_Seal_Roundel.svg`, from a Wikimedia Commons drawing by SemperAdiuvans,
CC BY-SA 4.0). It is free to share, but only with its credit and under the
same license, and it is kept here so that nothing the project publishes asks
for a credit.

A church that may use its own emblem can still put it in the middle of its own
wheel:

- on the web page: **Settings → All → Make a page… → Add a picture of your own**;
- from Python: `python church_year.py --own-art emblem.svg churches=KEY`
  or `python church_year_image.py KEY --art emblem.svg`.

To use one of these while working privately, copy its row from `artwork.csv`
here into `data/artwork.csv` (the `file` column already points at this folder)
and name its key as the church's `center_art` in that church's `tradition.csv`.

The scripts that drew them are in `tools/` here (`make_roundels.py` for the
roundels, and a `trace_*.py` for each traced emblem), and the pictures they
work from in `sources/`.
