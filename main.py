#!/usr/bin/env python3
"""The World in One Page -- 26 November 2026.

A newspaper-style front page that sums up Thursday 26 November 2026's
world news in a single 1024x1024 image, drawn with pure-stdlib Python.

Stories covered (all verified 26 Nov 2026):
  1. TARIFF SHOCK -- Trump announces sweeping new tariffs on China,
     Japan, the EU, Taiwan and others; Nasdaq sinks almost 4% as an
     AI-stock rout rattles Wall Street.
  2. BRENT TOPS $94 -- Houthis claim a strike on Saudi Arabia's Ras
     Tanura refinery; oil prices jump on supply fears.
  3. FIRST PAKISTANI ASTRONAUT REACHES TIANGONG -- Muhammad Zeeshan
     Ali joins China's Shenzhou-24 crew at the Tiangong station.
  4. 31 KILLED IN CAIRO TANKER FIRE -- a fuel tanker crash ignites
     a massive blaze on a Cairo highway.
  5. Also today: Israeli strike kills a senior Hamas official in
     Gaza; Russia's own figures show nearly 500,000 war dead.

Deterministic: no randomness, no clock, no network. The program writes
exactly the same bytes on every run. Pure stdlib only (zlib + struct
PNG encoder, hand-rolled 5x7 bitmap font).
"""

import os
import struct
import zlib

W, H = 1024, 1024
OUT = "/output/entry.png"

# ---- palette ---------------------------------------------------------
PAPER = (248, 244, 232)
INK = (18, 18, 18)
RED = (176, 30, 36)
DARKRED = (140, 20, 26)
BLUE = (24, 64, 120)
GOLD = (198, 142, 28)
GREY = (110, 108, 100)
LIGHTGREY = (222, 216, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY = (214, 232, 245)
ORANGE = (224, 110, 20)

# ---- 5x7 bitmap font --------------------------------------------------
# Each glyph: 7 rows of 5 pixels, '#' = on, '.' = off.
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ";": [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."],
    "'": ["..#..", "..#..", "..#..", ".....", ".....", ".....", "....."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "$": ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    "%": ["##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "(": ["...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"],
    ")": ["##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."],
    "&": [".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."],
    "*": [".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."],
}

# ---- canvas ------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def frame(self, x, y, w, h, c, t=2):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for row in range(7):
                for col in range(5):
                    if g[row][col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_center(self, y, s, scale, c, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        tw = self.text_w(s, scale)
        return self.text(x0 + (x1 - x0 - tw) // 2, y, s, scale, c)

    def wrap(self, x, y, s, scale, c, max_w, lh=None):
        """Word-wrap text; returns y after the last line."""
        if lh is None:
            lh = 9 * scale
        words = s.split(" ")
        lines, cur = [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if self.text_w(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        for ln in lines:
            self.text(x, y, ln, scale, c)
            y += lh
        return y


def chunk(data, kind):
    c = struct.pack(">I", len(data)) + kind + data
    c += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return c


def write_png(cv, path):
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(ihdr, b"IHDR")
    png += chunk(zlib.compress(bytes(raw), 9), b"IDAT")
    png += chunk(b"", b"IEND")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def flame(cv, x, y, s):
    """A stylised flame, base at (x, y), size s."""
    cv.disc(x, y - s // 2, s // 2, ORANGE)
    cv.disc(x, y - s, s // 3, RED)
    cv.disc(x, y - s // 4, s // 4, GOLD)
    for dx, dy, r, c in ((-s // 3, -s // 4, s // 6, ORANGE),
                         (s // 3, -s // 3, s // 6, RED),
                         (0, -s * 3 // 4, s // 6, GOLD)):
        cv.disc(x + dx, y + dy, r, c)


def draw(cv):
    # ---- outer frame --------------------------------------------------
    cv.frame(16, 16, W - 32, H - 32, INK, 4)
    cv.frame(26, 26, W - 52, H - 52, INK, 1)

    # ---- masthead ------------------------------------------------------
    cv.text_center(40, "THE WORLD TODAY", 9, INK)
    cv.hline(40, 128, W - 80, INK, 3)
    cv.text_center(140, "THURSDAY, 26 NOVEMBER 2026", 2, RED)
    cv.text(48, 140, "NO. 330", 1, GREY)
    cv.text(W - 48 - cv.text_w("ONE PAGE, ONE DAY", 1), 140,
            "ONE PAGE, ONE DAY", 1, GREY)
    cv.hline(40, 164, W - 80, INK, 3)

    # ---- lead headline --------------------------------------------------
    cv.text_center(186, "TARIFF SHOCK", 10, RED)
    cv.text_center(252, "ROCKS MARKETS", 10, INK)
    y = cv.wrap(60, 326, "Trump unveils sweeping new tariffs on China, "
                "Japan, the EU and Taiwan. Nasdaq sinks almost 4% as an "
                "AI-stock rout rattles Wall Street.", 2, INK, W - 120, 20)
    cv.hline(40, 392, W - 80, INK, 2)

    # ---- lead art row: market chart + oil ------------------------------
    # Left: Nasdaq chart panel
    cv.frame(40, 408, 452, 196, INK, 2)
    cv.text(56, 420, "NASDAQ", 2, INK)
    cv.text(56, 444, "-3.9% TODAY", 3, RED)
    pts = [(64, 480), (110, 470), (156, 492), (202, 478), (248, 510),
           (294, 500), (340, 536), (386, 528), (432, 566), (472, 556)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cv.line(x0, y0, x1, y1, RED, 4)
    for (x, yy) in pts:
        cv.disc(x, yy, 4, DARKRED)
    cv.hline(56, 588, 420, GREY, 1)
    cv.text(56, 570, "AI ROUT: TECH STOCKS TUMBLE", 1, GREY)

    # Right: oil panel
    cv.frame(532, 408, 452, 196, INK, 2)
    cv.rect(532, 408, 452, 196, (250, 238, 210))
    cv.frame(532, 408, 452, 196, INK, 2)
    cv.text(548, 420, "BRENT TOPS $94", 3, RED)
    # oil derrick
    cv.line(596, 566, 636, 462, INK, 5)
    cv.line(676, 566, 636, 462, INK, 5)
    cv.line(608, 530, 664, 530, INK, 4)
    cv.line(618, 498, 654, 498, INK, 4)
    cv.line(636, 462, 696, 444, INK, 4)
    # barrel + flame
    cv.rect(760, 520, 90, 60, BLUE)
    cv.rect(760, 520, 90, 12, (16, 44, 84))
    cv.text(772, 542, "OIL", 2, WHITE)
    flame(cv, 805, 520, 46)
    cv.text(548, 574, "HOUTHIS CLAIM STRIKE ON SAUDI", 1, INK)
    cv.text(548, 588, "RAS TANURA REFINERY", 1, INK)

    # ---- middle row: space + Cairo --------------------------------------
    # Left: space panel
    cv.frame(40, 624, 452, 210, INK, 2)
    cv.rect(42, 626, 448, 110, (12, 24, 52))
    for (sx, sy) in [(80, 650), (140, 700), (220, 648), (300, 712),
                      (380, 656), (450, 690), (180, 724), (330, 668)]:
        cv.disc(sx, sy, 3, WHITE)
    # rocket
    cv.rect(236, 660, 20, 56, WHITE)
    cv.rect(236, 660, 20, 12, RED)
    cv.line(236, 660, 246, 640, WHITE, 3)
    cv.line(256, 660, 246, 640, WHITE, 3)
    cv.line(236, 716, 222, 730, RED, 4)
    cv.line(256, 716, 270, 730, RED, 4)
    flame(cv, 246, 724, 22)
    # station
    cv.rect(360, 668, 90, 22, GOLD)
    cv.rect(372, 660, 66, 8, GOLD)
    cv.rect(372, 690, 66, 8, GOLD)
    cv.text(52, 748, "FIRST PAKISTANI ASTRONAUT", 2, RED)
    cv.text(52, 772, "REACHES TIANGONG", 2, RED)
    cv.wrap(52, 796, "Muhammad Zeeshan Ali joins China's Shenzhou-24 "
            "crew at the space station.", 1, INK, 428, 14)

    # Right: Cairo panel
    cv.frame(532, 624, 452, 210, INK, 2)
    cv.rect(534, 626, 448, 110, (48, 40, 36))
    # road
    cv.rect(534, 700, 448, 36, (70, 68, 64))
    cv.hline(534, 717, 448, (240, 200, 40), 3)
    # tanker truck
    cv.rect(600, 664, 190, 34, (200, 200, 200))
    cv.rect(600, 664, 190, 8, (150, 150, 150))
    cv.rect(790, 676, 60, 22, RED)
    cv.disc(640, 700, 12, INK)
    cv.disc(700, 700, 12, INK)
    cv.disc(760, 700, 12, INK)
    cv.disc(820, 700, 12, INK)
    flame(cv, 660, 664, 52)
    flame(cv, 740, 664, 40)
    flame(cv, 880, 664, 30)
    cv.text(548, 748, "31 KILLED IN CAIRO", 2, RED)
    cv.text(548, 772, "TANKER FIRE", 2, RED)
    cv.wrap(548, 796, "Fuel tanker crash ignites a massive blaze on a "
            "Cairo highway.", 1, INK, 428, 14)

    # ---- bottom strip ----------------------------------------------------
    cv.rect(40, 854, W - 80, 92, INK)
    cv.text(56, 866, "ALSO TODAY", 2, GOLD)
    cv.wrap(56, 890, "Israeli strike kills senior Hamas official in "
            "Gaza - Russia's own figures show nearly 500,000 war dead "
            "in Ukraine - US tariffs hit 14 trading partners.", 1,
            WHITE, W - 112, 16)

    # ---- footer ------------------------------------------------------------
    cv.text_center(962, "THE WORLD IN ONE PAGE - 26 NOVEMBER 2026", 1, GREY)



def main():
    cv = Canvas(W, H, PAPER)
    draw(cv)
    n = write_png(cv, OUT)
    print(f"wrote {OUT} ({n} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
