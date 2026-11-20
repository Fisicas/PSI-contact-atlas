# Final diff review — v1.1.0 local candidate

*Historical review record. For v1.1.0 publication and citation information, see [release notes](RELEASE_NOTES_1.1.0.md) and the [citation guide](CITATION.md).*

Reviewed November 20, 2026 against published v1.0.0 commit `f57f8bc7e6228f025f8b89d24e4f5a061c4be2a3`. This is a review result, not publication authorization or a remote CI result.

## Scientific identity

- All 128 existing scenes retain their residues, atoms, bonds, contacts, labels, cameras, pivots, water rules and download paths exactly. All 1,184 existing comparison cells match. All 128 existing scene-contact CSV files match byte for byte.
- All 149 checked archived coordinate/CCD/crop files match. The eight additions supply 32 new scenes: 22 structures, 40 deposited protomers and 160 scenes total. The scientific retention decision and all geometry/water/source qualifications remain explicit.
- No original published file is removed. The current published checkout's 593 inventoried files remain unchanged. Additional generic UNK/UNL CCD definitions are retained as auxiliary public source files; no scientific interpretation is assigned to them by this review.

## Runtime, build and presentation review

Reviewed changes include guarded asynchronous navigation and resize cleanup, exact file-preview download payloads, optional closed density panels, split-PsaA/revision labels, concise notices with collapsed provenance, and wrapped export footers. The molecular draw/label algorithms are retained. Build changes add source-bound context, notices and exact-download generation; checks cover numerical identity and corruption cases. The configured actions/setup-node v7.1.0 release was verified against the official action release page; remote execution is still pending.

Two hardcoded review-state labels were corrected so they do not persist accidentally into release output. The README uses a single-column four-GIF gallery with wrapping captions, approved icon and social artwork, plus a subscripted P<sub>A</sub> in rendered prose.

## Final social artwork

User-selected editorial layout 1 is installed in this local candidate. The complete displayed native environment fits inside the frame; no text overlaps the molecular region. Source credit uses a true subscripted A. Exactly four donor–acceptor-compatible protein polar guides and five water guides are shown. Mg–His coordination, packing and intramolecular/acceptor–acceptor guides are omitted only from the artwork. The atlas's explicit classifications, toggles and data are unchanged. Native coordinates remain unchanged; phytyl atoms and labels remain hidden as documented. Candidates do not establish actual hydrogen bonds.

## Metadata review and publication boundary

Version/tag, title, author/ORCID, licenses, scope and all five citation formats are synchronized and checked. Planned date: November 20, 2026. The actual publication date and genuine new version DOI remain unset; no authenticated Zenodo access is configured in this session. Neither the concept DOI nor v1.0.0 DOI is substituted for a new version identifier. See [metadata review](RELEASE_METADATA_REVIEW.md).

The complete supplement and accepted manuscript contain no discussion of the quinone distortion found in this scoped check. The supplied main PDF is the same accepted manuscript, not the final typeset article; wording remains limited accordingly. This does not prevent retention of the independently verified deposited-coordinate observation with its qualifications.

All 23 tests and fresh metadata/notices/source-context/closure/density/download/DOM checks passed before the final artwork/docs installation; final branding, local-browser and strict final-manifest checks cover that installation separately. Earlier full-160-scene browser and clean-build evidence is retained at its stated scope. No blanket chemical model validation is claimed.

Remaining publication transaction: approve this final package; obtain genuine version DOI/actual date through the chosen existing-series workflow; regenerate all publication-state/citation outputs and verify the exact payload/CI; make one coordinated approved release and verify the live result. No push, tag, DOI reservation, remote settings change or deployment occurred here.


## Current v06 interactive-density review

The candidate now integrates all 156 available interactive density scenes (39 protomers / 21 structures) and 208 exact clickable thumbnail presets, retaining every static image. The full atlas remains 22 structures / 40 protomers / 160 scenes; 1JB0's four density routes are explicitly unavailable. The 312-load file/HTTP browser review and independent native-atom/map/preset verifier pass. New receipts state current scope separately from historical original-viewer checks. Original molecule/label algorithms, native source files, canonical contacts/downloads, static figures and selected branding are preserved. See [interactive methods](INTERACTIVE_DENSITY.md) and [current validation receipts](VALIDATION.md). Publication, remote CI and live settings remain pending approval.
