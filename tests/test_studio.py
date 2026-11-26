"""End-to-end smoke test: builds tiny clips with ffmpeg lavfi and renders stills + a short video."""
import json, os, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-shorts-studio", "scripts")


def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


class StudioTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp()
        lib = os.path.join(cls.d, "library"); os.makedirs(lib)
        ff("-f", "lavfi", "-i", "testsrc2=s=540x960:r=24:d=3", "-pix_fmt", "yuv420p", os.path.join(lib, "916_a.mp4"))
        ff("-f", "lavfi", "-i", "testsrc2=s=540x960:r=24:d=3", "-vf", "hue=h=90", "-pix_fmt", "yuv420p", os.path.join(lib, "916_b.mp4"))
        ff("-f", "lavfi", "-i", "testsrc=s=540x540:r=24:d=3", "-vf", "pad=960:540:210:0", "-pix_fmt", "yuv420p", os.path.join(lib, "sq_a.mp4"))
        ff("-f", "lavfi", "-i", "sine=f=220:d=7", os.path.join(cls.d, "voice.mp3"))
        json.dump({"root": "library", "clips": [
            {"id": "a", "file": "916_a.mp4", "mask_ok": True}, {"id": "b", "file": "916_b.mp4", "mask_ok": True},
            {"id": "sq", "file": "sq_a.mp4", "mask_ok": True}]}, open(os.path.join(cls.d, "library.json"), "w"))
        json.dump({"library": "library.json", "voice": "voice.mp3", "channel_name": "Test Channel",
                   "captions": [{"s": 0.2, "e": 2.0, "text": "हेलो AI दुनिया test"}], "hot_words": {"AI": "cyan"},
                   "scenes": [
                       {"type": "full", "clip": "a", "t0": 0, "t1": 2.0, "overlay": {"title": [
                           {"words": ["TOP", "1"], "colors": ["white", "yellow"], "size": 150, "font": "title", "t": 0.2}]}},
                       {"type": "board", "clip": "sq", "t0": 2.0, "t1": 4.5, "card": {"rank": 1, "name": "TOOL", "tag": "Test tag",
                        "chips": ["One", "Two"], "color": [0, 229, 255], "num_t": 2.1, "name_t": 2.5},
                        "broll": {"style": "code", "t0": 3.3, "t1": 4.3}},
                       {"type": "outro", "clip": "b", "t0": 4.5, "t1": 7.0, "overlay": {"question": "आपका FAVORITE?",
                        "question_t": 4.6, "comment_t": 5.0, "follow_t": 5.5}}]},
                  open(os.path.join(cls.d, "timeline.json"), "w"), ensure_ascii=False)

    def run_studio(self, *extra):
        out = os.path.join(self.d, "out", "v.mp4")
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "studio.py"), os.path.join(self.d, "timeline.json"), out, *extra], check=True)
        return out

    def test_stills(self):
        self.run_studio("--stills")
        for i in range(3):
            self.assertTrue(os.path.exists(os.path.join(self.d, "out", f"still_{i:02d}.jpg")))

    def test_render(self):
        out = self.run_studio()
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))
        self.assertAlmostEqual(dur, 7.0, delta=0.3)
        wh = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", out]).decode().strip()
        self.assertEqual(wh, "1080,1920")


    def test_broll_styles(self):
        sys.path.insert(0, SCRIPTS); import broll
        for st in broll.STYLES:
            f = broll.broll_frame(st, 1.0, 2.5, (0, 229, 255), 540, 480)
            self.assertEqual(f.shape, (480, 540, 3)); self.assertGreater(f.std(), 5)

    def test_qc_pre_broll_outside_scene(self):
        def edit(T): T["scenes"][1]["broll"]["t1"] = 6.0
        r = self.qc("pre", self.bad_timeline(edit))
        self.assertEqual(r.returncode, 1); self.assertIn("broll", r.stdout)

    def test_qc_pre_title_over_face(self):
        def edit(T): T["scenes"][0]["overlay"]["title"][0]["y"] = 600
        r = self.qc("pre", self.bad_timeline(edit))
        self.assertEqual(r.returncode, 1); self.assertIn("face", r.stdout)

    def test_end_hold_and_at(self):
        def edit(T): T["end_hold"] = 0.8; T["scenes"][2]["speed"] = 0.9
        tl = self.bad_timeline(edit)
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "studio.py"), tl, os.path.join(self.d, "at", "x.mp4"), "--at", "0.5,7.5"], check=True)
        self.assertTrue(os.path.exists(os.path.join(self.d, "at", "at_000.50.jpg")))
        self.assertTrue(os.path.exists(os.path.join(self.d, "at", "at_007.50.jpg")))
        out = os.path.join(self.d, "hold", "v.mp4")
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "studio.py"), tl, out], check=True)
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))
        self.assertAlmostEqual(dur, 7.8, delta=0.3)

    def qc(self, *args):
        return subprocess.run([sys.executable, os.path.join(SCRIPTS, "qc.py"), *args], capture_output=True, text=True)

    def test_qc_pre_pass(self):
        r = self.qc("pre", os.path.join(self.d, "timeline.json"))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("coverage", r.stdout)

    def bad_timeline(self, edit):
        T = json.load(open(os.path.join(self.d, "timeline.json"), encoding="utf-8")); edit(T)
        p = os.path.join(self.d, "bad.json"); json.dump(T, open(p, "w"), ensure_ascii=False); return p

    def test_qc_pre_repeated_clip(self):
        def edit(T): T["scenes"][2]["clip"] = "a"
        r = self.qc("pre", self.bad_timeline(edit))
        self.assertEqual(r.returncode, 1); self.assertIn("already used", r.stdout)

    def test_qc_pre_board_needs_square(self):
        def edit(T): T["scenes"][1]["clip"] = "b"; T["scenes"][2]["clip"] = "sq"
        r = self.qc("pre", self.bad_timeline(edit))
        self.assertEqual(r.returncode, 1); self.assertIn("square", r.stdout)

    def test_qc_pre_gap_and_loop(self):
        def edit(T): T["scenes"][1]["t0"] = 2.4; T["scenes"][2]["t1"] = 9.0
        r = self.qc("pre", self.bad_timeline(edit))
        self.assertEqual(r.returncode, 1); self.assertIn("gap", r.stdout); self.assertIn("would loop", r.stdout)

    def test_render_refuses_failed_qc(self):
        def edit(T): T["scenes"][2]["clip"] = "a"
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "studio.py"), self.bad_timeline(edit), os.path.join(self.d, "x", "x.mp4")], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)

    def test_qc_post(self):
        out = self.run_studio()
        r = self.qc("post", out, "--timeline", os.path.join(self.d, "timeline.json"), "--sheet", os.path.join(self.d, "cuts.jpg"))
        self.assertIn("[PASS] format: 1080x1920", r.stdout, r.stdout)
        self.assertTrue(os.path.exists(os.path.join(self.d, "cuts.jpg")))


if __name__ == "__main__":
    unittest.main()
