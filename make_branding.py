#!/usr/bin/env python3
"""Curious Cortex channel art v2: thumbnail, logo, banner (clean doodle style)."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os

OUT = os.path.expanduser("~/YouTube/CuriousCortex/branding")
os.makedirs(OUT, exist_ok=True)

BG     = (13, 15, 30)
PINK   = (255, 93, 162)
YELLOW = (255, 214, 90)
WHITE  = (245, 245, 250)
TEAL   = (90, 220, 210)
DIM    = (30, 34, 60)

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(sz): return ImageFont.truetype(FB, sz)

def fit_font(draw, text, max_w, start_sz):
    """Shrink font until text fits max_w."""
    sz = start_sz
    while sz > 10:
        f = font(sz)
        w = draw.textbbox((0, 0), text, font=f)[2]
        if w <= max_w:
            return f
        sz -= 4
    return font(10)

def text_center(draw, cx, cy, text, f, fill):
    b = draw.textbbox((0, 0), text, font=f)
    draw.text((cx - (b[2]-b[0])/2 - b[0], cy - (b[3]-b[1])/2 - b[1]), text, font=f, fill=fill)

def doodle_brain(d, cx, cy, s, color, w):
    """Clean cute brain: rounded blob outline + folds + cerebellum + stem."""
    pad = int(s*0.1)
    # main lobe
    d.ellipse([cx-s, cy-s*0.72, cx+s*0.95, cy+s*0.72], outline=color, width=w)
    # cerebellum
    d.ellipse([cx+s*0.18, cy+s*0.42, cx+s*0.82, cy+s*0.88], outline=color, width=max(2, w-2))
    # stem
    d.line([cx+s*0.5, cy+s*0.88, cx+s*0.5, cy+s*1.12], fill=color, width=w)
    # central divide
    d.line([cx-s*0.02, cy-s*0.72, cx-s*0.02, cy+s*0.4], fill=color, width=max(2, w-2))
    # folds
    for y1, y2 in [(-0.5, -0.25), (-0.15, 0.05), (0.2, 0.3)]:
        d.line([cx-s*0.55, cy+y1*s, cx-s*0.25, cy+y2*s], fill=color, width=max(2, w-4))
        d.line([cx+s*0.3, cy+y1*s, cx+s*0.6, cy+y2*s], fill=color, width=max(2, w-4))
    # synapse dots
    for dx, dy in [(-0.95, 0.55), (0.95, -0.6)]:
        r = w
        d.ellipse([cx+dx*s-r, cy+dy*s-r, cx+dx*s+r, cy+dy*s+r], fill=color)

def sparkle(d, cx, cy, r, color, w):
    d.line([cx-r, cy, cx+r, cy], fill=color, width=w)
    d.line([cx, cy-r, cx, cy+r], fill=color, width=w)
    d.line([cx-r*0.45, cy-r*0.45, cx+r*0.45, cy+r*0.45], fill=color, width=max(2, w-2))
    d.line([cx+r*0.45, cy-r*0.45, cx-r*0.45, cy+r*0.45], fill=color, width=max(2, w-2))

def dotted_grid(d, W, H, step):
    for gx in range(step//2, W, step):
        for gy in range(step//2, H, step):
            d.ellipse([gx-2, gy-2, gx+2, gy+2], fill=DIM)

S = 2  # supersampling

# ============ THUMBNAIL 1280x720 ============
W, H = 1280*S, 720*S
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
dotted_grid(d, W, H, 55*S)
# pink glow bottom-left
glow = Image.new("RGB", (W, H), BG)
gd = ImageDraw.Draw(glow)
gd.ellipse([-200*S, 350*S, 700*S, 1000*S], fill=(110, 28, 66))
img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(70*S)), 0.5)
d = ImageDraw.Draw(img)

doodle_brain(d, 330*S, 270*S, 175*S, PINK, 11*S)
sparkle(d, 560*S, 120*S, 24*S, YELLOW, 7*S)
sparkle(d, 90*S, 520*S, 16*S, TEAL, 5*S)

# big question mark right side
q = fit_font(d, "?", 300*S, 420*S)
d.text((880*S, 90*S), "?", font=q, fill=YELLOW)

# headline (bottom band)
f1 = fit_font(d, "CURIOUS CORTEX", 640*S, 92*S)
text_center(d, 640*S, 600*S, "CURIOUS CORTEX", f1, WHITE)
f2 = fit_font(d, "why your brain does weird things", 620*S, 46*S)
text_center(d, 640*S, 668*S, "why your brain does weird things", f2, TEAL)

img = img.resize((1280, 720), Image.LANCZOS)
img.save(f"{OUT}/thumbnail_channel.png", optimize=True)

# ============ LOGO 800x800 ============
W = H = 800*S
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
dotted_grid(d, W, H, 60*S)
d.rounded_rectangle([80*S, 80*S, 720*S, 720*S], radius=90*S, outline=PINK, width=13*S)
doodle_brain(d, 400*S, 350*S, 150*S, PINK, 12*S)
sparkle(d, 590*S, 180*S, 22*S, YELLOW, 6*S)
f = fit_font(d, "CC", 300*S, 130*S)
text_center(d, 400*S, 610*S, "CC", f, WHITE)
img = img.resize((800, 800), Image.LANCZOS)
img.save(f"{OUT}/logo_800.png", optimize=True)

# ============ BANNER 2048x1152 (safe zone: center 1546x423) ============
W, H = 2048*S, 1152*S
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
dotted_grid(d, W, H, 70*S)
doodle_brain(d, 280*S, 480*S, 130*S, PINK, 10*S)
doodle_brain(d, 1790*S, 660*S, 115*S, TEAL, 9*S)
sparkle(d, 470*S, 300*S, 20*S, YELLOW, 6*S)
sparkle(d, 1650*S, 430*S, 15*S, PINK, 5*S)

f1 = fit_font(d, "CURIOUS CORTEX", 1200*S, 150*S)
text_center(d, 1024*S, 505*S, "CURIOUS CORTEX", f1, WHITE)
f2 = fit_font(d, "why your brain does weird things", 1000*S, 56*S)
text_center(d, 1024*S, 625*S, "why your brain does weird things", f2, TEAL)

img = img.resize((2048, 1152), Image.LANCZOS)
img.save(f"{OUT}/banner_2048x1152.png", optimize=True)

print("done ->", OUT)
