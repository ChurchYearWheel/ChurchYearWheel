# Data that disagree with sources

Found in October 2026 while looking for sources for the uncited data and colors (see [provenance.md](provenance.md)). Each item gives the file and row, what the calendar has, what the source says and a suggested fix. Where a source gives two colors the first is drawn and the others are named in the page readout. A published source (a hymnal, a prayer book, a church's printed lectionary) is preferred to a website, unless the church has officially changed its use since it was printed. Where a church's use changed in a known year, the change applies from that year and the oldest use on record covers the years before.

## Status

**Applied (version 85):**

- Armenian 1–3: the Sundays after the Nativity and after the Assumption; the Advent wording.
- Ethiopian 1–2 and Coptic 3: Aster'eyo Mariam; the Fast of the Prophets from 15 Hidar; Coptic white vestments with black hangings in Holy Week.
- West Syriac: Mor Barsawmo a feast; the Patriarchate and Malankara fasts split by variant.
- Assyrian: the Cross on 13 September; Shlikhe; the Praise of the Virgin, Peter and Paul and the two Marian feasts.
- Byzantine 5–9: black Great Lent with purple on its weekends; gold Nativity (white named); Pascha white (bright red named); Great Thursday dark red; St Catherine on 24 November.
- Church in Wales: the 2011 scheme from the 2011–12 year, the 1984 colors before it, including the Paul feasts and All Souls.
- Anglican Church of Canada: the Conversion of St Paul white.
- Episcopal: purple Advent and Lent, royal blue and unbleached linen named.
- LSB (LCMS, LCC): Ash Wednesday stays black, which LSB lists first; violet, gold and violet named for Ash Wednesday and Advent, Easter Day and Holy Week.
- ELCA: Ash Wednesday purple; Holy Week purple; scarlet lesser festivals; the Sunday of the Passion and Holy Saturday as the lists give them; the Emanuel Nine added.
- LCA, Iceland, Finland, Estonia, United Methodist: the first-listed colors, with the options named.
- Good Friday and other days with no color are drawn as white hatched with gray and read "no color".

**Applied (version 172):**

- Ethiopian 5: Gizret (6 Tir) and Megabit Meskel (10 Megabit); Lidete Simeon and the Advent Sundays wait for their dates.
- Methodist Church in Britain 20 and 22: the Sundays of the Passion named; Mothering Sunday and Remembrance Sunday.
- Reformed 25: the RCA's Reformation Sunday (the Sunday before 31 October, unless 31 October is a Sunday) and Reformation Day.

**Still open** (the items below that are not listed above), chiefly: WELS's Christian Worship (2021) colors; Estonia's 1st Sunday of Advent (white or violet); Sweden's disputed days; LSB Maundy Thursday (LSB's first color not confirmed); Norway's Day of Repentance; the Syriac feasts of 30 June and 3 July; the Ethiopian minor feasts without known dates; the Armenian additions; the Ruthenian Holy Eucharist and St Josaphat. Strike an item off (or delete it) when it is fixed or decided, and update the matching row of `provenance.csv`.

## Armenian

Web fetching hit a rate limit partway through. I checked the Armenian data against sources I opened. I opened no Ethiopian or Coptic pages, so those sections only list what still needs checking.

### Armenian (data/Armenian)

#### 1. days.csv `after_nativity`: the count starts a week too early in some years
- **Repo:** `after_nativity` runs from `@theophany+1` (7 January), with the first Sunday numbered 1. In 2025, Sunday 12 January becomes "1st Sunday after Nativity".
- **Source:** The Prelacy's 2025 lectionary has 12 January as "Seventh Day of Nativity" and 19 January as "First Sunday after Nativity (octave)". 26 January is "Second Sunday after Nativity" and 2 February is "Third Sunday after Nativity". https://armenianprelacy.org/wp-content/uploads/2025/01/01-January-2025.pdf and .../02-February-2025.pdf
- **Fix:** Start the run after the octave: `from` = `01-14` (the day after the Naming, 13 January). The count is then right every year. Also check that the `NATIVITY` season in periods.csv (01-06 to 01-13) still lines up.

#### 2. days.csv `after_assumption`: the numbering is one too high
- **Repo:** `after_assumption` has `first` = 2, so the Sunday a week after the Assumption is "2nd Sunday after the Assumption".
- **Source:** In the Prelacy's 2025 lectionary, the Assumption falls on 17 August. 24 August is "First Sunday after the Assumption of the Holy Mother of God", 31 August is "Second Sunday after the Assumption" and 7 September is "Third Sunday after the Assumption". https://armenianprelacy.org/wp-content/uploads/2025/01/08-August-2025.pdf and .../09-September-2025.pdf
- **Fix:** Set `first` = 1.
- For comparison, the same source counts the feast itself as Sunday 1 for the Transfiguration ("Second Sunday of Transfiguration", 3 Aug) and for the Cross ("Second Sunday of the Exaltation", 21 Sep; "Seventh Sunday of the Exaltation", 26 Oct). For these two the repo's `first` = 2 already gives the same numbers. The Prelacy's wording is "of the Transfiguration/of the Exaltation", not "after". You could also rename those titles to match.

#### 3. Advent (Hisnak): the start and the "fifty days" don't fit together
- **Repo:** tradition.csv `year_start` is `sun>=11-22`, the Sunday nearest 25 November. docs/traditions.md says Advent is "fifty days from the Sunday nearest 25 November". The days.csv header comment says the same.
- **Sources:**
  - The Prelacy's November 2025 lectionary has 16 November as "Tenth Sunday of the Exaltation of the Holy Cross (Eve of the Fast of Advent)" and 23 November as "First Sunday of Advent". https://armenianprelacy.org/wp-content/uploads/2025/01/11-November-2025.pdf
  - Armenian Church Sydney: "Advent begins on the day after the Sunday nearest November 18". https://armenianchurchsydney.org.au/hisnag/
  - Diocese of Georgia: Advent from "the Sunday nearest to the 25th of November". https://www.armenianchurch.ge/en/kalendar-prazdnikov/description-2/november/eve-of-the-fast-of-advent
  - Eastern Diocese: Hisnag is "the 50-day period" before the Nativity. https://armenianchurch.us/?p=2427
- **Analysis:** The repo's start date is right for the *First Sunday of Advent*. The fifty days, though, run from the Monday after the Sunday nearest 18 November (the Advent fast) to 5 January: 17 Nov to 5 Jan 2025-26 is 50 days. From the Sunday nearest 25 November it is only about 44 days.
- **Fix (minimum):** Change the wording in docs/traditions.md and the days.csv comment to "about fifty days from the Monday after the Sunday nearest 18 November; the First Sunday of Advent is the Sunday nearest 25 November".
- **Fix (optional):** Start the Advent season a week earlier, at the eve of the Advent fast (`sun>=11-15`).

#### 4. Not verified, and possible additions (no clear conflict)
- I did not verify the "Remembrance of the Dead" (Merelots) rows: 7 Jan, Easter+1, Vardavar+1, Assumption+1 and Exaltation+1. The Prelacy lectionary does not list them; for example, 7 January is "Second Day of Nativity". Fetching a Prelacy page on Merelots failed because of the rate limit.
- These days are in the Prelacy's 2025 lectionary but not in the repo, so you may want to add them:
  - Easter+28, "Apparition of the Holy Cross" (18 May 2025). The repo calls it "5th Sunday of Eastertide".
  - The Passion and Descent into the Pit of St Gregory, Saturday before the 6th Sunday of Lent (5 Apr 2025).
  - The Discovery of the Box of the Theotokos, 5th Sunday after Pentecost (13 Jul 2025).
  - The Belt of the Theotokos, 2nd Sunday after the Assumption (31 Aug 2025).
- The full name of `green_sunday` is "Sunday of the World Church (Kanach Kiraki)". The Prelacy just says "Green Sunday". I did not verify the extra name.
- The repo's "Holy Martyrs of the Genocide" (24 Apr) is called "Commemoration of the Holy Martyrs of 1915" in the Prelacy lectionary. Either name is fine.

#### 5. Colors
None of the Armenian church pages I opened say anything about a seasonal color cycle. Nothing I found contradicts the repo's note that the church prescribes none. The white/gold/violet/black scheme is still the project's own choice, and provenance should keep calling it that (`guess`).

## Ethiopian and Coptic

### 1. Ethiopian 21 Tir: the feast's name
- **File/row:** `data/Ethiopian/feasts.csv`, `e0521` (name `Astemehro`)
- **Repo:** "Astemehro"
- **Source:** "Aster'eyo Mariam", glossed "Aster'eyo/revelation/", and "died honorably on Tir 21" (https://eotcmk.org/e/asterio-mariam/). Other Mahibere Kidusan posts spell it "Astereyo Mariam" (https://eotcmk.org/e/the-commemoration-of-the-death-of-st-mary-astereyo-mariam/, seen in search results only).
- **Fix:** set name to `Aster'eyo Maryam` (or `Asterio Maryam`). The date (21 Tir) is correct.

### 2. Ethiopian Fast of the Prophets starts a day late
- **File/row:** `data/Ethiopian/days.csv` `advent_fast` (`@genna-43`); `data/Ethiopian/periods.csv` season `Tsome Nebiyat` (start `@genna-43`) and `After Meskel` (end `@genna-44`)
- **Repo:** 43 days before Genna, which is 25 November
- **Source:** "starts on 15th Hedar (November 24) ... ends on Christmas eve 28th of Tahsas (January 06)", "44 days of fast" (https://eotcmk.org/e/the-fast-of-the-prophets-tsome-nebiyat/). The 2015 post gives "Hidar 15 (November 25)" with 43 days, because that was the year before a Gregorian leap year (https://eotcmk.org/e/?p=3893). The church site also gives "15 Hedar to Christmas eve" (https://www.ethiopianorthodox.org/english/calendar.html).
- **Fix:** use `ethiopian(03-15)` for `advent_fast` and the season start, and `ethiopian(03-14)` for the end of `After Meskel`. This gives 24 November most years and 25 November in the year before a leap year. The Coptic `@nativity-43` (25 November) is correct and should stay as it is. Also update the full_name ("forty-three days" should read "from 15 Hidar; 44 days, 43 in the year before a leap year").

### 3. Coptic colors: black is the church's hangings, not the vestments
- **Files:** `data/Coptic/tradition.csv` comment ("Its vestments are white all year, black in Holy Week"); `docs/provenance.csv` oriental-coptic,colors ("following the vestments"); `docs/traditions.md` Coptic bullet ("Vestments are white all year and black in Holy Week") and the sentence "Except for the Coptic church, these churches prescribe no cycle of colors."
- **Repo:** the vestments turn black in Holy Week, and the Coptic church prescribes a color cycle
- **Source:** the tonia is "A white tunic worn by all monks and priests while celebrating the Holy Mass" (https://st-takla.org/faith/en/terms/tonya.html). In Holy Week "Black veils are draped over the walls and along the columns of the church" and icons are covered in black, then "replaced with glowing white veils" for the Resurrection (https://egyptianstreets.com/2023/04/09/what-is-holy-week-and-how-do-copts-celebrate-it/).
- **Fix:** reword to say that vestments are white and that in Holy Week the church is hung in black and its icons veiled. Say that no church prescribes a color cycle; the Coptic wheel follows this practice. The wheel's colors themselves can stay as they are.

### 4. Coptic and Ethiopian Nativity label in years after a leap year (minor)
- **Files/rows:** `data/Coptic/days.csv` `nativity` full_name "(29 Koiak)"; `data/Ethiopian/days.csv` `genna` full_name "(29 Tahsas)"; `docs/traditions.md` "The Nativity is kept on 29 Koiak, 7 January"
- **Repo:** the date rule is `julian(12-25)`, which is always 7 January. That is right. The label always says 29.
- **Source:** the Synaxarium lists the Nativity under Kiahk 29 (https://copticchurch.net/synaxarium/4_29.html). It is kept on 7 January (https://www.copticchurch.net/calendar/feasts/2026, https://brilliant-ethiopia.com/guide/festivals). The repo's own arithmetic makes 29 Koiak fall on 8 January 2028, so the feast falls on 28 Koiak/Tahsas that year. That it moves to 28 Koiak/Tahsas, rather than the label being wrong, is from memory and unverified.
- **Fix:** optional. Change the label to "(29 Koiak; 28 in the year after a leap year)", or drop the day number.

### 5. Ethiopian minor feasts of the Lord missing (omission)
- **File:** `data/Ethiopian/days.csv`
- **Repo:** has Kana (12 Tir) and Debre Zeit. It does not have Gizret (Circumcision, 6 Tir), Lidete Simeon (Presentation), Megabit Meskel (10 Megabit), or the Advent Sundays Sibket, Birhan and Nolawi.
- **Source:** "Minor feasts of the Lord (9): Sibket, Brahan, Nolwae, Gena, Gizret, Kana ze Galilee, Debra zeit, Megabit Meskel, Ledete Simon" (https://www.ethiopianorthodox.org/english/calendar.html). "Our Lord and Savior Jesus Christ's Circumcision is celebrated on Tir 6" (https://eotcmk.org/e/?p=8511).
- **Fix:** add at least `gizret` `ethiopian(05-06)` and `megabit_meskel` `ethiopian(07-10)`. Leave Lidete Simeon and the Advent Sundays until a source gives their exact dates (not verified here).

### 6. Coptic month spellings (style, not an error)
- **File:** `data/Coptic/days.csv` `sundays_01`–`sundays_13` titles
- **Repo:** Thout, Paopi, Hathor, Koiak, Tobi, Meshir, Paremhat, Parmouti, Pashons, Paoni, Epip, Mesori
- **Source:** the Katameros heading reads "First Sunday of Amshir" (https://saintbishoy.ca/wp-content/uploads/Katameros_Sunday_Readings_Amshir.pdf). The Synaxarium uses Tout, Kiahk, Mesra and Paona (copticchurch.net/synaxarium).
- **Fix:** optional. Use the church's own spellings if the titles are meant to follow the Katameros.

### Not verified (no disagreement found, but no source either)
- Ethiopian `rikbe_kahinat` at Easter+24, `apostles` on 5 Hamle (the Coptic 5 Epip, the same calendar day, is verified), Gabriel on 19 Hamle (the source names Hamle without a day), and Nineveh at Easter-69 for Ethiopia directly (the Coptic date is verified for 2026).
- The Coptic "Sunday of the Little Month" in the Katameros.
- Covenant Thursday shown in WHITE (Coptic).
- Ethiopian colors: no source prescribes any. They stay the project's own scheme (guess).
- Encyclopaedia Aethiopica and suscopts.org were not opened. Wikipedia was not used.

## Syriac Orthodox, Malankara and Assyrian

Sources fetched:
- SOR: Skaria, "Automating the Liturgical Calendar of the Syrian Orthodox Church" (2003), https://syriacorthodoxresources.org/Calendar
- WUS: Syriac Orthodox Church (Western US) site, https://soc-wus.org/ourchurch/syriac%20calendar.htm
- AND: Rev. Tower Andrious, "The Ecclesiastical Liturgical Year for the Church of the East" (Assyrian Church of the East, Beth Kokheh), https://bethkokheh.assyrianchurch.org/wp-content/uploads/2020/08/The-Liturgical-Year.pdf
- CAL24: Assyrian Church of the East (California) 2024 calendar, https://acoecalifornia.org/files/2024-Calendar-without-photos.pdf
- LEC: ACOE lectionary (labeled 2024, dates for Nov 2024-Dec 2025), https://maryosipparish.org/documents/assyrian/Propers2024.html
- MAC: Maclean, East Syrian Daily Offices (1894), transcription at https://www.bombaxo.com/an-east-syrian-kalendar-and-lectionary-maclean/
- GEDSH: Coakley, "Shemʿon, Eshai," https://gedsh.bethmardutho.org/Shemon-Eshai

- NEA: Northeast American Diocese, Malankara Orthodox Syrian Church, "Feasts & Memorials," https://www.neamericandiocese.org/feasts
- KL: "Fasting in the Malankara Orthodox Syrian Church" (adapted from mosc.in), https://orthodoxchurchmy.com/blog/fasting-in-the-malankara-orthodox-syrian-church/
- BLR: Bangalore Orthodox Diocese, "Feasts and Fasts," https://www.bangaloreorthodoxdiocese.org/?p=3415
- DXB: St Thomas Orthodox Cathedral Dubai, https://www.stthomascathedraldubai.com/lent-feast-days
- UKE: Malankara Diocese of UK-Europe and Africa, Easter circular dated 11 April 2020, https://indianorthodoxuk.org/storage/4MJh2rOlf9m6xjsxAnVRLVXUV68SwXkO1FNLqwek.pdf
- BSM: St Mary's JSO Cathedral, Bengaluru (Syriac Orthodox in India), https://bsmcathedral.org/Liturgical_calendar.html
- BAR: Afram Barsoum, *Golden Key to the Divine Worship* (1951), as given at https://syriacorthodoxresources.org/Feast/fasts.html

Not usable:
- syriacpatriarchate.org: no fast-date page turned up in search.
- mosc.in: the home page loaded, but calendar.mosc.in shows only the current month.
- assyrianchurch.org: event pages are blocked by robots.txt.
- news.assyrianchurch.org: the Holy Cross article gives no day.

### West Syriac (data/Syriac)

1. **periods.csv, "Apostles' Fast" 06-16..06-28 (both variants).**
   - Repo: 13 days, 16-28 June, for both variants.
   - The Syriac Orthodox Church keeps three days from 26 June:
     - BAR: "Three days commencing of the 26th of June."
     - SOR: "Formerly 13 days, beginning on the 16th."
     - WUS and BSM: 26-29 June.
   - The Malankara Orthodox keep 13 days, 16-29 June (KL: "from June 16 to 29"; BLR and DXB agree). NEA lists the "Apostles' Fast" on 16 Jun.
   - Fix: split by variant. Keep `malankara` at 06-16..06-28. Make `syriac` 06-26..06-28, adjusting the `when` guard; Pentecost can never be later than 26 June.

2. **periods.csv, "Shunoyo Fast" 08-01..08-14 (both variants).**
   - Repo: 1-14 August, for both variants.
   - Syriac Orthodox: BAR has "Five days commencing on the 10th of August." SOR, WUS and BSM give 10-15 August, "formerly ... August 1."
   - Malankara: KL has "starts from the first day of August and ends with the Soonoyo feast on the fifteenth day." BLR and DXB agree, and NEA lists "Virgin Mary's Fast" on 1 Aug.
   - Fix: keep `malankara` at 08-01..08-14 and make `syriac` 08-10..08-14.

3. **periods.csv, Nativity fast (syriac 12-15..12-24).** Agrees with the sources. SOR and WUS: "begins December 1, but is obligatory only from December 15."

4. **docs/traditions.md, "Malankara keeps a 25-day Nativity fast", against periods.csv 12-01..12-24.**
   - These are not in conflict.
   - KL (from mosc.in): "this fast lasts for 25 days, from the first of December till the Christmas day." BLR and DXB agree.
   - The 25 days count Christmas Day, which the data show as the feast. Both the data and the docs are right.
   - Optional doc wording: "the 25-day Nativity fast, 1 December to Christmas".

5. **days.csv year start (`sun<12-25-49`).**
   - This matches SOR and WUS: Qudosh Idto is "the last Sunday of October if that is the 30th or 31st, otherwise the first Sunday of November".
   - No change needed.

6. **feasts.csv: items not found in sources, or found on other dates.**
   - St George 04-23 is confirmed by NEA.
   - Not confirmed anywhere: First church of the Virgin 06-15, Baselios Yeldo 10-02, Sergius and Bacchus 10-07.
   - St Thomas 07-03 applies to both variants, but NEA (Malankara) lists Thomas only on 21 Dec. 3 July is the Latin and Syro-Malabar date. Consider limiting it to `syriac`, or confirm it for Malankara.
   - "All Saints; Mor Yaqub Burdono" 06-30: NEA has the "12 Apostles" on 30 Jun and "St. Jacob Baradaeus" on 28 Nov. Check before keeping it.
   - Missing from the repo but in SOR and NEA: Holy Innocents 27 Dec, Mary of the Sowing 15 Jan, Mary of the Harvest 15 May.

6a. **days.csv movable saints' days, against NEA's fixed dates.**
   - Repo: `severius` easter-66, `ephrem` easter-43, `barsawmo` easter+46.
   - NEA lists St Severus of Antioch on 8 Feb, St Barsaumo on 3 Feb, and St Ephrem with St Theodore on 24 Feb, all as fixed dates in a 2025 list.
   - NEA's dates may be one year's instance of a movable rule. Ephrem and Theodore are traditionally on the first Saturday of Lent, which would make 24 Feb 2025 an odd date.
   - Barsaumo on 3 Feb is a well-known fixed date, so easter+46 looks wrong.
   - Fix: check a printed Malankara or Patriarchate calendar. At minimum, move Barsawmo to 02-03 in feasts.csv.

6b. **Malankara-only feasts.** Both are confirmed by NEA: Parumala on 2 Nov ("St. Geevarghese Mar Gregorios") and "St. Thomas the Apostle" on 21 Dec. NEA does not label 21 Dec as his martyrdom.

6c. **Easter.**
    - Malankara: Skaria says the church switched "entirely" to the Gregorian calendar in 1953. Indirect support for the Western Easter: UKE's Easter circular is dated 11 April 2020 (the Western Easter was 12 April, the Julian 19 April), and BSM, a Syriac Orthodox cathedral in India, lists Easter 2026 on 5 April, the Western date.
    - No fetched Malankara Orthodox page states the Easter rule outright.
    - The Syriac Orthodox Church in India also keeps the Western Easter, so the `syriac` variant's Julian paschalion describes the Patriarchate outside India only. The docs could say so.

7. **Names.**
   - NEA (Malankara) spells "Suboro" exactly as the repo does, but writes "Ma`altho" where the repo has "Mayaltho".
   - SOR uses ma`alto and soboro.
   - Not an error. "Ma`altho" would match an official Malankara source.

8. **Colors.** None of SOR, WUS, BSM or the Malankara pages mentions liturgical colors, and no fetched source prescribes a seasonal color cycle for the Syriac Orthodox or Malankara churches. The white, gold, violet and black wheel is a project choice. The existing "guess" status is right.

### Assyrian Church of the East (data/Assyrian)

9. **days.csv `sliba` 09-14.**
   - Repo: Feast of the Cross on 14 September.
   - AND: "This feast happens in The Church of the East precisely on the 13th of September" and "not on 14th of September, but on the 13th."
   - CAL24: "September 13, Feast of the Finding of the Holy Cross."
   - LEC: "Sep 13: Feast of the Holy Cross."
   - MAC: "Feast of the Cross, September 13."
   - Fix: set `sliba` to 09-13.
   - The Church's own news site (news.assyrianchurch.org, "San Diego church marks Feast of the Holy Cross") says only "celebrated each year in September". The assyrianchurch.org event pages are blocked to fetching, so the date rests on the four sources above.

10. **days.csv / periods.csv Eliya rule `min(easter+147,sun<=09-13)`.**
    - AND: the period "begins at the latest on the Sunday before the cross."
    - With the Cross on 13 Sep, the Sunday before it is `sun<=09-12`. The current rule finds the Sunday before 14 Sep, which is 13 Sep itself whenever the 13th is a Sunday.
    - In such a year, with a late Easter, the repo starts Eliya one week late.
    - Fix: replace `sun<=09-13` with `sun<=09-12` everywhere in days.csv and periods.csv (eliya, qaita, moshe, the season and broad/half rows).
    - All other season rules were checked against CAL24 (2024) and LEC (2025) and match exactly: Ninevites, Great Fast, Easter, Pentecost/Apostles, Summer, Elijah, Moses, Hallowing and Subara.

11. **feasts.csv 12-26 "Praise of the Virgin Mary".**
    - Repo: fixed on 26 December. That is the West Syriac date (SOR: "Glorification of the Virgin: the day after Christmas").
    - AND: the East Syriac commemoration "falls on the day of the second Friday after Christmas" (the first Friday if a Friday coincides with the Nativity and the Epiphany). CAL24 has it on 5 January 2024, with St James.
    - Fix: a movable rule (the Friday after the Nativity, per AND), or drop the row.

12. **feasts.csv 06-29 "Sts. Peter and Paul".**
    - Repo: 29 June.
    - CAL24: Peter and Paul with the Four Evangelists on Friday 19 January 2024.
    - MAC lists "Friday. Patrus-Polus" among the Fridays of the Epiphany.
    - AND lists Peter and Paul among the Friday commemorations of the Epiphany period.
    - Fix: move it to the second Friday after Denha (in 2024, 19 Jan was the second Friday after 6 Jan), or drop it.

13. **feasts.csv 05-15 "Virgin Mary (of the Seeds)" and 08-15 "Virgin Mary (of the Vines)".**
    - The dates are confirmed. AND: "the second is on May 15 and the third is on August 15."
    - The labels are not confirmed. CAL24 calls 15 May "Commemoration of Mart Mariam the Blessed Virgin, Protectress of the Harvest" and 15 Aug "Falling Asleep (Dormition) of St. Mary", after the 1-15 August Rogation of the Virgin Mary.
    - SOR (West Syriac) puts the seeds on 15 Jan and the crops on 15 May.
    - Fix: rename 15 May "Virgin Mary (of the Harvest)" or "(of the Ears)", and 15 Aug "Dormition of the Virgin Mary".

14. **feasts.csv 03-25 Annunciation.** Not found in CAL24 or AND. The East Syriac Annunciation is the season of Subara, not a fixed day. This was not contradicted outright, but it is unconfirmed.

15. **Colors (colors.csv note, seasons.csv, RED in days.csv/feasts.csv).**
    - Neither AND (a long study of the year) nor CAL24 nor LEC mentions liturgical colors. The ACOE publishes none.
    - The provenance status should be "guess", not "inferred".
    - The RED used for Pentecost, Sliba, Peter and Paul and Thomas is not mentioned in the colors.csv note.

16. **Names.**
    - LEC uses Subara, Yalda, Denha, Shlikhe, Qaita (Nusardeil) and Qudash Edta, and CAL24 has Sawma Rabba.
    - The repo spells Shlihe; Shlikhe is the ACOE's own spelling.
    - Qyamta and Moshe were not seen verbatim; the fetched pages used English.

17. **tradition.csv: Easter.** The repo is correct.
    - No `paschalion_default`, so the Western Easter applies.
    - CAL24 has Easter on 31 March 2024, the Western date (the Julian Easter that year was 5 May).
    - GEDSH: the 1964 synodical letter of Mar Shimun XXIII Eshai adopted "the Gregorian calendar"; a schism followed in 1968 under Mar Toma Darmo (the Ancient Church of the East).
    - Wikipedia (last resort): the Ancient Church of the East kept the Julian Christmas until June 2010.
    - The Ancient Church's current Easter practice was not confirmed in a fetched source.

## Byzantine (Orthodox, UGCC, Ruthenian)

Scope: data/Orthodox/*.csv, docs/traditions.md ("The Eastern Orthodox churches"), docs/provenance.csv rows 75-80, 94.
Research was cut short by a fetch quota. OCA, GOARCH and Wikipedia pages were **not** fetched, so the fixed-feast list and the colors have not been checked against them.

### 1. Ruthenian variant of the Greek Catholic additions is unconfirmed
- **File/row:** data/Orthodox/feasts.csv, the last two rows (`easter+60` Holy Eucharist and `11-12` Josaphat, variant `ugcc ruthenian`). Also docs/provenance.csv row 78.
- **Repo:** both feasts apply to the Ruthenian church too.
- **Source:** the Archeparchy of Pittsburgh's 2026 calendar has no entry on Thursday 4 June 2026 (Pascha+60) and none on 12 November 2026. Its November entries go from 8 Nov (Archangels) to 15 Nov (St Philip's Fast) with nothing between. https://mci.archpitt.org/LiturgicalCalendar.html
- **Caveat:** that calendar does not list every day, so the gap is evidence, not proof. The docs text in traditions.md itself credits the additions only to the UGCC.
- **Suggested fix:** limit the variant to `ugcc`, or keep `ruthenian` and mark it `guess` in provenance until a Ruthenian Typikon or Liturgical Guide confirms it.

### 2. UGCC calendar named "Revised Julian"; the UGCC says "Gregorian"
- **File/row:** docs/traditions.md (Eastern Catholic paragraph), data/Orthodox/tradition.csv `calendar,revised-julian`, docs/provenance.csv row 76.
- **Repo:** the UGCC is "on the Revised Julian calendar since 2023".
- **Source:** "will follow the Gregorian style in celebrating the fixed holidays ... starting September 1, 2023". Movable feasts "will be kept following the current Paschal calendar". https://pdf.ugcc.ua/en/data/starting-september-1-ugcc-will-follow-the-gregorian-style-in-celebrating-fixed-feasts-the-head-of-the-ugcc-in-his-pastoral-message-556/ ; also https://ugcc.ua/en/data/historical-decision-the-ugcc-in-ukraine-switches-to-a-new-calendar-232/ (6 Feb 2023).
- **Effect:** none on dates before 2800, because the two calendars give the same dates until then.
- **Suggested fix:** wording only: "on the new (Gregorian / Revised Julian) style for fixed feasts since 1 September 2023 (UGCC in Ukraine; Julian paschalion kept)". Cite both UGCC pages.

### 3. Ruthenian English titles differ from the repo's
- **File/rows:** data/Orthodox/days.csv `indiction`, `thomas`, `holy_fathers`; data/Orthodox/feasts.csv `11-21`; periods.csv "Nativity Fast".
- **Repo:** Church New Year / Sunday of Thomas / Sunday before the Nativity / Entry of the Theotokos / Nativity Fast.
- **Source (Ruthenian):** "Beginning of the Church Year", "Thomas Sunday", "Sunday before the Nativity (Sunday of the Ancestors)", "Entrance of the Mother of God into the Temple", "St. Phillip's Fast". https://mci.archpitt.org/LiturgicalCalendar.html
- **Suggested fix:** optional `ruthenian` name variants. The current names are acceptable as general English usage.

### 4. Zacchaeus Sunday also carries its number in Ruthenian usage
- **File/row:** data/Orthodox/days.csv `zacchaeus` (claims=TRUE).
- **Source:** "Thirty-second Sunday after Pentecost; Sunday of Zacchaeus" (18 Jan 2026). https://mci.archpitt.org/LiturgicalCalendar.html
- **Suggested fix:** none needed if the page only shows the proper title. Note it in provenance.

### 5. Great Lent weekdays should be black, not dark red
- **Files:** data/Orthodox/seasons.csv `LENT,PURPLE` (#88023c, dark red), applied in periods.csv from easter-48 to easter-9, weekdays included. docs/traditions.md says "dark red for the Cross and the weekends of Lent", which disagrees with the data.
- **Source:** Nastol'naya Kniga, as translated: "During the first week of that Lent and on the weekdays of the following weeks, the vestment color is black. On Sundays and feast days of this period, the vestments are of a dark color with gold or coloured ornaments." https://catalog.obitel-minsk.com/blog/2016/12/the-liturgical-colors-of-vestments-in (same text at https://orthodoxwiki.org/Liturgical_colors)
- **Suggested fix:**
  - Color Lenten weekdays BLACK, and Saturdays and Sundays PURPLE (dark red).
  - Or keep the data and say in the docs that the whole of Lent is shown in the dark color.
  - Either way, cite the source above instead of "Wikipedia" in docs/traditions.md, colors.csv and provenance row 79.

### 6. The Nativity season is white in the repo, gold in the source
- **File/row:** data/Orthodox/seasons.csv `NATIVITY,WHITE`; periods.csv "Nativity and Theophany" from 12-25 to 01-14. Also feasts.csv `12-25` color WHITE.
- **Source:** "Gold is worn from Christmas to Epiphany", "in some places, white is worn on Christmas day". In Moscow style, "bright red is worn on Pascha and on the Nativity". White is given for "the feasts and post-feasts of Epiphany". https://catalog.obitel-minsk.com/blog/2016/12/the-liturgical-colors-of-vestments-in
- **Suggested fix:** use GOLD for 12-26 to 01-05, with 12-25 white or gold, and WHITE from Theophany (01-06) to 01-14. Or document white as a local custom.

### 7. Paschal season white: matches Carpatho-Russian use, not Russian
- **File/row:** seasons.csv `EASTER,WHITE`.
- **Source:** in Russian use, white is worn until the end of Paschal Matins and then "bright red ... throughout the Paschal season". By contrast, "In Carpatho-Russian style, in the Paschal season, white, exclusively, is worn." (same URL)
- **Suggested fix:** no data change needed. Say in the docs that the Paschal white follows the Carpatho-Russian custom, and Russian use is red after Matins.

### 8. Minor color points (same source)
- **Great Thursday:** the repo has `RED`; the source has "dark red" (the repo's PURPLE = #88023c). Consider PURPLE.
- **Exaltation (`PURPLE`):** matches "purple or dark red" for the Cross. The source notes that red, or green in some places, is also worn on 14 Sept.
- **Ascension `WHITE`:** "In some places in Russia, white is worn from Ascension to Pentecost, but in other places, gold". In Carpatho-Russian use, gold is worn from the eve of Ascension to the eve of Pentecost. This is acceptable as a local custom.

### 9. St Catherine's date: OCA has 24 November, the repo has 25
- **File/row:** data/Orthodox/feasts.csv `11-25,Catherine of Alexandria`.
- **Source:** the OCA lists "Great Martyr Katherine of Alexandria" on 24 November. https://www.oca.org/saints/lives/2026/11/24
- **Note:** 25 November is the Greek (GOARCH/Sinai) date. I did not fetch a GOARCH page to confirm this.
- **Suggested fix:** keep 11-25 as the Greek date and note the Slavic 24 November. Or use 11-24 to match the OCA (Slavic usage, which the color scheme also follows).

### 10. No Sunday after the Nativity when the Nativity falls on a Sunday
- **File/row:** data/Orthodox/days.csv `after_nativity` (`sun>12-25`, `date le 12-31`). In years when 25 Dec is a Sunday, this gives nothing.
- **Source:** in that case the OCA reads the Sunday-after-Nativity lessons (Gal 1:11-19, Matt 2:13-23) on Monday 26 December, under the Synaxis of the Theotokos. https://www.oca.org/readings/daily/2022/12/26
- **Suggested fix:** optional. The OCA page does not use the title on 26 December, so no label is required.
- **Related check:** `before_theophany` with `date ge 01-01` agrees with the OCA. When 30 or 31 December is a Sunday, the OCA calls it only "Sunday after Nativity" (https://www.oca.org/readings/daily/2023/12/31, https://www.oca.org/readings/daily/2018/12/30), and 1 January 2023 is "Sunday before Theophany" (https://www.oca.org/readings/daily/2023/01/01).

### Items checked that agree with the source
Every one below matches https://mci.archpitt.org/LiturgicalCalendar.html (2026, Gregorian Pascha 5 Apr):
- 1 Sept start of year
- Sunday before/after the Exaltation (`sun<09-14`, `sun>09-14`)
- Fathers of the Seventh Council `sun>=10-11` (11 Oct)
- Forefathers `sun>=12-11` (13 Dec)
- Sunday before the Nativity `sun>=12-18` (20 Dec)
- Sunday after the Nativity (27 Dec)
- Sunday before Theophany (4 Jan) and after Theophany (11 Jan)
- Zacchaeus `easter-77` (18 Jan)
- Prodigal Son `easter-63` (1 Feb)
- Thomas `easter+7`
- All Saints `easter+56`
- Apostles' Fast from `easter+57` to 06-28
- Nativity Fast 11-15 to 12-24
- Leave-taking of Pentecost on Saturday `easter+55`
- Ruthenian Gregorian Pascha

UGCC Holy Eucharist on Thursday after All Saints (`easter+60`) matches 19 June 2025 (https://stnicholasucp.ca/event/feast-day-of-the-holy-eucharist/). UGCC St Josaphat on 12 November matches https://nweparchy.ca/2025/11/vernon-parish-celebrates-annual-praznyk/.

The official UGCC site confirms the Holy Eucharist feast. On Thursday 11 June 2026 (Julian Pascha 12 April + 60) the Head of the UGCC preached "у свято Торжественного поклоніння пречистим Тайнам Тіла і Крові Господа нашого Ісуса Христа": https://ugcc.ua/data/taynstvo-evharystiy-tse-dzherelo-stiykosti-ukraynskogo-narodu-glava-ugkts-8879/

It also confirms St Josaphat on 12 November under the new calendar: on 12 November 2023 he addressed pilgrims "on the day of his memory": https://ugcc.ua/en/data/the-life-of-josaphat-gives-us-hope-the-jubilee-year-of-st-josaphat-concluded-with-a-solemn-liturgy-in-the-vatican-738/

OCA spot checks match the repo's dates and names:
- 1 Sept: Church New Year and Simeon Stylites
- 4 Dec: Barbara and John of Damascus
- 11 June: Bartholomew and Barnabas
- 31 Aug: Placing of the Cincture

### Still not checked
- The other fixed feasts, one by one against the OCA/GOARCH (they are standard Menaion dates).
- A GOARCH page for 25 November.
- An official UGCC printed calendar (the ugcc.ua 2025 calendar link was not reachable from the worship index).

## Anglican, Roman and Maronite

Sources used:
- CinW = Church in Wales, *Lectionary Year A, Advent 2025 - Kingdom 2026*, "Liturgical Colours" note (scheme agreed by the Bench of Bishops, June 2011): https://churchinwales.contentfiles.net/media/documents/2455_-_Lectionary_Year_A_WD_2a_-_Advent_2025_-_Kingdom_2026_-_English.pdf
- TEC = Episcopal Church dictionary, "Liturgical Colors": https://www.episcopalchurch.org/?p=170554
- WP = Wikipedia, "Liturgical colours" (last resort): https://en.wikipedia.org/wiki/Liturgical_colours

The maintainer prefers the first color when a source gives two options.

### Church in Wales 1984 (`wales-1984`): season colors

The repo gives Wales the historic prayer-book scheme. The Church in Wales' own scheme differs:

1. **data/Anglican/periods.csv, wales-1984 `season,,01-14,easter-64,EPIPHANY`** (green from 14 Jan). CinW: "Christmas Day to Candlemas (2nd February) in WHITE". **Fix:** white (the CW-style `EPIPHANY_SEASON`) from 01-06 to `min(02-02, easter-47)`.
2. **wales-1984 `Pre-Lent,easter-63,easter-47,PRE_LENT`** (purple). CinW: "3rd February to Shrove Tuesday in GREEN". **Fix:** green (ORDINARY) from 02-03 to Shrove Tuesday.
3. **wales-1984 `Whitsuntide,easter+49,easter+55,PENTECOST`** (red all week). CinW: "Pentecost Sunday in RED and the Monday after Pentecost to eve of Advent Sunday in GREEN ... Trinity Sunday in WHITE". **Fix:** red on Pentecost Sunday only, then green.
4. **data/Anglican/days.csv `good_friday,wales-1984` = BLACK.** CinW: "Palm Sunday and Holy Week in PASSION RED or PURPLE"; the Good Friday notes say only "Black can be used today". **Fix:** RED, which is the first option (Passion red is "a dark mulberry red"). Black is allowed, so keeping it is defensible, but red follows the first-option rule.
5. **`easter_even,wales-1984` = PURPLE.** CinW: Holy Week is Passion red or purple; the Easter Eve note says "Purple can be used until Easter Day". This is consistent; no change needed.
6. Optional: CinW lists "RED as option for Kingdom Season". The first option is green, so no change.

### Church in Wales 1984: feasts (data/Anglican/feasts.csv)

7. **06-30 "The Martyrdom of Paul", wales-1984 = WHITE.** By CinW's rule, apostles are red, and lesser festivals are "RED (for Martyrs)". **Fix:** RED.
8. **01-25 "The Conversion of Paul", wales-1984 (and every other book) = WHITE.** CinW: "Apostles and Evangelists (except John the Evangelist), Holy Cross Day, Holy Innocents in RED", and the 25 January entry is headed "THE CONVERSION OF PAUL, APOSTLE". Read literally, Wales makes it red. Many English kalendars use white for it (it is not a martyrdom), so treat this as a question for the maintainer. **Suggested:** RED for wales-1984 only.
9. **01-25 Conversion of St Paul, bcp-1962 = RED, but WHITE in all 16 other books.** This is an internal inconsistency. **Fix:** make it WHITE to match the others (or RED everywhere, if item 8 is accepted generally).
10. **The rule text itself.** The feasts.csv header and the provenance row say "red for apostles, evangelists and martyrs, white otherwise". The data, rightly, also make Holy Cross Day red and St John (apostle and evangelist) white. CinW confirms both exceptions. **Fix:** update the comment and provenance detail to say so.

### Common Worship (`common-worship`)

11. **days.csv `good_friday,common-worship` = NONE.** WP says the Church of England lectionary's colors match post-1969 Roman usage (red on Good Friday), with "no liturgical colour at all ... for Holy Saturday" ("hangings removed"). This supports NONE for **Easter Eve**, but suggests **red** for Good Friday. Still unverified after a second attempt:
    - churchofengland.org pages load their body text client-side, so only the menus could be read.
    - No diocese reproducing the Lectionary's color table was found.
    - One parish chart, with no source named, has Good Friday "Everything stripped" (https://chalkevalleychurches.org/files/lectionary/vestment-changes-plus-paschal-candle-2024-25.pdf). That supports the repo's NONE, but it is not authoritative.

    **Suggested:** leave NONE for now, and check a printed CW Lectionary booklet. If it reads "red (or hangings removed)", use RED as the first option.

    **Resolved (October 2026):** the Rules page, saved by the maintainer: "Coloured hangings are traditionally removed for Good Friday and Easter Eve, but red is the colour for the liturgy on Good Friday." Good Friday is now `RED; hangings removed`; Easter Eve stays NONE.
12. **days.csv `next_before_lent,common-worship` = GREEN.** This is consistent with WP's statement that Ordinary Time starts the day after Candlemas. No change.

### Episcopal (`episcopal`)

13. **data/Episcopal/seasons.csv `ADVENT,BLUE`.** TEC: "PURPLE/VIOLET for Advent (or ROYAL BLUE) & Lent (or UNBLEACHED LINEN)". Purple is listed first and blue as the alternative. **Fix:** under the first-color rule, `ADVENT,PURPLE`. Blue is a permitted option, so keep it only if the blue Advent is a deliberate choice, and note that in the provenance row.
14. TEC says nothing about Maundy Thursday white or Good Friday/Holy Saturday with no color (NONE). These are not contradicted, just unsourced.

### Roman 1962 (`roman-1962`)

No contradictions found. Source: the 1960 General Rubrics in Murphy's English translation (Sydney, 1960), https://archive.ccwatershed.org/media/pdfs/20/11/19/23-29-59_0.pdf. The relevant rubrics:

- n. 128(a): violet in Advent to the Christmas vigil.
- n. 128(b): violet "from Septuagesima Sunday to the Easter Vigil". This covers Palm Sunday and Holy Week, which the repo leaves violet.
- n. 130(a): violet on the Rogation days.
- n. 131: rose on Gaudete and Laetare.
- n. 132(a): black on Good Friday.
- n. 132(b): black for Offices and Masses of the Dead, which covers All Souls.
- n. 119: white from Christmas to the end of Epiphany.
- n. 123: red from the Pentecost vigil to the following Saturday.

The repo's Holy Saturday VIOLET/WHITE matches n. 128(b) together with the white Vigil Mass (n. 119(b)).

### Roman (`roman`)

No contradictions. Source: GIRM 346, read in full at https://www.usccb.org/prayer-and-worship/the-mass/general-instruction-of-the-roman-missal/girm-chapter-6. It gives:

- white for Christmas and Easter Time;
- red for Palm Sunday, Good Friday, Pentecost, apostles, evangelists and martyrs;
- rose optional on Gaudete and Laetare;
- (h): "gold or silver" allowed in the US on more solemn occasions.

The pale-gold and deeper-gold shades are a display choice that no source states.

### Anglican Church of Canada (`bcp-1962`)

No guidance from the Canadian church on colors, or on the Conversion of St Paul, was found online. Item 9 (bcp-1962 makes the Conversion of St Paul red where all other books have white) therefore stands as an internal inconsistency with no Canadian source either way.

### Maronite (`maronite`)

15. No source found for any color cycle. The Our Lady of Lebanon cathedral page (https://olol.org.au/liturgical-life/the-maronite-liturgical-year) does not mention colors, so the row stays a guess. The structure checks out against it: the year starts on the first Sunday of November with the Consecration and Renewal, the three Commemoration Sundays precede Lent, and Lent starts with Cana Sunday then Ash Monday.
16. St Sharbel on the third Sunday of July is confirmed by Catholic World Report (https://www.catholicworldreport.com/2024/07/24/the-enduring-faith-of-st-charbel-thousands-celebrate-in-lebanon/). St Maron on 9 Feb is confirmed by the Brooklyn eparchy parish bulletin of 8 Feb 2026 ("Monday, February 9, 2026, Feast of Saint Maron, is a Holy Day of Obligation"; https://www.ololdc.org/wp-content/uploads/2026/02/Bulletin_February_8_2026.pdf). That bulletin also shows the Faithful Departed Sunday on 8 Feb 2026. That is easter-56 for Easter on 5 April 2026, which matches the repo.

### Brazilian/Portuguese books

17. No IEAB or Igreja Lusitana guidance on colors was found, so there is nothing to compare against. The row stays uncited.

## Lutheran (LCMS, LCC, TLH, ELHB, ELCA, WELS, LCA, Poland and others)

The rule followed here: where a source gives two colors, the first one is preferred.

### LSB (data/LCMS/LSB, data/LCC)

1. **LCMS/LSB/days.csv and LCC/days.csv, `maundy_thursday`**
   - Repo: `WHITE`.
   - Source: the LCMS calendar says "Scarlet. Violet may be used where scarlet vestments are not present, and white may be used in some places." (https://calendar.lcms.org/events/category/church-year/2026-04/?ical=1). The Palm Sunday entry says "Scarlet will adorn the altar on Palm Sunday through Maundy Thursday" (…/2026-03/?ical=1).
   - Counter-source: the Altar Guild Manual (LSB ed.), via the CPH blog, says "With the celebration of Holy Communion on Maundy Thursday, the preferred color is white" (https://blog.cph.org/worship/preparing-the-church-sanctuary-for-lent-and-holy-week).
   - Fix: `SCARLET`, or SCARLET with `color_bottom` WHITE. The maintainer should choose.
2. **LCMS/LSB/days.csv and LCC/days.csv, `ash_wednesday`: no change.**
   - Repo: `BLACK`, as Lutheran Service Book lists it (black first, violet the alternative).
   - The LCMS's online calendar (calendar.lcms.org) words it the other way round ("violet or with black"), but the hymnal governs this calendar.
3. **`last_sunday`**
   - Repo: green.
   - Source: the 1994 LCMS essay suggests gold (https://www.lcms.org/worship/church-year/colors-of-liturgical-seasons). This is weak evidence for LSB.
   - Fix: none for now.

### TLH / ELHB (data/LCMS/TLH, data/LCMS/ELHB): matches the Common Service Book

Source: CSB General Rubrics, "Paraments", https://acollectionofprayers.com/wp-content/uploads/2017/01/nn_general-rubrics-common-service-book-of-the-lutheran-church.pdf. There are no hard conflicts. Two gray areas:

- **TLH/feasts.csv `12-28 The Holy Innocents`** (no color): CSB has white "through the Epiphany Season (except the Day of St. Stephen, Martyr, on which Day the Color is Red)", but also red "On Martyrs' Days". The repo follows the first rule. Fine as is, or set RED in the lower half.
- **TLH/feasts.csv and ELHB/feasts.csv `01-25 Conversion of St. Paul`** (no color): this is the same conflict, between the white Epiphany season and red on "the Apostles' Days". Fine as is, or set the lower half RED.

### ELCA (data/ELCA)

Source: ELCA yearly reading lists, https://cdn.elca.org/cdn/wp-content/uploads/yeara_25_26_all.pdf and https://cdn.elca.org/cdn/wp-content/uploads/YearC_24-25ALL.pdf.

4. **ELCA/days.csv `ash_wednesday`**
   - Repo: `BLACK`.
   - Source: "Ash Wednesday … Color: Purple" (both lists).
   - Fix: `PURPLE`.
5. **ELCA/seasons.csv `HOLY_WEEK,SCARLET`**, which colors Monday to Wednesday of Holy Week.
   - Source: "Monday in Holy Week … Color: Purple/Scarlet" (both lists). The Sunday of the Passion is "Scarlet/Purple" (it already has its own SCARLET row) and Maundy Thursday is "Scarlet/White" (this matches).
   - Fix: `HOLY_WEEK,PURPLE`, keeping `palm_sunday` SCARLET.
6. **ELCA/days.csv `holy_saturday`**
   - Repo: `NONE`.
   - Source: the lists date the Easter Vigil to Holy Saturday, "Color: White/Gold".
   - Fix: `NONE` with `color_bottom` WHITE, as LCMS does with BLACK/WHITE. This is optional.
7. **ELCA/feasts.csv, all lesser festivals with `RED`** (apostles, evangelists, martyrs, Holy Cross, Reformation).
   - Source: "Color: Scarlet/Red" (e.g. Andrew, Stephen, Thomas, Holy Cross).
   - Fix: under the first-color rule, `SCARLET`. Keeping RED is also reasonable, since the lists offer both. The lists give Pentecost plain "Red".
8. **ELCA/feasts.csv: Emanuel Nine missing**
   - Source: "designating June 17 as a commemoration of the martyrdom of the Emanuel 9", adopted by the 2019 Churchwide Assembly on Aug 8, 2019 (https://blogs.elca.org/worship/9578/).
   - Fix: add `,06-17,Emanuel Nine,"Emanuel Nine, martyrs, 2015",,,,,` as a commemoration. Use the full name the maintainer prefers. The ELCA calls it a "commemoration … and day of repentance".
9. **Checked, no discrepancy:** Thomas, Apostle on 07-03 and Matthias on 05-14 are correct for the ELCA. The lists print "Thu. July 3 — Thomas, Apostle" and "Matthias, Apostle (transferred)" on Fri May 15, 2026. The earlier suggestion of Dec 21 / Feb 24 was wrong and is withdrawn. Thanksgiving is "Green or White (the color of the season)", which matches the repo's lack of a color.

### WELS (data/RCLWorld, variant wels)

Source: WELS South Atlantic District, *Planning Christian Worship – Year C – Festival Half*, for CW 1993 (https://static1.squarespace.com/static/57c5699b29687fa2d85f8c8f/t/5a0bb0d271c10b723404b381/1510715605058/Planning_Christian_Worship_--_Year_C_--Festival_Half_--_Final.pdf). No source for CW 2021 colors was found.

10. **Advent**
    - Repo: PURPLE (shared RCLWorld/seasons.csv).
    - Source: "Color Blue or Purple".
    - Fix: give the WELS `advent` row in RCLWorld/days.csv `color` BLUE. The season file is shared, so it cannot be changed for WELS alone.
11. **`ash_wednesday,wels`**
    - Repo: `PURPLE`.
    - Source: "Color Black or Purple".
    - Fix: `BLACK`.
12. **`maundy_thursday,wels`**
    - Repo: `WHITE`.
    - Source: "Color Purple".
    - Fix: `PURPLE`, if the CW 1993 guide is accepted for CW 2021.

**Done (October 2026):** these colors are now used for Christian Worship (1993), the years before 2021–22 (`year lt 2021`), from the WELS PCWR tables the maintainer supplied. CW 2021 keeps its colors until a CW 2021 source is found.

### LCA (RCLWorld, variant lca): matches

Source: https://www.lca.org.au/worship/wpp/planning-ahead/. Violet Advent "(or blue)", violet Ash Wednesday and Palm Sunday, white Maundy Thursday, black Good Friday "(or bare altar)", green Last Sunday. Trinity is listed under gold "(or white)". The repo has no GOLD, so WHITE is fine. There is no conflict.

### Poland (LutheranWorld, variant poland): matches where checked

Sopot parish (https://sopot.luteranie.pl/2021/02/3791): "Dzień Pokuty i Modlitwy (tzw. Środa Popielcowa)", violet. wiadomosci.ox.pl, 3 Apr 2023: Maundy Thursday white, Good Friday black, Easter white. There is no conflict.

### No source found

ELCT, FLM, Slovakia (ECAV), Latvia (LELB), and the Ukrainian Lutheran Good Friday. Their statuses are unchanged.

## Nordic, Iceland, Estonia, Methodist and Reformed

Sources read October 2026. Where a source gives two colors, the suggested fix uses the first.

### Finland (data/Nordic/days.csv, variant finland)

1. **`maundy_thursday,finland`**: the repo has `WHITE`. The source gives "Liturginen väri: violetti tai sininen" (https://kirkkovuosikalenteri.fi/kirkkovuosipaiva/kiirastorstai/). **Fix:** set the color to `PURPLE`, or leave it blank so the HOLY_WEEK season color (purple) applies.
2. **`all_saints,finland`** (Pyhäinpäivä): the repo has `WHITE`. The source gives "Liturginen väri: punainen, tai varsinkin iltajumalanpalveluksessa, valkoinen" (https://kirkkovuosikalenteri.fi/kirkkovuosipaiva/pyhainpaiva/). **Fix:** `RED`.
3. **docs/traditions.md, Nordic section** says "white feasts". This is still true in general, but Finland's All Saints is red. **Fix:** add "Finland's All Saints red, Maundy Thursday violet" once the data are changed.

### Sweden (data/Nordic/days.csv and seasons.csv, variant sweden)

No national Kyrkohandbok color table was found online, so these are weaker. The sources are parish pages and an unofficial list.

4. **`judgment,sweden`** (Domssöndagen): the repo has no color, so it shows green. Ystad: "Ofta används lila på Domssöndagen" (https://www.svenskakyrkan.se/ystad/lar-dig-mer-om-kyrkoarets-fem-farger). S:t Stefanus koinonia: "Blå" (https://www.stefanuskoinonia.org/wp-content/uploads/2011/11/Kyrko%C3%A5rslista.pdf). A non-church blog (korsudden) has green. **Fix:** possibly `PURPLE`. Sources disagree, so this needs an authoritative check before changing.
5. **`after_all_saints,sweden`**: the repo has `PURPLE`. Ystad says black "kan ... användas"; Stefanus koinonia gives "Alla själars dag: Blå" (violet, so it agrees with the repo); korsudden gives white. **Fix:** none for now. Note that sources vary.
6. **`trinity,sweden`**: the repo has `WHITE`. Stefanus koinonia gives "Heliga trefaldighets dag: Röd"; korsudden gives white. **Fix:** none (unofficial sources only). Flag it for a check against Kyrkohandboken.
7. **`mid_lent,sweden`** (Midfastosöndagen): the repo has no color, so it shows purple. Stefanus koinonia gives "Rosa". This is an unofficial list and the Nordic palette has no ROSE. **Fix:** none. Optional.
8. **`before_judgment,sweden`**: the repo has no color, so it shows green. Stefanus koinonia gives "Blå". **Fix:** none (single unofficial source).

### Denmark (data/Nordic/periods.csv, variant denmark)

9. **`season,Fasten,easter-63,...`**: the repo gives Septuagesima, Sexagesima and Fastelavn purple (LENT). lex.dk: "violet til advent og faste", "grøn til helligtrekongers- og trinitatistiden" (https://lex.dk/liturgiske_farver). No source names the pre-Lent Sundays, and the church prescribes nothing ("I folkekirken er der intet foreskrevet herom"). **Fix:** none required. Note in provenance that Denmark's colors are custom, not rule.

### Norway (data/Nordic, variant norway)

No color discrepancies. The 2010 rule (https://www.kirken.no/globalassets/kirken.no/migrering/km2010_10_liturgfarger_vedtak.pdf) matches every repo color. Good Friday is "fiolett - eller svart", so violet is right.

- Out of scope but noticed: the same rule places "Bots- og bededag" on the "20. søndag i treenighetstiden", while the repo (`repentance,norway`, `sun#1:11-7`) uses the Sunday before All Saints. The 2010 rule predates the 2011 lectionary, so this may be outdated. Check before changing.
- `whitsun_eve,norway` is `RED`. The rule names only "Pinse (Pinsedag – Andre pinsedag): rødt" and runs Easter season to "Søndag før pinse", so it does not cover Pentecost Eve. No change suggested.

### Iceland (data/LutheranWorld, variant iceland)

10. **docs/provenance.csv**, row `lutheran-iceland,colors,inferred,Good Friday violet`: the source lists violet first ("Litur: Fjólublár eða svartur", https://kirkjan.is/kirkjuarid/wx384ilhknix30dt7kslh8xc). **Fix:** status `sourced`. The repo value is correct.

### Estonia (data/LutheranWorld, variant estonia)

11. **docs/provenance.csv**, row `lutheran-estonia,colors,inferred,Good Friday black`, note "Church gives red or black". The sources say black only. Jõhvi: "Suure Reede liturgiline värv on must" (https://johvi.eelk.ee/kogudus/kirikuaasta/). Eesti Kirik: textiles black on Good Friday and Holy Saturday (https://eestikirik.ee/suur-nadal-kirikutekstiilides). Red appears only for Holy Saturday ("must või punane"). **Fix:** status `sourced` and correct the note.
12. **`maundy_thursday,estonia`**: the repo has `WHITE`. Jõhvi gives violet, "erandlikult" white. Eesti Kirik gives violet, with white allowed. **Fix:** `PURPLE`.
13. **`holy_saturday,estonia`**: the repo has no color, so it shows purple. Jõhvi: "must või punane". Eesti Kirik: black. **Fix:** `BLACK`.
14. **`advent,estonia`**: the repo has `WHITE|PURPLE|PURPLE|PURPLE`. Jõhvi says Advent textiles are "violett", with no white for the 1st Sunday. The repo's white comes from the church's sermon helps (provenance row 190), which I could not reopen; the e-kirik.eelk.ee post for 30 November 2025 shows no color. **Fix:** none until the sermon-helps source is rechecked. Flag the conflict.
15. **feasts.csv `11-01 Pühakutepäev` (estonia)**: no color in the repo. Jõhvi: "pühakutepäeval punane või valge". **Fix:** `color_override_bottom` `RED` (optional).
16. **feasts.csv `11-02 Hingedepäev`** and **days.csv `all_souls_sun,estonia`**: no color in the repo. Jõhvi: "hingedepäeval valge või must". **Fix:** `WHITE` (optional).

### United Methodist (data/Methodist)

Source: https://www.umcdiscipleship.org/book-of-worship/the-calendar

17. **feasts.csv `thanksgiving,thu#4:11`**: no color in the repo. The source has "Thanksgiving (red or white)". **Fix:** `color_override_bottom` `RED`.
18. **days.csv `christmas_eve`**: the repo has a blank top (the Advent season's purple) and a `WHITE` bottom. The source lists "Nativity of the Lord (Christmas Eve, Christmas Day)" under "CHRISTMAS SEASON (white or gold)". **Fix:** set `color` to `WHITE`, or leave it as it is if the split cell is intentional for an evening observance.
19. **docs/provenance.csv**, row `methodist,colors,inferred,...` ("No source named for the colors"). **Fix:** status `sourced`, citing the page above. It confirms purple Advent and Lent, red as the Holy Week alternative, and "Good Friday+ (no color)" and "Holy Saturday+ (no color)".

### Methodist Church in Britain (data/RCLWorld, variant methodist-gb)

Source: Year A lectionary 2025-26, https://media.methodist.org.uk/media/documents/LECTIONARY_YR_A_2025-26_28EyMMU.pdf

20. **days.csv `lent,methodist-gb` / `palm_sunday,methodist-gb`**: the repo has "{ordinal} Sunday in Lent" and "Palm Sunday". The source has "5th Sunday in Lent ... 1st Sunday of the Passion" and "6th Sunday in Lent ... 2nd Sunday of the Passion / Palm Sunday". **Fix:** add the full names, e.g. a `full_name` of "Fifth Sunday in Lent (First Sunday of the Passion)" and "Palm Sunday (Second Sunday of the Passion)".
21. **feasts.csv `aldersgate,sun<05-24`**: the repo uses the Sunday strictly before 24 May. methodist.org.uk says "Traditionally held on the Sunday preceding Wesley Day, 24 May", but also says that in 2026 Wesley Day and Aldersgate Sunday fall on the same day (https://www.methodist.org.uk/for-churches/resources/seasons-and-themes/special-sundays/aldersgate-sunday/). The lectionary instead puts "Conversion of John and Charles Wesley" on the 7th Sunday of Easter, 17 May 2026. **Fix:** none needed under the "preceding" wording. If the maintainer follows the 2026 note, use `sun<=05-24`. The sources conflict.
22. **Mothering Sunday is missing**: the source says "4th Sunday in Lent ... or for MOTHERING SUNDAY", and the special-Sundays page says "Celebrated on the 4th Sunday in Lent" (https://www.methodist.org.uk/for-churches/resources/seasons-and-themes/special-sundays/). The repo has no methodist-gb entry. **Fix:** optionally add it. The same page also gives Remembrance Sunday as the 2nd Sunday in November.
23. **feasts.csv `,12-31,Watchnight`**: the lectionary gives Watchnight readings but no date. 31 December comes from memory (unverified). **Fix:** none. Mark it inferred.
24. **feasts.csv Wesley Day / Aldersgate Sunday `RED` bottoms**, and all methodist-gb colors: no source found. **Fix:** none. Keep status uncited or guess.

### Reformed (data/Reformed/feasts.csv)

25. **feasts.csv** has "All Saints Day only". The RCA key-dates list agrees: All Saints Day is the only day in it that is not a day of the Lord (https://www.rca.org/wp-content/uploads/2024/09/Liturgical-Calendar-2025-FINAL.pdf). But the RCA's observances list includes "Reformation Sunday, the Sunday before October 31" and "Reformation Day, October 31" (https://www.rca.org/liturgical-calendar/). **Fix:** optionally add Reformation Sunday (`sun<10-31`) or Reformation Day. Otherwise mark the row `partial` and note that the RCA lists Reformation as an observance. The CRC overlay (crc_canada.csv) already uses `sun<=10-31` for Reformation Sunday, which differs from the RCA's "Sunday before October 31". Check which rule is intended.
26. **days.csv** (Reformed): the RCA key dates list neither Christmas Eve nor Holy Saturday. They also do not show colors in extracted text, so the red Palm/Passion Sunday and the "no color" from Maundy Thursday onward could not be rechecked here.

