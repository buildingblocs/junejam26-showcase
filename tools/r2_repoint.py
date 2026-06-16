#!/usr/bin/env python3
"""Repoint the Unity index.html big-file URLs (wasm/data) to the R2 public URLs.
The responsive-canvas fix already applied to index.html is left intact."""
import json

r2 = json.load(open("r2-assets.json"))

def patch(path, repl):
    with open(path, encoding="utf-8") as f:
        c = f.read()
    for old, new in repl:
        assert c.count(old) == 1, f"{path}: expected 1 of {old!r}, got {c.count(old)}"
        c = c.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("repointed", path)

for g in ("u2", "u4", "u13", "u16"):
    wasm = r2[f"site/public/play/{g}/Build/{g}.wasm"]
    data = r2[f"site/public/play/{g}/Build/{g}.data"]
    patch(f"site/public/play/{g}/index.html", [
        (f'codeUrl: buildUrl + "/{g}.wasm",', f'codeUrl: "{wasm}",'),
        (f'dataUrl: buildUrl + "/{g}.data",', f'dataUrl: "{data}",'),
    ])

u8w = r2["site/public/play/u8/Build/u8.wasm.unityweb"]
u8p0 = r2["site/public/play/u8/Build/data-parts/u8.data.unityweb.part00"]
u8p1 = r2["site/public/play/u8/Build/data-parts/u8.data.unityweb.part01"]
patch("site/public/play/u8/index.html", [
    ('codeUrl: buildUrl + "/u8.wasm.unityweb",', f'codeUrl: "{u8w}",'),
    ('dataUrl: buildUrl + "/data-parts/u8.data.unityweb.part00",', f'dataUrl: "{u8p0}",'),
    ('          buildUrl + "/data-parts/u8.data.unityweb.part00",\n          buildUrl + "/data-parts/u8.data.unityweb.part01",',
     f'          "{u8p0}",\n          "{u8p1}",'),
])
print("ALL REPOINTED to R2")
