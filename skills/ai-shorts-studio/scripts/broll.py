"""Code-rendered B-roll inserts for AI Shorts Studio (no credits, no readable text, no logos).

broll_frame(style, t, dur, color, w, h) -> RGB uint8 array (h, w, 3)
styles: code, search, multimodal, mindmap, chat
Everything is abstract: bars instead of text, simple glyphs instead of brand marks.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

STYLES = ("code", "search", "multimodal", "mindmap", "chat")


def _clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def _ease(t): t = _clamp(t); return 1 - (1 - t) ** 3


def _bg(w, h, color, t):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base = np.zeros((h, w, 3), np.float32); base[:] = (8, 10, 22)
    r = np.sqrt((xx - w * (0.5 + 0.12 * math.sin(t * 0.8))) ** 2 + (yy - h * 0.45) ** 2)
    base += np.exp(-(r / (0.55 * w)) ** 2)[..., None] * np.array(color, np.float32) * 0.45
    grid = (((xx + t * 25) % 54) < 1.5) | (((yy + t * 25) % 54) < 1.5)
    base += grid.astype(np.float32)[..., None] * 14
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")


def _glow(layer, radius=14, strength=1.0):
    g = layer.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        a = np.asarray(g).astype(np.float32); a[..., 3] *= strength; g = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(layer); return out


def _panel(d, box, color, alpha=200, radius=28):
    d.rounded_rectangle(box, radius, fill=(18, 22, 40, alpha), outline=tuple(color) + (230,), width=3)


def _bar(d, x, y, length, hgt, rgba): d.rounded_rectangle((x, y, x + max(hgt, length), y + hgt), hgt // 2, fill=rgba)


def _code(L, d, w, h, t, dur, c):
    x0, y0, x1, y1 = int(w * .08), int(h * .1), int(w * .92), int(h * .9)
    _panel(d, (x0, y0, x1, y1), c)
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((x0 + 26 + i * 34, y0 + 22, x0 + 46 + i * 34, y0 + 42), fill=col + (255,))
    rng = np.random.default_rng(7); palette = [(120, 200, 255), (255, 140, 200), (170, 255, 170), (255, 220, 120), tuple(c)]
    lines = 16; lh = (y1 - y0 - 90) / lines; shown = (t / dur) * lines * 1.3
    for i in range(lines):
        y = y0 + 70 + i * lh; indent = int(rng.integers(0, 4)) * 40
        d.text((x0 + 24, y), "", fill=(0, 0, 0, 0))
        _bar(d, x0 + 24, int(y + lh * .3), 26, int(lh * .35), (90, 100, 130, 200))      # line-number stub
        segs = rng.integers(2, 5); x = x0 + 80 + indent
        for k in range(segs):
            ln = int(rng.integers(50, 190)); p = _clamp(shown - i)
            if p <= 0: break
            col = palette[int(rng.integers(0, len(palette)))]
            ghost = i == int(shown) + 1
            _bar(d, x, int(y + lh * .28), int(ln * (p if not ghost else 1)), int(lh * .42), col + ((90 if ghost else 235),))
            x += ln + 18
        if i == min(lines - 1, int(shown)) and int(t * 3) % 2 == 0:
            d.rectangle((x + 6, int(y + lh * .15), x + 12, int(y + lh * .85)), fill=(255, 255, 255, 255))


def _search(L, d, w, h, t, dur, c):
    cx = w // 2
    d.rounded_rectangle((int(w * .1), int(h * .1), int(w * .9), int(h * .1) + 90), 45, fill=(255, 255, 255, 40), outline=tuple(c) + (255,), width=3)
    d.ellipse((int(w * .1) + 30, int(h * .1) + 25, int(w * .1) + 70, int(h * .1) + 65), outline=(255, 255, 255, 230), width=5)
    d.line((int(w * .1) + 64, int(h * .1) + 60, int(w * .1) + 80, int(h * .1) + 76), fill=(255, 255, 255, 230), width=6)
    typed = _ease(t / (dur * .35)); _bar(d, int(w * .1) + 100, int(h * .1) + 35, int(420 * typed), 20, (255, 255, 255, 200))
    ans = (int(w * .15), int(h * .55), int(w * .85), int(h * .9))
    srcs = [(int(w * .2), int(h * .33)), (cx, int(h * .3)), (int(w * .8), int(h * .33))]
    for i, (sx, sy) in enumerate(srcs):
        p = _ease((t - dur * (.3 + i * .12)) / .35)
        if p <= 0: continue
        d.line((sx, sy + 40, cx, ans[1]), fill=tuple(c) + (int(160 * p),), width=3)
        d.rounded_rectangle((sx - 95, sy - 40 + int(20 * (1 - p)), sx + 95, sy + 40 + int(20 * (1 - p))), 20, fill=(30, 36, 64, int(230 * p)), outline=tuple(c) + (int(255 * p),), width=2)
        d.ellipse((sx - 80, sy - 14, sx - 52, sy + 14), fill=tuple(c) + (int(255 * p),))
        _bar(d, sx - 40, sy - 8, 110, 16, (255, 255, 255, int(200 * p)))
    p = _ease((t - dur * .65) / .4)
    if p > 0:
        _panel(d, ans, c, int(200 * p))
        for i in range(4):
            _bar(d, ans[0] + 40, ans[1] + 45 + i * 52, int((ans[2] - ans[0] - 80) * (.95 - .15 * (i % 2)) * p), 22, (230, 235, 255, int(220 * p)))


def _multimodal(L, d, w, h, t, dur, c):
    cx, cy = w // 2, int(h * .5)
    pulse = 1 + .06 * math.sin(t * 6)
    for k in range(3, 0, -1):
        r = int((70 + k * 28) * pulse)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tuple(c) + (40 * k,))
    R = int(min(w, h) * .36)
    for i in range(3):
        a = t * .9 + i * 2 * math.pi / 3; x, y = int(cx + R * math.cos(a)), int(cy + R * .75 * math.sin(a))
        p = _ease((t - i * .25) / .4)
        if p <= 0: continue
        d.line((cx, cy, x, y), fill=tuple(c) + (int(120 * p),), width=3)
        d.rounded_rectangle((x - 80, y - 60, x + 80, y + 60), 22, fill=(24, 28, 52, int(240 * p)), outline=tuple(c) + (int(255 * p),), width=3)
        if i == 0:   # image tile: sun + mountains
            d.ellipse((x + 22, y - 40, x + 50, y - 12), fill=(255, 210, 90, int(255 * p)))
            d.polygon([(x - 62, y + 45), (x - 15, y - 15), (x + 20, y + 25), (x + 40, y + 5), (x + 65, y + 45)], fill=(120, 200, 255, int(255 * p)))
        elif i == 1:  # audio waveform
            for k in range(9):
                bh = int(12 + 34 * abs(math.sin(t * 5 + k)))
                d.rounded_rectangle((x - 60 + k * 14, y - bh, x - 52 + k * 14, y + bh), 4, fill=(255, 255, 255, int(230 * p)))
        else:         # text lines
            for k in range(3): _bar(d, x - 58, y - 32 + k * 26, [116, 90, 104][k], 14, (255, 255, 255, int(220 * p)))
    d.ellipse((cx - 62, cy - 62, cx + 62, cy + 62), fill=(255, 255, 255, 235))


def _mindmap(L, d, w, h, t, dur, c):
    cx, cy = w // 2, int(h * .5)
    nodes = [(0, 0)] + [(math.cos(a) * .32, math.sin(a) * .36) for a in np.linspace(-math.pi / 2, 1.5 * math.pi, 7)[:-1]]
    kids = [(math.cos(a) * .44, math.sin(a) * .44) for a in np.linspace(-math.pi / 3, 1.67 * math.pi, 7)[:-1]]
    for i, (nx, ny) in enumerate(nodes[1:]):
        p = _ease((t - .2 - i * .18) / .35)
        if p <= 0: continue
        x, y = int(cx + nx * w * p), int(cy + ny * h * p)
        d.line((cx, cy, x, y), fill=tuple(c) + (200,), width=4)
        kx, ky = int(cx + kids[i][0] * w * p), int(cy + kids[i][1] * h * p)
        q = _ease((t - 1.0 - i * .12) / .35)
        if q > 0:
            d.line((x, y, kx, ky), fill=tuple(c) + (int(140 * q),), width=2)
            d.ellipse((kx - 16, ky - 16, kx + 16, ky + 16), fill=(255, 255, 255, int(200 * q)))
        d.rounded_rectangle((x - 75, y - 30, x + 75, y + 30), 30, fill=(28, 30, 56, 240), outline=tuple(c) + (255,), width=3)
        _bar(d, x - 50, y - 8, 100, 16, (255, 255, 255, 220))
    r = int(70 * (1 + .05 * math.sin(t * 5)))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tuple(c) + (255,))
    d.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), fill=(255, 255, 255, 240))


def _chat(L, d, w, h, t, dur, c):
    msgs = [("u", 2), ("a", 3), ("a_img", 0), ("u", 1), ("a", 2)]
    y = int(h * .88)
    vis = [m for i, m in enumerate(msgs) if t > .2 + i * .45]
    for i, (who, n) in enumerate(reversed(vis)):
        right = who == "u"; hh = 70 + n * 34 if who != "a_img" else 190
        bw = int(w * (.5 if right else .66)); x0 = int(w * .92) - bw if right else int(w * .08)
        y -= hh + 26
        if y < h * .05: break
        fill = tuple(c) + (235,) if right else (34, 38, 66, 240)
        d.rounded_rectangle((x0, y, x0 + bw, y + hh), 30, fill=fill)
        if who == "a_img":
            for k in range(3):
                tx = x0 + 24 + k * ((bw - 48) // 3)
                d.rounded_rectangle((tx, y + 22, tx + (bw - 48) // 3 - 14, y + hh - 22), 18, fill=[(120, 200, 255, 255), (255, 170, 120, 255), (170, 255, 170, 255)][k])
        else:
            for k in range(n): _bar(d, x0 + 30, y + 30 + k * 34, int((bw - 60) * (.9 - .2 * (k == n - 1))), 18, (255, 255, 255, 220))
    if int(t * 3) % 2 == 0 and t > .2 + len(msgs) * .45 - .2:
        for k in range(3): d.ellipse((int(w * .1) + k * 30, int(h * .9), int(w * .1) + 18 + k * 30, int(h * .9) + 18), fill=(255, 255, 255, 200))


_DRAW = {"code": _code, "search": _search, "multimodal": _multimodal, "mindmap": _mindmap, "chat": _chat}


def broll_frame(style, t, dur, color, w, h):
    if style not in _DRAW: raise ValueError(f"unknown B-roll style {style!r}; use one of {STYLES}")
    color = tuple(int(v) for v in color)
    img = _bg(w, h, color, t)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    _DRAW[style](layer, d, w, h, t, dur, color)
    img.alpha_composite(_glow(layer, 10, .9))
    return np.asarray(img.convert("RGB"))
