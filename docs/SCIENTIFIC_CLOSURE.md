# Scientific closure and remaining release gates — 1.1.0 release review

*Historical review record. For v1.1.0 publication and citation information, see [release notes](RELEASE_NOTES_1.1.0.md) and the [citation guide](CITATION.md).*

Prepared November 20, 2026. Unpublished development candidate: 22 structures, 40 deposited protomers, 160 scenes. The published v1.0.0 remains unchanged. This document supersedes the earlier 15-protomer review scope; older receipts remain historical evidence.

## Completed work

All 39 protomers with experimental data now received a scoped local-feature screen: 462 section/mesh figure presentations covering the packaged environments, organized in 85 sheets across two review stages. The final stage adds 24 baseline protomers / 260 figures / 48 sheets. Eight additional native planes examine 7COY oxygens and 9KZ9/5OY0 Mg–His sites. Current source/archived atom identity, coordinates, occupancy and B records remain identical for all 22 models (1,152,290 records). 1JB0 has no released experimental data in the checked sources and remains explicitly unavailable, not reviewed.

There are 388 diagnostic native map point samples: 351 modeled cofactor oxygen positions and 37 assigned water oxygens. Unmodeled atoms and waters were not reconstructed. Map values use the existing native-source recipe; EM values were not normalized, sharpened or smoothed. X-ray main/difference coefficients are independently normalized over the full cell. Samples/contour ratios give within-map display context; they are not standardized scores, fit validation, occupancy or coordinate uncertainty. No statistical species comparison or atom exclusion was performed.

The 462-figure scope is a staged scientific feature screen. The earlier 202-figure screen used its preserved review derivative versions; subsequent Mg-selector corrections changed mesh overlays without moving atoms or changing maps/contours, and corrected representative meshes were inspected. The final 260 baseline figures were inspected at the current hash-bound versions. This is not a claim of fresh visual adjudication of every final raster after the display correction; all final raster hashes and processing records are separately checked.

## Scientific disposition ledger

| Issue | Evidence and action completed | Retained interpretation limit | Release disposition |
|---|---|---|---|
| Previously unscreened baseline density | All remaining 24 available baseline protomers screened individually; figure hashes and source identities recorded. | Local-feature screen only; no all-atom/half-map/local-FSC approval. | Coverage gap closed. |
| 1JB0 / 7DKZ / 9KZ9 A1 chemistry | Native carbonyl geometry, planarity and official ligand flags retained; broad-map observations checked where available. | Long C–O / nonplanarity flags are unresolved. No redox, bond-order or species-dependent chemistry from these geometries. | Retain descriptive records and visible qualifications. Do not clear the geometry. |
| 9KZ9 axial site | Mg–NE2 3.056972 Å; ND1 5.130784 Å. Native Mg/His plane inspected; role/mapping gate retained. | Nearer NE2 identity is not normal coordination, a tautomer assignment or a validated bond. | Mapping qualification remains; no general discovery-threshold change. |
| 5OY0 protomer 3 axial site | Mg–NE2 3.924019 Å; Mg–ND1 3.747000 Å. Native plane inspected. CE1 at 2.984687 Å is carbon, not a nitrogen alternative. | Broad model-phased density cannot establish normal axial coordination. Other protomers are not independent replicates. | Native separations retained; explicit scene/comparison caution. The stored scene list still has 79 Mg pairs. |
| 7COY local oxygen features | All three A1_A O1 samples 0.473–0.570 × author contour; P_B O2A 0.356–0.923 ×. Six native planes containing the actual target oxygens inspected. | Oxygen-specific placement/contact conclusions are limited; not proof of absence. P_B O2A is a CCD ester single-bond oxygen. Ring flags remain. | Retain values and qualify relevant scenes/comparisons. |
| 7DKZ site water | HOH A923 about 1.09 full-cell σ; below displayed 1.5 σ. | Contour-sensitive; no strong occupancy/conservation/H-bond claim. | Retained with weak-support qualification. |
| 9S6P / 9SK3 site waters | 9S6P A909 = 0.072970 raw vs level 0.2; 9SK3 aA/bA/cA3210 = 0.045595/0.015762/0.006388 raw vs level 0.1. No distinct author-contour features. | Weak support for deposited positions; no conserved/equal occupancy or biological absence inference. | Retain actual assigned coordinates and add visible cautions. |
| 9AU4 contour metadata | Current EMDB explicitly says unsharpened/unmasked; author 0.0149 raw has no stated σ unit. Header/grid/axis/source bindings checked. | Flooded author display has no inferred unit conversion. Separate mean + 3 full-grid SD view remains exploratory, not author recommended or a support cutoff. | Retain both labeled options; no map renormalization. |
| Preparation / model ancestry | Tagged 9SE6, split-chain 9HYU, related assemblies, 9OY9/9OZ3 genotype/assembly correction and primary sources retained. 9KZ9 primary Methods explicitly use 8WM6. | 9LUT grid allocation and nonexplicit SWISS-MODEL parent details remain unknown. The notice-source follow-up resolved 9UH3 α-DDM preparation/8Z11 ancestry, 9HYU combined-dataset provenance and 7DKZ cultivar Alaska. | Publish unknowns as unknowns; do not infer WT, lineage or independent preparation. |
| Baseline/addition selection scope | Eight additions received the prospective N/O-neighborhood supplement; 14 baseline selections preserved. | Counts are not exhaustive/equally sampled cross-species contact inventories. | Explicit scope statement retained. |

These unresolved scientific properties block stronger claims, rather than requiring silent coordinate repair or omission from a descriptive deposited-model atlas. Removing a qualification would require claim-specific new evidence, possibly source records or re-refinement/independent map validation. No such evidence or new refinement is claimed here.

## What still blocks publication

1. Scientific retention dispositions accepted by the user on November 20, 2026; the qualifications and descriptive scope remain binding. This is not publication authorization. In particular, the release must not present flagged oxygen contacts as validated hydrogen bonds, waters as conserved occupancy, long Mg distances as normal coordination, or quinone geometry as a redox/species effect.
2. Final release metadata and artifact: choose the genuine final version/date and handle a genuine new version DOI as applicable; review the final diff and archive. The rc.3 candidate has no new DOI/date and is not published.
3. Run remote CI against the exact proposed final commit. Local passes do not establish that GitHub Actions or deployment succeeded.
4. Explicit publication authorization before push/tag/upload/deployment or GitHub About/social-setting changes. No external mutation was performed.

The local website review already passed in isolated Chrome/Edge sessions. Its earlier evidence remains scoped to the earlier candidate; the rc.3 follow-up verifies that the new scientific notes reach scenes/comparisons and that the existing defaults still work. No personal browser was controlled. Safari, Firefox, physical mobile and accessibility audits remain outside that scope.

## Inspectable evidence and reproduction

- [Full scientific review](SCIENTIFIC_REVIEW.md), [comparison scope](COMPARISON_SCOPE.md), [density processing](DENSITY_VISUALIZATION_PILOT.md).
- [Source-bound cofactor and review JSON](../downloads/validation/cofactor_geometry.json), [diagnostic samples CSV](../downloads/validation/diagnostic_density_samples.csv), [native axial geometry JSON](../downloads/validation/axial_geometry.json).
- `build/provenance/scientific_closure/` preserves final-stage figure identities/hashes, targeted-plane source/coordinate records and current 9AU4 metadata summary. Full-size additional planes and the 48 review sheets remain in the sibling scientific_closure_20261120_v01 work folder; local file paths in that provenance are audit references, not website links.
- `python tools/verify_scientific_closure.py --json /outside/repository/closure.json` checks scope, additional figure hashes, native axial geometry, diagnostic export identities/ratios and retained warnings. Optional `--map-cache CACHE --work-dir WORK` directly resamples the six qualified entries from hash-bound original maps; it never downloads or substitutes sources.

Default scientific view, labels, deposited atom identities/coordinates/occupancies/B factors, selected contact rows and comparison matrix values remain unchanged. Only review notes/derived qualification context, candidate markers and associated checks are updated. Earlier rc.1/rc.2 archives remain preserved. Technical verification receipts state their actual scope and limitations.

## Final-version preparation

Version 1.1.0 is staged in a separate review copy. Scientific retention with the documented qualifications was accepted by the user on November 20. Actual release date and version DOI remain unset; the existing concept DOI is contextual. Citation formats are generated from a shared metadata configuration and checked against the official CFF 1.2.0 schema. No GitHub/Zenodo mutation or publication occurred. [Citation plan](CITATION.md) · [Release review](RELEASE_REVIEW.md). Earlier rc.3 evidence remains historical at its stated scope.

## Notice and source follow-up

Obsolete review-status wording was removed after user review. The 7DKZ bent-quinone curator note and interpretation-in-progress statement are explicit; [the literature/coordinate check](7DKZ_QUINONE_REVIEW.md) distinguishes accepted manuscript inspection from an unverified final typeset/supplement. [Resolved metadata and presentation changes](NOTICE_REVIEW.md) do not clear the retained geometry/density qualifications.
