# raster-2-vector

Typography-aware Agent Skill for creating compact SVG from raster lettering and logos, refining existing vector outlines, and verifying results against the original image.

## Features

- **trace**: raster to SVG using Potrace-based candidate tracing
- **refine**: simplify existing SVG outlines while respecting contour tangency, topology and quality thresholds
- **audit**: compare an SVG with the source raster before accepting the result
- Exactly three output artifacts: `.svg`, rendered `.png`, and `_overlay.png`
- Automated tests and the `doctor` environment check

## Install (Ubuntu / WSL2)

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip libpotrace0
git clone https://github.com/shubinlab/raster-2-vector.git
cd raster-2-vector
bash install.sh codex
~/.agents/skills/raster-2-vector/.venv/bin/python ~/.agents/skills/raster-2-vector/scripts/r2v.py doctor
```

For Claude Code use `bash install.sh claude`; for both use `bash install.sh both`.

**[Полная инструкция на русском](INSTALL_RU.md)** · **[Skill instructions](SKILL.md)** · **[Typography principles](references/typography.md)**

## Verification

```bash
~/.agents/skills/raster-2-vector/.venv/bin/python -m unittest discover -s ~/.agents/skills/raster-2-vector/tests -v
```

## Notes

Designed primarily for single-color logos, letterforms, and wordmarks, not photographs. Native `libpotrace` is required for tracing; refine/audit can run without it. IoU alone is not a substitute for typographic review.

No private user artwork, original AEROID files, or credentials are included. This repository currently has **no open-source LICENSE**; public visibility does not grant permission to reuse the code under an open-source license.
