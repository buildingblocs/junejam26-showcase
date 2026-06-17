# Big-file CDN hosting

The large Unity WebGL files (`*.wasm` / `*.data`, ~450 MB across the five Unity
games) are not served from the GitHub Pages repo. They live on a CDN and the
game `index.html` files point at it.

## Hack Club CDN — uploaded, but cannot serve the browser

Per the original instruction, every big file was uploaded to the Hack Club CDN
through `POST https://cdn.hackclub.com/api/v4/upload` (Bearer key, kept locally
in the gitignored `.cdn_key`). The resulting object URLs are recorded in
`hackclub-cdn-uploads.json`, and the uploader is `tools/hackclub_cdn_upload.py`.

However, the Hack Club CDN **cannot be used to load these files in a browser**.
Every object it serves comes back with **duplicate `Access-Control-Allow-Origin`
headers** (verified: 2–3 copies on the final response). The Fetch/CORS spec
requires exactly one, so browsers reject the response — a real
`fetch('https://cdn.hackclub.com/.../u13.wasm')` from another origin fails with
`TypeError: Failed to fetch`. (`curl` tolerates the duplicate header, so it
looks fine from the shell; only browsers reject it.) Unity's loader and pygbag
both fetch their wasm/data, so the games would not load. This is a CDN-side
configuration bug that can't be fixed from our side.

## Cloudflare R2 — what actually serves the site

Because of the above, the site loads the big files from a public Cloudflare R2
bucket (`pub-…​.r2.dev`), which returns a single, correct `Access-Control-Allow-
Origin` header and supports range requests. Egress is free on R2, so this stays
within the free tier. Tooling: `tools/r2_upload.py`, `tools/r2_finalize.py`
(credentials in the gitignored `.r2_creds`).

If the Hack Club CDN fixes its duplicate-CORS-header bug, switching the game
`index.html` files from the R2 URLs to the Hack Club URLs in
`hackclub-cdn-uploads.json` is a one-line-per-game change.
