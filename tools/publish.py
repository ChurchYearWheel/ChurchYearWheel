#!/usr/bin/env python3
"""
Publish the web page to a here.now site, replacing what is there.

    python tools/publish.py --site crisp-nimbus-6xz9
    python tools/publish.py --site crisp-nimbus-6xz9 --add center.svg
    python tools/publish.py --site crisp-nimbus-6xz9 --no-page --add a.html --add b.svg
    python tools/publish.py --site crisp-nimbus-6xz9 --html church_year.html --dry-run
    python tools/publish.py --site crisp-nimbus-6xz9 --password      # set or change it (asks)
    python tools/publish.py --site crisp-nimbus-6xz9 --no-password   # take it off

It builds the page (church_year.py, with config.csv's settings) and
uploads it as the site's index.html, with any --add files beside it (a
center.svg, say).  The site then holds exactly those files: a here.now update
replaces the whole site, and the version before it stays in the site's
Versions panel, where it can be restored.  Files that have not changed are
not uploaded again.

The API key is read from the HERENOW_API_KEY environment variable, else from
~/.herenow/credentials (the key on its own line), else --key-file.  Make one
in the here.now dashboard.  It is never printed or written anywhere.

Only Python's standard library is used.  here.now's API:
https://here.now/docs
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import mimetypes
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = os.environ.get("HERENOW_API_BASE", "https://here.now/api/v1")   # the base is only changed for testing
CLIENT = "church-year/publish.py"

TYPES = {".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png",
         ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp",
         ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
         ".json": "application/json", ".md": "text/markdown; charset=utf-8",
         ".csv": "text/csv; charset=utf-8", ".pdf": "application/pdf", ".ics": "text/calendar",
         ".txt": "text/plain; charset=utf-8"}


def api_key(key_file: str | None) -> str:
    key = os.environ.get("HERENOW_API_KEY", "").strip()
    paths = [Path(key_file).expanduser()] if key_file else [Path.home() / ".herenow" / "credentials"]
    for path in ([] if key else paths):
        if path.exists():
            text = path.read_text(encoding="utf-8").strip()
            try:                                  # a JSON file, as some tools write it
                data = json.loads(text)
                text = str(data.get("apiKey") or data.get("api_key") or data.get("key") or "")
            except (ValueError, AttributeError):
                pass
            key = text.splitlines()[0].strip() if text else ""
            if key:
                break
    if not key:
        sys.exit("✗ No here.now API key: set HERENOW_API_KEY, or put the key in "
                 f"{Path.home() / '.herenow' / 'credentials'} (make one in the here.now dashboard)")
    return key


def call(method: str, url: str, key: str | None = None, body=None, data: bytes | None = None,
         headers: dict | None = None) -> dict:
    # The presigned upload URLs get only the headers here.now names for them.
    head = {"X-HereNow-Client": CLIENT} if url.startswith(API.rsplit("/api/", 1)[0]) else {}
    if key:
        head["Authorization"] = "Bearer " + key
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        head["Content-Type"] = "application/json"
    head.update(headers or {})
    req = urllib.request.Request(url, data=data, method=method, headers=head)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            text = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        sys.exit(f"✗ {method} {url.split('?')[0]}: HTTP {exc.code} {detail}")
    except urllib.error.URLError as exc:
        sys.exit(f"✗ {method} {url.split('?')[0]}: {exc.reason}")
    try:
        return json.loads(text) if text.strip() else {}
    except ValueError:
        return {}


def build_page(out: Path, extra: list[str]) -> None:
    cmd = [sys.executable, str(ROOT / "church_year.py"), "--out", str(out)] + extra
    run = subprocess.run(cmd, cwd=str(ROOT))
    if run.returncode:
        sys.exit("✗ church_year.py failed")


def describe(path: Path, name: str) -> dict:
    blob = path.read_bytes()
    ctype = TYPES.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return {"path": name, "size": len(blob), "contentType": ctype,
            "hash": hashlib.sha256(blob).hexdigest()}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().split("\n\n")[0])
    p.add_argument("--site", required=True, metavar="SLUG",
                   help="the site's name, the part before .here.now (crisp-nimbus-6xz9)")
    p.add_argument("--html", metavar="FILE",
                   help="publish this page instead of building one (default: build it)")
    p.add_argument("--no-page", action="store_true",
                   help="publish only the --add files: no index.html is built or uploaded")
    p.add_argument("--add", action="append", default=[], metavar="FILE",
                   help="another file to publish beside the page, under its own name (repeatable)")
    p.add_argument("--page-args", default="", metavar="ARGS",
                   help='options for church_year.py when building, e.g. "--zoom 2 --show calendar"')
    p.add_argument("--key-file", metavar="FILE", help="read the API key from this file")
    p.add_argument("--password", action="store_true",
                   help="also set or change the site's password (asked for, not echoed)")
    p.add_argument("--no-password", action="store_true", help="also take the site's password off")
    p.add_argument("--dry-run", action="store_true", help="show what would be published and stop")
    a = p.parse_args(argv)

    with tempfile.TemporaryDirectory(prefix="publish-") as tmp:
        files = []
        if a.no_page:
            if a.html:
                sys.exit("✗ --no-page and --html: choose one")
            if not a.add:
                sys.exit("✗ --no-page needs at least one --add file")
        elif a.html:
            page = Path(a.html)
            if not page.exists():
                sys.exit(f"✗ no file {page}")
            files.append((page, "index.html"))
        else:
            page = Path(tmp) / "index.html"
            build_page(page, a.page_args.split())
            files.append((page, "index.html"))
        for extra in a.add:
            path = Path(extra)
            if not path.is_file():
                sys.exit(f"✗ no file {path}")
            if path.name.lower() == "index.html" and not a.no_page:
                sys.exit("✗ --add index.html would replace the page")
            files.append((path, path.name))

        manifest = [describe(path, name) for path, name in files]
        for f in manifest:
            print(f"  {f['path']:<24} {f['size'] / 1024:>9.0f} KB  {f['contentType']}")
        if a.dry_run:
            print(f"(dry run: nothing sent to https://{a.site}.here.now/)")
            return 0

        key = api_key(a.key_file)
        staged = call("PUT", f"{API}/publish/{a.site}", key, {"files": manifest})
        upload = staged.get("upload") or {}
        if not upload.get("finalizeUrl") or not upload.get("versionId"):
            sys.exit("✗ here.now did not return an upload to finish: "
                     + json.dumps(staged)[:300])
        local = {name: path for path, name in files}
        for item in upload.get("uploads") or []:
            path = local.get(item.get("path"))
            if path is None:
                sys.exit(f"✗ here.now asked for an unknown file {item.get('path')}")
            print(f"  uploading {item['path']} ...")
            call(item.get("method") or "PUT", item["url"], data=path.read_bytes(),
                 headers=item.get("headers") or {})
        skipped = upload.get("skipped") or []
        if skipped:
            print(f"  unchanged: {', '.join(str(s.get('path', s)) if isinstance(s, dict) else str(s) for s in skipped)}")
        call("POST", upload["finalizeUrl"], key, {"versionId": upload["versionId"]})

    if a.password or a.no_password:
        if a.password:
            secret = getpass.getpass("New password for the site: ")
            if not secret or secret != getpass.getpass("Again: "):
                sys.exit("✗ the passwords were empty or did not match; the site was published "
                         "but its password is unchanged")
            body = {"password": secret}
        else:
            body = {"password": None}
        call("PATCH", f"{API}/publish/{a.site}/metadata", key, body)
        print("✓ password " + ("set" if a.password else "removed"))

    print(f"✓ Published https://{staged.get('slug') or a.site}.here.now/  "
          f"(earlier versions are in the site's Versions panel)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
