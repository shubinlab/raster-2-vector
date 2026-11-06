# raster-2-vector

**Typography-first bitmap → SVG** for wordmarks, fonts, glyphs and clean geometric logos.

[![CI](https://github.com/shubinlab/raster-2-vector/actions/workflows/ci.yml/badge.svg)](https://github.com/shubinlab/raster-2-vector/actions/workflows/ci.yml)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-SKILL.md-181717)](https://agentskills.io/specification)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](https://python.org/)
[![Runtime](https://img.shields.io/badge/Runtime-Docker%20%7C%20Linux%20%7C%20macOS-556677)](docs/COMPATIBILITY.md)
[![License](https://img.shields.io/badge/License-not%20yet%20selected-lightgrey)](#license)

> **The geometry matters.** Straight typographic strokes should be straight, bowls should be regular, Bézier transitions should be smooth. The best SVG is not necessarily the one with the highest pixel IoU.

## Install the skill in any supported agent

The maintained [skills CLI](https://github.com/vercel-labs/skills) handles discovery and installation in dozens of agent clients. Node.js 22.20+ is required **only for this installer**, not the Python vector engine.

```sh
npx skills add shubinlab/raster-2-vector
```

Select your agent interactively, or install globally into all agents supported by the CLI:

```sh
npx skills add shubinlab/raster-2-vector --skill raster-2-vector --agent '*' -g -y
```

**Important:** installing `SKILL.md` instructions is separate from installing the **Python/Potrace/Cairo image engine**. See [Installation](docs/INSTALL.md). The list of supported agents depends on the installed skills CLI version.

## Run the engine on any desktop OS with Docker

Docker gives Windows, macOS and Linux hosts a consistent Linux runtime. After [installing Docker](https://docs.docker.com/get-docker/):

```sh
git clone https://github.com/shubinlab/raster-2-vector.git
cd raster-2-vector
docker build -t raster-2-vector:local .
docker run --rm raster-2-vector:local doctor
```

Then run from a directory containing `source.png`:

```sh
docker run --rm -v "${PWD}:/work" -w /work raster-2-vector:local \
  trace /work/source.png --out /work/result.svg --min-iou 0.95
```

Windows PowerShell also supports `"${PWD}:/work"` in a Docker volume argument. Native setup instructions: [Linux, macOS and Windows](docs/INSTALL.md).

## Exactly three output files

| File | Purpose |
|---|---|
| `result.svg` | Editable SVG vector paths |
| `result.png` | Rendered SVG preview |
| `result_overlay.png` | Raster comparison: **white** = common, **red** = missing, **cyan** = extra |

The program measures overall **and per-component IoU** (small wing detail cannot hide behind a large glyph), boundary error, missed/extra pixels, component/hole topology, **SVG join-angle risks**, bytes and segment counts. During `refine`, freshly introduced tangent kinks and material per-component fidelity regressions are hard rejected **after serialization**. It **cannot automatically prove aesthetic quality**; a human or visual agent must still review intentional corners, wing roots, and the overlay.

## Commands

```sh
python scripts/r2v.py doctor
python scripts/r2v.py trace source.png --out result.svg --goal balanced
python scripts/r2v.py refine existing.svg --source source.png --out refined.svg
python scripts/r2v.py audit source.png existing.svg --out verified.svg
python -m unittest discover -s tests -v
```

The commands require the engine dependencies. `trace` uses native Potrace, while `refine` and `audit` do not. The original raster is always the ground truth; independent x/y foreground stretching is forbidden. A failing quality gate is **not** reported as success.

## Install the Python CLI locally

After installing the native Potrace/Cairo dependencies (see [installation](docs/INSTALL.md)):

```sh
python -m pip install -e .
raster-2-vector doctor
```

This is a local package; it is **not** published to PyPI.

## Supported agent clients

This follows the portable [Agent Skills specification](https://agentskills.io/specification). The optional Python installer provides explicit paths for **Codex, Claude Code, Cursor, OpenCode, Gemini CLI, GitHub Copilot, Hermes Agent, and OpenClaw**. The skills CLI targets more. **File installation tests do not prove runtime execution by each agent.** See the [compatibility matrix](docs/COMPATIBILITY.md).

## Project map

```text
raster-2-vector/
├── SKILL.md                  Portable agent skill
├── scripts/                  SVG engine + installer
├── tests/                    Geometry and distribution tests
├── references/               Typography and open-source references
├── docs/                     Platform matrix, installation and research
├── .github/workflows/ci.yml  Continuous integration
├── Dockerfile                Reproducible runtime
└── README.md                 Quick start
```

## Docs and project policies

- [Installation on each OS](docs/INSTALL.md) · [Русская инструкция](INSTALL_RU.md)
- [Compatibility and limits](docs/COMPATIBILITY.md)
- [31 GitHub projects above 200k stars: presentation benchmark](docs/GITHUB_RESEARCH.md)
- [Typographic guidelines](references/typography.md)
- [Security](SECURITY.md) · [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)

## Limitations

Optimized for flat, single-color wordmarks and simple filled shapes. **Not for photographs or general-purpose complex SVG editing.** Windows-native vector engine is **not yet end-to-end verified**; Docker or WSL2 is recommended. CI status is authoritative only after jobs finish; do not interpret a badge as proof of every platform.

## License

**No open-source license has been chosen yet.** Public access to this repository does not grant copyright permission to redistribute or modify its code. Libraries have their own licensing obligations.
