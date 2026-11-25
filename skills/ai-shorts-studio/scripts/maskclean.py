#!/usr/bin/env python3
"""Mask cleaner for the masked mascot: removes mouth/lip/smile shapes that video models paint
on a fabric face mask, then restores real fabric texture from a clean reference frame.
usage: python3 maskclean.py in.mp4 out.mp4 [--ref 0.0] [--trim 7.3] [--no-polish]
Works for 9:16 clips and for square images pillarboxed inside 16:9 (black bars are ignored)."""
import cv2, numpy as np, sys, argparse, subprocess, os, tempfile

ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--ref", type=float, default=0.0, help="time (s) of a frame where the mask is clean")
ap.add_argument("--trim", type=float, default=1e9, help="cut the clip at this time (s)")
ap.add_argument("--no-polish", action="store_true")
a = ap.parse_args()

cap = cv2.VideoCapture(a.src)
if not cap.isOpened(): sys.exit(f"cannot open {a.src}")
fps = cap.get(5) or 24; frames = []
while True:
    ok, f = cap.read()
    if not ok or len(frames) / fps >= a.trim: break
    frames.append(f)
if not frames: sys.exit(f"no frames could be read from {a.src}")
H, W = frames[0].shape[:2]
g = cv2.cvtColor(frames[len(frames) // 2], cv2.COLOR_BGR2GRAY)
cols = np.where(g.mean(0) > 14)[0]; rows = np.where(g.mean(1) > 14)[0]
if len(cols) < 16 or len(rows) < 16: cols, rows = np.arange(W), np.arange(H)   # dark frame: use the whole frame
cx0, cx1, cy0, cy1 = cols[0], cols[-1], rows[0], rows[-1]; cw, chh = cx1 - cx0, cy1 - cy0
S = max(cw, chh) / 1080.0 if chh <= cw * 1.3 else cw / 1080.0
K = lambda n: np.ones((max(3, int(n * S)) | 1,) * 2, np.uint8)
portrait = chh > cw * 1.3
by = (0.30, 0.56) if portrait else (0.05, 0.60)             # where the mask can be (fraction of content box)
bx = (0.30, 0.72) if portrait else (0.33, 0.67)

def detect(f):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV); hh, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    dark = ((v < 60) & ~((hh >= 3) & (hh <= 30) & (s > 60))).astype(np.uint8)   # black fabric, not brown hair
    band = np.zeros_like(dark)
    band[cy0 + int(chh * by[0]):cy0 + int(chh * by[1]), cx0 + int(cw * bx[0]):cx0 + int(cw * bx[1])] = 1
    d = cv2.morphologyEx(dark * band, cv2.MORPH_OPEN, K(3)); d = cv2.morphologyEx(d, cv2.MORPH_CLOSE, K(13))
    n, lab, st, _ = cv2.connectedComponentsWithStats(d)
    if n < 2: return None
    i = 1 + np.argmax(st[1:, 4]); m = (lab == i).astype(np.uint8)
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    m = np.zeros_like(m); cv2.drawContours(m, cnts, -1, 1, -1); return m, dark

masks, darks, boxes, areas = [], [], [], []
for f in frames:
    r = detect(f); ok = r is not None
    if ok:
        m, dk = r; ar = m.sum(); b = cv2.boundingRect(m); med = np.median(areas[-30:]) if areas else ar
        ok = 0.6 * med < ar < 1.4 * med and b[3] < b[2] * 1.3 and (not boxes or (abs(b[0] - boxes[-1][0]) < 60 * S and abs(b[1] - boxes[-1][1]) < 60 * S))
    if ok: masks.append(m); darks.append(dk); boxes.append(np.array(b, np.float32)); areas.append(ar)
    else:                                                     # outlier frame: reuse previous mask
        masks.append(masks[-1] if masks else None); darks.append(r[1] if r else None)
        boxes.append(boxes[-1].copy() if boxes else None)
first = next((i for i, m in enumerate(masks) if m is not None), None)
if first is None: sys.exit("no face mask found in this clip — nothing to clean (is it the masked mascot?)")
for i in range(first): masks[i], boxes[i] = masks[first], boxes[first]
B = np.array(boxes); Bs = np.array([B[max(0, i - 2):i + 3].mean(0) for i in range(len(B))])

def logo_mask(v, m):
    x, y, bw, bh = cv2.boundingRect(m)
    lg = (v > 120).astype(np.uint8); lg[:, :x + int(bw * 0.62)] = 0; lg[y + int(bh * 0.8):, :] = 0   # logo sits upper-right
    return cv2.dilate(lg, K(9))

# 1) flatten: replace inside of mask with blur of its own dark pixels (mouth shapes vanish)
flat = []
for f, m, dk in zip(frames, masks, darks):
    if dk is None: dk = np.ones(m.shape, np.uint8)
    v = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)[..., 2]
    df = (dk * m).astype(np.float32)
    num = cv2.GaussianBlur(f.astype(np.float32) * df[..., None], (0, 0), 18 * S); den = cv2.GaussianBlur(df, (0, 0), 18 * S)[..., None] + 1e-3
    inner = cv2.erode(m, K(6)).astype(np.float32) * (1 - logo_mask(v, m))
    al = cv2.GaussianBlur(inner, (0, 0), 2.5 * S)[..., None]
    flat.append((f * (1 - al) + np.clip(num / den, 0, 255) * al).astype(np.uint8))

# 2) polish: add back fabric grain + soft folds from a clean reference frame, warped to follow the mask
if not a.no_polish:
    ri = min(len(frames) - 1, int(a.ref * fps)); ref = frames[ri]; mref = masks[ri]; rx, ry, rw, rh = cv2.boundingRect(mref)
    v = cv2.cvtColor(ref, cv2.COLOR_BGR2HSV)[..., 2]
    lg = cv2.dilate(((v > 120) & (mref > 0)).astype(np.uint8), K(15))
    refc = cv2.inpaint(ref, lg, 9, cv2.INPAINT_TELEA).astype(np.float32)
    fine = refc - cv2.GaussianBlur(refc, (0, 0), 2.0 * S); mid = cv2.GaussianBlur(refc, (0, 0), 2.0 * S) - cv2.GaussianBlur(refc, (0, 0), 14 * S)
    inner_ref = cv2.erode(mref, K(25)).astype(np.float32) * (1 - lg)
    detail = (fine + 0.7 * mid) * cv2.GaussianBlur(inner_ref, (0, 0), 5 * S)[..., None]
    for i in range(len(flat)):
        x, y, w, h = Bs[i]; sx, sy = w / rw, h / rh
        M = np.array([[sx, 0, x - rx * sx], [0, sy, y - ry * sy]], np.float32)
        d = cv2.warpAffine(detail, M, (W, H))
        vv = cv2.cvtColor(frames[i], cv2.COLOR_BGR2HSV)[..., 2]
        gate = cv2.erode(masks[i], K(21)).astype(np.float32) * (1 - logo_mask(vv, masks[i]))
        gate = cv2.GaussianBlur(gate, (0, 0), 6 * S)[..., None]
        flat[i] = np.clip(flat[i].astype(np.float32) + d * gate, 0, 255).astype(np.uint8)

fd, tmp = tempfile.mkstemp(suffix=".avi"); os.close(fd)
try:
    out = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"MJPG"), fps, (W, H))
    for f in flat: out.write(f)
    out.release()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", a.dst], check=True)
finally:
    if os.path.exists(tmp): os.remove(tmp)
print("wrote", a.dst, len(flat), "frames")
