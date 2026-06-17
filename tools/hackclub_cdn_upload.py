#!/usr/bin/env python3
"""Upload the big Unity build files to the Hack Club CDN via POST /api/v4/upload.

The files are uploaded as instructed. NOTE: the Hack Club CDN currently serves
every object with duplicate `Access-Control-Allow-Origin` headers, which all
browsers reject for cross-origin fetch() (verified: a real browser fetch of any
HC CDN object fails with "TypeError: Failed to fetch"). Unity wasm/data load via
fetch(), so the site cannot actually load them from this CDN in a browser; it
serves them from Cloudflare R2 instead. This script exists so the upload is done
and recorded; the resulting URLs are written to hackclub-cdn-uploads.json."""
import json
import os
import subprocess

KEY = open(".cdn_key").read().strip()
SRC = "/tmp/hc_upload"
FILES = [
    "u2.wasm", "u2.data",
    "u4.wasm", "u4.data",
    "u8.wasm.unityweb", "u8.data.unityweb.part00", "u8.data.unityweb.part01",
    "u13.wasm", "u13.data",
    "u16.wasm", "u16.data",
]
out = {}
if os.path.exists("hackclub-cdn-uploads.json"):
    out = json.load(open("hackclub-cdn-uploads.json"))
for fn in FILES:
    path = os.path.join(SRC, fn)
    if fn in out:
        print("skip (done):", fn); continue
    mb = os.path.getsize(path) / 1e6
    print(f"uploading {fn} ({mb:.0f} MB) to Hack Club CDN ...", flush=True)
    res = subprocess.run(
        ["curl", "-s", "--max-time", "600", "-X", "POST",
         "-H", f"Authorization: Bearer {KEY}",
         "-F", f"file=@{path}", "https://cdn.hackclub.com/api/v4/upload"],
        capture_output=True, text=True)
    try:
        url = json.loads(res.stdout)["url"]
    except Exception:
        print("  FAILED:", res.stdout[:200]); raise SystemExit(1)
    out[fn] = url
    print("  ->", url, flush=True)
    json.dump(out, open("hackclub-cdn-uploads.json", "w"), indent=2)
print("DONE; uploaded", len(out), "files to Hack Club CDN")
