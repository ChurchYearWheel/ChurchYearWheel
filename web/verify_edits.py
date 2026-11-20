#!/usr/bin/env python3
"""Check Edit the data... (web/page.js) against the scripts.

1. Every data file the page can write comes back byte for byte when nothing
   has changed (page.js: csvText against lib/csvlayout.py's layouts).
2. Changes of every sort (a feast renamed, removed and added; readings
   changed, removed and added in a shared lectionary and in a folder's own new
   readings.csv; a new kind with its name; the order of the kinds; a season's
   color; a color of every church's and one of a tradition's own, in a new
   colors.csv; a period's color) are made on the page, and the files it
   downloads are laid over a copy of data/.  The page Make a page then makes
   must be the page church_year.py makes from that copy, table for table
   and element for element, and made again it must not change.

Needs Node and Playwright, as web/verify_pages.py does.

    python3 web/verify_edits.py
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "lib"))
import export_data as E  # noqa: E402

SCRIPT = r"""
const { chromium } = require('playwright');
const fs = require('fs');
const [src, dir, editsJson] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ acceptDownloads: true });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + src + '#lectionary=lcms-three-year&date=2025-11-30'); await p.waitForTimeout(800);
  const files = await p.evaluate(() => {
    const ed = document.querySelector('.cy-app').cyEdits;
    const out = {}; for (const path of ed.paths()) out[path] = ed.file(path); return out;
  });
  fs.writeFileSync(dir + '/asis.json', JSON.stringify(files));
  const changed = await p.evaluate(edits => {
    const ed = document.querySelector('.cy-app').cyEdits; ed.set(edits); return ed.changed();
  }, JSON.parse(editsJson));
  fs.writeFileSync(dir + '/changed.json', JSON.stringify(changed));
  // Make a page, as it opens.
  const make = async (page, file) => {
    await page.evaluate(() => { document.querySelector('details').open = true; document.querySelector('#pageBtn').click(); });
    await page.evaluate(() => document.querySelector('#pageOwn').click());
    const [d] = await Promise.all([page.waitForEvent('download', { timeout: 120000 }), page.click('#pageMake')]);
    await d.saveAs(file);
  };
  await make(p, dir + '/made.html');
  const q = await ctx.newPage(); q.on('pageerror', e => errs.push(e.message));
  await q.goto('file://' + dir + '/made.html'); await q.waitForTimeout(800);
  await make(q, dir + '/again.html');
  await b.close();
  if (errs.length) { console.error(errs.join('\n')); process.exit(2); }
})().catch(e => { console.error(e); process.exit(2); });
"""

READ = r"""
const { chromium } = require('playwright');
const [a, b] = process.argv.slice(2);
(async () => {
  const br = await chromium.launch(); const ctx = await br.newContext({ javaScriptEnabled: false });
  const out = [];
  for (const f of [a, b]) {
    const p = await ctx.newPage(); await p.goto('file://' + f);
    out.push(await p.evaluate(() => {
      const s = Array.from(document.scripts).find(x => x.textContent.startsWith('window.CHURCH_YEAR_DATA = '));
      const t = s.textContent; const data = JSON.parse(t.slice(26, t.lastIndexOf(';')));
      // Packed tables (gzip, base64) are unpacked below, outside the page.
      s.textContent = '';
      return { data, html: document.documentElement.outerHTML };
    }));
    const last = out[out.length - 1];
    if (typeof last.data === 'string') last.data = JSON.parse(require('zlib').gunzipSync(Buffer.from(last.data, 'base64')).toString('utf8'));
  }
  console.log(JSON.stringify(out));
  await br.close();
})();
"""


def index_of(rows: list, **match) -> int:
    for i, r in enumerate(rows):
        if all(r.get(k, "") == v for k, v in match.items()):
            return i
    raise SystemExit(f"✗ no row {match}")


def edits() -> list:
    data = ROOT / "data"
    feasts = E.T.read_rows(data / "LCMS/LSB/feasts.csv")
    lsb = E.reading_rows(data / "readings/lsb.csv")
    periods = E.T.read_rows(data / "LCMS/LSB/periods.csv")
    seasons = E.T.read_rows(data / "LCMS/LSB/seasons.csv")
    colors = E.T.read_rows(data / "colors.csv")
    andrew = index_of(feasts, date="11-30")
    verse = index_of(lsb, day="advent:1", cycle="A", kind="verse")
    gradual = index_of(lsb, day="advent:2", cycle="A", kind="gradual")
    advent = index_of(seasons, season="ADVENT")
    blue = index_of(colors, name="BLUE")
    lent = index_of(periods, name="Lent") if any(r.get("name") == "Lent" for r in periods) else 0
    return [
        {"p": "LCMS/LSB/feasts.csv", "op": "set", "i": andrew,
         "row": dict(E.compact([feasts[andrew]])[0], name="St. Andrew the Apostle", color_override="RED")},
        {"p": "LCMS/LSB/feasts.csv", "op": "del", "i": andrew + 1},
        {"p": "LCMS/LSB/feasts.csv", "op": "add", "id": "n1", "after": andrew,
         "row": {"date": "12-01", "name": "A Test Day, \"quoted\"", "color_override_bottom": "GREEN", "variant": "three-year"}},
        {"p": "readings/lsb.csv", "op": "set", "i": verse, "row": dict(E.compact([lsb[verse]])[0], reading="Psalm 24:7–8")},
        {"p": "readings/lsb.csv", "op": "add", "id": "n2", "after": verse,
         "row": {"day": "advent:1", "cycle": "A", "variant": "three-year", "kind": "tract", "reading": "Psalm 25:1–3"}},
        {"p": "readings/lsb.csv", "op": "del", "i": gradual},
        {"p": "LCMS/LSB/tradition.csv", "op": "add", "id": "n3", "after": None,
         "row": {"setting": "reading_labels", "value": "tract=Tract", "variant": "three-year"}},
        {"p": "LCMS/LSB/tradition.csv", "op": "add", "id": "n4", "after": "n3",
         "row": {"setting": "reading_order", "value": "tract | introit | ot | psalm | epistle | gradual | verse | gospel",
                 "variant": "three-year"}},
        {"p": "LCMS/LSB/seasons.csv", "op": "set", "i": advent, "row": {"season": "ADVENT", "color": "PURPLE; blue"}},
        {"p": "colors.csv", "op": "set", "i": blue, "row": dict(E.compact([colors[blue]])[0], fill="#123456")},
        {"p": "LCMS/LSB/colors.csv", "op": "add", "id": "n5", "after": None,
         "row": {"name": "ROSE", "fill": "#c06080", "text": "#ffffff"}},
        {"p": "LCMS/LSB/colors.csv", "op": "add", "id": "n6", "after": "n5",
         "row": {"name": "GREEN", "fill": "#2e7d32", "text": "#ffffff"}},
        {"p": "LCMS/LSB/periods.csv", "op": "set", "i": lent, "row": dict(E.compact([periods[lent]])[0], color="BLACK")},
        {"p": "LCMS/LSB/readings.csv", "op": "add", "id": "n7", "after": None,
         "row": {"day": "12-03", "variant": "three-year", "title": "A Test Set", "kind": "ot", "reading": "Isaiah 40:1–11"}},
    ]


def diff(a, b, path, out):
    if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True):
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            diff(a.get(k), b.get(k), path + "." + k, out)
    else:
        out.append(f"{path}: {json.dumps(a)[:150]}  vs  {json.dumps(b)[:150]}")


def main() -> int:
    page = ROOT / "church_year.html"
    subprocess.run([sys.executable, str(ROOT / "church_year.py")], check=True, capture_output=True)
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "check.js").write_text(SCRIPT)
        (tmp / "read.js").write_text(READ)
        run = subprocess.run(["node", str(tmp / "check.js"), str(page), str(tmp), json.dumps(edits())],
                             capture_output=True, text=True, cwd=ROOT)
        if run.returncode:
            print(run.stdout, run.stderr)
            print("✗ the page could not make its changes")
            return 1
        asis = json.loads((tmp / "asis.json").read_text())
        same = [p for p, text in asis.items() if (ROOT / "data" / p).read_text(encoding="utf-8") == text]
        print(f"{'ok  ' if len(same) == len(asis) else 'DIFF'} {len(same)} of {len(asis)} files written back unchanged")
        for p in sorted(set(asis) - set(same))[:8]:
            print("       data/" + p)
        bad += len(same) != len(asis)
        # The files the page downloads, over a copy of data/.
        data = tmp / "data"
        shutil.copytree(ROOT / "data", data)
        changed = json.loads((tmp / "changed.json").read_text())
        for f in changed:
            (data / f["path"]).write_text(f["text"], encoding="utf-8")
        print(f"     {len(changed)} files changed: " + ", ".join(f["path"] for f in changed))
        ref = tmp / "ref.html"
        made = subprocess.run([sys.executable, str(ROOT / "church_year.py"), "--data", str(data), "-o", str(ref)],
                              capture_output=True, text=True, cwd=ROOT)
        if made.returncode:
            print(made.stderr)
            print("✗ church_year.py could not read the changed files")
            return 1
        for name, a, b in (("made", "made.html", "ref.html"), ("made again", "again.html", "made.html")):
            read = subprocess.run(["node", str(tmp / "read.js"), str(tmp / a), str(tmp / b)],
                                  capture_output=True, text=True, cwd=ROOT)
            A, B = json.loads(read.stdout)
            for d in (A["data"], B["data"]):
                d.pop("edited", None)
            out = []
            diff(A["data"], B["data"], "DATA", out)
            markup = A["html"] == B["html"]
            print(("ok   " if not out and markup else "DIFF ") + name + ("" if markup else ": markup differs"))
            for line in out[:10]:
                print("       " + line)
            bad += bool(out) or not markup
    print("all the same" if not bad else "✗ some differ")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
