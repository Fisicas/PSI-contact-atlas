# Methods

## Sources

Each entry is read from the deposited mmCIF archived in `build/inputs/structures/` (model 1, author chain and residue numbering, highest-occupancy alternate location). `data/sources.json` gives the PDB structure-model revision, its date and the SHA-256 of each file. Chemical-component definitions (`build/inputs/ccd/`) give atom names, bonds and the carbonyl oxygens of the quinones.

## Scenes

A scene is one protomer and one environment: the special pair (P<sub>A</sub> and P<sub>B</sub> with their ligands), the isolated P<sub>A</sub> network, and the A<sub>1A</sub> and A<sub>1B</sub> quinone pockets.

- **Curated scenes** (the first 112) list atoms and atom pairs chosen in an earlier PyMOL build and reviewed scene by scene; `build/config/scenes.json` records them with their earlier annotation and value. They are a curated subset of nearby pairs, not an exhaustive census.
- **Waters.** P<sub>A</sub> scenes show the reference-site water. Special-pair scenes show every deposited water within 5 Å of the P<sub>A</sub>/P<sub>B</sub> Mg and oxygens (O1A, O2A, O1D, O2D, OBD). Nothing is added where the deposit has no water.
- **Derived scenes** (entries released after the curated build). For each environment the template is the curated scene of the most similar entry: same organism, then the same deposited cofactor components, then the best resolution. The derived scene contains the residues at the homologous positions (PsaA/PsaB aligned to 1JB0 numbering; cofactors by role), the template’s atoms, and the template’s atom pairs mapped to the new model. Chlorophyll atoms map by name (Chl *a* and *a*′ share names); quinone atoms of a different component map to the nearest atom of the same element after superposition, so each carbonyl keeps its position. Waters follow the rules above; each special-pair water is paired with its nearest diagnostic atom. The camera is the template camera superposed on the new coordinates. Template pairs with no counterpart are listed in the scene notes. Cofactor roles are found from 1JB0 anchors: the P<sub>A</sub>/P<sub>B</sub> Mg nearest the PsaA His680 / PsaB His660 NE2 positions, and the quinone oxygen nearest the PsaA Leu722 / PsaB Leu706 backbone N.
- **Check of the derivation rule.** Re-deriving curated scenes of five entries from another entry reproduces most curated pairs (non-water pairs reproduced: 95/106). Every difference traces to the curated selections themselves differing between entries, or to a residue that differs at that position. Full output: `build/provenance/derive_rule_check.txt`.

## Distances, classes and chemical basis

Distances are Euclidean separations between deposited heavy atoms. Class rule, in order: Mg involved → `mg`; same residue → `intra`; C or S involved → `cs_contact`; more than 3.5 Å → `context`; water involved → `water`; both atoms are oxygens that cannot carry a hydrogen (any cofactor oxygen; a backbone or Asn/Gln amide C=O) → `acceptor_pair`; otherwise → `polar`. Carboxylate O and His N stay `polar` because their protonation state is not known; the `chemical_basis` column says so. The chemical basis states what the atom types allow; a backbone N–H (not Pro), Ser/Thr/Tyr OH, Trp NE1, Asn ND2, Gln NE2, Lys NZ and Arg N are treated as donors. No hydrogens are added and no angles are evaluated.

## Homologous comparison

PsaA and PsaB of every protomer are aligned to 1JB0 chains A and B (global alignment, BLOSUM62, gap open −10, extend −0.5); the full mapping is `build/provenance/alignment_to_1JB0.csv`. It reproduces all 133 P<sub>A</sub>-network mappings of the curated build. A comparison column is created when any scene of an environment lists a polar, water, O···O or Mg pair between a cofactor atom and a PsaA/PsaB atom (or the site water); every protomer is then evaluated for that column.

## Reference-site water

For each protomer the 25 chlorin-core atoms of P<sub>A</sub> are superposed on those of 1JB0 P<sub>A</sub> (`CHLORIN_CORE` in `tools/build_atlas.py`), the position of 1JB0 HOH5011 is carried over, and the nearest deposited water within 3 Å is the site water. `build/provenance/site_water.csv` lists the core RMSD, the offset and the next-nearest water for every protomer. A positional assignment is not proof that a water is conserved, and a short pigment–water distance is a separate fact (9AU4 HOH907 lies 3.95 Å from P<sub>A</sub> O2D but is not at the site).

## Not assessed

Map density, local resolution and per-atom validation (each structure page links its wwPDB validation report); Mg coordination geometry; protonation and hydrogen positions; model ancestry. Protomers of one entry are not independent replicates; no standard errors are given.
