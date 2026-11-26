#!/usr/bin/env python3
"""Quality control for AI Shorts Studio.

  python3 qc.py pre  timeline.json            # before rendering: plan, clips, captions, cards, logos
  python3 qc.py post out.mp4 [--timeline t.json] [--sheet qc_cuts.jpg]   # after rendering: format, loudness, black/frozen/silence, flashes

Every check is graded PASS / WARN / FAIL. Exit code 1 if anything FAILs.
Ideas for the post-render checks are adapted (no code copied) from kajisho5/ffmpeg-skill (graded PASS/WARN/FAIL content
checks) and browser-use/video-use (inspect the render at every cut, loudness targets).
"""
import json, os, re, subprocess, sys

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
MAX_HOLD = 1.0        # seconds a clip may hold its last frame when the scene is longer than the clip


class Report:
    def __init__(self): self.rows = []
    def add(self, grade, check, msg): self.rows.append((grade, check, msg))
    def ok(self, check, msg="ok"): self.add(PASS, check, msg)
    def warn(self, check, msg): self.add(WARN, check, msg)
    def fail(self, check, msg): self.add(FAIL, check, msg)
    @property
    def failed(self): return any(g == FAIL for g, _, _ in self.rows)
    def print(self, title):
        print(f"== QC {title} ==")
        for g, c, m in self.rows: print(f"[{g}] {c}: {m}")
        n = {k: sum(1 for g, _, _ in self.rows if g == k) for k in (PASS, WARN, FAIL)}
        print(f"-- {n[PASS]} pass, {n[WARN]} warn, {n[FAIL]} fail -> {'FAIL' if self.failed else 'OK'}")


def probe(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate,nb_frames",
                              "-of", "json", path], capture_output=True, text=True, check=True).stdout
        return json.loads(out)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return None


def duration(path):
    p = probe(path)
    try: return float(p["format"]["duration"])
    except (TypeError, KeyError, ValueError): return None


def vstream(p):
    return next((s for s in (p or {}).get("streams", []) if s.get("codec_type") == "video"), None)


# ------------------------------------------------------------------ pre-render
def check_timeline(tl_path, rep=None):
    rep = rep or Report()
    try:
        T = json.load(open(tl_path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        rep.fail("timeline", f"cannot read {tl_path}: {e}"); return rep
    base = os.path.dirname(os.path.abspath(tl_path))
    try:
        L = json.load(open(os.path.join(base, T["library"]), encoding="utf-8"))
        lib = {c["id"]: c for c in L["clips"]}; root = os.path.join(base, L.get("root", "."))
    except (OSError, KeyError, json.JSONDecodeError) as e:
        rep.fail("library", f"cannot read library: {e}"); return rep

    voice = os.path.join(base, T.get("voice", ""))
    vdur = duration(voice) if T.get("voice") else None
    if vdur is None: rep.fail("voice", f"voice file missing or unreadable: {T.get('voice')}")
    else: rep.ok("voice", f"{vdur:.2f} s")

    scenes = T.get("scenes", [])
    if not scenes: rep.fail("scenes", "no scenes"); return rep
    # coverage: sorted, contiguous, no gaps/overlaps, covers the voice
    t = 0.0
    for i, s in enumerate(scenes):
        if s.get("type") not in ("full", "board", "outro"): rep.fail(f"scene {i}", f"unknown type {s.get('type')!r}")
        t0, t1 = s.get("t0"), s.get("t1")
        if not isinstance(t0, (int, float)) or not isinstance(t1, (int, float)) or t1 <= t0:
            rep.fail(f"scene {i}", f"bad times t0={t0} t1={t1}"); continue
        if abs(t0 - t) > 0.02: rep.fail(f"scene {i}", f"{'gap' if t0 > t else 'overlap'} of {abs(t0 - t):.2f} s before it (starts {t0}, previous ends {t:.2f})")
        if t1 - t0 < 1.2: rep.warn(f"scene {i}", f"only {t1 - t0:.2f} s — feels like a flash")
        if t1 - t0 > 9.5: rep.warn(f"scene {i}", f"{t1 - t0:.1f} s on one layout — split it or add B-roll (target 2–4 s changes, items 6–8 s)")
        t = t1
    if vdur and abs(t - vdur) > 0.35: rep.fail("coverage", f"scenes end at {t:.2f} s but voice is {vdur:.2f} s")
    else: rep.ok("coverage", f"scenes cover 0–{t:.2f} s")

    # clips: exist, distinct, long enough (no looping), checked, board clips square
    used = {}
    for i, s in enumerate(scenes):
        cid = s.get("clip"); c = lib.get(cid)
        if not c: rep.fail(f"scene {i}", f"clip id {cid!r} not in library"); continue
        if cid in used: rep.fail(f"scene {i}", f"clip {cid!r} already used in scene {used[cid]} — every scene needs its own clip")
        used.setdefault(cid, i)
        path = os.path.join(root, c["file"]); p = probe(path); vs = vstream(p)
        if not vs: rep.fail(f"clip {cid}", f"missing or unreadable: {path}"); continue
        cdur = float(p["format"]["duration"]) - s.get("clip_offset", 0)
        need = s["t1"] - s["t0"]
        if need > cdur + MAX_HOLD and not T.get("allow_loop"):
            rep.fail(f"clip {cid}", f"{cdur:.1f} s usable but scene needs {need:.1f} s — would loop. Split the scene or add a clip")
        elif need > cdur: rep.warn(f"clip {cid}", f"holds last frame for {need - cdur:.2f} s")
        if not c.get("mask_ok", False): rep.warn(f"clip {cid}", "not mask/hand-checked (mask_ok false)")
        if s.get("type") == "board":
            w, h = int(vs["width"]), int(vs["height"])
            if h > w * 1.3: rep.fail(f"clip {cid}", "board panel needs a square (sq_) clip, got 9:16 — never crop 9:16 into the panel")

    # cards and logos
    ranks = []
    for i, s in enumerate(scenes):
        if s.get("type") != "board": continue
        c = s.get("card") or {}
        for k in ("rank", "name", "num_t", "name_t"):
            if k not in c: rep.fail(f"card {i}", f"missing {k}")
        if "num_t" in c and not (s["t0"] - 0.05 <= c["num_t"] <= s["t1"]) and not c.get("no_pop"):
            rep.fail(f"card {i}", f"num_t {c['num_t']} outside scene {s['t0']}–{s['t1']}")
        if "num_t" in c and "name_t" in c and c["name_t"] < c["num_t"]: rep.warn(f"card {i}", "name appears before the rank")
        br = s.get("broll")
        if br:
            if br.get("style") not in ("code", "search", "multimodal", "mindmap", "chat"): rep.fail(f"broll {i}", f"unknown style {br.get('style')!r}")
            if not (s["t0"] <= br.get("t0", -1) < br.get("t1", -1) <= s["t1"]): rep.fail(f"broll {i}", f"window {br.get('t0')}–{br.get('t1')} outside scene {s['t0']}–{s['t1']}")
            elif "name_t" in c and br["t0"] < c["name_t"] + 0.8: rep.warn(f"broll {i}", "starts before the name has settled — viewers may miss which tool it is")
        if not c.get("no_pop"): ranks.append(c.get("rank"))
        logo = c.get("logo")
        if not logo: rep.warn(f"card {i}", f"no logo for {c.get('name')} — viewers may not recognise the product")
        else:
            lp = os.path.join(base, logo)
            if not os.path.exists(lp): rep.fail(f"card {i}", f"logo file missing: {logo}")
            else:
                try:
                    from PIL import Image
                    im = Image.open(lp)
                    if im.mode not in ("RGBA", "LA", "P") and "transparency" not in im.info:
                        rep.warn(f"card {i}", f"logo {logo} has no transparency")
                except Exception as e: rep.fail(f"card {i}", f"logo unreadable: {e}")
    if ranks and sorted(r for r in ranks if r is not None) != list(range(1, len(ranks) + 1)):
        rep.warn("ranks", f"ranks are {ranks} — expected a full countdown")

    # captions
    caps = T.get("captions", [])
    prev = 0.0
    for j, c in enumerate(caps):
        s0, e0, txt = c.get("s"), c.get("e"), c.get("text", "")
        if not isinstance(s0, (int, float)) or not isinstance(e0, (int, float)) or e0 <= s0:
            rep.fail(f"caption {j}", f"bad times {s0}–{e0}"); continue
        if s0 < prev - 0.05: rep.warn(f"caption {j}", f"overlaps the previous caption ({s0} < {prev:.2f})")
        if vdur and e0 > vdur + 0.1: rep.fail(f"caption {j}", f"ends at {e0} after the voice ({vdur:.2f} s)")
        cps = len(txt) / (e0 - s0)
        if cps > 22: rep.warn(f"caption {j}", f"{cps:.0f} chars/s — too fast to read: {txt[:30]}")
        prev = e0
    if caps: rep.ok("captions", f"{len(caps)} lines checked")
    else: rep.warn("captions", "no captions")

    av = T.get("channel_avatar")
    if av and not os.path.exists(os.path.join(base, av)): rep.fail("outro", f"channel avatar missing: {av}")
    if not T.get("channel_name"): rep.warn("outro", "no channel_name — follow pill will say 'My Channel'")
    fl = T.get("flash", 160)
    if not (0 <= fl <= 255): rep.fail("flash", f"flash {fl} outside 0–255")
    return rep


# ------------------------------------------------------------------ post-render
def _ff_filter(path, vf=None, af=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", path]
    if vf: cmd += ["-vf", vf]
    if af: cmd += ["-af", af]
    if not vf: cmd += ["-vn"]
    if not af: cmd += ["-an"]
    cmd += ["-f", "null", "-"]
    return subprocess.run(cmd, capture_output=True, text=True).stderr


def check_render(path, tl_path=None, sheet=None, rep=None):
    rep = rep or Report()
    p = probe(path); vs = vstream(p)
    if not vs: rep.fail("file", f"cannot read video {path}"); return rep
    w, h = int(vs["width"]), int(vs["height"])
    (rep.ok if (w, h) == (1080, 1920) else rep.fail)("format", f"{w}x{h}")
    num, den = (vs.get("r_frame_rate") or "0/1").split("/")
    fps = float(num) / max(1.0, float(den))
    (rep.ok if abs(fps - 30) < 0.5 else rep.warn)("fps", f"{fps:.2f}")
    dur = float(p["format"]["duration"])
    if not any(s.get("codec_type") == "audio" for s in p.get("streams", [])): rep.fail("audio", "no audio stream")
    T = None
    if tl_path:
        T = json.load(open(tl_path, encoding="utf-8"))
        vdur = duration(os.path.join(os.path.dirname(os.path.abspath(tl_path)), T["voice"]))
        if vdur: (rep.ok if abs(dur - vdur) < 0.3 else rep.fail)("duration", f"{dur:.2f} s (voice {vdur:.2f} s)")
    else: rep.ok("duration", f"{dur:.2f} s")
    if dur > 180: rep.warn("duration", "over 3 minutes — not a Short")

    # loudness (EBU R128)
    err = _ff_filter(path, af="ebur128=peak=true")
    mi = re.findall(r"I:\s+(-?[\d.]+) LUFS", err); mp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)
    if mi:
        lufs = float(mi[-1]); tp = float(mp[-1]) if mp else None
        (rep.ok if -16.5 <= lufs <= -12.5 else rep.warn)("loudness", f"{lufs:.1f} LUFS (target about -14)")
        if tp is not None: (rep.ok if tp <= -1.0 else rep.warn)("true peak", f"{tp:.1f} dBTP (keep ≤ -1)")
    # black, frozen, silence
    err = _ff_filter(path, vf="blackdetect=d=0.25:pix_th=0.08")
    bl = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)
    (rep.fail if bl else rep.ok)("black frames", ", ".join(f"{float(a):.2f}–{float(b):.2f}s" for a, b in bl) or "none")
    err = _ff_filter(path, vf="freezedetect=n=0.001:d=1.5")
    fz = re.findall(r"freeze_start: ([\d.]+)", err)
    (rep.warn if fz else rep.ok)("frozen video", ", ".join(f"{float(a):.2f}s" for a in fz) or "none")
    err = _ff_filter(path, af="silencedetect=noise=-45dB:d=1.2")
    si = re.findall(r"silence_start: ([\d.]+)", err)
    (rep.warn if si else rep.ok)("silence gaps", ", ".join(f"{float(a):.2f}s" for a in si) or "none")

    # flashes and cut sheet
    try:
        import cv2, numpy as np
        cap = cv2.VideoCapture(path); prev = None; flashes = []; i = 0
        while True:
            ok, f = cap.read()
            if not ok: break
            m = float(cv2.cvtColor(cv2.resize(f, (54, 96)), cv2.COLOR_BGR2GRAY).mean())
            if prev is not None and m - prev > 70: flashes.append(i / fps)
            prev = m; i += 1
        (rep.warn if flashes else rep.ok)("flashes", ("big brightness jumps at " + ", ".join(f"{t:.2f}s" for t in flashes[:8])) if flashes else "none")
        if sheet and T:
            cuts = [s["t0"] for s in T["scenes"][1:]]
            tiles = []
            for t in cuts:
                row = []
                for dt in (-0.5, 0.1, 0.6):
                    cap.set(cv2.CAP_PROP_POS_MSEC, max(0, t + dt) * 1000); ok, f = cap.read()
                    f = cv2.resize(f, (180, 320)) if ok else np.zeros((320, 180, 3), np.uint8)
                    cv2.putText(f, f"{t + dt:.1f}s", (6, 22), 0, 0.6, (0, 255, 255), 2); row.append(f)
                tiles.append(np.hstack(row))
            if tiles:
                cols = 3; rows = [np.hstack(tiles[k:k + cols] + [np.zeros_like(tiles[0])] * (cols - len(tiles[k:k + cols]))) for k in range(0, len(tiles), cols)]
                cv2.imwrite(sheet, np.vstack(rows)); rep.ok("cut sheet", f"{len(cuts)} cuts -> {sheet} (look at it)")
    except ImportError:
        rep.warn("flashes", "opencv not installed — skipped")
    return rep


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("pre", "post"):
        print(__doc__); sys.exit(2)
    if sys.argv[1] == "pre":
        rep = check_timeline(sys.argv[2]); rep.print("pre-render")
    else:
        args = sys.argv[3:]
        tl = args[args.index("--timeline") + 1] if "--timeline" in args else None
        sh = args[args.index("--sheet") + 1] if "--sheet" in args else None
        rep = check_render(sys.argv[2], tl, sh); rep.print("post-render")
    sys.exit(1 if rep.failed else 0)


if __name__ == "__main__":
    main()
