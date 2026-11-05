# Compatibility matrix

**Skill compatibility and SVG processing are different questions.** We do not claim that every OS/agent pair has been verified.

## Agent installation

| Agent | Manual user-scope folder | Manual project-scope folder | Validated |
|---|---|---|---|
| Codex | `~/.agents/skills/` | `.agents/skills/` | Copy test |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | Copy test |
| Cursor | `~/.cursor/skills/` | `.agents/skills/` | Copy test |
| OpenCode | `~/.config/opencode/skills/` | `.agents/skills/` | Copy test |
| Gemini CLI | `~/.gemini/skills/` | `.agents/skills/` | Copy test |
| GitHub Copilot | `~/.copilot/skills/` | `.agents/skills/` | Copy test |
| Hermes Agent | `~/.hermes/skills/` | `.hermes/skills/` | Copy test |
| OpenClaw | `~/.openclaw/skills/` | `skills/` | Copy test |
| Other clients | Use `npx skills add ...` | CLI-managed | Not tested |

The `npx skills` command follows the evolving agent compatibility registry. Copy tests prove the files are in position; they do not prove each agent has successfully discovered and executed this skill.

## Image-processing engine

| OS / method | Intended engine status | Evidence |
|---|---|---|
| Linux native | Full `trace`, `refine`, `audit` | Local test suite and AEROID audit passed |
| macOS native | Expected with Homebrew Cairo + Potrace | Added CI, outcome pending |
| Windows native | Not yet supported end-to-end | Requires suitable native Cairo and libpotrace DLL |
| Windows/macOS/Linux with Docker | Same Linux engine image on all hosts | Dockerfile added; GitHub CI is the verification gate |
| WSL2 on Windows | Linux engine inside WSL | Not separately tested |

### Supported inputs

Target: black/white and flat single-color logos, typography, wordmarks and uncomplicated vector silhouettes. Not designed for photographs or general SVG: unsupported external assets, gradients, fonts, masks and unexpected SVG tags are intentionally refused.

### Quality

Default mask IoU: 95%; a user may deliberately trade pixel similarity for better typography, but it must be disclosed and the geometry visually inspected. Topology, boundary deviations, bytes and segment count are recorded separately.

For current CI results, inspect the [Actions tab](https://github.com/shubinlab/raster-2-vector/actions).
