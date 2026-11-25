# Changelog

## 1.0.0 — 2026-11-26

First public release. Fuses two private skills (AI Flow Story Video + Mascot Shorts Studio) and adds the Editing Studio review loop.

- **Mode A — Story kit:** topic → script → character reference sheets → numbered 8-second Google Flow (Veo) clip prompts → assembly → publish pack. Presets: history, mythology, kids-3d, viral-cute, custom. Notes on the Nov 2026 Flow UI (Agent panel, Animate, "Return silent videos" + Retry).
- **Mode B — Mascot Shorts Studio:** reusable presenter clip library (`library.json`), full-size mask + hand QA, `maskclean.py` mask-mouth fix with fabric texture restore, `studio.py` renderer (full / board / outro scenes, rank cards with official logos, 3-word captions with hot-word colours, whoosh + pop SFX, voice mix), offline Hindi transcription with sherpa-onnx.
- **Mode C — Editing Studio:** creates the studio folders, learns the channel's style from reference and approved videos (1 frame per second) into `Brand Kit/brand-kit.md`, cuts the A-roll into beats, builds a storyboard dashboard with Approve / Reject / Feedback, saves `notes.json`, plans the next draft and logs approved changes in the brand kit.
- **Never renders or generates without the user's OK** — plan and stills first.
- Fonts bundled (Anton, Poppins Bold — SIL OFL). End-to-end tests with generated clips.
