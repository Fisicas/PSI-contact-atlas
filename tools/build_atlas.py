"""Build every scientific output of the PSI Contact Atlas from the archived inputs in build/.

Inputs (all in this repository):
  build/inputs/structures/<PDB>.cif.gz   exact deposited mmCIF files used (SHA-256 of the uncompressed file in
                                         build/config/sources.json)
  build/inputs/ccd/<COMP>.cif            chemical-component definitions (atom names, bonds, carbonyl O)
  build/config/structures.json           entry metadata, protomers, cofactor roles, PsaA/PsaB chains
  build/config/scenes.json               scenes: atoms, measured pairs, labels, camera (curated or derived)
  build/config/release.json              version, date and DOI fields

Outputs: data/atlas.js, data/views/*.js, data/sources.json, data/verification.json, downloads/ (CSV tables,
mmCIF crops, PyMOL scripts) and build/provenance/ (alignment and site-water audit tables).

Every scene atom is read from the deposited file and every distance is computed from it; the build stops on any
inconsistency (missing atom, bond graph different from the CCD, alignment different from the earlier curated
mapping, site water different from the earlier assignment).

    pip install -r build/requirements.txt
    python tools/build_atlas.py
"""
import csv, gzip, hashlib, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path

import gemmi
import numpy as np
from Bio import Align
from Bio.Align import substitution_matrices

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / 'build'
OUT_DATA, OUT_DL, PROV = ROOT / 'data', ROOT / 'downloads', BUILD / 'provenance'

POLAR_SCREEN_A = 3.5
ROUNDING_BOUND_A = 3 ** .5 * 1e-3 + 1e-6   # earlier build stored coordinates rounded to 0.001 Å
FRAME_PAD_A = 1.5
PARTS = ('special_pair', 'P_A', 'A1A', 'A1B')
PART_LABEL = {'special_pair': 'Special pair', 'P_A': 'P_A network', 'A1A': 'A1_A quinone', 'A1B': 'A1_B quinone'}
PART_ROUTE = {'special_pair': 'special-pair', 'P_A': 'pa-network', 'A1A': 'a1a', 'A1B': 'a1b'}
TABLE_NAME = {'special_pair': 'atlas_table_special_pair', 'P_A': 'atlas_table_PA_network', 'A1A': 'atlas_table_A1A',
              'A1B': 'atlas_table_A1B'}
QUINONES = {'PQN', 'PL9', 'A1AGD'}
COFACTOR_COMPS = {'CLA', 'CL0', 'CL7', 'G9R', 'PQN', 'PL9', 'A1AGD'}
COVALENT = {'C': .76, 'N': .71, 'O': .66, 'S': 1.05, 'Mg': 1.41}
MAX_VALENCE = {'C': 4, 'N': 4, 'O': 2, 'S': 2}
CLASS_INFO = {
    'mg': 'Mg–ligand atom separation (coordination geometry not assessed)',
    'polar': f'Polar heavy-atom candidate (N/O···N/O ≤ {POLAR_SCREEN_A} Å; see chemical basis)',
    'water': f'Water-involved polar candidate (≤ {POLAR_SCREEN_A} Å)',
    'acceptor_pair': f'Two oxygen acceptors (carbonyl, ester or backbone C=O) ≤ {POLAR_SCREEN_A} Å; neither carries a hydrogen, '
                     'so not a hydrogen-bond candidate',
    'context': f'Longer polar context (> {POLAR_SCREEN_A} Å)',
    'cs_contact': 'Separation involving carbon or sulfur; element-based only, not evidence of an attractive interaction',
    'intra': 'Intramolecular separation',
}
# Earlier free-text annotation -> class implied by it (used only to list where this build classes a pair differently).
LEGACY = {
    'polar heavy-atom candidate': 'polar', 'Mg coordination': 'mg', 'packing distance': 'cs_contact',
    'intramolecular oxygen separation': 'intra', 'intramolecular keto-to-ester oxygen separation': 'intra',
    'water proximity': 'water', 'water oxygen proximity': 'water', 'water-protein proximity': 'water',
    'longer water context': 'context', 'longer context distance': 'context', 'longer polar context': 'context',
    'context distance beyond 4 A contact screen': 'context',
    'context water-protein distance beyond 3.5 A bridge screen': 'context',
    'donor-compatible proximity': 'polar', 'oxygen proximity; hydrogen geometry unvalidated': 'polar',
    'Heavy-atom candidate only; donor hydrogens, protonation and angles unvalidated': 'polar',
    'Atom type can provide a donor H in a compatible protonation/tautomer; donor-H angle remains unvalidated.': 'polar',
    'Deposited oxygen is an acceptor-side atom; it cannot donate an H in the current heavy-atom model.': 'acceptor_pair',
    'derived by homology': None,
}
THREE = {'ALA': 'Ala', 'ARG': 'Arg', 'ASN': 'Asn', 'ASP': 'Asp', 'CYS': 'Cys', 'GLN': 'Gln', 'GLU': 'Glu',
         'GLY': 'Gly', 'HIS': 'His', 'ILE': 'Ile', 'LEU': 'Leu', 'LYS': 'Lys', 'MET': 'Met', 'PHE': 'Phe',
         'PRO': 'Pro', 'SER': 'Ser', 'THR': 'Thr', 'TRP': 'Trp', 'TYR': 'Tyr', 'VAL': 'Val'}
HYDROXYL = {('SER', 'OG'), ('THR', 'OG1'), ('TYR', 'OH')}
# Atoms that carry a hydrogen in every ordinary protonation state (definite donors).
DONOR = {('SER', 'OG'), ('THR', 'OG1'), ('TYR', 'OH'), ('TRP', 'NE1'), ('ASN', 'ND2'), ('GLN', 'NE2'), ('LYS', 'NZ'),
         ('ARG', 'NE'), ('ARG', 'NH1'), ('ARG', 'NH2')}
# Atoms whose hydrogen depends on protonation state or tautomer.
UNRESOLVED = {('HIS', 'ND1'), ('HIS', 'NE2'), ('ASP', 'OD1'), ('ASP', 'OD2'), ('GLU', 'OE1'), ('GLU', 'OE2')}
PROTEIN_ACCEPTOR_O = {('ASN', 'OD1'), ('GLN', 'OE1')}
_BB = {'N', 'CA', 'C', 'O'}
AA_ATOMS = {k: _BB | set(v.split()) for k, v in {
    'ALA': 'CB', 'ARG': 'CB CG CD NE CZ NH1 NH2', 'ASN': 'CB CG OD1 ND2', 'ASP': 'CB CG OD1 OD2', 'CYS': 'CB SG',
    'GLN': 'CB CG CD OE1 NE2', 'GLU': 'CB CG CD OE1 OE2', 'GLY': '', 'HIS': 'CB CG ND1 CD2 CE1 NE2',
    'ILE': 'CB CG1 CG2 CD1', 'LEU': 'CB CG CD1 CD2', 'LYS': 'CB CG CD CE NZ', 'MET': 'CB CG SD CE',
    'PHE': 'CB CG CD1 CD2 CE1 CE2 CZ', 'PRO': 'CB CG CD', 'SER': 'CB OG', 'THR': 'CB OG1 CG2',
    'TRP': 'CB CG CD1 CD2 NE1 CE2 CE3 CZ2 CZ3 CH2', 'TYR': 'CB CG CD1 CD2 CE1 CE2 CZ OH', 'VAL': 'CB CG1 CG2'}.items()}
CHLORIN_CORE = ['MG', 'NA', 'NB', 'NC', 'ND', 'C1A', 'C2A', 'C3A', 'C4A', 'C1B', 'C2B', 'C3B', 'C4B',
                'C1C', 'C2C', 'C3C', 'C4C', 'C1D', 'C2D', 'C3D', 'C4D', 'CHA', 'CHB', 'CHC', 'CHD']
REF_WATER = 'HOH:A:5011:O'   # 1JB0 water of the P_A network; its position defines the reference site


def fail(msg):
    raise SystemExit('BUILD FAILED: ' + msg)


def split_id(atom_id):
    return tuple(atom_id.split(':'))


def read_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def write_js(path, var, obj):
    path.write_text(f'{var}=' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8', newline='\n')


# ---------------------------------------------------------------- deposited structures
class Source:
    """Index of one deposited mmCIF (first model), keyed by native identity (component:auth chain:auth seq:atom)."""

    def __init__(self, path, expect_sha):
        self.path = Path(path)
        raw = gzip.decompress(self.path.read_bytes()) if self.path.suffix == '.gz' else self.path.read_bytes()
        self.sha = hashlib.sha256(raw).hexdigest()
        if self.sha != expect_sha:
            fail(f'{self.path.name}: SHA-256 differs from build/config/sources.json')
        self.doc = gemmi.cif.read_string(raw.decode('utf-8'))
        st = gemmi.make_structure_from_block(self.doc.sole_block())
        st.setup_entities()
        self.st = st
        self.atoms = defaultdict(list)
        self.waters = []
        for ch in st[0]:
            for r in ch:
                rid = str(r.seqid.num) + (r.seqid.icode.strip() or '')
                for a in r:
                    rec = dict(xyz=np.array([a.pos.x, a.pos.y, a.pos.z]), element=a.element.name,
                               altloc=a.altloc if a.altloc != '\0' else '', occ=a.occ, B=a.b_iso, label_asym=r.subchain)
                    self.atoms[(r.name, ch.name, rid, a.name)].append(rec)
                    if r.name == 'HOH' and a.name == 'O':
                        self.waters.append((f'HOH:{ch.name}:{rid}:O', rec['xyz']))
        self.water_xyz = np.array([w[1] for w in self.waters]) if self.waters else np.zeros((0, 3))

    def get(self, atom_id):
        recs = self.atoms.get(split_id(atom_id))
        return max(recs, key=lambda r: r['occ']) if recs else None

    def polymer(self, chain_name):
        for ch in self.st[0]:
            if ch.name == chain_name:
                pol = ch.get_polymer()
                seq, nums = [], []
                for r in pol:
                    info = gemmi.find_tabulated_residue(r.name)
                    seq.append(info.one_letter_code.upper() if info and info.one_letter_code != ' ' else 'X')
                    nums.append((r.name, str(r.seqid.num) + (r.seqid.icode.strip() or '')))
                return ''.join(seq), nums
        return '', []

    def value(self, tag):
        v = self.doc.sole_block().find_value(tag)
        return None if v in (None, '?', '.') else gemmi.cif.as_string(v)

    def technique(self):
        """Experimental-method fields exactly as deposited (absent fields are omitted, never inferred)."""
        val, b = self.value, self.doc.sole_block()
        method = val('_exptl.method')
        out = dict(method=method)
        if method == 'X-RAY DIFFRACTION':
            out.update(resolution_A=val('_refine.ls_d_res_high'), R_work=val('_refine.ls_R_factor_R_work'),
                       R_free=val('_refine.ls_R_factor_R_free'), space_group=val('_symmetry.space_group_name_H-M'),
                       phasing=val('_refine.pdbx_method_to_determine_struct'), temperature_K=val('_diffrn.ambient_temp'),
                       source=' '.join(x for x in (val('_diffrn_source.pdbx_synchrotron_site'),
                                                   val('_diffrn_source.pdbx_synchrotron_beamline')) if x) or None)
        else:
            rel = b.find(['_pdbx_database_related.db_name', '_pdbx_database_related.db_id', '_pdbx_database_related.content_type'])
            emdb = [gemmi.cif.as_string(r[1]) for r in rel if gemmi.cif.as_string(r[0]) == 'EMDB'
                    and 'associated' in gemmi.cif.as_string(r[2])] if rel else []
            out.update(resolution_A=val('_em_3d_reconstruction.resolution'), resolution_method=val('_em_3d_reconstruction.resolution_method'),
                       particles=val('_em_3d_reconstruction.num_particles'), point_symmetry=val('_em_single_particle_entity.point_symmetry'),
                       microscope=val('_em_imaging.microscope_model'), voltage_kV=val('_em_imaging.accelerating_voltage'),
                       detector=val('_em_image_recording.film_or_detector_model'), emdb=emdb[0] if emdb else None)
        return {k: v for k, v in out.items() if v is not None}

    def revision(self):
        rows = [r for r in self.doc.sole_block().find('_pdbx_audit_revision_history.',
                                                       ['data_content_type', 'major_revision', 'minor_revision', 'revision_date'])
                if gemmi.cif.as_string(r[0]) == 'Structure model']
        last = max(rows, key=lambda r: (int(r[1]), int(r[2])))
        return dict(revision=f'{last[1]}.{last[2]}', revision_date=last[3])

    def crop(self, atom_ids, name):
        """mmCIF of the scene atoms only, with deposited names, numbering, chains and coordinates."""
        keep = {split_id(a) for a in atom_ids}
        st = self.st.clone()
        st.remove_hydrogens()
        model = st[0]
        for ch in model:
            for r in ch:
                rid = str(r.seqid.num) + (r.seqid.icode.strip() or '')
                for i in range(len(r) - 1, -1, -1):
                    if (r.name, ch.name, rid, r[i].name) not in keep:
                        del r[i]
            for i in range(len(ch) - 1, -1, -1):
                if len(ch[i]) == 0:
                    del ch[i]
        for i in range(len(model) - 1, -1, -1):
            if len(model[i]) == 0:
                del model[i]
        for i in range(len(st) - 1, 0, -1):
            del st[i]
        st.name = name
        groups = gemmi.MmcifOutputGroups(False)
        for g in ('block_name', 'entry', 'entity', 'chem_comp', 'atom_type', 'atoms', 'auth_all', 'group_pdb'):
            setattr(groups, g, True)
        return st.make_mmcif_document(groups).as_string()


def ccd_graph(path):
    block = gemmi.cif.read(str(path)).sole_block()
    atoms = {n: e.capitalize() for n, e in zip(block.find_loop('_chem_comp_atom.atom_id'), block.find_loop('_chem_comp_atom.type_symbol'))}
    heavy = {n for n, e in atoms.items() if e != 'H'}
    bonds, double_O = set(), defaultdict(set)
    for a, b, order in zip(block.find_loop('_chem_comp_bond.atom_id_1'), block.find_loop('_chem_comp_bond.atom_id_2'),
                           block.find_loop('_chem_comp_bond.value_order')):
        a, b = gemmi.cif.as_string(a), gemmi.cif.as_string(b)
        if a in heavy and b in heavy:
            bonds.add(frozenset((a, b)))
            if order.upper().startswith('DOUB'):
                for x, y in ((a, b), (b, a)):
                    if atoms[x] == 'O' and atoms[y] == 'C':
                        double_O[x].add(y)
    return dict(heavy=heavy, bonds=bonds, carbonyl_O={o: sorted(c)[0] for o, c in double_O.items()})


# ---------------------------------------------------------------- geometry and chemistry
def infer_bonds(atoms):
    """Covalent bonds inside residues (radii + 0.40 Å), Mg–pyrrole N inside a chlorophyll, peptide C–N."""
    bonds, by_res = [], defaultdict(list)
    for i, a in enumerate(atoms):
        by_res[a['res']].append(i)
    xyz = np.array([a['xyz'] for a in atoms])
    for idx in by_res.values():
        for p in range(len(idx)):
            for q in range(p + 1, len(idx)):
                i, j = idx[p], idx[q]
                ei, ej = atoms[i]['element'], atoms[j]['element']
                d = float(np.linalg.norm(xyz[i] - xyz[j]))
                if 'Mg' in (ei, ej):
                    if (ej if ei == 'Mg' else ei) == 'N' and d < 2.5:
                        bonds.append((i, j, 'coord'))
                    continue
                if .4 < d < COVALENT[ei] + COVALENT[ej] + .40:
                    bonds.append((i, j, 'cov'))
    cs = [i for i, a in enumerate(atoms) if a['atom'] == 'C' and a['kind'] == 'protein']
    ns = [i for i, a in enumerate(atoms) if a['atom'] == 'N' and a['kind'] == 'protein']
    for i in cs:
        for j in ns:
            if atoms[i]['res'] != atoms[j]['res'] and atoms[i]['chain'] == atoms[j]['chain'] and float(np.linalg.norm(xyz[i] - xyz[j])) < 1.75:
                bonds.append((i, j, 'cov'))
    return bonds


def kabsch(P, Q):
    pc, qc = P.mean(0), Q.mean(0)
    U, S, Vt = np.linalg.svd((P - pc).T @ (Q - qc))
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, d]) @ U.T
    return R, qc - R @ pc


def camera_from_view(v):
    """PyMOL view -> (rows of model-to-camera rotation, pivot, tx, ty)."""
    return [[v[0], v[3], v[6]], [v[1], v[4], v[7]], [v[2], v[5], v[8]]], v[12:15], v[9], v[10]


def acceptor_only(x):
    """Oxygen that cannot carry a hydrogen here: any cofactor O, or a backbone / Asn / Gln amide C=O."""
    if x['element'] != 'O':
        return False
    return x['comp'] in COFACTOR_COMPS or (x['comp'] in THREE and (x['atom'] == 'O' or (x['comp'], x['atom']) in PROTEIN_ACCEPTOR_O))


def classify(a, b, d):
    if 'Mg' in (a['element'], b['element']):
        return 'mg'
    if a['res'] == b['res']:
        return 'intra'
    if {'C', 'S'} & {a['element'], b['element']}:
        return 'cs_contact'
    if d > POLAR_SCREEN_A:
        return 'context'
    if 'HOH' in (a['comp'], b['comp']):
        return 'water'
    if acceptor_only(a) and acceptor_only(b):
        return 'acceptor_pair'
    return 'polar'


def is_donor(x):
    if (x['comp'], x['atom']) in DONOR:
        return True
    return x['comp'] in THREE and x['atom'] == 'N' and x['comp'] != 'PRO'   # backbone N–H


def chemical_basis(a, b, cls):
    """Short statement of what the atom types allow; nothing here is a hydrogen-bond assignment."""
    if cls == 'mg':
        return 'Mg–ligand separation; coordination not assessed'
    if cls == 'intra':
        return 'same residue'
    if cls == 'cs_contact':
        return 'involves C or S; no polar interpretation'
    if cls == 'context':
        return f'beyond the {POLAR_SCREEN_A} Å screen'
    if cls == 'water':
        return 'water-involved; water can donate or accept'
    if cls == 'acceptor_pair':
        return 'acceptor–acceptor; neither atom carries a hydrogen'
    if is_donor(a) or is_donor(b):
        return 'donor–acceptor compatible'
    if (a['comp'], a['atom']) in UNRESOLVED or (b['comp'], b['atom']) in UNRESOLVED:
        return 'unresolved; depends on protonation state or tautomer'
    return 'unresolved'


def residue_label(comp, num):
    return (THREE.get(comp, comp) + num) if comp != 'HOH' else 'HOH' + num


def contact_id(pdb, protomer, a1, a2):
    x, y = sorted((a1, a2))
    return f'{pdb}.p{protomer}.{x}~{y}'


def comparison_id(part, rd):
    if rd.get('from_water'):
        return f"{part}.site_water~{rd['subunit']}{rd['ref_pos']}.{rd['partner_atom'].replace(' ', '_')}"
    left = f"{part}.{rd['cof_role']}.{rd['cof_atom'].replace(' ', '_')}"
    if rd['partner'] == 'site-water':
        return left + '~site_water'
    return f"{left}~{rd['subunit']}{rd['ref_pos']}.{rd['partner_atom'].replace(' ', '_')}"


# ---------------------------------------------------------------- build
def main():
    release = read_json(BUILD / 'config' / 'release.json')
    src_cfg = read_json(BUILD / 'config' / 'sources.json')
    structs = read_json(BUILD / 'config' / 'structures.json')
    scenes = read_json(BUILD / 'config' / 'scenes.json')
    for d in (OUT_DATA / 'views', OUT_DL / 'contacts', OUT_DL / 'cif', OUT_DL / 'tables', PROV):
        d.mkdir(parents=True, exist_ok=True)
    for d in (OUT_DATA / 'views', OUT_DL / 'contacts', OUT_DL / 'cif'):   # no stale files from earlier builds
        for f in d.iterdir():
            f.unlink()

    prot_meta = {(s['pdb'], p['number']): p for s in structs for p in s['protomers']}
    scene_keys = {k for s in structs for p in s['protomers'] for k in p['views']}
    if scene_keys != {sc['key'] for sc in scenes}:
        fail('structures.json views and scenes.json differ')
    sources = {p: Source(BUILD / c['file'], c['sha256']) for p, c in sorted(src_cfg.items())}
    ccd = {f.stem: ccd_graph(f) for f in sorted((BUILD / 'inputs' / 'ccd').glob('*.cif'))}
    print('sources read:', len(sources))

    # ---- PsaA/PsaB alignment to 1JB0 numbering
    aligner = Align.PairwiseAligner(mode='global')
    aligner.substitution_matrix = substitution_matrices.load('BLOSUM62')
    aligner.open_gap_score, aligner.extend_gap_score = -10, -.5
    ref = sources['1JB0']
    ref_seq = {'PsaA': ref.polymer('A'), 'PsaB': ref.polymer('B')}
    to_ref, from_ref, align_report, align_rows = {}, {}, {}, []
    for (pdb, num), p in prot_meta.items():
        for sub, chain in (('PsaA', p['psaA']), ('PsaB', p['psaB'])):
            if (pdb, chain) in to_ref:
                continue
            seq, nums = sources[pdb].polymer(chain)
            rseq, rnums = ref_seq[sub]
            aln = aligner.align(seq, rseq)[0]
            fwd, back, ident = {}, {}, 0
            for (s0, s1), (r0, _r1) in zip(*aln.aligned):
                for k in range(s1 - s0):
                    nat, rr = nums[s0 + k], rnums[r0 + k]
                    fwd[nat[1]] = (rr[1], rr[0])
                    back[rr[1]] = nat
                    ident += seq[s0 + k] == rseq[r0 + k]
                    align_rows.append([pdb, chain, sub, nat[0], nat[1], rr[0], rr[1]])
            to_ref[(pdb, chain)], from_ref[(pdb, chain)] = fwd, back
            align_report[f'{pdb}:{chain}'] = dict(subunit=sub, score=float(aln.score), observed_residues=len(seq),
                                                  aligned=len(fwd), identity_fraction=round(ident / max(1, len(fwd)), 4))
    align_checks = []
    for sc in scenes:
        for pos, (comp, _model, resnum) in (sc.get('earlier_mapped_residues') or {}).items():
            got = from_ref[(sc['pdb'], prot_meta[(sc['pdb'], sc['protomer'])]['psaA'])].get(pos)
            if got != (comp, resnum):
                fail(f"alignment disagrees with the earlier curated mapping for {sc['key']} position {pos}")
            align_checks.append(pos)
    print('alignment cross-checks:', len(align_checks), 'all agree')

    # ---- scenes
    verification = dict(views={}, class_changes=[], rounding_changes=[], bond_graph=[], valence_warnings=[])
    all_rows, atlas_views = [], {}
    max_dev = max_ddist = 0.0
    for sc in scenes:
        key, pdb, num, part = sc['key'], sc['pdb'], sc['protomer'], sc['part']
        src, pm = sources[pdb], prot_meta[(pdb, num)]
        cof_roles = {c['identity']: role for role, c in pm['cofactors'].items() if c}
        atoms, index, res_list, res_index = [], {}, [], {}
        for aid in sc['atoms']:
            comp, chain, resn, name = split_id(aid)
            s = src.get(aid)
            if s is None:
                fail(f'{key}: {aid} not found in the deposited file')
            rid = f'{comp}:{chain}:{resn}'
            if rid not in res_index:
                res_index[rid] = len(res_list)
                res_list.append(dict(id=rid, comp=comp, chain=chain, num=resn, label_asym=s['label_asym'],
                                     kind='water' if comp == 'HOH' else ('cofactor' if comp not in THREE else 'protein'),
                                     role=cof_roles.get(rid, ''), label=residue_label(comp, resn)))
            index[aid] = len(atoms)
            atoms.append(dict(id=aid, comp=comp, chain=chain, atom=name, element=s['element'], xyz=[float(x) for x in s['xyz']],
                              res=res_index[rid], kind=res_list[res_index[rid]]['kind'], occ=s['occ'], B=s['B'], altloc=s['altloc']))
        bonds = infer_bonds(atoms)
        for r_i, r in enumerate(res_list):
            if r['comp'] in ccd:
                present = {a['atom'] for a in atoms if a['res'] == r_i}
                inferred = {frozenset((atoms[i]['atom'], atoms[k]['atom'])) for i, k, t in bonds
                            if t == 'cov' and atoms[i]['res'] == r_i and atoms[k]['res'] == r_i}
                expected = {b for b in ccd[r['comp']]['bonds'] if b <= present and 'MG' not in b}
                n_coord = sum(1 for i, k, t in bonds if t == 'coord' and atoms[i]['res'] == r_i)
                if 'MG' in present and n_coord != 4:
                    fail(f"{key}: {r['id']} has {n_coord} Mg–pyrrole N lines, expected 4")
                if inferred != expected:
                    fail(f"{key}: inferred bonds for {r['id']} differ from the CCD")
                verification['bond_graph'].append(dict(view=key, residue=r['id'], atoms_present=len(present),
                                                       ccd_heavy_atoms=len(ccd[r['comp']]['heavy'])))
        deg = Counter()
        for i, k, t in bonds:
            if t == 'cov':
                deg[i] += 1
                deg[k] += 1
        verification['valence_warnings'] += [dict(view=key, atom=atoms[i]['id'], bonds=n) for i, n in deg.items()
                                             if n > MAX_VALENCE.get(atoms[i]['element'], 4)]

        contacts = []
        for c in sc['contacts']:
            a1, a2 = c['atom_1'], c['atom_2']
            if a1 not in index or a2 not in index:
                fail(f'{key}: contact endpoint missing from scene: {a1} {a2}')
            A, Bt = atoms[index[a1]], atoms[index[a2]]
            d = float(np.linalg.norm(np.array(A['xyz']) - np.array(Bt['xyz'])))
            if c.get('earlier_distance_A') is not None:
                dd = abs(d - c['earlier_distance_A'])
                max_ddist = max(max_ddist, dd)
                if dd > ROUNDING_BOUND_A:
                    fail(f'{key}: {a1}–{a2} differs from the earlier curated value by {dd:.4f} Å')
                if f'{d:.2f}' != f"{c['earlier_distance_A']:.2f}":
                    verification['rounding_changes'].append(dict(view=key, atom_1=a1, atom_2=a2, earlier_display=f"{c['earlier_distance_A']:.2f}",
                                                                 now_display=f'{d:.2f}'))
            cls = classify(A, Bt, d)
            if c['curated_annotation'] not in LEGACY:
                fail(f"{key}: unmapped curated annotation {c['curated_annotation']!r}")
            implied = LEGACY[c['curated_annotation']]
            if implied is not None and implied != cls:
                verification['class_changes'].append(dict(view=key, atom_1=a1, atom_2=a2, distance_A=round(d, 4),
                                                          earlier_annotation=c['curated_annotation'], class_now=cls))
            basis = chemical_basis(A, Bt, cls)
            cid = contact_id(pdb, num, a1, a2)
            contacts.append(dict(i=index[a1], j=index[a2], d=round(d, 5), cls=cls, basis=basis, id=cid, src=c['curated_annotation']))
            all_rows.append(dict(contact_id=cid, view=key, pdb=pdb, protomer=num, part=part, atom_1=a1, atom_2=a2,
                                 label_asym_1=A_label(src, a1), label_asym_2=A_label(src, a2), distance_A=f'{d:.5f}',
                                 contact_class=cls, chemical_basis=basis, curated_annotation=c['curated_annotation'],
                                 occupancy_1=A['occ'], occupancy_2=Bt['occ'], B_iso_1=round(A['B'], 2), B_iso_2=round(Bt['B'], 2)))

        labels = []
        for lb in sc['labels']:
            if lb['atom'] not in index:
                fail(f"{key}: label anchor {lb['atom']} is not a scene atom")
            ai = index[lb['atom']]
            if lb.get('role'):
                labels.append(dict(a=ai, text=lb['role'], kind='role'))
            else:
                comp, chain, resn, _ = split_id(lb['atom'])
                labels.append(dict(a=ai, text=residue_label(comp, resn), chain=chain, kind='water' if comp == 'HOH' else 'residue'))

        cam = sc['camera']
        M, pivot, tx, ty = camera_from_view(cam['view'])
        Mn = np.array(M)
        pc = (np.array([a['xyz'] for a in atoms]) - np.array(pivot)) @ Mn.T
        roi = sorted({c['i'] for c in contacts} | {c['j'] for c in contacts} | {l['a'] for l in labels})
        centre_cam = (pc[roi].min(0) + pc[roi].max(0)) / 2
        centre = (np.array(pivot) + Mn.T @ centre_cam).tolist()

        def extents(idx):
            q = pc[idx] - centre_cam
            return [round(float(np.sqrt(q[:, 0] ** 2 + q[:, 2] ** 2).max()) + FRAME_PAD_A, 3), round(float(np.abs(q[:, 1]).max()) + FRAME_PAD_A, 3)]

        data = dict(
            key=key, pdb=pdb, protomer=num, part=part, origin=sc['origin'], template=sc.get('template'),
            residues=res_list,
            atoms=[[a['atom'], a['element'], a['res'], *[round(x, 3) for x in a['xyz']], a['occ'], round(a['B'], 2)] for a in atoms],
            bonds=[[i, k, 1 if t == 'coord' else 0] for i, k, t in bonds],
            contacts=contacts, labels=labels,
            camera=dict(rot=M, pivot=pivot, tx=tx, ty=ty, scale=cam['scale'], width=cam['width'], height=cam['height'],
                        spin_sign=cam['spin_sign'], still_frame=cam['still_frame'],
                        still_angle_deg=round(cam['still_frame'] * 360 / cam['frames'], 3),
                        centre=[round(x, 4) for x in centre], roi=extents(roi), whole=extents(list(range(len(atoms)))),
                        pymol_view=[round(x, 6) for x in cam['view']]),
            pivot_atom=sc['pivot_atom'], notes=sc.get('notes') or [], water_rule=sc.get('water_rule'),
            downloads=dict(contacts=f'downloads/contacts/{key}_contacts.csv', cif=f'downloads/cif/{key}.cif', pymol=f'downloads/pymol/{key}.pml'),
        )
        write_js(OUT_DATA / 'views' / f'{key}.js', 'window.PSI_VIEWS=window.PSI_VIEWS||{};PSI_VIEWS[' + json.dumps(key) + ']', data)
        (OUT_DL / 'cif' / f'{key}.cif').write_text(src.crop(sc['atoms'], key), encoding='utf-8', newline='\n')
        verification['views'][key] = dict(atoms=len(atoms), bonds=len(bonds), contacts=len(contacts), labels=len(labels))
        atlas_views[key] = dict(key=key, part=part, atoms=len(atoms), contacts=len(contacts), origin=sc['origin'],
                                classes=dict(Counter(c['cls'] for c in contacts)),
                                shortest=min((c['d'] for c in contacts if c['cls'] in ('polar', 'water')), default=None),
                                overlap_frames=sc.get('overlap_frames'), roi=data['camera']['roi'])
        write_csv(OUT_DL / 'contacts' / f'{key}_contacts.csv', [r for r in all_rows if r['view'] == key])
    print(f'scenes: {len(scenes)}  scene contact rows {len(all_rows)}  max change vs earlier values {max_ddist:.2e} Å')
    write_csv(OUT_DL / 'all_contacts.csv', all_rows)

    # ---- unique physical atom pairs (a pair shown in two scenes is one observation)
    unique = {}
    for r in all_rows:
        u = unique.setdefault(r['contact_id'], {k: r[k] for k in ('contact_id', 'pdb', 'protomer', 'atom_1', 'atom_2', 'label_asym_1',
                                                                  'label_asym_2', 'distance_A', 'contact_class', 'chemical_basis',
                                                                  'occupancy_1', 'occupancy_2', 'B_iso_1', 'B_iso_2')} | dict(scenes=[]))
        if u['distance_A'] != r['distance_A'] or u['contact_class'] != r['contact_class']:
            fail(f"{r['contact_id']}: differs between scenes")
        u['scenes'].append(r['view'])
    write_csv(OUT_DL / 'tables' / 'atlas_unique_contacts.csv', [dict(u, scenes=' '.join(u['scenes'])) for u in unique.values()])
    print('unique atom pairs:', len(unique))

    # ---- reference water site (1JB0 HOH5011) per protomer
    ref_pa = prot_meta[('1JB0', 1)]['cofactors']['P_A']['identity']
    ref_core = {n: ref.get(f'{ref_pa}:{n}')['xyz'] for n in CHLORIN_CORE if ref.get(f'{ref_pa}:{n}') is not None}
    ref_water_xyz = ref.get(REF_WATER)['xyz']
    water_sites, water_checks = {}, []
    earlier_water = {(sc['pdb'], sc['protomer']): sc.get('earlier_site_water') for sc in scenes if sc['part'] == 'P_A'}
    for (pdb, num), p in prot_meta.items():
        src = sources[pdb]
        pa = p['cofactors']['P_A']['identity']
        common = [n for n in CHLORIN_CORE if n in ref_core and src.get(f'{pa}:{n}') is not None]
        P, Q = np.array([ref_core[n] for n in common]), np.array([src.get(f'{pa}:{n}')['xyz'] for n in common])
        R, t = kabsch(P, Q)
        rmsd = float(np.sqrt(((P @ R.T + t - Q) ** 2).sum(1).mean()))
        site = R @ ref_water_xyz + t
        dist = np.linalg.norm(src.water_xyz - site, axis=1) if len(src.water_xyz) else np.array([])
        order = np.argsort(dist) if len(dist) else []
        w_id = w_off = nxt = None
        if len(dist) and dist[order[0]] <= 3.0:
            w_id, w_off = src.waters[order[0]][0], float(dist[order[0]])
        if len(dist) > 1:
            nxt = float(dist[order[1]]) if w_id else float(dist[order[0]])
        ew = earlier_water.get((pdb, num))
        if ew is not None and ew != w_id:
            fail(f'{pdb} p{num}: site water {w_id} differs from the earlier assignment {ew}')
        water_sites[(pdb, num)] = w_id
        water_checks.append(dict(pdb=pdb, protomer=num, core_atoms=len(common), core_rmsd_A=round(rmsd, 4), water=w_id,
                                 offset_A=round(w_off, 3) if w_off is not None else None,
                                 next_water_offset_A=round(nxt, 3) if nxt is not None else None, earlier_water=ew))
    print('site waters:', sum(1 for w in water_sites.values() if w), '/', len(water_sites))

    # ---- homologous-contact comparison across protomers
    compare = {}
    for part in ('P_A', 'special_pair', 'A1A', 'A1B'):
        rowdefs = {}
        for sc in (x for x in scenes if x['part'] == part):
            pm = prot_meta[(sc['pdb'], sc['protomer'])]
            cof = {c['identity']: r for r, c in pm['cofactors'].items() if c}
            chains = {pm['psaA']: 'PsaA', pm['psaB']: 'PsaB'}
            wsite = water_sites.get((sc['pdb'], sc['protomer']))
            for c in sc['contacts']:
                ends = []
                for aid in (c['atom_1'], c['atom_2']):
                    comp, chain, resn, name = split_id(aid)
                    rid = f'{comp}:{chain}:{resn}'
                    if rid in cof:
                        ends.append(('cof', cof[rid], comp, name))
                    elif comp == 'HOH':
                        ends.append(('wat', 'site' if aid == wsite else None, comp, name))
                    elif name.startswith('C') and comp in THREE:
                        ends.append(None)
                    elif chain in chains and resn in to_ref[(sc['pdb'], chain)]:
                        refnum, refcomp = to_ref[(sc['pdb'], chain)][resn]
                        ends.append(('prot', chains[chain], refnum, 'hydroxyl O' if (comp, name) in HYDROXYL else name, refcomp))
                    else:
                        ends.append(None)
                if None in ends:
                    continue
                kinds = sorted(e[0] for e in ends)
                cofe = [e for e in ends if e[0] == 'cof']
                if kinds == ['cof', 'cof']:
                    continue
                if kinds in (['cof', 'prot'], ['cof', 'wat']):
                    ce, pe = cofe[0], next(e for e in ends if e[0] != 'cof')
                    if pe[0] == 'wat' and pe[1] != 'site':
                        continue
                    catom = 'carbonyl O' if ce[2] in QUINONES else ce[3]
                    if pe[0] == 'prot':
                        rowdefs.setdefault((ce[1], catom, pe[1], pe[2], pe[3]), dict(cof_role=ce[1], cof_atom=catom, partner='prot', subunit=pe[1],
                                                                                   ref_pos=pe[2], ref_comp=pe[4], partner_atom=pe[3]))
                    else:
                        rowdefs.setdefault((ce[1], catom, 'site-water'), dict(cof_role=ce[1], cof_atom=catom, partner='site-water'))
                elif kinds == ['prot', 'wat'] and ends[[e[0] for e in ends].index('wat')][1] == 'site':
                    pe = next(e for e in ends if e[0] == 'prot')
                    rowdefs.setdefault(('site-water', pe[1], pe[2], pe[3]), dict(cof_role=None, partner='prot', subunit=pe[1], ref_pos=pe[2],
                                                                               ref_comp=pe[4], partner_atom=pe[3], from_water=True))
        rows = []
        for rd in rowdefs.values():
            cells = []
            for (pdb, num), pm in prot_meta.items():
                src, cell = sources[pdb], dict(pdb=pdb, protomer=num)
                if rd.get('from_water'):
                    w = water_sites.get((pdb, num))
                    ends1 = [w] if w else []
                    if not w:
                        cell['missing'] = 'no deposited water meets the site rule (≤ 3 Å from the reference position)'
                else:
                    cid = pm['cofactors'][rd['cof_role']]['identity']
                    comp = cid.split(':')[0]
                    names = sorted(ccd[comp]['carbonyl_O']) if rd['cof_atom'] == 'carbonyl O' else [rd['cof_atom']]
                    ends1 = [f'{cid}:{o}' for o in names if src.get(f'{cid}:{o}') is not None]
                    if not ends1:
                        cell['missing'] = f'{rd["cof_atom"]} not modelled in {cid}'
                ends2 = []
                if rd['partner'] == 'site-water':
                    w = water_sites.get((pdb, num))
                    if w:
                        ends2 = [w]
                    else:
                        cell.setdefault('missing', 'no deposited water meets the site rule (≤ 3 Å from the reference position)')
                else:
                    chain = pm['psaA'] if rd['subunit'] == 'PsaA' else pm['psaB']
                    nat = from_ref[(pdb, chain)].get(rd['ref_pos'])
                    if nat is None:
                        cell.setdefault('missing', f'1JB0 position {rd["ref_pos"]} not aligned to an observed residue')
                    else:
                        comp, resn = nat
                        cell['partner'] = f'{THREE.get(comp, comp)}{resn}.{chain}'
                        names = [n for (c2, n) in HYDROXYL if c2 == comp] if rd['partner_atom'] == 'hydroxyl O' else [rd['partner_atom']]
                        ends2 = [f'{comp}:{chain}:{resn}:{n}' for n in names if src.get(f'{comp}:{chain}:{resn}:{n}') is not None]
                        if not ends2:
                            label = f'{THREE.get(comp, comp)}{resn}'
                            if names and set(names) <= AA_ATOMS.get(comp, set()):
                                cell.setdefault('missing', f'{label} {"/".join(names)} not modelled in the deposited coordinates')
                            else:
                                cell.setdefault('missing', f'residue differs: {label} has no {rd["partner_atom"]}')
                if 'missing' not in cell and ends1 and ends2:
                    best = min(((float(np.linalg.norm(src.get(x)['xyz'] - src.get(y)['xyz'])), x, y) for x in ends1 for y in ends2))
                    cell.update(d=round(best[0], 4), a=best[1], b=best[2])
                    alt = [e for e in (best[1], best[2]) if src.get(e)['altloc']]
                    if alt:
                        cell['altloc'] = alt
                cells.append(cell)
            rows.append(dict(rd, id=comparison_id(part, rd), cells=cells))

        def sortkey(r):
            role_order = {'P_A': 0, 'P_B': 1, 'A1_A': 0, 'A1_B': 0, None: 2}
            return (role_order.get(r.get('cof_role'), 3), r.get('partner') != 'prot' and not r.get('from_water'), r.get('subunit') or '',
                    int(''.join(ch for ch in str(r.get('ref_pos') or '0') if ch.isdigit()) or 0), r.get('cof_atom') or '')
        rows.sort(key=sortkey)
        compare[part] = rows
        print(f'compare {part}: {len(rows)} homologous contacts')

    header = ['comparison_id', 'part', 'cofactor_role', 'cofactor_atom', 'partner_subunit', '1JB0_position', '1JB0_residue', 'partner_atom',
              'pdb', 'protomer', 'native_partner', 'atom_1', 'atom_2', 'distance_A', 'missing_reason']
    all_cmp = []
    for part, rows in compare.items():
        part_rows = [[r['id'], part, r.get('cof_role') or 'site water', r.get('cof_atom', ''), r.get('subunit', ''), r.get('ref_pos', ''),
                      r.get('ref_comp', ''), r.get('partner_atom', 'site water'), c['pdb'], c['protomer'], c.get('partner', ''),
                      c.get('a', ''), c.get('b', ''), f"{c['d']:.4f}" if 'd' in c else '', c.get('missing', '')] for r in rows for c in r['cells']]
        all_cmp += part_rows
        write_rows(OUT_DL / 'tables' / f'{TABLE_NAME[part]}.csv', header, part_rows)
    write_rows(OUT_DL / 'compare_matrix.csv', header, all_cmp)

    # ---- provenance tables
    write_rows(PROV / 'alignment_to_1JB0.csv', ['pdb', 'chain', 'subunit', 'native_residue', 'native_number', '1JB0_residue', '1JB0_number'], align_rows)
    write_rows(PROV / 'site_water.csv', list(water_checks[0].keys()), [list(w.values()) for w in water_checks])

    # ---- atlas
    structures = []
    for s in structs:
        src = sources[s['pdb']]
        ss = {k: v for k, v in s.items() if k != 'protomers'}
        ss['technique'] = src.technique()
        ss['validation_report'] = f"https://files.rcsb.org/pub/pdb/validation_reports/{s['pdb'].lower()[1:3]}/{s['pdb'].lower()}/{s['pdb'].lower()}_full_validation.pdf"
        ss['protomers'] = []
        for p in s['protomers']:
            pp = {k: v for k, v in p.items() if k != 'views'}
            pp['views'] = [atlas_views[k] for k in p['views']]
            wc = next(w for w in water_checks if w['pdb'] == s['pdb'] and w['protomer'] == p['number'])
            pp['site_water'], pp['site_water_offset_A'] = wc['water'], wc['offset_A']
            pp['site_water_source'] = (('earlier assignment reproduced' if wc['earlier_water'] else 'site rule applied in this build')
                                       if wc['water'] else 'no deposited water meets the site rule')
            ss['protomers'].append(pp)
        structures.append(ss)
    sources_out = {p: dict(src.revision(), sha256=src.sha, url=src_cfg[p]['url'], file=src_cfg[p]['file'], retrieved=src_cfg[p]['retrieved'])
                   for p, src in sources.items()}
    counts = dict(structures=len(structures), protomers=len(prot_meta), views=len(scenes), contacts=len(all_rows), unique_contacts=len(unique),
                  scene_atoms=sum(v['atoms'] for v in verification['views'].values()),
                  derived_views=sum(1 for sc in scenes if sc['origin'] == 'derived'))
    atlas = dict(version=release['version'], release_date=release['release_date'], doi=release.get('version_doi'),
                 concept_doi=release.get('concept_doi'), citation=release['citation'], recheck=release.get('recheck'),
                 built=release['release_date'],
                 parts=[dict(key=k, label=PART_LABEL[k], route=PART_ROUTE[k], table=TABLE_NAME[k]) for k in PARTS],
                 classes=CLASS_INFO, polar_screen_A=POLAR_SCREEN_A, structures=structures, compare=compare, counts=counts,
                 verification=dict(atoms=counts['scene_atoms'], contacts=len(all_rows), unique_contacts=len(unique),
                                   max_distance_deviation_A=max_ddist, alignment_crosschecks=len(align_checks),
                                   cofactor_graphs=len(verification['bond_graph']), class_changes=verification['class_changes'],
                                   rounding_changes=verification['rounding_changes'], site_water=water_checks),
                 sources={p: dict(revision=v['revision'], revision_date=v['revision_date']) for p, v in sources_out.items()})
    write_js(OUT_DATA / 'atlas.js', 'window.PSI_ATLAS', atlas)
    (OUT_DATA / 'sources.json').write_text(json.dumps(sources_out, indent=1) + '\n', encoding='utf-8', newline='\n')
    verification.update(status='PASS', built=atlas['built'], counts=counts, max_distance_change_vs_earlier_A=max_ddist,
                        alignment=align_report, alignment_crosschecks=len(align_checks), site_water=water_checks,
                        tools=dict(python=sys.version.split()[0], gemmi=gemmi.__version__, numpy=np.__version__,
                                   biopython=__import__('Bio').__version__))
    verification.pop('bond_graph_detail', None)
    (OUT_DATA / 'verification.json').write_text(json.dumps(verification, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')

    sys.path.insert(0, str(ROOT / 'tools'))
    import make_pymol_scripts
    make_pymol_scripts.main()
    print(f"class changes vs earlier annotation: {len(verification['class_changes'])}; 0.01 Å display changes: {len(verification['rounding_changes'])}")
    print('BUILD PASS')


def A_label(src, aid):
    return src.get(aid)['label_asym']


def write_csv(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def write_rows(path, header, rows):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(header)
        w.writerows(rows)


if __name__ == '__main__':
    main()
