#!/usr/bin/env python3
"""Render the front page of THE WORLD IN ONE PAGE for 21 November 2026.

Draws a newspaper front page (1024x1024) in pure PIL: no network, no
photos, no downloaded assets. Every map, ship and chart is drawn from
vector primitives in this file, so the output is deterministic: run it
three times and the bytes are identical.

Stories: 36, across 9 regions. The five core stories were checked
against live news reporting on 22 November 2026; the rest appear in
at least two of the day's top-ranked entries and in the named outlets.
Nothing here is invented: figures are as first reported, claims are
labelled CLAIM, and the DATE CHECK box says what was left out and why.
"""

import hashlib
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
PAPER_DARK = (238, 232, 214)
INK = (17, 17, 17)
INK_SOFT = (60, 58, 52)
RED = (178, 34, 34)
RED_DARK = (139, 0, 0)
BLUE = (31, 78, 121)
SEA = (198, 220, 232)
LAND = (232, 220, 184)
LAND_DARK = (214, 198, 158)
GREEN = (36, 110, 60)
GOLD = (176, 141, 42)
GREY = (120, 118, 110)
RULE = (90, 86, 76)

REGION_COLORS = {
    "Europe": (31, 78, 121),
    "Middle East": (178, 34, 34),
    "Americas": (36, 110, 60),
    "Africa": (176, 141, 42),
    "South Asia": (124, 58, 120),
    "East Asia": (178, 90, 20),
    "South-East Asia": (0, 128, 128),
    "Oceania": (90, 90, 160),
    "Global": (60, 60, 60),
}

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype"
SERIF_B = f"{FD}/liberation/LiberationSerif-Bold.ttf"
SERIF = f"{FD}/liberation/LiberationSerif-Regular.ttf"
SERIF_I = f"{FD}/liberation/LiberationSerif-Italic.ttf"
SANS_B = f"{FD}/liberation/LiberationSans-Bold.ttf"
SANS = f"{FD}/liberation/LiberationSans-Regular.ttf"
SANS_I = f"{FD}/liberation/LiberationSans-Italic.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


f_headline = F(SERIF_B, 62)
f_headline_small = F(SERIF_B, 46)
f_hero_head = F(SERIF_B, 20)
f_hero_head2 = F(SERIF_B, 19)
f_small_head = F(SERIF_B, 13)
f_deck = F(SERIF, 11)
f_deck_small = F(SERIF, 10)
f_kicker = F(SANS_B, 9)
f_kicker_sm = F(SANS_B, 8)
f_label = F(SANS_B, 9)
f_label_sm = F(SANS_B, 8)
f_tiny = F(SANS, 8)
f_tiny_b = F(SANS_B, 8)
f_stat = F(SERIF_B, 26)
f_stat_sm = F(SERIF_B, 20)
f_italic = F(SERIF_I, 11)
f_italic_sm = F(SERIF_I, 10)
f_sans = F(SANS, 9)
f_sans_sm = F(SANS, 8)
f_list = F(SANS, 10)
f_list_b = F(SANS_B, 10)
f_num = F(SERIF_B, 13)

# ---------------------------------------------------------------- helpers
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)


def text_wrapped(draw, xy, text, font, max_w, fill=INK, spacing=1):
    """Draw text wrapped to max_w; return the y just below the last line."""
    x, y = xy
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + spacing
    return y


def centered(draw, y, text, font, fill=INK, cx=W // 2):
    w = draw.textlength(text, font=font)
    draw.text((cx - w / 2, y), text, font=font, fill=fill)
    return y + font.size + 2


def hline(y, x0=16, x1=W - 16, fill=RULE, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def badge(draw, x, y, text, fill=GREEN):
    """Small CONFIRMED / OFFICIAL / REPORTED / CLAIM pill."""
    w = draw.textlength(text, font=f_kicker_sm) + 10
    h = 12
    draw.rounded_rectangle([x, y, x + w, y + h], radius=2, fill=fill)
    draw.text((x + 5, y + 1), text, font=f_kicker_sm, fill=(255, 255, 255))
    return x + w


def kicker_line(draw, x, y, num, place, topic, status):
    """'1  BAHRAIN · STRAIT OF HORMUZ · WAR' + status pill on the right."""
    draw.text((x, y), str(num), font=f_num, fill=RED)
    nx = x + 16
    draw.text((nx, y + 1), f"{place} · {topic}", font=f_kicker, fill=INK)
    return y


def source_line(draw, x, y, text, max_x=W - 16):
    draw.text((x, y), text, font=f_tiny, fill=GREY)

# ------------------------------------------------------- hero illustrations
def draw_hormuz(draw, x0, y0, w, h):
    """Strait of Hormuz map: Iran top-right, Gulf below, Bahrain on fire."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA, outline=RULE, width=1)
    # Iran landmass (top right)
    draw.polygon([(x0 + w * 0.52, y0), (x0 + w, y0), (x0 + w, y0 + h * 0.52),
                  (x0 + w * 0.66, y0 + h * 0.44), (x0 + w * 0.58, y0 + h * 0.30)],
                 fill=LAND)
    # Arabian peninsula (bottom left)
    draw.polygon([(x0, y0 + h * 0.62), (x0 + w * 0.42, y0 + h * 0.58),
                  (x0 + w * 0.55, y0 + h), (x0, y0 + h)], fill=LAND)
    # Qatar bump
    draw.polygon([(x0 + w * 0.30, y0 + h * 0.60), (x0 + w * 0.38, y0 + h * 0.56),
                  (x0 + w * 0.40, y0 + h * 0.70), (x0 + w * 0.32, y0 + h * 0.72)],
                 fill=LAND_DARK)
    # Oman (right edge, lower)
    draw.polygon([(x0 + w * 0.86, y0 + h * 0.55), (x0 + w, y0 + h * 0.58),
                  (x0 + w, y0 + h * 0.78), (x0 + w * 0.88, y0 + h * 0.72)],
                 fill=LAND)
    # Strait label + dashed tanker route
    draw.text((x0 + w * 0.60, y0 + h * 0.52), "STRAIT OF", font=f_tiny_b, fill=INK)
    draw.text((x0 + w * 0.60, y0 + h * 0.52 + 10), "HORMUZ", font=f_tiny_b, fill=INK)
    for i in range(9):
        t = i / 8.0
        px = x0 + w * (0.42 + 0.30 * t)
        py = y0 + h * (0.44 + 0.10 * t)
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    # tanker icons (two small hulls)
    for tx, ty in [(x0 + w * 0.78, y0 + h * 0.60), (x0 + w * 0.86, y0 + h * 0.68)]:
        draw.rectangle([tx - 9, ty - 3, tx + 9, ty + 3], fill=(40, 40, 40))
        draw.rectangle([tx - 5, ty - 7, tx + 1, ty - 3], fill=(40, 40, 40))
        draw.polygon([(tx + 9, ty - 3), (tx + 14, ty), (tx + 9, ty + 3)], fill=RED)
    # Bahrain fire burst (left, on the coast)
    bx, by = x0 + w * 0.24, y0 + h * 0.52
    for ang in range(0, 360, 45):
        import math
        r = 13
        ex = bx + r * math.cos(math.radians(ang))
        ey = by + r * math.sin(math.radians(ang))
        draw.line([(bx, by), (ex, ey)], fill=(255, 140, 0), width=3)
    draw.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=RED)
    draw.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(255, 200, 0))
    draw.rounded_rectangle([bx - 34, by + 14, bx + 34, by + 28], radius=2, fill=RED)
    draw.text((bx - 29, by + 16), "SITE ON FIRE", font=f_tiny_b, fill=(255, 255, 255))
    # labels
    draw.text((x0 + w * 0.68, y0 + 6), "IRAN", font=f_label, fill=INK)
    draw.text((x0 + 8, y0 + h - 26), "SAUDI", font=f_tiny_b, fill=INK_SOFT)
    draw.text((x0 + 8, y0 + h - 16), "ARABIA", font=f_tiny_b, fill=INK_SOFT)
    draw.text((x0 + w * 0.30, y0 + h * 0.78), "QATAR", font=f_tiny, fill=INK_SOFT)
    draw.text((x0 + w * 0.86, y0 + h * 0.80), "OMAN", font=f_tiny, fill=INK_SOFT)
    draw.text((x0 + w * 0.42, y0 + h * 0.82), "THE GULF", font=f_tiny_b, fill=BLUE)
    draw.text((x0 + 6, y0 + 6), "BAHRAIN", font=f_label, fill=RED_DARK)


def draw_sparta(draw, x0, y0, w, h):
    """Sparta II cargo ship on fire in the Gulf of Finland."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(24, 32, 44), outline=RULE, width=1)
    # sky glow + smoke
    for i, (sx, sy, sr) in enumerate([(0.42, 0.30, 26), (0.52, 0.22, 30), (0.62, 0.30, 24),
                                     (0.50, 0.12, 22), (0.58, 0.08, 18)]):
        draw.ellipse([x0 + w * sx - sr, y0 + h * sy - sr * 0.7,
                      x0 + w * sx + sr, y0 + h * sy + sr * 0.7],
                     fill=(90, 92, 96))
    # flames on deck
    fx, fy = x0 + w * 0.52, y0 + h * 0.52
    draw.polygon([(fx - 26, fy + 8), (fx - 14, fy - 22), (fx - 4, fy - 2),
                  (fx + 6, fy - 30), (fx + 16, fy - 6), (fx + 26, fy + 8)],
                 fill=(255, 140, 0))
    draw.polygon([(fx - 14, fy + 8), (fx - 6, fy - 12), (fx + 4, fy - 2),
                  (fx + 12, fy - 16), (fx + 16, fy + 8)], fill=(255, 210, 0))
    # sea
    draw.rectangle([x0, y0 + h * 0.62, x0 + w, y0 + h], fill=(38, 68, 96))
    for i in range(6):
        wx = x0 + 12 + i * 52
        draw.line([(wx, y0 + h * 0.70 + (i % 2) * 8), (wx + 26, y0 + h * 0.70 + (i % 2) * 8)],
                  fill=(120, 170, 210), width=2)
    # hull
    draw.polygon([(x0 + w * 0.10, y0 + h * 0.52), (x0 + w * 0.90, y0 + h * 0.52),
                  (x0 + w * 0.84, y0 + h * 0.72), (x0 + w * 0.16, y0 + h * 0.72)],
                 fill=(16, 16, 18))
    draw.rectangle([x0 + w * 0.10, y0 + h * 0.52, x0 + w * 0.90, y0 + h * 0.56],
                   fill=(120, 20, 20))
    # containers
    for i, cx in enumerate([0.16, 0.28, 0.40, 0.62, 0.74]):
        c = [(200, 60, 40), (40, 90, 140), (180, 150, 40), (60, 120, 70), (150, 80, 30)][i]
        draw.rectangle([x0 + w * cx, y0 + h * 0.36, x0 + w * (cx + 0.10), y0 + h * 0.52],
                       fill=c, outline=(20, 20, 20))
    # bridge tower
    draw.rectangle([x0 + w * 0.84, y0 + h * 0.30, x0 + w * 0.90, y0 + h * 0.52],
                   fill=(220, 220, 215), outline=(20, 20, 20))
    # drones with dashed paths
    for dx, dy in [(0.18, 0.14), (0.30, 0.08)]:
        px, py = x0 + w * dx, y0 + h * dy
        draw.line([(px, py), (px + 26, py + 18)], fill=(200, 200, 200), width=1)
        draw.ellipse([px - 4, py - 2, px + 4, py + 2], fill=(220, 220, 220))
        draw.line([(px - 6, py - 4), (px + 6, py + 4)], fill=(220, 220, 220), width=1)
    draw.text((x0 + 8, y0 + h - 40), "06:50 UTC", font=f_label, fill=(255, 255, 255))
    draw.text((x0 + 8, y0 + h - 28), "two drones, taken off", font=f_tiny, fill=(220, 220, 220))
    draw.rounded_rectangle([x0 + w - 108, y0 + h - 24, x0 + w - 6, y0 + h - 8],
                           radius=2, fill=(255, 255, 255))
    draw.text((x0 + w - 103, y0 + h - 22), "SPARTA II", font=f_tiny_b, fill=INK)
    # inset mini-map: Finland / Gulf
    ix, iy, iw, ih = x0 + w - 96, y0 + 8, 88, 44
    draw.rectangle([ix, iy, ix + iw, iy + ih], fill=SEA, outline=(255, 255, 255))
    draw.polygon([(ix + 8, iy + 4), (ix + 52, iy + 4), (ix + 48, iy + ih - 4),
                  (ix + 8, iy + ih - 4)], fill=LAND)
    draw.text((ix + 10, iy + 6), "FINLAND", font=f_tiny, fill=INK)
    draw.text((ix + 56, iy + 26), "RUSSIA", font=f_tiny, fill=INK)
    draw.ellipse([ix + 44, iy + 22, ix + 50, iy + 28], fill=RED)


def draw_cop31(draw, x0, y0, w, h):
    """COP31: November calendar in overtime + 1.5C thermometer + draft text."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(232, 242, 228), outline=RULE, width=1)
    # header
    draw.rectangle([x0, y0, x0 + w, y0 + 26], fill=GREEN)
    draw.text((x0 + 8, y0 + 4), "COP31", font=F(SANS_B, 15), fill=(255, 255, 255))
    draw.text((x0 + 62, y0 + 8), "ANTALYA · UN CLIMATE SUMMIT", font=f_kicker_sm,
              fill=(220, 240, 220))
    draw.text((x0 + w - 92, y0 + 8), "DAY 13 OF 12", font=f_kicker_sm, fill=(255, 255, 255))
    # calendar grid: Nov 9..21
    gx, gy = x0 + 10, y0 + 36
    cw, ch = 22, 20
    days = list(range(9, 22))
    for i, day in enumerate(days):
        cx = gx + (i % 7) * (cw + 3)
        cy = gy + (i // 7) * (ch + 3)
        if day == 21:
            draw.rectangle([cx, cy, cx + cw, cy + ch], fill=RED)
            draw.text((cx + 5, cy + 3), "21", font=f_tiny_b, fill=(255, 255, 255))
        else:
            draw.rectangle([cx, cy, cx + cw, cy + ch], fill=(255, 255, 255),
                           outline=(150, 150, 140))
            draw.text((cx + 5, cy + 3), str(day), font=f_tiny, fill=INK)
    draw.text((gx, gy + 2 * (ch + 3) + 4), "NOV 9–20 SCHEDULED", font=f_tiny, fill=GREY)
    draw.text((gx + 118, gy + 2 * (ch + 3) + 4), "+1 DAY", font=f_tiny_b, fill=RED)
    # thermometer
    tx = x0 + w - 56
    ty = y0 + 40
    draw.rounded_rectangle([tx + 12, ty, tx + 22, ty + 62], radius=8,
                           outline=RED, width=2, fill=(255, 255, 255))
    draw.ellipse([tx + 6, ty + 56, tx + 28, ty + 80], fill=RED)
    draw.rectangle([tx + 15, ty + 34, tx + 19, ty + 62], fill=RED)
    draw.text((tx - 8, ty + 84), "1.5°C", font=f_tiny_b, fill=RED_DARK)
    # draft text box
    bx, by = x0 + 10, y0 + h - 52
    draw.rectangle([bx, by, x0 + w - 10, by + 42], fill=(255, 255, 255),
                   outline=(150, 150, 140))
    draw.text((bx + 8, by + 4), "DRAFT TEXT", font=f_kicker_sm, fill=GREY)
    draw.text((bx + 8, by + 18), "fossil fuels", font=F(SERIF_B, 13), fill=INK)
    draw.line([(bx + 8, by + 26), (bx + 78, by + 26)], fill=RED, width=2)
    draw.text((bx + 86, by + 20), "no mention", font=f_tiny, fill=RED_DARK)
    draw.text((bx + 86, by + 30), "in the draft", font=f_tiny, fill=RED_DARK)
    # overtime clock
    ox, oy = x0 + w - 66, y0 + h - 52
    draw.ellipse([ox, oy, ox + 40, oy + 40], outline=INK, width=2, fill=(255, 255, 255))
    draw.line([(ox + 20, oy + 20), (ox + 20, oy + 6)], fill=INK, width=2)
    draw.line([(ox + 20, oy + 20), (ox + 32, oy + 24)], fill=INK, width=2)
    draw.text((ox - 4, oy + 42), "OVERTIME", font=f_tiny_b, fill=RED)

# ---------------------------------------------------------- small icons
def icon_quake(draw, x, y, s=62):
    draw.rectangle([x, y, x + s, y + s], fill=(245, 235, 210), outline=RULE)
    pts = [(x + 4, y + s * 0.55), (x + 14, y + s * 0.55), (x + 20, y + s * 0.25),
           (x + 28, y + s * 0.80), (x + 36, y + s * 0.35), (x + 44, y + s * 0.55),
           (x + 58, y + s * 0.55)]
    draw.line(pts, fill=RED, width=2)
    draw.text((x + 6, y + 4), "M6.7", font=F(SERIF_B, 13), fill=INK)
    draw.text((x + 6, y + s - 14), "108 KM", font=f_tiny_b, fill=GREY)


def icon_cuffs(draw, x, y, s=62):
    draw.rectangle([x, y, x + s, y + s], fill=(232, 238, 244), outline=RULE)
    draw.ellipse([x + 10, y + 22, x + 28, y + 40], outline=INK, width=3)
    draw.ellipse([x + 34, y + 22, x + 52, y + 40], outline=INK, width=3)
    draw.line([(x + 28, y + 31), (x + 34, y + 31)], fill=INK, width=3)
    draw.text((x + 6, y + 4), "11 DEAD", font=f_tiny_b, fill=RED_DARK)
    draw.text((x + 6, y + s - 14), "FBI TOP TEN", font=f_tiny, fill=GREY)


def icon_robot(draw, x, y, s=62):
    draw.rectangle([x, y, x + s, y + s], fill=(238, 238, 238), outline=RULE)
    draw.rectangle([x + 16, y + 14, x + 46, y + 42], fill=(200, 205, 210),
                   outline=INK, width=2)
    draw.ellipse([x + 23, y + 22, x + 29, y + 28], fill=RED)
    draw.ellipse([x + 33, y + 22, x + 39, y + 28], fill=RED)
    draw.line([(x + 24, y + 34), (x + 38, y + 34)], fill=INK, width=2)
    draw.line([(x + 22, y + 14), (x + 22, y + 8)], fill=INK, width=2)
    draw.line([(x + 40, y + 14), (x + 40, y + 8)], fill=INK, width=2)
    draw.text((x + 6, y + 46), "DRAFT BY", font=f_tiny, fill=GREY)
    draw.text((x + 6, y + s - 14), "2028", font=F(SERIF_B, 13), fill=INK)


def icon_mercury(draw, x, y, s=62):
    draw.rectangle([x, y, x + s, y + s], fill=(16, 20, 30), outline=RULE)
    draw.ellipse([x + 6, y + 8, x + 56, y + 34], outline=(150, 160, 180), width=1)
    draw.ellipse([x + 24, y + 20, x + 40, y + 36], fill=(180, 170, 150))
    draw.ellipse([x + 44, y + 12, x + 50, y + 18], fill=(220, 220, 220))
    draw.text((x + 6, y + 40), "18:24", font=F(SERIF_B, 13), fill=(255, 255, 255))
    draw.text((x + 6, y + s - 14), "ESA · JAXA", font=f_tiny, fill=(205, 205, 205))


def icon_trade(draw, x, y, s=62):
    draw.rectangle([x, y, x + s, y + s], fill=(232, 238, 244), outline=RULE)
    draw.ellipse([x + 8, y + 8, x + 28, y + 28], fill=BLUE)
    for i in range(8):
        import math
        ax = x + 18 + 7 * math.cos(i * math.pi / 4)
        ay = y + 18 + 7 * math.sin(i * math.pi / 4)
        draw.ellipse([ax - 1, ay - 1, ax + 1, ay + 1], fill=(255, 220, 0))
    draw.rectangle([x + 34, y + 8, x + 54, y + 28], fill=(255, 255, 255), outline=RED)
    draw.rectangle([x + 34, y + 8, x + 54, y + 18], fill=RED)
    draw.text((x + 6, y + 34), "90.4%", font=F(SERIF_B, 15), fill=INK)
    draw.text((x + 6, y + s - 14), "DUTY-FREE", font=f_tiny_b, fill=GREY)


def icon_boat(draw, x, y, s=62):
    draw.rectangle([x, y, x + s, y + s], fill=(198, 220, 232), outline=RULE)
    draw.polygon([(x + 10, y + 40), (x + 52, y + 40), (x + 44, y + 50),
                  (x + 18, y + 50)], fill=(60, 60, 60))
    draw.rectangle([x + 26, y + 26, x + 36, y + 40], fill=(120, 60, 40))
    draw.line([(x + 6, y + 54), (x + 56, y + 54)], fill=BLUE, width=2)
    draw.text((x + 6, y + 4), "24", font=F(SERIF_B, 16), fill=INK)
    draw.text((x + 28, y + 8), "DEAD", font=f_tiny_b, fill=RED_DARK)


def icon_bottle(draw, x, y, s=62):
    draw.rectangle([x, y, x + s, y + s], fill=(245, 235, 210), outline=RULE)
    draw.rectangle([x + 24, y + 10, x + 38, y + 44], fill=(90, 70, 40), outline=INK)
    draw.rectangle([x + 27, y + 4, x + 35, y + 10], fill=(90, 70, 40))
    draw.polygon([(x + 44, y + 8), (x + 56, y + 30), (x + 32, y + 30)], fill=(255, 200, 0),
                 outline=INK)
    draw.text((x + 43, y + 16), "!", font=F(SANS_B, 12), fill=INK)
    draw.text((x + 6, y + 46), "11 DEAD", font=f_tiny_b, fill=RED_DARK)


def icon_rugby(draw, x, y, s=62):
    draw.rectangle([x, y, x + s, y + s], fill=(30, 90, 50), outline=RULE)
    draw.ellipse([x + 10, y + 14, x + 52, y + 40], fill=(200, 170, 90), outline=(255, 255, 255))
    draw.line([(x + 31, y + 14), (x + 31, y + 40)], fill=(255, 255, 255), width=2)
    draw.text((x + 6, y + 44), "37–12", font=F(SERIF_B, 14), fill=(255, 255, 255))


def icon_march(draw, x, y, s=62):
    draw.rectangle([x, y, x + s, y + s], fill=(238, 232, 214), outline=RULE)
    for i, px in enumerate([12, 24, 36, 48]):
        draw.ellipse([x + px, y + 14, x + px + 8, y + 22], fill=INK)
        draw.rectangle([x + px + 1, y + 22, x + px + 7, y + 44], fill=INK)
    draw.rectangle([x + 6, y + 48, x + 56, y + 50], fill=INK)
    draw.text((x + 6, y + 4), "82,500", font=F(SERIF_B, 13), fill=INK)
    draw.text((x + 6, y + s - 12), "MARCHERS", font=f_tiny_b, fill=GREY)


ICONS = {
    "quake": icon_quake, "cuffs": icon_cuffs, "robot": icon_robot,
    "mercury": icon_mercury, "trade": icon_trade, "boat": icon_boat,
    "bottle": icon_bottle, "rugby": icon_rugby, "march": icon_march,
}

# ------------------------------------------------------------------- data
# (num, region, place, topic, status, headline, deck, source, icon)
SMALL = [
    (4, "Americas", "JUNÍN, PERU · QUAKE", "OFFICIAL",
     "Deep 6.7 quake shakes central Peru",
     "Centred near Ondores and felt in Lima; landslides and minor damage, no deaths.",
     "USGS · IGP · AFP · Anadolu", "quake"),
    (5, "Americas", "SINALOA, MEXICO · CRIME", "CONFIRMED",
     "Mexico captures cartel boss 'El Chapo Isidro'",
     "FBI most-wanted, seized in Guasave. 11 dead in the raid that followed.",
     "AP · Al Jazeera · Mexican defence ministry", "cuffs"),
    (6, "Global", "GENEVA · ARMS CONTROL", "CONFIRMED",
     "128 nations back 'killer robot' talks",
     "US, Russia, Israel opposed binding rules. Draft rules due by 2028.",
     "AFP · Anadolu · Al Jazeera", "robot"),
    (7, "Global", "MERCURY · SCIENCE", "OFFICIAL",
     "BepiColombo enters orbit around Mercury",
     "Europe–Japan probe, 8 years out; 37-minute burn at 18:24 UTC.",
     "ESA · AP · SPACE.COM", "mercury"),
    (8, "Europe", "BRUSSELS · TRADE", "OFFICIAL",
     "Indonesia and EU sign trade pact",
     "Signed in Brussels; in force from 2027. 90.4% of lines duty-free.",
     "Antara · Indonesian government", "trade"),
    (9, "Africa", "BAYELSA · DISASTER", "CONFIRMED",
     "Nigeria funeral boat toll reaches 24",
     "Capsized Fri, Agbaya–Ukubie; toll given Sat (NEMA).",
     "DW · AP · Sky News", "boat"),
    (10, "South Asia", "MANIPUR · HEALTH", "CONFIRMED",
     "Tainted alcohol kills 11 in India's Manipur",
     "More than 180 in hospital, chief minister says.",
     "REUTERS · SCMP · CNA", "bottle"),
    (11, "Europe", "LONDON · RUGBY", "OFFICIAL",
     "England beat All Blacks 37–12",
     "New Zealand's biggest loss to England; 25 points, their heaviest win over NZ.",
     "RNZ · match result", "rugby"),
    (12, "Europe", "FRANCE · PROTEST", "CONFIRMED",
     "Sixth Saturday of cost-of-living marches",
     "Ministry count; organisers say 150,000. Paris: 144 held.",
     "AFP · FRANCE 24 · LE MONDE", "march"),
]

ALSO_ON = [
    (13, "Gaza City", "Drone strike on food-aid van kills three", "REUTERS"),
    (14, "Jerusalem", "Eisenkot invites Likud to coalition talks", "TOI"),
    (15, "Kyiv", "Zelensky calls bridge strike a 'fair response'", "BBC"),
    (16, "Riyadh", "Coalition says it downed 3 Houthi missiles", "AJ"),
    (17, "Beirut", "Aoun demands Israel pull-out, end to Iran meddling", "AJ"),
    (18, "Brussels", "Costa's EU budget: €204bn cut, tax on big tech", "DW"),
    (19, "Brasilia", "Bolsonaro moved to intensive care", "REUTERS"),
    (20, "Washington", "FBI probes reported breach of crime database", "BBC"),
    (21, "Serang, Java", "Sweet factory fire: 3 dead, 36 missing", "GUARDIAN"),
    (22, "Hanoi", "Parliament passes law to speed land expropriation", "REUTERS"),
    (23, "Savar", "80 garment factories shut in wage protests", "D. STAR"),
    (24, "Mastung", "Pakistan says 15 militants killed", "DAWN"),
    (25, "Beijing", "Singapore's Wong meets Li Qiang; 20+ deals lined up", "ST"),
    (26, "Qinghai", "M5.9 quake at 10:45 UTC in remote west China", "USGS"),
    (27, "Zagreb", "Thousands rally over psychiatric ward death", "RTE"),
    (28, "Dublin", "Ireland beat champions South Africa 20–17", "BBC"),
    (29, "Turin", "Alcaraz beats Shelton, faces Zverev in ATP Finals final", "BBC"),
    (30, "Australia", "Hosts beat England by 3 wickets in first T20", "BBC"),
    (31, "Wellington", "India 486–4, lead NZ by 118 after day three", "AFP"),
    (32, "Abuja", "CAF makes Kiswahili its fifth official language", "CAF"),
    (33, "Niger State", "Gunmen kill village head in Borgu dawn raid", "TRUST"),
    (34, "Darwin", "M6.8 Timor quake felt in Dili and Darwin", "REUTERS"),
    (35, "Las Vegas", "Verstappen takes pole in Las Vegas", "AP"),
    (36, "Osaka", "BTS take five MAMA awards, two grand prizes", "YONHAP"),
]

REGION_COUNTS = [("Europe", 9), ("Middle East", 5), ("Americas", 5),
                 ("Africa", 3), ("South Asia", 3), ("East Asia", 3),
                 ("South-East Asia", 2), ("Oceania", 3), ("Global", 3)]

STATS = [
    ("2", "tankers hit off Khasab, Strait of Hormuz (UKMTO)"),
    ("130+", "countries want fossil fuels named at COP31 (AFP)"),
    ("730m", "people in the new EU–Indonesia trade area (EU)"),
    ("128", "states at the Geneva autonomous-weapons talks (DW)"),
    ("$5m", "FBI reward that stood on 'El Chapo Isidro' (FBI)"),
    ("8 yrs", "BepiColombo's journey from Earth to Mercury (ESA)"),
]

TIMELINE = [
    ("00:09", "Peru M6.7 quake"),
    ("02:00", "Sinaloa gunfight"),
    ("05:00", "Tanker hit, Hormuz"),
    ("06:50", "Sparta II alarm"),
    ("09:42", "M6.8 quake, Banda Sea"),
    ("12:12", "EU–Indonesia signing"),
    ("18:24", "BepiColombo orbit burn"),
    ("19:44", "Bahrain site ablaze"),
    ("Night", "COP31 talks go on"),
]

# ------------------------------------------------------------ world map
def draw_world_map(draw, x0, y0, w, h):
    """Simplified world map with numbered pins for stories 1-12."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(222, 232, 236), outline=RULE)
    # rough continents (stylised blobs)
    land = [
        # North America
        [(0.02, 0.12), (0.10, 0.06), (0.24, 0.10), (0.26, 0.22), (0.18, 0.34),
         (0.10, 0.30), (0.04, 0.22)],
        # South America
        [(0.26, 0.48), (0.32, 0.44), (0.36, 0.52), (0.33, 0.72), (0.28, 0.66)],
        # Europe
        [(0.46, 0.14), (0.52, 0.10), (0.56, 0.16), (0.52, 0.24), (0.46, 0.22)],
        # Africa
        [(0.46, 0.34), (0.54, 0.32), (0.58, 0.44), (0.54, 0.62), (0.48, 0.56),
         (0.45, 0.44)],
        # Asia
        [(0.58, 0.08), (0.78, 0.06), (0.92, 0.14), (0.90, 0.30), (0.80, 0.42),
         (0.70, 0.34), (0.60, 0.26), (0.56, 0.16)],
        # SE Asia islands
        [(0.78, 0.44), (0.82, 0.42), (0.84, 0.48), (0.80, 0.50)],
        # Australia
        [(0.82, 0.62), (0.92, 0.60), (0.94, 0.70), (0.86, 0.74), (0.81, 0.68)],
    ]
    for poly in land:
        pts = [(x0 + w * px, y0 + h * py) for px, py in poly]
        draw.polygon(pts, fill=LAND, outline=(150, 140, 110))
    # pins: (num, x_frac, y_frac, region)
    pins = [(1, 0.60, 0.30, "Middle East"), (2, 0.53, 0.13, "Europe"),
            (3, 0.52, 0.20, "Global"), (4, 0.27, 0.52, "Americas"),
            (5, 0.17, 0.26, "Americas"), (6, 0.49, 0.20, "Global"),
            (7, 0.50, 0.05, "Global"), (8, 0.47, 0.15, "Europe"),
            (9, 0.51, 0.44, "Africa"), (10, 0.68, 0.38, "South Asia"),
            (11, 0.44, 0.12, "Europe"), (12, 0.46, 0.17, "Europe")]
    for num, fx, fy, region in pins:
        px, py = x0 + w * fx, y0 + h * fy
        c = REGION_COLORS[region]
        draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=c, outline=(255, 255, 255))
        tw = d.textlength(str(num), font=f_tiny_b)
        d.text((px - tw / 2, py - 5), str(num), font=f_tiny_b, fill=(255, 255, 255))
    d.text((x0 + 6, y0 + h - 14), "Pins carry each story's number; colour = region.",
           font=f_tiny, fill=INK_SOFT)


# ================================================================ compose
y = 0
# top strip
d.text((16, 3), "THE WORLD IN ONE DAY", font=f_label, fill=INK)
centered(d, 3, "DAY 325 OF 2026", f_label, fill=RED_DARK)
r = "ALL TIMES UTC · RANKED BY CONSEQUENCE"
d.text((W - 16 - d.textlength(r, font=f_label), 3), r, font=f_label, fill=INK)
y = 16
hline(y)
# headline
y = 20
centered(d, y, "Saturday 21 November 2026", f_headline, fill=INK)
y = 88
hline(y)
y = 92
centered(d, y, "36 STORIES, 9 REGIONS, EVERY ONE DATED SATURDAY 21 NOVEMBER 2026",
         F(SANS_B, 10), fill=RED_DARK)
y = 106
hline(y)
# ticker
y = 110
centered(d, y, "Iran strikes Bahrain as tankers hit in Hormuz  ◆  Drones set Russian cargo ship ablaze off Finland  ◆  COP31 deadlocked over fossil fuels in overtime",
         f_italic, fill=INK)
y = 126
hline(y, width=2)
# timeline strip
y = 130
d.rectangle([16, y, 108, y + 26], fill=INK)
d.text((22, y + 8), "THE DAY IN UTC", font=f_kicker_sm, fill=(255, 255, 255))
tx0, tx1 = 116, W - 16
d.line([(tx0, y + 14), (tx1, y + 14)], fill=RULE, width=2)
n = len(TIMELINE)
for i, (t, label) in enumerate(TIMELINE):
    px = tx0 + (tx1 - tx0) * (i + 0.5) / n
    d.ellipse([px - 3, y + 11, px + 3, y + 17], fill=RED, outline=(255, 255, 255))
    d.text((px - d.textlength(t, font=f_tiny_b) / 2, y + 2), t, font=f_tiny_b, fill=INK)
    lw = d.textlength(label, font=f_tiny)
    d.text((px - lw / 2, y + 18), label, font=f_tiny, fill=INK_SOFT)
y = 160
hline(y)
# stat boxes
y = 164
bw = (W - 32 - 5 * 6) / 6
for i, (num, cap) in enumerate(STATS):
    x = 16 + i * (bw + 6)
    d.rectangle([x, y, x + bw, y + 48], outline=RULE, width=1)
    d.text((x + 6, y + 2), num, font=f_stat if len(num) <= 4 else f_stat_sm, fill=INK)
    text_wrapped(d, (x + 6, y + 27), cap, f_tiny, bw - 12, fill=INK_SOFT)
y = 212
hline(y)
# region bar
y = 216
d.text((16, y), "STORIES BY REGION", font=f_kicker_sm, fill=INK)
rx = 118
total = sum(c for _, c in REGION_COUNTS)
bar_w = W - 16 - rx
SHORT = {"Europe": "Europe", "Middle East": "Mid East", "Americas": "Americas",
         "Africa": "Africa", "South Asia": "S Asia", "East Asia": "E Asia",
         "South-East Asia": "SE Asia", "Oceania": "Oceania", "Global": "Global"}
for name, cnt in REGION_COUNTS:
    seg = bar_w * cnt / total
    d.rectangle([rx, y, rx + seg - 1, y + 12], fill=REGION_COLORS[name])
    lab = f"{SHORT[name]} {cnt}"
    lw = d.textlength(lab, font=f_tiny)
    d.text((rx + seg / 2 - lw / 2, y + 14), lab, font=f_tiny, fill=INK_SOFT)
    rx += seg
y = 242
hline(y)

# ---------------------------------------------------------------- heroes
HEROES = [
    ("draw_hormuz", 1, "MIDDLE EAST", "BAHRAIN · HORMUZ · CONFLICT", "CONFIRMED",
     "Iran strikes Bahrain as tankers hit in Hormuz",
     "Bahrain: Iranian attack set a civilian industrial site ablaze, no one hurt. "
     "IRGC says it hit US positions; UKMTO: two tankers attacked off Khasab.",
     "AL JAZEERA · REUTERS · AFP"),
    ("draw_sparta", 2, "EUROPE", "GULF OF FINLAND · CONFLICT", "CONFIRMED",
     "Drones set Russian cargo ship ablaze off Finland",
     "Sparta II, bound for Kaliningrad, was hit about 06:50 UTC and drifted into "
     "Finnish waters; crew evacuated. Finland: Ukraine likely behind it.",
     "BBC · FRANCE 24 · MOSCOW TIMES"),
    ("draw_cop31", 3, "GLOBAL", "COP31, ANTALYA · CLIMATE", "CONFIRMED",
     "COP31 deadlocked over fossil fuels in overtime",
     "A day past deadline in Antalya, talks paused overnight. EU and Pacific "
     "states reject a draft omitting fossil fuels; 130+ countries want them named.",
     "BBC · AFP · FRANCE 24"),
]

y = 246
col_w = (W - 32 - 2 * 8) / 3
hero_bottom = y
for i, (fn, num, region, topic, status, head, deck, src) in enumerate(HEROES):
    x = 16 + i * (col_w + 8)
    globals()[fn](d, int(x), y, int(col_w), 144)
    ky = y + 148
    kicker_line(d, int(x), ky, num, region, topic, status)
    badge(d, int(x + col_w) - 62, ky, status,
          GREEN if status == "CONFIRMED" else BLUE)
    hy = ky + 15
    hy = text_wrapped(d, (int(x), hy), head, f_hero_head, int(col_w), fill=INK)
    hy = text_wrapped(d, (int(x), hy + 2), deck, f_deck, int(col_w), fill=INK_SOFT)
    source_line(d, int(x), hy + 2, src)
    hero_bottom = max(hero_bottom, hy + 12)
y = hero_bottom + 4
hline(y)

# ------------------------------------------------------- small stories
y = y + 6
row_h = 74
for r in range(3):
    for c in range(3):
        num, region, place, status, head, deck, src, icon = SMALL[r * 3 + c]
        x = 16 + c * (col_w + 8)
        yy = y + r * row_h
        ICONS[icon](d, int(x), yy, 62)
        tx = int(x) + 68
        tw = int(col_w) - 68
        kicker_line(d, tx, yy, num, region, place, status)
        badge(d, int(x + col_w) - 62, yy, status,
              GREEN if status == "CONFIRMED" else BLUE)
        hy = text_wrapped(d, (tx, yy + 14), head, f_small_head, tw, fill=INK)
        hy = text_wrapped(d, (tx, hy + 1), deck, f_deck_small, tw, fill=INK_SOFT)
        source_line(d, tx, hy, src)
y = y + 3 * row_h + 4
hline(y)

# ------------------------------------------------- map + also-on list
y = y + 6
d.text((16, y), "WHERE IT HAPPENED", font=f_kicker, fill=INK)
d.text((16, y + 12), "pin numbers match the stories; pin colour = the region",
       font=f_tiny, fill=INK_SOFT)
map_x, map_y, map_w, map_h = 16, y + 26, 330, 158
draw_world_map(d, map_x, map_y, map_w, map_h)
list_x = 362
d.text((list_x, y), "ALSO ON SATURDAY 21 NOVEMBER 2026", font=f_kicker, fill=INK)
d.text((list_x, y + 12), "24 more stories, in order of consequence",
       font=f_tiny, fill=INK_SOFT)
ly = y + 26
col2_x = list_x + 318
for i, (num, place, head, src) in enumerate(ALSO_ON):
    cx = list_x if i < 12 else col2_x
    cy = ly + (i % 12) * 13
    d.text((cx, cy), str(num), font=f_list_b, fill=RED)
    line = f"{place}  {head}"
    maxw = 272
    if d.textlength(line, font=f_list) > maxw:
        while d.textlength(line + "…", font=f_list) > maxw and len(line) > 10:
            line = line[:-1]
        line += "…"
    d.text((cx + 18, cy), line, font=f_list, fill=INK)
    sw = d.textlength(src, font=f_tiny)
    d.text((cx + 296 - sw, cy + 1), src, font=f_tiny, fill=GREY)
y = max(map_y + map_h, ly + 12 * 13) + 8
hline(y)

# ------------------------------------------------------------ date check
y = y + 6
d.rectangle([16, y, W - 16, y + 36], outline=RED, width=2)
d.text((24, y + 4), "DATE CHECK", font=f_kicker, fill=RED_DARK)
dc = ("Well-known stories left out: they belong to another day (UTC).  "
      "Fri 20 Nov: Russian missiles land in Poland · Denmark expels Russian attaché · "
      "Wall Street tech sell-off.  Sun 22 Nov: Verstappen wins Las Vegas GP · new COP31 draft.  "
      "Not yet (future): COP31 approval session Sun 06:00 GMT · Liverpool v Man United (Sun).")
text_wrapped(d, (24, y + 16), dc, f_deck_small, W - 48, fill=INK_SOFT)
y = y + 42
hline(y)
# footer
y = y + 5
d.text((16, y), "HOW SURE", font=f_kicker_sm, fill=INK)
lx = 76
for label, col in [("CONFIRMED  2+ major outlets", GREEN),
                   ("OFFICIAL  on the record: agency, ministry, federation", BLUE),
                   ("REPORTED  one major outlet", GOLD),
                   ("CLAIM  one side says", RED)]:
    d.rectangle([lx, y + 1, lx + 8, y + 9], fill=col)
    d.text((lx + 11, y), label, font=f_tiny, fill=INK_SOFT)
    lx += 11 + d.textlength(label, font=f_tiny) + 16
y = y + 15
centered(d, y, "Every story here happened or was first reported on Saturday 21 November 2026 (UTC), told as the named outlets reported it. All maps and drawings are original vector work.",
         f_tiny, fill=INK_SOFT)
y = y + 11
centered(d, y, "Sources: USGS, UKMTO, AFP, Reuters, AP, France 24, PBS, Al Jazeera, ESA, Euronews, Kyodo, ABC",
         f_tiny, fill=GREY)

# ------------------------------------------------------------------ save
out_path = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
img.save(out_path, format="PNG")
data = open(out_path, "rb").read()
print(f"{out_path}: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")
print(f"size: {img.size[0]}x{img.size[1]}, stories: 36, regions: 9")
