#!/usr/bin/env python3
"""
Check that lectionary.py and the web page (church_year.js) give every church
the same readings, day by day.

    python web/verify_readings.py                      # every church with readings, 2025-2030
    python web/verify_readings.py --from 2000 --to 2060 --church lcms-elhb-one-year
    python web/verify_readings.py --feasts principal   # as the Feasts menu leaves them

Each day's sets are compared with their titles, their kind (day, feasts,
dated, daily, office: the page's Readings boxes) and their readings.

Needs Node.js (https://nodejs.org) and an up-to-date web/data.json
(python web/export_data.py).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

import lectionary as L          # noqa: E402
import traditions as T          # noqa: E402
from calendars import GREGORIAN  # noqa: E402

JS = r"""
const CY = require(process.argv[1]).ChurchYear;
const data = require(process.argv[2]);
const [key, y0, y1, detail] = [process.argv[3], +process.argv[4], +process.argv[5], process.argv[6]];
const out = {};
for (let y = y0; y <= y1; y++) {
  out[y] = CY.build(data, { tradition: key, year: y, feastDetail: detail || undefined }).readings;
}
process.stdout.write(JSON.stringify(out));
"""


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().split("\n\n")[0])
    p.add_argument("--from", dest="start", type=int, default=2025)
    p.add_argument("--to", dest="end", type=int, default=2030)
    p.add_argument("--church", action="append", default=[], metavar="KEY")
    p.add_argument("--feasts", choices=T.FEAST_DETAIL, default="",
                   help="the Feasts setting to compare at (default: config.csv's feast_detail)")
    a = p.parse_args(argv)
    node = shutil.which("node") or shutil.which("nodejs")
    if not node:
        sys.exit("✗ Node.js is needed: install it from https://nodejs.org")
    keys = a.church or [t.key for t in T.load_registry(L.DATA)
                        if L.source_readings(T.Source(L.DATA, t))]
    bad = 0
    for key in keys:
        run = subprocess.run([node, "-e", JS, str(HERE / "church_year.js"), str(HERE / "data.json"),
                              key, str(a.start), str(a.end), a.feasts], capture_output=True, text=True,
                             encoding="utf-8")
        if run.returncode:
            print(f"✗ {key}: {run.stderr.strip()[:300]}")
            bad += 1
            continue
        js = json.loads(run.stdout)
        diffs = []
        for y in range(a.start, a.end + 1):
            _, index = L.church_year(key, y, feasts=a.feasts)
            py = {GREGORIAN.isoformat(d): [{"title": g["title"], "category": g["category"],
                                            "items": g["items"]} for g in groups]
                  for d, groups in index.items()}
            want = js[str(y)]
            for day in sorted(set(py) | set(want)):
                if py.get(day) != want.get(day):
                    diffs.append(f"{day}: python {json.dumps(py.get(day), ensure_ascii=False)[:160]}"
                                 f"\n            page   {json.dumps(want.get(day), ensure_ascii=False)[:160]}")
        if diffs:
            bad += 1
            print(f"✗ {key}: {len(diffs)} days differ")
            print("\n".join("    " + d for d in diffs[:5]))
        else:
            print(f"✓ {key}  {a.start}-{a.end} identical")
    print(f"{len(keys) - bad}/{len(keys)} identical")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
