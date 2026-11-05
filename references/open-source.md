# Open-source influences and limits (verified November 2026)

These are **references**, not vendored dependencies; no third-party code copied into this skill.

- **Potrace**: Peter Selinger's bitmap contour tracing. `alphamax` controls corners and `opttolerance` trades curve fidelity for simplification. Best initial candidate for black/white silhouettes. Native `libpotrace` used through a small ctypes wrapper. Source: https://potrace.sourceforge.net/
- **VTracer**: color vectorization, fast geometry pipeline; new versions offer refit/simplify modes. Use for color images, not necessarily better for small letterform contours. Source: https://github.com/visioncortex/vtracer
- **SVGO**: strong SVG serialization optimizations (`convertPathData`, multipass, precision). Treat it as *syntax optimization*, not typographic judgment. Always rerender afterward. Source: https://github.com/svg/svgo
- **FontForge**: `simplify` supports `mergelines`, `nearlyhvlines`, `forcelines`, `smoothcurves`, `choosehv`; extrema and intended on-curve points matter. Source: https://fontforge.org/docs/scripting/python/fontforge.html
- **zyipeng/image-to-svg**: agent skill for explicit raster QA, background analysis, spacing and counter checks. Its reported results do not guarantee any minimum IoU. Source: https://github.com/zyipeng/image-to-svg
- **ol-dad-the-guru/raster-vectorize-skill**: Potrace workflow with rerasterization QA; oriented to flat-color art and accurate colors. Source: https://github.com/ol-dad-the-guru/raster-vectorize-skill
- **oaustegard/claude-skills image-to-svg**: broad color/image extraction and optional line-art composition; different target problem (many filled shapes), not assumed ideal for logos. Source: https://github.com/oaustegard/claude-skills/blob/main/plugins/media-processing/skills/image-to-svg/SKILL.md
- **Agent Skills specification**: minimal discoverable metadata and progressive loading of references/scripts. Source: https://agentskills.io/specification

Benchmark claims are local measurements of the scripts in this bundle. Do not equate repository star counts with vector accuracy. Evaluate each tool on the same source masks and visually check final paths before choosing.
