# Build inputs

Everything needed to rebuild the atlas without anything outside this repository.

| Path | Contents |
|---|---|
| `inputs/structures/<PDB>.cif.gz` | The deposited mmCIF files used, byte-for-byte (gzip); SHA-256 of each uncompressed file in `config/sources.json`. |
| `inputs/ccd/<COMP>.cif` | wwPDB chemical-component definitions of the cofactors. |
| `config/structures.json` | Entry metadata, protomers, PsaA/PsaB chains and cofactor roles. |
| `config/scenes.json` | Every scene: atoms, measured pairs (with the earlier curated annotation and value), labels and camera; `origin` is `curated` or `derived` (with its `template`). |
| `config/sources.json`, `config/release.json` | Source files and their hashes; version, date and DOI fields. |
| `provenance/` | Alignment to 1JB0 numbering, site-water audit and validation records (written by the tools). |
| `requirements.txt` | Package versions used for this build. |

```bash
pip install -r build/requirements.txt
python tools/build_atlas.py      # data/ and downloads/ from build/
python tools/write_docs.py       # README, metadata, docs and MANIFEST.json
python tools/verify_public.py    # independent check
```

To add a newly released entry: `python tools/derive_scenes.py add <PDB> <file.cif> --condition "..." --description "..."`, then rebuild. Archive new sources; do not silently replace the files a released version was built from.
