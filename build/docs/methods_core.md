# Methods

## Scope and source snapshots

The atlas contains selected special-pair, P_A and A1 environments from 22 PDB entries / 40 deposited protomers / 160 scenes. It is separate from the structural census. All coordinate measurements are re-derived from packaged deposited mmCIF snapshots bound by uncompressed SHA-256 in build/config/sources.json. Archived CCD atom identities/bond definitions are retained. No native coordinates, component identities, water positions, occupancies or B factors are repaired or replaced.

Model 1 and native author chain/residue/atom identifiers are used. Chain IDs are case-sensitive. Alternate coordinates are selected by deposited occupancy according to the builder's deterministic source rule. Absent atoms, hydrogens and incomplete tails are not reconstructed. Scene JS positions are rounded to 0.001 Å for display; reported separations are computed from full-precision archived coordinates rather than from rounded display positions. Coordinate crops and figure-only native derivatives are documented separately.

Current-coordinate rechecks found identical atom identity/XYZ/occupancy/B records for all 22 entries (1,152,290 atoms). This separates current metadata updates from the archived coordinate provenance; it does not prove chemical geometry or experimental accuracy.

## Mapping and scene construction

PsaA/PsaB sequence alignment to 1JB0 uses global BLOSUM62 alignment, gap-open −10 and gap-extension −0.5. Functional cofactor roles are distinct from native chain IDs and deposited component names. A deposited CLA at P_A is not silently reassigned to the chlorophyll-a-prime epimer. 9HYU's pocket-bearing C-terminal PsaA chain A and N-terminal chain a are recorded separately; A/a/B case is preserved.

Curated scene atoms, selected pairs, label anchors and cameras retain the earlier reviewed selections. Homology-derived scenes use the documented curated template rule (same organism, then same cofactor components, then resolution) and source-native protein/cofactor mappings. Quinone carbonyl roles follow positional correspondence with component-specific atom names. A scene derived by rule is not relabeled as fully individually curated because it received a local-density screen.

The general automatic Mg anchor-discovery cutoff remains 3.0 Å. 9KZ9's P_A assignment uses a separate source-hash-bound mapping report: its deposited Mg–His679 NE2 separation is 3.05697 Å. Sequence anchors, distinct-cofactor identity and role completeness support the mapping exception; normal coordination geometry is not established. The gate rejects incompatible or changed source inputs rather than lowering the general cutoff.

The eight additions received a prospective diagnostic-neighborhood supplement: relevant core-subunit N/O atoms within 3.5 Å of the declared diagnostic pigment oxygens, including their residue heavy atoms. For chlorophyll environments the declared oxygens are OBD/O1A/O2A/O1D/O2D; quinones follow their component-specific carbonyl names. The 9HYU screen includes both PsaA fragments. This supplement was not retroactively applied to the 14 baseline entries. [Comparison scope](COMPARISON_SCOPE.md) records the resulting selection asymmetry.

## Distances and chemical classes

Distances are Euclidean heavy-atom separations in Å from archived native positions. 0.01 Å is display precision, not a coordinate uncertainty. No donor-H angles, protonation states, hydrogen positions, occupancies, redox states or energies are established.

The classifier applies these rules in order: Mg involved → Mg–ligand separation; same residue → intramolecular; C or S involved → C/S context; separation beyond 3.5 Å → longer context; water involved → water-involved candidate; two oxygen atoms that cannot carry donor hydrogens under the declared heavy-atom basis → acceptor pair; otherwise → polar candidate. Carboxylate and histidine states remain qualified because protonation/tautomerism is unknown. The CSV chemical-basis field is part of the interpretation. A short separation or dashed line is not a confirmed hydrogen bond.

The graph uses source CCD cofactor bonds plus declared protein/peptide connectivity. Source geometry flags do not trigger coordinate editing. Quantitative intraligand chemistry is specifically qualified for 1JB0/7DKZ/9KZ9 A1 and other reported outliers. Source metrics are contextual evidence, not an atlas-wide quality ranking.

## Water and homologous comparisons

Each scene retains its declared water-display rule and earlier mapped content. The common reference-site water is the nearest deposited water oxygen within 3 Å of the aligned 1JB0 HOH5011 position, using the declared chlorophyll-core alignment. This is a positional assignment, not proof of a conserved molecule. Water display selection and the 3.5 Å analytical proximity screen are separate. Missing deposited water is not proof of biological absence.

The comparison matrix evaluates declared homologous atom pairs across deposited protomers, retaining native identifiers and explicit missing reasons. Scene pair counts are not exhaustive or equivalent inventories, particularly because the eight additions received the extra neighborhood supplement. Deposited protomers, related reconstructions and template-derived models are not independent biological replicates. Method/resolution, sample preparation, source ancestry and ligand-geometry qualifications must accompany interpretation of small distance changes.

## Optional density figures

The molecular view and original web label layout remain the default. Optional panels start closed and create/load images only after opening. Unmasked sections and fixed mesh previews cover every deposited protomer; figures exist for 39 protomers / 156 scenes. 1JB0 has explicit unavailable-experimental-data messaging. There are 254 sections and 208 meshes.

Cryo-EM maps retain deposited voxel values and native sampling; no EM smoothing, sharpening, normalization, fitting or refinement is applied. Values and author contour levels are source-specific and not standardized across entries. Positions outside physical EM source extents are blank rather than periodically wrapped.

For 5OY0 and 7DKZ, deposited weighted main/difference coefficients are transformed with Gemmi at FFT sample rate 3. Each map is independently mean-subtracted and scaled by its own full-cell standard deviation. Crops are not renormalized. Main contours are 1.0/1.5 full-cell sigma; difference contours are ±3 sigma. These are model-phased maps, not omit maps or a new refinement.

Sections use a ±7 Å field, 0.14 Å trilinear raster sampling and source-native figure coordinates. Oversampling adds no experimental resolution. Model atoms within ±1 Å of the plane are projected onto the thin map section; a projected marker outside a contour is not proof of absent 3D density at the atom. Carbonyl-centered sections supplement highly nonplanar quinones where provided.

Meshes use a model-centered 2 Å display carve and 4 Å buffer, with PyMOL map normalization disabled. The carve is not independent model support. The original intended Mg spheres are restored by a case-correct `elem MG` selector; camera/atom coordinates, contour values and molecular label layout are unchanged by that display correction.

9AU4's author level 0.0149 raw units floods its sections. Both author-level views and separately labeled exploratory mean+3 full-grid SD views (3.0006282866 raw units) are retained. The latter is a display choice, not normalization, a local sigma/support criterion, an uncertainty or a quality score.

The scoped visual screen now covers all 39 protomers with available experimental data: all 462 packaged figures / 85 sheets, plus eight targeted native planes. 1JB0 remains unavailable. This closes coverage, not all-atom fit or chemical validation. No half-map validation, local FSC, all-atom density adjudication, occupancy assignment or coordinate-uncertainty analysis was performed. [Scientific review](SCIENTIFIC_REVIEW.md) and [source-specific density methods](DENSITY_VISUALIZATION_PILOT.md) retain these limits.

## Reproducibility and display

Protein/cofactor display alignment to 1JB0 and the recorded orthographic camera are viewing conventions; they do not alter measured native coordinates or imply evolutionary/model ancestry. Original molecular label positioning is preserved. Source data, diagnostic-neighborhood scope, cofactor-role gates and scientific qualifications are part of the build inputs.

The offline coordinate build, independent verifier, source-review verifier and corruption tests are separate from optional map regeneration and browser/renderer checks. A recorded technical pass does not clear known chemical-geometry concerns. [Validation receipts](VALIDATION.md), [build instructions](../build/README.md) and [download context](../downloads/README.md) state the actual checks and requirements. No candidate publication or DOI is asserted.
