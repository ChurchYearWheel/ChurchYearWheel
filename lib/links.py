"""
Where a reading or a commemoration opens: the links the web page makes,
worked out the same way for the scripts that list them (lectionary.py,
feasts.py).

Each function is a port of the one in web/page.js it is named after, line for
line, and web/verify_links.py runs both over every reading and feast in the
data to keep them identical.  Change one, change the other.

    bible_url("Isaiah 2:1–5", "ESV", "biblegateway")
    reading_links("Matthew 24:36–44 or Luke 21:25–36")   # [(text, url or None), ...]
    feast_url("St. Andrew, Apostle", "", pattern)
"""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import quote

from versification import convert, numbering_books, psalter_citation  # noqa: F401

# Versions that number the verses the Hebrew way, as the Bible sites show them;
# every other version there uses the English numbering (docs/versification.md).
HEBREW_NUMBERED = {"NABRE"}

# Code, name, language (page.js: BIBLE_VERSIONS).
BIBLE_VERSIONS = [
    ("ESV", "English Standard Version", "en"), ("EHV", "Evangelical Heritage Version", "en"),
    ("NKJV", "New King James Version", "en"), ("KJV", "King James Version", "en"),
    ("NIV", "New International Version", "en"), ("NLT", "New Living Translation", "en"),
    ("CSB", "Christian Standard Bible", "en"), ("NASB", "New American Standard Bible", "en"),
    ("NRSVUE", "New Revised Standard Version Updated Edition", "en"),
    ("NRSVA", "New Revised Standard Version, Anglicised", "en"), ("RSV", "Revised Standard Version", "en"),
    ("NABRE", "New American Bible, Revised Edition", "en"), ("CEB", "Common English Bible", "en"),
    ("RSVCE", "Revised Standard Version Catholic Edition", "en"), ("DRA", "Douay-Rheims 1899 American Edition", "en"),
    ("MSG", "The Message", "en"),
    ("LUTH1545", "Luther Bibel 1545", "de"), ("SCH2000", "Schlachter 2000", "de"),
    ("SFB15", "Svenska Folkbibeln 2015", "sv"), ("DNB1930", "Det Norsk Bibelselskap 1930", "no"),
    ("DN1933", "Dette er Biblen på dansk", "da"), ("R1933", "Raamattu 1933/38", "fi"),
    ("ICELAND", "Icelandic Bible", "is"), ("KAR", "Hungarian Károli", "hu"), ("UKR", "Ukrainian Bible", "uk"),
    ("ARC", "Almeida Revista e Corrigida 2009", "pt"),
    ("TB", "Alkitab Terjemahan Baru", "id"),
]
VERSION_CODES = sorted(code for code, _, _ in BIBLE_VERSIONS)

# Bible.com's numbers for them; a version it does not carry opens at Bible Gateway
# (page.js: YOUVERSION).
YOUVERSION = {"ESV": 59, "KJV": 1, "NKJV": 114, "NIV": 111, "NLT": 116, "CSB": 1713, "NASB": 2692,
              "NRSVUE": 3523, "RSV": 2020, "NABRE": 463, "CEB": 37, "MSG": 97, "TB": 306}

# Versions Bible Gateway does not carry: a reading opens at Bible.com whichever
# site is chosen, and a set has no link of its own (page.js: NOT_AT_BIBLE_GATEWAY).
NOT_AT_BIBLE_GATEWAY = {"TB"}

# The books of the Apocrypha, which many versions leave out (page.js: APOCRYPHA).
# A reading from them opens in a version that has them: at Bible Gateway the
# RSV, whose Apocrypha the ESV's (not online) revises; at Bible.com, which has
# no RSV Apocrypha, the NRSVUE.  A set with one opens in the same version.
APOCRYPHA = re.compile(r"(?:[1-4] )?(?:Tobit|Judith|Wisdom|Sirach|Ecclesiasticus|Baruch|Maccabees"
                       r"|Esdras|Prayer of Manasseh|Prayer of Azariah|Song of the Three|Susanna"
                       r"|Bel and the Dragon|Letter of Jeremiah|Additions to Esther|Greek Esther)(?![A-Za-z0-9_])")
APOCRYPHA_AT_BIBLE_GATEWAY = {"NRSVUE", "NRSVA", "RSV", "NABRE", "CEB", "RSVCE", "DRA"}
APOCRYPHA_AT_YOUVERSION = {"NRSVUE", "CEB", "NABRE"}

# page.js: USFM.
USFM = {
    "Genesis": "GEN", "Exodus": "EXO", "Leviticus": "LEV", "Numbers": "NUM", "Deuteronomy": "DEU",
    "Joshua": "JOS", "Judges": "JDG", "Ruth": "RUT", "1 Samuel": "1SA", "2 Samuel": "2SA",
    "1 Kings": "1KI", "2 Kings": "2KI", "1 Chronicles": "1CH", "2 Chronicles": "2CH",
    "Ezra": "EZR", "Nehemiah": "NEH", "Esther": "EST", "Job": "JOB", "Psalm": "PSA", "Psalms": "PSA",
    "Proverbs": "PRO", "Ecclesiastes": "ECC", "Song of Solomon": "SNG", "Song of Songs": "SNG",
    "Isaiah": "ISA", "Jeremiah": "JER", "Lamentations": "LAM", "Ezekiel": "EZK", "Daniel": "DAN",
    "Hosea": "HOS", "Joel": "JOL", "Amos": "AMO", "Obadiah": "OBA", "Jonah": "JON", "Micah": "MIC",
    "Nahum": "NAM", "Habakkuk": "HAB", "Zephaniah": "ZEP", "Haggai": "HAG", "Zechariah": "ZEC",
    "Malachi": "MAL", "Matthew": "MAT", "Mark": "MRK", "Luke": "LUK", "John": "JHN", "Acts": "ACT",
    "Romans": "ROM", "1 Corinthians": "1CO", "2 Corinthians": "2CO", "Galatians": "GAL",
    "Ephesians": "EPH", "Philippians": "PHP", "Colossians": "COL", "1 Thessalonians": "1TH",
    "2 Thessalonians": "2TH", "1 Timothy": "1TI", "2 Timothy": "2TI", "Titus": "TIT",
    "Philemon": "PHM", "Hebrews": "HEB", "James": "JAS", "1 Peter": "1PE", "2 Peter": "2PE",
    "1 John": "1JN", "2 John": "2JN", "3 John": "3JN", "Jude": "JUD", "Revelation": "REV",
    "Tobit": "TOB", "Judith": "JDT", "Wisdom of Solomon": "WIS", "Wisdom": "WIS", "Sirach": "SIR",
    "Baruch": "BAR", "1 Maccabees": "1MA", "2 Maccabees": "2MA", "Ecclesiasticus": "SIR",
    "1 Esdras": "1ES", "2 Esdras": "2ES", "Susanna": "SUS", "Letter of Jeremiah": "LJE",
    "Greek Esther": "ESG",
}

# Where a reading can open (page.js: the Open in menu), and none.
SITES = ("biblegateway", "none", "youversion")

# JavaScript's \s, \d and \b are not Python's (Python's take in all of
# Unicode), so they are spelled out.
_S = "[\t\n\v\f\r    -     　﻿]"
_D = "[0-9]"
_B = "(?![A-Za-z0-9_])"          # \b after a word character


def _trim(text: str) -> str:
    return re.sub(f"\\A{_S}+|{_S}+\\Z", "", text)


def encode_uri_component(text: str) -> str:
    """JavaScript's encodeURIComponent."""
    return quote(text, safe="-_.!~*'()")


def page_bibles(spec: str) -> list:
    """config.csv's `page_bibles` (church_year.py --bible), lowercased as
    the page keeps it: version codes, languages (english, de ...), or own."""
    return [w.strip().lower() for w in str(spec or "").replace(",", " ").split() if w.strip()]


def bible_allowed(code: str, bibles=()) -> bool:
    """Whether a page offering `bibles` lists this version (page.js: bibleAllowed)."""
    if not bibles or bibles[0] == "own":
        return True
    lang = next((v[2] for v in BIBLE_VERSIONS if v[0] == code), None)
    return lang is not None and any(b == code.lower() or {"english": "en"}.get(b, b) == lang
                                    for b in bibles)


def bible_default(settings: dict, bibles=()) -> str:
    """The tradition's own Bible version (tradition.csv `bible_version`), or ESV;
    where only some versions are offered (`bibles`: page_bibles), the first of
    them it names, else ESV, else the first (page.js: bibleDefault)."""
    own = _trim(str(settings.get("bible_version", "") or "")).upper()
    want = own if any(code == own for code, _, _ in BIBLE_VERSIONS) else "ESV"
    if bible_allowed(want, bibles):
        return want
    named = next((b.upper() for b in bibles if bible_allowed(b.upper(), bibles)), None)
    if named:
        return named
    if bible_allowed("ESV", bibles):
        return "ESV"
    first = next((v[0] for v in BIBLE_VERSIONS if bible_allowed(v[0], bibles)), None)
    return first or "ESV"


def plain_citation(text: str) -> str:
    """A citation as Bible Gateway reads it: plain hyphens, no optional-verse
    brackets or half-verse letters (page.js: plainCitation)."""
    s = re.sub(rf"^Canticle:{_S}*", "", str(text), count=1)
    # "Psalm 104:30; Liturgical Text": the words not from Scripture are not looked up;
    # "Psalm 68:1, 4a, c": a half-verse letter on its own adds nothing to the passage.
    s = re.sub(rf"{_S}*;{_S}*Liturgical Text{_B}|(?<![A-Za-z0-9_])Liturgical Text{_S}*;{_S}*", "", s)
    s = re.sub(rf",{_S}*[a-c](?={_S}*[,;]|{_S}*$)", "", s)
    s = re.sub(rf"({_D}+):{_D}+[ab]?{_S}*[–-]{_S}*end{_B}", r"\1", s)
    s = re.sub(rf"{_S}*\([^)]*[A-Za-z]{{2,}}[^)]*\)", "", s)
    s = re.sub(rf"({_D}[a-z]?){_S}+\((?={_D})", r"\1, (", s)
    s = re.sub(rf"\){_S}+(?={_D})", "), ", s)
    s = re.sub(r"[()]", "", s)
    s = re.sub(rf"({_D})[abc]{_B}", r"\1", s)
    s = re.sub(rf"{_S}*[–—]{_S}*", "-", s)
    return _trim(re.sub(f"{_S}+", " ", s))


_BOOK_CHAPTER = re.compile(rf"((?:[1-3] )?[A-Z][A-Za-z]*(?: of [A-Z][a-z]+| [A-Z][a-z]+)*) "
                           rf"({_D}+)(?::({_D}+)(?:-({_D}+)(?![:0-9]))?)?")


def bible_url(citation: str, version: str, site: str = "biblegateway",
              numbering=None) -> str:
    """Where one citation opens (page.js: bibleUrl).  `numbering` is the
    church's verse numbering (versification.numbering_books): a citation in
    the Hebrew numbering opens at the same verses in an English-numbered
    version."""
    if numbering and version not in HEBREW_NUMBERED:
        citation = convert(citation, numbering)
    q = plain_citation(citation)
    if APOCRYPHA.match(q):
        if site == "youversion" or version in NOT_AT_BIBLE_GATEWAY:
            if version not in APOCRYPHA_AT_YOUVERSION:
                version = "NRSVUE"
        elif version not in APOCRYPHA_AT_BIBLE_GATEWAY:
            version = "RSV"
    if (site == "youversion" or version in NOT_AT_BIBLE_GATEWAY) and YOUVERSION.get(version):
        m = _BOOK_CHAPTER.match(q)
        code = m and USFM.get(m.group(1))
        if code:
            verses = ("." + m.group(3) + ("-" + m.group(4) if m.group(4) else "")) if m.group(3) else ""
            return (f"https://www.bible.com/bible/{YOUVERSION[version]}/{code}."
                    f"{m.group(2)}{verses}.{version}")
    return ("https://www.biblegateway.com/passage/?search=" + encode_uri_component(q)
            + "&version=" + encode_uri_component(version))


# The Book of Concord, at bookofconcord.org (the Triglot translation, revised),
# whose pages have an anchor for every paragraph (#ac-iv-0001); CPH's
# bookofconcord.cph.org has a page for every article but none for paragraphs.
# A citation opens at the first article and paragraph it names (page.js:
# CONCORD).  A document's articles are cited by Roman or Arabic numerals
# ("Augsburg Confession XX 1–8", "Apology 4:117–146"); the Smalcald Articles by
# part and article ("Smalcald Articles 3/3:1–18", "III VIII"); the Treatise
# and the prefaces by paragraph.
CONCORD_SITE = "https://bookofconcord.org/"
CONCORD_DOCS = [   # (how a reading names it, its key)
    ("Augsburg Confession", "ac"), ("Apology of the Augsburg Confession", "ap"), ("Apology", "ap"),
    ("Smalcald Articles", "sa"), ("Treatise on the Power and Primacy of the Pope", "tr"),
    ("Power and Primacy of the Pope", "tr"), ("Treatise", "tr"), ("Small Catechism", "sc"),
    ("Large Catechism", "lc"), ("Formula of Concord, Epitome", "ep"), ("Formula of Concord Epitome", "ep"),
    ("Epitome", "ep"), ("Formula of Concord, Solid Declaration", "sd"),
    ("Formula of Concord Solid Declaration", "sd"), ("Solid Declaration", "sd"),
    ("Catalog of Testimonies", "ct"), ("Preface to the Book of Concord", "bc"),
    ("Apostles' Creed", "apc"), ("Apostles’ Creed", "apc"), ("Nicene Creed", "nc"),
    ("Athanasian Creed", "athc"),
]
# Each document: its pages by name or article number.  A page is
# "path#prefix@offset": paragraph n of the citation is the anchor
# prefix-(n + offset), four digits ("" prefix: the page has none; a prefix
# ending in "#": a fixed anchor).  An article whose paragraphs run on into a
# second page lists both, "first paragraph>page".
CONCORD_PAGES = {
    "ac": {"": "augsburg-confession/preface#ac-preface", "Preface": "augsburg-confession/preface#ac-preface",
           "Conclusion": "augsburg-confession/conclusion#ac-conclusion",
           "1": "augsburg-confession/of-god#ac-i", "2": "augsburg-confession/original-sin#ac-ii",
           "3": "augsburg-confession/son-of-god#ac-iii", "4": "augsburg-confession/of-justification#ac-iv",
           "5": "augsburg-confession/of-the-ministry#ac-v", "6": "augsburg-confession/of-new-obedience#ac-vi",
           "7": "augsburg-confession/of-the-church#ac-vii", "8": "augsburg-confession/what-the-church-is#ac-viii",
           "9": "augsburg-confession/of-baptism#ac-ix", "10": "augsburg-confession/of-the-lords-supper#ac-x",
           "11": "augsburg-confession/of-confession#ac-xi", "12": "augsburg-confession/of-repentance#ac-xii",
           "13": "augsburg-confession/use-of-the-sacraments#ac-xiii",
           "14": "augsburg-confession/of-ecclesiastical-order#", "15": "augsburg-confession/of-ecclesiastical-usages#ac-xv",
           "16": "augsburg-confession/of-civil-affairs#ac-xvi",
           "17": "augsburg-confession/of-christs-return-to-judgment#ac-xvii",
           "18": "augsburg-confession/of-free-will#ac-xviii", "19": "augsburg-confession/cause-of-sin#",
           "20": "augsburg-confession/of-good-works#ac-xx", "21": "augsburg-confession/of-worship-of-saints#ac-xxi",
           "22": "augsburg-confession/of-both-kinds-in-the-sacrament#ac-xxii",
           "23": "augsburg-confession/of-marriage-of-priests#ac-xxiii", "24": "augsburg-confession/of-the-mass#ac-xxiv",
           "25": "augsburg-confession/of-confession-xxv#ac-xxv",
           "26": "augsburg-confession/of-the-distinction-of-meats#ac-xxvi",
           "27": "augsburg-confession/of-monastic-vows#ac-xxvii",
           "28": "augsburg-confession/of-ecclesiastical-power#ac-xxviii"},
    # The site numbers some articles on from the one before (the Triglot's
    # numbers: IX is 51-53); the citations' (Kolb-Wengert, Concordia) start at 1.
    # IV 122-400 is its own page (IV-b, 1-279), as is XII 98-178 (VI, 1-81).
    "ap": {"": "defense/#", "Preface": "defense/#",
           "1": "defense/of-god#ap-i", "2": "defense/of-original-sin#ap-ii", "3": "defense/of-christ#ap-iii@51",
           "4": "defense/of-justification#ap-iv 122>defense/of-love-and-fulfilling-the-law#ap-ivib@-121",
           "7": "defense/of-the-church#ap-vii", "8": "defense/of-the-church#ap-vii",
           "9": "defense/of-baptism#ap-ix@50", "10": "defense/of-the-holy-supper#ap-x@53",
           "11": "defense/of-confession#ap-xi@57",
           "12": "defense/of-repentance#ap-xii 98>defense/of-confession-and-satisfaction#ap-vi@-97",
           "13": "defense/of-the-number-and-use-of-sacraments#ap-xiii", "14": "defense/of-ecclesiastical-order#ap-xiv@23",
           "15": "defense/of-human-traditions-in-the-church#ap-xv", "16": "defense/of-political-order#ap-xvi@52",
           "17": "defense/of-christs-return-to-judgment#ap-xvii@65", "18": "defense/of-free-will#ap-xviii@66",
           "19": "defense/of-the-cause-of-sin#ap-xix@76", "20": "defense/of-good-works#ap-xx@77",
           "21": "defense/of-the-invocation-of-saints#ap-xxi", "22": "defense/of-both-kinds-in-the-lords-supper#ap-xxii",
           "23": "defense/of-marriage-of-priests#ap-xxiii", "24": "defense/of-the-mass#ap-xxiv",
           "27": "defense/of-monastic-vows#ap-xxvii", "28": "defense/of-ecclesiastical-power#ap-xxviii"},
    # Part/article; the Preface is numbered on the document's first page.
    "sa": {"": "smalcald-articles/#", "Preface": "smalcald-articles/#@0", "1": "smalcald-articles/i/divine-majesty#",
           "2/1": "smalcald-articles/ii/first-and-chief-article#sa-ii-i", "2/2": "smalcald-articles/ii/of-the-mass#sa-ii-ii",
           "2/3": "smalcald-articles/ii/of-chapters-and-cloisters#sa-ii-iii", "2/4": "smalcald-articles/ii/of-the-papacy#sa-ii-iv",
           "3/1": "smalcald-articles/iii/of-sin#sa-iii-i", "3/2": "smalcald-articles/iii/of-the-law#sa-iii-ii",
           "3/3": "smalcald-articles/iii/of-repentance#sa-iii-iii", "3/4": "smalcald-articles/iii/of-the-gospel#",
           "3/5": "smalcald-articles/iii/of-baptism#sa-iii-v", "3/6": "smalcald-articles/iii/of-the-scarament-of-the-altar#sa-iii-vi",
           "3/7": "smalcald-articles/iii/of-the-keys#sa-iii-vii", "3/8": "smalcald-articles/iii/of-confession#sa-iii-viii",
           "3/9": "smalcald-articles/iii/of-excommunication#", "3/10": "smalcald-articles/iii/of-ordination#sa-iii-x",
           "3/11": "smalcald-articles/iii/of-the-marriage-of-priests#sa-iii-xi", "3/12": "smalcald-articles/iii/of-the-church#",
           "3/13": "smalcald-articles/iii/of-good-works#sa-iii-xiii", "3/14": "smalcald-articles/iii/of-monastic-vows#sa-iii-xiv",
           "3/15": "smalcald-articles/iii/of-human-tradition#sa-iii-xv"},
    # Paragraphs 1-82 run through both pages.
    "tr": {"": "power-and-primacy/treatise-compiled-at-smalcald#tr-i 60>power-and-primacy/power-and-jurisdiction-of-bishops#tr-ii"},
    "sc": {"": "small-catechism/preface#sc-preface", "Preface": "small-catechism/preface#sc-preface",
           "1": "small-catechism/ten-commandments#sc-ten-commandments", "Ten Commandments": "small-catechism/ten-commandments#sc-ten-commandments",
           "2": "small-catechism/the-creed#sc-creed", "Creed": "small-catechism/the-creed#sc-creed",
           "3": "small-catechism/the-lords-prayer#sc-lords-prayer", "Lord's Prayer": "small-catechism/the-lords-prayer#sc-lords-prayer",
           "Lord’s Prayer": "small-catechism/the-lords-prayer#sc-lords-prayer",
           "4": "small-catechism/the-sacrament-of-holy-baptism#sc-baptism", "Baptism": "small-catechism/the-sacrament-of-holy-baptism#sc-baptism",
           "5": "small-catechism/how-christians-confess#sc-christian-confession", "Confession": "small-catechism/how-christians-confess#sc-christian-confession",
           "6": "small-catechism/the-sacrament-of-the-altar#sc-sacrament-altar",
           "Sacrament of the Altar": "small-catechism/the-sacrament-of-the-altar#sc-sacrament-altar",
           "Daily Prayers": "small-catechism/daily-prayers#sc-daily-prayers", "Table of Duties": "small-catechism/table-of-duties#sc-table-duties"},
    "lc": {"": "large-catechism/preface#lc-preface", "Preface": "large-catechism/preface#lc-preface",
           "Short Preface": "large-catechism/preface#lc-preface",
           "1": "large-catechism/ten-commandments#lc-i", "Ten Commandments": "large-catechism/ten-commandments#lc-i",
           "2": "large-catechism/apostles-creed#lc-ii", "Creed": "large-catechism/apostles-creed#lc-ii",
           "3": "large-catechism/lords-prayer#lc-iii", "Lord's Prayer": "large-catechism/lords-prayer#lc-iii",
           "Lord’s Prayer": "large-catechism/lords-prayer#lc-iii",
           "4": "large-catechism/holy-baptism#lc-iv", "Baptism": "large-catechism/holy-baptism#lc-iv",
           "5": "large-catechism/sacrament-of-the-altar#lc-v", "Sacrament of the Altar": "large-catechism/sacrament-of-the-altar#lc-v"},
    "ep": {"": "epitome/rule-and-norm#ep-rule-and-norm", "Summary": "epitome/rule-and-norm#ep-rule-and-norm",
           "Rule and Norm": "epitome/rule-and-norm#ep-rule-and-norm",
           "1": "epitome/original-sin#ep-i", "2": "epitome/free-will#ep-ii", "3": "epitome/righteousness-of-faith#ep-iii",
           "4": "epitome/good-works#ep-iv", "5": "epitome/law-and-gospel#ep-v", "6": "epitome/third-use-of-the-law#ep-vi",
           "7": "epitome/the-lords-supper#ep-vii", "8": "epitome/person-of-christ#ep-viii",
           "9": "epitome/descent-of-christ-into-hell#ep-ix", "10": "epitome/church-rites#ep-x",
           "11": "epitome/election#ep-xi", "12": "epitome/other-sects#ep-xii"},
    "sd": {"": "solid-declaration/preface#sd-preface", "Preface": "solid-declaration/preface#sd-preface",
           "Introduction": "solid-declaration/preface#sd-preface",
           "Summary": "solid-declaration/rule-and-norm#sd-ruleandnorm", "Rule and Norm": "solid-declaration/rule-and-norm#sd-ruleandnorm",
           "1": "solid-declaration/original-sin#sd-i", "2": "solid-declaration/free-will#sd-ii",
           "3": "solid-declaration/righteousness-of-faith#sd-iii", "4": "solid-declaration/good-works#sd-iv",
           "5": "solid-declaration/law-and-gospel#sd-v", "6": "solid-declaration/third-use-of-the-law#sd-vi",
           "7": "solid-declaration/the-holy-supper#sd-vii", "8": "solid-declaration/person-of-christ#sd-viii",
           "9": "solid-declaration/christs-descent-into-hell#sd-ix", "10": "solid-declaration/church-rites-adiaphora#sd-x",
           "11": "solid-declaration/election#sd-xi", "12": "solid-declaration/other-sects#sd-xii"},
    # The Catalog's articles have no anchors of their own.
    "ct": {"": "testimonies/#the-catalog-of-testimonies#", "Preface": "testimonies/#to-the-christian-reader#",
           "Conclusion": "testimonies/#conclusion#"},
    "bc": {"": "preface/#preface-to-the-christian-book-of-concord#"},
    "apc": {"": "ecumenical-creeds/apostles-creed#"}, "nc": {"": "ecumenical-creeds/nicene-creed#"},
    "athc": {"": "ecumenical-creeds/athanasian-creed#"},
}
_ROMAN = re.compile(r"[IVXL]+(?![A-Za-z])")


def _roman_value(text: str) -> int:
    values = {"I": 1, "V": 5, "X": 10, "L": 50}
    total = 0
    for i, c in enumerate(text):
        v = values[c]
        total += -v if i + 1 < len(text) and values[text[i + 1]] > v else v
    return total


def _concord_page(spec: str, para: Optional[int]) -> str:
    """A CONCORD_PAGES entry and a paragraph: the URL."""
    parts = spec.split(" ")
    page = parts[0]
    for more in parts[1:]:
        first, other = more.split(">", 1)
        if para is not None and para >= int(first):
            page = other
    m = re.fullmatch(r"([^#]*)#([^@]*)(?:@(-?\d+))?", page)
    path, prefix, offset = m.group(1), m.group(2), m.group(3)
    url = CONCORD_SITE + path + ("" if path.endswith("/") else "/")
    if prefix.endswith("#"):                 # a fixed anchor
        return url + "#" + prefix[:-1]
    if not prefix and offset is None:        # no anchors
        return url
    n = (para if para is not None else 1) + int(offset or 0)
    return url + "#" + (prefix + "-" if prefix else "") + "%04d" % n


def concord_url(text: str) -> Optional[str]:
    """Where a reading from the Book of Concord opens, at its first article and
    paragraph ("Augsburg Confession XX 1–8", "Apology 4:117–146", "Smalcald
    Articles 3/3:1–18", "Treatise 12–21", "Small Catechism, Baptism",
    "Formula of Concord, Solid Declaration 2:1–7"), or None when it cites none
    (page.js: concordUrl)."""
    t = _trim(str(text))
    key = rest = None
    for name, k in CONCORD_DOCS:
        if t.startswith(name) and not re.match(r"[A-Za-z]", t[len(name):len(name) + 1]):
            key, rest = k, _trim(t[len(name):].lstrip(",:;"))
            break
    if key is None:
        return None
    pages = CONCORD_PAGES[key]
    word = next((w for w in sorted(pages, key=len, reverse=True)
                 if w and not re.fullmatch(r"[\d/]+", w) and rest.startswith(w)), None)
    if word:
        m = re.search(r"(\d+)", rest[len(word):])
        return _concord_page(pages[word], int(m.group(1)) if m else None)
    # Arabic: article[:paragraph], or part/article[:paragraph] (the Smalcald
    # Articles), or part:paragraph; the Treatise by paragraph alone.
    m = re.match(r"(\d+)(?:/(\d+))?(?::(\d+))?", rest)
    if m:
        a, b, para = m.group(1), m.group(2), m.group(3)
        if key == "tr":
            return _concord_page(pages[""], int(a))
        art = a + "/" + b if key == "sa" and b else a
        spec = pages.get(art)
        return _concord_page(spec, int(para) if para else None) if spec else _concord_page(pages[""], None)
    m = re.match(r"([IVXL]+)(?![A-Za-z])(?:\s+([IVXL]+)(?![A-Za-z]))?(?:\s+(\d+))?", rest)
    if m:
        a, b, para = m.group(1), m.group(2), m.group(3)
        if key == "sa" and a in ("II", "III"):
            art = str(_roman_value(a)) + "/" + str(_roman_value(b) if b else 1)
        else:
            art = str(_roman_value(a))
        spec = pages.get(art)
        return _concord_page(spec, int(para) if para else None) if spec else _concord_page(pages[""], None)
    return _concord_page(pages[""], None)


_ALTERNATIVES = re.compile(r"( or |, or the Passion History| or [Tt]he [A-Z][a-z]+ [A-Za-z ]+\Z)")


def reading_links(text: str, version: str = "ESV", site: str = "biblegateway",
                  numbering=None, cite: Optional[str] = None) -> list[tuple[str, Optional[str]]]:
    """A reading as (text, url) parts: each alternative ("A or B") opens on its
    own, and the words between them have no url (page.js: readingLinks).
    `cite`: the reading in the English verses, where the church cites its own
    psalter's (lectionary.readings_index); the links open that."""
    out: list[tuple[str, Optional[str]]] = []
    parts = _ALTERNATIVES.split(str(text))
    targets = _ALTERNATIVES.split(str(cite)) if cite else parts
    if len(targets) != len(parts):
        targets = parts
    for part, target in zip(parts, targets):
        if not part:
            continue
        concord = None if re.match(r" or |, or ", part) else concord_url(part)
        if concord:
            out.append((part, concord))
        elif re.match(r" or |, or ", part) or not (re.search(_D, part) or APOCRYPHA.match(part)):
            out.append((part, None))
        else:
            out.append((part, bible_url(target, version, site, numbering)))
    return out


def reading_choices(text: str) -> list[str]:
    """A reading's choices: each part of "A or B" that cites verses, or a book of
    the Apocrypha whole ("Prayer of Manasseh") (page.js: readingChoices)."""
    return [part for part in _ALTERNATIVES.split(str(text))
            if part and not re.match(r" or |, or ", part) and (re.search(_D, part) or APOCRYPHA.match(part))
            and not concord_url(part)]


def group_citation(readings, numbering=None, english: bool = True, canon: bool = False) -> str:
    """A set's readings as one search, every choice of each, joined with
    semicolons; in the English numbering when `english`; without the
    Apocrypha when `canon` (page.js: groupCitation).  The Book of Concord is
    never in it (reading_choices)."""
    return "; ".join(plain_citation(convert(c, numbering) if english and numbering else c)
                     for text in readings for c in reading_choices(text)
                     if not (canon and APOCRYPHA.match(plain_citation(c))))


def group_url(readings, version: str = "ESV", numbering=None) -> str:
    """Bible Gateway with a set's readings together, one after another
    (page.js: groupUrl).  Bible.com opens one passage at a time, so a set
    always opens at Bible Gateway; a version it does not carry, or a set with
    nothing it has (the Book of Concord), gives none ("")."""
    if version in NOT_AT_BIBLE_GATEWAY:
        return ""
    if version not in APOCRYPHA_AT_BIBLE_GATEWAY and any(
            APOCRYPHA.match(plain_citation(c)) for text in readings for c in reading_choices(text)):
        version = "RSV"
    q = group_citation(readings, numbering, version not in HEBREW_NUMBERED)
    if not q:                       # nothing Bible Gateway has (the Book of Concord)
        return ""
    return ("https://www.biblegateway.com/passage/?search=" + encode_uri_component(q)
            + "&version=" + encode_uri_component(version))


def word_to_worship_url(readings, numbering=None) -> str:
    """Word to Worship's search for songs on a set's readings
    (page.js: wordToWorshipUrl).  It knows the Protestant canon only, so the
    Apocrypha and the Book of Concord are left out, and a set of nothing else
    has none ("")."""
    cited = group_citation(readings, numbering, True, canon=True)
    if not cited:
        return ""
    q = encode_uri_component("{" + cited + "}")
    return "https://wordtoworship.com/search/node/" + q.replace("%3A", ":").replace("%3B", ";")


# Hymnary.org's results in the hymnal's own order (page.js: HYMNARY_ORDER).
HYMNARY_ORDER = "&sort=hymnalNumber&order=asc"


def hymnary_url(readings, hymnal: str, numbering=None) -> str:
    """Hymnary.org's search for the hymns of one hymnal on a set's readings
    (tradition.csv `hymnary_hymnal`, its code there: lsb2006) (page.js:
    hymnaryUrl).  Its scripture index is written with hyphens.  As for Word
    to Worship, the Apocrypha and the Book of Concord are left out, and a set
    of nothing else, or a church with no hymnal there, has none ("")."""
    cited = group_citation(readings, numbering, True, canon=True)
    if not cited or not hymnal:
        return ""
    q = f"scripture:{cited.replace(chr(0x2013), '-')} hymnalNumber:{hymnal} in:instance"
    return "https://hymnary.org/search?qu=" + encode_uri_component(q) + HYMNARY_ORDER


def feast_url(name: str, link: str = "", pattern: str = "") -> str:
    """Where to read about a commemoration: its own link, the tradition's
    pattern (tradition.csv `feast_link`), or Wikipedia (page.js: feastUrl)."""
    if link:
        return link
    clean = _trim(re.sub(rf"{_S}*\(transferred from [^)]*\)", "", str(name), count=1))
    pattern = _trim(str(pattern or ""))
    if pattern and "{name}" in pattern:
        return pattern.replace("{name}", encode_uri_component(clean))
    # The name before its first comma ("St. James of Jerusalem, Brother of Jesus
    # and Martyr") is the one an encyclopedia knows.
    short = re.sub(r"^The ", "", re.sub(r"^St\.? ", "Saint ", clean.split(",")[0], count=1), count=1)
    return "https://en.wikipedia.org/w/index.php?search=" + encode_uri_component(short)
