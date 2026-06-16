#!/usr/bin/env python3
"""Serve a pygbag/WebGL build dir and screenshot it in headless chromium.

Usage: python3 verify_build.py <build_dir> [--wait SECONDS] [--out shot.png] [--click]
Exits 0 always; prints console logs, errors, and a canvas-pixel summary so the
caller can judge whether the game actually rendered (non-blank canvas).
"""
import sys, os, threading, http.server, socketserver, functools, argparse, time

ISOLATE = False

class COOPHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        if ISOLATE:
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
        super().end_headers()
    def log_message(self, *a):
        pass

def serve(directory, port):
    handler = functools.partial(COOPHandler, directory=directory)
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build_dir")
    ap.add_argument("--wait", type=float, default=30)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--out", default=None)
    ap.add_argument("--click", action="store_true", help="click center after load")
    ap.add_argument("--clickxy", default=None, help="x,y to click ~10s before end (gameplay check)")
    ap.add_argument("--isolate", action="store_true", help="send COOP/COEP headers")
    args = ap.parse_args()

    global ISOLATE
    ISOLATE = args.isolate
    d = os.path.abspath(args.build_dir)
    assert os.path.isfile(os.path.join(d, "index.html")), f"no index.html in {d}"
    httpd = serve(d, args.port)
    url = f"http://127.0.0.1:{args.port}/index.html"
    print(f"serving {d} at {url}")

    from playwright.sync_api import sync_playwright
    msgs, errors = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": 960, "height": 720})
        page.on("console", lambda m: msgs.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(url, wait_until="load", timeout=60000)
        deadline = time.time() + args.wait
        gestured = False
        gameplay_clicked = False
        cx, cy = (None, None)
        if args.clickxy:
            cx, cy = [int(v) for v in args.clickxy.split(",")]
        while time.time() < deadline:
            page.wait_for_timeout(1500)
            # once the runtime is up, give a user gesture so audio/start screens proceed
            if args.click and not gestured and any("apk" in m or "MEDIA" in m for m in msgs):
                try:
                    page.mouse.click(480, 360)
                    page.keyboard.press("Space")
                    page.keyboard.press("Enter")
                    gestured = True
                except Exception:
                    pass
            # gameplay click near the end (after the game has had time to load its menu)
            if cx is not None and not gameplay_clicked and time.time() > deadline - 10:
                try:
                    page.mouse.click(cx, cy)
                    gameplay_clicked = True
                except Exception:
                    pass
        if args.out:
            try:
                page.screenshot(path=os.path.abspath(args.out), timeout=15000)
                print("screenshot:", args.out)
            except Exception as e:
                print("SCREENSHOT FAILED (page likely frozen):", e)
        # canvas pixel diversity check
        diversity = page.evaluate("""() => {
            const c = document.querySelector('canvas');
            if (!c) return {found:false};
            const w=c.width, h=c.height;
            try {
              const gl = c.getContext('webgl2')||c.getContext('webgl');
              let data;
              if (gl) { const px=new Uint8Array(w*h*4); gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,px); data=px; }
              else { const ctx=c.getContext('2d'); data=ctx.getImageData(0,0,w,h).data; }
              const seen=new Set(); let n=0;
              for (let i=0;i<data.length;i+=4000){ seen.add(data[i]+','+data[i+1]+','+data[i+2]); n++; }
              return {found:true, w, h, distinct:seen.size, sampled:n};
            } catch(e){ return {found:true, w, h, err:String(e)}; }
        }""")
        print("CANVAS:", diversity)
        browser.close()
    httpd.shutdown()
    print("--- console (last 40) ---")
    for m in msgs[-40:]:
        print(m)
    print("--- pageerrors ---")
    for e in errors:
        print(e)

if __name__ == "__main__":
    main()
