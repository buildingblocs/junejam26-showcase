#!/usr/bin/env python3
"""Upload the big Unity build files to R2 (public bucket), mirroring repo paths.
Writes the public-URL map to r2-assets.json. Forces IPv4 (this network's IPv6
path to *.r2.cloudflarestorage.com fails the TLS handshake)."""
import socket
import json
import os
import boto3
from botocore.config import Config

_orig = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in _orig(*a, **k) if r[0] == socket.AF_INET]

creds = dict(l.strip().split("=", 1) for l in open(".r2_creds") if "=" in l)
s3 = boto3.client(
    "s3",
    endpoint_url=creds["R2_ENDPOINT"],
    aws_access_key_id=creds["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=creds["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4", region_name="auto"),
)
BUCKET = "junejam-showcase"
PUBLIC = "https://pub-be8869d68a2b4911bc34532d32ceb12b.r2.dev"

FILES = [
    "site/public/play/u2/Build/u2.wasm",
    "site/public/play/u2/Build/u2.data",
    "site/public/play/u4/Build/u4.wasm",
    "site/public/play/u4/Build/u4.data",
    "site/public/play/u8/Build/u8.wasm.unityweb",
    "site/public/play/u8/Build/data-parts/u8.data.unityweb.part00",
    "site/public/play/u8/Build/data-parts/u8.data.unityweb.part01",
    "site/public/play/u13/Build/u13.wasm",
    "site/public/play/u13/Build/u13.data",
    "site/public/play/u16/Build/u16.wasm",
    "site/public/play/u16/Build/u16.data",
]

def ctype(path):
    if path.endswith(".wasm"):
        return "application/wasm"
    return "application/octet-stream"

mapping = {}
if os.path.exists("r2-assets.json"):
    mapping = json.load(open("r2-assets.json"))

for f in FILES:
    key = f[len("site/public/"):]          # e.g. play/u13/Build/u13.wasm
    url = f"{PUBLIC}/{key}"
    if mapping.get(f) == url:
        print("skip (done):", key); continue
    sz = os.path.getsize(f) / 1e6
    print(f"uploading {key} ({sz:.0f} MB) ...", flush=True)
    s3.upload_file(f, BUCKET, key, ExtraArgs={"ContentType": ctype(f)})
    mapping[f] = url
    json.dump(mapping, open("r2-assets.json", "w"), indent=2)
    print("  ->", url, flush=True)

print("DONE; uploaded/confirmed", len(mapping), "files")
