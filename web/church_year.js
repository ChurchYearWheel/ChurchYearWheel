/*
 * The church year wheel, drawn in the browser.
 *
 * This is a port of church_year_image.py and new_year.py, and it has to agree with
 * them exactly: `web/verify.py` renders a long run of years both ways and
 * compares the markup, so any drift here shows up as a failing year rather
 * than as a quietly wrong calendar.  Where a line looks unidiomatic for
 * JavaScript it is usually because it is matching Python's arithmetic or
 * number formatting on purpose.
 *
 * Everything that does not depend on the year — the font metrics, the parsed
 * settings, the colors, styles, rings and commemorations, the artwork for the
 * middle — arrives as the JSON that web/export_data.py freezes.
 */
(function (root) {
'use strict';

// ---------------------------------------------------------------------------
// Dates
// ---------------------------------------------------------------------------
// Days since 1970-01-01, computed rather than taken from Date, so that nothing
// here can be shifted by the reader's time zone.

const MONTH_LENGTHS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

/**
 * A reckoning: how a day on the line is named, and how a name finds its day.
 *
 * The days themselves are one unbroken count from 1 January 1970, so a
 * reckoning only changes the labels.  Weekdays never shift, which is why Advent
 * Sunday stays a Sunday whichever calendar is chosen.
 */
function Reckoning(name, label, isLeap, toDay, fromDay) {
  this.name = name; this.label = label;
  this.isLeap = isLeap; this.toDay = toDay; this.fromDay = fromDay;
}

Reckoning.prototype.daysInMonth = function (y, m) {
  return (m === 2 && this.isLeap(y)) ? 29 : MONTH_LENGTHS[m - 1];
};

Reckoning.prototype.valid = function (y, m, d) {
  return m >= 1 && m <= 12 && d >= 1 && d <= this.daysInMonth(y, m);
};

Reckoning.prototype.monthDay = function (y, dayOfYear) {
  for (let m = 1; m <= 12; m++) {
    const length = this.daysInMonth(y, m);
    if (dayOfYear < length) return [m, dayOfYear + 1];
    dayOfYear -= length;
  }
  throw new Error('day of year out of range');
};

/** Estimate the year from the day, then walk to it.  Two steps at the most. */
Reckoning.prototype.searchFromDay = function (z, daysPerYear) {
  let y = 1970 + Math.floor((z - this.toDay(1970, 1, 1)) / daysPerYear);
  while (this.toDay(y, 1, 1) > z) y -= 1;
  while (this.toDay(y + 1, 1, 1) <= z) y += 1;
  const md = this.monthDay(y, z - this.toDay(y, 1, 1));
  return { y: y, m: md[0], d: md[1] };
};

// -- Gregorian: the civil calendar since 1582 -------------------------------
// Howard Hinnant's closed form, with floor division throughout.

const GREGORIAN = new Reckoning('gregorian', 'Gregorian',
  y => y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0),
  function (y, m, d) {
    y -= m <= 2 ? 1 : 0;
    const era = Math.floor(y / 400);
    const yoe = y - era * 400;                                 // [0, 399]
    const doy = Math.floor((153 * (m + (m > 2 ? -3 : 9)) + 2) / 5) + d - 1;
    const doe = yoe * 365 + Math.floor(yoe / 4) - Math.floor(yoe / 100) + doy;
    return era * 146097 + doe - 719468;
  },
  function (z) {
    z += 719468;
    const era = Math.floor(z / 146097);
    const doe = z - era * 146097;                              // [0, 146096]
    const yoe = Math.floor((doe - Math.floor(doe / 1460) + Math.floor(doe / 36524)
                            - Math.floor(doe / 146096)) / 365);
    const y = yoe + era * 400;
    const doy = doe - (365 * yoe + Math.floor(yoe / 4) - Math.floor(yoe / 100));
    const mp = Math.floor((5 * doy + 2) / 153);
    const d = doy - Math.floor((153 * mp + 2) / 5) + 1;
    const m = mp + (mp < 10 ? 3 : -9);
    return { y: y + (m <= 2 ? 1 : 0), m: m, d: d };
  });

// -- Julian: Christendom's calendar until 1582 ------------------------------
// A leap year every fourth without exception, now thirteen days adrift.
// Anchored on the changeover: Julian 5 October and Gregorian 15 October 1582
// name the same day.

const JULIAN_OFFSET = -719470;

const JULIAN = new Reckoning('julian', 'Julian',
  y => ((y % 4) + 4) % 4 === 0,
  function (y, m, d) {
    y -= m <= 2 ? 1 : 0;
    const doy = Math.floor((153 * (m + (m > 2 ? -3 : 9)) + 2) / 5) + d - 1;
    return 365 * y + Math.floor(y / 4) + doy + JULIAN_OFFSET;
  },
  function (z) { return JULIAN.searchFromDay(z, 365.25); });

// -- Revised Julian: the Orthodox reform of 1923 ----------------------------
// A century is a leap year only when it leaves 200 or 600 on division by 900.
// Agrees with the Gregorian calendar from March 1600 until February 2800.

function revisedLeapsBefore(y) {
  // As in the Gregorian form, y // 4 - y // 100 already counts the leap days
  // that fall inside the March-shifted years below y, not the leap years below
  // it -- easy to mistake for an off-by-one and "fix" the wrong way.
  let count = Math.floor(y / 4) - Math.floor(y / 100);
  for (const keep of [200, 600]) {
    if (y >= keep) count += Math.floor((y - keep) / 900) + 1;
  }
  return count;
}

let REVISED_JULIAN_OFFSET = 0;    // measured once below, against the Gregorian

const REVISED_JULIAN = new Reckoning('revised-julian', 'Revised Julian',
  function (y) {
    if (((y % 4) + 4) % 4 !== 0) return false;
    if (((y % 100) + 100) % 100 !== 0) return true;
    const r = ((y % 900) + 900) % 900;
    return r === 200 || r === 600;
  },
  function (y, m, d) {
    y -= m <= 2 ? 1 : 0;
    const doy = Math.floor((153 * (m + (m > 2 ? -3 : 9)) + 2) / 5) + d - 1;
    return 365 * y + revisedLeapsBefore(y) + doy + REVISED_JULIAN_OFFSET;
  },
  function (z) { return REVISED_JULIAN.searchFromDay(z, 365.2422); });

// Anchored so the two land together through the years the reform was built to
// agree with.  Measured by asking the calendar itself where 1 January 2000
// falls while the offset is still zero, rather than by repeating the formula
// here: a copy of it would go quietly stale the first time the original
// changed.
REVISED_JULIAN_OFFSET = GREGORIAN.toDay(2000, 1, 1)
                      - REVISED_JULIAN.toDay(2000, 1, 1);

const RECKONINGS = {};
for (const r of [GREGORIAN, JULIAN, REVISED_JULIAN]) RECKONINGS[r.name] = r;

// The calendar in force for whatever is being drawn; set by Calendar.
let reckoning = GREGORIAN;

const daysFromCivil = (y, m, d) => reckoning.toDay(y, m, d);
const civilFromDays = z => reckoning.fromDay(z);

const pad2 = n => String(n).padStart(2, '0');

/**
 * An ISO date.  Years 1 to 9999 are the ordinary four-digit form, character for
 * character what Python's date.isoformat() gives.  Anything outside that takes
 * ISO 8601's expanded form -- a sign and six digits, "-000500-04-15" -- which
 * keeps the string parseable and unambiguous where the short form would not be.
 */
function iso(z) {
  const c = civilFromDays(z);
  const year = (c.y >= 1 && c.y <= 9999)
    ? String(c.y).padStart(4, '0')
    : (c.y < 0 ? '-' : '+') + String(Math.abs(c.y)).padStart(6, '0');
  return year + '-' + pad2(c.m) + '-' + pad2(c.d);
}

function fromIso(s) {
  const m = /^([+-]?)(\d{4,})-(\d{2})-(\d{2})$/.exec(String(s).trim());
  if (!m) throw new Error('not a date: ' + s);
  return daysFromCivil((m[1] === '-' ? -1 : 1) * +m[2], +m[3], +m[4]);
}

/** A year as people write it: 2026, or 501 BC.  Year 0 is 1 BC. */
function yearName(y) { return y >= 1 ? String(y) : (1 - y) + ' BC'; }

/** The two years a church year spans, with the era said once where it can be. */
function spanName(a, b) {
  if (a < 1 && b < 1) return (1 - a) + '–' + (1 - b) + ' BC';
  return yearName(a) + '–' + yearName(b);
}
// Python's date.weekday(): Monday 0 ... Sunday 6.  1970-01-01 was a Thursday.
const weekday = z => ((z + 3) % 7 + 7) % 7;
const yearOf = z => civilFromDays(z).y;
const monthOf = z => civilFromDays(z).m;
const dayOf = z => civilFromDays(z).d;

// Python's // and % floor toward minus infinity and never return a negative
// remainder; JavaScript's / truncates and its % keeps the sign of the dividend.
// The two agree for positive years and part company before year 1, so the
// computus below is written in Python's terms throughout.
const fdiv = (a, b) => Math.floor(a / b);
const fmod = (a, b) => ((a % b) + b) % b;

/**
 * Easter by the Julian computus, which the Orthodox churches keep.
 *
 * The rule names a date in the Julian calendar, but the day it lands on is the
 * same day whatever calendar the wheel is drawn in.  It runs later than the
 * Gregorian rule in most years and coincides with it in a few.
 */
function julianEaster(year) {
  const a = fmod(year, 4), b = fmod(year, 7), c = fmod(year, 19);
  const d = fmod(19 * c + 15, 30);
  const e = fmod(2 * a + 4 * b - d + 34, 7);
  const t = d + e + 114;
  return JULIAN.toDay(year, fdiv(t, 31), fmod(t, 31) + 1);
}

/**
 * Gregorian Easter (the anonymous / Meeus-Jones-Butcher algorithm).
 *
 * Run on a year before 1583 this is an extrapolation, not a record: it is the
 * modern rule applied to a calendar that was not yet in use.  It still yields
 * a Sunday in March or April for any year at all, which is what lets the wheel
 * be drawn for one.
 */
function gregorianEaster(year) {
  const a = fmod(year, 19);
  const b = fdiv(year, 100), c = fmod(year, 100);
  const d = fdiv(b, 4), e = fmod(b, 4);
  const f = fdiv(b + 8, 25);
  const g = fdiv(b - f + 1, 3);
  const h = fmod(19 * a + b - d - g + 15, 30);
  const i = fdiv(c, 4), k = fmod(c, 4);
  const el = fmod(32 + 2 * e + 2 * i - h - k, 7);
  const m = fdiv(a + 11 * h + 22 * el, 451);
  const t = h + el - 7 * m + 114;
  return GREGORIAN.toDay(year, fdiv(t, 31), fmod(t, 31) + 1);
}

const PASCHALIONS = { gregorian: gregorianEaster, julian: julianEaster };

// calendars.py: the Alexandrian calendars.  Twelve months of thirty days and a
// thirteenth of five (six before a Julian leap year); Coptic and Ethiopian
// differ only in their era.  They name days for the rules, never the wheel.
const JDN_1970 = 2440588;
const ALEXANDRIAN_EPOCHS = { coptic: 1825030, ethiopian: 1724221 };
function alexandrianToDay(cal, y, m, d) {
  return ALEXANDRIAN_EPOCHS[cal] + 365 * (y - 1) + Math.floor(y / 4) + 30 * (m - 1) + d - 1 - JDN_1970;
}
function alexandrianYear(cal, z) {
  return Math.floor((4 * (z + JDN_1970 - ALEXANDRIAN_EPOCHS[cal]) + 1463) / 1461);
}
function alexandrianValid(y, m, d) {
  if (d < 1) return false;
  if (m >= 1 && m <= 12) return d <= 30;
  return m === 13 && d <= (fmod(y, 4) === 3 ? 6 : 5);
}
// traditions.py: OTHER_CALENDARS, the words that name a date in another calendar.
const OTHER_CALENDARS = ['gregorian', 'julian', 'coptic', 'ethiopian'];

/** Easter by whichever computus was asked for. */
function easter(year, paschalion) {
  return (PASCHALIONS[paschalion] || gregorianEaster)(year);
}

/** First Sunday in Advent: the fourth Sunday before Christmas. */
function adventSunday(year) {
  const christmas = daysFromCivil(year, 12, 25);
  return christmas - (weekday(christmas) + 1) - 21;
}


// ---------------------------------------------------------------------------
// Traditions: a year worked out from a tradition's rules
// ---------------------------------------------------------------------------
// A port of traditions.py, and it has to agree with it exactly: the Python
// side writes these rows out as the year's CSVs and church_year_image.py draws from
// them, while the browser draws straight from what is worked out here, and
// web/verify.py compares the two drawings.

const ORDINALS = ['', 'First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth',
  'Seventh', 'Eighth', 'Ninth', 'Tenth', 'Eleventh', 'Twelfth', 'Thirteenth',
  'Fourteenth', 'Fifteenth', 'Sixteenth', 'Seventeenth', 'Eighteenth',
  'Nineteenth', 'Twentieth', 'Twenty-first', 'Twenty-second', 'Twenty-third',
  'Twenty-fourth', 'Twenty-fifth', 'Twenty-sixth', 'Twenty-seventh',
  'Twenty-eighth', 'Twenty-ninth', 'Thirtieth', 'Thirty-first',
  'Thirty-second', 'Thirty-third', 'Thirty-fourth', 'Thirty-fifth',
  'Thirty-sixth', 'Thirty-seventh', 'Thirty-eighth', 'Thirty-ninth',
  'Fortieth'];

const WEEKDAYS = { mon: 0, tue: 1, wed: 2, thu: 3, fri: 4, sat: 5, sun: 6 };
const HALF_ENDS = { 'pentecost-eve': 'easter+48', 'pentecost-week': 'easter+55',
                    'trinity-week': 'easter+62' };
const DEFAULT_YEAR_START = 'sun<12-25-21';

const truthy = v => ['TRUE', '1', 'YES', 'Y', 'ON'].indexOf(String(v == null ? '' : v)
  .trim().toUpperCase()) >= 0;
const cell = (row, key) => (row && row[key] != null ? String(row[key]) : '');

/** A blank cell applies to every variant; otherwise a space-separated list. */
function variantMatches(value, variant) {
  const c = String(value || '').trim().toLowerCase();
  if (!c) return true;
  return c.replace(/,/g, ' ').split(/\s+/).filter(Boolean)
          .indexOf(String(variant || '').toLowerCase()) >= 0;
}

function findTradition(data, key) {
  const wanted = String(key || '').trim().toLowerCase();
  for (const t of data.traditions) if (t.key === wanted) return t;
  throw new Error('no tradition ' + key);
}

/** The tradition's own settings, for its variant, as written.  Later rows win. */
function traditionSettings(data, tradition) {
  const out = {};
  for (const row of data.folders[tradition.folder].settings) {
    const name = cell(row, 'setting');
    if (!name || !variantMatches(cell(row, 'variant'), tradition.variant)) continue;
    out[name] = cell(row, 'value');
  }
  return out;
}

const slug = text => String(text || '').toLowerCase().replace(/[^a-z0-9]+/g, '');

/**
 * Lay a subcalendar's rows over the tradition's own; see merge_rows in
 * traditions.py, which this follows step for step.
 */
function mergeRows(days, feasts, extra, source) {
  for (const row of extra) {
    const action = cell(row, 'action').toLowerCase();
    let target = null;
    const rid = cell(row, 'id');
    if (rid) {
      for (const table of [days, feasts]) {
        const hit = table.find(e => cell(e, 'id') === rid);
        if (hit) { target = [table, hit]; break; }
      }
    }
    if (target === null && !rid && cell(row, 'date') && cell(row, 'name')) {
      const hit = feasts.find(e => cell(e, 'date') === cell(row, 'date')
                                && slug(cell(e, 'name')) === slug(cell(row, 'name')));
      if (hit) target = [feasts, hit];
    }
    if (target !== null) {
      const table = target[0], existing = target[1];
      if (action === 'remove') { table.splice(table.indexOf(existing), 1); continue; }
      for (const k of Object.keys(row)) {
        const v = row[k];
        if (k === 'action' || v === '' || v == null) continue;
        existing[k] = v === '-' ? '' : v;
      }
      existing.source = source;
      continue;
    }
    if (action === 'remove') continue;
    const added = Object.assign({}, row, { source: source });
    if (cell(added, 'title') || cell(added, 'from')) days.push(added);
    else feasts.push(added);
  }
}

/**
 * A table of readings as export_data.py packs it (pack_rows): `cols`, every
 * distinct cell once in `strings`, and each row as the indexes of its cells.
 * Unpacked once, as rows with their blank cells left out.
 */
const unpackedRows = new WeakMap();
function readingRows(table) {
  if (!table) return [];
  let rows = unpackedRows.get(table);
  if (!rows) {
    rows = table.rows.map((cells, n) => {
      const row = {};
      cells.forEach((x, i) => { if (table.strings[x] !== '') row[table.cols[i]] = table.strings[x]; });
      PACKED_ROW.set(row, { table: table, index: n });
      return row;
    });
    unpackedRows.set(table, rows);
  }
  return rows;
}

/**
 * Where a row the drawing worked from was written, for the page's editor:
 * the copies a Source makes lead back to the rows of the page's tables, and
 * a row of readings to its packed table and its place there.
 */
const COPIED_FROM = new WeakMap();
const PACKED_ROW = new WeakMap();
function copyOf(row, from) {
  const out = Object.assign({}, row);
  COPIED_FROM.set(out, from || row);
  return out;
}
/** The row of the page's tables a drawn day or reading came from: { row, table?, index? }. */
function rowOrigin(row) {
  let r = row;
  for (let n = 0; r && COPIED_FROM.has(r) && n < 20; n++) r = COPIED_FROM.get(r);
  if (!r) return null;
  const packed = PACKED_ROW.get(r);
  return packed ? { row: r, table: packed.table, index: packed.index } : { row: r };
}
/** A drawn day's or reading's own row, unseen by anything that copies or prints it. */
function withRow(out, row) {
  Object.defineProperty(out, 'row', { value: row, enumerable: false });
  return out;
}

/** Rows packed as export_data.py packs them (pack_rows). */
function packRows(rows) {
  const cols = [];
  for (const row of rows) for (const k of Object.keys(row)) if (cols.indexOf(k) < 0) cols.push(k);
  const index = new Map();
  const packed = rows.map(row => {
    const cells = cols.map(c => (row[c] === undefined ? '' : row[c]));
    while (cells.length && cells[cells.length - 1] === '') cells.pop();
    return cells.map(v => { if (!index.has(v)) index.set(v, index.size); return index.get(v); });
  });
  return { cols: cols, strings: Array.from(index.keys()), rows: packed };
}

/**
 * The tables with only the readings of these kinds of set (READING_CATEGORIES)
 * that some church on the page has, whatever subcalendar it is drawn with
 * (church_year.py: prune_readings).  A folder's `omit` and `=kind` rows
 * stay; a shared lectionary left with nothing goes.
 */
function pruneReadings(data, kinds) {
  if (READING_CATEGORIES.every(c => kinds.indexOf(c) >= 0)) return data;
  const want = new Set(kinds);
  const keyOf = (file, r) => [file, cell(r, 'day').trim(), toInt(cell(r, 'offset'), 0) || 0, cell(r, 'title')].join('\n');
  const keep = new Set();
  for (const t of data.traditions) {
    const subs = (data.folders[t.folder].subcalendars || []).map(e => e.key);
    for (const chosen of [[]].concat(subs.map(k => [k]))) {
      const source = new Source(data, t, chosen);
      const info = readingInfo(source);
      for (const r of source.readings) if (want.has(info.category(r))) keep.add(keyOf(cell(r, '_file'), r));
    }
  }
  const out = Object.assign({}, data);
  out.sharedReadings = {};
  for (const name of Object.keys(data.sharedReadings || {})) {
    const rows = readingRows(data.sharedReadings[name]).filter(r => keep.has(keyOf(name, r)));
    if (rows.length) out.sharedReadings[name] = packRows(rows);
  }
  out.folders = {};
  for (const f of Object.keys(data.folders)) {
    const rows = readingRows(data.folders[f].readings)
      .filter(r => cell(r, 'kind') === 'omit' || cell(r, 'kind').charAt(0) === '=' || keep.has(keyOf('', r)));
    out.folders[f] = Object.assign({}, data.folders[f], { readings: packRows(rows) });
  }
  out.csv = keptLayouts(data, out);
  return out;
}

/**
 * The folder whose file `path` (under data/) is: the longest that holds it;
 * readings/NAME for a shared lectionary, blank for the palette
 * (church_year.py: file_owner).
 */
function fileOwner(data, path) {
  if (path.indexOf('readings/') === 0) return path;
  const owners = Object.keys(data.folders).filter(f => path.indexOf(f + '/') === 0);
  return owners.reduce((a, b) => (b.length > a.length ? b : a), '');
}

/**
 * The file layouts of the tables `out` still carries whole
 * (church_year.py: kept_layouts): a folder dropped takes its files, a
 * lectionary pruned or dropped takes its own.
 */
function keptLayouts(data, out) {
  const kept = {};
  for (const path of Object.keys(data.csv || {})) {
    const owner = fileOwner(data, path);
    if (owner.indexOf('readings/') === 0) {
      const name = owner.slice('readings/'.length, -'.csv'.length);
      const old = (data.sharedReadings || {})[name], now = (out.sharedReadings || {})[name];
      if (!now || now.rows.length !== old.rows.length) continue;
    } else if (owner) {
      if (!out.folders[owner]) continue;
      if (path === owner + '/readings.csv'
          && out.folders[owner].readings.rows.length !== data.folders[owner].readings.rows.length) continue;
    }
    kept[path] = data.csv[path];
  }
  return kept;
}

/** Everything a tradition's folder says, filtered to its variant. */
function Source(data, tradition, subcalendars) {
  const folder = data.folders[tradition.folder];
  const v = tradition.variant;
  const copy = r => copyOf(r);
  this.tradition = tradition;
  this.settings = traditionSettings(data, tradition);
  this.days = folder.days.filter(r => variantMatches(cell(r, 'variant'), v)).map(copy);
  this.periods = folder.periods.filter(r => variantMatches(cell(r, 'variant'), v)).map(copy);
  this.feasts = folder.feasts.filter(r => variantMatches(cell(r, 'variant'), v)).map(copy);
  this.subcalendarList = folder.subcalendars;
  // Every variant's days (the Readings boxes read their titles: readingInfo).
  this.folderDays = folder.days;
  // Its own readings.csv, then any shared lectionary its `readings` setting names.
  const sharedNames = String(this.settings.readings || '').split(/[\s,]+/).filter(Boolean);
  const shared = sharedNames.map(name => readingRows((data.sharedReadings || {})[name]));
  // A row of the folder's own whose kind is `omit` drops the shared rows it
  // names: those of its title (blank: the day's own propers), on its day and
  // offset (blank day: every day), of its cycle (blank: every year) and of
  // the kinds listed in its reading (blank: every kind).
  const own = readingRows(folder.readings).filter(r => variantMatches(cell(r, 'variant'), v));
  const omits = own.filter(r => cell(r, 'kind') === 'omit');
  const dropped = r => omits.some(o => {
    const day = cell(o, 'day').trim(), cyc = cell(o, 'cycle').trim();
    const kinds = cell(o, 'reading').split(/\s+/).filter(Boolean);
    return cell(o, 'title') === cell(r, 'title')
      && (!day || (day === cell(r, 'day').trim()
                   && (toInt(cell(o, 'offset'), 0) || 0) === (toInt(cell(r, 'offset'), 0) || 0)))
      && (!cyc || cyc === cell(r, 'cycle').trim())
      && (!kinds.length || kinds.indexOf(cell(r, 'kind')) >= 0);
  });
  // A row whose kind is `=` and a kind (`=psalm`) gives another reading for
  // the shared row of that kind with its day, offset, cycle and title, which
  // keeps its place; several such rows replace several such readings in turn.
  const keyOf = (r, kind) => [cell(r, 'day').trim(), toInt(cell(r, 'offset'), 0) || 0,
    cell(r, 'cycle').trim(), cell(r, 'title'), kind].join('|');
  const swaps = {};
  const swapRow = new WeakMap();      // a swapped row: the `=kind` row its reading is from
  for (const r of own) {
    const kind = cell(r, 'kind');
    if (kind.charAt(0) === '=') (swaps[keyOf(r, kind.slice(1))] = swaps[keyOf(r, kind.slice(1))] || []).push(r);
  }
  const swapped = r => {
    const list = swaps[keyOf(r, cell(r, 'kind'))];
    if (!list || !list.length) return r;
    const from = list.shift();
    const out = Object.assign({}, r, { reading: cell(from, 'reading') });
    swapRow.set(out, from);
    return out;
  };
  // `_file` names the shared lectionary a row came from (a daily one puts
  // its sets among the daily readings).
  this.readings = own.filter(r => cell(r, 'kind') !== 'omit' && cell(r, 'kind').charAt(0) !== '=').concat(
    ...shared.map((rows, i) => rows.filter(r => variantMatches(cell(r, 'variant'), v) && !dropped(r))
      .map(r => { const w = swapped(r); return Object.assign(copyOf(w, w === r ? r : swapRow.get(w)), { _file: sharedNames[i] }); })));
  // Hymnal topics matched to days (hymn_topics.csv), for the hymn marks by a day's name.
  this.hymnTopics = folder.hymnTopics.filter(r => variantMatches(cell(r, 'variant'), v));
  this.chosen = [];
  for (const key of subcalendars || []) if (key) this.applySubcalendar(key);
}

Source.prototype.applySubcalendar = function (key) {
  const entry = this.subcalendarList.find(s => s.key === key);
  if (!entry) return;
  if (this.chosen.indexOf(key) >= 0) return;
  for (const other of String(entry.include || '').split(/\s+/).filter(Boolean)) {
    this.applySubcalendar(other);
  }
  this.chosen.push(key);
  const rows = entry.rows.filter(r => variantMatches(cell(r, 'variant'), this.tradition.variant))
                         .map(r => copyOf(r));
  mergeRows(this.days, this.feasts, rows, key);
};

// -- the date language ------------------------------------------------------

const TOKEN = /\s*(y-?\d+:\d\d-\d\d|\d\d-\d\d|@[A-Za-z_]\w*|[A-Za-z_]\w*|\d+|>=|<=|[<>+\-(),#:])/y;

function tokenize(text) {
  const tokens = [];
  text = String(text).trim();
  let pos = 0;
  while (pos < text.length) {
    TOKEN.lastIndex = pos;
    const m = TOKEN.exec(text);
    if (!m || TOKEN.lastIndex === pos) throw new Error('cannot read date rule ' + text);
    tokens.push(m[1]);
    pos = TOKEN.lastIndex;
    while (pos < text.length && /\s/.test(text[pos])) pos += 1;
  }
  return tokens;
}

function Context(reck, paschalion, year, variant, latin, settings, subcalendars) {
  this.reckoning = reck;
  this.paschalion = paschalion;
  this.year = year;
  this.variant = variant;
  this.latin = latin;
  this.settings = settings;
  this.subcalendars = subcalendars || [];
  this.ids = {};
  this.memo = {};
  this.busy = {};
  this.start = null; this.end = null; this.nextStart = null;
  this._easter = null;
}

Context.prototype.yearOf = function (z) { return this.reckoning.fromDay(z).y; };

Context.prototype.easter = function () {
  if (this._easter === null) {
    const rule = PASCHALIONS[this.paschalion];
    const y = this.yearOf(this.start);
    let day = rule(y);
    if (day < this.start) day = rule(y + 1);
    this._easter = day;
  }
  return this._easter;
};

Context.prototype.monthDay = function (month, day) {
  if (this.start === null) return this.reckoning.toDay(this.year, month, day);
  const y = this.yearOf(this.start);
  for (const candidate of [y, y + 1, y + 2]) {
    if (this.reckoning.valid(candidate, month, day)) {
      const z = this.reckoning.toDay(candidate, month, day);
      if (z >= this.start) return z;
    }
  }
  throw new Error('no ' + pad2(month) + '-' + pad2(day) + ' after the start of the year');
};

/** traditions.py: Context.prev_easter.  The last Easter before the year begins. */
Context.prototype.prevEaster = function () {
  const rule = PASCHALIONS[this.paschalion];
  let y = this.yearOf(this.start);
  let day = rule(y);
  while (day >= this.start) { y -= 1; day = rule(y); }
  return day;
};

/** traditions.py: Context.other_month_day.  julian(12-25), coptic(04-29). */
Context.prototype.otherMonthDay = function (cal, month, day) {
  const base = this.start !== null ? this.start : this.reckoning.toDay(this.year, 1, 1);
  if (Object.prototype.hasOwnProperty.call(ALEXANDRIAN_EPOCHS, cal)) {
    const y = alexandrianYear(cal, base);
    for (const c of [y, y + 1, y + 2]) {
      if (alexandrianValid(c, month, day)) {
        const z = alexandrianToDay(cal, c, month, day);
        if (z >= base) return z;
      }
    }
  } else {
    const r = RECKONINGS[cal];
    const y = r.fromDay(base).y;
    for (const c of [y, y + 1, y + 2]) {
      if (r.valid(c, month, day)) {
        const z = r.toDay(c, month, day);
        if (z >= base) return z;
      }
    }
  }
  throw new Error('no ' + cal + ' ' + pad2(month) + '-' + pad2(day) + ' after the start of the year');
};

Context.prototype.monthStart = function (month) {
  if (this.start === null) return [this.year, month];
  const y = this.yearOf(this.start);
  for (const candidate of [y, y + 1]) {
    if (this.reckoning.toDay(candidate, month, 1) >= this.start) return [candidate, month];
  }
  return [y + 1, month];
};

Context.prototype.ref = function (name) {
  if (Object.prototype.hasOwnProperty.call(this.memo, name)) return this.memo[name];
  if (!Object.prototype.hasOwnProperty.call(this.ids, name)) throw new Error("no row with id '" + name + "'");
  if (this.busy[name]) throw new Error("row '" + name + "' is dated in terms of itself");
  this.busy[name] = true;
  let value;
  try { value = this.eval(this.ids[name]); } finally { delete this.busy[name]; }
  this.memo[name] = value;
  return value;
};

Context.prototype.halfEnd = function () {
  let rule = String(this.settings.festival_half_end || 'auto').trim().toLowerCase() || 'auto';
  if (rule === 'auto') {
    rule = String(this.settings.festival_half_end_auto || 'pentecost-week').trim().toLowerCase()
        || 'pentecost-week';
  }
  return this.eval(HALF_ENDS[rule] || rule);
};

Context.prototype.eval = function (text) {
  const t = tokenize(text);
  const r = this.additive(t, 0);
  if (r[1] !== t.length) throw new Error('unexpected ' + t[r[1]] + ' in date rule ' + text);
  return r[0];
};

Context.prototype.additive = function (t, pos) {
  let r = this.primary(t, pos);
  let value = r[0];
  pos = r[1];
  while (pos < t.length && (t[pos] === '+' || t[pos] === '-')
         && pos + 1 < t.length && /^\d+$/.test(t[pos + 1])) {
    const n = parseInt(t[pos + 1], 10);
    value = t[pos] === '+' ? value + n : value - n;
    pos += 2;
  }
  return [value, pos];
};

Context.prototype.primary = function (t, pos) {
  if (pos >= t.length) throw new Error('a date rule ended too soon');
  const tok = t[pos];
  const low = tok.toLowerCase();
  if (tok === '(') {
    const r = this.additive(t, pos + 1);
    if (r[1] >= t.length || t[r[1]] !== ')') throw new Error("missing ')' in a date rule");
    return [r[0], r[1] + 1];
  }
  if ((low === 'max' || low === 'min') && pos + 1 < t.length && t[pos + 1] === '(') {
    const a = this.additive(t, pos + 2);
    if (a[1] >= t.length || t[a[1]] !== ',') throw new Error(low + '() takes two dates');
    const b = this.additive(t, a[1] + 1);
    if (b[1] >= t.length || t[b[1]] !== ')') throw new Error("missing ')' after " + low + '()');
    return [low === 'max' ? Math.max(a[0], b[0]) : Math.min(a[0], b[0]), b[1] + 1];
  }
  if (Object.prototype.hasOwnProperty.call(WEEKDAYS, low) && pos + 1 < t.length) {
    const wd = WEEKDAYS[low];
    const op = t[pos + 1];
    if (op === '#') {
      let p = pos + 2, sign = 1;
      if (p < t.length && t[p] === '-') { sign = -1; p += 1; }
      const count = sign * parseInt(t[p], 10);
      if (t[p + 1] !== ':') throw new Error('write the nth weekday as thu#4:11');
      const month = parseInt(t[p + 2], 10);
      return [this.nthWeekday(month, wd, count), p + 3];
    }
    if (op === '>=' || op === '>' || op === '<=' || op === '<') {
      const r = this.primary(t, pos + 2);
      return [weekdayFrom(r[0], wd, op), r[1]];
    }
  }
  if (/^\d\d-\d\d$/.test(tok)) {
    return [this.monthDay(parseInt(tok.slice(0, 2), 10), parseInt(tok.slice(3), 10)), pos + 1];
  }
  if (OTHER_CALENDARS.indexOf(low) >= 0 && pos + 3 < t.length && t[pos + 1] === '('
      && /^\d\d-\d\d$/.test(t[pos + 2]) && t[pos + 3] === ')') {
    const md = t[pos + 2];
    return [this.otherMonthDay(low, parseInt(md.slice(0, 2), 10), parseInt(md.slice(3), 10)), pos + 4];
  }
  const ym = /^y(-?\d+):(\d\d)-(\d\d)$/.exec(tok);
  if (ym) {
    const y = (this.start !== null ? this.yearOf(this.start) : this.year) + parseInt(ym[1], 10);
    return [this.reckoning.toDay(y, parseInt(ym[2], 10), parseInt(ym[3], 10)), pos + 1];
  }
  if (tok[0] === '@') return [this.ref(tok.slice(1)), pos + 1];
  if (low === 'easter') return [this.easter(), pos + 1];
  if (low === 'prev_easter') return [this.prevEaster(), pos + 1];
  if (low === 'start') return [this.start, pos + 1];
  if (low === 'end') return [this.end, pos + 1];
  if (low === 'next_start') return [this.nextStart, pos + 1];
  if (low === 'half_end') return [this.halfEnd(), pos + 1];
  throw new Error('unknown word ' + tok + ' in a date rule');
};

function weekdayFrom(base, wd, op) {
  if (op === '>=') return base + fmod(wd - weekday(base), 7);
  if (op === '>') return base + 1 + fmod(wd - weekday(base + 1), 7);
  if (op === '<=') return base - fmod(weekday(base) - wd, 7);
  return base - 1 - fmod(weekday(base - 1) - wd, 7);
}

Context.prototype.nthWeekday = function (month, wd, count) {
  const ym = this.monthStart(month);
  const y = ym[0], m = ym[1];
  if (count > 0) {
    const first = this.reckoning.toDay(y, m, 1);
    return first + fmod(wd - weekday(first), 7) + 7 * (count - 1);
  }
  const last = this.reckoning.toDay(y, m, this.reckoning.daysInMonth(y, m));
  return last - fmod(weekday(last) - wd, 7) + 7 * (count + 1);
};

/** Every clause of a `when` cell, separated by '&', must hold. */
Context.prototype.holds = function (when, date) {
  when = String(when || '').trim();
  if (!when) return true;
  for (const clause of when.split('&')) {
    // "A or B and C": the clause holds when any of its alternatives does,
    // each of them its conditions joined by "and" (traditions.py: holds).
    const alts = clause.trim().split(/\s+or\s+/);
    if (alts.length > 1 || /\s+and\s+/.test(clause)) {
      if (!alts.some(a => a.split(/\s+and\s+/).every(c => this.holds(c, date)))) return false;
      continue;
    }
    const words = clause.split(/\s+/).filter(Boolean);
    if (!words.length) continue;
    if (words.length === 1) {
      let flag = words[0].toLowerCase();
      const negate = flag[0] === '!';
      flag = flag.replace(/^!+/, '');
      let ok;
      if (flag === 'latin') ok = this.latin;
      else if (flag.slice(0, 4) === 'sub:') ok = this.subcalendars.indexOf(flag.slice(4)) >= 0;
      else throw new Error('unknown condition ' + words[0]);
      if (ok === negate) return false;
      continue;
    }
    if (words.length !== 3) throw new Error('cannot read condition ' + clause.trim());
    const left = words[0], op = words[1], right = words[2];
    if (left.toLowerCase() === 'year') {
      // The church year, by the calendar year it begins in (traditions.py: holds).
      const y = this.year, b = parseInt(right, 10);
      const ok = { eq: y === b, ne: y !== b, lt: y < b, le: y <= b, gt: y > b, ge: y >= b }[op];
      if (ok === undefined) throw new Error('unknown comparison ' + op);
      if (!ok) return false;
      continue;
    }
    if (left.toLowerCase() === 'variant') {
      const ok = right.toLowerCase().split('|').indexOf(String(this.variant || '').toLowerCase()) >= 0;
      if ((op === 'eq') !== ok) return false;
      continue;
    }
    if (op === 'wd' || op === 'nwd') {
      const day = left.toLowerCase() === 'date' ? date : this.eval(left);
      if (day == null) throw new Error("'date' used where a row has none");
      const ok = right.toLowerCase().split('|').some(n => WEEKDAYS[n] === weekday(day));
      if ((op === 'wd') !== ok) return false;
      continue;
    }
    const a = left.toLowerCase() === 'date' ? date : this.eval(left);
    const b = right.toLowerCase() === 'date' ? date : this.eval(right);
    if (a == null || b == null) throw new Error("'date' used where a row has none");
    const cmp = { eq: a === b, ne: a !== b, lt: a < b, le: a <= b, gt: a > b, ge: a >= b }[op];
    if (cmp === undefined) throw new Error('unknown comparison ' + op);
    if (!cmp) return false;
  }
  return true;
};

// -- a year --------------------------------------------------------------------

/** A cell may hold one value, or one per step of a sequence split by '|'. */
function pickCell(value, index) {
  value = value == null ? '' : String(value);
  if (value.indexOf('|') < 0) return value;
  const parts = value.split('|');
  return index < parts.length ? parts[index] : '';
}

function toInt(value, fallback) {
  const s = value == null ? '' : String(value);
  if (s === '') return fallback === undefined ? null : fallback;
  return /^[+-]?\d+$/.test(s.trim()) && s === s.trim() ? parseInt(s, 10)
       : (fallback === undefined ? null : fallback);
}

/** traditions.py: _first.  A number, or a date rule counted from in weeks. */
function firstOf(ctx, value, fallback) {
  const text = String(value || '').trim();
  if (!text || /^[+-]?\d+$/.test(text)) return [toInt(text, fallback), null];
  return [fallback, ctx.eval(text)];
}

/** traditions.py: _count.  Blank counts up; `down` ends on `first`; `before` counts down to it. */
function countAt(mode, first, index, length) {
  const m = String(mode || '').trim().toLowerCase();
  if (m === 'down') return first - (length - 1 - index);
  if (m === 'before') return first + (length - 1 - index);
  return first + index;
}

function ordinalOf(number) {
  return number >= 0 && number < ORDINALS.length ? ORDINALS[number] : number + 'th';
}

/** traditions.py: _roman. */
function romanOf(number) {
  if (number <= 0) return String(number);
  const table = [[1000, 'M'], [900, 'CM'], [500, 'D'], [400, 'CD'], [100, 'C'], [90, 'XC'],
    [50, 'L'], [40, 'XL'], [10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']];
  let out = '';
  for (const [value, letters] of table) {
    while (number >= value) { out += letters; number -= value; }
  }
  return out;
}

/** traditions.py: _title.  `{number2}`/`{ordinal2}` are a run's second count. */
function titleFrom(template, number, name, number2) {
  let t = String(template);
  if (number2 !== null && number2 !== undefined) {
    t = t.split('{ordinal2}').join(ordinalOf(number2)).split('{roman2}').join(romanOf(number2))
      .split('{number2}').join(String(number2));
  }
  return t.split('{ordinal}').join(ordinalOf(number)).split('{roman}').join(romanOf(number))
    .split('{number}').join(String(number)).split('{name}').join(name);
}

/** A church year of one tradition, worked out from its rules. */
function Year(source, year, calendar, paschalion, latin, settings) {
  const cfg = Object.assign({}, settings || {}, source.settings);
  this.source = source;
  this.tradition = source.tradition;
  this.settings = cfg;
  calendar = String(calendar || cfg.calendar || 'gregorian').trim().toLowerCase();
  if (!RECKONINGS[calendar]) throw new Error('calendar must be one of ' + Object.keys(RECKONINGS));
  this.paschalionNamed = !!paschalion;
  if (!paschalion) {
    paschalion = cfg.paschalion_default || (calendar === 'gregorian' ? 'gregorian' : 'julian');
  }
  if (!PASCHALIONS[paschalion]) throw new Error('paschalion must be gregorian or julian');
  this.calendar = calendar;
  this.paschalion = paschalion;
  this.reckoning = RECKONINGS[calendar];
  this.year = year;
  this.latin = !!latin && truthy(cfg.latin_names_available);
  this.variant = source.tradition.variant;

  this.contexts = {};
  const ctx = this.context(year);
  this.ctx = ctx;
  this.start = ctx.start; this.end = ctx.end; this.nextStart = ctx.nextStart;
  this.easter = ctx.easter();

  this.principal = this.principalDays();
  this.periods = this.periodRows('season');
  this.broad = this.periodRows('broad');
  this.halves = this.periodRows('half');
  this.feasts = this.feastRows();
  if (String(cfg.precedence || '').trim().toLowerCase() === 'roman') this.romanPrecedence();
  this.principal = this.principal.filter(r => !r.hidden);
}

/**
 * The rules' view of church year `year` of this tradition: this year's own,
 * or a neighbor's (a reading plan counts its days through a whole calendar
 * year, which two church years share).
 */
Year.prototype.context = function (year) {
  if (!Object.prototype.hasOwnProperty.call(this.contexts, year)) {
    const cfg = this.settings, source = this.source;
    const ctx = new Context(this.reckoning, this.paschalion, year, this.variant, this.latin, cfg,
                            source.chosen);
    const rule = cfg.year_start || DEFAULT_YEAR_START;
    ctx.start = ctx.eval(rule);
    const ahead = new Context(this.reckoning, this.paschalion, year + 1, this.variant, this.latin, cfg);
    ctx.nextStart = ahead.eval(rule);
    ctx.end = ctx.nextStart - 1;
    for (const row of source.days) {
      if (cell(row, 'id') && cell(row, 'date')) ctx.ids[row.id] = row.date;
    }
    for (const row of source.feasts) {
      if (cell(row, 'id') && cell(row, 'date') && !Object.prototype.hasOwnProperty.call(ctx.ids, row.id)
          && !/^\d\d-\d\d$/.test(row.date)) ctx.ids[row.id] = row.date;
    }
    this.contexts[year] = ctx;
  }
  return this.contexts[year];
};

Year.prototype.principalDays = function () {
  const ctx = this.ctx;
  const singles = new Map();
  const claimed = new Set();
  // A Sunday a fixed-date feast takes (one whose date rule names a month
  // and day: Reformation Day on the Sunday on or before 31 October) still
  // names the week after it: the Sunday of the run it displaced is kept here
  // for weekdayTitle.
  const byFeast = new Set(), bySunday = new Set();
  this.displaced = {};
  for (const row of this.source.days) {
    if (!cell(row, 'date')) continue;
    const day = ctx.eval(row.date);
    if (ctx.holds(cell(row, 'when'), day)) {
      singles.set(row, day);
      if (truthy(cell(row, 'claims'))) {
        claimed.add(day);
        (/\d\d-\d\d/.test(row.date) ? byFeast : bySunday).add(day);
      }
    }
  }
  for (const day of bySunday) byFeast.delete(day);
  const out = [];
  for (const row of this.source.days) {
    if (cell(row, 'date')) {
      if (!singles.has(row)) continue;
      const day = singles.get(row);
      if (this.start <= day && day <= this.end) {
        // traditions.py: a single day's `first` may be a date too.
        const [first, since] = firstOf(ctx, row.first, 1);
        const number = since !== null ? Math.floor((day - since) / 7) : first;
        out.push(this.entry(row, day, 0, number, toInt(row.first2)));
      }
      continue;
    }
    if (!cell(row, 'from')) continue;
    if (!ctx.holds(cell(row, 'when'), null)) continue;
    const firstDay = ctx.eval(row.from);
    const lastDay = cell(row, 'to') ? ctx.eval(row.to) : this.end;
    let every = (cell(row, 'every') || 'sun').trim().toLowerCase();
    if (every === 'sunday' || every === 'sundays') every = 'sun';
    const days = [];
    if (every === 'day') {
      for (let d = firstDay; d <= lastDay; d++) days.push(d);
    } else {
      const wanted = every.replace(/,/g, ' ').split(/\s+/).filter(Boolean).map(w => WEEKDAYS[w]);
      for (let d = firstDay; d <= lastDay; d++) if (wanted.indexOf(weekday(d)) >= 0) days.push(d);
    }
    const [first, since] = firstOf(ctx, cell(row, 'first'), 1);
    const [first2, since2] = firstOf(ctx, cell(row, 'first2'), null);
    days.forEach((day, index) => {
      if (!(this.start <= day && day <= this.end)) return;
      if (claimed.has(day) && !byFeast.has(day)) return;
      const number = since !== null ? Math.floor((day - since) / 7)
        : countAt(cell(row, 'count'), first, index, days.length);
      const number2 = since2 !== null ? Math.floor((day - since2) / 7)
        : first2 === null ? null
        : countAt(cell(row, 'count2'), first2, index, days.length);
      const e = this.entry(row, day, index, number, number2);
      if (claimed.has(day)) {
        if (e.title && !this.displaced[day]) this.displaced[day] = e;
        return;
      }
      out.push(e);
    });
  }
  // Stable, so rows on the same day keep the order the file gives them.
  return out.map((r, i) => [r, i]).sort((a, b) => a[0].day - b[0].day || a[1] - b[1])
            .map(p => p[0]);
};

Year.prototype.entry = function (row, day, index, number, number2) {
  const name = pickCell(cell(row, 'names'), index);
  let title = titleFrom(cell(row, 'title'), number, name, number2);
  const note = titleFrom(pickCell(cell(row, 'notes'), index), number, name, number2);
  if (title && note) title = title + '\n(' + note + ')';
  const latin = pickCell(cell(row, 'latin'), index);
  if (title && this.latin && latin) title = title + '\n(' + latin + ')';
  const full = cell(row, 'full_name');
  const iconOk = !cell(row, 'icon_when') || this.ctx.holds(row.icon_when, day);
  return withRow({
    day: day, title: title,
    color: pickCell(cell(row, 'color'), index).toUpperCase(),
    bottom: pickCell(cell(row, 'color_bottom'), index).toUpperCase(),
    style: pickCell(cell(row, 'style'), index),
    icon: iconOk ? pickCell(cell(row, 'icon'), index) : '',
    fullName: full ? titleFrom(pickCell(full, index), number, name, number2) : '',
    rank: toInt(pickCell(cell(row, 'rank'), index)),
    yield: toInt(cell(row, 'yield')),
    id: cell(row, 'id'), number: number,
    // A day of its own (a `date` row), not one of a run's (`from`/`to`).
    single: !!cell(row, 'date'),
  }, row);
};

Year.prototype.periodRows = function (kind) {
  const ctx = this.ctx;
  const out = [];
  for (const row of this.source.periods) {
    if ((cell(row, 'kind') || 'season').trim().toLowerCase() !== kind) continue;
    if (!ctx.holds(cell(row, 'when'), null)) continue;
    out.push({
      name: cell(row, 'name'), start: ctx.eval(row.start), end: ctx.eval(row.end),
      season: cell(row, 'season').toUpperCase(), color: cell(row, 'color').toUpperCase(),
      subtitle: cell(row, 'subtitle'), scale: cell(row, 'scale'),
      rankWeekday: toInt(cell(row, 'rank_weekday')), rankSunday: toInt(cell(row, 'rank_sunday')),
    });
  }
  return out;
};

Year.prototype.level = function (row) {
  const given = cell(row, 'level').trim().toLowerCase();
  if (given === 'principal' || given === 'festival' || given === 'all') return given;
  const rank = toInt(cell(row, 'rank'));
  const top = toInt(String(this.settings.principal_max_rank == null ? '' : this.settings.principal_max_rank));
  const mid = toInt(String(this.settings.festival_max_rank == null ? '' : this.settings.festival_max_rank));
  if (rank !== null && top !== null && mid !== null) {
    return rank <= top ? 'principal' : rank <= mid ? 'festival' : 'all';
  }
  if (cell(row, 'color_override')) return 'principal';
  if (cell(row, 'color_override_bottom')) return 'festival';
  return 'all';
};

Year.prototype.feastRows = function () {
  const ctx = this.ctx;
  const mode = String(this.settings.feast_repeat || 'all').trim().toLowerCase() || 'all';
  const out = [];
  this.source.feasts.forEach((row, order) => {
    const text = cell(row, 'name'), raw = cell(row, 'date');
    if (!text || !raw) return;
    let days = [];
    const md = /^(\d\d)-(\d\d)$/.exec(raw);
    if (md) {
      const month = parseInt(md[1], 10), dom = parseInt(md[2], 10);
      if (!this.reckoning.valid(2000, month, dom)) return;
      const y0 = ctx.yearOf(this.start), y1 = ctx.yearOf(this.end);
      for (let y = y0; y <= y1; y++) {
        if (!this.reckoning.valid(y, month, dom)) continue;
        const z = this.reckoning.toDay(y, month, dom);
        if (this.start <= z && z <= this.end) days.push(z);
      }
    } else if (/^[+-]?\d{4,}-\d\d-\d\d$/.test(raw)) {
      const m = /^([+-]?)(\d{4,})-(\d\d)-(\d\d)$/.exec(raw);
      const z = this.reckoning.toDay((m[1] === '-' ? -1 : 1) * +m[2], +m[3], +m[4]);
      if (this.start <= z && z <= this.end) days.push(z);
    } else {
      let z;
      try { z = ctx.eval(raw); } catch (e) { return; }
      if (this.start <= z && z <= this.end) days.push(z);
    }
    if (days.length > 1 && (mode === 'first' || mode === 'last')) {
      days = mode === 'first' ? days.slice(0, 1) : days.slice(-1);
    }
    for (const z of days) {
      if (!ctx.holds(cell(row, 'when'), z)) continue;
      let icon = cell(row, 'icon');
      if (icon && cell(row, 'icon_when') && !ctx.holds(row.icon_when, z)) icon = '';
      out.push(withRow({
        day: z, name: text, fullName: cell(row, 'full_name'), link: cell(row, 'link'),
        color: cell(row, 'color_override').toUpperCase(),
        bottom: cell(row, 'color_override_bottom').toUpperCase(),
        rank: toInt(cell(row, 'rank')), level: this.level(row),
        style: cell(row, 'style'), icon: icon, transfer: cell(row, 'transfer'),
        fontSize: cell(row, 'font_size_override'), maxChars: cell(row, 'max_chars_override'),
        verticalOffset: cell(row, 'vertical_offset'),
        id: cell(row, 'id'), order: order, transferredFrom: null,
      }, row));
    }
  });
  return out.map((r, i) => [r, i]).sort((a, b) => a[0].day - b[0].day || a[1] - b[1])
            .map(p => p[0]);
};

Year.prototype.temporalRank = function (day) {
  let best = null;
  for (const r of this.principal) {
    if (r.day === day && r.rank !== null && r.title) best = best === null ? r.rank : Math.min(best, r.rank);
  }
  if (best !== null) return best;
  for (const p of this.periods) {
    if (p.season && p.start <= day && day <= p.end) {
      const wanted = weekday(day) === 6 ? p.rankSunday : p.rankWeekday;
      if (wanted !== null) return wanted;
    }
  }
  return 13;
};

/** Settle which celebrations are kept when two fall on one day; see traditions.py. */
Year.prototype.romanPrecedence = function () {
  const temporal = {};
  for (let d = this.start; d <= this.end; d++) temporal[d] = this.temporalRank(d);
  const tget = (d, fallback) => (Object.prototype.hasOwnProperty.call(temporal, d) ? temporal[d] : fallback);
  const placed = {};
  const kept = [];
  const rankOf = f => (f.rank !== null ? f.rank : 12);
  const pending = this.feasts.map((f, i) => [f, i]).sort((a, b) =>
    rankOf(a[0]) - rankOf(b[0]) || a[0].day - b[0].day || a[0].order - b[0].order || a[1] - b[1])
    .map(p => p[0]);
  const bestPlaced = d => (placed[d] || []).reduce((m, f) => Math.min(m, f.rank), 99);
  // A day a feast ranked 1 to 8 keeps on its own date is not free for a moved
  // one, even before that feast is placed (traditions.py: owned).
  const owned = new Set(this.feasts.filter(f => rankOf(f) <= 8 && rankOf(f) < tget(f.day, 13)).map(f => f.day));
  const free = d => tget(d, 99) > 8 && bestPlaced(d) > 8 && !owned.has(d);
  const hide = truthy(this.settings.hide_outranked_titles);
  const place = (feast, day) => {
    feast.day = day;
    (placed[day] = placed[day] || []).push(feast);
    kept.push(feast);
    const r = feast.rank || 99;
    if (r < tget(day, 99) && r <= 8) {
      for (const row of this.principal) {
        if (row.day === day && row.rank !== null && row.rank > feast.rank && hide) {
          row.hidden = true;
        }
      }
    }
  };
  for (const feast of pending) {
    const rank = rankOf(feast);
    feast.rank = rank;
    const day = feast.day;
    const t = tget(day, 13);
    const p = bestPlaced(day);
    if (p < rank) {
      if (rank >= 10 && p >= 10 && (rank <= 11 || p >= 12)) place(feast, day);
      else if (rank <= 4) this.transfer(feast, free, place);
      continue;
    }
    if (rank < t) place(feast, day);
    else if (rank <= 4) this.transfer(feast, free, place);
    else if (rank >= 10 && t === 9) {
      feast.rank = 12;
      feast.level = 'all';
      const demoted = this.settings.commemoration_style || '';
      if (demoted) feast.style = demoted;
      place(feast, day);
    }
  }
  this.feasts = kept.map((f, i) => [f, i]).sort((a, b) => a[0].day - b[0].day
                                                   || a[0].order - b[0].order || a[1] - b[1])
                    .map(p => p[0]);
  const solemn = new Set();
  for (const d of Object.keys(placed)) if (placed[d].some(f => f.rank <= 4)) solemn.add(+d);
  this.principal = this.principal.filter(r => !(r.yield !== null && solemn.has(r.day)
                                                 && placed[r.day].some(f => f.rank <= r.yield)));
};

Year.prototype.transfer = function (feast, free, place) {
  const day = feast.day;
  let target = null;
  for (let clause of String(feast.transfer || 'next').split(';')) {
    clause = clause.trim();
    if (!clause) continue;
    if (clause.indexOf('=>') >= 0) {
      const i = clause.indexOf('=>');
      const span = clause.slice(0, i), to = clause.slice(i + 2);
      const j = span.indexOf('..');
      const a = j >= 0 ? span.slice(0, j) : span, b = j >= 0 ? span.slice(j + 2) : '';
      const lo = this.ctx.eval(a);
      const hi = b ? this.ctx.eval(b) : lo;
      if (lo <= day && day <= hi) { target = this.ctx.eval(to); break; }
      continue;
    }
    if (clause === 'next' || clause === 'prev') {
      const step = clause === 'next' ? 1 : -1;
      let d = day + step;
      while (this.start <= d && d <= this.end && !free(d)) d += step;
      target = d;
      break;
    }
    if (clause === 'none') return;
  }
  if (target === null || !(this.start <= target && target <= this.end)) return;
  if (target !== day) {
    feast.transferredFrom = day;
    feast.icon = feast.icon.split(/\s+/).filter(k => k && k !== 'obligation').join(' ');
  }
  place(feast, target);
};

/** The first day of a tradition's church year that begins in `year`. */
function yearStart(data, key, year) {
  const tradition = findTradition(data, key);
  const settings = traditionSettings(data, tradition);
  const ctx = new Context(reckoning, 'gregorian', year, tradition.variant, false, settings);
  return ctx.eval(settings.year_start || DEFAULT_YEAR_START);
}

// ---------------------------------------------------------------------------
// Numbers, formatted the way Python formats them
// ---------------------------------------------------------------------------
// The markup is compared against church_year_image.py's character for character, so
// these have to reproduce Python's formatting, not JavaScript's.

/**
 * f"{x:.Nf}".  Python rounds a value that lands exactly halfway to the nearer
 * EVEN last digit; JavaScript's toFixed rounds it away from zero.  Most
 * coordinates here are irrational and never land on a tie, but a stacked line
 * of text at 9.25pt puts its baselines on exact eighths -- 4.625 -- and then
 * the two disagree in the last decimal on every such line.
 *
 * A tie has to be read off the number's exact decimal expansion, not guessed
 * at by arithmetic: -15.675 is not representable as a double, so multiplying
 * it out lands on a whole number and looks like a tie when it is not one.
 */
function pyFixed(x, digits) {
  if (x === 0) x = 0;                                  // fold -0 to 0
  const exact = Math.abs(x).toFixed(Math.min(100, digits + 25));
  const dot = exact.indexOf('.');
  const tail = exact.slice(dot + 1 + digits);          // what we are dropping
  if (!/^50*$/.test(tail)) return x.toFixed(digits);   // not a tie: agree already

  const kept = exact.slice(0, dot) + exact.slice(dot + 1, dot + 1 + digits);
  let n = BigInt(kept);
  if (n % 2n === 1n) n += 1n;                          // round half to even
  const text = n.toString().padStart(digits + 1, '0');
  const body = digits ? text.slice(0, -digits) + '.' + text.slice(-digits) : text;
  return (x < 0 ? '-' : '') + body;
}

const f2 = x => pyFixed(x, 2);                           // f"{x:.2f}"
const f6 = x => pyFixed(x, 6);                           // f"{x:.6f}"

/** str(float): an integral value keeps its trailing ".0". */
function pyFloat(x) {
  return Number.isInteger(x) ? x.toFixed(1) : String(x);
}

/** f"{x:g}" -- six significant digits, trailing zeros trimmed. */
function g(x) {
  if (x === 0) return '0';
  const a = Math.abs(x);
  let exp = Math.floor(Math.log10(a));
  // log10 is not exact at the powers of ten, so settle the exponent by hand.
  if (a >= Math.pow(10, exp + 1)) exp += 1;
  else if (a < Math.pow(10, exp)) exp -= 1;
  if (exp < -4 || exp >= 6) {
    const parts = x.toExponential(5).split('e');
    let mantissa = parts[0];
    if (mantissa.indexOf('.') >= 0) {
      mantissa = mantissa.replace(/0+$/, '').replace(/\.$/, '');
    }
    const sign = parts[1][0] === '-' ? '-' : '+';
    return mantissa + 'e' + sign + parts[1].replace(/^[+-]/, '').padStart(2, '0');
  }
  let s = x.toFixed(Math.max(0, 5 - exp));
  if (s.indexOf('.') >= 0) s = s.replace(/0+$/, '').replace(/\.$/, '');
  return s;
}

function xmlEscape(text) {
  return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');
}

// ---------------------------------------------------------------------------
// Measuring text
// ---------------------------------------------------------------------------

/** The step from one line of a two-line date label to the next, in font sizes (church_year_image.py). */
const DATE_LINE_HEIGHT = 1.15;

function TextMeasurer(data, fudge, smallCapsRatio) {
  this.faces = data.metrics.faces;
  this.first = data.metrics.first;
  this.defaultWidth = data.metrics.default;
  // Past ASCII: the letters the calendars use (church_year_image.py: _FONT_EXTRA).
  this.extra = data.metrics.extra;
  this.last = this.first + this.faces['serif|normal|normal'].length - 1;
  this.hints = data.sansHints;
  this.fudge = fudge;
  this.smallCapsRatio = smallCapsRatio;
  this.cache = new Map();
}

/** Pick the metric table.  `family` is the role (serif / sans-serif). */
TextMeasurer.prototype.faceKey = function (family, weight, style) {
  const name = String(family || '').trim().toLowerCase();
  const fam = this.hints.some(h => name.indexOf(h) >= 0) ? 'sans' : 'serif';
  const w = String(weight == null ? '' : weight).trim().toLowerCase();
  const numeric = parseFloat(w);
  const bold = isNaN(numeric)
    ? (w === 'bold' || w === 'bolder' || w === '800' || w === '900')
    : numeric >= 600;
  const s = String(style == null ? '' : style).trim().toLowerCase();
  const italic = s === 'italic' || s === 'oblique';
  return fam + '|' + (bold ? 'bold' : 'normal') + '|' + (italic ? 'italic' : 'normal');
};

TextMeasurer.prototype.width = function (text, size, family, weight, style, variant) {
  if (!text) return 0.0;
  // Text goes last, so no separator can make two different calls collide.
  const key = [size, family, weight, style, variant, text].join('|');
  const hit = this.cache.get(key);
  if (hit !== undefined) return hit;

  const widths = this.faces[this.faceKey(family, weight, style)]
              || this.faces['serif|normal|normal'];
  const extra = this.extra[this.faceKey(family, weight, style)] || this.extra['serif|normal|normal'];
  const smallCaps = String(variant == null ? '' : variant).trim().toLowerCase()
                    === 'small-caps';
  let total = 0.0;
  for (const raw of text) {
    let glyphs = raw, scale = 1.0;
    // Python's str.islower(): true only for cased characters that are lower.
    if (smallCaps && raw !== raw.toUpperCase() && raw === raw.toLowerCase()) {
      glyphs = raw.toUpperCase();     // may be two letters: "ß" -> "SS"
      scale = this.smallCapsRatio;
    }
    for (const ch of glyphs) {
      const code = ch.codePointAt(0);
      const w = (code >= this.first && code <= this.last)
        ? widths[code - this.first] : (extra[code] !== undefined ? extra[code] : this.defaultWidth);
      total += w * scale;
    }
  }
  const result = total / 1000.0 * size * this.fudge;
  this.cache.set(key, result);
  return result;
};

// ---------------------------------------------------------------------------
// Geometry
// ---------------------------------------------------------------------------

const rad = d => d * Math.PI / 180;
const deg = r => r * 180 / Math.PI;

/** Polar -> Cartesian.  0 deg points right; angles increase clockwise. */
function polar(cx, cy, r, angleDeg) {
  return [cx + r * Math.cos(rad(angleDeg)), cy + r * Math.sin(rad(angleDeg))];
}

/** Angular width in degrees, coping with wrap past 360. */
function arcSpan(a0, a1) { return a1 < a0 ? (360 - a0) + a1 : a1 - a0; }

/** The annular sector a label has to live in. */
function Wedge(rInner, rOuter, angleStart, angleEnd) {
  this.rInner = rInner; this.rOuter = rOuter;
  this.angleStart = angleStart; this.angleEnd = angleEnd;
}
Object.defineProperties(Wedge.prototype, {
  angleMid: { get: function () { return (this.angleStart + this.angleEnd) / 2.0; } },
  angleSpan: { get: function () { return arcSpan(this.angleStart, this.angleEnd); } },
  radialExtent: { get: function () { return this.rOuter - this.rInner; } },
  rMid: { get: function () { return (this.rInner + this.rOuter) / 2.0; } },
});
/** Width of a straight tangential line at radius r that stays inside. */
Wedge.prototype.chordAt = function (r) {
  return Math.max(0.0, 2.0 * r * Math.tan(rad(this.angleSpan) / 2.0));
};

// ---------------------------------------------------------------------------
// Fitting text into a wedge
// ---------------------------------------------------------------------------

const TANGENTIAL = 'tangential', RADIAL = 'radial';

// The feasts CSV holds three kinds of row: those that set the day's color,
// those that only color the lower half of the cell, and those with no color.
const FEAST_DETAIL = ['all', 'festivals', 'principal', 'none'];

function FittedText(lines, size, orientation, lineHeight, rCenter, overflow) {
  this.lines = lines; this.size = size; this.orientation = orientation;
  this.lineHeight = lineHeight; this.rCenter = rCenter;
  this.overflow = !!overflow;
}
Object.defineProperty(FittedText.prototype, 'blockThickness', {
  get: function () { return this.lineHeight * this.lines.length; },
});

/** Greedy word wrap by rendered width, optionally capped by character count. */
function wrapToWidth(paragraphs, maxWidth, style, size, family, measurer, maxChars) {
  const lines = [];
  for (const paragraph of paragraphs) {
    const words = String(paragraph).split(/\s+/).filter(Boolean);
    if (!words.length) continue;
    let current = [];
    for (const word of words) {
      const candidate = current.concat([word]).join(' ');
      const tooWide = measurer.width(candidate, size, family, style.fontWeight,
                                     style.fontStyle, style.fontVariant) > maxWidth;
      const tooLong = maxChars != null && candidate.length > maxChars;
      if (current.length && (tooWide || tooLong)) {
        lines.push(current.join(' '));
        current = [word];
      } else {
        current.push(word);
      }
    }
    if (current.length) lines.push(current.join(' '));
  }
  return lines.length ? lines : [''];
}

/**
 * Wrap into the same number of lines but as evenly as possible.  Plain greedy
 * wrapping leaves a short last line; squeezing the width down as far as it
 * will go without adding a line produces a tidier, more centered block.
 */
function balanceLines(paragraphs, maxWidth, style, size, family, measurer, maxChars) {
  const baseline = wrapToWidth(paragraphs, maxWidth, style, size, family, measurer, maxChars);
  const target = baseline.length;
  if (target <= 1) return baseline;
  let low = 0.0, high = maxWidth, best = baseline;
  for (let i = 0; i < 12; i++) {
    const mid = (low + high) / 2.0;
    const trial = wrapToWidth(paragraphs, mid, style, size, family, measurer, maxChars);
    if (trial.length <= target) { best = trial; high = mid; } else { low = mid; }
  }
  return best;
}

function widest(lines, style, size, family, measurer) {
  let most = 0.0;
  for (const line of lines) {
    most = Math.max(most, measurer.width(line, size, family, style.fontWeight,
                                         style.fontStyle, style.fontVariant));
  }
  return lines.length ? most : 0.0;
}

// ---------------------------------------------------------------------------
// The fitter
// ---------------------------------------------------------------------------

function TextFitter(cfg, measurer) { this.cfg = cfg; this.measurer = measurer; }

TextFitter.prototype.candidateSizes = function (style, pinned) {
  const cfg = this.cfg;
  if (pinned != null) return [pinned];
  const top = style.fontSize * (cfg.autofit_allow_grow ? cfg.autofit_max_scale : 1.0);
  if (!cfg.autofit) return [top];
  const step = Math.max(0.05, cfg.autofit_step);
  const floor = Math.min(style.minFontSize, top);
  const sizes = [];
  // Python rounds each candidate to 3 places as it walks down from the top.
  for (let value = top; value >= floor - 1e-9; value -= step) {
    sizes.push(round3(value));
  }
  if (!sizes.length || Math.abs(sizes[sizes.length - 1] - floor) > 1e-9) {
    sizes.push(round3(floor));
  }
  return sizes;
};

/** Python's round(x, 3): half to even, on the decimal value. */
function round3(x) {
  const scaled = x * 1000;
  const floor = Math.floor(scaled);
  const diff = scaled - floor;
  let n;
  if (Math.abs(diff - 0.5) < 1e-9) n = (floor % 2 === 0) ? floor : floor + 1;
  else n = Math.round(scaled);
  return n / 1000;
}

TextFitter.prototype.tryTangential = function (paragraphs, style, family, size,
                                               wedge, rCenter, maxChars, widthBudget) {
  const cfg = this.cfg;
  const pad = cfg.cell_padding;
  const lineHeight = size * cfg.line_height_factor;
  const heightBudget = wedge.radialExtent - 2 * pad;
  if (heightBudget < lineHeight) return null;
  let lines = [''], countGuess = 1;
  for (let i = 0; i < 8; i++) {
    // The innermost line is the narrowest, so measure there.
    const rRef = rCenter - (countGuess - 1) * lineHeight / 2.0;
    const available = wedge.chordAt(Math.max(rRef, 1.0)) * widthBudget - 2 * pad;
    if (available <= 0) return null;
    lines = balanceLines(paragraphs, available, style, size, family,
                         this.measurer, maxChars);
    if (lines.length === countGuess) break;
    countGuess = lines.length;
  }
  if (lines.length > style.maxLines) return null;
  const rRef = rCenter - (lines.length - 1) * lineHeight / 2.0;
  const available = wedge.chordAt(Math.max(rRef, 1.0)) * widthBudget - 2 * pad;
  if (widest(lines, style, size, family, this.measurer) > available) return null;
  if (lineHeight * lines.length > heightBudget) return null;
  return new FittedText(lines, size, TANGENTIAL, lineHeight, rCenter);
};

TextFitter.prototype.tryRadial = function (paragraphs, style, family, size,
                                           wedge, rCenter, maxChars, widthBudget) {
  const cfg = this.cfg;
  const pad = cfg.cell_padding;
  const lineHeight = size * cfg.line_height_factor;
  const available = wedge.radialExtent - 2 * pad;
  if (available <= 0) return null;
  const lines = balanceLines(paragraphs, available, style, size, family,
                             this.measurer, maxChars);
  if (lines.length > style.maxLines) return null;
  if (widest(lines, style, size, family, this.measurer) > available) return null;
  const stackBudget = wedge.chordAt(rCenter) * widthBudget * cfg.radial_clearance - 2 * pad;
  if (lineHeight * lines.length > stackBudget) return null;
  return new FittedText(lines, size, RADIAL, lineHeight, rCenter);
};

/** The best fit; falls back to the minimum size with overflow flagged. */
TextFitter.prototype.fit = function (paragraphs, style, wedge, pinnedSize,
                                     maxChars, rCenter, orientation) {
  const cfg = this.cfg;
  const family = style.fontFamily;          // the role, never the rendered stack
  const center = rCenter == null ? wedge.rMid : rCenter;
  const widthBudget = cfg.text_fill_ratio;

  let wanted = String(orientation || style.orientation || 'auto').toLowerCase();
  if (String(cfg.text_orientation).toLowerCase() !== 'auto' && wanted === 'auto') {
    wanted = String(cfg.text_orientation).toLowerCase();
  }
  const allowTangential = wanted === 'auto' || wanted === TANGENTIAL;
  const allowRadial = wanted === 'auto' || wanted === RADIAL;

  let best = null;
  for (const size of this.candidateSizes(style, pinnedSize)) {
    const flat = allowTangential
      ? this.tryTangential(paragraphs, style, family, size, wedge, center,
                           maxChars, widthBudget) : null;
    const spoke = allowRadial
      ? this.tryRadial(paragraphs, style, family, size, wedge, center,
                       maxChars, widthBudget) : null;
    if (!flat && !spoke) continue;
    if (!flat) best = spoke;
    else if (!spoke) best = flat;
    else {
      // Both work at this size.  Turning a label radial only pays off if it
      // saves real wrapping, so keep it flat unless the gain is clear.
      const saving = flat.lines.length - spoke.lines.length;
      best = saving >= cfg.radial_min_line_saving ? spoke : flat;
    }
    break;
  }
  if (best) return best;

  // Nothing fits: fall back to the smallest allowed size and let it overflow.
  const size = pinnedSize != null ? pinnedSize : style.minFontSize;
  const lineHeight = size * cfg.line_height_factor;
  const available = (allowRadial && !allowTangential)
    ? wedge.radialExtent - 2 * cfg.cell_padding
    : Math.max(1.0, wedge.chordAt(center) * widthBudget - 2 * cfg.cell_padding);
  const lines = balanceLines(paragraphs, Math.max(available, 1.0), style, size,
                             family, this.measurer, maxChars);
  const chosen = (allowRadial && !allowTangential) ? RADIAL : TANGENTIAL;
  return new FittedText(lines, size, chosen, lineHeight, center, true);
};

// ---------------------------------------------------------------------------
// Building the markup
// ---------------------------------------------------------------------------

function SVGBuilder(cfg, measurer, styles) {
  this.cfg = cfg; this.measurer = measurer; this.styles = styles;
  this.parts = [];
  this.pathId = 0;
  this.clipId = 0;
  this.patterns = new Set();
}

SVGBuilder.prototype.write = function (markup) { this.parts.push(markup); };
SVGBuilder.prototype.content = function () { return this.parts.join(''); };

SVGBuilder.prototype.openDocument = function () {
  const cfg = this.cfg;
  this.write(
    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
    + 'width="' + cfg.width + '" height="' + cfg.height + '" '
    + 'viewBox="0 0 ' + cfg.width + ' ' + cfg.height + '">\n'
    + '<rect x="0" y="0" width="' + cfg.width + '" height="' + cfg.height + '" '
    + 'fill="' + cfg.background_fill + '" />\n');
};

SVGBuilder.prototype.closeDocument = function () { this.write('</svg>\n'); };

SVGBuilder.prototype.addCredit = function (lines) {
  const cfg = this.cfg;
  const size = 12, step = 16, x = 16;
  const bottom = cfg.height - 16;
  this.write('<g font-family="' + xmlEscape(cfg.font_family_sans) + '" font-size="' + size
           + '" fill="#555555">\n');
  lines.forEach((line, i) => {
    const y = bottom - (lines.length - 1 - i) * step;
    this.write('<text x="' + x + '" y="' + y + '">' + xmlEscape(line) + '</text>\n');
  });
  this.write('</g>\n');
};

/** How a credit goes on to its author: " by NAME" for a name, and ", drawn for
 *  this project" for a phrase, which begins in lower case (church_year_image.py:
 *  by_author). */
function byAuthor(author) {
  if (!author) return '';
  const first = author.charAt(0);
  return (first !== first.toUpperCase() ? ', ' : ' by ') + author;
}

/** The artwork credit as two short lines (church_year_image.py: credit_lines). */
function creditLines(art) {
  const title = art.title || art.label || art.key || '';
  const first = 'Center artwork: ' + title + byAuthor(art.author);
  let source = art.sourceUrl || '';
  for (const prefix of ['https://', 'http://']) {
    if (source.startsWith(prefix)) { source = source.slice(prefix.length); break; }
  }
  let second = [art.license || '', source].filter(Boolean).join(' · ');
  if (art.changes && art.changes.toLowerCase() !== 'none') second += ' · ' + art.changes;
  return second ? [first, second] : [first];
}

SVGBuilder.prototype.annulusPath = function (rInner, rOuter, a0, a1) {
  const cfg = this.cfg;
  const largeArc = (a1 - a0) > 180 ? 1 : 0;
  const o0 = polar(cfg.cx, cfg.cy, rOuter, a0), o1 = polar(cfg.cx, cfg.cy, rOuter, a1);
  const i1 = polar(cfg.cx, cfg.cy, rInner, a1), i0 = polar(cfg.cx, cfg.cy, rInner, a0);
  return 'M ' + f2(o0[0]) + ',' + f2(o0[1]) + ' '
       + 'A ' + f2(rOuter) + ',' + f2(rOuter) + ' 0 ' + largeArc + ' 1 '
       + f2(o1[0]) + ',' + f2(o1[1]) + ' '
       + 'L ' + f2(i1[0]) + ',' + f2(i1[1]) + ' '
       + 'A ' + f2(rInner) + ',' + f2(rInner) + ' 0 ' + largeArc + ' 0 '
       + f2(i0[0]) + ',' + f2(i0[1]) + ' Z';
};

/**
 * A fill as SVG paints it.  "#ffffff/#bfbfbf" (colors.csv) is a hatch: the
 * second color in fine diagonal lines over the first -- no color, the hangings
 * removed (church_year_image.py: SVGBuilder.paint).
 */
SVGBuilder.prototype.paint = function (fill) {
  if (String(fill).indexOf('/') < 0) return fill;
  const i = fill.indexOf('/');
  const ground = fill.slice(0, i).trim(), line = fill.slice(i + 1).trim();
  const pid = 'hatch-' + (ground + line).replace(/#/g, '');
  if (!this.patterns.has(pid)) {
    this.patterns.add(pid);
    this.write('<defs><pattern id="' + pid + '" width="6" height="6" '
             + 'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             + '<rect width="6" height="6" fill="' + ground + '" />'
             + '<line x1="0" y1="0" x2="0" y2="6" stroke="' + line + '" stroke-width="1.5" />'
             + '</pattern></defs>\n');
  }
  return 'url(#' + pid + ')';
};

/**
 * Recolor what was written since `start` for a two-color cell: the part above
 * rSplit keeps topFill, the part below takes bottomFill, so one label centered
 * on the whole cell reads on both colors (church_year_image.py: SVGBuilder.split_colors).
 */
SVGBuilder.prototype.splitColors = function (start, rInner, rSplit, rOuter, a0, a1, topFill, bottomFill) {
  const drawn = this.parts.slice(start).join('');
  this.parts.length = start;
  if (!drawn || topFill === bottomFill) { this.write(drawn); return; }
  const n = ++this.clipId;
  const upper = this.annulusPath(rSplit, rOuter, a0, a1);
  const lower = this.annulusPath(rInner, rSplit, a0, a1);
  this.write('<defs><clipPath id="clip' + n + 'a"><path d="' + upper + '" /></clipPath>'
           + '<clipPath id="clip' + n + 'b"><path d="' + lower + '" /></clipPath></defs>\n');
  this.write('<g clip-path="url(#clip' + n + 'a)">\n' + drawn + '</g>\n');
  // The copy reuses the arcs the first one defined.
  const copy = drawn.replace(/<defs>[\s\S]*?<\/defs>\n?/g, '')
    .split('fill="' + topFill + '"').join('fill="' + bottomFill + '"');
  this.write('<g clip-path="url(#clip' + n + 'b)">\n' + copy + '</g>\n');
};

SVGBuilder.prototype.addSector = function (rInner, rOuter, a0, a1, fill, stroke, strokeWidth) {
  const paint = this.paint(fill);
  this.write('<path d="' + this.annulusPath(rInner, rOuter, a0, a1) + '" fill="' + paint
           + '" stroke="' + (stroke || 'none') + '" stroke-width="'
           + pyFloat(strokeWidth || 0.0) + '" />\n');
};

/** A line across a ring at one angle: where the year ends and begins (church_year_image.py: add_radial_line). */
SVGBuilder.prototype.addRadialLine = function (rInner, rOuter, angle, stroke, strokeWidth) {
  const cfg = this.cfg;
  const a = polar(cfg.cx, cfg.cy, rInner, angle), b = polar(cfg.cx, cfg.cy, rOuter, angle);
  this.write('<line x1="' + f2(a[0]) + '" y1="' + f2(a[1]) + '" x2="' + f2(b[0]) + '" y2="' + f2(b[1])
           + '" stroke="' + stroke + '" stroke-width="' + pyFloat(strokeWidth) + '" />\n');
};

/** An icon from icons.csv, drawn in its 100 x 100 box at `size` units. */
SVGBuilder.prototype.addIcon = function (icon, x, y, rotation, size, fill) {
  this.write('<path transform="translate(' + f2(x) + ',' + f2(y) + ') rotate(' + f2(rotation)
           + ') scale(' + g(size / 100.0) + ') translate(-50,-50)" d="' + icon.path
           + '" fill="' + fill + '" fill-rule="evenodd" />\n');
};

SVGBuilder.prototype.addCircleStroke = function (radius, color, width) {
  const cfg = this.cfg;
  this.write('<circle cx="' + pyFloat(cfg.cx) + '" cy="' + pyFloat(cfg.cy)
           + '" r="' + f2(radius) + '" fill="none" stroke="' + color
           + '" stroke-width="' + pyFloat(width) + '" />\n');
};

/**
 * Split text into [chunk, isReduced, isSpace] runs for small caps.
 *
 * Characters that were lower case become capitals drawn at a reduced size;
 * everything else keeps its own case and full size.  Spaces are kept in runs
 * of their own and never merged into a letter run: each run is drawn at an
 * absolute x, and XML strips leading whitespace from an element, so a run
 * beginning with a space would have its first letter pulled back onto the
 * previous word ("OUR LORD" set as "OURL ORD").
 */
function smallCapsRuns(text) {
  const runs = [];
  for (const ch of text) {
    const space = /\s/.test(ch);
    const reduced = ch !== ch.toUpperCase() && ch === ch.toLowerCase();
    const glyph = reduced ? ch.toUpperCase() : ch;
    const last = runs[runs.length - 1];
    if (last && last[1] === reduced && last[2] === space) last[0] += glyph;
    else runs.push([glyph, reduced, space]);
  }
  return runs;
}

SVGBuilder.prototype.resolvedFamily = function (style) {
  const key = String(style.fontFamily).trim().toLowerCase();
  if (key === 'serif' || key === 'font_family_serif') return this.cfg.font_family_serif;
  if (key === 'sans' || key === 'sans-serif' || key === 'font_family_sans') {
    return this.cfg.font_family_sans;
  }
  return style.fontFamily;
};

/**
 * Small caps as capitals at two sizes, each run placed at an exact x.
 *
 * Letting the runs flow (tspans with no x) is what the SVG spec intends, but
 * renderers disagree about it -- CairoSVG re-applies the parent's x to every
 * tspan, which stacks the whole line on top of its first letter.  Measuring
 * each run and writing its x removes the question entirely.
 */
SVGBuilder.prototype.smallCapsBody = function (content, x, size, style) {
  const reduced = size * this.cfg.small_caps_ratio;
  const runs = smallCapsRuns(content).map(r => [r[0], r[1] ? reduced : size, r[2]]);
  const advance = (chunk, runSize) =>
    this.measurer.width(chunk, runSize, style.fontFamily, style.fontWeight, style.fontStyle);

  let total = 0.0;
  for (const r of runs) total += advance(r[0], r[1]);
  let cursor = x - total / 2.0;
  const parts = [];
  for (const r of runs) {
    // Spaces only move the pen along; drawing them would leave every following
    // x one space adrift wherever a renderer strips them.
    if (!r[2]) {
      parts.push('<tspan x="' + f2(cursor) + '" font-size="' + g(r[1]) + '" textLength="'
               + f2(advance(r[0], r[1])) + '" lengthAdjust="spacingAndGlyphs">'
               + xmlEscape(r[0]) + '</tspan>');
    }
    cursor += advance(r[0], r[1]);
  }
  return parts.join('');
};

SVGBuilder.prototype.textElement = function (content, x, y, style, size, fill) {
  const family = this.resolvedFamily(style);
  const smallCaps = String(style.fontVariant).trim().toLowerCase() === 'small-caps';
  const synthesise = smallCaps && this.cfg.small_caps_synthetic;

  const attrs = ['x="' + f2(x) + '"', 'y="' + f2(y) + '"',
                 'font-family="' + family + '"', 'font-size="' + g(size) + '"'];
  if (style.fontWeight && style.fontWeight !== 'normal') {
    attrs.push('font-weight="' + style.fontWeight + '"');
  }
  if (style.fontStyle && style.fontStyle !== 'normal') {
    attrs.push('font-style="' + style.fontStyle + '"');
  }
  // Synthesised runs carry their own absolute x, so each is its own text chunk
  // and must anchor at its start.
  attrs.push('text-anchor="' + (synthesise ? 'start' : 'middle') + '"');
  attrs.push('dominant-baseline="middle"');
  attrs.push('fill="' + fill + '"');

  let body;
  if (synthesise) {
    body = this.smallCapsBody(content, x, size, style);
  } else {
    if (style.fontVariant && style.fontVariant !== 'normal') {
      attrs.push('style="font-variant: ' + style.fontVariant + '"');
    }
    attrs.push(this.textLength(content, size, style, style.fontStyle, style.fontVariant));
    body = xmlEscape(content);
  }
  return '  <text ' + attrs.join(' ') + '>' + body + '</text>\n';
};

/**
 * Draw a fitted block, centered on its wedge's mid angle.  Tangential blocks
 * stack their lines inward; radial blocks run outward from the center of the
 * wheel and stack their lines sideways.
 */
SVGBuilder.prototype.addFittedText = function (fitted, style, wedge, fill, radialShift) {
  if (!fitted.lines.length) return;
  const cfg = this.cfg;
  const radius = fitted.rCenter - (radialShift || 0.0);
  const anchor = polar(cfg.cx, cfg.cy, radius, wedge.angleMid);
  const rotation = fitted.orientation === RADIAL ? wedge.angleMid : wedge.angleMid + 90.0;

  const total = fitted.lineHeight * fitted.lines.length;
  const start = -(total - fitted.lineHeight) / 2.0;
  this.write('<g transform="translate(' + f2(anchor[0]) + ',' + f2(anchor[1])
           + ') rotate(' + f2(rotation) + ')">\n');
  fitted.lines.forEach((line, index) => {
    this.write(this.textElement(line, 0.0, start + index * fitted.lineHeight,
                                style, fitted.size, fill));
  });
  this.write('</g>\n');
};

/** A single line placed at an exact point (day numbers, month labels). */
/**
 * The width the line was fitted at, as the line's own length: a browser
 * without Times New Roman or Arial (a phone's Noto Serif is a tenth wider)
 * draws it to that width rather than past its cell (church_year_image.py:
 * _text_length).
 */
SVGBuilder.prototype.textLength = function (content, size, style, fontStyle, variant) {
  const width = this.measurer.width(content, size, style.fontFamily, style.fontWeight,
                                    fontStyle, variant == null ? 'normal' : variant);
  return 'textLength="' + f2(width) + '" lengthAdjust="spacingAndGlyphs"';
};

SVGBuilder.prototype.addAnchoredText = function (text, x, y, rotation, style,
                                                 size, fill, anchor) {
  const family = this.resolvedFamily(style);
  const baseline = (anchor || 'middle') === 'middle' ? ' dominant-baseline="middle"' : '';
  this.write('<g transform="translate(' + f2(x) + ',' + f2(y) + ') rotate('
           + f2(rotation) + ')">\n'
           + '  <text x="0" y="0" font-family="' + family + '" font-size="' + g(size)
           + '" font-weight="' + style.fontWeight + '" text-anchor="'
           + (anchor || 'middle') + '"' + baseline + ' fill="' + fill + '" '
           + this.textLength(text, size, style, 'normal') + '>'
           + xmlEscape(text) + '</text>\n</g>\n');
};

/**
 * A label bent along a ring, optionally with a smaller trailing part.
 *
 * With a subtitle the two sit on one baseline at two sizes, as two runs that
 * meet at one point along the arc: renderers disagree about how a tspan
 * advances inside a textPath (CairoSVG anchors every tspan by itself, stacking
 * the two), but none disagree about an anchor at an offset written down in
 * user units.  The metrics only place that point, so if a 900-weight face is
 * wider than they say, the label sits a little off center; the parts never meet.
 */
SVGBuilder.prototype.addCurvedLabel = function (text, a0, a1, radius, size,
                                                family, weight, color,
                                                metricFamily, subtitle) {
  const cfg = this.cfg;
  const pathId = 'arc' + (++this.pathId);
  const adjusted = radius + size * cfg.curved_text_vertical_offset;
  const largeArc = (a1 - a0) > 180 ? 1 : 0;
  const s = polar(cfg.cx, cfg.cy, adjusted, a0), e = polar(cfg.cx, cfg.cy, adjusted, a1);
  this.write('<defs><path id="' + pathId + '" d="M ' + f2(s[0]) + ',' + f2(s[1])
           + ' A ' + f2(adjusted) + ',' + f2(adjusted) + ' 0 ' + largeArc + ' 1 '
           + f2(e[0]) + ',' + f2(e[1]) + '" /></defs>\n');

  const attrs = 'font-family="' + family + '" font-size="' + g(size)
              + '" font-weight="' + weight + '" fill="' + color + '"';
  const ref = '<textPath href="#' + pathId + '" xlink:href="#' + pathId + '" ';
  if (!subtitle) {
    this.write('<text ' + attrs + ' text-anchor="middle" xml:space="preserve">' + ref
             + 'startOffset="50%" text-anchor="middle">' + xmlEscape(text)
             + '</textPath></text>\n');
    return;
  }
  const small = size * cfg.ring_subtitle_ratio;
  const sep = cfg.ring_subtitle_separator;
  const trimmed = sep.replace(/\s+$/, '');
  const name = text + trimmed;
  const gap = this.measurer.width(sep.slice(trimmed.length), size, metricFamily, weight);
  const wName = this.measurer.width(name, size, metricFamily, weight);
  const wSub = this.measurer.width(subtitle, small, metricFamily, 'normal', 'italic');
  const length = (a1 - a0) * Math.PI / 180 * adjusted;
  const joint = length / 2.0 + (wName - gap - wSub) / 2.0;
  this.write('<text ' + attrs + ' text-anchor="end" xml:space="preserve">' + ref
           + 'startOffset="' + f2(joint) + '" text-anchor="end">' + xmlEscape(name)
           + '</textPath></text>\n'
           + '<text font-family="' + family + '" font-size="' + g(small)
           + '" font-style="italic" font-weight="normal" fill="' + color
           + '" text-anchor="start" xml:space="preserve">' + ref
           + 'startOffset="' + f2(joint + gap) + '" text-anchor="start">'
           + xmlEscape(subtitle) + '</textPath></text>\n');
};

/** Scale the artwork frozen by export_data.py (an SVG's drawing, or an embedded
 *  image) to fill the middle of the wheel. */
SVGBuilder.prototype.addCenterArtwork = function (art, radius, clip) {
  const cfg = this.cfg;
  const size = radius * 2.0;
  const scale = size / Math.max(art.w, art.h);
  // Centered on its own width and height (church_year_image.py: add_center_artwork).
  const x = cfg.cx - art.w * scale / 2.0 - (art.x || 0) * scale;
  const y = cfg.cy - art.h * scale / 2.0 - (art.y || 0) * scale;
  // Enlarged past the middle's circle: cut to it, off the rings around it.
  const cut = clip > 0 && radius > clip;
  if (cut) {
    this.write('<clipPath id="cy-center-clip"><circle cx="' + f2(cfg.cx) + '" cy="' + f2(cfg.cy)
             + '" r="' + f2(clip) + '" /></clipPath>\n<g clip-path="url(#cy-center-clip)">\n');
  }
  this.write('<g transform="translate(' + f2(x) + ',' + f2(y) + ') scale(' + f6(scale) + ')">\n'
           + art.body + '\n</g>\n');
  if (cut) this.write('</g>\n');
};

// ---------------------------------------------------------------------------
// The calendar
// ---------------------------------------------------------------------------

/**
 * Pull the remaining rings together over the space a disabled one leaves.
 *
 * A ring switched off would otherwise leave a blank annulus where it used to
 * be.  Everything outside the gap slides inward to close it, and the whole set
 * is then scaled back out so the wheel still reaches its original edge -- so
 * turning a ring off gives its room to the rings that are left rather than
 * shrinking the drawing.  With every ring on this changes nothing.
 */
function closeRingGaps(rings, hidden) {
  const live = rings.map(r => Object.assign({}, r,
    { enabled: r.enabled && !(hidden && hidden[r.key]) }));
  const gaps = live.filter(r => !r.enabled).map(r => [r.rInner, r.rOuter])
                   .sort((a, b) => a[0] - b[0]);
  if (!gaps.length) return live;

  const edge = live.reduce((m, r) => Math.max(m, r.rOuter), 0);
  // Two kinds of ring are held at their own size rather than stretched: the
  // artwork in the middle, which is a drawing and not a band, and a plain
  // band, which is usually a border -- growing either reads as the thing
  // itself having changed.  A band that is switched off stops being fixed, so
  // the wheel does grow into the rim when the rim is what was dropped.
  const fixed = live.filter(r => r.enabled && (r.kind === 'center' || r.kind === 'band'))
                    .map(r => [r.rInner, r.rOuter])
                    .sort((a, b) => a[0] - b[0]);

  const free = [];
  let lower = 0;
  for (const [inner, outer] of fixed) {
    if (inner > lower) free.push([lower, inner]);
    lower = Math.max(lower, outer);
  }
  if (lower < edge) free.push([lower, edge]);

  const moves = [];
  for (const [lo, hi] of free) {
    const inside = gaps.map(g => [Math.max(lo, g[0]), Math.min(hi, g[1])])
                       .filter(g => g[1] > g[0]);
    const lost = inside.reduce((sum, g) => sum + g[1] - g[0], 0);
    if (!inside.length || hi - lo <= lost) continue;
    moves.push([lo, hi, (hi - lo) / (hi - lo - lost), inside]);
  }
  if (!moves.length) return live;

  const pulled = radius => {
    for (const [lo, hi, factor, inside] of moves) {
      if (radius < lo || radius > hi) continue;
      let below = 0;
      for (const [a, b] of inside) {
        if (radius > a) below += Math.min(radius, b) - a;
      }
      return lo + (radius - lo - below) * factor;
    }
    return radius;
  };
  return live.filter(r => r.enabled).map(r => Object.assign({}, r, {
    rInner: pulled(r.rInner), rOuter: pulled(r.rOuter),
  }));
}

/**
 * Which feasts the Feasts setting leaves showing, by the row's level: see
 * feast_shown in church_year_image.py.
 */
function feastShown(level, detail) {
  if (detail === 'none') return false;
  if (detail === 'principal') return level === 'principal';
  if (detail === 'festivals') return level === 'principal' || level === 'festival';
  return true;
}

/** The artwork for the middle: named outright, or the tradition's own. */
function artworkKey(data, cfg, profile, asked) {
  const known = data.artworkOrder || [];
  if (asked === 'none') return '';          // the page draws a picture of its own there
  if (asked && known.indexOf(asked) >= 0) return asked;
  // "The tradition's own" (auto) is each church's own picture, whatever the settings name.
  const name = asked === 'auto' ? 'auto' : String(cfg.center_svg || '').trim();
  if (!name || name.toLowerCase() === 'none') return '';
  if (name.toLowerCase() !== 'auto' && known.indexOf(name.toLowerCase()) >= 0) return name.toLowerCase();
  const own = String(profile.art || 'lutherrose').toLowerCase();
  if (own === 'none') return '';            // its picture left out of the page
  if (known.indexOf(own) >= 0) return own;
  return known.length ? known[0] : '';
}

/**
 * The picture a season shows when the middle follows the season
 * (season_art.csv; church_year_image.py: season_art), or '' for the church's own.
 *
 * A row's `season` is a season's name as the wheel gives it ("Advent") or its
 * word in season_periods.csv ("ADVENT"); its `church` is one church's key, or
 * blank for every church; its `week` is the week of the season the picture
 * comes in with (1 is the season's first seven days; 0 the whole season).  A
 * church's own rows win, by name and then by word; then every church's, by
 * word and then by name.  Of the rows found, the one for the latest week that
 * has come: four rows for Advent's weeks light a candle a week.  A row with
 * no `art`, or naming a picture this page does not have, leaves the church's
 * own.
 */
function seasonArt(data, church, name, word, week) {
  const rows = data.seasonArt || [];
  const now = week || 1;
  const find = (who, what) => {
    let best = null;
    if (what) {
      for (const r of rows) {
        if (r.church === who && r.season === what && (r.week || 0) <= now
            && (!best || (r.week || 0) > (best.week || 0))) best = r;
      }
    }
    return best;
  };
  const row = find(church, name) || find(church, word) || find('', word) || find('', name);
  return row && row.art && (data.artwork || {})[row.art] ? row.art : '';
}

/**
 * A church year of one tradition, ready to draw.
 *
 * `opts`: year (the year it begins in), tradition, subcalendars, latinNames,
 * calendar, paschalion, feastDetail, hiddenRings, art, artDate (a day, as
 * 2026-12-25: the middle holds the picture of that day's season, where
 * season_art.csv gives it one).
 */
/**
 * A church's language, as the wheel writes dates in it (church_year_image.py:
 * load_language): the month ring's names, the names in a date, the patterns
 * for a day and for the year's first day (| where it may break), and the
 * Bible book names the page shows.  What a language leaves out is English.
 */
function languageOf(data, code) {
  const all = data.languages || {};
  const english = all.en || { months: Object.keys(data.monthNames || {}).sort((a, b) => a - b).map(k => data.monthNames[k]) };
  const lang = all[String(code || 'en').trim().toLowerCase()] || english;
  const months = lang.months || english.months;
  return {
    months: months,
    dateMonths: lang.dateMonths || months,
    monthDay: lang.monthDay || '{month} {day}',
    fullDate: lang.fullDate || '{month} {day},|{year}',
    chapterVerse: lang.chapterVerse || ':',
    books: lang.books || {},
    colors: lang.colors || {},
    orWord: lang.or || 'or',
    readings: lang.readings || {},
    /** church_year_image.py: Language.day_text. */
    dayText(month, day) {
      return this.monthDay.split('{month}').join(this.dateMonths[month - 1] || String(month))
        .split('{day}').join(String(day));
    },
    /** church_year_image.py: Language.full_text.  Keeps the | break mark. */
    fullText(month, day, year) {
      return this.fullDate.split('{month}').join(this.dateMonths[month - 1] || String(month))
        .split('{day}').join(String(day)).split('{year}').join(year);
    },
  };
}

function Calendar(data, opts) {
  opts = opts || {};
  const tradition = findTradition(data, opts.tradition || data.defaultTradition);
  const profile = data.profiles[tradition.key];
  const cfg = Object.assign({}, profile.settings);
  if (opts.latinNames != null) cfg.latin_names = !!opts.latinNames;
  if (opts.calendar) cfg.calendar = opts.calendar;
  if (opts.paschalion != null) cfg.paschalion = opts.paschalion;
  if (opts.feastDetail) cfg.feast_detail = opts.feastDetail;
  if (opts.midText) cfg.mid_text = opts.midText;
  if (opts.yearLine != null) cfg.year_line = !!opts.yearLine;
  this.tradition = tradition;
  this.profile = profile;

  // Rings the page has turned off for this drawing, by key.  The center and
  // the day cells are the drawing itself, so they are never in this list --
  // not even when a hand-made link asks for it.
  this.hidden = Object.assign({}, opts.hiddenRings || {});
  for (const ring of data.rings) {
    if (ring.kind === 'days' || ring.kind === 'center') delete this.hidden[ring.key];
  }

  // Setting the reckoning here is what makes every date below land in the
  // chosen calendar: daysFromCivil and civilFromDays read it, and iso() too.
  reckoning = RECKONINGS[cfg.calendar] || GREGORIAN;
  const source = new Source(data, tradition, opts.subcalendars || []);
  const year = new Year(source, opts.year, reckoning.name, cfg.paschalion || '',
                        cfg.latin_names, data.configRaw);
  this.year = year;
  this.source = source;
  cfg.calendar = year.calendar;
  cfg.paschalion = year.paschalion;
  cfg.church_year_start = iso(year.start);
  cfg.church_year_end = iso(year.end);
  cfg.cx = cfg.width / 2.0;
  cfg.cy = cfg.height / 2.0;
  const detail = FEAST_DETAIL.indexOf(String(cfg.feast_detail || 'all').trim().toLowerCase()) < 0
    ? 'all' : String(cfg.feast_detail).trim().toLowerCase();
  cfg.feast_detail = detail;

  this.data = data;
  this.cfg = cfg;
  this.cy = { start: year.start, end: year.end, calendar: year.calendar,
              paschalion: year.paschalion, reckoning: year.reckoning };
  // The page's Colors menu may repaint any color or ring for this drawing
  // (church_year_image.py --color-changes does the same; the files are not changed).
  const over = opts.colorOverrides || {};
  this.colors = withOverrides(withMidText(profile.colors, cfg.mid_text), over.days);
  if (over.empty) cfg.empty_cell_fill = over.empty;
  this.styles = profile.styles;
  this.rings = closeRingGaps(data.rings, this.hidden).map(r => {
    const fill = (over.rings || {})[r.key], text = (over.ringText || {})[r.key];
    return fill || text ? Object.assign({}, r, fill ? { fill: fill } : {}, text ? { textColor: text } : {}) : r;
  });
  this.language = languageOf(data, cfg.language);
  this.monthNames = {};
  this.language.months.forEach((name, i) => { this.monthNames[String(i + 1)] = name; });
  this.monthOverrides = data.monthOverrides;
  this.iconDefs = data.icons || {};
  this.art = artworkKey(data, cfg, profile, opts.art);

  const colors = this.colors;
  // "PURPLE; blue": the first color is drawn; the others a source allows are
  // only named, in the readout (church_year_image.py: make_color_lookup).
  const colorOf = name => {
    const parts = String(name || '').split(';');
    const base = colors[parts[0].trim().toUpperCase()];
    if (!base) return null;
    const alt = parts.slice(1).map(s => s.trim()).filter(Boolean).join('; ');
    return alt ? Object.assign({}, base, { alt: alt }) : base;
  };
  const seasonColors = {};
  for (const k in profile.seasonColors) seasonColors[k] = colorOf(profile.seasonColors[k]);
  this.seasonColors = seasonColors;
  this.defaultColor = seasonColors.DEFAULT || colors[Object.keys(colors)[0]];

  this.seasonPeriods = year.periods.map(p => ({
    name: p.name, start: p.start, end: p.end, season: p.season,
    color: colorOf(p.color) || seasonColors[p.season] || null,
  }));
  if (opts.artDate) {
    const seasonal = this.seasonArtOn(fromIso(String(opts.artDate)));
    if (seasonal) this.art = seasonal;
  }
  this.broadSeasons = year.broad.map(p => ({
    name: p.name, start: p.start, end: p.end, subtitle: '', scale: 1.0, scaleIsSubtitle: false,
  }));
  this.halves = year.halves.map(p => ({
    name: p.name, start: p.start, end: p.end, subtitle: p.subtitle,
    scale: Number(p.scale) || 1.0,
    scaleIsSubtitle: String(p.scale).trim().toLowerCase() === 'subtitle',
  }));

  this.titles = {};
  this.icons = {};
  const addIcons = (day, keys) => {
    for (const key of String(keys || '').split(/\s+/).filter(Boolean)) {
      const have = (this.icons[day] = this.icons[day] || []);
      if (have.indexOf(key) < 0) have.push(key);
    }
  };
  for (const row of year.principal) {
    addIcons(row.day, row.icon);
    if (!row.title) continue;
    (this.titles[row.day] = this.titles[row.day] || []).push({
      text: row.title, color: colorOf(row.color), bottomColor: colorOf(row.bottom),
      fontSize: null, maxChars: null, verticalOffset: 0.0, style: row.style,
      fullName: row.fullName,
    });
  }
  const num = v => (v === undefined || v === null || v === '' ? null : parseFloat(v));
  this.feasts = {};
  for (const f of year.feasts) {
    if (detail !== 'all' && !feastShown(f.level, detail)) continue;
    addIcons(f.day, f.icon);
    let full = f.fullName;
    if (f.transferredFrom !== null) {
      const moved = reckoning.fromDay(f.transferredFrom);
      full = (full || f.name) + ' (transferred from ' + pad2(moved.m) + '-' + pad2(moved.d) + ')';
    }
    (this.feasts[f.day] = this.feasts[f.day] || []).push({
      text: f.name, color: colorOf(f.color), bottomColor: colorOf(f.bottom),
      fontSize: num(f.fontSize),
      maxChars: f.maxChars ? parseInt(f.maxChars, 10) : null,
      verticalOffset: num(f.verticalOffset) || 0.0,
      style: f.style || '', fullName: full, link: f.link || '',
    });
  }
  this.everyDayYields = this.findEveryDayYields();

  this.days = [];
  for (let d = year.start; d <= year.end; d++) this.days.push(d);
  this.weeks = groupIntoWeeks(this.days, cfg.week_starts_on, cfg.day_bands);
  this.anglePerWeek = 360.0 / this.weeks.length;

  this.measurer = new TextMeasurer(data, cfg.text_width_fudge, cfg.small_caps_ratio);
  this.fitter = new TextFitter(cfg, this.measurer);
  this.warnings = [];
}

/**
 * The days in weeks, each week a row of `bands` cells.  A year that does not
 * begin on the first day of a week -- the Orthodox year begins on 1
 * September -- is padded with empty cells in front, so each day keeps the
 * band its weekday belongs to; the last week is padded after.
 */
function groupIntoWeeks(days, weekStartsOn, bands) {
  bands = bands || 7;
  const weeks = [];
  let current = [];
  for (const day of days) {
    if (weekday(day) === weekStartsOn && current.length) { weeks.push(current); current = []; }
    if (!current.length && !weeks.length && bands === 7) {
      for (let i = 0; i < fmod(weekday(day) - weekStartsOn, 7); i++) current.push(null);
    }
    current.push(day);
  }
  if (current.length) weeks.push(current);
  return weeks.map(w => (w.length < bands ? w.concat(new Array(bands - w.length).fill(null)) : w));
}

/** The colored period a day falls in; a label-only row is not one. */
/** The picture a day's season shows (seasonArt), or '' for the church's own. */
Calendar.prototype.seasonArtOn = function (day) {
  const within = p => p.start <= day && day <= p.end;
  const named = this.seasonPeriods.find(p => p.name && within(p));
  const colored = this.seasonPeriods.find(p => p.season && within(p));
  // The week of the season: its first seven days are week 1.
  const whole = named || colored;
  const week = whole ? Math.floor((day - whole.start) / 7) + 1 : 1;
  return seasonArt(this.data, this.tradition.key, named ? named.name : '',
                   colored ? colored.season : '', week);
};

Calendar.prototype.seasonFor = function (day) {
  for (const period of this.seasonPeriods) {
    if (period.color && period.start <= day && day <= period.end) return period;
  }
  return null;
};

// Precedence, as church_year_image.py keeps it.  When a saint's day falls on a day
// that outranks it, the day keeps the top of the cell and the feast's color
// takes the lower half.  A day outranks a feast anywhere in Holy Week and Easter
// week; on a Sunday or a named day in Advent, Lent or Easter; and on any day the
// Sundays file gives a color of its own.  Elsewhere a feast colors its day as
// before: the whole cell, or the lower half.
const DEFAULT_FEAST_YIELD = ['ADVENT', 'LENT', 'HOLY_WEEK', 'EASTER', 'POST_EASTER',
                             'PRE_PENTECOST'];
const DEFAULT_FEAST_EVERY_DAY = ['HOLY_WEEK'];
const seasonKeys = (value, fallback) => (Array.isArray(value) ? value
  : value == null || String(value).trim() === '' ? fallback
  : String(value).replace(/,/g, ' ').split(/\s+/).filter(Boolean))
  .map(k => String(k).toUpperCase());

Calendar.prototype.findEveryDayYields = function () {
  const seasons = seasonKeys(this.cfg.feast_yield_every_day, DEFAULT_FEAST_EVERY_DAY);
  const days = {};
  for (const period of this.seasonPeriods) {
    if (!period.season || seasons.indexOf(period.season.toUpperCase()) < 0) continue;
    // The season itself and the seven days after it: Easter week.
    for (let d = period.start; d <= period.end + 7; d++) days[d] = true;
  }
  return days;
};

Calendar.prototype.feastOutranked = function (day) {
  if (this.everyDayYields[day]) return true;
  const titles = this.titles[day] || [];
  if (titles.some(entry => entry.color)) return true;
  const period = this.seasonFor(day);
  const yieldIn = seasonKeys(this.cfg.feast_yield_seasons, DEFAULT_FEAST_YIELD);
  return !!period && yieldIn.indexOf(String(period.season).toUpperCase()) >= 0
      && (weekday(day) === 6 || titles.length > 0);
};

Calendar.prototype.colorFor = function (day) {
  for (const entry of (this.titles[day] || [])) if (entry.color) return entry.color;
  if (!this.feastOutranked(day)) {
    for (const entry of (this.feasts[day] || [])) if (entry.color) return entry.color;
  }
  const period = this.seasonFor(day);
  if (period && period.color) return period.color;
  return this.defaultColor;
};

Calendar.prototype.bottomColorFor = function (day) {
  // A day's own split (Christmas Eve, Holy Saturday) is part of the day.
  for (const entry of (this.titles[day] || [])) if (entry.bottomColor) return entry.bottomColor;
  const feasts = this.feasts[day] || [];
  for (const entry of feasts) if (entry.bottomColor) return entry.bottomColor;
  // A feast that would color the whole cell yields the top and takes the foot.
  if (this.feastOutranked(day)) for (const entry of feasts) if (entry.color) return entry.color;
  return null;
};

Calendar.prototype.dayAngle = function (weekIndex, bandIndex) {
  return this.cfg.start_angle + weekIndex * this.anglePerWeek
       + (bandIndex / this.cfg.day_bands) * this.anglePerWeek;
};

/** Angular runs of each calendar month, cut at the exact day of change. */
/** church_year_image.py: year_seams.  The padding where a year starts or ends midweek. */
Calendar.prototype.yearSeams = function () {
  if (!this.weeks.length) return [];
  const start = this.cfg.start_angle;
  const full = start + this.weeks.length * this.anglePerWeek;
  const seams = [];
  let lead = this.weeks[0].findIndex(d => d !== null);
  if (lead < 0) lead = 0;
  if (lead) seams.push([start, this.dayAngle(0, lead)]);
  const lastWeek = this.weeks[this.weeks.length - 1];
  const filled = lastWeek.filter(d => d !== null).length;
  if (filled < lastWeek.length) seams.push([this.dayAngle(this.weeks.length - 1, filled), full]);
  return seams;
};

Calendar.prototype.monthSegments = function () {
  const segments = [];
  let currentMonth = null, segmentStart = this.cfg.start_angle;
  this.weeks.forEach((week, weekIndex) => {
    week.forEach((day, bandIndex) => {
      if (day === null) return;
      const angle = this.dayAngle(weekIndex, bandIndex);
      const month = monthOf(day);
      if (currentMonth === null) { currentMonth = month; segmentStart = angle; }
      else if (month !== currentMonth) {
        segments.push([currentMonth, segmentStart, angle]);
        currentMonth = month; segmentStart = angle;
      }
    });
  });
  if (currentMonth !== null) {
    // The last month runs to the end of the last day; when the year ends
    // partway through a week, that is short of the full circle.
    const lastWeek = this.weeks[this.weeks.length - 1];
    const filled = lastWeek.filter(d => d !== null).length;
    const end = filled === lastWeek.length
      ? this.cfg.start_angle + this.weeks.length * this.anglePerWeek
      : this.dayAngle(this.weeks.length - 1, filled);
    segments.push([currentMonth, segmentStart, end]);
  }
  return segments;
};

/** One angular run per dated period, from its first day to the end of its last. */
Calendar.prototype.periodSegments = function (periods) {
  const dayWidth = this.anglePerWeek / this.cfg.day_bands;
  const positions = {};
  this.weeks.forEach((week, weekIndex) => {
    week.forEach((day, bandIndex) => {
      if (day !== null) positions[day] = this.dayAngle(weekIndex, bandIndex);
    });
  });
  const segments = [];
  for (const period of periods) {
    let lowest = Infinity, highest = -Infinity;
    for (const day of this.days) {
      if (day >= period.start && day <= period.end && positions[day] !== undefined) {
        lowest = Math.min(lowest, positions[day]);
        highest = Math.max(highest, positions[day]);
      }
    }
    if (lowest !== Infinity) segments.push([period, lowest, highest + dayWidth]);
  }
  return segments;
};

Calendar.prototype.segmentsForSource = function (source) {
  if (source === 'months') return this.monthSegments();
  // Only the rows that name something reach the ring; a color-only row has
  // no label to put on it.
  if (source === 'season_periods')
    return this.periodSegments(this.seasonPeriods.filter(p => p.name));
  if (source === 'broad_seasons') return this.periodSegments(this.broadSeasons);
  if (source === 'halves') return this.periodSegments(this.halves);
  return [];
};

Calendar.prototype.labelForSegment = function (source, item) {
  if (source === 'months') return this.monthNames[String(item)] || String(item);
  return item.name === undefined ? String(item) : item.name;
};

Calendar.prototype.warn = function (day, where, message) {
  this.warnings.push({ day: day == null ? null : iso(day), where: where, message: message });
};

// ---------------------------------------------------------------------------
// The renderer
// ---------------------------------------------------------------------------

function Renderer(calendar) {
  this.cal = calendar;
  this.cfg = calendar.cfg;
  this.svg = new SVGBuilder(this.cfg, calendar.measurer, calendar.styles);
}

/**
 * Draw each ring, keeping its markup separately: everything but the artwork in
 * the middle turns when the wheel turns.
 */
Renderer.prototype.renderRings = function () {
  const pieces = [];
  for (const ring of this.cal.rings) {
    if (!ring.enabled) continue;
    const mark = this.svg.parts.length;
    if (ring.kind === 'days') this.renderWeekRing(ring);
    else if (ring.kind === 'segments' || ring.kind === 'months') this.renderSegmentRing(ring);
    else if (ring.kind === 'band') this.renderBandRing(ring);
    else if (ring.kind === 'center') this.renderCenter(ring);
    if (truthy(this.cfg.year_line) && ['days', 'segments', 'months'].indexOf(ring.kind) >= 0) {
      this.svg.addRadialLine(ring.rInner, ring.rOuter, this.cfg.start_angle,
                             this.cfg.day_stroke, this.cfg.year_line_width);
    }
    pieces.push([ring, this.svg.parts.slice(mark).join('')]);
  }
  return pieces;
};

Renderer.prototype.render = function () {
  this.svg.openDocument();
  this.renderRings();
  this.renderCredit();
  this.svg.closeDocument();
  return this.svg.content();
};

/** The artwork's credit in a corner, when its license asks for one (church_year_image.py: _render_credit). */
Renderer.prototype.renderCredit = function () {
  const mode = String(this.cfg.artwork_credit || 'auto').trim().toLowerCase();
  const center = this.cal.rings.find(r => r.kind === 'center' && r.enabled);
  if (mode === 'none' || !center) return;
  const art = this.cal.art && this.cal.data.artwork[this.cal.art];
  // A picture of the user's own is credited only with a credit given (own_art_row).
  if (!art || (art.own && !art.title)) return;
  const needed = ['required', 'owner', 'yes', 'true'].indexOf(String(art.attribution || '').toLowerCase()) >= 0;
  if (mode !== 'always' && !needed) return;
  this.svg.addCredit(creditLines(art));
};

Renderer.prototype.renderBandRing = function (ring) {
  const rMid = (ring.rInner + ring.rOuter) / 2.0;
  if (ring.fill && ring.fill !== 'none') {
    this.svg.addCircleStroke(rMid, ring.fill, ring.rOuter - ring.rInner);
  }
  if (ring.innerBorderColor && ring.innerBorderWidth) {
    // Drawn wholly inside the band rather than straddling its inner edge.  A
    // straddling stroke puts half its width over whatever is inside the ring,
    // and that half survives or not depending on whether a later ring paints
    // over it -- so the border looked twice as thick the moment the ring below
    // it was switched off.  Inside the band it is the same thickness whatever
    // its neighbors do, and the width is simply what you see.
    const width = Math.min(ring.innerBorderWidth, ring.rOuter - ring.rInner);
    this.svg.addCircleStroke(ring.rInner + width / 2.0, ring.innerBorderColor, width);
  }
};

Renderer.prototype.renderCenter = function (ring) {
  // A ground for the picture (church_year_image.py: _render_center).
  if (ring.fill && ring.fill !== 'none') {
    this.svg.addCircleStroke(ring.rOuter / 2.0, ring.fill, ring.rOuter);
  }
  const art = this.cal.art && this.cal.data.artwork[this.cal.art];
  if (!art) return;
  const scale = art.scale ? Number(art.scale) : 1.0;
  this.svg.addCenterArtwork(art, ring.rOuter * (isFinite(scale) ? scale : 1.0), ring.rOuter);
};

Renderer.prototype.renderSegmentRing = function (ring) {
  const source = ring.source || (ring.kind === 'months' ? 'months' : '');
  const segments = this.cal.segmentsForSource(source);
  const painted = [];
  for (const seg of segments) {
    // A source may nest one span inside another -- CHRISTMAS inside the
    // festival half -- so that both can be labeled on one ring.  Only the
    // covering span is painted; a second wedge over the same arc would show up
    // the moment the ring is given a stroke.
    if (painted.some(p => p[0] <= seg[1] && seg[2] <= p[1])) continue;
    painted.push([seg[1], seg[2]]);
    this.svg.addSector(ring.rInner, ring.rOuter, seg[1], seg[2],
                       ring.fill, ring.stroke, ring.strokeWidth);
  }
  // church_year_image.py: close the notch where the year starts or ends midweek.
  let seam = String(this.cfg.year_seam_fill || 'auto').trim();
  if (seam.toLowerCase() === 'auto') seam = this.cfg.empty_cell_fill;
  if (seam && seam.toLowerCase() !== 'none') {
    for (const [a0, a1] of this.cal.yearSeams()) {
      this.svg.addSector(ring.rInner, ring.rOuter, a0, a1, seam, ring.stroke, ring.strokeWidth);
    }
  }
  if (ring.labelMode === 'none') return;

  let labeled = segments;
  if (source === 'months' && this.cfg.month_label_largest_only) {
    const widestSeg = new Map();
    for (const seg of segments) {
      const span = arcSpan(seg[1], seg[2]);
      const seen = widestSeg.get(seg[0]);
      if (!seen || span > seen[3]) widestSeg.set(seg[0], [seg[0], seg[1], seg[2], span]);
    }
    labeled = Array.from(widestSeg.values()).map(v => [v[0], v[1], v[2]]);
  }
  const plans = labeled.map(seg => this.planRingLabel(
    ring, this.cal.labelForSegment(source, seg[0]), seg[1], seg[2],
    (seg[0] && seg[0].subtitle) || '', labelScale(seg[0])));
  this.settleRingLabels(ring, plans);
  if (!this.uniformRingLabels(ring, plans)) this.spillRingLabels(ring, plans);
  for (const plan of plans) this.drawRingLabel(ring, plan);
};

/** A nested label's size against its ring's, or 0 for "the subtitle's". */
function labelScale(item) {
  if (item && item.scaleIsSubtitle) return 0.0;
  return (item && Number(item.scale)) || 1.0;
}

/** Choose a size for one ring label, against its own arc alone. */
Renderer.prototype.planRingLabel = function (ring, text, a0, a1, subtitle, scale) {
  const cfg = this.cfg;
  const measurer = this.cal.measurer;
  const style = {
    name: 'ring:' + ring.key, fontFamily: ring.fontFamily, fontSize: ring.fontSize,
    fontWeight: ring.fontWeight, fontStyle: 'normal', fontVariant: 'normal',
    minFontSize: cfg.ring_label_min_font_size, maxLines: 3, orientation: RADIAL, fill: '',
  };
  const span = arcSpan(a0, a1);
  const radius = (ring.rInner + ring.rOuter) / 2.0;
  const factor = scale === 0.0 ? cfg.ring_subtitle_ratio : scale;

  // The label and its subtitle together, since both share the arc.  The
  // subtitle is set in italics at regular weight, so it is measured that way.
  const fullWidth = at => subtitle
    ? measurer.width(text + cfg.ring_subtitle_separator, at,
                     style.fontFamily, ring.fontWeight)
      + measurer.width(subtitle, at * cfg.ring_subtitle_ratio,
                       style.fontFamily, 'normal', 'italic')
    : measurer.width(text, at, style.fontFamily, ring.fontWeight);

  let size = ring.fontSize * factor;
  if ((ring.labelMode === 'curve' || ring.labelMode === 'auto') && cfg.ring_label_autofit) {
    const budget = rad(span) * radius * cfg.ring_label_arc_usage;
    while (size > cfg.ring_label_min_font_size) {
      if (fullWidth(size) <= budget) break;
      size -= Math.max(0.25, cfg.autofit_step);
    }
  }
  return { text: text, subtitle: subtitle, style: style, a0: a0, a1: a1,
           size: size, width: fullWidth, full: ring.fontSize * factor, spill: false };
};

/**
 * Shrink labels that would run into one another on the same ring.
 *
 * Segments that sit side by side never collide, because each label is already
 * held inside its own arc.  Nested segments are the reason this exists:
 * FESTIVAL HALF spans the arcs CHRISTMAS and EASTER divide between them, so
 * all three are centered inside the same stretch of ring.  The narrower span
 * speaks first -- it has nowhere else to go -- and the wider one gives way
 * until it clears, which in an ordinary year costs it nothing.
 */
Renderer.prototype.settleRingLabels = function (ring, plans) {
  if (plans.length < 2 || ring.labelMode === 'radial') return;
  const cfg = this.cfg;
  const radius = (ring.rInner + ring.rOuter) / 2.0;
  const step = Math.max(0.25, cfg.autofit_step);

  const extent = plan => {
    const middle = plan.a0 + arcSpan(plan.a0, plan.a1) / 2.0;
    const reach = deg(plan.width(plan.size) / 2.0 / radius);
    return [middle - reach, middle + reach];
  };

  const claimed = [];
  const order = plans.slice().sort((p, q) => arcSpan(p.a0, p.a1) - arcSpan(q.a0, q.a1));
  for (const plan of order) {
    while (plan.size > cfg.ring_label_min_font_size) {
      const e = extent(plan);
      if (!claimed.some(c => e[0] < c[1] && c[0] < e[1])) break;
      plan.size -= step;
    }
    claimed.push(extent(plan));
  }
};

/**
 * One size for every label on the ring (ring_label_uniform; church_year_image.py:
 * _uniform_ring_labels): the largest, from the ring's own down, at which every
 * label fits along its arc or past a short arc into the free ring beside it,
 * each half its size clear of the next.  A sliver of a name the ring shows
 * elsewhere is left unlabeled.  False when the ring does not ask for it, or
 * nothing fits even at the smallest size.
 */
Renderer.prototype.uniformRingLabels = function (ring, plans) {
  const cfg = this.cfg;
  const keys = String(cfg.ring_label_uniform || '').replace(/,/g, ' ').split(/\s+/).filter(Boolean);
  if (keys.indexOf(ring.key) < 0 || !cfg.ring_label_autofit
      || (ring.labelMode !== 'auto' && ring.labelMode !== 'curve')) return false;
  const live = plans.filter(p => p.text);
  if (!live.length || !ring.fontSize) return false;
  const radius = (ring.rInner + ring.rOuter) / 2.0;
  const step = Math.max(0.25, cfg.autofit_step);
  const smallest = cfg.ring_label_min_font_size;
  const low = Math.min(...plans.map(p => p.a0));
  const high = Math.max(...plans.map(p => p.a0 + arcSpan(p.a0, p.a1)));
  const middle = new Map(live.map(p => [p, p.a0 + arcSpan(p.a0, p.a1) / 2.0]));
  const factor = new Map(live.map(p => [p, p.full / ring.fontSize]));
  const reach = (plan, size) => deg(plan.width(size) / 2.0 / radius);
  const ownArc = (plan, size) =>
    plan.width(size) <= rad(arcSpan(plan.a0, plan.a1)) * radius * cfg.ring_label_arc_usage;

  const slivers = live.filter(p => !ownArc(p, smallest * factor.get(p)) && live.some(o =>
    o !== p && o.text === p.text && ownArc(o, smallest * factor.get(o))));
  const rest = live.filter(p => slivers.indexOf(p) < 0);

  const attempt = base => {
    const size = new Map(rest.map(p => [p, base * factor.get(p)]));
    const center = new Map();
    const taken = other => {
      const s = size.get(other);
      if (center.has(other) || ownArc(other, s)) {
        const c = center.has(other) ? center.get(other) : middle.get(other);
        const r = reach(other, s);
        return [c - r, c + r];
      }
      return [other.a0, other.a0 + arcSpan(other.a0, other.a1)];
    };
    const order = rest.slice().sort((p, q) => arcSpan(p.a0, p.a1) - arcSpan(q.a0, q.a1));
    for (const plan of order) {
      const mid = middle.get(plan), s = size.get(plan);
      let left = low, right = high;
      for (const other of rest) {
        if (other === plan) continue;
        const [c, d] = taken(other);
        if (d <= mid) left = Math.max(left, d);
        else if (c >= mid) right = Math.min(right, c);
        else return null;
      }
      const r = reach(plan, s);
      const pad = deg(s / 2.0 / radius);
      const lo = left + pad + r, hi = right - pad - r;
      if (lo > hi) return null;
      const at = Math.min(Math.max(mid, lo), hi);
      if (Math.abs(at - mid) > r) return null;
      center.set(plan, at);
    }
    return [size, center];
  };

  for (let base = ring.fontSize; base >= smallest - 1e-9; base -= step) {
    const found = attempt(base);
    if (found) {
      const [size, center] = found;
      for (const plan of rest) {
        plan.size = size.get(plan);
        plan.center = center.get(plan);
        plan.spill = !ownArc(plan, plan.size) || Math.abs(plan.center - middle.get(plan)) > 1e-9;
      }
      for (const plan of slivers) plan.hidden = true;
      return true;
    }
  }
  return false;
};

/**
 * Give a label shrunk by a short arc the free ring on either side
 * (church_year_image.py: _spill_ring_labels).  The shortest arcs go first.  A label
 * takes the free stretch of ring around its arc's middle (up to the next
 * label, half its size clear of it, never past the year's start or end), keeps
 * its arc's middle under it, sits as near centered on its arc as that allows,
 * and grows back toward its ring's size, or from a turn across the ring to a
 * curve along it.
 */
Renderer.prototype.spillRingLabels = function (ring, plans) {
  const cfg = this.cfg;
  if (!truthy(cfg.ring_label_spill) || !cfg.ring_label_autofit || !plans.length
      || (ring.labelMode !== 'auto' && ring.labelMode !== 'curve')) return;
  const radius = (ring.rInner + ring.rOuter) / 2.0;
  const step = Math.max(0.25, cfg.autofit_step);
  const low = Math.min(...plans.map(p => p.a0));
  const high = Math.max(...plans.map(p => p.a0 + arcSpan(p.a0, p.a1)));
  const middle = new Map(plans.map(p => [p, p.a0 + arcSpan(p.a0, p.a1) / 2.0]));
  const center = new Map();

  const reach = (plan, size) => deg(plan.width(size) / 2.0 / radius);
  const ownArc = (plan, size) =>
    plan.width(size) <= rad(arcSpan(plan.a0, plan.a1)) * radius * cfg.ring_label_arc_usage;
  const taken = other => {
    if (other.spill || ownArc(other, other.size)) {
      const c = center.has(other) ? center.get(other) : middle.get(other);
      const r = reach(other, other.size);
      return [c - r, c + r];
    }
    return [other.a0, other.a0 + arcSpan(other.a0, other.a1)];   // turned across the ring
  };
  const place = (plan, size) => {
    const mid = middle.get(plan);
    let left = low, right = high;
    for (const other of plans) {
      if (other === plan || !other.text) continue;
      const [c, d] = taken(other);
      if (d <= mid) left = Math.max(left, d);
      else if (c >= mid) right = Math.min(right, c);
      else return null;                // another label already covers this arc's middle
    }
    const r = reach(plan, size);
    const pad = deg(size / 2.0 / radius);
    const lo = left + pad + r, hi = right - pad - r;
    if (lo > hi) return null;
    const at = Math.min(Math.max(mid, lo), hi);
    return Math.abs(at - mid) <= r ? at : null;
  };

  const order = plans.slice().sort((p, q) => arcSpan(p.a0, p.a1) - arcSpan(q.a0, q.a1));
  for (const plan of order) {
    if (!plan.text || plan.size >= plan.full) continue;
    let at = place(plan, plan.size);
    if (at === null) continue;           // no room: it stays as it was
    let size = plan.size;
    while (size + step <= plan.full + 1e-9) {
      const nxt = place(plan, size + step);
      if (nxt === null) break;
      size += step; at = nxt;
    }
    if (size > plan.size || !ownArc(plan, plan.size)) {
      plan.size = size;
      plan.spill = true;
      plan.center = at;
      center.set(plan, at);
    }
  }
  // A sliver that could only turn across the ring, of a name the ring reads
  // elsewhere, is left unlabeled rather than crowd its neighbors.
  for (const plan of plans) {
    if (plan.text && !plan.spill && !ownArc(plan, plan.size) && plans.some(other =>
      other !== plan && other.text === plan.text && (other.spill || ownArc(other, other.size)))) {
      plan.hidden = true;
    }
  }
};

/** Curve the label along the ring; turn it across the ring if the arc is too short. */
Renderer.prototype.drawRingLabel = function (ring, plan) {
  if (!plan.text || plan.hidden) return;
  const cfg = this.cfg;
  const style = plan.style;
  const family = this.svg.resolvedFamily(style);
  const span = arcSpan(plan.a0, plan.a1);
  const radius = (ring.rInner + ring.rOuter) / 2.0;
  const budget = rad(span) * radius * cfg.ring_label_arc_usage;
  const fits = plan.width(plan.size) <= budget;

  if (plan.spill) {
    // Past its own arc: a path as long as the label, where it was placed.
    const reach = deg(plan.width(plan.size) / 2.0 / radius) / cfg.ring_label_arc_usage;
    this.svg.addCurvedLabel(plan.text, plan.center - reach, plan.center + reach, radius, plan.size, family,
                            ring.fontWeight, ring.textColor, style.fontFamily, plan.subtitle);
    return;
  }
  if (ring.labelMode === 'curve' || (fits && ring.labelMode !== 'radial')) {
    this.svg.addCurvedLabel(plan.text, plan.a0, plan.a1, radius, plan.size, family,
                            ring.fontWeight, ring.textColor,
                            style.fontFamily, plan.subtitle);
    if (!fits) {
      this.cal.warn(null, 'ring:' + ring.key,
                    "'" + plan.text + "' overflows its arc even at " + g(plan.size) + 'pt');
    }
    return;
  }

  const wedge = new Wedge(ring.rInner, ring.rOuter, plan.a0, plan.a1);
  const fitted = this.cal.fitter.fit([plan.text], style, wedge, null, null, null, RADIAL);
  if (fitted.overflow && cfg.ring_label_hide_if_unfit) {
    this.cal.warn(null, 'ring:' + ring.key, "'" + plan.text + "' dropped: no room");
    return;
  }
  if (fitted.overflow) {
    this.cal.warn(null, 'ring:' + ring.key,
                  "'" + plan.text + "' turned radial and still tight at " + g(fitted.size) + 'pt');
  }
  this.svg.addFittedText(fitted, style, wedge, ring.textColor, 0.0);
};

Renderer.prototype.renderWeekRing = function (ring) {
  const bands = this.cfg.day_bands;
  const bandHeight = (ring.rOuter - ring.rInner) / bands;
  this.cal.weeks.forEach((week, weekIndex) => {
    const a0 = this.cfg.start_angle + weekIndex * this.cal.anglePerWeek;
    const a1 = a0 + this.cal.anglePerWeek;
    for (let bandIndex = 0; bandIndex < bands; bandIndex++) {
      const day = bandIndex < week.length ? week[bandIndex] : null;
      const rOuter = ring.rOuter - bandIndex * bandHeight;
      this.renderDay(day, new Wedge(rOuter - bandHeight, rOuter, a0, a1));
    }
  });
};

/**
 * Space the day number occupies, as [inner radius, half-width the text must
 * stay inside].  The number sits in the leading top corner of the cell, and
 * labels are centered, so a label clears it only if half its width stays inside
 * the limit, or if it sits below the radius.
 */
Renderer.prototype.numberGuard = function (day, wedge) {
  const cfg = this.cfg;
  const style = this.cal.styles.day_number;
  const size = style.fontSize;
  const text = String(dayOf(day));
  const width = this.cal.measurer.width(text, size, style.fontFamily,
                                        style.fontWeight, style.fontStyle);
  const rNumber = wedge.rOuter - cfg.day_number_vertical_ratio * wedge.radialExtent;
  const rGuard = rNumber - 0.15 * size;
  // Tangential position of the number's leading edge, from the cell center.
  const offsetDeg = (cfg.day_number_horizontal_ratio - 0.5) * wedge.angleSpan;
  const start = rNumber * Math.tan(rad(offsetDeg));
  return [rGuard, -(start + width + cfg.day_number_gap)];
};

Renderer.prototype.collidesWithNumber = function (fitted, guard, style) {
  const rGuard = guard[0], limit = guard[1];
  if (fitted.orientation === RADIAL) {
    // Radial lines run the depth of the cell, so they always reach the
    // number's row; only their sideways spread decides.
    return fitted.blockThickness / 2.0 > limit;
  }
  const total = fitted.blockThickness;
  const topRadius = fitted.rCenter + (total - fitted.lineHeight) / 2.0 + fitted.size * 0.4;
  if (topRadius <= rGuard) return false;
  const half = widest(fitted.lines.slice(0, 1), style, fitted.size,
                      style.fontFamily, this.cal.measurer) / 2.0;
  return half > limit;
};

Renderer.prototype.renderDay = function (day, wedge) {
  const cfg = this.cfg, cal = this.cal;

  if (day === null) {
    this.svg.addSector(wedge.rInner, wedge.rOuter, wedge.angleStart, wedge.angleEnd,
                       cfg.empty_cell_fill, cfg.empty_cell_stroke, cfg.day_stroke_width);
    return;
  }

  const color = cal.colorFor(day);
  let bottom = cal.bottomColorFor(day);
  if (bottom && bottom.fill === color.fill) {
    // Both halves the same color: splitting would only draw a line across an
    // otherwise plain cell.
    bottom = null;
  }
  // The labels are settled before the cell is painted, because where the color
  // breaks depends on how much each of them has to say.
  const titles = cal.titles[day] || [];
  let feasts = cal.feasts[day] || [];

  if (cfg.deduplicate_day_labels && titles.length && feasts.length) {
    // A principal day and a commemoration can name the same thing -- when 31
    // October falls on a Sunday, Reformation Day is both.  Colors are already
    // settled above, so dropping the repeat only affects text.
    const flat = s => s.toLowerCase().split(/\s+/).filter(Boolean).join(' ');
    const spoken = new Set(titles.map(e => flat(e.text)));
    const kept = feasts.filter(e => !spoken.has(flat(e.text)));
    for (const dropped of feasts.filter(e => kept.indexOf(e) < 0)) {
      cal.warn(day, 'duplicate', "'" + dropped.text + "' also appears as the day's "
               + 'title; the commemoration was not drawn');
    }
    feasts = kept;
  }

  // A day with icons keeps a strip along its inner edge for them, and the
  // labels are fitted in what is left above it.
  const icons = cal.icons[day] || [];
  const tw = icons.length
    ? new Wedge(wedge.rInner + cfg.icon_size + cfg.icon_gap + cfg.cell_padding, wedge.rOuter,
                wedge.angleStart, wedge.angleEnd)
    : wedge;

  const rSplit = bottom ? this.colorSplit(day, tw, titles, feasts) : wedge.rMid;

  if (bottom) {
    this.svg.addSector(rSplit, wedge.rOuter, wedge.angleStart, wedge.angleEnd,
                       color.fill, cfg.day_stroke, cfg.day_stroke_width);
    this.svg.addSector(wedge.rInner, rSplit, wedge.angleStart, wedge.angleEnd,
                       bottom.fill, cfg.day_stroke, cfg.day_stroke_width);
  } else {
    this.svg.addSector(wedge.rInner, wedge.rOuter, wedge.angleStart, wedge.angleEnd,
                       color.fill, cfg.day_stroke, cfg.day_stroke_width);
  }

  const textColor = color.text;
  const bottomTextColor = bottom ? bottom.text : textColor;

  const hasTopLabel = this.renderDayNumber(day, wedge, textColor);
  const guard = hasTopLabel ? null : this.numberGuard(day, wedge);
  if (icons.length) this.drawIcons(icons, wedge, bottomTextColor);

  if (!titles.length && !feasts.length) return;

  // Space available to the labels once the date line has taken its slice.
  let body = tw;
  if (hasTopLabel) {
    body = new Wedge(tw.rInner,
                     wedge.rOuter - this.topLabelRoom(day, wedge),
                     wedge.angleStart, wedge.angleEnd);
  } else if (guard && titles.length && feasts.length) {
    // Two labels have to share the cell, so keep both out of the date's row.
    body = new Wedge(tw.rInner, Math.min(wedge.rOuter, guard[0]),
                     wedge.angleStart, wedge.angleEnd);
  }

  if (titles.length && feasts.length) {
    let topBox, bottomBox;
    if (bottom) {
      topBox = new Wedge(Math.max(rSplit, body.rInner), body.rOuter,
                         wedge.angleStart, wedge.angleEnd);
      bottomBox = new Wedge(tw.rInner, Math.min(rSplit, body.rOuter),
                            wedge.angleStart, wedge.angleEnd);
    } else {
      const share = this.splitShare(day, titles, feasts);
      const cut = body.rOuter - share * body.radialExtent;
      topBox = new Wedge(cut, body.rOuter, wedge.angleStart, wedge.angleEnd);
      bottomBox = new Wedge(body.rInner, cut, wedge.angleStart, wedge.angleEnd);
    }
    this.drawEntries(day, titles, topBox, textColor, true, guard);
    this.drawEntries(day, feasts, bottomBox, bottomTextColor, false, null);
  } else if (titles.length && bottom && this.spansTwoDays(day, color, bottom)
             && this.drawTitleHalves(day, titles, body, rSplit, textColor, bottomTextColor, guard)) {
    // The day's own name alone, on a day of two colors (Christmas Eve, Holy
    // Saturday): its first words on the upper color, the rest on the lower.
  } else if (titles.length && bottom && this.spansTwoDays(day, color, bottom)) {
    // One word on a day of two colors: centered on the whole cell, each part of
    // it in the text color of the color behind it (church_year_image.py).
    const start = this.svg.parts.length;
    this.drawEntries(day, titles, body, textColor, true, guard);
    this.svg.splitColors(start, wedge.rInner, rSplit, wedge.rOuter,
                         wedge.angleStart, wedge.angleEnd, textColor, bottomTextColor);
  } else if (titles.length) {
    // The name on the color of its own occasion, the upper part.
    const box = bottom
      ? new Wedge(Math.max(rSplit, body.rInner), body.rOuter, wedge.angleStart, wedge.angleEnd)
      : body;
    this.drawEntries(day, titles, box, textColor, true, guard);
  } else {
    // A commemoration alone sits on the color it brings, the lower part.
    const box = bottom
      ? new Wedge(body.rInner, Math.min(rSplit, body.rOuter), wedge.angleStart, wedge.angleEnd)
      : body;
    this.drawEntries(day, feasts, box, bottomTextColor, false, guard);
  }
};

/**
 * Whether a day's two colors are both its own: the day before's above and the
 * day after's below (Christmas Eve, Holy Saturday) (church_year_image.py: _spans_two_days).
 */
Renderer.prototype.spansTwoDays = function (day, color, bottom) {
  if (!this.dayIndex) {
    this.dayIndex = new Map();
    this.cal.days.forEach((d, i) => this.dayIndex.set(d, i));
  }
  const i = this.dayIndex.get(day);
  const days = this.cal.days;
  if (i === undefined || i === 0 || i + 1 >= days.length) return false;
  return this.cal.colorFor(days[i - 1]).fill === color.fill
    && this.cal.colorFor(days[i + 1]).fill === bottom.fill;
};

/**
 * A day's name split over the two colors of its cell: the first words above
 * the break, the rest below, at one size (church_year_image.py: _draw_title_halves).
 */
Renderer.prototype.drawTitleHalves = function (day, titles, body, rSplit, topFill, bottomFill, guard) {
  let firsts, seconds, words = [];
  const lines = titles[0].text.split('\n').filter(p => p.trim());
  if (titles.length > 1) {
    // Two names (Advent 4 on Christmas Eve): one on each color.
    firsts = titles.slice(0, 1); seconds = titles.slice(1);
  } else if (lines.length > 1) {
    // A name already in lines: the first above, the rest below.
    firsts = [Object.assign({}, titles[0], { text: lines[0] })];
    seconds = [Object.assign({}, titles[0], { text: lines.slice(1).join('\n') })];
  } else {
    words = titles[0].text.split(/\s+/).filter(Boolean);
    if (words.length < 2) return false;
  }
  let k = 1, best = null;
  const note = words.findIndex((w, i) => i > 0 && w.startsWith('('));
  if (note > 0) { k = note; best = -1; }
  for (let i = 1; i < words.length && best !== -1; i++) {
    const score = Math.max(words.slice(0, i).join(' ').length, words.slice(i).join(' ').length);
    if (best === null || score < best) { best = score; k = i; }
  }
  // The upper name stays out of the day number's row.
  const topOuter = guard ? Math.min(body.rOuter, guard[0]) : body.rOuter;
  const topBox = new Wedge(Math.max(rSplit, body.rInner), topOuter, body.angleStart, body.angleEnd);
  const footBox = new Wedge(body.rInner, Math.min(rSplit, body.rOuter), body.angleStart, body.angleEnd);
  if (topBox.radialExtent <= 0 || footBox.radialExtent <= 0) return false;
  if (words.length) {
    firsts = [Object.assign({}, titles[0], { text: words.slice(0, k).join(' ') })];
    seconds = [Object.assign({}, titles[0], { text: words.slice(k).join(' ') })];
  }
  const style = this.styleFor(day, titles[0], true);
  const size = Math.min(this.fitEntries(firsts, style, topBox).fitted.size,
                        this.fitEntries(seconds, style, footBox).fitted.size);
  this.drawEntries(day, firsts.map(e => Object.assign({}, e, { fontSize: size })), topBox, topFill, true, guard);
  this.drawEntries(day, seconds.map(e => Object.assign({}, e, { fontSize: size })), footBox, bottomFill, true, null);
  return true;
};

/** A day's icons, side by side and centered along the cell's inner edge. */
Renderer.prototype.drawIcons = function (keys, wedge, fill) {
  const cfg = this.cfg;
  const known = keys.filter(k => this.cal.iconDefs[k]).map(k => this.cal.iconDefs[k]);
  if (!known.length) return;
  const size = cfg.icon_size;
  const radius = wedge.rInner + cfg.cell_padding + size / 2.0;
  const total = known.length * size + (known.length - 1) * cfg.icon_gap;
  known.forEach((icon, index) => {
    const offset = -total / 2.0 + size / 2.0 + index * (size + cfg.icon_gap);
    const angle = wedge.angleMid + offset / radius * 180.0 / Math.PI;
    const p = polar(cfg.cx, cfg.cy, radius, angle);
    this.svg.addIcon(icon, p[0], p[1], wedge.angleMid + 90.0, size, fill);
  });
};

/** How much of the cell the upper label gets, based on how much text each has. */
Renderer.prototype.splitShare = function (day, titles, feasts) {
  const cfg = this.cfg;
  const titleStyle = this.styleFor(day, titles[0], true);
  const feastStyle = this.styleFor(day, feasts[0], false);
  let titleMass = 0, feastMass = 0;
  for (const e of titles) titleMass += e.text.length * titleStyle.fontSize;
  for (const e of feasts) feastMass += e.text.length * feastStyle.fontSize;
  const total = titleMass + feastMass;
  if (total <= 0) return 0.5;
  return Math.min(cfg.split_share_max,
                  Math.max(cfg.split_share_min, titleMass / total));
};

Renderer.prototype.styleFor = function (day, entry, isTitle) {
  const styles = this.cal.styles;
  if (entry.style && styles[entry.style]) return styles[entry.style];
  if (!isTitle) return styles.feast;
  return styles[weekday(day) === this.cfg.week_starts_on ? 'sunday_title' : 'weekday_title'];
};

/**
 * Fit a cell's labels, and say which way the line breaks fell out.
 *
 * A line break written into a title is a preference, not a command.  Both
 * forms are fitted and the break is kept only when it costs nothing.
 */
Renderer.prototype.fitEntries = function (entries, style, box) {
  let pinned = null, maxChars = null;
  for (const e of entries) {
    if (pinned === null && e.fontSize != null) pinned = e.fontSize;
    if (maxChars === null && e.maxChars != null) maxChars = e.maxChars;
  }
  const apart = [];
  for (const e of entries) {
    for (const part of e.text.split('\n')) if (part) apart.push(part);
  }
  const flowed = entries.map(e => e.text.split(/\s+/).filter(Boolean).join(' '));
  let paragraphs = apart;
  let fitted = this.cal.fitter.fit(apart, style, box, pinned, maxChars, null, null);
  if (apart.join('\u0000') !== flowed.join('\u0000')) {
    const together = this.cal.fitter.fit(flowed, style, box, pinned, maxChars, null, null);
    if ((fitted.overflow && !together.overflow) || together.size > fitted.size) {
      fitted = together;
      paragraphs = flowed;
    }
  }
  return { fitted: fitted, paragraphs: paragraphs };
};

/**
 * Whether this cell's date runs as a line across the top of it.
 *
 * The first day of the year and the first of each month do; every other day
 * gets a bare number in the corner.  The cell has to know before it is
 * painted, because where the color breaks depends on what room is left under
 * the line.
 */
Renderer.prototype.hasTopLabel = function (day) {
  return iso(day) === this.cfg.church_year_start || dayOf(day) === 1;
};

/**
 * Where the color changes in a cell whose commemoration recolors the foot.
 *
 * Half and half wherever that works, because a ring of cells all breaking at
 * the same radius reads as a pattern and one breaking at a different radius
 * each time reads as a mistake.  It stops working when the upper half has far
 * more to say than the lower: Advent 1 on St. Andrew carries an opening date
 * line and a Sunday title with its Latin name over a commemoration of two
 * words, and half the cell is nothing like enough for the one while being
 * twice what the other needs.
 *
 * So the two are fitted at a few positions and the line goes where the
 * worse-off label comes closest to the size its style asks for -- but only if
 * that is `color_split_gain` better than the middle manages.  Nearly every
 * split cell gains a little from a nudge, and taking every one of those would
 * leave the wheel with no two breaks alike for the sake of a point of type.
 */
Renderer.prototype.colorSplit = function (day, wedge, titles, feasts) {
  const cfg = this.cfg;
  const middle = wedge.rMid;
  if (!titles.length || !feasts.length || wedge.radialExtent <= 0) return middle;

  let bodyOuter = wedge.rOuter;
  if (this.hasTopLabel(day)) {
    bodyOuter -= this.topLabelRoom(day, wedge);
  } else {
    const guard = this.numberGuard(day, wedge);
    if (guard) bodyOuter = Math.min(bodyOuter, guard[0]);
  }
  if (bodyOuter <= wedge.rInner) return middle;

  const titleStyle = this.styleFor(day, titles[0], true);
  const feastStyle = this.styleFor(day, feasts[0], false);

  const shareOf = radius => {
    const top = new Wedge(Math.max(radius, wedge.rInner), bodyOuter,
                          wedge.angleStart, wedge.angleEnd);
    const foot = new Wedge(wedge.rInner, Math.min(radius, bodyOuter),
                           wedge.angleStart, wedge.angleEnd);
    if (top.radialExtent <= 0 || foot.radialExtent <= 0) return -1.0;
    let worst = Infinity;
    const pairs = [[titles, titleStyle, top], [feasts, feastStyle, foot]];
    for (const [entries, style, box] of pairs) {
      const f = this.fitEntries(entries, style, box).fitted;
      const score = f.overflow ? 0.0 : Math.min(1.0, f.size / style.fontSize);
      if (score < worst) worst = score;
    }
    return worst;
  };

  // Every candidate is judged against the middle, not against the one before
  // it, so a run of small improvements cannot creep past the threshold a step
  // at a time.
  const centered = shareOf(middle);
  let best = middle, bestScore = centered;
  const step = 0.05;
  for (let share = 0.5 + step; share <= cfg.color_split_max + 1e-9; share += step) {
    const radius = wedge.rOuter - share * wedge.radialExtent;
    const value = shareOf(radius);
    if (value >= centered + cfg.color_split_gain && value > bestScore + 1e-9) {
      best = radius;
      bestScore = value;
    }
  }
  return best;
};

Renderer.prototype.drawEntries = function (day, entries, box, fill, isTitle, guard) {
  if (box.radialExtent <= 0) return;
  const style = this.styleFor(day, entries[0], isTitle);
  let pinned = null, maxChars = null, shift = 0.0;
  for (const e of entries) {
    if (pinned === null && e.fontSize != null) pinned = e.fontSize;
    if (maxChars === null && e.maxChars != null) maxChars = e.maxChars;
    shift += e.verticalOffset;
  }
  const chosen = this.fitEntries(entries, style, box);
  let fitted = chosen.fitted, paragraphs = chosen.paragraphs;
  if (guard && this.collidesWithNumber(fitted, guard, style)) {
    // Drop the label clear of the day number and fit again in what is left.
    const clear = new Wedge(box.rInner, Math.min(box.rOuter, guard[0]),
                            box.angleStart, box.angleEnd);
    if (clear.radialExtent > 0) {
      const retry = this.cal.fitter.fit(paragraphs, style, clear, pinned, maxChars, null, null);
      if (!(retry.overflow && !fitted.overflow)) { fitted = retry; box = clear; }
    }
  }
  const where = isTitle ? 'title' : 'feast';
  if (fitted.overflow) {
    this.cal.warn(day, where, "'" + paragraphs.join(' / ') + "' does not fit (placed at "
                  + g(fitted.size) + 'pt, ' + fitted.lines.length + ' lines)');
  } else if (fitted.size < this.cfg.warn_below_font_size) {
    this.cal.warn(day, where, "'" + paragraphs.join(' / ') + "' shrunk to "
                  + g(fitted.size) + 'pt');
  }
  this.svg.addFittedText(fitted, style, box, fill, shift);
};

/** Draw the day number.  Returns true if it took the full width of the cell. */
/**
 * How deep a slice the date line at the top of a cell really needs.
 *
 * `top_label_reserve` is a share of the band, which is a fair proxy while the
 * label has the whole cell to itself.  It stops being one as soon as something
 * else has taken part of the cell: a day whose commemoration recolors the
 * lower half leaves its title only the strip between the color line and this
 * reserve, and a flat third of the band can be most of that strip.  So the
 * reserve is measured instead -- where the line is drawn, plus half its own
 * height and a padding -- with `top_label_reserve` left as the ceiling, so
 * this only ever hands space back, never takes it.
 */
Renderer.prototype.topLabelRoom = function (day, wedge) {
  const cfg = this.cfg;
  const cal = this.cal;
  const band = wedge.radialExtent;
  const isFirst = iso(day) === cfg.church_year_start;
  const style = cal.styles[isFirst ? 'first_day_label' : 'month_day_label'];
  const key = String(monthOf(day));
  let size = style.fontSize;
  if (!isFirst) size = cal.monthOverrides.fontSize[key] || size;
  const drop = isFirst ? cal.monthOverrides.firstDayVertical
                       : (cal.monthOverrides.vertical[key] || 0.0);
  if (isFirst) {
    // The year's first day may take a second line ("September 11," / "2026");
    // then the cell gives it the room, ceiling or not.
    const rLabel = wedge.rOuter - cfg.day_number_vertical_ratio * band - drop;
    const [lines, fit] = this.dateLabelFit(this.firstDayText(day), style, wedge, rLabel, null);
    if (lines.length > 1) {
      return cfg.day_number_vertical_ratio * band + drop
        + (lines.length - 1) * fit * DATE_LINE_HEIGHT + fit / 2.0 + cfg.cell_padding;
    }
  }
  const needed = cfg.day_number_vertical_ratio * band + drop + size / 2.0 + cfg.cell_padding;
  return Math.min(cfg.top_label_reserve * band, Math.max(0.0, needed));
};

/** church_year_image.py: _first_day_text. */
Renderer.prototype.firstDayText = function (day) {
  const month = monthOf(day);
  return this.cal.language.fullText(month, dayOf(day), yearName(yearOf(day)));
};

Renderer.prototype.renderDayNumber = function (day, wedge, fill) {
  const cfg = this.cfg, cal = this.cal;
  let rLabel = wedge.rOuter - cfg.day_number_vertical_ratio * wedge.radialExtent;
  const month = monthOf(day), dayNum = dayOf(day);

  if (iso(day) === cfg.church_year_start) {
    const style = cal.styles.first_day_label;
    rLabel -= cal.monthOverrides.firstDayVertical;
    this.centeredDateLabel(this.firstDayText(day), style, wedge, rLabel, fill, null, null);
    return true;
  }

  if (dayNum === 1) {
    const style = cal.styles.month_day_label;
    const key = String(month);
    rLabel -= cal.monthOverrides.vertical[key] || 0.0;
    const angle = wedge.angleMid + (cal.monthOverrides.horizontal[key] || 0.0);
    const pinned = cal.monthOverrides.fontSize[key];
    this.centeredDateLabel(cal.language.dayText(month, dayNum), style, wedge, rLabel, fill,
                           pinned === undefined ? null : pinned, angle);
    return true;
  }

  const style = cal.styles.day_number;
  const angle = wedge.angleStart + cfg.day_number_horizontal_ratio * wedge.angleSpan;
  const p = polar(cfg.cx, cfg.cy, rLabel, angle);
  this.svg.addAnchoredText(String(dayNum), p[0], p[1], wedge.angleMid + 90.0,
                           style, style.fontSize, fill, 'start');
  return false;
};

/** A "January 1" style line, shrunk if the wedge is too narrow for it. */
/**
 * The lines and size of a "January 1" style label: one line, shrunk if the
 * wedge is too narrow for it; one that does not fit even at the style's
 * smallest size breaks where its | marks onto a second line ("September 11," /
 * "2026"), each line fitted to the width at its own radius (church_year_image.py:
 * _date_label_fit).
 */
Renderer.prototype.dateLabelFit = function (text, style, wedge, radius, pinned) {
  const cfg = this.cfg;
  const whole = text.split('|').join(' ');
  if (pinned != null || !cfg.autofit) return [[whole], pinned != null ? pinned : style.fontSize];
  const fits = (lines, size) => lines.every((line, i) => {
    const r = radius - i * size * DATE_LINE_HEIGHT;
    const room = wedge.chordAt(r) * cfg.text_fill_ratio - 2 * cfg.cell_padding;
    return this.cal.measurer.width(line, size, style.fontFamily, style.fontWeight, style.fontStyle) <= room;
  });
  const candidates = [[whole]];
  const at = text.lastIndexOf('|');
  if (at >= 0) candidates.push([text.slice(0, at).split('|').join(' ').trim(), text.slice(at + 1).trim()]);
  let lines = candidates[0], size = style.fontSize;
  for (lines of candidates) {
    size = style.fontSize;
    while (size > style.minFontSize && !fits(lines, size)) size -= Math.max(0.05, cfg.autofit_step);
    if (fits(lines, size)) return [lines, size];
  }
  return [lines, size];
};

/** A "January 1" style label (dateLabelFit), its lines centered, the first at `radius`, the next below. */
Renderer.prototype.centeredDateLabel = function (text, style, wedge, radius, fill,
                                                 pinned, angleOverride) {
  const cfg = this.cfg;
  const [lines, size] = this.dateLabelFit(text, style, wedge, radius, pinned);
  const angle = angleOverride == null ? wedge.angleMid : angleOverride;
  lines.forEach((line, i) => {
    const p = polar(cfg.cx, cfg.cy, radius - i * size * DATE_LINE_HEIGHT, angle);
    this.svg.addAnchoredText(line, p[0], p[1], wedge.angleMid + 90.0, style, size, fill);
  });
};

// ---------------------------------------------------------------------------
// What the page and the verifier use
// ---------------------------------------------------------------------------

const WEEKDAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const ORDINAL_START = /^(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth|Fifteenth|Sixteenth|Seventeenth|Eighteenth|Nineteenth|Twentieth|Twenty-\w+|Thirtieth|Thirty-\w+|Last|Sunday)\b/;
const OWN_WEEK = /^(The )?Sunday\b|Nativity|Christmas|Epiphany|Theophany|Holy Family|Baptism|Circumcision|Holy Name|Wedding at Cana/;
const ARTICLE_NAMES = /^(Baptism|Transfiguration|Resurrection|Holy Trinity|Feast|Nativity|Presentation|Epiphany|Ascension|Annunciation|Holy Family)\b/;

/**
 * A weekday's name from the Sunday before it, for a weekday the calendar
 * gives no name of its own (tradition.csv `weekday_titles`):
 *   after (the default; the Lutheran and Anglican books): "Tuesday after the
 *     Sixth Sunday after Pentecost", "Wednesday of Laetare" where the Sunday
 *     is named by its Latin name;
 *   week (the Roman Missal, the Byzantine books): "Tuesday of the Sixth Week
 *     after Pentecost", "Tuesday of the First Week of Advent", "Tuesday of the
 *     Thirteenth Week in Ordinary Time";
 *   none: no such names (a calendar whose names are not in English).
 * A Sunday a fixed-date feast takes (Reformation Day, All Saints' Day
 * observed) gives way to the Sunday it displaced: "Tuesday after the
 * Twenty-first Sunday after Pentecost" -- but not the feasts of Christmas
 * and the Epiphany, or a named Sunday ("Sunday of the Forefathers"), except
 * where the weeks are counted ("week").
 * None for a Sunday, or before the year's first Sunday.
 */
function weekdayTitle(cal, day) {
  const style = String((cal.year.settings || {}).weekday_titles || '').trim().toLowerCase();
  const wd = weekday(day);
  if (wd === 6 || style === 'none') return '';
  const sunday = day - wd - 1;
  if (sunday < cal.year.start) return '';
  let entry = (cal.titles[sunday] || [])[0];
  // Where the weeks are not counted, a named Sunday ("Sunday of the
  // Forefathers") and the feasts of Christmas and the Epiphany still name
  // their weeks.
  const moved = (cal.year.displaced || {})[sunday];
  const own = entry && OWN_WEEK.test(String(entry.fullName || entry.text));
  if (moved && (style === 'week' || !own)) entry = { text: moved.title, fullName: moved.fullName };
  if (!entry) return '';
  const flat = s => String(s).split(/\s+/).filter(Boolean).join(' ');
  const dayName = WEEKDAY_NAMES[wd];
  const latin = cal.year.latin && /\n\(([^()]+)\)\s*$/.exec(String(entry.text));
  if (latin) return dayName + ' of ' + flat(latin[1]);
  // The name before any alternative ("..., or Easter Day", "...: Proper 8",
  // "(Whit Sunday)").
  let name = flat(entry.fullName || entry.text).split(': ')[0].split(/, (?:or|commonly called) /)[0]
    .replace(/\s*\([^()]*\)\s*$/, '');
  if (!name) return '';
  if (style === 'week') {
    const m = /^(?:The )?(\S+) Sunday (of|in|after) (.+)$/.exec(name);
    if (m) return dayName + ' of the ' + m[1] + ' Week ' + m[2] + ' ' + m[3];
  }
  if (/^The /.test(name)) name = 'the ' + name.slice(4);
  else if (ORDINAL_START.test(name) || ARTICLE_NAMES.test(name)) name = 'the ' + name;
  return dayName + ' after ' + name;
}

/**
 * The hymnal topics of each day (a folder's hymn_topics.csv): day -> [{h:
 * the hymnal's Hymnary.org code, t: the topic or section, s: its sub-topic
 * (blank for all of the topic), n: the section's
 * numbers ("331-357"), blank for a topic}], each once, for the
 * hymn marks after the day's name.  Keys are read as readings.csv's are
 * (dayKeyResolver); a feast's id counts while the wheel shows it.
 */
function hymnTopicsIndex(cal) {
  const year = cal.year, out = {};
  const rows = cal.source.hymnTopics;
  if (!rows.length) return out;
  const byId = {};
  for (const e of year.principal) if (e.id) (byId[e.id] = byId[e.id] || []).push(e);
  const feastId = {};
  for (const f of year.feasts.filter(f => feastShown(f.level, cal.cfg.feast_detail || 'all'))) {
    if (f.id) (feastId[f.id] = feastId[f.id] || []).push({ day: f.day, title: String(f.name || '') });
  }
  const daysOf = dayKeyResolver(year, byId, feastId);
  // `{abc}` in a topic or sub-topic is the year of the three-year lectionary
  // (A, B or C), as a hymnal's index files a Sunday's hymns under "Year A".
  const abc = 'ABC'[fmod(year.year - 2025, 3)];
  for (const row of rows) {
    const hymnal = cell(row, 'hymnal').trim();
    const topic = cell(row, 'topic').trim().split('{abc}').join(abc);
    const sub = cell(row, 'subtopic').trim().split('{abc}').join(abc);
    const numbers = cell(row, 'numbers').trim();
    const when = cell(row, 'when').trim();
    if (!hymnal || !topic) continue;
    for (const [day] of daysOf(cell(row, 'day').trim())) {
      if (day < year.start || day > year.end) continue;
      if (when) {
        let ok;
        try { ok = year.ctx.holds(when, day); } catch (e) { ok = false; }
        if (!ok) continue;
      }
      const list = (out[day] = out[day] || []);
      if (!list.some(x => x.h === hymnal && x.t === topic && x.s === sub)) list.push({ h: hymnal, t: topic, s: sub, n: numbers });
    }
  }
  return out;
}

/** Where every day sits on the wheel, and what to say about it. */
function dayIndex(cal) {
  const days = {};
  const topics = hymnTopicsIndex(cal);
  const flat = s => String(s).split(/\s+/).filter(Boolean).join(' ');
  const low = s => flat(s).toLowerCase();
  cal.weeks.forEach((week, weekIndex) => {
    week.forEach((day, bandIndex) => {
      if (day === null) return;
      const titleEntries = cal.titles[day] || [];
      let feastEntries = cal.feasts[day] || [];
      if (cal.cfg.deduplicate_day_labels) {
        const spoken = new Set(titleEntries.map(e => low(e.text)));
        feastEntries = feastEntries.filter(e => !spoken.has(low(e.text)));
      }
      // The readout names the season the ring shows.  In the one-year series
      // some rows color days without naming them, so the name is looked for
      // among the rows that carry one.
      const period = cal.seasonPeriods.find(q => q.name && q.start <= day && day <= q.end)
                  || cal.seasonFor(day);
      const broad = cal.broadSeasons.find(b => b.start <= day && day <= b.end);
      const color = cal.colorFor(day);
      days[iso(day)] = {
        w: weekIndex, b: bandIndex,
        t: titleEntries.map(e => flat(e.text)), f: feastEntries.map(e => flat(e.text)),
        // The whole names, where the cell carries a short one.
        T: titleEntries.map(e => flat(e.fullName || e.text)),
        F: feastEntries.map(e => flat(e.fullName || e.text)),
        // Where to read about each of them (feasts.csv `link`), if anywhere.
        L: feastEntries.map(e => e.link || ''),
        // A weekday without a name of its own: named from its Sunday.
        W: titleEntries.length ? '' : weekdayTitle(cal, day),
        // Hymnal topics for the day (hymnTopicsIndex), if any.
        H: topics[day] || [],
        i: (cal.icons[day] || []).filter(k => cal.iconDefs[k]),
        s: period ? period.name : '', B: broad ? broad.name : '',
        // The picture its season shows when the middle follows the season
        // (season_art.csv), or '' for the church's own.
        A: cal.seasonArtOn(day),
        c: color.name, fill: color.fill, a: color.alt || '',
      };
    });
  });
  return days;
}

/** WCAG relative luminance of a #rrggbb color (church_year_image.py: _luminance). */
function luminance(color) {
  const h = String(color || '').trim().replace(/^#/, '');
  if (h.length !== 6) return 1.0;
  let out = 0.0;
  for (const [weight, i] of [[0.2126, 0], [0.7152, 2], [0.0722, 4]]) {
    let c = parseInt(h.slice(i, i + 2), 16) / 255.0;
    c = c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    out += weight * c;
  }
  return out;
}

/** A fill on which black and white text both reach 3:1 (church_year_image.py: is_mid_tone). */
function isMidTone(fill) {
  const lum = luminance(fill);
  return (lum + 0.05) / 0.05 >= 3.0 && 1.05 / (lum + 0.05) >= 3.0;
}

/** A strong red: hue within 20 degrees of red, well saturated (church_year_image.py: is_red). */
function isRed(fill) {
  const h = String(fill || '').trim().replace(/^#/, '');
  if (h.length !== 6) return false;
  const r = parseInt(h.slice(0, 2), 16), g = parseInt(h.slice(2, 4), 16), b = parseInt(h.slice(4, 6), 16);
  const hi = Math.max(r, g, b), lo = Math.min(r, g, b);
  if (hi === 0 || (hi - lo) / hi < 0.5 || r !== hi) return false;
  const hue = 60.0 * (g - b) / (hi - lo);
  return hue >= -20.0 && hue <= 20.0;
}

/** Colors with the text on mid-tone fills set by mid_text (church_year_image.py: with_mid_text). */
function withMidText(colors, rule) {
  rule = String(rule || 'as-set').trim().toLowerCase();
  if (rule !== 'dark' && rule !== 'light' && rule !== 'dark-reds') return colors;
  const text = rule === 'light' ? '#ffffff' : '#000000';
  const out = {};
  for (const k in colors) {
    const c = colors[k];
    const wanted = isMidTone(c.fill) && (rule !== 'dark-reds' || isRed(c.fill));
    out[k] = wanted ? Object.assign({}, c, { text: text }) : c;
  }
  return out;
}

/** Black or white, whichever reads better on a fill. */
function readableText(fill) {
  const lum = luminance(fill);
  return (lum + 0.05) / 0.05 >= 1.05 / (lum + 0.05) ? '#000000' : '#ffffff';
}

/** The contrast ratio of two #rrggbb colors. */
function contrast(a, b) {
  const x = luminance(a), y = luminance(b);
  return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
}

/**
 * Colors with some fills replaced (the page's Colors menu): name -> #rrggbb.
 * The text keeps its color while it still reads (4.5:1); otherwise it turns
 * black or white, whichever reads better.
 */
function withOverrides(colors, fills) {
  if (!fills) return colors;
  const out = Object.assign({}, colors);
  for (const k in fills) {
    const c = out[k];
    if (!c || !/^#[0-9a-f]{6}$/i.test(fills[k])) continue;
    const text = contrast(fills[k], c.text) >= 4.5 ? c.text : readableText(fills[k]);
    out[k] = Object.assign({}, c, { fill: fills[k].toLowerCase(), text: text });
  }
  return out;
}

/** The colors this year's cells are painted in, tops and lower halves, in palette order. */
function colorsUsed(cal) {
  const used = {};
  for (const week of cal.weeks) for (const day of week) {
    if (day === null) continue;
    used[cal.colorFor(day).name] = true;
    const b = cal.bottomColorFor(day);
    if (b) used[b.name] = true;
  }
  return Object.keys(cal.colors).filter(k => used[k])
    .map(k => ({ name: k, fill: cal.colors[k].fill, text: cal.colors[k].text }));
}

/**
 * Draw a church year.  Returns the markup split into the part that turns and
 * the artwork that stays put, along with the day index and the geometry the
 * page needs to place its highlight.
 */
/** Calendar options from what the page or the verifier asks for. */
function calendarOptions(opts) {
  return {
    year: opts.year != null ? opts.year : opts.adventYear,
    tradition: opts.tradition || opts.lectionary, subcalendars: opts.subcalendars || [],
    latinNames: opts.latinNames, calendar: opts.calendar, paschalion: opts.paschalion,
    feastDetail: opts.feastDetail, hiddenRings: opts.hiddenRings, art: opts.art,
    artDate: opts.artDate,
    midText: opts.midText, yearLine: opts.yearLine, colorOverrides: opts.colorOverrides,
  };
}

function build(data, options) {
  const opts = options || {};
  const cal = new Calendar(data, calendarOptions(opts));
  const renderer = new Renderer(cal);
  const pieces = renderer.renderRings();
  const cfg = cal.cfg;
  const weekRing = cal.rings.find(r => r.kind === 'days' && r.enabled);

  const out = {
    turning: pieces.filter(p => p[0].kind !== 'center').map(p => p[1]).join(''),
    center: pieces.filter(p => p[0].kind === 'center').map(p => p[1]).join(''),
    days: dayIndex(cal),
    warnings: cal.warnings,
    label: spanName(yearOf(cal.cy.start), yearOf(cal.cy.end)),
    geometry: {
      cx: cfg.cx, cy: cfg.cy, startAngle: cfg.start_angle,
      anglePerWeek: cal.anglePerWeek, bands: cfg.day_bands,
      rInner: weekRing.rInner, rOuter: weekRing.rOuter,
      width: cfg.width, height: cfg.height,
      start: cfg.church_year_start, end: cfg.church_year_end,
      // The center artwork is kept out of the turning group and so is drawn
      // only when it changes; closing the gap left by a hidden ring resizes
      // it, which is what this is here to let the page notice.
      centerRadius: (cal.rings.find(r => r.kind === 'center') || {}).rOuter || 0,
    },
    rings: cal.rings.filter(r => r.enabled).map(r => ({ key: r.key, kind: r.kind,
                                                         fill: r.fill, text: r.textColor,
                                                         labeled: r.labelMode !== 'none' })),
    palette: colorsUsed(cal),
    emptyFill: cfg.empty_cell_fill,
    calendar: cal.cy.calendar,
    calendarLabel: cal.cy.reckoning.label,
    paschalion: cal.cy.paschalion,
    tradition: cal.tradition.key,
    subcalendars: cal.source.chosen.slice(),
    art: cal.art,
    readings: readingsIndex(cal),
  };
  // The calendar itself, for the page's editor (which rows made the day).
  Object.defineProperty(out, 'cal', { value: cal, enumerable: false });
  return out;
}

// ---------------------------------------------------------------------------
// Readings (page only: they are listed under the day's name, not drawn)
// ---------------------------------------------------------------------------

/** What the page calls each kind of reading, unless the tradition renames it. */
const READING_LABELS = {
  ot: 'Old Testament', ot2: 'Old Testament', ot_opt: 'Old Testament (additional)',
  psalm: 'Psalm', psalm_morning: 'Psalm (morning)', psalm_evening: 'Psalm (evening)',
  epistle: 'Epistle', gospel: 'Gospel', nt: 'New Testament',
  nt_opt: 'New Testament (additional)', introit: 'Introit', gradual: 'Gradual', verse: 'Verse',
  procession: 'Procession', morning: 'Morning', evening: 'Evening',
  first: 'First Lesson', second: 'Second Lesson',
  ot_s: 'Old Testament (semicontinuous)', psalm_s: 'Psalm (semicontinuous)',
  ot_c: 'Old Testament (complementary)', psalm_c: 'Psalm (complementary)',
  nt_gospel: 'New Testament (Gospels)', nt_epistle: 'New Testament (Epistles)',
  sermon: 'Sermon Text', story: 'Story Text', lesson: 'Lesson', apocrypha: 'Apocrypha',
  confessions: 'Lutheran Confessions',
};

/** Words of the date language that are not row ids. */
const RULE_WORDS = ['easter', 'prev_easter', 'start', 'end', 'next_start', 'half_end'];

/**
 * The kinds of set a day's readings fall into, in the order the page's
 * Readings boxes list them (lectionary.py: READING_CATEGORIES): the day's own
 * propers; a feast's or festival's; another day kept by its date or a date
 * rule that the calendar has no row for (Ember and Rogation Days,
 * Thanksgiving and national days, the Byzantine Saturdays before and after a
 * feast); a daily or weekday lectionary; the additional readings a daily
 * lectionary offers beside its own (LSB's, printed in italics, for reading
 * more of the Bible); a table of psalms for daily prayer (LSB's, morning and
 * evening by season and weekday); a plan of Bible reading kept by the calendar year
 * rather than the church year (Reading the Word of God); and the lessons of
 * the Office (Morning and Evening Prayer, Matins, a second or third service).
 */
const READING_CATEGORIES = ['day', 'feasts', 'dated', 'daily', 'additional', 'psalms', 'plan', 'office'];
const OFFICE_TITLE = /\b(Morning|Evening) Prayer\b|\bLessons\b|\bMatins\b|\bVespers\b|\bMidnight Office\b|\bCompline\b|\bEvensong\b|\b(Second|Third) Service\b/;
/**
 * The hours of the Office in the order of the day (lectionary.py:
 * OFFICE_HOURS): a day's sets of the Office are listed by the hour they are
 * read at, Matins before Vespers and Compline last.
 */
const OFFICE_HOURS = [
  [/\b(Midnight|Nocturns?)\b/, 0],
  [/\b(Matins|Mattins|Lauds|Orthros|Morning)\b/, 1],
  [/\b(Prime|Terce|Sext|None|Midday|Noonday)\b/, 2],
  [/\b(Vespers|Evening|Evensong)\b/, 4],
  [/\bCompline\b/, 5],
];
/** Where a set falls in the day: an Office's by its hour, the rest at 3. */
function officeHour(group) {
  if (group.category !== 'office') return 3;
  const hit = OFFICE_HOURS.find(([re]) => re.test(group.title));
  return hit ? hit[1] : 3;
}
const DAILY_TITLE = /\bDaily\b/;
const ADDITIONAL_TITLE = /\bAdditional Readings?\b/;
const PSALMS_TITLE = /^Psalms\b/;
/**
 * A shared reading plan (data/readings/plan-*.csv): its rows are keyed
 * `plan:N`, the Nth day of the calendar year that none of its other rows (its
 * festivals) take, and its `cycle` is the year a cycle was first read.
 */
const PLAN_FILE = /^plan-/;
const PLAN_KEY = /^plan:(\d+)$/;
/** A shared lectionary of this name is a daily or weekday one throughout. */
const DAILY_FILE = /-(daily|weekday)$/;
/**
 * A title of a day kept by its date rather than a saint's or a feast's: a
 * set of one keyed to a month and day is not taken for a feast's.
 */
const DATED_TITLE = /\b(Ember|Rogation|Independence|Dominion|Remembrance|National|Founders)\b|\bThanksgiving Day\b|\bNew Year's Day\b|Gedenkens|Samefolkets|^\d+\. mai$|Nyttårsaften/;
/** A day named by the feast it comes before or after ("Saturday before Theophany") is not that feast's day. */
const RELATIVE_TITLE = /^(Saturday|Sunday) (before|after) /;
/** Words that say nothing about which saint or feast a title names. */
const FEAST_STOP = new Set(('st sts ss saint saints the of and day a an in on to for our lord apostle apostles '
  + 'evangelist martyr martyrs bishop blessed virgin feast festival holy jesus christ '
  + 'der die des tag und von').split(' '));

function titleWords(text) {
  const plain = String(text || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  return (plain.match(/[a-z0-9]+/g) || []).filter(w => w.length > 1 && !FEAST_STOP.has(w));
}

/**
 * Whether a set's title names this feast: they share a word that is not a
 * saint's or a feast's common one.  What follows a ": " in the title is the
 * service (lectionary.py: same_feast).
 */
function sameFeast(title, name) {
  const a = titleWords(String(title).split(': ')[0]), b = titleWords(name);
  return a.some(x => b.some(y => x === y
    || (x.length >= 5 && y.length >= 5 && (x.indexOf(y) >= 0 || y.indexOf(x) >= 0))));
}

/**
 * What a folder's readings are tied to, worked out once for each Source
 * (lectionary.py: ReadingInfo): the days.csv ids and titles, and the
 * feasts.csv ids and names by date -- every subcalendar's too, chosen or not,
 * so that a feast left off with its calendar takes its readings.
 */
function readingInfo(source) {
  if (source.readingInfo) return source.readingInfo;
  const v = source.tradition.variant;
  const dayIds = new Set(source.days.map(r => cell(r, 'id')).filter(Boolean));
  const dayTitles = source.days.map(r => cell(r, 'title')).filter(Boolean);
  let feasts = source.feasts.slice();
  for (const entry of source.subcalendarList || []) {
    feasts = feasts.concat((entry.rows || []).filter(r => variantMatches(cell(r, 'variant'), v)
                                                     && !(cell(r, 'title') || cell(r, 'from'))));
  }
  const feastIds = new Set(feasts.map(r => cell(r, 'id')).filter(Boolean));
  const byDate = {};
  for (const r of feasts) {
    if (cell(r, 'date') && cell(r, 'name')) (byDate[cell(r, 'date').trim()] = byDate[cell(r, 'date').trim()] || []).push(cell(r, 'name'));
  }
  const feastNames = [].concat(...Object.keys(byDate).map(d => byDate[d]));
  const sameWords = (a, b) => a.length === b.length && a.every(w => b.indexOf(w) >= 0)
    && b.every(w => a.indexOf(w) >= 0);
  const dayWords = dayTitles.map(t => Array.from(new Set(titleWords(t))));
  // The days.csv titles of every variant of the folder: one that keeps
  // another language's names may read a sibling's English sets.
  const folderDayTitles = (source.folderDays || []).map(r => cell(r, 'title')).filter(Boolean);
  // The days and offsets the day's own (untitled) propers are keyed to: a
  // titled set beside them is another of that day's ("Christmas Dawn
  // (Proper II)", "Three-year series").
  const untitled = new Set(source.readings.filter(r => !cell(r, 'title'))
    .map(r => cell(r, 'day').trim() + '\n' + (toInt(cell(r, 'offset'), 0) || 0)));
  // The titles of sets keyed to a days.csv day: a heading of the day's
  // propers ("Three-year series"), wherever it is keyed.
  const daySetTitles = new Set(source.readings.filter(r => cell(r, 'title')
    && dayIds.has(cell(r, 'day').trim().split(':')[0])).map(r => cell(r, 'title')));
  // Whether a title names one of the calendar's days.csv days: in the same
  // words, or (unless it is a day before or after one) sharing one.
  const namesDay = title => {
    const words = Array.from(new Set(titleWords(String(title).split(': ')[0])));
    if (dayWords.some(w => sameWords(words, w))) return true;
    return !RELATIVE_TITLE.test(title) && dayTitles.some(t => sameFeast(title, t));
  };
  const tiedMemo = {}, catMemo = {};
  const info = {
    isFeastId: key => /^[A-Za-z_]\w*$/.test(key) && !dayIds.has(key) && feastIds.has(key),
    // The feasts a titled set keyed to a date (not a feast's id) belongs to:
    // those of its title kept on that same date.
    tied: (key, title) => {
      const k = key + '\n' + title;
      if (!(k in tiedMemo)) tiedMemo[k] = title ? (byDate[key] || []).filter(n => sameFeast(title, n)) : [];
      return tiedMemo[k];
    },
    category: row => {
      const key = cell(row, 'day').trim(), title = cell(row, 'title'), file = cell(row, '_file');
      const offset = toInt(cell(row, 'offset'), 0) || 0;
      const k = key + '\n' + offset + '\n' + title + '\n' + file;
      if (!(k in catMemo)) {
        const m = /^([A-Za-z_]\w*)(?::\d+)?$/.exec(key);
        const relative = RELATIVE_TITLE.test(title);
        let cat;
        if (PLAN_FILE.test(file)) cat = 'plan';
        else if (OFFICE_TITLE.test(title)) cat = 'office';
        else if (ADDITIONAL_TITLE.test(title)) cat = 'additional';
        else if (PSALMS_TITLE.test(title)) cat = 'psalms';
        else if (DAILY_TITLE.test(title) || DAILY_FILE.test(file)) cat = 'daily';
        else if (info.isFeastId(key) || (title && info.tied(key, title).length)) cat = 'feasts';
        else if (!title || (m && RULE_WORDS.indexOf(m[1].toLowerCase()) < 0)) cat = 'day';
        else if (untitled.has(key + '\n' + offset) || daySetTitles.has(title) || namesDay(title)) cat = 'day';
        else if (DATED_TITLE.test(title)) cat = 'dated';
        else if (/^\d\d-\d\d$/.test(key)) cat = 'feasts';
        else if (!relative && feastNames.some(n => sameFeast(title, n))) cat = 'feasts';
        else if (!relative && folderDayTitles.some(t => sameFeast(title, t))) cat = 'day';
        else cat = 'dated';
        catMemo[k] = cat;
      }
      return catMemo[k];
    },
  };
  source.readingInfo = info;
  return info;
}

/** The kinds of set a church's readings have, in READING_CATEGORIES order. */
function readingCategories(data, key) {
  const source = new Source(data, findTradition(data, key), []);
  const info = readingInfo(source);
  const found = new Set(source.readings.map(r => info.category(r)));
  return READING_CATEGORIES.filter(c => found.has(c));
}

/**
 * Every day's readings: iso date -> [{title, category, items: [{kind, label,
 * reading}]}].  A row's `day` is a days.csv id (with `:n` for the nth of a
 * run) or a date rule; `offset` moves it, `when` and `cycle` keep it only in
 * some years.  A feast the wheel does not show that day -- left off by the
 * Feasts setting, outranked, moved, or of a calendar not laid over it --
 * takes its readings with it.
 */
/**
 * What a `day` key of readings.csv (or hymn_topics.csv) names in this year:
 * [day, the title of the row it is keyed to] for each day.  A days.csv id
 * (`advent`, `advent:2`), a feasts.csv id kept that year, a month and day
 * (both, where it falls twice), or a date rule.
 */
function dayKeyResolver(year, byId, feastId) {
  const ctx = year.ctx;
  const memo = {};
  return key => {
    if (Object.prototype.hasOwnProperty.call(memo, key)) return memo[key];
    let days = [];
    const m = /^([A-Za-z_]\w*)(?::(\d+))?$/.exec(key);
    const md = /^(\d\d)-(\d\d)$/.exec(key);
    if (m && RULE_WORDS.indexOf(m[1].toLowerCase()) < 0) {
      const n = m[2] === undefined ? null : parseInt(m[2], 10);
      days = (byId[m[1]] || []).filter(e => n === null || e.number === n)
        .map(e => [e.day, String(e.title || '').split('\n')[0]]);
      if (!days.length && n === null) days = (feastId[m[1]] || []).map(e => [e.day, e.title.split('\n')[0]]);
    } else if (md) {
      // A month and day may fall twice in a church year that starts late
      // in November; feastRows finds both, and so does this.
      const month = +md[1], dom = +md[2];
      for (let y = ctx.yearOf(year.start); y <= ctx.yearOf(year.end); y++) {
        if (year.reckoning.valid(y, month, dom)) days.push([year.reckoning.toDay(y, month, dom), '']);
      }
    } else {
      try { days = [[ctx.eval(key), '']]; } catch (e) { days = []; }
    }
    memo[key] = days;
    return days;
  };
}

// Prayer Book psalters against the English verse numbers
// (lib/versification.py: PSALTERS, psalter_citation): psalm: psalter verse =
// the English verse(s) it holds.  A church whose own readings cite its
// psalter's verses names it in its `psalter` setting; their links open the
// English ones.
const PSALTERS = {
  'acna-2019': (
    '1:4=3|5=4|6=5|7=6; 5:10=9|11=10|12=11|13=12; ' +
    '7:10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17; ' +
    '10:10=9|11=10|12=11|13=12|14=13|15=14|16=14|17=15|18=16|19=17|20=18; 11:5=4|6=5|7=6|8=7; ' +
    '12:7=6|8=7|9=8; 14:2=1|3=2|4=3|5=4|6=5|7=6|8=7; 15:5=4|6=5|7=5; ' +
    '16:5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11; 17:15=14|16=15; ' +
    '18:1=1-2|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22|24=23|25=24|26=25|27=26|28=27|29=28|30=29|31=30|32=31|33=32|34=33|35=34|36=35|37=36|38=37|39=38|40=39|41=40|42=41|43=42|44=43|45=43|46=44|47=45|48=46|49=47|50=48|51=49|52=50; ' +
    '25:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8|8=9|9=10|10=11|11=12|12=13|13=14|14=15|15=16|16=17|17=18|18=19|19=20|20=21|21=22; ' +
    '27:5=4|6=5|7=6|8=6|9=7|10=8|11=9|12=9|13=10|14=11|15=12|16=13|17=14; ' +
    '28:5=4|6=5|7=6|8=7|9=8|10=9; 29:7=7-8|8=9|9=10|10=11; 30:10=9|11=10|12=11|13=12; ' +
    '31:3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=10|13=11|14=12|15=13|16=13|17=14-15|18=16|19=17|20=18|21=19|22=20|23=21|24=22|25=22|26=23|27=24; ' +
    '32:6=5|7=6|8=7|9=8|10=9|11=10|12=11; ' +
    '33:13=13-14|14=15|15=16|16=17|17=18|18=19|19=20|20=21|21=21-22; ' +
    '37:29=28|30=29|31=30|32=31|33=32|34=33|35=34|36=35|37=36|38=37|39=38|40=39|41=40; ' +
    '39:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=12|15=13; ' +
    '40:4=3|5=4|6=5|7=5|8=6|9=6|10=7-8|11=9|12=10|13=10|14=11|15=12|16=13|17=14|18=15|19=16|20=17|21=17; ' +
    '42:5=4|6=5|7=5|8=6|9=7|10=8|11=9|12=10|13=10|14=11|15=11; 43:6=5; ' +
    '49:15=14|16=15|17=16|18=17|19=18|20=19|21=20; 50:22=21|23=22|24=23; ' +
    '52:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9; 53:2=1|3=2|4=3|5=4|6=5|7=5|8=6|9=6; ' +
    '55:13=12|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22|24=23|25=23; ' +
    '63:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11; 65:10=9|11=10|12=11|13=12|14=13; ' +
    '66:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8|8=9|9=10|10=11|11=12|12=13|13=14|14=15|15=16|16=17|17=18|18=19|19=20; ' +
    '68:31=30|32=31|33=32|34=33|35=34|36=35; ' +
    '69:5=4-5|14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22|24=23|25=24|26=25|27=26|28=27|29=28|30=29|31=30|32=31|33=32|34=33|35=34|36=35|37=36; ' +
    '70:6=5; ' +
    '71:10=10-11|11=12|12=13|13=14|14=15|15=16|16=17|17=18|18=19|19=20|20=21|21=22|22=23|23=24; ' +
    '72:19=19-20; 75:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=8|11=9|12=10; ' +
    '78:6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22|24=23|25=24|26=25|27=26|28=27|29=28|30=29|31=30-31|39=38|40=39|41=40|42=41|43=42|44=43|45=44|46=45|47=46|48=47|49=48|50=49|51=50|52=51|53=52|54=53|55=54|56=55|57=56|58=57|59=58|60=59|61=60|62=61|63=62|64=63|65=64|66=65|67=66|68=67|69=68|70=69|71=70|72=71|73=72; ' +
    '79:11=10|12=11|13=12|14=13; 84:11=10|12=11|13=12; ' +
    '89:32=32-33|33=34|34=35|35=36|36=37|37=38|38=39|39=40|40=41|41=42|42=43|43=44|44=45|45=46|46=47|47=48|48=49|49=50|50=51|51=52; ' +
    '92:7=7-8|8=9|9=10|10=11|11=12|12=13|13=14|14=15; 93:2=1|3=2|4=3|5=4|6=5; ' +
    '98:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8-9|10=9; 100:1=1-2|2=3|3=4|4=5; ' +
    '101:3=2|4=3|5=4|6=5|7=5|8=6|9=6|10=7|11=8; ' +
    '105:12=11-12|34=34-35|35=36|36=37|37=38|38=39|39=40|40=41|41=42|42=43|43=44|44=45; ' +
    '106:36=36-37|37=38|38=39|39=40|40=41|41=42|42=43|43=44|44=45-46|45=47|46=48; ' +
    '109:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8|8=9|9=10|10=11|11=12|12=13|13=14|14=15|15=16|16=17|17=18|18=19|19=20|20=21|21=22|22=23|23=24|24=25|25=26|26=27|27=28|28=29|29=30|30=31; ' +
    '113:5=5-6|6=7|7=8|8=9; 116:10=10-11|11=12|12=13|13=14-15|14=16|15=17|16=18-19; ' +
    '120:3=3-4|4=5|5=6|6=7; 123:3=2|4=3|5=4; 124:1=1-2|2=3|3=4-5|4=6|5=7|6=8; ' +
    '126:3=2|4=3|5=4|6=5|7=6; 127:2=1|3=2|4=3|5=4|6=5; 128:4=3|5=4|6=5|7=6; 131:2=1|3=2|4=3; ' +
    '132:12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18; 133:4=3; 134:2=1|3=2|4=3; 136:27=26; ' +
    '141:6=5|7=6|8=7|9=8|10=9|11=10; 142:5=4|6=5|7=6|8=6|9=7; 146:1=1-2|8=7|9=8|10=9|11=10'),
  'american-1928': (
    '1:4=3|5=4|6=5|7=6; 4:7=6|8=7|9=8; 5:10=9|11=10|12=11|13=12; ' +
    '7:3=2-3|10=9|11=10|12=11|13=12|14=13|15=14|16=15-16|17=16|18=17; ' +
    '10:6=6-7|9=8-9|10=9|11=10|12=11|13=12|14=13|15=14|16=14|17=15|18=16|19=17|20=18; ' +
    '11:5=4|6=5|7=6|8=7; 12:6=5|7=6|8=7|9=8; 14:2=1|3=2|4=3|5=4|6=5|7=6|8=7; 15:5=4|6=5|7=5; ' +
    '16:5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11; 17:5=4-5|6=5-6|15=14|16=15; ' +
    '18:1=1-2|6=5-6|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22-23|24=23|25=24|26=25|27=26|28=27|29=28|30=29|31=30|32=31|33=32|34=33|35=34|36=35|37=36|38=37|39=38|40=39|41=40|42=41|43=42|44=43|45=44|46=45|47=46|48=47|49=48|50=49|51=50; ' +
    '22:17=16-17|30=29|31=30|32=31; ' +
    '25:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8|8=9-10|9=10-11|10=11|11=12|12=13|13=14|14=15|15=16|16=17|17=18|18=19|19=20|20=21|21=22; ' +
    '27:7=6|8=7|9=8|10=9|11=9|12=10|13=11|14=12|15=13|16=14; 28:5=4|6=5|7=6|8=7|9=8|10=9; ' +
    '29:7=7-8|8=9|9=10|10=11; 30:6=6-7|8=7-8|10=9|11=10|12=11|13=12; ' +
    '31:3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=10|13=11|14=12|15=13|16=13|17=15|18=16|19=17|20=18|21=18-19|22=20|23=21|24=22|25=22|26=23|27=24; ' +
    '32:5=4-5|6=5|7=6|8=7|9=8|10=9|11=10|12=11; ' +
    '33:13=13-14|14=15|15=16|16=17|17=17-18|18=19|19=20|20=21|21=22; ' +
    '37:13=13-14|20=20-21|29=28|30=29|31=30|32=31|33=32|34=33|35=34-35|36=35|37=36|38=37|39=38|40=39|41=40; ' +
    '39:2=1|3=2|4=3|5=4|6=5|7=6|8=6-7|9=8|10=9|11=10|12=11|13=12|14=12|15=13; ' +
    '40:4=3|5=4|6=5|7=5|8=6|9=6|10=7-8|11=9|12=10|13=10|14=11|15=12|16=13|17=14|18=14-15|19=16|20=17|21=17; ' +
    '42:5=4|6=5|7=5|8=6|9=7|10=8|11=9|12=10|13=10|14=11|15=11; 43:6=5; ' +
    '48:3=4|4=5|5=6|6=7|7=8|8=9|9=10|10=11|11=12|12=13|13=14; ' +
    '52:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9; 53:2=1|3=2|4=3|5=4|6=5|7=6|8=6; ' +
    '55:12=11-12|13=12|14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22|24=23|25=23; ' +
    '57:4=3-4|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11; ' +
    '63:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11; 65:10=9|11=10|12=11|13=12|14=13; ' +
    '66:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8|8=9|9=9-10|10=11|11=12|12=13-14|13=15|14=16|15=17|16=18|17=19|18=20; ' +
    '69:5=4-5|14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22|24=23|25=24|26=25|27=26|28=27|29=28|30=29|31=30|32=31|33=32|34=33|35=34|36=35|37=36; ' +
    '70:5=4-5|6=5; ' +
    '71:1=1-2|2=3|3=4|4=4-5|5=6|6=7|7=8|8=9|9=10|10=11|11=12|12=13|13=14|14=15|15=16|16=17|17=18|18=19|19=20|20=21|21=22|22=23|23=24; ' +
    '72:8=7-8|19=19-20; ' +
    '74:3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22|24=23; ' +
    '75:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=8|11=9|12=9-10; ' +
    '78:6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18|20=19-20|21=20|22=21|23=22|24=23|25=24|26=25|27=26|28=27|29=28|30=29-30|39=38|40=39|41=40|42=41|43=42-43|44=43|45=44|46=45|47=46|48=47|49=48|50=49|51=50|52=51|53=52|54=53|55=54|56=55|57=56|58=57|59=58|60=59|61=60|62=61|63=62|64=63|65=64|66=65|67=66|68=67|69=68|70=69|71=70|72=71|73=72; ' +
    '79:11=10|12=11|13=12|14=13; 81:8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16; ' +
    '84:7=7-8|11=10|12=11|13=12; ' +
    '89:5=4-5|6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=15-16|18=17|19=18|20=19|21=20|22=21|23=22|24=23|25=24|26=25|27=26|28=27|29=28|30=29|31=30|32=31-32|34=34-35|35=36|36=37|37=38|38=39|39=40|40=41|41=42|42=43|43=44|44=45|45=46|46=47|47=48|48=49|49=50|50=51|51=52; ' +
    '92:8=9|9=10|10=11|11=12|12=13|13=14|14=15; 93:2=1|3=2|4=3|5=4|6=5; ' +
    '98:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9; 100:1=1-2|2=3|3=4|4=5; ' +
    '101:3=2|4=3|5=4|6=5|7=5|8=6|9=7|10=7|11=8; 104:15=14-15|26=25-26|36=35; ' +
    '105:33=33-34|34=34-35|35=36|36=37|37=38|38=39|39=40|40=41|41=42|42=43|43=44|44=45; ' +
    '106:36=36-37|37=38|38=39|39=40|40=41|41=42|42=43|43=44|44=45-46|45=47|46=48; ' +
    '109:1=1-2|2=2-3|3=4|4=5|5=6|6=7|7=8|8=9|9=10|10=11|11=12|12=13|13=14|14=15-16|15=16|16=17|17=18|18=19|19=20|20=21|21=22|22=23|23=24|24=24-25|25=26|26=27|27=28|28=29|29=30|30=31; ' +
    '113:5=5-6|6=7|7=8-9|8=9; 116:4=3-4|10=10-11|11=12|12=13|13=14-15|14=16|15=17|16=18-19; ' +
    '120:3=3-4|4=5|5=6|6=7; 124:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8; 126:3=2|4=3|5=4|6=5|7=6; ' +
    '127:2=1|3=2|4=3|5=4|6=5; 128:4=3|5=4|6=5|7=6; 131:2=1|3=2|4=3; ' +
    '132:11=10-11|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18; 133:4=3; 134:2=1|3=2|4=3; ' +
    '136:27=26; 141:1=1-2|6=5|7=6|8=7|9=8|10=9|11=10; 142:5=4|6=5|7=6|8=6|9=7; 148:12=12-13|13=14'),
  'canada-1962': (
    '1:4=3|5=4|6=5|7=6; 5:10=9|11=9|12=10|13=11|14=12; ' +
    '7:3=2-3|10=9|11=10|12=11|13=12|14=13|15=14|16=15-16|17=16|18=17; ' +
    '10:6=6-7|9=8-9|10=9|11=10|12=11|13=12|14=13|15=14|16=14|17=15|18=16|19=17|20=18; ' +
    '12:6=5|7=6|8=7|9=8; 14:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=7; 15:5=4|6=5|7=5; ' +
    '16:5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11; 17:15=14|16=15; ' +
    '18:6=5-6|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=15|18=16|19=16-17|20=18|21=19|22=20|23=21|24=22|25=23|26=24|27=25|28=26|29=27|30=28|31=29|32=30-31|33=32|34=32-33|35=33|36=34|37=35|38=36|39=37|40=38|41=39|42=40|43=41|44=42|45=43|46=44|47=45|48=46|49=47|50=48-49|51=50|52=50; ' +
    '27:7=6|8=7|9=8-9|10=9|11=9|12=10|13=11|14=12|15=13|16=14; 28:5=4|6=5|7=6|8=7|9=8|10=9; ' +
    '29:7=7-8|8=9|9=10|10=11; 30:6=6-7|8=7-8|10=9|11=10|12=11|13=12; ' +
    '31:3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=10|13=11|14=11|15=12|16=13|17=13|18=14-15|19=16|20=17|21=18|22=19|23=20|24=21|25=22|26=22|27=23|28=24; ' +
    '32:5=4-5|6=5|7=6|8=7|9=8|10=9|11=10|12=11; ' +
    '37:2=1-2|13=13-14|20=20-21|29=28|30=29|31=30|32=31|33=32|34=33|35=34-35|36=35|37=36|38=37|39=38|40=39|41=40; ' +
    '39:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=12|15=13; ' +
    '40:4=3|5=4|6=5|7=5|8=6|9=6-7|10=7-8|11=9|12=10|13=10|14=11|15=12|16=12|17=13|18=14|19=15|20=16|21=17|22=17; ' +
    '42:5=4|6=5|7=5|8=6|9=7|10=8|11=9|12=10|13=11|14=11; 43:6=5; ' +
    '44:4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22|24=23|25=24|26=25|27=26; ' +
    '46:5=4|6=5|7=6|8=7|9=8-9|10=9|11=10|12=11; 47:10=9; ' +
    '48:3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14; ' +
    '49:15=14|16=15|17=16|18=17|19=18|20=19|21=20; 53:2=1|3=2|4=3|5=4|6=5|7=6|8=6; ' +
    '55:12=11-12|13=12|14=13|15=14|24=23; ' +
    '57:2=1|3=2|4=3|5=3-4|6=4|7=5|8=6|9=7-8|10=8|11=9|12=10|13=11; ' +
    '63:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11; ' +
    '65:5=4|6=5|7=6|8=7|9=8|10=9|11=9|12=10|13=11|14=12|15=13; ' +
    '66:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8|8=9|9=9-10|10=11|11=12|12=13|13=14|14=15|15=16|16=17|17=18|18=19|19=20; ' +
    '68:2=1-2|3=3-4|4=5|18=18-19|19=20|20=21-22|21=23-24|22=25|23=26|24=27|25=28|26=29|27=30|28=31|29=32|30=33|31=34|32=35; ' +
    '69:5=4-5|14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20-22|22=23-25|23=26-28|24=29|25=30-31|26=32|27=33|28=34|29=35|30=36; ' +
    '70:6=5; 72:17=16|18=17|19=17|20=18|21=19-20; ' +
    '75:2=1|3=2-3|4=3|5=4|6=5|7=6|8=7|9=8|10=8|11=9|12=9-10; ' +
    '78:2=1-2|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22|24=23|25=24|26=25|27=26|28=27|29=28|30=29|31=30-31|32=31|33=32|34=33|35=34|36=35|37=36|38=37|39=38|40=38|41=39|42=40|43=41|44=42-43|45=43|46=44|47=45|48=46|49=47|50=48|51=49|52=50|53=51|54=52|55=53|56=54|57=55|58=56|59=57|60=58|61=59|62=60|63=61|64=62|65=63|66=64|67=65|68=66|69=67|70=68|71=69|72=70|73=71|74=72; ' +
    '79:11=10|12=11|13=12|14=13; 84:7=7-8|11=10|12=11|13=12; ' +
    '88:4=3-4|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18; ' +
    '89:2=1-2|31=31-32|32=33|33=34|34=35|35=36|36=37|37=38|38=39|39=40|40=41|41=42|42=43|43=44|44=45|45=46|46=47|47=48|48=49|49=50|50=51|51=52; ' +
    '90:11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17; 93:2=1|3=1-2|4=3|5=4|6=5; ' +
    '98:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9; 100:1=1-2|2=3|3=4|4=5; ' +
    '101:3=2|4=3|5=4|6=5|7=5|8=6|9=6|10=7|11=8; ' +
    '104:2=1-2|15=14-15|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22|24=23|25=24|26=25|27=26|28=27|29=28|30=29|31=30|32=31|33=32|34=33|35=34|36=35; ' +
    '109:1=1-2|2=3-5|3=6-8|4=9-11|5=12-14|6=15-17|7=18-20|8=21-22|9=23-25|10=26|11=27|12=28|13=29|14=30|15=31; ' +
    '116:4=3-4|10=10-11|11=12|12=13|13=14|14=15|15=16|16=17|17=18|18=19; 120:3=3-4|4=5|5=6|6=7; ' +
    '123:3=2|4=3|5=4; 124:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8; 126:3=2|4=3|5=4|6=5|7=6; ' +
    '127:2=1|3=2|4=3|5=4|6=5; 128:4=3|5=4|6=5|7=6; 131:2=1|3=2|4=3; ' +
    '132:7=6-7|11=10-11|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18; 133:4=3; 134:2=1|3=2|4=3; ' +
    '137:6=6-8; 140:8=8-9|9=10-11|10=12|11=13; 141:4=4-5|7=7-8|8=9|9=10; ' +
    '142:1=1-2|2=2-3|5=4|6=5|7=6|8=6|9=7|10=7; ' +
    '145:14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21'),
  'bcp-1979': (
    '5:10=9|11=10|12=10|13=11|14=11|15=12; ' +
    '7:3=2-3|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17; ' +
    '8:2=1-2|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=8-9; 10:6=6-7|15=14|16=15|17=16|18=17|19=18; ' +
    '11:5=4|6=5|7=6|8=7; 15:5=4|6=5|7=5; 17:15=14|16=15; 21:10=9|11=10|12=11|13=12|14=12-13; ' +
    '22:17=17-18|18=19|19=20|20=21|21=22|22=23|23=24|24=25|25=26|26=27|27=28|28=29|29=29-30|30=31; ' +
    '25:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8|8=9|9=10|10=11|11=12|12=13|13=14|14=15|15=16|16=17|17=18|18=19|19=20|20=21|21=22; ' +
    '27:4=3|5=4|6=4|7=5|8=6|9=6|10=7|11=8|12=9|13=9|14=10|15=11|16=12|17=13|18=14; ' +
    '28:5=4|6=5|7=6|8=7|9=7|10=8|11=9; 30:6=5|7=6-7|8=7|9=8-9|10=9|11=10|12=11|13=12; ' +
    '32:5=4-5|6=5|7=6|8=7|9=8|10=9|11=10|12=11; ' +
    '37:8=7|9=8|10=9|11=10|12=11|13=12|14=13-14|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22|24=23|25=24|26=25|27=26|28=27|29=28|30=28|31=29|32=30|33=31|34=32|35=33|36=34|37=35|38=36|39=37|40=38|41=39|42=40; ' +
    '39:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=12|15=13; ' +
    '40:6=5|7=6|8=6|9=7-8|10=9|11=10|12=11|13=12|14=13|15=14|16=14-15|17=16|18=16-17|19=17; ' +
    '42:5=4|6=5|7=5|8=6|9=7|10=8|11=9|12=10|13=10|14=11|15=11; 43:6=5; ' +
    '45:5=4-5|6=5|7=6-7|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17; ' +
    '46:4=3|5=4|6=5|7=6|8=7|9=8-9|10=9|11=10|12=11; 47:10=9; ' +
    '48:6=6-7|7=8|8=9|9=10|10=11|11=12|12=13|13=14; 50:22=21|23=22|24=23; ' +
    '51:5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18|20=19; ' +
    '55:4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16-17|18=17|19=18|20=19|21=20|22=21|23=21|24=22|25=23|26=23; ' +
    '56:10=10-11|11=12|12=13; ' +
    '59:3=3-4|6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=13|16=14|17=15|18=16|19=16|20=17; ' +
    '62:5=4|6=5|7=6|8=7|9=8|10=9|11=9|12=10|13=11|14=12; 65:10=9|11=10|12=11|13=12|14=13; ' +
    '66:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8|8=9|9=10|10=11-12|11=12|12=13-14|13=15|14=16|15=17|16=18|17=19|18=20; ' +
    '68:31=30|32=31|33=32|34=33|35=34|36=35; ' +
    '69:3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=13|16=14|17=15|18=16|19=17|20=18|21=19|22=20|23=21|24=22|25=23|26=24|27=25|28=26|29=27|30=28|31=29|32=30|33=31|34=32|35=33|36=34|37=35|38=36; ' +
    '70:6=5; 72:19=19-20; 73:22=22-23|29=28; ' +
    '74:5=5-6|6=7|7=8|8=9|9=10|10=11|11=12|12=13|13=14|14=15|15=16|16=17|17=18|18=19|19=20|20=21|21=22|22=23; ' +
    '80:14=14-15|15=16|16=17|17=18|18=19; 87:1=1-2|2=3|3=4|4=5|5=6|6=7; ' +
    '88:2=2-3|4=3-4|6=5|7=6|8=7|9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=17-18; ' +
    '92:6=6-7|7=7-8|8=9|9=10|10=11|11=12|12=13|13=14|14=15; 93:2=1|3=1-2|4=3|5=4|6=5; ' +
    '98:2=1|3=2|4=3|5=4|6=5|7=6|8=7|9=8|10=9; 100:1=1-2|2=3|3=4|4=5; ' +
    '104:15=14-15|16=15|17=16|18=17|19=18|20=19|21=20|22=21|23=22|24=23|25=24|26=25|27=26|28=27|29=28|30=29|31=30|32=31|33=32|34=33|35=34|36=35|37=35; ' +
    '109:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8|8=9|9=10|10=11|11=12|12=13|13=14|14=15-16|15=16|16=17|17=18|18=19|19=20|20=21|21=22|22=23|23=24|24=25|25=26|26=27|27=28|28=29|29=30|30=31; ' +
    '113:5=5-6|6=7|7=8|8=9; ' +
    '116:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8|8=9|9=10-11|10=12|11=13|12=14|13=15|14=16|15=17|16=18|17=19; ' +
    '123:3=2|4=3-4|5=4; 126:3=2|4=3|5=4|6=5-6|7=6; 127:2=1|3=2|4=3|5=4|6=5; ' +
    '130:1=1-2|2=3|3=4|4=5|5=6|6=7|7=7-8; 131:2=1|3=2|4=3; ' +
    '132:7=6-7|11=10-11|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18; 133:3=2|4=3|5=3; 134:2=2-3; ' +
    '138:3=2|4=3|5=4|6=5|7=6|8=7|9=8; ' +
    '139:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8|8=9|9=9-10|10=11|11=12|12=13|13=14|14=15|15=16|16=17|17=18|18=19|19=20|20=21|21=22|22=23|23=24; ' +
    '144:3=2-3|11=10-11|12=11|13=12|14=13|15=14|16=15; ' +
    '145:14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20|22=21; ' +
    '146:1=1-2|2=3|3=4|4=5|5=6|6=7|7=8|8=9|9=10; ' +
    '147:9=8|10=9|11=10|12=11|13=12|14=13|15=14|16=15|17=16|18=17|19=18|20=19|21=20'),
};
const psalterTables = {};

/** The English verse of a psalter's: the first it holds, or with `end` the last. */
function psalterVerse(name, psalm, verse, end) {
  if (!psalterTables[name]) {
    const table = psalterTables[name] = {};
    for (const entry of PSALTERS[name].split(';')) {
      const [psalm, rows] = entry.trim().split(':');
      const verses = table[parseInt(psalm, 10)] = {};
      for (const row of rows.split('|')) {
        const [v, eng] = row.split('=');
        const [lo, hi] = eng.split('-');
        verses[parseInt(v, 10)] = [parseInt(lo, 10), parseInt(hi || lo, 10)];
      }
    }
  }
  const r = (psalterTables[name][psalm] || {})[verse] || [verse, verse];
  return end ? r[1] : r[0];
}

/** A citation's psalms from a psalter's verses into the English ones (versification.py: psalter_citation). */
function psalterCitation(citation, name) {
  const token = /((?:[1-4] )?(?:Song of Solomon|Wisdom of Solomon|[A-Z][a-z]+)) (?=\d)|(\d+)([a-c]?)(:)?/g;
  const out = [];
  let pos = 0, psalm = false, chapter = null, m;
  while ((m = token.exec(citation)) !== null) {
    const gap = citation.slice(pos, m.index);
    out.push(gap);
    pos = token.lastIndex;
    // After "; " or "–end" the next bare number is another psalm.
    if (gap.indexOf(';') >= 0 || gap.indexOf('end') >= 0) chapter = null;
    if (m[1]) { psalm = m[1] === 'Psalm' || m[1] === 'Psalms'; chapter = null; out.push(m[0]); continue; }
    const n = parseInt(m[2], 10);
    if (m[4] || !psalm || chapter === null) { if (m[4]) chapter = n; out.push(m[0]); continue; }
    const starts = /^\s*[–-]/.test(citation.slice(pos));
    const ends = /[–-]$/.test(out.join('').replace(/\s+$/, ''));
    const first = psalterVerse(name, chapter, n, false), last = psalterVerse(name, chapter, n, true);
    if (ends) out.push(last + m[3]);
    else if (starts || first === last) out.push(first + m[3]);
    else out.push(first + '–' + last);
  }
  out.push(citation.slice(pos));
  return out.join('');
}

function readingsIndex(cal) {
  const year = cal.year;
  const rows = cal.source.readings || [];
  const out = {};
  if (!rows.length) return out;
  const ctx = year.ctx;
  const cfg = year.settings;
  const psalter = String(cfg.psalter || '').trim();
  const detail = cal.cfg.feast_detail || 'all';
  const info = readingInfo(cal.source);
  const shown = year.feasts.filter(f => feastShown(f.level, detail));
  const shownNames = {};
  for (const f of shown) (shownNames[f.day] = shownNames[f.day] || []).push(String(f.name || ''));
  const dayTitles = {};
  for (const e of year.principal) {
    if (e.title) (dayTitles[e.day] = dayTitles[e.day] || []).push(String(e.title));
  }
  const labels = Object.assign({}, READING_LABELS);
  for (const part of String(cfg.reading_labels || '').split(';')) {
    const i = part.indexOf('=');
    if (i > 0) labels[part.slice(0, i).trim()] = part.slice(i + 1).trim();
  }
  // `reading_cycle`: abc (Year A = Advent 2025), or a cycle's names and the
  // year its first began ("I II III IV V VI 2018"), or `year` (a row's cycle
  // is the year its church year begins, for a church that chooses each
  // year's texts afresh); several cycles, kept side by side, are split by
  // `;`.  A row of any of this year's names is read.
  const cycles = new Set();
  for (const part of String(cfg.reading_cycle || '').split(';')) {
    const words = part.trim().split(/\s+/).filter(Boolean);
    if (words.length === 1 && words[0].toLowerCase() === 'abc') {
      cycles.add('ABC'[fmod(year.year - 2025, 3)]);
    } else if (words.length === 1 && words[0].toLowerCase() === 'year') {
      cycles.add(String(year.year));
    } else if (words.length > 2 && /^-?\d+$/.test(words[words.length - 1])) {
      const names = words.slice(0, -1).map(w => w.toUpperCase());
      cycles.add(names[fmod(year.year - parseInt(words[words.length - 1], 10), names.length)]);
    }
  }
  const byId = {};
  for (const e of year.principal) {
    if (!e.id) continue;
    (byId[e.id] = byId[e.id] || []).push(e);
  }
  // A feasts.csv row may be named too, on the day it is kept (after any
  // transfer), when no days.csv row has that id -- and only while the wheel
  // shows it.
  const feastId = {};
  for (const f of shown) {
    if (!f.id) continue;
    (feastId[f.id] = feastId[f.id] || []).push({ day: f.day, title: String(f.name || '') });
  }
  // Each `day` names one or more days: [day, the name of the row it is keyed
  // to (a days.csv row's own title, for headings), ...].
  // `reading_rotate` (ELHB): "after_epiphany 6 Morning and Evening Lessons"
  // -- the weeks of lessons a short run cannot hold are left out, a different
  // week each year in turn, so that over several years all are read.  The
  // rows of that title keyed to the run's nth week are moved to the Sunday
  // that reads them.
  const rot = String(cfg.reading_rotate || '').trim().split(/\s+/);
  // The run's id, and any other rows that take a Sunday of it (TLH's
  // Transfiguration): "after_epiphany|transfiguration".
  const rotIds = (rot[0] || '').split('|');
  const rotId = rotIds[0], rotTotal = toInt(rot[1], 0) || 0, rotTitle = rot.slice(2).join(' ');
  const rotDay = {};
  if (rotId && rotTotal) {
    const sundays = [].concat(...rotIds.map(i => byId[i] || [])).sort((a, b) => a.day - b.day);
    const n = sundays.length;
    let kept = [];
    for (let w = 1; w <= rotTotal; w++) kept.push(w);
    if (n < rotTotal) {
      const s = fmod(year.year, rotTotal);
      const omit = new Set();
      for (let i = 0; i < rotTotal - n; i++) omit.add(fmod(s + i, rotTotal) + 1);
      kept = kept.filter(w => !omit.has(w));
    }
    kept.forEach((w, j) => { if (sundays[j]) rotDay[w] = sundays[j]; });
  }
  const daysOf = dayKeyResolver(year, byId, feastId);
  // A reading plan (PLAN_FILE) is kept by the calendar year.  Its cycles are
  // the years they were first read, taken in turn; its rows keyed by a date
  // rule are its festivals, and `plan:N` is the Nth day of the year that none
  // of them takes.  A set past the year's plan days (a cycle written for a
  // leap year, read in a common one) is read on the last.
  const plans = {};
  for (const row of rows) {
    const f = cell(row, '_file');
    if (!PLAN_FILE.test(f)) continue;
    const plan = plans[f] = plans[f] || { cycles: new Set(), fixed: {} };
    const c = cell(row, 'cycle').trim();
    if (/^-?\d+$/.test(c)) plan.cycles.add(parseInt(c, 10));
    const key = cell(row, 'day').trim();
    if (!PLAN_KEY.test(key)) (plan.fixed[c] = plan.fixed[c] || new Set()).add(key);
  }
  const planCycle = (f, y) => {
    const known = Array.from(plans[f].cycles).sort((a, b) => a - b);
    const c = known.find(k => fmod(y - k, known.length) === 0);
    return c === undefined ? '' : String(c);
  };
  const planMemo = {};
  // The plan days of calendar year y, in order.
  const planDays = (f, y) => {
    const k = f + '\n' + y;
    if (!(k in planMemo)) {
      const rk = year.reckoning;
      const first = rk.toDay(y, 1, 1), last = rk.toDay(y + 1, 1, 1) - 1;
      const taken = new Set();
      for (const key of plans[f].fixed[planCycle(f, y)] || []) {
        const md = /^(\d\d)-(\d\d)$/.exec(key);
        if (md) {
          if (rk.valid(y, +md[1], +md[2])) taken.add(rk.toDay(y, +md[1], +md[2]));
          continue;
        }
        // A rule of the church year: the two that share this calendar year.
        for (const cy of [y - 1, y]) {
          let z;
          try { z = year.context(cy).eval(key); } catch (e) { continue; }
          if (z >= first && z <= last) taken.add(z);
        }
      }
      const days = [];
      for (let z = first; z <= last; z++) if (!taken.has(z)) days.push(z);
      planMemo[k] = days;
    }
    return planMemo[k];
  };
  const civilYears = [];
  for (let y = ctx.yearOf(year.start); y <= ctx.yearOf(year.end); y++) civilYears.push(y);

  const found = {};
  for (const row of rows) {
    const f = cell(row, '_file');
    const plan = Object.prototype.hasOwnProperty.call(plans, f) ? f : '';
    const want = cell(row, 'cycle').trim().toUpperCase();
    if (want && !plan && !cycles.has(want)) continue;
    const offset = toInt(cell(row, 'offset'), 0) || 0;
    const category = info.category(row);
    // A set keyed to a date under a feast's name is that feast's: it is read
    // only where the wheel shows the feast (or the day's own title names it),
    // so Ember days, weekdays and the day's propers stay.
    const tied = category !== 'daily' && category !== 'psalms' && category !== 'plan'
      ? info.tied(cell(row, 'day').trim(), cell(row, 'title')) : [];
    const pm = plan ? PLAN_KEY.exec(cell(row, 'day').trim()) : null;
    let keyed;
    if (pm) {
      const n = parseInt(pm[1], 10);
      keyed = [];
      for (const y of civilYears) {
        const days = planDays(plan, y);
        if (n > 0 && n <= days.length) keyed.push([days[n - 1], '']);
        else if (n > days.length && days.length) keyed.push([days[days.length - 1], '']);
      }
    } else {
      keyed = daysOf(cell(row, 'day').trim());
    }
    if (plan && want) keyed = keyed.filter(([b]) => planCycle(plan, ctx.yearOf(b + offset)) === want);
    if (rotId && cell(row, 'title') === rotTitle && offset > 0) {
      const m = new RegExp('^' + rotId + ':(\\d+)$').exec(cell(row, 'day').trim());
      if (m) {
        const e = rotDay[parseInt(m[1], 10)];
        keyed = e ? [[e.day, String(e.title || '').split('\n')[0]]] : [];
      }
    }
    for (const [base, name] of keyed) {
      if (tied.length && !(shownNames[base] || []).some(n => tied.indexOf(n) >= 0)
          && !(dayTitles[base] || []).some(t => sameFeast(cell(row, 'title'), t))) continue;
      const day = base + offset;
      if (day < year.start || day > year.end) continue;
      let ok;
      try { ok = ctx.holds(cell(row, 'when'), day); } catch (e) { ok = false; }
      if (!ok) continue;
      // A blank title is the day's own propers; keyed to a named row they
      // carry its name, so that two sets on one day (a Sunday and a festival
      // kept on it) stay apart.
      const own = !cell(row, 'title');
      const title = cell(row, 'title') || (offset ? '' : name);
      const groups = found[day] = found[day] || [];
      let group = groups.find(g => g.title === title && g.own === own);
      if (!group) groups.push(group = { title: title, own: own, category: category, items: [] });
      const kind = cell(row, 'kind');
      const item = withRow({ kind: kind, label: labels[kind] || kind, reading: cell(row, 'reading') }, row);
      // The church's own psalms cited in its Prayer Book psalter's verses
      // (`psalter`): `cite` is the citation in the English ones, for the links.
      if (psalter && !cell(row, '_file') && item.reading.indexOf('Psalm') >= 0) {
        const cited = psalterCitation(item.reading, psalter);
        if (cited !== item.reading) item.cite = cited;
      }
      group.items.push(item);
    }
  }
  // `reading_order`: groups of kinds, split by `|`; within each set the
  // readings of those kinds take the places they hold among themselves,
  // group by group in this order (each group's own order kept), and the
  // rest stay put.
  const rank = {};
  String(cfg.reading_order || '').split('|').forEach((part, i) => {
    for (const k of part.split(/\s+/).filter(Boolean)) rank[k] = i;
  });
  if (Object.keys(rank).length) {
    for (const day in found) {
      for (const g of found[day]) {
        const slots = [], picked = [];
        g.items.forEach((it, i) => { if (it.kind in rank) { slots.push(i); picked.push(it); } });
        picked.sort((a, b) => rank[a.kind] - rank[b.kind]);
        slots.forEach((s, j) => { g.items[s] = picked[j]; });
      }
    }
  }
  for (const day in found) {
    out[iso(+day)] = found[day].map((g, i) => [g, i])
      .sort((a, b) => (b[0].own - a[0].own) || officeHour(a[0]) - officeHour(b[0]) || a[1] - b[1])
      .map(p => ({ title: p[0].title, category: p[0].category, items: p[0].items }));
  }
  return out;
}

/** The whole SVG document, the way church_year_image.py writes it. */
function renderDocument(data, options) {
  return new Renderer(new Calendar(data, calendarOptions(options || {}))).render();
}

/** The Advent year (or other starting year) whose church year holds this day. */
function yearFor(data, key, day) {
  const y = civilFromDays(day).y;
  for (const candidate of [y, y - 1, y + 1]) {
    if (day >= yearStart(data, key, candidate) && day < yearStart(data, key, candidate + 1)) {
      return candidate;
    }
  }
  return y;
}

root.ChurchYear = {
  build: build,
  seasonArt: seasonArt,
  byAuthor: byAuthor,
  // What the lists (web/listings.js) work from, as lectionary.py, colors.py
  // and feasts.py do.
  Calendar: Calendar, readingsIndex: readingsIndex, feastShown: feastShown, psalterCitation: psalterCitation,
  truthy: truthy, isoIn: (reck, z) => { const r = reckoning; reckoning = reck; const s = iso(z); reckoning = r; return s; },
  renderDocument: renderDocument,
  Year: Year, Source: Source, findTradition: findTradition,
  traditionSettings: traditionSettings,
  languageOf: languageOf,
  yearStart: (data, key, year) => yearStart(data, key, year),
  yearFor: yearFor,
  readingCategories: readingCategories, READING_CATEGORIES: READING_CATEGORIES,
  readingRows: readingRows, packRows: packRows, pruneReadings: pruneReadings,
  keptLayouts: keptLayouts, fileOwner: fileOwner, rowOrigin: rowOrigin, READING_LABELS: READING_LABELS,
  iso: iso, fromIso: fromIso, daysFromCivil: daysFromCivil,
  yearName: yearName, spanName: spanName,
  RECKONINGS: RECKONINGS, GREGORIAN: GREGORIAN,
  reckoningNow: () => reckoning,
  setReckoning: name => { reckoning = RECKONINGS[name] || GREGORIAN; },
  // Today is a moment, not a label: find its day through the Gregorian
  // calendar the browser clock speaks, then name it in the wheel's calendar.
  todayDay: () => { const n = new Date();
    return GREGORIAN.toDay(n.getFullYear(), n.getMonth() + 1, n.getDate()); },
  gregorianOf: z => GREGORIAN.fromDay(z),
  civilFromDays: civilFromDays, weekday: weekday, easter: easter,
  adventSunday: adventSunday,
};

})(typeof module !== 'undefined' && module.exports ? module.exports : window);
