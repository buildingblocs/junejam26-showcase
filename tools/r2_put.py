#!/usr/bin/env python3
"""Upload arbitrary build files to the public R2 bucket, mirroring repo paths
under site/public/ -> the r2.dev root. Reusable for the Unity WebGL batch.

Usage:  python3 tools/r2_put.py <path> [<path> ...]
where each <path> is a real file under site/public/ (e.g.
site/public/play/u1/Build/u1.wasm.unityweb). Prints the public URL for each.

Forces IPv4 (this network's IPv6 path to *.r2.cloudflarestorage.com fails the
TLS handshake). Credentials come from the gitignored .r2_creds."""
import socket
import sys
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


def ctype(path):
    if path.endswith(".wasm"):
        return "application/wasm"
    return "application/octet-stream"


for f in sys.argv[1:]:
    if not f.startswith("site/public/"):
        print("SKIP (not under site/public/):", f); continue
    if not os.path.exists(f):
        print("SKIP (missing):", f); continue
    key = f[len("site/public/"):]
    sz = os.path.getsize(f) / 1e6
    print(f"uploading {key} ({sz:.0f} MB) ...", flush=True)
    s3.upload_file(f, BUCKET, key, ExtraArgs={"ContentType": ctype(f)})
    print("  ->", f"{PUBLIC}/{key}", flush=True)

print("DONE")
