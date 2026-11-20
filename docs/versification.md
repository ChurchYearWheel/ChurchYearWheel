# Verse numbers

Bibles number some verses in two ways, and a citation in one numbering opens
the wrong verses, or misses one, in the other.

## The two numberings

**The Hebrew numbering** is the printed Hebrew Bible's. It is still the one in
the Bibles most of these churches read today: Luther 2017 and the other German
Bibles, the Polish, Norwegian (2011), Danish (1992), Finnish (1992), Estonian,
Icelandic (2007) and Hungarian Bibles, and in the Psalms the Swedish, Slovak
and Indonesian ones. In English, the New American Bible, Revised Edition
(NABRE) of the Roman Catholic lectionary uses it too.

- A psalm's heading ("A Psalm of David") is a verse of its own, two verses in
  Psalms 51, 52, 54 and 60, so every verse after it is one (or two) higher:
  Hebrew Psalm 80:2–20 is Psalm 80:1–19 in an English Bible.
- A few chapters break at a different verse. Joel has four chapters and
  Malachi three (Hebrew Malachi 3:19–24 is Malachi 4:1–6), Hebrew Isaiah 9:1–6
  is Isaiah 9:2–7, Micah 5:1–4 is 5:2–5, Zechariah 2:14–17 is 2:10–13, Jonah
  2:1–11 is 1:17–2:10, 1 Kings 22:52 is 22:51, and a few more
  (lib/versification.py lists them all).

**The English numbering** is the King James Version's, used by the other
English Bibles. Bible Gateway and Bible.com number every version they carry
this way, the Luther Bible and the Scandinavian ones included; only the NABRE
keeps its own numbers there.

## What the calendar does

A citation is given as the church gives it, in the numbering its Bible uses,
so it can be looked up in the church's own Bible. A church whose readings are
in the Hebrew numbering says so in its `verse_numbering` setting (tradition.csv:
`hebrew` for every book, or the books, as `Psalms` for Sweden), and the links
then translate the citation, so that an English-numbered version on Bible
Gateway or Bible.com opens at the same verses. A link in the NABRE is not
translated.

| Church | verse_numbering |
|---|---|
| EKD (Germany, Austria), Poland, Norway, Denmark, Finland, Estonia, Iceland, Hungary | `hebrew` |
| Sweden | `Psalms` |
| Slovakia | `Psalms Joel` |
| HKBP | `Psalms Isaiah Joel Micah` |
| Roman Catholic (the NABRE) | `hebrew` |
| Latvia | `hebrew`: its source mixes the two numberings; the few citations in the English one (as the RCL prints them) are given in the Latvian Bible's, so the Bible and the links agree |

Where a church's own Bible no longer uses the Hebrew numbering, the citation is
given in the English one, and docs/source-errors.csv notes it: ELHB's 1 Kings
22:52 (the numbering of the German Bibles of its time) is 1 Kings 22:51 here,
as in TLH and every Bible the LCMS reads today.

A whole psalm ("Psalm 24") is the same in both numberings. A citation of a
psalm's heading in the Hebrew numbering ("Psalm 51:1–14") opens at verse 1 in
an English Bible, where the heading belongs to verse 1.

## Prayer Book psalters

A Prayer Book psalter can divide a psalm's verses its own way. Coverdale's
psalter, and the revisions of it the prayer books keep, often split one Bible
verse in two or join two: the ACNA's Psalm 33:17–21 is 33:18–22 in an English
Bible. A church whose own readings (its folder's readings.csv) cite such a
psalter names it in its `psalter` setting; each of those psalm citations is
shown as the church gives it, and its link opens the same verses in the
English numbering. The shared lectionaries it also reads (the RCL and its
Daily Readings) are in the English numbering already and are left alone.

| Church | psalter | Psalms that differ |
|---|---|---|
| ACNA 2019 | `acna-2019` (its revised Coverdale) | 66 |
| BCP 1928, REC 2005 | `american-1928` (the American Coverdale, from REC 2005's text) | 69 |
| BCP 1962 (Canada) | `canada-1962` | 65 |
| BCP 1979 (`episcopal`) | `bcp-1979` | 62 |

Each table (lib/versification.py and web/church_year.js: PSALTERS) covers the
psalms whose verse count in that psalter differs from the King James
Version's, each aligned verse by verse by their words and lengths. The psalms
with as many verses as the King James Version's are taken to divide them
alike, and Psalm 119 is left alone. A psalter verse that holds two English
verses opens both ("Psalm 33:13" opens 33:13–14). Where a psalter leaves
verses out (the Canadian book omits Psalm 58 and some verses of others), the
verses it keeps still open their English places. After "; " or "–end" the
next bare number is another psalm ("Psalms 21:1–6; 24"), so BCP 1928's and REC
2005's lists of psalms are written with a semicolon after a part of a psalm.

The Church of England's table of differences between Coverdale and Common
Worship could not serve: Common Worship's psalter numbers some psalms
differently from English Bibles too (its Psalm 8 has ten verses).
