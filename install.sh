#!/usr/bin/env bash
# Manual skill installer. For more agents, use npx skills add.
set -euo pipefail
mode="${1:-}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.10+ is required to install without Node.js." >&2
  exit 1
fi
case "$mode" in
  both)
    python3 "$root/scripts/install.py" --platform codex --scope user
    python3 "$root/scripts/install.py" --platform claude-code --scope user
    ;;
  codex|claude|claude-code|cursor|opencode|gemini-cli|github-copilot|hermes-agent|openclaw|all)
    python3 "$root/scripts/install.py" --platform "$mode" --scope user
    ;;
  *)
    echo "Usage: bash install.sh codex|claude|both|cursor|opencode|gemini-cli|github-copilot|hermes-agent|openclaw|all" >&2
    exit 2
    ;;
esac
echo "Agent instructions installed. Install the separate Python engine using docs/INSTALL.md."
