# Validation

What was checked for version 1.0.0, with the scope of each check. None of these checks establishes a hydrogen bond, local experimental accuracy or biological function.

| Check | Scope | Result |
|---|---|---|
| Build (`tools/build_atlas.py`) | every scene atom read from the archived file; cofactor bonds vs CCD (160 cofactor residues); alignment vs 133 curated mappings; distances vs the earlier curated values (max change 0.0009 Å, bound √3 × 0.001 Å from earlier rounding); site waters vs earlier assignments | PASS |
| Independent verifier, archived inputs (`tools/verify_public.py`, strict) | every scene atom, distance, class, chemical basis and ID; every exported table at its precision; per-scene vs combined tables; unique pairs; comparison tables vs `atlas.js`; crops; manifest | PASS — 18,378 scene-atom occurrences, 865 scene rows, 691 unique pairs, 1121 comparison cells, 128 crops, 590 manifest files |
| Independent verifier, current RCSB files | same checks against files downloaded 2026-11-17 | PASS — 18,378 scene-atom occurrences, 865 scene rows, 691 unique pairs, 1121 comparison cells, 128 crops, 590 manifest files; newer structure-model revisions: 1JB0 2.0 -> 2.1, 5OY0 3.1 -> 3.2, 6KMW 3.0 -> 3.1, 6KMX 3.0 -> 3.1, 7COY 1.2 -> 2.2, 9EYS 1.1 -> 2.0, 9I9L 1.0 -> 2.0, 9QFP 1.0 -> 1.1, 9S6P 1.0 -> 2.0, 9SK3 1.0 -> 2.0 |
| Deliberate-corruption tests (`tests/test_verify.py`) | the verifier must pass on a clean copy and fail on a changed CSV value, class, duplicate row, comparison value, crop coordinate, documentation file (manifest) and archived input | 8 of 8 tests passed (local run; also in CI) |
| PyMOL (`tools/check_pymol_scripts.py`, PyMOL 3.1.0) | every script run as written (crop) and on the full deposited entry; every distance object vs the atlas | PASS — 128 scripts, 1730 distances, max deviation 3.2e-05 Å |
| Derivation rule (`tools/derive_scenes.py check`) | curated scenes of five entries re-derived from another entry | non-water pairs reproduced: 95/106 |
| Clean rebuild (CI) | `tools/build_atlas.py` reproduces the committed `data/` and `downloads/` byte for byte | identical on a second local build (2026-11-17); CI repeats it in a fresh checkout |
| Site | home, structure, scene, compare and methods pages in Chromium; no console errors | checked 2026-11-17 |

**Not checked:** density or local map quality; Firefox, Safari, screen readers and touch devices; any functional or spectroscopic interpretation.
