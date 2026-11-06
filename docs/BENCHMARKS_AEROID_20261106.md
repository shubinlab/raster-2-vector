# AEROID & red-team regression notebook — 2026-11-06

## Provenance and restrictions
Two raster source files were supplied by the user in ChatGPT. **Their raw bytes are not committed to this public repository.** SHA-256 and dimensions enable re-verification only when the owner supplies the files.

| Fixture | Source dimensions | SHA-256 |
|---|---|---|
| AEROID bold, winged a | 2508 × 627 | `f90fe869d714945d26b2b7c5f03d051efd008c21a1459e36c02bcb3ddff4e31e` |
| AEROID minimalist | 1672 × 941 | `f3b3cc4de5e0edfe48a1534a28b8e075665cb67e7ab22025fa6aefa74bcbab66` |

Both use the exact original pixel canvas, binary foreground from source luminance, native Potrace 1.16, and CairoSVG render into original dimensions. **Do not** scale each foreground bounding box separately. Four Potrace presets were tried per source. The smallest topology-preserving candidate with IoU ≥0.95 was chosen.

| Fixture | Potrace settings | Native SVG bytes | IoU | Minimum local component IoU | Segments | Render boundary P95 |
|---|---|---:|---:|---:|---:|---:|
| Bold | `alphamax=1, opttolerance=0.8, precision=1` | 4,012 | 0.993677 | 0.984428 | 107 | 1 px |
| Minimal | same | 3,685 | 0.991657 | 0.977307 | 99 | 1 px |

Guarded Scour compaction produced 2,917 and 2,682 bytes, with IoU of 0.993698 and 0.991747 respectively, and unchanged component/hole topology. The slight IoU increase is due to path numeric rewriting; it is not a claim about improved design aesthetics.

## Synthetic adversarial inputs
All are generated locally using vector paths/raster masks, not third-party logos. Measurements were on 480×260 source canvases, using the smallest topology-preserving candidate that meets 95%:

| Case | Source-space IoU | Topology | SVG bytes |
|---|---:|---|---:|
| Thin layered wings and sharp tips | 0.977572 | preserved | 569 |
| Holes / counters | 1.000000 | preserved | 540 |
| Very narrow one-sided spacing | 1.000000 | preserved | 319 |
| Compound sharp cusps | 0.991202 | preserved | 532 |
| Long thin stroke | 0.950951 | preserved | 537 |
| Smooth oval bowl and counter | 0.985155 | preserved | 381 |
| White on dark | 0.987565 | preserved | 343 |
| Transparent alpha | 0.987565 | preserved | 343 |
| Deliberately wrong viewBox aspect | rejected | n/a | n/a |

## Red-team findings
1. A tiny wing can be damaged while whole-wordmark IoU remains above 95%, so isolated component IoU is mandatory.
2. Angle-only G1 checks miss a smooth-tangent join with a sudden curvature change; G2 discontinuity is now also reported and blocked if newly introduced.
3. Independent bounding-box resizing can fabricate high IoU from a distorted SVG; strict source-canvas viewBox check prevents this.
4. A thin stroke at 0.950951 IoU is close to the gate; the benchmark cannot promise every future shape will pass.
5. Proved minification must be checked AFTER serialization and rendering; byte count alone is not proof of quality.
6. Tests and CI are necessary but not sufficient to establish typography aesthetics: deliberate corners require visual inspection.

Follow-up objective: add a locally runnable benchmark command that reads two owner-provided AEROID images (without publishing them) and compares versions with locked thresholds and deterministic renderer configuration.
