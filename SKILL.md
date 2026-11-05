---
name: raster-2-vector
description: Reconstruct or refine raster logos, lettering, wordmarks, glyphs, and clean graphic marks into compact editable SVG with typographic straight strokes, smooth Bézier tangencies, original-raster comparison, and three verified outputs (SVG, PNG, overlay). Use for raster-to-vector conversion and iterative logo contour cleanup; not for photographic illustrations or original logo ideation.
---
# raster-2-vector

**Objective:** produce the simplest *visually correct* geometry, not the greatest pixel IoU or the smallest byte count at any cost. Prefer a valid typographic line, coherent bowl, counter, spacing, and tangent over tracing raster noise. Never claim aesthetic perfection by IoU alone.

## Execution policy
1. Find the **original raster** in the current conversation or attached files. Never compare only with a previous SVG. Check whether a previous **approved SVG** is available: refine it rather than restart tracing.
2. Run `python scripts/r2v.py doctor`. Inspect raster polarity, background, counters, intended corners, glyph boundaries. If the drawing is a logo/wordmark, consult `references/typography.md` only when reconstructing or editing glyph geometry.
3. First pass:
   - Existing SVG: `python scripts/r2v.py refine existing.svg --source original.png --out work.svg --min-iou .95`
   - Raster only: `python scripts/r2v.py trace original.png --out work.svg --min-iou .95 --goal balanced`
   - Pure QA: `python scripts/r2v.py audit original.png work.svg --out checked.svg`
4. Inspect the generated PNG and overlay **visually**. For each requested letter, check long straight strokes are actual `H/V/L`, bowls use few large curves/arcs, smooth seams match tangent direction, counters remain open, kerning and repeated proportions harmonize. Deliberate sharp terminals are allowed. Where geometry is still visibly wrong, adjust only the relevant SVG path in a controlled pass and rerun `audit`. Do not merely shrink a renderer image and call it SVG.
5. Use **multi-objective selection**: reject broken topology, visible kinks, or lost terminals; prefer lower segment count and smaller bytes when aesthetic quality is comparable. Default raster IoU ≥ .95, but may fall below only on **user-authorized aesthetic grounds**. State the exact score and reason. To test an approved intentional exception use `--min-iou .92 --aesthetic-override` (replace `.92` with the explicitly agreed threshold); do not silently relax the gate.
6. Require verification against exact saved SVG, not a draft string. Record elapsed runtime, byte count, segment count, mask IoU, topology, boundary P95, and per-letter differences when appropriate. A failed gate means no successful delivery claim.
7. **Deliver exactly three logo outputs:** one editable SVG with transparent background, one rendered PNG, one overlay PNG. Do not repeat old file links. The script prints JSON metadata to stdout; keep QA logs internal unless requested. Only link paths that exist and were checked in this run.

## Cost and speed
- **One analysis, one scripted candidate batch, one QA pass.** Avoid repeatedly asking an LLM to generate raw coordinates or to visually self-score. Run geometry/measurement in Python, not in model tokens.
- Default `trace` evaluates three Potrace settings, plus optional analytic ellipses; expensive 7-setting exploration only with `--mode quality`. Reuse cached source mask; do not run contour extraction repeatedly just to change SVG syntax.
- `refine` tests a small shortlist of line/cubic merges screened by geometric error and G1 tangency. Never smooth intended corners.
- `--goal size|balanced|fidelity` controls compression tradeoff. Avoid global vector simplification when a single glyph is defective.
- Open `references/open-source.md` only when considering alternate libraries or special cases. Keep instructions in this file short; scripts own the numeric details.

## Constraints
- Flat, filled, single-path SVG is supported for automatic `refine`; if SVG has transforms, groups, gradients, multiple fills, masks or strokes, use an editor or `trace`. The tool refuses unsupported features instead of silently erasing them.
- Current automatic code **cannot judge typographic aesthetics**. A model/human must inspect overlays and approve optical corrections. No promise of mathematically minimal segment count or guaranteed 95% on every raster.
- The native Potrace library is optional for `refine`/`audit` but required for `trace`. CairoSVG/Pillow/OpenCV/NumPy/SciPy are required for local execution.
