# Pictures kept for private use (not published)

This folder holds pictures that are not part of the published project: church
emblems, which belong to the churches they name, and pictures whose licenses
ask for a credit. `.gitignore` leaves out everything here but this note, the
pictures are not in `data/artwork.csv`, and no page built from the project
carries them. Every picture the project publishes is its own (CC0) or in the
public domain, and none needs a credit.

A church that may use its own emblem can still put it in the middle of its own
wheel:

- on the web page: **Settings → All → Make a page… → Add a picture of your own**;
- from Python: `python church_year.py --own-art emblem.svg churches=KEY`
  or `python church_year_image.py KEY --art emblem.svg`.
