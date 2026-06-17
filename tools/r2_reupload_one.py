#!/usr/bin/env python3
"""Re-upload one game's rebuilt wasm/data to R2 (overwrites same keys).
Mirrors the working r2_upload.py exactly. Forces IPv4."""
import socket, sys, os, boto3
from botocore.config import Config
_orig = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in _orig(*a, **k) if r[0] == socket.AF_INET]
creds = dict(l.strip().split("=", 1) for l in open(".r2_creds") if "=" in l)
s3 = boto3.client("s3", endpoint_url=creds["R2_ENDPOINT"],
    aws_access_key_id=creds["R2_ACCESS_KEY_ID"], aws_secret_access_key=creds["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4", region_name="auto"))
BUCKET = "junejam-showcase"
g = sys.argv[1]
src_dir = f"site/playable-src/unity/build-out/{g}/Build"
for fn, ct in [(f"{g}.wasm", "application/wasm"), (f"{g}.data", "application/octet-stream")]:
    key = f"play/{g}/Build/{fn}"
    s3.upload_file(os.path.join(src_dir, fn), BUCKET, key, ExtraArgs={"ContentType": ct})
    print("uploaded", key)
print("done", g)
