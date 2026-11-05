#!/usr/bin/env bash
set -euo pipefail
usage() { echo "Usage: bash install.sh codex|claude|both"; }
case "${1:-}" in codex|claude|both) target="$1";; *) usage; exit 2;; esac
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v python3 >/dev/null; then echo "Python 3 is required" >&2; exit 1; fi
install_one() {
  dest="$1"
  mkdir -p "$(dirname "$dest")"
  if [ -e "$dest" ]; then
    echo "Refusing to overwrite $dest. Move or backup the existing skill first." >&2
    exit 1
  fi
  mkdir -p "$dest"
  cp -R "$root"/. "$dest"/
  rm -rf "$dest/.venv" "$dest/.git"
  python3 -m venv "$dest/.venv"
  "$dest/.venv/bin/python" -m pip install -r "$dest/requirements.txt"
  "$dest/.venv/bin/python" "$dest/scripts/r2v.py" doctor
  (cd "$dest" && "$dest/.venv/bin/python" -m unittest discover -s tests -v)
  echo "Installed: $dest"
}
if [ "$target" = codex ] || [ "$target" = both ]; then install_one "$HOME/.agents/skills/raster-2-vector"; fi
if [ "$target" = claude ] || [ "$target" = both ]; then install_one "$HOME/.claude/skills/raster-2-vector"; fi
