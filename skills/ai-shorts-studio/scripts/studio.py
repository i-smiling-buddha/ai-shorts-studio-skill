#!/usr/bin/env python3
"""Mascot Shorts Studio — renders a 9:16 Short from a clip library + timeline JSON.
usage: python3 studio.py timeline.json out.mp4 [--stills]
"""
import json, os, sys, math, subprocess, tempfile
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
def _font(name, *fallbacks):
    for p in [os.path.join(HERE, "..", "fonts", name), *fallbacks]:
        if os.path.exists(p): return p
    sys.exit(f"font not found: {name} (put it in the skill's fonts/ folder)")
FONT_DEV = _font("Poppins-Bold.ttf", "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf")      # has Devanagari
FONT_TITLE = _font("Anton-Regular.ttf", "/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf")
YEL, WHT, CYN, RED, GRN = (255, 214, 10, 255), (255, 255, 255, 255), (80, 230, 255, 255), (255, 70, 70, 255), (90, 255, 140, 255)
COLORS = {"yellow": YEL, "white": WHT, "cyan": CYN, "red": RED, "green": GRN}

_fc = {}
def F(path, size):
    if (path, size) not in _fc:
        _fc[(path, size)] = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
    return _fc[(path, size)]
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_back(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

# ---------------- text ----------------
def text_img(words, size, colors, stroke=10, font=FONT_DEV, maxw=980, shadow=True):
    f = F(font, size); sp = f.getlength(" ")
    lines, cur, cw = [], [], 0
    for w, c in zip(words, colors):
        wl = f.getlength(w)
        if cur and cw + sp + wl > maxw: lines.append(cur); cur, cw = [], 0
        cur.append((w, c, wl)); cw += (sp if len(cur) > 1 else 0) + wl
    if cur: lines.append(cur)
    asc, desc = f.getmetrics(); lh = int((asc + desc) * 1.08)
    widths = [sum(x[2] for x in L) + sp * (len(L) - 1) for L in lines]
    iw, ih = int(max(widths) + stroke * 4 + 20), int(lh * len(lines) + stroke * 4 + 20)
    im = Image.new("RGBA", (iw, ih), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for li, L in enumerate(lines):
        x = (iw - widths[li]) / 2; y = stroke * 2 + 10 + li * lh
        for w, c, wl in L:
            d.text((x, y), w, font=f, fill=c, stroke_width=stroke, stroke_fill=(0, 0, 0, 255)); x += wl + sp
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.split()[3].point(lambda v: int(v * .55)))
        sh = sh.filter(ImageFilter.GaussianBlur(8)); out = Image.new("RGBA", (iw, ih + 10), (0, 0, 0, 0))
        out.alpha_composite(sh, (0, 10)); out.alpha_composite(im, (0, 0)); im = out
    return im

def paste(fr, rgba, cx, cy, scale=1., alpha=1., rot=0):
    if alpha <= .01 or scale <= .01: return
    im = rgba.rotate(rot, resample=Image.BICUBIC, expand=True) if rot else rgba
    if abs(scale - 1) > 1e-3: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    a = np.asarray(im).astype(np.float32); x0, y0 = int(cx - im.width / 2), int(cy - im.height / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + im.width), min(H, y0 + im.height)
    if xa >= xb or ya >= yb: return
    s = a[ya - y0:yb - y0, xa - x0:xb - x0]; al = s[..., 3:4] / 255. * alpha
    fr[ya:yb, xa:xb] = (fr[ya:yb, xa:xb] * (1 - al) + s[..., :3] * al).astype(np.uint8)

# ---------------- clips ----------------
def content_box(path):
    """Detect pillar/letterbox: returns x0,y0,x1,y1 of non-black content."""
    c = cv2.VideoCapture(path); n = int(c.get(7)); c.set(1, n // 2); ok, f = c.read()
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    cols = np.where(g.mean(0) > 14)[0]; rows = np.where(g.mean(1) > 14)[0]
    return cols[0], rows[0], cols[-1] + 1, rows[-1] + 1

def load_clip(path, box_w, box_h, mode, focus=(0.5, 0.4)):
    """Return list of RGB frames fitted to the box. mode: cover | width_top. Whole image scaled proportionally."""
    x0, y0, x1, y1 = content_box(path)
    c = cv2.VideoCapture(path); fps = c.get(5) or 24; out = []
    while True:
        ok, f = c.read()
        if not ok: break
        f = cv2.cvtColor(f[y0:y1, x0:x1], cv2.COLOR_BGR2RGB); ih, iw = f.shape[:2]
        if mode == "width_top":
            s = box_w / iw; f = cv2.resize(f, (box_w, int(ih * s)), interpolation=cv2.INTER_AREA)
            if f.shape[0] < box_h: f = np.vstack([f, np.repeat(f[-1:], box_h - f.shape[0], 0)])
            out.append(f[:box_h])
        else:
            s = max(box_w / iw, box_h / ih) * 1.06  # small headroom for the push-in
            f = cv2.resize(f, (int(iw * s) + 1, int(ih * s) + 1), interpolation=cv2.INTER_AREA)
            out.append(f)
    return out, fps, focus

def clip_frame(clip, t, box_w, box_h, mode, zoom=1.0):
    frames, fps, focus = clip; n = len(frames); dur = n / fps
    u = t % (2 * dur); u = u if u < dur else 2 * dur - u          # ping-pong only if scene > clip
    f = frames[min(n - 1, int(u * fps))]
    if mode == "width_top":
        if zoom != 1.0:
            hh, ww = f.shape[:2]; f2 = cv2.resize(f, (int(ww * zoom), int(hh * zoom))); xo = (f2.shape[1] - box_w) // 2
            return f2[:box_h, xo:xo + box_w]
        return f
    hh, ww = f.shape[:2]
    s = zoom; cw, ch = int(box_w / s * 1.0), int(box_h / s * 1.0)
    cw, ch = min(cw, ww), min(ch, hh)
    cx = int(clamp(focus[0] * ww - cw / 2, 0, ww - cw)); cy = int(clamp(focus[1] * hh - ch * 0.4, 0, hh - ch))
    return cv2.resize(f[cy:cy + ch, cx:cx + cw], (box_w, box_h), interpolation=cv2.INTER_LINEAR)

# ---------------- captions ----------------
def build_captions(caps, hot):
    chunks = []
    for c in caps:
        ws = c["text"].split(); groups = []; i = 0
        while i < len(ws):
            k = 3 if len(ws) - i != 4 else 2; groups.append(ws[i:i + k]); i += k
        tot = sum(len(" ".join(g)) for g in groups); t = c["s"]
        for g in groups:
            d = (c["e"] - c["s"]) * len(" ".join(g)) / tot; chunks.append([t, t + d, g]); t += d
    for i in range(len(chunks) - 1): chunks[i][1] = min(chunks[i + 1][0], chunks[i][1] + .35)
    imgs = [text_img(g, 78, [COLORS.get(hot.get(w.strip(",.?!"), ""), WHT) for w in g], stroke=9) for _, _, g in chunks]
    return chunks, imgs

def draw_caption(fr, t, cy, CH):
    chunks, imgs = CH
    for (s, e, g), im in zip(chunks, imgs):
        if s <= t < e:
            p = (t - s) / .18; paste(fr, im, W / 2, cy, scale=.75 + .25 * ease_back(p), alpha=clamp(p * 1.5))

# ---------------- board card ----------------
def chip(txt, col):
    f = F(FONT_DEV, 40); w = int(f.getlength(txt)) + 56
    im = Image.new("RGBA", (w, 76), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 75), 38, fill=(255, 255, 255, 28), outline=tuple(col) + (255,), width=3)
    d.text((28, 12), txt, font=f, fill=WHT); return im

def make_card(c, total):
    col = tuple(c.get("color", [0, 229, 255])); c["_col"] = col
    c["_num"] = text_img(["#%d" % c["rank"]], 290, [YEL if c["rank"] == 1 else col + (255,)], 12, FONT_TITLE)
    c["_name"] = text_img([c["name"]], 150 if len(c["name"]) < 9 else 120, [WHT], 10, FONT_TITLE)
    c["_tag"] = text_img(c.get("tag", "").split(), 58, [col + (255,)] * len(c.get("tag", "").split()), 6)
    c["_chips"] = [chip(x, col) for x in c.get("chips", [])]
    c["_logo"] = None
    if c.get("logo") and os.path.exists(c["logo"]):  # path resolved against the timeline folder in main()
        lg = Image.open(c["logo"]).convert("RGBA"); s = 150 / max(lg.size)   # official file, scaled proportionally only
        c["_logo"] = lg.resize((int(lg.width * s), int(lg.height * s)), Image.LANCZOS)
    c["_ranks"] = [text_img([str(n)], 46, [WHT], 4, FONT_TITLE, shadow=False) for n in range(total, 0, -1)]

def draw_card(fr, c, t, CARD_H, total):
    col = c["_col"]; yy, xx = np.mgrid[0:CARD_H, 0:W].astype(np.float32)
    base = np.zeros((CARD_H, W, 3), np.float32); base[:] = (10, 12, 24)
    r = np.sqrt((xx - W * (.5 + .18 * math.sin(t * .7))) ** 2 + (yy - CARD_H * .45) ** 2)
    base += np.exp(-(r / 520) ** 2)[..., None] * np.array(col, np.float32) * (.5 + .1 * math.sin(t * 3))
    base += ((((xx + t * 20) % 60) < 2) | (((yy + t * 20) % 60) < 2)).astype(np.float32)[..., None] * 18
    fr[:CARD_H] = np.clip(base, 0, 255).astype(np.uint8)
    for i, n in enumerate(range(total, 0, -1)):
        cx = W / 2 - (total - 1) * 52.5 + i * 105; active = n == c["rank"]; done = n > c["rank"]
        cv2.circle(fr, (int(cx), 90), 40, col if active else ((70, 75, 95) if not done else (40, 44, 60)), -1, cv2.LINE_AA)
        cv2.circle(fr, (int(cx), 90), 40, (255, 255, 255), 3 if active else 1, cv2.LINE_AA)
        paste(fr, c["_ranks"][i], cx, 92, alpha=1 if (active or not done) else .5)
    p = (t - c["num_t"]) / .35
    if p > 0:
        if c["_logo"] is not None:   # rank + official logo side by side
            paste(fr, c["_num"], W / 2 - 120, 305, scale=.4 + .6 * ease_back(p), alpha=clamp(p * 2), rot=(1 - ease_out(p)) * 12)
            paste(fr, c["_logo"], W / 2 + 170, 305, scale=ease_back((t - c["num_t"] - .15) / .35), alpha=clamp(p * 2))
        else:
            paste(fr, c["_num"], W / 2, 305, scale=.4 + .6 * ease_back(p), alpha=clamp(p * 2), rot=(1 - ease_out(p)) * 12)
    p = (t - c["name_t"]) / .35
    if p > 0: paste(fr, c["_name"], W / 2 + (1 - ease_out(p)) * 600, 545, alpha=clamp(p * 2))
    p = (t - c["name_t"] - .35) / .3
    if p > 0: paste(fr, c["_tag"], W / 2, 680, alpha=clamp(p * 1.5), scale=.9 + .1 * ease_out(p))
    rows, cur, cw = [], [], 0
    for ch in c["_chips"]:
        if cur and cw + ch.width + 20 > 1000: rows.append(cur); cur, cw = [], 0
        cur.append(ch); cw += ch.width + 20
    if cur: rows.append(cur)
    k = 0
    for ri, row in enumerate(rows):
        x = (W - (sum(ch.width for ch in row) + 20 * (len(row) - 1))) / 2
        for ch in row:
            p = (t - c["name_t"] - .8 - k * .15) / .3
            if p > 0: paste(fr, ch, x + ch.width / 2, 800 + ri * 90 + (1 - ease_out(p)) * 40, alpha=clamp(p * 2))
            x += ch.width + 20; k += 1
    cv2.line(fr, (0, CARD_H), (W, CARD_H), col, 6, cv2.LINE_AA)

# ---------------- outro bits ----------------
def follow_pill(name, avatar=None):
    im = Image.new("RGBA", (640, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 639, 149), 75, fill=(255, 255, 255, 255))
    if avatar and os.path.exists(avatar):
        av = Image.open(avatar).convert("RGBA").resize((114, 114)); mk = Image.new("L", (114, 114), 0)
        ImageDraw.Draw(mk).ellipse((0, 0, 113, 113), fill=255); im.paste(av, (18, 18), mk)
    else:
        d.ellipse((18, 18, 132, 132), fill=(180, 140, 255, 255))
        d.text((75, 75), "".join(w[0] for w in name.split()[:2]).upper(), font=F(FONT_TITLE, 54), fill=WHT, anchor="mm")
    d.text((150, 26), name, font=F(FONT_DEV, 42), fill=(20, 20, 30, 255))
    d.rounded_rectangle((150, 84, 330, 132), 24, fill=(230, 30, 60, 255))
    d.text((240, 108), "Follow", font=F(FONT_DEV, 32), fill=WHT, anchor="mm"); return im

def comment_icon():
    im = Image.new("RGBA", (200, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((5, 5, 195, 145), 40, fill=YEL, outline=(0, 0, 0, 255), width=6)
    d.polygon([(50, 140), (40, 185), (95, 142)], fill=YEL, outline=(0, 0, 0, 255))
    for i in range(3): d.ellipse((50 + i * 40, 62, 70 + i * 40, 82), fill=(0, 0, 0, 255))
    return im

GRAD = np.clip((np.arange(H) - H * .62) / (H * .38), 0, 1)[:, None, None].astype(np.float32) * .55
def shade(fr, y0=0): return (fr.astype(np.float32) * (1 - GRAD[y0:y0 + fr.shape[0]])).astype(np.uint8)

# ---------------- main ----------------
def main():
    tl_path, out = sys.argv[1], sys.argv[2]; stills = "--stills" in sys.argv
    T = json.load(open(tl_path)); base = os.path.dirname(os.path.abspath(tl_path))
    L = json.load(open(os.path.join(base, T["library"])))
    lib = {c["id"]: c for c in L["clips"]}
    for c in lib.values():
        if not c.get("mask_ok", False): print("WARNING: clip not mask-checked:", c["id"])
    CARD_H = T.get("card_height", 945)
    CH = build_captions(T.get("captions", []), T.get("hot_words", {}))
    total = max([s["card"]["rank"] for s in T["scenes"] if s["type"] == "board"] or [0])
    for s in T["scenes"]:
        if s["type"] == "board":
            if s["card"].get("logo"): s["card"]["logo"] = os.path.join(base, s["card"]["logo"])
            make_card(s["card"], total)
    if out and os.path.dirname(out): os.makedirs(os.path.dirname(out), exist_ok=True)
    FLASH = float(T.get("flash", 160))   # white flash strength at cuts (0 = off)
    tmp = tempfile.mkdtemp(); parts = []
    for si, s in enumerate(T["scenes"]):
        cl = lib[s["clip"]]; path = os.path.join(base, L.get("root", "."), cl["file"])
        if s["type"] == "board": box, mode = (W, H - CARD_H), "width_top"
        else: box, mode = (W, H), "cover"
        clip = load_clip(path, box[0], box[1], mode, tuple(cl.get("focus", [.5, .4])))
        ov = s.get("overlay", {})
        if ov.get("title"):
            ov["_imgs"] = [text_img(line["words"], line.get("size", 170), [COLORS.get(x, WHT) for x in line["colors"]], 12,
                                    FONT_TITLE if line.get("font") == "title" else FONT_DEV) for line in ov["title"]]
        if s["type"] == "outro":
            ov["_q"] = text_img(ov.get("question", "").split(), 96, [COLORS.get(x, WHT) for x in ov.get("question_colors", [])] or [WHT] * 9, 11)
            ov["_c"] = comment_icon(); ov["_f"] = follow_pill(T.get("channel_name", "My Channel"), T.get("channel_avatar") and os.path.join(base, T["channel_avatar"]))

        def frame(t):
            lt = t - s["t0"]; zoom = 1.0 + 0.003 * lt
            if s["type"] == "board":
                fr = np.zeros((H, W, 3), np.uint8)
                fr[CARD_H:] = shade(clip_frame(clip, lt + s.get("clip_offset", 0), *box, mode, zoom), CARD_H)
                draw_card(fr, s["card"], t, CARD_H, total); draw_caption(fr, t, 1770, CH)
            else:
                pz = 1 + .07 * (1 - ease_out(lt / .28)) if si > 0 else 1
                fr = shade(clip_frame(clip, lt + s.get("clip_offset", 0), *box, mode, zoom * pz))
                if ov.get("title"):
                    for li, (line, im) in enumerate(zip(ov["title"], ov["_imgs"])):
                        p = (t - line["t"]) / .4
                        if p > 0: paste(fr, im, W / 2, line["y"], scale=.5 + .5 * ease_back(p), alpha=clamp(p * 2))
                if s["type"] == "outro":
                    p = (t - ov["question_t"]) / .4
                    if p > 0: paste(fr, ov["_q"], W / 2, 170, scale=.5 + .5 * ease_back(p), alpha=clamp(p * 2))
                    p = (t - ov["comment_t"]) / .35
                    if p > 0: paste(fr, ov["_c"], 880, 520 + 8 * math.sin(t * 6), scale=ease_back(p), rot=8 * math.sin(t * 4))
                    p = (t - ov["follow_t"]) / .35
                    if p > 0: paste(fr, ov["_f"], W / 2, 1270, scale=ease_back(p))
                draw_caption(fr, t, 1560 if s["type"] == "full" else 1640, CH)
            if si > 0 and lt < .15: fr = np.clip(fr.astype(np.float32) + FLASH * (1 - lt / .15), 0, 255).astype(np.uint8)
            return fr

        if stills:
            tm = (s["t0"] + s["t1"]) / 2 if s["type"] != "board" else s["card"]["name_t"] + 2.5
            Image.fromarray(frame(max(s["t0"] + .5, min(tm, s["t1"] - .05)))).resize((540, 960)).save(os.path.join(os.path.dirname(out) or ".", f"still_{si:02d}.jpg"), quality=88)
            continue
        part = os.path.join(tmp, f"s{si:02d}.mp4")
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", part], stdin=subprocess.PIPE)
        for n in range(round(s["t0"] * FPS), round(s["t1"] * FPS)): p.stdin.write(frame(n / FPS).tobytes())
        p.stdin.close(); p.wait(); parts.append(part); print("scene", si, "done", flush=True)
        del clip
    if stills: return
    lst = os.path.join(tmp, "list.txt"); open(lst, "w").write("".join(f"file '{x}'\n" for x in parts))
    vid = os.path.join(tmp, "video.mp4"); subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid], check=True)
    # SFX: whoosh at scene cuts, pop on card numbers
    sr = 48000; dur = T["scenes"][-1]["t1"]; sfx = np.zeros(int(dur * sr) + sr, np.float32); rng = np.random.default_rng(1)
    def add(t, y):
        i = int(t * sr); sfx[i:i + len(y)] += y[:max(0, len(sfx) - i)]
    for s in T["scenes"][1:]:
        n = int(.45 * sr); x = rng.standard_normal(n).astype(np.float32); y = np.convolve(x, np.ones(40) / 40, "same")
        add(s["t0"] - .05, (y / np.abs(y).max() * np.sin(np.linspace(0, np.pi, n)) ** 2 * .2).astype(np.float32))
    tt = np.arange(int(.12 * sr)) / sr; pop = (np.sin(2 * np.pi * 880 * (1 + 2 * np.exp(-tt * 40)) * tt) * np.exp(-tt * 30) * .18).astype(np.float32)
    for s in T["scenes"]:
        if s["type"] == "board" and not s["card"].get("no_pop"): add(s["card"]["num_t"], pop)
    import wave
    sp = os.path.join(tmp, "sfx.wav"); w = wave.open(sp, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(sfx, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    voice = os.path.join(base, T["voice"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", voice, "-i", sp, "-filter_complex",
                    "[1:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3,loudnorm=I=-15:TP=-1.5,aresample=48000[v];[v][2:a]amix=inputs=2:normalize=0:duration=first[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    print("wrote", out)

if __name__ == "__main__":
    main()
