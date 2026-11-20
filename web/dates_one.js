/*
 * Dump the browser's date arithmetic for a span of years, for verify_bc.py.
 * Not part of the page.
 *
 *   node web/dates_one.js <fromYear> <toYear> [data.json]
 */
const fs = require('fs');
const path = require('path');
const CY = require(path.join(__dirname, 'church_year.js')).ChurchYear;
const [from, to] = process.argv.slice(2, 4).map(Number);
const data = JSON.parse(fs.readFileSync(process.argv[4] || path.join(__dirname, 'data.json'), 'utf8'));
const source = new CY.Source(data, CY.findTradition(data, 'lcms-three-year'), []);
const out = [];
for (let y = from; y <= to; y++) {
  const year = new CY.Year(source, y, 'gregorian', '', false);
  const at = id => year.ctx.ref(id);
  out.push([y, CY.iso(year.start), CY.iso(year.end), CY.iso(year.easter),
            CY.iso(at('ash_wednesday')), CY.iso(at('pentecost')), CY.iso(at('reformation')),
            CY.iso(at('thanksgiving')), CY.iso(at('all_saints')),
            year.end - year.start + 1].join(','));
}
process.stdout.write(out.join('\n') + '\n');
