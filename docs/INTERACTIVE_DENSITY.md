# Interactive experimental-density views

Version 1.1.0 includes 156 interactive scenes across 21 structures and 39 deposited protomers. All 208 mesh thumbnails open the matching scene and contour preset. The four 1JB0 scenes report unavailable experimental data and do not synthesize a map. The collection itself contains 22 structures, 40 protomers and 160 molecular scenes.

## Controls and atom inspection

Open an atlas scene, expand **Density views · optional**, choose **3D mesh previews**, then select a thumbnail or **Inspect in 3D**. Each preview also retains a direct **Static PNG** link. Images and density options start closed; maps and the pinned local viewer load only in the separate density page. File and HTTP previews work without a CDN or personal browser profile. A missing WebGL/viewer dependency leaves static links and return navigation available.

Drag to rotate, choose **Hand / pan** to translate, and use the wheel to zoom. Reset restores the initial camera; Fit whole scene frames the native crop. Controls expose the exact selected preset, source contour, opacity, primary/difference density, wire mesh or transparent surface, optional 2 Å display carve and classified contact guides (off initially). Save PNG exports the current view. The processing panel provides the native scene CIF and original primary CCP4 crop.

**Inspect an atom** first lists endpoints of existing polar contacts whose chemical basis is donor–acceptor compatible, then additional water-contact endpoints, then every remaining atom. Atoms are deduplicated. Selecting an atom displays native identity, XYZ in Å, deposited occupancy/B factor, nearest-grid value and clickable compatible partner atoms. Contact rows remain separately selectable. This ordering does not create new assignments or establish hydrogen positions, donor angles, protonation, occupancy or actual hydrogen bonds. Acceptor–acceptor contacts retain their explicit original class and remain in the atlas.

## Native coordinates, grids and units

The interactive payload contains full-precision archived deposited coordinates for the unchanged scene atom selection; no missing atoms are reconstructed. Explicit original scene edges are used as single-stick display bonds, including coordination edges. They are not a chemical bond-order model. Original default atlas labels/drawing and canonical measured contact tables are unchanged.

Each payload embeds exact bytes of the prepared native CCP4 crop. Axis/start/origin/cell transforms and voxel values are independently checked. No browser normalization, negation, smoothing, sharpening, resampling, fitting or refinement is applied. Browser triangulation and camera differ from the PyMOL still, so pixel identity is not expected. Crops have a finite 5 Å bounding margin around the selected scene atoms; the optional 2 Å carve is a display mask around diagnostic focus atoms, not a new map. Full cofactor tails can extend beyond the focused density display.

EM contours retain deposited raw units. X-ray main and difference maps were independently normalized over the full unit cell upstream, before cropping; contours use full-cell σ. Main source level is 1 σ, while difference contours are +3 σ (green) and −3 σ (red). These are model-phased weighted maps, not omit maps. 9AU4's author level 0.0149 raw units and explicit mean + 3 full-grid SD alternative remain distinct; the latter is exploratory, not a support/occupancy criterion. Every thumbnail preserves its own contour choice, including higher-level water previews.

Existing source-model geometry, weak-water, preparation, split-chain and contour qualifications remain visible. Positive density does not validate unusual intraligand chemistry or establish a redox interpretation. See [scientific review](SCIENTIFIC_REVIEW.md) and [density sources/processing](DENSITY_VISUALIZATION_PILOT.md).

## Reproduction and checks

`tools/build_interactive_density.py --repo <fresh build copy> --work-dir <density work cache>` packages the prepared native crops and native scene CIFs after source-hash checks. The work cache also contains the multi-GB deposited maps/retrieval records; it is intentionally outside the website. The builder refuses an existing `data/density_interactive` output directory: use a fresh copy with generated interactive outputs omitted. Do not overwrite raw maps or earlier review packages. The pinned 3Dmol.js 2.5.5 package and BSD-3-Clause license are included under `vendor/3dmol`; hashes are recorded in provenance.

Run `python tools/verify_interactive_density.py` and the ordinary numerical/source/metadata/density/download checks. This independent check covers all 156 payloads, 22,379 native scene atom occurrences, 172 map crops, 8,664,627 voxels and 208 preset/fallback bindings. CI includes it before and after coordinate rebuilding. The clean interactive rebuild receipt records byte identity of generated outputs using the external hash-bound cache.

The isolated local Chrome browser review loaded all 156 available scenes over HTTP and local files (312 loads), checked exact voxel-byte hashes, physical transforms/sample values and candidate ordering, and exercised every contour preset. Seven representative scenes per protocol exercised rotation, hand pan, zoom/reset, atom picking/partners, contact selection and display controls; HTTP representatives also exercised PNG/map/CIF downloads and narrow/light/dark layouts. Thumbnail clicks were exercised for representative EM, X-ray, split-chain and alternative-contour entries. All 160 panel links were independently checked in the DOM. Follow-up checks cover lazy loading, deliberate viewer failure/static fallback and invalid routes.

These checks use isolated Chrome with SwiftShader software WebGL. They do not establish behavior on every hardware GPU/browser, a live GitHub deployment, all-atom map fit or scientific validation of every feature.

Optional reproducible isolated-browser driver: `python tools/browser/review_interactive_density.py --all --repo <repository> --output <new review folder> [--runtime-dir <existing Playwright package directory>]`. It uses an installed Chrome and software WebGL, permits only local requests and writes screenshots/download receipts outside the repository. It does not install or upgrade browser dependencies.
