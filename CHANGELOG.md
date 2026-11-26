# Changelog

## 1.3.0 — 2026-11-26

- **Text never covers the presenter's face (owner rule).** Captions always in the bottom band (`caption_y`, defaults full/outro 1720, board 1770); hook title lines without `"y"` stack in the bottom band automatically. `qc.py pre` FAILs any title or caption inside the face band (`face_band`, default y 330–1000 on 1080×1920).
- **Hook timing:** `qc.py pre` warns when the first title appears after 0.5 s.
- **B-roll caption-safe area:** graphics stay above the caption band (`safe_bottom`, default 230 px).
- **`end_hold`:** keep the last frame (with outro overlays) for N seconds after the voice; audio is padded to match.
- **`speed`** per scene (0.5–1.5) to slow a clip instead of freezing it; **`flash`** per scene (e.g. 0 for a soft cut into the outro).
- **`studio.py --at T1,T2,…`** saves full-size stills at exact times without rendering the video.
- 12 tests.

## 1.2.0 — 2026-11-26

- **Code-rendered B-roll (`scripts/broll.py`)**: five abstract styles — `code`, `search`, `multimodal`, `mindmap`, `chat` — drawn in the board's clip panel with a 0.25 s fade, tinted with the card colour. Free (no Flow credits), no readable text, no logos. Add `"broll": {"style", "t0", "t1"}` to a board scene.
- `qc.py pre` checks B-roll style and window (inside the scene, after the name has settled).
- Stills show the B-roll moment when a scene has one. 10 tests.

## 1.1.0 — 2026-11-26

Improvements from an external code review and from studying other open-source video skills.

- **Pre-render QC (`scripts/qc.py pre`)**: timeline gaps/overlaps, voice coverage, missing or repeated clips, scene longer than its clip (+1 s hold), 9:16 clip on a board, card fields and timing, logo files and transparency, caption timing and reading speed, avatar, flash range. `studio.py` runs it first and stops on FAIL (`--force` to override).
- **Post-render QC (`scripts/qc.py post`)**: format and fps, duration vs voice, EBU R128 loudness and true peak, black frames, frozen video, silence gaps, harsh brightness flashes, and a contact sheet of every cut. Self-review capped at 3 passes. *(ideas from kajisho5/ffmpeg-skill and browser-use/video-use)*
- **No hidden looping:** a clip that ends early holds its last frame (max 1 s); ping-pong only with `"allow_loop": true`.
- **Audio:** loudness target −14 LUFS and a limiter so true peak stays under −1 dBTP after SFX.
- **Robustness:** clear errors for unreadable/empty clips in `studio.py` and `maskclean.py`, dark-frame fallback, "no mask found" message, safe temp files with guaranteed cleanup.
- **Storyboard works outside Claude:** loads `beats.js` from disk (file://), saves notes in the browser, Download / Import `notes.json`.
- **Decision log:** `Storyboard/project.md` per project.
- Infographic in the README. 8 tests.

## 1.0.0 — 2026-11-26

First public release. Fuses two private skills (AI Flow Story Video + Mascot Shorts Studio) and adds the Editing Studio review loop.

- **Mode A — Story kit:** topic → script → character reference sheets → numbered 8-second Google Flow (Veo) clip prompts → assembly → publish pack. Presets: history, mythology, kids-3d, viral-cute, custom. Notes on the Nov 2026 Flow UI (Agent panel, Animate, "Return silent videos" + Retry).
- **Mode B — Mascot Shorts Studio:** reusable presenter clip library (`library.json`), full-size mask + hand QA, `maskclean.py` mask-mouth fix with fabric texture restore, `studio.py` renderer (full / board / outro scenes, rank cards with official logos, 3-word captions with hot-word colours, whoosh + pop SFX, voice mix), offline Hindi transcription with sherpa-onnx.
- **Mode C — Editing Studio:** creates the studio folders, learns the channel's style from reference and approved videos (1 frame per second) into `Brand Kit/brand-kit.md`, cuts the A-roll into beats, builds a storyboard dashboard with Approve / Reject / Feedback, saves `notes.json`, plans the next draft and logs approved changes in the brand kit.
- **Never renders or generates without the user's OK** — plan and stills first.
- Fonts bundled (Anton, Poppins Bold — SIL OFL). End-to-end tests with generated clips.
