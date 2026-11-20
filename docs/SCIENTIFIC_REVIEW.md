# Scientific review and source-model qualifications

*Historical review record. For v1.1.0 publication and citation information, see [release notes](RELEASE_NOTES_1.1.0.md) and the [citation guide](CITATION.md).*

Unpublished development review, November 20, 2026. This is a scoped screen, not a universal model-quality pass or a new refinement.

The scoped local-feature screen now covers all **21 structures / 39 protomers with available experimental data**, **462 figure presentations covering the packaged scene environments** (254 sections + 208 meshes), and 85 review sheets across two stages. The final stage inspected 260 figures / 24 previously unscreened baseline protomers in 48 sheets. Eight additional native-coordinate planes address 7COY oxygen features and the 9KZ9/5OY0 axial sites. **1JB0 has no available experimental data and is not visually reviewed.** This closes the coverage gap; it does not establish an all-atom fit or chemical-validation pass.

All 22 current-vs-archived models match for 1,152,290 atom identity/XYZ/occupancy/B records, with no added/removed identities or coordinate shifts. This does not make every deposited geometry chemically correct. The dataset preserves the archived input hashes and coordinates; current recheck dates are separate provenance.

The 462-figure scope is a staged scientific feature screen. The earlier 202-figure screen used its preserved review derivative versions; subsequent Mg-selector corrections changed mesh overlays without moving atoms or changing maps/contours, and corrected representative meshes were inspected. The final 260 baseline figures were inspected at the current hash-bound versions. This is not a claim of fresh visual adjudication of every final raster after the display correction; all final raster hashes and processing records are separately checked.

## Retained qualifications

- **7DKZ A1:** modeled quinone C–O 1.42110–1.43833 Å and ring-plane RMS 0.28961–0.30407 Å. Broad model-phased density does not clear the geometry. HOH A923 is contour-sensitive (about 1.09 full-cell sigma, below 1.5 sigma). Retain native records; hold quantitative A1 chemistry and strong water-occupancy claims.
- **9KZ9 A1:** modeled quinone C–O 1.39311–1.39568 Å; reported carbonyl Z about +7.8–7.9. Density and near-planarity do not establish correct carbonyl chemistry or a redox state. The P_A Mg–His679 NE2 distance is 3.05697 Å (ND1 is farther away at 5.13078 Å); the explicit source-bound mapping gate supports identity rather than normal coordination geometry.
- **1JB0 A1:** reference quinone C–O is approximately 1.42 Å with ligand-geometry flags; the numbering/alignment reference is not a chemical gold standard. No released experimental data were found in the checked official sources.
- **8WEY and older entries:** retain quinone ring-bond flags, including those in 6KMW/6KMX/7COY. Chlorophyll bond outliers are reported per cofactor across the collection. An outlier is context for interpretation, not automatically a biological difference; absence of a reported flag is not proof of correctness.
- **5OY0 axial site:** protomer 3 native P_A Mg–His676 NE2 is 3.92402 Å and Mg–ND1 3.74700 Å. The nearer carbon CE1 (2.98469 Å) is not an alternative nitrogen ligand. Protomer 1/2 NE2 values are 2.93727/2.81404 Å. Model-phased density and occupancy 1 do not establish normal coordination or equal biological states. No 80th selected scene Mg pair is invented; 79 stored pairs remain unchanged.
- **7COY local oxygen positions:** all three A1_A O1 samples are 0.473–0.570 times the author contour; P_B ester O2A samples are 0.356–0.923 times it. Targeted planes include each actual oxygen and confirm weak/contour-sensitive local features. Hold oxygen-specific placement/contact conclusions; broad envelopes do not clear those positions. O2A is an ester single-bond oxygen in CL7 CCD connectivity, not its carbonyl oxygen.
- **9S6P/9SK3 site waters:** modeled 9S6P HOH A909 samples 0.072970 raw units versus author level 0.2. 9SK3 aA/bA/cA HOH3210 samples 0.045595/0.015762/0.006388 raw units versus author level 0.1. Distinct features are absent at those displayed levels. Retain the deposited positions with weak local support; no conserved occupancy, equal occupancy, biological absence or confirmed hydrogen-bond claim.
- **9AU4:** current EMDB metadata explicitly describe the primary map as unsharpened and unmasked. The author level has no stated sigma unit or supported conversion to the alternative display. Author-level sections are flooded at 0.0149 raw units. The separate mean+3 full-grid SD display (3.0006282866 raw units) is exploratory, not a quality score, uncertainty estimate or independent support criterion.
- **Preparation/mapping:** keep tagged 9SE6, split 9HYU A/a PsaA, exact-condition uncertainties, model-lineage limits and related-assembly provenance explicit. Deposited protomers and reconstructions are not independent biological replicates.

## Primary metadata correction

[9OY9](https://www.rcsb.org/structure/9OY9) and [9OZ3](https://www.rcsb.org/structure/9OZ3) now link to [Asido et al., bioRxiv](https://doi.org/10.64898/2026.10.01.756128). The study identifies a monomer and a trimer refined in C1, respectively. 9OZ3's deposited monomer title is retained as a documented discrepancy, while the atlas describes its three deposited protomers. Current sequence-difference annotations identify PsaB H95Q and AWPNYGNV linker residues 486–493; no alternative allele is inferred from a missing mutation field.

## Density and interpretation limits

EM maps retain native values and source-specific contours; they are not standardized across species. X-ray weighted main/difference maps are separately normalized over the full crystallographic cell, not over each crop. Sections are thin map planes with model atoms within ±1 Å projected onto them. A slab-projected atom can fall outside an in-plane contour while the actual 3D atom sample remains positive. Mesh carving is model-centered display selection, not independent evidence. No half-map cross-validation, local-FSC analysis, all-atom density adjudication, refitting, occupancy assignment or coordinate uncertainty estimate was performed.

The numbers are deposited heavy-atom separations. Display precision of 0.01 Å is not experimental accuracy. Strong density does not establish a hydrogen bond, protonation state, bond order or oxidation state.

## What remains scientifically unresolved

The deposited geometry and weak local features above remain unresolved model properties. The release disposition is to retain the native descriptive records and explicitly withhold the affected chemical, axial-coordination and water-support claims. Removing a qualifier would require claim-specific evidence, potentially re-refinement, independent half-map/omit-map tests or preparation records; this review supplies none of those. Source-condition unknowns remain unknown, rather than being converted to wild type, an explicit model parent or an independent preparation.

These are limitations of interpretation for a descriptive atlas. They become scientific blockers if the release is presented as establishing those stronger claims. The user accepted retaining these entries with their qualifications on November 20, 2026. Remaining release gates are review of the final-version package, validation of the exact final commit in remote CI, genuine release-date/new-version-DOI handling, and explicit publication authorization. [Detailed closure and blocker ledger](SCIENTIFIC_CLOSURE.md).

## Inspectable context

- [388 native diagnostic map samples](../downloads/validation/diagnostic_density_samples.csv) — source-specific display context; no cross-map ranking, occupancy estimate or automatic cutoff
- [Focused native axial geometry](../downloads/validation/axial_geometry.json)
- [Per-cofactor geometry CSV](../downloads/validation/cofactor_geometry.csv)
- [Full geometry/outlier context JSON](../downloads/validation/cofactor_geometry.json)
- [Source bond-outlier CSV](../downloads/validation/bond_outliers.csv)
- [Archived-source/current-snapshot comparison](../downloads/validation/source_snapshot_check.json)
- [Comparison scope](COMPARISON_SCOPE.md)
- [Density methods and source levels](DENSITY_VISUALIZATION_PILOT.md)

Official validation XML snapshots are retained under build/inputs/validation, tied to source-coordinate hashes in build/config/scientific_review.json. The full local review sheets and audit workflow are retained outside the public web package. No flagged atom, water, cofactor identity or measured pair was corrected, removed or reinterpreted as a confirmed chemical interaction.
