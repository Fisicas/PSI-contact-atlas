# Reproduction inputs and tools

Coordinate build: Python 3.12 with the pinned `requirements.txt`; run `python tools/build_atlas.py`, then `python tools/write_docs.py`, from the repository root. This re-derives the scientific tables/crops/views from archived source files and fixed configuration. Use a fresh copy when comparing rebuilds; the builder regenerates derived files under data/views and downloads/cif/contacts.

- `inputs/structures/`: exact archived deposited-coordinate snapshots; uncompressed SHA-256 in `config/sources.json`.
- `inputs/ccd/`: component atom/bond definitions.
- `inputs/validation/`: source-validation XML snapshots tied to coordinate hashes in `config/scientific_review.json`.
- `config/structures.json`, `scenes.json`: native mappings, selected atoms/pairs, cameras, metadata and scientific qualifications.
- `config/release.json`: candidate version/build date/publication state/DOI fields. An unpublished review package has no assigned release date or new DOI; the concept DOI is contextual and never a substitute for the version DOI.
- `config/citation.json`: shared author, title, ORCID, license and citation fields for every generated citation format.
- `requirements-metadata.txt`: separate pinned citation-validator dependencies.
- `config/scientific_review.json`: source-bound derived geometry, visual-screen scope, manual dispositions and source-check records.
- `docs/methods_core.md`: current Methods source, preserved by the documentation generator.
- `provenance/`: alignment/site-water, figure-source/crop records and actual validation receipts.

The metadata/geometry context is exported by `tools/build_review_context.py` and independently checked by `tools/verify_review_context.py` against the packaged coordinates and official validation XML. Reproduction does not query current online metadata or silently replace a source.

Density regeneration is a separate explicit step using `tools/density/` and an external hash-checked map/work cache. Large raw maps remain outside the web repository. Read `docs/DENSITY_VISUALIZATION_PILOT.md` and the density-tool README for processing, versions, source levels and limitations. Packaged image integrity checks do not claim bitwise regeneration across renderer versions or platforms.

Run the independent verifier, scientific-review verifier, density verifier, exact-download verifier, Python test suite and Node DOM test before preparing the final manifest. `tools/write_docs.py` reports missing test receipts as unrecorded and never invents historical validation passes. To add a new entry, use `derive_scenes.py` with explicit metadata and, where needed, a source-hash-bound `--mapping-report`; do not lower general discovery thresholds or overwrite archived inputs.
