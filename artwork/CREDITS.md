# Artwork credits

The pictures for the middle of the wheel: most drawn for this project, a few
from Wikimedia Commons. The same
details are in `data/artwork.csv`. The web page prints the credit for
whichever picture is showing, with links to its source and license.

## church-emblems/Anglican_Compass_Rose.svg — Anglican compass rose (not published)

- Source: <https://commons.wikimedia.org/wiki/File:Anglican_Compass_Rose_(without_background).svg>
- Author: Gregor Shapiro, after JaMikePA's drawing
- License: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)
- Changes: as above, with the id prefix `acr-`.

## church-emblems/Episcopal_Shield_Roundel.svg — Episcopal shield (not published)

- Source: <https://commons.wikimedia.org/wiki/File:Episcopal_Shield.svg>
  (kept as `church-emblems/sources/Episcopal_Shield.svg`)
- Author: Pattleboats; the roundel drawn for this project
- License: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)
- Changes: editor metadata removed and coordinates rounded; a stray point off
  to one side dropped; the shield set in a blue roundel (`church-emblems/tools/make_roundels.py`).

## Logo_of_the_United_Methodist_Church.svg — Cross and flame

- Source: <https://commons.wikimedia.org/wiki/File:Logo_of_the_United_Methodist_Church.svg>
- Designers: Edward J. Mikula and Edwin H. Maynard
- License: public domain as a drawing; the cross and flame is a registered
  trademark of The United Methodist Church
- Changes: as above, with the id prefix `umc-`.

## church-emblems/Calvin_Seal_Roundel.svg — Calvin's seal (not published)

- Source: <https://commons.wikimedia.org/wiki/File:Pseudo-Arms_of_John_Calvin.svg>
  (kept as `church-emblems/sources/Pseudo-Arms_of_John_Calvin.svg`)
- Author: SemperAdiuvans; the roundel and lettering for this project
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- Changes: the shield and the sun left out, and the heart in the hand set in a
  roundel with Calvin's motto, *Cor meum tibi offero Domine prompte et
  sincere*, in TeX Gyre Pagella (GUST Font License) (`church-emblems/tools/make_roundels.py`).
  This adapted file is shared under the same license and must carry its
  credit, which is why it is set aside with the church emblems: nothing the
  project publishes asks for a credit.

## Insignia and trademarks

The Episcopal shield, the compass rose, and the logos and seals of the
Presbyterian Church (U.S.A.), the Church of Scotland, the Moravian Church, the
GKLI and the Ukrainian Lutheran Church are the emblems of churches. Commons
notes that, whatever the copyright status of the drawings, the use of official
emblems may be restricted in some countries. The cross and flame is a
registered trademark: The United Methodist Church permits its congregations and
agencies to use it. Using any of these to mark that church's calendar is
descriptive. Using one in a way that suggests the church endorses a
publication is a different matter, and is the user's responsibility.

### Before publishing the project

These churches' published terms ask outsiders for permission, or forbid
redrawing (checked October 2026), so their files are **not published**: they
are kept in `artwork/church-emblems/`, which `.gitignore` leaves out, they are
not in `data/artwork.csv`, and each church's wheel carries one of the project's
own emblems instead (below). A church may still add its own emblem to its own
page (`artwork/church-emblems/README.md`).

- `PCUSA_logo.svg`: the seal is a registered trademark and registered
  copyright; anyone other than a congregation or governing body needs prior
  approval, and the design may not be altered (pcusa.org, "PC(USA) Seal").
- `Church_of_Scotland_logo.svg`: use by outside parties needs the
  Communications Department's approval, and the emblem may not be redrawn
  (Visual Identity Guidelines).
- `Logo_of_the_United_Methodist_Church.svg`: the cross and flame is reserved
  to United Methodist bodies; commercial use by others needs GCFA's written
  permission (Cross and Flame Guidelines).
- `GKLI_logo.svg` and `Methodist_Orb_and_Cross.svg`: church emblems redrawn
  here; no terms for outside use are published, so ask.
- `Anglican_Compass_Rose.svg` and `Episcopal_Shield_Roundel.svg`: the drawings
  are CC0 on Commons, but the emblems are the Anglican Communion's and The
  Episcopal Church's own marks, so they are set aside with the others to
  leave no impression of endorsement.
- `Moravian_Seal.svg` and `Moravian_Seal_1923.svg`: traced from the church's modern
  seal and from the 1923 hymnal's; neither is in use (the Moravian Church opens
  on the Moravian star).

The rest are free to share, and none needs a credit: the Orthodox, Armenian
and Syriac crosses are in the public domain, and the pictures drawn for this
project are CC0: the Luther rose, the Coptic and Ethiopian crosses, and the
roundels below.

## The project's own roundels

Drawn for this project by `tools/make_emblems.py` and released into the public
domain ([CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)): no
credit is needed and nothing is asked of a drawing that includes one. Each
fills the middle with color, in the manner of a stained-glass roundel, within
a gold ring. None is traced from anything.

- `Luther_Rose.svg`, key `lutherrose`: the black cross in the middle of a red
  heart on a white double rose (five outer petals whose lips rise to a point,
  five smaller ones round the heart, the sepals' points between), in a
  sky-blue field within a gold ring, as Luther described his seal in 1530.
  Every Lutheran church's own (key `lutherrose`). It took the place of the
  drawing from Wikimedia Commons (Daniel Csörföly's `Lutherrose.svg`, CC BY-SA
  3.0), so no wheel now carries a credit that must be kept or a share-alike
  condition.
- `Chi_Rho_Roundel.svg`, `chi_rho`: gold on a red sunburst. The Methodist
  churches.
- `Celtic_Cross_Roundel.svg`, `celtic_cross`: a standing cross on a green hill
  before the rising sun. The Presbyterian Church (U.S.A.) and the Church of
  Scotland.
- `Canterbury_Cross_Roundel.svg`, `canterbury_cross`: gold and red on blue.
  The Anglican prayer books and The Episcopal Church.
- `Burning_Bush_Roundel.svg`, `burning_bush`: the bush that burned and was not
  consumed (Exodus 3). The Reformed churches.
- `Moravian_Star_Roundel.svg`, `moravian_star`: the many-pointed Advent star,
  lit from within, on a night sky. The Moravian Church. The Moravian Church.
- `Chalice_and_Host_Roundel.svg`, `chalice`: the chalice with the host
  shining above it. The Roman and Ambrosian calendars (it replaces the IHS
  roundel, which is gone).

## The seasons' pictures

`Season_Advent_1.svg` to `Season_Advent_4.svg` (the wreath with one to four
candles lit, one for each week of Advent), `Season_Christmas.svg`
(the manger under the star), `Season_Epiphany.svg` (the star and three
crowns), `Season_Lent.svg` (the cross and crown of thorns),
`Season_Holy_Week.svg` (three crosses on the hill), `Season_Easter.svg` (the
empty tomb at sunrise) and `Season_Pentecost.svg` (the dove as one white shape in a glory, as the old
windows have it, and the tongues of fire): drawn for this project by `tools/make_emblems.py`, CC0 like the
roundels above. They are what **Artwork: By season** shows
(`data/season_art.csv`), and each can be chosen on its own.

## The Eastern crosses, set in roundels

`Orthodox_Cross_Roundel.svg`, `Armenian_Cross_Roundel.svg`,
`Syriac_Cross_Roundel.svg`, `Coptic_Cross_Roundel.svg` and
`Ethiopian_Cross_Roundel.svg`: the crosses described below, kept as they were
in `artwork/sources/`, set by `tools/make_emblems.py` in gold on a sunburst of
each church's own color within the gold ring. Their licenses are unchanged
(public domain, all five).

## Set aside with the church emblems

`church-emblems/Moravian_Seal_1923.svg` (public domain, but a rough tracing of
a small print) and `church-emblems/Ukrlc_logo.svg` (the Ukrainian Lutheran
Church's own seal) are no longer in the Artwork menu.

## sources/OrthodoxCross.svg — Orthodox cross

- Source: <https://commons.wikimedia.org/wiki/File:OrthodoxCross.svg>
- Author: Ariane Schmidt
- License: public domain
- Changes: editor metadata removed, a viewBox added, coordinates rounded to
  two decimals; the ends of the slanted foot cut upright, as on the Russian
  cross.

## Armenian_Cross.svg — Armenian cross

- Source: <https://commons.wikimedia.org/wiki/File:USVA_headstone_emblem_Armenian_Cross.svg>
- Author: U.S. Department of Veterans Affairs (emblem of belief for
  headstones and markers)
- License: public domain (a work of the U.S. federal government)
- Changes: editor metadata removed.

## Western_Syriac_Cross.svg — West Syriac cross

- Source: <https://commons.wikimedia.org/wiki/File:Western_Syriac_Cross.svg>
- Author: Rafy
- License: public domain
- Changes: editor metadata removed, the path rewritten in absolute
  coordinates rounded to whole units. The drawing is otherwise unchanged.

## Coptic_Cross.svg and Ethiopian_Cross.svg — Coptic and Ethiopian crosses

Drawn for this project from simple shapes, after the common forms of the
Coptic cross and the Ethiopian processional cross. Released into the public
domain.

## Ukrlc_logo.svg — Ukrainian Lutheran Church seal

- Source: <https://commons.wikimedia.org/wiki/File:Ukrlc_logo.svg>
- Author: unknown (from the church's website); vectorized by Ch.Andrew
- License: public domain. The seal is the church's insignia and may be
  protected as a trademark.
- Changes: redrawn from that drawing (`church-emblems/tools/trace_ulc.py`). The yellow ring
  and blue field are true circles; the rose and the heart are traced as drawn
  (the rose's pointed, half-white leaves and curved lines kept, and the heart's
  slight lean around the cross), both with potrace; the cross is drawn as
  three bars and the slanted foot as a parallelogram measured from the picture. The gray and black slivers at the old edge are gone.

## GKLI_logo.svg — Gereja Kristen Luther Indonesia logo

- Source: the logo printed in the *Almanak GKLI 2026* (Gereja Kristen Luther
  Indonesia, <https://www.gkli.org/>)
- Author: Gereja Kristen Luther Indonesia
- License: all rights reserved. The logo is the church's emblem; it is used here
  only to identify the church's calendar.
- Changes: redrawn from the almanac's raster image (`church-emblems/tools/trace_logo.py`).
  The disc, the blue field, the cross and the stars are drawn as geometry
  measured from the picture; the lettering is set in Liberation Sans Bold
  (SIL Open Font License) on a true circle, sized and spaced to the picture;
  the rose and the heart are traced with potrace from smoothed outlines.

## PCUSA_logo.svg — Presbyterian Church (U.S.A.) seal

- Source: two pictures of the seal of the Presbyterian Church (U.S.A.)
  (<https://www.presbyterianmission.org/>): a navy-on-white one and a
  white-on-blue one
- Author: Presbyterian Church (U.S.A.)
- License: all rights reserved. The seal is the church's emblem and a
  registered mark; it is used here only to identify the church's calendar.
- Changes: redrawn (`church-emblems/tools/trace_pcusa.py`) in the white-on-blue colors. The
  symbol is traced with potrace from the sharper navy-on-white picture, at
  eight times its size, and made mirror-symmetric; the lettering is set in TeX
  Gyre Pagella (GUST Font License), a Palatino, each letter at the angle it has
  in the picture; the field is a true circle, lighter at the center.

## Church_of_Scotland_logo.svg — Church of Scotland emblem

- Source: a picture of the Church of Scotland's emblem
  (<https://www.churchofscotland.org.uk/>)
- Author: Church of Scotland
- License: all rights reserved. The emblem is the church's mark; it is used
  here only to identify the church's calendar.
- Changes: redrawn (`church-emblems/tools/trace_cos.py`). The rings and the field are true
  circles and the saltire two straight bands, fitted to the picture; the
  burning bush and its white leaves and branches are traced with potrace as
  drawn.

## Moravian_Seal.svg — Seal of the Moravian Church

- Source: a picture of the Moravian Church's seal (<https://www.moravian.org/>)
- Author: Moravian Church
- License: all rights reserved. The seal is the church's emblem; it is used
  here only to identify the church's calendar.
- Changes: redrawn (`church-emblems/tools/trace_moravian.py`). The rings and the field are
  true circles; the Lamb, the flag, the halo and the grass are traced as drawn,
  color by color, with potrace; the motto (OUR LAMB HAS CONQUERED · LET US
  FOLLOW HIM) is set in Carlito (SIL Open Font License) in place of the seal's
  own lettering.

## Moravian_Seal_1923.svg — Seal of the Moravian Church, 1923 (not in use)

- Source: the seal on the title page of the *Hymnal and Liturgies of the
  Moravian Church (Unitas Fratrum)*, Bethlehem, 1923
  (<https://archive.org/details/hymnalliturgieso1920mora>; kept as
  `church-emblems/sources/Moravian_Seal_1923.png`). The Lamb and banner, with the motto
  *Vicit Agnus noster, eum sequamur* ("our Lamb has conquered, let us follow
  him"), has been the Unity's seal since the sixteenth century.
- License: public domain (published in the United States in 1923).
- Changes: redrawn (`church-emblems/tools/trace_moravian_1923.py`). The field is a true circle
  fitted to the picture; the Lamb, its halo, the staff and the grass are traced
  as drawn with potrace, the print's speckle left out; the banner is drawn as
  a parallelogram measured from the picture, with its cross as the print has
  it, a pair of thin lines on each arm; the motto and its two stars are set in
  TeX Gyre Heros Bold (GUST Font License) over the arcs they take in the
  picture.

## Methodist_Orb_and_Cross.svg — Orb and cross of the Methodist Church in Britain

- Source: a picture of the Methodist Church in Britain's emblem
  (<https://www.methodist.org.uk/>)
- Author: Methodist Church in Britain
- License: all rights reserved. The emblem is the church's mark; it is used
  here only to identify the church's calendar.
- Changes: redrawn as geometry (`church-emblems/tools/make_roundels.py`): a red disc cut by a
  white cross whose arms widen toward the rim, measured from the picture; the
  caption under the picture left out.
