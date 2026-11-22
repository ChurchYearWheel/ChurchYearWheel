/*
 * The lists the page makes for download, as lectionary.py, colors.py and
 * feasts.py write them: the readings, the colors and the feasts of a church's
 * years, in CSV, HTML, iCalendar, JSON or Markdown.  Each function here
 * follows its Python twin line for line (named beside it), so a list made on
 * the page is the file the script writes; web/verify_lists.py checks that
 * they are.
 *
 * Needs church_year.js (window.ChurchYear, or require in Node).  The links
 * (Bible Gateway, Bible.com, a feast's page) come from the page, which keeps
 * them in one place for its readout too: `links` is
 *   { parts(text, version, site, numbering) -> [[text, url|null] ...],
 *     group(readings, version, numbering) -> url,
 *     feast(name, link, pattern) -> url,
 *     numbering(setting) -> the books a church cites in the Hebrew numbering }.
 */
(function (root) {
'use strict';

const CY = root.ChurchYear || (typeof require !== 'undefined' ? require('./church_year.js').ChurchYear : null);

// The words of a list's headings, notes and dates in the reader's language
// (page.js: setWords; English, as the Python scripts write them, otherwise).
let TR = s => s;
let LANG = 'en';
/** English words in the list's language; {0}, {1} ... take the values given. */
function tf(s) {
  let t = TR(s);
  for (let i = 1; i < arguments.length; i++) t = t.split('{' + (i - 1) + '}').join(arguments[i]);
  return t;
}
function setWords(fn, code) { TR = fn || (s => s); LANG = code || 'en'; }

const WEEKDAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                     'August', 'September', 'October', 'November', 'December'];

// ---------------------------------------------------------------------------
// listing.py
// ---------------------------------------------------------------------------

/** A church year's short name, as in file names (traditions.py: year_label). */
function yearLabel(y) {
  if (y >= 1 && y + 1 <= 9999) return y + '-' + String((y + 1) % 100).padStart(2, '0');
  if (y < 1 && y + 1 < 1) return (1 - y) + '-' + (-y) + 'BC';
  if (y === 0) return '1BC-1';
  return y + '-' + (y + 1);
}

function heading(label, what, first, last) {
  return tf('{0}: {1} for {2}', label, TR(what), first === last ? yearLabel(first) : tf('{0} to {1}', yearLabel(first), yearLabel(last)));
}

function spanLabel(first, last) { return first === last ? yearLabel(first) : first + '-' + last; }

function defaultName(key, first, last, kind, fmt) {
  return (key || 'church_year') + '_' + spanLabel(first, last) + '_' + kind + '.' + fmt;
}

/** date (Gregorian), weekday and, in another calendar, own_date (listing.py: day_fields). */
function dayFields(z, reck) {
  const out = { date: CY.isoIn(CY.GREGORIAN, z), weekday: WEEKDAY_NAMES[CY.weekday(z)] };
  const own = CY.isoIn(reck || CY.GREGORIAN, z);
  if (own !== out.date) out.own_date = own;
  return out;
}

const hasOwnDates = recs => recs.some(r => 'own_date' in r);

const titleCase = s => s.replace(/[A-Za-z]+/g, w => w[0].toUpperCase() + w.slice(1).toLowerCase());

function longDate(r, calendar) {
  const m = /^([+-]?\d+)-(\d\d)-(\d\d)$/.exec(r.date);
  let text = tf('{0}, {1} {2}, {3}', TR(r.weekday), TR(MONTH_NAMES[+m[2] - 1]), +m[3], +m[1]);
  if (r.own_date) {
    text += ' (' + r.own_date + (calendar ? ' ' + titleCase(calendar.replace(/-/g, ' ')) + ')' : ')');
  }
  return text;
}

function splitColor(text) {
  const parts = String(text || '').split(';');
  return [parts[0].trim().toUpperCase(), parts.slice(1).map(a => a.trim()).filter(Boolean)];
}

function colorText(name, alt, every) {
  return every && name ? [name].concat(alt).join('; ') : name;
}

function colorWords(name, alt) {
  const say = c => (c.toLowerCase() === 'none' ? 'no color' : c.toLowerCase().replace(/_/g, ' '));
  const others = (alt || []).map(say);
  return say(name) + (others.length ? ' (or ' + others.join(' or ') + ')' : '');
}

function cssPaint(fill) {
  const i = String(fill || '').indexOf('/');
  if (i < 0) return fill || '';
  return 'repeating-linear-gradient(45deg, ' + fill.slice(i + 1).trim() + ' 0 1.5px, '
    + fill.slice(0, i).trim() + ' 1.5px 5px)';
}

const CSS_COLOR = { BLUE: 'blue', WHITE: 'white', GREEN: 'green', PURPLE: 'purple', SCARLET: 'crimson',
                    BLACK: 'black', RED: 'red', GOLD: 'gold', ROSE: 'pink', VIOLET: 'violet' };

/** Python's csv writer: a field is quoted when it holds a comma, a quote or a line break. */
function csvText(header, rows) {
  const field = v => {
    const s = v == null ? '' : String(v);
    return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  };
  const line = row => (row.length === 1 && String(row[0]) === '' ? '""' : row.map(field).join(','));
  return [header].concat(rows).map(line).join('\n') + '\n';
}

/** json.dumps(v, ensure_ascii=False, separators=(", ", ": ")). */
function pyJson(v) {
  if (Array.isArray(v)) return '[' + v.map(pyJson).join(', ') + ']';
  if (v && typeof v === 'object') {
    return '{' + Object.keys(v).map(k => JSON.stringify(k) + ': ' + pyJson(v[k])).join(', ') + '}';
  }
  return JSON.stringify(v);
}

function jsonText(payload) {
  const lines = [];
  for (const k of Object.keys(payload)) {
    const v = payload[k];
    if (Array.isArray(v) && v.length && v.every(x => x && typeof x === 'object' && !Array.isArray(x))) {
      lines.push('  ' + pyJson(k) + ': [\n' + v.map(x => '    ' + pyJson(x)).join(',\n') + '\n  ]');
    } else {
      lines.push('  ' + pyJson(k) + ': ' + pyJson(v));
    }
  }
  return '{\n' + lines.join(',\n') + '\n}\n';
}

const mdEscape = text => String(text).replace(/([\\`*_\[\]<>|])/g, '\\$1');
const mdLink = (text, url) => (url ? '[' + mdEscape(text) + '](<' + url + '>)' : mdEscape(text));

function mdTable(header, rows) {
  const lines = ['| ' + header.join(' | ') + ' |', '|' + header.map(() => '---').join('|') + '|'];
  for (const row of rows) lines.push('| ' + row.map(c => String(c).replace(/\n/g, ' ')).join(' | ') + ' |');
  return lines.concat(['']);
}

const footer = script => tf("Made by {0} from the church year calendar's data.", script);

function mdPage(title, notes, body, script) {
  let lines = ['# ' + mdEscape(title), ''];
  if (notes.length) lines = lines.concat([notes.map(mdEscape).join('  \n'), '']);
  lines = lines.concat(body, ['---', '', mdEscape(footer(script)), '']);
  return lines.join('\n');
}

const HTML_STYLE = (
  'body{font:15px/1.4 Georgia,serif;max-width:46em;margin:2em auto;padding:0 1em;'
  + 'color:#111;background:#fff}'
  + 'h2{font-size:1.05em;margin:1.4em 0 .2em}h3{font-size:.95em;margin:.4em 0 0;font-style:italic;'
  + 'font-weight:normal}p.note{color:#555;margin:.2em 0}footer{color:#555;font-size:.85em;'
  + 'margin-top:2em;border-top:1px solid #ccc;padding-top:.4em}'
  + 'table{border-collapse:collapse}td,th{padding:0 .8em 0 0;vertical-align:top;text-align:left}'
  + 'table.readings td:first-child{color:#555;white-space:nowrap}'
  + 'table.list{width:100%}table.list th{border-bottom:1px solid #999;font-size:.9em}'
  + 'table.list td{border-bottom:1px solid #e4e4e4;padding:.15em .8em .15em 0}'
  + 'td.date,td.color{white-space:nowrap}'
  + '.sw{display:inline-block;width:.85em;height:.85em;border:1px solid #888;'
  + 'vertical-align:-.08em;margin-right:.35em;-webkit-print-color-adjust:exact;'
  + 'print-color-adjust:exact}'
  + 'a{color:#1a4f8b}@media print{h2{break-after:avoid}a{color:inherit;text-decoration:none}'
  + 'tr{break-inside:avoid}}'
);

/** Python's html.escape. */
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;').replace(/'/g, '&#x27;');
const htmlLink = (text, url) => (url ? '<a href="' + esc(url) + '">' + esc(text) + '</a>' : esc(text));
const htmlSwatch = fill => (fill ? '<span class="sw" style="background:' + esc(cssPaint(fill)) + '"></span>' : '');

function htmlTable(header, rows, cls) {
  const out = ['<table class="' + (cls || 'list') + '">', '<tr>' + header.map(h => '<th>' + esc(h) + '</th>').join('') + '</tr>'];
  for (const row of rows) {
    out.push('<tr>' + row.map((c, i) => (i === 0 ? '<td class="date">' + c + '</td>'
      : c.indexOf('<span class="sw"') === 0 ? '<td class="color">' + c + '</td>' : '<td>' + c + '</td>')).join('') + '</tr>');
  }
  out.push('</table>');
  return out.join('\n');
}

function htmlPage(title, notes, body, script) {
  const out = ['<!doctype html>', '<html lang="' + LANG + '"><head><meta charset="utf-8">',
               '<meta name="viewport" content="width=device-width, initial-scale=1">',
               '<title>' + esc(title) + '</title>', '<style>' + HTML_STYLE + '</style>',
               '</head><body><h1>' + esc(title) + '</h1>']
    .concat(notes.map(n => '<p class="note">' + esc(n) + '</p>'), body,
            ['<footer>' + esc(footer(script)) + '</footer>', '</body></html>']);
  return out.join('\n') + '\n';
}

const icsText = text => String(text).replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\n/g, '\\n');
const utf8Length = s => (typeof TextEncoder !== 'undefined' ? new TextEncoder().encode(s).length : Buffer.byteLength(s));

function icsFold(line) {
  const out = [];
  let current = '';
  for (const ch of line) {
    const limit = out.length ? 74 : 75;
    if (utf8Length(current + ch) > limit) { out.push(current); current = ch; }
    else current += ch;
  }
  out.push(current);
  return [out[0]].concat(out.slice(1).map(p => ' ' + p));
}

/** YYYYMMDD of a Gregorian ISO date, and of the day after it. */
function compact(isoDate, plus) {
  const m = /^(\d{4})-(\d\d)-(\d\d)$/.exec(isoDate);
  const z = CY.GREGORIAN.toDay(+m[1], +m[2], +m[3]) + (plus || 0);
  const c = CY.GREGORIAN.fromDay(z);
  return String(c.y).padStart(4, '0') + String(c.m).padStart(2, '0') + String(c.d).padStart(2, '0');
}

function icsEvent(uid, day, stamp, summary, description, extra) {
  return ['BEGIN:VEVENT', 'UID:' + uid, 'DTSTAMP:' + stamp,
          'DTSTART;VALUE=DATE:' + compact(day), 'DTEND;VALUE=DATE:' + compact(day, 1),
          'SUMMARY:' + icsText(summary)]
    .concat(description ? ['DESCRIPTION:' + icsText(description)] : [], extra || [],
            ['TRANSP:TRANSPARENT', 'END:VEVENT']);
}

const icsStamp = firstDay => compact(firstDay) + 'T000000Z';

function icsCalendar(name, script, events) {
  let lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Church Year Wheel//' + script + '//EN',
               'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'X-WR-CALNAME:' + icsText(name), 'NAME:' + icsText(name)];
  for (const e of events) lines = lines.concat(e);
  lines.push('END:VCALENDAR');
  const parts = [];
  for (const l of lines) for (const p of icsFold(l)) parts.push(p);
  return parts.join('\r\n') + '\r\n';
}

const flat = text => String(text == null ? '' : text).split(/\s+/).filter(Boolean).join(' ');
const capitalize = s => (s ? s[0].toUpperCase() + s.slice(1).toLowerCase() : s);

/** One church year of one church, as the page draws it: the Calendar and its Year. */
function calendarOf(data, o, year) {
  return new CY.Calendar(data, { tradition: o.tradition, year: year, subcalendars: o.subcalendars || [],
                                 latinNames: o.latinNames, calendar: o.calendar, paschalion: o.paschalion,
                                 feastDetail: o.feastDetail });
}

// ---------------------------------------------------------------------------
// lectionary.py
// ---------------------------------------------------------------------------

function dayNames(year, detail) {
  const names = {};
  for (const e of year.principal) {
    if (e.title) (names[e.day] = names[e.day] || []).push(e.title.split('\n').join(' '));
  }
  for (const f of year.feasts) {
    if (!CY.feastShown(f.level, detail)) continue;
    const text = f.fullName || f.name;
    if (text && (names[f.day] || []).indexOf(text) < 0) (names[f.day] = names[f.day] || []).push(text);
  }
  return names;
}

/** A reading as the lists write it, without its link citation (lectionary.py: plain). */
function plain(it) {
  const out = Object.assign({}, it);
  delete out.cite;
  return out;
}

/** The kinds that are parts of the service rather than readings (lectionary.py: propers_of). */
const propersOf = cfg => String((cfg || {}).reading_propers || '').replace(/,/g, ' ').split(/\s+/).filter(Boolean);

function readingRecords(cal, o, links) {
  const year = cal.year;
  const detail = cal.cfg.feast_detail;
  const names = dayNames(year, detail);
  const index = CY.readingsIndex(cal);
  const numbering = links && o.site !== 'none' ? links.numbering(year.settings.verse_numbering) : null;
  const kinds = o.kinds || CY.READING_CATEGORIES;
  const own = propersOf(year.settings);
  const withPropers = o.propers !== false;
  const item = it => (o.site !== 'none'
    ? Object.assign(plain(it), { links: links.parts(it.reading, o.version, o.site, numbering, it.cite) })
    : plain(it));
  const link = items => (o.site !== 'none' && items.length
    ? { link: links.group(items.map(it => it.cite || it.reading), o.version, numbering) } : {});
  // A set's readings, then apart its parts of the service (lectionary.py: records).
  const one = (s, title) => {
    const readings = s.items.filter(it => own.indexOf(it.kind) < 0);
    const parts = withPropers ? s.items.filter(it => own.indexOf(it.kind) >= 0) : [];
    const out = Object.assign({ title: title }, link(readings.length ? readings : parts), { readings: readings.map(item) });
    if (parts.length) {
      out.propers = parts.map(item);
      if (o.site !== 'none' && readings.length) out.propers_link = link(parts).link;
    }
    return out;
  };
  const days = Object.keys(index).map(CY.fromIso).sort((a, b) => a - b);
  const label = yearLabel(year.year);
  const recs = [];
  for (const day of days) {
    const fields = dayFields(day, year.reckoning);
    let sets = index[CY.iso(day)].filter(s => kinds.indexOf(s.category) >= 0);
    if (!withPropers) sets = sets.filter(s => s.items.some(it => own.indexOf(it.kind) < 0));
    if (!sets.length) continue;
    const first = (names[day] || [''])[0];
    recs.push(Object.assign({}, fields, {
      church_year: label, names: names[day] || [],
      sets: sets.map(s => one(s, s.title || (sets.length > 1 ? first : ''))),
    }));
  }
  return recs;
}

const urls = it => (it.links || []).filter(p => p[1]).map(p => p[1]);
const setHeading = s => s.title || TR('Readings');
// What a set's parts of the service (reading_propers) are headed (lectionary.py: PROPERS).
const propersWord = () => TR('Propers');

function lectionaryNotes(linked, site, version) {
  const where = { biblegateway: 'Bible Gateway', youversion: 'Bible.com' }[site] || '';
  return linked ? [tf("Each reading opens at {0} in the {1}; each heading opens its set's readings together at Bible Gateway (its propers apart).", where, version)] : [];
}

const LECTIONARY = {
  csv(recs, a) {
    const own = hasOwnDates(recs);
    const header = (a.span ? ['church_year'] : []).concat(['date', 'weekday'], own ? ['own_date'] : [],
      ['day', 'set', 'kind', 'label', 'reading'], a.linked ? ['url'] : []);
    const rows = [];
    for (const r of recs) for (const s of r.sets) for (const it of s.readings.concat(s.propers || [])) {
      rows.push((a.span ? [r.church_year] : []).concat([r.date, r.weekday], own ? [r.own_date || ''] : [],
        [r.names.join(' / '), s.title, it.kind, it.label, it.reading], a.linked ? [urls(it).join(' ')] : []));
    }
    return csvText(header, rows);
  },
  json(recs, a) {
    const days = recs.map(r => {
      const one = it => Object.assign({ kind: it.kind, label: it.label, reading: it.reading }, a.linked ? { urls: urls(it) } : {});
      const sets = r.sets.map(s => Object.assign({ title: s.title }, 'link' in s ? { url: s.link } : {},
        { readings: s.readings.map(one) }, s.propers && s.propers.length ? { propers: s.propers.map(one) } : {},
        'propers_link' in s ? { propers_url: s.propers_link } : {}));
      const day = {};
      for (const k of ['date', 'weekday', 'own_date', 'names']) if (k in r) day[k] = r[k];
      day.sets = sets;
      return day;
    });
    return jsonText(Object.assign({ title: a.heading, church: a.key }, a.linked ? { bible: a.version } : {}, { days: days }));
  },
  md(recs, a) {
    let body = [];
    for (const r of recs) {
      body.push('## ' + mdEscape(longDate(r, a.calendar)) + (r.names.length ? ' — ' + mdEscape(r.names.join(' / ')) : ''), '');
      for (const s of r.sets) {
        if (s.title || r.sets.length > 1) body.push('**' + mdEscape(setHeading(s)) + '**', '');
        const line = it => '- ' + mdEscape(it.label) + ': '
          + (a.linked ? it.links.map(p => mdLink(p[0], p[1])).join('') : mdEscape(it.reading));
        body = body.concat(s.readings.map(line), ['']);
        if (s.propers && s.propers.length) {
          body = body.concat(['*' + ('propers_link' in s ? mdLink(propersWord(), s.propers_link) : propersWord()) + '*', ''], s.propers.map(line), ['']);
        }
      }
    }
    return mdPage(a.heading, lectionaryNotes(a.linked, a.site, a.version), body, 'lectionary.py');
  },
  html(recs, a) {
    const body = [];
    for (const r of recs) {
      body.push('<h2>' + esc(longDate(r, a.calendar)) + (r.names.length ? ' — ' + esc(r.names.join(' / ')) : '') + '</h2>');
      for (const s of r.sets) {
        if (a.linked) body.push('<h3>' + htmlLink(s.title || TR('Readings'), s.link) + '</h3>');
        else if (s.title || r.sets.length > 1) body.push('<h3>' + esc(setHeading(s)) + '</h3>');
        const table = (items, cls) => '<table class="' + cls + '">' + items.map(it => '<tr><td>' + esc(it.label) + '</td><td>'
          + (a.linked ? it.links.map(p => htmlLink(p[0], p[1])).join('') : esc(it.reading)) + '</td></tr>').join('') + '</table>';
        if (s.readings.length) body.push(table(s.readings, 'readings'));
        if (s.propers && s.propers.length) {
          body.push('<h4>' + ('propers_link' in s ? htmlLink(propersWord(), s.propers_link) : esc(propersWord())) + '</h4>');
          body.push(table(s.propers, 'readings propers'));
        }
      }
    }
    return htmlPage(a.heading, lectionaryNotes(a.linked, a.site, a.version), body, 'lectionary.py');
  },
  ics(recs, a) {
    const stamp = recs.length ? icsStamp(recs[0].date) : '20000101T000000Z';
    const events = recs.map(r => {
      let body = [];
      for (const s of r.sets) {
        if (s.title || r.sets.length > 1) body.push(setHeading(s) + ':');
        for (const it of s.readings) body = body.concat([it.label + ': ' + it.reading], urls(it));
        if (s.propers && s.propers.length) {
          body.push(propersWord() + ':');
          for (const it of s.propers) body = body.concat([it.label + ': ' + it.reading], urls(it));
        }
      }
      return icsEvent(a.key + '-' + r.date.replace(/-/g, '') + '@churchyearwheel', r.date, stamp,
                      r.names.join(' / ') || TR('Readings'), body.join('\n'));
    });
    return icsCalendar(a.heading, 'lectionary.py', events);
  },
};

/**
 * The readings list (lectionary.py).  `o`: tradition, first, last (church
 * years), subcalendars, latinNames, calendar, paschalion, feastDetail, kinds
 * (the Readings boxes), site (none, biblegateway or youversion), version.
 */
function readingsList(data, o, fmt, links) {
  o = Object.assign({ site: 'none', version: 'ESV' }, o);
  let recs = [], cal = null;
  for (let y = o.first; y <= o.last; y++) {
    cal = calendarOf(data, o, y);
    if (!(cal.source.readings || []).length) throw new Error(cal.tradition.label + ' has no readings yet');
    recs = recs.concat(readingRecords(cal, o, links));
  }
  const h = heading(cal.tradition.label, 'readings', o.first, o.last);
  return { text: LECTIONARY[fmt](recs, { heading: h, key: cal.tradition.key, span: o.first !== o.last,
                                         linked: o.site !== 'none', site: o.site, version: o.version,
                                         calendar: cal.year.calendar }),
           name: defaultName(cal.tradition.key, o.first, o.last, 'readings', fmt), count: recs.length };
}

// ---------------------------------------------------------------------------
// colors.py
// ---------------------------------------------------------------------------

const others = alt => String(alt || '').split(';').map(c => c.trim()).filter(Boolean);

function colorRecords(cal, days) {
  const cfg = cal.cfg;
  const label = yearLabel(cal.year.year);
  const recs = [];
  for (const day of cal.days) {
    const isSunday = CY.weekday(day) === Number(cfg.week_starts_on);
    const titles = cal.titles[day] || [], feasts = cal.feasts[day] || [];
    const solemn = feasts.filter(e => e.style === 'solemnity').map(e => flat(e.text));
    const wanted = days === 'all' || isSunday || (days === 'named' && (titles.length || feasts.length))
      || (days === 'principal' && (titles.length || solemn.length));
    if (!wanted) continue;
    const fields = dayFields(day, cal.cy.reckoning);
    let labels = titles.map(e => flat(e.text));
    if (days === 'all' || days === 'named' || !labels.length) labels = labels.concat(feasts.map(e => flat(e.text)));
    else labels = labels.concat(solemn);
    const top = cal.colorFor(day);
    let lower = cal.bottomColorFor(day);
    if (lower && lower.fill === top.fill) lower = null;
    recs.push(Object.assign({}, fields, { church_year: label, titles: labels,
      color: top.name, alternatives: others(top.alt), fill: top.fill,
      lower_color: lower ? lower.name : '', lower_alternatives: lower ? others(lower.alt) : [],
      lower_fill: lower ? lower.fill : '' }));
  }
  return recs;
}

function yearDetails(cal, o) {
  return { church_year: yearLabel(cal.year.year),
           start: dayFields(cal.cy.start).date, end: dayFields(cal.cy.end).date,
           lectionary: cal.tradition.key, calendar: cal.cy.calendar, paschalion: cal.cy.paschalion,
           subcalendars: (o.subcalendars || []).slice(),
           latin_names: !!cal.year.latin, feast_detail: cal.cfg.feast_detail };
}

function icsSeries(cal, o) {
  let series = cal.tradition.key;
  const subs = o.subcalendars || [];
  if (subs.length) series += '+' + subs.join('+');
  if (cal.cy.calendar !== 'gregorian') series += '-' + cal.cy.calendar;
  const natural = cal.cy.calendar === 'gregorian' ? 'gregorian' : 'julian';
  if (cal.cy.paschalion !== natural) series += '-' + cal.cy.paschalion + '-easter';
  return series;
}

const colorNotes = every => (every
  ? [TR("Each color is the day's own, the top of its cell on the wheel; the others the church allows follow in parentheses, and the lower half's is given where the wheel splits the cell.")]
  : [TR("Each color is the day's own, the top of its cell on the wheel.")]);
const colorHeader = every => ['Date', 'Day', 'Color'].concat(every ? ['Lower half'] : []).map(h => TR(h));
const colorWordsOf = (r, every, lower) => (lower
  ? (r.lower_color ? colorWords(r.lower_color, r.lower_alternatives) : '')
  : colorWords(r.color, every ? r.alternatives : []));

function sections(recs) {
  const order = [], groups = {};
  for (const r of recs) {
    if (!(r.church_year in groups)) { groups[r.church_year] = []; order.push(r.church_year); }
    groups[r.church_year].push(r);
  }
  return order.map(k => [k, groups[k]]);
}

const COLORS = {
  csv(recs, a) {
    const own = hasOwnDates(recs);
    const header = (a.span ? ['church_year'] : []).concat(['date', 'weekday'], own ? ['own_date'] : [],
      ['title', 'color'], a.every ? ['lower_color'] : []);
    return csvText(header, recs.map(r => (a.span ? [r.church_year] : []).concat([r.date, r.weekday],
      own ? [r.own_date || ''] : [], [r.titles.join(' / '), colorText(r.color, r.alternatives, a.every)],
      a.every ? [colorText(r.lower_color, r.lower_alternatives, true)] : [])));
  },
  json(recs, a) {
    const own = ['church_year', 'start', 'end'];
    const years = a.years;
    const shared = {};
    if (years.length) {
      for (const k of Object.keys(years[0])) {
        if (own.indexOf(k) >= 0) continue;
        const v = pyJson(years[0][k]);
        if (years.every(y => pyJson(y[k]) === v)) shared[k] = years[0][k];
      }
    }
    if (shared.lectionary === a.key) delete shared.lectionary;
    const keys = ['date', 'weekday', 'own_date', 'titles', 'color'].concat(
      a.every ? ['alternatives', 'lower_color', 'lower_alternatives'] : []);
    return jsonText(Object.assign({ title: a.heading, church: a.key }, shared, {
      years: years.map(y => { const o = {}; for (const k of Object.keys(y)) if (!(k in shared) && !(k === 'lectionary' && y[k] === a.key)) o[k] = y[k]; return o; }),
      days: recs.map(r => { const o = {}; for (const k of keys) if (k in r) o[k] = r[k]; return o; }),
    }));
  },
  md(recs, a) {
    let body = [];
    const secs = sections(recs);
    for (const [label, rows] of secs) {
      if (secs.length > 1) body.push('## ' + label, '');
      body = body.concat(mdTable(colorHeader(a.every), rows.map(r => [mdEscape(longDate(r, a.calendar)),
        mdEscape(r.titles.join(' / ')), mdEscape(colorWordsOf(r, a.every))].concat(
        a.every ? [mdEscape(colorWordsOf(r, a.every, true))] : []))));
    }
    return mdPage(a.heading, colorNotes(a.every), body, 'colors.py');
  },
  html(recs, a) {
    const body = [];
    const secs = sections(recs);
    for (const [label, rows] of secs) {
      if (secs.length > 1) body.push('<h2>' + esc(label) + '</h2>');
      body.push(htmlTable(colorHeader(a.every), rows.map(r => [esc(longDate(r, a.calendar)), esc(r.titles.join(' / ')),
        htmlSwatch(r.fill) + esc(colorWordsOf(r, a.every))].concat(a.every
        ? [r.lower_color ? htmlSwatch(r.lower_fill) + esc(colorWordsOf(r, a.every, true)) : ''] : []))));
    }
    return htmlPage(a.heading, colorNotes(a.every), body, 'colors.py');
  },
  ics(recs, a) {
    const stamps = {};
    for (const y of a.years) stamps[y.church_year] = icsStamp(y.start);
    const events = recs.map(r => {
      let words = tf('Liturgical color: {0}', capitalize(colorWordsOf(r, a.every)));
      if (a.every && r.lower_color) words += tf('; lower half {0}', colorWordsOf(r, a.every, true));
      const names = [r.color].concat(a.every && r.lower_color ? [r.lower_color] : []);
      return icsEvent(r.date + '-' + a.series[r.church_year] + '@churchyearwheel', r.date, stamps[r.church_year],
        r.titles.join(' / ') || r.weekday, words,
        ['CATEGORIES:' + names.map(icsText).join(',')].concat(r.color in CSS_COLOR ? ['COLOR:' + CSS_COLOR[r.color]] : []));
    });
    return icsCalendar(a.heading, 'colors.py', events);
  },
};

/** The colors list (colors.py).  `o` as readingsList's, with days (sundays,
 * principal, named, all) and every (the other colors and the lower halves). */
function colorsList(data, o, fmt) {
  let recs = [], cal = null;
  const details = [], series = {};
  for (let y = o.first; y <= o.last; y++) {
    cal = calendarOf(data, o, y);
    recs = recs.concat(colorRecords(cal, o.days || 'principal'));
    details.push(yearDetails(cal, o));
    series[yearLabel(y)] = icsSeries(cal, o);
  }
  const key = cal.tradition.key;
  const h = heading(cal.tradition.label, 'colors', o.first, o.last);
  return { text: COLORS[fmt](recs, { heading: h, key: key, span: o.first !== o.last, every: !!o.every,
                                     years: details, series: series, calendar: cal.cy.calendar }),
           name: defaultName(key, o.first, o.last, 'colors', fmt), count: recs.length };
}

// The overview (colors.py --overview; new_year.py: overview): one row a year,
// its movable dates and how many Sundays it holds.
const OVERVIEW_IDS = [
  ['christmas', ['christmas']], ['epiphany', ['epiphany']], ['transfiguration', ['transfiguration']],
  ['septuagesima', ['septuagesima']], ['ash_wednesday', ['ash_wednesday']], ['palm_sunday', ['palm_sunday']],
  ['good_friday', ['good_friday']], ['easter', ['easter']], ['ascension', ['ascension']],
  ['pentecost', ['pentecost']], ['trinity', ['trinity']],
  ['reformation_observed', ['reformation', 'reformation_day']],
  ['all_saints_observed', ['all_saints', 'all_saints_day']], ['thanksgiving', ['thanksgiving']],
  ['last_sunday', ['last_sunday', 'christ_the_king']],
];

function overviewRow(cal) {
  const year = cal.year, iso = z => CY.isoIn(year.reckoning, z);
  const byId = {};
  for (const r of year.principal) if (r.id && r.title && !(r.id in byId)) byId[r.id] = r.day;
  const out = { church_year: yearLabel(year.year), lectionary: cal.tradition.key,
                calendar: year.calendar, paschalion: year.paschalion, advent_1: iso(year.start) };
  for (const [column, ids] of OVERVIEW_IDS) {
    let day = null;
    for (const i of ids) if (i in byId) { day = byId[i]; break; }
    if (column === 'easter') day = year.easter;
    out[column] = day !== null ? iso(day) : '';
  }
  out.end = iso(year.end);
  const count = (phrase, before) => year.principal.filter(r => r.title && r.title.indexOf(phrase) >= 0
    && (before === undefined || r.day < before)).length || '';
  out.sundays_after_epiphany = count('Sunday after Epiphany', year.easter) || count('Sunday after the Epiphany', year.easter);
  out.sundays_after_pentecost = count('Sunday after Pentecost');
  out.sundays_after_trinity = count('Sunday after Trinity');
  out.days = year.end - year.start + 1;
  out.weeks = Math.floor((out.days + 6) / 7);
  return out;
}

const OVERVIEW = {
  csv: (rows, columns) => csvText(columns, rows.map(g => columns.map(k => g[k]))),
  json: (rows, columns, h) => jsonText({ title: h, years: rows }),
  md: (rows, columns, h) => mdPage(h, [], mdTable(columns, rows.map(g => columns.map(k => mdEscape(String(g[k]))))), 'colors.py'),
  html: (rows, columns, h) => htmlPage(h, [], [htmlTable(columns, rows.map(g => columns.map(k => esc(String(g[k])))))], 'colors.py'),
};

/** The year at a glance (colors.py --overview): csv, html, json or md, no ics. */
function overviewList(data, o, fmt) {
  if (!OVERVIEW[fmt]) throw new Error('the overview is one row per year, not a list of days: it has no ' + fmt + ' form');
  const rows = [];
  let cal = null;
  for (let y = o.first; y <= o.last; y++) {
    cal = calendarOf(data, o, y);
    rows.push(overviewRow(cal));
  }
  const columns = Object.keys(rows[0]);
  const h = heading(cal.tradition.label, 'the year at a glance', o.first, o.last);
  return { text: OVERVIEW[fmt](rows, columns, h), name: defaultName(cal.tradition.key, o.first, o.last, 'overview', fmt),
           count: rows.length };
}

// ---------------------------------------------------------------------------
// feasts.py
// ---------------------------------------------------------------------------

const KEEPS = { none: [], principal: ['principal'], festivals: ['principal', 'festival'],
                all: ['principal', 'festival', 'all'] };
const LEVEL_NAMES = { principal: 'principal', festival: 'festival', all: 'commemoration' };
const MAJOR_DAY = 'major day';
const ORDINARY_SUNDAYS = new Set(`
after_christmas after_christmas_1 after_christmas_2 after_new_year after_octave after_nativity
after_theophany after_exaltation before_exaltation before_nativity before_theophany after_ascension
after_all_saints septuagesima sexagesima quinquagesima estomihi shrove_sunday invocavit lent1
laetare judica gaudete rogate exaudi low_sunday new_sunday first_sunday octave_sunday
third_last third_last_sunday second_last second_last_sunday penultimate last_sunday
next_before_lent next_before_advent fathers_first fathers_fourth fathers_seventh forefathers
holy_fathers zacchaeus publican prodigal meatfare forgiveness orthodoxy palamas climacus
mary_of_egypt myrrhbearers paralytic samaritan blind blind_man bent_woman canaanite leper
hemorrhaging sower steward fifty_3 fifty_4 fifty_5 fifty_6 green_sunday red_sunday
`.split(/\s+/).filter(Boolean));

function majorDays(year) {
  const skip = new Set(ORDINARY_SUNDAYS);
  for (const k of String(year.settings.major_days_exclude || '').split(/\s+/).filter(Boolean)) skip.add(k);
  return year.principal.filter(e => e.single && e.title && !skip.has(e.id));
}

function feastRecords(year, detail, everyColor, withLinks, major, links) {
  const keep = KEEPS[detail];
  const pattern = year.source.settings.feast_link || '';
  const dedupe = CY.truthy(year.settings.deduplicate_day_labels || 'TRUE');
  const titles = {};
  for (const e of year.principal) {
    if (e.title) (titles[e.day] = titles[e.day] || new Set()).add(flat(e.title).toLowerCase());
  }
  const label = yearLabel(year.year);
  const recs = [];
  if (major) {
    for (const e of majorDays(year)) {
      const fields = dayFields(e.day, year.reckoning);
      const name = flat(e.title.split('\n')[0]);
      const full = flat(e.fullName || e.title);
      const rec = Object.assign({}, fields, { church_year: label, name: name, full_name: full, level: MAJOR_DAY });
      const [color, alt] = splitColor(e.color);
      Object.assign(rec, { color: color, alternatives: everyColor ? alt : [] });
      if (withLinks) rec.url = links.feast(name, '', pattern);
      recs.push([e.day, -1, rec]);
    }
  }
  const feasts = year.feasts.slice().sort((a, b) => (a.day - b.day) || (a.order - b.order));
  for (const f of feasts) {
    if (keep.indexOf(f.level) < 0) continue;
    if (dedupe && titles[f.day] && titles[f.day].has(flat(f.name).toLowerCase())) continue;
    const fields = dayFields(f.day, year.reckoning);
    const full = flat(f.fullName || f.name);
    const moved = f.transferredFrom;
    const rec = Object.assign({}, fields, { church_year: label, name: flat(f.name), full_name: full,
                                            level: LEVEL_NAMES[f.level] });
    const [name, alt] = splitColor(f.color || f.bottom);
    Object.assign(rec, { color: name, alternatives: everyColor ? alt : [] });
    let note = '';
    if (moved !== null && moved !== undefined) {
      rec.transferred_from = dayFields(moved).date;
      const c = year.reckoning.fromDay(moved);
      note = ' (transferred from ' + String(c.m).padStart(2, '0') + '-' + String(c.d).padStart(2, '0') + ')';
    }
    if (withLinks) rec.url = links.feast(full + note, f.link || '', pattern);
    recs.push([f.day, f.order, rec]);
  }
  return recs.sort((a, b) => (a[0] - b[0]) || (a[1] - b[1])).map(t => t[2]);
}

function moved(r) {
  if (!r.transferred_from) return '';
  const p = r.transferred_from.split('-');
  return ' (' + tf('transferred from {0} {1}', TR(MONTH_NAMES[+p[1] - 1]), +p[2]) + ')';
}

function feastNotes(detail, major) {
  return ({ none: [], principal: [TR("Principal feasts only: those whose color replaces the season's.")],
            festivals: [TR('Festivals: the feasts that color their day or its lower half.')], all: [] }[detail])
    .concat(major ? [TR("With the major days: the principal days set on dates of their own, Christmas, Easter, Pentecost and the like; a blank color is the season's.")] : []);
}

const feastRows = (recs, calendar, cellName, cellColor) =>
  recs.map(r => [longDate(r, calendar), cellName(r), TR(r.level), cellColor(r)]);

const FEASTS = {
  csv(recs, a) {
    const own = hasOwnDates(recs);
    const header = (a.span ? ['church_year'] : []).concat(['date', 'weekday'], own ? ['own_date'] : [],
      ['name', 'full_name', 'level', 'color', 'transferred_from'], a.linked ? ['url'] : []);
    return csvText(header, recs.map(r => (a.span ? [r.church_year] : []).concat([r.date, r.weekday],
      own ? [r.own_date || ''] : [], [r.name, r.full_name, r.level, colorText(r.color, r.alternatives, a.every),
      r.transferred_from || ''], a.linked ? [r.url] : [])));
  },
  json(recs, a) {
    const keys = ['date', 'weekday', 'own_date', 'name', 'full_name', 'level', 'color']
      .concat(a.every ? ['alternatives'] : [], ['transferred_from', 'url']);
    return jsonText({ title: a.heading, church: a.key,
                      feasts: recs.map(r => { const o = {}; for (const k of keys) if (k in r) o[k] = r[k]; return o; }) });
  },
  md(recs, a) {
    const rows = feastRows(recs, a.calendar, r => mdLink(r.full_name, r.url) + mdEscape(moved(r)),
                           r => (r.color ? colorWords(r.color, r.alternatives) : ''));
    return mdPage(a.heading, feastNotes(a.detail, a.major), mdTable(['Date', 'Feast', 'Level', 'Color'].map(h => TR(h)), rows), 'feasts.py');
  },
  html(recs, a) {
    const rows = feastRows(recs, a.calendar, r => htmlLink(r.full_name, r.url) + esc(moved(r)),
                           r => (r.color ? htmlSwatch(a.fills[r.color] || '') + esc(colorWords(r.color, r.alternatives)) : ''));
    return htmlPage(a.heading, feastNotes(a.detail, a.major), [htmlTable(['Date', 'Feast', 'Level', 'Color'].map(h => TR(h)), rows)], 'feasts.py');
  },
  ics(recs, a) {
    const stamp = recs.length ? icsStamp(recs[0].date) : '20000101T000000Z';
    const order = [], byDay = {};
    for (const r of recs) { if (!(r.date in byDay)) { byDay[r.date] = []; order.push(r.date); } byDay[r.date].push(r); }
    const events = order.map(day => {
      const feasts = byDay[day];
      const body = [];
      for (const r of feasts) {
        const color = r.color ? colorWords(r.color, r.alternatives) : '';
        body.push(r.full_name + moved(r) + ' (' + r.level + (color ? ', ' + color + ')' : ')'));
        if (r.url) body.push(r.url);
      }
      const first = (feasts.find(r => r.color) || {}).color || '';
      return icsEvent(day + '-' + a.key + '-feasts@churchyearwheel', day, stamp,
                      feasts.map(r => r.name).join(' / '), body.join('\n'),
                      first in CSS_COLOR ? ['COLOR:' + CSS_COLOR[first]] : []);
    });
    return icsCalendar(a.heading, 'feasts.py', events);
  },
};

/** The feasts list (feasts.py).  `o` as readingsList's, with detail (all,
 * festivals, principal, none), major (the major days too), every (the other
 * colors) and links (where to read about each). */
function feastsList(data, o, fmt, links) {
  const detail = o.detail || 'all';
  let recs = [], cal = null;
  for (let y = o.first; y <= o.last; y++) {
    cal = calendarOf(data, Object.assign({}, o, { latinNames: false }), y);
    recs = recs.concat(feastRecords(cal.year, detail, !!o.every, !!o.links, !!o.major, links));
  }
  const fills = {};
  const colors = data.profiles[cal.tradition.key].colors;
  for (const k of Object.keys(colors)) fills[k] = colors[k].fill;
  const h = heading(cal.tradition.label, o.major ? 'feasts and major days' : 'feasts', o.first, o.last);
  return { text: FEASTS[fmt](recs, { heading: h, key: cal.tradition.key, span: o.first !== o.last,
                                     every: !!o.every, linked: !!o.links, detail: detail, major: !!o.major,
                                     calendar: cal.year.calendar, fills: fills }),
           name: defaultName(cal.tradition.key, o.first, o.last, 'feasts', fmt), count: recs.length };
}

root.ChurchYearLists = { readingsList: readingsList, colorsList: colorsList, feastsList: feastsList,
                         overviewList: overviewList,
                         yearLabel: yearLabel, setWords: setWords, FORMATS: ['csv', 'html', 'ics', 'json', 'md'] };

})(typeof module !== 'undefined' && module.exports ? module.exports : window);
