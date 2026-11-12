#!/usr/bin/env python3
# Thumbnail for video 2: x-ray brain frame + big text (Curious Cortex look).
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

BASE = os.path.expanduser('~/faceless-shorts/3am-cringe')
img = Image.open(f'{BASE}/review/thumb_brain.jpg').convert('RGB')  # t=14.2, x-ray brain glowing

# crop away the baked-in caption zone, zoom on head+brain
W0, H0 = img.size
img = img.crop((0, 120, W0, 1400))
s = 1920 / 1280
img = img.resize((int(W0 * s), 1920), Image.LANCZOS)
x0 = (img.width - 1080) // 2
img = img.crop((x0, 0, x0 + 1080, 1920))

# slight dark vignette so text pops
W, H = img.size
vig = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(vig)
d.ellipse([-W * 0.3, -H * 0.25, W * 1.3, H * 1.05], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(160))
img = Image.composite(img, Image.new('RGB', (W, H), (10, 14, 28)), vig)

dr = ImageDraw.Draw(img)
def font(sz, bold=True):
    p = os.path.expanduser(f'~/faceless-shorts/3am-cringe/fonts/Inter-{"Black" if bold else "ExtraBold"}.otf')
    return ImageFont.truetype(p, sz)

def outline_text(xy, text, f, fill, oc=(17, 17, 17), ow=14, anchor='mm'):
    x, y = xy
    for dx in (-ow, 0, ow):
        for dy in (-ow, 0, ow):
            if dx or dy: dr.text((x + dx, y + dy), text, font=f, fill=oc, anchor=anchor)
    dr.text(xy, text, font=f, fill=fill, anchor=anchor)

# shrink-to-fit helper
def fit(text, maxw, start):
    sz = start
    while sz > 40 and dr.textlength(text, font=font(sz)) > maxw: sz -= 4
    return font(sz)

# top kicker
outline_text((W / 2, 170), 'YOUR BRAIN AT', fit('YOUR BRAIN AT', 940, 120), (255, 255, 255))
# giant 3 AM
dr.text((W / 2, 330), '3 AM', font=font(300), fill=(255, 212, 59), anchor='mm',
        stroke_width=22, stroke_fill=(17, 17, 17))
# bottom hook
outline_text((W / 2, 1700), 'THE CRINGE MACHINE', fit('THE CRINGE MACHINE', 940, 110), (255, 255, 255))

img.save(os.path.expanduser('~/YouTube/CuriousCortex/video2-3am-cringe/thumbnail.jpg'), quality=92)
print('saved thumbnail.jpg', img.size)
