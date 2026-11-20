"""Generate current release-candidate documentation without inventing validation receipts."""
import hashlib,json,re,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TITLE='PSI Contact Atlas'
PAGES_URL='https://fisicas.github.io/PSI-contact-atlas/'
REPO_URL='https://github.com/Fisicas/PSI-contact-atlas'
def read(p,default=None):return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default
def write(rel,text):(ROOT/rel).write_text(text,encoding='utf-8',newline='\n')
def load_js(path):
    text=path.read_text(encoding='utf-8');return json.loads(text[text.index('=',text.index('PSI_ATLAS'))+1:].strip().rstrip(';'))
def manifest():
    skip={'.git','__pycache__','cif_cache'}
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and not set(p.relative_to(ROOT).parts)&skip and p.relative_to(ROOT).as_posix()!='MANIFEST.json' and not (p.relative_to(ROOT).as_posix().startswith('build/provenance/verify_') and p.suffix=='.json'))
    value={p.relative_to(ROOT).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files}
    write('MANIFEST.json',json.dumps(value,indent=1)+'\n');return len(value)

def main():
    A=load_js(ROOT/'data/atlas.js');R=read(ROOT/'build/config/release.json');c=A['counts'];cfg=read(ROOT/'build/config/scientific_review.json')
    date=R.get('build_date') or R.get('release_date');version=R['version'];released=R.get('status')=='published'
    with (ROOT/'downloads/compare_matrix.csv').open(encoding='utf-8',newline='') as f: comparison_rows=list(csv.DictReader(f))
    numeric_comparisons=sum(bool(row['distance_A'].strip()) for row in comparison_rows)
    status='Published release' if released else 'UNPUBLISHED RELEASE REVIEW'
    lifecycle=(('Release date '+R['release_date']+'. See the [versioned GitHub release]('+R['release_url']+') for citation and archive details.') if released else 'Prepared for review; no release date or new version DOI is assigned. Published v1.0.0 remains unchanged.')
    doi = (R.get('registered_version_doi') or R.get('version_doi')) if released else None
    doi_line = f'**Cite v{version}** · [DOI {doi}](https://doi.org/{doi})\n\n' if doi else ''
    readme=f'''<p><img src="media/branding/icon-192.png" width="48" height="48" alt="PSI Contact Atlas chlorin-ring icon"></p>

# PSI Contact Atlas

{doi_line}<p><a href="{PAGES_URL}"><img src="media/branding/social-preview.png" width="960" alt="PSI Contact Atlas: P700 and A1 quinone environments, with a deposited chlorophyll contact network"></a></p>

**{status} · {version}.** {lifecycle}

## What changed since v1.0.0

- **Eight added structures:** 9SE6, 9LUT, 8WEY, 7DKZ, 9UH3, 9HYU, 9KZ9 and 8XLS. Coverage expands from **14 to 22 structures, 32 to 40 protomers and 128 to 160 scenes**.
- **New optional density views:** unmasked sections and clickable mesh previews open interactive native-atom/density views for 39 protomers (156 scenes), with static PNG fallbacks and explicit 1JB0 unavailability. Density options start closed; the original molecule/label view remains the default.
- **New source and scientific checks:** new-entry mappings/preparation provenance, all-entry cofactor-geometry checks and a scoped local-density feature screen, with downloadable diagnostic samples and retained source-model qualifications.
- **Presentation and reliability:** concise notices/collapsed provenance, exact local downloads, navigation/export fixes, a wrapping four-GIF README gallery and the selected icon/social artwork.

[Full release notes and added-structure table](docs/RELEASE_NOTES_1.1.0.md) · [Scientific/comparison scope](docs/COMPARISON_SCOPE.md). Mesh previews now open the exact scene and contour in the [interactive density viewer](docs/INTERACTIVE_DENSITY.md); static images remain available.

Interactive deposited heavy-atom environments around the photosystem I special pair (P700 or its source-specific counterpart), P<sub>A</sub>, and A₁ quinones. Rotate scenes, compare homologous atom pairs, inspect optional local-density figures and download coordinate crops, CSVs and PyMOL scripts.

| Coverage | Version {version} {'release' if released else 'review package'} |
|---|---:|
| Structures | {c['structures']} |
| Deposited protomers | {c['protomers']} |
| Scenes | {c['views']} |
| Scene contact rows | {c['contacts']:,} |
| Unique atom pairs | {c['unique_contacts']} |
| Numeric homologous comparison values | {numeric_comparisons:,} |
| Comparison cells, including blanks | {len(comparison_rows):,} |
| Interactive density scenes | 156 |
| Protomers with experimental-density figures | 39 |
| Scenes with experimental-density figures | 156 |

Open `index.html` locally or serve this directory. The molecular view and original label layout remain the default. Optional unmasked sections and mesh previews start closed and load on demand. All 208 mesh thumbnails open an interactive density view with rotation, Hand / pan, contour controls and candidate-first atom inspection; direct Static PNG links remain available. Interactive maps load only on the separate density page. 1JB0 retains coordinate views with explicit unavailable-experimental-data messaging. There are 254 section and 208 mesh images; figures are display aids, not automatic model validation.

## Molecular previews

Four examples from the atlas. Each animation appears on its own line so the molecules and captions fit the reading column, including on narrow screens. Select a molecule to open its interactive scene.

<p><a href="{PAGES_URL}#/view/1JB0_prot1_P_A"><img src="media/spin_1JB0_prot1_P_A.gif" width="720" alt="1JB0 P_A chlorophyll and its protein/water network, rotating"></a></p>

**1JB0 · P<sub>A</sub> network** — *S. elongatus*, X-ray 2.5 Å. [Open scene]({PAGES_URL}#/view/1JB0_prot1_P_A).

<p><a href="{PAGES_URL}#/view/7COY_prot1_special_pair"><img src="media/spin_7COY_prot1_special_pair.gif" width="720" alt="7COY chlorophyll d special-pair environment, rotating"></a></p>

**7COY · special pair** — *A. marina*, Chl *d* / P740, cryo-EM 2.5 Å. [Open scene]({PAGES_URL}#/view/7COY_prot1_special_pair).

<p><a href="{PAGES_URL}#/view/9YL7_prot1_A1A"><img src="media/spin_9YL7_prot1_A1A.gif" width="720" alt="9YL7 A1A plastoquinone-9 pocket, rotating"></a></p>

**9YL7 · A<sub>1A</sub>** — PQ-9 (30 of 55 heavy atoms deposited), cryo-EM 1.68 Å. [Open scene]({PAGES_URL}#/view/9YL7_prot1_A1A).

<p><a href="{PAGES_URL}#/view/9AU4_prot1_A1B"><img src="media/spin_9AU4_prot1_A1B.gif" width="720" alt="9AU4 A1B DMPBQ pocket, rotating"></a></p>

**9AU4 · A<sub>1B</sub>** — DMPBQ in the MenB variant, cryo-EM 2.03 Å. [Open scene]({PAGES_URL}#/view/9AU4_prot1_A1B).

Each loop is drawn by the atlas viewer from deposited heavy atoms: gray C, blue N, red O, green Mg and yellow S; thicker sticks mark the cofactor. Dashed guides show measured separations in Å: dark polar candidates, teal water contacts, green Mg–ligand contacts, mauve two-acceptor O···O contacts and gray longer context. A short separation is not proof of a hydrogen bond. The animations are illustrative baseline scenes; use the interactive atlas and source-specific qualifications for the current 22-structure / 40-protomer comparison.

## Scientific interpretation

Every measurement is a Euclidean separation between named atoms in the archived deposited model, in Å. Two decimal places are display precision, not a distance uncertainty. Hydrogen positions, donor angles, protonation, occupancy and redox state are not established by these measurements.

Source-specific qualifications are integral to this dataset. In particular, 1JB0/7DKZ/9KZ9 quinone chemical geometry, the 9KZ9 axial Mg separation, weak site waters in 7DKZ/9S6P/9SK3, local oxygen features in 7COY, long 5OY0 protomer 3 axial distances and the 9AU4 contour exception remain explicit. Positive density does not clear intraligand chemistry. [Scientific review](docs/SCIENTIFIC_REVIEW.md) · [Per-cofactor context](downloads/validation/cofactor_geometry.csv) · [Methods](docs/METHODS.md).

The eight additions received an extra diagnostic N/O-neighborhood supplement; the 14 baseline scene selections were retained. Pair counts are not exhaustive cross-species inventories. Deposited protomers and related reconstructions are not independent biological replicates. [Comparison scope](docs/COMPARISON_SCOPE.md). The structural census remains a separate project.

## Sources and provenance

Archived PDB coordinates and CCD definitions are included under `build/inputs`, with source hashes/revisions. Current-coordinate rechecks found identical identity/XYZ/occupancy/B records for all 22 entries (1,152,290 atoms). Current source-validation snapshots and source-bound review context are packaged separately from the atomic inputs. Neither current metadata revisions nor branding caused coordinate replacement.

The eight additions are 9SE6, 9LUT, 8WEY, 7DKZ, 9UH3, 9HYU, 9KZ9 and 8XLS. Preparation, split-chain, source-model ancestry and unresolved-condition notes are retained. 9OY9/9OZ3 cite the linked bioRxiv preprint; their monomer/trimer description follows the primary study while documenting the deposited title discrepancy.

## Rebuild and verify

Use Python 3.12 with the pinned `build/requirements.txt`; citation checks also use `build/requirements-metadata.txt`. Install dependencies into an appropriate project environment rather than upgrading an established shared environment.

```text
python tools/build_atlas.py
python tools/write_docs.py
python tools/verify_public.py
python tools/verify_review_context.py
python tools/verify_scientific_closure.py
python tools/verify_release_metadata.py
python tools/verify_density_views.py
python tools/verify_interactive_density.py
python tools/verify_download_payloads.py
python tools/verify_branding.py
python tools/verify_readme_counts.py
python -m unittest discover -s tests -v
node tests/test_density_options_all.cjs . /path/outside/repository/report.json
```

The coordinate build is offline from packaged inputs. Full density regeneration additionally requires the hash-checked external map cache and the specified scientific/PyMOL environments; multi-GB raw maps are not part of the website. [Build instructions](build/README.md) · [Density methods](docs/DENSITY_VISUALIZATION_PILOT.md) · [Validation receipts and limits](docs/VALIDATION.md) · [Release candidate review](docs/RELEASE_CANDIDATE.md) · [Browser review](docs/BROWSER_REVIEW.md).

## Citation, licensing and release status

{lifecycle} Citation metadata are synchronized in `CITATION.cff`, `.zenodo.json`, `CITATION.bib`, `CITATION.ris` and `CITATION.csl.json`. Cite the individual PDB entries and primary papers as well. [Citation scope and DOI handling](docs/CITATION.md).

Code: [MIT](LICENSE). Data/figures/documentation: [CC BY 4.0](LICENSE-DATA.md). Unmodified wwPDB source files retain their source terms. [Published website]({PAGES_URL}) · [Repository]({REPO_URL}).
'''
    write('README.md',readme)
    import build_release_metadata
    build_release_metadata.main(ROOT)
    write('CHANGELOG.md',f'''# Changelog

## {version} — {'released '+R['release_date'] if released else 'unpublished review package prepared '+date}

- Added eight plant/algal PSI entries: 22 structures, 40 deposited protomers, 160 scenes. Archived coordinates and original molecular labels are preserved.
- Added optional closed-by-default unmasked sections and 208 clickable density mesh previews. Interactive density covers 39 protomers / 156 scenes, with rotation/pan/zoom, contour and atom inspection, compatible polar/water candidate atoms first, and static PNG fallbacks. 1JB0 remains explicitly unavailable; 9AU4 contour choices remain distinct.
- Completed the scoped density feature screen across all 39 available-data protomers and source-bound global geometry review; the user accepted retention with the documented qualifications. Retained chemical-geometry and preparation qualifications, including newly identified 9KZ9 quinone concerns and baseline 1JB0 context.
- Corrected 9OY9/9OZ3 primary-citation/assembly metadata without changing their coordinates.
- Documented the eight-entry-only neighborhood supplement and comparison selection asymmetry.
- Corrected case-sensitive PyMOL Mg sphere selection; atom coordinates, contact values and molecular web labels are unchanged.
- Fixed scene/preview callback cleanup, wrapped narrow-export captions, and preserved exact local-preview data downloads. Molecular drawing and label routines remain unchanged.
- Removed obsolete unreviewed/pilot notices, consolidated site-specific cautions and resolved preparation/model-lineage metadata from primary papers. Added the 7DKZ bent-quinone curator observation and interpretation-in-progress evidence page.
- Prepared the approved chlorin icon and exact-native social preview, reproducibility tooling and validation receipts for review. {"Release metadata refer to the published version." if released else "No publication occurred during review-package preparation."}

## 1.0.0 — 2026-11-17

Previous published baseline: 14 structures, 32 deposited protomers, 128 scenes. Its publication record is unchanged. See the Git history and release archive for the original complete changelog.
''')
    write('docs/METHODS.md',(ROOT/'build/docs/methods_core.md').read_text(encoding='utf-8'))
    receipt=read(ROOT/'build/provenance/release_candidate_checks.json',dict(checks={}))
    lines=[]
    names=['independent_atlas','scientific_review_context','scientific_closure','release_metadata','release_notices','density_assets','density_DOM_contract','unit_tests','clean_rebuild','pymol_exports','download_payloads','browser_review','published_preservation','readme_media_layout','documentation_preservation','final_diff_review','social_branding','interactive_density_source','interactive_density_browser','interactive_density_followup','interactive_density_rebuild','readme_counts']
    for name in names:
        check=receipt.get('checks',{}).get(name,{})
        lines.append(f'| {name} | {check.get("status","NOT YET RECORDED")} | {check.get("summary","No receipt recorded; no pass is inferred.")} |')
    write('docs/VALIDATION.md',f'''# Validation and limits — {version}

Prepared {date}; {status.lower()}. The table is generated from recorded receipts in `build/provenance/release_candidate_checks.json`. A missing receipt is not a pass. Local checks do not claim that future GitHub Actions or live publication have succeeded.

| Check | Recorded status | Evidence summary |
|---|---|---|
'''+ '\n'.join(lines)+'''

The coordinate/geometry scientific screen and its retained limitations are documented in [SCIENTIFIC_REVIEW.md](SCIENTIFIC_REVIEW.md). Local density review now covers all 39 protomers with available experimental data: 462 packaged figures / 85 review sheets, plus eight targeted native planes. This is a scoped local-feature screen, not all-atom fit validation; 1JB0 remains unavailable. Generated figures, positive contours and source validation metrics are distinct evidence.

Independent numerical verification checks native scene atoms/distances, crops, comparison cells and public-file hashes. Source-review verification separately checks coordinate/validation hashes, intraligand distances, planarity, official XML records and retained critical warnings. Density verification checks coverage, native protomer asset identities, source/frame/crop provenance, image hashes and PNG integrity. Interactive-density verification independently checks 22,379 native scene atom occurrences, 172 exact CCP4 crops (8,664,627 voxels), 208 preset/fallback bindings and the pinned viewer. The browser receipt separately records 312 file/HTTP scene loads, map transforms, candidate ordering and representative interactions. The Node test checks the optional-panel DOM contract; it does not establish real browser rendering, downloads or interaction unless a browser receipt is separately recorded.

Clean coordinate rebuilding uses archived inputs and fixed configuration. Density image regeneration needs external hash-checked maps, the declared recipe and the scientific/PyMOL environments. Image hashes verify the packaged derivatives; bitwise image identity across renderer/platform versions is not promised. Browser and PyMOL checks state their actual scope and environment in the receipts.

No test establishes hydrogen bonds, occupancy, protonation, redox state, biological independence, or a general uncertainty for a modeled distance. Known geometry qualifications remain after technical checks pass. No publication or DOI update is implied by these records.
''')
    write('downloads/README.md','''# Downloaded measurements and context

`all_contacts.csv` contains selected scene rows; `unique_contacts.csv` deduplicates atom pairs. Per-scene CSVs use native atom identities, distances in Å, contact IDs, classes, chemical basis and earlier annotation. `compare_matrix.csv` and `tables/` contain declared homologous comparisons and missing-reason fields. A missing cell is not proof of biological absence. Decimal display precision is not experimental accuracy.

The eight additions received an extra diagnostic N/O-neighborhood supplement; the 14 baseline scene selections were retained. Counts are not exhaustive, equivalent species inventories. [Comparison scope](../docs/COMPARISON_SCOPE.md).

`cif/` contains scene coordinate crops, with native identities. The full archived coordinates and CCD definitions are under `build/inputs/`. For local file previews, lazy `data/downloads/` scripts provide exactly the same UTF-8 bytes to native Blob downloads; HTTP links retain the canonical files. These payloads are generated after the canonical files and independently byte/hash/identity checked. No coordinate or line-ending conversion is performed.

`pymol/` reproduces the original molecular label style and measured pairs; run scripts from the repository root. The case-sensitive Mg selector is uppercase `MG`, while author chain IDs remain case-sensitive.

`validation/cofactor_geometry.csv` provides source-qualified cofactor context. `validation/cofactor_geometry.json` includes official ligand metrics/outliers and source hashes; `bond_outliers.csv` retains reported atom names/Z values. Q scores, residue inclusion and Mogul statistics are source metrics, not an atlas-wide quality ranking. `source_snapshot_check.json` records the current-vs-archived comparison date without replacing archived inputs. `diagnostic_density_samples.csv` contains 388 native diagnostic point samples with source-specific levels; ratios are display context, not cross-map quality scores or occupancy. `axial_geometry.json` records the focused native Mg/histidine measurements.

All distances refer to deposited models. [Scientific qualifications](../docs/SCIENTIFIC_REVIEW.md) remain integral to their interpretation; do not infer confirmed hydrogen bonds or species-dependent chemical geometry from flagged values.
''')
    write('build/README.md','''# Reproduction inputs and tools

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
''')
    text=(ROOT/'index.html').read_text(encoding='utf-8')
    title=f'PSI Contact Atlas — {version}'+('' if released else ' unpublished release review')
    text=re.sub(r'<title>.*?</title>',f'<title>{title}</title>',text,count=1)
    text=re.sub(r'\?v=[^"\s]+',f'?v={version}',text)
    badge=version if released else version+' · UNPUBLISHED'
    text=re.sub(r'<span class="status"[^>]*>.*?</span>',f'<span class="status" title="{status}">{badge}</span>',text,count=1)
    banner='' if released else f'<div role="note" style="padding:12px 20px;background:#533b12;color:#fff3ce;font-weight:600">UNPUBLISHED RELEASE REVIEW — version {version}; {c["structures"]} structures, {c["protomers"]} deposited protomers. Scientific retention dispositions accepted; qualifications retained. Published v1.0.0 is unchanged.</div>'
    text=re.sub(r'<div role="note" style="[^"]+">.*?</div>',banner,text,count=1)
    foot=('Released '+version+'.' if released else 'Unpublished release review. No publication or new DOI.')+' Deposited heavy-atom separations; 0.01 Å is display precision. <a href="docs/SCIENTIFIC_REVIEW.md">Scientific review</a> · <a href="docs/COMPARISON_SCOPE.md">Comparison scope</a> · <a href="docs/CITATION.md">Citation</a> · <a href="docs/VALIDATION.md">Validation receipts</a>.'
    text=re.sub(r'<footer class="site-foot">.*?</footer>','<footer class="site-foot"><div class="wrap">'+foot+'</div></footer>',text,count=1,flags=re.S)
    write('index.html',text)
    density_path=ROOT/'density.html'
    if density_path.exists():
        density_text=density_path.read_text(encoding='utf-8')
        density_text=re.sub(r'<p class="eyebrow">.*?</p>', '<p class="eyebrow">PSI CONTACT ATLAS · '+('VERSION '+version if released else 'DEVELOPMENT REVIEW')+'</p>', density_text, count=1)
        density_text=re.sub(r'(<footer>.*?) (?:Published atlas unchanged pending review\.|Released version [^<]+\.)(</footer>)',lambda m:m.group(1)+' '+('Released version '+version+'.' if released else 'Published atlas unchanged pending review.')+m.group(2),density_text,count=1)
        write('density.html',density_text)
    n=manifest();print('Current candidate documentation generated; manifest files:',n)
if __name__=='__main__':main()
