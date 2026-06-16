#!/usr/bin/env python3
"""One-time R2 bucket setup: create bucket, set CORS, upload a test object."""
import socket
import boto3
from botocore.config import Config

# This network's IPv6 path to *.r2.cloudflarestorage.com fails the TLS handshake;
# IPv4 works. Force IPv4 for all connections.
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_only(*args, **kwargs):
    return [r for r in _orig_getaddrinfo(*args, **kwargs) if r[0] == socket.AF_INET]
socket.getaddrinfo = _ipv4_only

creds = dict(l.strip().split("=", 1) for l in open(".r2_creds") if "=" in l)
s3 = boto3.client(
    "s3",
    endpoint_url=creds["R2_ENDPOINT"],
    aws_access_key_id=creds["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=creds["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4", region_name="auto"),
)

BUCKET = "junejam-showcase"
existing = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
print("existing buckets:", existing)
if BUCKET not in existing:
    s3.create_bucket(Bucket=BUCKET)
    print("created bucket", BUCKET)
else:
    print("bucket exists", BUCKET)

s3.put_bucket_cors(Bucket=BUCKET, CORSConfiguration={"CORSRules": [{
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["*"],
    "MaxAgeSeconds": 86400,
}]})
print("CORS set")

s3.put_object(Bucket=BUCKET, Key="_test/ping.txt", Body=b"pong", ContentType="text/plain")
print("uploaded _test/ping.txt")
