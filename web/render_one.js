/*
 * Draw one church year with the browser renderer and write the SVG.
 * Used by verify.py; not part of the page.
 *
 *   node web/render_one.js <year> <tradition> <latin:0|1> <out.svg> \
 *                           [data.json] [calendar] [paschalion] [feasts] [subcalendars]
 *
 * `subcalendars` is a comma-separated list of keys from the tradition's
 * subcalendars.csv.  With --serve it reads the tables once and draws a year
 * for each request on stdin (verify.py's way).
 */
const fs = require('fs');
const path = require('path');

const here = __dirname;
const ChurchYear = require(path.join(here, 'church_year.js')).ChurchYear;
const args = process.argv.slice(2);

/** One year's drawing, as verify.py asks for it. */
const render = (data, q) => ChurchYear.renderDocument(data, {
  year: q.year,
  tradition: q.tradition,
  latinNames: !!q.latin,
  calendar: q.calendar || 'gregorian',
  paschalion: q.paschalion || '',
  feastDetail: q.feasts || 'all',
  subcalendars: q.subcalendars || [],
  // verify.py --color-changes: the page's Colors menu, for this church.
  colorOverrides: q.colorOverrides || undefined,
  // verify.py --art-date: the middle holds that day's season's picture.
  artDate: q.artDate || undefined,
});

if (args[0] === '--serve') {
  // node web/render_one.js --serve [data.json]: one request a line on stdin
  // ({"year": 2025, "tradition": "...", ...}), one answer a line on stdout
  // ({"svg": "..."} or {"error": "..."}), the tables read once.
  const data = JSON.parse(fs.readFileSync(args[1] || path.join(here, 'data.json'), 'utf8'));
  const lines = require('readline').createInterface({ input: process.stdin });
  lines.on('line', line => {
    let answer;
    try { answer = { svg: render(data, JSON.parse(line)) }; } catch (err) { answer = { error: String(err && err.stack || err) }; }
    process.stdout.write(JSON.stringify(answer) + '\n');
  });
} else {
  const data = JSON.parse(fs.readFileSync(args[4] || path.join(here, 'data.json'), 'utf8'));
  fs.writeFileSync(args[3], render(data, {
    year: parseInt(args[0], 10), tradition: args[1], latin: args[2] === '1',
    calendar: args[5], paschalion: args[6], feasts: args[7],
    subcalendars: (args[8] || '').split(',').filter(Boolean),
  }), 'utf8');
}
