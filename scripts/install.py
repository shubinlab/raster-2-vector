#!/usr/bin/env python3
"""Copy raster-2-vector into Codex or Claude Code skill folders.

This installer copies files only. It does not execute remote code or install dependencies.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys

NAME = "raster-2-vector"
ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=["codex", "claude"], required=True)
    parser.add_argument("--scope", choices=["user", "project"], default="user")
    parser.add_argument("--project-dir", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "SKILL.md").exists() or not (ROOT / "scripts/r2v.py").exists():
        parser.error("Incomplete skill directory")
    if args.scope == "project" and args.project_dir is None:
        parser.error("--project-dir is required for project scope")
    base = Path.home() if args.scope == "user" else args.project_dir.resolve()
    folder = ".agents/skills" if args.platform == "codex" else ".claude/skills"
    dest = base / folder / NAME
    if dest.resolve() == ROOT.resolve():
        print("Already installed:", dest)
        return 0
    if dest.exists():
        if not args.force:
            print("Refusing to overwrite existing skill:", dest, file=sys.stderr)
            return 2
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns(".venv", "venv", "__pycache__", "*.pyc", ".git", ".DS_Store"))
    print("Skill installed:", dest)
    print("Install Python dependencies from requirements.txt and run doctor and tests.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
