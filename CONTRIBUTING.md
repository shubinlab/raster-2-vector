# Contributing

**A public repository without a LICENSE file is not automatically open source.** Before substantial contributions, contact the maintainer about rights and licensing.

## Local checks

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/r2v.py doctor
```

Geometry changes must be tested against the original raster and preserve counters/topology unless explicitly requested. Include side-by-side IoU, boundary error, SVG bytes, segment counts, and a visual overlay. Never include proprietary logos or unlicensed fonts in test fixtures.

The agent skill should retain valid `SKILL.md` frontmatter and exactly three output artifacts per successful SVG task.
