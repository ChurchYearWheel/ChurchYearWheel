// ---------------------------------------------------------------------------
// The page
// ---------------------------------------------------------------------------
// Draws the year in the browser, turns the chosen week to the top, and leaves
// the artwork in the middle upright.

(function () {
'use strict';

const CY = window.ChurchYear;
const NS = 'http://www.w3.org/2000/svg';

// Everything is looked up inside the app rather than the whole document, so
// the wheel still finds its own parts when it sits in someone else's page:
// that page's first <svg> is usually a logo, not the wheel.
const app = (document.currentScript && document.currentScript.closest('.cy-app'))
          || document.querySelector('.cy-app') || document.body;
const $ = id => app.querySelector('#' + id);
// The page as it came, before anything below changes it: Make a page writes
// a page like it from this, with its tables and settings swapped.
// This page as it came, for Make a page.  The parser has not yet reached the
// line break after this script when it runs, so that is put back.
const PRISTINE = { app: app.outerHTML.replace(/<\/script><\/div>$/, '<\/script>\n</div>'),
                   style: app.previousElementSibling && app.previousElementSibling.tagName === 'STYLE'
                     ? app.previousElementSibling.outerHTML : '' };

// The tables, as the page carries them: packed (gzip, then base64; see
// church_year.py: build) or, made with --no-compress, as they are.  The
// page starts once they are unpacked; PRISTINE_TEXT keeps them as they came.
const SHIPPED = window.CHURCH_YEAR_DATA;
let PRISTINE_TEXT = '';
const PACKED = typeof SHIPPED === 'string';
if (PACKED) {
  unpackTables(SHIPPED).then(text => { PRISTINE_TEXT = text; start(JSON.parse(text)); }, err => {
    const note = $('note');
    if (note) note.textContent = 'This page could not open its tables (' + (err && err.message || err)
      + '). It needs a browser from 2023 or later.';
  });
} else {
  start(SHIPPED);
}

/** The tables' text from their packed form. */
async function unpackTables(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
  return new Response(stream).text();
}

/** Tables' text packed as the page carries them (unpackTables). */
async function packTables(text) {
  const stream = new Blob([text]).stream().pipeThrough(new CompressionStream('gzip'));
  const bytes = new Uint8Array(await new Response(stream).arrayBuffer());
  let bin = '';
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}

function start(DATA) {

// ---- Edits to the page's tables ---------------------------------------------
// Edit the data... changes the rows of the tables the page draws from, each
// table the rows of one file under data/ (export_data.py: csv_layouts).  The
// changes are kept as a list, each naming its file and a row of it as the
// page came (`i`, its place there) or as an earlier change added it (`id`):
// { p: path, op: 'set' | 'del' | 'add', i | id, after, row }.  The page's
// tables are the tables as it came with the changes laid over them; the
// files are written again from the rows and the layout (csvText), so a file
// with no changes comes back byte for byte.

// Each file's table in the page's data (export_data.py: folder_tables).
const TABLE_NAMES = { 'tradition.csv': 'settings', 'days.csv': 'days', 'periods.csv': 'periods',
  'feasts.csv': 'feasts', 'hymn_topics.csv': 'hymnTopics', 'colors.csv': 'colors', 'seasons.csv': 'seasons',
  'readings.csv': 'readings' };
// The columns of a file the editor may start, as the project's own files have them.
const NEW_FILE_COLUMNS = { 'colors.csv': ['name', 'fill', 'text'], 'seasons.csv': ['season', 'color'],
  'tradition.csv': ['setting', 'value', 'variant'],
  'readings.csv': ['day', 'offset', 'when', 'cycle', 'variant', 'title', 'kind', 'reading'] };

/** A file's table in `data`: get() and set(), and whether it is packed (readings). */
function tableAt(data, path) {
  if (path === 'colors.csv') return { get: () => data.colorRows || [], set: v => { data.colorRows = v; }, packed: false };
  const owner = CY.fileOwner(data, path);
  if (owner.indexOf('readings/') === 0) {
    const name = path.slice('readings/'.length, -'.csv'.length);
    if (!data.sharedReadings || !data.sharedReadings[name]) return null;
    return { get: () => data.sharedReadings[name], set: v => { data.sharedReadings[name] = v; }, packed: true };
  }
  if (!owner) return null;
  const folder = data.folders[owner], rest = path.slice(owner.length + 1);
  const name = TABLE_NAMES[rest];
  if (name) {
    const empty = () => (name === 'readings' ? { cols: [], strings: [], rows: [] } : []);
    return { get: () => folder[name] || empty(), set: v => { folder[name] = v; }, packed: name === 'readings' };
  }
  const sub = (folder.subcalendars || []).find(e => e.file === rest);
  return sub ? { get: () => sub.rows, set: v => { sub.rows = v; }, packed: false } : null;
}
const tableRows = (t, v) => (t.packed ? CY.readingRows(v) : v);

/** A file's layout, or a new one for a file the folder has not got yet. */
function layoutOf(data, path) {
  const lay = (data.csv || {})[path];
  if (lay) return lay;
  const cols = NEW_FILE_COLUMNS[path.split('/').pop()];
  const t = tableAt(data, path);
  // (on this page: empty as the page came, whatever the changes have added)
  const base = data === DATA && EDIT_ORIG[path] !== undefined ? EDIT_ORIG[path] : t && t.get();
  if (!cols || !t || tableRows(t, base).length) return null;
  return { head: cols.join(','), cols: cols, n: 0, fresh: true };
}

/** The rows of a table with the changes to it laid over: each with its key (place or id). */
function editNodes(rows, ops) {
  const nodes = rows.map((r, i) => ({ key: i, orig: i, row: r, del: false }));
  for (const o of ops) {
    if (o.op === 'add') {
      const at = o.after === undefined || o.after === null ? -1 : nodes.findIndex(n => n.key === o.after);
      nodes.splice(at < 0 && o.after !== undefined && o.after !== null ? nodes.length : at + 1, 0,
                   { key: o.id, orig: null, row: o.row, del: false });
    } else {
      const n = nodes.find(x => x.key === (o.id !== undefined ? o.id : o.i));
      if (!n) continue;
      if (o.op === 'del') n.del = true; else n.row = o.row;
    }
  }
  return nodes;
}

/** One cell as the file has it (csvlayout.py: cell_text). */
const csvCell = v => (/[,"\n\r]/.test(v) || v !== v.trim() ? '"' + v.replace(/"/g, '""') + '"' : v);
/** A row in these columns (csvlayout.py: row_text). */
const csvRow = (row, cols) => cols.map(c => csvCell(row[c] === undefined ? '' : String(row[c]))).join(',');
/** The columns a file needs for its rows: its own, then any a change gave a row. */
function csvCols(lay, rows) {
  const cols = lay.cols.slice();
  for (const r of rows) for (const k of Object.keys(r)) if (cols.indexOf(k) < 0) cols.push(k);
  return cols;
}

/**
 * The file again, from its layout and its rows with the changes (editNodes,
 * over `base`, the rows as the page came): its comments where they were, a
 * row as it was written unless it was changed (csvlayout.py: write).
 */
function csvText(lay, nodes, base) {
  const live = nodes.filter(n => !n.del).map(n => n.row);
  const cols = csvCols(lay, live);
  const head = cols.length > lay.cols.length ? lay.head + ',' + cols.slice(lay.cols.length).map(csvCell).join(',') : lay.head;
  const before = {}, lines = [];
  for (const [i, t] of lay.notes || []) {
    if (i < 0) lines.push(t); else (before[i] = before[i] || []).push(t);
  }
  lines.push(head);
  const raw = lay.raw || {};
  for (const n of nodes) {
    if (n.orig !== null) lines.push(...(before[n.orig] || []));
    if (n.del) continue;
    const same = n.orig !== null && n.row === base[n.orig];
    lines.push(same ? (raw[n.orig] !== undefined ? raw[n.orig] : csvRow(n.row, lay.cols)) : csvRow(n.row, cols));
  }
  lines.push(...(before[lay.n] || []));
  return (lay.bom ? '﻿' : '') + lines.join('\n') + (lay.open ? '' : '\n');
}

/** The layout of the file csvText writes (what export_data.py would find in it). */
function relayout(lay, nodes, base) {
  const live = nodes.filter(n => !n.del).map(n => n.row);
  const cols = csvCols(lay, live);
  const out = { head: cols.length > lay.cols.length ? lay.head + ',' + cols.slice(lay.cols.length).map(csvCell).join(',') : lay.head,
                cols: cols, n: 0 };
  const notes = [], raw = {};
  for (const [i, t] of lay.notes || []) if (i < 0) notes.push([-1, t]);
  const before = {};
  for (const [i, t] of lay.notes || []) if (i >= 0) (before[i] = before[i] || []).push(t);
  let k = 0;
  for (const n of nodes) {
    if (n.orig !== null) for (const t of before[n.orig] || []) notes.push([k, t]);
    if (n.del) continue;
    if (n.orig !== null && n.row === base[n.orig]) {
      const text = (lay.raw || {})[n.orig] !== undefined ? lay.raw[n.orig] : csvRow(n.row, lay.cols);
      if (text !== csvRow(n.row, cols)) raw[String(k)] = text;
    }
    k++;
  }
  for (const t of before[lay.n] || []) notes.push([k, t]);
  out.n = k;
  if (notes.length) out.notes = notes;
  if (Object.keys(raw).length) out.raw = raw;
  if (lay.bom) out.bom = true;
  if (lay.open) out.open = true;
  return out;
}

/** A row as a file holds it: its cells trimmed, blank ones left out, in the file's column order. */
function tidyRow(row, cols) {
  const out = {};
  const keys = cols.concat(Object.keys(row).filter(k => cols.indexOf(k) < 0));
  for (const k of keys) {
    const v = row[k] === undefined || row[k] === null ? '' : String(row[k]).trim();
    if (v !== '') out[k] = v;
  }
  return out;
}

/**
 * Lay `edits` over `data`'s tables, from the tables as the page came (`orig`,
 * path -> table, filled in as tables are first changed).  The churches'
 * colors, season colors and reading settings, which the page keeps worked
 * out (export_data.py: profile), follow the files they come from.
 */
function applyEdits(data, edits, orig) {
  const paths = new Set(Object.keys(orig));
  for (const e of edits) paths.add(e.p);
  const nodes = {};
  for (const path of paths) {
    const t = tableAt(data, path);
    if (!t) continue;
    if (orig[path] === undefined) orig[path] = t.get();
    const base = orig[path];
    const ops = edits.filter(e => e.p === path);
    if (!ops.length) { t.set(base); continue; }
    nodes[path] = editNodes(tableRows(t, base), ops);
    const rows = nodes[path].filter(n => !n.del).map(n => n.row);
    t.set(t.packed ? CY.packRows(rows) : rows);
  }
  refreshProfiles(data, Array.from(paths));
  return nodes;
}

/** The churches' colors, season colors and reading settings again, after their files changed. */
function refreshProfiles(data, paths) {
  const named = name => paths.some(p => p === name || p.slice(-name.length - 1) === '/' + name);
  if (!named('colors.csv') && !named('seasons.csv') && !named('tradition.csv')) return;
  for (const t of data.traditions) {
    const p = data.profiles[t.key], folder = data.folders[t.folder];
    if (!p || !folder) continue;
    if (paths.some(x => x === 'colors.csv' || x === t.folder + '/colors.csv' || x === t.folder + '/seasons.csv')) {
      // church_year_image.py: load_colors, load_season_colors.
      const colors = {};
      for (const r of (data.colorRows || []).concat(folder.colors || [])) {
        const name = String(r.name || '').trim().toUpperCase();
        if (name) colors[name] = { name: name, fill: String(r.fill || '').trim() || '#ffffff', text: String(r.text || '').trim() || '#000000' };
      }
      const seasons = {};
      for (const r of folder.seasons || []) {
        const season = String(r.season || '').trim().toUpperCase();
        const parts = String(r.color || '').split(';');
        const key = parts[0].trim().toUpperCase();
        if (!season || !key || !colors[key]) continue;
        const alt = parts.slice(1).map(a => a.trim()).filter(Boolean).join('; ');
        seasons[season] = key + (alt ? '; ' + alt : '');
      }
      p.colors = colors;
      p.seasonColors = seasons;
    }
    if (paths.indexOf(t.folder + '/tradition.csv') >= 0) {
      const own = CY.traditionSettings(data, t);
      for (const k of ['reading_order', 'reading_labels', 'reading_propers']) {
        p.settings[k] = k in own ? String(own[k]).trim() : (data.settings || {})[k] || '';
      }
    }
  }
}

/** The changes written into a page's own tables and layouts (Make a page). */
function bakeEdits(data, edits) {
  const paths = Array.from(new Set(edits.map(e => e.p)));
  const lays = {};
  for (const path of paths) {
    const t = tableAt(data, path), lay = layoutOf(data, path);
    if (!t || !lay) continue;
    const base = tableRows(t, t.get());
    lays[path] = relayout(lay, editNodes(base, edits.filter(e => e.p === path)), base);
  }
  applyEdits(data, edits, {});
  data.csv = Object.assign({}, data.csv || {}, lays);
  const was = Array.isArray(data.edited) ? data.edited : [];
  data.edited = was.concat(paths.filter(p => lays[p] && was.indexOf(p) < 0)).sort();
}

// The changes kept in this browser for this page (the file where it is), with
// a mark of the page they were made on, so a page made over this one does not
// take changes meant for the one before it.
const EDIT_KEY = 'cy-edits:' + location.pathname;
const EDIT_SIG = (() => {
  const text = PRISTINE.app;
  let h = 2166136261;
  for (let i = 0; i < text.length; i += 61) h = Math.imul(h ^ text.charCodeAt(i), 16777619) >>> 0;
  return text.length.toString(36) + '.' + h.toString(36);
})();
let EDITS = [];
let EDITS_SET_ASIDE = 0;      // changes kept for an earlier form of this page, not used
const EDIT_ORIG = {};
let EDIT_NODES = {};
try {
  const kept = JSON.parse(localStorage.getItem(EDIT_KEY) || 'null');
  if (kept && kept.sig === EDIT_SIG && Array.isArray(kept.edits)) EDITS = kept.edits;
  else if (kept && Array.isArray(kept.edits)) EDITS_SET_ASIDE = kept.edits.length;
} catch (err) { /* none kept */ }
try { EDIT_NODES = applyEdits(DATA, EDITS, EDIT_ORIG); } catch (err) { EDITS = []; EDIT_NODES = applyEdits(DATA, EDITS, EDIT_ORIG); }

const svg = app.querySelector('.stage > svg');
const art = $('art');
const rotor = $('rotor');
const center = $('center');
let centerRadius = null;   // the radius the artwork in it was drawn for
const hiUnder = $('hiUnder');
const hiOver = $('hiOver');
const box = $('pick');
const yearBox = $('yearBox');
const tradBox = $('tradition');
const churchBox = $('church');
const seriesBox = $('series');
const seriesRow = $('seriesRow');
const seriesLabel = $('seriesLabel');
const bookBox = $('book');
const bookRow = $('bookRow');
const bookLabel = $('bookLabel');
const subRows = $('subRows');
const latinBox = $('latin');
const latinRow = $('latinRow');
const readingsBox = $('readings');
const readingsRow = $('readingsRow');
// The Readings boxes, one for each kind of set (CY.READING_CATEGORIES).
const readingBoxes = Array.from(readingsRow.querySelectorAll('input[data-reading]'));
const bibleBox = $('bibleVersion');
const siteBox = $('bibleSite');
const bibleRow = $('bibleRow');
const bibleSiteRow = $('bibleSiteRow');
const w2wBox = $('w2w');
const hymnsBox = $('hymns');
const layoutBox = $('readingsLayout');
const layoutRow = $('layoutRow');
// The columns' slide (slideSets): its speed in milliseconds, 0 for none.
// The reader's own choice, kept in this browser only.
const slideBox = $('slideSpeed'), slideRow = $('slideRow');
const SLIDE_KEY = 'cy-readings-slide';
slideBox.value = '700';
try { pick(slideBox, localStorage.getItem(SLIDE_KEY)); } catch (err) { /* the medium speed */ }
slideBox.addEventListener('change', () => { try { localStorage.setItem(SLIDE_KEY, slideBox.value); } catch (err) { /* not kept */ } });
// How the readings are laid out when a day has several sets
// (church_year.py --readings-layout / page_readings_layout): tabs or
// columns; a page offering both has the menu, the first opening.
const layoutsOffered = () => (Array.isArray(DATA.readingsLayout) && DATA.readingsLayout.length
  ? DATA.readingsLayout : ['tabs', 'columns']);
const layoutDefault = () => layoutsOffered()[0];
const layoutNow = () => (layoutsOffered().length > 1 ? layoutBox.value : layoutDefault());
// The slide is the columns' own, so its speed is offered only beside them.
function syncSlideRow() { slideRow.hidden = !hasReadings() || layoutNow() !== 'columns'; }
const w2wRow = $('w2wRow');
const hymnsRow = $('hymnsRow');
const propersBox = $('propers'), propersRow = $('propersRow');
const hymnalBox = $('hymnal'), hymnalRow = $('hymnalRow');
const artBox = $('artwork');
const credit = $('credit');
const calBox = $('calendar');
const paschalionBox = $('paschalion');
const feastBox = $('feasts');
const darkReds = $('darkReds');
const yearLineBox = $('yearLine');
// Whether the arrow keys go on into the next year at the year's end, or round
// the year on the wheel (config.csv page_arrows_next_year, --arrows-same-year).
const arrowsBox = $('arrowsOn');
const arrowsDefault = () => !!DATA.arrowsNext;
// The thicker line where the year ends and begins (config.csv year_line).
const yearLineDefault = () => CY.truthy(DATA.settings.year_line);
// The page's box sets mid_text to dark-reds; unchecked it is config.csv's choice
// (or as-set when that choice is dark-reds itself).
const midDefault = () => String(DATA.settings.mid_text || 'as-set');
const midValue = () => (darkReds.checked ? 'dark-reds'
                        : (midDefault() === 'dark-reds' ? 'as-set' : midDefault()));
const settings = $('settings');
const gear = $('gear');
// Simple or All settings: Simple puts away the rows that are set once, if
// ever (the template marks them .adv).  The reader's own choice, kept in this
// browser only; a page opens Simple.
const panel = settings.querySelector('.panel');
const VIEW_KEY = 'cy-settings-view';
const viewButtons = Array.from(panel.querySelectorAll('.viewrow button'));
function setView(view, keep) {
  const simple = view !== 'all';
  panel.classList.toggle('simple', simple);
  for (const b of viewButtons) b.setAttribute('aria-pressed', String((b.dataset.view === 'all') !== simple));
  if (keep) { try { localStorage.setItem(VIEW_KEY, simple ? 'simple' : 'all'); } catch (err) { /* not kept */ } }
  tidyHeads();
}
/** A heading stands only over rows that are shown: it goes when every row down to the next heading or group is hidden. */
function tidyHeads() {
  for (const head of panel.querySelectorAll(':scope > .head')) {
    let shown = false;
    for (let el = head.nextElementSibling; el && !el.matches('.head, .group, .reset'); el = el.nextElementSibling) {
      if (!el.hidden && !(el.classList.contains('rows') && !el.children.length)) { shown = true; break; }
    }
    head.hidden = !shown;
  }
}
for (const b of viewButtons) b.addEventListener('click', () => setView(b.dataset.view, true));
{
  let view = 'simple';
  try { view = localStorage.getItem(VIEW_KEY) || view; } catch (err) { /* Simple */ }
  setView(view, false);
}
// The rows come and go with the church; the headings follow when the panel opens or anything in it changes.
settings.addEventListener('toggle', tidyHeads);
panel.addEventListener('change', () => setTimeout(tidyHeads, 0));
const ringList = $('ringList');
const colorsBtn = $('colorsBtn');
const colorDialog = $('colorDialog');
const dayColors = $('dayColors');
const ringColors = $('ringColors');
const colorsReset = $('colorsReset');
// The Colors menu's changes, for this page only: fills of the day colors by
// name, for every church (`days`), a tradition (`traditions`: slug -> name ->
// fill) or one church (`churches`: key -> name -> fill, with the tradition
// its change named in `churchTrad`), the nearer winning; ring fills and ring
// text by ring key; and the cells outside the year.
const colorOverrides = { days: {}, traditions: {}, churches: {}, churchTrad: {}, rings: {}, ringText: {}, empty: '' };
/** A tradition as a color change names it: Church of the East -> church-of-the-east. */
const tradSlug = name => String(name || '').trim().toLowerCase().replace(/\s+/g, '-');
/** The day colors changed for this church: every church's changes, then its tradition's. */
function dayOverridesFor(key) {
  return Object.assign({}, colorOverrides.days, colorOverrides.traditions[tradSlug(traditionOf(key).tradition)] || {},
                       colorOverrides.churches[key] || {});
}
let lastBuilt = null;
const zoomG = $('zoom');
const stage = app.querySelector('.stage');
const mag = $('mag');
const magOut = $('magOut');
const when = $('when');
const what = $('what');
const dot = $('dot');
const nowBtn = $('now');
const headYear = $('headYear');
const headChurch = $('headChurch');
const note = $('note');
const timing = $('timing');
const copyBtn = $('copyLink');
const printBtn = $('printBtn');
const resetBtn = $('resetBtn');

// Whether the wheel is the whole page -- its own file, or the fragment alone in
// a host's page skeleton -- or one part of someone else's page.  Only a wheel
// that owns the page retitles the tab, writes the address bar, answers the
// keyboard wherever the focus is, and stops the page scrolling.  The full page
// says so in its markup; a fragment is judged once the page has loaded, since
// whatever follows the wheel has not been read yet while this script runs.
const QUIET = /^(SCRIPT|STYLE|TITLE|LINK|META|NOSCRIPT|TEMPLATE)$/;
const quiet = el => QUIET.test(el.tagName) || el.tagName.indexOf('-') >= 0 || el.hidden;
function ownsPage() {
  if (document.documentElement.classList.contains('cy-page')) return true;
  for (let node = app; node !== document.body; node = node.parentElement) {
    if (!node || !node.parentElement) return false;
    for (const other of node.parentElement.children) {
      if (other !== node && !quiet(other)) return false;
    }
  }
  return true;
}
let owned = null;                      // settled at the end, once the page is read
let pageTitle = document.title;

// How far the wheel will go.
//
// 9998 is the last church year whose final day still falls in a four-digit
// year, which is as far as an ISO date, a date box, and Python's own date type
// will go.
//
// Downwards there is no such wall, only meaning.  The Gregorian calendar began
// in October 1582, and 1582 is the first church year lying wholly inside it.
// Below that the wheel is running the modern rules backwards over a calendar
// nobody kept -- interesting, but an extrapolation, and the page says so.
const FIRST_YEAR = -9999, LAST_YEAR = 9998;
const GREGORIAN_YEAR = 1582;

// Years 1 to 9999 are the only ones a native date box can express.
const PICKABLE_FIRST = '0001-01-01', PICKABLE_LAST = '9999-12-31';

let G = null, DAYS = {}, READINGS = {}, dates = [], bandHeight = 0;
let turned = 0, chosen = null, drawn = null, drawnIn = '', paschalionName = 'Gregorian';
let magnify = 1;                       // 1 = the whole wheel in view
let panX = 0, panY = 0;                // offset in the wheel's own coordinates
let dragFrom = null, dragged = false;  // pointer drag, and whether it moved
const touches = new Map();             // fingers on the wheel, by pointer id
let pinch = null;                      // the two-finger gesture in progress
let quietUntil = 0;                    // swallow the click a pinch can leave behind
const hiddenRings = {};                // rings switched off from the menu

const rad = d => d * Math.PI / 180;
const pt = (r, a) => [G.cx + r * Math.cos(rad(a)), G.cy + r * Math.sin(rad(a))];

// Today is a moment, not a label: CY.todayDay finds the day through the
// Gregorian calendar the browser clock speaks, and iso() names it in whatever
// calendar the wheel is currently drawn in.
const isoToday = () => CY.iso(CY.todayDay());

/**
 * The year whose church year contains this date: its Advent year, for most
 * traditions, or the year of the September that begins it, for the Orthodox.
 */
function adventYearFor(iso) {
  return CY.yearFor(DATA, currentTradition(), CY.fromIso(iso));
}

// ---------------------------------------------------------------------------
// The lines under the wheel (page_footer in config.csv, --footer)
// ---------------------------------------------------------------------------

const hint = $('hint');
const infoBtn = $('infoBtn');
const showHelp = $('showHelp');
const showCredit = $('showCredit');
let lastArt = null;
/** What page_footer (or --footer) asks to show: full, credit or none. */
const footDefaults = () => {
  const mode = DATA.footer || 'full';
  return { help: mode === 'full', credit: mode !== 'none' };
};
/**
 * The lines under the wheel, as the two boxes in the panel say.  With the
 * credit off, artwork whose license requires credit keeps a small (i) that
 * opens it, and the credit is still printed.
 */
function applyFooter(art) {
  if (art !== undefined) lastArt = art;
  const required = !!lastArt && /^(required|yes|true)$/i.test(String(lastArt.attribution || ''));
  const help = showHelp.checked, cred = showCredit.checked;
  hint.classList.toggle('req', required);
  hint.classList.toggle('no-help', !help);
  hint.classList.toggle('no-credit', !cred);
  hint.classList.toggle('foot-info', !help && !cred && required);
  hint.classList.toggle('foot-none', !help && !cred && !required);
  infoBtn.hidden = cred || !required;
  if (infoBtn.hidden) { hint.classList.remove('open'); infoBtn.setAttribute('aria-expanded', 'false'); }
}
showHelp.addEventListener('change', () => { applyFooter(); markChanged(); syncLink(); });
showCredit.addEventListener('change', () => { applyFooter(); markChanged(); syncLink(); });
infoBtn.addEventListener('click', () => {
  const open = hint.classList.toggle('open');
  infoBtn.setAttribute('aria-expanded', String(open));
});

// ---------------------------------------------------------------------------
// The traditions, and the menus that follow from the one chosen
// ---------------------------------------------------------------------------

const byLabel = (a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' });
const TRADITIONS = DATA.traditions;
const traditionOf = key => TRADITIONS.find(t => t.key === key) || TRADITIONS[0];
const profileOf = key => DATA.profiles[key] || DATA.profiles[DATA.defaultTradition];

// Three menus: the Tradition (Lutheran, Catholic, Orthodox...), the Church
// within it, and -- for a church with more than one calendar -- the series or
// prayer book.
const uniq = xs => xs.filter((x, i) => xs.indexOf(x) === i);

function buildTraditionMenu() {
  const names = uniq(TRADITIONS.map(t => t.tradition)).sort(byLabel);
  tradBox.replaceChildren(...names.map(n => new Option(n, n)));
  // A page made for some churches only hides a menu with nothing to choose.
  $('tradRow').hidden = names.length < 2;
  $('churchRow').hidden = uniq(TRADITIONS.map(t => t.tradition + '|' + t.church)).length < 2;
  // ... and a setting it was made without (page_fixed, --fixed) keeps each church's own.
  $('calRow').hidden = isFixed('calendar');
  $('easterRow').hidden = isFixed('easter');
  $('artRow').hidden = isFixed('artwork') || (DATA.artworkOrder || []).length < 2;
  $('redsRow').hidden = isFixed('reds');
}
/** Whether the page was made with this setting left out (calendar, easter, artwork, reds). */
function isFixed(name) { return (DATA.fixed || []).indexOf(name) >= 0; }

/**
 * A church's name in the Church menu.  A church with a single calendar has
 * no menu after it to name its book, so the book goes with its name:
 * "Church in Wales (BCP 1984)", "ACNA (Anglican Church in North America,
 * BCP 2019)".
 */
function churchName(name) {
  const rows = TRADITIONS.filter(t => t.tradition === tradBox.value && t.church === name);
  if (rows.length !== 1 || !rows[0].series) return name;
  const book = rows[0].series;
  return /\)$/.test(name) ? name.replace(/\)$/, ', ' + book + ')') : name + ' (' + book + ')';
}

function buildChurchMenu() {
  const keep = churchBox.value;
  const names = uniq(TRADITIONS.filter(t => t.tradition === tradBox.value).map(t => t.church))
    .sort(byLabel);
  churchBox.replaceChildren(...names.map(n => new Option(churchName(n), n)));
  // A new tradition opens on its first church in traditions.csv.
  const first = TRADITIONS.find(t => t.tradition === tradBox.value);
  if (first) churchBox.value = first.church;
  pick(churchBox, keep);
}

/** The calendars of the chosen church: one, or several to choose between. */
const churchRows = () => TRADITIONS.filter(t => t.tradition === tradBox.value &&
                                                t.church === churchBox.value);

// A church whose calendar changed with its books (the LCMS: LSB, LW, TLH)
// has a menu of them; the series menu then lists that book's calendars.
function buildBookMenu() {
  const keep = bookBox.value;
  const rows = churchRows();
  const books = uniq(rows.map(t => t.book || ''));
  bookBox.replaceChildren(...books.map(b => new Option(b || '\u2014', b)));
  pick(bookBox, keep);
  bookRow.hidden = books.length < 2;
  bookLabel.textContent = (rows.find(t => t.bookMenu) || {}).bookMenu || 'Hymnal';
}

const bookRows = () => churchRows().filter(t => (t.book || '') === (bookBox.value || ''));

// The series last chosen from a menu that offered more than one, so that
// passing through a book or church with only one (LW, TLH) and back keeps it.
let wantedSeries = '';

function buildSeriesMenu() {
  const rows = bookRows();
  const shown = seriesBox.selectedOptions[0] && !seriesRow.hidden ? seriesBox.selectedOptions[0].text : '';
  const keepLabel = shown || wantedSeries;
  // Listed A to Z; a book still opens on its first series in traditions.csv.
  const listed = rows.slice().sort((a, b) => byLabel(a.series || a.label, b.series || b.label));
  seriesBox.replaceChildren(...listed.map(t => new Option(t.series || t.label, t.key)));
  if (rows.length) seriesBox.value = rows[0].key;
  const same = rows.find(t => t.series && t.series === keepLabel);
  if (same) seriesBox.value = same.key;
  // A menu with a single entry has nothing to choose: it is left out.
  seriesRow.hidden = rows.length < 2;
  seriesLabel.textContent = (rows.find(t => t.seriesMenu) || {}).seriesMenu || 'Series';
  if (rows.length > 1 && seriesBox.selectedOptions[0]) wantedSeries = seriesBox.selectedOptions[0].text;
}

function currentTradition() {
  return seriesBox.value || (bookRows()[0] || churchRows()[0] || TRADITIONS[0]).key;
}

/** Point the menus at a tradition, by key. */
function setTradition(key) {
  const t = traditionOf(String(key || '').trim().toLowerCase());
  pick(tradBox, t.tradition);
  buildChurchMenu();
  pick(churchBox, t.church);
  buildBookMenu();
  pick(bookBox, t.book || '');
  buildSeriesMenu();
  pick(seriesBox, t.key);
  if (!seriesRow.hidden && t.series) wantedSeries = t.series;
  buildSubMenus();
}

/**
 * The calendars that can be laid over the chosen tradition, one menu for each
 * kind (national, religious order, personal jurisdiction), each A to Z with
 * None first.  Only a tradition that has them shows them.
 */
let subFolder = null;
function buildSubMenus() {
  const t = traditionOf(currentTradition());
  latinRow.hidden = !/^(true|1|yes|y|on)$/i.test(
    String(CY.traditionSettings(DATA, t).latin_names_available || ''));
  readingsRow.hidden = !hasReadings();
  const kinds = readingKindsOf(currentTradition());
  for (const b of readingBoxes) b.parentElement.hidden = kinds.indexOf(b.dataset.reading) < 0;
  bibleSiteRow.hidden = !hasReadings() || !bibleLinks;
  w2wRow.hidden = !hasReadings() || w2wOff();
  hymnsRow.hidden = !hasReadings() || hymnaryOff() || !hymnalOf(currentTradition());
  // The parts of the service a church lists with its readings: the box names them.
  const parts = propersOf(currentTradition());
  propersRow.hidden = !hasReadings() || !parts.length;
  $('propersName').textContent = 'Propers' + (parts.length ? ' (' + parts.map(k => kindLabel(currentTradition(), k)).join(', ') + ')' : '');
  // A church with several hymnals: the Hymnal menu, keeping the one chosen.
  const hymnals = hymnalsOf(currentTradition());
  const keep = hymnalBox.value;
  hymnalBox.replaceChildren(...hymnals.map(h => new Option(h.name || h.code, h.code)));
  if (hymnals.some(h => h.code === keep)) hymnalBox.value = keep;
  else hymnalBox.value = hymnalDefault();
  hymnalRow.hidden = hymnsRow.hidden || hymnals.length < 2;
  layoutRow.hidden = !hasReadings() || layoutsOffered().length < 2;
  syncSlideRow();
  bibleRow.hidden = !hasReadings() || bibleFixed() || !bibleLinks;
  if (t.folder === subFolder) return;
  subFolder = t.folder;
  const folder = DATA.folders[t.folder] || { subcalendars: [] };
  const menus = [];
  for (const s of folder.subcalendars) {
    let m = menus.find(x => x.menu === s.menu);
    if (!m) { m = { menu: s.menu, label: s.menuLabel || s.menu, items: [] }; menus.push(m); }
    m.items.push(s);
  }
  subRows.replaceChildren(...menus.map(m => {
    const row = document.createElement('label');
    const select = document.createElement('select');
    select.dataset.menu = m.menu;
    select.appendChild(new Option('None', ''));
    for (const s of m.items.slice().sort((a, b) => byLabel(a.label, b.label))) {
      select.appendChild(new Option(s.label, s.key));
    }
    select.addEventListener('change', () => redrawSameDay());
    row.appendChild(document.createTextNode(m.label));
    row.appendChild(select);
    return row;
  }));
}

const subSelects = () => Array.from(subRows.querySelectorAll('select'));
const chosenSubs = () => subSelects().map(s => s.value).filter(Boolean);

/** Put the subcalendar menus on these keys, each in whichever menu offers it. */
function setSubs(keys) {
  for (const select of subSelects()) {
    select.value = '';
    for (const k of keys) pick(select, k);
  }
}

/** Whether this page has a picture for any season (season_art.csv), and so can offer By season. */
const hasSeasonArt = () => (DATA.seasonArt || []).some(r => r.art && DATA.artwork[r.art]);
/**
 * The order of the Artwork menus: the pictures A to Z, then the seasons'
 * pictures (season_art.csv) at the foot, in the order of the church year as
 * that file first names them (Advent's four wreaths, Christmas ... Pentecost).
 */
function artOrder(x, y) {
  const seasons = [];
  for (const r of DATA.seasonArt || []) if (r.art && seasons.indexOf(r.art) < 0) seasons.push(r.art);
  const i = seasons.indexOf(x.key), j = seasons.indexOf(y.key);
  if (i < 0 && j < 0) return byLabel(x.label, y.label);
  if (i < 0 || j < 0) return i < 0 ? -1 : 1;
  return i - j;
}

/** The Artwork menu: the tradition's own, by season, then every picture A to Z. */
function buildArtMenu() {
  const items = (DATA.artworkOrder || []).map(k => ({ key: k, label: DATA.artwork[k].label || k }))
                                         .sort(artOrder);
  artBox.replaceChildren(new Option("The tradition's own", 'auto'),
                         ...(hasSeasonArt() ? [new Option('By season', 'season')] : []),
                         ...items.map(i => new Option(i.label, i.key)));
  if (localArt) artBox.insertBefore(new Option(localArt + ' (beside this page)', 'local'), artBox.options[1]);
}

// ---------------------------------------------------------------------------
// A picture beside the page: center.svg (or .png, .jpg, .webp) in the folder
// the page was opened from is offered in the Artwork menu, and the page opens
// on it.  It is looked for when the page opens; nothing is uploaded anywhere.
// ---------------------------------------------------------------------------

const LOCAL_ART = ['center.svg', 'center.png', 'center.jpg', 'center.jpeg', 'center.webp', 'center.gif'];
let localArt = '';

/** Find the first of LOCAL_ART that loads, then call back with its name (or ''). */
function findLocalArt(done) {
  let i = 0;
  const next = () => {
    if (i >= LOCAL_ART.length) { done(''); return; }
    const name = LOCAL_ART[i++];
    const img = new Image();
    img.onload = () => done(name);
    img.onerror = next;
    img.src = name;
  };
  try { next(); } catch (e) { done(''); }
}

/** Draw the picture beside the page in the middle, cut to the center circle. */
function drawLocalArt(radius) {
  if (!localArt || !G) return;
  const ns = 'http://www.w3.org/2000/svg';
  const r = radius * 0.97;
  const clip = document.createElementNS(ns, 'clipPath');
  clip.id = 'cy-local-art-clip';
  const circle = document.createElementNS(ns, 'circle');
  circle.setAttribute('cx', G.cx); circle.setAttribute('cy', G.cy); circle.setAttribute('r', r);
  clip.appendChild(circle);
  const img = document.createElementNS(ns, 'image');
  img.setAttribute('href', localArt);
  img.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', localArt);
  img.setAttribute('x', G.cx - r); img.setAttribute('y', G.cy - r);
  img.setAttribute('width', 2 * r); img.setAttribute('height', 2 * r);
  // A drawing is shown whole; a photo fills the circle.
  img.setAttribute('preserveAspectRatio', /\.svg$/i.test(localArt) ? 'xMidYMid meet' : 'xMidYMid slice');
  img.setAttribute('clip-path', 'url(#cy-local-art-clip)');
  const defs = document.createElementNS(ns, 'defs');
  defs.appendChild(clip);
  center.append(defs, img);
}

/** Say whose the artwork in the middle is, and under what license: its license asks for this. */
function syncCredit(key) {
  // A picture of the user's own has a credit only when one was given.
  const own = DATA.artwork[key];
  const art = own && !(own.own && !own.title && !own.author && !own.license) ? own : null;
  credit.replaceChildren();
  applyFooter(art);
  if (!art) return;
  const link = (text, href) => {
    if (!href) return document.createTextNode(text);
    const a = document.createElement('a');
    a.href = href; a.textContent = text; a.target = '_blank'; a.rel = 'noopener';
    return a;
  };
  credit.append('Artwork: ', link(art.title || art.label, art.sourceUrl));
  if (art.author) credit.append(CY.byAuthor(art.author));
  if (art.license) credit.append(', ', link(art.license, art.licenseUrl));
  if (art.changes && art.changes !== 'none') credit.append(' (' + art.changes + ')');
}

/** The Advent year currently on the wheel, taken from what was drawn. */
const drawnYear = () => (drawn === null ? NaN : parseInt(drawn, 10));

function parseChildren(markup) {
  const doc = new DOMParser().parseFromString(
    '<svg xmlns="' + NS + '" xmlns:xlink="http://www.w3.org/1999/xlink">'
    + markup + '</svg>', 'image/svg+xml');
  if (doc.querySelector('parsererror')) throw new Error('the drawing would not parse');
  // adoptNode, not importNode: importNode copies the node and leaves the
  // original in place, so draining the parsed document this way never ends.
  const frag = document.createDocumentFragment();
  let node;
  while ((node = doc.documentElement.firstChild) !== null) {
    frag.appendChild(document.adoptNode(node));
  }
  return frag;
}

/** Draw a church year and put it on the wheel. */
// The picker carries both axes at once: the wheel offers the pairings churches
// actually keep, while config.csv can still set the two independently.
// Two independent axes: how a day is named, and where Easter falls.  Left
// blank, the paschalion follows the calendar -- a Julian wheel with a Western
// Easter is nobody's practice, so it is not what an unattended choice gives.
const chosenCalendar = () => calBox.value;
const chosenPaschalion = () => paschalionBox.value;

const ringKey = () => Object.keys(hiddenRings).filter(k => hiddenRings[k]).sort().join(',');
/** The rings a page opens with turned off (church_year.py --hide / page_hide). */
const hiddenDefault = () => (Array.isArray(DATA.hiddenDefault) ? DATA.hiddenDefault : []);
const hiddenDefaultKey = () => hiddenDefault().slice().sort().join(',');
function setHidden(keys) {
  for (const k in hiddenRings) delete hiddenRings[k];
  const known = {};
  for (const r of DATA.rings) if (!FIXED[r.kind]) known[r.key] = true;
  for (const k of keys) if (k && known[k]) hiddenRings[k] = true;
  for (const b of ringList.querySelectorAll('input[data-ring]')) {
    if (!b.disabled) b.checked = !hiddenRings[b.dataset.ring];
  }
}

const drawKey = year => year + '|' + currentTradition() + '|' + chosenSubs().join(',')
                      + '|' + latinBox.checked
                      + '|' + calBox.value + '|' + paschalionBox.value
                      + '|' + feastBox.value + '|' + midValue() + '|' + yearLineBox.checked + '|' + artBox.value
                      + '|' + ringKey() + '|' + colorsParam();

/** What the wheel is drawn with: the year and every setting behind the gear. */
function drawOptions(adventYear) {
  return { year: adventYear, tradition: currentTradition(),
           subcalendars: chosenSubs(),
           latinNames: latinBox.checked,
           calendar: chosenCalendar(),
           paschalion: chosenPaschalion(),
           feastDetail: feastBox.value,
           midText: midValue(),
           yearLine: yearLineBox.checked,
           hiddenRings: hiddenRings,
           colorOverrides: { days: dayOverridesFor(currentTradition()), rings: colorOverrides.rings,
                             ringText: colorOverrides.ringText, empty: colorOverrides.empty },
           // By season: the church's own, and the middle is changed for the day chosen (showCenter).
           art: artBox.value === 'auto' || artBox.value === 'season' ? 'auto'
                : (artBox.value === 'local' ? 'none' : artBox.value) };
}

/**
 * The picture in the middle, for the day chosen.
 *
 * It stays out of the part that turns and is redrawn only when it changes:
 * hiding a ring pulls the rings in and widens the middle, and artwork left at
 * the old radius would sit in a ring-shaped gap of its own.  With Artwork: By
 * season it is the picture of the chosen day's season (the day index's `A`),
 * or the church's own in a season that has none; each season's is drawn once
 * for the wheel that is up and kept.
 */
let centerCache = {};
function showCenter(iso) {
  const built = lastBuilt;
  if (!built) return;
  const key = (artBox.value === 'season' && (DAYS[iso] || {}).A) || built.art;
  const centerKey = built.geometry.centerRadius + '|' + key + '|' + artBox.value;
  if (centerKey === centerRadius) return;
  let markup = key === built.art ? built.center : centerCache[key];
  if (markup === undefined) {
    markup = centerCache[key] = CY.build(DATA, Object.assign(drawOptions(drawnYear()), { art: key })).center;
  }
  center.replaceChildren(parseChildren(markup));
  if (artBox.value === 'local') drawLocalArt(built.geometry.centerRadius);
  centerRadius = centerKey;
  syncCredit(artBox.value === 'local' ? '' : key);
}

function drawYear(adventYear, iso) {
  const tradition = currentTradition();
  const key = drawKey(adventYear);
  if (key !== drawn) {
    const started = performance.now();
    const built = CY.build(DATA, drawOptions(adventYear));
    art.replaceChildren(parseChildren(built.turning));
    G = built.geometry;
    // The middle is drawn by choose(), for the day it lands on (showCenter).
    lastBuilt = built;
    centerCache = {};
    if (colorDialog.open) buildColorMenu();
    DAYS = built.days;
    READINGS = built.readings || {};
    dates = Object.keys(DAYS).sort((a, b) => CY.fromIso(a) - CY.fromIso(b));
    bandHeight = (G.rOuter - G.rInner) / G.bands;
    const name = traditionOf(tradition).label;
    // Two lines: the year, and under it the church, which can be long.
    headYear.textContent = 'Church Year ' + built.label;
    headChurch.textContent = name;
    headChurch.title = name;
    pageTitle = 'Church Year ' + built.label + ' \u00b7 ' + name;
    if (owned) document.title = pageTitle;
    yearBox.value = adventYear;
    paschalionName = built.paschalion === 'julian' ? 'Julian' : 'Gregorian';
    // From the file's own ring list, not the drawing's: a ring hidden by a link
    // is missing from what was drawn but still belongs in the menu.
    buildRingMenu(DATA.rings.filter(r => r.enabled));
    markChanged();
    drawn = key;

    const shrunk = built.warnings.filter(w => w.message.indexOf('does not fit') >= 0);
    drawnIn = 'Drawn in ' + Math.round(performance.now() - started) + ' ms'
      + (shrunk.length ? ' · ' + shrunk.length + ' label(s) did not fit' : '');

    // The wheel under the highlight is a different drawing now, so spinning
    // from the old year's angle would animate a journey that means nothing.
    rotor.style.transition = 'none';
    choose(landingDate(iso), true);
    rotor.getBoundingClientRect();
    rotor.style.transition = '';
    return;
  }
  choose(landingDate(iso), true);
}

/**
 * Which day to light up in the year just drawn.  Asking for a year the reader
 * typed must not bounce straight back to today's year, so today is used only
 * when it falls inside the year now on the wheel.
 */
function landingDate(iso) {
  if (iso && DAYS[iso]) return iso;
  const today = isoToday();
  return DAYS[today] ? today : dates[0];
}

// `grow` pushes the outline just outside the cell, so the ring of stroke
// frames the day rather than covering its number.
function wedge(info, grow) {
  // On the cell's own outline, so the frame covers no more of the cells
  // beside it than of its own (a long name runs close to the edge).
  grow = grow === undefined ? 0 : grow;
  const half = grow / ((G.rOuter - info.b * bandHeight) - bandHeight / 2) * 180 / Math.PI;
  const a0 = G.startAngle + info.w * G.anglePerWeek - half;
  const a1 = G.startAngle + (info.w + 1) * G.anglePerWeek + half;
  const rO = G.rOuter - info.b * bandHeight + grow, rI = rO - bandHeight - 2 * grow;
  const xy = p => p[0] + ' ' + p[1];
  return 'M ' + xy(pt(rO, a0))
       + ' A ' + rO + ' ' + rO + ' 0 0 1 ' + xy(pt(rO, a1))
       + ' L ' + xy(pt(rI, a1))
       + ' A ' + rI + ' ' + rI + ' 0 0 0 ' + xy(pt(rI, a0)) + ' Z';
}

// Turn the shortest way round, so stepping across the New Year does not spin
// the wheel the long way about.
function faceUp(info) {
  const mid = G.startAngle + (info.w + 0.5) * G.anglePerWeek;
  const target = 270 - mid;
  turned += ((target - turned) % 360 + 540) % 360 - 180;
  rotor.style.transform = 'rotate(' + turned + 'deg)';
}

/** A Date carrying exactly these calendar fields, whatever the year. */
function utcOn(y, m, d) {
  const at = new Date(Date.UTC(2000, m - 1, d, 12));
  at.setUTCFullYear(y);                    // years 0-99 would land in the 1900s
  return at;
}

function pretty(iso) {
  const day = CY.fromIso(iso);
  const options = { weekday: 'long', year: 'numeric', month: 'long',
                    day: 'numeric', timeZone: 'UTC' };
  // Say the era only where it is in doubt, so ordinary dates are not shouted at.
  if (day < CY.fromIso(PICKABLE_FIRST)) options.era = 'short';

  const here = CY.reckoningNow();
  const named = here.fromDay(day);
  if (here === CY.GREGORIAN) return utcOn(named.y, named.m, named.d)
    .toLocaleDateString(undefined, options);

  // Outside the Gregorian calendar the label and the weekday come from
  // different places: the month and year are what this calendar calls the day,
  // while the weekday belongs to the day itself and is the same in every
  // calendar.  Formatting the label as if it were Gregorian would name the
  // wrong weekday, so the two are formatted apart and joined.
  const weekday = new Intl.DateTimeFormat(undefined, { weekday: 'long', timeZone: 'UTC' })
    .format(utcOn(CY.gregorianOf(day).y, CY.gregorianOf(day).m, CY.gregorianOf(day).d));
  const rest = Object.assign({}, options);
  delete rest.weekday;
  const label = utcOn(named.y, named.m, named.d).toLocaleDateString(undefined, rest);
  const said = weekday + ', ' + label + ' (' + here.label + ')';

  // Where this calendar names a day differently from the one the reader's own
  // diary uses, say both.  Christmas on the Julian wheel is 25 December and
  // that is correct, but it is the 7th of January to everyone outside it, and
  // a wheel that only ever says "25 December" looks as though the feast had
  // not been converted at all.  The Revised Julian calendar agrees with the
  // Gregorian from 1600 to 2800, so through those years it adds nothing and
  // nothing is added.
  const g = CY.gregorianOf(day);
  if (g.y === named.y && g.m === named.m && g.d === named.d) return said;
  return said + ' \u2014 ' + utcOn(g.y, g.m, g.d).toLocaleDateString(undefined, rest)
              + ' Gregorian';
}

/** "purple (or blue)"; NONE is "no color". */
function colorWords(name, alt) {
  const say = c => (/^none$/i.test(c) ? 'no color' : c.toLowerCase().replace(/_/g, ' '));
  const others = String(alt || '').split(';').map(s => s.trim()).filter(Boolean).map(say);
  return say(name) + (others.length ? ' (or ' + others.join(' or ') + ')' : '');
}

/** A colors.csv fill as CSS paints it: "#ffffff/#bfbfbf" is the hatch of no color. */
function cssPaint(fill) {
  const f = String(fill || '');
  const i = f.indexOf('/');
  if (i < 0) return f;
  const ground = f.slice(0, i).trim(), line = f.slice(i + 1).trim();
  return 'repeating-linear-gradient(45deg, ' + line + ' 0 1.5px, ' + ground + ' 1.5px 5px)';
}

function choose(iso, turn) {
  // Any date names exactly one church year -- Advent Sunday to Advent Sunday is
  // a whole number of weeks, so the years tile the calendar without a gap or an
  // overlap.  A date outside the year on the wheel therefore redraws for its
  // own year rather than being refused.
  if (!DAYS[iso]) {
    const wanted = Math.min(LAST_YEAR, Math.max(FIRST_YEAR, adventYearFor(iso)));
    if (drawKey(wanted) !== drawn) return drawYear(wanted, iso);
    // Only reachable for a date outside what the wheel can draw at all.
    iso = iso < dates[0] ? dates[0] : dates[dates.length - 1];
  }
  chosen = iso;
  showCenter(iso);
  const info = DAYS[iso];
  const d = wedge(info);
  hiUnder.setAttribute('d', d);
  hiOver.setAttribute('d', d);
  if (turn !== false) faceUp(info);
  syncDateBox();
  when.textContent = pretty(iso);
  // The whole names here, where the cell has room only for short ones, and
  // what any icon on the day means.
  // A commemoration's name opens a page about it.
  const parts = [];
  for (const t of info.T || info.t) parts.push(t);
  if (!parts.length && info.W) parts.push(info.W);
  (info.F || info.f).forEach((f, i) => {
    if (!feastLinks) { parts.push(f); return; }
    const a = document.createElement('a');
    a.href = feastUrl(f, (info.L || [])[i]);
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = f;
    a.title = 'Read about ' + f;
    parts.push(a);
  });
  const signs = (info.i || []).map(k => DATA.icons[k].label);
  const bits = [];
  parts.forEach((p, i) => { if (i) bits.push(' \u00b7 '); bits.push(p); });
  // After the day's names, a hymn mark for each topic of the chosen hymnal's
  // index the day has (hymn_topics.csv), as the readings' marks are.
  const hymnal = hymnsOn() && bibleLinks ? chosenHymnal(currentTradition()) : null;
  for (const x of hymnal ? (info.H || []).filter(x => x.h.toLowerCase() === hymnal.code.toLowerCase()) : []) {
    const a = document.createElement('a');
    a.className = 'w2w hymns';
    a.target = '_blank';
    a.rel = 'noopener';
    const book = hymnal.name || 'the church\'s hymnal';
    if (x.n) {
      // A section of the hymnal's contents: its hymns, listed here.
      const nums = hymnNumbers(x.n);
      a.href = hymnaryHymnUrl(x.h, nums[0]);
      a.title = x.t + ' (' + nums.length + ' hymns) in ' + book;
      a.onclick = ev => { ev.preventDefault(); showHymnList(x, book); };
    } else {
      a.href = hymnaryTopicUrl(x.h, x.t, x.s);
      a.title = 'Hymns on ' + x.t + (x.s ? ', ' + x.s : '') + ' in ' + book + ' at Hymnary.org';
    }
    a.setAttribute('aria-label', a.title);
    a.innerHTML = HYMN_ICON;
    bits.push(' ', a);
  }
  if (parts.length) bits.push(' \u2014 ');
  bits.push(info.s + (info.c ? ' \u00b7 ' + colorWords(info.c, info.a) : '')
            + (signs.length ? ' \u00b7 ' + signs.join(' \u00b7 ') : ''));
  what.replaceChildren(...bits);
  dot.style.background = cssPaint(info.fill);
  showDayReadings();
  focusChosen(true);
  syncNote(drawnIn);
  // Say which day the button will actually go to.  "Today" comes from the
  // browser's own local date, and when a machine's time zone is not the one on
  // the clock in front of you -- a remote session, or a browser set to report
  // UTC -- the two disagree silently.  Naming it makes that visible.
  nowBtn.title = 'Jump to today (T) \u2014 ' + pretty(isoToday());
  syncLink();
}

/**
 * Magnifying, panning, and where the two are anchored.
 *
 * The transform is kept as a scale and an offset in the wheel's own
 * coordinates, so any point can be pinned: rolling the mouse keeps the point
 * under the cursor exactly where it is, the way a map behaves, while the
 * slider and the buttons pin the chosen day instead, since that is the thing
 * you asked to look at.  At 1x with no pan the transform is cleared, so nothing
 * moves until asked.
 */
function applyTransform(animate, live) {
  if (!live) syncMagMenu();
  if (mag && Math.round(magnify * 100) !== +mag.value) {
    mag.value = Math.round(magnify * 100);
  }
  zoomG.style.transition = animate ? '' : 'none';
  zoomG.style.transform = (magnify === 1 && !panX && !panY) ? ''
    : `translate(${panX}px, ${panY}px) scale(${magnify})`;
  // In the middle of a gesture (`live`) the easing stays off until it ends,
  // so no frame is caught mid-flight and nothing forces a layout each event.
  if (!animate && !live) {
    // Settle the un-animated frame so the next change is not caught mid-flight.
    zoomG.getBoundingClientRect();
    zoomG.style.transition = '';
  }
  stage.classList.toggle('grabbable', magnify > 1);
  clearTimeout(applyTransform.later);
  applyTransform.later = setTimeout(syncLink, 300);
}

/**
 * Keep whatever sits at the middle of the view somewhere on the drawing.
 *
 * That is how far the view may stray from the wheel's own middle at 1.5x and
 * beyond.  Below it the leash shortens with the magnification, to nothing at
 * 1x: zooming out with the wheel pushed to one side draws it back to the
 * middle as it shrinks, where it used to hold its place down to the last step
 * and then jump there.  (focusChosen's pull toward the middle, k - 1/k of the
 * way, is always within it.)
 */
function clampPan() {
  if (!G) return;
  const midX = G.width / 2, midY = G.height / 2;
  const leash = magnify * Math.min(1, 2 * (magnify - 1));
  const homeX = (1 - magnify) * midX, homeY = (1 - magnify) * midY;
  panX = Math.min(homeX + leash * midX, Math.max(homeX - leash * midX, panX));
  panY = Math.min(homeY + leash * midY, Math.max(homeY - leash * midY, panY));
}

const withinRange = k => Math.min(6, Math.max(1, Math.round(k * 20) / 20));

/** Screen coordinates to the wheel's own, before the zoom is applied. */
function atCursor(ev) {
  const p = svg.createSVGPoint();
  p.x = ev.clientX; p.y = ev.clientY;
  return p.matrixTransform(svg.getScreenCTM().inverse());
}

/** Magnify about a point given in the wheel's coordinates, pinning it. */
function zoomAbout(k, vx, vy) {
  const next = withinRange(k);
  if (next === magnify) return;
  const holdX = (vx - panX) / magnify, holdY = (vy - panY) / magnify;
  magnify = next;
  panX = vx - next * holdX;
  panY = vy - next * holdY;
  clampPan();
  applyTransform(false);
}

/**
 * Bring the chosen day into view at the current magnification.
 *
 * The wheel has already turned that day to the top, so it is always on the
 * vertical line above the center, at whichever radius its band sits.  The
 * point is drawn in toward the middle of the view by 1 - 1/k, which arrives
 * smoothly rather than jumping there, and is identity at 1x.
 */
function focusChosen(animate) {
  if (!G) return;
  const band = chosen && DAYS[chosen] ? DAYS[chosen].b : 0;
  const focusX = G.cx;
  const focusY = G.cy - (G.rOuter - (band + 0.5) * bandHeight);
  const pull = 1 - 1 / magnify;
  panX = focusX + (G.cx - focusX) * pull - magnify * focusX;
  panY = focusY + (G.cy - focusY) * pull - magnify * focusY;
  clampPan();
  applyTransform(animate !== false);
}

/** The slider and the buttons magnify about the chosen day. */
function setZoom(k) {
  const next = withinRange(k);
  if (next === magnify) return;
  magnify = next;
  focusChosen(true);
}

function resetZoom() {
  magnify = 1; panX = 0; panY = 0;
  applyTransform(true);
}

// The magnification menu in the bar: 1x to 6x by halves, and the zoom in hand
// when the mouse wheel or a pinch has left it between them.
const MAG_STEPS = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6];
const magLabel = k => (Number.isInteger(k * 10) ? k.toFixed(1) : String(+k.toFixed(2))) + '\u00d7';
function syncMagMenu() {
  if (!magOut || magOut.tagName !== 'SELECT') return;
  if (!magOut.options.length) {
    for (const k of MAG_STEPS) magOut.appendChild(new Option(magLabel(k), String(k)));
  }
  const value = String(+magnify.toFixed(2));
  const extra = magOut.querySelector('option[data-between]');
  if (MAG_STEPS.indexOf(+value) >= 0) {
    if (extra) extra.remove();
  } else {
    const o = extra || new Option('', '');
    o.dataset.between = '1';
    o.value = value; o.textContent = magLabel(+value);
    // In order among the steps.
    const after = Array.from(magOut.options).find(x => !x.dataset.between && +x.value > +value);
    magOut.insertBefore(o, after || null);
  }
  magOut.value = value;
}
if (magOut && magOut.tagName === 'SELECT') {
  magOut.addEventListener('change', () => {
    const k = parseFloat(magOut.value);
    if (k <= 1) { zoomBefore = magnify > 1 ? magnify : zoomBefore; resetZoom(); }
    else setZoom(k);
  });
}

// 0 shows the whole wheel; pressed again it goes back to the zoom it left
// (or, the first time, to the page's own, church_year.py --zoom).
let zoomBefore = null;
function toggleWholeWheel() {
  if (magnify > 1) { zoomBefore = magnify; resetZoom(); return; }
  const back = zoomBefore || (defaultZoom() > 1 ? defaultZoom() : null);
  zoomBefore = null;
  if (back) setZoom(back);
}

/** Step a day, rolling into the next or previous church year at either end. */
function step(n) {
  const i = dates.indexOf(chosen);
  if (i < 0) return;
  const j = i + n;
  if (j >= 0 && j < dates.length) return choose(dates[j]);
  // Past either end of the years the page can draw, stay put.
  const y = drawnYear() + Math.sign(n);
  if (y < FIRST_YEAR || y > LAST_YEAR) return;
  choose(CY.iso(CY.fromIso(chosen) + n));
}

/**
 * The keys' steps.  With "Arrow keys go on into the next year" they roll into
 * the next or previous church year at either end, as the buttons do.  Without
 * it they stay in the church year on the wheel, going round it: past the last
 * day the step comes back in at the beginning, and a week's step keeps its
 * weekday, landing in the first (or last) week.
 */
function stepInYear(n) {
  if (arrowsBox.checked) return step(n);
  const i = dates.indexOf(chosen);
  if (i < 0) return;
  const len = dates.length;
  let j = i + n;
  if (n % 7 === 0) {
    const round = Math.ceil(len / 7) * 7;     // whole weeks round the wheel
    while (j >= len) j -= round;
    while (j < 0) j += round;
    while (j >= len) j -= 7;                  // a year of odd days: the nearest week in
    while (j < 0) j += 7;
  } else {
    j = ((j % len) + len) % len;
  }
  choose(dates[j]);
}

/**
 * The same weekday of the same week a month on or back, in the calendar on the
 * wheel: the third Sunday of March to the third Sunday of April.  A fifth one
 * the month lacks becomes its last (the fifth Thursday to the fourth).  With
 * `round`, a month past either end of the church year comes back in at the
 * other: that month a year earlier (or later).
 */
function stepMonth(n, round) {
  if (!chosen) return;
  const here = CY.reckoningNow();
  const now = CY.fromIso(chosen);
  const c = here.fromDay(now);
  let m = c.m + n, y = c.y;
  while (m > 12) { m -= 12; y += 1; }
  while (m < 1) { m += 12; y -= 1; }
  const week = Math.ceil(c.d / 7);                   // 1 to 5: which of the month's
  const sameWeek = yy => {
    const first = here.toDay(yy, m, 1);
    let d = first + ((now - first) % 7 + 7) % 7 + 7 * (week - 1);
    while (here.fromDay(d).m !== m) d -= 7;
    return d;
  };
  let day = sameWeek(y);
  if (round && dates.length) {
    const lo = CY.fromIso(dates[0]), hi = CY.fromIso(dates[dates.length - 1]);
    if (day > hi) day = sameWeek(y - 1);
    else if (day < lo) day = sameWeek(y + 1);
    // A month the year has only in part: its days that are in it.
    while (day < lo) day += 7;
    while (day > hi) day -= 7;
  }
  // Past either end of the years the page can draw, stay put.
  const g = CY.gregorianOf(day);
  if (g.y < FIRST_YEAR || g.y > LAST_YEAR + 1) return;
  choose(CY.iso(day));
}

svg.addEventListener('click', ev => {
  if (dragged) { dragged = false; return; }
  if (performance.now() < quietUntil) return;
  const p = svg.createSVGPoint();
  p.x = ev.clientX; p.y = ev.clientY;
  const q = p.matrixTransform(zoomG.getScreenCTM().inverse());
  const dx = q.x - G.cx, dy = q.y - G.cy;
  const r = Math.hypot(dx, dy);
  if (r < G.rInner || r > G.rOuter) return;
  let a = Math.atan2(dy, dx) * 180 / Math.PI - turned;
  a = ((a - G.startAngle) % 360 + 360) % 360;
  const w = Math.floor(a / G.anglePerWeek);
  const b = Math.min(G.bands - 1, Math.floor((G.rOuter - r) / bandHeight));
  const hit = dates.find(k => DAYS[k].w === w && DAYS[k].b === b);
  if (hit) { pushNext = hit !== chosen; choose(hit); }
});

box.addEventListener('change', () => {
  // An empty or half-typed box reports ''; put back the day actually on the
  // wheel rather than treating it as a request to go somewhere.
  if (box.value) { pushNext = true; choose(box.value); } else syncDateBox();
});
$('prev').onclick = () => step(-1);
$('next').onclick = () => step(1);
nowBtn.onclick = () => { pushNext = true; choose(isoToday()); };
yearBox.addEventListener('change', () => {
  const y = parseInt(yearBox.value, 10);
  if (isNaN(y) || y < FIRST_YEAR || y > LAST_YEAR) { yearBox.value = drawnYear(); return; }
  // A number box fires change again when it loses focus, value unchanged.
  // Redrawing then would throw away the day the reader is looking at.
  if (y === drawnYear()) return;
  pushNext = true;
  drawYear(y, null);
});
// A new tradition brings its own calendar and Easter with it (the Orthodox
// keep the Julian paschalion), and its own menus of calendars to lay over it.
// The day in hand is kept: it is the same day in any tradition.
function traditionChanged() {
  buildSubMenus();
  latinBox.checked = latinDefault();
  pick(bibleBox, bibleDefault());
  const own = profileOf(currentTradition()).settings;
  pick(calBox, own.calendar);
  paschalionBox.value = '';
  pick(paschalionBox, own.paschalion || '');
  redrawSameDay();
}
tradBox.onchange = () => { buildChurchMenu(); buildBookMenu(); buildSeriesMenu(); traditionChanged(); };
churchBox.onchange = () => { buildBookMenu(); buildSeriesMenu(); traditionChanged(); };
bookBox.onchange = () => { buildSeriesMenu(); traditionChanged(); };
seriesBox.onchange = () => {
  if (seriesBox.selectedOptions[0]) wantedSeries = seriesBox.selectedOptions[0].text;
  traditionChanged();
};
latinBox.onchange = () => drawYear(parseInt(yearBox.value, 10), chosen);
for (const b of readingBoxes) b.onchange = () => { showDayReadings(); markChanged(); syncLink(); };
bibleBox.onchange = siteBox.onchange = w2wBox.onchange = hymnsBox.onchange = propersBox.onchange = hymnalBox.onchange = layoutBox.onchange = () => { showDayReadings(); markChanged(); syncLink(); };
pick(layoutBox, layoutDefault());
artBox.onchange = () => drawYear(parseInt(yearBox.value, 10), chosen);
// Changing the calendar renames every day, so the date in hand is carried
// across as the same day rather than as the same label.
feastBox.onchange = () => drawYear(parseInt(yearBox.value, 10), chosen);
darkReds.onchange = yearLineBox.onchange = () => drawYear(parseInt(yearBox.value, 10), chosen);
arrowsBox.onchange = () => { markChanged(); syncLink(); };

/**
 * The ring menu, built from whatever rings.csv defines.
 *
 * The day cells and the artwork in the middle are the drawing itself rather
 * than decoration, so they are listed but cannot be switched off -- turning
 * them off would leave nothing to look at.
 */
// The `halves` ring holds the year's great divisions: the Festival and
// Non-festival halves for the Lutherans, but three, four or five parts in the
// Ambrosian, East Syriac and West Syriac years -- hence its name in the menu.
const RING_NAMES = { days: 'Day cells', center: 'Center artwork',
                     gold: 'Outer band', broad_seasons: 'Times of the year',
                     halves: 'Parts of the year', seasons: 'Seasons', months: 'Months' };

/** A ring with no name of its own: its key, tidied up enough to read. */
const ringName = key => RING_NAMES[key]
  || key.replace(/_/g, ' ').replace(/^./, c => c.toUpperCase());
const FIXED = { days: true, center: true };

function buildRingMenu(rings) {
  if (ringList.childElementCount) return;      // the rings do not change
  // Listed as they lie on the wheel, outermost first (rings.csv's order is
  // the order they are drawn in, the day cells first).
  const outward = rings.slice().sort((a, b) => (b.rOuter - a.rOuter) || (b.rInner - a.rInner));
  for (const ring of outward) {
    const row = document.createElement('label');
    const box = document.createElement('input');
    box.type = 'checkbox';
    box.checked = !hiddenRings[ring.key];
    box.dataset.ring = ring.key;
    if (FIXED[ring.kind]) { box.disabled = true; row.className = 'fixed'; }
    else box.addEventListener('change', () => {
      hiddenRings[ring.key] = !box.checked;
      drawYear(parseInt(yearBox.value, 10), chosen);
    });
    row.appendChild(box);
    row.appendChild(document.createTextNode(ringName(ring.key)));
    ringList.appendChild(row);
  }
}

// ---------------------------------------------------------------------------
// The Colors menu
// ---------------------------------------------------------------------------

const hex6 = c => /^#[0-9a-f]{6}$/i.test(String(c || '').trim())
  ? String(c).trim().toLowerCase()
  : (/^#[0-9a-f]{3}$/i.test(String(c || '').trim())
     ? '#' + String(c).trim().slice(1).split('').map(x => x + x).join('').toLowerCase() : '');
const colorName = k => k.charAt(0) + k.slice(1).toLowerCase().replace(/_/g, ' ');

/** One row: a swatch to click, the name, and the color written out. */
function colorRow(label, value, changed, onPick, extra) {
  const row = document.createElement('label');
  if (changed) row.className = 'changed';
  const box = document.createElement('input');
  box.type = 'color';
  box.value = hex6(value) || '#ffffff';
  const name = document.createElement('span');
  name.className = 'name';
  name.textContent = label;
  const code = document.createElement('code');
  code.textContent = box.value;
  box.addEventListener('input', () => { code.textContent = box.value; });
  box.addEventListener('change', () => onPick(box.value));
  row.append(box, name, code);
  if (extra) row.appendChild(extra); else row.appendChild(document.createElement('span'));
  return row;
}

function redrawColors() {
  drawYear(parseInt(yearBox.value, 10), chosen);
  markChanged();
  syncLink();
}

/** Fill the menu from the drawing on the wheel: its colors and its rings. */
function buildColorMenu() {
  if (!lastBuilt) return;
  dayColors.replaceChildren();
  for (const c of lastBuilt.palette) {
    // A change goes where this church's color is already changed: its own,
    // its tradition's, or else every church's.
    const key = currentTradition();
    const church = colorOverrides.churches[key] || {};
    const trad = colorOverrides.traditions[tradSlug(traditionOf(key).tradition)] || {};
    const into = church[c.name] ? church : trad[c.name] ? trad : colorOverrides.days;
    dayColors.appendChild(colorRow(colorName(c.name), c.fill, !!(church[c.name] || trad[c.name] || colorOverrides.days[c.name]),
      v => { into[c.name] = v; redrawColors(); }));
  }
  if (hex6(lastBuilt.emptyFill)) {
    dayColors.appendChild(colorRow('Outside the year', lastBuilt.emptyFill, !!colorOverrides.empty,
      v => { colorOverrides.empty = v; redrawColors(); }));
  }
  ringColors.replaceChildren();
  const outward = lastBuilt.rings.slice();
  const order = {};
  DATA.rings.forEach(r => { order[r.key] = r.rOuter; });
  outward.sort((a, b) => (order[b.key] || 0) - (order[a.key] || 0));
  for (const r of outward) {
    if (!hex6(r.fill)) continue;          // the day cells have no fill of their own
    let extra = null;
    if (r.labeled && hex6(r.text)) {
      extra = document.createElement('span');
      extra.className = 'text';
      extra.title = 'The color of the ring\'s words';
      const box = document.createElement('input');
      box.type = 'color';
      box.value = hex6(r.text);
      box.setAttribute('aria-label', ringName(r.key) + ' text');
      box.addEventListener('change', () => { colorOverrides.ringText[r.key] = box.value; redrawColors(); });
      extra.append('text ', box);
    }
    ringColors.appendChild(colorRow(ringName(r.key), r.fill,
      !!(colorOverrides.rings[r.key] || colorOverrides.ringText[r.key]),
      v => { colorOverrides.rings[r.key] = v; redrawColors(); }, extra));
  }
}

/** The page's own color changes (church_year.py --colors / page_colors), as colorsParam writes them. */
let colorsDefaultCache = null;
function colorsDefaultKey() {
  if (colorsDefaultCache === null) {
    const saved = JSON.stringify(colorOverrides);
    readColorsParam(DATA.colorsDefault || '');
    colorsDefaultCache = colorsParam();
    const back = JSON.parse(saved);
    for (const k in back) colorOverrides[k] = back[k];
  }
  return colorsDefaultCache;
}

function clearColors() {
  colorOverrides.days = {}; colorOverrides.traditions = {}; colorOverrides.churches = {}; colorOverrides.churchTrad = {};
  colorOverrides.rings = {}; colorOverrides.ringText = {};
  colorOverrides.empty = '';
}

/** The changes as the link writes them: PURPLE-7a1f7a (every church), lutheran:WHITE-fffff0 (a
 * tradition), lutheran:wels-one-year:RED-c00000 (a church), ring.halves-e6c3f7, text.halves-000000,
 * empty-f0f0f0. */
function colorsParam() {
  const out = [];
  for (const k of Object.keys(colorOverrides.days).sort()) out.push(k + '-' + colorOverrides.days[k].slice(1));
  for (const t of Object.keys(colorOverrides.traditions).sort()) {
    const m = colorOverrides.traditions[t];
    for (const k of Object.keys(m).sort()) out.push(t + ':' + k + '-' + m[k].slice(1));
  }
  const slugOf = key => colorOverrides.churchTrad[key] || tradSlug((TRADITIONS.find(t => t.key === key) || {}).tradition);
  const churches = Object.keys(colorOverrides.churches)
    .sort((a, b) => (slugOf(a) < slugOf(b) ? -1 : slugOf(a) > slugOf(b) ? 1 : a < b ? -1 : a > b ? 1 : 0));
  for (const c of churches) {
    const m = colorOverrides.churches[c];
    for (const k of Object.keys(m).sort()) out.push(slugOf(c) + ':' + c + ':' + k + '-' + m[k].slice(1));
  }
  for (const k of Object.keys(colorOverrides.rings).sort()) out.push('ring.' + k + '-' + colorOverrides.rings[k].slice(1));
  for (const k of Object.keys(colorOverrides.ringText).sort()) out.push('text.' + k + '-' + colorOverrides.ringText[k].slice(1));
  if (colorOverrides.empty) out.push('empty-' + colorOverrides.empty.slice(1));
  return out.join(',');
}

function readColorsParam(text) {
  clearColors();
  for (const item of String(text || '').split(',')) {
    const i = item.lastIndexOf('-');
    if (i <= 0) continue;
    const key = item.slice(0, i), value = hex6('#' + item.slice(i + 1));
    if (!value) continue;
    if (key === 'empty') colorOverrides.empty = value;
    else if (key.indexOf('ring.') === 0) colorOverrides.rings[key.slice(5)] = value;
    else if (key.indexOf('text.') === 0) colorOverrides.ringText[key.slice(5)] = value;
    else if (key.indexOf(':') > 0) {
      const parts = key.split(':');
      const t = tradSlug(parts[0]);
      if (parts.length === 3) {
        const c = parts[1].trim().toLowerCase();
        colorOverrides.churchTrad[c] = t;
        (colorOverrides.churches[c] = colorOverrides.churches[c] || {})[parts[2].toUpperCase()] = value;
      } else (colorOverrides.traditions[t] = colorOverrides.traditions[t] || {})[parts[1].toUpperCase()] = value;
    } else colorOverrides.days[key.toUpperCase()] = value;
  }
}

colorsBtn.addEventListener('click', () => {
  buildColorMenu();
  if (colorDialog.showModal) colorDialog.showModal(); else colorDialog.setAttribute('open', '');
});
colorsReset.addEventListener('click', () => {
  if (colorsParam() === colorsDefaultKey()) return;
  readColorsParam(DATA.colorsDefault || '');     // the page's own colors
  redrawColors();
});

// Clicking away closes the panel, the way a dropdown would.
addEventListener('pointerdown', ev => {
  if (settings.open && !settings.contains(ev.target)) settings.open = false;
}, true);
addEventListener('keydown', ev => {
  // Escape first closes the Colors menu (the browser does that), not the panel under it.
  if (ev.key === 'Escape' && settings.open && !colorDialog.open) { settings.open = false; gear.focus(); }
});

/** The Latin names box's default: the tradition's own (the one-year series), else config.csv's. */
function latinDefault(key) {
  const own = CY.traditionSettings(DATA, traditionOf(key || currentTradition()));
  if (typeof DATA.latinDefault === 'boolean') return DATA.latinDefault;    // church_year.py --latin-names
  const v = String(own.latin_names_default || '').trim();
  return v ? /^(true|1|yes|y|on)$/i.test(v) : !!DATA.settings.latin_names;
}


// ---------------------------------------------------------------------------
// Bible links
// ---------------------------------------------------------------------------
// A reading opens at Bible Gateway or Bible.com.  Both sites' apps claim their
// addresses on phones and tablets, so where the app is installed the link
// opens in it; elsewhere it opens in the browser.  (A web page cannot ask
// which apps are installed, so this is the way to reach them.)
const NT_BOOKS = /^(Matthew|Mark|Luke|John|Acts|Romans|[12] Corinthians|Galatians|Ephesians|Philippians|Colossians|[12] Thessalonians|[12] Timothy|Titus|Philemon|Hebrews|James|[12] Peter|[123] John|Jude|Revelation)\b/;
// Code, name, language (church_year.py reads the codes and languages for --bible).
const BIBLE_VERSIONS = [
  ['ESV', 'English Standard Version', 'en'], ['EHV', 'Evangelical Heritage Version', 'en'],
  ['NKJV', 'New King James Version', 'en'], ['KJV', 'King James Version', 'en'],
  ['NIV', 'New International Version', 'en'], ['NLT', 'New Living Translation', 'en'],
  ['CSB', 'Christian Standard Bible', 'en'], ['NASB', 'New American Standard Bible', 'en'],
  ['NRSVUE', 'New Revised Standard Version Updated Edition', 'en'],
  ['NRSVA', 'New Revised Standard Version, Anglicised', 'en'], ['RSV', 'Revised Standard Version', 'en'],
  ['NABRE', 'New American Bible, Revised Edition', 'en'], ['CEB', 'Common English Bible', 'en'],
  ['RSVCE', 'Revised Standard Version Catholic Edition', 'en'], ['DRA', 'Douay-Rheims 1899 American Edition', 'en'],
  ['MSG', 'The Message', 'en'],
  ['LUTH1545', 'Luther Bibel 1545', 'de'], ['SCH2000', 'Schlachter 2000', 'de'],
  ['SFB15', 'Svenska Folkbibeln 2015', 'sv'], ['DNB1930', 'Det Norsk Bibelselskap 1930', 'no'],
  ['DN1933', 'Dette er Biblen på dansk', 'da'], ['R1933', 'Raamattu 1933/38', 'fi'],
  ['ICELAND', 'Icelandic Bible', 'is'], ['KAR', 'Hungarian Károli', 'hu'], ['UKR', 'Ukrainian Bible', 'uk'],
  ['ARC', 'Almeida Revista e Corrigida 2009', 'pt'], ['RVR1995', 'Reina-Valera 1995', 'es'],
  ['TB', 'Alkitab Terjemahan Baru', 'id'],
];
// The versions a page offers (--bible / page_bibles): codes, languages
// ("english" or a code such as "de"), or "own" (each church's own, no menu).
const BIBLES = (DATA.bibles || []).map(b => String(b).toLowerCase());
const BIBLE_LANGS = { english: 'en' };
function bibleAllowed(code) {
  if (!BIBLES.length || BIBLES[0] === 'own') return true;
  const v = BIBLE_VERSIONS.find(x => x[0] === code);
  return !!v && BIBLES.some(b => b === code.toLowerCase() || (BIBLE_LANGS[b] || b) === v[2]);
}
/** Whether the page leaves the version menu out (one version, or each church's own). */
const bibleFixed = () => BIBLES[0] === 'own' || bibleBox.options.length < 2;
// Bible.com's numbers for them; a version it does not carry opens at Bible Gateway.
const YOUVERSION = { ESV: 59, KJV: 1, NKJV: 114, NIV: 111, NLT: 116, CSB: 1713, NASB: 2692,
  NRSVUE: 3523, RSV: 2020, NABRE: 463, CEB: 37, MSG: 97, TB: 306 };
// Versions Bible Gateway does not carry: a reading opens at Bible.com whichever
// site is chosen, and a set has no link of its own (links.py: NOT_AT_BIBLE_GATEWAY).
const NOT_AT_BIBLE_GATEWAY = { TB: true };
/**
 * The books of the Apocrypha, which many versions leave out (links.py:
 * APOCRYPHA).  A reading from them opens in a version that has them: at Bible
 * Gateway the RSV, whose Apocrypha the ESV's (not online) revises; at
 * Bible.com, which has no RSV Apocrypha, the NRSVUE.  A set with one opens in
 * the same version.
 */
const APOCRYPHA = /^(?:[1-4] )?(?:Tobit|Judith|Wisdom|Sirach|Ecclesiasticus|Baruch|Maccabees|Esdras|Prayer of Manasseh|Prayer of Azariah|Song of the Three|Susanna|Bel and the Dragon|Letter of Jeremiah|Additions to Esther|Greek Esther)(?![A-Za-z0-9_])/;
const APOCRYPHA_AT_BIBLE_GATEWAY = { NRSVUE: 1, NRSVA: 1, RSV: 1, NABRE: 1, CEB: 1, RSVCE: 1, DRA: 1 };
const APOCRYPHA_AT_YOUVERSION = { NRSVUE: 1, CEB: 1, NABRE: 1 };
const USFM = {
  Genesis: 'GEN', Exodus: 'EXO', Leviticus: 'LEV', Numbers: 'NUM', Deuteronomy: 'DEU',
  Joshua: 'JOS', Judges: 'JDG', Ruth: 'RUT', '1 Samuel': '1SA', '2 Samuel': '2SA',
  '1 Kings': '1KI', '2 Kings': '2KI', '1 Chronicles': '1CH', '2 Chronicles': '2CH',
  Ezra: 'EZR', Nehemiah: 'NEH', Esther: 'EST', Job: 'JOB', Psalm: 'PSA', Psalms: 'PSA',
  Proverbs: 'PRO', Ecclesiastes: 'ECC', 'Song of Solomon': 'SNG', 'Song of Songs': 'SNG',
  Isaiah: 'ISA', Jeremiah: 'JER', Lamentations: 'LAM', Ezekiel: 'EZK', Daniel: 'DAN',
  Hosea: 'HOS', Joel: 'JOL', Amos: 'AMO', Obadiah: 'OBA', Jonah: 'JON', Micah: 'MIC',
  Nahum: 'NAM', Habakkuk: 'HAB', Zephaniah: 'ZEP', Haggai: 'HAG', Zechariah: 'ZEC',
  Malachi: 'MAL', Matthew: 'MAT', Mark: 'MRK', Luke: 'LUK', John: 'JHN', Acts: 'ACT',
  Romans: 'ROM', '1 Corinthians': '1CO', '2 Corinthians': '2CO', Galatians: 'GAL',
  Ephesians: 'EPH', Philippians: 'PHP', Colossians: 'COL', '1 Thessalonians': '1TH',
  '2 Thessalonians': '2TH', '1 Timothy': '1TI', '2 Timothy': '2TI', Titus: 'TIT',
  Philemon: 'PHM', Hebrews: 'HEB', James: 'JAS', '1 Peter': '1PE', '2 Peter': '2PE',
  '1 John': '1JN', '2 John': '2JN', '3 John': '3JN', Jude: 'JUD', Revelation: 'REV',
  Tobit: 'TOB', Judith: 'JDT', 'Wisdom of Solomon': 'WIS', Wisdom: 'WIS', Sirach: 'SIR',
  Baruch: 'BAR', '1 Maccabees': '1MA', '2 Maccabees': '2MA', Ecclesiasticus: 'SIR',
  '1 Esdras': '1ES', '2 Esdras': '2ES', Susanna: 'SUS', 'Letter of Jeremiah': 'LJE',
  'Greek Esther': 'ESG',
};

// Verse numbers.  Some churches cite the Hebrew numbering their Bibles still
// use (a psalm's heading a verse of its own, Malachi in three chapters); the
// Bible sites number every version but these the English way, so a link
// translates the citation to open at the same verses (lib/versification.py,
// docs/versification.md).
const HEBREW_NUMBERED = { NABRE: true };
// How many verses a psalm's heading takes in the Hebrew numbering.
const PSALM_HEADING = {
  3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 12: 1, 13: 1, 18: 1, 19: 1, 20: 1, 21: 1, 22: 1,
  30: 1, 31: 1, 34: 1, 36: 1, 38: 1, 39: 1, 40: 1, 41: 1, 42: 1, 44: 1, 45: 1, 46: 1, 47: 1,
  48: 1, 49: 1, 51: 2, 52: 2, 53: 1, 54: 2, 55: 1, 56: 1, 57: 1, 58: 1, 59: 1, 60: 2, 61: 1,
  62: 1, 63: 1, 64: 1, 65: 1, 67: 1, 68: 1, 69: 1, 70: 1, 75: 1, 76: 1, 77: 1, 80: 1, 81: 1,
  83: 1, 84: 1, 85: 1, 88: 1, 89: 1, 92: 1, 102: 1, 108: 1, 140: 1, 142: 1,
};
// Hebrew chapter, first and last verse -> English chapter, verse shift.
const VERSE_SHIFTS = {
  Genesis: [[32, 1, 1, 31, 54], [32, 2, 33, 32, -1]],
  Exodus: [[7, 26, 29, 8, -25], [8, 1, 28, 8, 4], [21, 37, 37, 22, -36], [22, 1, 30, 22, 1]],
  Leviticus: [[5, 20, 26, 6, -19], [6, 1, 23, 6, 7]],
  Numbers: [[17, 1, 15, 16, 35], [17, 16, 28, 17, -15], [30, 1, 1, 29, 39], [30, 2, 17, 30, -1]],
  Deuteronomy: [[13, 1, 1, 12, 31], [13, 2, 19, 13, -1], [23, 1, 1, 22, 29], [23, 2, 26, 23, -1],
                [28, 69, 69, 29, -68], [29, 1, 28, 29, 1]],
  '1 Samuel': [[21, 1, 1, 20, 41], [21, 2, 16, 21, -1], [24, 1, 1, 23, 28], [24, 2, 23, 24, -1]],
  '2 Samuel': [[19, 1, 1, 18, 32], [19, 2, 44, 19, -1]],
  '1 Kings': [[5, 1, 14, 4, 20], [5, 15, 32, 5, -14], [22, 44, 54, 22, -1]],
  '2 Kings': [[12, 1, 1, 11, 20], [12, 2, 22, 12, -1]],
  '1 Chronicles': [[5, 27, 41, 6, -26], [6, 1, 66, 6, 15]],
  '2 Chronicles': [[1, 18, 18, 2, -17], [2, 1, 17, 2, 1], [13, 23, 23, 14, -22], [14, 1, 14, 14, 1]],
  Nehemiah: [[3, 33, 38, 4, -32], [4, 1, 17, 4, 6], [10, 1, 1, 9, 37], [10, 2, 40, 10, -1]],
  Job: [[40, 25, 32, 41, -24], [41, 1, 26, 41, 8]],
  Ecclesiastes: [[4, 17, 17, 5, -16], [5, 1, 19, 5, 1]],
  'Song of Solomon': [[7, 1, 1, 6, 12], [7, 2, 14, 7, -1]],
  Isaiah: [[8, 23, 23, 9, -22], [9, 1, 20, 9, 1], [64, 1, 11, 64, 1]],
  Jeremiah: [[8, 23, 23, 9, -22], [9, 1, 25, 9, 1]],
  Ezekiel: [[21, 1, 5, 20, 44], [21, 6, 37, 21, -5]],
  Daniel: [[3, 31, 33, 4, -30], [4, 1, 34, 4, 3], [6, 1, 1, 5, 30], [6, 2, 29, 6, -1]],
  Hosea: [[2, 1, 2, 1, 9], [2, 3, 25, 2, -2], [12, 1, 1, 11, 11], [12, 2, 15, 12, -1],
          [14, 1, 1, 13, 15], [14, 2, 10, 14, -1]],
  Joel: [[3, 1, 5, 2, 27], [4, 1, 21, 3, 0]],
  Jonah: [[2, 1, 1, 1, 16], [2, 2, 11, 2, -1]],
  Micah: [[4, 14, 14, 5, -13], [5, 1, 14, 5, 1]],
  Nahum: [[2, 1, 1, 1, 14], [2, 2, 14, 2, -1]],
  Zechariah: [[2, 1, 4, 1, 17], [2, 5, 17, 2, -4]],
  Malachi: [[3, 19, 24, 4, -18]],
};

/** A church's verse_numbering setting: null (English), 'all', or the books numbered the Hebrew way. */
function numberingBooks(setting) {
  const words = String(setting || '').replace(/,/g, ' ').split(/\s+/).filter(Boolean);
  if (!words.length || (words.length === 1 && words[0] === 'english')) return null;
  if (words.indexOf('hebrew') >= 0 || words.indexOf('all') >= 0) return 'all';
  const books = {};
  for (const w of words) books[w === 'Psalm' || w === 'Psalms' ? 'Psalms' : w.replace(/_/g, ' ')] = true;
  return books;
}

/** The English chapter and verse of a Hebrew one. */
function englishVerse(book, chapter, verse) {
  if (book === 'Psalm' || book === 'Psalms') return [chapter, Math.max(1, verse - (PSALM_HEADING[chapter] || 0))];
  for (const [ch, lo, hi, ech, shift] of (VERSE_SHIFTS[book] || [])) {
    if (chapter === ch && lo <= verse && verse <= hi) return [ech, verse + shift];
  }
  return [chapter, verse];
}

/** A citation in the Hebrew numbering, in the English one (lib/versification.py: convert). */
function englishCitation(citation, books) {
  if (/^\s*(Psalm|Psalms)\s+(\d+)\s*$/.test(citation)) return citation;
  const token = /((?:[1-4] )?(?:Song of Solomon|Wisdom of Solomon|[A-Z][a-z]+)) (?=\d)|(\d+)([a-c]?)(:)?/g;
  const out = [];
  let pos = 0, book = null, chapter = null, cur = null, active = true, m;
  while ((m = token.exec(citation)) !== null) {
    out.push(citation.slice(pos, m.index));
    pos = token.lastIndex;
    if (m[1]) {
      book = m[1]; chapter = cur = null;
      active = books === 'all' || !!books[book === 'Psalm' || book === 'Psalms' ? 'Psalms' : book];
      out.push(m[0]);
      continue;
    }
    if (!active) { out.push(m[0]); continue; }
    const n = parseInt(m[2], 10);
    if (m[4]) {
      chapter = n;
      const nxt = /^\(?(\d+)/.exec(citation.slice(pos));
      const ech = book && nxt ? englishVerse(book, chapter, parseInt(nxt[1], 10))[0] : chapter;
      if (ech === cur && /[–-]$/.test(out.join('').replace(/\s+$/, ''))) continue;
      cur = ech;
      out.push(ech + ':');
      continue;
    }
    if (book === null || chapter === null) { out.push(m[0]); continue; }
    const [ech, ev] = englishVerse(book, chapter, n);
    if (ech !== cur) { out.push(ech + ':' + ev + m[3]); cur = ech; } else out.push(ev + m[3]);
  }
  out.push(citation.slice(pos));
  return out.join('');
}

/** The verse numbering of the church on the wheel. */
function verseNumbering() {
  return numberingBooks(CY.traditionSettings(DATA, traditionOf(currentTradition())).verse_numbering);
}

/** The tradition's own Bible version, or ESV. */
function bibleDefault(key) {
  // A page built with --bible-default opens every church in that version, if it offers it.
  if (DATA.bibleDefault && bibleAllowed(DATA.bibleDefault)) return DATA.bibleDefault;
  const own = String(CY.traditionSettings(DATA, traditionOf(key || currentTradition())).bible_version || '').trim().toUpperCase();
  const want = BIBLE_VERSIONS.some(v => v[0] === own) ? own : 'ESV';
  if (bibleAllowed(want)) return want;
  // A page that offers only some versions: the first one it names, else ESV, else the first.
  const named = BIBLES.map(b => b.toUpperCase()).find(b => bibleAllowed(b));
  if (named) return named;
  if (bibleAllowed('ESV')) return 'ESV';
  const first = BIBLE_VERSIONS.find(v => bibleAllowed(v[0]));
  return first ? first[0] : 'ESV';
}
// Phones and tablets open Bible.com (its app, when installed); computers
// Bible Gateway.
const IS_MOBILE = (navigator.userAgentData && navigator.userAgentData.mobile)
  || /Android|iPhone|iPad|iPod|Mobile|Windows Phone/i.test(navigator.userAgent || '')
  || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
// Word to Worship's mark after each set of readings: the page's own choice
// (church_year.py --word-to-worship: on, off, or none for no box at all).
const w2wOff = () => DATA.wordToWorship === 'none';
const w2wDefault = () => !w2wOff() && DATA.wordToWorship !== 'off';
const w2wOn = () => !w2wOff() && w2wBox.checked;
// Hymnary.org's hymns on a set, in the church's hymnal (tradition.csv
// hymnary_hymnal), likewise on, off or none (church_year.py --hymnary).
const hymnaryOff = () => DATA.hymnary === 'none';
const hymnaryDefault = () => !hymnaryOff() && DATA.hymnary !== 'off';
/**
 * A church's hymnals at Hymnary.org (tradition.csv hymnary_hymnal, codes
 * separated by spaces, and hymnary_hymnal_name, names by |), newest first;
 * the first opens.
 */
function hymnalsOf(key) {
  const s = CY.traditionSettings(DATA, traditionOf(key));
  const names = String(s.hymnary_hymnal_name || '').split('|').map(x => x.trim());
  return String(s.hymnary_hymnal || '').split(/\s+/).filter(Boolean)
    .map((code, i) => ({ code: code, name: names[i] || '' }));
}
/** The hymnal Hymn search looks in: the one chosen in Settings, or the church's first. */
function chosenHymnal(key) {
  const list = hymnalsOf(key);
  if (key === currentTradition()) { const hit = list.find(h => h.code === hymnalBox.value); if (hit) return hit; }
  return list.find(h => h.code === DATA.hymnalDefault) || list[0] || null;
}
const hymnalOf = key => { const h = chosenHymnal(key); return h ? h.code : ''; };
// The hymnal a church opens on: the page's own (church_year.py --hymnal)
// where the church has it, else the church's first.
const hymnalDefault = () => { const list = hymnalsOf(currentTradition());
  const own = list.find(h => h.code === DATA.hymnalDefault); return own ? own.code : list.length ? list[0].code : ''; };
const hymnsOn = () => !hymnaryOff() && hymnsBox.checked;
// The links a page has (--links / page_links): to the Bible, to pages about
// the feasts; a page made without them shows plain text.
const LINKS = Array.isArray(DATA.links) ? DATA.links : ['bible', 'feasts'];
const bibleLinks = LINKS.indexOf('bible') >= 0, feastLinks = LINKS.indexOf('feasts') >= 0;
// A small music note in a circle: the mark that opens the search.
const W2W_ICON = '<svg viewBox="0 0 16 16" width="1em" height="1em" aria-hidden="true" style="vertical-align:-.15em">'
  + '<circle cx="8" cy="8" r="7.2" fill="none" stroke="currentColor" stroke-width="1.3"/>'
  + '<path d="M6.6 11.2V4.6l4.4-1v5.6" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>'
  + '<ellipse cx="5.5" cy="11.3" rx="1.4" ry="1.1" fill="currentColor"/>'
  + '<ellipse cx="9.9" cy="9.3" rx="1.4" ry="1.1" fill="currentColor"/></svg>';
// A hymnal with a note on its cover: the mark that searches its hymns.
const HYMN_ICON = '<svg viewBox="0 0 16 16" width="1em" height="1em" aria-hidden="true" style="vertical-align:-.15em">'
  + '<path d="M3.2 1.8h9.3v12.4H3.2a1.2 1.2 0 0 1-1.2-1.2V3a1.2 1.2 0 0 1 1.2-1.2z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>'
  + '<path d="M4.6 2v12" stroke="currentColor" stroke-width="1"/>'
  + '<path d="M9.9 4.3v5.2l1.8-.6" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/>'
  + '<ellipse cx="8.7" cy="9.8" rx="1.35" ry="1.05" fill="currentColor"/></svg>';
const bibleSiteDefault = () => (DATA.bibleSite || (IS_MOBILE ? 'youversion' : 'biblegateway'));

/** A citation as Bible Gateway reads it: plain hyphens, no optional-verse brackets or half-verse letters. */
function plainCitation(text) {
  // A note in words, "Psalm 31 (first part)", is not part of the passage;
  // "Canticle: " is a label; "4:2–end" opens the whole chapter.
  // "Psalm 104:30; Liturgical Text": words not from Scripture are not looked up;
  // "Psalm 68:1, 4a, c": a half-verse letter on its own adds nothing to the passage.
  return String(text).replace(/^Canticle:\s*/, '').replace(/\s*;\s*Liturgical Text\b|\bLiturgical Text\s*;\s*/g, '')
    .replace(/,\s*[a-c](?=\s*[,;]|\s*$)/g, '').replace(/(\d+):\d+[ab]?\s*[–-]\s*end\b/g, '$1')
    .replace(/\s*\([^)]*[A-Za-z]{2,}[^)]*\)/g, '')
    // Optional verses, "1:1–6 (7–12)" or "2:(22–24) 25–38", are part of the passage.
    .replace(/(\d[a-z]?)\s+\((?=\d)/g, '$1, (').replace(/\)\s+(?=\d)/g, '), ').replace(/[()]/g, '').replace(/(\d)[abc]\b/g, '$1')
    .replace(/\s*[–—]\s*/g, '-').replace(/\s+/g, ' ').trim();
}

/** Where one citation opens. */
function bibleUrl(citation, version, site, numbering) {
  if (numbering && !HEBREW_NUMBERED[version]) citation = englishCitation(citation, numbering);
  const q = plainCitation(citation);
  if (APOCRYPHA.test(q)) {
    if (site === 'youversion' || NOT_AT_BIBLE_GATEWAY[version]) {
      if (!APOCRYPHA_AT_YOUVERSION[version]) version = 'NRSVUE';
    } else if (!APOCRYPHA_AT_BIBLE_GATEWAY[version]) version = 'RSV';
  }
  if ((site === 'youversion' || NOT_AT_BIBLE_GATEWAY[version]) && YOUVERSION[version]) {
    const m = /^((?:[1-3] )?[A-Z][A-Za-z]*(?: of [A-Z][a-z]+| [A-Z][a-z]+)*) (\d+)(?::(\d+)(?:-(\d+)(?![:\d]))?)?/.exec(q);
    const code = m && USFM[m[1]];
    if (code) {
      const verses = m[3] ? '.' + m[3] + (m[4] ? '-' + m[4] : '') : '';
      return 'https://www.bible.com/bible/' + YOUVERSION[version] + '/' + code + '.' + m[2] + verses + '.' + version;
    }
  }
  return 'https://www.biblegateway.com/passage/?search=' + encodeURIComponent(q) + '&version=' + encodeURIComponent(version);
}

/**
 * The Book of Concord, at bookofconcord.org (the Triglot translation,
 * revised), whose pages have an anchor for every paragraph (#ac-iv-0001);
 * CPH's bookofconcord.cph.org has a page for every article but none for
 * paragraphs.  A citation opens at the first article and paragraph it names
 * (links.py: CONCORD_SITE, CONCORD_DOCS, CONCORD_PAGES, concord_url).
 */
const CONCORD_SITE = 'https://bookofconcord.org/';
const CONCORD_DOCS = [
  ['Augsburg Confession', 'ac'],
  ['Apology of the Augsburg Confession', 'ap'],
  ['Apology', 'ap'],
  ['Smalcald Articles', 'sa'],
  ['Treatise on the Power and Primacy of the Pope', 'tr'],
  ['Power and Primacy of the Pope', 'tr'],
  ['Treatise', 'tr'],
  ['Small Catechism', 'sc'],
  ['Large Catechism', 'lc'],
  ['Formula of Concord, Epitome', 'ep'],
  ['Formula of Concord Epitome', 'ep'],
  ['Epitome', 'ep'],
  ['Formula of Concord, Solid Declaration', 'sd'],
  ['Formula of Concord Solid Declaration', 'sd'],
  ['Solid Declaration', 'sd'],
  ['Catalog of Testimonies', 'ct'],
  ['Preface to the Book of Concord', 'bc'],
  ["Apostles' Creed", 'apc'],
  ['Apostles’ Creed', 'apc'],
  ['Nicene Creed', 'nc'],
  ['Athanasian Creed', 'athc'],
];
const CONCORD_PAGES = {
  ac: {
    '': 'augsburg-confession/preface#ac-preface',
    Preface: 'augsburg-confession/preface#ac-preface',
    Conclusion: 'augsburg-confession/conclusion#ac-conclusion',
    '1': 'augsburg-confession/of-god#ac-i',
    '2': 'augsburg-confession/original-sin#ac-ii',
    '3': 'augsburg-confession/son-of-god#ac-iii',
    '4': 'augsburg-confession/of-justification#ac-iv',
    '5': 'augsburg-confession/of-the-ministry#ac-v',
    '6': 'augsburg-confession/of-new-obedience#ac-vi',
    '7': 'augsburg-confession/of-the-church#ac-vii',
    '8': 'augsburg-confession/what-the-church-is#ac-viii',
    '9': 'augsburg-confession/of-baptism#ac-ix',
    '10': 'augsburg-confession/of-the-lords-supper#ac-x',
    '11': 'augsburg-confession/of-confession#ac-xi',
    '12': 'augsburg-confession/of-repentance#ac-xii',
    '13': 'augsburg-confession/use-of-the-sacraments#ac-xiii',
    '14': 'augsburg-confession/of-ecclesiastical-order#',
    '15': 'augsburg-confession/of-ecclesiastical-usages#ac-xv',
    '16': 'augsburg-confession/of-civil-affairs#ac-xvi',
    '17': 'augsburg-confession/of-christs-return-to-judgment#ac-xvii',
    '18': 'augsburg-confession/of-free-will#ac-xviii',
    '19': 'augsburg-confession/cause-of-sin#',
    '20': 'augsburg-confession/of-good-works#ac-xx',
    '21': 'augsburg-confession/of-worship-of-saints#ac-xxi',
    '22': 'augsburg-confession/of-both-kinds-in-the-sacrament#ac-xxii',
    '23': 'augsburg-confession/of-marriage-of-priests#ac-xxiii',
    '24': 'augsburg-confession/of-the-mass#ac-xxiv',
    '25': 'augsburg-confession/of-confession-xxv#ac-xxv',
    '26': 'augsburg-confession/of-the-distinction-of-meats#ac-xxvi',
    '27': 'augsburg-confession/of-monastic-vows#ac-xxvii',
    '28': 'augsburg-confession/of-ecclesiastical-power#ac-xxviii',
  },
  ap: {
    '': 'defense/#',
    Preface: 'defense/#',
    '1': 'defense/of-god#ap-i',
    '2': 'defense/of-original-sin#ap-ii',
    '3': 'defense/of-christ#ap-iii@51',
    '4': 'defense/of-justification#ap-iv 122>defense/of-love-and-fulfilling-the-law#ap-ivib@-121',
    '7': 'defense/of-the-church#ap-vii',
    '8': 'defense/of-the-church#ap-vii',
    '9': 'defense/of-baptism#ap-ix@50',
    '10': 'defense/of-the-holy-supper#ap-x@53',
    '11': 'defense/of-confession#ap-xi@57',
    '12': 'defense/of-repentance#ap-xii 98>defense/of-confession-and-satisfaction#ap-vi@-97',
    '13': 'defense/of-the-number-and-use-of-sacraments#ap-xiii',
    '14': 'defense/of-ecclesiastical-order#ap-xiv@23',
    '15': 'defense/of-human-traditions-in-the-church#ap-xv',
    '16': 'defense/of-political-order#ap-xvi@52',
    '17': 'defense/of-christs-return-to-judgment#ap-xvii@65',
    '18': 'defense/of-free-will#ap-xviii@66',
    '19': 'defense/of-the-cause-of-sin#ap-xix@76',
    '20': 'defense/of-good-works#ap-xx@77',
    '21': 'defense/of-the-invocation-of-saints#ap-xxi',
    '22': 'defense/of-both-kinds-in-the-lords-supper#ap-xxii',
    '23': 'defense/of-marriage-of-priests#ap-xxiii',
    '24': 'defense/of-the-mass#ap-xxiv',
    '27': 'defense/of-monastic-vows#ap-xxvii',
    '28': 'defense/of-ecclesiastical-power#ap-xxviii',
  },
  sa: {
    '': 'smalcald-articles/#',
    Preface: 'smalcald-articles/#@0',
    '1': 'smalcald-articles/i/divine-majesty#',
    '2/1': 'smalcald-articles/ii/first-and-chief-article#sa-ii-i',
    '2/2': 'smalcald-articles/ii/of-the-mass#sa-ii-ii',
    '2/3': 'smalcald-articles/ii/of-chapters-and-cloisters#sa-ii-iii',
    '2/4': 'smalcald-articles/ii/of-the-papacy#sa-ii-iv',
    '3/1': 'smalcald-articles/iii/of-sin#sa-iii-i',
    '3/2': 'smalcald-articles/iii/of-the-law#sa-iii-ii',
    '3/3': 'smalcald-articles/iii/of-repentance#sa-iii-iii',
    '3/4': 'smalcald-articles/iii/of-the-gospel#',
    '3/5': 'smalcald-articles/iii/of-baptism#sa-iii-v',
    '3/6': 'smalcald-articles/iii/of-the-scarament-of-the-altar#sa-iii-vi',
    '3/7': 'smalcald-articles/iii/of-the-keys#sa-iii-vii',
    '3/8': 'smalcald-articles/iii/of-confession#sa-iii-viii',
    '3/9': 'smalcald-articles/iii/of-excommunication#',
    '3/10': 'smalcald-articles/iii/of-ordination#sa-iii-x',
    '3/11': 'smalcald-articles/iii/of-the-marriage-of-priests#sa-iii-xi',
    '3/12': 'smalcald-articles/iii/of-the-church#',
    '3/13': 'smalcald-articles/iii/of-good-works#sa-iii-xiii',
    '3/14': 'smalcald-articles/iii/of-monastic-vows#sa-iii-xiv',
    '3/15': 'smalcald-articles/iii/of-human-tradition#sa-iii-xv',
  },
  tr: {
    '': 'power-and-primacy/treatise-compiled-at-smalcald#tr-i 60>power-and-primacy/power-and-jurisdiction-of-bishops#tr-ii',
  },
  sc: {
    '': 'small-catechism/preface#sc-preface',
    Preface: 'small-catechism/preface#sc-preface',
    '1': 'small-catechism/ten-commandments#sc-ten-commandments',
    'Ten Commandments': 'small-catechism/ten-commandments#sc-ten-commandments',
    '2': 'small-catechism/the-creed#sc-creed',
    Creed: 'small-catechism/the-creed#sc-creed',
    '3': 'small-catechism/the-lords-prayer#sc-lords-prayer',
    "Lord's Prayer": 'small-catechism/the-lords-prayer#sc-lords-prayer',
    'Lord’s Prayer': 'small-catechism/the-lords-prayer#sc-lords-prayer',
    '4': 'small-catechism/the-sacrament-of-holy-baptism#sc-baptism',
    Baptism: 'small-catechism/the-sacrament-of-holy-baptism#sc-baptism',
    '5': 'small-catechism/how-christians-confess#sc-christian-confession',
    Confession: 'small-catechism/how-christians-confess#sc-christian-confession',
    '6': 'small-catechism/the-sacrament-of-the-altar#sc-sacrament-altar',
    'Sacrament of the Altar': 'small-catechism/the-sacrament-of-the-altar#sc-sacrament-altar',
    'Daily Prayers': 'small-catechism/daily-prayers#sc-daily-prayers',
    'Table of Duties': 'small-catechism/table-of-duties#sc-table-duties',
  },
  lc: {
    '': 'large-catechism/preface#lc-preface',
    Preface: 'large-catechism/preface#lc-preface',
    'Short Preface': 'large-catechism/preface#lc-preface',
    '1': 'large-catechism/ten-commandments#lc-i',
    'Ten Commandments': 'large-catechism/ten-commandments#lc-i',
    '2': 'large-catechism/apostles-creed#lc-ii',
    Creed: 'large-catechism/apostles-creed#lc-ii',
    '3': 'large-catechism/lords-prayer#lc-iii',
    "Lord's Prayer": 'large-catechism/lords-prayer#lc-iii',
    'Lord’s Prayer': 'large-catechism/lords-prayer#lc-iii',
    '4': 'large-catechism/holy-baptism#lc-iv',
    Baptism: 'large-catechism/holy-baptism#lc-iv',
    '5': 'large-catechism/sacrament-of-the-altar#lc-v',
    'Sacrament of the Altar': 'large-catechism/sacrament-of-the-altar#lc-v',
  },
  ep: {
    '': 'epitome/rule-and-norm#ep-rule-and-norm',
    Summary: 'epitome/rule-and-norm#ep-rule-and-norm',
    'Rule and Norm': 'epitome/rule-and-norm#ep-rule-and-norm',
    '1': 'epitome/original-sin#ep-i',
    '2': 'epitome/free-will#ep-ii',
    '3': 'epitome/righteousness-of-faith#ep-iii',
    '4': 'epitome/good-works#ep-iv',
    '5': 'epitome/law-and-gospel#ep-v',
    '6': 'epitome/third-use-of-the-law#ep-vi',
    '7': 'epitome/the-lords-supper#ep-vii',
    '8': 'epitome/person-of-christ#ep-viii',
    '9': 'epitome/descent-of-christ-into-hell#ep-ix',
    '10': 'epitome/church-rites#ep-x',
    '11': 'epitome/election#ep-xi',
    '12': 'epitome/other-sects#ep-xii',
  },
  sd: {
    '': 'solid-declaration/preface#sd-preface',
    Preface: 'solid-declaration/preface#sd-preface',
    Introduction: 'solid-declaration/preface#sd-preface',
    Summary: 'solid-declaration/rule-and-norm#sd-ruleandnorm',
    'Rule and Norm': 'solid-declaration/rule-and-norm#sd-ruleandnorm',
    '1': 'solid-declaration/original-sin#sd-i',
    '2': 'solid-declaration/free-will#sd-ii',
    '3': 'solid-declaration/righteousness-of-faith#sd-iii',
    '4': 'solid-declaration/good-works#sd-iv',
    '5': 'solid-declaration/law-and-gospel#sd-v',
    '6': 'solid-declaration/third-use-of-the-law#sd-vi',
    '7': 'solid-declaration/the-holy-supper#sd-vii',
    '8': 'solid-declaration/person-of-christ#sd-viii',
    '9': 'solid-declaration/christs-descent-into-hell#sd-ix',
    '10': 'solid-declaration/church-rites-adiaphora#sd-x',
    '11': 'solid-declaration/election#sd-xi',
    '12': 'solid-declaration/other-sects#sd-xii',
  },
  ct: {
    '': 'testimonies/#the-catalog-of-testimonies#',
    Preface: 'testimonies/#to-the-christian-reader#',
    Conclusion: 'testimonies/#conclusion#',
  },
  bc: {
    '': 'preface/#preface-to-the-christian-book-of-concord#',
  },
  apc: {
    '': 'ecumenical-creeds/apostles-creed#',
  },
  nc: {
    '': 'ecumenical-creeds/nicene-creed#',
  },
  athc: {
    '': 'ecumenical-creeds/athanasian-creed#',
  },
};

/** A Roman numeral's value. */
function romanValue(text) {
  const values = { I: 1, V: 5, X: 10, L: 50 };
  let total = 0;
  for (let i = 0; i < text.length; i++) {
    const v = values[text[i]];
    total += i + 1 < text.length && values[text[i + 1]] > v ? -v : v;
  }
  return total;
}

/** A CONCORD_PAGES entry and a paragraph (or null): the URL (links.py: _concord_page). */
function concordPage(spec, para) {
  const parts = spec.split(' ');
  let page = parts[0];
  for (const more of parts.slice(1)) {
    const i = more.indexOf('>');
    if (para !== null && para >= parseInt(more.slice(0, i), 10)) page = more.slice(i + 1);
  }
  const m = /^([^#]*)#([^@]*)(?:@(-?\d+))?$/.exec(page);
  const path = m[1], prefix = m[2], offset = m[3];
  const url = CONCORD_SITE + path + (path.endsWith('/') ? '' : '/');
  if (prefix.endsWith('#')) return url + '#' + prefix.slice(0, -1);
  if (!prefix && offset === undefined) return url;
  const n = (para !== null ? para : 1) + parseInt(offset || '0', 10);
  return url + '#' + (prefix ? prefix + '-' : '') + String(n).padStart(4, '0');
}

/**
 * Where a reading from the Book of Concord opens, at its first article and
 * paragraph ("Augsburg Confession XX 1–8", "Apology 4:117–146", "Smalcald
 * Articles 3/3:1–18", "Treatise 12–21", "Small Catechism, Baptism"), or null
 * when it cites none (links.py: concord_url).
 */
function concordUrl(text) {
  const t = String(text).trim();
  let key = null, rest = null;
  for (const [name, k] of CONCORD_DOCS) {
    if (t.startsWith(name) && !/^[A-Za-z]/.test(t.slice(name.length, name.length + 1))) {
      key = k; rest = t.slice(name.length).replace(/^[,:;]+/, '').trim();
      break;
    }
  }
  if (key === null) return null;
  const pages = CONCORD_PAGES[key];
  const word = Object.keys(pages).filter(w => w && !/^[\d/]+$/.test(w))
    .sort((a, b) => b.length - a.length).find(w => rest.startsWith(w));
  if (word) {
    const m = /(\d+)/.exec(rest.slice(word.length));
    return concordPage(pages[word], m ? parseInt(m[1], 10) : null);
  }
  let m = /^(\d+)(?:\/(\d+))?(?::(\d+))?/.exec(rest);
  if (m) {
    if (key === 'tr') return concordPage(pages[''], parseInt(m[1], 10));
    const art = key === 'sa' && m[2] ? m[1] + '/' + m[2] : m[1];
    const spec = pages[art];
    return spec ? concordPage(spec, m[3] ? parseInt(m[3], 10) : null) : concordPage(pages[''], null);
  }
  m = /^([IVXL]+)(?![A-Za-z])(?:\s+([IVXL]+)(?![A-Za-z]))?(?:\s+(\d+))?/.exec(rest);
  if (m) {
    const art = key === 'sa' && (m[1] === 'II' || m[1] === 'III')
      ? romanValue(m[1]) + '/' + (m[2] ? romanValue(m[2]) : 1) : String(romanValue(m[1]));
    const spec = pages[art];
    return spec ? concordPage(spec, m[3] ? parseInt(m[3], 10) : null) : concordPage(pages[''], null);
  }
  return concordPage(pages[''], null);
}

/** A reading's parts, [text, url]: each alternative ("A or B") opens on its own, the words between have no url (links.py: reading_links). */
function readingParts(text, version, site, numbering, cite) {
  const out = [];
  const split = t => String(t).split(/( or |, or the Passion History| or [Tt]he [A-Z][a-z]+ [A-Za-z ]+$)/);
  const parts = split(text);
  let targets = cite ? split(cite) : parts;
  if (targets.length !== parts.length) targets = parts;
  for (let i = 0; i < parts.length; i++) {
    const part = parts[i];
    if (!part) continue;
    const concord = /^ or |^, or /.test(part) ? null : concordUrl(part);
    if (concord) out.push([part, concord]);
    else if (/^ or |^, or /.test(part) || !(/\d/.test(part) || APOCRYPHA.test(part))) out.push([part, null]);
    else out.push([part, bibleUrl(targets[i], version, site, numbering)]);
  }
  return out;
}

/** A reading as links: each alternative ("A or B") opens on its own; `cite`, the reading in the English verses, is where they open. */
function readingLinks(text, cite) {
  if (!bibleLinks) return [text];
  return readingParts(text, bibleBox.value || bibleDefault(), siteBox.value, verseNumbering(), cite).map(([t, url]) => {
    if (!url) return t;
    const a = document.createElement('a');
    a.href = url;
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = t;
    return a;
  });
}

/** A reading's choices: each part of "A or B" that cites verses. */
function readingChoices(text) {
  const parts = String(text).split(/( or |, or the Passion History| or [Tt]he [A-Z][a-z]+ [A-Za-z ]+$)/);
  return parts.filter(p => p && !/^ or |^, or /.test(p) && (/\d/.test(p) || APOCRYPHA.test(p)) && !concordUrl(p));
}

/** A set's readings as one search, every choice of each, joined with semicolons. */
function groupCitation(readings, numbering, english, canon) {
  return [].concat(...readings.map(readingChoices))
    .filter(c => !(canon && APOCRYPHA.test(plainCitation(c))))
    .map(c => plainCitation(english && numbering ? englishCitation(c, numbering) : c)).join('; ');
}

/** Bible Gateway with a set's readings together (Bible.com opens one passage at a time). */
function groupUrl(readings, version, numbering) {
  if (NOT_AT_BIBLE_GATEWAY[version]) return '';
  if (!APOCRYPHA_AT_BIBLE_GATEWAY[version]
      && readings.some(text => readingChoices(text).some(c => APOCRYPHA.test(plainCitation(c))))) version = 'RSV';
  const q = groupCitation(readings, numbering, !HEBREW_NUMBERED[version]);
  if (!q) return '';
  return 'https://www.biblegateway.com/passage/?search=' + encodeURIComponent(q) + '&version=' + encodeURIComponent(version);
}

/** Word to Worship's search for worship songs on a set's readings. */
function wordToWorshipUrl(readings, numbering) {
  const cited = groupCitation(readings, numbering, true, true);
  if (!cited) return '';
  const q = encodeURIComponent('{' + cited + '}');
  return 'https://wordtoworship.com/search/node/' + q.replace(/%3A/g, ':').replace(/%3B/g, ';');
}

/**
 * Hymnary.org's search for the hymns of one hymnal on a set's readings
 * (tradition.csv `hymnary_hymnal`: lsb2006) (links.py: hymnary_url).
 */
// Hymnary.org's results in the hymnal's own order (links.py: HYMNARY_ORDER).
const HYMNARY_ORDER = '&sort=hymnalNumber&order=asc';
function hymnaryUrl(readings, hymnal, numbering) {
  // Without the Apocrypha and the Book of Concord, as for Word to Worship.
  const cited = groupCitation(readings, numbering, true, true);
  if (!cited || !hymnal) return '';
  const q = 'scripture:' + cited.replace(/\u2013/g, '-') + ' hymnalNumber:' + hymnal + ' in:instance';
  return 'https://hymnary.org/search?qu=' + encodeURIComponent(q) + HYMNARY_ORDER;
}

/** "331-357 590-593" -> [331, ..., 357, 590, ..., 593]. */
function hymnNumbers(spec) {
  const out = [];
  for (const part of String(spec).split(/[\s,]+/).filter(Boolean)) {
    const m = /^(\d+)(?:-(\d+))?$/.exec(part);
    if (!m) continue;
    for (let n = +m[1]; n <= +(m[2] || m[1]); n++) out.push(n);
  }
  return out;
}

/** A hymn's own page at Hymnary.org. */
const hymnaryHymnUrl = (hymnal, number) => 'https://hymnary.org/hymn/' + encodeURIComponent(hymnal) + '/' + number;

/** The hymns of a section of a hymnal's contents (hymn_topics.csv `numbers`), in a window. */
function showHymnList(x, book) {
  const dlg = $('hymnsDialog');
  const key = Object.keys(DATA.hymnals || {}).find(k => k.toLowerCase() === x.h.toLowerCase());
  const lines = key ? DATA.hymnals[key] : {};
  $('hymnsHead').textContent = x.t;
  $('hymnsNote').textContent = book + ', ' + x.n.replace(/-/g, '\u2013').split(/[\s,]+/).join(', ') + '. Each opens at Hymnary.org.';
  $('hymnsList').replaceChildren(...hymnNumbers(x.n).map(n => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = hymnaryHymnUrl(x.h, n);
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = String(n);
    li.append(a, ' ', lines[String(n)] || '');
    return li;
  }));
  if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
}

/**
 * Hymnary.org's list of the hymns of one hymnal filed under a topic of its
 * index (a folder's hymn_topics.csv), and under a sub-topic if one is given,
 * in the hymnal's order.  The topic must be the index's own, word for word:
 * the browse page matches it exactly, where a search would match its words
 * anywhere ("The Second Sunday of Advent" and "The Second Sunday before Advent").
 */
function hymnaryTopicUrl(hymnal, topic, sub) {
  const q = s => encodeURIComponent(s).replace(/%20/g, '+');
  return 'https://hymnary.org/browse/topics/' + encodeURIComponent(hymnal)
    + '?subject1=' + q(topic) + (sub ? '&subject2=' + q(sub) : '');
}

/** Where to read about a commemoration: its own link, the tradition's pattern, or Wikipedia. */
function feastUrl(name, link) {
  return feastUrlFor(name, link, CY.traditionSettings(DATA, traditionOf(currentTradition())).feast_link);
}

/** The same, given the tradition's feast_link pattern (links.py: feast_url). */
function feastUrlFor(name, link, pattern) {
  if (link) return link;
  const clean = String(name).replace(/\s*\(transferred from [^)]*\)/, '').trim();
  pattern = String(pattern || '').trim();
  if (pattern && pattern.indexOf('{name}') >= 0) return pattern.split('{name}').join(encodeURIComponent(clean));
  // The name before its first comma ("St. James of Jerusalem, Brother of Jesus
  // and Martyr") is the one an encyclopedia knows.
  const short = clean.split(',')[0].replace(/^St\.? /, 'Saint ').replace(/^The /, '');
  return 'https://en.wikipedia.org/w/index.php?search=' + encodeURIComponent(short);
}

// The menu groups the versions by language, English first and then the others
// by language name, each A to Z by abbreviation, as it shows them.  With only
// one language offered there are no group headings.
const LANGUAGE_NAMES = { da: 'Danish', de: 'German', en: 'English', fi: 'Finnish', hu: 'Hungarian',
  id: 'Indonesian', is: 'Icelandic', no: 'Norwegian', pt: 'Portuguese', es: 'Spanish', sv: 'Swedish', uk: 'Ukrainian' };
{
  const langName = l => LANGUAGE_NAMES[l] || l;
  const offered = BIBLE_VERSIONS.filter(v => bibleAllowed(v[0]));
  const langs = [...new Set(offered.map(v => v[2]))]
    .sort((x, y) => (x === 'en' ? -1 : y === 'en' ? 1 : langName(x).localeCompare(langName(y), 'en')));
  for (const lang of langs) {
    const parent = langs.length > 1 ? document.createElement('optgroup') : bibleBox;
    if (parent !== bibleBox) { parent.label = langName(lang); bibleBox.append(parent); }
    for (const [code, name] of offered.filter(v => v[2] === lang).sort((x, y) => x[0].localeCompare(y[0], 'en'))) {
      const o = document.createElement('option');
      o.value = code;
      o.textContent = code + ' (' + name + ')';
      o.title = name;
      parent.append(o);
    }
  }
}

/** Whether the church on the wheel has readings (of the kinds this page carries). */
function hasReadings() {
  return readingKindsOf(currentTradition()).length > 0;
}

/** The kinds of readings a church has (CY.readingCategories), worked out once. */
const readingKinds = {};
function readingKindsOf(key) {
  if (!readingKinds[key]) readingKinds[key] = CY.readingCategories(DATA, key);
  return readingKinds[key];
}

/** The kinds checked when the page opens (church_year.py --readings / page_readings; all unless set). */
const readingsDefault = () => (Array.isArray(DATA.readingsDefault) ? DATA.readingsDefault : CY.READING_CATEGORIES);
const readingDefaultOn = kind => readingsDefault().indexOf(kind) >= 0;

/** The kinds of readings whose box is checked. */
const readingsOn = () => readingBoxes.filter(b => b.checked).map(b => b.dataset.reading);

/**
 * The `readings=` of a link: none; all; the kinds to show (day,feasts); or
 * the kinds to leave out (-daily,-office).  `0` and `1` also mean none and
 * all, as for the other boxes.  Unknown kinds are skipped (lectionary.py: parse_categories).
 */
function readingKindsFrom(text) {
  const all = CY.READING_CATEGORIES;
  const t = String(text || '').trim().toLowerCase();
  if (/^(0|false|no|off|none)$/.test(t)) return [];
  if (/^(|1|true|yes|on|all)$/.test(t)) return all.slice();
  const words = t.split(',').map(w => w.trim()).filter(Boolean);
  if (words.some(w => w.charAt(0) === '-')) {
    const off = words.map(w => w.replace(/^-+/, ''));
    return all.filter(k => off.indexOf(k) < 0);
  }
  return all.filter(k => words.indexOf(k) >= 0);
}

/**
 * The link's `readings=`, or '' while the boxes are as the page opens with
 * them: `all`, `none`, or the shorter of the kinds shown (day,daily) and the
 * kinds left out (-office).
 */
function readingsParam() {
  const on = readingsOn();
  const off = readingBoxes.filter(b => !b.checked).map(b => b.dataset.reading);
  if (readingBoxes.every(b => b.checked === readingDefaultOn(b.dataset.reading))) return '';
  if (!off.length) return 'all';
  if (!on.length) return 'none';
  const shown = on.join(','), left = off.map(k => '-' + k).join(',');
  return shown.length < left.length ? shown : left;
}

/**
 * The chosen day's readings, under the day's name: one line for each set (the
 * day's propers, a festival kept on it, a daily lectionary) of the kinds
 * checked behind the gear.  The box keeps one height whatever the day holds,
 * so the wheel below it does not jump as the days go by.  The sets stand on
 * the right, under the day's name; when they need more than its three lines,
 * "▾ n more" opens the box and reads them across two columns, the first on
 * the left (layReadings).  A column with more below than it shows fades at
 * its foot.
 */
/** The kinds of reading a church lists as parts of the service, not readings (reading_propers). */
function propersOf(key) {
  return String((((DATA.profiles[key] || {}).settings || {}).reading_propers) || '').replace(/,/g, ' ').split(/\s+/).filter(Boolean);
}
/** What the page calls a kind of reading for a church (reading_labels, else its own name). */
function kindLabel(key, kind) {
  for (const part of String(((DATA.profiles[key] || {}).settings || {}).reading_labels || '').split(';')) {
    const i = part.indexOf('=');
    if (i > 0 && part.slice(0, i).trim() === kind) return part.slice(i + 1).trim();
  }
  return CY.READING_LABELS[kind] || kind;
}

function showDayReadings() {
  const want = readingsOn();
  const on = hasReadings() && readingKindsOf(currentTradition()).some(k => want.indexOf(k) >= 0);
  readingsBox.hidden = !on;
  syncSlideRow();
  if (!on || !chosen) return;
  const lines = readingLinesFor(chosen);
  // A day with none (of the kinds chosen) leaves the box blank.
  readingLines = lines;
  layReadings();
  readingsBox.title = lines.map(l => l.textContent).join('\n');
}

/** A day's sets of readings (of the kinds shown), a line each, with their links and marks. */
function readingLinesFor(iso) {
  const want = readingsOn();
  const info = DAYS[iso] || {};
  const names = [].concat(info.T || [], info.t || [], info.F || [], info.f || []);
  const appointed = READINGS[iso] || [];
  const groups = appointed.filter(g => want.indexOf(g.category) >= 0);
  const numbering = verseNumbering();
  // The parts of the service (reading_propers: an Introit, a Gradual ...) come
  // after a set's readings, on a line of their own with a link of their own:
  // the set's name opens only its readings, as a lector prints them.
  const own = propersOf(currentTradition());
  const lines = groups.filter(g => propersBox.checked || g.items.some(it => own.indexOf(it.kind) < 0)).map(g => {
    const line = document.createElement('div');
    const mine = g.items.filter(it => own.indexOf(it.kind) < 0);
    const parts = g.items.filter(it => own.indexOf(it.kind) >= 0);
    const readings = (mine.length ? mine : parts).map(it => it.cite || it.reading);
    // The set's name opens all its readings together at Bible Gateway.
    const together = bibleLinks ? groupUrl(readings, bibleBox.value || bibleDefault(), numbering) : '';
    const head = document.createElement(together ? 'a' : 'span');
    head.className = 'set';
    if (together) {
      head.href = together;
      head.target = '_blank';
      head.rel = 'noopener';
      head.title = 'Open all these readings together at Bible Gateway';
    }
    // The first set, when it is the day named above, is just "Readings"; any
    // other set says whose it is.
    const plain = !g.title || (appointed.indexOf(g) === 0 && names.indexOf(g.title) >= 0);
    head.textContent = plain ? 'Readings' : g.title;
    line.dataset.cat = g.category;
    line.dataset.tab = TAB_NAMES[g.category] || head.textContent;
    line.append(head, ': ');
    const listItems = (into, items) => items.forEach((it, i) => {
      if (i) into.append(' \u00b7 ');
      // A reading's label and citation stay on one line when they can.
      const item = document.createElement('span');
      item.className = 'item';
      into.append(item);
      // An "Old Testament" slot that holds Acts or Revelation (Eastertide) is
      // the first reading.
      let text = it.label;
      if (/^Old Testament/.test(text) && NT_BOOKS.test(it.reading)) {
        text = text.replace('Old Testament', 'First Reading');
      }
      // "Psalm 122" says what it is without a "Psalm" before it.
      if (it.reading.indexOf(text + ' ') !== 0) {
        const label = document.createElement('span');
        label.className = 'kind';
        label.textContent = text + ' ';
        item.append(label);
      }
      item.append(...readingLinks(it.reading, it.cite));
    });
    listItems(line, mine.length ? mine : parts);
    // After the set, a mark for Word to Worship's worship songs on it (none
    // for a set of only the Apocrypha or the Book of Concord, which it lacks).
    // Hymns in the church's hymnal at Hymnary.org, then contemporary songs;
    // the propers below have marks of their own.
    const marks = (into, cites, what) => {
      const hymns = hymnsOn() ? hymnaryUrl(cites, hymnalOf(currentTradition()), numbering) : '';
      if (hymns) {
        const a = document.createElement('a');
        a.className = 'w2w hymns';
        a.href = hymns;
        a.target = '_blank';
        a.rel = 'noopener';
        const hymnal = (chosenHymnal(currentTradition()) || {}).name;
        a.title = 'Hymns for these ' + what + ' in ' + (hymnal || 'the church\'s hymnal') + ' at Hymnary.org';
        a.setAttribute('aria-label', a.title);
        a.innerHTML = HYMN_ICON;
        into.append(' ', a);
      }
      const songs = w2wOn() ? wordToWorshipUrl(cites, numbering) : '';
      if (songs) {
        const a = document.createElement('a');
        a.className = 'w2w';
        a.href = songs;
        a.target = '_blank';
        a.rel = 'noopener';
        a.title = 'Contemporary worship songs for these ' + what + ' at Word to Worship';
        a.setAttribute('aria-label', a.title);
        a.innerHTML = W2W_ICON;
        into.append(' ', a);
      }
    };
    marks(line, readings, mine.length ? 'readings' : 'propers');
    if (mine.length && parts.length && propersBox.checked) {
      const block = document.createElement('span');
      block.className = 'propers';
      const url = bibleLinks ? groupUrl(parts.map(it => it.cite || it.reading), bibleBox.value || bibleDefault(), numbering) : '';
      const h = document.createElement(url ? 'a' : 'span');
      h.className = 'set';
      if (url) { h.href = url; h.target = '_blank'; h.rel = 'noopener'; h.title = 'Open these propers together at Bible Gateway'; }
      h.textContent = 'Propers';
      block.append(h, ': ');
      listItems(block, parts);
      marks(block, parts.map(it => it.cite || it.reading), 'propers');
      line.append(block);
    }
    return line;
  });
  return lines;
}

let readingLines = [];
// A tab's name: the set's own, or a short one for the daily kinds.
const TAB_NAMES = { daily: 'Daily lectionary', additional: 'Additional', psalms: 'Psalms', plan: 'Reading plan' };
// The tab last chosen, by name and kind: the next day opens on the same one
// when it has it.
let readingsTab = { tab: '', cat: '' };
const readingsTabs = document.createElement('div');
readingsTabs.className = 'tabrow';
readingsTabs.setAttribute('role', 'tablist');
const readingCols = { left: document.createElement('div'), right: document.createElement('div') };
readingCols.left.className = 'col left';
readingCols.right.className = 'col right';
for (const col of Object.values(readingCols)) col.addEventListener('scroll', () => markMore(col));
// "▾ 2 more": shown when the sets do not all fit (most often on a phone);
// it opens the box to show them all, and "▴ less" closes it again.  Open
// stays open from day to day until closed.
const readingsMore = document.createElement('button');
readingsMore.type = 'button';
readingsMore.className = 'more-btn';
let readingsOpen = false;
readingsMore.addEventListener('click', () => {
  readingsOpen = !readingsOpen;
  layReadings();
});

/** How many of a column's sets end below what it shows. */
function hiddenSets(col) {
  const bottom = col.getBoundingClientRect().bottom;
  return Array.from(col.children).filter(el => el.getBoundingClientRect().bottom > bottom + 2).length;
}

/**
 * Tabs: a row of the sets' names, and the chosen one's readings under it.
 * The tab chosen is kept from day to day (by its name, else its kind).
 */
function layTabs() {
  const { left, right } = readingCols;
  const lines = readingLines;
  readingsBox.classList.add('tabs');
  let at = lines.findIndex(l => l.dataset.tab === readingsTab.tab);
  if (at < 0) at = lines.findIndex(l => l.dataset.cat === readingsTab.cat);
  if (at < 0) at = 0;
  readingsTabs.replaceChildren(...lines.map((l, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('role', 'tab');
    b.setAttribute('aria-selected', String(i === at));
    b.className = i === at ? 'on' : '';
    b.textContent = l.dataset.tab;
    b.title = l.querySelector('.set') ? l.querySelector('.set').textContent : l.dataset.tab;
    b.addEventListener('click', () => {
      readingsTab = { tab: l.dataset.tab, cat: l.dataset.cat };
      layReadings();
    });
    return b;
  }));
  left.replaceChildren();
  right.replaceChildren(lines[at]);
  readingsBox.replaceChildren(readingsTabs, right);
  right.scrollTop = 0;
  markMore(right);
  if (right.scrollHeight > right.clientHeight + 2) {
    if (readingsOpen) readingsBox.classList.add('open');
    markMore(right);
    readingsMore.textContent = readingsOpen ? '\u25b4 less' : '\u25be more';
    readingsMore.title = readingsOpen ? 'Show two lines again' : 'Show all of this set\u2019s readings';
    readingsBox.append(readingsMore);
  }
}

/** Whether a column has more below than it shows: a fade at its foot. */
function markMore(col) {
  col.classList.toggle('more', col.scrollHeight - col.scrollTop - col.clientHeight > 2);
}

/**
 * Lay the day's sets out, in reading order.  Closed, they stand on the right
 * under the day's name, as many as its three lines hold, with "▾ n more"
 * when there are others.  Opened, the box grows and the sets read across two
 * columns, the first ones sliding over to the left (under the church's name)
 * and the later ones filling the right, split where the taller column is as
 * short as it can be.  On a narrow screen (the box one column wide) they
 * stay in one column and the box only grows.
 */
function layReadings() {
  const { left, right } = readingCols;
  const lines = readingLines;
  // Where each set stood before, for the slide (slideSets).
  const before = new Map(lines.filter(l => l.isConnected).map(l => [l, setBox(l)]));
  readingsBox.classList.remove('two', 'open', 'tabs');
  if (layoutNow() === 'tabs' && lines.length > 1) return layTabs();
  left.replaceChildren();
  right.replaceChildren(...lines);
  readingsBox.replaceChildren(left, right);
  right.scrollTop = 0;
  markMore(right);
  const hidden = hiddenSets(right);
  if (!hidden) { slideSets(before); return; }
  if (!readingsOpen) {
    readingsMore.textContent = '\u25be ' + hidden + ' more';
    readingsMore.title = 'Show all the day\u2019s readings';
    readingsBox.append(readingsMore);
    slideSets(before);
    return;
  }
  readingsBox.classList.add('open');
  const narrow = getComputedStyle(readingsBox).getPropertyValue('--cols').trim() === '1';
  if (lines.length > 1 && !narrow) {
    readingsBox.classList.add('two');
    let best = 1, height = Infinity;
    for (let k = 1; k < lines.length; k++) {
      left.replaceChildren(...lines.slice(0, k));
      right.replaceChildren(...lines.slice(k));
      const tall = Math.max(right.scrollHeight, left.scrollHeight);
      if (tall < height - 1) { height = tall; best = k; }
    }
    left.replaceChildren(...lines.slice(0, best));
    right.replaceChildren(...lines.slice(best));
  }
  for (const col of [left, right]) { col.scrollTop = 0; markMore(col); }
  readingsMore.textContent = '\u25b4 less';
  readingsMore.title = 'Show the readings in three lines again';
  readingsBox.append(readingsMore);
  slideSets(before);
}

/** Where a set's text starts: its name (the line's own box spans the column, whichever side the text is on). */
function setBox(line) {
  return (line.firstElementChild || line).getBoundingClientRect();
}

/** Slide each set from where it stood to where it stands now (when it moved). */
function slideSets(before) {
  const speed = parseInt(slideBox.value, 10) || 0;
  if (!before.size || !speed || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const moved = [];
  for (const [el, was] of before) {
    if (!el.isConnected) continue;
    const now = setBox(el);
    const dx = was.left - now.left, dy = was.top - now.top;
    if (Math.abs(dx) < 2 && Math.abs(dy) < 2) continue;
    moved.push(el.animate([{ transform: 'translate(' + dx + 'px,' + dy + 'px)' }, { transform: 'none' }],
                          { duration: speed, easing: 'cubic-bezier(.45, 0, .2, 1)' }).finished);
  }
  // The columns let the sets pass over their edges while they move.
  if (!moved.length) return;
  readingsBox.classList.add('sliding');
  Promise.all(moved).catch(() => {}).then(() => readingsBox.classList.remove('sliding'));
}
let resizeFrame = 0;
window.addEventListener('resize', () => {
  if (!readingLines.length || resizeFrame) return;
  resizeFrame = requestAnimationFrame(() => { resizeFrame = 0; layReadings(); });
});

/**
 * A dot on the gear when anything behind it is set away from what the file
 * asked for.  The Year box is left out of the reckoning: moving through the
 * years is what the wheel is for, and a dot that is always lit says nothing.
 */
function markChanged() {
  const d = DATA.settings;
  const own = profileOf(currentTradition()).settings;
  const changed = currentTradition() !== DATA.defaultTradition
               || chosenSubs().join(',') !== DATA.defaultSubcalendars.join(',')
               || calBox.value !== own.calendar
               || paschalionBox.value !== (own.paschalion || '')
               || latinBox.checked !== latinDefault()
               || readingBoxes.some(b => b.checked !== readingDefaultOn(b.dataset.reading))
               || bibleBox.value !== bibleDefault()
               || siteBox.value !== bibleSiteDefault()
               || (!w2wOff() && w2wBox.checked !== w2wDefault())
               || (!hymnaryOff() && hymnsBox.checked !== hymnaryDefault())
               || !propersBox.checked
               || (!hymnalRow.hidden && hymnalBox.value !== hymnalDefault())
               || yearLineBox.checked !== yearLineDefault()
               || arrowsBox.checked !== arrowsDefault()
               || layoutNow() !== layoutDefault()
               || feastBox.value !== d.feast_detail
               || darkReds.checked !== (midDefault() === 'dark-reds')
               || artBox.value !== defaultArt()
               || showHelp.checked !== footDefaults().help
               || showCredit.checked !== footDefaults().credit
               || ringKey() !== hiddenDefaultKey()
               || colorsParam() !== colorsDefaultKey();
  gear.classList.toggle('changed', changed);
  resetBtn.disabled = !changed;
}

/** The settings behind the gear, as config.csv asks for them. */
const defaultArt = () => {
  // A page made with the artwork left out keeps each church's own.
  if (isFixed('artwork')) return 'auto';
  const k = String(DATA.defaultArt || 'auto').toLowerCase();
  // A picture put beside the page is the one it is meant to show.
  if (localArt && k === 'auto') return 'local';
  if (k === 'season') return hasSeasonArt() ? 'season' : 'auto';
  return (DATA.artworkOrder || []).indexOf(k) >= 0 ? k : 'auto';
};

function applyDefaults() {
  const d = DATA.settings;
  setTradition(DATA.defaultTradition);
  setSubs(DATA.defaultSubcalendars);
  const own = profileOf(currentTradition()).settings;
  pick(calBox, own.calendar);
  paschalionBox.value = '';
  pick(paschalionBox, own.paschalion || '');
  pick(feastBox, d.feast_detail);
  darkReds.checked = midDefault() === 'dark-reds';
  latinBox.checked = latinDefault();
  for (const b of readingBoxes) b.checked = readingDefaultOn(b.dataset.reading);
  pick(bibleBox, bibleDefault());
  pick(siteBox, bibleSiteDefault());
  w2wBox.checked = w2wDefault();
  hymnsBox.checked = hymnaryDefault();
  propersBox.checked = true;
  hymnalBox.value = hymnalDefault();
  yearLineBox.checked = yearLineDefault();
  arrowsBox.checked = arrowsDefault();
  pick(layoutBox, layoutDefault());
  showHelp.checked = footDefaults().help;
  showCredit.checked = footDefaults().credit;
  applyFooter();
  pick(artBox, defaultArt());
  setHidden(hiddenDefault());
  readColorsParam(DATA.colorsDefault || '');
}

/**
 * Put everything behind the gear back to what config.csv asks for.  The day
 * on the wheel is kept -- it is the same day whatever calendar names it -- and
 * so is the magnification, which lives in the bar rather than behind the gear.
 */
function resetSettings() {
  const day = CY.fromIso(chosen);
  applyDefaults();
  // Draw once so the day is named in the default calendar, then choose it;
  // choose redraws for its own year if the calendar moved it across Advent.
  drawYear(parseInt(yearBox.value, 10), null);
  choose(CY.iso(day));
  // Settings that do not redraw (the boxes under the wheel) still clear the dot.
  markChanged();
  syncLink();
}
// Changing either axis redraws the year, and the day that was chosen is kept:
// it is the same day whatever it is called, so the wheel turns to it again
// rather than jumping back to Advent 1.
/** Move a whole church year, keeping the day of it that is chosen. */
function stepYear(by) {
  const year = drawnYear() + by;
  if (year < FIRST_YEAR || year > LAST_YEAR || !chosen) return;
  // The same date a year on or back, in the calendar on the wheel; 29 February
  // becomes the 28th.  Near Advent the same date can belong to the year beyond,
  // so it is held inside the year asked for: Advent Sunday stays Advent Sunday.
  const here = CY.reckoningNow();
  const c = here.fromDay(CY.fromIso(chosen));
  let d = c.d;
  while (d > 28 && !here.valid(c.y + by, c.m, d)) d -= 1;
  const t = currentTradition();
  const first = CY.yearStart(DATA, t, year), last = CY.yearStart(DATA, t, year + 1) - 1;
  // The year's first day goes to the next year's first day, wherever it falls.
  const day = CY.fromIso(chosen) === CY.yearStart(DATA, t, year - by) ? first
            : Math.min(last, Math.max(first, here.toDay(c.y + by, c.m, d)));
  drawYear(year, CY.iso(day));
}

const redrawSameDay = () => {
  const day = CY.fromIso(chosen);
  drawYear(parseInt(yearBox.value, 10), null);
  choose(CY.iso(day));
};
calBox.onchange = redrawSameDay;
paschalionBox.onchange = redrawSameDay;
$('in').onclick = () => setZoom(magnify + 0.5);
$('out').onclick = () => setZoom(magnify - 0.5);
mag.addEventListener('input', () => setZoom(+mag.value / 100));

// Rolling the mouse magnifies about the cursor, pinning whatever is under it.
// The page itself never scrolls, so nothing is taken away by claiming this.
//
// A trackpad (Apple's above all) sends the same wheel events, but many small
// ones a second, with momentum after the fingers lift, and in both axes: a
// two-finger swipe pans, and a pinch arrives as a wheel event with Ctrl held
// (Chrome, Edge, Firefox) or as Safari's own gesture events.  So the wheel's
// movement is measured, not counted: the magnification follows the size of
// each step, the pan follows the fingers, and all of it is applied once a
// frame, without the easing that the buttons and the menu use.
const WHEEL_LINE = 16, WHEEL_PAGE = 800;        // pixels per line, per page
// Magnification per pixel of wheel: 100 pixels (one notch of most mice) is
// the old fixed step of 18 per cent.
const ZOOM_PER_PIXEL = Math.log(1.18) / 100;
const gestureRange = k => Math.min(6, Math.max(1, k));
let wheelZoom = 1, wheelPanX = 0, wheelPanY = 0, wheelAt = null, wheelFrame = 0, gestureIdle = 0;

/** Apply what the wheel and the gestures have gathered since the last frame. */
function flushWheel() {
  wheelFrame = 0;
  if (wheelZoom !== 1 && wheelAt) {
    const next = gestureRange(magnify * wheelZoom);
    if (next !== magnify) {
      const holdX = (wheelAt.x - panX) / magnify, holdY = (wheelAt.y - panY) / magnify;
      magnify = next;
      if (magnify === 1) { panX = 0; panY = 0; }
      else { panX = wheelAt.x - next * holdX; panY = wheelAt.y - next * holdY; }
    }
  }
  if ((wheelPanX || wheelPanY) && magnify > 1) {
    const perPixel = 1 / svg.getScreenCTM().a;
    panX -= wheelPanX * perPixel;
    panY -= wheelPanY * perPixel;
  }
  wheelZoom = 1; wheelPanX = 0; wheelPanY = 0;
  clampPan();
  applyTransform(false, true);
  // When the gesture has died away, settle the magnification on a step the
  // menu and the link can name (to the nearest 0.05) without moving the view.
  clearTimeout(gestureIdle);
  gestureIdle = setTimeout(() => {
    const k = withinRange(magnify);
    if (k !== magnify && wheelAt) { wheelZoom = k / magnify; flushWheel(); }
    applyTransform(false);
  }, 200);
}
const queueWheel = () => { if (!wheelFrame) wheelFrame = requestAnimationFrame(flushWheel); };

/** A wheel event's movement in pixels, whatever unit it came in. */
function wheelPixels(ev) {
  const unit = ev.deltaMode === 1 ? WHEEL_LINE : ev.deltaMode === 2 ? WHEEL_PAGE : 1;
  return { x: ev.deltaX * unit, y: ev.deltaY * unit };
}

/** Whether a wheel event looks like a trackpad's two-finger swipe rather than a mouse wheel. */
function fromTrackpad(ev) {
  if (ev.deltaMode !== 0) return false;                 // lines or pages: a mouse
  if (ev.deltaX !== 0) return true;                     // sideways: fingers
  // A mouse notch is a large whole step (100 or 120 pixels, or a multiple);
  // fingers send small, often fractional ones.
  return Math.abs(ev.deltaY) < 50 || !Number.isInteger(ev.deltaY);
}

stage.addEventListener('wheel', ev => {
  // Inside someone else's page a plain roll scrolls that page, and Ctrl (or a
  // trackpad pinch, which arrives as Ctrl) magnifies, the way an embedded map
  // behaves.
  if (!owned && !ev.ctrlKey) return;
  ev.preventDefault();
  const d = wheelPixels(ev);
  wheelAt = atCursor(ev);
  if (!ev.ctrlKey && fromTrackpad(ev)) {
    // Two fingers move the magnified wheel the way they move a map.
    wheelPanX += d.x; wheelPanY += d.y;
  } else {
    // A pinch (Ctrl) is gentle per event, so it is given more weight than a
    // mouse notch, close to the fingers' own spread.
    wheelZoom *= Math.exp(-d.y * ZOOM_PER_PIXEL * (ev.ctrlKey ? 4 : 1));
  }
  queueWheel();
}, { passive: false });

// Safari reports a trackpad pinch as gesture events with the scale since the
// pinch began; without this it magnifies the whole page instead.
let gestureFrom = null;
stage.addEventListener('gesturestart', ev => {
  ev.preventDefault();
  gestureFrom = { magnify: magnify, scale: 1 };
});
stage.addEventListener('gesturechange', ev => {
  ev.preventDefault();
  if (!gestureFrom) return;
  wheelAt = atCursor(ev);
  wheelZoom *= (ev.scale || 1) / gestureFrom.scale;
  gestureFrom.scale = ev.scale || 1;
  queueWheel();
});
stage.addEventListener('gestureend', ev => { ev.preventDefault(); gestureFrom = null; });

// Dragging pans, but only once the pointer has actually moved: a press that
// stays put is a click, and clicking still picks the day underneath.
stage.addEventListener('pointerdown', ev => {
  if (ev.pointerType === 'touch') {
    touches.set(ev.pointerId, { x: ev.clientX, y: ev.clientY });
    if (touches.size === 2) { startPinch(); return; }
  }
  if (pinch || ev.button !== 0 || magnify === 1) return;
  dragFrom = { x: ev.clientX, y: ev.clientY, panX: panX, panY: panY };
  dragged = false;
});

/**
 * Two fingers magnify about the point between them and carry it with them, so
 * pinching and moving at once zooms and pans in one gesture, the way a map on
 * a phone does.  The point under the fingers is held in the wheel's own
 * coordinates, exactly as rolling the mouse holds the point under the cursor.
 */
function fingers() {
  const [a, b] = Array.from(touches.values());
  return { dist: Math.hypot(b.x - a.x, b.y - a.y) || 1,
           mid: { clientX: (a.x + b.x) / 2, clientY: (a.y + b.y) / 2 } };
}

function startPinch() {
  dragFrom = null;
  const f = fingers();
  const v = atCursor(f.mid);
  pinch = { dist: f.dist, magnify: magnify,
            holdX: (v.x - panX) / magnify, holdY: (v.y - panY) / magnify };
}

function movePinch() {
  const f = fingers();
  const v = atCursor(f.mid);
  magnify = gestureRange(pinch.magnify * f.dist / pinch.dist);
  if (magnify === 1) { panX = 0; panY = 0; }
  else { panX = v.x - magnify * pinch.holdX; panY = v.y - magnify * pinch.holdY; }
  clampPan();
  applyTransform(false, true);
}

stage.addEventListener('pointermove', ev => {
  if (touches.has(ev.pointerId)) touches.set(ev.pointerId, { x: ev.clientX, y: ev.clientY });
  if (pinch) { if (touches.size >= 2) movePinch(); return; }
  if (!dragFrom) return;
  const dx = ev.clientX - dragFrom.x, dy = ev.clientY - dragFrom.y;
  if (!dragged && Math.hypot(dx, dy) < 4) return;
  if (!dragged) { dragged = true; stage.setPointerCapture(ev.pointerId); }
  // A screen pixel is this many of the wheel's own units.  Taken from the
  // matrix rather than from the element's width: the element now fills the
  // stage, so its width is the window's, not the drawing's.
  const perPixel = 1 / svg.getScreenCTM().a;
  panX = dragFrom.panX + dx * perPixel;
  panY = dragFrom.panY + dy * perPixel;
  clampPan();
  applyTransform(false, true);
});

for (const done of ['pointerup', 'pointercancel', 'pointerleave']) {
  stage.addEventListener(done, ev => {
    if (dragged && stage.hasPointerCapture(ev.pointerId)) {
      stage.releasePointerCapture(ev.pointerId);
    }
    // A drag or a pinch has moved the view without easing; settle it.
    if (dragFrom && dragged) applyTransform(false);
    dragFrom = null;
    if (touches.delete(ev.pointerId) && pinch && touches.size < 2) {
      // The finger left behind must not become a drag or a tap on its own.
      pinch = null;
      quietUntil = performance.now() + 400;
      wheelAt = null;
      const k = withinRange(magnify);
      if (k !== magnify) zoomAbout(k, G.width / 2, G.height / 2);
      applyTransform(false);
    }
  });
}

addEventListener('keydown', ev => {
  const t = ev.target;
  if (t && (/^(INPUT|SELECT|TEXTAREA)$/.test(t.tagName) || t.isContentEditable)) return;
  // In someone else's page the keys are the wheel's only while it has the focus.
  if (!owned && !app.contains(document.activeElement)) return;
  // On the wheel Left and Right go round it a week at a time, Up and Down a
  // day (Up back, Down on); Shift with any of them, a month.
  const back = ev.key === 'ArrowLeft' || ev.key === 'ArrowUp';
  const arrow = back ? -1 : ((ev.key === 'ArrowRight' || ev.key === 'ArrowDown') ? 1 : 0);
  const days = (ev.key === 'ArrowLeft' || ev.key === 'ArrowRight') ? 7 : 1;
  if (arrow && ev.shiftKey && !ev.ctrlKey && !ev.altKey && !ev.metaKey) { pushNext = true; stepMonth(arrow, !arrowsBox.checked); ev.preventDefault(); return; }
  // Ctrl, Cmd and Alt belong to the browser: Ctrl + and - zoom the page for
  // anyone who needs larger text, and Alt+Left goes Back.
  if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
  if (arrow) { if (days > 1) pushNext = true; stepInYear(days * arrow); ev.preventDefault(); }
  else if (ev.key === '+' || ev.key === '=') { setZoom(magnify + 0.5); ev.preventDefault(); }
  else if (ev.key === '-' || ev.key === '_') { setZoom(magnify - 0.5); ev.preventDefault(); }
  else if (ev.key === '0') { toggleWholeWheel(); ev.preventDefault(); }
  else if (ev.key.toLowerCase() === 't') { pushNext = true; choose(isoToday()); }
  else if (ev.key.toLowerCase() === 'f') { findBox.focus(); findBox.select(); ev.preventDefault(); }
  else if (ev.key.toLowerCase() === 'w') { openWeek(); ev.preventDefault(); }
  // The Year box now lives behind the gear, so the keyboard steps whole
  // years rather than making that a trip into the panel each time: PageDown
  // goes on a year and PageUp back, as they do in a date picker.
  else if (ev.key === 'PageUp') { stepYear(-1); ev.preventDefault(); }
  else if (ev.key === 'PageDown') { stepYear(1); ev.preventDefault(); }
});

// ---- Find a day ----------------------------------------------------------
// A name typed in the bar's search box, matched against the days of the year
// on the wheel: their titles, feasts and the first day of each season.

/** A day as a short label: "Sun, Dec 25" (the weekday the day's own, the month and day this calendar's). */
function shortDate(iso) {
  const day = CY.fromIso(iso);
  const named = CY.reckoningNow().fromDay(day), g = CY.gregorianOf(day);
  const wd = new Intl.DateTimeFormat(undefined, { weekday: 'short', timeZone: 'UTC' }).format(utcOn(g.y, g.m, g.d));
  return wd + ', ' + utcOn(named.y, named.m, named.d).toLocaleDateString(undefined, { month: 'short', day: 'numeric', timeZone: 'UTC' });
}
/** Text as it is matched: lower case, without accents, one kind of apostrophe, single spaces. */
const findForm = text => String(text || '').normalize('NFD').replace(/[̀-ͯ]/g, '')
  .toLowerCase().replace(/[‘’ʼ`]/g, "'").replace(/\s+/g, ' ').trim();
const findBox = $('find'), findList = $('findList');
let findIndex = null, findKey = '', findAt = -1, findHits = [];

/** The year's names to match: [{ iso, name, form }], in the year's order. */
function findNames() {
  if (findIndex && findKey === drawn) return findIndex;
  const out = [];
  let season = '';
  for (const iso of dates) {
    const info = DAYS[iso] || {};
    const seen = new Set();
    const add = name => {
      name = String(name || '').replace(/\s*\n\s*/g, ' ').trim();
      if (name && !seen.has(name)) { seen.add(name); out.push({ iso: iso, name: name, form: findForm(name) }); }
    };
    (info.T || info.t || []).forEach(add);
    (info.F || info.f || []).forEach(add);
    if (info.s && info.s !== season) add(info.s);
    season = info.s || season;
  }
  findIndex = out;
  findKey = drawn;
  return out;
}

function findShow() {
  const q = findForm(findBox.value);
  findAt = -1;
  if (!q) { findList.hidden = true; findBox.setAttribute('aria-expanded', 'false'); return; }
  const words = q.split(' ');
  const hits = findNames().filter(n => words.every(w => n.form.indexOf(w) >= 0));
  // Names that begin with what was typed first, then the rest, each in the year's order.
  const first = hits.filter(n => n.form.indexOf(q) === 0);
  findHits = first.concat(hits.filter(n => n.form.indexOf(q) !== 0)).slice(0, 40);
  if (!findHits.length) {
    const li = document.createElement('li');
    li.className = 'none';
    li.textContent = 'No day of ' + headYear.textContent + ' by that name';
    findList.replaceChildren(li);
  } else {
    findList.replaceChildren(...findHits.map((n, i) => {
      const li = document.createElement('li');
      li.id = 'findHit' + i;
      li.setAttribute('role', 'option');
      li.setAttribute('aria-selected', 'false');
      const on = document.createElement('span');
      on.className = 'on';
      on.textContent = shortDate(n.iso);
      li.append(on, n.name);
      li.addEventListener('pointerdown', ev => { ev.preventDefault(); findPick(i); });
      return li;
    }));
  }
  findList.hidden = false;
  findBox.setAttribute('aria-expanded', 'true');
}

function findMark(i) {
  if (!findHits.length) return;
  findAt = (i + findHits.length) % findHits.length;
  findList.querySelectorAll('li[role=option]').forEach((li, k) => li.setAttribute('aria-selected', String(k === findAt)));
  const li = $('findHit' + findAt);
  if (li) { li.scrollIntoView({ block: 'nearest' }); findBox.setAttribute('aria-activedescendant', li.id); }
}

function findPick(i) {
  const hit = findHits[i];
  if (!hit) return;
  findClose();
  findBox.value = '';
  pushNext = hit.iso !== chosen;
  choose(hit.iso);
  stage.focus({ preventScroll: true });
}

function findClose() {
  findList.hidden = true;
  findBox.setAttribute('aria-expanded', 'false');
  findBox.removeAttribute('aria-activedescendant');
}

findBox.addEventListener('input', findShow);
findBox.addEventListener('focus', () => { if (findBox.value) findShow(); });
findBox.addEventListener('blur', findClose);
findBox.addEventListener('keydown', ev => {
  if (ev.key === 'ArrowDown') { if (findList.hidden) findShow(); findMark(findAt + 1); ev.preventDefault(); }
  else if (ev.key === 'ArrowUp') { findMark(findAt - 1); ev.preventDefault(); }
  else if (ev.key === 'Enter') { findPick(findAt >= 0 ? findAt : 0); ev.preventDefault(); }
  else if (ev.key === 'Escape') {
    if (!findList.hidden) findClose(); else { findBox.value = ''; stage.focus({ preventScroll: true }); }
    ev.preventDefault();
  }
});

// ---- The week in a list -----------------------------------------------------
// The chosen day's week, Sunday to Saturday: each day's names, color and
// readings (of the kinds the Readings boxes show), for reading on a phone,
// where the wheel's cells are small.  A day's date chooses it.
const weekDialog = $('weekDialog'), weekList = $('weekList');
let weekFrom = null;

/** The Sunday on or before a day. */
const sundayOf = day => day - (((day + 3) % 7 + 7) % 7 + 1) % 7;

function showWeek(from) {
  weekFrom = from;
  const first = CY.iso(from), last = CY.iso(from + 6);
  $('weekHead').textContent = shortDate(first) + ' – ' + shortDate(last);
  const items = [];
  for (let z = from; z < from + 7; z++) {
    const iso = CY.iso(z);
    const info = DAYS[iso];
    const li = document.createElement('li');
    if (iso === chosen) li.className = 'chosen';
    const head = document.createElement('div');
    head.className = 'day';
    const go = document.createElement('button');
    go.type = 'button';
    go.textContent = shortDate(iso);
    go.title = 'Choose ' + pretty(iso) + ' on the wheel';
    go.addEventListener('click', () => {
      pushNext = iso !== chosen;
      choose(iso);
      if (DAYS[iso]) showWeek(sundayOf(CY.fromIso(iso)));
    });
    head.append(go);
    if (info) {
      const sw = document.createElement('span');
      sw.className = 'swatch';
      sw.style.background = cssPaint(info.fill);
      const names = [].concat(info.T || info.t || [], info.F || info.f || []).map(n => String(n).replace(/\s*\n\s*/g, ' '));
      const nm = document.createElement('span');
      nm.className = 'names';
      nm.textContent = names.join(' · ') || info.W || '';
      const sea = document.createElement('span');
      sea.className = 'season';
      sea.textContent = (info.s || '') + (info.c ? ' · ' + colorWords(info.c, info.a) : '');
      head.append(sw, nm, sea);
      li.append(head);
      const want = readingsOn();
      if (hasReadings() && readingKindsOf(currentTradition()).some(k => want.indexOf(k) >= 0)) {
        const sets = document.createElement('div');
        sets.className = 'sets';
        sets.append(...readingLinesFor(iso));
        if (sets.childNodes.length) li.append(sets);
      }
    } else {
      const sea = document.createElement('span');
      sea.className = 'season';
      sea.textContent = 'In another church year: choose the day to draw it.';
      head.append(sea);
      li.append(head);
    }
    items.push(li);
  }
  weekList.replaceChildren(...items);
}

function openWeek() {
  if (!chosen) return;
  showWeek(sundayOf(CY.fromIso(chosen)));
  if (weekDialog.showModal) { if (!weekDialog.open) weekDialog.showModal(); } else weekDialog.setAttribute('open', '');
  $('weekHead').focus();
}
$('weekBtn').addEventListener('click', openWeek);
$('weekPrev').addEventListener('click', () => showWeek(weekFrom - 7));
// Printed, the week stands alone on the paper: the church and year, the week,
// and each day with its names, color and readings, the links as plain text.
// The dialog closes while it prints and opens again after.
$('weekPrint').addEventListener('click', () => {
  let box = app.querySelector(':scope > .weekprint');
  if (!box) { box = document.createElement('div'); box.className = 'weekprint'; app.append(box); }
  const h1 = document.createElement('h1');
  h1.textContent = headYear.textContent;
  const church = document.createElement('div');
  church.className = 'church';
  church.textContent = headChurch.textContent;
  const h2 = document.createElement('h2');
  h2.textContent = $('weekHead').textContent;
  const list = weekList.cloneNode(true);
  list.removeAttribute('id');
  // Each day's date as text rather than a button, with its year.
  list.querySelectorAll('.day button').forEach((b, i) => {
    const s = document.createElement('span');
    s.className = 'date';
    s.textContent = pretty(CY.iso(weekFrom + i));
    b.replaceWith(s);
  });
  box.replaceChildren(h1, church, h2, list);
  app.classList.add('printing-week');
  weekDialog.close();
  let done = false;
  const after = () => {
    if (done) return;
    done = true;
    app.classList.remove('printing-week');
    box.replaceChildren();
    if (weekDialog.showModal) weekDialog.showModal(); else weekDialog.setAttribute('open', '');
  };
  addEventListener('afterprint', after, { once: true });
  window.print();
  // A browser whose print() waits for the dialog has finished by now; one that does
  // not (some phones) says so with afterprint.
  setTimeout(() => { if (!matchMedia('print').matches) after(); }, 500);
});
$('weekNext').addEventListener('click', () => showWeek(weekFrom + 7));

// The page opens on whatever config.csv asked for.  A blank paschalion means
// "follow the calendar", which is the blank first option in its picker.
buildTraditionMenu();
buildArtMenu();
applyDefaults();

box.min = PICKABLE_FIRST;
box.max = PICKABLE_LAST;

/**
 * A native date box cannot hold a year outside 1 to 9999 -- there is no value
 * it would accept -- so outside that it is turned off rather than left showing
 * a date that is not the one on the wheel.  The Year box, the arrows and
 * clicking a cell all still work, and the readout still names the day.
 */
function syncDateBox() {
  const day = CY.fromIso(chosen);
  const reachable = day >= CY.fromIso(PICKABLE_FIRST)
                 && day <= CY.fromIso(PICKABLE_LAST);
  box.disabled = !reachable;
  box.title = reachable ? '' : 'Dates outside AD 1 to 9999 cannot be typed; '
            + 'use the Year box, the arrows, or click a cell';
  box.value = reachable ? chosen : '';
}

/** Say plainly when the reader has left the calendar this rule belongs to. */
function syncNote(extra) {
  const here = CY.reckoningNow();
  const year = here.fromDay(CY.fromIso(chosen)).y;
  const parts = [];
  // The warning is about extrapolating the Gregorian rules backwards, so it
  // does not apply when the wheel is honestly drawn in the older calendar.
  if (here === CY.GREGORIAN && year < GREGORIAN_YEAR) {
    parts.push('Before the Gregorian calendar — these are the modern rules '
             + 'run backwards, not a record of what was kept.');
  }
  // Name the pairing whenever it is not the plain Western one, which now
  // includes a Gregorian wheel that has been given the Eastern Easter.
  if (here !== CY.GREGORIAN || paschalionName !== 'Gregorian') {
    parts.push(here.label + ' dates, ' + paschalionName + ' Easter.');
  }
  note.textContent = parts.join(' · ');
  timing.textContent = extra || '';
}

// ---------------------------------------------------------------------------
// Links
// ---------------------------------------------------------------------------
// The address carries the day on the wheel and anything set away from what
// config.csv asked for, so a link opens exactly this view:
//
//   #date=2026-12-25
//   #date=2027-04-18&lectionary=lcms-one-year&latin=1&zoom=2.5
//   #year=2030                      (an Advent year, opening on its first day)
//   #2026-12-25                     (a bare date works too)
//   #date=today                     (whatever day it is when the link is opened)
//
// Settings left at the file's own values are left out, so a plain link stays
// short and follows the file if config.csv changes later.  While the wheel is on
// today the address says `date=today` rather than the date, so a bookmark or a
// reload next week opens on next week's today; Copy link writes the date out.

let lastHash = '';

function linkState(explicit) {
  const d = DATA.settings;
  const parts = [['date', explicit || chosen !== isoToday() ? chosen : 'today']];
  const own = profileOf(currentTradition()).settings;
  if (currentTradition() !== DATA.defaultTradition) parts.push(['lectionary', currentTradition()]);
  if (chosenSubs().join(',') !== DATA.defaultSubcalendars.join(',')) {
    parts.push(['sub', chosenSubs().join(',') || 'none']);
  }
  if (calBox.value !== own.calendar) parts.push(['calendar', calBox.value]);
  if (paschalionBox.value !== (own.paschalion || '')) {
    parts.push(['easter', paschalionBox.value || 'calendar']);
  }
  if (artBox.value !== defaultArt()) parts.push(['art', artBox.value]);
  if (feastBox.value !== d.feast_detail) parts.push(['feasts', feastBox.value]);
  if (darkReds.checked !== (midDefault() === 'dark-reds')) parts.push(['reds', darkReds.checked ? 'dark' : 'set']);
  if (latinBox.checked !== latinDefault()) parts.push(['latin', latinBox.checked ? '1' : '0']);
  if (readingsParam()) parts.push(['readings', readingsParam()]);
  if (bibleBox.value !== bibleDefault()) parts.push(['bible', bibleBox.value]);
  if (siteBox.value !== bibleSiteDefault()) parts.push(['bibleat', siteBox.value]);
  if (!w2wOff() && w2wBox.checked !== w2wDefault()) parts.push(['songs', w2wBox.checked ? '1' : '0']);
  if (!hymnaryOff() && hymnsBox.checked !== hymnaryDefault()) parts.push(['hymns', hymnsBox.checked ? '1' : '0']);
  if (!propersBox.checked) parts.push(['propers', '0']);
  if (!hymnalRow.hidden && hymnalBox.value !== hymnalDefault()) parts.push(['hymnal', hymnalBox.value]);
  if (yearLineBox.checked !== yearLineDefault()) parts.push(['yearline', yearLineBox.checked ? '1' : '0']);
  if (arrowsBox.checked !== arrowsDefault()) parts.push(['arrows', arrowsBox.checked ? '1' : '0']);
  if (layoutNow() !== layoutDefault()) parts.push(['layout', layoutNow()]);
  if (showHelp.checked !== footDefaults().help) parts.push(['help', showHelp.checked ? '1' : '0']);
  if (showCredit.checked !== footDefaults().credit) parts.push(['credit', showCredit.checked ? '1' : '0']);
  if (ringKey() !== hiddenDefaultKey()) parts.push(['hide', ringKey() || 'none']);
  if (colorsParam() !== colorsDefaultKey()) parts.push(['colors', colorsParam() || 'none']);
  if (Math.abs(magnify - defaultZoom()) > 0.005) parts.push(['zoom', String(+magnify.toFixed(2))]);
  return '#' + parts.map(p => p[0] + '=' + encodeURIComponent(p[1]).replace(/%2C/g, ',').replace(/%3A/g, ':'))
                     .join('&');
}

// Back and Forward go through the reader's changes: a change of settings, or
// a day picked (clicked, typed, Today, a new year), is a step of its own in
// the browser's history.  Stepping day by day with the arrows and zooming
// only rewrite the current step, so Back does not crawl through every day.
let pushNext = false;       // the next change of address is a day picked
let restoring = true;       // while opening, and while Back/Forward applies a step
const settingsPart = h => h.replace(/^#/, '').split('&')
  .filter(p => !/^(date|zoom)=/.test(p)).join('&');

function syncLink() {
  // Someone else's page keeps its own address; Copy link still works there.
  if (!chosen || !owned) return;
  const hash = linkState();
  lastHash = hash;
  const push = pushNext;
  pushNext = false;
  if (hash === location.hash) return;
  const step = !restoring && (push || settingsPart(hash) !== settingsPart(location.hash));
  // A browser that refuses the history API for a local file falls back to
  // location.replace, which for a change of hash does not reload.
  try {
    if (step) history.pushState(null, '', hash);
    else history.replaceState(null, '', hash);
  } catch (e) { location.replace(hash); }
}

function readLink(hash) {
  const text = (hash || '').replace(/^#/, '');
  if (!text) return null;
  if (/^[+-]?\d{4,6}-\d\d-\d\d$/.test(text) || /^today$/i.test(text)) return { date: text };
  const out = {};
  for (const part of text.split('&')) {
    const i = part.indexOf('=');
    if (i <= 0) continue;
    try { out[part.slice(0, i).toLowerCase()] = decodeURIComponent(part.slice(i + 1)); }
    catch (e) { /* a mangled value is skipped, not fatal */ }
  }
  return Object.keys(out).length ? out : null;
}

/** Set a dropdown only to a value it actually offers. */
function pick(select, value) {
  if (value == null) return;
  if (Array.from(select.options).some(o => o.value === value)) select.value = value;
}

/** Put the page into the state a link describes.  Returns false if it named no day. */
function applyLink(state) {
  if (!state) return false;
  if (state.lectionary) {
    const key = String(state.lectionary).trim().toLowerCase();
    if (TRADITIONS.some(t => t.key === key)) {
      setTradition(key);
      const own = profileOf(key).settings;
      pick(calBox, own.calendar);
      paschalionBox.value = '';
      pick(paschalionBox, own.paschalion || '');
      latinBox.checked = latinDefault();
      pick(bibleBox, bibleDefault());
    }
  }
  if (state.sub != null) setSubs(state.sub === 'none' ? [] : state.sub.split(','));
  if (state.art != null && !isFixed('artwork')) pick(artBox, state.art);
  if (!isFixed('calendar')) pick(calBox, state.calendar);
  if (state.easter != null && !isFixed('easter')) pick(paschalionBox, state.easter === 'calendar' ? '' : state.easter);
  pick(feastBox, state.feasts);
  if (state.reds != null && !isFixed('reds')) darkReds.checked = /^(dark|1|true|yes|on)$/i.test(state.reds);
  if (state.latin != null) latinBox.checked = /^(1|true|yes|on)$/i.test(state.latin);
  if (state.readings != null) {
    const kinds = readingKindsFrom(state.readings);
    for (const b of readingBoxes) b.checked = kinds.indexOf(b.dataset.reading) >= 0;
  }
  if (state.bible != null && !bibleFixed()) pick(bibleBox, String(state.bible).toUpperCase());
  if (state.bibleat != null) pick(siteBox, state.bibleat);
  if (state.songs != null && !w2wOff()) w2wBox.checked = /^(1|true|yes|on)$/i.test(state.songs);
  if (state.hymns != null && !hymnaryOff()) hymnsBox.checked = /^(1|true|yes|on)$/i.test(state.hymns);
  if (state.propers != null) propersBox.checked = /^(1|true|yes|on)$/i.test(state.propers);
  if (state.hymnal != null) pick(hymnalBox, state.hymnal);
  if (state.yearline != null) yearLineBox.checked = /^(1|true|yes|on)$/i.test(state.yearline);
  if (state.arrows != null) arrowsBox.checked = /^(1|true|yes|on)$/i.test(state.arrows);
  if (state.layout != null && layoutsOffered().indexOf(String(state.layout)) >= 0) pick(layoutBox, String(state.layout));
  if (state.help != null) showHelp.checked = /^(1|true|yes|on)$/i.test(state.help);
  if (state.credit != null) showCredit.checked = /^(1|true|yes|on)$/i.test(state.credit);
  applyFooter();
  // The day cells and the artwork cannot be switched off from the menu, and a
  // hand-made link cannot do it either: without the day cells there is no
  // wheel to draw (setHidden skips them).  hide=none shows every ring.
  if (state.hide != null) setHidden(state.hide === 'none' ? [] : state.hide.split(','));

  if (state.colors != null) readColorsParam(state.colors);

  let landed = false;
  const year = parseInt(state.year, 10);
  const m = /^([+-]?\d{4,6})-(\d\d)-\d\d$/.exec(state.date || '');
  try {
    if (/^today$/i.test(state.date || '')) {
      // Today is a day, not a label: find it after the link's calendar is set.
      const day = CY.todayDay(), g = CY.gregorianOf(day);
      drawYear(g.m >= 11 ? g.y : g.y - 1, null);
      choose(CY.iso(day));
      landed = true;
    } else if (m) {
      // Draw first so the date is read in the calendar the link asked for,
      // then choose it: if the guess of its Advent year was a year out, choose
      // redraws for the right one.
      const y = parseInt(m[1], 10);
      const guess = +m[2] >= 11 ? y : y - 1;
      drawYear(Math.min(LAST_YEAR, Math.max(FIRST_YEAR, guess)), null);
      choose(CY.iso(CY.fromIso(state.date)));
      landed = true;
    } else if (!isNaN(year) && year >= FIRST_YEAR && year <= LAST_YEAR) {
      drawYear(year, null);
      landed = true;
    }
  } catch (e) {
    landed = false;                          // a date the wheel cannot read
  }
  if (!landed) return false;
  applyZoom(state);
  return true;
}

/** The magnification the page opens at (church_year.py --zoom / page_zoom; 1: the whole wheel). */
const defaultZoom = () => {
  const z = parseFloat(DATA.openZoom);
  return isNaN(z) ? 1 : withinRange(z);
};

/** The magnification a link asks for (none: the page's own, defaultZoom). */
function applyZoom(state) {
  const z = parseFloat(state && state.zoom);
  magnify = isNaN(z) ? defaultZoom() : withinRange(z);
  if (magnify === 1) resetZoom(); else focusChosen(false);
}

addEventListener('hashchange', () => {
  if (location.hash === lastHash) return;    // our own write coming back
  lastHash = location.hash;
  // A link describes the whole page: whatever it leaves out is at its default,
  // so the settings in hand are put back first rather than carried over.
  const state = readLink(location.hash);
  restoring = true;
  applyDefaults();
  // A link that names no day still changes the settings: redraw the day in hand.
  if (!applyLink(state)) { redrawSameDay(); applyZoom(state); }
  markChanged();
  syncLink();
  restoring = false;
});

/** Put text on the clipboard; true if it got there. */
async function copyText(text) {
  let ok = false;
  try { await navigator.clipboard.writeText(text); ok = true; }
  catch (e) {
    // No clipboard API here (an old browser, or a local file in some): copy
    // through a scratch text box instead.
    const t = document.createElement('textarea');
    t.value = text; t.setAttribute('readonly', ''); t.style.position = 'fixed';
    t.style.opacity = '0'; document.body.appendChild(t); t.select();
    try { ok = document.execCommand('copy'); } catch (e2) { ok = false; }
    t.remove();
  }
  return ok;
}

/** Say on a button whether its copy worked, then put its name back. */
function copied(btn, ok, label) {
  btn.textContent = ok ? 'Copied' : 'Copy failed';
  setTimeout(() => { btn.textContent = label; }, 1600);
}

async function copyLink() {
  syncLink();
  // The day written out, so the link opens on this day however late it is read.
  copied(copyBtn, await copyText(location.href.replace(/#.*$/, '') + linkState(true)), 'Copy link');
}
copyBtn.addEventListener('click', copyLink);

// Copy embed code: an iframe of this page, to show it inside another website's
// page.  It carries the settings on screen and the magnification, but not the
// day, so it always opens on the day it is read.  A page that is itself pasted into another
// (church_year.py --fragment) has no address of its own to give, so it has no
// such button.
const embedBtn = $('embedBtn');
async function copyEmbed() {
  syncLink();
  const src = location.href.replace(/#.*$/, '') + linkState(false).replace(/^#date=[^&]*(&|$)/, '#').replace(/^#$/, '');
  const esc = s => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;');
  const code = '<iframe src="' + esc(src) + '" title="' + 'Church year calendar'
    + '" style="width:100%;height:90vh;border:0" allow="clipboard-write"></iframe>';
  copied(embedBtn, await copyText(code), 'Copy embed code');
}
embedBtn.addEventListener('click', copyEmbed);

// The Feedback link in the bottom left corner (church_year.py --feedback / page_feedback):
// the form, with the day on screen, its church and a link back to it.
const feedbackLink = $('feedback');
function feedbackUrl() {
  const base = String(DATA.feedback || '');
  const values = {
    link: location.href.replace(/#.*$/, '') + linkState(true),
    date: chosen || '',
    church: (traditionOf(currentTradition()) || {}).label || currentTradition(),
  };
  if (/\{(link|date|church)\}/.test(base)) {
    return base.replace(/\{(link|date|church)\}/g, (m, k) => encodeURIComponent(values[k]));
  }
  if (/^mailto:/i.test(base)) {
    const body = 'Date: ' + values.date + '\nChurch: ' + values.church + '\nLink: ' + values.link + '\n\n';
    return base + (base.indexOf('?') >= 0 ? '&' : '?') + 'body=' + encodeURIComponent(body);
  }
  return base + (base.indexOf('?') >= 0 ? '&' : '?')
    + Object.keys(values).map(k => k + '=' + encodeURIComponent(values[k])).join('&');
}
// The Help button beside it (church_year.py --help-link / page_help): the user guide.
if (DATA.help) { const helpLink = $('help'); helpLink.hidden = false; helpLink.href = DATA.help; }
if (DATA.feedback) {
  feedbackLink.hidden = false;
  feedbackLink.href = DATA.feedback;
  // Brought up to date just before it is followed, however it is opened.
  for (const ev of ['pointerdown', 'focus', 'click', 'contextmenu']) {
    feedbackLink.addEventListener(ev, () => { feedbackLink.href = feedbackUrl(); });
  }
}
printBtn.addEventListener('click', () => { settings.open = false; window.print(); });

// ---------------------------------------------------------------------------
// Download: the wheel as SVG and PNG files, made here in the browser from the
// same drawing church_year_image.py writes (CY.renderDocument), for the year on the
// wheel or a run of years.  More than one file comes as a .zip.
// ---------------------------------------------------------------------------

const filesDialog = $('filesDialog');
const filesFrom = $('filesFrom'), filesTo = $('filesTo');
const filesSvg = $('filesSvg'), filesPng = $('filesPng');
const filesWidth = $('filesWidth'), filesBack = $('filesBack');
const filesStatus = $('filesStatus'), filesMake = $('filesMake');
const listReadings = $('listReadings'), listLinks = $('listLinks'), listColors = $('listColors');
const listDays = $('listDays'), listEvery = $('listEvery'), listFeasts = $('listFeasts');
const listMajor = $('listMajor'), listFeastLinks = $('listFeastLinks'), listFormat = $('listFormat');
const listOverview = $('listOverview');
const LISTS = window.ChurchYearLists;
// The page's own link makers, for the lists' links (as the readout makes them).
const LIST_LINKS = { parts: readingParts, group: groupUrl, feast: feastUrlFor, numbering: numberingBooks };
const MAX_FILE_YEARS = 101;

/** A church year's short name, as in file names: 2026-27, 9999-10000, 6-5BC (traditions.py: year_label). */
function yearLabel(y) {
  if (y >= 1 && y + 1 <= 9999) return y + '-' + String((y + 1) % 100).padStart(2, '0');
  if (y < 1 && y + 1 < 1) return (1 - y) + '-' + (-y) + 'BC';
  if (y === 0) return '1BC-1';
  return y + '-' + (y + 1);
}

const filesYears = $('filesYears');
function filesYearsNote() {
  const a = Math.round(+filesFrom.value), b = Math.round(+filesTo.value);
  const n = b - a + 1;
  filesYears.textContent = !(n > 0) ? 'The last year is before the first.'
    : n > MAX_FILE_YEARS ? 'At most ' + MAX_FILE_YEARS + ' years at a time.'
    : n === 1 ? 'The church year ' + CY.spanName(a, a + 1) + '.'
    : n + ' church years, ' + CY.spanName(a, a + 1) + ' to ' + CY.spanName(b, b + 1) + '.';
  // A long run of PNGs is large: about 4.8 MB each at 5,000 pixels, growing with the area.
  if (n > 1 && n <= MAX_FILE_YEARS && filesPng.checked) {
    const w = Math.max(500, Math.min(16000, Math.round(+filesWidth.value) || 5000));
    const mb = n * (4.8 * (w / 5000) * (w / 5000) + (filesSvg.checked ? 0.26 : 0));
    if (mb >= 50) filesYears.textContent += ' The PNGs make this about ' + (mb >= 1000 ? (mb / 1024).toFixed(1) + ' GB' : Math.round(mb / 10) * 10 + ' MB')
      + ' and take a while; a narrower PNG makes it smaller.';
  }
}

$('filesBtn').addEventListener('click', () => {
  const y = drawnYear();
  filesFrom.min = filesTo.min = FIRST_YEAR; filesFrom.max = filesTo.max = LAST_YEAR;
  filesFrom.value = filesTo.value = y;
  if (!filesWidth.dataset.set) {
    filesWidth.value = +(DATA.settings && DATA.settings.png_width) || 5000;
    const back = String((DATA.settings && DATA.settings.png_background) || 'none').toLowerCase();
    filesBack.value = /^#?f{3}(f{3})?$|^white$/.test(back) ? '#ffffff' : 'none';
    filesWidth.dataset.set = '1';
  }
  filesStatus.textContent = '';
  // A church with no readings yet has no readings list.
  $('listReadingsRow').hidden = !hasReadings();
  // A page without links offers lists without them.
  $('listReadingsOpts').hidden = !hasReadings() || !bibleLinks;
  listFeastLinks.parentElement.hidden = !feastLinks;
  if (!bibleLinks) listLinks.checked = false;
  if (!feastLinks) listFeastLinks.checked = false;
  if (!hasReadings()) listReadings.checked = false;
  filesYearsNote();
  if (filesDialog.showModal) filesDialog.showModal(); else filesDialog.setAttribute('open', '');
});
filesFrom.addEventListener('input', () => { if (+filesTo.value < +filesFrom.value) filesTo.value = filesFrom.value; filesYearsNote(); });
filesTo.addEventListener('input', filesYearsNote);
for (const el of [filesPng, filesSvg, filesWidth]) el.addEventListener('input', filesYearsNote);

/** A picture put beside the page, as a data: address the files can carry (or '' when it cannot be read). */
async function localArtData() {
  if (!localArt) return '';
  try {
    const blob = await (await fetch(localArt)).blob();
    return await new Promise((ok, no) => { const r = new FileReader(); r.onload = () => ok(r.result); r.onerror = no; r.readAsDataURL(blob); });
  } catch (e) { return ''; }
}

/** The wheel's SVG for a year, as church_year_image.py draws it, with a picture of the page's own in the middle. */
function wheelSvg(year, artData) {
  // By season: a file holds one picture, the season's of the day chosen here
  // when that day is in the year drawn, and the church's own in any other year.
  const seasonal = artBox.value === 'season' && chosen ? { artDate: chosen } : {};
  let svg = CY.renderDocument(DATA, Object.assign(drawOptions(year), seasonal));
  if (artData && G) {
    const r = G.centerRadius * 0.97, x = G.cx - r, y = G.cy - r;
    const fit = /^data:image\/svg/.test(artData) ? 'xMidYMid meet' : 'xMidYMid slice';
    svg = svg.replace(/<\/svg>\s*$/, '<defs><clipPath id="cy-own-art"><circle cx="' + G.cx + '" cy="' + G.cy + '" r="' + r + '"/></clipPath></defs>'
      + '<image href="' + artData + '" xlink:href="' + artData + '" x="' + x + '" y="' + y + '" width="' + 2 * r + '" height="' + 2 * r
      + '" preserveAspectRatio="' + fit + '" clip-path="url(#cy-own-art)"/>\n</svg>\n');
  }
  return svg;
}

/** A PNG of an SVG, `width` pixels wide, on a clear or colored background. */
function svgToPng(svg, width, background) {
  return new Promise((ok, no) => {
    const m = /viewBox="0 0 ([\d.]+) ([\d.]+)"/.exec(svg);
    const w = m ? +m[1] : 2100, h = m ? +m[2] : 2100;
    const img = new Image();
    const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = width; canvas.height = Math.round(width * h / w);
      const ctx = canvas.getContext('2d');
      if (background && background !== 'none') { ctx.fillStyle = background; ctx.fillRect(0, 0, canvas.width, canvas.height); }
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);
      canvas.toBlob(b => (b ? ok(b) : no(new Error('the browser could not make the PNG'))), 'image/png');
    };
    img.onerror = () => { URL.revokeObjectURL(url); no(new Error('the browser could not read the drawing')); };
    img.src = url;
  });
}

// A .zip with its files stored as they are (PNG is already compressed).
const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
  return t;
})();
function crc32(bytes) {
  let c = 0xffffffff;
  for (let i = 0; i < bytes.length; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
async function makeZip(files) {
  const parts = [], central = [];
  let offset = 0;
  const now = new Date();
  const time = (now.getHours() << 11) | (now.getMinutes() << 5) | (now.getSeconds() >> 1);
  const date = ((now.getFullYear() - 1980) << 9) | ((now.getMonth() + 1) << 5) | now.getDate();
  for (const f of files) {
    const data = new Uint8Array(await f.blob.arrayBuffer());
    const name = new TextEncoder().encode(f.name);
    const crc = crc32(data);
    const head = new DataView(new ArrayBuffer(30));
    head.setUint32(0, 0x04034b50, true); head.setUint16(4, 20, true); head.setUint16(6, 0x0800, true);
    head.setUint16(10, time, true); head.setUint16(12, date, true);
    head.setUint32(14, crc, true); head.setUint32(18, data.length, true); head.setUint32(22, data.length, true);
    head.setUint16(26, name.length, true);
    parts.push(head, name, data);
    const dir = new DataView(new ArrayBuffer(46));
    dir.setUint32(0, 0x02014b50, true); dir.setUint16(4, 20, true); dir.setUint16(6, 20, true); dir.setUint16(8, 0x0800, true);
    dir.setUint16(12, time, true); dir.setUint16(14, date, true);
    dir.setUint32(16, crc, true); dir.setUint32(20, data.length, true); dir.setUint32(24, data.length, true);
    dir.setUint16(28, name.length, true); dir.setUint32(42, offset, true);
    central.push(dir, name);
    offset += 30 + name.length + data.length;
  }
  const size = central.reduce((n, p) => n + p.byteLength, 0);
  const end = new DataView(new ArrayBuffer(22));
  end.setUint32(0, 0x06054b50, true); end.setUint16(8, files.length, true); end.setUint16(10, files.length, true);
  end.setUint32(12, size, true); end.setUint32(16, offset, true);
  return new Blob([...parts, ...central, end], { type: 'application/zip' });
}

function saveBlob(blob, name) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  document.body.append(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
}

filesMake.addEventListener('click', async () => {
  const from = Math.round(+filesFrom.value), to = Math.round(+filesTo.value);
  const width = Math.max(500, Math.min(16000, Math.round(+filesWidth.value) || 5000));
  if (!(to >= from) || to - from + 1 > MAX_FILE_YEARS || from < FIRST_YEAR || to > LAST_YEAR) { filesYearsNote(); return; }
  const lists = [listReadings, listColors, listFeasts, listOverview].filter(b => b.checked && !b.closest('[hidden]'));
  if (!filesSvg.checked && !filesPng.checked && !lists.length) { filesStatus.textContent = 'Choose the wheel, a list, or both.'; return; }
  if (listFeasts.checked && feastBox.value === 'none' && !listMajor.checked) {
    filesStatus.textContent = 'The Feasts setting is None: choose another, or “with major days”, for a feasts list.'; return;
  }
  filesMake.disabled = true;
  const key = currentTradition();
  const files = [];
  try {
    const artData = artBox.value === 'local' ? await localArtData() : '';
    for (let y = from; y <= to && (filesSvg.checked || filesPng.checked); y++) {
      filesStatus.textContent = 'Drawing ' + yearLabel(y) + '…';
      await new Promise(r => setTimeout(r));          // let the note show
      const svg = wheelSvg(y, artData);
      const base = key + '_' + yearLabel(y) + '_calendar';
      if (filesSvg.checked) files.push({ name: base + '.svg', blob: new Blob([svg], { type: 'image/svg+xml' }) });
      if (filesPng.checked) files.push({ name: base + '.png', blob: await svgToPng(svg, width, filesBack.value) });
    }
    // The lists, each over the whole run of years, as the scripts write them.
    const fmt = listFormat.value;
    const o = { tradition: key, first: from, last: to, subcalendars: chosenSubs(), latinNames: latinBox.checked,
                calendar: chosenCalendar(), paschalion: chosenPaschalion(), feastDetail: feastBox.value };
    const type = { csv: 'text/csv', html: 'text/html', ics: 'text/calendar', json: 'application/json', md: 'text/markdown' }[fmt];
    const add = (made, t) => files.push({ name: made.name, blob: new Blob([made.text], { type: (t || type) + ';charset=utf-8' }) });
    for (const box of lists) {
      filesStatus.textContent = 'Listing ' + (box === listReadings ? 'the readings' : box === listColors ? 'the colors'
        : box === listOverview ? 'the years' : 'the feasts') + '…';
      await new Promise(r => setTimeout(r));
      if (box === listReadings) {
        add(LISTS.readingsList(DATA, Object.assign({}, o, { kinds: readingsOn(), propers: propersBox.checked,
          site: listLinks.checked ? siteBox.value : 'none', version: bibleBox.value || bibleDefault() }), fmt, LIST_LINKS));
      } else if (box === listOverview) {
        // One row a year has no calendar form (colors.py refuses it): with iCalendar it comes as CSV.
        if (fmt === 'ics') add(LISTS.overviewList(DATA, o, 'csv'), 'text/csv');
        else add(LISTS.overviewList(DATA, o, fmt));
      } else if (box === listColors) {
        add(LISTS.colorsList(DATA, Object.assign({}, o, { days: listDays.value, every: listEvery.checked }), fmt));
      } else {
        add(LISTS.feastsList(DATA, Object.assign({}, o, { detail: feastBox.value, major: listMajor.checked,
          every: listEvery.checked, links: listFeastLinks.checked }), fmt, LIST_LINKS));
      }
    }
    if (files.length === 1) saveBlob(files[0].blob, files[0].name);
    else saveBlob(await makeZip(files), key + '_' + (from === to ? yearLabel(from) : yearLabel(from) + '_to_' + yearLabel(to)) + '_files.zip');
    filesStatus.textContent = (files.length === 1 ? 'Saved ' + files[0].name : 'Saved ' + files.length + ' files in a .zip')
      + (artBox.value === 'local' && !artData ? '. Your own picture could not be read from here and is left out.' : '.');
  } catch (e) {
    filesStatus.textContent = 'Could not make the files: ' + (e && e.message || e);
  } finally {
    filesMake.disabled = false;
  }
});
resetBtn.addEventListener('click', resetSettings);

// A link in the address wins; then --year; otherwise the year holding today.
const today = isoToday();
const opened = readLink(location.hash);
if (!applyLink(opened)) {
  const opening = DATA.openOn == null ? adventYearFor(today) : DATA.openOn;
  drawYear(opening, opening === adventYearFor(today) ? today : null);
  applyZoom(opened);
}

// Look for a picture beside the page; when there is one, offer it and, unless a
// link chose another, show it.
// Only when the page was made to (--local-art): each name tried and missing is
// a "file not found" in the browser's console.
if (DATA.localArt) findLocalArt(name => {
  if (!name || isFixed('artwork')) return;
  localArt = name;
  const keep = artBox.value;
  buildArtMenu();
  const linked = opened && opened.art != null && opened.art !== 'local';
  artBox.value = linked ? keep : 'local';
  if (artBox.value !== keep || !linked) drawYear(parseInt(yearBox.value, 10), chosen);
  markChanged();
  syncLink();
});

function settleOwnership() {
  owned = ownsPage();
  document.documentElement.classList.toggle('cy-page', owned);
  embedBtn.hidden = !owned;
  if (owned) {
    document.title = pageTitle;
    syncLink();
  }
  restoring = false;
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', settleOwnership);
} else {
  settleOwnership();
}
// ---------------------------------------------------------------------------
// Make a page: a page like this one, written in the browser as
// church_year.py writes it.  The window holds every one of the script's
// options (the churches one by one); pageOptions() reads them as the script's
// arguments, pageCommand() writes them as its command line, and buildPage()
// is the script's main() over this page's own tables (PRISTINE).
// ---------------------------------------------------------------------------

const pageDialog = $('pageDialog');
const pageTree = $('pageTree'), pageCount = $('pageCount'), pageChurch = $('pageChurch'), pageSubs = $('pageSubs');
const pageYear = $('pageYear'), pageYearNum = $('pageYearNum'), pageZoom = $('pageZoom');
const pageFeasts = $('pageFeasts'), pageLatin = $('pageLatin'), pageMid = $('pageMid');
const pageReadingBoxes = Array.from($('pageReadings').querySelectorAll('input'));
let pageKinds = null;
/** The kinds of set the churches on this page have (worked out when Make a page first opens). */
function pageKindsOffered() {
  if (!pageKinds) pageKinds = new Set([].concat(...DATA.traditions.map(t => readingKindsOf(t.key))));
  return pageKinds;
}
const pageLayout = $('pageLayout');
/** A readings-layout setting as the Make a page menu keeps it (blank: tabs,columns). */
const layoutText = s => String(s || '').toLowerCase().split(/[\s,]+/).filter(Boolean).join(',') || 'tabs,columns';
const pageBible = $('pageBible'), pageSite = $('pageSite'), pageW2w = $('pageW2w'), pageRings = $('pageRings');
const pageHymns = $('pageHymns'), pageYearLine = $('pageYearLine'), pageHymnal = $('pageHymnal');
/** Make a page's Hymnal menu: each hymnal of the churches here that have several, newest first. */
function pageHymnalFill() {
  const codes = [];
  pageHymnal.replaceChildren(new Option("Each church's first", ''));
  for (const t of DATA.traditions) {
    const list = hymnalsOf(t.key);
    if (list.length < 2) continue;
    for (const h of list) if (codes.indexOf(h.code) < 0) { codes.push(h.code); pageHymnal.append(new Option(h.name || h.code, h.code)); }
  }
}
const pageColors = $('pageColors'), pageArtwork = $('pageArtwork'), pageArtFile = $('pageArtFile');
const pageArtKeep = $('pageArtKeep'), pageArtNone = $('pageArtNone'), pageOwnArts = $('pageOwnArts');
const pageCal = $('pageCal'), pageEaster = $('pageEaster'), pageArt = $('pageArt'), pageReds = $('pageReds');
const pageDownload = $('pageDownload'), pageMakePage = $('pageMakePage'), pageEdit = $('pageEdit'), pageLinks = $('pageLinks');
const pageLocalArt = $('pageLocalArt'), pageArrows = $('pageArrows');
/** What a page without Bible links leaves out of the window: the Bible, Open in and the Bible menu. */
function pageLinksShow() {
  const sets = pageKindsOffered().size > 0;
  const bible = sets && (pageLinks.value === 'all' || pageLinks.value === 'bible');
  for (const el of [pageBible, pageSite, pageBibles]) el.closest('label').hidden = !bible;
  pageBibleList.hidden = !bible || pageBibles.value !== 'some';
  for (const el of [pageLayout, pageW2w]) el.closest('label').hidden = !sets;
  pageHymns.closest('label').hidden = !sets || !DATA.traditions.some(t => hymnalOf(t.key));
  pageHymnal.closest('label').hidden = pageHymns.closest('label').hidden || pageHymns.value === 'none' || pageHymnal.options.length < 2;
}

/**
 * The versions the Bible menu chosen offers (church_year.py:
 * bible_allowed): every one, those ticked and the languages ticked, or none
 * (each church's own).  The version the page opens in is one of them, so
 * the Bible list shows only those; one no longer offered goes back to each
 * church's own, and the note says so.
 */
function pageBibleFit() {
  const menu = pageBibles.value;
  const ticked = new Set(Array.from(pageBibleList.querySelectorAll('input[data-lang]')).filter(b => b.checked).map(b => b.value));
  const ok = code => menu === 'all' || (menu === 'some' && ticked.has(code));
  for (const g of pageBible.querySelectorAll('optgroup')) {
    let any = false;
    for (const o of g.querySelectorAll('option')) { o.hidden = o.disabled = !ok(o.value); any = any || !o.hidden; }
    g.hidden = !any;
  }
  if (pageBible.value && !ok(pageBible.value)) { const was = pageBible.value; pageBible.value = ''; return was; }
  return '';
}
pageLinks.addEventListener('change', () => {
  // No links at all: the songs mark is a link too.
  if (pageLinks.value === 'none' && pageW2w.value !== 'none') pageW2w.value = 'none';
  if (pageLinks.value === 'none' && pageHymns.value !== 'none') pageHymns.value = 'none';
  pageLinksShow(); pageCommandShow();
});
// A page made without them (--no-download, --no-make-page) does not offer them.
$('filesBtn').hidden = !!DATA.noDownload;
$('pageBtn').hidden = !!DATA.noMakePage;
const pageBibles = $('pageBibles'), pageBibleList = $('pageBibleList');
const pageFooter = $('pageFooter'), pageFeedback = $('pageFeedback'), pageHelp = $('pageHelp'), pageFragment = $('pageFragment');
const pageCompress = $('pageCompress');
const pageName = $('pageName'), pageCmd = $('pageCmd'), pageStatus = $('pageStatus');
const DATA_HEAD = '<script>window.CHURCH_YEAR_DATA = ';
// The pictures of your own (--own-art), in the order added: { name, data (the file's bytes; null for one
// this page already carries, or one a command named but could not carry), fields, churches (a Set) }.
let ownArts = [];
// The churches' own pictures left out of the page (--drop-art).
let artDropped = new Set();
const ownKey = name => 'file:' + String(name).split(/[\\/]/).pop().toLowerCase();
const OWN_FIELDS = ['credit', 'author', 'license', 'licenseUrl', 'source', 'scale', 'attribution'];
const OWN_SPEC = { credit: 'credit', author: 'author', license: 'license', licenseUrl: 'license-url',
                   source: 'source', scale: 'scale', attribution: 'attribution' };

/** The tables this page came with, before anything on it changed. */
function pristineData() {
  if (PRISTINE_TEXT) return JSON.parse(PRISTINE_TEXT);
  const i = PRISTINE.app.indexOf(DATA_HEAD) + DATA_HEAD.length;
  const j = PRISTINE.app.indexOf(';<\/script>', i);
  return JSON.parse(PRISTINE.app.slice(i, j));
}
const RAW = () => DATA.configRaw || {};
const rawText = k => String(RAW()[k] == null ? '' : RAW()[k]).trim();
const words = s => String(s || '').replace(/,/g, ' ').split(/\s+/).filter(Boolean);
const ALL_CHURCHES = DATA.traditions.filter(t => t.tradition);

// ---- The churches, one box each, under their tradition and church ----------

function buildChurchTree() {
  const tree = new Map();
  for (const t of ALL_CHURCHES) {
    if (!tree.has(t.tradition)) tree.set(t.tradition, new Map());
    const churches = tree.get(t.tradition);
    if (!churches.has(t.church)) churches.set(t.church, []);
    churches.get(t.church).push(t);
  }
  const box = (cls, label, title) => {
    const l = document.createElement('label'); l.className = 'check ' + cls;
    const b = document.createElement('input'); b.type = 'checkbox';
    l.append(b, ' ' + label); if (title) l.title = title; return [l, b];
  };
  const out = [];
  for (const trad of [...tree.keys()].sort(byLabel)) {
    const d = document.createElement('details'); d.className = 'trad';
    const s = document.createElement('summary');
    // The summary opens and closes (its +, or the name); only the box ticks.
    const tw = document.createElement('span'); tw.className = 'twisty'; tw.setAttribute('aria-hidden', 'true');
    const tb = document.createElement('input'); tb.type = 'checkbox'; tb.dataset.group = 'trad';
    tb.setAttribute('aria-label', 'Every ' + trad + ' church');
    const name = document.createElement('span'); name.className = 'name'; name.textContent = trad;
    const n = document.createElement('span'); n.className = 'n';
    s.title = 'Show or hide the ' + trad + ' churches';
    s.append(tw, tb, name, n); d.append(s);
    const churches = tree.get(trad);
    for (const church of [...churches.keys()].sort(byLabel)) {
      const list = churches.get(church);
      if (list.length === 1) {
        const [l, b] = box('leaf', list[0].label, list[0].key); b.value = list[0].key; d.append(l);
        continue;
      }
      const [cl, cb] = box('church', church); cb.dataset.group = 'church'; d.append(cl);
      const inner = document.createElement('div'); inner.className = 'leaves';
      for (const t of list) {
        const name = [t.series, t.book].filter(Boolean).join(', ') || t.label;
        const [l, b] = box('leaf', name, t.key); b.value = t.key; inner.append(l);
      }
      d.append(inner);
    }
    out.push(d);
  }
  pageTree.replaceChildren(...out);
}
const leafBoxes = () => Array.from(pageTree.querySelectorAll('label.leaf input'));
const pageKeys = () => leafBoxes().filter(b => b.checked).map(b => b.value);

/** Tick these churches, and show each group's boxes as all, some or none of its own. */
function setChurches(keys) {
  const on = new Set(keys);
  for (const b of leafBoxes()) b.checked = on.has(b.value);
  churchesChanged();
}
function groupLeaves(groupBox) {
  if (groupBox.dataset.group === 'trad') return Array.from(groupBox.closest('details').querySelectorAll('label.leaf input'));
  return Array.from(groupBox.closest('label').nextElementSibling.querySelectorAll('input'));
}
function churchesChanged() {
  for (const g of pageTree.querySelectorAll('input[data-group]')) {
    const leaves = groupLeaves(g), n = leaves.filter(b => b.checked).length;
    g.checked = n === leaves.length; g.indeterminate = n > 0 && n < leaves.length;
  }
  for (const d of pageTree.querySelectorAll('details.trad')) {
    const leaves = Array.from(d.querySelectorAll('label.leaf input')), n = leaves.filter(b => b.checked).length;
    d.querySelector('summary .n').textContent = n + ' of ' + leaves.length;
  }
  const keys = pageKeys();
  pageCount.textContent = '(' + keys.length + ' of ' + ALL_CHURCHES.length + ')';
  const was = pageChurch.value;
  pageChurch.replaceChildren(...ALL_CHURCHES.filter(t => keys.indexOf(t.key) >= 0)
    .sort((a, b) => byLabel(a.label, b.label)).map(t => new Option(t.label, t.key)));
  pick(pageChurch, was);
  if (pageChurch.value !== was) pick(pageChurch, currentTradition());   // else the church on screen, if ticked
  if (pageChurch.value !== was) churchMenus();
  artMenu();
  pageColorsShow();
  pageCommandShow();
}
pageTree.addEventListener('change', e => {
  const b = e.target;
  if (b.dataset.group) for (const l of groupLeaves(b)) l.checked = b.checked;
  churchesChanged();
});
pageTree.addEventListener('click', e => {        // the box in a summary ticks; the rest of it opens
  if (e.target.tagName === 'INPUT' && e.target.closest('summary')) {
    const b = e.target, want = b.checked;
    e.preventDefault();                            // which would also open or close the tradition
    setTimeout(() => { b.checked = want; b.indeterminate = false; b.dispatchEvent(new Event('change', { bubbles: true })); });
  }
});
$('pageQuick').addEventListener('click', e => {
  const how = e.target.dataset && e.target.dataset.pick;
  if (!how) return;
  const here = traditionOf(currentTradition());
  setChurches(how === 'none' ? [] : ALL_CHURCHES.filter(t => how === 'all'
    || (how === 'tradition' && t.tradition === here.tradition)
    || (how === 'church' && t.church === here.church)
    || (how === 'one' && t.key === here.key)).map(t => t.key));
});

// ---- What it opens with ------------------------------------------------------

/** The calendar menus for the church it opens on, one per menu as on the page. */
function churchMenus(keep) {
  const chosen = keep || pageSubKeys();
  const t = traditionOf(pageChurch.value);
  const folder = DATA.folders[t.folder] || { subcalendars: [] };
  const menus = [];
  for (const s of folder.subcalendars) {
    let m = menus.find(x => x.menu === s.menu);
    if (!m) { m = { menu: s.menu, label: s.menuLabel || s.menu, items: [] }; menus.push(m); }
    m.items.push(s);
  }
  pageSubs.replaceChildren(...menus.map(m => {
    const row = document.createElement('label'); row.title = '--subcalendar';
    const select = document.createElement('select');
    select.appendChild(new Option('None', ''));
    for (const s of m.items.slice().sort((a, b) => byLabel(a.label, b.label))) select.appendChild(new Option(s.label, s.key));
    for (const k of chosen) pick(select, k);
    row.append(m.label + ' ', select);
    return row;
  }));
}
const pageSubKeys = () => Array.from(pageSubs.querySelectorAll('select')).map(s => s.value).filter(Boolean);
pageChurch.addEventListener('change', () => { churchMenus(); pageCommandShow(); });

function buildOpenMenus() {
  const langName = l => LANGUAGE_NAMES[l] || l;
  pageBible.replaceChildren(new Option("Each church's own", ''));
  const list = [];
  for (const l of [...new Set(BIBLE_VERSIONS.map(v => v[2]))].sort((a, b) => byLabel(langName(a), langName(b)))) {
    const g = document.createElement('optgroup'); g.label = langName(l);
    const vs = BIBLE_VERSIONS.filter(v => v[2] === l).sort((a, b) => byLabel(a[1], b[1]));
    g.append(...vs.map(v => new Option(v[1] + ' (' + v[0] + ')', v[0])));
    pageBible.append(g);
    // The Bible menu's own list: a language, then its versions.
    const lang = document.createElement('label'); lang.className = 'check lang';
    const lb = document.createElement('input'); lb.type = 'checkbox'; lb.value = l === 'en' ? 'english' : l;
    lang.append(lb, ' ' + langName(l) + ' (every version)');
    const inner = document.createElement('div'); inner.className = 'leaves';
    for (const v of vs) {
      const r = document.createElement('label'); r.className = 'check';
      const b = document.createElement('input'); b.type = 'checkbox'; b.value = v[0]; b.dataset.lang = l;
      r.append(b, ' ' + v[1] + ' (' + v[0] + ')'); inner.append(r);
    }
    list.push(lang, inner);
  }
  pageBibleList.replaceChildren(...list);
  const rings = (DATA.rings || []).filter(r => !FIXED[r.kind]).sort((a, b) => (b.rOuter - a.rOuter) || (b.rInner - a.rInner));
  pageRings.append(...rings.map(r => {
    const l = document.createElement('label'); l.className = 'check';
    const b = document.createElement('input'); b.type = 'checkbox'; b.value = r.key;
    l.append(b, ' ' + ringName(r.key)); return l;
  }));
}
const ringBoxes = () => Array.from(pageRings.querySelectorAll('input'));
pageHymns.addEventListener('change', () => pageLinksShow());
// The day's own hymn marks follow Hymn search and the Hymnal menu too.
hymnsBox.addEventListener('change', () => { if (chosen) choose(chosen, false); });
hymnalBox.addEventListener('change', () => { if (chosen) choose(chosen, false); });
pageBibles.addEventListener('change', () => { pageBibleList.hidden = pageBibles.value !== 'some'; pageBibleFit(); pageCommandShow(); });
pageBibleList.addEventListener('change', e => {
  if (e.target.parentElement.classList.contains('lang')) {
    for (const b of e.target.parentElement.nextElementSibling.querySelectorAll('input')) { b.checked = e.target.checked; b.disabled = e.target.checked; }
  }
  pageBibleFit();
  pageCommandShow();
});
/** A church's own picture, not one of yours (a page made already keeps it as churchArt). */
function churchArt(k) {
  const p = DATA.profiles[k] || {};
  return p.churchArt !== undefined ? p.churchArt : p.art;
}
/** The churches' own pictures (not one of yours) of the churches ticked. */
/** The seasons' pictures these churches would show (season_art.csv rows for every church, or for one of them). */
function seasonArts(keys) {
  const out = [];
  for (const r of DATA.seasonArt || []) {
    if (r.art && DATA.artwork[r.art] && (!r.church || keys.indexOf(r.church) >= 0) && out.indexOf(r.art) < 0) out.push(r.art);
  }
  return out;
}

function builtinArts(keys) {
  const out = [];
  for (const k of keys) {
    const a = churchArt(k);
    if (a && DATA.artwork[a] && !DATA.artwork[a].own && out.indexOf(a) < 0) out.push(a);
  }
  for (const a of seasonArts(keys)) if (!DATA.artwork[a].own && out.indexOf(a) < 0) out.push(a);
  for (const a of artDropped) if (out.indexOf(a) < 0 && DATA.artwork[a]) out.push(a);
  return out.sort((x, y) => artOrder({ key: x, label: DATA.artwork[x].label || x }, { key: y, label: DATA.artwork[y].label || y }));
}
/** The church each of your pictures is the own picture of. */
function ownChurches() {
  const m = {};
  for (const a of ownArts) for (const c of a.churches) m[c] = ownKey(a.name);
  return m;
}
/**
 * The Artwork menu (the picture the page opens on), the pictures kept, the
 * churches a dropped picture leaves with none, and your own pictures.
 */
function artMenu() {
  const was = pageArtwork.value;
  const keys = pageKeys();
  const builtin = builtinArts(keys);
  const items = builtin.filter(k => !artDropped.has(k)).map(k => ({ key: k, label: DATA.artwork[k].label || k }))
    .concat(ownArts.map(a => ({ key: ownKey(a.name), label: a.name.split(/[\\/]/).pop() })))
    .sort(artOrder);
  const seasonal = seasonArts(keys).some(k => !artDropped.has(k));
  pageArtwork.replaceChildren(new Option("The tradition's own", 'auto'),
    ...(seasonal ? [new Option('By season', 'season')] : []), new Option('None', 'none'),
    ...items.map(i => new Option(i.label, i.key)));
  pick(pageArtwork, was);
  pageArtKeep.replaceChildren('Pictures kept', ...builtin.map(k => {
    const l = document.createElement('label');
    l.className = 'check';
    const b = document.createElement('input');
    b.type = 'checkbox'; b.value = k; b.checked = !artDropped.has(k);
    b.addEventListener('change', () => {
      if (b.checked) artDropped.delete(k); else artDropped.add(k);
      artMenu(); pageCommandShow();
    });
    l.append(b, ' ' + (DATA.artwork[k].label || k));
    return l;
  }));
  pageArtKeep.hidden = !builtin.length;
  const mine = ownChurches();
  const none = keys.filter(k => !mine[k] && (artDropped.has(churchArt(k)) || churchArt(k) === 'none'));
  pageArtNone.hidden = !none.length;
  pageArtNone.textContent = none.length ? 'Left with no picture of their own (add one for them below): '
    + none.map(k => traditionOf(k).label).join('; ') + '.' : '';
  artCardsShow();
}
/** A picture of your own as the page will carry it: from its file, else as this page already carries it. */
function ownEntry(a) {
  if (a.data) return ownArtwork(Object.assign({ name: a.name, data: a.data }, a.fields))[1];
  const was = DATA.artwork[ownKey(a.name)];
  if (!was) return null;
  return ownFieldsOn(Object.assign({}, was), a.name, a.fields);
}
/** Draw a picture in the middle of a small wheel: as the page draws it, cut to the circle, the next ring around it. */
function artPreview(svg, entry) {
  const ns = 'http://www.w3.org/2000/svg';
  const R = 44, c = 60;
  svg.replaceChildren();
  const disc = document.createElementNS(ns, 'circle');
  disc.setAttribute('cx', c); disc.setAttribute('cy', c); disc.setAttribute('r', R); disc.setAttribute('fill', '#fff');
  svg.append(disc);
  if (entry) {
    try {
      const id = 'cy-art-preview-' + Math.random().toString(36).slice(2);
      const scale = entry.scale ? parseFloat(entry.scale) : 1;
      const k = 2 * R * scale / Math.max(entry.w, entry.h);
      const x = c - entry.w * k / 2 - (entry.x || 0) * k, y = c - entry.h * k / 2 - (entry.y || 0) * k;
      const g = document.createElementNS(ns, 'g');
      g.setAttribute('transform', 'translate(' + x + ',' + y + ') scale(' + k + ')');
      g.append(parseChildren(entry.body.replace(/cy-own-art-clip/g, id + '-own')));
      const clip = document.createElementNS(ns, 'clipPath');
      clip.id = id;
      const cc = document.createElementNS(ns, 'circle');
      cc.setAttribute('cx', c); cc.setAttribute('cy', c); cc.setAttribute('r', R);
      clip.append(cc);
      const wrap = document.createElementNS(ns, 'g');
      wrap.setAttribute('clip-path', 'url(#' + id + ')');
      wrap.append(g);
      svg.append(clip, wrap);
    } catch (err) { /* left blank: the picture is reported when the page is made */ }
  }
  const ring = document.createElementNS(ns, 'circle');
  ring.setAttribute('cx', c); ring.setAttribute('cy', c); ring.setAttribute('r', R + 8);
  ring.setAttribute('fill', 'none'); ring.setAttribute('stroke', '#c9c9c9'); ring.setAttribute('stroke-width', 16);
  ring.setAttribute('opacity', '.85');
  svg.append(ring);
}
/** One card for each picture of your own: its preview, credit, the churches it is the own picture of, and Remove. */
function artCardsShow() {
  const keys = pageKeys();
  pageOwnArts.replaceChildren(...ownArts.map(a => {
    const card = document.createElement('div');
    card.className = 'row sub ownart';
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('class', 'artpreview'); svg.setAttribute('viewBox', '0 0 120 120');
    svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', 'How ' + a.name + ' sits in the middle of the wheel');
    const redraw = () => { let e = null; try { e = ownEntry(a); } catch (err) { /* reported when made */ } artPreview(svg, e); };
    redraw();
    const fields = document.createElement('div');
    fields.className = 'fields';
    const head = document.createElement('div');
    head.className = 'artname';
    head.textContent = a.name.split(/[\\/]/).pop();
    if (!a.data && !DATA.artwork[ownKey(a.name)]) {
      const warn = document.createElement('span');
      warn.className = 'warn';
      warn.textContent = ' — choose this file again with Add a picture (a command names it but cannot carry it)';
      head.append(warn);
    }
    const remove = document.createElement('button');
    remove.type = 'button'; remove.textContent = 'Remove'; remove.className = 'remove';
    remove.addEventListener('click', () => {
      ownArts = ownArts.filter(x => x !== a);
      if (pageArtwork.value === ownKey(a.name)) pageArtwork.value = 'auto';
      artMenu(); pageCommandShow();
    });
    head.append(' ', remove);
    fields.append(head);
    const field = (label, k, type, title, placeholder) => {
      const l = document.createElement('label');
      l.title = title;
      const i = document.createElement('input');
      i.type = type; i.value = a.fields[k] || '';
      if (placeholder) i.placeholder = placeholder;
      if (type === 'number') { i.min = '0.05'; i.step = '0.05'; }
      const set = () => { a.fields[k] = i.value.trim(); if (k === 'scale') redraw(); pageCommandShow(); };
      i.addEventListener('input', set); i.addEventListener('change', set);
      l.append(label + ' ', i);
      return l;
    };
    fields.append(field('Size', 'scale', 'number', 'scale=: 1 fills the circle', '1'),
      field('Credit', 'credit', 'text', "credit=: the picture's title or a line of credit", 'Title, or Drawn by ...'),
      field('Artist or owner', 'author', 'text', 'author='),
      field('License or copyright', 'license', 'text', 'license=: a license (CC BY 4.0) or a copyright notice', 'CC BY 4.0, or © 2026 ...'),
      field('License link', 'licenseUrl', 'url', 'license-url=', 'https://'),
      field('Source link', 'source', 'url', 'source=', 'https://'));
    const req = document.createElement('label');
    req.className = 'check';
    req.title = 'attribution=: required keeps the credit under the wheel (or an i button when the footer is off); optional leaves it to the footer';
    const rb = document.createElement('input');
    rb.type = 'checkbox'; rb.checked = String(a.fields.attribution || 'required').toLowerCase() !== 'optional';
    rb.addEventListener('change', () => { a.fields.attribution = rb.checked ? '' : 'optional'; pageCommandShow(); });
    req.append(rb, ' The credit must be shown');
    fields.append(req);
    // The churches it is the own picture of ("The tradition's own" shows it for them).
    const used = document.createElement('details');
    used.className = 'tree usedby';
    const sum = document.createElement('summary');
    const n = keys.filter(k => a.churches.has(k)).length;
    sum.textContent = 'The own picture of: ' + (n ? n + (n === 1 ? ' church' : ' churches') : 'no church (the Artwork menu only)');
    used.append(sum);
    if (a.open) used.open = true;
    used.addEventListener('toggle', () => { a.open = used.open; });
    const groups = {};
    for (const k of keys) { const t = traditionOf(k); (groups[t.tradition] = groups[t.tradition] || []).push(t); }
    for (const name of Object.keys(groups).sort(byLabel)) {
      const g = document.createElement('div');
      g.className = 'tgroup';
      const tl = document.createElement('label');
      tl.className = 'check tname';
      const tb = document.createElement('input');
      tb.type = 'checkbox'; tb.value = name;
      const inG = groups[name].filter(t => a.churches.has(t.key)).length;
      tb.checked = inG === groups[name].length; tb.indeterminate = inG > 0 && !tb.checked;
      tb.addEventListener('change', () => { for (const t of groups[name]) setOwnChurch(a, t.key, tb.checked); artMenu(); pageCommandShow(); });
      tl.append(tb, ' ' + name);
      g.append(tl);
      for (const t of groups[name].sort((x, y) => byLabel(x.label, y.label))) {
        const cl = document.createElement('label');
        cl.className = 'check';
        const cb = document.createElement('input');
        cb.type = 'checkbox'; cb.value = t.key; cb.checked = a.churches.has(t.key);
        cb.addEventListener('change', () => { setOwnChurch(a, t.key, cb.checked); artMenu(); pageCommandShow(); });
        cl.append(cb, ' ' + t.label);
        g.append(cl);
      }
      used.append(g);
    }
    fields.append(used);
    card.append(svg, fields);
    return card;
  }));
}
/** Make a picture of yours the own picture of a church, or not; a church has only one. */
function setOwnChurch(a, key, on) {
  for (const x of ownArts) x.churches.delete(key);
  if (on) a.churches.add(key);
}
pageArtwork.addEventListener('change', () => pageCommandShow());
pageArtFile.addEventListener('change', async () => {
  const f = pageArtFile.files && pageArtFile.files[0];
  if (!f) return;
  const data = new Uint8Array(await f.arrayBuffer());
  const was = ownArts.find(x => ownKey(x.name) === ownKey(f.name));
  if (was) was.data = data;
  else ownArts.push({ name: f.name, data: data, fields: {}, churches: new Set(), open: true });
  pageArtFile.value = '';
  artMenu();
  // A picture added opens the page, as the only choice the reader is sure to see (one chosen again stays as it was).
  if (!was) pick(pageArtwork, ownKey(f.name));
  pageCommandShow();
});
/** The pictures of your own this page carries already, as Make a page starts from them. */
function ownArtsOfPage() {
  return (DATA.artworkOrder || []).filter(k => DATA.artwork[k] && DATA.artwork[k].own).map(k => {
    const e = DATA.artwork[k];
    return { name: e.label, data: null, open: false,
             fields: { credit: e.title || '', author: e.author || '', license: e.license || '', licenseUrl: e.licenseUrl || '',
                       source: e.sourceUrl || '', scale: e.scale || '', attribution: e.attribution === 'required' || !(e.title || e.author || e.license) ? '' : 'optional' },
             churches: new Set(Object.keys(DATA.profiles).filter(c => DATA.profiles[c].art === k)) };
  });
}

// ---- Colors: for every church, tradition by tradition, or church by church --

const pageColorRows = $('pageColorRows'), pageColorsN = $('pageColorsN'), pageColorMode = $('pageColorMode');
const pageColorOpen = new Set();                  // the traditions and churches opened in the list
const isDayKey = k => k !== 'empty' && !/^(ring|text)\./.test(k);
const scopeDepth = k => (isDayKey(k) ? k.split(':').length - 1 : -1);   // 0 every church, 1 tradition, 2 church
/** The text's changes: { PURPLE: '#7a1f7a', 'lutheran:WHITE': .., 'lutheran:wels-one-year:RED': .., 'ring.halves': .., empty: .. }. */
function pageColorMap() {
  const out = {};
  for (const item of pageColors.value.split(',')) {
    const t = item.trim(), i = t.lastIndexOf('-');
    if (i <= 0) continue;
    const v = hex6('#' + t.slice(i + 1));
    if (!v) continue;
    let k = t.slice(0, i);
    if (isDayKey(k)) {
      const p = k.split(':');
      k = p.length === 3 ? tradSlug(p[0]) + ':' + p[1].trim().toLowerCase() + ':' + p[2].toUpperCase()
        : p.length === 2 ? tradSlug(p[0]) + ':' + p[1].toUpperCase() : k.toUpperCase();
    }
    out[k] = v;
  }
  return out;
}
/** Write the changes back as colorsParam does: every church's, each tradition's, each church's, rings, words, outside. */
function setPageColorMap(m) {
  const keys = Object.keys(m);
  const cmp = (a, b) => { const x = a.split(':'), y = b.split(':');
    for (let i = 0; i < x.length; i++) if (x[i] !== y[i]) return x[i] < y[i] ? -1 : 1; return 0; };
  const depth = d => keys.filter(k => scopeDepth(k) === d).sort(cmp);
  const part = pre => keys.filter(k => k.indexOf(pre) === 0).sort();
  pageColors.value = depth(0).concat(depth(1), depth(2), part('ring.'), part('text.'), keys.filter(k => k === 'empty'))
    .map(k => k + '-' + m[k].slice(1)).join(',');
}
function pageColorsShow() {
  const m = pageColorMap(), keys = new Set(pageKeys()), mode = pageColorMode.value;
  // name -> fill -> [church labels]: for all the churches ticked, each tradition, each church
  const all = {}, byTrad = {}, byChurch = {}, page = {};
  const ticked = ALL_CHURCHES.filter(t => keys.has(t.key) && DATA.profiles[t.key]);
  for (const t of ALL_CHURCHES) {                  // every shade on this page, to choose from
    const colors = (DATA.profiles[t.key] || {}).colors || {};
    for (const name of Object.keys(colors)) {
      const fill = hex6(colors[name].fill);
      if (fill) ((page[name] = page[name] || {})[fill] = page[name][fill] || []).push(t.label);
    }
  }
  for (const t of ticked) {
    const colors = DATA.profiles[t.key].colors || {};
    const tr = byTrad[t.tradition] = byTrad[t.tradition] || {}, ch = byChurch[t.key] = {};
    for (const name of Object.keys(colors)) {
      const fill = hex6(colors[name].fill);
      if (!fill) continue;
      for (const book of [all, tr, ch]) ((book[name] = book[name] || {})[fill] = book[name][fill] || []).push(t.label);
    }
  }
  const changed = () => { setPageColorMap(m); pageColorsShow(); pageCommandShow(); };
  const swatch = (fill, who, key, mine) => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'sw' + (mine ? '' : ' other');
    b.style.background = fill; b.title = fill + ': ' + who.join(', ') + ' (click to use it)';
    b.setAttribute('aria-label', fill + ', ' + who.join(', '));
    b.addEventListener('click', () => { m[key] = fill; changed(); });
    return b;
  };
  /** A row: a picker, the name, its own shades and the others' to choose from, and × to put it back. */
  const row = (key, label, value, own, others, note) => {
    const r = document.createElement('div'); r.className = 'crow' + (m[key] ? ' changed' : '');
    const box = document.createElement('input'); box.type = 'color'; box.value = value || '#ffffff';
    box.setAttribute('aria-label', label);
    box.addEventListener('change', () => { m[key] = box.value; changed(); });
    const name = document.createElement('span'); name.className = 'name'; name.textContent = label;
    if (note) { const n = document.createElement('small'); n.textContent = ' ' + note; name.append(n); }
    const opts = document.createElement('span'); opts.className = 'own';
    for (const [fill, who] of own) opts.append(swatch(fill, who, key, true));
    if (others.length) { const sep = document.createElement('span'); sep.className = 'sep'; opts.append(sep); }
    for (const [fill, who] of others) opts.append(swatch(fill, who, key, false));
    const x = document.createElement('button'); x.type = 'button'; x.className = 'undo'; x.textContent = '×';
    x.title = 'Put ' + label.toLowerCase() + ' back'; x.hidden = !m[key];
    x.addEventListener('click', () => { delete m[key]; changed(); });
    r.append(box, name, opts, x); return r;
  };
  const head = text => { const h = document.createElement('div'); h.className = 'crowhead'; h.textContent = text; return h; };
  const byName = o => Object.keys(o).sort((a, b) => byLabel(colorName(a), colorName(b)));
  /** A section to open: + and a name, and how many of its colors are changed. */
  const section = (id, label, prefix, cls) => {
    const d = document.createElement('details'); d.className = 'ctrad' + (cls ? ' ' + cls : ''); d.open = pageColorOpen.has(id);
    d.addEventListener('toggle', () => { if (d.open) pageColorOpen.add(id); else pageColorOpen.delete(id); });
    const s = document.createElement('summary');
    const n = Object.keys(m).filter(k => k.indexOf(prefix) === 0 && (cls || scopeDepth(k) === 1)).length;
    const tw = document.createElement('span'); tw.className = 'twisty'; tw.setAttribute('aria-hidden', 'true');
    const nm = document.createElement('span'); nm.className = 'name'; nm.textContent = label;
    const cnt = document.createElement('span'); cnt.className = 'n'; cnt.textContent = n ? n + ' changed' : '';
    s.append(tw, nm, cnt); d.append(s); return d;
  };
  /** The other shades of a color: whose they are, leaving out the ones already shown as `own`. */
  const othersOf = (c, own, book) => Object.entries(page[c] || {}).filter(([f]) => !(f in book[c]));
  const rows = [head(mode === 'all' ? 'Every church' : 'Every church (unless changed below)')];
  for (const n of byName(all)) {
    const fills = Object.entries(all[n]);
    rows.push(row(n, colorName(n), m[n] || fills[0][0], fills, othersOf(n, fills, all)));
  }
  if (mode !== 'all') {
    for (const trad of Object.keys(byTrad).sort(byLabel)) {
      const slug = tradSlug(trad), mine = byTrad[trad];
      const d = section(slug, trad, slug + ':');
      if (mode === 'church') d.append(head('Every ' + trad + ' church'));
      for (const c of byName(mine)) {
        const key = slug + ':' + c, own = Object.entries(mine[c]);
        d.append(row(key, colorName(c), m[key] || m[c] || own[0][0], own, othersOf(c, own, mine),
          !m[key] && m[c] ? '(every church’s change)' : ''));
      }
      if (mode === 'church') {
        for (const t of ticked.filter(x => x.tradition === trad).sort((a, b) => byLabel(a.label, b.label))) {
          const cd = section(slug + ':' + t.key, t.label, slug + ':' + t.key + ':', 'cchurch'), book = byChurch[t.key];
          for (const c of byName(book)) {
            const key = slug + ':' + t.key + ':' + c, own = Object.entries(book[c]);
            const inherited = m[slug + ':' + c] ? '(the ' + trad + ' change)' : m[c] ? '(every church’s change)' : '';
            cd.append(row(key, colorName(c), m[key] || m[slug + ':' + c] || m[c] || own[0][0], own,
              othersOf(c, own, book), !m[key] ? inherited : ''));
          }
          d.append(cd);
        }
      }
      rows.push(d);
    }
  }
  // Changes this way of listing does not show are kept, and said so.
  const hidden = Object.keys(m).filter(k => scopeDepth(k) > ({ all: 0, tradition: 1, church: 2 })[mode]).length;
  if (hidden) {
    const p = document.createElement('p'); p.className = 'text';
    p.textContent = hidden + (hidden === 1 ? ' change' : ' changes') + ' for single ' + (mode === 'all' ? 'traditions or churches' : 'churches')
      + ' still apply; change them ' + (mode === 'all' ? '“tradition by tradition” or “church by church”' : '“church by church”') + ' to see ' + (hidden === 1 ? 'it' : 'them') + '. ';
    const clear = document.createElement('button'); clear.type = 'button'; clear.textContent = 'Put them back';
    clear.addEventListener('click', () => { for (const k of Object.keys(m)) if (scopeDepth(k) > ({ all: 0, tradition: 1, church: 2 })[mode]) delete m[k]; changed(); });
    p.append(clear); rows.push(p);
  }
  rows.push(head('Rings and the rest'));
  const empty = hex6(DATA.settings.empty_cell_fill);
  if (empty) rows.push(row('empty', 'Outside the year', m.empty || empty, [[empty, ['every church']]], []));
  const rings = (DATA.rings || []).filter(r => hex6(r.fill)).sort((a, b) => (b.rOuter - a.rOuter) || (b.rInner - a.rInner));
  for (const r of rings) {
    rows.push(row('ring.' + r.key, ringName(r.key), m['ring.' + r.key] || hex6(r.fill), [[hex6(r.fill), ['as drawn']]], []));
    if (r.labelMode && r.labelMode !== 'none' && hex6(r.textColor)) {
      rows.push(row('text.' + r.key, ringName(r.key) + ' words', m['text.' + r.key] || hex6(r.textColor), [[hex6(r.textColor), ['as drawn']]], []));
    }
  }
  pageColorRows.replaceChildren(...rows);
  const total = Object.keys(m).length;
  pageColorsN.textContent = total ? total + ' changed' : 'as each church has them';
}
/** List the colors as finely as the changes already made are. */
function pageColorModeFit() {
  const depth = Math.max(0, ...Object.keys(pageColorMap()).map(scopeDepth));
  pageColorMode.value = ['all', 'tradition', 'church'][depth];
}
pageColorMode.addEventListener('change', () => pageColorsShow());
pageColors.addEventListener('input', () => pageColorsShow());

/** Set what it opens with: as on screen now, or as this page itself opens. */
function pageOpensAs(now) {
  const P = pristineData();
  const t = now ? currentTradition() : P.defaultTradition;
  if (pageKeys().indexOf(t) >= 0) pageChurch.value = t;
  churchMenus(now ? chosenSubs() : (P.defaultSubcalendars || []));
  const year = now ? drawnYear() : P.openOn;
  pageYear.checked = (now ? DATA.openOn : P.openOn) != null;
  pageYearNum.value = year != null && !isNaN(year) ? year : drawnYear();
  pageZoom.value = now ? +magnify.toFixed(2) : (P.openZoom || 1);
  pageFeasts.value = now ? feastBox.value : (P.settings.feast_detail || 'all');
  pageMid.value = now ? midValue() : (P.settings.mid_text || 'as-set');
  const latinSet = typeof P.latinDefault === 'boolean' ? (P.latinDefault ? 'on' : 'off') : '';
  if (!now) pageLatin.value = latinSet;
  else {
    const own = (() => { const keep = DATA.latinDefault; delete DATA.latinDefault;
      const v = latinDefault(currentTradition()); if (keep !== undefined) DATA.latinDefault = keep; return v; })();
    pageLatin.value = typeof DATA.latinDefault === 'boolean' && latinBox.checked === DATA.latinDefault
      ? (latinBox.checked ? 'on' : 'off') : latinBox.checked === own ? '' : (latinBox.checked ? 'on' : 'off');
  }
  const kinds = now ? readingsOn() : (Array.isArray(P.readingsDefault) ? P.readingsDefault : CY.READING_CATEGORIES);
  for (const b of pageReadingBoxes) b.checked = kinds.indexOf(b.value) >= 0;
  // Only the kinds of set some church on this page has.
  const offered = pageKindsOffered();
  for (const b of pageReadingBoxes) b.parentElement.hidden = !offered.has(b.value);
  $('pageReadings').hidden = !offered.size;
  if (now) {
    const own = (() => { const keep = DATA.bibleDefault; delete DATA.bibleDefault;
      const v = bibleDefault(currentTradition()); if (keep !== undefined) DATA.bibleDefault = keep; return v; })();
    pageBible.value = !hasReadings() || !bibleBox.value ? (DATA.bibleDefault || '')
      : DATA.bibleDefault && bibleBox.value === DATA.bibleDefault ? bibleBox.value
      : bibleBox.value === own ? '' : bibleBox.value;
    pageSite.value = siteBox.value === bibleSiteDefault() ? (DATA.bibleSite || '') : siteBox.value;
    pageW2w.value = w2wOff() ? 'none' : (w2wBox.checked ? 'on' : 'off');
    pageHymns.value = hymnaryOff() ? 'none' : (hymnsBox.checked ? 'on' : 'off');
    const first = (hymnalsOf(currentTradition())[0] || {}).code;
    pageHymnal.value = !hymnalRow.hidden && hymnalBox.value !== first ? hymnalBox.value : (DATA.hymnalDefault || '');
    if (pageHymnal.selectedIndex < 0) pageHymnal.value = '';
    pageYearLine.checked = yearLineBox.checked;
    const offered = layoutsOffered();
    pageLayout.value = offered.length > 1 ? [layoutNow()].concat(offered.filter(x => x !== layoutNow())).join(',') : offered[0];
  } else {
    pageLayout.value = Array.isArray(P.readingsLayout) && P.readingsLayout.length ? P.readingsLayout.join(',') : 'tabs,columns';
    pageBible.value = P.bibleDefault || '';
    pageSite.value = P.bibleSite || '';
    pageW2w.value = P.wordToWorship || 'on';
    pageHymns.value = P.hymnary || 'on';
    pageHymnal.value = P.hymnalDefault || '';
    if (pageHymnal.selectedIndex < 0) pageHymnal.value = '';
    pageYearLine.checked = CY.truthy(P.settings.year_line);
  }
  pageBibleFit();
  const hidden = now ? Object.keys(hiddenRings).filter(k => hiddenRings[k]) : (P.hiddenDefault || []);
  for (const b of ringBoxes()) b.checked = hidden.indexOf(b.value) < 0;
  // Unchanged from the page's own, its own text is kept as written.
  pageColors.value = !now || colorsParam() === colorsDefaultKey() ? (P.colorsDefault || '') : colorsParam();
  pageColorModeFit();
  pageColorsShow();
  // The pictures: this page's own pictures of yours, none dropped, and the one it opens on
  // (a picture beside the page, center.svg, cannot go into another: the tradition's own instead).
  ownArts = ownArtsOfPage();
  artDropped = new Set();
  artMenu();
  const art = now ? artBox.value : String(P.defaultArt || 'auto');
  pageArtwork.value = 'auto';
  if (art !== 'local') pick(pageArtwork, art);
  pageCommandShow();
}
$('pageNow').addEventListener('click', () => pageOpensAs(true));
$('pageOwn').addEventListener('click', () => pageOpensAs(false));

$('pageBtn').addEventListener('click', () => {
  if (!pageTree.childElementCount) buildChurchTree();
  $('pageChurchesBox').open = false;
  if (!pageBible.options.length) buildOpenMenus();
  pageHymnalFill();
  setChurches(ALL_CHURCHES.map(t => t.key));
  const bibles = (DATA.bibles || []).map(String);
  pageBibles.value = !bibles.length ? 'all' : bibles[0].toLowerCase() === 'own' ? 'own' : 'some';
  for (const b of pageBibleList.querySelectorAll('input')) {
    b.checked = bibles.some(x => x.toLowerCase() === b.value.toLowerCase()); b.disabled = false;
  }
  for (const b of pageBibleList.querySelectorAll('label.lang input')) {
    if (b.checked) for (const v of b.parentElement.nextElementSibling.querySelectorAll('input')) { v.checked = true; v.disabled = true; }
  }
  pageBibleList.hidden = pageBibles.value !== 'some';
  pageOpensAs(true);
  pageCal.checked = !isFixed('calendar');
  pageEaster.checked = !isFixed('easter');
  pageArt.checked = !isFixed('artwork');
  pageReds.checked = !isFixed('reds');
  pageDownload.checked = !DATA.noDownload;
  pageLinks.value = bibleLinks && feastLinks ? 'all' : bibleLinks ? 'bible' : feastLinks ? 'feasts' : 'none';
  pageMakePage.checked = !DATA.noMakePage;
  pageEdit.checked = !DATA.noEdit;
  pageLocalArt.checked = !!DATA.localArt;
  pageArrows.checked = !!DATA.arrowsNext;
  pageLinksShow();
  pageFooter.value = DATA.footer || 'full';
  pageFeedback.value = DATA.feedback || '';
  pageHelp.value = DATA.help || '';
  pageFragment.checked = false;
  // Packed as this page's tables are, unless changed.
  pageCompress.checked = PACKED;
  pageName.value = 'church_year.html';
  pageStatus.textContent = '';
  pageCommandShow();
  if (pageDialog.showModal) pageDialog.showModal(); else pageDialog.setAttribute('open', '');
  // Start at the top, not on the folded churches' line.
  $('pageHead').focus();
});
pageDialog.addEventListener('input', () => pageCommandShow());
pageDialog.addEventListener('change', () => pageCommandShow());

// ---- The window as the script's options, and as its command line -----------

/** The window's choices as church_year.py's arguments. */
function pageOptions() {
  const o = {};
  const keys = pageKeys();
  if (!keys.length) throw new Error('choose at least one church');
  o.churches = keys.length === ALL_CHURCHES.length ? null : keys;
  o.church = pageChurch.value;
  o.subcalendar = pageSubKeys();
  o.year = pageYear.checked ? Math.round(+pageYearNum.value) : null;
  if (o.year !== null && !isFinite(o.year)) throw new Error('the year is not a number');
  o.zoom = +pageZoom.value || 1;
  if (!(o.zoom >= 1 && o.zoom <= 6)) throw new Error('the zoom must be from 1 to 6');
  o.feasts = pageFeasts.value;
  o.latin = pageLatin.value === '' ? null : pageLatin.value === 'on';
  o.midText = pageMid.value;
  const kinds = pageReadingBoxes.filter(b => b.checked).map(b => b.value);
  o.readings = kinds.length === CY.READING_CATEGORIES.length ? 'all' : kinds.length ? kinds.join(',') : 'none';
  o.bibleDefault = pageBible.value || null;
  o.bibleSite = pageSite.value || null;
  o.w2w = pageW2w.value;
  o.hymns = pageHymns.value;
  o.hymnal = o.hymns === 'none' ? null : (pageHymnal.value || null);
  o.yearLine = pageYearLine.checked;
  o.layout = pageLayout.value;
  o.hide = ringBoxes().filter(b => !b.checked).map(b => b.value);
  o.colors = pageColors.value.trim().replace(/\s+/g, '');
  // Pictures of your own, the churches' pictures dropped, and the picture the page opens on.
  const onPage = new Set(o.churches || ALL_CHURCHES.map(t => t.key));
  o.ownArt = ownArts.map(a => {
    if (!a.data && !DATA.artwork[ownKey(a.name)]) throw new Error('choose ' + a.name + ' again with Add a picture of your own');
    return { name: a.name.split(/[\\/]/).pop(), data: a.data, fields: Object.assign({}, a.fields),
             churches: ALL_CHURCHES.map(t => t.key).filter(k => a.churches.has(k) && onPage.has(k)) };
  });
  o.dropArt = builtinArts(Array.from(onPage)).filter(k => artDropped.has(k));
  const opens = pageArtwork.value;
  const own = ownArts.find(a => ownKey(a.name) === opens);
  o.art = own ? own.name.split(/[\\/]/).pop() : opens;
  o.show = [pageCal.checked && 'calendar', pageEaster.checked && 'easter'].filter(Boolean);
  o.fixed = [!pageArt.checked && 'artwork', !pageReds.checked && 'reds'].filter(Boolean);
  if (pageBibles.value === 'all') o.bible = [];
  else if (pageBibles.value === 'own') o.bible = ['own'];
  else {
    const langs = Array.from(pageBibleList.querySelectorAll('label.lang input')).filter(b => b.checked);
    const shown = new Set(langs.map(b => b.value === 'english' ? 'en' : b.value));
    o.bible = langs.map(b => b.value).concat(Array.from(pageBibleList.querySelectorAll('input[data-lang]'))
      .filter(b => b.checked && !shown.has(b.dataset.lang)).map(b => b.value));
    if (!o.bible.length) throw new Error('choose the Bible versions the menu offers');
  }
  o.links = pageLinks.value;
  if (o.links === 'feasts' || o.links === 'none') {     // no Bible links: no Bible to choose
    o.bibleDefault = null; o.bibleSite = null; o.hymnal = null; o.bible = words(rawText('page_bibles'));
  }
  o.download = pageDownload.checked;
  o.makePage = pageMakePage.checked;
  o.edit = pageEdit.checked;
  o.localArt = pageLocalArt.checked;
  o.arrows = pageArrows.checked;
  o.footer = pageFooter.value;
  o.feedback = pageFeedback.value.trim();
  o.help = pageHelp.value.trim();
  o.fragment = pageFragment.checked;
  o.compress = pageCompress.checked;
  let name = pageName.value.trim() || 'church_year.html';
  if (!/\.html?$/i.test(name)) name += '.html';
  o.out = name.replace(/[\\/:*?"<>|]+/g, '_');
  return o;
}

/** A word for a shell: quoted when it has anything a shell reads. */
const shellWord = w => (/^[\w.,:/=+@%-]+$/.test(w) ? w : '"' + String(w).replace(/(["\\$`])/g, '\\$1') + '"');

/** church_year.py's command line for these options, leaving out what config.csv already says. */
function pageCommand(o) {
  const a = ['python', 'church_year.py'];
  const add = (...w) => a.push(...w.map(shellWord));
  if (o.churches) add('--churches', o.churches.join(','));
  if (o.church !== rawText('lectionary').toLowerCase()) add('--church', o.church);
  if (o.subcalendar.join(',') !== words(rawText('subcalendars')).join(',')) add('--subcalendar', o.subcalendar.length ? o.subcalendar.join(',') : 'none');
  if (o.year !== null) add('--year', String(o.year));
  if (o.zoom !== (parseFloat(rawText('page_zoom')) || 1)) add('--zoom', String(o.zoom));
  if (o.feasts !== rawText('feast_detail').toLowerCase()) add('--feasts', o.feasts);
  if (o.latin !== null) add(o.latin ? '--latin-names' : '--no-latin-names');
  if (o.midText !== rawText('mid_text').toLowerCase()) add('--mid-text', o.midText);
  if (o.readings !== (rawText('page_readings') || 'all')) add('--readings', o.readings);
  if (o.bibleDefault) add('--bible-default', o.bibleDefault);
  if (o.bibleSite && o.bibleSite !== rawText('page_bible_site').toLowerCase()) add('--bible-site', o.bibleSite);
  if (o.w2w !== (rawText('page_word_to_worship').toLowerCase() || 'on')) add('--word-to-worship', o.w2w);
  if (o.hymns !== (rawText('page_hymnary').toLowerCase() || 'on')) add('--hymnary', o.hymns);
  if (o.hymnal) add('--hymnal', o.hymnal);
  if (o.yearLine !== CY.truthy(rawText('year_line'))) add(o.yearLine ? '--year-line' : '--no-year-line');
  if (o.layout !== layoutText(rawText('page_readings_layout'))) add('--readings-layout', o.layout);
  if (o.hide.join(',') !== words(rawText('page_hide')).join(',')) add('--hide', o.hide.join(','));
  if (o.colors !== rawText('page_colors')) add('--color-changes', o.colors);
  for (const a of o.ownArt) add('--own-art', ownSpec(a));
  if (o.dropArt.length) add('--drop-art', o.dropArt.join(','));
  add('--art', o.art);
  const cfgFixed = words(rawText('page_fixed').toLowerCase()).map(w => (w === 'art' ? 'artwork' : w));
  const cfgShow = words(rawText('page_show').toLowerCase());
  if (o.fixed.join(',') !== cfgFixed.join(',')) add('--fixed', o.fixed.join(','));
  if (o.show.join(',') !== cfgShow.join(',')) add('--show', o.show.join(','));
  if (o.bible.join(',') !== words(rawText('page_bibles')).join(',')) add('--bible', o.bible.join(','));
  if (o.footer !== (rawText('page_footer').toLowerCase() || 'full')) add('--footer', o.footer);
  const cfgFeedback = /^none$/i.test(rawText('page_feedback')) ? '' : rawText('page_feedback');
  if (o.feedback !== cfgFeedback) add('--feedback', o.feedback || 'none');
  const cfgHelp = /^none$/i.test(rawText('page_help')) ? '' : rawText('page_help');
  if (o.help !== cfgHelp) add('--help-link', o.help || 'none');
  const cfgLinks = (() => { const w = words(rawText('page_links').toLowerCase());
    if (!w.length || w.indexOf('all') >= 0) return 'all'; if (w.indexOf('none') >= 0) return 'none';
    return w.indexOf('bible') >= 0 ? (w.indexOf('feasts') >= 0 ? 'all' : 'bible') : 'feasts'; })();
  if (o.links !== cfgLinks) add('--links', o.links);
  const cfgOn = k => !rawText(k) || /^(true|1|yes|on|y)$/i.test(rawText(k));
  if (o.download !== cfgOn('page_download')) add(o.download ? '--download' : '--no-download');
  if (o.makePage !== cfgOn('page_make_page')) add(o.makePage ? '--make-page' : '--no-make-page');
  if (o.edit !== cfgOn('page_edit')) add(o.edit ? '--edit' : '--no-edit');
  if (o.arrows !== /^(true|1|yes|on|y)$/i.test(rawText('page_arrows_next_year'))) add(o.arrows ? '--arrows-next-year' : '--arrows-same-year');
  const cfgLocal = /^(true|1|yes|on|y)$/i.test(rawText('page_local_art'));
  if (o.localArt !== cfgLocal) add(o.localArt ? '--local-art' : '--no-local-art');
  if (o.fragment) add('--fragment');
  if (!o.compress) add('--no-compress');
  if (o.out !== 'church_year.html') add('-o', o.out);
  return a.join(' ');
}
function pageCommandShow() {
  try { pageCmd.textContent = pageCommand(pageOptions()); }
  catch (e) { pageCmd.textContent = '(' + (e && e.message || e) + ')'; }
}

// ---- A command back into the window ------------------------------------------

/** Words as a shell splits them: quotes ("…" with \ escapes, '…' as is) hold spaces. */
function shellWords(text) {
  const out = [];
  let cur = null, i = 0;
  const s = String(text).replace(/\\\r?\n/g, ' ').replace(/\^\r?\n/g, ' ');   // a line continued (sh, cmd)
  while (i < s.length) {
    const c = s[i];
    if (/\s/.test(c)) { if (cur !== null) { out.push(cur); cur = null; } i++; continue; }
    cur = cur || '';
    if (c === '"') {
      i++;
      while (i < s.length && s[i] !== '"') {
        if (s[i] === '\\' && i + 1 < s.length && /["\\$`]/.test(s[i + 1])) i++;
        cur += s[i++];
      }
      i++;
    } else if (c === "'") {
      i++;
      while (i < s.length && s[i] !== "'") cur += s[i++];
      i++;
    } else if (c === '\\' && i + 1 < s.length) { cur += s[i + 1]; i += 2; }
    else { cur += c; i++; }
  }
  if (cur !== null) out.push(cur);
  return out;
}

// church_year.py's options: the name each spelling stands for, and whether it takes a value.
const CMD_OPTIONS = {
  '--churches': 'churches', '--church': 'church', '--subcalendar': 'subcalendar', '--year': 'year',
  '--zoom': 'zoom', '--feasts': 'feasts', '--latin-names': 'latin+', '--no-latin-names': 'latin-',
  '--mid-text': 'mid', '--readings': 'readings', '--bible-default': 'bibleDefault', '--bible-site': 'site',
  '--word-to-worship': 'w2w', '--hymnary': 'hymns', '--hymnal': 'hymnal', '--year-line': 'yearLine+', '--no-year-line': 'yearLine-', '--readings-layout': 'layout', '--hide': 'hide', '--color-changes': 'colors', '--art': 'art',
  '--own-art': 'ownArt', '--drop-art': 'dropArt', '--fixed': 'fixed', '--show': 'show',
  '--bible': 'bible', '--footer': 'footer', '--feedback': 'feedback', '--help-link': 'help', '--links': 'links',
  '--download': 'download+', '--no-download': 'download-', '--make-page': 'makePage+',
  '--no-make-page': 'makePage-', '--edit': 'edit+', '--no-edit': 'edit-', '--local-art': 'localArt+', '--no-local-art': 'localArt-', '--arrows-next-year': 'arrows+', '--arrows-same-year': 'arrows-', '--fragment': 'fragment+', '--no-compress': 'compress-', '-o': 'out', '--output': 'out', '--out': 'out',
  '--data': 'data', '--settings': 'settings', '--list': 'list+', '--list-churches': 'list+',
};

/** The command's options, as argparse reads them (a long option may be cut short while it is the only one so begun). */
function readCommand(text) {
  // A settings file's # lines are notes.
  let args = shellWords(String(text).split(/\r?\n/).filter(l => !/^\s*#/.test(l)).join('\n'));
  const at = args.findIndex(w => /church_year(_web)?(\.py)?$/i.test(w));     // church_year_web.py was its old name
  if (at >= 0) args = args.slice(at + 1);
  else while (args.length && !/^-/.test(args[0])) args.shift();     // "python" and the like
  const o = { subcalendar: [], ownArt: [] }, unknown = [];
  for (let i = 0; i < args.length; i++) {
    let w = args[i], value = null;
    const eq = w.indexOf('=');
    if (w.indexOf('--') === 0 && eq > 0) { value = w.slice(eq + 1); w = w.slice(0, eq); }
    let name = CMD_OPTIONS[w];
    if (!name && w.indexOf('--') === 0) {
      const hits = Object.keys(CMD_OPTIONS).filter(k => k.indexOf(w) === 0);
      if (hits.length === 1) name = CMD_OPTIONS[hits[0]];
    }
    if (!name) { unknown.push(w); continue; }
    if (/[+-]$/.test(name)) { o[name.slice(0, -1)] = name.slice(-1) === '+'; continue; }
    if (value === null) value = args[++i];
    if (value === undefined) throw new Error(w + ' needs a value');
    if (name === 'subcalendar') o.subcalendar.push(value);
    else if (name === 'ownArt') o.ownArt.push(value);
    else o[name] = value;
  }
  if (!o.subcalendar.length) delete o.subcalendar;
  if (!o.ownArt.length) delete o.ownArt;
  return { o, unknown };
}

/** The churches a --churches value keeps (select_churches): keys, key prefixes ending in *, or tradition names. */
function churchesFrom(spec, bad) {
  const keep = [];
  for (const w of words(spec)) {
    const lw = w.toLowerCase();
    const hits = ALL_CHURCHES.filter(t => t.key === lw || (lw.endsWith('*') && t.key.indexOf(lw.slice(0, -1)) === 0)
      || String(t.tradition || '').toLowerCase() === lw);
    if (!hits.length) bad.push(w);
    for (const t of hits) if (keep.indexOf(t.key) < 0) keep.push(t.key);
  }
  return keep;
}

/** Set every choice in the window as the command does, and the rest as config.csv does (as the script would). */
function useCommand(text) {
  const { o, unknown } = readCommand(text);
  const notes = [];
  // What would stop it is found before anything in the window changes.
  const kindsText = o.readings !== undefined ? o.readings : rawText('page_readings');
  const wrong = String(kindsText).split(',').map(x => x.trim().replace(/^-+/, '').toLowerCase())
    .filter(x => x && !/^(0|false|no|off|none|1|true|yes|on|all)$/.test(x) && CY.READING_CATEGORIES.indexOf(x) < 0);
  if (wrong.length) throw new Error("--readings: no kind of reading '" + wrong[0] + "'");
  if (unknown.length) notes.push('left out what the script does not take: ' + unknown.join(' '));
  if (o.data) notes.push('--data (a folder of CSVs) needs the script; this page has its own tables');
  if (o.settings) notes.push('--settings ' + o.settings + ' is a file: load it with Load settings');
  // Churches: --churches, else page_churches, else every one here.
  const bad = [];
  const spec = o.churches !== undefined ? o.churches : rawText('page_churches');
  const keys = words(spec).length ? churchesFrom(spec, bad) : ALL_CHURCHES.map(t => t.key);
  if (bad.length) notes.push('no church here named ' + bad.join(', '));
  if (!keys.length) throw new Error('none of those churches are on this page');
  if (o.layout !== undefined) o.layout = layoutText(o.layout);
  for (const k of ['feasts', 'mid', 'site', 'w2w', 'hymns', 'footer', 'layout']) {
    const menu = { feasts: pageFeasts, mid: pageMid, site: pageSite, w2w: pageW2w, hymns: pageHymns, footer: pageFooter, layout: pageLayout }[k];
    if (o[k] !== undefined && !Array.from(menu.options).some(x => x.value === String(o[k]).toLowerCase())) {
      throw new Error("'" + o[k] + "' is not one of " + Array.from(menu.options).map(x => x.value).filter(Boolean).join(', '));
    }
  }
  setChurches(keys);
  // The church it opens on, and its calendars.
  const want = String(o.church || rawText('lectionary')).trim().toLowerCase();
  const first = ALL_CHURCHES.find(t => keys.indexOf(t.key) >= 0).key;
  pageChurch.value = keys.indexOf(want) >= 0 ? want : first;
  if (o.church && keys.indexOf(want) < 0) notes.push('--church ' + o.church + ' is not among the churches kept');
  const subs = o.subcalendar ? [].concat(...o.subcalendar.map(words)) : words(rawText('subcalendars'));
  churchMenus(subs.length === 1 && subs[0] === 'none' ? [] : subs);
  pageYear.checked = o.year !== undefined;
  if (o.year !== undefined) pageYearNum.value = parseInt(o.year, 10);
  pageZoom.value = o.zoom !== undefined ? o.zoom : (parseFloat(rawText('page_zoom')) || 1);
  pageFeasts.value = String(o.feasts || rawText('feast_detail') || 'all').toLowerCase();
  pageMid.value = String(o.mid || rawText('mid_text') || 'as-set').toLowerCase();
  pageLatin.value = o.latin === undefined ? '' : (o.latin ? 'on' : 'off');
  const kinds = readingKindsFrom(kindsText);
  for (const b of pageReadingBoxes) b.checked = kinds.indexOf(b.value) >= 0;
  pageBible.value = '';
  if (o.bibleDefault) { pick(pageBible, o.bibleDefault.toUpperCase()); if (!pageBible.value) notes.push('no Bible version ' + o.bibleDefault); }
  pageSite.value = '';
  if (o.site) pick(pageSite, o.site.toLowerCase());
  pageW2w.value = String(o.w2w || rawText('page_word_to_worship') || 'on').toLowerCase();
  pageHymns.value = String(o.hymns || rawText('page_hymnary') || 'on').toLowerCase();
  pageHymnal.value = '';
  if (o.hymnal) {
    const hit = Array.from(pageHymnal.options).find(x => x.value && x.value.toLowerCase() === String(o.hymnal).toLowerCase());
    if (hit) pageHymnal.value = hit.value; else notes.push('no hymnal ' + o.hymnal + ' among the churches here with several');
  }
  pageYearLine.checked = o.yearLine !== undefined ? !!o.yearLine : CY.truthy(rawText('year_line'));
  pageLayout.value = o.layout || layoutText(rawText('page_readings_layout'));
  const hide = words(o.hide !== undefined ? o.hide : rawText('page_hide'));
  for (const b of ringBoxes()) b.checked = hide.indexOf(b.value) < 0;
  pageColors.value = o.colors !== undefined ? o.colors : rawText('page_colors');
  pageColorModeFit();
  // The artwork: pictures of your own (their files chosen again unless the window or the page
  // has them: a command names a picture but cannot carry it), those dropped, and the one it opens on.
  const before = ownArts;
  const again = [];
  const adopt = (name, fields, churches) => {
    const was = before.find(x => ownKey(x.name) === ownKey(name));
    const data = was ? was.data : null;
    if (!data && !DATA.artwork[ownKey(name)]) again.push(name.split(/[\\/]/).pop());
    return { name: name.split(/[\\/]/).pop(), data: data, fields: fields, churches: new Set(churches), open: false };
  };
  ownArts = [];
  for (const spec of o.ownArt || []) {
    const { name, fields, churches } = parseOwnSpec(spec);
    if (!/\.(svg|png|jpe?g|gif|webp)$/i.test(name)) throw new Error('--own-art ' + name + ': not a picture file (.svg, .png, .jpg, .jpeg, .gif, .webp)');
    const bad = churches.filter(c => keys.indexOf(c) < 0);
    if (bad.length) throw new Error('--own-art ' + name + ": no church '" + bad[0] + "' on this page");
    const a = adopt(name, fields, churches);
    for (const x of ownArts) for (const c of a.churches) x.churches.delete(c);
    ownArts = ownArts.filter(x => ownKey(x.name) !== ownKey(a.name)).concat([a]);
  }
  artDropped = new Set(words(String(o.dropArt || '').toLowerCase()));
  const art = String(o.art !== undefined ? o.art : (rawText('center_svg') || 'auto')).trim();
  if (/\.(svg|png|jpe?g|gif|webp)$/i.test(art) && !ownArts.some(x => ownKey(x.name) === ownKey(art))
      && !(DATA.artwork[ownKey(art)] && o.ownArt === undefined && o.art === undefined)) {
    ownArts.push(adopt(art, {}, []));
  }
  if (o.ownArt === undefined && o.art === undefined) ownArts = ownArtsOfPage();
  if (again.length) notes.push('choose ' + again.join(', ') + ' again with Add a picture of your own: a command names a picture but cannot carry it');
  artMenu();
  pageArtwork.value = 'auto';
  pick(pageArtwork, /\.(svg|png|jpe?g|gif|webp)$/i.test(art) ? ownKey(art) : art.toLowerCase());
  // What it shows.
  const fixed = words(String(o.fixed !== undefined ? o.fixed : rawText('page_fixed')).toLowerCase()).map(w => (w === 'art' ? 'artwork' : w));
  const show = words(String(o.show !== undefined ? o.show : rawText('page_show')).toLowerCase());
  pageCal.checked = show.indexOf('calendar') >= 0 && fixed.indexOf('calendar') < 0;
  pageEaster.checked = show.indexOf('easter') >= 0 && fixed.indexOf('easter') < 0;
  pageArt.checked = fixed.indexOf('artwork') < 0;
  pageReds.checked = fixed.indexOf('reds') < 0;
  const bibles = words(o.bible !== undefined ? o.bible : rawText('page_bibles'));
  pageBibles.value = !bibles.length ? 'all' : /^own$/i.test(bibles[0]) ? 'own' : 'some';
  for (const b of pageBibleList.querySelectorAll('input')) {
    b.checked = bibles.some(x => x.toLowerCase() === b.value.toLowerCase()); b.disabled = false;
  }
  for (const b of pageBibleList.querySelectorAll('label.lang input')) {
    if (b.checked) for (const v of b.parentElement.nextElementSibling.querySelectorAll('input')) { v.checked = true; v.disabled = true; }
  }
  pageBibleList.hidden = pageBibles.value !== 'some';
  const links = words(String(o.links !== undefined ? o.links : rawText('page_links')).toLowerCase());
  pageLinks.value = !links.length || links.indexOf('all') >= 0 || (links.indexOf('bible') >= 0 && links.indexOf('feasts') >= 0) ? 'all'
    : links.indexOf('none') >= 0 ? 'none' : links.indexOf('bible') >= 0 ? 'bible' : 'feasts';
  const cfgOn = k => !rawText(k) || /^(true|1|yes|on|y)$/i.test(rawText(k));
  pageDownload.checked = o.download !== undefined ? o.download : cfgOn('page_download');
  pageMakePage.checked = o.makePage !== undefined ? o.makePage : cfgOn('page_make_page');
  pageEdit.checked = o.edit !== undefined ? o.edit : cfgOn('page_edit');
  pageArrows.checked = o.arrows !== undefined ? o.arrows : /^(true|1|yes|on|y)$/i.test(rawText('page_arrows_next_year'));
  pageLocalArt.checked = o.localArt !== undefined ? o.localArt : /^(true|1|yes|on|y)$/i.test(rawText('page_local_art'));
  pageFooter.value = String(o.footer || rawText('page_footer') || 'full').toLowerCase();
  const fb = o.feedback !== undefined ? o.feedback : rawText('page_feedback');
  pageFeedback.value = /^none$/i.test(fb) ? '' : fb;
  const hl = o.help !== undefined ? o.help : rawText('page_help');
  pageHelp.value = /^none$/i.test(hl) ? '' : hl;
  pageFragment.checked = !!o.fragment;
  pageCompress.checked = o.compress !== undefined ? o.compress : true;
  pageName.value = o.out ? String(o.out).split(/[\\/]/).pop() || 'church_year.html' : 'church_year.html';
  if (o.out && /[\\/]$/.test(o.out)) pageName.value = 'church_year.html';
  const dropped = pageBibleFit();
  if (dropped) notes.push('the Bible ' + dropped + ' is not on the Bible menu, so each church opens in its own');
  pageLinksShow();
  pageColorsShow();
  pageCommandShow();
  return notes;
}

$('pageCmdUse').addEventListener('click', () => {
  const note = $('pageCmdNote');
  try {
    const notes = useCommand($('pageCmdIn').value);
    note.textContent = 'Set from the command.' + (notes.length ? ' Note: ' + notes.join('; ') + '.' : '');
  } catch (e) {
    note.textContent = 'Could not read the command: ' + (e && e.message || e);
  }
});
// Settings as a small file: the command, with a note of what it is.
$('pageCmdSave').addEventListener('click', () => {
  const cmd = pageCmd.textContent;
  if (/^\(/.test(cmd)) { $('pageCmdNote').textContent = 'Nothing to save yet: ' + cmd.slice(1, -1) + '.'; return; }
  const text = '# Church Year Wheel: Make a page settings, saved ' + isoToday() + '.\n'
    + '# Load this file in Make a page to set the window again, or run the command in the project folder.\n'
    + cmd + '\n';
  const name = (pageName.value.trim().replace(/\.html?$/i, '') || 'church_year').replace(/[\\/:*?"<>|]+/g, '_') + '_settings.txt';
  saveBlob(new Blob([text], { type: 'text/plain;charset=utf-8' }), name);
  $('pageCmdNote').textContent = 'Saved ' + name + '.';
});
$('pageCmdLoad').addEventListener('click', () => $('pageCmdFile').click());
$('pageCmdFile').addEventListener('change', async () => {
  const f = $('pageCmdFile').files && $('pageCmdFile').files[0], note = $('pageCmdNote');
  if (!f) return;
  try {
    const text = await f.text();
    $('pageCmdIn').value = text.split(/\r?\n/).filter(l => !/^\s*#/.test(l)).join('\n').trim();
    const notes = useCommand(text);
    note.textContent = 'Set from ' + f.name + '.' + (notes.length ? ' Note: ' + notes.join('; ') + '.' : '');
  } catch (e) {
    note.textContent = 'Could not read ' + f.name + ': ' + (e && e.message || e);
  }
  $('pageCmdFile').value = '';
});
$('pageCmdCopy').addEventListener('click', async () => {
  const note = $('pageCmdNote');
  try { await navigator.clipboard.writeText(pageCmd.textContent); note.textContent = 'Copied.'; }
  catch (e) {
    const r = document.createRange(); r.selectNodeContents(pageCmd);
    const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
    note.textContent = 'Selected: copy it with Ctrl+C (\u2318C on a Mac).';
  }
});

// ---- Edit the data... ---------------------------------------------------------
// The day's names and colors and its readings, the kinds of reading (their
// names and order), the season colors and the palette, changed on the page,
// kept in this browser and written into a page Make a page makes; and the
// files they change, downloaded for the Python scripts.

const editDialog = $('editDialog'), editBody = $('editBody'), editStatus = $('editStatus');
const editTabs = Array.from(editDialog.querySelectorAll('[data-tab]'));
let editTab = 'day';

/** The files the page's tables are written from, by table: to find the file of a row. */
function tablePaths() {
  const out = new Map();
  const paths = new Set(Object.keys(DATA.csv || {}).concat(EDITS.map(e => e.p)));
  for (const p of paths) {
    const t = tableAt(DATA, p);
    if (t) out.set(t.get(), p);
  }
  return out;
}

/**
 * Where a row the wheel drew from is written: its file, and its key there
 * (its place as the page came, or the id of the change that added it), or
 * null where the page cannot write the file back.
 */
function rowPlace(row) {
  const o = row && CY.rowOrigin(row);
  if (!o) return null;
  const paths = tablePaths();
  let path, index;
  if (o.table) { path = paths.get(o.table); index = o.index; }
  else {
    for (const [table, p] of paths) {
      if (Array.isArray(table)) { const i = table.indexOf(o.row); if (i >= 0) { path = p; index = i; break; } }
    }
  }
  if (!path || !layoutOf(DATA, path)) return null;
  const live = EDIT_NODES[path] ? EDIT_NODES[path].filter(n => !n.del) : null;
  const key = live ? live[index].key : index;
  return { path: path, key: key, row: live ? live[index].row : o.row };
}

/** Keep the changes, lay them over the tables and draw the year again. */
function editsChanged(note, keepView) {
  try { localStorage.setItem(EDIT_KEY, JSON.stringify({ sig: EDIT_SIG, edits: EDITS })); } catch (err) { /* this visit only */ }
  EDIT_NODES = applyEdits(DATA, EDITS, EDIT_ORIG);
  colorsDefaultCache = null;
  for (const k of Object.keys(readingKinds)) delete readingKinds[k];
  const keep = chosen, year = drawnYear();
  drawn = null;
  drawYear(year, keep);
  editStatus.textContent = note || '';
  if (keepView) $('editExport').disabled = !changedFiles().length; else editShow();
}
let editIds = EDITS.reduce((n, e) => Math.max(n, +(String(e.id || '').slice(1)) || 0), 0);
const newId = () => 'n' + (++editIds);
function editSet(place, row) {
  const lay = layoutOf(DATA, place.path);
  EDITS.push({ p: place.path, op: 'set', [typeof place.key === 'string' ? 'id' : 'i']: place.key, row: tidyRow(row, lay.cols) });
}
function editDel(place) {
  EDITS.push({ p: place.path, op: 'del', [typeof place.key === 'string' ? 'id' : 'i']: place.key });
}
/** A row added to a file, after the row with key `after` (null: the file's last). */
function editAdd(path, row, after) {
  const lay = layoutOf(DATA, path);
  const t = tableAt(DATA, path);
  let anchor = after;
  if (anchor === null || anchor === undefined) {
    const live = EDIT_NODES[path] || tableRows(t, t.get()).map((r, i) => ({ key: i, del: false }));
    const last = live.filter(n => !n.del).pop();
    anchor = last ? last.key : null;
  }
  const id = newId();
  EDITS.push({ p: path, op: 'add', id: id, after: anchor, row: tidyRow(row, lay.cols) });
  return id;
}

// Small pieces of the dialog.
const el = (tag, props, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (k === 'class') e.className = v;
    else if (k === 'list' || k === 'style' || !(k in e)) e.setAttribute(k, v);
    else e[k] = v;
  }
  e.append(...kids.filter(k => k !== null && k !== undefined && k !== false));
  return e;
};
const field = (label, value, title, attrs) => {
  const input = el('input', Object.assign({ type: 'text', value: value || '' }, attrs || {}));
  return [el('label', { title: title || '' }, label + ' ', input), input];
};
const fileNote = (path, row) => {
  const v = row ? words(row.variant) : [];
  const users = churchesReading(path).filter(k => !v.length || v.indexOf(traditionOf(k).variant) >= 0);
  return 'data/' + path + (users.length > 1 ? ' · read by ' + users.length + ' churches: a change here changes them all' : '');
};
/** The churches whose drawing or readings a file feeds. */
function churchesReading(path) {
  const owner = CY.fileOwner(DATA, path);
  if (!owner) return DATA.traditions.map(t => t.key);
  if (owner.indexOf('readings/') === 0) {
    const name = path.slice('readings/'.length, -'.csv'.length);
    return DATA.traditions.filter(t => words(CY.traditionSettings(DATA, t).readings || (DATA.settings || {}).readings).indexOf(name) >= 0).map(t => t.key);
  }
  return DATA.traditions.filter(t => t.folder === owner).map(t => t.key);
}
/** The color names the church knows, for the color boxes. */
function colorList() {
  const id = 'editColorNames';
  let list = editDialog.querySelector('#' + id);
  if (!list) { list = el('datalist', { id: id }); editDialog.append(list); }
  const p = DATA.profiles[currentTradition()];
  list.replaceChildren(...Object.keys(p.colors).map(k => el('option', { value: k })));
  return id;
}
const colorField = (label, value, title) => field(label, value, title, { list: colorList(), class: 'colorname', spellcheck: false });

/** The kinds of reading a church has, with the names the page gives them. */
function editKindsOf(key) {
  const t = traditionOf(key);
  const source = new CY.Source(DATA, t, []);
  const seen = [];
  for (const r of source.readings) { const k = String(r.kind || '').trim(); if (k && seen.indexOf(k) < 0) seen.push(k); }
  const labels = Object.assign({}, CY.READING_LABELS);
  for (const part of String(DATA.profiles[key].settings.reading_labels || '').split(';')) {
    const i = part.indexOf('=');
    if (i > 0) labels[part.slice(0, i).trim()] = part.slice(i + 1).trim();
  }
  const rank = {};
  String(DATA.profiles[key].settings.reading_order || '').split('|').forEach((part, i) => {
    for (const k of part.split(/\s+/).filter(Boolean)) rank[k] = i;
  });
  const ordered = seen.filter(k => k in rank).sort((a, b) => rank[a] - rank[b]).concat(seen.filter(k => !(k in rank)));
  return { kinds: ordered, labels: labels };
}

/** The church's own row of a setting in its tradition.csv, or where to add one. */
function settingPlace(key, name) {
  const t = traditionOf(key);
  const path = t.folder + '/tradition.csv';
  if (!layoutOf(DATA, path)) return null;
  const rows = DATA.folders[t.folder].settings;
  let found = null;
  rows.forEach((r, i) => {
    const v = words(r.variant);
    if (r.setting === name && (!v.length || v.indexOf(t.variant) >= 0)) found = i;
  });
  const live = EDIT_NODES[path] ? EDIT_NODES[path].filter(n => !n.del) : null;
  if (found !== null) {
    const r = rows[found], v = words(r.variant);
    const only = v.length ? v.length === 1 && v[0] === t.variant : churchesReading(path).length === 1;
    if (only) return { path: path, key: live ? live[found].key : found, row: r };
  }
  return { path: path, key: null, row: null, variant: t.variant || '' };
}
function saveSetting(key, name, value) {
  const place = settingPlace(key, name);
  if (!place) return false;
  if (place.row) editSet(place, Object.assign({}, place.row, { value: value }));
  else editAdd(place.path, { setting: name, value: value, variant: place.variant }, null);
  return true;
}

function editShow() {
  for (const b of editTabs) b.setAttribute('aria-selected', String(b.dataset.tab === editTab));
  const key = currentTradition();
  editTabs.find(b => b.dataset.tab === 'changes').textContent = 'Changes' + (EDITS.length ? ' (' + EDITS.length + ')' : '');
  const body = { day: editDayView, kinds: editKindsView, seasons: editSeasonsView, colors: editColorsView, changes: editChangesView }[editTab](key);
  editBody.replaceChildren(...body);
  $('editExport').disabled = !changedFiles().length;
}

// This day: its names and colors, and its readings.
function editDayView(key) {
  const out = [el('p', { class: 'text' }, pretty(chosen) + ' · ' + traditionOf(key).label)];
  const cal = lastBuilt && lastBuilt.cal;
  const z = CY.fromIso(chosen);
  const entries = [];
  if (cal) {
    for (const e of cal.year.principal.concat(cal.year.feasts)) {
      if (e.day !== z || !e.row) continue;
      const place = rowPlace(e.row);
      if (place && !entries.some(x => x.place.path === place.path && x.place.key === place.key)) entries.push({ e: e, place: place });
    }
  }
  const names = el('div', { class: 'group' }, 'Names and colors');
  for (const { e, place } of entries) {
    const r = place.row, feast = 'name' in e;
    const run = !!r.from;
    const card = el('div', { class: 'card' });
    const cols = feast
      ? [['name', 'Name'], ['full_name', 'Full name'], ['link', 'Link'], ['color_override', 'Color'], ['color_override_bottom', 'Lower half']]
      : [['title', run ? 'Names (a pattern)' : 'Name'], ['full_name', 'Full name'], ['color', 'Color'], ['color_bottom', 'Lower half']];
    const inputs = {};
    for (const [c, label] of cols) {
      const [l, i] = /color/.test(c) ? colorField(label, r[c], c) : field(label, r[c], c);
      inputs[c] = i; card.append(l);
    }
    const save = el('button', { type: 'button', textContent: 'Save' });
    save.addEventListener('click', () => {
      const row = Object.assign({}, r);
      for (const c in inputs) row[c] = inputs[c].value;
      editSet(place, row); editsChanged('Saved.');
    });
    const acts = el('div', { class: 'row' }, save);
    if (!run && feast) {
      const del = el('button', { type: 'button', textContent: 'Remove' });
      del.addEventListener('click', () => { editDel(place); editsChanged('Removed.'); });
      acts.append(del);
    }
    card.append(acts, el('p', { class: 'text small' }, fileNote(place.path, r) + (run ? ' · a run of days: the change is the whole run’s' : '')));
    names.append(card);
  }
  if (!entries.length) names.append(el('p', { class: 'text' }, 'Nothing on this day comes from a file this page can write.'));
  // A feast of its own on this date.
  const t = traditionOf(key);
  const feastPath = t.folder + '/feasts.csv';
  if (layoutOf(DATA, feastPath)) {
    const card = el('details', { class: 'card add' }, el('summary', {}, 'Add a feast on this date'));
    const [l1, name] = field('Name', '', 'name');
    const [l2, full] = field('Full name', '', 'full_name');
    const [l3, color] = colorField('Color', '', 'color_override: the whole day');
    const [l4, bottom] = colorField('Lower half', '', 'color_override_bottom');
    const only = el('input', { type: 'checkbox', checked: !!t.variant });
    const add = el('button', { type: 'button', textContent: 'Add' });
    add.addEventListener('click', () => {
      if (!name.value.trim()) { editStatus.textContent = 'A feast needs a name.'; return; }
      editAdd(feastPath, { date: chosen.slice(5), name: name.value, full_name: full.value, color_override: color.value,
        color_override_bottom: bottom.value, variant: only.checked ? t.variant : '' }, null);
      editsChanged('Added.');
    });
    card.append(l1, l2, l3, l4, t.variant ? el('label', { class: 'check' }, only, ' Only for ' + t.label) : null, el('div', { class: 'row' }, add));
    names.append(card);
  }
  out.push(names);
  // The day's readings, set by set.
  const { kinds, labels } = editKindsOf(key);
  const kindSelect = (value, onNew) => {
    const s = el('select', {});
    const all = kinds.indexOf(value) >= 0 || !value ? kinds : kinds.concat([value]);
    for (const k of all) s.append(el('option', { value: k, textContent: (labels[k] || k) + ' (' + k + ')' }));
    s.append(el('option', { value: '\u0000new', textContent: 'A new kind…' }));
    s.value = value || kinds[0] || '\u0000new';
    s.addEventListener('change', () => { if (s.value === '\u0000new') onNew(s); });
    return s;
  };
  // A new kind: its key and its name, kept in the church's reading_labels.
  const newKind = s => {
    const box = el('span', { class: 'newkind' });
    const [lk, k] = field('Key', '', 'a short word: tract, verse, canticle');
    const [ln, n] = field('Name', '', 'what the page calls it: Tract');
    const ok = el('button', { type: 'button', textContent: 'OK' });
    ok.addEventListener('click', () => {
      const kk = k.value.trim().toLowerCase().replace(/[^a-z0-9_]+/g, '_');
      if (!kk || kk === 'omit' || kk.charAt(0) === '=') { editStatus.textContent = 'A kind needs a key of letters and numbers.'; return; }
      const name = n.value.trim() || kk;
      if ((labels[kk] || '') !== name) {
        const own = String(DATA.profiles[key].settings.reading_labels || '').split(';').map(x => x.trim()).filter(x => x && x.split('=')[0].trim() !== kk);
        own.push(kk + '=' + name);
        if (!saveSetting(key, 'reading_labels', own.join('; '))) { editStatus.textContent = 'This page cannot write this church’s tradition.csv.'; return; }
        labels[kk] = name;
        editsChanged('The kind ' + name + ' is kept; give it a reading.', true);
      }
      if (kinds.indexOf(kk) < 0) kinds.push(kk);
      s.insertBefore(el('option', { value: kk, textContent: name + ' (' + kk + ')' }), s.lastChild);
      s.value = kk; box.remove();
      s.dispatchEvent(new Event('change'));
    });
    box.append(lk, ln, ok);
    s.after(box);
  };
  const reads = el('div', { class: 'group' }, 'Readings');
  for (const g of READINGS[chosen] || []) {
    const set = el('div', { class: 'card' }, el('div', { class: 'settitle' }, g.title || 'The day’s own'));
    let last = null, lastPath = null, proto = null;
    for (const it of g.items) {
      const place = it.row ? rowPlace(it.row) : null;
      const line = el('div', { class: 'row reading' });
      if (!place) {
        line.append(el('span', { class: 'kind' }, it.label + ':'), ' ' + it.reading, el('span', { class: 'text small' }, ' (not in a file this page can write)'));
        set.append(line); continue;
      }
      last = place.key; lastPath = place.path; proto = place.row;
      const k = kindSelect(it.kind, newKind);
      const text = el('input', { type: 'text', value: place.row.reading || '', class: 'readingtext' });
      const save = () => {
        if (k.value === '\u0000new') return;
        if (k.value === place.row.kind && text.value.trim() === (place.row.reading || '')) return;
        if (!text.value.trim()) { editStatus.textContent = 'A reading cannot be blank: Remove takes it away.'; return; }
        editSet(place, Object.assign({}, place.row, { kind: k.value, reading: text.value }));
        editsChanged('Saved.');
      };
      k.addEventListener('change', save);
      text.addEventListener('change', save);
      const del = el('button', { type: 'button', textContent: '✕', title: 'Remove this reading', class: 'remove' });
      del.addEventListener('click', () => { editDel(place); editsChanged('Removed.'); });
      line.append(k, text, del);
      set.append(line);
    }
    if (proto) {
      const add = el('details', { class: 'add' }, el('summary', {}, 'Add a reading to this set'));
      const k = kindSelect('', newKind);
      const text = el('input', { type: 'text', class: 'readingtext', placeholder: 'Psalm 23' });
      const ok = el('button', { type: 'button', textContent: 'Add' });
      const anchor = last, path = lastPath, row = proto;
      ok.addEventListener('click', () => {
        if (k.value === '\u0000new' || !text.value.trim()) { editStatus.textContent = 'Choose its kind and write the reading.'; return; }
        const r = {};
        for (const c of ['day', 'offset', 'when', 'cycle', 'variant', 'title']) if (row[c] !== undefined) r[c] = row[c];
        editAdd(path, Object.assign(r, { kind: k.value, reading: text.value }), anchor);
        editsChanged('Added.');
      });
      add.append(el('div', { class: 'row reading' }, k, text, ok), el('p', { class: 'text small' }, fileNote(path, row)));
      set.append(add);
    }
    reads.append(set);
  }
  // A set of readings of its own on this date.
  const ownPath = t.folder + '/readings.csv';
  if (layoutOf(DATA, ownPath)) {
    const card = el('details', { class: 'card add' }, el('summary', {}, 'Add a set of readings on this date'));
    const [lt, title] = field('Title', '', 'blank: the day’s own readings; a feast’s name keeps them to that feast');
    const k = kindSelect('', newKind);
    const text = el('input', { type: 'text', class: 'readingtext', placeholder: 'Isaiah 9:2–7' });
    const ok = el('button', { type: 'button', textContent: 'Add' });
    ok.addEventListener('click', () => {
      if (k.value === '\u0000new' || !text.value.trim()) { editStatus.textContent = 'Choose its kind and write the reading.'; return; }
      editAdd(ownPath, { day: chosen.slice(5), variant: t.variant || '', title: title.value, kind: k.value, reading: text.value }, null);
      editsChanged('Added: further readings join it with Add a reading.');
    });
    card.append(lt, el('div', { class: 'row reading' }, k, text, ok), el('p', { class: 'text small' }, fileNote(ownPath)));
    reads.append(card);
  }
  out.push(reads);
  return out;
}

// The kinds of reading: their names and their order within a set.
function editKindsView(key) {
  const { kinds, labels } = editKindsOf(key);
  const order = kinds.slice(), names = Object.assign({}, labels);
  const out = [el('p', { class: 'text' }, 'The kinds of reading ' + traditionOf(key).label + ' has, in the order a set lists them. A new kind is added with a reading of it (This day).')];
  const list = el('ol', { class: 'kinds' });
  const draw = () => {
    list.replaceChildren(...order.map((k, i) => {
      const up = el('button', { type: 'button', textContent: '↑', title: 'Earlier', disabled: i === 0 });
      const down = el('button', { type: 'button', textContent: '↓', title: 'Later', disabled: i === order.length - 1 });
      up.addEventListener('click', () => { order.splice(i - 1, 0, order.splice(i, 1)[0]); draw(); });
      down.addEventListener('click', () => { order.splice(i + 1, 0, order.splice(i, 1)[0]); draw(); });
      const name = el('input', { type: 'text', value: names[k] || k });
      name.addEventListener('input', () => { names[k] = name.value; });
      return el('li', { class: 'row' }, up, down, el('code', {}, k), name);
    }));
  };
  draw();
  const save = el('button', { type: 'button', textContent: 'Save' });
  save.addEventListener('click', () => {
    const own = [];
    for (const part of String(DATA.profiles[key].settings.reading_labels || '').split(';')) {
      const i = part.indexOf('=');
      if (i > 0 && order.indexOf(part.slice(0, i).trim()) < 0) own.push(part.trim());
    }
    for (const k of order) if ((names[k] || '').trim() && names[k].trim() !== (CY.READING_LABELS[k] || k)) own.push(k + '=' + names[k].trim());
    const labelsNow = own.join('; '), orderNow = order.join(' | ');
    let ok = true;
    if (labelsNow !== String(DATA.profiles[key].settings.reading_labels || '')) ok = saveSetting(key, 'reading_labels', labelsNow) && ok;
    if (orderNow !== String(DATA.profiles[key].settings.reading_order || '')) ok = saveSetting(key, 'reading_order', orderNow) && ok;
    if (!ok) { editStatus.textContent = 'This page cannot write this church’s tradition.csv.'; return; }
    editsChanged('Saved.');
  });
  out.push(list, el('div', { class: 'row' }, save), el('p', { class: 'text small' }, 'Kept as reading_labels and reading_order in data/' + traditionOf(key).folder + '/tradition.csv.'));
  return out;
}

// The seasons' colors (seasons.csv) and the colors the church's periods give (periods.csv).
function editSeasonsView(key) {
  const t = traditionOf(key);
  const out = [el('p', { class: 'text' }, 'The colors of ' + t.label + '’s seasons. A color may name others the church allows after it: PURPLE; blue.')];
  const path = t.folder + '/seasons.csv';
  const group = el('div', { class: 'group' }, 'Seasons');
  const rows = DATA.folders[t.folder].seasons || [];
  if (!layoutOf(DATA, path)) group.append(el('p', { class: 'text' }, 'This page cannot write data/' + path + '.'));
  else {
    rows.forEach((r, i) => {
      const [l, c] = colorField(r.season, r.color, 'color');
      c.addEventListener('change', () => {
        const place = rowPlace(r) || { path: path, key: i, row: r };
        editSet(place, Object.assign({}, r, { color: c.value })); editsChanged('Saved.');
      });
      group.append(l);
    });
    const [ls, s] = field('Season', '', 'its key, as periods.csv names it: ADVENT');
    const [lc, c] = colorField('Color', '', 'color');
    const add = el('button', { type: 'button', textContent: 'Add' });
    add.addEventListener('click', () => {
      if (!s.value.trim() || !c.value.trim()) return;
      editAdd(path, { season: s.value.toUpperCase(), color: c.value }, null); editsChanged('Added.');
    });
    group.append(el('details', { class: 'add' }, el('summary', {}, 'Add a season'), ls, lc, el('div', { class: 'row' }, add)));
    group.append(el('p', { class: 'text small' }, fileNote(path)));
  }
  out.push(group);
  const ppath = t.folder + '/periods.csv';
  const periods = el('div', { class: 'group' }, 'Periods with a color of their own');
  if (layoutOf(DATA, ppath)) {
    for (const r of DATA.folders[t.folder].periods) {
      if (!r.color || !(words(r.variant).length === 0 || words(r.variant).indexOf(t.variant) >= 0)) continue;
      const [l, c] = colorField((r.name || r.season || '') + ' (' + r.start + ' – ' + r.end + ')', r.color, 'color');
      c.addEventListener('change', () => {
        const place = rowPlace(r);
        if (!place) return;
        editSet(place, Object.assign({}, r, { color: c.value })); editsChanged('Saved.');
      });
      periods.append(l);
    }
    periods.append(el('p', { class: 'text small' }, fileNote(ppath)));
    if (periods.querySelector('label')) out.push(periods);
  }
  return out;
}

// The palette: what each color name looks like.
function editColorsView(key) {
  const t = traditionOf(key);
  const own = t.folder + '/colors.csv';
  const out = [el('p', { class: 'text' }, 'What each color looks like on the wheel: its fill and the color of text on it. A color changed for this tradition only goes into its own colors.csv; one for every church into data/colors.csv.')];
  const scope = el('select', {}, el('option', { value: 'own', textContent: 'This tradition (' + t.folder + ')' }), el('option', { value: 'all', textContent: 'Every church' }));
  out.push(el('label', {}, 'Change for ', scope));
  const list = el('div', { class: 'group palette' });
  const p = DATA.profiles[key];
  const rowIn = (path, name) => {
    const t2 = tableAt(DATA, path);
    const rows = t2 ? tableRows(t2, t2.get()) : [];
    return rows.find(r => String(r.name || '').trim().toUpperCase() === name);
  };
  const save = (name, fill, text) => {
    const path = scope.value === 'own' ? own : 'colors.csv';
    if (!layoutOf(DATA, path)) { editStatus.textContent = 'This page cannot write data/' + path + '.'; return; }
    const r = rowIn(path, name);
    if (r) editSet(rowPlace(r) || { path: path, key: tableRows(tableAt(DATA, path), tableAt(DATA, path).get()).indexOf(r), row: r },
                   Object.assign({}, r, { fill: fill, text: text }));
    else editAdd(path, { name: name, fill: fill, text: text }, null);
    editsChanged('Saved.');
  };
  for (const name of Object.keys(p.colors)) {
    const c = p.colors[name];
    const fill = el('input', { type: 'color', value: /^#[0-9a-f]{6}$/i.test(c.fill) ? c.fill : '#ffffff', title: 'fill' });
    const text = el('input', { type: 'color', value: /^#[0-9a-f]{6}$/i.test(c.text) ? c.text : '#000000', title: 'text' });
    const where = rowIn(own, name) ? t.folder : 'every church';
    fill.addEventListener('change', () => save(name, fill.value, text.value));
    text.addEventListener('change', () => save(name, fill.value, text.value));
    list.append(el('div', { class: 'row swatchrow' }, el('span', { class: 'chip', style: 'background:' + c.fill + ';color:' + c.text }, name), fill, text, el('span', { class: 'text small' }, where)));
  }
  out.push(list);
  const [ln, n] = field('Name', '', 'a word in capitals: ROSE');
  const fill = el('input', { type: 'color', value: '#c06080' });
  const text = el('input', { type: 'color', value: '#ffffff' });
  const add = el('button', { type: 'button', textContent: 'Add' });
  add.addEventListener('click', () => {
    const name = n.value.trim().toUpperCase().replace(/[^A-Z0-9_]+/g, '_');
    if (name) save(name, fill.value, text.value);
  });
  out.push(el('details', { class: 'add' }, el('summary', {}, 'Add a color'), ln, el('label', {}, 'Fill ', fill), el('label', {}, 'Text ', text), el('div', { class: 'row' }, add)));
  return out;
}

/** The files the changes make, and those a page made from this one carries changed. */
function changedFiles() {
  const out = new Set(Array.isArray(DATA.edited) ? DATA.edited : []);
  for (const e of EDITS) out.add(e.p);
  return Array.from(out).filter(p => tableAt(DATA, p) && layoutOf(DATA, p)).sort();
}

function editChangesView() {
  const out = [];
  if (EDITS_SET_ASIDE) out.push(el('p', { class: 'text' }, EDITS_SET_ASIDE + ' change(s) kept for an earlier form of this page were set aside: the page has changed since.'));
  if (Array.isArray(DATA.edited) && DATA.edited.length) {
    out.push(el('p', { class: 'text' }, 'This page was made with changes to: ' + DATA.edited.map(p => 'data/' + p).join(', ') + '. They are part of it, and Download changed files includes these files.'));
  }
  if (!EDITS.length) { out.push(el('p', { class: 'text' }, 'No changes on this page yet.')); return out; }
  const files = {};
  for (const e of EDITS) files[e.p] = (files[e.p] || 0) + 1;
  const list = el('ul', { class: 'files' });
  for (const p of Object.keys(files).sort()) {
    const undo = el('button', { type: 'button', textContent: 'Undo these' });
    undo.addEventListener('click', () => { EDITS = EDITS.filter(e => e.p !== p); editsChanged('Undone.'); });
    list.append(el('li', {}, 'data/' + p + ': ' + files[p] + ' change' + (files[p] === 1 ? '' : 's') + ' ', undo));
  }
  const last = el('button', { type: 'button', textContent: 'Undo the last change' });
  last.addEventListener('click', () => { EDITS.pop(); editsChanged('Undone.'); });
  const all = el('button', { type: 'button', textContent: 'Undo every change' });
  all.addEventListener('click', () => { EDITS = []; editsChanged('Every change undone.'); });
  out.push(list, el('div', { class: 'row' }, last, all),
           el('p', { class: 'text small' }, 'Kept in this browser for this page. Make a page writes them into the page it makes.'));
  return out;
}

/** A file written again from the page's tables (csvText). */
function fileText(p) {
  const t = tableAt(DATA, p), lay = layoutOf(DATA, p);
  const base = tableRows(t, EDIT_ORIG[p] !== undefined ? EDIT_ORIG[p] : t.get());
  const nodes = EDIT_NODES[p] || base.map((r, i) => ({ key: i, orig: i, row: r, del: false }));
  return csvText(lay, nodes, base);
}
/** Every changed file, written again. */
const changedFileTexts = () => changedFiles().map(p => ({ path: p, text: fileText(p) }));

$('editExport').addEventListener('click', async () => {
  const files = changedFileTexts().map(f => ({ name: 'data/' + f.path, blob: new Blob([f.text], { type: 'text/csv' }) }));
  if (!files.length) return;
  files.push({ name: 'README.txt', blob: new Blob([
    'The data files changed on the church year page (' + new Date().toISOString().slice(0, 10) + ').\n\n'
    + 'Put the data folder from this zip over the project\'s own (each file replaces the one of the same name),\n'
    + 'then run church_year_image.py, the listing scripts or church_year.py as usual: they read the changes.\n\n'
    + files.map(f => '  ' + f.name).join('\n') + '\n'], { type: 'text/plain' }) });
  saveBlob(await makeZip(files), 'church-year-data-changes.zip');
  editStatus.textContent = 'Downloaded ' + (files.length - 1) + ' file' + (files.length === 2 ? '' : 's') + '.';
});
for (const b of editTabs) b.addEventListener('click', () => { editTab = b.dataset.tab; editStatus.textContent = ''; editShow(); });
$('editBtn').addEventListener('click', () => {
  editStatus.textContent = '';
  editShow();
  if (editDialog.showModal) editDialog.showModal(); else editDialog.setAttribute('open', '');
});
$('editBtn').hidden = !!DATA.noEdit;
// For web/verify_edits.py: every file the page can write, and changes made from outside.
app.cyEdits = {
  paths: () => Object.keys(DATA.csv || {}),
  file: fileText,
  changed: () => changedFileTexts(),
  set: list => {
    EDITS = list.map(e => (e.row ? Object.assign({}, e, { row: tidyRow(e.row, (layoutOf(DATA, e.p) || { cols: [] }).cols) }) : e));
    editsChanged();
  },
};

// ---- church_year.py's main(), over this page's tables -------------------

/** Keep only these churches, their folders, artwork and shared lectionaries (select_churches). */
function selectChurches(data, keys) {
  const keep = new Set(keys);
  const out = Object.assign({}, data);
  out.traditions = data.traditions.filter(t => keep.has(t.key));
  out.profiles = {};
  for (const k of Object.keys(data.profiles)) if (keep.has(k)) out.profiles[k] = data.profiles[k];
  const folders = new Set(out.traditions.map(t => t.folder));
  out.folders = {};
  for (const k of Object.keys(data.folders)) if (folders.has(k)) out.folders[k] = data.folders[k];
  const arts = new Set(Object.values(out.profiles).map(p => p.art).filter(Boolean));
  for (const k of Object.keys(data.artwork)) if (data.artwork[k].own) arts.add(k);
  // The seasons' pictures these churches show with Artwork: By season.
  for (const r of data.seasonArt || []) if (r.art && (!r.church || keep.has(r.church))) arts.add(r.art);
  out.artwork = {};
  for (const k of Object.keys(data.artwork)) if (arts.has(k)) out.artwork[k] = data.artwork[k];
  out.artworkOrder = data.artworkOrder.filter(k => arts.has(k));
  if (!arts.has(out.defaultArt) && out.defaultArt !== 'auto' && out.defaultArt !== 'season' && out.defaultArt !== '') {
    out.defaultArt = out.artworkOrder[0] || '';
  }
  const variants = new Set(out.traditions.map(t => t.variant || ''));
  const names = new Set(words((data.settings || {}).readings));
  for (const f of folders) {
    for (const s of data.folders[f].settings || []) {
      if (s.setting !== 'readings') continue;
      const v = words(s.variant);
      if (!v.length || v.some(x => variants.has(x))) for (const n of words(s.value)) names.add(n);
    }
  }
  out.sharedReadings = {};
  for (const k of Object.keys(data.sharedReadings || {})) if (names.has(k)) out.sharedReadings[k] = data.sharedReadings[k];
  out.csv = CY.keptLayouts(data, out);
  if (!keep.has(data.defaultTradition)) out.defaultTradition = out.traditions[0].key;
  return out;
}

/** Open on this artwork (export_data.py: use_artwork). */
function useArtwork(data, key) {
  data.defaultArt = key;
  data.configRaw = Object.assign({}, data.configRaw || {}, { center_svg: key });
}

/** Python's '%g'. */
function fmtG(x) {
  let s = Number(x).toPrecision(6);
  if (/e/.test(s)) {
    let [m, e] = s.split('e'); if (m.indexOf('.') >= 0) m = m.replace(/0+$/, '').replace(/\.$/, '');
    const n = parseInt(e, 10); return m + 'e' + (n < 0 ? '-' : '+') + String(Math.abs(n)).padStart(2, '0');
  }
  if (s.indexOf('.') >= 0) s = s.replace(/0+$/, '').replace(/\.$/, '');
  return s;
}
/** Python's repr of a float. */
const pyFloat = x => (Number.isInteger(x) ? x.toFixed(1) : String(x));

/** A raster picture's size from its header (church_year_image.py: raster_size). */
function rasterSize(b) {
  const u16be = i => (b[i] << 8) | b[i + 1], u16le = i => b[i] | (b[i + 1] << 8);
  const u32be = i => ((b[i] << 24) >>> 0) + (b[i + 1] << 16) + (b[i + 2] << 8) + b[i + 3];
  const u24le = i => b[i] | (b[i + 1] << 8) | (b[i + 2] << 16);
  const head = (n, i = 0) => String.fromCharCode(...b.slice(i, i + n));
  if (head(8) === '\x89PNG\r\n\x1a\n') return [u32be(16), u32be(20)];
  if (head(6) === 'GIF87a' || head(6) === 'GIF89a') return [u16le(6), u16le(8)];
  if (head(4) === 'RIFF' && head(4, 8) === 'WEBP') {
    const kind = head(4, 12);
    if (kind === 'VP8 ') return [u16le(26) & 0x3FFF, u16le(28) & 0x3FFF];
    if (kind === 'VP8L') { const bits = (b[21] | (b[22] << 8) | (b[23] << 16) | (b[24] << 24)) >>> 0; return [(bits & 0x3FFF) + 1, ((bits >>> 14) & 0x3FFF) + 1]; }
    if (kind === 'VP8X') return [u24le(24) + 1, u24le(27) + 1];
  }
  if (b[0] === 0xFF && b[1] === 0xD8) {
    let i = 2;
    while (i + 9 < b.length) {
      if (b[i] !== 0xFF) { i++; continue; }
      const m = b[i + 1];
      if (m === 0xD8 || m === 0x01 || (m >= 0xD0 && m <= 0xD7) || m === 0xFF) { i += m === 0xFF ? 1 : 2; continue; }
      const len = u16be(i + 2);
      if (m >= 0xC0 && m <= 0xCF && m !== 0xC4 && m !== 0xC8 && m !== 0xCC) return [u16be(i + 7), u16be(i + 5)];
      i += 2 + len;
    }
  }
  return [0, 0];
}

const SVG_NS = 'http://www.w3.org/2000/svg', XLINK_NS = 'http://www.w3.org/1999/xlink';
const ET_PREFIXES = { [SVG_NS]: '', [XLINK_NS]: 'xlink', 'http://www.w3.org/XML/1998/namespace': 'xml',
  'http://www.w3.org/1999/xhtml': 'html', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf',
  'http://schemas.xmlsoap.org/wsdl/': 'wsdl', 'http://www.w3.org/2001/XMLSchema': 'xs',
  'http://www.w3.org/2001/XMLSchema-instance': 'xsi', 'http://purl.org/dc/elements/1.1/': 'dc' };
const etText = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const etAttr = s => etText(s).replace(/"/g, '&quot;').replace(/\r/g, '&#13;').replace(/\n/g, '&#10;').replace(/\t/g, '&#09;');
const isText = n => n.nodeType === 3 || n.nodeType === 4;
const ownAttrs = el => Array.from(el.attributes).filter(a => a.namespaceURI !== 'http://www.w3.org/2000/xmlns/');
/** Text up to the next element, as ElementTree keeps it (comments dropped). */
function textRun(node) {
  let s = '';
  for (let n = node; n && n.nodeType !== 1; n = n.nextSibling) if (isText(n)) s += n.data;
  return s;
}
/** One element as Python's ElementTree.tostring writes it, with church_year_image.py's namespaces. */
function etToString(el) {
  const qnames = new Map(), ns = new Map();
  const qn = (uri, local) => {
    const key = (uri || '') + '}' + local;
    if (qnames.has(key)) return;
    if (!uri) { qnames.set(key, local); return; }
    let p = ns.get(uri);
    if (p === undefined) {
      p = uri in ET_PREFIXES ? ET_PREFIXES[uri] : 'ns' + ns.size;
      if (p !== 'xml') ns.set(uri, p);
    }
    qnames.set(key, p ? p + ':' + local : local);
  };
  const walk = e => { qn(e.namespaceURI, e.localName); for (const a of ownAttrs(e)) qn(a.namespaceURI, a.localName);
    for (const c of e.children) walk(c); };
  walk(el);
  const name = (uri, local) => qnames.get((uri || '') + '}' + local);
  const out = [];
  const ser = (e, top) => {
    const tag = name(e.namespaceURI, e.localName);
    out.push('<' + tag);
    if (top) for (const [uri, p] of [...ns.entries()].sort((x, y) => (x[1] < y[1] ? -1 : x[1] > y[1] ? 1 : 0))) {
      out.push(' xmlns' + (p ? ':' + p : '') + '="' + etAttr(uri) + '"');
    }
    for (const a of ownAttrs(e)) out.push(' ' + name(a.namespaceURI, a.localName) + '="' + etAttr(a.value) + '"');
    const text = textRun(e.firstChild);
    if (text || e.children.length) {
      out.push('>');
      if (text) out.push(etText(text));
      for (const c of e.children) ser(c, false);
      out.push('</' + tag + '>');
    } else out.push(' />');
    const tail = textRun(e.nextSibling);
    if (tail) out.push(etText(tail));
  };
  ser(el, true);
  return out.join('');
}
function base64(bytes) {
  let s = '';
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(s);
}
const RASTER_TYPES = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp' };

/** A picture's credit, license, size and whether its credit must be shown (export_data.py: own_artwork). */
function ownFieldsOn(entry, name, art) {
  const scale = (() => { const v = parseFloat(art.scale || '1'); return art.scale && !isFinite(Number(art.scale)) ? 1 : (v > 0 && isFinite(v) ? v : 1); })();
  const credit = (art.credit || '').trim(), author = (art.author || '').trim(), license = (art.license || '').trim();
  const credited = !!(credit || author || license);
  return Object.assign(entry, { label: name, title: credit, author: author, license: license,
    licenseUrl: (art.licenseUrl || '').trim(), sourceUrl: (art.source || '').trim(), changes: '',
    attribution: credited && (art.attribution || 'required') === 'required' ? 'required' : '',
    scale: scale === 1 ? '' : pyFloat(scale), own: true });
}

/** --own-art as the command writes it: FILE|churches=...|credit=...|... (church_year.py: own_art_spec). */
function ownSpec(a) {
  const parts = [a.name];
  if (a.churches.length) parts.push('churches=' + a.churches.join(','));
  for (const k of OWN_FIELDS) {
    const v = String(a.fields[k] || '').trim();
    if (v) parts.push(OWN_SPEC[k] + '=' + v);
  }
  return parts.join('|');
}
/** The file, fields and churches an --own-art names. */
function parseOwnSpec(spec) {
  const parts = String(spec).split('|').map(p => p.trim());
  const name = parts[0], fields = {}, back = {};
  for (const k of OWN_FIELDS) back[OWN_SPEC[k]] = k;
  let churches = [];
  for (const part of parts.slice(1)) {
    if (!part) continue;
    const eq = part.indexOf('=');
    const k = (eq > 0 ? part.slice(0, eq) : part).trim().toLowerCase(), v = eq > 0 ? part.slice(eq + 1).trim() : '';
    if (eq < 0 || (k !== 'churches' && !back[k])) throw new Error('--own-art ' + name + ": '" + part + "' is not one of churches=, " + OWN_FIELDS.map(f => OWN_SPEC[f] + '=').join(', '));
    if (k === 'churches') churches = words(v.toLowerCase()); else fields[back[k]] = v;
  }
  if (!name) throw new Error('--own-art needs a picture file');
  if (fields.attribution && !/^(required|optional)$/i.test(fields.attribution)) throw new Error('--own-art ' + name + ': attribution is required or optional');
  if (fields.attribution && /^required$/i.test(fields.attribution)) fields.attribution = '';
  return { name: name, fields: fields, churches: churches };
}

/** A picture of your own as the page carries it (export_data.py: own_artwork). */
function ownArtwork(art) {
  const name = art.name.split(/[\\/]/).pop();
  const ext = (/\.[^.]*$/.exec(name) || [''])[0].toLowerCase();
  if (ext !== '.svg' && !RASTER_TYPES[ext]) throw new Error(name + ' is not a picture file (.svg, .png, .jpg, .jpeg, .gif, .webp)');
  let entry;
  if (RASTER_TYPES[ext]) {
    const [w, h] = rasterSize(art.data);
    if (!(w && h)) throw new Error(name + ' could not be read: it has no size');
    const uri = 'data:' + RASTER_TYPES[ext] + ';base64,' + base64(art.data);
    entry = { x: 0, y: 0, w: w, h: h, body: '<clipPath id="cy-own-art-clip"><circle cx="' + fmtG(w / 2) + '" cy="' + fmtG(h / 2)
      + '" r="' + fmtG(Math.max(w, h) / 2) + '" /></clipPath><image x="0" y="0" width="' + w + '" height="' + h
      + '" clip-path="url(#cy-own-art-clip)" xlink:href="' + uri + '" />' };
  } else {
    const doc = new DOMParser().parseFromString(new TextDecoder().decode(art.data), 'image/svg+xml');
    if (doc.getElementsByTagName('parsererror').length) throw new Error(name + ' could not be read as SVG');
    const root = doc.documentElement;
    const box = root.getAttribute('viewBox');
    let x = 0, y = 0, w, h;
    if (box) {
      const v = box.replace(/,/g, ' ').trim().split(/\s+/).map(Number);
      if (v.length !== 4 || v.some(n => isNaN(n))) throw new Error(name + ' has a viewBox that is not four numbers');
      [x, y, w, h] = v;
    } else {
      const num = (value, fallback) => { const d = String(value || '').replace(/[^\d.]/g, ''); return d ? parseFloat(d) : fallback; };
      w = num(root.getAttribute('width') || '100', 100); h = num(root.getAttribute('height') || '100', 100);
    }
    entry = { x, y, w, h, body: Array.from(root.children).map(c => etToString(c)).join('') };
  }
  ownFieldsOn(entry, name, art);
  return ['file:' + name.toLowerCase(), entry];
}

/** The new page's tables: church_year.py's main() over this page's own. */
function buildPage(o) {
  let d = pristineData();
  // The changes made on this page (Edit the data...), written into the new one.
  if (EDITS.length) bakeEdits(d, EDITS);
  // What the script reads from data.json rather than from an earlier page.
  for (const k of ['latinDefault', 'bibleDefault', 'readingsDefault', 'hiddenDefault', 'colorsDefault',
                   'bibleSite', 'wordToWorship', 'hymnary', 'hymnalDefault', 'readingsLayout', 'feedback', 'help', 'openZoom', 'openOn', 'noDownload', 'noMakePage', 'noEdit', 'arrowsNext', 'localArt', 'links']) delete d[k];
  d.defaultTradition = o.church;
  d.defaultSubcalendars = o.subcalendar.slice();
  d.settings.feast_detail = o.feasts;
  d.settings.mid_text = o.midText;
  if (o.latin !== null) d.latinDefault = o.latin;
  if (o.bibleDefault) d.bibleDefault = o.bibleDefault;
  if (o.churches) d = selectChurches(d, o.churches);
  d.footer = o.footer;
  d.fixed = o.fixed.concat(['calendar', 'easter'].filter(w => o.show.indexOf(w) < 0 && o.fixed.indexOf(w) < 0));
  d.bibles = o.bible.map(w => (/^own$/i.test(w) ? 'own' : BIBLE_VERSIONS.some(v => v[0] === w.toUpperCase()) ? w.toUpperCase() : w.toLowerCase()));
  // The pictures (church_year.py: choose_artwork).  A page made already gives each church
  // its own picture back first, and keeps only the pictures of yours named again.
  const named = new Set(o.ownArt.map(a => ownKey(a.name)));
  for (const p of Object.values(d.profiles)) {
    if (p.churchArt === undefined) continue;
    p.art = p.churchArt;                  // none, below, if the page left it out
    delete p.churchArt;
  }
  for (const k of Object.keys(d.artwork)) {
    if (!d.artwork[k].own || named.has(k)) continue;
    delete d.artwork[k];
    d.artworkOrder = d.artworkOrder.filter(x => x !== k);
  }
  const assigned = new Set();
  for (const a of o.ownArt) {
    let key, entry;
    if (a.data) [key, entry] = ownArtwork(Object.assign({ name: a.name, data: a.data }, a.fields));
    else { key = ownKey(a.name); entry = ownFieldsOn(Object.assign({}, DATA.artwork[key]), a.name, a.fields); }
    d.artwork[key] = entry;
    if (d.artworkOrder.indexOf(key) < 0) d.artworkOrder.push(key);
    for (const c of a.churches) {
      const p = d.profiles[c];
      if (p.churchArt === undefined) p.churchArt = p.art || '';
      p.art = key; assigned.add(c);
    }
  }
  for (const key of o.dropArt) {
    delete d.artwork[key];
    d.artworkOrder = d.artworkOrder.filter(k => k !== key);
    for (const [c, p] of Object.entries(d.profiles)) if (p.art === key && !assigned.has(c)) p.art = 'none';
  }
  for (const [c, p] of Object.entries(d.profiles)) if (p.art && p.art !== 'none' && !d.artwork[p.art] && !assigned.has(c)) p.art = 'none';
  useArtwork(d, /\.(svg|png|jpe?g|gif|webp)$/i.test(o.art) ? ownKey(o.art) : o.art.toLowerCase());
  if (o.year !== null) d.openOn = o.year;
  if (o.readings !== 'all') {
    d.readingsDefault = o.readings === 'none' ? [] : o.readings.split(',');
    // Only those sets come along (church_year.py: prune_readings).
    d = CY.pruneReadings(d, d.readingsDefault);
  }
  if (o.hide.length) d.hiddenDefault = o.hide.slice();
  if (o.colors) {
    for (const item of o.colors.split(',')) {
      const i = item.lastIndexOf('-');
      if (i <= 0 || !/^([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$/.test(item.slice(i + 1))) {
        throw new Error("colors changed: '" + item + "' is not NAME-rrggbb (PURPLE-7a1f7a, ring.halves-e6c3f7)");
      }
      const scope = item.slice(0, i).split(':');
      if (scope.length > 1 && !d.traditions.some(t => tradSlug(t.tradition) === tradSlug(scope[0]))) {
        throw new Error("colors changed: '" + item + "' names no tradition on the page");
      }
      if (scope.length > 2 && !d.traditions.some(t => t.key === scope[1].trim().toLowerCase() && tradSlug(t.tradition) === tradSlug(scope[0]))) {
        throw new Error("colors changed: '" + item + "' names no " + scope[0] + " church on the page");
      }
    }
    d.colorsDefault = o.colors;
  }
  const site = o.bibleSite || rawText('page_bible_site').toLowerCase();
  if (site) d.bibleSite = site;
  if (o.w2w !== 'on') d.wordToWorship = o.w2w;
  if (o.hymns !== 'on') d.hymnary = o.hymns;
  if (o.hymnal) d.hymnalDefault = o.hymnal;
  d.settings.year_line = o.yearLine;
  if (o.layout !== 'tabs,columns') d.readingsLayout = o.layout.split(',');
  if (o.feedback && !/^none$/i.test(o.feedback)) {
    if (!/^(https?:|mailto:)/i.test(o.feedback)) throw new Error('the feedback link must start with https:// (or mailto:)');
    d.feedback = o.feedback;
  }
  if (o.help && !/^none$/i.test(o.help)) {
    if (!/^https?:/i.test(o.help)) throw new Error('the help link must start with https://');
    d.help = o.help;
  }
  if (o.links !== 'all') d.links = { bible: ['bible'], feasts: ['feasts'], none: [] }[o.links];
  if (!o.download) d.noDownload = true;
  if (!o.makePage) d.noMakePage = true;
  if (!o.edit) d.noEdit = true;
  if (o.arrows) d.arrowsNext = true;
  if (o.localArt) d.localArt = true;
  if (o.zoom !== 1) d.openZoom = o.zoom;
  return d;
}

/** The new page's HTML, as church_year.py writes it (build): its tables packed unless asked not to be (--no-compress). */
async function pageHtml(d, fragment, compress) {
  const i = PRISTINE.app.indexOf(DATA_HEAD) + DATA_HEAD.length;
  const j = PRISTINE.app.indexOf(';<\/script>', i);
  const tables = compress ? '"' + await packTables(JSON.stringify(d)) + '"' : JSON.stringify(d).replace(/<\//g, '<\\/');
  const app = PRISTINE.app.slice(0, i) + tables + PRISTINE.app.slice(j);
  const body = PRISTINE.style + '\n\n' + app + '\n';
  if (fragment) return '<title>Church Year Wheel</title>\n' + body;
  return '<!doctype html>\n<html lang="en" class="cy-page">\n<head>\n<meta charset="utf-8">\n'
    + '<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Church Year Wheel</title>\n'
    + '</head>\n<body>\n' + body + '</body>\n</html>\n';
}

$('pageMake').addEventListener('click', async () => {
  try {
    const o = pageOptions();
    const d = buildPage(o);
    const html = await pageHtml(d, o.fragment, o.compress);
    saveBlob(new Blob([html], { type: 'text/html;charset=utf-8' }), o.out);
    const n = d.traditions.length;
    pageStatus.textContent = 'Saved ' + o.out + ' (' + (new Blob([html]).size / 1048576).toFixed(1) + ' MB, '
      + n + (n === 1 ? ' church).' : ' churches).');
  } catch (e) {
    pageStatus.textContent = 'Could not make the page: ' + (e && e.message || e);
  }
});

}

})();
