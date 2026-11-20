# Eukaryotic PSI development pilot methods

Historical pilot derivation record, carried into unpublished candidate 1.1.0-rc.1. Mapping and metadata gates were completed before scene generation; packaged gate summaries are under build/provenance, with full intake evidence in the separate pilot audit folders. Current review status and qualifications are in [SCIENTIFIC_REVIEW.md](SCIENTIFIC_REVIEW.md).

The first four entries were added from current RCSB files fetched November 19, 2026. All selected native atom coordinates are identical to the older local snapshots (156,973 common native atom identities in total); hashes and source revisions differ, and the current raw files are archived separately. Model 1, native author identifiers, deposited highest-occupancy alternate positions, and coordinate precision are retained. No atoms are fitted, corrected, added, or interpolated.

Scenes begin with the existing homology derivation. New scenes only receive a prospective diagnostic-neighborhood supplement: for special-pair and P_A scenes, use the existing diagnostic pigment oxygens OBD/O1A/O2A/O1D/O2D; for each quinone scene, use PQN O1/O4. Include every PsaA/PsaB N/O atom within 3.5 Å and its residue heavy atoms. Existing pair classes and chemical-basis rules are applied by the builder. These are heavy-atom separations, not confirmed hydrogen bonds. This supplements template-selected pairs and can expose eukaryote-specific contacts such as the P_B ester/Tyr environment. Water rules are unchanged.

The supplement is not a full contact census and is not retroactively applied to the 14 baseline entries. New comparison columns can evaluate homologous pairs across the existing entries, but the old curated scenes remain unchanged. Record this selection asymmetry when comparing scene pair counts.

9SE6 is a tagged PsaB-His20 preparation from the Cyt-c6 crosslinking study, not an unmodified wild-type label. 9LUT is the monomer isolated under its stated detergent conditions; 9LUU is a related, differently prepared dimer. 8WEY is strain RK-1 (NIES-2137), with Phyre2/model-building ancestry distinguished from an explicit PDB starting model. 7DKZ remains X-ray, 2.393 Å, with source name Pisum sativum, taxon 3888, and the RCSB resolved-name synonym Lathyrus oleraceus; the deposited CLA P_A is not silently relabeled or corrected.

Validation reports were archived and their cofactor records extracted. All eight additions now have the scoped local-map screen documented in [the current scientific review](SCIENTIFIC_REVIEW.md). The original four-entry screen remains a historical record in the separate label/density audit folder. 7DKZ quinone geometry and site-water claims remain on hold. This pilot checks coordinate reproduction and mappings; it is not approval of new biological or hydrogen-bond claims.

The PyMOL callout experiment was reverted at the user's request. All new-entry exports use the original styling, and the web viewer label renderer is unchanged.

## Full eight-entry development expansion

9UH3, 9HYU, 9KZ9 and 8XLS were added after independent sequence/role/revision/site-water checks and primary/deposition metadata reconciliation. All 233,771 common native atom identities in these four entries agree exactly with the older local snapshots; the source revisions and hashes are archived separately. Each adds one deposited protomer and four environments. Totals: 22 structures, 40 protomers, 160 scenes. The current scoped density screen covers these four as well as the first four; coordinate reproduction and positive map contours do not establish correct chemistry or scientific acceptance. The retained 9KZ9 A1 geometry concern is detailed in the current review.

9HYU has split PsaA. Native A is the C-terminal pocket-bearing fragment and a the N-terminal fragment; both are shown in the chain annotation. The reaction-center mapping uses A/B, while the diagnostic N/O neighborhood is screened on A, a and B. The generic chain-A description does not justify misassigning the shorter a fragment as a full PsaA.

9KZ9's P_A Mg–His679 NE2 separation is 3.05697 Å, outside the 3.0 Å automatic discovery gate. Its role is supported by independent sequence anchors, the nearest cofactor identity with a large margin to alternatives, P700 Mg-pair geometry, diagnostic completeness and the archived census assignment. An explicit `--mapping-report` route binds this exception to the inspected source SHA-256, rejects missing/incompatible roles, and leaves general discovery thresholds unchanged. It does not validate Mg coordination geometry. Tyr602 OH and Thr742 OG1 are the two N/O candidates within 3.5 Å of P_A O1D; their hydrogens and donor angles remain unverified.

9UH3 remains linked to its 1/4/6/8/9-FCPI study series without interpreting antenna number as a physiological time course. 8XLS is the five-FCPI diatom assembly; primary Methods describe ModelAngelo and map processing, distinguished from the sparse deposited initial-model category. The atlas core frame is not an antenna inventory or antenna superposition.

## Optional density views

The default molecular view and original labels are retained. Unmasked sections and fixed 3D mesh previews are available in a closed optional panel for every deposited protomer. See [DENSITY_VISUALIZATION_PILOT.md](DENSITY_VISUALIZATION_PILOT.md). The 7DKZ flags remain visible. No local map support is automatically approved by generating these views. 1JB0 has an explicit unavailable-data status.

### Complete protomer coverage

The density extension now indexes all 22 structures, 40 deposited protomers and 160 scene keys. Experimental figures cover 21 structures and 39 protomers; 1JB0 has no released experimental data in RCSB and no usable source in the checked archives. Every protomer keeps the original molecular default and closed density panel. Native source coordinates and entry-specific map levels are retained; figures are not evidence of biological independence or a blanket density-validation pass. See the density methods and complete source/figure provenance.
