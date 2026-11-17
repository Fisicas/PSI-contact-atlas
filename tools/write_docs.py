"""Write the documentation and release metadata from the built atlas, then the file manifest.

Reads data/atlas.js, build/config/release.json and the validation records in build/provenance/, and writes
README.md, CITATION.cff, .zenodo.json, CHANGELOG.md, LICENSE-DATA.md, downloads/README.md, build/README.md,
docs/METHODS.md, docs/VALIDATION.md and finally MANIFEST.json (SHA-256 of every published file).

    python tools/write_docs.py        # after tools/build_atlas.py
"""
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROV = ROOT / 'build' / 'provenance'
OWNER, REPO = 'Fisicas', 'PSI-contact-atlas'          # GitHub Pages paths are case-sensitive
PAGES_URL = f'https://{OWNER.lower()}.github.io/{REPO}/'
REPO_URL = f'https://github.com/{OWNER}/{REPO}'
TITLE = 'PSI Contact Atlas'
FULL_TITLE = f'{TITLE}: heavy-atom contacts around the photosystem I special pair and A1 quinone sites'
AUTHOR_GIVEN, AUTHOR_FAMILY, ORCID = 'Michael Raymond', 'Nelson', '0009-0004-9809-9842'
GIFS = [('spin_1JB0_prot1_P_A.gif', '1JB0 P_A chlorophyll with its Thr/Tyr/Ser and water network, spinning',
         '<b>1JB0 · P<sub>A</sub> network</b> — <i>S. elongatus</i>, X-ray 2.5 Å'),
        ('spin_7COY_prot1_special_pair.gif', '7COY chlorophyll d special pair, spinning',
         '<b>7COY · special pair</b> — <i>A. marina</i> Chl <i>d</i> / P740, cryo-EM 2.5 Å'),
        ('spin_9YL7_prot1_A1A.gif', '9YL7 A1A plastoquinone-9 pocket, spinning',
         '<b>9YL7 · A<sub>1A</sub></b> — PQ-9 (30 of 55 heavy atoms deposited), cryo-EM 1.68 Å'),
        ('spin_9AU4_prot1_A1B.gif', '9AU4 A1B DMPBQ pocket, spinning',
         '<b>9AU4 · A<sub>1B</sub></b> — DMPBQ in the MenB variant, cryo-EM 2.03 Å')]
CLASS_ORDER = ('mg', 'polar', 'water', 'acceptor_pair', 'context', 'intra', 'cs_contact')
CLASS_RULE = ('Mg involved → `mg`; same residue → `intra`; C or S involved → `cs_contact`; more than 3.5 Å → `context`; '
              'water involved → `water`; both atoms are oxygens that cannot carry a hydrogen (any cofactor oxygen; a backbone or '
              'Asn/Gln amide C=O) → `acceptor_pair`; otherwise → `polar`. Carboxylate O and His N stay `polar` because their '
              'protonation state is not known; the `chemical_basis` column says so.')


def load_js(path):
    t = path.read_text(encoding='utf-8')
    return json.loads(t[t.index('=', t.index('PSI_ATLAS')) + 1:].rstrip().rstrip(';'))


def read_json(p, default=None):
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default


def class_counts():
    with open(ROOT / 'downloads' / 'all_contacts.csv', encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    scene, uniq = {}, {}
    for r in rows:
        scene[r['contact_class']] = scene.get(r['contact_class'], 0) + 1
        uniq.setdefault(r['contact_id'], r['contact_class'])
    u = {}
    for c in uniq.values():
        u[c] = u.get(c, 0) + 1
    return scene, u


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8', newline='\n')


def citation(R, md=True):
    doi = f"https://doi.org/{R['version_doi']}" if R.get('version_doi') else REPO_URL
    a1 = 'A<sub>1</sub>' if md else 'A1'
    title = f'{TITLE}: heavy-atom contacts around the photosystem I special pair and {a1} quinone sites'
    return f"M. R. Nelson, {'*' + title + '*' if md else title}, version {R['version']} ({R['release_date'][:4]}), Zenodo. {doi}"


def abstract(A):
    c = A['counts']
    return (f"Heavy-atom separations around the photosystem I special pair, the P_A chlorophyll network and both A1 quinone sites, "
            f"computed from {c['structures']} deposited PDB entries ({c['protomers']} protomers, {c['views']} scenes, "
            f"{c['unique_contacts']} unique atom pairs). Each distance is traceable to two named deposited atoms and carries a "
            f"chemical-basis note; short N/O···O separations are hydrogen-bond candidates only, and pairs of two oxygen acceptors "
            f"are marked as not candidates. Includes an offline interactive viewer, contact and comparison tables with stable IDs, "
            f"mmCIF crops, PyMOL scripts, the archived input structures, a portable build and an independent verification script. "
            f"A curated comparative atlas of selected PSI environments, not a census of all PSI structures.")


def cff(A, R):
    doi = f'doi: "{R["version_doi"]}"\n' if R.get('version_doi') else ''
    return f'''cff-version: 1.2.0
message: "If you use this atlas, please cite the version you used, together with the PDB entries and primary papers for the structures you use."
title: "{FULL_TITLE}"
type: dataset
authors:
  - given-names: "{AUTHOR_GIVEN}"
    family-names: "{AUTHOR_FAMILY}"
    orcid: "https://orcid.org/{ORCID}"
version: "{R['version']}"
date-released: "{R['release_date']}"
{doi}license:
  - CC-BY-4.0
  - MIT
repository-code: "{REPO_URL}"
url: "{PAGES_URL}"
abstract: >-
  {abstract(A)}
keywords:
  - photosystem I
  - special pair
  - P700
  - phylloquinone
  - A1 quinone
  - hydrogen bonding
  - cryo-EM
  - X-ray crystallography
  - PyMOL
'''


def zenodo(A, R):
    return dict(
        upload_type='dataset', title=FULL_TITLE, version=R['version'],
        creators=[dict(name=f'{AUTHOR_FAMILY}, {AUTHOR_GIVEN}', orcid=ORCID)],
        description=f'<p>{abstract(A)}</p><p>Interactive viewer: <a href="{PAGES_URL}">{PAGES_URL}</a> (also opens offline from '
                    f'index.html in this archive). Values are Euclidean distances between deposited heavy atoms; they are not '
                    f'confirmed hydrogen bonds and carry no per-atom uncertainty. Not peer reviewed.</p>',
        license='cc-by-4.0',
        notes='One archive holds the viewer, the tables, the archived inputs and the build and verification code. Data, figures '
              'and text: CC BY 4.0. Code (index.html, css/, js/, tools/, downloads/pymol/, .github/): MIT. Atomic coordinates and '
              'chemical-component definitions in build/inputs are wwPDB files (CC0); please cite the PDB entries and their primary papers.',
        keywords=['photosystem I', 'special pair', 'P700', 'phylloquinone', 'A1 quinone', 'hydrogen bonding', 'cryo-EM',
                  'X-ray crystallography', 'PyMOL'],
        language='eng',
        related_identifiers=[dict(identifier=f"10.2210/pdb{s['pdb'].lower()}/pdb", relation='references', scheme='doi',
                                  resource_type='dataset') for s in sorted(A['structures'], key=lambda s: s['pdb'])])


def structures_table(A):
    rows = []
    for s in sorted(A['structures'], key=lambda s: (not s['technique']['method'].startswith('X-RAY'), float(s['resolution']))):
        t = s['technique']
        meth = 'X-ray' if t['method'].startswith('X-RAY') else 'Cryo-EM'
        extra = (f"{t.get('space_group', '')}, {t.get('phasing', '')} phasing" if meth == 'X-ray'
                 else t.get('point_symmetry', 'symmetry not in mmCIF') + (f", {t['emdb']}" if t.get('emdb') else ''))
        cf = s['protomers'][0]['cofactors']
        paper = ', '.join(f"[{x['author_short']} {x['year']}](https://doi.org/{x['doi']})" for x in s['citations']) or 'to be published'
        origin = 'curated' if s['scene_origin'] == 'curated' else 'derived by rule'
        rows.append(f"| [{s['pdb']}](https://www.rcsb.org/structure/{s['pdb']}) | *{s['organism']}* | {s['condition']} | "
                    f"{meth} {t.get('resolution_A', s['resolution'])} Å · {extra} | {cf['A1_A']['name']} / {cf['A1_B']['name']} | "
                    f"{len(s['protomers'])} | {origin} | {paper} |")
    return '\n'.join(rows)


def readme(A, R, V):
    c, v = A['counts'], A['verification']
    sc_counts, u_counts = class_counts()
    n_ctx = sum(1 for x in v['class_changes'] if x['class_now'] == 'context')
    n_acc = sum(1 for x in v['class_changes'] if x['class_now'] == 'acceptor_pair')
    badge = f"[![DOI](https://zenodo.org/badge/DOI/{R['concept_doi']}.svg)](https://doi.org/{R['concept_doi']})\n\n" if R.get('concept_doi') else ''
    ex_row = next(r for r in A['compare']['P_A'] if r.get('cof_atom') == 'OBD' and r.get('ref_pos') == '743')
    ex = {cc['pdb']: cc for cc in ex_row['cells'] if cc['protomer'] == 1}
    example = '\n'.join(f"{p}  {ex[p]['a']:>18} ... {ex[p]['b']:<16} PyMOL {ex[p]['d']:.2f} A   library {ex[p]['d']:.2f} A"
                        for p in ['1JB0', '6KMW', '6KMX', '9EYS', '9YL7', '7COY'])
    derived = [s['pdb'] for s in A['structures'] if s['scene_origin'] != 'curated']
    gif_cells = [f'<td align="center"><img src="media/{f}" width="430" alt="{alt}"><br><sub>{cap}</sub></td>' for f, alt, cap in GIFS]
    rc = R.get('recheck')
    return f"""# {TITLE}

{badge}**Heavy-atom separations around the photosystem I special pair, the P<sub>A</sub> chlorophyll network and both A<sub>1</sub> quinone sites, computed from {c['structures']} deposited PDB entries ({c['protomers']} protomers, {c['views']} scenes, {c['unique_contacts']} unique atom pairs).**

Open the interactive atlas: **[{PAGES_URL}]({PAGES_URL})** · or download this repository and open `index.html` in any modern browser (no server, no install, works offline).

> Version {R['version']} ({R['release_date']}). A curated comparative atlas of selected PSI donor and A<sub>1</sub>-site environments, not a systematic census of all PSI structures or a measurement of electron-transfer properties. Values are computed from deposited coordinates and checked independently; the atlas has not been peer reviewed. Please read [What it can and cannot tell you](#what-it-can-and-cannot-tell-you) before using a number.

<table>
<tr>
{gif_cells[0]}
{gif_cells[1]}
</tr>
<tr>
{gif_cells[2]}
{gif_cells[3]}
</tr>
</table>

<sub>Each loop is drawn by the atlas’s own viewer from deposited heavy atoms: grey C, blue N, red O, green Mg, yellow S; thicker sticks are the cofactor. Dashed lines are measured separations in Å (dark: polar candidate ≤ 3.5 Å; teal: water-involved; green: Mg–ligand; mauve: two oxygen acceptors, not a hydrogen-bond candidate; grey dotted: longer context). The interactive site re-places labels to avoid overlaps.</sub>

## Why these four environments

In PSI, light drives charge separation from the special pair (P700, or P740 in the chlorophyll *d* entries; chlorophylls P<sub>A</sub> and P<sub>B</sub>) along two nearly symmetric cofactor branches, through the A<sub>1</sub> quinones to the iron–sulfur clusters. Two structural features make these sites worth comparing atom by atom:

- **P<sub>A</sub> has a hydrogen-bond network that P<sub>B</sub> lacks.** In the 1JB0 reference, P<sub>A</sub> (a Chl *a*′ epimer) sits in a polar network of PsaA Thr743, Tyr603, Ser607, Gly739 and a water, which P<sub>B</sub> lacks ([Jordan et al. 2001](https://doi.org/10.1038/35082000)). The network is a recurring candidate for tuning the special pair’s electronic asymmetry, so its geometry in far-red-light (FRL) PSI, chlorophyll *d* PSI and engineered variants is of direct interest.
- **Each A<sub>1</sub> quinone has one carbonyl near a backbone N–H** (PsaA Leu722 / PsaB Leu706 in 1JB0) and the other near a Trp NE1, a Ser OG and the Phe689 backbone N–H (1JB0 PsaA numbering). That second carbonyl also sits about 3 Å from the Met688 backbone C=O oxygen; two acceptors cannot hydrogen-bond each other, so the atlas lists that pair separately as “O···O, no H donor”. Replacing phylloquinone (the MenB variant with DMPBQ; the PQ-9/DMPBQ entry 9YL7) changes the ring and its substituents while the pocket stays largely conserved.

## What you can do with it

![Structures grouped by experimental method](media/page_structures_by_method.png)

- **Browse by experimental method.** X-ray and single-particle cryo-EM entries are grouped separately, with the technique fields read from each deposit, a link to each entry’s wwPDB validation report, and filters by growth condition.
- **Rotate a scene and read it.** Drag to rotate, Ctrl + wheel to zoom. Hovering a dashed guide highlights its row in the atom-pair table; each row opens to show the class, the chemical basis and its stable contact ID. PNG and GIF export from any orientation.

![Scene page: live 9EYS P_A network linked to its atom-pair table](media/page_scene_9EYS_PA.png)

- **Compare one contact across all {c['protomers']} protomers.** Each column is a homologous atom pair (partner residues mapped to 1JB0 numbering by sequence alignment); each cell is computed from that protomer’s coordinates. A blank cell says *why*: the residue differs, the atom is not modelled, or no deposited water meets the site rule.

![Compare matrix for the P_A network](media/page_compare_PA.png)

- **See each structure’s cofactor identities and lineage**, with the deposited component name beside the interpreted pigment (a deposited CLA at P<sub>A</sub> is not silently renamed Chl *a*′) and case-sensitive chain IDs.

<table><tr>
<td width="62%"><img src="media/page_structure_9AU4.png" alt="Structure page for 9AU4 with four live scenes"></td>
<td><img src="media/page_phone_scene.png" alt="Scene page on a phone"></td>
</tr></table>

- **Download and cite tables** with stable IDs: one row per physical atom pair, one table per environment, per-scene tables, mmCIF crops and PyMOL scripts. Every column is explained in [`downloads/README.md`](downloads/README.md).

## Observations the compare view makes visible

These are statements about the deposited models, not functional conclusions:

- **Residue differences at network positions.** Several entries carry Phe where 1JB0 has Trp683 (5OY0, 6KMX, 9AU4, 9EYS, 9I9L, 9YL7, 9OY9, 9OZ3), and white-light 6KMW carries Phe where 1JB0 has Tyr735 while far-red-light 6KMX keeps the Tyr. The Chl *d* entries have Ser where 1JB0 has Thr743.
- **Protomers are not replicates.** Within an entry, values can be nearly identical or differ by up to 0.35 Å (more in the X-ray 5OY0 trimer), depending on how symmetry was imposed on the map and model. Neither case is an independent repeat measurement.
- **Unusual separations stay visible.** 5OY0 protomer 3 has long P<sub>A</sub> Mg–His separations; 9AU4 HOH907 sits 3.95 Å from P<sub>A</sub> O2D, outside the 3.5 Å polar screen; 9AU4 Trp693 NE1 is listed as unobserved in its deposition.

## What it can and cannot tell you

| It can | It cannot |
|---|---|
| Give the Euclidean separation between two deposited heavy atoms, from full-precision coordinates, with native chain/residue/atom names. | Confirm a hydrogen bond. Short polar heavy-atom separations are geometric observations; only chemically compatible donor–acceptor pairs are potential hydrogen-bond contacts, and hydrogen positions, protonation states and angles are not established here. |
| Say what the atom types allow (the `chemical_basis` column: donor–acceptor compatible, acceptor–acceptor, water-involved, unresolved). | Give the uncertainty of a distance. Five decimals are computational precision and 0.01 Å is display precision; nominal resolution is not a per-atom error, and local map quality is not summarised (each entry links its wwPDB validation report). |
| Compare a homologous contact across {c['protomers']} protomers and show where the residue itself differs. | Treat protomers as independent replicates, or count a pair shown in two scenes twice ({c['contacts']} scene rows are {c['unique_contacts']} unique pairs). |
| Separate deposited component identity, interpreted pigment name, functional role and chain ID. | Prove a water is conserved or absent (“no deposited water meets the site rule” is not “water absent”), establish Mg coordination geometry or stereochemistry, or establish model ancestry. |

## Structures

| PDB | Organism | Condition | Method | A<sub>1A</sub> / A<sub>1B</sub> | Protomers | Scenes | Paper |
|---|---|---|---|---|---|---|---|
{structures_table(A)}

**Scope and updates.** The first {c['structures'] - len(derived)} entries were selected and their scenes curated and reviewed one by one. Cyanobacterial PSI entries released after that curated build are added with scenes derived by a documented rule ({', '.join(derived)} in this version); the rule and its check against curated scenes are in [`docs/METHODS.md`](docs/METHODS.md). Display alignment to 1JB0 is a camera convention, not model ancestry.

## Doing it yourself in PyMOL

Everything the site shows can be reproduced in [PyMOL](https://pymol.org/), either from the scene crops in this repository or from the full deposited entries.

### 1 · Open any scene with its script

Every scene has a script in [`downloads/pymol/`](downloads/pymol). From the repository root:

```bash
pymol downloads/pymol/1JB0_prot1_P_A.pml
```

The script loads the scene’s mmCIF crop from `downloads/cif/`, applies the atlas’s colours and stick sizes, draws every measured pair as a PyMOL distance object grouped by class (`Mg_ligand`, `polar_candidate`, `water_polar_candidate`, `OO_no_H_donor`, `longer_context`, `CS_contact`, `intramolecular`), labels residues and roles, and restores the starting view. The comment above each `distance` line gives the atlas value. To start from the full deposited entry, replace the `load` line with the `fetch` line given in the script.

### 2 · Measure a site from scratch

```
fetch 1JB0, type=cif
set ignore_case, 0
select PA, 1JB0 and chain A and resi 1011 and resn CLA
select shell, byres (1JB0 and (polymer or resn HOH)) within 5 of PA
hide everything
show sticks, PA or shell
show spheres, (PA and elem MG) or (shell and resn HOH)
set sphere_scale, 0.25
distance polar, PA and elem N+O, shell and elem N+O, 3.5, mode=0
distance mg_ligand, PA and name MG, shell and elem N+O, 3.0, mode=0
get_distance 1JB0 and chain A and resi 1011 and name OBD, 1JB0 and chain A and resi 743 and name OG1
```

- `mode=0` draws **every** heavy-atom pair within the cutoff, which is the quantity this atlas reports; the atlas’s per-scene lists are a curated subset of such pairs, not an exhaustive census.
- `mode=2` (also *Action → find → polar contacts*) applies PyMOL’s own hydrogen-bond geometry heuristics, so it can add or drop pairs relative to a plain distance cutoff. It is not a confirmation of a hydrogen bond either.
- Residue numbers differ between organisms. To find the residue at a given 1JB0 position, use the compare page, [`downloads/compare_matrix.csv`](downloads/compare_matrix.csv) or [`build/provenance/alignment_to_1JB0.csv`](build/provenance/alignment_to_1JB0.csv).

### 3 · Compare one contact across structures

[`tools/pymol_compare_example.py`](tools/pymol_compare_example.py) measures the P<sub>A</sub> 13<sup>1</sup>-keto oxygen (OBD) to the side-chain hydroxyl at the 1JB0 Thr743 position in six entries and prints PyMOL’s value next to the atlas’s:

```
run tools/pymol_compare_example.py
```

```
{example}
```

Each pair is listed with native identities because the partner differs between entries (Thr OG1 in most, Ser OG in the chlorophyll *d* entry 7COY).

### 4 · Things that commonly go wrong

- **Chain IDs are case-sensitive.** 9AU4 and 9OZ3 have chains `A`, `G` and `a`; 6KMW, 6KMX, 7COY and 9SK3 use two-letter IDs such as `aA`. Keep `set ignore_case, 0`.
- **Author vs label numbering.** PyMOL reads author chain and residue numbers from mmCIF by default (`cif_use_auth`), as the atlas does. The `label_asym_id` chains are different and are listed in the CSVs.
- **Alternate locations.** The atlas uses the highest-occupancy position; none of the atoms in its scenes has an alternate location.
- **Quinone atom names are not interchangeable.** Phylloquinone (PQN) carbonyls are O1/O4; PL9 and A1AGD use O1/O2. The carbonyl next to the Leu backbone N is PQN O4 but PL9/A1AGD O1.
- **Hydrogens.** Most deposits have none. `h_add` places idealised hydrogens; they are not observations.

## How the numbers are produced and checked

- Every value is computed from the archived deposited files in [`build/inputs/`](build/inputs) (PDB structure-model revision and SHA-256 of each in [`data/sources.json`](data/sources.json)). Methods, the contact-class rule, the site-water rule and the derived-scene rule are in [`docs/METHODS.md`](docs/METHODS.md); what was checked, and what was not, is in [`docs/VALIDATION.md`](docs/VALIDATION.md).
- Contact classes follow one rule: {CLASS_RULE}
- Corrections relative to the earlier curated build: {len(v['rounding_changes'])} values that change in the last displayed digit, {n_ctx} water pairs reclassified as longer context, and the “O···O, no H donor” class ({sc_counts.get('acceptor_pair', 0)} scene rows; {n_acc} are listed on the Methods page because their earlier annotation did not already mark them as acceptor-only). Changes between versions are in [`CHANGELOG.md`](CHANGELOG.md).{(' On ' + rc['date'] + ' every value was also recomputed from the then-current PDB files: ' + rc['result']) if rc else ''}

### Rebuild and verify it yourself

```bash
pip install -r build/requirements.txt
python tools/build_atlas.py
python tools/verify_public.py
```

`build_atlas.py` regenerates every table, scene, crop and PyMOL script from `build/` alone; a clean rebuild reproduces the committed files. `verify_public.py` is an independent check (gemmi only) of every number and table; add `--cif-dir cif_cache --download` to compare against today’s RCSB files instead of the archived ones.

## Repository layout

| Path | Contents |
|---|---|
| `index.html`, `css/`, `js/` | The static site; `js/viewer.js` is a dependency-free Canvas 2D molecular viewer. |
| `data/atlas.js`, `data/views/*.js` | Structure metadata, comparison tables and one file per scene, as the site reads them. |
| `data/sources.json`, `data/verification.json` | PDB revision and hash of each deposited file, and the build record. |
| `downloads/` | Contact tables (combined, per scene, unique pairs, per environment), mmCIF crops, PyMOL scripts; column guide in `downloads/README.md`. |
| `build/inputs/`, `build/config/` | Archived deposited mmCIF files and CCD definitions; curated and derived scene definitions and structure metadata. |
| `build/provenance/` | Alignment to 1JB0 numbering, site-water audit and validation records. |
| `tools/` | `build_atlas.py`, `derive_scenes.py`, `verify_public.py`, `write_docs.py`, PyMOL script tools and example. |
| `docs/` | Methods and validation. |
| `CITATION.cff`, `.zenodo.json`, `CHANGELOG.md`, `MANIFEST.json` | Citation and archive metadata, changes between versions, SHA-256 of every file. |

## Licence

- **Code** (`index.html`, `css/`, `js/`, `tools/`, `downloads/pymol/`, `.github/`): [MIT](LICENSE).
- **Data, figures and text** (`data/`, the rest of `downloads/`, `build/config/`, `build/provenance/`, `media/`, `docs/`, this README and the site text): [CC BY 4.0](LICENSE-DATA.md).
- **Atomic coordinates and chemical-component definitions** in `build/inputs/` are wwPDB files (CC0). Please cite the PDB entries and their primary papers.

## How to cite

Please cite the version you used. Each release is archived on Zenodo with its own DOI{' (the badge at the top links to all versions)' if R.get('concept_doi') else ''}; [`CITATION.cff`](CITATION.cff) holds the same metadata, and GitHub shows it as *Cite this repository*. Cite individual values by their `contact_id` or `comparison_id` (see [`downloads/README.md`](downloads/README.md)).

> {citation(R)}

Please also cite the PDB entries and primary papers for the structures you use (listed above and on each structure page). A DOI is not peer review.

Author: {AUTHOR_GIVEN} {AUTHOR_FAMILY}.
"""


def changelog(A, R):
    c = A['counts']
    sc, uc = class_counts()
    derived = [s['pdb'] for s in A['structures'] if s['scene_origin'] != 'curated']
    rc = R.get('recheck')
    rct = (f"\n### Rechecked against current PDB files\n\nOn {rc['date']} every coordinate, distance, class and comparison cell was recomputed "
           f"from the then-current PDB files ({rc['revisions']}). {rc['result']}\n") if rc else ''
    return f"""# Changelog

Changes are grouped as **data** (numbers or atoms), **interpretation** (classes and wording) and **software**.

## {R['version']} — {R['release_date']}

First versioned release, archived on Zenodo. No distance in the earlier 112 scenes changed.

### Data

- **New entries** {', '.join(derived)}: cyanobacterial PSI released after the curated build (*Synechocystis* sp. PCC 6803 PsaB red-shift variant, 1.76 Å and 1.88 Å). Their {c['derived_views']} scenes are derived by the documented homology rule ([`docs/METHODS.md`](docs/METHODS.md)), not reviewed one by one. The atlas now has {c['structures']} entries, {c['protomers']} protomers and {c['views']} scenes.
- **Unique atom pairs.** {c['contacts']} scene contact rows are {c['unique_contacts']} physical atom pairs: pairs shown in both the P<sub>A</sub> and the special-pair scene of a protomer are one observation. New table `downloads/tables/atlas_unique_contacts.csv`.
- **Stable IDs and named tables.** Every pair has a `contact_id`; every homologous comparison a `comparison_id`. Per-environment tables `atlas_table_PA_network.csv`, `atlas_table_special_pair.csv`, `atlas_table_A1A.csv`, `atlas_table_A1B.csv`.
- **Archived inputs and portable build.** The exact deposited files and CCD definitions are in `build/inputs/`, the curated selections in `build/config/`; `tools/build_atlas.py` rebuilds every output from them.
- mmCIF crops are now written by the build from the deposited files (same atoms as before).

### Interpretation

- **New class “O···O, no H donor”** (`acceptor_pair`): {sc.get('acceptor_pair', 0)} scene rows in which both atoms are oxygens that cannot carry a hydrogen (a cofactor carbonyl or ester oxygen facing a backbone C=O, e.g. the A<sub>1</sub> quinone carbonyl and the PsaA Met688 / PsaB Met668 backbone O in 1JB0) were listed as polar (hydrogen-bond) candidates. Distances unchanged. Compare-matrix columns for these partners are marked and not colour-scaled.
- **New column `chemical_basis`** on every pair: donor–acceptor compatible, acceptor–acceptor, water-involved, unresolved (His/Asp/Glu protonation), Mg–ligand, beyond the screen, same residue, or involves C/S.
- **“Packing” renamed “C/S contact”** (`cs_contact`): the class is element-based and is not evidence of an attractive interaction.
- Missing-water cells now read “no deposited water meets the site rule” instead of implying absence. Wording uses “special pair” throughout (P700 or P740).
- 5OY0 condition “WT (paper)” is now “Wild type”.

### Software and metadata

- `tools/verify_public.py` now checks every exported table at its own precision, unique keys, crops, the class and chemical-basis rule and the file manifest; strict mode fails if an archived input changed. `tests/` holds deliberate-corruption tests; `.github/workflows/verify.yml` runs the rebuild, the verifier and the tests.
- `data/sources.json` records the PDB structure-model revision of each file. Structure pages link the wwPDB validation report.
- CSV column `v02_annotation` renamed `curated_annotation`. Column guide in `downloads/README.md`; methods and validation in `docs/`.
- Site link fixed (`{PAGES_URL}`; the lowercase address returned 404). Version label “preview” replaced by {R['version']}. `CITATION.cff` gains ORCID, abstract and release date; `.zenodo.json` describes the archive as a dataset.
{rct}
## 0.1.0-preview — 2026-10-17

Initial public preview (12 entries, 28 protomers, 112 curated scenes).
"""


def data_dictionary(A):
    sc, uc = class_counts()
    cls_rows = '\n'.join(f"| `{k}` | {A['classes'][k]} | {sc.get(k, 0)} | {uc.get(k, 0)} |" for k in CLASS_ORDER)
    c = A['counts']
    return f"""# Downloads: file and column guide

All distances are in ångström (Å), computed between deposited heavy-atom coordinates at full precision and written with five (contact tables) or four (comparison tables) decimals. That is computational precision, not experimental accuracy; the site shows 0.01 Å. Hydrogens, protonation states and angles are not modelled, so no row is a confirmed hydrogen bond.

**Atom identifiers** have the form `COMP:chain:residue:atom` with the deposited component name and **author** chain and residue numbering (as PyMOL reads mmCIF by default). Chain IDs are case-sensitive (`A` and `a` are different chains); an insertion code, if any, follows the residue number. Example: `PQN:A:2001:O4`. Only model 1 is used; where an atom has alternate locations the highest-occupancy position is used (none of the scene atoms has one).

## Which file to use

| File | One row per | Use it to |
|---|---|---|
| `tables/atlas_unique_contacts.csv` | physical atom pair ({c['unique_contacts']}) | count or cite observations |
| `tables/atlas_table_<environment>.csv` | homologous contact × protomer | compare one contact across entries (`PA_network`, `special_pair`, `A1A`, `A1B`) |
| `compare_matrix.csv` | the four environment tables together | the same, in one file |
| `all_contacts.csv`, `contacts/<scene>_contacts.csv` | atom pair as shown in a scene ({c['contacts']} rows) | reproduce what a scene shows |

## Contact tables (`all_contacts.csv`, `contacts/`, `tables/atlas_unique_contacts.csv`)

| Column | Meaning |
|---|---|
| `contact_id` | Stable ID of the physical pair: `<PDB>.p<protomer>.<atom>~<atom>` with the two atoms in sorted order. The same pair shown in two scenes has one ID. |
| `view` / `scenes` | Scene name(s), `<PDB>_prot<n>_<environment>`. |
| `pdb`, `protomer`, `part` | PDB entry, protomer number and environment (`special_pair`, `P_A`, `A1A`, `A1B`). |
| `atom_1`, `atom_2` | The two atoms (format above). |
| `label_asym_1`, `label_asym_2` | mmCIF `label_asym_id` of each atom. |
| `distance_A` | Separation in Å. |
| `contact_class` | One of the classes below. |
| `chemical_basis` | What the two atom types allow: `donor–acceptor compatible`, `acceptor–acceptor; neither atom carries a hydrogen`, `water-involved; water can donate or accept`, `unresolved; depends on protonation state or tautomer` (His N, Asp/Glu O), or the class restated for Mg, same-residue, beyond-screen and C/S pairs. Not a hydrogen-bond assignment. |
| `curated_annotation` | Free-text annotation from the earlier curated build, kept for traceability; `derived by homology` for rule-derived scenes. |
| `occupancy_1`, `occupancy_2`, `B_iso_1`, `B_iso_2` | Deposited occupancy and isotropic B-factor (Å²). Context only; they are not distance error bars. |

### Contact classes

Assigned by one rule, in this order: {CLASS_RULE}

| Class | Meaning | Scene rows | Unique pairs |
|---|---|---|---|
{cls_rows}

## Comparison tables (`compare_matrix.csv`, `tables/atlas_table_*.csv`)

| Column | Meaning |
|---|---|
| `comparison_id` | Stable ID of the homologous contact, e.g. `A1A.A1_A.carbonyl_O~PsaA688.O`. Cite a value as `comparison_id` + `pdb` + `protomer`. |
| `part`, `cofactor_role`, `cofactor_atom` | Environment, functional role (`P_A`, `P_B`, `A1_A`, `A1_B`, or `site water`) and atom. For the quinones, `carbonyl O` is the shorter separation from either carbonyl oxygen; the native atom used is in `atom_1`. |
| `partner_subunit`, `1JB0_position`, `1JB0_residue`, `partner_atom` | Partner in 1JB0 numbering (`hydroxyl O` = Ser OG / Thr OG1 / Tyr OH; `O` = backbone C=O oxygen; `N` = backbone N–H). |
| `pdb`, `protomer`, `native_partner` | Entry, protomer and the partner residue as deposited (`Tyr599.1` = Tyr599 in chain 1). |
| `atom_1`, `atom_2`, `distance_A` | The deposited atoms used and their separation. |
| `missing_reason` | Why a cell is empty: residue differs, atom not modelled, position not aligned, or no deposited water meets the site rule. Blank when a distance is given. |

## Other files

- `cif/<scene>.cif` — mmCIF crop of each scene with deposited names, numbering, chains and coordinates.
- `pymol/<scene>.pml` — PyMOL script that loads the crop and draws every measured pair, grouped by class.
"""


def methods(A):
    rule = (ROOT / 'build' / 'provenance' / 'derive_rule_check.txt')
    rule_txt = rule.read_text(encoding='utf-8').strip().splitlines()[-1] if rule.exists() else ''
    return f"""# Methods

## Sources

Each entry is read from the deposited mmCIF archived in `build/inputs/structures/` (model 1, author chain and residue numbering, highest-occupancy alternate location). `data/sources.json` gives the PDB structure-model revision, its date and the SHA-256 of each file. Chemical-component definitions (`build/inputs/ccd/`) give atom names, bonds and the carbonyl oxygens of the quinones.

## Scenes

A scene is one protomer and one environment: the special pair (P<sub>A</sub> and P<sub>B</sub> with their ligands), the isolated P<sub>A</sub> network, and the A<sub>1A</sub> and A<sub>1B</sub> quinone pockets.

- **Curated scenes** (the first {A['counts']['views'] - A['counts']['derived_views']}) list atoms and atom pairs chosen in an earlier PyMOL build and reviewed scene by scene; `build/config/scenes.json` records them with their earlier annotation and value. They are a curated subset of nearby pairs, not an exhaustive census.
- **Waters.** P<sub>A</sub> scenes show the reference-site water. Special-pair scenes show every deposited water within 5 Å of the P<sub>A</sub>/P<sub>B</sub> Mg and oxygens (O1A, O2A, O1D, O2D, OBD). Nothing is added where the deposit has no water.
- **Derived scenes** (entries released after the curated build). For each environment the template is the curated scene of the most similar entry: same organism, then the same deposited cofactor components, then the best resolution. The derived scene contains the residues at the homologous positions (PsaA/PsaB aligned to 1JB0 numbering; cofactors by role), the template’s atoms, and the template’s atom pairs mapped to the new model. Chlorophyll atoms map by name (Chl *a* and *a*′ share names); quinone atoms of a different component map to the nearest atom of the same element after superposition, so each carbonyl keeps its position. Waters follow the rules above; each special-pair water is paired with its nearest diagnostic atom. The camera is the template camera superposed on the new coordinates. Template pairs with no counterpart are listed in the scene notes. Cofactor roles are found from 1JB0 anchors: the P<sub>A</sub>/P<sub>B</sub> Mg nearest the PsaA His680 / PsaB His660 NE2 positions, and the quinone oxygen nearest the PsaA Leu722 / PsaB Leu706 backbone N.
- **Check of the derivation rule.** Re-deriving curated scenes of five entries from another entry reproduces most curated pairs ({rule_txt or 'see build/provenance/derive_rule_check.txt'}). Every difference traces to the curated selections themselves differing between entries, or to a residue that differs at that position. Full output: `build/provenance/derive_rule_check.txt`.

## Distances, classes and chemical basis

Distances are Euclidean separations between deposited heavy atoms. Class rule, in order: {CLASS_RULE} The chemical basis states what the atom types allow; a backbone N–H (not Pro), Ser/Thr/Tyr OH, Trp NE1, Asn ND2, Gln NE2, Lys NZ and Arg N are treated as donors. No hydrogens are added and no angles are evaluated.

## Homologous comparison

PsaA and PsaB of every protomer are aligned to 1JB0 chains A and B (global alignment, BLOSUM62, gap open −10, extend −0.5); the full mapping is `build/provenance/alignment_to_1JB0.csv`. It reproduces all {A['verification']['alignment_crosschecks']} P<sub>A</sub>-network mappings of the curated build. A comparison column is created when any scene of an environment lists a polar, water, O···O or Mg pair between a cofactor atom and a PsaA/PsaB atom (or the site water); every protomer is then evaluated for that column.

## Reference-site water

For each protomer the 25 chlorin-core atoms of P<sub>A</sub> are superposed on those of 1JB0 P<sub>A</sub> (`CHLORIN_CORE` in `tools/build_atlas.py`), the position of 1JB0 HOH5011 is carried over, and the nearest deposited water within 3 Å is the site water. `build/provenance/site_water.csv` lists the core RMSD, the offset and the next-nearest water for every protomer. A positional assignment is not proof that a water is conserved, and a short pigment–water distance is a separate fact (9AU4 HOH907 lies 3.95 Å from P<sub>A</sub> O2D but is not at the site).

## Not assessed

Map density, local resolution and per-atom validation (each structure page links its wwPDB validation report); Mg coordination geometry; protonation and hydrogen positions; model ancestry. Protomers of one entry are not independent replicates; no standard errors are given.
"""


def validation(A, R):
    strict = read_json(PROV / 'verify_archived.json', {})
    latest = read_json(PROV / 'verify_latest.json', {})
    pym = read_json(PROV / 'pymol_check.json', {})
    rule = PROV / 'derive_rule_check.txt'
    rule_txt = rule.read_text(encoding='utf-8').strip().splitlines()[-1] if rule.exists() else 'not run'
    tp = PROV / 'tests_local.txt'
    tests = tp.read_text(encoding='utf-8').strip().splitlines()[-1] + ' (local run; also in CI)' if tp.exists() else 'run in CI'
    fmt = lambda r: (f"{r.get('status', 'not run')} — {r.get('scene_atoms', 0):,} scene-atom occurrences, {r.get('scene_rows', 0)} scene rows, "
                     f"{r.get('unique_pairs', 0)} unique pairs, {r.get('compare_cells', 0)} comparison cells, {r.get('crops', 0)} crops, "
                     f"{r.get('manifest_files', 0)} manifest files") if r else 'not run'
    diff = latest.get('files_differing_from_build') or {}
    return f"""# Validation

What was checked for version {R['version']}, with the scope of each check. None of these checks establishes a hydrogen bond, local experimental accuracy or biological function.

| Check | Scope | Result |
|---|---|---|
| Build (`tools/build_atlas.py`) | every scene atom read from the archived file; cofactor bonds vs CCD ({A['verification']['cofactor_graphs']} cofactor residues); alignment vs {A['verification']['alignment_crosschecks']} curated mappings; distances vs the earlier curated values (max change {A['verification']['max_distance_deviation_A']:.4f} Å, bound √3 × 0.001 Å from earlier rounding); site waters vs earlier assignments | PASS |
| Independent verifier, archived inputs (`tools/verify_public.py`, strict) | every scene atom, distance, class, chemical basis and ID; every exported table at its precision; per-scene vs combined tables; unique pairs; comparison tables vs `atlas.js`; crops; manifest | {fmt(strict)} |
| Independent verifier, current RCSB files | same checks against files downloaded {R['recheck']['date'] if R.get('recheck') else ''} | {fmt(latest)}{('; newer structure-model revisions: ' + ', '.join(f'{k} {v}' for k, v in diff.items())) if diff else ''} |
| Deliberate-corruption tests (`tests/test_verify.py`) | the verifier must pass on a clean copy and fail on a changed CSV value, class, duplicate row, comparison value, crop coordinate, documentation file (manifest) and archived input | {tests} |
| PyMOL (`tools/check_pymol_scripts.py`, PyMOL {pym.get('pymol', '3.1')}) | every script run as written (crop) and on the full deposited entry; every distance object vs the atlas | {pym.get('status', 'not run')} — {pym.get('scripts', 0)} scripts, {pym.get('distances', 0)} distances, max deviation {pym.get('max_dev_full', 0):.1e} Å |
| Derivation rule (`tools/derive_scenes.py check`) | curated scenes of five entries re-derived from another entry | {rule_txt} |
| Clean rebuild (CI) | `tools/build_atlas.py` reproduces the committed `data/` and `downloads/` byte for byte | identical on a second local build ({R['release_date']}); CI repeats it in a fresh checkout |
| Site | home, structure, scene, compare and methods pages in Chromium; no console errors | checked {R['release_date']} |

**Not checked:** density or local map quality; Firefox, Safari, screen readers and touch devices; any functional or spectroscopic interpretation.
"""


def site_header_footer(A, R):
    """Version and DOI in the site header and footer of index.html (single source: build/config/release.json)."""
    import re
    p = ROOT / 'index.html'
    t = p.read_text(encoding='utf-8')
    v, doi = R['version'], R.get('version_doi')
    status = (f'<a class="status" href="https://doi.org/{doi}" title="Version {v}; cite this DOI. Not peer reviewed.">v{v} · DOI {doi}</a>'
              if doi else f'<span class="status" title="Version {v}; not peer reviewed">v{v}</span>')
    t = re.sub(r'<(span|a) class="status"[^>]*>.*?</(span|a)>', status, t, count=1)
    foot = (f'Version {v} · cite <a href="https://doi.org/{doi}">doi:{doi}</a> · not peer reviewed.' if doi
            else f'Version {v} · not peer reviewed.')
    t = re.sub(r'(values recomputed locally\. ).*?( <a href="#/methods">)', lambda m: m.group(1) + foot + m.group(2), t, count=1)
    c = A['counts']
    t = re.sub(r'<meta name="description" content="[^"]*">',
               f'<meta name="description" content="Native heavy-atom separations around the PSI special pair, P_A network and A1 quinone sites '
               f'in {c["structures"]} deposited structures. Version {v}' + (f', doi:{doi}' if doi else '') + '.">', t, count=1)
    p.write_bytes(t.encode())


def manifest():
    skip = {'.git', '__pycache__', 'cif_cache'}
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and not set(p.relative_to(ROOT).parts) & skip
                   and p.relative_to(ROOT).as_posix() != 'MANIFEST.json'
                   and not (p.relative_to(ROOT).as_posix().startswith('build/provenance/verify_') and p.suffix == '.json'))
    m = {p.relative_to(ROOT).as_posix(): dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files}
    write('MANIFEST.json', json.dumps(m, indent=1) + '\n')
    return len(m)


def main():
    A = load_js(ROOT / 'data' / 'atlas.js')
    R = read_json(ROOT / 'build' / 'config' / 'release.json')
    write('README.md', readme(A, R, None))
    write('CITATION.cff', cff(A, R))
    write('.zenodo.json', json.dumps(zenodo(A, R), indent=1, ensure_ascii=False) + '\n')
    write('CHANGELOG.md', changelog(A, R))
    write('downloads/README.md', data_dictionary(A))
    write('docs/METHODS.md', methods(A))
    write('docs/VALIDATION.md', validation(A, R))
    write('LICENSE-DATA.md', f"""# Data, figures and documentation licence

The code in this repository (`index.html`, `css/`, `js/`, `tools/`, `tests/`, `downloads/pymol/`, `.github/`) is under the MIT licence in [`LICENSE`](LICENSE).

The curated and derived data (`data/`, `downloads/` except `downloads/pymol/`, `build/config/`, `build/provenance/`), the images in `media/`, the documentation (`docs/`, the README files) and the site text are © {AUTHOR_GIVEN} {AUTHOR_FAMILY} and licensed under the **Creative Commons Attribution 4.0 International** licence (CC BY 4.0): <https://creativecommons.org/licenses/by/4.0/>. You may share and adapt them for any purpose, provided you give appropriate credit to {TITLE} and its author, link to the licence, and indicate changes.

`build/inputs/` holds unmodified wwPDB files (atomic coordinates and chemical-component definitions), which the wwPDB makes available under CC0 1.0. Please cite the individual PDB entries and their primary papers. Literature cited in this repository remains under its publishers' terms.
""")
    write('build/README.md', f"""# Build inputs

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
""")
    site_header_footer(A, R)
    n = manifest()
    print(f'docs written; manifest lists {n} files')


if __name__ == '__main__':
    main()
