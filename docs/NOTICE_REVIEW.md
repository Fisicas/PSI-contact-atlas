# Release notice and source follow-up

Prepared November 20, 2026. The user completed review and requested removal of obsolete/repeated notices while retaining relevant scientific qualifications. Published v1.0.0 and review package v01 remain unchanged; these updates are in review package v02.

## Presentation changes

- Removed the obsolete “not individually reviewed” wording from 48 derived-scene records and removed repeated development-pilot status paragraphs. Homology/template/RMSD provenance remains in the canonical notes and the new collapsed details.
- Default warning panels now contain concise, relevant cautions rather than all sample facts, selection rules and review history. The same serious source-model flags remain visible at the relevant sites; full context remains downloadable.
- Sample, mapping and review details start collapsed. Taxonomic display differences, deposited component labels, strain/growth/preparation facts, unknowns and source lineage remain inspectable. Molecular coordinates, labels, selected contacts, distance values and optional-density defaults are unchanged.
- 7DKZ has the explicit curator observation that the quinones are unusually bent, match the deposited coordinates, and are under interpretation. The literature claim covers the accepted manuscript and complete supplement actually checked; the final typeset main article remains unchecked.

## Primary-source resolutions

| Entry | Resolved fact | Remaining limit |
|---|---|---|
| 7DKZ | Cultivar Alaska; β-DDM/β-DDTM preparation; 4XK8 protein search model omitted cofactors before Coot cofactor placement and phenix.refine. Accepted manuscript Methods pp.16–18. | Causal origin/physical significance of bent quinones remains unresolved. Full seven-page SI checked: no quinone-geometry discussion found. Supplied main PDF is the accepted manuscript; final typeset article remains unchecked. |
| 9HYU | SEC and native-PAGE datasets were combined; consensus/focused maps form composite EMD-52518 used for the deposited model. Primary Results/Methods/Data availability, PMC12830998. | No single-preparation assignment is appropriate; an explicit SWISS-MODEL PDB parent is not inferred from a sequence-comparison template. |
| 9UH3 | PSI–9 FCPI is the α-DDM preparation; starting model explicitly 8Z11. Primary Results §2.1–2.2 and Methods §4.1/§4.8. | Related antenna classes are not independent biological replicates or a time course. |
| 9LUT | Monomer protocol is explicit; cultivar/accession study uses Tak-1 and Tak-2. | Exact Tak-1/Tak-2 allocation to this grid remains unassigned. |

Sources: [7DKZ primary DOI](https://doi.org/10.1111/jipb.13095), [9HYU primary text](https://europepmc.org/articles/PMC12830998), [9UH3 primary DOI](https://doi.org/10.1016/j.bbabio.2026.149588), [9LUT primary DOI](https://doi.org/10.1038/s42003-026-09631-w). Focused current RCSB lookups used the RCSB skill, and the local source-follow-up ledger retains method/record hashes. No source coordinate snapshot was silently replaced.

## Retained cautions

Quinone geometry flags (1JB0/7DKZ/9KZ9 and ring-bond flags in other entries), weak local 7COY oxygen features, weak/contour-sensitive modeled waters, long axial Mg separations, unavailable 1JB0 experimental data and the 9AU4 contour exception remain. Review completion does not establish occupancy, hydrogen bonding, redox state, atom-fit accuracy or normal coordination. Remaining sample/model ancestry unknowns are stated as unknowns in details.

The notice policy is explicit in `build/config/release_notices.json`; `tools/build_release_notices.py` generates `data/release_notices.js`. Critical canonical scientific notes and the full evidence are retained even when presentation is shortened or moved into details.
