#!/usr/bin/env python3
"""news-image-20261125 -- draw the front page of 25 November 2026.

Draws a 1024x1024 newspaper front page ("THE WORLD TODAY") summing up
Wednesday 25 November 2026, using only the Python standard library.
No network, no clock, no randomness: two runs write byte-identical PNGs.

Layout (1024 x 1024, paper background):
  masthead -> lead story (Pacific treaty) with drawn scene
  -> two rows of two stories each, each with a small drawn pictogram
  -> ALSO TODAY strip -> footer with sources.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (22, 22, 22)
RED = (176, 34, 34)
BLUE = (28, 78, 138)
GREY = (122, 116, 102)
GREEN = (38, 118, 68)
GOLD = (198, 158, 42)
SKY = (168, 205, 228)
SEA = (52, 120, 168)
SAND = (226, 205, 150)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, written as 7 rows of 5 bits ("#" on, "." off).
# Uppercase, lowercase, digits and common punctuation.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": (".....", ".....", ".1110", "....1", ".1111", "10001", ".1111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": (".....", ".....", ".1110", "10000", "10000", "10001", ".1110"),
    "d": ("....1", "....1", ".1111", "10001", "10001", "10001", ".1111"),
    "e": (".....", ".....", ".1110", "10001", "11111", "10000", ".1110"),
    "f": ("..110", ".1001", ".1000", "11110", ".1000", ".1000", ".1000"),
    "g": (".....", ".1111", "10001", "10001", ".1111", "....1", ".1110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("..100", ".....", ".1100", "..100", "..100", "..100", ".1110"),
    "j": ("...10", ".....", "..110", "...10", "...10", "10010", ".1100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": (".1100", "..100", "..100", "..100", "..100", "..100", ".1110"),
    "m": (".....", ".....", "11010", "10101", "10101", "10101", "10101"),
    "n": (".....", ".....", "11110", "10001", "10001", "10001", "10001"),
    "o": (".....", ".....", ".1110", "10001", "10001", "10001", ".1110"),
    "p": (".....", ".....", "11110", "10001", "10001", "11110", "10000"),
    "q": (".....", ".....", ".1111", "10001", "10001", ".1111", "....1"),
    "r": (".....", ".....", "10110", "11001", "10000", "10000", "10000"),
    "s": (".....", ".....", ".1111", "10000", ".1110", "....1", "11110"),
    "t": (".1000", ".1000", "11100", ".1000", ".1000", ".1000", "..110"),
    "u": (".....", ".....", "10001", "10001", "10001", "10011", ".1101"),
    "v": (".....", ".....", "10001", "10001", "10001", ".1010", "..100"),
    "w": (".....", ".....", "10001", "10101", "10101", "10101", ".1010"),
    "x": (".....", ".....", "10001", ".1010", "..100", ".1010", "10001"),
    "y": (".....", ".....", "10001", "10001", ".1111", "....1", ".1110"),
    "z": (".....", ".....", "11111", "...10", "..100", ".1000", "11111"),
    "0": (".1110", "10001", "10011", "10101", "11001", "10001", ".1110"),
    "1": ("..100", ".1100", "..100", "..100", "..100", "..100", ".1110"),
    "2": (".1110", "10001", "....1", "...10", "..100", ".1000", "11111"),
    "3": ("11111", "...10", "..100", "...10", "....1", "10001", ".1110"),
    "4": ("...10", "..110", ".1010", "10010", "11111", "...10", "...10"),
    "5": ("11111", "10000", "11110", "....1", "....1", "10001", ".1110"),
    "6": ("..110", ".1000", "10000", "11110", "10001", "10001", ".1110"),
    "7": ("11111", "....1", "...10", "..100", ".1000", ".1000", ".1000"),
    "8": (".1110", "10001", "10001", ".1110", "10001", "10001", ".1110"),
    "9": (".1110", "10001", "10001", ".1111", "....1", "...10", ".1100"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".1100", ".1100"),
    ",": (".....", ".....", ".....", ".....", ".1100", "..100", ".1000"),
    "'": ("..100", "..100", ".1000", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".1110", ".....", ".....", "....."),
    ":": (".....", ".1100", ".1100", ".....", ".1100", ".1100", "....."),
    ";": (".....", ".1100", ".1100", ".....", ".1100", "..100", ".1000"),
    "!": ("..100", "..100", "..100", "..100", "..100", ".....", "..100"),
    "?": (".1110", "10001", "....1", "...10", "..100", ".....", "..100"),
    "(": ("...10", "..100", ".1000", ".1000", ".1000", "..100", "...10"),
    ")": (".1000", "..100", "...10", "...10", "...10", "..100", ".1000"),
    "$": ("..100", ".1111", "10100", ".1110", "..101", "11110", "..100"),
    "%": ("11001", "11010", "...10", "..100", ".1000", ".1011", "10011"),
    "&": (".1100", "10010", "10100", ".1000", "10101", "10010", ".1101"),
    "/": ("....1", "...10", "...10", "..100", ".1000", ".1000", "10000"),
    "+": (".....", "..100", "..100", "11111", "..100", "..100", "....."),
    "=": (".....", ".....", "11111", ".....", "11111", ".....", "....."),
    '"': (".1010", ".1010", ".1010", ".....", ".....", ".....", "....."),
    "*": (".....", "10101", ".1110", "10101", ".....", ".....", "....."),
    "#": (".1010", ".1010", "11111", ".1010", "11111", ".1010", ".1010"),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "11111"),
    "<": ("...10", "..100", ".1000", "10000", ".1000", "..100", "...10"),
    ">": (".1000", "..100", "...10", "....1", "...10", "..100", ".1000"),
    "[": (".1110", ".1000", ".1000", ".1000", ".1000", ".1000", ".1110"),
    "]": (".1110", "...10", "...10", "...10", "...10", "...10", ".1110"),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill(self, x0, y0, x1, y1, c):
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w, x1); y1 = min(self.h, y1)
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1):
                i = base + (x - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x0, y0, x1, y1, c, t=1):
        self.fill(x0, y0, x1, y0 + t, c)
        self.fill(x0, y1 - t, x1, y1, c)
        self.fill(x0, y0, x0 + t, y1, c)
        self.fill(x1 - t, y0, x1, y1, c)

    def hline(self, x0, x1, y, c, t=1):
        self.fill(x0, y, x1, y + t, c)

    def vline(self, x, y0, y1, c, t=1):
        self.fill(x, y0, x + t, y1, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0); dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def thick_line(self, x0, y0, x1, y1, c, t=3):
        for dx in range(-(t // 2), t // 2 + 1):
            for dy in range(-(t // 2), t // 2 + 1):
                self.line(x0 + dx, y0 + dy, x1 + dx, y1 + dy, c)

    def disc(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, c)

    def triangle(self, ax, ay, bx, by, cx, cy, c):
        # filled triangle by scanlines
        ys = sorted([(ay, ax), (by, bx), (cy, cx)])
        (y0, x0), (y1, x1), (y2, x2) = ys
        def interp(y, ya, xa, yb, xb):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(y0, y2 + 1):
            if y < y1:
                xa = interp(y, y0, x0, y1, x1)
            else:
                xa = interp(y, y1, x1, y2, x2)
            xb = interp(y, y0, x0, y2, x2)
            lo, hi = (xa, xb) if xa < xb else (xb, xa)
            self.fill(int(lo), y, int(hi) + 1, y + 1, c)

    # ---- text ----
    def text_w(self, s, scale):
        return len(s) * 6 * scale

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                g = FONT["?"]
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill(cx + col * scale, y + row * scale,
                                  cx + (col + 1) * scale, y + (row + 1) * scale, c)
            cx += 6 * scale
        return cx

    def text_c(self, y, s, scale, c):
        self.text((self.w - self.text_w(s, scale)) // 2, y, s, scale, c)

    def wrap(self, s, width, scale):
        """Greedy word wrap; returns list of lines fitting `width` px."""
        lines, cur = [], ""
        for word in s.split(" "):
            trial = word if not cur else cur + " " + word
            if self.text_w(trial, scale) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, width, scale, c, lh=None):
        lh = lh or (9 * scale)
        for ln in self.wrap(s, width, scale):
            self.text(x, y, ln, scale, c)
            y += lh
        return y


# ---------------------------------------------------------------- scenes
def draw_lead_scene(cv, x0, y0, x1, y1):
    """Pacific treaty signing: sky, sun, sea, two islands, treaty paper."""
    cv.fill(x0, y0, x1, y1, SKY)
    cv.disc(x0 + 52, y0 + 42, 26, GOLD)                 # sun
    cv.fill(x0, y0 + 128, x1, y1, SEA)                  # sea
    for wx in range(x0 + 8, x1 - 8, 46):                # waves
        cv.hline(wx, wx + 26, y0 + 148, WHITE, 3)
        cv.hline(wx + 12, wx + 38, y0 + 168, WHITE, 3)
    # left island (Solomon Islands) with flag pole
    cv.triangle(x0 + 18, y0 + 132, x0 + 96, y0 + 132, x0 + 57, y0 + 84, GREEN)
    cv.vline(x0 + 57, y0 + 52, y0 + 86, INK, 3)
    cv.fill(x0 + 60, y0 + 52, x0 + 92, y0 + 70, BLUE)
    cv.disc(x0 + 68, y0 + 61, 3, GOLD)
    # right island (Australia) with flag pole
    cv.triangle(x1 - 118, y0 + 132, x1 - 22, y0 + 132, x1 - 70, y0 + 78, SAND)
    cv.vline(x1 - 70, y0 + 46, y0 + 80, INK, 3)
    cv.fill(x1 - 67, y0 + 46, x1 - 35, y0 + 64, RED)
    cv.fill(x1 - 67, y0 + 46, x1 - 51, y0 + 64, BLUE)
    # treaty document between the islands
    dx0, dy0 = x0 + 118, y0 + 118
    cv.fill(dx0, dy0, dx0 + 108, dy0 + 96, WHITE)
    cv.rect(dx0, dy0, dx0 + 108, dy0 + 96, INK, 2)
    cv.hline(dx0 + 10, dx0 + 98, dy0 + 16, INK, 2)
    cv.hline(dx0 + 10, dx0 + 78, dy0 + 30, GREY, 2)
    cv.hline(dx0 + 10, dx0 + 88, dy0 + 42, GREY, 2)
    cv.hline(dx0 + 10, dx0 + 66, dy0 + 54, GREY, 2)
    cv.disc(dx0 + 84, dy0 + 76, 11, RED)                # seal
    cv.disc(dx0 + 84, dy0 + 76, 6, GOLD)
    cv.line(dx0 + 8, dy0 + 88, dx0 + 46, dy0 + 74, INK)  # signature
    cv.line(dx0 + 46, dy0 + 74, dx0 + 62, dy0 + 86, INK)
    cv.rect(x0, y0, x1, y1, INK, 2)


def draw_storefront(cv, x, y, w, h):
    """Supermarket front with a door and a warning sign."""
    cv.fill(x, y, x + w, y + h, WHITE)
    cv.rect(x, y, x + w, y + h, INK, 2)
    cv.fill(x, y, x + w, y + 14, BLUE)
    cv.text(x + 8, y + 3, "MARKET", 1, WHITE)
    for i in range(3):                                   # windows
        cv.fill(x + 10 + i * 30, y + 22, x + 32 + i * 30, y + 40, SKY)
        cv.rect(x + 10 + i * 30, y + 22, x + 32 + i * 30, y + 40, INK, 1)
    cv.fill(x + w // 2 - 10, y + 22, x + w // 2 + 10, y + h - 6, INK)
    cv.disc(x + w - 16, y + 12, 7, RED)
    cv.text(x + w - 19, y + 9, "!", 1, WHITE)


def draw_bars(cv, x, y, w, h):
    """Rising bar chart ending in a tall red bar."""
    cv.fill(x, y, x + w, y + h, WHITE)
    cv.rect(x, y, x + w, y + h, INK, 2)
    heights = [10, 16, 14, 22, 20, 30]
    bw = (w - 16) // len(heights)
    for i, bh in enumerate(heights):
        bx = x + 8 + i * bw
        col = RED if i == len(heights) - 1 else BLUE
        cv.fill(bx, y + h - 6 - bh, bx + bw - 3, y + h - 6, col)
    cv.hline(x + 4, x + w - 4, y + h - 6, INK, 2)


def draw_derrick(cv, x, y, w, h):
    """Oil derrick silhouette."""
    cv.fill(x, y, x + w, y + h, WHITE)
    cv.rect(x, y, x + w, y + h, INK, 2)
    cx = x + w // 2
    cv.thick_line(cx - 26, y + h - 8, cx - 6, y + 8, INK)
    cv.thick_line(cx + 26, y + h - 8, cx + 6, y + 8, INK)
    cv.thick_line(cx - 26, y + h - 8, cx + 26, y + h - 8, INK)
    cv.thick_line(cx - 18, y + h - 20, cx + 18, y + h - 20, INK)
    cv.thick_line(cx - 12, y + h - 32, cx + 12, y + h - 32, INK)
    cv.fill(cx - 6, y + 6, cx + 30, y + 10, INK)
    cv.disc(cx + 34, y + 8, 4, INK)
    cv.disc(cx - 32, y + h - 22, 6, GOLD)
    cv.disc(cx + 32, y + h - 22, 6, GOLD)


def draw_chart(cv, x, y, w, h):
    """Upward arrow chart with a coin."""
    cv.fill(x, y, x + w, y + h, WHITE)
    cv.rect(x, y, x + w, y + h, INK, 2)
    cv.thick_line(x + 10, y + h - 16, x + 34, y + h - 30, GREEN)
    cv.thick_line(x + 34, y + h - 30, x + 58, y + h - 26, GREEN)
    cv.thick_line(x + 58, y + h - 26, x + w - 16, y + 14, GREEN)
    cv.triangle(x + w - 26, y + 8, x + w - 8, y + 8, x + w - 16, y + 24, GREEN)
    cv.disc(x + 16, y + 16, 10, GOLD)
    cv.text(x + 12, y + 12, "E", 1, INK)


# ---------------------------------------------------------------- page
LEAD_HEAD = "AUSTRALIA SEALS HISTORIC SECURITY TREATY WITH SOLOMON ISLANDS"
LEAD_BODY = ("Canberra becomes Honiara's defence partner of choice. The treaty "
             "rules out foreign military bases, boosts police and border "
             "support, and follows the Solomons scrapping its 2022 pact "
             "with China. Albanese and Wale signed in Canberra on Wednesday.")
LEAD_CAP = "Prime ministers Anthony Albanese and Matthew Wale signed the treaty in Canberra."

STORIES = [
    dict(kicker="COLOMBIA", head="GUNMEN HOLD DOZENS HOSTAGE IN CARTAGENA SUPERMARKET",
         body=("Gunmen held dozens hostage in a Cartagena supermarket after a "
               "failed armoured-van robbery. Police said 25 people were "
               "still held inside."),
         pic="store"),
    dict(kicker="UKRAINE WAR", head="MORE THAN 700,000 RUSSIAN SOLDIERS KILLED, STUDY FINDS",
         body=("A new analysis counts more than 700,000 Russian soldiers "
               "killed in nearly five years of war in Ukraine. The toll "
               "lays bare the scale of Moscow's losses."),
         pic="bars"),
    dict(kicker="IRAQ", head="BAGHDAD ORDERS FORCES TO SEIZE KURDISH OILFIELDS",
         body=("Iraq's prime minister ordered federal forces to seize "
               "oilfields and crossings in Kurdish-run regions, "
               "escalating a long dispute over oil."),
         pic="derrick"),
    dict(kicker="GERMANY", head="TAX TAKE TO HIT RECORD ONE TRILLION EUROS BY 2027",
         body=("Germany expects tax revenue to reach a record one trillion "
               "euros by 2027, a new forecast says, as Europe's biggest "
               "economy counts on a slow recovery."),
         pic="chart"),
]

ALSO = [
    "IOWA: Army to blast 68 barrels of toxic lead azide today.",
    "BRITAIN sanctions the Houthis and four top rebel officials.",
    "SENEGAL gets its 2025 AFCON title back after a CAS ruling.",
    "MADRID: Bellingham and Mbappe star as Real beat PSV 5-1.",
]

PICS = {"store": draw_storefront, "bars": draw_bars,
        "derrick": draw_derrick, "chart": draw_chart}


def build():
    cv = Canvas(W, H, PAPER)
    M = 28
    # ---- masthead ----
    cv.text_c(30, "THE WORLD TODAY", 7, INK)
    cv.hline(M, W - M, 118, INK, 2)
    cv.hline(M, W - M, 124, INK, 5)
    cv.text(M, 136, "WORLD EDITION", 1, GREY)
    cv.text_c(134, "Wednesday 25 November 2026", 3, RED)
    rw = cv.text_w("ONE DAY, ONE PAGE", 1)
    cv.text(W - M - rw, 136, "ONE DAY, ONE PAGE", 1, GREY)
    # ---- lead story ----
    y = 168
    cv.text(M, y, "THE PACIFIC  -  LEAD STORY", 2, RED)
    y += 30
    head_lines = cv.wrap(LEAD_HEAD, 600, 3)
    for ln in head_lines:
        cv.text(M, y, ln, 3, INK)
        y += 28
    y += 6
    y = cv.para(M, y, LEAD_BODY, 600, 2, INK)
    y += 8
    y = cv.para(M, y, LEAD_CAP, 600, 1, GREY)
    draw_lead_scene(cv, 660, 198, 996, 432)
    cv.text(660, 440, "The treaty, signed in Canberra.", 1, GREY)
    # ---- rule ----
    cv.hline(M, W - M, 478, INK, 3)
    # ---- story grid: two rows x two columns ----
    col_w = (W - 2 * M - 24) // 2
    row_ys = [492, 696]
    for r in range(2):
        y0 = row_ys[r]
        for c in range(2):
            st = STORIES[r * 2 + c]
            x0 = M + c * (col_w + 24)
            cv.text(x0, y0, st["kicker"], 2, BLUE)
            hy = y0 + 26
            for ln in cv.wrap(st["head"], col_w, 2):
                cv.text(x0, hy, ln, 2, INK)
                hy += 24
            by = hy + 4
            by = cv.para(x0, by, st["body"], col_w, 2, INK)
            # pictogram band at the bottom of the cell
            py = y0 + 148
            PICS[st["pic"]](cv, x0, py, col_w, 44)
        cv.hline(M, W - M, row_ys[r] + 196, INK, 2)
    # ---- also today ----
    y = 902
    cv.text(M, y, "ALSO TODAY", 2, RED)
    y += 28
    half = (W - 2 * M - 24) // 2
    for i, item in enumerate(ALSO):
        x0 = M + (i % 2) * (half + 24)
        yy = y + (i // 2) * 40
        cv.disc(x0 + 4, yy + 7, 4, RED)
        cv.para(x0 + 16, yy, item, half - 16, 2, INK)
    # ---- footer ----
    cv.hline(M, W - M, 1006, INK, 1)
    cv.text(M, 1012, "All events of Wednesday 25 November 2026. Sources: Reuters, AAP, RFE/RL, AP, Des Moines Register.",
            1, GREY)
    return cv


# ---------------------------------------------------------------- png
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    n = write_png(cv, path)
    print(f"wrote {path} ({n} bytes)")


if __name__ == "__main__":
    main()
