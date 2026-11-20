#!/usr/bin/env python3
"""
Check that the page's Make a page writes the page church_year.py writes
with the same options: the same tables (window.CHURCH_YEAR_DATA, compared as
data) and the same markup (compared as the browser reads it, with scripts off).

    python web/verify_pages.py

Each case opens church_year.html at a link, sets the Make a page window,
saves the page it makes, and runs the command line the window shows ("The
same page from Python"), so the window's options, its command line and its
build are all checked together; the command pasted back into a fresh window
must set it to the same command.  A page made from a made page is checked too,
and pictures of your own (an SVG with other namespaces, comments and CDATA;
a PNG) are carried in as --art FILE carries them.

Needs Node.js with Playwright (npm install -g playwright) and a current
church_year.html (python church_year.py).
"""

from __future__ import annotations

import json
import os
import shlex
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# name, link, steps: ["pick", how] presses a Churches button, ["keys", [...]]
# ticks just those churches, ["untick", [...]] clears some, ["file", name]
# chooses a picture of your own, [id, value] sets a box or menu, ["css:SELECTOR", value]
# the box a selector finds (a picture's card).
CASES = [
    ("as-is", "", []),
    # Artwork: By season, with one season's picture left out of the page.
    ("season", "#lectionary=lcms-three-year&date=2026-12-25&art=season", [
        ["pick", "church"], ["pageArtwork", "season"], ["pageArtKeep:season_epiphany", False]]),
    ("wels", "#lectionary=wels-one-year&date=2026-12-01", [
        ["keys", ["wels-one-year", "wels-three-year"]], ["pageChurch", "wels-one-year"],
        ["pageYear", True], ["pageYearNum", "2026"], ["pageZoom", "2.5"], ["pageFeasts", "principal"],
        ["pageLatin", "off"], ["pageReadings:dated", False], ["pageReadings:daily", False],
        ["pageBible", "EHV"], ["pageSite", "youversion"], ["pageW2w", "none"], ["pageRings:halves", False],
        ["pageColors", "PURPLE-7a1f7a,lutheran:WHITE-fffff0,ring.halves-e6c3f7"], ["pageArt", False],
        ["pageBibles", "some"], ["pageBibleList:english", True], ["pageBibleList:LUTH1545", True],
        ["pageFooter", "credit"], ["pageFeedback", "https://example.org/form"], ["pageHelp", "https://example.org/help"], ["pageCompress", False]]),
    ("lutheran", "#lectionary=elca&date=2026-04-05", [
        ["pick", "tradition"], ["untick", ["elca", "lutheran-sweden"]], ["pageCal", True],
        ["pageMid", "dark"], ["pageLatin", "on"], ["pageReadings:day", False], ["pageReadings:feasts", False],
        ["pageReadings:dated", False], ["pageReadings:daily", False], ["pageReadings:office", False],
        ["pageColors", "lutheran:PURPLE-88023c,GREEN-117711,text.months-333333"],
        ["pageBibles", "own"], ["pageW2w", "off"], ["pageFeedback", ""], ["pageHelp", ""], ["pageArtwork", "none"],
        ["pageFragment", True], ["pageName", "lutheran wheel"], ["pageDownload", False], ["pageEdit", False], ["pageLinks", "none"],
        ["pageArrows", True]]),
    ("roman-svg", "#lectionary=roman&sub=united_states&date=2025-12-25", [
        ["pick", "church"], ["pageEaster", True], ["pageReds", False], ["pageMid", "dark-reds"],
        ["file", "Rose Window.svg"], ["css:#pageOwnArts .ownart:nth-child(1) label[title^=\"credit=\"] input", "Drawn by A. Friend & co."],
        ["css:#pageOwnArts .ownart:nth-child(1) label[title^=\"scale=\"] input", "0.8"], ["css:#pageOwnArts .ownart:nth-child(1) label[title^=\"author=\"] input", "A. Friend"],
        ["css:#pageOwnArts .ownart:nth-child(1) label[title^=\"license=\"] input", "CC BY 4.0"],
        ["css:#pageOwnArts .ownart:nth-child(1) label[title^=\"license-url=\"] input", "https://creativecommons.org/licenses/by/4.0/"],
        ["css:#pageOwnArts .ownart:nth-child(1) label[title^=\"source=\"] input", "https://example.org/rose"], ["css:#pageOwnArts .ownart:nth-child(1) .usedby input[value=\"roman\"]", True],
        ["pageMakePage", False], ["pageLinks", "feasts"], ["pageBibles", "some"], ["pageBibleList:NABRE", True], ["pageBibleList:de", True]]),
    ("lcms-png", "#lectionary=lcms-three-year&date=2026-06-01", [
        ["pick", "tradition"], ["file", "seal.png"], ["css:#pageOwnArts .ownart:nth-child(1) label[title^=\"scale=\"] input", "2"],
        ["css:#pageOwnArts .ownart:nth-child(1) label[title^=\"license=\"] input", "\u00a9 2026 St. Mark's, used by permission"], ["css:#pageOwnArts .ownart:nth-child(1) label.check[title^=\"attribution=\"] input", False],
        ["css:#pageOwnArts .ownart:nth-child(1) .usedby input[value=\"lcms-three-year\"]", True], ["css:#pageOwnArts .ownart:nth-child(1) .usedby input[value=\"lcms-one-year\"]", True],
        ["file", "Rose Window.svg"], ["css:#pageOwnArts .ownart:nth-child(2) .usedby input[value=\"wels-one-year\"]", True], ["pageArtKeep:lutherrose", False], ["pageArtwork", "auto"],
        ["pageRings:gold", False], ["pageRings:months", False],
        ["pageReadings:plan", False], ["pageReadings:psalms", False],
        ["pageYearLine", True], ["pageHymns", "off"],
        ["pageColors", "lutheran:lcms-one-year:PURPLE-123456,lutheran:WHITE-fffff0,RED-aa0000"],
        ["pageColorMode", "church"]]),
    ("anglican-hymnal", "#lectionary=anglican-common-worship&date=2026-11-01&hymnal=CAH2000", [
        ["pick", "tradition"], ["pageHymnal", "CPAM2000"], ["pageYearLine", True]]),
    ("own-defaults", "#lectionary=anglican-common-worship&feasts=none&date=2026-01-10", [
        ["pick", "one"], ["pageOwn", "click"], ["pageDownload", False]]),
]

SVG = """<?xml version="1.0" encoding="UTF-8"?>
<!-- a comment ElementTree drops -->
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
     width="200px" height="150px">
  <sodipodi:namedview id="nv" inkscape:zoom="1.5"/>
  <defs><linearGradient id="g"><stop offset="0" stop-color="#c00"/><stop offset="1" stop-color="#fc0"/></linearGradient></defs>
  <g inkscape:label="Layer &amp; one" inkscape:groupmode="layer">
    <!-- inside -->
    <circle cx="100" cy="75" r="60" fill="url(#g)"/>
    <text x="100" y="80" text-anchor="middle" xml:space="preserve">A &lt;b&gt; "q" <![CDATA[x < y]]></text>
    <use xlink:href="#g" title="tab	and
line"/>
  </g>
</svg>
"""


def png(w: int, h: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    rows = b"".join(b"\x00" + bytes([200, 30, 30]) * w for _ in range(h))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


SCRIPT = r"""
const { chromium } = require('playwright');
const fs = require('fs');
const [src, dir, casesJson] = process.argv.slice(2);
const CASES = JSON.parse(casesJson);
const step = process.argv[5];          // 'make' or 'compare'
function canon(v) { if (Array.isArray(v)) return v.map(canon); if (v && typeof v === 'object') { const o = {}; for (const k of Object.keys(v).sort()) o[k] = canon(v[k]); return o; } return v; }
async function make(ctx, url, steps, file) {
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(url); await p.waitForTimeout(800);
  await p.evaluate(() => { document.querySelector('details').open = true; document.querySelector('#pageBtn').click(); });
  for (const [k, v] of steps) {
    if (k === 'file') { await p.setInputFiles('#pageArtFile', dir + '/' + v); await p.waitForTimeout(200); continue; }
    await p.evaluate(([k, v]) => {
      const fire = e => e.dispatchEvent(new Event('change', { bubbles: true }));
      const q = s => document.querySelector(s);
      if (k === 'pick') return q('#pageQuick [data-pick="' + v + '"]').click();
      if (k === 'keys' || k === 'untick') {
        for (const b of document.querySelectorAll('#pageTree label.leaf input')) {
          if (k === 'keys') b.checked = v.indexOf(b.value) >= 0; else if (v.indexOf(b.value) >= 0) b.checked = false;
        }
        return fire(q('#pageTree label.leaf input'));
      }
      const css = k.startsWith('css:') && k.slice(4);
      const [id, sub] = css ? [] : k.split(':');
      const e = css ? q(css) : sub ? q('#' + id + ' input[value="' + sub + '"]') : q('#' + id);
      if (v === 'click') return e.click();
      if (e.type === 'checkbox') e.checked = v; else e.value = v;
      fire(e);
    }, [k, v]);
  }
  const cmd = await p.textContent('#pageCmd');
  const [d] = await Promise.all([p.waitForEvent('download', { timeout: 120000 }), p.click('#pageMake')]);
  await d.saveAs(file); await p.close();
  if (errs.length) throw new Error(errs.join('; '));
  return { cmd, name: d.suggestedFilename() };
}
// The command pasted back into a fresh window sets it to the same command.
async function restore(ctx, url, cmd, steps) {
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(url); await p.waitForTimeout(800);
  await p.evaluate(() => { document.querySelector('details').open = true; document.querySelector('#pageBtn').click(); });
  await p.evaluate(cmd => { document.querySelector('#pageCmdIn').value = cmd; document.querySelector('#pageCmdUse').click(); }, cmd);
  for (const [k, v] of steps) if (k === 'file') { await p.setInputFiles('#pageArtFile', dir + '/' + v); await p.waitForTimeout(200); }
  const back = await p.textContent('#pageCmd'), note = await p.textContent('#pageCmdNote');
  await p.close();
  if (errs.length) throw new Error(errs.join('; '));
  return { back, note };
}
async function read(ctx, file) {
  // A fragment carries no charset of its own: read both as UTF-8.
  const g = file + '.u.html'; fs.writeFileSync(g, '<meta charset="utf-8">\n' + fs.readFileSync(file, 'utf8'));
  const p = await ctx.newPage(); await p.goto('file://' + g);
  const r = await p.evaluate(() => {
    const s = Array.from(document.scripts).find(x => x.textContent.startsWith('window.CHURCH_YEAR_DATA = '));
    const t = s.textContent; const data = JSON.parse(t.slice(26, t.lastIndexOf(';')));
      // Packed tables (gzip, base64) are unpacked below, outside the page.
    s.textContent = '';
    return { data, html: document.documentElement.outerHTML };
  });
  await p.close();
  if (typeof r.data === 'string') r.data = JSON.parse(require('zlib').gunzipSync(Buffer.from(r.data, 'base64')).toString('utf8'));
  return r;
}
function diff(a, b, path, out) {
  if (JSON.stringify(a) === JSON.stringify(b)) return;
  if (a && b && typeof a === 'object' && typeof b === 'object' && !Array.isArray(a)) {
    for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) diff(a[k], b[k], path + '.' + k, out);
  } else out.push(path + ': ' + String(JSON.stringify(a)).slice(0, 150) + '  vs  ' + String(JSON.stringify(b)).slice(0, 150));
}
(async () => {
  const b = await chromium.launch();
  const on = await b.newContext({ acceptDownloads: true }), off = await b.newContext({ javaScriptEnabled: false });
  if (step === 'make') {
    const made = {};
    for (const c of CASES) {
      const m = await make(on, 'file://' + src + c.link, c.steps, dir + '/' + c.name + '.made.html');
      m.restored = await restore(on, 'file://' + src + '#lectionary=roman&date=2024-08-15', m.cmd, c.steps);
      if (!c.fragment) await make(on, 'file://' + dir + '/' + c.name + '.made.html', [], dir + '/' + c.name + '.again.html');
      made[c.name] = m;
    }
    console.log(JSON.stringify(made));
  } else {
    let bad = 0;
    for (const c of CASES) {
      const pairs = [[c.name + '.made.html', c.name + '.ref.html', '']];
      if (!c.fragment) pairs.push([c.name + '.again.html', c.name + '.made.html', ' (made again)']);
      for (const [x, y, note] of pairs) {
        const [A, B] = [await read(off, dir + '/' + x), await read(off, dir + '/' + y)];
        const out = []; diff(canon(A.data), canon(B.data), 'DATA', out);
        const markup = A.html === B.html;
        if (out.length || !markup) bad++;
        console.log((!out.length && markup ? 'ok   ' : 'DIFF ') + c.name + note + (markup ? '' : ': markup differs'));
        for (const l of out.slice(0, 8)) console.log('       ' + l);
      }
    }
    process.exitCode = bad ? 1 : 0;
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(2); });
"""


def main() -> int:
    src = ROOT / "church_year.html"
    if not src.exists():
        sys.exit("✗ no church_year.html: run python church_year.py first")
    root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    env = dict(os.environ, NODE_PATH=root)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "Rose Window.svg").write_text(SVG, encoding="utf-8")
        (tmp / "seal.png").write_bytes(png(37, 24))
        (tmp / "check.js").write_text(SCRIPT, encoding="utf-8")
        cases = [{"name": n, "link": l, "steps": s,
                  "fragment": any(k == "pageFragment" and v for k, v in s)} for n, l, s in CASES]
        r = subprocess.run(["node", str(tmp / "check.js"), str(src), str(tmp), json.dumps(cases), "make"],
                           env=env, capture_output=True, text=True)
        if r.returncode:
            print(r.stdout, r.stderr)
            sys.exit("✗ the page could not make its pages")
        made = json.loads(r.stdout.strip().splitlines()[-1])
        bad_restore = []
        for c in cases:
            cmd, name = made[c["name"]]["cmd"], made[c["name"]]["name"]
            print(f"  {c['name']}: {cmd}")
            back = made[c["name"]]["restored"]
            if back["back"] != cmd:
                bad_restore.append(c["name"])
                print(f"DIFF {c['name']}: pasted back, the window gives\n       {back['back']}\n       ({back['note']})")
            argv = shlex.split(cmd)[2:]
            if "-o" in argv:
                i = argv.index("-o")
                del argv[i:i + 2]
            out = subprocess.run([sys.executable, str(ROOT / "church_year.py"), *argv,
                                  "-o", str(tmp / f"{c['name']}.ref.html")],
                                 cwd=tmp, capture_output=True, text=True)
            if out.returncode:
                print(out.stdout, out.stderr)
                sys.exit(f"✗ {c['name']}: the command failed")
            want = shlex.split(cmd)[shlex.split(cmd).index("-o") + 1] if "-o" in shlex.split(cmd) else "church_year.html"
            if name != want:
                print(f"DIFF {c['name']}: saved as {name}, the command writes {want}")
        r = subprocess.run(["node", str(tmp / "check.js"), str(src), str(tmp), json.dumps(cases), "compare"], env=env)
        if not bad_restore:
            print(f"ok   every command pasted back sets the window to the same command ({len(cases)})")
        ok = r.returncode == 0 and not bad_restore
        print("all the same" if ok else "✗ some pages differ")
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
