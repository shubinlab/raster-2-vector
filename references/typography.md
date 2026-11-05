# Typeface-first geometric checklist

For vector lettering, **font design conventions guide regularization**, while the original raster supplies location and identity.

1. **Recognize the skeleton**: x-height, cap height, baseline, stroke thickness, bowls, shoulder, stem, terminals, counters. Decompose separately into lines, regular arcs, and freeform curves. Preserve recognizability and original kerning.
2. **Straighten known-straight strokes**: use one H, V, or L, not several almost-collinear cubics. Example: `a` horizontal top; `r` vertical stem; `i` vertical bar. Respect deliberate italic slant and optical corrections.
3. **Bowl and repeated parts**: start with shared reference radii/widths for `a/e/o/d`; compare optical weight, inside/outside diameter, top/bottom overshoot. A nominal circle need not be mathematically circular. Prefer 2 SVG arc segments or 4 symmetric cubics if either reproduces the desired contour with fewer bytes and smoothness.
4. **G1 smoothness**: tangent vectors on intended seamless junctions point in the same direction; preserve continuity when fitting or merging cubics. G2 (curvature rate) may also matter visually; inspect enlarged joins. Do not destroy intentional corners, cut ends, or transitions to wing tips.
5. **Counters**: inspect positive/negative spaces at small size, hole count, side bearing, stroke thickness, open apertures. Global IoU can hide a broken counter or malformed `r` shoulder.
6. **Wing or flourish**: isolate the feature, keep its terminal sharp if intended, fit each long edge with few cubic curves, enforce tangent where it joins a stem; do not fake a long tangent with many small kinks.
7. **Optical balance**: review whole wordmark at target usage size and enlargement. Use symmetry only when it simplifies construction *and* preserves visual harmony. Shape clarity is more important than mathematically identical radii or a perfect 95% mask score.
8. **Quality exception**: an aesthetically improved typographic reconstruction may score below 95% IoU. Such an exception requires the user’s permission, honest score, visual overlay, and documented cause (symmetry, stroke regularization, spacing or optical correction).

Aesthetic QA still requires human review. Do not assign numerical scores to beauty or pretend a point-matching threshold proves a good logo.
