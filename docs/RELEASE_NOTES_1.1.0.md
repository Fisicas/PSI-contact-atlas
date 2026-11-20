# PSI Contact Atlas 1.1.0 — changes since the original release

This document compares v1.1.0 with the original v1.0.0 release of November 17, 2026.

## Eight added structures

The following entries are new in v1.1.0. Each contributes one deposited protomer and four scenes: special pair, P<sub>A</sub> network, A<sub>1A</sub> and A<sub>1B</sub>. Together they add eight protomers and 32 scenes. The 14 original entries remain included.

| Added PDB | Organism | Deposited method / nominal resolution | Preparation / assembly context |
|---|---|---|---|
| [9SE6](https://www.rcsb.org/structure/9SE6) | *Chlamydomonas reinhardtii* | Cryo-EM / 1.83 Å | Green alga, PsaB-His20 PSI preparation |
| [9LUT](https://www.rcsb.org/structure/9LUT) | *Marchantia polymorpha* | Cryo-EM / 1.94 Å | Liverwort, PSI-LHCI monomer |
| [8WEY](https://www.rcsb.org/structure/8WEY) | *Cyanidium caldarium RK-1 (NIES-2137)* | Cryo-EM / 1.92 Å | Red alga, PSI-LHCI monomer |
| [7DKZ](https://www.rcsb.org/structure/7DKZ) | *Pisum sativum (pea)* | X-ray crystallography / 2.3930 Å | Flowering plant, PSI-LHCI, X-ray |
| [9UH3](https://www.rcsb.org/structure/9UH3) | *Chrysotila roscoffensis* | Cryo-EM / 1.74 Å | Haptophyte, PSI-9 FCPI |
| [9HYU](https://www.rcsb.org/structure/9HYU) | *Chromera velia* | Cryo-EM / 1.84 Å | Alveolate, PSI-FCP with SOD heterodimer |
| [9KZ9](https://www.rcsb.org/structure/9KZ9) | *Rhodomonas sp. NIES-2332* | Cryo-EM / 2.08 Å | Cryptophyte, PSI-14 ACPI |
| [8XLS](https://www.rcsb.org/structure/8XLS) | *Thalassiosira pseudonana CCMP1335* | Cryo-EM / 2.3 Å | Diatom, PSI-5 FCPI |

The table preserves deposited resolution values; these are not per-atom coordinate uncertainties. Preparation and mapping qualifications remain on each structure page. In particular, 9SE6 has a PsaB His20 tag; 9HYU has case-sensitive split PsaA chains A/a; 7DKZ retains the deposited pea source name while documenting its current taxonomy display. Related antenna assemblies are not biological replicates or a physiological time course.

## Coverage change

| Measure | Original v1.0.0 | v1.1.0 |
|---|---:|---:|
| Deposited PDB structures | 14 | 22 |
| Deposited protomers | 32 | 40 |
| Molecular scenes | 128 | 160 |
| Selected scene contact rows | 865 | 1,107 |
| Unique atom pairs | 691 | 882 |
| Numeric homologous comparison values | 1,121 | 1,617 |
| Comparison cells, including blanks | 1,184 | 1,720 |
| Protomers with packaged experimental-density figures | 0 | 39 |

## New visualization features

- **Optional unmasked sections and fixed 3D mesh previews:** controls now cover all 160 scene pages, including original entries and protomers 2/3. Panels start closed; the original molecular viewer and label style remain the default.
- **Experimental-density figures:** 254 section images and 208 fixed mesh images cover 21 structures, 39 protomers and 156 scenes. The four 1JB0 scenes explicitly report unavailable experimental data; no simulated density is substituted.
- **Source-specific contour information:** source IDs, processing, contour values/units and limitations accompany the figures. The 9AU4 author-contour and explicitly exploratory alternative remain separate display options. Contour appearance is not a cross-map quality score.
- **Readable presentation:** scientific concerns remain visible; routine sample/mapping provenance starts collapsed. The README has four single-column animated examples with wrapping captions, the approved chlorin icon and the selected native-coordinate social preview. The social artwork restricts guides to chemically compatible polar/water candidates; the atlas retains all explicit contact classifications.

All **208 mesh thumbnails are clickable**, opening the exact native scene and contour in an interactive viewer covering **39 protomers / 156 scenes**. Rotate, Hand / pan, zoom, adjust contour/opacity, inspect native atoms and compatible partner choices, or export PNG/map/CIF. Compatible polar-contact atoms appear first, additional water-contact candidates second, then other atoms. The original atlas contact classes are retained; candidates are not confirmed hydrogen bonds. Static PNG links remain a fallback, and 1JB0 remains unavailable. See [interactive density methods and limits](INTERACTIVE_DENSITY.md).

## New analyses and source checks

1. **New-entry mappings and sample context.** PsaA/PsaB sequence alignment, cofactor roles, split-chain handling, homology-derived scene selections, reference-site waters, preparation and primary-paper metadata were checked before scene generation. Primary-source follow-up resolved 7DKZ cultivar Alaska, 9UH3 α-DDM preparation/8Z11 starting model and 9HYU combined datasets/composite map. Documented unknowns remain unknown.
2. **All-entry source and cofactor-geometry audit.** Archived/current atom-record identity was checked for all 22 structures (1,152,290 atom records), alongside source hashes and validation context. The cofactor review includes 414 carbonyl bond measurements and 79 Mg–ligand pairs, with source-specific planarity and geometry flags. This did not replace coordinates or refine models.
3. **Scoped local-density feature screen.** All 39 available-data protomers received the documented feature-level review. Packaged results include 388 native diagnostic map samples and 20 focused axial distances, plus map/frame/crop provenance. These are not an all-atom fit validation, half-map cross-validation, an omit-map result or a distance-uncertainty estimate.
4. **7DKZ quinone investigation.** Both quinone scenes were checked directly against the current deposited coordinates and CCD connectivity. Severe ring nonplanarity/long carbonyl bonds are documented as source-model concerns. The curator is working on interpretation; no physical conformation, causal refinement failure or redox assignment is established. The accepted manuscript and complete supplement were checked; the final typeset main article remains unchecked. [Coordinate and literature review](7DKZ_QUINONE_REVIEW.md).

The review retains qualifications for 1JB0/7DKZ/9KZ9 quinone geometry, long 9KZ9/5OY0 axial separations, weak local 7COY features, contour-sensitive modeled waters and source/preparation limitations. It does not remove weak waters or repair ligands to improve the pictures. [Scientific review](SCIENTIFIC_REVIEW.md) · [Scientific dispositions](SCIENTIFIC_CLOSURE.md).

## Comparison scope and corrections

The eight additions received an extra 3.5 Å diagnostic N/O-neighborhood supplement. The 14 original scene selections were retained. Consequently, selected pair counts are not equal or exhaustive species inventories; deposited protomers and related reconstructions are not independent biological replicates. [Comparison scope](COMPARISON_SCOPE.md).

9OY9/9OZ3 primary-citation and monomer/trimer descriptions were corrected without replacing atomic inputs; their linked primary study remains identified as a preprint. The original 128 scenes retain their atoms, bonds, contacts, labels, cameras and water rules. All 1,184 existing comparison cells and 128 original scene-contact CSV files are preserved. The structural census remains a separate project.

## Software and reproducibility changes

- Fixed stale asynchronous scene/preview callbacks and observer cleanup; wrapped narrow PNG/GIF export captions.
- Added exact-byte local-file downloads for CSV/mmCIF/PyMOL assets and corrected case-sensitive PyMOL Mg sphere selection. The original molecular draw/label algorithms and native coordinates are retained.
- Packaged source/validation hashes, cofactor context, diagnostic samples, optional-figure provenance and numerical/source/asset/download checks. Added density/DOM, metadata and branding checks to CI; remote CI on the actual final commit is still pending.
- Synchronized CFF, BibTeX, RIS, CSL-JSON and Zenodo metadata from shared configuration, including official CFF-schema and publication-state consistency checks. Local browser, test and build receipts retain their actual scope.

## Citation and release boundary

For citation and version DOI details, see the [citation guide](CITATION.md) and the [v1.1.0 release](https://github.com/Fisicas/PSI-contact-atlas/releases/tag/v1.1.0).

Author: Michael Raymond Nelson, ORCID 0009-0004-9809-9842. Code: MIT. Derived data, figures and documentation: CC BY 4.0; source terms retained. Cite the atlas version actually used, individual PDB entries and primary papers. [Release metadata review](RELEASE_METADATA_REVIEW.md).
