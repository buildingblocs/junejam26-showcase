#!/usr/bin/env python3
"""Enable the free managed (r2.dev) public URL for the bucket and print it."""
import socket
import json
import requests

_orig = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in _orig(*a, **k) if r[0] == socket.AF_INET]

creds = dict(l.strip().split("=", 1) for l in open(".r2_creds") if "=" in l)
ACCOUNT = creds["R2_ACCOUNT_ID"]
TOKEN = creds["R2_API_TOKEN"]
BUCKET = "junejam-showcase"
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
BASE = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/r2/buckets/{BUCKET}"

# enable managed public domain
r = requests.put(f"{BASE}/domains/managed", headers=H, data=json.dumps({"enabled": True}), timeout=30)
print("enable status:", r.status_code)
print(json.dumps(r.json(), indent=2)[:800])

# fetch its current state to read the public hostname
g = requests.get(f"{BASE}/domains/managed", headers=H, timeout=30)
print("get status:", g.status_code)
print(json.dumps(g.json(), indent=2)[:800])
