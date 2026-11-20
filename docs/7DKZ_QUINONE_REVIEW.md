# 7DKZ quinone geometry — curator observation and literature check

Reviewed November 20, 2026. Coordinates are preserved; interpretation is in progress. This is a source-model observation, not a validated native chemical conformation.

## Curator note for the atlas

The unusually bent A1 quinones and elongated C–O bonds are present in the deposited 7DKZ model. I have verified the coordinates and am working on interpretations; their physical significance remains unresolved.

## Direct source verification

The atlas's PQN A842 and PQN B843 each reproduce all **33 deposited heavy-atom positions exactly** in a fresh 7DKZ mmCIF retrieval. All **34 intramolecular bonds** in each scene agree with the retained PQN CCD connectivity. The nonplanarity is present before scene rotation and rendering; no atoms were fitted, flattened or repaired in this check.

| Native cofactor | Ten-carbon ring plane RMS (Å) | Largest absolute ring offset (Å) | C1–O1 (Å) | C4–O4 (Å) |
|---|---:|---:|---:|---:|
| A1_A, PQN A842 | 0.304066 | 0.515332 | 1.434580 | 1.438334 |
| A1_B, PQN B843 | 0.289606 | 0.524694 | 1.431356 | 1.421102 |

The source ligand-validation report independently flags the long carbonyl bonds. For B843 it reports carbonyl Z values 9.63 and 9.14 against its reference mean of 1.23 Å; the reported ring C2–C3 bond Z is 10.43. The ligand's RSCC is 0.962. That local map correlation does not make the intraligand chemistry correct at the deposited 2.393 Å resolution.

## What the paper says — and what was actually checked

Wang et al., *Journal of Integrative Plant Biology* 63, 1367–1381 (2021), [DOI 10.1111/jipb.13095](https://doi.org/10.1111/jipb.13095), is the primary 7DKZ paper. The complete **32-page Accepted Article** in the curator's local library was searched, with the Methods and all eight main figures/captions inspected. No discussion of quinone bending/nonplanarity or a mechanism for that distortion was found in that version. The accessible publisher abstract and supporting-information descriptions focus on antenna shifts, lipids and selected cofactor density. The complete seven-page supplementary PDF (Figures S1–S5) was subsequently searched and visually inspected: no discussion of quinone geometry or a dedicated A1 quinone density panel was found. Figure S5 covers lipid, chlorophyll and carotenoid density. The main PDF supplied on November 20 is byte-for-byte identical to the accepted manuscript, whose first-page notice explicitly states that it precedes copyediting/typesetting/pagination. The final typeset Version of Record is **not independently inspected**; this is not an absolute claim that the final article does not mention quinone geometry.

The accepted manuscript identifies pea cultivar **Alaska** (Methods p.16), describes β-DDM purification followed by β-DDTM in the final gradient, and discusses pH 9.0 crystallization at 285 K (pp.16–17). Its refinement Methods (p.18) specify **4XK8 with cofactors, lipids and detergents removed** as the molecular-replacement search model, then cofactor incorporation with Coot and refinement with phenix.refine. The paper does not establish that the crystallization pH caused the quinone distortion, and this atlas makes no such assignment.

## Interpretation status

A conjugated quinone headgroup is expected to favor substantially planar ring geometry; protein-induced strain is possible, but a deposited coordinate model alone cannot establish this degree of puckering as real. The simultaneous long C–O bonds and severe validation flags make ligand geometry/model building/refinement an important possibility to investigate. The actual cause is unknown. Neither a redox-state assignment nor a specific ligand-restraint failure has been demonstrated.

As descriptive context, the four PQN rings in the **current 4XK8 record** have plane RMS values about 0.0012–0.0032 Å, and the retained CCD ideal PQN ring about 0.0017 Å. These are reference geometries, not proof of a protein-bound energy minimum or a reconstruction of the authors' refinement history. Because the paper says cofactors were removed from the molecular-replacement model, direct inheritance of its quinone conformation must not be assumed.

Further interpretation would require the actual ligand-restraint/model-building records and/or an independently documented constrained refit against the deposited experimental data, with geometry, local fit and cross-validation assessed together. Merely flattening the display would conceal the deposited result. No re-refinement, DFT optimization or coordinate correction has been performed here.

## Inspectable evidence

- [Coordinate comparison figure](../downloads/validation/7DKZ_quinone/7DKZ_quinone_coordinate_comparison_v05.png) and [PDF](../downloads/validation/7DKZ_quinone/7DKZ_quinone_coordinate_comparison_v05.pdf).
- [Exact source/scene/bond check and native values](../downloads/validation/7DKZ_quinone/7DKZ_direct_coordinate_check_v02.json), [ring atom coordinates and signed plane offsets](../downloads/validation/7DKZ_quinone/7DKZ_ring_atoms_v01.csv).
- [Official 7DKZ record](https://www.rcsb.org/structure/7DKZ), [fresh deposited mmCIF](https://files.rcsb.org/download/7DKZ.cif), [official validation XML](https://files.rcsb.org/pub/pdb/validation_reports/dk/7dkz/7dkz_validation.xml.gz).

The accepted-manuscript source hash and search/visual inspection scope, including the supplement check, are retained in the packaged literature audit; the copyrighted manuscript itself is not redistributed with the website. The coordinate figure uses rigid centering/rotation for display and omits flexible tails; no atoms are moved onto a plane or optimized. The original molecular labeling style and native coordinates remain the atlas default.

Re-render the comparison from its packaged coordinates and CCD topology with `python tools/plot_quinone_review.py --output-dir PATH_OUTSIDE_REPO`. Display axes are a proper rigid rotation; plane fits are descriptive and do not change native atoms.
