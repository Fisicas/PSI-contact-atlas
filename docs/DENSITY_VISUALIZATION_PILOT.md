# Optional density visualizations — all deposited protomers

On **any of the 160 scene pages**, expand **Density views · optional**, then choose **Unmasked sections** or **3D mesh previews**. Controls cover all **22 structures and 40 deposited protomers**, including the older cyanobacterial entries and protomers 2 and 3. Each panel starts closed, density images are created only when opened, and the original molecular viewer/labels remain the default. Select a mesh image to open its exact scene/contour in the separate [interactive density viewer](INTERACTIVE_DENSITY.md). Direct Static PNG links retain the fixed images as a fallback. The original molecular controls continue to apply to the original molecular scene; density controls act only in the separate viewer.

Experimental figures are available for **21 structures and 39 protomers**: 254 unmasked sections and 208 fixed mesh previews, including the explicitly labeled 9AU4 contour alternatives. **1JB0** is marked unavailable because [RCSB](https://www.rcsb.org/structure/1JB0) lists `has_released_experimental_data = N`; the standard wwPDB structure-factor, PDBe map-MTZ and RCSB validation-coefficient URLs returned 404. Its four scene pages retain density controls with an explanation. No coordinate-derived simulated map is substituted for experimental data.

## Sources, units and contour choices

| Entry | Source | Processing/level |
|---|---|---|
| 1JB0 | No released experimental data | No experimental density reconstructed. |
| 5OY0 | Deposited weighted coefficients | Deposited weighted coefficients; independent full-cell mean/SD normalization of main and difference maps. No crop renormalization or re-refinement; model-phased, not omit maps. |
| 6KMW | EMD-0726 | Deposited primary EM map; author contour 0.06 raw units. No normalization, smoothing or sharpening. |
| 6KMX | EMD-0727 | Deposited primary EM map; author contour 0.06 raw units. No normalization, smoothing or sharpening. |
| 7COY | EMD-30420 | Deposited primary EM map; author contour 0.00637 raw units. No normalization, smoothing or sharpening. |
| 9AU4 | EMD-43843 | Deposited primary EM map; author contour 0.0149 raw units. No normalization, smoothing or sharpening. |
| 9EYS | EMD-50063 | Deposited primary EM map; author contour 0.054 raw units. No normalization, smoothing or sharpening. |
| 9I9L | EMD-52762 | Deposited primary EM map; author contour 0.13 raw units. No normalization, smoothing or sharpening. |
| 9QFP | EMD-53120 | Deposited primary EM map; author contour 0.08 raw units. No normalization, smoothing or sharpening. |
| 9S6P | EMD-54627 | Deposited primary EM map; author contour 0.2 raw units. No normalization, smoothing or sharpening. |
| 9SK3 | EMD-54956 | Deposited primary EM map; author contour 0.1 raw units. No normalization, smoothing or sharpening. |
| 9YL7 | EMD-73077 | Deposited primary EM map; author contour 0.0353 raw units. No normalization, smoothing or sharpening. |
| 9OY9 | EMD-71005 | Deposited primary EM map; author contour 4.4 raw units. No normalization, smoothing or sharpening. |
| 9OZ3 | EMD-71048 | Deposited primary EM map; author contour 0.065 raw units. No normalization, smoothing or sharpening. |
| 9SE6 | EMD-54803 | Deposited primary EM map; author contour 0.04 raw units. No normalization, smoothing or sharpening. |
| 9LUT | EMD-63404 | Deposited primary EM map; author contour 0.07 raw units. No normalization, smoothing or sharpening. |
| 8WEY | EMD-37480 | Deposited primary EM map; author contour 0.016 raw units. No normalization, smoothing or sharpening. |
| 7DKZ | Deposited weighted coefficients | Deposited weighted coefficients; independent full-cell mean/SD normalization of main and difference maps. No crop renormalization or re-refinement; model-phased, not omit maps. |
| 9UH3 | EMD-64153 | Deposited primary EM map; author contour 0.065 raw units. No normalization, smoothing or sharpening. |
| 9HYU | EMD-52518 | Deposited primary EM map; author contour 8 raw units. No normalization, smoothing or sharpening. |
| 9KZ9 | EMD-62656 | Deposited primary EM map; author contour 0.032 raw units. No normalization, smoothing or sharpening. |
| 8XLS | EMD-38457 | Deposited primary EM map; author contour 0.012 raw units. No normalization, smoothing or sharpening. |

EM maps are the full deposited primary files, not adaptively downsampled or quantized streaming data. Voxel values and native grid sampling are retained without normalization, smoothing, sharpening or refinement. Author-recommended contours are retained in raw map units; they are not a common quality scale. Sections show 0.8/1.0/1.2 times each entry's author contour. Higher water meshes use 1.2 times that contour.

For **9AU4**, current EMDB metadata describe the primary source as unsharpened and unmasked. The author level has no stated sigma unit or demonstrated conversion to the alternative display. The author contour 0.0149 is about 0.015 times the full-grid standard deviation and floods the local view. Its author-level figures are retained. Additional figures explicitly use raw-map mean + 3 full-grid SD (approximately 3.00063 raw units), with sensitivity levels printed on the images/captions. This is an exploratory display choice, not normalization, a model-support pass/fail criterion, a quality ranking or an uncertainty.

For **5OY0 and 7DKZ**, deposited FWT/PHWT and DELFWT/DELPHWT coefficients are transformed by Gemmi at FFT sample rate 3. Main and difference maps are independently mean-subtracted and divided by their own full-cell standard deviation once. Crops are not renormalized. Main sections use 1.0/1.5 full-cell σ and difference contours ±3 σ; main meshes use 1.0 σ with higher water views at 1.5 σ. These are model-phased weighted maps, not omit maps or a new refinement. Global σ is not coordinate uncertainty.

## Coordinates and geometry

Full-precision archived native coordinates are used for these figure derivatives; original atlas scene JSON/CIF files and pair tables are unchanged. For every scene, the full-precision atoms also match the current deposited model. The separate 0.001 Å scene-serialization rounding bound is recorded rather than mistaken for a coordinate-frame change. Native-coordinate figure CIFs reproduce the sampled positions exactly. No atoms, water molecules, missing tails, alternate positions, occupancies or B factors are reconstructed or corrected.

Unmasked sections span ±7 Å with 0.14 Å trilinear sampling. Oversampling adds no experimental resolution. Only model atoms within ±1 Å of a plane are drawn; density itself is not masked by that slab. Pixels outside an EM source's actual physical extent are blank rather than periodically wrapped. Crystallographic maps are periodic. Section plane centers/bases, target atom IDs and source-coverage fractions are archived.

P_A ester views are available even when no reference-site water is assigned. A water section is added only for the actual assigned native water in that protomer. Missing assignment is not biological absence. Quinone carbonyl labels come from each deposited component's CCD double-bond definitions, including components whose carbonyls are named O1/O2 rather than O1/O4. Additional carbonyl-centered planes are shown where an oxygen lies more than 0.75 Å outside the C1/C2/C3 section.

Meshes use a **2 Å model-centered display carve** with a 4 Å buffer; that carve is not independent map support. PyMOL CCP4 normalization is disabled. Crops retain the native frame and 5 Å scene margin. EM crop serialization is checked within 10⁻⁵ raw map units; crystal-map interpolation within 10⁻⁴ full-cell σ, accounting for CCP4's float32 unit-cell header precision. Actual errors are recorded. Unmasked sections are sampled directly from the original full grids, not these crops.

## Review limits

Rendering density for every protomer is not a scientific approval of every model or contact. Prior **7DKZ quinone-geometry and site-water flags**, **8WEY ring-bond outliers**, preparation/mapping caveats and nonindependence of related/symmetrized models remain. No occupancy, redox-state or confirmed hydrogen-bond assignment is inferred. The current scoped screen covers all 39 available protomers / 462 packaged figures in 85 sheets, plus eight targeted native planes. 1JB0 remains unavailable. New baseline qualifications include local 7COY oxygen features, weak modeled site waters in 9S6P/9SK3 and long 5OY0 protomer 3 axial distances; they remain explicit rather than being cleared by broad envelopes. The earlier four-entry screen remains historical provenance. See [Scientific review](SCIENTIFIC_REVIEW.md) for the retained 9KZ9 and baseline 1JB0 geometry qualifications as well as the other dispositions.

Complete source hashes, levels, coordinate-frame checks, processing, native atom samples, crop checks and figure hashes are recorded in `build/provenance/density_all_protomers_v01.json` and the neighboring `density_all_protomers_20261120_v01` audit folder. Raw maps remain outside the web repository. The published atlas is unchanged.

## Reproduction and display correction

Use the explicit cache/work/output paths in [the portable density recipe](../tools/density/README.md). Source manifests and small metadata snapshots are packaged; the large hash-checked maps remain outside the web repository. The preparation recipe was exercised in a fresh work directory for 7DKZ, 9KZ9 and the unavailable 1JB0 case; all 208 mesh previews were regenerated using the portable renderer. PyMOL `ignore_case=0` requires `elem MG`, so the PML selector was corrected to display Mg spheres. All mesh reports check intended Mg visibility, disabled map normalization and zero before/after coordinate change. The 254 unmasked sections are byte-identical to the prior development images. This is a display correction, not coordinate refinement.
