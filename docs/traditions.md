# Traditions

The wheel can follow more than one church's year. Each **tradition** is a
folder under `data/` holding the rules for its principal days and seasons, its
saints' days, and any colors, styles and settings of its own. On the page,
three menus pick one: the **Tradition** (Anglican, Catholic, Lutheran,
Orthodox…), the **Church** within it, and — for a church with more than one
calendar — the series or prayer book. In `config.csv` and on the command line
it is named by its key (`lectionary`, `--lectionary`).

| Key | Tradition → Church → series | Folder |
|---|---|---|
| `anglican-acna-2019` | Anglican → ACNA (Anglican Church in North America) → BCP 2019 | `data/Anglican` (variant `acna-2019`) |
| `anglican-bcp-1962` | Anglican → Anglican Church of Canada → BCP 1962 | `data/Anglican` (variant `bcp-1962`) |
| `anglican-wales-1984` | Anglican → Church in Wales → BCP 1984 | `data/Anglican` (variant `wales-1984`) |
| `anglican-bcp-1662` | Anglican → Church of England → BCP 1662 | `data/Anglican` (variant `bcp-1662`) |
| `anglican-common-worship` | Anglican → Church of England → Common Worship | `data/Anglican` (variant `common-worship`) |
| `anglican-locb-2008` | Anglican → Diocese Anglicana do Recife → LOCb 2008 | `data/Anglican` (variant `locb-2008`) |
| `anglican-bcp-1928` | Anglican → Episcopal Church (USA) → BCP 1928 | `data/Anglican` (variant `bcp-1928`) |
| `episcopal` | Anglican → Episcopal Church (USA) → BCP 1979 | `data/Episcopal` |
| `anglican-iab-2021` | Anglican → Igreja Anglicana no Brasil (IAB) → LOC 2021 | `data/Anglican` (variant `iab-2021`) |
| `anglican-iarb-1662` | Anglican → Igreja Anglicana Reformada do Brasil (IARB) → LOC 1662 | `data/Anglican` (variant `iarb-1662`) |
| `anglican-ieab-2015` | Anglican → Igreja Episcopal Anglicana do Brasil (IEAB) → LOC 2015 | `data/Anglican` (variant `ieab-2015`) |
| `anglican-iecb-1987` | Anglican → Igreja Episcopal Carismática do Brasil (IECB) → LOC 1987 | `data/Anglican` (variant `iecb-1987`) |
| `anglican-lusitana-1991` | Anglican → Igreja Lusitana (Portugal) → LOC 1991 | `data/Anglican` (variant `lusitana-1991`) |
| `anglican-reb-2027` | Anglican → Rede Episcopal Brasileira (REB) → LOC 2027 | `data/Anglican` (variant `reb-2027`) |
| `anglican-rec-2005` | Anglican → Reformed Episcopal Church → BCP 2005 | `data/Anglican` (variant `rec-2005`) |
| `ambrosian` | Catholic → Ambrosian Rite (Archdiocese of Milan) | `data/Ambrosian` |
| `eastern-catholic-ruthenian` | Catholic → Byzantine Catholic Church (Ruthenian) | `data/Orthodox` (variant `ruthenian`) |
| `maronite` | Catholic → Maronite Catholic Church | `data/Maronite` |
| `anglican-divine-worship-2021` | Catholic → Personal Ordinariates → Divine Worship 2021 | `data/Anglican` (variant `divine-worship-2021`) |
| `roman-1962` | Catholic → Roman Catholic → 1962 (Extraordinary Form) | `data/Roman/1962` |
| `roman` | Catholic → Roman Catholic → General Roman Calendar | `data/Roman` |
| `eastern-catholic-ugcc` | Catholic → Ukrainian Greek Catholic Church | `data/Orthodox` (variant `ugcc`) |
| `assyrian` | Church of the East → Assyrian Church of the East | `data/Assyrian` |
| `lutheran-norway` | Lutheran → Den norske kirke (Church of Norway) | `data/Nordic` (variant `norway`) |
| `lutheran-estonia` | Lutheran → Eesti Evangeelne Luterlik Kirik (Estonia) | `data/LutheranWorld` (variant `estonia`) |
| `elca` | Lutheran → ELCA (Evangelical Lutheran Church in America) | `data/ELCA` |
| `els-one-year` | Lutheran → ELS (Evangelical Lutheran Synod) → One-year | `data/ELS` (variant `one-year`) |
| `els-three-year` | Lutheran → ELS (Evangelical Lutheran Synod) → Three-year | `data/ELS` (variant `three-year`) |
| `lutheran-austria` | Lutheran → Evangelische Kirche A.B. in Österreich (Austria) | `data/LutheranWorld` (variant `ekd`) |
| `lutheran-ekd` | Lutheran → EKD (Evangelische Kirche in Deutschland) | `data/LutheranWorld` (variant `ekd`) |
| `lutheran-slovakia` | Lutheran → Evanjelická cirkev a. v. na Slovensku (Slovakia) | `data/LutheranWorld` (variant `slovakia`) |
| `lutheran-flm` | Lutheran → Fiangonana Loterana Malagasy (Madagascar) | `data/LutheranWorld` (variant `flm`) |
| `lutheran-denmark` | Lutheran → Folkekirken (Evangelical Lutheran Church in Denmark) | `data/Nordic` (variant `denmark`) |
| `lutheran-gkli` | Lutheran → GKLI (Gereja Kristen Luther Indonesia) | `data/LutheranWorld` (variant `gkli`) |
| `lutheran-hkbp` | Lutheran → HKBP (Huria Kristen Batak Protestan, Indonesia) | `data/LutheranWorld` (variant `hkbp`) |
| `lutheran-elct` | Lutheran → KKKT (Evangelical Lutheran Church in Tanzania) | `data/LutheranWorld` (variant `elct`) |
| `lutheran-poland` | Lutheran → Kościół Ewangelicko-Augsburski (Poland) | `data/LutheranWorld` (variant `poland`) |
| `lutheran-latvia` | Lutheran → Latvijas Evaņģēliski luteriskā baznīca (Latvia) | `data/LutheranWorld` (variant `latvia`) |
| `lutheran-lca` | Lutheran → LCA (Lutheran Church of Australia and New Zealand) | `data/RCLWorld` (variant `lca`) |
| `lutheran-iele` | Lutheran → IELE (Iglesia Evangélica Luterana en España) | `data/IELE` (variant `one-year`) |
| `lcc-one-year` | Lutheran → LCC (Lutheran Church–Canada) → One-year | `data/LCC` (variant `one-year`) |
| `lcc-three-year` | Lutheran → LCC (Lutheran Church–Canada) → Three-year | `data/LCC` (variant `three-year`) |
| `lcms-one-year` | Lutheran → LCMS (Lutheran Church–Missouri Synod) → LSB (2006) → One-year | `data/LCMS/LSB` (variant `one-year`) |
| `lcms-three-year` | Lutheran → LCMS (Lutheran Church–Missouri Synod) → LSB (2006) → Three-year | `data/LCMS/LSB` (variant `three-year`) |
| `lcms-lw` | Lutheran → LCMS (Lutheran Church–Missouri Synod) → LW (1982) | `data/LCMS/LW` |
| `lcms-tlh-one-year` | Lutheran → LCMS (Lutheran Church–Missouri Synod) → TLH (1941) | `data/LCMS/TLH` |
| `lcms-elhb-one-year` | Lutheran → LCMS (Lutheran Church–Missouri Synod) → ELHB (1912) | `data/LCMS/ELHB` |
| `lutheran-hungary` | Lutheran → Magyarországi Evangélikus Egyház (Hungary) | `data/LutheranWorld` (variant `hungary`) |
| `lutheran-finland` | Lutheran → Suomen ev.-lut. kirkko (Evangelical Lutheran Church of Finland) | `data/Nordic` (variant `finland`) |
| `lutheran-sweden` | Lutheran → Svenska kyrkan (Church of Sweden) | `data/Nordic` (variant `sweden`) |
| `ukrainian-lutheran` | Lutheran → Ukrainian Lutheran Church | `data/UkrainianLutheran` |
| `wels-one-year` | Lutheran → WELS (Wisconsin Evangelical Lutheran Synod) → One-year | `data/RCLWorld` (variant `wels-one-year`) |
| `wels-three-year` | Lutheran → WELS (Wisconsin Evangelical Lutheran Synod) → Three-year | `data/RCLWorld` (variant `wels`) |
| `lutheran-iceland` | Lutheran → Þjóðkirkjan (Evangelical Lutheran Church of Iceland) | `data/LutheranWorld` (variant `iceland`) |
| `methodist-gb` | Methodist → Methodist Church in Britain | `data/RCLWorld` (variant `methodist-gb`) |
| `methodist` | Methodist → United Methodist Church | `data/Methodist` |
| `moravian` | Moravian → Moravian Church in America | `data/RCLWorld` (variant `moravian`) |
| `oriental-armenian` | Oriental Orthodox → Armenian Apostolic Church | `data/Armenian` |
| `oriental-coptic` | Oriental Orthodox → Coptic Orthodox Church | `data/Coptic` |
| `oriental-ethiopian` | Oriental Orthodox → Ethiopian and Eritrean Orthodox Tewahedo | `data/Ethiopian` |
| `oriental-malankara` | Oriental Orthodox → Malankara Orthodox Syrian Church | `data/Syriac` (variant `malankara`) |
| `oriental-syriac` | Oriental Orthodox → Syriac Orthodox Church of Antioch | `data/Syriac` (variant `syriac`) |
| `eastern-orthodox` | Orthodox → Eastern Orthodox | `data/Orthodox` (variant `eastern-orthodox`) |
| `anglican-proposed-2025` | Orthodox → Western Rite Orthodox → Proposed BCP 2025 | `data/Anglican` (variant `proposed-2025`) |
| `scotland` | Reformed and Presbyterian → Church of Scotland | `data/RCLWorld` (variant `scotland`) |
| `presbyterian` | Reformed and Presbyterian → Presbyterian Church (U.S.A.) | `data/Presbyterian` |
| `reformed` | Reformed and Presbyterian → Reformed (RCA / CRC) | `data/Reformed` |

## The LCMS hymnals

The LCMS calendar is drawn from the hymnal a congregation uses, chosen in the
**Hymnal** menu; for LSB the **Lectionary** menu then offers its two
series. A hymnal with one calendar has no Lectionary menu: LW reads both its
lectionaries on one calendar, and TLH and the ELHB have the one-year series
only. (Any menu after Church with a single entry is left out the same way;
the Church menu then names the church's one book with it: "Church in Wales
(BCP 1984)", "ACNA (Anglican Church in North America, BCP 2019)".)

- **LSB** — *Lutheran Service Book* (2006), the one-year and three-year
  series (`data/LCMS/LSB`).
- **LW** — *Lutheran Worship* (1982), "The Church Year" (pp. 8–9): one
  calendar for both its lectionaries with its suggested colors (the first where it gives two):
  purple Advent, the Baptism of Our Lord and the Transfiguration framing the
  Sundays after the Epiphany, a black Ash Wednesday, a scarlet Holy Week, the
  Sundays *of* Easter, the Holy Trinity, the Sundays after Pentecost and the
  Sunday of the Fulfillment; its minor festivals by date; and its three Times
  (of Christmas, of Easter, of the Church) on the outer ring (`data/LCMS/LW`).
- **TLH** — *The Lutheran Hymnal* (1941), "The Calendar" (p. [3]): the
  one-year series, with the Sundays after Christmas and after New Year, one to
  six Sundays after the Epiphany ending with the Transfiguration, the
  pre-Lenten Sundays, the Sundays in Lent and after Easter by their Latin
  names (on by default), Easter Monday and Tuesday, Whitsunday with Monday and
  Tuesday of Whitsun week, the Feast of the Holy Trinity and 22 to 27 Sundays
  after Trinity, and its red-letter days (`data/LCMS/TLH`).
- **ELHB** — *Evangelical Lutheran Hymn-Book* (Concordia, 1912; the American
  Lutheran Publication Board printing of 1909 on archive.org), the synod's
  first English hymnal: its calendar and the headings of its Introits and
  Collects. Christmas and the Second Christmas Day, New Year's Eve and Day,
  the Sundays after Christmas and New Year, up to six Sundays after the
  Epiphany (no Transfiguration Sunday; the sixth has its collect), the
  pre-Lenten Sundays, Lent with its Latin names, Monday to Thursday in Holy
  Week, Easter Monday, Monday in Whitsun-week, the Festival of the Trinity,
  up to 27 Sundays after Trinity, the Reformation and the apostles' days
  (`data/LCMS/ELHB`).

TLH and the ELHB print no colors. Both are drawn in those of the *Common
Service Book* (1917, p. 296), the book of the same Common Service tradition
that gives them: violet in Advent and Lent, black on Good Friday; white from
Christmas Eve through the Epiphany season, from Easter to Whitsunday, on the
Transfiguration, the Presentation, the Annunciation, the Visitation, St.
Michael, and the Festival of the Trinity and its octave; red at Whitsuntide,
on the apostles' and evangelists' days (St. John excepted), martyrs' days,
All Saints' and the Reformation; green from Septuagesima to Ash Wednesday and
through the Trinity season.

The three folders were first written by a one-off script, since removed.

Each LCMS hymnal also has its readings (`readings.csv`; the page lists them
under the day, see [readings.csv](#readingscsv)):

- **LSB**: the three-year series (Old Testament, Psalm, Epistle, Gospel for
  Years A, B and C, the Propers after Pentecost by their dates), the one-year
  series, the feasts and festivals, and the Daily Lectionary (pp. 299–304),
  from Year At A Glance, the Wartburg Project, LutheranLectionary.org and CPH
  copies of the Daily Lectionary.
- **LW**: its one-year and three-year series (with the last three Sundays' own
  propers) and its minor festivals, each with its Psalm, from the book's
  Propers of the Day (pp. 10–122); the one-year propers are their own set,
  "One-Year Series", beside the year's three-year set. The Daily Lectionary is
  pp. 295–299. LW's occasions without a date (Mission Festival, Harvest
  Festival ...) are left out.
- **TLH**: the Epistles and Gospels of its propers and minor festivals (TLH has
  no Old Testament lessons).
- **ELHB**: its Epistles and Gospels, its two Old Testament lessons (from the
  Historical and the Poetical Books) and two New Testament lessons (from the
  Gospels and the Epistles) for each Sunday and festival, and its Table of
  Lessons for Morning and Evening for every day of the year.

LSB's Daily Lectionary prints, beside each day's two readings, an optional
third in italics "for reading more of the Bible"; those are their own set,
**Daily Lectionary: Additional Reading**, with their own Readings box
(*Additional readings*). On the days LSB gives none, the set has the
additional reading of the draft Daily Lectionary the data were checked
against (St. John's, Austin), which fills every day from the Apocrypha
(Sirach, the Maccabees, Tobit, Judith, Wisdom, Baruch ...), the Lutheran
Confessions (the Smalcald Articles and Treatise in Easter, the Augsburg
Confession in Pentecost week, the Solid Declaration from late July to
November, the Apology from late January to March) and the Catalog of
Testimonies. Its table of psalms (p. 304), a morning psalm and two
evening psalms for each weekday of Advent, Lent and Easter and of four
"General" weeks for the season of Epiphany and the Time of the Church, with
the Christmas days by date, is the set **Psalms for Daily Prayer**, under the
box *Psalm table*. LSB says only that the General weeks "may be repeated as
often as necessary"; here each of the two runs begins at Week 1 and goes on
in turn, Week 1 to 4 and round again: in Epiphany the week 7 January falls in
is Week 1 and the next Sunday begins Week 2, and after Pentecost Holy Trinity
begins Week 1.

Every LCMS calendar, and Lutheran Church–Canada's, also has **Reading the Word
of God** (`data/readings/plan-rwg.csv`), the daily Bible reading plan the LCC,
LCMS and North American Lutheran Church published for 2018–2020 and again for
2021–2023: an Old Testament reading, a psalm and a New Testament reading for
each day, through the Old Testament once in three years and the Psalms and New
Testament twice, with readings of their own on fourteen festivals. It is kept
by the calendar year, not the church year (see [readings.csv](#readingscsv)),
under its own box, *Bible reading plan*.

### Wilhelm Loehe's calendars of saints

Two more LCMS entries, **Loehe Martyrologium (1868)** and **Loehe Kirchenbuch
(1859)** (`data/LCMS/Loehe`, variants `1868` and `1859`), give the calendars
of saints of Wilhelm Loehe (1808–1872), the Neuendettelsau pastor whose
missionaries helped found the synod, as Benjamin T. G. Mayes translated them
(2001): the *Calendarium sanctorum* of his *Haus-, Schul- und Kirchenbuch*
(1859), with two or three names for most days and the Epistles and Gospels of
its feasts, and the shorter, corrected list of his *Martyrologium* (1868),
about one name a day. Loehe gives only the saints and the fixed feasts; the
Sundays, movable feasts and seasons are the historic one-year calendar's, as
the Evangelical Lutheran Hymn-Book gives them (copied from `data/LCMS/ELHB`),
and the colors the Common Service Book's, as for the ELHB. A name on the wheel
leaves out the entry's dates and Bible references, which its full name keeps.
Links are as for the LCMS: CPH's post where LSB keeps the saint, else a
Wikipedia article, else a Wikipedia search for the name and its place.

H. R. Curtis's *Daily Divine Service Book* (2010), which builds propers for
every day on Loehe's calendar and LSB, is under copyright and is not drawn on.

## The ELS, IELE, LCC and WELS

**Lutheran Church–Canada** uses Lutheran Service Book as the LCMS does, in
both series; only Thanksgiving differs (the second Monday in October).

**The Iglesia Evangélica Luterana en España** (IELE) keeps Lutheran Service
Book's one-year series in Spanish, as its *Calendario Litúrgico de la Iglesia,
Serie Anual* (2025–26) gives it: the readings and propers are LSB's set for
set, the feasts and festivals without the commemorations, and the colors are
the calendar's (violet Advent with a rose Gaudete, white Holy Saturday, red
Pentecost Monday and Tuesday). The Bible citations keep LSB's English book
names; the Bible links open the Reina-Valera 1995. LSB's daily lectionary is
left out, since the IELE's hymnal, *Himnario Luterano* (2021), has its own.

**The Evangelical Lutheran Synod** (Evangelical Lutheran Hymnary) is taken
from its own calendars, *ELS Historic*, *ELS 3-year* and *ELS Saint Days*
(els.org, *Lectionary Calendar*), for 2016–2028. The three-year series is the
LCMS one. The one-year series differs:

- the **Baptism of Our Lord** is kept on Quinquagesima, the Sunday before Ash
  Wednesday; the Sundays after the Epiphany are counted from the first Sunday
  after 6 January;
- the **Transfiguration** is the last Sunday after the Epiphany, ten weeks
  before Easter, but only when that is at least the third Sunday after it
  (not in 2016 or 2027). The synod's printed wheel for 2023–24 keeps it on 21
  January 2024, where the 2024 Google calendar has a plain "Epiphany 3";
- Exaudi is the **Sunday after the Ascension**;
- **St. Michael and All Angels** takes the Sunday it falls on (29 September
  2024), and the year ends with the **Third-Last**, **Second-Last** and
  **Last Sunday of the Church Year**; All Saints' Sunday wins when it falls on
  the third-last, as in 2016, 2021 and 2022. (The Google calendars from 2023
  number the third-last after Trinity instead; the printed wheel names it.)

Reformation Sunday (the last Sunday of October, red) and All Saints Sunday
(the first of November, white) are kept in full color. From 2026 the
Confession of St. Peter is on 22 February.

The colors are those of the synod's **ELS Liturgical Calendar A.D. 2023–2024**,
a wheel much like this one: blue in Advent (violet is allowed) with rose for
Gaudete and Laetare; gold for Christmas Day and Easter Day; white for the
Sundays after the Epiphany, the Transfiguration, the Baptism, Holy Saturday,
Michaelmas, All Saints and the Last Sunday; violet in Lent; black on Good
Friday; red at Pentecost and the Reformation; green after Trinity and on the
second- and third-last Sundays. Where the wheel shades one color into another,
the outer color is the cell's and the inner its lower half: Septuagesima and
Sexagesima green over violet, Ash Wednesday violet over black, Palm Sunday
violet over scarlet, and Maundy Thursday violet over white. The three-year
series uses the same colors.

**The Wisconsin Evangelical Lutheran Synod** (Christian Worship 2021) keeps
the Revised Common Lectionary's year without numbered propers: the
Reformation on the last Sunday of October, All Saints on the first of
November, and the Last Sunday of the Church Year (Christ the King).

Before the church year 2021–22 the synod used **Christian Worship (1993)**,
and so does this calendar (`year lt 2021`), from WELS's *Planning Christian
Worship* tables and Bible-study guides. Its last four Sundays are **End
Time**: Reformation Sunday (red), Last Judgment (red), Saints Triumphant
(white) and Christ the King (white). The Sundays after Pentecost are counted
from Holy Trinity and the last of them are dropped. Advent is blue (or
purple), Ash Wednesday black (or purple), Maundy Thursday purple, Good Friday
black and Easter white (or gold). Its readings have the Psalm of the Day, and
the supplemental lectionary of Christian Worship Supplement (2008) is shown as
a second set. Year A's Pentecost 21–23 have no Psalm in the sources, and its
Pentecost 24 (only in years with the earliest Easter) is in none of them: its
readings are inferred (Malachi 2:1–2, 4–10; 1 Thessalonians 2:8–13; Matthew
23:1–12, the Lutheran three-year series' Proper 26, as CW 1993 has in Years B
and C) and the set is titled as inferred. The Psalms of Pentecost 21–24 A are
inferred as well (23, 96, 1, 43: the psalm the other lectionaries with these
Gospels agree on) and marked so.

Christian Worship (2021) also has a **one-year series** (`wels-one-year`,
the Lectionary menu's One-year beside Three-year). It has its readings from
the Wartburg Project and its psalms from the hymnal's Psalm Appointments:

- The Sundays carry the Latin names the hymnal gives (Ad Te Levavi,
  Invocavit, Misericordia Domini, Exaudi), shown by default.
- There is no Baptism of Our Lord. The Transfiguration is the last Sunday
  after the Epiphany, followed by Septuagesima, Sexagesima and
  Quinquagesima, which are green like the Sundays around them because the
  hymnal gives no colors.
- The Sundays after Pentecost are counted after Trinity, from one.
- Reformation and All Saints are named on their Sundays beside the Sunday
  after Trinity, which keeps its readings, since the series gives them none
  of their own.
- The Last Sunday of the Church Year has only its psalm (45), since the
  Wartburg Project lists nothing for it.

The series is shown as the 2021 hymnal has it for every year, including
those before it.

## The churches of the Revised Common Lectionary

The Episcopal, ELCA, United Methodist, Presbyterian and Reformed calendars
share the year of the Revised Common Lectionary: Advent, Christmas, the
Epiphany and the Baptism, the Sundays after the Epiphany ending with the
Transfiguration, Lent, Holy Week, the fifty days of Easter to Pentecost,
Trinity Sunday, the Sundays after Pentecost with their Propers, and Christ the
King. They differ in names, in colors, and in the days they add:

| | Advent | Holy Week | Maundy Thursday | Good Friday | Sundays after Pentecost |
|---|---|---|---|---|---|
| Episcopal | blue | red | white | none | Proper *n* |
| ELCA | blue | scarlet | scarlet and white | none | Lectionary *n* |
| Methodist | purple | purple | purple | none | Proper *n* |
| Presbyterian | purple | purple | purple and white | none | Proper *n* |
| Reformed | purple | purple (red Palm Sunday) | none | none | Proper *n* |

All of them (and the Methodist Church in Britain, the Moravian Church, the
Church of Scotland and the LCA) list the readings of the Revised Common
Lectionary under the day (`data/readings/rcl.csv`, from the Vanderbilt
Divinity Library): Old Testament, Psalm, Epistle and Gospel for Years A, B
and C, with both series after Pentecost (semicontinuous and complementary;
the Episcopal Church's Track 1 and Track 2), the Christmas propers, Holy
Week, the Easter Vigil, the festivals the RCL provides for, and Thanksgiving
Day for the American churches; and on weekdays the RCL Daily Readings
(`data/readings/rcl-daily.csv`: a psalm and two lessons, Thursday to Saturday
preparing for the coming Sunday and Monday to Wednesday reflecting on the
past one), from Vanderbilt's three years (2025–28) and, for the weeks those
years lack, from liturgical-calendar.com's RCL Daily Readings. The ELCA, Episcopal and other books make
small changes of their own to the RCL that are not shown.

- **Episcopal:** the Holy Days of the 1979 Prayer Book (colored in the lower
  half of the cell) and the lesser feasts of *Lesser Feasts and Fasts*. The
  Prayer Book's Daily Office Lectionary is listed every day under Morning and
  Evening Prayer: the two years' psalms for each office and three lessons
  (Year One from Advent 2024, 2026 ..., Year Two from Advent 2025 ...), the
  Eves of the feasts, Holy Week and Easter Day by office, and the Holy Days'
  own psalms and lessons at both offices.
- **ELCA:** the lesser festivals and commemorations of *Evangelical Lutheran
  Worship* (2006), with those added since. Reformation Sunday and All Saints
  Sunday are kept as the LCMS calendar keeps them.
- **Methodist:** the festivals of the *Book of Worship*, Aldersgate Day, and
  the special Sundays of the *Book of Discipline* that have set dates (Human
  Relations Day, UMCOR Sunday, Native American Ministries Sunday, Peace with
  Justice Sunday, World Communion Sunday and the rest). The Sundays each
  annual conference dates for itself are left out.
- **Presbyterian:** the festivals of the *Book of Common Worship* (2018) and the
  four special offerings. Colors follow the PC(USA)'s planning calendars.
- **Reformed:** colors follow the Reformed Church in America's calendar with
  liturgical colors. The **Special days** menu lays the Christian Reformed
  Church's Canadian observances over it, from its offering schedule: Sanctity
  of Human Life Sunday, the Annual Day of Prayer, Refugee Sunday, Canadian
  Thanksgiving, Remembrance Day and the rest.

Three more churches of the Revised Common Lectionary share `data/RCLWorld`
(with WELS and the Lutheran Church of Australia, described with the
Lutherans):

- **Moravian Church in America:** its lectionary calendar (moravian.org) with
  its colors, and the Moravian festivals: 1 March (the Unity's founding), 12
  May (the Brotherly Agreement), 17 June, 6 July (Jan Hus), 13 August (the
  renewal of 1727), 17 August, 16 September and 13 November (the Chief Elder
  festival). All Saints is kept on the Sunday when 1 November is one.
- **Methodist Church in Britain:** the Sundays in Ordinary Time numbered as in
  the Roman calendar, the Sunday before Lent (the Transfiguration) and the
  Sunday before Advent (Christ the King); Covenant Sunday (the first Sunday
  of January), Aldersgate Sunday (the Sunday before 24 May), Wesley Day and
  the Watchnight.
- **Church of Scotland:** the year of its *Weekly Worship*, with Remembrance
  Sunday (the second Sunday in November) and St Andrew's Day, and the
  optional colors the Church Service Society describes.

## The Anglican prayer books

The **Anglican** tradition lists the churches, and the **Prayer book** menu picks the
book. The historic books (1662, 1928, 1962 and the Reformed Episcopal Church's)
keep the Sundays after the Epiphany, Septuagesima, Sexagesima and
Quinquagesima, the Sundays after Easter and after Trinity, and the Sunday next
before Advent. ACNA 2019 follows the Revised Common Lectionary year with
Sundays after Trinity and their Propers, and reads its own Sunday, Holy Day,
and Commemoration Lectionary (BCP 2019, pp. 716-732): three years of four
readings, the holy days, the Ember and Rogation Days and the national days. Common Worship keeps the Epiphany
season white until the Presentation, numbers the Sundays before Lent and
before Advent, and ends with Christ the King. BCP 1979 (`episcopal`) is the
Episcopal calendar.

BCP 1962 also has its Table of Lessons for Morning and Evening Prayer: two
years, Year I when Advent Sunday falls in an even year, each day's first and
second lessons at both Offices, and the holy days' own lessons for First
Evensong (on the eve), Morning Prayer and Evening Prayer.

BCP 1928 has the 1943 lectionary's Table of Psalms and Lessons for the
Christian Year: each day's psalms and two lessons at Morning and Evening
Prayer, the Sundays with two or three sets (the psalms and lessons on one line
go together), the Sundays after Trinity giving way to the three weeks before
Advent, and the fixed holy days' psalms and lessons for the Eve, Morning and
Evening, with the book's footnoted changes when the day falls after
Septuagesima, after Easter or near Trinity.

REC 2005 has the Epistles and Gospels of BCP 1928 and its own Table of Psalms
and Lessons for the Christian Year (from An Australian Prayer Book 1978, with
the 1945 American table's Sunday psalms and lessons): the Sundays with up to
five sets, one to a row of the table, each weekday's psalms and lessons at
Morning and Evening Prayer, the Ember Days, the fixed holy days (Eve, Morning
and Evening) and Independence Day, Thanksgiving Day and the End of the Year.

The books prescribe no colors. The historic books use the customary Western
ones: purple Advent, Pre-Lent and Lent, red Holy Week and Whitsuntide, white
festivals, green otherwise. Each book's fixed holy days and commemorations
come from the calendars at anglicanlectionary.com.

**Common Worship** is taken from the Church of England's own pages (*The
Church's Year*: the Calendar, the Rules and the Lectionary). Principal Feasts
color the whole day, Festivals its lower half; Lesser Festivals are set in
roman and Commemorations in italics, as the Calendar prints them. The colors
are the Rules': purple in Advent (or blue; rose on the Third Sunday), purple in
Lent (or the Lent array; rose on the Fourth Sunday), white for Maundy Thursday
(or red), red for the Good Friday liturgy with the hangings removed, no color
on Easter Eve, and red or green from All Saints to Advent. The readings are
the Principal, Second and Third Service lectionary and the Daily Eucharistic
Lectionary.

The Rules' precedence is kept. A Festival on a Sunday of Advent, Lent or
Eastertide, or on a Principal Feast or Principal Holy Day, moves to the next
free day (Andrew on Advent Sunday to the Monday); one between Palm Sunday and
the Second Sunday of Easter moves to the Monday after it (George, then Mark on
the Tuesday; the Annunciation before Joseph). A Festival on another Sunday is
kept on it. A Lesser Festival or Commemoration on a Sunday, a Festival or in
Holy Week and Easter Week is left out that year. A moved feast takes its
readings, and its eve's, with it. When 6 January is a Sunday it is the First
Sunday of Epiphany, and the Baptism of Christ the Second. The Rules let a
parish keep three Principal Feasts on a nearby Sunday instead: the Epiphany on
the Sunday between 2 and 8 January, Candlemas on the Sunday between 28 January
and 3 February, and All Saints on the Sunday between 30 October and 5 November.
They state no preference (parishes often take the Sunday, cathedrals the
date), so both are shown, as the LCMS Reformation Day is: the date in full, and
the Sunday as "The Epiphany (observed)", "Candlemas (observed)" or, in Common
Worship's own words, "All Saints' Sunday", white in its lower half, with the
feast's readings beside the Sunday's. When the Epiphany is kept on Sunday 7 or
8 January, the Baptism of Christ is also shown on the Monday, "(observed)".

The Prayer book menu also offers:

- **Church in Wales 1984**, with the Welsh saints. From Advent 2003 it follows
  the Church in Wales's *New Calendar and the Collects* (2003), the calendar of
  its lectionary booklets: Sundays of Epiphany to the Presentation, Sundays
  before Lent, of Lent and of Easter, after Trinity (to the Last Sunday after
  Trinity, Bible Sunday), and the Kingdom season from All Saints (the First to
  Third Sundays of the Kingdom and Christ the King, the Fourth), with Thomas on
  3 July, the Visit of the Virgin Mary on 31 May, Thanksgiving for Holy
  Communion and the newer Welsh and other commemorations. The 1984 book's year
  (Septuagesima, Thomas on 21 December, the Visitation on 2 July) holds before. For
  2025-26 it also has the booklet's Second and Third Services, Daily
  Eucharist and Morning and Evening Prayer.
- ***Divine Worship* (2021)**, the Personal Ordinariates' book: the Anglican
  year with Septuagesima and the Sundays after Trinity, plus the Holy Family,
  the Baptism of the Lord, Corpus Christi, the Sacred Heart and Christ the
  King on the Sunday next before Advent, named as *Divine Worship: The
  Missal* names them (the Sundays of Advent, of Christmas and of Easter, the
  Second to the Seventh). The Missal's Table of Liturgical Days settles which
  day is kept (`precedence,roman`): All Saints replaces a Sunday after
  Trinity, a saint's feast on a Sunday is omitted. This is the Missal's
  universal calendar: the Ordinariate of the Chair of St Peter keeps the
  Epiphany and Corpus Christi on Sundays, and the Chair of St Peter as its
  Solemnity of Title. (The Roman calendar's Personal jurisdiction menu lays the
  ordinariates' own days over the Roman year instead.) Its readings are the
  Roman Lectionary's, with the citations of the Ordinariate's Ordo for
  2025-26 (its Coverdale psalms and the RSV-2CE's numbering) for Year A and
  Advent of Year B; Years B and C have no psalm yet. For 2025-26 (to 31
  December 2026) it also has the Ordo's weekday Mass readings and the Daily
  Office's psalms and lessons at Morning and Evening Prayer.
- **Proposed BCP 2025**, the Western Rite Orthodox book. It keeps Easter by
  the Julian paschalion, as the Orthodox do.
- The **Portuguese-language** books, with their calendars in Portuguese:
  - IARB 1662 (Brazil's Reformed Anglican Church), a translation of 1662;
  - Igreja Lusitana 1991 (Portugal);
  - IEAB 2015, REB 2027, LOCb 2008, IECB 1987 and IAB 2021 (Brazil).

The Church in Wales follows its 2011 color scheme from the 2011–12 year on:
the Sunday next before Advent as Christ the King (white), red for Holy Week,
Good Friday and Easter Eve (purple or black permitted), red for the
Conversion and the Martyrdom of St Paul, purple (or black) for All Souls, and
green (or red) from All Saints to Advent. The 1984 book's colors hold for the
years before.

The fixed days of these ten books come from their calendars at
anglicanlectionary.com, keeping that site's feast names. Its Sunday names and
colors are generic, so the Sundays follow the book's structure instead.

## The Roman calendar of 1962

**Roman Catholic 1962 (Extraordinary Form)** is the General Roman Calendar of
1960, used with the 1962 Missal. Its saints' days are transcribed from the
decree of January 1960 (Acta Apostolicae Sedis), from Wikipedia's transcription,
by a one-off script since removed. Names are in English, with the
Latin for the Sundays when **Latin names** is on.

The year has the shape the modern calendar replaced: Advent with its Ember
days; the Christmas octave, the Holy Name (the Sunday 2–5 January, otherwise
2 January), the Holy Family on the Sunday after Epiphany and the Baptism on
13 January; Sundays after Epiphany; Septuagesima, Sexagesima and
Quinquagesima; Lent with Passion Sunday; the octaves of Easter and Pentecost;
the Rogation days; Sundays after Pentecost, with the Sundays after Epiphany
left over in winter resumed in November before the Twenty-fourth and last;
the September Ember days; Christ the King on the last Sunday of October; and
All Souls on 2 November (3 November when the 2nd is a Sunday), in black.

The 1960 classes are drawn onto the ranks the engine's [Roman
precedence](#roman-precedence) already uses, so the same rules move and drop
the days: I class feasts are transferred when impeded (the Annunciation on
Maundy Thursday 2027 goes to 5 April), II class feasts of the Lord replace a
II class Sunday, III class feasts in Lent become commemorations, and a
feast of the Lord or a I class feast on a Sunday hides the Sunday's own name.

## The Ambrosian Rite

The Archdiocese of Milan keeps its own rite, from the *Messale Ambrosiano* and
the diocese's liturgical calendar (chiesadimilano.it), in Italian:

- **Avvento** has six Sundays, from the Sunday after St Martin (11 November);
  the sixth is the **Domenica dell'Incarnazione** (the Divine Motherhood), in
  white. When that falls on 17 December, 24 December is a Sunday too, the
  **Domenica prenatalizia**.
- Christmas, the Sunday in its octave and the Sunday after it, the Epiphany,
  the Baptism of the Lord on the following Sunday, the Sundays after the
  Epiphany with the Holy Family on the last Sunday of January, and the
  *Penultima* and *Ultima* Sundays after the Epiphany.
- **Quaresima** begins on the Sunday six weeks before Easter (there is no Ash
  Wednesday), its Sundays named for the Samaritan woman, Abraham, the man
  born blind and Lazarus; Palm Sunday and the **Settimana Autentica** in red.
- Easter, its Sundays, the Ascension, Pentecost and the Holy Trinity; the
  Sundays after Pentecost (in red) up to the Sunday before the Martyrdom of
  St John the Baptist (29 August, or that day itself when it is a Sunday); the Sundays after the Martyrdom; the
  **Dedication of the Cathedral** on the third Sunday of October and the
  Sundays after it; and Christ the King on the last Sunday before Advent.
- Colors: *morello* (a dark red-violet) for Advent and Lent, white, red and
  green as the missal gives them.
- The solemnities and feasts of the calendar, and the saints' feasts that
  have readings of their own (the Apostles and Evangelists, St Lawrence, St
  Benedict, St Martin, Sant'Anatalo and the rest), in the lower half of their
  cell: red for apostles, evangelists and martyrs, white for the others (as
  GCatholic's Common Ambrosian Calendar colors them). A Sunday, the Ascension,
  Corpus Domini, Holy Week and the Easter octave take their place.

The readings are the *Lezionario Ambrosiano*'s, from the Archdiocese's own
tables of it (the Ordo of its three books, for Sundays and feasts and for
weekdays):

- Sundays and feasts in three years, **A**, **B** and **C** as the Roman
  (A is the year beginning in November 2025); weekdays in two, **I** and
  **II** (I is the year beginning in an even year). Each Sunday also has its
  **Gospel of the Resurrection**, read at the vigil; the weekdays of Lent and
  some feasts have more than one reading of a kind, given in order.
- The kinds: *Lettura* (Reading), *Salmo*, the weekdays' second reading from
  the prophets or Proverbs (also Reading), *Epistola*, the *Canto al Vangelo*
  (Verse before the Gospel, listed with the propers, since it is sung) and
  the *Vangelo*.
- The weeks after the Epiphany are counted from the Baptism, so the week after
  the Holy Family keeps its weekdays; the Saturday before the Dedication and
  the *Sabato in traditione symboli* before Palm Sunday have their own.
- The saints' days and feasts kept by the date (St Joseph, the Apostles, the
  Assumption, St Charles, St Ambrose's ordination and the rest, 40 days) come
  from the Archdiocese's readings of each day, as read in at least two years
  from 2019; their psalms are cited without verses there. 16 December has
  its own readings every year, in place of the weekday of Advent.
- The psalms are numbered as in the Hebrew Bible (the Lectionary uses the
  Greek and Latin numbers: its *Salmo 50* is Psalm 51), with the psalms the
  Greek divides otherwise (9, 114–115, 146–147) given their Hebrew verses.

## The Nordic Lutheran churches

The Nordic churches are in the **Lutheran** tradition: Sweden, Norway,
Denmark and Finland. Each church's days are named
in its own language and taken from its church year as the Swedish, Norwegian,
Danish and Finnish Wikipedias give it. All four keep the old pattern:
Septuagesima (or its counterpart), a Sunday before Lent, Sundays numbered
after Trinity (or, in Finland, after Pentecost), and an end of the year that
looks toward the Last Judgment.

Several feasts move to a nearby Sunday or Saturday:

| | Sweden | Norway | Denmark | Finland |
|---|---|---|---|---|
| Candlemas | Sunday Feb 2–8 (the Sunday before if that is the Sunday before Lent) | — | — | as Sweden |
| Annunciation | Sunday Mar 22–28 (the Sunday before Palm Sunday if later) | as Sweden | 5th Sunday in Lent | as Sweden |
| Epiphany | Jan 6 | Sunday Jan 2–8 | Sunday Jan 2–8 | Jan 6 |
| Midsummer | Saturday Jun 20–26 | — | — | Saturday Jun 20–26 |
| St John the Baptist | Sunday Jun 21–27 | — | — | (Midsummer Day) |
| St Michael | Sunday Sep 29–Oct 5 | — | — | Sunday Sep 29–Oct 5 |
| All Saints | Saturday Oct 31–Nov 6 | first Sunday of November | first Sunday of November | Saturday Oct 31–Nov 6 |

Other named Sundays: Sweden's Apostles' Day (the 5th Sunday after Trinity,
left out when it falls on St John's day, as in 2027), Transfiguration (7th after Trinity)
and Thanksgiving (2nd Sunday of October); Norway's Day of Repentance and
Prayer (the Sunday before All Saints), Apostles' Day (the 6th Sunday in
Trinitytide), St Olav's Day (July 29) and Christ the King; Finland's
Apostles' Day, Transfiguration and Reformation Day (the 6th, 8th and 22nd
Sundays after Pentecost). Colors are each church's: violet Advent and Lent
(Sweden and Finland begin Advent in white), black Good Friday in Sweden,
Denmark and Finland, white feasts, red for St Stephen and Pentecost, green
otherwise. Denmark's Great Prayer Day, no longer a public holiday since 2024, is left
out.

## Lutheran churches worldwide

These churches are in the **Lutheran** tradition. All keep the historic one-year order, each in
its own language.

**Germany (EKD).** The Protestant churches in Germany (EKD, VELKD, UEK) as the
*Ordnung gottesdienstlicher Texte und Lieder* of 2018 sets the year, from the
German Wikipedia's *Perikopenordnung* and *Liturgische Farbe*:

- Christfest I and II, the 1st and 2nd Sundays after Christmas, Altjahrsabend
  and Neujahrstag; Epiphanias on 6 January.
- The Epiphany season ends with the **Letzter Sonntag nach Epiphanias**,
  always the Sunday before 2 February (a week earlier when Easter is so early
  that this Sunday would be Estomihi).
- One to five **Sundays before Passiontide**, counted backwards: the 5th and
  4th, Septuagesimä, Sexagesimä and Estomihi.
- Invokavit to Judika, Palmsonntag; Quasimodogeniti to Rogate, Exaudi.
- Sundays after Trinitatis, with the Israelsonntag (the 10th) and
  Erntedankfest (the first Sunday after Michaelis), up to the
  Drittletzter and Vorletzter Sonntag, Buß- und Bettag on the Wednesday
  before the Ewigkeitssonntag, and the Ewigkeitssonntag (Totensonntag).
- The apostles', evangelists' and Marian days and the days of remembrance on
  their dates, in `feasts.csv`.
- Colors: violet Advent and Passiontide, white Christmas to the Last Sunday
  after Epiphany and the Easter season, green the pre-Passion Sundays and
  Trinitatis season, red Pentecost, Reformation Day, martyrs and apostles;
  black on Good Friday.

**Indonesia (HKBP).** The Batak Protestant Christian Church, the largest
Lutheran church in Indonesia, from its own almanac (hkbp.or.id/almanak, 2025
and 2026), with the Batak names and the color it gives each day: Advent I–IV;
Parpunguan Bodari (Christmas Eve), Pesta Natal I and II, the Sunday after
Christmas, the year's-end service and the New Year; Epiphanias (*Hapapatar*)
and the Sundays after it, white; Septuagesima to Invocavit green, Reminiscere
to Palmarum violet; Good Friday blue; Easter, Hananaek Tuhan Jesus (the
Ascension) and Pentakosta I and II; the Sundays after Trinitatis (*Dung
Trinitatis*) in green, the last of them the *Ujung Taon Parhuriaon*, the end of
the church year. Reformation Day (31 October) and the church's anniversary
(7 October) are feasts.

**Indonesia (GKLI).** The Indonesian Christian Lutheran Church, from its
*Almanak GKLI 2026*: the heading of each day, its list of Sunday names and the
altar color it gives for each Sunday and feast. Advent I–IV in violet; Malam
Natal, Natal I and II, the Sunday after Christmas, the year's-end service, New
Year and the Sunday after it, Epiphanias and the Sundays after it, all white;
Septuagesima, Sexagesima and Estomihi in green; the five Passion Sundays
(Invocavit to Judika) in violet; **Palmarum in red**; Kamis Putih; Jumat Agung
in black; Paskah I and II and the Sundays to Exaudi in white; Pentakosta I and
II in red; Trinitatis in white; the Sundays after Trinitatis in green; and the
**Minggu Akhir Tahun Gereja** in black, when the dead are remembered. Reformation
Day is kept on 31 October. The center artwork is the Luther rose.

**Madagascar (FLM).** The Malagasy Lutheran Church, from the weekly Sunday
titles of its *Hira sy Filazantsara* (2020–2024): Alahady I–IV amin'ny
Advento, Noely, the Sunday after Christmas, Alahadin'ny Epifania (the first
Sunday of January), the Sundays after Epiphany, then the nine Sundays
before Easter counted down (*Alahady IX … II mialoha ny Paska*) to
Alahadin'ny Sampan-drofia (Palm Sunday), Andro Paska I and II, the Sundays
after Easter, Fiakarana (Ascension), Pentekosta I and II, Alahadin'ny
Trinite and the Sundays after Trinity to the end of the year. The 2021
titles still followed an older count before Easter (the Sundays after
Epiphany ran on to Quinquagesima); the 2022 pattern is used. Colors as for
HKBP.

**Poland.** The Evangelical Church of the Augsburg Confession in Poland took
over the German order from Advent 2018, so its year is Germany's with the
Polish names its Sunday pages use (*niedziela pasyjna*, *niedziela przed
postem*, *Niedziela Wieczności*) and the German colors. Ash Wednesday is the
*Dzień Pokuty i Modlitwy*; there is no November day of repentance. Harvest
thanksgiving follows the German rule.

**Iceland.** The Evangelical Lutheran Church of Iceland (Þjóðkirkjan), from the church year it publishes with
each day's color: Advent begins in white (rose on the 4th Sunday); the Sunday
between Christmas and New Year and between New Year and Epiphany; the
**Last Sunday after Epiphany** ten weeks before Easter; the two Sundays of
*níuviknafasta* and the Sunday before Lent; the Annunciation on the Sunday
22–28 March (the 5th Sunday in Lent when that would be Palm Sunday or
later); the first day of summer (the Thursday after 18 April); Sundays after
Trinity; All Saints on the first Sunday of November and Mission Day on the
second; the second-to-last and last Sundays of the church year. Reformation Day is
31 October, kept on the last Sunday in October: when the 31st is not a
Sunday, that Sunday keeps its number after Trinity, with *Siðbótardagurinn*
beneath it and red in its lower half. Trinity
Sunday and Mission Day are red, as the color rule of the 1981 service book
gives them (Morgunblaðið, 25 November 2001); Good Friday is violet (the
church's site gives violet or black; violet is now the more common, black the
older use).

**Estonia.** The Estonian Evangelical Lutheran Church, from its description
of the church year and the colors in its sermon helps: Advent begins in white;
one or two Sundays of Christmastide (*Jõuluaja 1. pühapäev*, Holy Family, and
*Jõuluaja 2. pühapäev* when the first falls by 31 December, as in 2024–25 and
2025–26); the Baptism of Christ on the 1st Sunday
after Epiphany; three Sundays before Lent; Sundays of Eastertide counted from
Easter (White Sunday is the 2nd, Prayer Sunday the 6th); Sundays counted after
Pentecost, with Apostles' Sunday (6th) and the Transfiguration (8th); Harvest
Thanksgiving on the 2nd Sunday of October and Mission Sunday on the 4th;
Watchfulness Sunday and Eternity Sunday. Good Friday is black (the church gives
red or black). The names follow the church's own calendar posts at
e-kirik.eelk.ee for 2025–26.

When 28 December, 2 February, 24 June, 29 September, 31 October or 2 November
falls on a Sunday in Estonia, the feast (Holy Innocents, Candlemas, St John's
Day, Michaelmas, Reformation Day or All Souls) is kept on that Sunday in place
of its name.

**Latvia.** The Evangelical Lutheran Church of Latvia, from a parish's
liturgical calendar for 2021: Sundays after the Day of the Star (Epiphany),
Septuagesima to Esto mihi, the Lent Sundays and Judica as the first Sunday of
Passiontide, White Sunday, Sundays of Easter counted from Easter, Sundays
after Pentecost, the harvest festival (the first Sunday of October, as in
2021) and Eternity Sunday, with the saints' and apostles' days. The church
publishes no colors, so the usual Lutheran ones are used.

**Hungary.** The Evangelical Lutheran Church in Hungary, from the propers of
its service book with their colors: Sundays after Epiphany and the last one
(white); Hetvened, Hatvanad and Ötvened vasárnap; the Sundays of Lent;
Fehérvasárnap and Pásztor vasárnapja; Sundays after Trinity, with the 10th
remembering the destruction of Jerusalem; and the three last Sundays,
Ítélet, Reménység and Örök élet vasárnap.

**Slovakia.** The Evangelical Church of the Augsburg Confession in Slovakia,
from its outline of the church year and a parish's Sunday titles for
2024–2026: *Nedeľa Deviatnik*, *Nedeľa po Deviatniku* and *Predpôstna
nedeľa*; six Sundays in Lent with *Smrtná* (5th) and *Kvetná* (6th); five
Sundays after Easter and the Sunday after the Ascension; Sundays after
Trinity with the **Kajúca nedeľa** (10th); the second-to-last Sunday and
*Nedeľa večnosti*; Cyril and Methodius, Jan Hus, the Reformation and All
Souls. The last Sunday after Epiphany is named so when there are fewer than
five (2026); with five or six they are numbered (2025). The church publishes
no colors, so the usual Lutheran ones are used.

**Austria** points to the German church's liturgical calendar from its own
page (evang.at, *Kirchenjahr – Liturgischer Kalender*), so it follows the
German order; it is listed under its own name with the German calendar.

**Tanzania (ELCT/KKKT).** The Evangelical Lutheran Church in Tanzania, from its
2018 Bible-reading calendar (*Kalenda*), in Swahili with its colors: the
Sundays of Advent (*Majilio*), Christmas Eve and Day, the Martyrs (26
December), the Sundays after Christmas and after Epiphany (*Ufunuo*), the
last of them the Transfiguration; the 9th, 8th and 7th Sundays before Easter
in green; Ash Wednesday and Lent counted down to Palm Sunday; Maundy Thursday
white and Good Friday black; the Sundays after Easter, the Ascension, Exaudi,
Pentecost and Trinity; the Sundays after Trinity (*baada ya Utatu*); the
Children's Sunday (the Sunday from 29 September, as in 2018), the
Reformation and All Saints; and the Sundays before Advent counted down.

**Australia and New Zealand (LCA).** The Lutheran Church of Australia keeps the
Revised Common Lectionary, with the Proper beneath each Sunday after
Pentecost and the colors of its own table (lca.org.au, *Planning ahead*);
Good Friday black; the Reformation, All Saints, Australia Day, Waitangi Day,
Anzac Day, Mother's and Father's Day.

The Ethiopian Evangelical Church Mekane Yesus publishes no church year that
could be followed (only Genna on 7 January and Easter by the Ethiopian
reckoning), and is not included. The North American Lutheran Church uses
Lutheran Service Book or the Revised Common Lectionary without a calendar of
its own; choose the LCMS or the ELCA.

## The Eastern Orthodox churches

**Eastern Orthodox** follows the Byzantine year. It begins on 1 September,
the Indiction, and the Sundays after Pentecost carry on into it, numbered
from the last Pentecost until the Sunday of Zacchaeus. Then come the Lenten
Triodion (the Publican and the Pharisee, the Prodigal Son, the Last
Judgment, Forgiveness Sunday and the Sundays of Great Lent), Holy Week, and
the Pentecostarion from Pascha to All Saints. The outer rings name the
service book of each part of the year. The Sundays named for the Exaltation,
the Fathers of the councils and the Forefathers take their places in the
count. The Twelve Great Feasts are colored in full, and the greater saints in
the lower half of their cells.

The wheel opens on the **Revised Julian** calendar with Pascha by the Julian
paschalion, as the Greek, Romanian, Bulgarian, Ukrainian (OCU) and most other
churches keep it. Choose the **Julian** calendar for the churches that keep
the Old Calendar (Russia, Serbia, Georgia, Jerusalem, Mount Athos). The
feasts then fall on the same names of days, and the page shows the civil date
beside each.

The service books prescribe only "light" and "dark" vestments. The colors are
the Slavic cycle as the Russian *Nastol'naya Kniga Sviashchenno-sluzhitelia*
(1983) gives it: gold when none other is given and from the Nativity to
Theophany, blue for the Theotokos, dark red for the Cross, Great Thursday and
the Saturdays and Sundays of Lent, black on the weekdays of Lent and in Holy
Week, red for the Nativity and Apostles' Fasts and the martyrs, green for Palm
Sunday and Pentecost, and white for Theophany, the Transfiguration and Pascha.
Where the book allows another color (white on Christmas Day, bright red at
Pascha), the page names it after the first.

**Eastern Catholic.** The **Ukrainian Greek Catholic Church** keeps the
Byzantine year as the Orthodox do (on the Revised Julian calendar since 2023,
Pascha by the Julian paschalion), adding the Feast of the Holy Eucharist on
the Thursday after All Saints' Sunday and St Josaphat on 12 November. The
**Byzantine Catholic Church** in America (Ruthenian) keeps the same year on
the Gregorian calendar with the Western date of Pascha.

## The Ukrainian Lutheran Church

**Ukrainian Lutheran Church** is a Lutheran church of the Byzantine rite, and
its year is both. It begins with Advent, the church New Year, and ends with
the Sundays of the Last Judgment, the Saints Triumphant and Christ the King.
Between them it is Byzantine: the Sundays of the Forefathers and before the
Nativity, Forgiveness Sunday and the Sundays of the Forty Days, the Sundays
of Thomas, the Myrrhbearers, the Paralytic, the Samaritan Woman and the Man
Born Blind, Holy Trinity on Pentecost Monday, and Sundays numbered after the
Trinity, carried on into the new year until the Sunday of the Publican and the
Pharisee. The names are in Ukrainian, with English in the full name.

The structure and the days come from the church's 2016 calendar and the
lectionaries of its 2003 service book (*Український лютеранський служебник*),
as its Kharkiv parish of All Saints publishes them. The church moved to the
Revised Julian calendar with the 2018 church year (RISU, 29 December 2017).
Its 2016 dates were the civil dates of the Julian calendar, so here they are
moved back thirteen days. The days it already kept on civil dates stay where
they were: Luther on 18 February, Cranach and Dürer on 6 April, Bach on
28 July and the Reformation on 31 October. Easter is by the Julian
paschalion, like the Orthodox churches of the New Calendar: the Kharkiv
parish's Easter sermons after the change are dated 28 April 2019 and
19 April 2020, the Orthodox Easters (the Western ones were 21 and 12 April).

The colors are those the parish describes: blue for Advent, white for the
feasts and Eastertide, green after the Theophany and after the Trinity, purple
for the Great Fast, and red for Pentecost and Trinity Monday, the martyrs, the
Cross and the Reformation. Black on Good Friday is assumed. The middle holds
the Luther rose.

## The Oriental Orthodox churches

The **Oriental Orthodox** tradition lists these churches.

| Church | Calendar | Easter | Year begins |
|---|---|---|---|
| Armenian Apostolic | Gregorian (Jerusalem: Julian) | Gregorian | Advent (Hisnak), the Sunday nearest 25 November |
| Coptic Orthodox | Coptic | Julian (Alexandrian) | Nayrouz, 1 Thout (11 or 12 September) |
| Ethiopian and Eritrean Tewahedo | Ethiopian | Julian (Alexandrian) | Enkutatash, 1 Meskerem (11 or 12 September) |
| Syriac Orthodox | Gregorian | Julian | Qudosh Idto, eight Sundays before the Nativity |
| Malankara (India) | Gregorian (since 1953, for every feast) | Gregorian | Qudosh Idto |

- **Armenian:** the year runs through five seasons: Advent (from its First Sunday,
  the Sunday nearest 25 November; the fifty days of its fast begin the Monday
  after the Sunday nearest 18 November), Eastertide (from nine weeks before Easter),
  Transfigurationtide, Assumptiontide and the season of the Cross. The five Tabernacle feasts (the Nativity and Theophany on
  6 January, Easter, the Transfiguration 98 days after Easter, the Assumption
  on the Sunday nearest 15 August and the Exaltation of the Cross on the Sunday
  nearest 14 September), each with its Sundays after. The many days kept on a
  set weekday counted from them are included: St Sarkis, Vartanants, St
  Gregory, the Holy Translators. Most saints' days move each year to a day
  that is not a fast, so only the fixed feasts are listed. Its readings, by
  date, are the Armenian Prelacy's for Advent 2025 to 6 January 2027.
- **Coptic:** dated in the Coptic calendar. The Great Fast's Sundays run from
  the Preparation Sunday to the Sunday of the Man Born Blind and Palm Sunday.
  Other Sundays outside the Fifty Days are named by their Coptic month. The
  Nativity is kept on 29 Koiak, 7 January. Vestments are white all year; in
  Holy Week the church is hung in black and the icons veiled, and the wheel
  follows both.
  Its readings are the Katameros: the Annual readings by Coptic date, the
  Sunday readings by month, Great Lent's and the Fifty Days' own, the feasts'
  and the hours of Pascha (`data/Coptic/readings.csv`, whose header gives the
  rules).
- **Ethiopian and Eritrean:** dated in the Ethiopian calendar, with the eight
  Sundays of the Great Fast under their Ge'ez names (Zewerede to Hosanna) and
  the seasons named for the fasts.
- **Syriac and Malankara:** the West Syriac year, from the Sanctification and
  Dedication of the Church through the Sundays of the Annunciation, the
  Nativity and Denho, the Great Fast (Kothne to Hosanna), the Resurrection,
  Pentecost and the Cross. The Patriarchate keeps the Apostles' fast from 26
  June and the Shunoyo fast from 10 August (formerly from 16 June and 1
  August, as Malankara still does); its fixed feasts are on the Gregorian
  calendar and Easter on the Julian (the Syriac Orthodox in India keep the
  Western Easter, like Malankara). Malankara keeps the 25-day Nativity fast
  (1 December to Christmas), and St Gregorios of Parumala and St Thomas on
  21 December. Malankara has its lectionary: each Sunday's and feast's
  Gospel at Vespers and at Matins, the lessons before the Holy Qurbana and
  the Qurbana's own, the weekdays of the fasts and the services of Holy Week;
  the Sundays after Pentecost give way to those after the Transfiguration
  and after Shunoyo. The Syriac Orthodox have theirs from the Archdiocese of
  the Eastern USA's Scripture Readings (2000): the Old Testament lessons,
  Acts or Catholic Epistle, Pauline Epistle and Gospels of each Sunday and
  feast, in the book's order (it does not name the services), the weekdays
  of the Fast of Nineveh and of the Great Fast, Holy Week's services and
  hours, the Sundays numbered from Easter to the 24th and those after the
  Cross.

Two more Eastern churches have folders of their own:

- **Maronite:** the West Syriac pattern as the Maronite Catholic Church keeps
  it, on the Gregorian calendar with the Western Easter: the Consecration of
  the Church on the first Sunday of November and the Renewal the week after
  (when there is room); six Sundays of the Announcements, ending with the
  Genealogy on the Sunday before Christmas; the Sundays after Christmas and
  Epiphany; the Sundays of the Deceased Priests, the Righteous and Just, and
  the Faithful Departed; the Great Lent from Cana Sunday (and Ash Monday)
  through the Sundays of the Leper, the Hemorrhaging Woman, the Prodigal Son,
  the Paralytic and the Blind Man to Hosanna; the Resurrection, New Sunday,
  Pentecost and its Sundays to the Holy Cross, and the Sundays of the Cross.
  Its readings are the Maronite Lectionary's Epistle and Gospel for each
  Sunday and the weekdays after it, as the Eparchy of Our Lady of Lebanon's
  Ordo gives them; the Sundays of Pentecost are numbered from Pentecost.
- **Assyrian Church of the East:** the East Syriac year in its weeks
  (*shabu'e*), on the Gregorian calendar with the Western Easter: Subara (four
  Sundays before Yalda, the Nativity), Denha, the Rogation of the Ninevites,
  the Great Fast, Qyamta (the Resurrection), the Apostles from Pentecost,
  Summer (*Qaita*), Elijah and the Cross (from the Sunday before 14 September
  at the latest), Moses, and the four Sundays of the Hallowing of the Church. Its
  readings are those of the Sundays and the Lord's feasts.

These churches prescribe no cycle of colors (the Copts keep white vestments
and black hangings in Holy Week).
The wheel shows feasts and their seasons in white, the time between them in
gold, the fasts in violet, and Holy Week in black. Their names are in English
with the church's own word beside them in the full name.

```
python new_year.py 2026 --lectionary roman
python new_year.py 2026 --lectionary roman --subcalendar united_states --subcalendar jesuits
python colors.py roman 2026 --subcalendar england
python web/verify.py --lectionary all --subcalendar each
```

Nothing is drawn differently because a tradition is new. Both renderers read
the same rules, and `web/verify.py` checks that they still agree.

## What a tradition folder holds

```
data/traditions.csv          the menus: key, label, tradition, church, series, folder, variant
data/<Folder>/
    tradition.csv            settings of its own (anything config.csv can say, and more)
    days.csv                 principal days: Sundays, festivals, fasts, as date rules
    periods.csv              seasons, the halves of the year, the cycles
    seasons.csv              season key -> color
    feasts.csv               saints' days and other commemorations
    colors.csv               optional: colors laid over the shared palette
    text_styles.csv          optional: styles laid over the shared ones
    subcalendars.csv         optional: calendars that can be laid over this one
    readings.csv             optional: the Bible readings, listed on the page under the day
```

A `variant` column in any of these files limits a row to one variant of the
folder. LCMS One-year and Three-year share a folder, and a row marked
`three-year` exists only in that series. More than one variant can be named,
separated by spaces (`bcp-1662 bcp-1928`).

`traditions.csv` places each calendar in the menus: its `tradition`, its
`church`, and a `series` when a church has more than one calendar (the LCMS
one-year and three-year, the Church of England's 1662 and Common Worship);
`series_menu` names that menu (**Lectionary**, **Prayer book**,
**Missal**). A church with more than one `book` (the LCMS: LSB, LW, TLH, ELHB)
gets a menu of them before it, named by `book_menu` (**Hymnal**). The first row of each tradition is the church it opens on.

### tradition.csv

Two columns, `setting` and `value`, and an optional `variant`. Any setting
from `config.csv` can be given, and it holds whenever this tradition is drawn.
A few settings exist only here:

| Setting | Meaning |
|---|---|
| `year_start` | a date rule for the first day of the year (`sun<12-25-21`, Advent Sunday; `09-01` for the Orthodox; `coptic(01-01)`) |
| `calendar` | the calendar the tradition opens in (`revised-julian` for the Orthodox). Unlike other settings it is only a default: the Calendar menu, `--calendar`, or a year folder made in another calendar wins |
| `paschalion_default` | the Easter rule when the calendar alone would pick another (`julian` for the Orthodox on the Revised Julian or Gregorian calendar) |
| `center_art` | the artwork `center_svg,auto` means for this tradition (a key from `artwork.csv`) |
| `latin_names_available` | offer the Latin names box (LCMS One-year) |
| `latin_names_default` | the tradition's own default for that box and for new_year.py (LCMS, ELS and LCC One-year: TRUE) |
| `festival_half_end_auto` | where `festival_half_end,auto` ends the festival half |
| `precedence` | `roman`: rank the days by the Table of Liturgical Days (below) |
| `hide_outranked_titles` | leave off a Sunday's name when a feast takes its place |
| `commemoration_style` | the text style for a memorial reduced to a commemoration |
| `principal_max_rank`, `festival_max_rank` | the ranks the Feasts menu's *principal* and *festival* levels reach |
| `readings` | shared lectionaries from `data/readings/` that this calendar uses, by file name: `rcl rcl-us rcl-daily` (the Revised Common Lectionary, its US Thanksgiving Day, and its Daily Readings) |
| `bible_version` | the Bible version the page's reading links open in (ESV when blank) |
| `verse_numbering` | the verse numbering the readings are cited in when it is the Hebrew one their church's Bible uses: `hebrew` for every book, or the books (`Psalms Joel`); the Bible links translate it (docs/versification.md) |
| `major_days_exclude` | ids of single-dated days.csv rows that feasts.py `--major-days` leaves out, beside its own list of Sundays of a sequence |
| `feast_link` | where a saint's name links when feasts.csv gives no `link`: a URL with `{name}` (a Wikipedia search when blank) |
| `reading_rotate` | ELHB: `after_epiphany 6 Morning and Evening Lessons` -- in a year with fewer than six Sundays after the Epiphany a different week of those lessons is left out each year, as the book directs. Other rows that take a Sunday of the run follow its id after `\|` (TLH: `after_epiphany\|transfiguration`) |
| `reading_cycle` | `abc`: `readings.csv` rows marked `A`, `B` or `C` follow a three-year series whose Year A begins with Advent 2025 (2028, 2031 ...). Any other series: its names in order and the year its first begins (EKD: `I II III IV V VI 2018`; Norway: `I II III 2025`). Several series running side by side are split by `;` (Sweden: `I II III 2005; MATTEUS MARKUS LUKAS JOHANNES 2003`), and a row may name any of them. `year`: a row's cycle is the year its church year begins (`2025` for Advent 2025 to Advent 2026), for a church that chooses its texts afresh each year (HKBP) |
| `hymnary_hymnal` | Hymnary.org's code for the church's hymnal (`lsb2006`, Lutheran Service Book; the code is the end of its page's address, hymnary.org/hymnal/LSB2006): the page's Hymn search marks search its scripture index for the hymns on each set of readings (blank: no such marks). Several codes, separated by spaces, give the page's Settings a Hymnal menu, the first opening (the Church of England: `AM2013 CAH2000 CPAM2000 NEH1985`). A hymnal is only as useful as Hymnary.org's scripture index of it: Lutheran Worship (LW1982), Evangelical Lutheran Worship (ELW2006) and the Hymnal 1982 (EH1982) have only a few dozen hymns indexed there, and TLH and the ELHB none; the Evangelical Lutheran Hymnary (ELH1996) and the New English Hymnal (NEH1985) are named anyway, for the hymns indexed later |
| `hymnary_hymnal_name` | that hymnal's name, for the mark's title and the Hymnal menu ("Lutheran Service Book (2006)"); for several, their names separated by `|` in the same order |
| `weekday_titles` | how the page names a weekday that has no name of its own, from the Sunday before it: `after` (blank; the Lutheran and Anglican convention: "Tuesday after the Sixth Sunday after Pentecost", and with the one-year series' Latin names "Wednesday of Laetare"), `week` (the Roman Missal's and the Byzantine books': "Tuesday of the Sixth Week after Pentecost", "Tuesday of the First Week of Advent", "Tuesday of the Thirteenth Week in Ordinary Time"; the Roman and Orthodox folders) or `none` (calendars whose names are not in English). A Sunday a fixed-date feast takes (a `days.csv` row that `claims` it with a date rule naming a month and day: Reformation Day, All Saints' Day observed) leaves the week to the Sunday it displaced: "Tuesday after the Twenty-first Sunday after Pentecost"; Christmas, the Epiphany and the feasts of their season, and named Sundays ("Sunday of the Forefathers"), keep their weeks, except with `week`, where every week keeps its number ("Tuesday of the Twenty-first Week after Pentecost" after the Sunday of the Holy Fathers) |
| `reading_order` | groups of kinds of reading, split by `\|`, put in this order within each set (each group keeping its own order, the other kinds their places) (ELCA: `ot_c psalm_c \| ot_s psalm_s`, the complementary series first as Evangelical Lutheran Worship prints it) |
| `reading_labels` | the page's names for kinds of reading, as `kind=Name; kind=Name` (ELHB: `ot=Old Testament (Historical Books); ot2=Old Testament (Poetical Books)`) |
| `reading_propers` | the kinds that are parts of the service, sung or said, rather than readings (LCMS, LCC: `introit gradual verse`): the page and `lectionary.py` list them apart, as *Propers*, after each set's readings, and a set's heading opens only its readings |

### readings.csv

The day's Bible readings, which the page lists under the day's name (the
**Readings** boxes behind the gear choose which kinds). They are not drawn on
the wheel. One row is one reading:

```
day,offset,when,cycle,variant,title,kind,reading
advent:1,,,A,three-year,,ot,Isaiah 2:1–5
advent:1,1,,,,Daily Lectionary,ot,Isaiah 1:1–20
11-30,,,,,St. Andrew,epistle,Romans 10:8–18
next_start-7,,date gt @trinity,,,,epistle,1 Thessalonians 5:1–11
```

| column | meaning |
|---|---|
| `day` | a `days.csv` id (`christmas`), with `:n` for the nth of a run (`advent:1`, `after_trinity:12`, the number in the day's title); a `feasts.csv` id (`st_joseph`: the day the feast is kept, after any transfer); a date rule (`11-30`, `easter-46`, `sun>=05-29`, `thu#4:11`); or, in a reading plan, `plan:N` |
| `offset` | days added: weekday readings are keyed to their Sunday (`advent:1` + 1 is the Monday after it) |
| `when` | conditions, as in `days.csv` (`date lt @fulfillment-14`, `date nwd sun`) |
| `cycle` | the series the row belongs to (`A`, `B`, `C` with `reading_cycle,abc`; `I`, `II` ... or another name `reading_cycle` gives); blank for every year. In a reading plan, the year its cycle was first read |
| `variant` | limits the row to one variant of the folder, as elsewhere |
| `title` | the heading the readings are listed under: blank for the day's own propers, or `Daily Lectionary`, a saint's day, `Morning and Evening Lessons` |
| `kind` | `ot`, `ot2`, `psalm`, `epistle`, `gospel`, `nt`, `morning`, `evening`, `first`, `second` (an Office lesson: First Lesson, Second Lesson), `sermon` (a preaching text: EKD), `story` (Norway's story text), `lesson` (Loehe's) ... : named on the page as Old Testament, Psalm, Epistle, Sermon Text, Story Text ... (see `reading_labels`) |
| `reading` | the citation |

A lectionary that several calendars keep is written once, in
`data/readings/<name>.csv`, with every day as a date rule so it reads the same
in any folder, and each calendar names it with its `readings` setting:
`data/readings/rcl.csv` is the Revised Common Lectionary (with `rcl-us` and
`rcl-daily`), `lsb.csv` Lutheran Service Book (the LCMS and Lutheran
Church–Canada, keyed by the day ids their calendars share), `cw21.csv`
Christian Worship (2021) of the WELS and `roman.csv` the Roman Lectionary for
Mass (the General Roman Calendar and *Divine Worship*, keyed by the Roman
calendar's day and feast ids: Divine Worship's `days.csv` has untitled rows
with those ids, `ordinary_1`, `ordinary_2`, `baptism` ..., that draw nothing
and only give the readings their days). A calendar's own lectionary stays in
its folder (`data/ELS/readings.csv`, `data/ELCA/readings.csv` ...).

A folder that keeps a shared lectionary with changes adds its own rows, and
drops the shared rows it replaces with a row of kind `omit`: it drops the
shared rows of its `title` (blank: the day's own propers) on its `day` and
`offset` (blank `day`: every day), of its `cycle` (blank: every year), and of
the kinds listed in its `reading` (blank: every kind). The ELCA's file drops
the RCL's Easter Vigil for the twelve readings of Evangelical Lutheran
Worship, and the semicontinuous series from the daily readings:

```
easter-1,,,,,Easter Vigil,omit,
,,,,,Daily Readings,omit,ot_s psalm_s
```

A row whose kind is `=` and a kind (`=psalm`) gives another reading for the
shared row of that kind on its `day`, `offset`, `cycle` and `title`, which
keeps its place among the others. The Episcopal Church's file uses it for the
psalms, which the Book of Common Prayer numbers its own way:

```
start+21,,,A,,,=psalm,"Psalm 80:1–7, 16–18"
```

A **reading plan** (`data/readings/plan-<name>.csv`, named in `readings` like
any shared lectionary) is kept by the calendar year. Its rows keyed `plan:N`
are read on the Nth day of the year that none of its other rows takes; those
others, keyed by date rules (`01-06`, `easter-46`, `start` ...), are its
festivals, and the sequence waits for them. Its `cycle` is the year a cycle
was first read: with cycles `2018`, `2019` and `2020`, a year Y reads the one
whose year differs from Y by a multiple of three (2026 reads 2020's). A set
past the year's plan days (a cycle written for a leap year, read in a common
one) is read on the last plan day; a plan day past the cycle's sets has none.

Rows with the same `title` on a day are listed together, in the order of the
file. Each file begins with comments naming its sources and anything in them
that is uncertain.

Each set is of one kind, which the page's Readings boxes and lectionary.py's
`--readings` choose by (church_year.js `readingInfo`, lectionary.py
`ReadingInfo`). The first of these that fits a set is its kind:

| kind | the sets |
|---|---|
| `plan` | any row of a shared reading plan, `data/readings/plan-<name>.csv` |
| `office` | a title with Morning or Evening Prayer, Lessons, Matins, Vespers, Evensong, or Second or Third Service |
| `additional` | a title with Additional Reading (LSB's "Daily Lectionary: Additional Reading") |
| `psalms` | a title beginning Psalms (LSB's "Psalms for Daily Prayer") |
| `daily` | a title with Daily, or any row of a shared lectionary whose name ends in `-daily` or `-weekday` (`rcl-daily`, `roman-weekday`) |
| `feasts` | keyed to a `feasts.csv` id; or titled and keyed to a date that a `feasts.csv` row of that title has (`11-30`, St. Andrew; a subcalendar's rows count) |
| `day` | untitled, or keyed to a `days.csv` id; or titled and keyed beside the day's own untitled propers ("Christmas Dawn (Proper II)" on `12-25`), or under a title the file also keys to a `days.csv` id ("Three-year series"), or under one naming a `days.csv` day ("Easter Vigil"; a Saturday or Sunday before or after a day, "Saturday before Theophany", only in that day's own words) |
| `dated` | a title of an Ember, Rogation, Thanksgiving, New Year's, national, founders' or remembrance day ("Ember Day", "Dominion Day", "17. mai", "Tag des Gedenkens ...") |
| `feasts` | the other titled sets keyed to a month and day (a saint the calendar does not list, "Seraphim of Sarov"); and those keyed to a date rule under the name of a feast of the calendar (on any date: a feast moved by rule) |
| `day` | keyed to a date rule under the name of a `days.csv` day of another of the folder's variants (one calendar keeping another language's names) |
| `dated` | the rest: titled sets keyed to a date rule that the calendar has no day or feast for ("Saturday before the Nativity", `sat<12-25`; Thanksgiving Day, `thu#4:11`, where it is no day of the calendar) |

So *Other dated days* holds the days the wheel does not name that a lectionary
keeps by their date: in 2025-26 the Ember and Rogation Days of BCP 1928 and
1962, Dominion Day (1962), Thanksgiving Day (TLH, ELHB, Moravian, Reformed),
New Year's Day (the RCL's set, in the churches without a 1 January row of that
name), Norway's Nyttårsaften, Samefolkets dag, 1. mai and 17. mai, the EKD's
and Austria's days of remembrance, the ELS's Norwegian Synod Founders' Day,
Hungary's Ash Wednesday (Hamvazószerda, which its calendar does not name) and
the Byzantine Saturdays before and after the Exaltation, the Nativity and
Theophany. A national day that is a `feasts.csv` row (the Episcopal Church's
Independence Day) is that feast's and stays with the feasts.

A set keyed to a feast's id or, under the feast's name, to its date belongs
to that feast and is listed only on a day the wheel shows it: with the Feasts
setting, precedence, a transfer or an unchosen subcalendar leaving the feast
off, its readings go too (unless the day's own title names it). A title is
the feast's when the two share a word other than the common ones (St., Saint,
Apostle, Day ...): "St. Andrew, Apostle" and "St. Andrew", "Martinstag" and
"Martin von Tours". Untitled rows keyed to a date are the day's own and stay.

## The date language

Every date in `days.csv`, `periods.csv`, `feasts.csv` and the settings is a
small expression, worked out for the year being drawn.

| Rule | Meaning |
|---|---|
| `12-25` | 25 December: the first one on or after the year's start |
| `y1:01-06` | 6 January of the year's second calendar year |
| `easter+49` | 49 days after Easter (Pentecost) |
| `start`, `end`, `next_start` | the year's first day, last day, and the next year's first day |
| `half_end` | the last day of the festival half |
| `@epiphany` | another row's date, by its `id` |
| `sun<12-25-21` | the Sunday before 25 December, then 21 days back (Advent Sunday) |
| `sun>=01-02`, `sun>X`, `sun<=X`, `sun<X` | the nearest Sunday on or after, after, on or before, before |
| `thu#4:11` | the fourth Thursday of November |
| `mon#-1:05` | the last Monday of May |
| `max(a, b)`, `min(a, b)` | the later or earlier of two dates |
| `prev_easter` | the last Easter before the year's start (for a year that begins in September) |
| `julian(12-25)`, `gregorian(12-25)` | that date in the Julian or Gregorian calendar, whichever calendar the wheel is drawn in |
| `coptic(04-29)`, `ethiopian(05-11)` | that day of the Coptic or Ethiopian year: month 1–13, day 1–30 (29 Koiak; 11 Tir) |

Rules combine with `+`, `-` and parentheses: `max(sun>01-06, @epiphany+1)` is
the Baptism of the Lord.

A date in another calendar keeps the civil date its people know. The Coptic
Church's Nativity is `julian(12-25)`, 7 January on a Gregorian wheel; its
Theophany, `coptic(05-11)`, is 19 January, or the 20th in the years the
Coptic leap day falls before it.

### hymn_topics.csv

Optional. Topics of a hymnal's index at Hymnary.org matched to days: the page
puts a hymn mark after the day's name (before its season) for each, which
opens Hymnary.org's list of the hymnal's hymns filed under that topic, in
hymn-number order (`hymnary.org/browse/topics/AM2013?subject1=Proper+10`, and
`&subject2=` for a sub-topic). The mark shows when Hymn search is on and the
hymnal is the one chosen.

| column | meaning |
|---|---|
| `day` | as in readings.csv: a `days.csv` id (`lent`, every Sunday of the run; `lent:2`, one), a `feasts.csv` id, a month and day (`09-29`), or a date rule (`next_start-14`) |
| `variant` | blank for every variant, or the variants it is for |
| `when` | optional: a further condition, as in readings.csv (see Conditions); `after_trinity` with `date ge 07-10 & date le 07-16` is Proper 10 |
| `hymnal` | the hymnal's Hymnary.org code (`LSB2006`), as in `hymnary_hymnal` |
| `topic` | the topic as Hymnary.org's index names it (hymnary.org/browse/topics/<code>), word for word and misspellings and all, or the name of a section of the hymnal's contents |
| `subtopic` | optional: one of the topic's sub-topics, word for word (UMH: `Christian Year`, `Advent`) |
| `numbers` | a section's hymns, by number (`331-357`; several ranges separated by spaces): the mark then lists them in a window, each with its first line (from `data/hymnals/<hymnal>.csv`, `number,first_line`) and opening its page at Hymnary.org (hymnary.org/hymn/LSB2006/331). Blank: the mark opens the topic's list |

`{abc}` in `topic` or `subtopic` is the year of the three-year lectionary, A,
B or C (Year A begins in Advent 2025): Complete Anglican Hymns Old and New
files its Sundays under `Year A`, `Year B` and `Year C`.

A day may have several rows, and gets a mark for each topic once. The topic
list matches the index's words exactly; Hymnary's search would match them
anywhere ("The Second Sunday of Advent" and "The Second Sunday before
Advent"). Where the index spells one topic two ways, each with hymns of its
own (NEH1985 "The Conversion of St Paul" and "... St. Paul"), both are rows.

Hymnary.org cannot list a range of hymn numbers, and its topics for Lutheran
Service Book name few days of the church year (none for Advent, Christmas,
Lent, Easter or Pentecost), so `data/LCMS/LSB` and `data/LCC` follow the
book's own Topical Index of Hymns and Songs (pp. 993–997). It gives a section
of the contents as a topic ("Advent, 331–357") and lists other hymns that suit
it below ("The Bridegroom soon will call us ... 514"), so a row's `numbers`
are the section and those hymns (`331-357 508-516 872`); and it has topics
of its own for days without a section (Baptism of Our Lord, Palm Sunday,
Maundy (Holy) Thursday, Good Friday, Presentation of Our Lord, St. Michael and
All Angels, Reformation, Holy Cross Day). The sections used are The Church
Year (Advent ... End Times, Feasts and Festivals), The Word of God, Holy
Baptism, Baptismal Life, Confession and Absolution, The Lord's Supper, The
Church Militant and Triumphant, Mission and Witness, Harvest and
Thanksgiving, New Year and Nation and National Songs.

The other hymnals' indexes name the seasons and many of the days themselves:

| hymnal | folder (variants) | what the rows use |
|---|---|---|
| CWH2021 | RCLWorld (wels, wels-one-year) | seasons and festivals; Second Coming and Church Triumphant for End Time |
| TIS1999 | RCLWorld (lca) | seasons and days, Christ the King Sunday, Close of the Year, New Year |
| StF2011 | RCLWorld (methodist-gb) | the book's sections for the seasons ("The Promised Christ: Advent" ...) |
| Mor1995 | RCLWorld (moravian) | "Christian year--" topics; the festivals of 6 July, 13 August and 13 November |
| CH4 | RCLWorld (scotland) | Christian Year sub-topics; the sections Christ Incarnate and Christ Risen; St Andrew, Remembrance Sunday, Mothering Sunday |
| UMH | Methodist | Christian Year sub-topics; Aldersgate (24 May) |
| GG2013 | Presbyterian | Christian Year sub-topics, and the Jesus Christ sections (Advent, Birth, Life, Passion and Death, Resurrection, Ascension and Reign) |
| LUYH2013 | Reformed | Church Year sub-topics |
| ELH1996 | ELS | its Sundays of the historic series (Advent 1 ... Trinity 24, Septuagesima, Sexagesima), for the one-year series, and the seasons' Sundays for both; festivals |
| WORS2011 | Roman, Roman/1962 | Advent I–IV, Lent I–V, Easter II–VII, every Sunday in Ordinary Time, solemnities and feasts; for 1962, the seasons and feasts the calendars share |
| AM2013, CPAM2000 | Anglican (common-worship) | every Sunday of Common Worship, Propers 4–25 by date |
| CAH2000 | Anglican (common-worship) | the same, under Year A, B or C |
| NEH1985 | Anglican (common-worship, bcp-1662) | the seasons and the saints' days, by each book's dates |
| CP1998 | Anglican (bcp-1962) | the seasons, saints' days, Harvest Thanksgiving and Remembrance Day |

### Conditions

A `when` column keeps a row only in years that meet it. Clauses are joined
with `&`:

| Clause | Holds when |
|---|---|
| `date lt @transfiguration` | the row's date is before that day (`lt le eq ne ge gt`) |
| `(sun>12-25) gt 12-31` | one rule compared with another |
| `date wd sat\|mon` / `date nwd sat\|mon` | the date is / is not one of those weekdays |
| `variant eq one-year`, `variant eq ugcc\|ruthenian` | the tradition's variant is one of those listed (separated by `\|`) |
| `year ge 2011` | the church year begins in that calendar year or later (`lt le eq ne ge gt`) |
| `latin`, `!latin` | Latin names are on / off |
| `sub:united_states` | that calendar has been laid over this one |
| `date lt easter-69 or date gt easter-66 and date lt easter-57` | any of the alternatives holds, each its conditions joined by `and` (`&` binds loosest: `A & B or C` is A, and B or C) |

In `feasts.csv`, `icon_when` does the same for a row's icon alone. In the
United States, `obligation` with `icon_when` `date nwd sat|mon` removes the
obligation from Mary, Mother of God, the Assumption and All Saints when they
fall on a Saturday or a Monday.

A church's colors or days that changed in a known year are written as two
rows with the same `id` (or date) and opposite `year` clauses: the newer use
from the year it was made, the older use for every year before. The oldest
use on record covers all earlier years. The Church in Wales's 2011 colors,
for example, start with the 2011–12 year; the 1984 book's colors hold before
it. In `periods.csv` the first period that covers a day gives its color, so a
year-limited row goes before the general one.

### Runs of days

A `days.csv` row with `from`, `to` and `every` is a run: every Sunday (or
other weekday) in the span, numbered from `first`. `count` says which way:

| `count` | the run's last day is | so |
|---|---|---|
| *(blank)* | `first` + the number of days − 1 | First, Second, Third Sunday of Advent |
| `down` | `first`, counting up to it | the Roman 32nd, 33rd, 34th Sunday in Ordinary Time, whatever the date of Easter |
| `before` | `first`, counting down to it | Common Worship's Fourth, Third, Second Sunday before Advent |

`first` can also be a date rule. The run is then numbered by the weeks since
that day: the Orthodox Sundays after Pentecost, which carry on past the
September start of the year, are a run with `first` `prev_easter+49`, so the
Sunday a week after last year's Pentecost is the First.
A single day can do the same, so that a day taking over a Sunday can keep
that Sunday's number in its title: Iceland's Reformation Sunday is
`{number}. sunnudagur eftir þrenningarhátíð` with `first` `easter+56`.

A run can carry a second number, `first2` and `count2`, the same way. The
Revised Common Lectionary churches use it for the Proper, counted back from
Christ the King: the run of Sundays after Pentecost has `first2` 29 and
`count2` `down`, so each Sunday is both "Eighth Sunday after Pentecost" and
"Proper 12". The ELCA's run uses 34 for its lectionary numbers.

The title, `notes` and `full_name` can use `{ordinal}` (Second), `{number}`
(2), `{roman}` (II), `{ordinal2}`, `{number2}` and `{roman2}` (the second
number), and `{name}`, taken from the `names` column. `names`, `notes`, `latin`, `color` and the other
per-day columns take `|` for one value per day in order, so Advent's `color`
of `||ROSE|` makes the third Sunday rose. A day another row claims (`claims` =
TRUE) is skipped by every run, though it still counts, so the numbering after
it is unchanged.

## Roman precedence

With `precedence,roman`, the days are ranked by the Table of Liturgical Days
in the *Universal Norms on the Liturgical Year and the Calendar*, from 1
(the Paschal Triduum) to 13 (weekdays of Ordinary Time). `rank_sunday` and
`rank_weekday` in `periods.csv` give each season's days their rank, and
`days.csv` and `feasts.csv` rank the rest.

- **Solemnities** that are impeded are moved to the next free day, or wherever
  their `transfer` column says: `next`, `prev`, `none`, or `a..b=>target`
  (Saint Joseph falling in Holy Week goes to the Saturday before Palm Sunday:
  `easter-7..easter-1=>easter-8;next`).
  A transferred holy day loses its obligation icon, as the obligation stays
  with the date.
- **Memorials** on a privileged weekday (rank 9: 17–24 December, the octave
  of Christmas, Lent) become commemorations, drawn in `commemoration_style`.
- Any other celebration that is outranked is left out for that year.
- `hide_outranked_titles` removes a Sunday's own name when a feast of the Lord
  or a solemnity is celebrated on it, with any untitled ranked row of that day
  (Divine Worship's Roman-id aliases), so the Sunday's readings go too.
- A `yield` rank in `days.csv` drops a row's icon-only mark when a
  celebration of that rank or higher falls on it. The Fridays of Lent keep
  abstinence, except when a solemnity falls on one.

The ranks also set how much the Feasts menu shows: *principal* is
solemnities (rank 4 and above) and *festival* adds feasts (rank 8).

## Laying another calendar over a tradition

`subcalendars.csv` lists calendars that add to or change the tradition's own:

```
menu,menu_label,key,label,file,include
national,National calendar,united_states,United States,national/united_states.csv,
personal,Personal jurisdiction,ordinariate_walsingham,Personal Ordinariate of Our Lady of Walsingham,personal/ordinariate_walsingham.csv,england
```

The page shows one menu for each `menu`. Choosing a calendar in any of them
lays its rows over the tradition's feasts. The Reformed calendar offers the
Christian Reformed Church's Canadian special days. The Roman Catholic calendar
offers:

- **National calendar**: 81 countries and regions.
- **Institutional/societal calendar**: 37 religious institutes and societies.
- **Personal jurisdiction**: the two Anglican-use ordinariates, each laid
  over its country's calendar through `include`.

A subcalendar's rows use the columns of `feasts.csv`:

- A row with an `id` changes that row of the tradition's feasts. Every
  non-blank cell replaces the original, and `-` blanks one. `action` =
  `remove` deletes the row.
- A row without an `id` but with the same date and name as an existing one
  replaces it.
- Any other row is added.

The Roman calendars were taken from Wikipedia's lists of the General Roman
Calendar and of the national and institutional calendars (revisions of
September 2026). Commemorations of the departed and dedications "if the date
is unknown" are left out, as are observances limited to one branch of an
order (the Poor Clares or the Third Order among the Franciscans, the Daughters
of Mary Help of Christians among the Salesians). Holy days of obligation and the
temporal changes of the United States, Canada and Australia (Epiphany, the
Ascension and Corpus Christi on Sundays; Thanksgiving) come from those bishops'
conferences' published norms. In the United States the Ascension is kept on the
following Sunday, as in most of its ecclesiastical provinces; the few that keep
it on Thursday can remove that row from `national/united_states.csv`.

## Icons

`data/icons.csv` holds small pictures a day can carry: `obligation` (a
chalice and host) for a holy day of obligation, `fast` (a bowl) for a day of
fasting and abstinence, and `abstinence` (a fish) for a day of abstinence
alone. Each is an SVG path in a 100 × 100 box. A day names its icons in an
`icon` column, separated by spaces. They are drawn in a row at the cell's
inner edge, `icon_size` high, and the text moves up to make room. The page's
readout names them in words.

`icon_when` keeps a row's icon only on the days that meet it (`date nwd
sat|mon`, `variant eq ugcc|ruthenian`, `date ne 03-25`), in `days.csv` as in
`feasts.csv`. The Catholic calendars carry their own church's law:

| Calendar | Holy days of obligation | Fasting (and abstinence) | Abstinence | Source |
|---|---|---|---|---|
| General Roman | can. 1246, less what the national calendar removes | Ash Wednesday, Good Friday | Fridays of Lent | 1983 Code, cans. 1246, 1251 |
| Roman 1962 | the same | the same | the same | the 1983 Code governs the 1962 books (*Universae Ecclesiae* 27) |
| Ukrainian Greek Catholic | Nativity, Theophany, Annunciation, Ascension, Sts Peter and Paul, Dormition | Clean Monday, Good Friday; the eves of the Nativity and Theophany, 29 August, 14 September | first week and Holy Week; Mondays, Wednesdays and Fridays of the Great Fast (not on the Annunciation) | UGCC Particular Law cans. 114–115 |
| Byzantine (Ruthenian) | Nativity, Theophany, Ascension, Sts Peter and Paul, Dormition | Pure Monday, Good Friday (strict abstinence) | Wednesdays and Fridays of the Great Fast | Norms of Particular Law, Metropolia of Pittsburgh (1999) |
| Maronite | Christmas, 1 January, Epiphany, St Maron, Ascension, Assumption, Immaculate Conception (US list) | Ash Monday, Good Friday | Fridays of Lent | US Maronite eparchies' Lenten guidelines (2024); parish list of holy days |
| Ambrosian | Christmas, 1 January, Epiphany, Assumption, All Saints, Immaculate Conception (Italy) | the first Friday of Lent, Good Friday | the other Fridays of Lent | CEI, *Il senso cristiano del digiuno e dell'astinenza* (1994) n. 13 |
| Divine Worship | Immaculate Conception, Christmas, 1 January, Ascension (Thursday), Assumption, All Saints; 1 January, Assumption and All Saints lapse on a Saturday or Monday | Ash Wednesday, Good Friday | Fridays of Lent | Ordinariate of the Chair of St Peter decree; USCCB and CCCB norms |

All Saints is a Maronite holy day in the US list but has no row in the
Maronite calendar yet. The Divine Worship marks follow the Ordinariate of the
Chair of St Peter (US and Canada); Walsingham and Southern Cross follow their
own bishops' conferences.

## Artwork

`data/artwork.csv` lists the pictures the middle of the wheel can hold, with
each one's author, license and source. `center_svg,auto` (the default) uses
the tradition's own `center_art`, and the page's Artwork menu can choose any
of them. The page prints the credit for whichever one is showing. See
[artwork/CREDITS.md](../artwork/CREDITS.md).

## Adding a tradition

[adding-a-church.md](adding-a-church.md) walks through it step by step, with a
working example folder to copy (`docs/example-church/`). In short:

1. Make a folder under `data/` with `tradition.csv`, `days.csv`,
   `periods.csv`, `seasons.csv` and `feasts.csv`. The LCMS and Roman folders
   are working examples.
2. Add a row to `data/traditions.csv`.
3. Add its artwork to `artwork/` and `data/artwork.csv`, and name it as
   `center_art`.
4. `python web/export_data.py` and `python church_year.py` to carry it to
   the page, then `python web/verify.py --lectionary <key>` to check the two
   renderers agree.
