# Contributing to AI Shorts Studio Skill

Thanks for helping creators make better Shorts with AI! 🎬

## Ways to help

- **Bug reports:** a render that breaks, a caption that doesn't shape correctly, a Flow UI step that changed. Include your OS, Python, Pillow, OpenCV and ffmpeg versions, the command and the output (without private files or paths).
- **Templates:** new scene types or card styles for `scripts/studio.py`.
- **Mask fix:** better detection for other masks, helmets or mascots in `scripts/maskclean.py`.
- **Docs and translations:** improvements to `README.md`, `README.hi.md` or `SKILL.md`.

## Ground rules

- **No media in the repo.** Don't commit videos, audio, logos or other copyrighted material; tests generate clips with ffmpeg `lavfi`.
- **Never render or generate without asking.** The skill always shows a plan and stills first — keep it that way.
- **Logos:** only files the user supplies, composited unchanged. Never generate or redraw a brand logo.

## Pull requests

1. Fork the repo and create a branch: `feat/<short-name>` or `fix/<short-name>`.
2. Run `python -m unittest discover -s tests -v` (needs ffmpeg, numpy, opencv-python-headless, pillow).
3. Keep the change focused; describe what it does and how you tested it. Beginners are welcome here.

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
