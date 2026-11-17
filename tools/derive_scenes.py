"""Add a newly released PDB entry to the atlas by a documented rule (no hand selection).

For each protomer and each environment (special pair, P_A network, A1A, A1B) a curated template scene is chosen:
same organism if possible, then the same deposited cofactor components, then the best resolution. The new scene
contains the residues and atom pairs at the homologous positions (PsaA/PsaB aligned to 1JB0 numbering), the same
cofactor atoms, the deposited waters chosen by the same water rules, and the template camera superposed on the
new coordinates. Pairs whose atoms are absent in the new model are dropped and listed in the scene notes.

    python tools/derive_scenes.py add 9OY9 path/to/9OY9.cif --condition "..." --description "..."
    python tools/derive_scenes.py check     # re-derive curated scenes from other curated scenes and compare

Writes build/inputs/structures/<PDB>.cif.gz and updates build/config/{sources,structures,scenes}.json.
Run tools/build_atlas.py afterwards.
"""
import argparse, gzip, hashlib, json, sys
from datetime import date
from pathlib import Path

import gemmi
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_atlas as BA  # noqa: E402

CFG = BA.BUILD / 'config'
CHL = {'CLA', 'CL0', 'CL7', 'G9R'}
DIAGNOSTIC = ['MG', 'O1A', 'O2A', 'O1D', 'O2D', 'OBD']   # special-pair water rule: waters within 5 Å of these P_A/P_B atoms
PIGMENT_NAME = {'CLA': 'Chl a (deposited CLA)', 'CL0': 'Chl a′ (deposited CL0)', 'G9R': 'Chl d′ (deposited G9R)',
                'CL7': 'Chl d (deposited CL7)', 'PQN': 'Phylloquinone', 'PL9': 'PQ-9', 'A1AGD': 'DMPBQ'}
ROLE_SUBUNIT = {'P_A': 'PsaA', 'P_B': 'PsaB', 'A1_A': 'PsaA', 'A1_B': 'PsaB'}
# 1JB0 anchors used to recognise each cofactor: P_A/P_B Mg ligands, A1 Leu backbone N
ANCHOR = {'P_A': ('680', 'NE2'), 'P_B': ('660', 'NE2'), 'A1_A': ('722', 'N'), 'A1_B': ('706', 'N')}
PART_ROLES = {'special_pair': ['P_A', 'P_B'], 'P_A': ['P_A'], 'A1A': ['A1_A'], 'A1B': ['A1_B']}


def load():
    return (BA.read_json(CFG / 'sources.json'), BA.read_json(CFG / 'structures.json'), BA.read_json(CFG / 'scenes.json'))


def save(sources, structs, scenes):
    for name, obj in (('sources', sources), ('structures', structs), ('scenes', scenes)):
        (CFG / f'{name}.json').write_text(json.dumps(obj, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')


class Mapper:
    """1JB0-numbering alignment for any PsaA/PsaB chain."""

    def __init__(self, ref):
        from Bio import Align
        from Bio.Align import substitution_matrices
        self.al = Align.PairwiseAligner(mode='global')
        self.al.substitution_matrix = substitution_matrices.load('BLOSUM62')
        self.al.open_gap_score, self.al.extend_gap_score = -10, -.5
        self.ref = {'PsaA': ref.polymer('A'), 'PsaB': ref.polymer('B')}
        self.cache = {}

    def maps(self, src, pdb, chain, sub):
        k = (pdb, chain)
        if k not in self.cache:
            seq, nums = src.polymer(chain)
            rseq, rnums = self.ref[sub]
            a = self.al.align(seq, rseq)[0]
            fwd, back = {}, {}
            for (s0, s1), (r0, _r) in zip(*a.aligned):
                for i in range(s1 - s0):
                    fwd[nums[s0 + i][1]] = rnums[r0 + i][1]
                    back[rnums[r0 + i][1]] = nums[s0 + i]
            self.cache[k] = (fwd, back)
        return self.cache[k]


def find_protomers(src, pdb, mapper):
    """PsaA/PsaB chains from the entity descriptions, paired by P700 proximity; cofactor roles from 1JB0 anchors."""
    block = src.doc.sole_block()
    desc = {gemmi.cif.as_string(r[0]): gemmi.cif.as_string(r[1]) for r in block.find('_entity.', ['id', 'pdbx_description'])}
    ent_of = {}
    for r in block.find('_struct_asym.', ['id', 'entity_id']):
        ent_of[gemmi.cif.as_string(r[0])] = gemmi.cif.as_string(r[1])
    chains = {'PsaA': [], 'PsaB': []}
    for ch in src.st[0]:
        pol = ch.get_polymer()
        if not len(pol):
            continue
        d = desc.get(ent_of.get(pol[0].subchain, ''), '').lower()
        if 'apoprotein a1' in d or 'psaa' in d:
            chains['PsaA'].append(ch.name)
        elif 'apoprotein a2' in d or 'psab' in d:
            chains['PsaB'].append(ch.name)
    prots = []
    for n, ca in enumerate(chains['PsaA'], 1):
        roles = {}
        for role in ('P_A', 'A1_A'):
            roles[role] = locate(src, pdb, ca, 'PsaA', role, mapper)
        # PsaB partner: the chain whose P_B Mg lies closest to this P_A Mg
        pa_mg = src.get(roles['P_A'] + ':MG')['xyz']
        best = None
        for cb in chains['PsaB']:
            pb = locate(src, pdb, cb, 'PsaB', 'P_B', mapper)
            d = float(np.linalg.norm(src.get(pb + ':MG')['xyz'] - pa_mg))
            if best is None or d < best[0]:
                best = (d, cb, pb)
        if best[0] > 8:
            raise SystemExit(f'{pdb}: no PsaB partner for chain {ca}')
        roles['P_B'] = best[2]
        roles['A1_B'] = locate(src, pdb, best[1], 'PsaB', 'A1_B', mapper)
        prots.append(dict(number=n, psaA=ca, psaB=best[1], roles=roles))
    return prots


def locate(src, pdb, chain, sub, role, mapper):
    pos, atom = ANCHOR[role]
    _fwd, back = mapper.maps(src, pdb, chain, sub)
    comp, num = back[pos]
    anchor = src.get(f'{comp}:{chain}:{num}:{atom}')['xyz']
    best = None
    for (c, ch, r, a), recs in src.atoms.items():
        if role.startswith('P') and not (c in CHL and a == 'MG'):
            continue
        if role.startswith('A1') and not (c in BA.QUINONES and a.startswith('O')):
            continue
        d = float(np.linalg.norm(recs[0]['xyz'] - anchor))
        if best is None or d < best[0]:
            best = (d, f'{c}:{ch}:{r}')
    limit = 3.0 if role.startswith('P') else 3.6
    if best is None or best[0] > limit:
        raise SystemExit(f'{pdb} {role}: no cofactor within {limit} Å of the 1JB0-{pos} {atom} position ({best})')
    return best[1]


def choose_template(scenes, structs, part, organism, comps):
    by_pdb = {s['pdb']: s for s in structs}
    best = None
    for sc in scenes:
        if sc['part'] != part or sc['origin'] != 'curated':
            continue
        s = by_pdb[sc['pdb']]
        p = next(p for p in s['protomers'] if p['number'] == sc['protomer'])
        tcomps = [p['cofactors'][r]['component'] for r in PART_ROLES[part]]
        score = (s['organism'] == organism, tcomps == comps, -float(s['resolution']), -sc['protomer'])
        if best is None or score > best[0]:
            best = (score, sc)
    return best[1]


def derive(sc_t, t_prot, t_src, new_src, pdb, prot, mapper, site_water):
    """Map one template scene onto a new protomer. Returns the new scene dict."""
    trole = {c['identity']: r for r, c in t_prot['cofactors'].items() if c}
    nrole = prot['roles']
    tch = {t_prot['psaA']: ('PsaA', prot['psaA']), t_prot['psaB']: ('PsaB', prot['psaB'])}
    t_site = None
    mapping, dropped = {}, []          # template residue id -> new residue id

    def map_res(rid):
        comp, chain, num = rid.split(':')
        if rid in trole:
            return nrole[trole[rid]]
        if comp == 'HOH':
            return None
        if chain in tch:
            sub, nchain = tch[chain]
            tf, _ = mapper.maps(t_src, sc_t['pdb'], chain, sub)
            _, nb = mapper.maps(new_src, pdb, nchain, sub)
            ref = tf.get(num)
            if ref is not None and ref in nb:
                c2, n2 = nb[ref]
                return f'{c2}:{nchain}:{n2}'
        return None

    for aid in sc_t['atoms']:
        rid = ':'.join(aid.split(':')[:3])
        if rid not in mapping and not aid.startswith('HOH'):
            mapping[rid] = map_res(rid)
    # superpose the template on the new model using atoms of identical residue type and name
    P, Q = [], []
    for aid in sc_t['atoms']:
        comp, chain, num, name = aid.split(':')
        nr = mapping.get(f'{comp}:{chain}:{num}')
        if nr and nr.split(':')[0] == comp and new_src.get(f'{nr}:{name}') is not None:
            P.append(t_src.get(aid)['xyz'])
            Q.append(new_src.get(f'{nr}:{name}')['xyz'])
    R, t = BA.kabsch(np.array(P), np.array(Q))
    rms = float(np.sqrt(((np.array(P) @ R.T + t - np.array(Q)) ** 2).sum(1).mean()))

    def map_atom(aid):
        """Same atom name in the mapped residue (chlorophyll components share names, so an epimer keeps O1D/O2D).
        For a different quinone (e.g. PQN vs PL9, whose carbonyls are O1/O4 vs O1/O2) the nearest atom of the same
        element after superposition (≤ 1.5 Å), so each carbonyl maps by position."""
        comp, chain, num, name = aid.split(':')
        nr = mapping.get(f'{comp}:{chain}:{num}')
        if not nr:
            return None
        ncomp = nr.split(':')[0]
        if ncomp == comp or ncomp in BA.THREE or (ncomp in CHL and comp in CHL):   # chlorophylls share atom names
            return f'{nr}:{name}' if new_src.get(f'{nr}:{name}') is not None else None
        tx = R @ t_src.get(aid)['xyz'] + t
        el = t_src.get(aid)['element']
        cand = [(float(np.linalg.norm(recs[0]['xyz'] - tx)), f'{nr}:{a}') for (c, ch, r, a), recs in new_src.atoms.items()
                if f'{c}:{ch}:{r}' == nr and recs[0]['element'] == el]
        best = min(cand) if cand else None
        return best[1] if best and best[0] <= 1.5 else None

    atoms = []
    for aid in sc_t['atoms']:
        rid = ':'.join(aid.split(':')[:3])
        if aid.startswith('HOH'):
            continue
        if mapping.get(rid) is None:
            dropped.append(rid)
            continue
        nid = map_atom(aid)
        if nid and nid not in atoms:
            atoms.append(nid)
    # residues whose type differs: add their own heavy atoms so the side chain is complete
    for rid, nr in mapping.items():
        if nr and rid.split(':')[0] != nr.split(':')[0]:
            for (c, ch, r, a) in list(new_src.atoms):
                if f'{c}:{ch}:{r}' == nr and f'{nr}:{a}' not in atoms:
                    atoms.append(f'{nr}:{a}')
    # waters by rule
    waters = []
    if sc_t['part'] in ('P_A', 'special_pair') and site_water:
        waters.append(site_water)
    if sc_t['part'] == 'special_pair':
        diag = [f"{nrole[r]}:{n}" for r in ('P_A', 'P_B') for n in DIAGNOSTIC if new_src.get(f"{nrole[r]}:{n}") is not None]
        dx = np.array([new_src.get(x)['xyz'] for x in diag])
        for wid, wxyz in new_src.waters:
            dd = np.linalg.norm(dx - wxyz, axis=1)
            if dd.min() <= 5.0 and wid not in waters:
                waters.append(wid)
    atoms += [w for w in waters if w not in atoms]

    # template water identities
    for c in sc_t['contacts']:
        for x in (c['atom_1'], c['atom_2']):
            if x.startswith('HOH') and x == sc_t.get('_site_water'):
                t_site = x
    contacts, lost = [], []
    for c in sc_t['contacts']:
        ends = []
        for x in (c['atom_1'], c['atom_2']):
            comp, chain, num, name = x.split(':')
            if comp == 'HOH':
                ends.append(site_water if (x == t_site and site_water) else None)
            else:
                ends.append(map_atom(x))
        if None in ends:
            if not any(x.startswith('HOH') and x != t_site for x in (c['atom_1'], c['atom_2'])):
                lost.append(f"{c['atom_1']}–{c['atom_2']}")
            continue
        contacts.append(dict(atom_1=ends[0], atom_2=ends[1], curated_annotation='derived by homology'))
    if sc_t['part'] == 'special_pair':   # every non-site water: one pair to its nearest diagnostic atom
        for w in waters:
            if w == site_water:
                continue
            wx = new_src.get(w)['xyz']
            dd = [(float(np.linalg.norm(new_src.get(x)['xyz'] - wx)), x) for x in diag]
            contacts.append(dict(atom_1=min(dd)[1], atom_2=w, curated_annotation='derived by homology'))
    have = set(atoms)
    contacts = [c for c in contacts if c['atom_1'] in have and c['atom_2'] in have]
    seen, uniq = set(), []
    for c in contacts:
        k = frozenset((c['atom_1'], c['atom_2']))
        if k not in seen:
            seen.add(k)
            uniq.append(c)

    # labels and pivot
    labels = []
    for lb in sc_t['labels']:
        comp, chain, num, name = lb['atom'].split(':')
        if comp == 'HOH':
            continue
        nr = mapping.get(f'{comp}:{chain}:{num}')
        if not nr:
            continue
        a = next((x for x in (map_atom(lb['atom']), f'{nr}:CA') if x in have), None)
        if a:
            labels.append(dict(lb, atom=a))
    for w in waters:
        labels.append(dict(atom=w))
    pivot_atom = map_atom(sc_t['pivot_atom'])

    v = list(sc_t['camera']['view'])
    M = np.array([[v[0], v[3], v[6]], [v[1], v[4], v[7]], [v[2], v[5], v[8]]]) @ R.T
    piv = R @ np.array(v[12:15]) + t
    nv = [M[0][0], M[1][0], M[2][0], M[0][1], M[1][1], M[2][1], M[0][2], M[1][2], M[2][2]] + v[9:12] + list(piv) + v[15:]
    notes = [f"Scene derived from the curated scene {sc_t['key']} by homology (1JB0-numbering alignment; template superposition "
             f"RMSD {rms:.2f} Å over {len(P)} atoms); not individually reviewed."]
    if lost:
        notes.append('Template pairs without a counterpart in this model: ' + '; '.join(lost) + '.')
    key = f"{pdb}_prot{prot['number']}_{sc_t['part']}"
    return dict(key=key, pdb=pdb, protomer=prot['number'], part=sc_t['part'], origin='derived', template=sc_t['key'],
                atoms=atoms, contacts=uniq, labels=labels, pivot_atom=pivot_atom,
                camera=dict(sc_t['camera'], view=[float(x) for x in nv]), notes=notes,
                water_rule=sc_t.get('water_rule') or ('Reference-site water (1JB0 HOH5011 position, ≤ 3 Å)' if sc_t['part'] == 'P_A' else None),
                overlap_frames=None)


def site_water_for(src, roles, ref, ref_pa):
    ref_core = {n: ref.get(f'{ref_pa}:{n}')['xyz'] for n in BA.CHLORIN_CORE if ref.get(f'{ref_pa}:{n}') is not None}
    pa = roles['P_A']
    common = [n for n in BA.CHLORIN_CORE if n in ref_core and src.get(f'{pa}:{n}') is not None]
    R, t = BA.kabsch(np.array([ref_core[n] for n in common]), np.array([src.get(f'{pa}:{n}')['xyz'] for n in common]))
    site = R @ ref.get(BA.REF_WATER)['xyz'] + t
    d = np.linalg.norm(src.water_xyz - site, axis=1)
    k = int(d.argmin())
    return src.waters[k][0] if d[k] <= 3.0 else None


def context(sources, structs, scenes):
    srcs = {}
    def get(pdb):
        if pdb not in srcs:
            srcs[pdb] = BA.Source(BA.BUILD / sources[pdb]['file'], sources[pdb]['sha256'])
        return srcs[pdb]
    ref = get('1JB0')
    return get, ref, Mapper(ref), next(p for s in structs if s['pdb'] == '1JB0' for p in s['protomers'])['cofactors']['P_A']['identity']


def template_prot(structs, sc):
    s = next(s for s in structs if s['pdb'] == sc['pdb'])
    return next(p for p in s['protomers'] if p['number'] == sc['protomer'])


def cmd_add(a):
    sources, structs, scenes = load()
    if a.pdb in sources:
        raise SystemExit(f'{a.pdb} is already in the atlas')
    raw = Path(a.cif).read_bytes()
    dst = BA.BUILD / 'inputs' / 'structures' / f'{a.pdb}.cif.gz'
    with gzip.GzipFile(dst, 'wb', mtime=0) as fo:
        fo.write(raw)
    sources[a.pdb] = dict(file=f'inputs/structures/{a.pdb}.cif.gz', sha256=hashlib.sha256(raw).hexdigest(),
                          url=f'https://files.rcsb.org/download/{a.pdb}.cif', retrieved=a.retrieved)
    get, ref, mapper, ref_pa = context(sources, structs, scenes)
    src = get(a.pdb)
    b = src.doc.sole_block()
    org = sorted({gemmi.cif.as_string(x) for x in b.find_loop('_entity_src_nat.pdbx_organism_scientific')} |
                 {gemmi.cif.as_string(x) for x in b.find_loop('_entity_src_gen.pdbx_gene_src_scientific_name')})
    organism = org[0] if org else a.organism
    if a.organism:
        organism = a.organism
    tech = src.technique()
    method = 'X-ray crystallography' if tech['method'].startswith('X-RAY') else 'Cryo-EM'
    prots = find_protomers(src, a.pdb, mapper)
    new_prots, new_scenes = [], []
    for prot in prots:
        sw = site_water_for(src, prot['roles'], ref, ref_pa)
        cof = {}
        for role, rid in prot['roles'].items():
            comp, chain, num = rid.split(':')
            n_atoms = sum(1 for (c, ch, r, _a) in src.atoms if f'{c}:{ch}:{r}' == rid and src.atoms[(c, ch, r, _a)][0]['element'] != 'H')
            cof[role] = dict(identity=rid, component=comp, chain=chain, residue=num,
                             label_asym=src.get(f'{rid}:' + ('MG' if comp in CHL else 'O1'))['label_asym'],
                             name=PIGMENT_NAME.get(comp, comp), heavy_atoms=n_atoms, atoms_note='')
        keys = []
        for part in BA.PARTS:
            comps = [cof[r]['component'] for r in PART_ROLES[part]]
            sc_t = choose_template(scenes, structs, part, organism, comps)
            tp = template_prot(structs, sc_t)
            sc_t = dict(sc_t, _site_water=sc_t.get('earlier_site_water') or site_water_for(get(sc_t['pdb']), {'P_A': tp['cofactors']['P_A']['identity']}, ref, ref_pa))
            new = derive(sc_t, tp, get(sc_t['pdb']), src, a.pdb, prot, mapper, sw)
            new_scenes.append(new)
            keys.append(new['key'])
        new_prots.append(dict(number=prot['number'], cofactors=cof, psaA=prot['psaA'], psaB=prot['psaB'],
                              network_status='Isolated P_A network available.', views=keys))
    n = len(new_prots)
    structs.append(dict(
        pdb=a.pdb, organism=organism, method=method, resolution=tech.get('resolution_A'),
        pdb_url=f'https://www.rcsb.org/structure/{a.pdb}', pdb_doi=f'10.2210/pdb{a.pdb}/pdb', condition=a.condition,
        description=a.description, context=f"{n} deposited protomer{'s' if n > 1 else ''}", notes=a.note or [],
        citations=[], lineage=[dict(text='Starting-model ancestry is not established from the deposited metadata.', doi='', locator='')],
        lineage_short='Starting-model ancestry is not established from the deposited metadata.',
        growth_light=None, genotype=a.genotype,
        deposition_authors=[gemmi.cif.as_string(x) for x in b.find_loop('_audit_author.name')],
        deposition_date=src.value('_pdbx_database_status.recvd_initial_deposition_date'),
        selector=f"{a.pdb} — {organism} — {method} {tech.get('resolution_A')} Å — {a.condition}",
        protomers=new_prots, scene_origin='derived by rule (tools/derive_scenes.py)'))
    scenes += new_scenes
    save(sources, structs, scenes)
    for s in new_scenes:
        print(f"{s['key']}: template {s['template']}, {len(s['atoms'])} atoms, {len(s['contacts'])} pairs; " + ' '.join(s['notes'][1:]))


def cmd_check(_a):
    """Re-derive each curated scene of Synechocystis entries from a different entry and compare the protein/cofactor pairs."""
    sources, structs, scenes = load()
    get, ref, mapper, ref_pa = context(sources, structs, scenes)
    by_key = {s['key']: s for s in scenes}
    tests = [('9AU4', 1, '9YL7'), ('5OY0', 1, '9YL7'), ('9YL7', 1, '5OY0'), ('6KMX', 1, '6KMW'), ('9I9L', 1, '9EYS')]
    total = same = 0
    for pdb, num, tpdb in tests:
        src = get(pdb)
        p = next(p for s in structs if s['pdb'] == pdb for p in s['protomers'] if p['number'] == num)
        prot = dict(number=num, psaA=p['psaA'], psaB=p['psaB'], roles={r: c['identity'] for r, c in p['cofactors'].items()})
        sw = site_water_for(src, prot['roles'], ref, ref_pa)
        for part in BA.PARTS:
            sc_t = by_key[f'{tpdb}_prot1_{part}']
            tp = template_prot(structs, sc_t)
            sc_t = dict(sc_t, _site_water=sc_t.get('earlier_site_water') or site_water_for(get(tpdb), {'P_A': tp['cofactors']['P_A']['identity']}, ref, ref_pa))
            d = derive(sc_t, tp, get(tpdb), src, pdb, prot, mapper, sw)
            cur = by_key[f'{pdb}_prot{num}_{part}']
            norm = lambda cs: {frozenset((c['atom_1'], c['atom_2'])) for c in cs if 'HOH' not in c['atom_1'] + c['atom_2']}
            a_, b_ = norm(d['contacts']), norm(cur['contacts'])
            total += len(b_)
            same += len(a_ & b_)
            print(f"{pdb} p{num} {part:12} from {tpdb}: curated {len(b_)}, derived {len(a_)}, shared {len(a_ & b_)}"
                  + (f"  only curated: {sorted('–'.join(sorted(x)) for x in b_ - a_)}" if b_ - a_ else '')
                  + (f"  only derived: {sorted('–'.join(sorted(x)) for x in a_ - b_)}" if a_ - b_ else ''))
    print(f'non-water pairs reproduced: {same}/{total}')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('add')
    p.add_argument('pdb')
    p.add_argument('cif')
    p.add_argument('--condition', required=True)
    p.add_argument('--description', required=True)
    p.add_argument('--note', action='append')
    p.add_argument('--genotype')
    p.add_argument('--organism')
    p.add_argument('--retrieved', default=date.today().isoformat())
    sub.add_parser('check')
    a = ap.parse_args()
    (cmd_add if a.cmd == 'add' else cmd_check)(a)


if __name__ == '__main__':
    main()
