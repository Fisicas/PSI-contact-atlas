"""Write one PyMOL script per scene (downloads/pymol/<key>.pml) from the library's scene data.

Each script loads the scene's native-identity mmCIF crop (or, optionally, the full PDB entry), applies the
library's element colours and stick style, draws every measured pair as a PyMOL distance object grouped
by contact class, labels residues and roles, and restores the reviewed starting view.
Paths in the scripts are relative to the repository root.

Run: python tools/make_pymol_scripts.py   (tools/build_atlas.py also runs it)
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'downloads' / 'pymol'
ELEMENT_RGB = {'C': (.50, .50, .50), 'N': (.15, .30, .90), 'O': (1.0, .12, .12), 'S': (.95, .80, .10), 'Mg': (.10, .75, .25)}
CLASS = {  # colour (same as the web viewer), dash length/gap in Å, label
    'mg': ('#178a3c', .30, 0.0, 'Mg_ligand'), 'polar': ('#1d2a3a', .25, .18, 'polar_candidate'),
    'water': ('#0b7f9c', .25, .18, 'water_polar_candidate'), 'context': ('#8a929c', .08, .30, 'longer_context'),
    'acceptor_pair': ('#a0527a', .12, .12, 'OO_no_H_donor'), 'cs_contact': ('#b0670f', .08, .30, 'CS_contact'), 'intra': ('#7a52c7', .30, .12, 'intramolecular'),
}
LABEL = {'acceptor_pair': 'O···O, no H donor', 'cs_contact': 'C/S contact'}
ROLE_TEXT = {'P_A': 'PA', 'P_B': 'PB', 'A1_A': 'A1A', 'A1_B': 'A1B'}
PART = {'special_pair': 'special pair', 'P_A': 'P_A network', 'A1A': 'A1_A quinone', 'A1B': 'A1_B quinone'}


def rgb(h):
    return [round(int(h[i:i + 2], 16) / 255, 3) for i in (1, 3, 5)]


def load_js(path, prefix):
    t = path.read_text(encoding='utf-8')
    return json.loads(t[t.index('=', t.index(prefix)) + 1:].rstrip().rstrip(';'))


def sel(r, atom=None):
    s = f"chain {r['chain']} and resi {r['num']} and resn {r['comp']}"
    return f"({s} and name {atom})" if atom else f"({s})"


def script(sc, atlas_struct):
    res, atoms = sc['residues'], sc['atoms']
    by_chain = defaultdict(list)
    for r in res:
        by_chain[r['chain']].append(r['num'])
    lib_sel = ' or '.join(f"(chain {c} and resi {'+'.join(sorted(set(n), key=lambda x: (len(x), x)))})" for c, n in by_chain.items())
    lines = [
        f"# PSI Contact Atlas — {sc['pdb']} protomer {sc['protomer']}, {PART[sc['part']]}",
        f"# {atlas_struct['organism']} · {atlas_struct['condition']} · {atlas_struct['method']} {atlas_struct['resolution']} Å",
        "#",
        "# Run from the repository root:   pymol downloads/pymol/" + sc['key'] + ".pml",
        "# Distances are Euclidean heavy-atom separations (Å). Short N/O···O pairs are hydrogen-bond CANDIDATES:",
        "# hydrogens, protonation and angles are not modelled. Pairs in group OO_no_H_donor are two oxygen",
        "# acceptors (neither carries a hydrogen), so they are not hydrogen-bond candidates.",
        "# Chain IDs are case-sensitive author IDs.",
        "",
        "reinitialize",
        "# chain IDs such as 'a' and 'A' are different chains. Use author chain/residue numbering as the library does.",
        "set ignore_case, 0",
        "set cif_use_auth, 1",
        f"load downloads/cif/{sc['key']}.cif, scene",
        f"# To start from the full deposited entry instead, replace the line above with:",
        f"#   fetch {sc['pdb']}, scene, type=cif",
        f"select lib_atoms, scene and ({lib_sel})",
        "",
        "# --- style: white background, grey carbon, element colours (library palette)",
        "bg_color white",
        "set orthoscopic, 1",
        "set stick_radius, 0.13",
        "set sphere_scale, 0.25",
        "hide everything",
        "show sticks, lib_atoms",
        "show spheres, lib_atoms and (elem Mg or resn HOH)",
    ]
    for e, c in ELEMENT_RGB.items():
        lines += [f"set_color lib_{e}, {list(c)}", f"color lib_{e}, lib_atoms and elem {e.upper() if e != 'Mg' else 'MG'}"]
    cof = [r for r in res if r['role']]
    if cof:
        lines += ["# cofactor(s) slightly thicker", "set_bond stick_radius, 0.16, scene and (" + ' or '.join(sel(r) for r in cof) + ")"]
    lines += ["", "# --- measured pairs (the comment above each line gives the library value, PyMOL recomputes it)",
              "set dash_radius, 0.035", "set label_distance_digits, 2", "set label_size, 18", "set label_color, black"]
    groups = defaultdict(list)
    for n, c in enumerate(sorted(sc['contacts'], key=lambda c: (list(CLASS).index(c['cls']), c['d'])), 1):
        a, b = atoms[c['i']], atoms[c['j']]
        ra, rb = res[a[2]], res[b[2]]
        name = f"d{n:02d}_{c['cls']}"
        groups[c['cls']].append(name)
        lines += [f"# {ra['comp']} {ra['chain']} {ra['num']} {a[0]} ··· {rb['comp']} {rb['chain']} {rb['num']} {b[0]} = {c['d']:.2f} Å ({LABEL.get(c['cls'], CLASS[c['cls']][3].replace('_', ' '))})",
                  f"distance {name}, scene and {sel(ra, a[0])}, scene and {sel(rb, b[0])}"]
    for cls, names in groups.items():
        col, length, gap, label = CLASS[cls]
        lines += [f"set_color cls_{cls}, {rgb(col)}", f"group {label}, {' '.join(names)}",
                  f"set dash_color, cls_{cls}, {label}", f"set dash_length, {length}, {label}", f"set dash_gap, {gap}, {label}"]
    lines += ["", "# --- labels (residues at the library anchor atoms, roles as plain text)",
              "set label_font_id, 7", "set label_size, 16", "set float_labels, 1"]
    for lb in sc['labels']:
        a = atoms[lb['a']]
        r = res[a[2]]
        text = ROLE_TEXT.get(lb['text'], lb['text']) + (f" {lb['chain']}" if lb.get('chain') else '')
        lines.append(f'label scene and {sel(r, a[0])}, "{text}"')
    v = sc['camera']['pymol_view']
    lines += ["", "# --- the reviewed starting orientation used by the library (orthoscopic)",
              "set_view (" + ', '.join(f'{x:.6f}' for x in v) + ")",
              "zoom lib_atoms, 2, complete=1",
              "deselect"]
    # PyMOL splits command lines on ';' even inside comments, so never emit one
    if any(';' in l for l in lines):
        raise SystemExit(f"{sc['key']}: generated line contains ';'")
    return '\n'.join(lines) + '\n'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    atlas = load_js(ROOT / 'data' / 'atlas.js', 'PSI_ATLAS')
    S = {s['pdb']: s for s in atlas['structures']}
    n = 0
    for f in sorted((ROOT / 'data' / 'views').glob('*.js')):
        sc = load_js(f, 'PSI_VIEWS[')
        (OUT / f"{sc['key']}.pml").write_text(script(sc, S[sc['pdb']]), encoding='utf-8', newline='\n')
        n += 1
    print(f'wrote {n} PyMOL scripts to {OUT}')


if __name__ == '__main__':
    main()
