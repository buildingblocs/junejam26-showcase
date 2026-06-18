#!/usr/bin/env python3
"""Assemble a served Unity WebGL play dir from a build-out, the way the showcased
Unity games are served: small files (loader, framework, TemplateData) committed
locally under site/public/play/<slug>/, big files (wasm + data) fetched from R2.

Usage:  python3 tools/assemble_unity.py <slug> "<title>" [W H]

It copies from site/playable-src/unity/build-out/<slug>/ and writes
site/public/play/<slug>/. You still upload the big files to R2 separately:
    python3 tools/r2_put.py site/public/play/<slug>/Build/<slug>.wasm.unityweb \
                            site/public/play/<slug>/Build/<slug>.data.unityweb
(then delete those two local copies — they live on R2).

All BuildWebGL.cs builds use Gzip + decompressionFallback, so the files are
<slug>.loader.js, <slug>.framework.js.unityweb, <slug>.wasm.unityweb,
<slug>.data.unityweb."""
import os
import shutil
import sys

R2 = "https://pub-be8869d68a2b4911bc34532d32ceb12b.r2.dev"

slug = sys.argv[1]
title = sys.argv[2]
W = sys.argv[3] if len(sys.argv) > 3 else "960"
H = sys.argv[4] if len(sys.argv) > 4 else "600"

src = f"site/playable-src/unity/build-out/{slug}"
dst = f"site/public/play/{slug}"
if not os.path.isdir(src):
    sys.exit(f"no build-out at {src}")

if os.path.isdir(dst):
    shutil.rmtree(dst)
os.makedirs(f"{dst}/Build", exist_ok=True)
shutil.copytree(f"{src}/TemplateData", f"{dst}/TemplateData")
shutil.copy(f"{src}/Build/{slug}.loader.js", f"{dst}/Build/{slug}.loader.js")
shutil.copy(f"{src}/Build/{slug}.framework.js.unityweb", f"{dst}/Build/{slug}.framework.js.unityweb")

index = f"""<!DOCTYPE html>
<html lang="en-us">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Unity Web Player | {title}</title>
    <link rel="shortcut icon" href="TemplateData/favicon.ico">
    <link rel="stylesheet" href="TemplateData/style.css">
  </head>
  <body>
    <div id="unity-container" class="unity-desktop">
      <canvas id="unity-canvas" width={W} height={H} tabindex="-1"></canvas>
      <div id="unity-loading-bar">
        <div id="unity-logo"></div>
        <div id="unity-progress-bar-empty"><div id="unity-progress-bar-full"></div></div>
      </div>
      <div id="unity-warning"> </div>
      <div id="unity-footer">
        <div id="unity-logo-title-footer"></div>
        <div id="unity-fullscreen-button"></div>
        <div id="unity-build-title">{title}</div>
      </div>
    </div>
    <script>
      var canvas = document.querySelector("#unity-canvas");
      function unityShowBanner(msg, type) {{
        var b = document.querySelector("#unity-warning");
        function upd() {{ b.style.display = b.children.length ? 'block' : 'none'; }}
        var div = document.createElement('div'); div.innerHTML = msg; b.appendChild(div);
        if (type == 'error') div.style = 'background: red; padding: 10px;';
        else {{ if (type == 'warning') div.style = 'background: yellow; padding: 10px;';
          setTimeout(function() {{ b.removeChild(div); upd(); }}, 5000); }}
        upd();
      }}
      var buildUrl = "Build";
      var loaderUrl = buildUrl + "/{slug}.loader.js";
      var config = {{
        arguments: [],
        dataUrl: "{R2}/play/{slug}/Build/{slug}.data.unityweb?v=r2",
        frameworkUrl: buildUrl + "/{slug}.framework.js.unityweb",
        codeUrl: "{R2}/play/{slug}/Build/{slug}.wasm.unityweb?v=r2",
        streamingAssetsUrl: "StreamingAssets",
        companyName: "DefaultCompany",
        productName: "{title}",
        productVersion: "0.1.0",
        showBanner: unityShowBanner,
      }};
      config.devicePixelRatio = 1;
      if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {{
        var meta = document.createElement('meta');
        meta.name = 'viewport';
        meta.content = 'width=device-width, height=device-height, initial-scale=1.0, user-scalable=no, shrink-to-fit=yes';
        document.getElementsByTagName('head')[0].appendChild(meta);
        document.querySelector("#unity-container").className = "unity-mobile";
        canvas.className = "unity-mobile";
      }} else {{
        config.matchWebGLToCanvasSize = true;
        var BASE_W = {W}, BASE_H = {H};
        var fitCanvas = function () {{
          var scale = Math.min(window.innerWidth / BASE_W, window.innerHeight / BASE_H);
          canvas.style.width = Math.round(BASE_W * scale) + "px";
          canvas.style.height = Math.round(BASE_H * scale) + "px";
        }};
        fitCanvas(); window.addEventListener("resize", fitCanvas);
      }}
      document.querySelector("#unity-loading-bar").style.display = "block";
      var script = document.createElement("script");
      script.src = loaderUrl;
      script.onload = () => {{
        createUnityInstance(canvas, config, (p) => {{
          document.querySelector("#unity-progress-bar-full").style.width = 100 * p + "%";
        }}).then((u) => {{
          document.querySelector("#unity-loading-bar").style.display = "none";
          document.querySelector("#unity-fullscreen-button").onclick = () => u.SetFullscreen(1);
        }}).catch((m) => alert(m));
      }};
      document.body.appendChild(script);
    </script>
  </body>
</html>
"""
with open(f"{dst}/index.html", "w") as f:
    f.write(index)

# stage big files into the served Build dir so r2_put mirrors the key; the caller
# uploads then deletes these two local copies.
for ext in ("wasm.unityweb", "data.unityweb"):
    shutil.copy(f"{src}/Build/{slug}.{ext}", f"{dst}/Build/{slug}.{ext}")

print(f"assembled {dst} (canvas {W}x{H}, title '{title}')")
print(f"next: python3 tools/r2_put.py {dst}/Build/{slug}.wasm.unityweb {dst}/Build/{slug}.data.unityweb")
print(f"then: rm -f {dst}/Build/{slug}.wasm.unityweb {dst}/Build/{slug}.data.unityweb")
