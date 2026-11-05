#!/usr/bin/env python3
"""Dependency-free installer for common Agent Skills clients.

For other clients, use the standard 'npx skills add' CLI.
This copies instructions and scripts; it does NOT install Python dependencies.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys

NAME = "raster-2-vector"
ROOT = Path(__file__).resolve().parents[1]
AGENTS = {
    "codex": (".agents/skills", ".agents/skills"),
    "claude-code": (".claude/skills", ".claude/skills"),
    "cursor": (".cursor/skills", ".agents/skills"),
    "opencode": (".config/opencode/skills", ".agents/skills"),
    "gemini-cli": (".gemini/skills", ".agents/skills"),
    "github-copilot": (".copilot/skills", ".agents/skills"),
    "hermes-agent": (".hermes/skills", ".hermes/skills"),
    "openclaw": (".openclaw/skills", "skills"),
}
ALIASES = {"claude":"claude-code","gemini":"gemini-cli","copilot":"github-copilot","hermes":"hermes-agent"}

def install(platform: str, scope: str = "user", project_dir: Path | None = None,
            force: bool = False, home: Path | None = None) -> list[Path]:
    if platform in ALIASES: platform = ALIASES[platform]
    if platform != "all" and platform not in AGENTS:
        raise ValueError(f"Unsupported platform: {platform}")
    if scope == "project" and project_dir is None:
        raise ValueError("--project-dir is required for project scope")
    if not (ROOT/"SKILL.md").is_file() or not (ROOT/"scripts"/"r2v.py").is_file():
        raise ValueError("Incomplete skill directory")
    base = (home or Path.home()) if scope=="user" else project_dir.resolve()
    selected = AGENTS if platform=="all" else {platform:AGENTS[platform]}
    paths = [base/Path(rel[0] if scope=="user" else rel[1])/NAME for rel in selected.values()]
    paths = list(dict.fromkeys(paths))
    for dest in paths:
        if dest.resolve()==ROOT.resolve():continue
        if dest.exists() and not force:
            raise FileExistsError(f"Refusing to overwrite {dest} without --force")
    installed=[]
    for dest in paths:
        if dest.resolve()==ROOT.resolve():
            installed.append(dest);continue
        if dest.exists():shutil.rmtree(dest)
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(ROOT,dest,ignore=shutil.ignore_patterns(
            ".git",".venv","venv","__pycache__","*.pyc",".DS_Store",".pytest_cache"))
        installed.append(dest)
    return installed

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--platform",choices=sorted([*AGENTS,*ALIASES,"all"]),required=True)
    p.add_argument("--scope",choices=["user","project"],default="user")
    p.add_argument("--project-dir",type=Path)
    p.add_argument("--force",action="store_true",help="Replace installed skill after review")
    args=p.parse_args()
    try:
        paths=install(args.platform,args.scope,args.project_dir,args.force)
        for path in paths:print("Installed",path)
        print("Restart the agent. Install the Python engine separately: docs/INSTALL.md")
    except (ValueError,FileExistsError) as e:
        print("Install failed:",e,file=sys.stderr);return 2
    return 0

if __name__=="__main__":raise SystemExit(main())
