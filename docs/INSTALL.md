# Installation on Linux, macOS and Windows

**There are two distinct installs:** (1) Agent Skill instructions; (2) the Python image-processing engine. Installing a skill does not install Cairo, Potrace or Python.

## 1. Install the Skill to your AI agent

The maintained [skills CLI](https://github.com/vercel-labs/skills) supports dozens of agent clients; Node.js 22.20+ is required for this installer only.

```sh
npx skills add shubinlab/raster-2-vector --list
npx skills add shubinlab/raster-2-vector --skill raster-2-vector
# Global install for every agent your CLI supports:
npx skills add shubinlab/raster-2-vector --skill raster-2-vector --agent '*' -g -y
```

Check available agents and update the CLI if a client is missing. Restart an agent after installing.

Without Node.js, clone this repo and use the dependency-free manual installer (Python 3.10+):

```sh
python scripts/install.py --platform codex --scope user
python scripts/install.py --platform cursor --scope project --project-dir /path/to/project
python scripts/install.py --platform all --scope user
```

Supported manual targets: codex, claude-code, cursor, opencode, gemini-cli, github-copilot, hermes-agent, openclaw. Existing installations are not overwritten unless explicitly passing `--force`.

## 2. Recommended for ALL desktop OSes: Docker runtime

Install Docker Engine/Desktop and clone the repository:

```sh
git clone https://github.com/shubinlab/raster-2-vector.git
cd raster-2-vector
docker build -t raster-2-vector:local .
docker run --rm raster-2-vector:local doctor
```

Linux/macOS Bash, when `source.png` is in the current working directory:

```sh
docker run --rm -v "${PWD}:/work" -w /work raster-2-vector:local trace /work/source.png --out /work/result.svg
```

Windows PowerShell:

```powershell
docker run --rm -v "${PWD}:/work" -w /work raster-2-vector:local trace /work/source.png --out /work/result.svg
```

Outputs are written into the mounted host directory. Mount only the required working directory. Docker is a dependency-management solution, not a security sandbox.

## 3. Native Linux

Ubuntu/Debian:

```sh
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip libpotrace0 libcairo2
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/r2v.py doctor
.venv/bin/python -m unittest discover -s tests -v
```

For other distros, install shared `libpotrace` and Cairo using the distro package manager.

## 4. Native macOS

```sh
brew install python potrace cairo
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/r2v.py doctor
.venv/bin/python -m unittest discover -s tests -v
```

If `doctor` cannot locate Potrace, use `POTRACE_LIB_PATH=/opt/homebrew/lib/libpotrace.dylib` (Apple Silicon) or inspect your Homebrew prefix. Do not assume success unless `ready_trace` is true.

## 5. Windows native

**Not end-to-end validated**. Installing the `potrace.exe` binary (e.g. with Scoop) does **not** automatically provide the Potrace DLL needed by Python `ctypes`. CairoSVG additionally needs Cairo native libraries. For full vectorization on Windows, prefer Docker Desktop (Linux containers) or WSL2 Ubuntu. The portable Python skill installer can install the instructions natively even without the image engine.

## 6. Three-output contract and CLI

```sh
python scripts/r2v.py doctor
python scripts/r2v.py trace source.png --out result.svg --min-iou 0.95
python scripts/r2v.py refine existing.svg --source source.png --out refined.svg
python scripts/r2v.py audit source.png existing.svg --out verified.svg
```

Each successful run delivers exactly `result.svg`, `result.png` and `result_overlay.png`. JSON statistics are printed to stdout. Existing source SVG files cannot be overwritten by `refine` and `audit`. Quality is checked against the original raster.
