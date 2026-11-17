# Changelog

Changes are grouped as **data** (numbers or atoms), **interpretation** (classes and wording) and **software**.

## 1.0.0 — 2026-11-17

First versioned release, archived on Zenodo. No distance in the earlier 112 scenes changed.

### Data

- **New entries** 9OY9, 9OZ3: cyanobacterial PSI released after the curated build (*Synechocystis* sp. PCC 6803 PsaB red-shift variant, 1.76 Å and 1.88 Å). Their 16 scenes are derived by the documented homology rule ([`docs/METHODS.md`](docs/METHODS.md)), not reviewed one by one. The atlas now has 14 entries, 32 protomers and 128 scenes.
- **Unique atom pairs.** 865 scene contact rows are 691 physical atom pairs: pairs shown in both the P<sub>A</sub> and the special-pair scene of a protomer are one observation. New table `downloads/tables/atlas_unique_contacts.csv`.
- **Stable IDs and named tables.** Every pair has a `contact_id`; every homologous comparison a `comparison_id`. Per-environment tables `atlas_table_PA_network.csv`, `atlas_table_special_pair.csv`, `atlas_table_A1A.csv`, `atlas_table_A1B.csv`.
- **Archived inputs and portable build.** The exact deposited files and CCD definitions are in `build/inputs/`, the curated selections in `build/config/`; `tools/build_atlas.py` rebuilds every output from them.
- mmCIF crops are now written by the build from the deposited files (same atoms as before).

### Interpretation

- **New class “O···O, no H donor”** (`acceptor_pair`): 51 scene rows in which both atoms are oxygens that cannot carry a hydrogen (a cofactor carbonyl or ester oxygen facing a backbone C=O, e.g. the A<sub>1</sub> quinone carbonyl and the PsaA Met688 / PsaB Met668 backbone O in 1JB0) were listed as polar (hydrogen-bond) candidates. Distances unchanged. Compare-matrix columns for these partners are marked and not colour-scaled.
- **New column `chemical_basis`** on every pair: donor–acceptor compatible, acceptor–acceptor, water-involved, unresolved (His/Asp/Glu protonation), Mg–ligand, beyond the screen, same residue, or involves C/S.
- **“Packing” renamed “C/S contact”** (`cs_contact`): the class is element-based and is not evidence of an attractive interaction.
- Missing-water cells now read “no deposited water meets the site rule” instead of implying absence. Wording uses “special pair” throughout (P700 or P740).
- 5OY0 condition “WT (paper)” is now “Wild type”.

### Software and metadata

- `tools/verify_public.py` now checks every exported table at its own precision, unique keys, crops, the class and chemical-basis rule and the file manifest; strict mode fails if an archived input changed. `tests/` holds deliberate-corruption tests; `.github/workflows/verify.yml` runs the rebuild, the verifier and the tests.
- `data/sources.json` records the PDB structure-model revision of each file. Structure pages link the wwPDB validation report.
- CSV column `v02_annotation` renamed `curated_annotation`. Column guide in `downloads/README.md`; methods and validation in `docs/`.
- Site link fixed (`https://fisicas.github.io/PSI-contact-atlas/`; the lowercase address returned 404). Version label “preview” replaced by 1.0.0. `CITATION.cff` gains ORCID, abstract and release date; `.zenodo.json` describes the archive as a dataset.

### Rechecked against current PDB files

On 2026-11-17 every coordinate, distance, class and comparison cell was recomputed from the then-current PDB files (structure-model revisions 1JB0 2.1, 5OY0 3.2, 6KMW 3.1, 6KMX 3.1, 7COY 2.2, 9AU4 1.1, 9EYS 2.0, 9I9L 2.0, 9OY9 1.0, 9OZ3 1.0, 9QFP 1.1, 9S6P 2.0, 9SK3 2.0, 9YL7 1.0). all 18,378 scene-atom occurrences, 865 scene distances and classes, 1,121 comparison cells and 128 crops were reproduced unchanged.

## 0.1.0-preview — 2026-10-17

Initial public preview (12 entries, 28 protomers, 112 curated scenes).
