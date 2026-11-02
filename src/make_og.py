#!/usr/bin/env python3
"""Megosztási kép (1200×630) a Melóradarhoz. Egyszer kell futtatni: python3 src/make_og.py <Montserrat.ttf>"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

font_path = sys.argv[1]
W, H = 1200, 630
img = Image.new("RGB", (W, H), "#232c3c")
px = img.load()
for y in range(H):  # tinta átmenet
    t = y / H
    r = int(0x32 + (0x23 - 0x32) * t); g = int(0x3c + (0x2c - 0x3c) * t); b = int(0x50 + (0x3c - 0x50) * t)
    for x in range(W):
        px[x, y] = (r, g, b)
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
d.ellipse((780, -260, 1460, 420), fill=(55, 175, 240, 34))
d.ellipse((960, 300, 1340, 680), fill=(80, 215, 190, 40))
img = Image.alpha_composite(img.convert("RGBA"), ov)
d = ImageDraw.Draw(img)

def font(size, weight):
    f = ImageFont.truetype(font_path, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f

# márkacsempe
tile = Image.new("RGBA", (112, 112))
tp = tile.load()
for x in range(112):
    t = x / 111
    c = (int(0x50 + (0x37 - 0x50) * t), int(0xd7 + (0xaf - 0xd7) * t), int(0xbe + (0xf0 - 0xbe) * t), 255)
    for y in range(112):
        tp[x, y] = c
mask = Image.new("L", (112, 112), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, 111, 111), 30, fill=255)
img.paste(tile, (88, 96), mask)
cx, cy = 144, 152
d.arc((cx-42, cy-42, cx+42, cy+42), -90, 315 - 360 + 360 - 45, fill="white", width=7)
d.arc((cx-24, cy-24, cx+24, cy+24), -90, 270, fill="white", width=7)
d.ellipse((cx-7, cy-7, cx+7, cy+7), fill="white")
d.line((cx+5, cy-5, cx+34, cy-34), fill="white", width=7)

d.text((88, 250), "Melóradar", font=font(112, "ExtraBold"), fill="white")
d.text((92, 392), "a világ munkaerőpiaca, rád szabva", font=font(40, "SemiBold"), fill="#8fe6d5")
d.text((92, 470), "Napi hírek, és hogy mit jelentenek neked itthon", font=font(30, "Medium"), fill="#dde3eb")
d.rectangle((92, 540, 92 + 120, 546), fill="#50d7be")
out = Path(__file__).resolve().parent / "og.png"
img.convert("RGB").save(out, optimize=True)
print("Mentve:", out)
