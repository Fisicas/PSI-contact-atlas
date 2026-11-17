"""Independent check of every number and table the PSI Contact Atlas publishes.

    python tools/verify_public.py                          # strict: the archived inputs in build/inputs (SHA-256 must match)
    python tools/verify_public.py --cif-dir DIR --download  # the same checks against other files, e.g. today's RCSB files
    python tools/verify_public.py --json result.json        # also write a machine-readable result

Needs Python 3.9+ and gemmi only; it does not import the builder. Checks:
  1. every scene atom (data/views/*.js) against the deposited coordinates (≤ 0.0006 Å; scenes store 0.001 Å);
  2. every scene distance (≤ 0.0001 Å), contact class, chemical basis and contact ID, re-derived from the two atoms;
  3. downloads/all_contacts.csv: one row per scene pair, no duplicates or extra rows, values at the exported 5 decimals;
  4. each downloads/contacts/<scene>_contacts.csv equals its rows of the combined table;
  5. downloads/tables/atlas_unique_contacts.csv: one row per physical atom pair, consistent with the scene rows;
  6. downloads/compare_matrix.csv and the four atlas_table_*.csv: every cell equals data/atlas.js and the deposited
     coordinates (4 decimals); comparison IDs are unique per protomer;
  7. every scene mmCIF crop parses and holds exactly the scene atoms at the deposited coordinates;
  8. MANIFEST.json lists every published file with its SHA-256 (excluded by rule: MANIFEST.json itself and the
     verifier's own result files build/provenance/verify_*.json, which are written after it).
In strict mode a source whose SHA-256 differs from data/sources.json is an error. With --cif-dir, differing
structure-model revisions are reported and the values are still compared.
"""
import argparse, csv, gzip, hashlib, io, json, math, sys, urllib.request
from pathlib import Path

import gemmi

ROOT = Path(__file__).resolve().parent.parent
COFACTORS = {'CLA', 'CL0', 'CL7', 'G9R', 'PQN', 'PL9', 'A1AGD'}
AMINO = {'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO',
         'SER', 'THR', 'TRP', 'TYR', 'VAL'}
DONOR = {('SER', 'OG'), ('THR', 'OG1'), ('TYR', 'OH'), ('TRP', 'NE1'), ('ASN', 'ND2'), ('GLN', 'NE2'), ('LYS', 'NZ'),
         ('ARG', 'NE'), ('ARG', 'NH1'), ('ARG', 'NH2')}
UNRESOLVED = {('HIS', 'ND1'), ('HIS', 'NE2'), ('ASP', 'OD1'), ('ASP', 'OD2'), ('GLU', 'OE1'), ('GLU', 'OE2')}


def is_result(rel):
    return rel.startswith('build/provenance/verify_') and rel.endswith('.json')


def load_js(path):
    t = path.read_text(encoding='utf-8')
    i = t.index('PSI_VIEWS[') if 'PSI_VIEWS[' in t else t.index('PSI_ATLAS')
    return json.loads(t[t.index('=', i) + 1:].rstrip().rstrip(';'))


def read_csv(path):
    with open(path, encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def acceptor_only(comp, atom, el):
    return el == 'O' and (comp in COFACTORS or (comp in AMINO and (atom == 'O' or (comp, atom) in {('ASN', 'OD1'), ('GLN', 'OE1')})))


def expected_class(A, B, same_residue, d):
    if 'Mg' in (A[2], B[2]):
        return 'mg'
    if same_residue:
        return 'intra'
    if {'C', 'S'} & {A[2], B[2]}:
        return 'cs_contact'
    if d > 3.5:
        return 'context'
    if 'HOH' in (A[0], B[0]):
        return 'water'
    if acceptor_only(*A) and acceptor_only(*B):
        return 'acceptor_pair'
    return 'polar'


def expected_basis(A, B, cls):
    fixed = {'mg': 'Mg–ligand separation; coordination not assessed', 'intra': 'same residue',
             'cs_contact': 'involves C or S; no polar interpretation', 'context': 'beyond the 3.5 Å screen',
             'water': 'water-involved; water can donate or accept', 'acceptor_pair': 'acceptor–acceptor; neither atom carries a hydrogen'}
    if cls in fixed:
        return fixed[cls]
    donor = lambda x: (x[0], x[1]) in DONOR or (x[0] in AMINO and x[1] == 'N' and x[0] != 'PRO')
    if donor(A) or donor(B):
        return 'donor–acceptor compatible'
    if (A[0], A[1]) in UNRESOLVED or (B[0], B[1]) in UNRESOLVED:
        return 'unresolved; depends on protonation state or tautomer'
    return 'unresolved'


class Coords:
    def __init__(self, cif_dir, download, sources):
        self.dir, self.download, self.sources = cif_dir, download, sources
        self.cache, self.revisions, self.sha = {}, {}, {}

    def text(self, pdb):
        if self.dir is None:
            raw = gzip.decompress((ROOT / 'build' / self.sources[pdb]['file']).read_bytes())
        else:
            p = Path(self.dir) / f'{pdb}.cif'
            if not p.exists():
                if not self.download:
                    raise SystemExit(f'missing {p}; pass --download to fetch it from RCSB')
                p.parent.mkdir(parents=True, exist_ok=True)
                urllib.request.urlretrieve(f'https://files.rcsb.org/download/{pdb}.cif', p)
            raw = p.read_bytes()
        self.sha[pdb] = hashlib.sha256(raw).hexdigest()
        return raw.decode('utf-8')

    def index(self, pdb):
        if pdb not in self.cache:
            doc = gemmi.cif.read_string(self.text(pdb))
            b = doc.sole_block()
            rows = [r for r in b.find('_pdbx_audit_revision_history.', ['data_content_type', 'major_revision', 'minor_revision'])
                    if gemmi.cif.as_string(r[0]) == 'Structure model']
            last = max(rows, key=lambda r: (int(r[1]), int(r[2])))
            self.revisions[pdb] = f'{last[1]}.{last[2]}'
            st = gemmi.make_structure_from_block(b)
            idx = {}
            for ch in st[0]:
                for r in ch:
                    rid = str(r.seqid.num) + (r.seqid.icode.strip() or '')
                    for a in r:
                        k = (r.name, ch.name, rid, a.name)
                        if k not in idx or a.occ > idx[k][1]:
                            idx[k] = ((a.pos.x, a.pos.y, a.pos.z), a.occ, a.element.name)
            self.cache[pdb] = idx
        return self.cache[pdb]

    def atom(self, pdb, ident):
        return self.index(pdb).get(tuple(ident.split(':')))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cif-dir')
    ap.add_argument('--download', action='store_true')
    ap.add_argument('--json')
    a = ap.parse_args()
    sources = json.loads((ROOT / 'data' / 'sources.json').read_text(encoding='utf-8'))
    C = Coords(a.cif_dir, a.download, sources)
    fails, n = [], dict(scene_atoms=0, scene_rows=0, unique_pairs=0, compare_cells=0, crops=0, manifest_files=0)
    F = fails.append

    # 1-2 scenes
    scene_rows = {}
    for f in sorted((ROOT / 'data' / 'views').glob('*.js')):
        sc = load_js(f)
        pdb, ids, info = sc['pdb'], [], []
        for at in sc['atoms']:
            r = sc['residues'][at[2]]
            ident = f"{r['comp']}:{r['chain']}:{r['num']}:{at[0]}"
            ids.append(ident)
            info.append(((r['comp'], at[0], at[1]), at[2]))
            dep = C.atom(pdb, ident)
            if dep is None:
                F(f"{sc['key']}: {ident} not in the deposited file")
                continue
            if max(abs(dep[0][k] - at[3 + k]) for k in range(3)) > 6e-4 or dep[2] != at[1]:
                F(f"{sc['key']}: {ident} coordinate or element differs")
            n['scene_atoms'] += 1
        for c in sc['contacts']:
            pa, pb = C.atom(pdb, ids[c['i']]), C.atom(pdb, ids[c['j']])
            if pa is None or pb is None:
                continue
            d = math.dist(pa[0], pb[0])
            (A, ra), (B, rb) = info[c['i']], info[c['j']]
            if abs(d - c['d']) > 1e-4:
                F(f"{sc['key']}: {ids[c['i']]}···{ids[c['j']]} shown {c['d']:.5f}, recomputed {d:.5f}")
            cls = expected_class(A, B, ra == rb, d)
            if c['cls'] != cls:
                F(f"{sc['key']}: class {c['cls']} for {ids[c['i']]}···{ids[c['j']]}, rule gives {cls}")
            if c['basis'] != expected_basis(A, B, cls):
                F(f"{sc['key']}: chemical basis differs for {ids[c['i']]}···{ids[c['j']]}")
            x, y = sorted((ids[c['i']], ids[c['j']]))
            if c['id'] != f"{pdb}.p{sc['protomer']}.{x}~{y}":
                F(f"{sc['key']}: contact ID {c['id']} malformed")
            key = (c['id'], sc['key'])
            if key in scene_rows:
                F(f'duplicate scene pair {key}')
            scene_rows[key] = dict(d=d, cls=cls, basis=c['basis'], pdb=pdb, protomer=sc['protomer'], a1=ids[c['i']], a2=ids[c['j']])
            n['scene_rows'] += 1
        # 7 crop
        crop = ROOT / 'downloads' / 'cif' / f"{sc['key']}.cif"
        try:
            st = gemmi.read_structure(str(crop))
            got = {}
            for ch in st[0]:
                for r in ch:
                    for at in r:
                        got[f"{r.name}:{ch.name}:{r.seqid.num}{r.seqid.icode.strip()}:{at.name}"] = (at.pos.x, at.pos.y, at.pos.z)
            if set(got) != set(ids):
                F(f"{crop.name}: atom set differs from the scene")
            for k, xyz in got.items():
                dep = C.atom(pdb, k)
                if dep is None or math.dist(dep[0], xyz) > 1e-3:
                    F(f"{crop.name}: {k} differs from the deposited coordinates")
            n['crops'] += 1
        except Exception as e:   # noqa: BLE001
            F(f'{crop.name}: {e}')

    # 3 combined CSV
    rows = read_csv(ROOT / 'downloads' / 'all_contacts.csv')
    seen = set()
    for r in rows:
        key = (r['contact_id'], r['view'])
        if key in seen:
            F(f'all_contacts.csv: duplicate row {key}')
        seen.add(key)
        s = scene_rows.get(key)
        if s is None:
            F(f'all_contacts.csv: row not in any scene {key}')
            continue
        if abs(float(r['distance_A']) - s['d']) > 5e-6 + 1e-9 or len(r['distance_A'].split('.')[1]) != 5:
            F(f"all_contacts.csv: {key} distance {r['distance_A']} vs {s['d']:.6f}")
        if (r['contact_class'], r['chemical_basis'], r['atom_1'], r['atom_2']) != (s['cls'], s['basis'], s['a1'], s['a2']):
            F(f'all_contacts.csv: {key} identity/class/basis differs from the scene')
    if seen != set(scene_rows):
        F(f'all_contacts.csv: {len(set(scene_rows) - seen)} scene pairs missing')

    # 4 per-scene CSVs
    by_view = {}
    for r in rows:
        by_view.setdefault(r['view'], []).append(r)
    files = {p.name for p in (ROOT / 'downloads' / 'contacts').glob('*.csv')}
    if files != {f'{v}_contacts.csv' for v in by_view}:
        F('downloads/contacts: file set differs from the scenes')
    for v, rs in by_view.items():
        p = ROOT / 'downloads' / 'contacts' / f'{v}_contacts.csv'
        if p.exists() and read_csv(p) != rs:
            F(f'{p.name}: differs from its rows of all_contacts.csv')

    # 5 unique pairs
    uniq = read_csv(ROOT / 'downloads' / 'tables' / 'atlas_unique_contacts.csv')
    ids_u = [u['contact_id'] for u in uniq]
    if len(ids_u) != len(set(ids_u)):
        F('atlas_unique_contacts.csv: duplicate contact_id')
    want = {}
    for (cid, view), s in scene_rows.items():
        want.setdefault(cid, set()).add(view)
    for u in uniq:
        if set(u['scenes'].split()) != want.get(u['contact_id'], set()):
            F(f"atlas_unique_contacts.csv: scene list differs for {u['contact_id']}")
        s = scene_rows.get((u['contact_id'], u['scenes'].split()[0]))
        if s is None or abs(float(u['distance_A']) - s['d']) > 5e-6 + 1e-9 or u['contact_class'] != s['cls']:
            F(f"atlas_unique_contacts.csv: values differ for {u['contact_id']}")
    if set(ids_u) != set(want):
        F('atlas_unique_contacts.csv: contact set differs from the scenes')
    n['unique_pairs'] = len(ids_u)

    # 6 comparison tables
    atlas = load_js(ROOT / 'data' / 'atlas.js')
    cells = {}
    for part, rws in atlas['compare'].items():
        for row in rws:
            for c in row['cells']:
                k = (row['id'], c['pdb'], str(c['protomer']))
                if k in cells:
                    F(f'compare: duplicate {k}')
                cells[k] = c
                if 'd' in c:
                    pa, pb = C.atom(c['pdb'], c['a']), C.atom(c['pdb'], c['b'])
                    if pa is None or pb is None or abs(math.dist(pa[0], pb[0]) - c['d']) > 1e-4:
                        F(f'compare {k}: value not reproduced')
                    n['compare_cells'] += 1
    matrix = read_csv(ROOT / 'downloads' / 'compare_matrix.csv')
    named = []
    for p in atlas['parts']:
        t = read_csv(ROOT / 'downloads' / 'tables' / f"{p['table']}.csv")
        if any(r['part'] != p['key'] for r in t):
            F(f"{p['table']}.csv: rows from another environment")
        named += t
    key = lambda r: (r['comparison_id'], r['pdb'], r['protomer'])
    if sorted(named, key=key) != sorted(matrix, key=key) or len(named) != len(matrix):
        F('the four atlas_table_*.csv files do not add up to compare_matrix.csv')
    if len(matrix) != len(cells):
        F(f'compare_matrix.csv: {len(matrix)} rows, atlas.js has {len(cells)} cells')
    for r in matrix:
        c = cells.get((r['comparison_id'], r['pdb'], r['protomer']))
        if c is None:
            F(f"compare_matrix.csv: unknown row {r['comparison_id']} {r['pdb']} p{r['protomer']}")
            continue
        if (r['distance_A'] != (f"{c['d']:.4f}" if 'd' in c else '') or r['missing_reason'] != c.get('missing', '')
                or r['atom_1'] != c.get('a', '') or r['atom_2'] != c.get('b', '')):
            F(f"compare_matrix.csv: {r['comparison_id']} {r['pdb']} p{r['protomer']} differs from atlas.js")

    # 8 manifest
    man_path = ROOT / 'MANIFEST.json'
    if man_path.exists():
        man = json.loads(man_path.read_text(encoding='utf-8'))
        for rel, m in man.items():
            p = ROOT / rel
            if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != m['sha256']:
                F(f'MANIFEST.json: {rel} missing or changed')
            n['manifest_files'] += 1
        skip = {'.git', '.github'}
        listed = set(man)
        for p in ROOT.rglob('*'):
            rel = p.relative_to(ROOT).as_posix()
            if p.is_file() and rel != 'MANIFEST.json' and not is_result(rel) and not set(p.relative_to(ROOT).parts) & (skip | {'__pycache__', 'cif_cache'}) and rel not in listed:
                F(f'MANIFEST.json: {rel} not listed')
    else:
        F('MANIFEST.json missing')

    # sources
    differing = {}
    for pdb, s in sources.items():
        if pdb in C.sha and C.sha[pdb] != s['sha256']:
            if a.cif_dir is None:
                F(f'{pdb}: archived input SHA-256 differs from data/sources.json')
            differing[pdb] = f"{s['revision']} -> {C.revisions.get(pdb)}"
    result = dict(status='PASS' if not fails else 'FAIL', mode='archived inputs (strict)' if a.cif_dir is None else f'files in {a.cif_dir}',
                  **n, structure_model_revisions=C.revisions, files_differing_from_build=differing, failures=fails[:200])
    print(json.dumps({k: v for k, v in result.items() if k != 'failures'}, indent=1))
    for f in fails[:40]:
        print('  ', f)
    if a.json:
        Path(a.json).write_text(json.dumps(result, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
