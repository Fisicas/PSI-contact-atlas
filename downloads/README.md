# Downloaded measurements and context

`all_contacts.csv` contains selected scene rows; `unique_contacts.csv` deduplicates atom pairs. Per-scene CSVs use native atom identities, distances in Å, contact IDs, classes, chemical basis and earlier annotation. `compare_matrix.csv` and `tables/` contain declared homologous comparisons and missing-reason fields. A missing cell is not proof of biological absence. Decimal display precision is not experimental accuracy.

The eight additions received an extra diagnostic N/O-neighborhood supplement; the 14 baseline scene selections were retained. Counts are not exhaustive, equivalent species inventories. [Comparison scope](../docs/COMPARISON_SCOPE.md).

`cif/` contains scene coordinate crops, with native identities. The full archived coordinates and CCD definitions are under `build/inputs/`. For local file previews, lazy `data/downloads/` scripts provide exactly the same UTF-8 bytes to native Blob downloads; HTTP links retain the canonical files. These payloads are generated after the canonical files and independently byte/hash/identity checked. No coordinate or line-ending conversion is performed.

`pymol/` reproduces the original molecular label style and measured pairs; run scripts from the repository root. The case-sensitive Mg selector is uppercase `MG`, while author chain IDs remain case-sensitive.

`validation/cofactor_geometry.csv` provides source-qualified cofactor context. `validation/cofactor_geometry.json` includes official ligand metrics/outliers and source hashes; `bond_outliers.csv` retains reported atom names/Z values. Q scores, residue inclusion and Mogul statistics are source metrics, not an atlas-wide quality ranking. `source_snapshot_check.json` records the current-vs-archived comparison date without replacing archived inputs. `diagnostic_density_samples.csv` contains 388 native diagnostic point samples with source-specific levels; ratios are display context, not cross-map quality scores or occupancy. `axial_geometry.json` records the focused native Mg/histidine measurements.

All distances refer to deposited models. [Scientific qualifications](../docs/SCIENTIFIC_REVIEW.md) remain integral to their interpretation; do not infer confirmed hydrogen bonds or species-dependent chemical geometry from flagged values.
