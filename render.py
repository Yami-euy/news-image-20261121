#!/usr/bin/env python3
"""Render THE WORLD IN ONE PAGE v3 — Saturday 21 November 2026.

A newspaper front page (1024x1024) drawn in pure PIL: no network, no
photos, no downloaded assets. Every map, ship and panel is drawn from
vector primitives in this file, so the output is deterministic: run it
three times and the bytes are identical.

v3 returns to the newspaper format of v1 and of the top-ranked entries
(the v2 poster was rejected by the owner as "aneh") and tightens it:
a cleaner timeline, shorter stat captions, a redrawn Sparta II panel,
a simpler COP31 panel, map pins that no longer pile up over Europe,
and a list whose sources can no longer collide with the headlines.

Stories: 37, across 9 regions. The five core stories were re-checked
against live reporting on 23 November 2026; two v1 errors are fixed
here: the Peru quake DID kill (1 dead, 16 hurt, 853 homeless) and the
Bahrain hero no longer claims "no one hurt" (casualties were only
confirmed the next day). New story 37: Lewis Pugh's 15 km Hormuz swim,
first reported 21 November. Claims are labelled CLAIM, and the DATE
CHECK box says what was left out and why.
"""

import hashlib
import math
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
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
DUSK = (52, 68, 92)
DUSK_DARK = (30, 40, 58)

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


def F(path, size):
    return ImageFont.truetype(path, size)


f_masthead = F(SERIF_B, 62)
f_hero_head = F(SERIF_B, 21)
f_small_head = F(SERIF_B, 13)
f_deck = F(SERIF, 11)
f_deck_sm = F(SERIF, 10)
f_kicker = F(SANS_B, 9)
f_kicker_sm = F(SANS_B, 8)
f_label = F(SANS_B, 9)
f_tiny = F(SANS, 8)
f_tiny_b = F(SANS_B, 8)
f_stat = F(SERIF_B, 26)
f_stat_sm = F(SERIF_B, 20)
f_italic = F(SERIF_I, 11)
f_sans = F(SANS, 9)
f_list = F(SANS, 10)
f_list_b = F(SANS_B, 10)
f_num = F(SERIF_B, 13)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)


# ---------------------------------------------------------------- helpers
def wrap(draw, xy, text, font, max_w, fill=INK, leading=1):
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
        y += font.size + leading
    return y


def centred(draw, y, text, font, fill=INK, cx=W // 2):
    w = draw.textlength(text, font=font)
    draw.text((cx - w / 2, y), text, font=font, fill=fill)
    return y + font.size + 2


def rule(y, x0=16, x1=W - 16, fill=RULE, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def pill(draw, x, y, text, fill=GREEN):
    """Small CONFIRMED / OFFICIAL / CLAIM status pill, white on colour."""
    w = draw.textlength(text, font=f_kicker_sm) + 10
    draw.rounded_rectangle([x, y, x + w, y + 12], radius=2, fill=fill)
    draw.text((x + 5, y + 1), text, font=f_kicker_sm, fill=(255, 255, 255))
    return x + w


def kicker(draw, x, y, num, place, status):
    """'1  BAHRAIN · HORMUZ · CONFLICT' with the story number in red."""
    draw.text((x, y), str(num), font=f_num, fill=RED)
    draw.text((x + 16, y + 1), place, font=f_kicker, fill=INK)
    return y


def status_fill(status):
    if status == "CONFIRMED":
        return GREEN
    if status == "OFFICIAL":
        return BLUE
    if status == "REPORTED":
        return GOLD
    return RED


def source(draw, x, y, text):
    draw.text((x, y), text, font=f_tiny, fill=GREY)

# ------------------------------------------------------- hero illustrations
def draw_hormuz(draw, x0, y0, w, h):
    """Strait of Hormuz map: Iran top-right, Gulf below, Bahrain on fire.

    Two dashed missile arcs run from Iran toward Bahrain, and both
    tankers burn — the day's two facts, drawn, not listed.
    """
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
    # dashed missile arcs from Iran down to Bahrain
    for arc in (0.30, 0.44):
        for i in range(14):
            t = i / 13.0
            px = x0 + w * (0.78 - 0.52 * t)
            py = y0 + h * (0.08 + 0.42 * t * t + arc * 0.10 * (1 - t))
            draw.ellipse([px - 1, py - 1, px + 1, py + 1], fill=RED)
    # dashed tanker route through the strait
    for i in range(9):
        t = i / 8.0
        px = x0 + w * (0.42 + 0.30 * t)
        py = y0 + h * (0.44 + 0.10 * t)
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    # two burning tankers (hull + flame)
    for tx, ty in [(x0 + w * 0.78, y0 + h * 0.60), (x0 + w * 0.86, y0 + h * 0.68)]:
        draw.polygon([(tx - 3, ty - 12), (tx + 2, ty - 4), (tx + 7, ty - 12),
                      (tx + 10, ty - 2)], fill=(255, 140, 0))
        draw.rectangle([tx - 9, ty - 3, tx + 9, ty + 3], fill=(40, 40, 40))
        draw.rectangle([tx - 5, ty - 7, tx + 1, ty - 3], fill=(40, 40, 40))
        draw.polygon([(tx + 9, ty - 3), (tx + 14, ty), (tx + 9, ty + 3)], fill=RED)
    # Bahrain fire burst on the coast
    bx, by = x0 + w * 0.24, y0 + h * 0.52
    for ang in range(0, 360, 45):
        r = 13
        ex = bx + r * math.cos(math.radians(ang))
        ey = by + r * math.sin(math.radians(ang))
        draw.line([(bx, by), (ex, ey)], fill=(255, 140, 0), width=3)
    draw.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=RED)
    draw.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(255, 200, 0))
    draw.rounded_rectangle([bx - 34, by + 14, bx + 34, by + 28], radius=2, fill=RED)
    draw.text((bx - 29, by + 16), "SITE ON FIRE", font=f_tiny_b, fill=(255, 255, 255))
    # labels
    draw.text((x0 + w * 0.60, y0 + h * 0.52), "STRAIT OF", font=f_tiny_b, fill=INK)
    draw.text((x0 + w * 0.60, y0 + h * 0.52 + 10), "HORMUZ", font=f_tiny_b, fill=INK)
    draw.text((x0 + w * 0.68, y0 + 6), "IRAN", font=f_label, fill=INK)
    draw.text((x0 + 8, y0 + h - 26), "SAUDI", font=f_tiny_b, fill=INK_SOFT)
    draw.text((x0 + 8, y0 + h - 16), "ARABIA", font=f_tiny_b, fill=INK_SOFT)
    draw.text((x0 + w * 0.30, y0 + h * 0.78), "QATAR", font=f_tiny, fill=INK_SOFT)
    draw.text((x0 + w * 0.86, y0 + h * 0.80), "OMAN", font=f_tiny, fill=INK_SOFT)
    draw.text((x0 + w * 0.42, y0 + h * 0.82), "THE GULF", font=f_tiny_b, fill=BLUE)
    draw.text((x0 + 6, y0 + 6), "BAHRAIN", font=f_label, fill=RED_DARK)


def draw_sparta(draw, x0, y0, w, h):
    """Sparta II cargo ship burning in the Gulf of Finland, at dusk.

    Redrawn for v3: a lighter dusk sky so the ship reads at small
    size, one big flame over the deck, containers sitting on the hull
    instead of floating above it, and two drones on dashed paths.
    """
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=DUSK, outline=RULE, width=1)
    # pale horizon band
    draw.rectangle([x0, y0 + h * 0.42, x0 + w, y0 + h * 0.55], fill=(120, 130, 150))
    # smoke, small and high so it does not swallow the ship
    for sx, sy, sr in [(0.46, 0.22, 20), (0.54, 0.15, 24), (0.62, 0.22, 18),
                       (0.52, 0.08, 16)]:
        draw.ellipse([x0 + w * sx - sr, y0 + h * sy - sr * 0.6,
                      x0 + w * sx + sr, y0 + h * sy + sr * 0.6],
                     fill=(140, 142, 148))
    # one big flame over the deck
    fx, fy = x0 + w * 0.52, y0 + h * 0.52
    draw.polygon([(fx - 24, fy + 8), (fx - 13, fy - 26), (fx - 4, fy - 4),
                  (fx + 6, fy - 34), (fx + 15, fy - 8), (fx + 24, fy + 8)],
                 fill=(255, 140, 0))
    draw.polygon([(fx - 13, fy + 8), (fx - 5, fy - 14), (fx + 4, fy - 4),
                  (fx + 11, fy - 18), (fx + 15, fy + 8)], fill=(255, 210, 0))
    # sea
    draw.rectangle([x0, y0 + h * 0.62, x0 + w, y0 + h], fill=(38, 68, 96))
    for i in range(6):
        wx = x0 + 12 + i * 52
        draw.line([(wx, y0 + h * 0.70 + (i % 2) * 8),
                   (wx + 26, y0 + h * 0.70 + (i % 2) * 8)],
                  fill=(120, 170, 210), width=2)
    # hull
    draw.polygon([(x0 + w * 0.10, y0 + h * 0.52), (x0 + w * 0.90, y0 + h * 0.52),
                  (x0 + w * 0.84, y0 + h * 0.72), (x0 + w * 0.16, y0 + h * 0.72)],
                 fill=(16, 16, 18))
    draw.rectangle([x0 + w * 0.10, y0 + h * 0.52, x0 + w * 0.90, y0 + h * 0.56],
                   fill=(120, 20, 20))
    # containers, sitting on the deck line
    for i, cx in enumerate([0.16, 0.28, 0.40, 0.62, 0.74]):
        c = [(200, 60, 40), (40, 90, 140), (180, 150, 40),
             (60, 120, 70), (150, 80, 30)][i]
        draw.rectangle([x0 + w * cx, y0 + h * 0.38, x0 + w * (cx + 0.10),
                        y0 + h * 0.52], fill=c, outline=(20, 20, 20))
    # bridge tower at the stern
    draw.rectangle([x0 + w * 0.84, y0 + h * 0.32, x0 + w * 0.90, y0 + h * 0.52],
                   fill=(220, 220, 215), outline=(20, 20, 20))
    # drones with dashed approach paths
    for dx, dy in [(0.16, 0.12), (0.28, 0.06)]:
        px, py = x0 + w * dx, y0 + h * dy
        for k in range(5):
            qx = px + k * 6
            qy = py + k * 4
            draw.ellipse([qx - 1, qy - 1, qx + 1, qy + 1], fill=(220, 220, 220))
        draw.ellipse([px - 4, py - 2, px + 4, py + 2], fill=(230, 230, 230))
        draw.line([(px - 6, py - 4), (px + 6, py + 4)], fill=(230, 230, 230), width=1)
    draw.text((x0 + 8, y0 + h - 40), "06:50 UTC", font=f_label, fill=(255, 255, 255))
    draw.text((x0 + 8, y0 + h - 28), "two drones, taken off", font=f_tiny,
              fill=(220, 220, 220))
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
    """COP31: November calendar in overtime + draft text + clock.

    Simplified for v3: the thermometer is gone (it duplicated the
    story's point); the calendar, the crossed-out draft line and the
    overtime clock each get room to breathe.
    """
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
    for i, day in enumerate(range(9, 22)):
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
    draw.text((x + 6, y + 4), "M6.7", font=F(SERIF_B, 13), fill=INK)
    pts = [(x + 4, y + s * 0.55), (x + 14, y + s * 0.55), (x + 20, y + s * 0.25),
           (x + 28, y + s * 0.80), (x + 36, y + s * 0.35), (x + 44, y + s * 0.55),
           (x + 58, y + s * 0.55)]
    draw.line(pts, fill=RED, width=2)
    draw.text((x + 6, y + s - 14), "108 KM", font=f_tiny_b, fill=GREY)


def icon_cuffs(draw, x, y, s=62):
    draw.rectangle([x, y, x + s, y + s], fill=(232, 238, 244), outline=RULE)
    draw.text((x + 6, y + 4), "11 DEAD", font=f_tiny_b, fill=RED_DARK)
    draw.ellipse([x + 10, y + 22, x + 28, y + 40], outline=INK, width=3)
    draw.ellipse([x + 34, y + 22, x + 52, y + 40], outline=INK, width=3)
    draw.line([(x + 28, y + 31), (x + 34, y + 31)], fill=INK, width=3)
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
        ax = x + 18 + 7 * math.cos(i * math.pi / 4)
        ay = y + 18 + 7 * math.sin(i * math.pi / 4)
        draw.ellipse([ax - 1, ay - 1, ax + 1, ay + 1], fill=(255, 220, 0))
    draw.rectangle([x + 34, y + 8, x + 54, y + 28], fill=(255, 255, 255), outline=RED)
    draw.rectangle([x + 34, y + 8, x + 54, y + 18], fill=RED)
    draw.text((x + 6, y + 34), "90.4%", font=F(SERIF_B, 15), fill=INK)
    draw.text((x + 6, y + s - 14), "DUTY-FREE", font=f_tiny_b, fill=GREY)


def icon_boat(draw, x, y, s=62):
    draw.rectangle([x, y, x + s, y + s], fill=(198, 220, 232), outline=RULE)
    draw.text((x + 6, y + 4), "24", font=F(SERIF_B, 16), fill=INK)
    draw.text((x + 28, y + 8), "DEAD", font=f_tiny_b, fill=RED_DARK)
    draw.polygon([(x + 10, y + 40), (x + 52, y + 40), (x + 44, y + 50),
                  (x + 18, y + 50)], fill=(60, 60, 60))
    draw.rectangle([x + 26, y + 26, x + 36, y + 40], fill=(120, 60, 40))
    draw.line([(x + 6, y + 54), (x + 56, y + 54)], fill=BLUE, width=2)


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
    draw.ellipse([x + 10, y + 14, x + 52, y + 40], fill=(200, 170, 90),
                 outline=(255, 255, 255))
    draw.line([(x + 31, y + 14), (x + 31, y + 40)], fill=(255, 255, 255), width=2)
    draw.text((x + 6, y + 44), "37–12", font=F(SERIF_B, 14), fill=(255, 255, 255))


def icon_march(draw, x, y, s=62):
    draw.rectangle([x, y, x + s, y + s], fill=(238, 232, 214), outline=RULE)
    draw.text((x + 6, y + 4), "82,500", font=F(SERIF_B, 13), fill=INK)
    for px in [12, 24, 36, 48]:
        draw.ellipse([x + px, y + 14, x + px + 8, y + 22], fill=INK)
        draw.rectangle([x + px + 1, y + 22, x + px + 7, y + 44], fill=INK)
    draw.rectangle([x + 6, y + 48, x + 56, y + 50], fill=INK)
    draw.text((x + 6, y + s - 12), "MARCHERS", font=f_tiny_b, fill=GREY)


ICONS = {
    "quake": icon_quake, "cuffs": icon_cuffs, "robot": icon_robot,
    "mercury": icon_mercury, "trade": icon_trade, "boat": icon_boat,
    "bottle": icon_bottle, "rugby": icon_rugby, "march": icon_march,
}

# ------------------------------------------------------------------- data
# (num, region, place, status, headline, deck, source, icon)
SMALL = [
    (4, "Americas", "JUNÍN, PERU · QUAKE", "OFFICIAL",
     "Deep 6.7 quake shakes central Peru",
     "Near Ondores, felt in Lima. 1 dead, 16 hurt, 853 homeless, 93,000 without power.",
     "USGS · IGP · AFP", "quake"),
    (5, "Americas", "SINALOA, MEXICO · CRIME", "CONFIRMED",
     "Mexico captures cartel boss 'El Chapo Isidro'",
     "FBI most-wanted, seized in Guasave. 4 soldiers, 7 gunmen dead in the raid.",
     "AP · Al Jazeera · DEFENSA", "cuffs"),
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

# (num, region, place, headline, source) — 25 more, in order of consequence
ALSO_ON = [
    (13, "Middle East", "Gaza City", "Drone strike on food-aid van kills three", "REUTERS"),
    (14, "Middle East", "Jerusalem", "Eisenkot invites Likud to coalition talks", "TOI"),
    (15, "Europe", "Kyiv", "Zelensky calls bridge strike a 'fair response'", "BBC"),
    (16, "Middle East", "Riyadh", "Coalition says it downed 3 Houthi missiles", "AJ"),
    (17, "Middle East", "Beirut", "Aoun demands Israel pull-out", "AJ"),
    (18, "Europe", "Brussels", "Costa's EU budget: €204bn cut, big-tech tax", "DW"),
    (19, "Americas", "Brasilia", "Bolsonaro moved to intensive care", "REUTERS"),
    (20, "Americas", "Washington", "FBI probes breach of crime database", "BBC"),
    (21, "South-East Asia", "Serang, Java", "Factory fire: 3 dead, 36 missing", "GUARDIAN"),
    (22, "South-East Asia", "Hanoi", "Law to speed land expropriation passed", "REUTERS"),
    (23, "South Asia", "Savar", "80 garment factories shut in wage protests", "D. STAR"),
    (24, "South Asia", "Mastung", "Pakistan says 15 militants killed", "DAWN"),
    (25, "East Asia", "Beijing", "Wong meets Li Qiang; 20+ deals lined up", "ST"),
    (26, "East Asia", "Qinghai", "M5.9 quake in remote west China", "USGS"),
    (27, "Europe", "Zagreb", "Thousands rally over psychiatric ward death", "RTE"),
    (28, "Europe", "Dublin", "Ireland beat champions South Africa 20–17", "BBC"),
    (29, "Europe", "Turin", "Alcaraz beats Shelton, faces Zverev in final", "BBC"),
    (30, "Oceania", "Australia", "Hosts beat England by 3 wickets in first T20", "BBC"),
    (31, "Oceania", "Wellington", "India 486–4, lead NZ by 118", "AFP"),
    (32, "Africa", "Abuja", "CAF makes Kiswahili fifth official language", "CAF"),
    (33, "Africa", "Niger State", "Gunmen kill village head in Borgu raid", "TRUST"),
    (34, "Oceania", "Darwin", "M6.8 Timor quake felt in Dili and Darwin", "REUTERS"),
    (35, "Americas", "Las Vegas", "Verstappen takes pole in Las Vegas", "AP"),
    (36, "East Asia", "Osaka", "BTS take five MAMA awards, two grand prizes", "YONHAP"),
    (37, "Middle East", "Hormuz", "Lewis Pugh ends 15 km swim for sea life", "AP"),
]

REGION_COUNTS = [("Europe", 9), ("Middle East", 6), ("Americas", 5),
                 ("Africa", 3), ("South Asia", 3), ("East Asia", 3),
                 ("South-East Asia", 2), ("Oceania", 3), ("Global", 3)]

# Short captions: each must fit two lines of 8pt in one stat box.
STATS = [
    ("2", "tankers hit off Khasab (UKMTO)"),
    ("130+", "states want fossil fuels named at COP31"),
    ("730m", "people in EU–Indonesia trade area"),
    ("128", "states at Geneva arms talks (DW)"),
    ("$5m", "FBI reward on 'El Chapo Isidro'"),
    ("8 yrs", "BepiColombo's trip to Mercury (ESA)"),
]

# Seven moments, one row, room to breathe (v1 squeezed nine).
TIMELINE = [
    ("00:09", "Peru M6.7 quake"),
    ("05:00", "Tanker hit, Hormuz"),
    ("06:50", "Sparta II alarm"),
    ("09:42", "M6.8 quake, Banda Sea"),
    ("12:12", "EU–Indonesia signing"),
    ("18:24", "BepiColombo orbit burn"),
    ("19:44", "Bahrain site ablaze"),
]

# ------------------------------------------------------------ world map
def draw_world_map(draw, x0, y0, w, h):
    """Simplified world map with numbered pins for stories 1-12.

    Europe pins are spread apart (v1 piled them on one spot); pin 7
    is Mercury, which has no place on Earth, so the caption says so.
    """
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(222, 232, 236), outline=RULE)
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
    # (num, x_frac, y_frac, region) — Europe pins spread out on purpose
    pins = [(1, 0.60, 0.30, "Middle East"), (2, 0.53, 0.11, "Europe"),
            (3, 0.55, 0.22, "Global"), (4, 0.27, 0.52, "Americas"),
            (5, 0.17, 0.26, "Americas"), (6, 0.485, 0.20, "Global"),
            (8, 0.465, 0.15, "Europe"), (9, 0.51, 0.44, "Africa"),
            (10, 0.68, 0.38, "South Asia"), (11, 0.435, 0.11, "Europe"),
            (12, 0.45, 0.19, "Europe")]
    for num, fx, fy, region in pins:
        px, py = x0 + w * fx, y0 + h * fy
        c = REGION_COLORS[region]
        draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=c, outline=(255, 255, 255))
        tw = d.textlength(str(num), font=f_tiny_b)
        d.text((px - tw / 2, py - 5), str(num), font=f_tiny_b, fill=(255, 255, 255))
    d.text((x0 + 6, y0 + h - 14), "Pins carry each story's number; colour = region. No. 7 is Mercury.",
           font=f_tiny, fill=INK_SOFT)


# ================================================================ compose
y = 0
# top strip
d.text((16, 3), "THE WORLD IN ONE DAY", font=f_label, fill=INK)
centred(d, 3, "DAY 325 OF 2026", f_label, fill=RED_DARK)
r = "ALL TIMES UTC · RANKED BY CONSEQUENCE"
d.text((W - 16 - d.textlength(r, font=f_label), 3), r, font=f_label, fill=INK)
y = 16
rule(y)
# headline
y = 20
centred(d, y, "Saturday 21 November 2026", f_masthead, fill=INK)
y = 88
rule(y)
y = 92
centred(d, y, "37 STORIES, 9 REGIONS, EVERY ONE DATED SATURDAY 21 NOVEMBER 2026",
        F(SANS_B, 10), fill=RED_DARK)
y = 106
rule(y)
# ticker
y = 110
centred(d, y, "Iran strikes Bahrain as tankers hit in Hormuz  ◆  Drones set Russian cargo ship ablaze off Finland  ◆  COP31 deadlocked over fossil fuels in overtime",
        f_italic, fill=INK)
y = 126
rule(y, width=2)
# timeline strip — seven moments, one row, labels wrapped to two lines
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
    col_w = (tx1 - tx0) / n - 8
    wrap(d, (px - col_w / 2, y + 20), label, f_tiny, col_w, fill=INK_SOFT)
y = 172
rule(y)
# stat boxes — short captions, two lines at most
y = 176
bw = (W - 32 - 5 * 6) / 6
for i, (num, cap) in enumerate(STATS):
    x = 16 + i * (bw + 6)
    d.rectangle([x, y, x + bw, y + 48], outline=RULE, width=1)
    d.text((x + 6, y + 2), num, font=f_stat if len(num) <= 4 else f_stat_sm, fill=INK)
    wrap(d, (x + 6, y + 27), cap, f_tiny, bw - 12, fill=INK_SOFT)
y = 224
rule(y)
# region bar
y = 228
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
y = 254
rule(y)

# ---------------------------------------------------------------- heroes
HEROES = [
    ("draw_hormuz", 1, "MIDDLE EAST · BAHRAIN · HORMUZ · CONFLICT", "CONFIRMED",
     "Iran strikes Bahrain as tankers hit in Hormuz",
     "Bahrain: Iranian attack set a civilian industrial site ablaze in Sitra. "
     "IRGC says it hit US positions; UKMTO: two tankers attacked off Khasab.",
     "AL JAZEERA · REUTERS · AFP"),
    ("draw_sparta", 2, "EUROPE · GULF OF FINLAND · CONFLICT", "CONFIRMED",
     "Drones set Russian cargo ship ablaze off Finland",
     "Sparta II, bound for Kaliningrad, hit about 06:50 UTC; drifted into "
     "Finnish waters. 16 crew evacuated, 1 hurt. Finland: Ukraine likely behind it.",
     "BBC · FRANCE 24 · MOSCOW TIMES"),
    ("draw_cop31", 3, "GLOBAL · COP31, ANTALYA · CLIMATE", "CONFIRMED",
     "COP31 deadlocked over fossil fuels in overtime",
     "A day past deadline in Antalya, talks paused overnight. EU and Pacific "
     "states reject a draft omitting fossil fuels.",
     "BBC · AFP · FRANCE 24"),
]

y = 258
col_w = (W - 32 - 2 * 8) / 3
hero_bottom = y
for i, (fn, num, topic, status, head, deck, src) in enumerate(HEROES):
    x = 16 + i * (col_w + 8)
    globals()[fn](d, int(x), y, int(col_w), 132)
    ky = y + 136
    kicker(d, int(x), ky, num, topic, status)
    pill(d, int(x + col_w) - 62, ky, status, status_fill(status))
    hy = ky + 15
    hy = wrap(d, (int(x), hy), head, f_hero_head, int(col_w), fill=INK)
    hy = wrap(d, (int(x), hy + 2), deck, f_deck, int(col_w), fill=INK_SOFT)
    source(d, int(x), hy + 2, src)
    hero_bottom = max(hero_bottom, hy + 12)
y = hero_bottom + 4
rule(y)

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
        kicker(d, tx, yy, num, place, status)
        pill(d, int(x + col_w) - 62, yy, status, status_fill(status))
        hy = wrap(d, (tx, yy + 14), head, f_small_head, tw, fill=INK)
        hy = wrap(d, (tx, hy + 1), deck, f_deck_sm, tw, fill=INK_SOFT)
        source(d, tx, hy, src)
y = y + 3 * row_h + 4
rule(y)

# ------------------------------------------------- map + also-on list
y = y + 6
d.text((16, y), "WHERE IT HAPPENED", font=f_kicker, fill=INK)
d.text((16, y + 12), "pin numbers match the stories; pin colour = the region",
       font=f_tiny, fill=INK_SOFT)
map_x, map_y, map_w, map_h = 16, y + 26, 330, 158
draw_world_map(d, map_x, map_y, map_w, map_h)
list_x = 362
d.text((list_x, y), "ALSO ON SATURDAY 21 NOVEMBER 2026", font=f_kicker, fill=INK)
d.text((list_x, y + 12), "25 more stories, in order of consequence",
       font=f_tiny, fill=INK_SOFT)
ly = y + 26
col2_x = list_x + 318
for i, (num, region, place, head, src) in enumerate(ALSO_ON):
    cx = list_x if i < 13 else col2_x
    cy = ly + (i % 13) * 12
    # region-colour square, then number, then headline, source right-aligned
    d.rectangle([cx, cy + 1, cx + 7, cy + 8], fill=REGION_COLORS[region])
    d.text((cx + 10, cy), str(num), font=f_list_b, fill=RED)
    line = f"{place}  {head}"
    maxw = 318 - 28 - 46 + 18
    if d.textlength(line, font=f_list) > maxw:
        while d.textlength(line + "…", font=f_list) > maxw and len(line) > 10:
            line = line[:-1]
        line += "…"
    d.text((cx + 28, cy), line, font=f_list, fill=INK)
    sw = d.textlength(src, font=f_tiny)
    d.text((cx + 314 - sw, cy + 1), src, font=f_tiny, fill=GREY)
y = max(map_y + map_h, ly + 13 * 12) + 8
rule(y)

# ------------------------------------------------------------ date check
y = y + 6
d.rectangle([16, y, W - 16, y + 36], outline=RED, width=2)
d.text((24, y + 4), "DATE CHECK", font=f_kicker, fill=RED_DARK)
dc = ("Well-known stories left out: they belong to another day (UTC).  "
      "Fri 20 Nov: Russian missiles land in Poland · Denmark expels Russian attaché · "
      "Wall Street tech sell-off.  Sun 22 Nov: Verstappen wins Las Vegas GP · new COP31 draft.  "
      "Not yet (future): COP31 approval session Sun 06:00 GMT · Liverpool v Man United (Sun).")
wrap(d, (24, y + 16), dc, f_deck_sm, W - 48, fill=INK_SOFT)
y = y + 42
rule(y)
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
y = y + 13
centred(d, y, "Every story here happened or was first reported on Saturday 21 November 2026 (UTC), told as the named outlets reported it. All maps and drawings are original vector work.",
        f_tiny, fill=INK_SOFT)
y = y + 9
centred(d, y, "Sources: USGS, UKMTO, AFP, Reuters, AP, France 24, PBS, Al Jazeera, ESA, Euronews, Kyodo, ABC",
        f_tiny, fill=GREY)

# ------------------------------------------------------------------ save
out_path = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
img.save(out_path, format="PNG")
data = open(out_path, "rb").read()
print(f"{out_path}: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")
print(f"size: {img.size[0]}x{img.size[1]}, stories: 37, regions: 9")
