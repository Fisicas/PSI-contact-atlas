# Release candidate review — 1.1.0 release review

*Historical review record. For v1.1.0 publication and citation information, see [release notes](RELEASE_NOTES_1.1.0.md) and the [citation guide](CITATION.md).*

Prepared November 20, 2026. **Unpublished final-version review copy. Scientific retention dispositions accepted; publication approval has not been given.** Candidate coverage is 22 structures, 40 deposited protomers and 160 scenes. Experimental-density figures cover 21 structures, 39 protomers and 156 scenes; 1JB0 remains explicitly unavailable. The published v1.0.0 checkout is unchanged.

| Prepublication item | Current disposition |
|---|---|
| Scientific review | Scoped screen completed with retained limitations. All 39 protomers with available data: 462 packaged figures / 85 sheets plus eight targeted planes. 1JB0 unavailable. 388 native diagnostic samples and focused axial geometry packaged. Global source/ligand audit covers all 22 entries. No blanket model-fit approval. |
| Comparison scope | Completed. Eight additions received the diagnostic N/O-neighborhood supplement; 14 baseline selections retained. Counts are selected contacts, not equal/exhaustive species inventories. |
| Reproducible build | Local checks pass. Fresh coordinate/download rebuild reproduces 816 files exactly; portable X-ray/EM density recipe exercised; all 208 mesh previews regenerated. New density/scientific/DOM CI gates prepared; GitHub CI has not run. |
| Website review | Completed in explicitly authorized isolated headless Chrome/Edge sessions. All 160 Chrome scenes, representative Edge scenes, all comparison tables, desktop/tablet/phone light/dark layouts, actual exports/downloads and delayed-navigation checks pass. Three observed browser issues were fixed; no personal browser was controlled. See BROWSER_REVIEW.md. |
| Release preparation | Approved chlorin icon/native-coordinate social preview installed locally; version/citation metadata synchronized as an unpublished candidate; review archive and provenance prepared. Final publication metadata, remote CI and publication approval remain gates; browser review is completed. |

## Scientific decision for review

Retain the deposited coordinate records with prominent source-specific qualifications. Do not use flagged 7DKZ/9KZ9 quinone bond geometry for species-dependent chemistry or redox assignments. Baseline 1JB0 is a numbering reference, not a chemical gold standard. Retain 9KZ9's long Mg–His separation, weak/contour-sensitive 7DKZ/9S6P/9SK3 waters, weak local 7COY oxygen features, long 5OY0 protomer 3 axial distances and exploratory 9AU4 contour exception. Mapping and preparation uncertainty remains explicit. See [Scientific review](SCIENTIFIC_REVIEW.md), [Comparison scope](COMPARISON_SCOPE.md), [Validation](VALIDATION.md).

## Proposed GitHub About text — not applied

Interactive PSI heavy-atom contact atlas: 22 PDB structures, 40 protomers, 160 scenes and 882 unique selected atom pairs. Compare P700/P_A and A1 environments; inspect experimental density for 39 protomers; download CSV, mmCIF and PyMOL scripts. Source-model qualifications retained.

The plain-text About field uses P_A; rendered README/page prose uses P<sub>A</sub>. Counts are selected rows/pairs, not confirmed hydrogen bonds. The exact proposed text is also in `GITHUB_ABOUT_PROPOSED.txt`; no remote description has been changed.

Apply the proposed description only with the approved updated version; published repository settings have not been changed here. The approved social preview is `media/branding/social-preview.png` (1280 x 640, under 1 MB). The selected favicon is chlorin option 3. GitHub social settings have not been changed.

## Version and DOI handling

The existing version-specific DOI [10.5281/zenodo.24318460](https://zenodo.org/records/24318460) belongs to v1.0.0. Its concept DOI is [10.5281/zenodo.24318459](https://doi.org/10.5281/zenodo.24318459), verified from the existing record API on November 20. No new DOI has been reserved or assigned. Candidate CFF/Zenodo metadata omit a release date and DOI; do not reuse the v1.0.0 version DOI for the expanded atlas.

After review of the retained scientific limitations and explicit approval, prepare the final release version/date and genuine new version DOI as applicable; update and review every generated citation/status marker (the documentation/citation generators use explicit publication state and reject missing or reused identifiers). Run final checks and remote CI against the exact proposed commit. Review the final diff, tag/archive contents and social/About settings before the authorized publication action. No push, tag, upload, external settings change or release has been performed here.

## Preserved scientific identity

All 160 scene atom/bond/contact/label/camera fields match the prior development copy exactly; only scene scientific notes changed. The molecular drawing and label routines are byte-identical; export-caption layout and app lifecycle/download transport were fixed after real-browser review. All 349 checked archived coordinate/CCD and scene-crop/contact files match. The PyMOL Mg display selector and optional mesh overlays were corrected without changing coordinates, measured distances or original web label styling. Earlier review outputs and figures remain preserved in the separate review backup.

## Browser fixes in rc.2

Disconnected stale resize callbacks and guarded delayed scene/preview loads; wrapped PNG/GIF footer captions at narrow viewports; added lazy exact-byte local-preview downloads. The canonical scientific files, measured values and original molecular label styling are preserved. [Browser evidence and limits](BROWSER_REVIEW.md). The earlier rc.1 review ZIP remains archived separately.

## Scientific closure in rc.3

The remaining 24 available baseline protomers were individually screened. The 7COY local oxygen, 9S6P/9SK3 modeled-water and 5OY0 axial qualifications are visible in scene notes and comparison context. Native diagnostic samples and focused axial geometry are downloadable and independently checked. Coordinates, contacts, comparison values and original label styling are retained. The user accepted the retained scientific dispositions; stronger chemistry/coordination/water claims remain unsupported. See [the blocker ledger](SCIENTIFIC_CLOSURE.md). Prior rc.1 and rc.2 archives are preserved.

## Final-version preparation

Version 1.1.0 is staged in a separate review copy. Scientific retention with the documented qualifications was accepted by the user on November 20. Actual release date and version DOI remain unset; the existing concept DOI is contextual. Citation formats are generated from a shared metadata configuration and checked against the official CFF 1.2.0 schema. No GitHub/Zenodo mutation or publication occurred. [Citation plan](CITATION.md) · [Release review](RELEASE_REVIEW.md). Earlier rc.3 evidence remains historical at its stated scope.


## Current v06 interactive-density review

The candidate now integrates all 156 available interactive density scenes (39 protomers / 21 structures) and 208 exact clickable thumbnail presets, retaining every static image. The full atlas remains 22 structures / 40 protomers / 160 scenes; 1JB0's four density routes are explicitly unavailable. The 312-load file/HTTP browser review and independent native-atom/map/preset verifier pass. New receipts state current scope separately from historical original-viewer checks. Original molecule/label algorithms, native source files, canonical contacts/downloads, static figures and selected branding are preserved. See [interactive methods](INTERACTIVE_DENSITY.md) and [current validation receipts](VALIDATION.md). Publication, remote CI and live settings remain pending approval.
