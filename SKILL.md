---
name: raster-2-vector
description: Reconstruct or refine raster logos, lettering, wordmarks, glyphs, and clean graphic marks into compact editable SVG with typographic straight strokes, smooth Bézier tangencies, original-raster comparison, and three verified outputs (SVG, PNG, overlay). Use for raster-to-vector conversion and iterative logo contour cleanup; not for photographic illustrations or original logo ideation.
---
# raster-2-vector

**Objective:** produce the simplest *visually correct* geometry, not the greatest pixel IoU or the smallest byte count at any cost. Prefer a valid typographic line, coherent bowl, counter, spacing, and tangent over tracing raster noise. Never claim aesthetic perfection by IoU alone.

## Runtime selection (cross-platform)

This is a portable Agent Skill, not an embedded Python runtime. Installing it through `npx skills` or a manual agent folder only installs instructions and scripts. Before invoking the engine, locate the skill directory and choose:
1. An already configured Python environment with `requirements.txt` installed and working Potrace/Cairo; run `python scripts/r2v.py doctor`.
2. Otherwise the documented Docker engine: build `docker build -t raster-2-vector .` from this repository, then run `docker run --rm -v "${PWD}:/work" -w /work raster-2-vector ...` with input/output in the mounted directory.
3. Do not claim universal execution solely from agent instruction discovery. If the engine is missing, state the install dependency and point to `docs/INSTALL.md`.

## Execution policy
1. Find the **original raster** in the current conversation or attached files. Never compare only with a previous SVG. Check whether a previous **approved SVG** is available: refine it rather than restart tracing.
2. Run `python scripts/r2v.py doctor`. Inspect raster polarity, background, counters, intended corners, glyph boundaries. If the drawing is a logo/wordmark, consult `references/typography.md` only when reconstructing or editing glyph geometry.
3. New strict preflight enforces the ORIGINAL raster coordinate system. Do not independently resize vector and raster foreground bounds. A different SVG viewBox aspect ratio is a hard audit failure. New G1 and G2 issues are rejected before choosing a compact candidate.
4. First pass:
   - Existing SVG: `python scripts/r2v.py refine existing.svg --source original.png --out work.svg --min-iou .95`
   - Raster only: `python scripts/r2v.py trace original.png --out work.svg --min-iou .95 --goal balanced`
   - Pure QA: `python scripts/r2v.py audit original.png work.svg --out checked.svg`
5. Inspect the generated PNG and overlay **visually**. For each requested letter, check long straight strokes are actual `H/V/L`, bowls use few large curves/arcs, smooth seams match tangent direction, counters remain open, kerning and repeated proportions harmonize. Deliberate sharp terminals are allowed. Where geometry is still visibly wrong, adjust only the relevant SVG path in a controlled pass and rerun `audit`. Do not merely shrink a renderer image and call it SVG.
6. Use **multi-objective selection**: before saving bytes, reject broken topology, visible kinks, lost terminals, **new G1 tangent discontinuities measured after SVG serialization**, or material regressions in **per-component IoU** (small wings must not be hidden by the large letter). Default raster IoU ≥ .95, but may fall below only on **user-authorized aesthetic grounds**. State the exact score and reason. The automatic comparison is against the same source raster and the original SVG; report any pre-existing suspicious seams for manual cleanup. To test an approved intentional exception use `--min-iou .92 --aesthetic-override` (replace `.92` with the explicitly agreed threshold); do not silently relax the gate.
7. Require verification against the exact saved SVG, not a draft string. Record elapsed runtime, byte count, segment count, mask IoU, **per-component IoU, new-kink rejections**, topology, boundary P95, and per-letter differences when appropriate. A passing 95% mask score alone does **not** certify smooth wings. Inspect the enlarged wing roots and both blade edges. A failed gate means no successful delivery claim.
8. **Deliver exactly three logo outputs:** one editable SVG with transparent background, one rendered PNG, one overlay PNG. Do not repeat old file links. The script prints JSON metadata to stdout; keep QA logs internal unless requested. Only link paths that exist and were checked in this run.

## Cost and speed
- **One analysis, one scripted candidate batch, one QA pass.** Avoid repeatedly asking an LLM to generate raw coordinates or to visually self-score. Run geometry/measurement in Python, not in model tokens.
- Default `trace` evaluates three Potrace settings, plus optional analytic ellipses; expensive 7-setting exploration only with `--mode quality`. Reuse cached source mask; do not run contour extraction repeatedly just to change SVG syntax.
- `refine` tests a small shortlist of line/cubic merges screened by geometric error and G1 tangency. It re-parses each serialized candidate, prevents new mid-angle seams, and forbids loss of local feature fidelity. Default merge bounds are 0.8 px fitting error and 3° at existing smooth joins. Never smooth intended corners.
- `--goal size|balanced|fidelity` controls compression tradeoff. Avoid global vector simplification when a single glyph is defective.
- Open `references/open-source.md` only when considering alternate libraries or special cases. Keep instructions in this file short; scripts own the numeric details.

## Constraints
- Flat, filled, single-path SVG is supported for automatic `refine`; if SVG has transforms, groups, gradients, multiple fills, masks or strokes, use an editor or `trace`. The tool refuses unsupported features instead of silently erasing them.
- Current automatic code **cannot judge typographic aesthetics**. Automatic verified Scour miniﬁcation is used when available and only accepted when the source-space raster gate passes. G2 warnings are not proof of a visual error and require manual review. A model/human must inspect overlays and approve optical corrections. No promise of mathematically minimal segment count or guaranteed 95% on every raster.
- The native Potrace library is optional for `refine`/`audit` but required for `trace`. CairoSVG/Pillow/OpenCV/NumPy/SciPy are required for local execution.

## AEROID wing regression / honest reporting
- Sharp outer wing **tips** may be intentional. The join checker screens probable accidental 3°–70° kinks and compares new candidates to the preexisting SVG; it cannot decide artistic intent automatically.
- If an existing SVG already contains a visually bad wing junction, automatic `refine` prevents worsening but does not promise to repair it. Edit the local cubic control points, then run `audit` and visually inspect the overlay.
- Do not claim `r2v.py` ran unless the engine command actually executed. An ad hoc Python transformation that merely imitates the skill is **not** a plugin execution.
- GitHub commits do not necessarily update a ChatGPT-installed copy of the skill immediately. Confirm the currently installed release before reporting the new version as active.
