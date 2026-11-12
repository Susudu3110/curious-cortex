#!/usr/bin/env python3
"""Video 1 thumbnail: 'AGE 3: DELETED' — baby + brain doodle."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os

OUT = os.path.expanduser("~/YouTube/CuriousCortex/video1/exports")
BG, PINK, YELLOW, WHITE, TEAL = (13,15,30), (255,93,162), (255,214,90), (245,245,250), (90,220,210)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
S = 2

img = Image.new("RGB", (1280*S, 720*S), BG)
d = ImageDraw.Draw(img)
for gx in range(55*S//2, 1280*S, 55*S):
    for gy in range(55*S//2, 720*S, 55*S):
        d.ellipse([gx-2*S, gy-2*S, gx+2*S, gy+2*S], fill=(30,34,60))
glow = Image.new("RGB", img.size, BG)
gd = ImageDraw.Draw(glow)
gd.ellipse([600*S, 100*S, 1400*S, 800*S], fill=(110,28,66))
img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(80*S)), 0.5)
d = ImageDraw.Draw(img)

def partial_poly(dd, pts, k, color, w):
    import math
    L = sum(math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1))
    if k <= 0: return
    target, acc = L*k, 0.0
    for i in range(len(pts)-1):
        seg = math.dist(pts[i], pts[i+1])
        if acc + seg >= target:
            f = (target-acc)/seg
            dd.line([pts[i], (pts[i][0]+(pts[i+1][0]-pts[i][0])*f, pts[i][1]+(pts[i+1][1]-pts[i][1])*f)], fill=color, width=w)
            break
        dd.line([pts[i], pts[i+1]], fill=color, width=w)
        acc += seg

# baby head (left, teal)
bx, by, bs = 300*S, 330*S, 210*S
w = int(11*S)
d.ellipse([bx-bs*0.8, by-bs*0.85, bx+bs*0.8, by+bs*0.9], outline=TEAL, width=w)
d.line([(bx, by-bs*0.85), (bx+bs*0.12, by-bs*1.05), (bx-bs*0.08, by-bs*1.12), (bx+bs*0.06, by-bs*1.3)], fill=TEAL, width=int(7*S))  # curl
for ex in (-0.32, 0.32):
    r = int(9*S)
    d.ellipse([bx+ex*bs-r, by-bs*0.18-r, bx+ex*bs+r, by-bs*0.18+r], fill=TEAL)
partial_poly(d, [(bx-bs*0.28, by+bs*0.3), (bx, by+bs*0.44), (bx+bs*0.28, by+bs*0.3)], 1.0, TEAL, int(7*S))
# erase streaks from baby toward right (being deleted)
for i, (y0, y1) in enumerate([(-0.4, -0.15), (0.0, 0.05), (0.35, 0.6)]):
    x0 = bx + bs*(0.9 + i*0.25)
    x1 = x0 + bs*0.5
    d.line([(x0, by+bs*y0), (x1, by+bs*y1)], fill=(90,220,210) if i%2 else (255,214,90), width=int(6*S))
    d.line([(x0+bs*0.08, by+bs*y0-bs*0.12), (x1+bs*0.08, by+bs*y1-bs*0.12)], fill=PINK, width=int(6*S))

# brain (right, half-fading with trash can)
cx, cy, s = 950*S, 300*S, 240*S
d.ellipse([cx-s, cy-s*0.72, cx+s*0.95, cy+s*0.72], outline=PINK, width=w)
d.line([(cx-s*0.02, cy-s*0.72), (cx-s*0.02, cy+s*0.4)], fill=PINK, width=int(7*S))
for y1, y2 in [(-0.5, -0.25), (-0.15, 0.05), (0.2, 0.3)]:
    d.line([(cx-s*0.55, cy+y1*s), (cx-s*0.25, cy+y2*s)], fill=PINK, width=int(5*S))
    d.line([(cx+s*0.3, cy+y1*s), (cx+s*0.6, cy+y2*s)], fill=PINK, width=int(5*S))
d.ellipse([cx+s*0.18, cy+s*0.42, cx+s*0.82, cy+s*0.88], outline=PINK, width=int(8*S))
d.line([(cx+s*0.5, cy+s*0.88), (cx+s*0.5, cy+s*1.12)], fill=PINK, width=w)

# trash can icon top-right of brain
tx, ty, ts = cx+s*0.85, cy-s*0.95, 70*S
d.rectangle([tx-ts*0.5, ty-ts*0.1, tx+ts*0.5, ty-ts*0.02], fill=YELLOW)
d.line([(tx-ts*0.42, ty), (tx-ts*0.3, ty+ts*0.9), (tx+ts*0.3, ty+ts*0.9), (tx+ts*0.42, ty)], fill=YELLOW, width=int(6*S))
d.line([(tx-ts*0.18, ty+ts*0.15), (tx-ts*0.14, ty+ts*0.7)], fill=BG, width=int(4*S))
d.line([(tx+ts*0.18, ty+ts*0.15), (tx+ts*0.14, ty+ts*0.7)], fill=BG, width=int(4*S))

def text_center(dd, cx2, cy2, text, f, fill):
    b = dd.textbbox((0,0), text, font=f)
    dd.text((cx2-(b[2]-b[0])/2-b[0], cy2-(b[3]-b[1])/2-b[1]), text, font=f, fill=fill)

f1 = ImageFont.truetype(FB, 120*S)
text_center(d, 640*S, 610*S, "AGE 3: DELETED", f1, WHITE)
f2 = ImageFont.truetype(FB, 46*S)
text_center(d, 640*S, 672*S, "why you can't remember being a baby", f2, TEAL)

img = img.resize((1280, 720), Image.LANCZOS)
img.save(f"{OUT}/thumbnail_video1.png", optimize=True)
print("saved", f"{OUT}/thumbnail_video1.png")
