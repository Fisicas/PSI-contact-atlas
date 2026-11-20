# Validation and limits — 1.1.0

Prepared 2026-11-20; published release. The table is generated from recorded receipts in `build/provenance/release_candidate_checks.json`. A missing receipt is not a pass. Local checks do not claim that future GitHub Actions or live publication have succeeded.

| Check | Recorded status | Evidence summary |
|---|---|---|
| independent_atlas | PASS | Final strict native numerical/source/manifest verification; this excluded verifier receipt is generated after final documentation/receipt insertion. |
| scientific_review_context | PASS | Fresh v06 review_context check passed; scientific qualifications retained. |
| scientific_closure | PASS | Fresh v06 scientific_closure check passed; scientific qualifications retained. |
| release_metadata | PASS | Fresh v06 release_metadata check passed; scientific qualifications retained. |
| release_notices | PASS | Fresh v06 release_notices check passed; scientific qualifications retained. |
| density_assets | PASS | Fresh v06 density_views check passed; scientific qualifications retained. |
| density_DOM_contract | PASS | Fresh v06 density_DOM check passed; scientific qualifications retained. |
| unit_tests | PASS | All 23 mapping/metadata/download/corruption tests pass against the regenerated v06 manifest. The initial premanifest failure is retained in local reports and resolved by regeneration. |
| clean_rebuild | PASS | Fresh notice/scientific/citation build reproduced 833 files exactly before the final figure-margin derivative and receipt insertion. Scientific coordinates/citations are unchanged; final additional figure is independently rendered from packaged native coordinate evidence. |
| pymol_exports | PASS | 160 scripts executed against crops and verified full models; 2,214 distance checks and 320 Mg display checks. Maximum distance deviation 0.000032326 A. All 160 PML files remain byte-identical to the checked rc.1 exports. The rc.3 preservation check again proves all PML files byte-identical; no new PyMOL execution is claimed. |
| download_payloads | PASS | Fresh v06 download_payloads check passed; scientific qualifications retained. |
| browser_review | PASS | Historical 160-scene review retained. Fresh v04 follow-up checks all 22 revision labels, 7DKZ notices at desktop/phone, corrected Methods wording and the new README media layouts with zero JS errors. |
| published_preservation | PASS | 1478 protected v05 scientific/display/input/metadata files and all 593 published files unchanged; published checkout clean. |
| readme_media_layout | PASS | Selected social image, icon and four unchanged animated GIFs fit in ten local light/dark media-layout checks; captions wrap. GitHub-hosted rendering not claimed. |
| documentation_preservation | PASS | Historical v03 documentation-only comparison retained at its stated scope. v04 additionally updates the selected artwork/provenance, release-state prose and review receipts; final scientific preservation is recorded by final_diff_review. |
| final_diff_review | PASS | 1478 protected v05 scientific/display/input/metadata files and all 593 published files unchanged; published checkout clean. |
| social_branding | PASS | Fresh v06 branding check passed; scientific qualifications retained. |
| interactive_density_source | PASS | Fresh v06 interactive_density check passed; scientific qualifications retained. |
| interactive_density_browser | PASS | 312 scene loads (156 over HTTP and file), 344 map parser checks, all presets/candidate order; seven representative full interactions per protocol. |
| interactive_density_followup | PASS | After one invalid-route guard: six representative HTTP/file loads, eight invalid routes, lazy loading, deliberate dependency failure/static fallback and seven exact native CIF downloads passed. |
| interactive_density_rebuild | PASS | Fresh output build reproduces 156 payloads, both indexes and packaging provenance byte for byte (159 files). |
| readme_counts | PASS | Canonical tables confirm 22 structures, 40 protomers, 160 scenes, 1,107 selected scene rows, 882 unique pairs and 1,617 numeric comparisons; 39 protomers / 156 interactive density scenes. Proposed About text checked; remote settings unchanged. |

The coordinate/geometry scientific screen and its retained limitations are documented in [SCIENTIFIC_REVIEW.md](SCIENTIFIC_REVIEW.md). Local density review now covers all 39 protomers with available experimental data: 462 packaged figures / 85 review sheets, plus eight targeted native planes. This is a scoped local-feature screen, not all-atom fit validation; 1JB0 remains unavailable. Generated figures, positive contours and source validation metrics are distinct evidence.

Independent numerical verification checks native scene atoms/distances, crops, comparison cells and public-file hashes. Source-review verification separately checks coordinate/validation hashes, intraligand distances, planarity, official XML records and retained critical warnings. Density verification checks coverage, native protomer asset identities, source/frame/crop provenance, image hashes and PNG integrity. Interactive-density verification independently checks 22,379 native scene atom occurrences, 172 exact CCP4 crops (8,664,627 voxels), 208 preset/fallback bindings and the pinned viewer. The browser receipt separately records 312 file/HTTP scene loads, map transforms, candidate ordering and representative interactions. The Node test checks the optional-panel DOM contract; it does not establish real browser rendering, downloads or interaction unless a browser receipt is separately recorded.

Clean coordinate rebuilding uses archived inputs and fixed configuration. Density image regeneration needs external hash-checked maps, the declared recipe and the scientific/PyMOL environments. Image hashes verify the packaged derivatives; bitwise image identity across renderer/platform versions is not promised. Browser and PyMOL checks state their actual scope and environment in the receipts.

No test establishes hydrogen bonds, occupancy, protonation, redox state, biological independence, or a general uncertainty for a modeled distance. Known geometry qualifications remain after technical checks pass. No publication or DOI update is implied by these records.
