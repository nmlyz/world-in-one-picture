#!/usr/bin/env python3
"""Draw a one-image newspaper front page summing up the world news of
Sunday 22 November 2026, and write it to /output/entry.png.

Standard library only, no network, fully deterministic: the same bytes
come out of every run. All text is drawn with a hand-made 5x7 bitmap
font; all pictures are drawn with code. Eight stories: the overnight
missile attack on Ukraine, the missiles stopped over Riyadh, the
market sell-off, the EU budget fight, the Nigeria boat disaster,
Cyclone Akvan, Voyager 1 reaching one light-day, and the Amputee
Football World Cup final.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (20, 22, 26)
RED = (179, 32, 42)
BLUE = (29, 78, 137)
DARKBLUE = (16, 42, 84)
NIGHT = (13, 20, 44)
YELLOW = (240, 192, 32)
GOLD = (212, 160, 32)
GRAY = (110, 110, 110)
LIGHT = (226, 219, 198)
WHITE = (255, 255, 255)
SKY = (188, 214, 235)
DUSK = (232, 140, 80)
SEA = (64, 120, 178)
DEEPSEA = (24, 68, 120)
SAND = (214, 188, 140)
GREEN = (46, 125, 50)
PITCH = (52, 138, 72)
ORANGE = (232, 119, 34)
BROWN = (120, 84, 50)
SKIN = (232, 190, 160)
TEAL = (18, 92, 96)

# ---------------------------------------------------------------- font
# Each glyph is 7 rows of 5 pixels, '#' is ink.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
}


def text_width(s, scale):
    if not s:
        return 0
    return len(s) * 6 * scale - scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def frame(self, x, y, w, h, c, t=3):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=3):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        r = t // 2
        while True:
            self.rect(x0 - r, y0 - r, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, pts, c, t=3):
        for i in range(len(pts) - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c, t)

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r + 2 * r:
                        self.set(xx, yy, c)

    def polygon(self, pts, c):
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    nodes.append(x0 + (yy - y0) * (x1 - x0) // (y1 - y0))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                self.rect(nodes[i], yy, nodes[i + 1] - nodes[i] + 1, 1, c)

    def star(self, cx, cy, r, c):
        # Five-point starburst used for explosions and intercepts.
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r // 2
            pts.append((cx + int(rr * math.cos(ang)),
                        cy + int(rr * math.sin(ang))))
        self.polygon(pts, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for ry in range(7):
                row = glyph[ry]
                for rx in range(5):
                    if row[rx] == "#":
                        self.rect(cx + rx * scale, y + ry * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_centered(self, cx, y, s, scale, c):
        return self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def text_wrapped(self, x, y, s, scale, c, max_w, line_gap=4):
        words = s.upper().split()
        lines = []
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        for i, ln in enumerate(lines):
            self.text(x, y + i * (7 * scale + line_gap), ln, scale, c)
        return len(lines)


# ---------------------------------------------------------------- png
def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        raw += canvas.px[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    os.chmod(path, 0o644)


def panel(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.frame(x, y, w, h, INK, 2)


def kicker(cv, x, y, s):
    cv.rect(x, y, text_width(s, 2) + 12, 18, RED)
    cv.text(x + 6, y + 2, s, 2, WHITE)


# ---------------------------------------------------------------- pictures
def pic_ukraine(cv, x, y, w, h):
    """Night over a Ukrainian city: three missile trails arc down, two
    blasts bloom, searchlights sweep the sky. Drawn for a 300x224 panel."""
    cv.rect(x, y, w, h, NIGHT)
    for sx, sy, r in ((28, 22, 2), (90, 14, 2), (150, 30, 2), (210, 16, 2),
                      (262, 34, 2), (60, 52, 1), (180, 48, 1), (240, 60, 1)):
        cv.circle(x + sx, y + sy, r, WHITE)
    # searchlight beams from the rooftops
    cv.line(x + 40, y + h - 40, x + 120, y + 20, (120, 140, 190), 4)
    cv.line(x + 250, y + h - 40, x + 200, y + 26, (120, 140, 190), 4)
    # three missile trails arcing down from the top
    for tx, bx in ((60, 96), (150, 190), (238, 262)):
        cv.polyline([(x + tx, y + 4), (x + tx + 14, y + 58),
                     (x + bx, y + 118)], YELLOW, 4)
        cv.circle(x + bx, y + 118, 7, ORANGE)
        cv.circle(x + bx, y + 118, 4, YELLOW)
    # two explosion bursts above the skyline
    cv.star(x + 96, y + 138, 26, ORANGE)
    cv.star(x + 96, y + 138, 14, YELLOW)
    cv.star(x + 236, y + 150, 20, ORANGE)
    cv.star(x + 236, y + 150, 11, YELLOW)
    # skyline with lit windows
    base = y + h
    for bx, bw, bh in ((0, 46, 62), (52, 34, 84), (92, 40, 58),
                       (138, 30, 92), (174, 44, 66), (224, 36, 80),
                       (266, 34, 56)):
        cv.rect(x + bx, base - bh, bw, bh, INK)
        for wx in range(bx + 7, bx + bw - 5, 12):
            for wy in range(base - bh + 8, base - 8, 14):
                if (wx + wy) % 3 == 0:
                    cv.rect(x + wx, wy, 4, 5, YELLOW)
    cv.rect(x, base - 6, w, 6, INK)


def pic_riyadh(cv, x, y, w, h):
    """Dusk over Riyadh: interceptors rise to meet three incoming
    missiles and burst in the sky above the towers."""
    cv.rect(x, y, w, h, (246, 178, 110))
    cv.rect(x, y + h // 2, w, h - h // 2, (214, 110, 74))
    cv.circle(x + w - 46, y + 26, 18, (250, 226, 160))
    # skyline with one tall tower with an arched top
    base = y + h
    for bx, bw, bh in ((0, 52, 44), (58, 36, 60), (100, 40, 50),
                       (300, 44, 58), (350, 52, 46), (408, 36, 54)):
        cv.rect(x + bx, base - bh, bw, bh, (74, 52, 66))
    tx = x + 168
    cv.rect(tx, base - 96, 56, 96, (74, 52, 66))
    cv.rect(tx + 12, base - 112, 32, 16, (74, 52, 66))
    cv.circle(tx + 28, base - 96, 10, (246, 178, 110))
    for bx, bw, bh in ((0, 52, 44), (58, 36, 60), (100, 40, 50),
                       (168, 56, 96), (300, 44, 58), (350, 52, 46),
                       (408, 36, 54)):
        for wx in range(bx + 7, bx + bw - 5, 12):
            for wy in range(base - bh + 8, base - 6, 14):
                if (wx * 7 + wy) % 4 == 0:
                    cv.rect(x + wx, wy, 4, 5, YELLOW)
    # three incoming missiles from the top, three interceptors rising
    for ix, mx in ((90, 120), (215, 235), (330, 350)):
        cv.line(x + mx, y + 6, x + ix, y + 44, WHITE, 4)
        cv.circle(x + mx, y + 6, 5, WHITE)
        cv.line(x + ix, y + h - 8, x + ix, y + 44, YELLOW, 4)
        cv.star(x + ix, y + 44, 15, YELLOW)
        cv.star(x + ix, y + 44, 8, WHITE)


def pic_markets(cv, x, y, w, h):
    """A market chart falling off a cliff: red line, red bars, down arrow."""
    cv.rect(x, y, w, h, WHITE)
    for gy in range(y + 16, y + h - 8, 18):
        cv.line(x + 8, gy, x + w - 8, gy, (228, 228, 228), 1)
    for gx in range(x + 40, x + w - 8, 44):
        cv.line(gx, y + 8, gx, y + h - 8, (228, 228, 228), 1)
    # falling line
    pts = [(x + 14, y + 16), (x + 78, y + 26), (x + 132, y + 22),
           (x + 196, y + 44), (x + 250, y + 40), (x + 310, y + 62),
           (x + 372, y + 58), (x + w - 16, y + h - 14)]
    cv.polyline(pts, RED, 5)
    for px, py in pts:
        cv.circle(px, py, 4, RED)
    # descending bars on the left
    for i, bh in enumerate((34, 26, 18, 10)):
        cv.rect(x + 16 + i * 20, y + h - 12 - bh, 12, bh, (214, 60, 70))
    # big down arrow on the right
    ax = x + w - 64
    cv.polygon([(ax, y + 12), (ax + 26, y + 12), (ax + 26, y + 44),
                (ax + 40, y + 44), (ax + 13, y + 78), (ax - 14, y + 44),
                (ax, y + 44)], RED)


def pic_eu(cv, x, y, w, h):
    """EU flag blue, a ring of twelve gold stars, a stack of gold coins
    and red scissors cutting the ribbon of the budget."""
    cv.rect(x, y, w, h, BLUE)
    cx, cy = x + 92, y + h // 2
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        sx = cx + int(62 * math.cos(ang))
        sy = cy + int(38 * math.sin(ang))
        cv.star(sx, sy, 7, YELLOW)
    # stack of gold coins
    for i in range(4):
        cv.rect(x + 250, y + h - 26 - i * 13, 92, 11, GOLD)
        cv.rect(x + 250, y + h - 26 - i * 13, 92, 2, YELLOW)
    cv.rect(x + 250, y + h - 26 - 4 * 13, 92, 11, GOLD)
    # red scissors cutting a white ribbon across the coins
    cv.line(x + 236, y + 12, x + 330, y + h - 30, GRAY, 5)
    cv.line(x + 330, y + 12, x + 236, y + h - 30, GRAY, 5)
    cv.circle(x + 232, y + 10, 9, GRAY, fill=False)
    cv.circle(x + 334, y + 10, 9, GRAY, fill=False)
    cv.rect(x + 356, y + h // 2 - 6, 76, 12, WHITE)
    cv.rect(x + 356, y + h // 2 - 6, 76, 3, RED)


def pic_boat(cv, x, y, w, h):
    """A capsized boat in heavy waves, an orange life ring floating by."""
    cv.rect(x, y, w, h, SKY)
    cv.rect(x, y + h // 2, w, h - h // 2, SEA)
    for wy in (y + h // 2 + 8, y + h // 2 + 30, y + h - 14):
        for wx in range(x + 4, x + w - 10, 26):
            cv.line(wx, wy, wx + 14, wy, WHITE, 3)
    # hull upside down, keel sticking up out of the water
    cv.polygon([(x + 40, y + h // 2 + 26), (x + 176, y + h // 2 + 26),
                (x + 158, y + h // 2 + 52), (x + 58, y + h // 2 + 52)],
               BROWN)
    cv.rect(x + 102, y + h // 2 + 12, 12, 14, BROWN)
    cv.rect(x + 40, y + h // 2 + 26, 136, 4, INK)
    # life ring
    rx, ry = x + w - 44, y + h - 30
    cv.circle(rx, ry, 16, ORANGE)
    cv.circle(rx, ry, 8, SEA)
    cv.rect(rx - 16, ry - 3, 8, 6, WHITE)
    cv.rect(rx + 8, ry - 3, 8, 6, WHITE)


def pic_cyclone(cv, x, y, w, h):
    """A cyclone spiral over the coast: curving arms, rain, bending palms."""
    cv.rect(x, y, w, h, (200, 222, 228))
    cx, cy = x + w // 2, y + 44
    for r in (12, 24, 36):
        cv.circle(cx, cy, r, WHITE, fill=False)
    for ang0 in (0.0, 2.1, 4.2):
        pts = []
        for k in range(9):
            a = ang0 + k * 0.45
            rr = 10 + k * 4
            pts.append((cx + int(rr * math.cos(a)),
                        cy + int(rr * math.sin(a))))
        cv.polyline(pts, TEAL, 4)
    cv.circle(cx, cy, 8, TEAL)
    # coastline and two bending palm trees
    cv.rect(x, y + h - 26, w, 26, SAND)
    cv.rect(x, y + h - 26, w, 4, SEA)
    for px in (x + 26, x + w - 34):
        cv.line(px, y + h - 26, px + 12, y + h - 62, BROWN, 5)
        for dx, dy in ((-16, -8), (-6, -14), (6, -12), (16, -6)):
            cv.line(px + 12, y + h - 62, px + 12 + dx, y + h - 62 + dy,
                    GREEN, 4)
    # rain streaks
    for rx in range(x + 60, x + w - 20, 22):
        cv.line(rx, y + h - 52, rx - 6, y + h - 38, (120, 150, 170), 3)


def pic_voyager(cv, x, y, w, h):
    """Voyager 1 in black space: gold bus, white dish, long antenna,
    a small blue Earth far behind it."""
    cv.rect(x, y, w, h, NIGHT)
    for sx, sy, r in ((12, 12, 2), (52, 26, 1), (110, 10, 2), (26, 66, 1),
                      (96, 80, 1), (130, 40, 2), (20, 40, 1)):
        cv.circle(x + sx, y + sy, r, WHITE)
    # small Earth at lower left
    cv.circle(x + 22, y + h - 22, 11, SEA)
    cv.circle(x + 19, y + h - 25, 4, GREEN)
    cv.circle(x + 25, y + h - 19, 3, GREEN)
    # spacecraft: gold bus, white dish, antenna boom
    bx, by = x + 62, y + 34
    cv.rect(bx, by, 44, 26, GOLD)
    cv.rect(bx + 6, by + 6, 32, 14, YELLOW)
    cv.circle(bx + 54, by + 13, 16, WHITE)
    cv.circle(bx + 54, by + 13, 10, LIGHT)
    cv.line(bx + 22, by + 26, bx + 22, by + 40, GRAY, 3)
    cv.line(bx + 22, by + 40, bx + 10, by + 48, GRAY, 3)
    cv.line(bx, by + 13, bx - 26, by + 4, GRAY, 3)
    cv.circle(bx - 28, by + 3, 4, YELLOW)
    # signal waves travelling back to Earth (kept inside the panel)
    for r in (14, 18, 21):
        cv.circle(x + 22, y + h - 22, r, (120, 140, 190), fill=False)


def pic_sport(cv, x, y, w, h):
    """A football pitch with the Moroccan and Ghanaian flags and a ball."""
    cv.rect(x, y, w, h, PITCH)
    cv.rect(x, y + h - 34, w, 34, (40, 110, 56))
    cv.line(x + 8, y + h - 34, x + w - 8, y + h - 34, WHITE, 2)
    cv.circle(x + w // 2, y + h - 34, 16, WHITE, fill=False)
    # Morocco flag: red field, green pentagram
    fx, fy = x + 14, y + 12
    cv.rect(fx, fy, 44, 30, RED)
    cv.star(fx + 22, fy + 15, 9, GREEN)
    cv.line(fx + 22, fy + 42, fx + 22, fy + 62, WHITE, 3)
    # Ghana flag: red, gold, green bands with a black star
    fx = x + 82
    cv.rect(fx, fy, 44, 10, RED)
    cv.rect(fx, fy + 10, 44, 10, YELLOW)
    cv.rect(fx, fy + 20, 44, 10, GREEN)
    cv.star(fx + 22, fy + 15, 7, INK)
    cv.line(fx + 22, fy + 42, fx + 22, fy + 62, WHITE, 3)
    # football
    cv.circle(x + w - 24, y + h - 52, 12, WHITE)
    cv.circle(x + w - 24, y + h - 52, 4, INK)
    for dx, dy in ((-8, -6), (8, -6), (-8, 6), (8, 6)):
        cv.circle(x + w - 24 + dx, y + h - 52 + dy, 2, INK)


# ---------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)

    # masthead
    cv.text_centered(W // 2, 14, "SUNDAY - THE WORLD IN ONE PICTURE", 3, INK)
    cv.rect(24, 50, W - 48, 5, INK)
    cv.text_centered(W // 2, 62, "22 NOVEMBER 2026", 9, RED)
    cv.rect(24, 134, W - 48, 3, INK)
    cv.rect(24, 141, W - 48, 7, INK)

    # ---- lead story: missiles over Ukraine
    ax, ay, aw, ah = 24, 160, W - 48, 240
    panel(cv, ax, ay, aw, ah)
    pic_ukraine(cv, ax + 14, ay + 14, 300, ah - 28)
    tx = ax + 330
    kicker(cv, tx, ay + 18, "UKRAINE")
    cv.text(tx, ay + 46, "MISSILES RAIN", 6, INK)
    cv.text(tx, ay + 92, "ON UKRAINE", 6, RED)
    cv.rect(tx, ay + 140, aw - 344, 3, INK)
    cv.text(tx, ay + 154, "3 BALLISTIC MISSILES, 148 DRONES", 3, INK)
    cv.text(tx, ay + 180, "OVERNIGHT - 117 SHOT DOWN", 3, INK)
    cv.text(tx, ay + 206, "KRYVYI RIH: 2 DEAD, ABOUT 60 HURT", 3, INK)

    # ---- row of two: Middle East, markets
    bw = (W - 48 - 16) // 2
    by, bh = 412, 238
    panel(cv, 24, by, bw, bh)
    pic_riyadh(cv, 38, by + 8, bw - 28, 92)
    kicker(cv, 38, by + 106, "MIDDLE EAST")
    cv.text(38, by + 130, "MISSILES STOPPED", 4, INK)
    cv.text(38, by + 158, "OVER RIYADH", 4, RED)
    cv.rect(38, by + 192, bw - 28, 3, INK)
    cv.text_wrapped(38, by + 200, "3 HOUTHI MISSILES INTERCEPTED. "
                    "TANKER HIT OFF OMAN. 6 KILLED IN GAZA.",
                    2, INK, bw - 28)

    qx = 24 + bw + 16
    panel(cv, qx, by, bw, bh)
    pic_markets(cv, qx + 14, by + 8, bw - 28, 92)
    kicker(cv, qx + 14, by + 106, "MARKETS")
    cv.text(qx + 14, by + 130, "MARKETS SLIDE", 4, INK)
    cv.text(qx + 14, by + 158, "INTO CORRECTION", 4, RED)
    cv.rect(qx + 14, by + 192, bw - 28, 3, INK)
    cv.text_wrapped(qx + 14, by + 200, "S&P 500 AND DOW IN CORRECTION. "
                     "NASDAQ DOWN FOR 2026.", 2, INK, bw - 28)

    # ---- row of two: EU budget, disasters
    cy = 662
    panel(cv, 24, cy, bw, bh)
    pic_eu(cv, 38, cy + 8, bw - 28, 92)
    kicker(cv, 38, cy + 106, "EUROPE")
    cv.text(38, cy + 130, "EU BUDGET FIGHT", 4, INK)
    cv.text(38, cy + 158, "204 BN CUT SOUGHT", 4, RED)
    cv.rect(38, cy + 192, bw - 28, 3, INK)
    cv.text_wrapped(38, cy + 200, "COSTA PROPOSES A 3% LEVY ON BIG TECH. "
                     "FRANCE AND GERMANY OBJECT.", 2, INK, bw - 28)

    panel(cv, qx, cy, bw, bh)
    kicker(cv, qx + 14, cy + 8, "DISASTERS")
    cv.text(qx + 14, cy + 32, "NIGERIA", 2, RED)
    cv.text(qx + 249, cy + 32, "INDIA", 2, RED)
    pic_boat(cv, qx + 14, cy + 48, 219, 96)
    pic_cyclone(cv, qx + 249, cy + 48, 219, 96)
    cv.text_wrapped(qx + 14, cy + 150, "BOAT CAPSIZES IN BAYELSA. "
                     "AT LEAST 24 DEAD.", 2, INK, 219)
    cv.text_wrapped(qx + 249, cy + 150, "CYCLONE AKVAN HITS ODISHA. "
                     "440,000 EVACUATED.", 2, INK, 219)

    # ---- bottom strip: Voyager 1, sport
    dy, dh = 912, 100
    panel(cv, 24, dy, bw, dh)
    pic_voyager(cv, 34, dy + 8, 140, 84)
    tx = 24 + 160
    kicker(cv, tx, dy + 8, "SCIENCE")
    cv.text(tx, dy + 30, "VOYAGER 1, ONE", 3, INK)
    cv.text(tx, dy + 55, "LIGHT-DAY AWAY", 3, RED)
    cv.text(tx, dy + 80, "SIGNALS TAKE A DAY.", 2, INK)

    panel(cv, qx, dy, bw, dh)
    pic_sport(cv, qx + 10, dy + 8, 140, 84)
    tx = qx + 160
    kicker(cv, tx, dy + 8, "SPORT")
    cv.text(tx, dy + 30, "MOROCCO VS GHANA", 3, INK)
    cv.text(tx, dy + 55, "CUP FINAL TODAY", 3, RED)
    cv.text(tx, dy + 80, "WORLD CUP FINAL, MEXICO.", 2, INK)

    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    try:
        os.umask(0o022)
    except OSError:
        pass
    write_png(build(), os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
