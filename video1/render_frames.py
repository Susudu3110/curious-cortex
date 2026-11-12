#!/usr/bin/env python3
"""Render doodle-animation frames for each scene (parallel across CPU cores)."""
import json, math, os
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.expanduser("~/YouTube/CuriousCortex/video1")
FPS = 12
S = 2          # supersample factor
W, H = 1280, 720
SS = (W*S, H*S)

BG     = (13, 15, 30)
PINK   = (255, 93, 162)
YELLOW = (255, 214, 90)
WHITE  = (245, 245, 250)
TEAL   = (90, 220, 210)
DIM    = (30, 34, 60)
COLORS = {"pink": PINK, "yellow": YELLOW, "white": WHITE, "teal": TEAL}

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

scenes = json.load(open(f"{BASE}/scenes.json"))
durations = json.load(open(f"{BASE}/voice/durations.json"))

def mix(c1, c2, k):
    return tuple(int(a + (b-a)*k) for a, b in zip(c1, c2))

def poly_len(pts):
    return sum(math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1))

def partial_poly(d, pts, k, color, w):
    """Draw polyline progressively: first k fraction of total length."""
    if k <= 0 or len(pts) < 2: return
    target = poly_len(pts) * k
    acc, done = 0.0, False
    for i in range(len(pts)-1):
        seg = math.dist(pts[i], pts[i+1])
        if acc + seg >= target:
            f = (target - acc) / seg
            end = (pts[i][0] + (pts[i+1][0]-pts[i][0])*f,
                   pts[i][1] + (pts[i+1][1]-pts[i][1])*f)
            d.line([pts[i], end], fill=color, width=w)
            done = True; break
        d.line([pts[i], pts[i+1]], fill=color, width=w)
        acc += seg
    if not done: d.line([pts[-2], pts[-1]], fill=color, width=w)

def pellipse(d, box, k, color, w, start=90):
    if k <= 0: return
    d.arc(box, start, start + 360*k, fill=color, width=w)

def partial_circle_center(d, cx, cy, rx, ry, k, color, w):
    pellipse(d, [cx-rx, cy-ry, cx+rx, cy+ry], k, color, w)

def partial_text(d, cx, cy, text, f, color, k):
    """Pop-in text: alpha-ish blend to bg while scaling."""
    if k <= 0: return
    e = min(1.0, k*1.6)
    col = mix(BG, color, e)
    scale = 0.85 + 0.15*min(1.0, k*2)
    # emulate scale by drawing at base size (scale factor baked into font choice by caller)
    b = d.textbbox((0,0), text, font=f)
    tw, th = b[2]-b[0], b[3]-b[1]
    d.text((cx-tw/2-b[0], cy-th/2-b[1]), text, font=f, fill=col)

# ---------------- element drawing ----------------

def el_brain(d, e, k):
    if k <= 0: return
    cx, cy, s = e["cx"]*W*S, e["cy"]*H*S, e["s"]*H*S*2
    col, w = COLORS[e["color"]], int(5*S)
    pellipse(d, [cx-s, cy-s*0.72, cx+s*0.95, cy+s*0.72], k, col, w)      # main lobe
    pellipse(d, [cx+s*0.18, cy+s*0.42, cx+s*0.82, cy+s*0.88], max(0, k-0.25)/0.75, col, max(2, w-2))
    partial_poly(d, [(cx+s*0.5, cy+s*0.88), (cx+s*0.5, cy+s*1.12)], max(0, k-0.35)/0.65, col, w)
    partial_poly(d, [(cx-s*0.02, cy-s*0.72), (cx-s*0.02, cy+s*0.4)], max(0, k-0.2)/0.8, col, max(2, w-2))
    for y1, y2 in [(-0.5, -0.25), (-0.15, 0.05), (0.2, 0.3)]:
        kk = max(0, k-0.3)/0.7
        partial_poly(d, [(cx-s*0.55, cy+y1*s), (cx-s*0.25, cy+y2*s)], kk, col, max(2, w-4))
        partial_poly(d, [(cx+s*0.3, cy+y1*s), (cx+s*0.6, cy+y2*s)], kk, col, max(2, w-4))

def el_baby(d, e, k):
    if k <= 0: return
    cx, cy, s = e["cx"]*W*S, e["cy"]*H*S, e["s"]*H*S*2
    col, w = COLORS[e["color"]], int(5*S)
    partial_circle_center(d, cx, cy, s*0.8, s*0.85, k, col, w)           # head
    for ex in (-0.32, 0.32):
        if k > 0.3: d.ellipse([cx+ex*s-int(3*S), cy-s*0.15-int(3*S), cx+ex*s+int(3*S), cy-s*0.15+int(3*S)], fill=col)
    if k > 0.5: partial_poly(d, [(cx-s*0.28, cy+s*0.28), (cx, cy+s*0.42), (cx+s*0.28, cy+s*0.28)], (k-0.5)/0.5, col, max(2, w-2))
    if k > 0.6: partial_poly(d, [(cx, cy-s*0.85), (cx+s*0.12, cy-s*1.05), (cx-s*0.08, cy-s*1.1), (cx+s*0.05, cy-s*1.28)], (k-0.6)/0.4, col, max(2, w-2))  # hair curl
    if k > 0.7:  # body bump
        partial_poly(d, [(cx-s*0.5, cy+s*0.85), (cx-s*0.5, cy+s*1.35)], (k-0.7)/0.3, col, w)
        partial_poly(d, [(cx+s*0.5, cy+s*0.85), (cx+s*0.5, cy+s*1.35)], (k-0.7)/0.3, col, w)

def el_waves(d, e, k):
    cx, cy, s = e["cx"]*W*S, e["cy"]*H*S, e["s"]*H*S*2
    col, w = COLORS[e["color"]], int(4*S)
    for i, rr in enumerate((0.85, 1.1, 1.35)):
        kk = max(0.0, min(1.0, (k - 0.15*i) / 0.7))
        if kk <= 0: continue
        a = 40 + 100*kk
        d.arc([cx-rr*s, cy-rr*s, cx+rr*s, cy+rr*s], 360-a, 360+a, fill=col, width=w)

def el_mobile(d, e, k):
    cx, cy0, s = e["cx"]*W*S, 0, e["s"]*H*S*2
    col, w = COLORS[e["color"]], int(5*S)
    cyh = cy0 + s*0.95                       # hanger height
    partial_poly(d, [(cx, cy0), (cx, cyh)], k, col, w)
    if k > 0.25:
        kk = (k-0.25)/0.75
        pellipse(d, [cx-s*0.55, cyh-s*0.12, cx+s*0.55, cyh+s*0.30], kk, col, w)   # arc bar
        for i, fx in enumerate((-0.42, 0.0, 0.42)):
            kk2 = max(0.0, (k - 0.4 - 0.15*i) / 0.3)
            if kk2 <= 0: continue
            partial_poly(d, [(cx+fx*s*0.95, cyh+s*0.1), (cx+fx*s*0.95, cyh+s*0.55)], kk2, col, max(2, w-2))
            r = int(6*S*min(1.0, kk2*2))
            d.ellipse([cx+fx*s*0.95-r, cyh+s*0.55-r, cx+fx*s*0.95+r, cyh+s*0.55+r], fill=col)

def el_arrow(d, e, k):
    x0, y0, x1, y1 = e["x0"]*W*S, e["y0"]*H*S, e["x1"]*W*S, e["y1"]*H*S
    col, w = COLORS[e["color"]], int(5*S)
    # curved path
    mx, my = (x0+x1)/2 + (y0-y1)*0.25, (y0+y1)/2 + (x1-x0)*0.25
    pts = []
    for i in range(13):
        t = i/12
        px = (1-t)**2*x0 + 2*(1-t)*t*mx + t**2*x1
        py = (1-t)**2*y0 + 2*(1-t)*t*my + t**2*y1
        pts.append((px, py))
    partial_poly(d, pts, k, col, w)
    if k >= 0.98:  # arrowhead
        ang = math.atan2(y1-my, x1-mx)
        for da in (2.6, -2.6):
            d.line([(x1, y1), (x1+18*S*math.cos(ang+da), y1+18*S*math.sin(ang+da))], fill=col, width=w)

def el_cabinet(d, e, k):
    cx, cy, s = e["cx"]*W*S, e["cy"]*H*S, e["s"]*H*S*2
    col, w = COLORS[e["color"]], int(5*S)
    x0, y0, x1, y1 = cx-s*0.55, cy-s*0.75, cx+s*0.55, cy+s*0.75
    partial_poly(d, [(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)], k, col, w)
    if k > 0.4:
        kk = (k-0.4)/0.6
        partial_poly(d, [(x0, cy), (x1, cy)], kk, col, max(2, w-2))
        for i, dy in enumerate((-0.35, 0.35)):
            kk2 = max(0.0, (k-0.55-0.1*i)/0.35)
            if kk2 > 0:
                partial_poly(d, [(x0+s*0.25, cy+dy*s), (x1-s*0.25, cy+dy*s)], kk2, col, max(2, w-3))
    if k > 0.75:  # magnifier leaning on it
        kk = (k-0.75)/0.25
        gx, gy, gr = x1+s*0.45, y0-s*0.05, s*0.28
        pellipse(d, [gx-gr, gy-gr, gx+gr, gy+gr], kk, YELLOW, max(2, w-1))
        partial_poly(d, [(gx+gr*0.7, gy+gr*0.7), (gx+gr*1.4, gy+gr*1.4)], kk, YELLOW, max(2, w-1))

def el_seahorse(d, e, k):
    """Doodle seahorse: head circle + snout + curled spiral tail + crown."""
    cx, cy = e["cx"]*W*S, e["cy"]*H*S
    s = e["s"]*H*S          # unit scale
    col, w = COLORS[e["color"]], int(5*S)
    # spine: head -> chest -> spiral
    pts = [(cx-s*0.05, cy-s*0.95), (cx+s*0.10, cy-s*0.60), (cx+s*0.30, cy-s*0.30),
           (cx+s*0.42, cy+s*0.05), (cx+s*0.30, cy+s*0.30)]
    # tail spiral around (cx+s*0.05, cy+s*0.30)
    scx, scy = cx+s*0.05, cy+s*0.30
    for i in range(30):
        t = i/29
        a = 0.35 + t*math.pi*3.1          # ~1.5 turns
        r = s*0.36*(1-t)**1.15 + s*0.03
        pts.append((scx + r*math.cos(a+math.pi/2), scy + r*math.sin(a+math.pi/2)))
    partial_poly(d, pts, k, col, w)
    # head circle
    if k > 0.1:
        hcx, hcy, hr = cx-s*0.02, cy-s*0.95, s*0.24
        kk = min(1.0, (k-0.1)/0.35)
        pellipse(d, [hcx-hr, hcy-hr, hcx+hr, hcy+hr], kk, col, w)
        # snout tube pointing left
        if k > 0.4:
            kk2 = min(1.0, (k-0.4)/0.25)
            partial_poly(d, [(hcx-hr*0.8, hcy+s*0.04), (hcx-hr*2.3, hcy+s*0.02)], kk2, col, w)
            partial_poly(d, [(hcx-hr*0.8, hcy-s*0.10), (hcx-hr*2.3, hcy-s*0.12)], kk2, col, w)
            d.ellipse([hcx-hr*2.4-int(2*S), hcy-s*0.14, hcx-hr*2.2+int(2*S), hcy+s*0.06], fill=col)
        # crown
        if k > 0.6:
            kk3 = min(1.0, (k-0.6)/0.25)
            partial_poly(d, [(hcx-hr*0.7, hcy-hr*1.05), (hcx-hr*0.2, hcy-hr*1.45),
                             (hcx+hr*0.3, hcy-hr*1.05), (hcx+hr*0.5, hcy-hr*1.30)], kk3, col, max(2, w-2))
        # eye
        if k > 0.7:
            d.ellipse([hcx+hr*0.15-4*S, hcy-hr*0.25-4*S, hcx+hr*0.15+4*S, hcy-hr*0.25+4*S], fill=col)
        # dorsal fin zigzag
        if k > 0.75:
            kk4 = min(1.0, (k-0.75)/0.25)
            partial_poly(d, [(cx+s*0.30, cy-s*0.28), (cx+s*0.50, cy-s*0.16), (cx+s*0.38, cy-s*0.04),
                             (cx+s*0.54, cy+s*0.10), (cx+s*0.36, cy+s*0.22)], kk4, col, max(2, w-2))

def el_neurons(d, e, k):
    cx, cy, s = e["cx"]*W*S, e["cy"]*H*S, e["s"]*H*S*2
    col, w = COLORS[e["color"]], int(4*S)
    nodes = [(-0.7,-0.55),(0.1,-0.8),(0.75,-0.45),(0.9,0.25),(0.2,0.0),(-0.15,0.65),(0.65,0.85),(-0.8,0.1),(0.0,-0.2)]
    edges = [(0,4),(1,4),(1,2),(2,3),(3,4),(4,5),(5,6),(3,6),(4,8),(7,8),(7,0),(5,7)]
    P = [(cx+nx*s, cy+ny*s) for nx, ny in nodes]
    for i, (a, b) in enumerate(edges):
        kk = max(0.0, min(1.0, (k - i*0.055) / 0.35))
        if kk > 0: partial_poly(d, [P[a], P[b]], kk, col, w)
    for i, p in enumerate(P):
        kk = max(0.0, min(1.0, (k - i*0.05) / 0.25))
        if kk > 0:
            r = int(9*S*min(1.0, kk*2))
            d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], outline=col, width=max(2, w-1))

def el_bubble(d, e, k):
    cx, cy, s = e["cx"]*W*S, e["cy"]*H*S, e["s"]*H*S*2
    col, w = COLORS[e["color"]], int(5*S)
    box = [cx-s, cy-s*0.55, cx+s, cy+s*0.55]
    pellipse(d, box, k, col, w)
    if k > 0.5: partial_poly(d, [(cx+s*0.35, cy+s*0.5), (cx+s*0.1, cy+s*0.9)], min(1,(k-0.5)/0.3), col, w)
    if k > 0.6:
        qf = ImageFont.truetype(FB, int(s*0.9))
        partial_text(d, cx, cy, "?", qf, WHITE, min(1,(k-0.6)/0.4))

def el_heart(d, e, k):
    cx, cy, s = e["cx"]*W*S, e["cy"]*H*S, e["s"]*H*S*2
    col, w = COLORS[e["color"]], int(6*S)
    pellipse(d, [cx-s*0.7, cy-s*0.7, cx-s*0.02, cy-s*0.05], min(1, k/0.5), col, w)
    pellipse(d, [cx-s*0.02, cy-s*0.7, cx+s*0.66, cy-s*0.05], min(1, max(0, k-0.15)/0.5), col, w)
    if k > 0.45:
        kk = (k-0.45)/0.55
        partial_poly(d, [(cx-s*0.68, cy-s*0.2), (cx, cy+s*0.75)], kk, col, w)
        partial_poly(d, [(cx+s*0.64, cy-s*0.2), (cx, cy+s*0.75)], kk, col, w)

def el_bolt(d, e, k):
    cx, cy, s = e["cx"]*W*S, e["cy"]*H*S, e["s"]*H*S*2
    col, w = COLORS[e["color"]], int(5*S)
    pts = [(cx+s*0.3, cy-s), (cx-s*0.25, cy+s*0.1), (cx+s*0.05, cy+s*0.1), (cx-s*0.3, cy+s)]
    partial_poly(d, pts, k, col, w)

def el_tower(d, e, k):
    cx, cy, s = e["cx"]*W*S, e["cy"]*H*S, e["s"]*H*S*2
    col, w = COLORS[e["color"]], int(5*S)
    # stacked blocks
    levels = 5
    for i in range(levels):
        kk = max(0.0, min(1.0, (k - i*0.09) / 0.25))
        if kk <= 0: continue
        y1 = cy + s*0.9 - i*s*0.4
        half = s*0.45
        pts = [(cx-half, y1), (cx+half, y1), (cx+half, y1-s*0.36), (cx-half, y1-s*0.36), (cx-half, y1)]
        partial_poly(d, pts, kk, col, w)
    # scaffold on side
    if k > 0.55:
        kk = (k-0.55)/0.45
        x0, top, bot = cx+s*0.75, cy-s*1.15, cy+s*0.9
        partial_poly(d, [(x0, bot), (x0, top)], kk, TEAL, w)
        for i in range(3):
            partial_poly(d, [(x0, bot-i*s*0.5), (cx+s*0.42, bot-i*s*0.5)], max(0.0, kk-0.2*i/2), TEAL, max(2, w-2))

def el_frame(d, e, k):
    cx, cy, s = e["cx"]*W*S, e["cy"]*H*S, e["s"]*H*S*2
    col, w = COLORS[e["color"]], int(5*S)
    pts = [(cx-s, cy-s*0.8), (cx+s, cy-s*0.8), (cx+s, cy+s*0.8), (cx-s, cy+s*0.8), (cx-s, cy-s*0.8)]
    partial_poly(d, pts, k, col, w)
    if k > 0.3:
        kk = (k-0.3)/0.7
        half = s*0.72
        pts = [(cx-half, cy-half*0.78), (cx+half, cy-half*0.78), (cx+half, cy+half*0.78), (cx-half, cy+half*0.78), (cx-half, cy-half*0.78)]
        partial_poly(d, pts, kk, DIM, max(2, w-2))

def el_qm(d, e, k):
    cx, cy, s = e["cx"]*W*S, e["cy"]*H*S, e["s"]*H*S*2
    qf = ImageFont.truetype(FB, int(s*2.2))
    partial_text(d, cx, cy, "?", qf, COLORS[e["color"]], k)

def el_sparkle(d, e, k):
    if k <= 0: return
    cx, cy, s = e["cx"]*W*S, e["cy"]*H*S, e["s"]*H*S*2
    col, w = COLORS[e["color"]], int(4*S)
    r = s*min(1.0, k*2)
    d.line([cx-r, cy, cx+r, cy], fill=col, width=w)
    d.line([cx, cy-r, cx, cy+r], fill=col, width=w)
    rr = r*0.45
    d.line([cx-rr, cy-rr, cx+rr, cy+rr], fill=col, width=max(2, w-1))
    d.line([cx+rr, cy-rr, cx-rr, cy+rr], fill=col, width=max(2, w-1))

def el_caption(d, e, k):
    if k <= 0: return
    f = ImageFont.truetype(FB, int(58*S))
    partial_text(d, W*S/2, H*S*0.88, e["text"], f, COLORS[e["color"]], k)

def el_label(d, e, k):
    if k <= 0: return
    f = ImageFont.truetype(FB, int(40*S))
    partial_text(d, W*S/2, H*S*0.88, e["text"], f, COLORS[e["color"]], k)

ELEMENTS = {"brain": el_brain, "baby": el_baby, "waves": el_waves, "mobile": el_mobile,
            "arrow": el_arrow, "cabinet": el_cabinet, "seahorse": el_seahorse,
            "neurons": el_neurons, "bubble": el_bubble, "heart": el_heart, "bolt": el_bolt,
            "tower": el_tower, "frame": el_frame, "qm": el_qm, "sparkle": el_sparkle,
            "caption": el_caption, "label": el_label}

def render_scene(scene):
    sid = scene["id"]
    dur = max(durations[sid] + 1.0, 4.0)
    nframes = int(round(dur * FPS))
    outdir = f"{BASE}/frames/{sid}"
    os.makedirs(outdir, exist_ok=True)
    for fi in range(nframes):
        p = fi / (nframes - 1)
        img = Image.new("RGB", SS, BG)
        d = ImageDraw.Draw(img)
        # subtle dotted texture
        step = 110*S
        for gx in range(step//2, SS[0], step):
            for gy in range(step//2, SS[1], step):
                d.ellipse([gx-int(2*S), gy-int(2*S), gx+int(2*S), gy+int(2*S)], fill=DIM)
        for el in scene["elements"]:
            e = dict(el)
            t0 = e.pop("t0"); dd = e.pop("dur", 0.35)
            k = max(0.0, min(1.0, (p - t0) / dd))
            e["k"] = k
            ELEMENTS[e["kind"]](d, e, k)
        small = img.resize((W, H), Image.LANCZOS)
        small.save(f"{outdir}/{fi:04d}.png", optimize=False)
    return sid, nframes, dur

if __name__ == "__main__":
    import time
    t0 = time.time()
    with Pool(8) as pool:
        for sid, n, dur in pool.imap_unordered(render_scene, scenes):
            print(f"{sid}: {n} frames, {dur:.1f}s  [{time.time()-t0:.1f}s]")
    total_frames = sum(int(round(max(durations[s['id']]+1.0, 4.0)*FPS)) for s in scenes)
    print(f"DONE: {total_frames} frames in {time.time()-t0:.1f}s")
