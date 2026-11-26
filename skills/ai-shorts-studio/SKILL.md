---
name: ai-shorts-studio
description: Plan, generate and edit AI YouTube Shorts and story videos — Google Flow/Veo story kits (history, mythology, kids 3D, viral cute), faceless masked-mascot Shorts (clip library, mask-mouth fix, board/split templates, official logos, Hindi captions, SFX) and a beginner Editing Studio that creates the folders, learns your style into a brand kit, cuts beats, builds an Approve/Reject storyboard and makes the next draft from your notes.
license: MIT
metadata:
  version: "1.2.0"
---


# AI Shorts Studio

One skill, three modes:
- **Mode A — Story kit**: topic → Hindi script → character reference sheets → numbered 8-second Google Flow (Veo) clip prompts → assembly → publish pack. For history, mythology, kids 3D, viral-cute and custom story videos.
- **Mode B — Mascot Shorts Studio**: the user's voice recording + topic → a finished 1080x1920 Short built from a reusable **presenter clip library** (made for faceless masked 3D mascots — e.g. a black fabric face mask, hoodie, studio set), with board/split-screen templates, Hindi captions, SFX, outro and the mask-fix tool. Two scripts in `scripts/` do the work: `studio.py` and `maskclean.py`.
- **Mode C — Editing Studio (review loop)**: beginner-friendly. Claude creates the editing folders, learns the channel's style from reference/approved videos into `Brand Kit/brand-kit.md`, cuts the A-roll into beats, publishes a storyboard dashboard (one card per beat: cut preview, captions, B-roll, assets, Approve / Reject / Feedback), saves the notes to `notes.json`, makes the next draft from them and logs every approved change in `brand-kit.md`. The user only drops files in folders and clicks Approve/Reject.

**Never render or generate a video without the user's OK.** Every full render, re-render and Flow generation costs the user's credits/usage. Always show the plan and stills (or the storyboard) first, ask, and render only after a clear yes — also for small fixes such as a changed name or one scene.

Talk to the user in their language; for Hindi speakers use Hindi written in Devanagari with English technical words (not Roman Hinglish). Prompts for Flow/image models stay in English; voice-over/dialogue lines are written in the channel's language (default: Hindi in Devanagari). Use the user's images and clips as they are; always scale whole images proportionally (never squeeze or crop to width only).

Pick the mode from the request: a voice recording + mascot/presenter/Top-N/explainer Short → Mode B. A story topic or a request for Flow prompts → Mode A. "Start editing", "set up my studio", brand kit, storyboard, review/approve, notes or "next draft" → Mode C (which uses Mode B's renderer). New mascot expression clips are generated with the Flow section of Mode A, then quality-checked and filed with Mode B.

---
# MODE A — STORY KIT

## Why this works (the core tricks)
1. **Character lock**: every recurring character gets a turnaround reference sheet (front/side/back, white background). The sheet is attached as an *Ingredient* in Flow for every clip, AND the character's full text description is copied word-for-word into every clip prompt. Never paraphrase it between clips.
2. **Unique outfit color per character** ("Radha – teal-blue saree", "Mohan – orange shirt") so the model never mixes them up.
3. **8-second atomic clips**: number of clips = total seconds / 8. Each clip prompt is self-contained (scene, era, lighting, action, camera, mood, sound).
4. **Fixed STYLE BLOCK** at the end of every clip, ending with `no face morphing, no outfit change, no subtitles, no text, no watermark, 8 seconds`.
5. **Voice-over budget**: max 15–18 Hindi words per 8-second clip (≈110–130 words/minute).
6. **Batching**: for videos over 2 minutes, give 10 clips, then wait for "Next".

## Step 0 — Pick the preset
Ask (one short question with options) only what is missing:
- **Preset**: `history` | `mythology` | `kids-3d` (Indian village moral story) | `viral-cute` (duck + baby style Shorts) | `custom`
- **Format**: Short 9:16 (30–60 s) or long-form 16:9 (5 / 10 / 15 / 20 / 30 min)
- **Topic**: if none, go to Step 1.

## Step 1 — Topic ideas (only if no topic)
10 numbered ideas: English SEO title (`History of X || <curiosity hook>` or niche equivalent) + one Hindi line on why viewers will click. Then ask "कौनसा topic चुनना है?". Prefer clear story arcs and dramatic turning points.

## Step 2 — Length
If not given: "वीडियो कितने मिनट का बनाना है?" — 5 | 10 | 15 | 20 | 30 मिनट (or 30 s / 60 s for Shorts).

## Step 3 — Deliver the kit, in this order
### A) SCRIPT
- Hindi narration in Devanagari, 110–130 words/min, calm confident storyteller voice.
- Chapters with timings. Curiosity hook in the first 15 s (first 3 s for Shorts). 2–4 twists. Closing takeaway + soft CTA.
- History: accurate and neutral; if unsure of a date/fact say so; balanced on political/religious topics, no propaganda.
- Mythology: commonly accepted version of the named source text; respectful depiction of deities.
- Mark which clip numbers each paragraph covers.

### B) CHARACTERS + REFERENCE SHEET PROMPTS
- Recurring characters only; optional recurring guide/narrator character.
- Each: name, role, unique outfit colour, one full fixed description (age, skin, face, eyes, hair, clothes with colours, accessories, expression).
- Sheet prompt: `Character design sheet of one character, shown in three full-body views side by side: front view, side view and back view, same character in all three, neutral standing pose, plain white background, evenly lit, consistent proportions. Character: [full fixed description]. Style: [STYLE BLOCK]`
- Generate as **Image** in Flow (16:9), pick the best, download.
- One fixed NARRATOR voice description used in every clip.

### C) VIDEO CLIP PROMPTS
```
CLIP [n] | [start]-[end]
CHARACTERS IN THIS CLIP: [name – outfit color], ... (or "None, establishing shot")
ATTACH REFERENCE SHEETS: [sheet names] (or "None")
PROMPT: Use the attached character reference sheets exactly: same face, same clothes, same colors, do not change outfits. [Full character descriptions word for word]. Scene: [location, era, architecture, props, time of day, lighting]. Action: [what happens in 8 seconds]. Camera: [slow pan / slow zoom / push-in / tracking / close-up then widen]. Mood: [emotion]. Sound: [ambience + soft background music].
VOICE-OVER (narrator, [voice description]): "[Hindi line, max 15–18 words]"
DIALOGUE: [Character (voice type)]: "[Hindi line]"   ← kids-3d / mythology / viral-cute only
[STYLE BLOCK]
======
```
- Voice-over follows the script order. Some clips can be pure establishing shots. Vary camera moves.
- Over 2 minutes: clips 1–10, then "अगले 10 clips के लिए 'Next' लिखिए।"

### D) FLOW SETTINGS CARD (also used to generate mascot clips)
- New project → Video, 9:16 (Shorts) or 16:9, 720p, 8 s, x1–x2. Veo 3.1 Fast/Lite for drafts, Quality only for hero shots. Credits change — read the cost Flow shows before running.
- **Ingredients** = attach character sheets. **Frames** = start/end on a specific image (use the last frame of the previous clip for continuity).
- Regenerate if face/outfit drifted. Name downloads `clip_001.mp4`…
- **Flow UI as of Nov 2026 (verify, it changes):** a project opens with an Agent panel. Animate an image: upload it (+ → Upload), tile ⋮ → **Animate**, prompt the Agent. The Agent states model/settings/cost and asks Approve / Always approve / Reject per generation (seen: Veo 3.1 Lite, 9:16, 720p, 8 s, 1 output = 10 credits; several videos can be requested in one message). Download: tile ⋮ → Download → **720p (original)**. Upgraded 1080p downloads also exist.
- **"Audio generation failed"**: turn on Settings (gear) → **Return silent videos**; Agent-started generations can still fail this way — press the failed tile's **Retry** (it then works). Flow says failed generations are refunded.
- Long-form: Veo's voice changes between clips — generate ambience-only clips and lay ONE narrator track over the edit. For Shorts Veo's voice is fine.
- Driving Flow in the user's browser: check which Google account is signed in before creating anything and ask which account to use the first time; if a sign-in or password is needed, the user does it. Confirm the credit total before a batch, approve one request at a time (not "Always approve"), never buy credits, ask before accepting the image-rights dialog and before downloads. Chrome blocks many automatic downloads until the user allows "multiple downloads" for flow.google.com.
- Uploading from Chrome: the Upload menu creates its file input on click; patch `HTMLInputElement.prototype.click` to attach the input to the DOM, or add your own `<input type=file>`, file-upload into it and dispatch a `drop` event with its files on the "Start creating or drop media" area. Menus that ignore synthetic clicks respond to dispatched pointerdown/mousedown/pointerup/mouseup/click events.

### E) ASSEMBLY (story videos)
Phone: InShot/CapCut — clips in order, BG music ~15–20 %, Hindi captions, export 1080p. Desktop/workspace:
```bash
for f in clip_*.mp4; do ffmpeg -y -i "$f" -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30" -c:v libx264 -preset veryfast -crf 20 -c:a aac -ar 48000 -ac 2 "n_$f"; done
ls n_clip_*.mp4 | sed "s/.*/file '&'/" > list.txt
ffmpeg -y -f concat -safe 0 -i list.txt -c copy joined.mp4
ffmpeg -y -i joined.mp4 -i narration.mp3 -i music.mp3 -filter_complex "[2:a]volume=0.18[m];[0:a]volume=0.6[c];[c][1:a][m]amix=inputs=3:duration=first[a]" -map 0:v -map "[a]" -c:v copy -c:a aac final.mp4
```
Use 1920:1080 for 16:9.

### F) PUBLISH PACK
- 3 title options (English SEO + Hindi hook), description (Hindi + English), YouTube chapters, **at least 5 hashtags**, 10–15 tags.
- Thumbnail prompt in the same style; leave an empty area for 1–3 words of title text.

## STYLE BLOCK presets
- **history**: `2D hand-drawn comic-book illustration, bold black ink outlines, light cross-hatching, flat watercolor-like colors with a slightly aged paper texture, muted earthy palette with warm golden-hour light, doodle-style characters with round heads, simple dot eyes, tiny mouth, thin stick-like arms and legs, era-accurate clothes, subtle wind and dust motion, slow cinematic pan or zoom, no text, no subtitles, no watermark, 8 seconds`
- **mythology**: `cinematic photoreal epic Indian mythology film, rich gold and crimson palace lighting, oil-lamp glow, ornate jewelry and crowns, volumetric light and haze, dramatic low-angle shots, shallow depth of field, divine aura effects used sparingly, characters keep exactly the same face and costume as the attached reference sheets, no face morphing, no outfit change, no subtitles, no text, no watermark, 8 seconds`
- **kids-3d**: `Animated 3D-style cartoon, bright saturated colors, gentle smooth motion, slow cinematic camera, warm natural lighting, colorful Indian village, characters keep exactly the same face and clothes as the attached reference sheets, no face morphing, no outfit change, no subtitles, no text, no watermark, 8 seconds`
- **viral-cute**: `premium 3D animated short film, Pixar-like quality, ultra-detailed, cinematic, super fluffy fur/feather texture, big expressive eyes, soft studio lighting, playful bouncy motion, cheerful music, same characters as the attached reference sheets, no subtitles, no text, no watermark, 8 seconds`
- **custom**: same structure from the user's description.

`viral-cute` formula: one hero cute creature + one human baby/kid, one simple funny situation, 3–5 clips, hook in clip 1, loopable ending. Propose 5 concepts first.

---
# MODE B — MASCOT SHORTS STUDIO

## 1. Clip library
Clips live in a folder on the user's computer (ask which the first time; connect it, stage clips into the workspace). Next to them keep `library.json`:
```json
{"root": "library", "clips": [
 {"id": "hook_leanin", "file": "916_hook_leanin.mp4", "aspect": "9:16", "tags": ["hook"], "mask_ok": true},
 {"id": "sq_explain", "file": "sq_explain.mp4", "aspect": "square-in-16:9", "tags": ["board","explain"], "mask_ok": true}
]}
```
- `916_<action>.mp4` = full-screen clips (from the 9:16 lotus-mask image); `sq_<action>.mp4` = board-panel clips (from the square board-format image, often pillarboxed inside 16:9 — the renderer removes black bars).
- Tags: `hook`, `talk`, `explain`, `think`, `point`, `count`, `agree`, `celebrate`, `surprise`, `greet`, `secret`, `disagree`, `outro`, `board`.
- `mask_ok: true` only after the full-size check below; the renderer warns about unchecked clips.

## 2. New mascot clips (generate → check → fix → file)
- Generate with Flow (section D) from the user's own 9:16 image and square board image. Image-to-video, silent, 8 s.
- **Calm gestures only**: point, count, thumbs-up, nod, namaste, wave, chin-tap, lean in + raise one finger. Excited wording ("excited", "clapping", "laugh", "announce", "listen to this") makes Veo animate a mouth under the mask.
- Always add: `the black face mask is a rigid, completely still piece of opaque fabric - it never moves, never opens, never deforms; no mouth, lips, teeth or mouth shape ever appear on or behind it. His jaw stays still and closed; he is silent. Only eyes, eyebrows, head and hands move. Static medium shot, natural eye blinks. No speech, no music, no text, no subtitles, no watermark.`
- **Check every clip at full size, never from thumbnails**: crop the mask (~380x330 px on 1080-wide frames) at 4 fps into a contact sheet, plus 3–5 single full-size crops at the most animated moments. Look for lip bulges, a moving centre crease, smile lines, openings, red/teeth highlights.
- Mouth found → `python3 scripts/maskclean.py in.mp4 out.mp4 [--trim SEC] [--ref SEC]` (`--ref` = time where the mask is clean, default 0; `--trim` cuts an unfixable ending). Compare before/after full-size crops side by side. A strong mouth that survives → drop the clip.
- **Also check the hands** on a full-body contact sheet (12 frames, whole figure): reject any clip where a gesture can read as rude (e.g. a raised middle finger look-alike) — seen in a "man explains calmly" clip.
- Tell the user which clips passed, were fixed, or were dropped. Never call a clip clean before the full-size check.

## 3. Making a Short
1. **Voice → captions.** Offline transcription when Hugging Face is blocked: `pip install sherpa-onnx soundfile`; model from GitHub `k2-fsa/sherpa-onnx` release `asr-models/sherpa-onnx-whisper-small.tar.bz2`; `language="hi"`; cut at pauses (`ffmpeg ... silencedetect=noise=-35dB:d=0.35`); `stream.set_option("max_tokens_per_second","40")`. Rewrite captions cleanly (Devanagari + English tech words) with timings from the pause segments; ask the user to proofread.
2. **Plan scenes** — target 45–60 s; something changes every 2–4 s (7–8 s held layouts feel slow; ~1 s title flashes feel too fast).
   - `full` hook (title overlay) → `full` talk → one `board` per list item → `outro`.
   - **Never use the same clip in two scenes; every `board` gets its own `sq_` clip.** Count clips needed vs the library first; if short, tell the user exactly how many more and which actions — do not render a video that loops one clip.
   - Board panels use only square (`sq_`) clips, scaled whole to the 1080 width under a ~945 px card. Never crop a 9:16 clip into the panel.
   - Optional per item: a 3–5 s full-screen B-roll of what the product does (abstract glowing UI, prompted with *no readable text and no logos*).
3. **Official logos** for named products (Top-N, reviews, comparisons) — required so viewers recognise the product. Only official files the user supplies from each company's brand/press kit (`logos/<name>.png`, transparent PNG; verify alpha with transparent-png-check). Never let a model generate a logo and never redraw one in code. Composite unchanged (no recolour/stretch/crop/effects on the mark; proportional scale; clear space; a glow behind is fine), brand's own spelling beside it, used only to identify the product, never implying sponsorship. Mention once that each company's brand guidelines govern logo use. Missing logo → name card only, and tell the user which are missing.
4. **All on-screen text is rendered in code** (ranks, names, taglines, chips, captions, pills) — never by the video model.
5. Write `timeline.json` and run **pre-render QC**: `python3 scripts/qc.py pre timeline.json`. Fix every FAIL (gaps/overlaps, scenes not covering the voice, missing or repeated clips, a scene longer than its clip + 1 s, 9:16 clip on a board, missing card fields or logo files, captions past the voice). Read the WARNs to the user in plain words.
6. Render stills (`python3 scripts/studio.py timeline.json out/x.mp4 --stills`), look at them, **show the user the stills + scene plan + QC summary and wait for OK**. Then render the full video (`studio.py` re-runs pre-render QC and stops on FAIL).
7. **Post-render QC + self-review**: `python3 scripts/qc.py post out/x.mp4 --timeline timeline.json --sheet out/qc_cuts.jpg` checks 1080x1920 / 30 fps, duration vs voice, loudness (about -14 LUFS, true peak ≤ -1 dBTP), black frames, frozen video, silence gaps and big flashes, and writes a sheet of every cut (0.5 s before, 0.1 s and 0.6 s after). Look at the sheet and at full-size frames for hidden captions, cropped mascot, wrong logo, mask mouth. Fix and re-check at most 3 times, then tell the user what is still open. Deliver with SendUserFile and save next to the user's library if connected.
8. Channel name and avatar for the outro pill come from `Brand Kit/brand-kit.md` (e.g. `"channel_name": "Techie Monk"` with `Brand Kit/channel_emblem.png`) — never a guessed name or the creator's pen name.

### timeline.json
```json
{"library": "library.json", "voice": "voice.mp3", "channel_name": "My Channel", "channel_avatar": "Brand Kit/channel_emblem.png",
 "card_height": 945,
 "hot_words": {"AI": "cyan", "MISS": "red", "FOLLOW": "green", "coding": "yellow"},
 "captions": [{"s": 5.35, "e": 8.88, "text": "2026 में AI की दुनिया तेज़ी से बढ़ रही है"}],
 "scenes": [
  {"type": "full", "clip": "hook_leanin", "t0": 0, "t1": 9.4, "overlay": {"title": [
     {"words": ["TOP","5"], "colors": ["white","yellow"], "size": 210, "font": "title", "y": 230, "t": 1.4}]}},
  {"type": "full", "clip": "talk_excited", "t0": 9.4, "t1": 15.0},
  {"type": "board", "clip": "sq_explain", "t0": 15.0, "t1": 22.3, "card": {"rank": 5, "name": "CURSOR", "tag": "AI Code Editor",
     "chips": ["Coding","Software Dev"], "color": [0,229,255], "num_t": 15.12, "name_t": 16.48, "logo": "logos/cursor.png"}},
  {"type": "outro", "clip": "outro_thumbs", "t0": 56.6, "t1": 65.3, "overlay": {"question": "आपका FAVORITE?",
     "question_colors": ["white","yellow"], "question_t": 57.7, "comment_t": 60.7, "follow_t": 62.3}}]}
```
`t0/t1` follow the voice; `num_t`/`name_t` = when the rank / name is spoken; scenes cover the whole voice; `clip_offset` starts a clip later; colours: white, yellow, cyan, red, green.
Optional B-roll on a board scene (code-rendered, free, no readable text, no logos), shown in the clip panel with a 0.25 s fade: `"broll": {"style": "code|search|multimodal|mindmap|chat", "t0": 18.5, "t1": 21.0}` — start ~2 s after `name_t`, 2–3 s long, inside the scene; colour follows the card.

## 4. Scripts (in `scripts/`)
- `scripts/studio.py` — `python3 scripts/studio.py timeline.json out/video.mp4 [--stills]`. Renders the 9:16 Short (full / board / outro scenes, cards, logos, captions, SFX, voice mix). Paths in the timeline are relative to the timeline file. Optional `"flash": 0–160` sets the white flash at cuts.
- `scripts/maskclean.py` — `python3 scripts/maskclean.py in.mp4 out.mp4 [--ref SEC] [--trim SEC] [--no-polish]`. Removes mouth/smile shapes a video model paints on a fabric face mask and restores fabric texture.
- `scripts/broll.py` — code-rendered B-roll styles: `code` (editor with typing lines), `search` (search bar → sources → answer), `multimodal` (image/audio/text orbiting a core), `mindmap` (nodes growing), `chat` (bubbles + image tiles).
- `scripts/qc.py` — `qc.py pre timeline.json` (plan checks) and `qc.py post video.mp4 --timeline timeline.json --sheet cuts.jpg` (render checks). Grades PASS / WARN / FAIL; exit code 1 on FAIL.
- `templates/storyboard.html` — the review dashboard for Mode C (reads `beats.json`, or `beats.js` when opened from disk, + `cuts/`). Saves notes to the Claude artifact database when available, otherwise in the browser with Download / Import `notes.json`.
- `examples/` — sample `library.json` and `timeline.json`.
- Fonts (Anton, Poppins Bold with Devanagari; SIL OFL) ship in `fonts/`.
- Needs Python 3.10+, `pip install numpy opencv-python-headless pillow` (Pillow with raqm for Hindi shaping), and FFmpeg.

---
# MODE C — EDITING STUDIO (review loop)

Goal: a beginner connects one folder and drops files; Claude does the rest. Keep every message short and in plain words; tell the user exactly which folder to put what in.

Tools: on claude.ai / the Claude desktop app with a linked computer use the device tools (`device_list_dir`, `device_stage_files`, `device_commit_files`) and the Artifact tools for the dashboard; in Claude Code or other local agents just read and write the folder directly and open `Storyboard/index.html` from `templates/storyboard.html` in a browser (notes then live in the page's Copy-JSON output — paste them back).

## C1. Studio folder (create it automatically)
Ask once which folder to use (or use the connected one), then create this layout on the user's computer (`device_commit_files` creates folders; or `mkdir` with device_bash), with a `README.txt` in each saying what goes there:
```
<Studio>/
  Brand Kit/          brand-kit.md, channel emblem/avatar, fonts
  References/         videos whose style you like (other creators, AI samples)
  Approved Videos/    your own finished videos you are happy with
  A-roll/             voice recording(s) for the next video
  Raw Clips/          mascot / presenter clips (9:16 and square)
  Media Data/         logos, images, B-roll, music
  Storyboard/         beats.json, notes.json, Cuts/ (Claude writes here)
  Finished Videos/    drafts and finals (Claude writes here)
```
If the user already has similar folders (e.g. `Sample Videos`, `Audio Tracks`, `Finished Videos`), map them instead of duplicating and say which is which. Never delete or move the user's files.

## C2. Learn the style → `Brand Kit/brand-kit.md`
1. Stage every video in References and Approved Videos; `ffmpeg -i v.mp4 -vf fps=1,scale=216:384 f_%03d.jpg` (1 frame per second), tile 24 per contact sheet with the second stamped on each tile, and look at every sheet.
2. Write `brand-kit.md`: channel name + emblem, colours (RGB), fonts, presenter rules, format and pacing, layouts (full / board with card height), card design, item colours, logo rules, caption style and hot-word colours, motion + SFX, B-roll style, outro/CTA, publishing rules (≥5 hashtags). Mark the user's own feedback rules as **(owner rule)**. Note what References do better (e.g. B-roll after each item) and what Approved Videos get wrong (e.g. a cut flash that washes the frame). End with `## Approved changes log`.
3. Save it to `Brand Kit/` and keep using it as the source of truth for every later render.

## C3. Analyse A-roll + assets → beats and cuts
- Transcribe the A-roll (Mode B step 1) and split it into **beats**: hook, context lines, one beat per list item (split an item over ~9 s into two beats with different clips), outro. One global beat for whole-video issues.
- For each beat pick a distinct checked clip, its logo/asset files, SFX, captions in that time range, and a B-roll proposal (abstract, no readable text, no logos; say whether it is code-rendered = free, or Flow = credits).
- Write `Storyboard/beats.json` and the same array as `Storyboard/beats.js` (`window.BEATS = [...]`, so the board also opens from disk with file://): `[{id:"b01", n, title, t0, t1, layout, clip, card, color, captions[], broll, assets[], sfx[], preview:"cuts/b01.mp4", poster:"cuts/b01.jpg"}]`.
- Cuts: if a draft exists, cut each beat from it (`ffmpeg -ss t0 -to t1 -vf scale=360:640 -crf 30`) plus a poster frame; if not, build the cuts from stills only and ask before any render. Save them to `Storyboard/Cuts/`.

## C4. Storyboard dashboard (artifact)
- Start from `templates/storyboard.html` (set the title). Publish a page with publish_files: `index.html`, `beats.json`, `cuts/*.mp4|jpg`. Then `declare_capabilities` with `{"db": {"rules": [{"path": "", "read": "view", "write": "admin"}]}}` so notes persist and Claude can read them.
- Page: title + Approved/Rejected/Pending counts; a proportional **beat timeline strip** coloured by status (click to jump); filter tabs; one card per beat with the cut playing (9:16 video, poster, preload none), time range, layout, card text in the item colour, captions, B-roll, assets/SFX, **Approve** and **Reject** toggles, a Feedback textarea + Save; a "Copy notes as JSON" button. Style it from the brand kit (e.g. lavender + deep plum, Anton + Poppins).
- Storage: `const db = await claude.use("db")`; doc `reviews/<beatId>` = `{status, feedback, beat, n, t0, t1, updatedAt}`; one `collection("reviews").onSnapshot` subscription with a 10 s loading note; don't re-render while the user is typing; escape every stored value.
- Without the Claude artifact tools (Claude Code, Codex, Cursor…): copy the template to `Storyboard/index.html` beside `beats.json`, `beats.js` and `cuts/`, and tell the user to open it in a browser; notes stay in that browser until they press **Download notes.json** and save it in `Storyboard/` (or paste it in chat).
- Tell the user in one line: review the cards, then write "review done".

## C5. Notes → next draft → brand kit
1. On "review done": read `reviews` with db_list (slug of the dashboard) — or read `Storyboard/notes.json` the user saved — and write `Storyboard/notes.json` = `{draft, video, storyboard, notes:[{id, beat, status, feedback, updatedAt}]}` and summarise the notes back to the user.
2. Plan Draft N+1: approved beats stay as they are; rejected beats and feedback become concrete changes (clip swap, timing, caption, B-roll, card text, global fixes). Show the change list + stills and **wait for OK before rendering**.
3. After OK: render, save `Finished Videos/<title>_draftN.mp4`, re-cut the changed beats, republish the dashboard as the next round (reset those beats to pending), and keep earlier notes in `notes.json` history.
4. Keep a short decision log in `Storyboard/project.md` (date, draft, what changed and why, open items) so a later session can continue.
5. Add every **approved** change to `brand-kit.md` under `## Approved changes log` with the date, and update the matching rule section so the next video follows it automatically. Rejected ideas are not added.

---
## Output handling
- Mode A: write the kit to files (`script.md`, `characters.md`, `clips.md` with blocks separated by `======`, `publish.md`) and send them; for short videos the reply alone is fine.
- Mode B: deliverables go to `/mnt/user-data/outputs/`, are sent with SendUserFile and, if the user's folder is connected, written next to the source clips.
- Staging a file from the user's computer can fail with "file is hardlinked" (seen with fresh Chrome downloads); then ask the user to attach it in chat instead of making copies in their folder.
- Never copy another channel's named characters, logos or exact thumbnails; build original characters. Product logos follow the official-logo rules in Mode B.