"""Run every downloads/pymol/*.pml in PyMOL and check it against the library's scene data.

For each script, both as written (scene crop) and with the full deposited entry loaded instead:
  * the script runs without error and creates every distance object;
  * each distance endpoint selects exactly one atom;
  * PyMOL's own distance equals the library value (crop: within the 0.001 Å rounding bound);
  * lib_atoms selects the scene's atoms (full entry: reports residues the crop includes only partly).
Renders two PNGs for visual inspection. Run with the PyMOL interpreter:
  <pymol python> tools/check_pymol_scripts.py <directory of deposited PDBID.cif files>
"""
import json, os, re, sys
from pathlib import Path
from pymol import cmd

ROOT = Path(__file__).resolve().parent.parent
CIF_DIR = Path(sys.argv[1]).resolve()


def load_js(path, prefix):
    t = path.read_text(encoding='utf-8')
    return json.loads(t[t.index('=', t.index(prefix)) + 1:].rstrip().rstrip(';'))


def run(text):
    """Execute the script exactly as PyMOL does for `pymol script.pml` / `@script.pml`."""
    tmp = ROOT / '_check_tmp.pml'
    tmp.write_text(text, encoding='utf-8')
    cmd.reinitialize()
    cmd.do('@' + tmp.as_posix())
    tmp.unlink()


def main():
    os.chdir(ROOT)
    out = dict(scripts=0, distances=0, max_dev_crop=0.0, max_dev_full=0.0, problems=[], partial_residues=[])
    for f in sorted((ROOT / 'downloads' / 'pymol').glob('*.pml')):
        key = f.stem
        sc = load_js(ROOT / 'data' / 'views' / f'{key}.js', 'PSI_VIEWS[')
        text = f.read_text(encoding='utf-8')
        if ';' in text:
            out['problems'].append(f'{key}: contains ";" (PyMOL splits lines on it, even in comments)')
        pairs =re.findall(r'^distance (\S+), (scene and \(.*?\)), (scene and \(.*?\))$', text, re.M)
        if len(pairs) != len(sc['contacts']):
            out['problems'].append(f'{key}: {len(pairs)} distance lines for {len(sc["contacts"])} contacts')
        expected = {name: c['d'] for name, c in zip([p[0] for p in pairs], sorted(sc['contacts'], key=lambda c: (['mg', 'polar', 'water', 'context', 'acceptor_pair', 'cs_contact', 'intra'].index(c['cls']), c['d'])))}
        for variant in ('crop', 'full'):
            t = text if variant == 'crop' else text.replace(f'load downloads/cif/{key}.cif, scene', f'load "{(CIF_DIR / (sc["pdb"] + ".cif")).as_posix()}", scene')
            run(t)
            names = set(cmd.get_names('all'))
            n_lib = cmd.count_atoms('lib_atoms')
            if variant == 'crop' and n_lib != len(sc['atoms']):
                out['problems'].append(f'{key}: lib_atoms {n_lib} vs scene {len(sc["atoms"])}')
            if variant == 'full' and n_lib != len(sc['atoms']):
                out['partial_residues'].append(f'{key}: full entry selects {n_lib} atoms vs {len(sc["atoms"])} in scene')
            for name, s1, s2 in pairs:
                if name not in names:
                    out['problems'].append(f'{key}/{variant}: missing object {name}')
                n1, n2 = cmd.count_atoms(s1), cmd.count_atoms(s2)
                if n1 != 1 or n2 != 1:
                    out['problems'].append(f'{key}/{variant}: {name} selects {n1}/{n2} atoms')
                    continue
                d = cmd.get_distance(s1, s2)
                dev = abs(d - expected[name])
                k = 'max_dev_crop' if variant == 'crop' else 'max_dev_full'
                out[k] = max(out[k], dev)
                if dev > (0.002 if variant == 'crop' else 1e-3):
                    out['problems'].append(f'{key}/{variant}: {name} PyMOL {d:.4f} vs library {expected[name]:.4f}')
                out['distances'] += 1
        out['scripts'] += 1
        if key in ('1JB0_prot1_P_A', '9YL7_prot1_A1A'):
            run(text)
            cmd.viewport(1200, 900)
            cmd.png(str(ROOT / 'media' / f'pymol_check_{key}.png'), width=1200, height=900, ray=1)
    out['status'] = 'PASS' if not out['problems'] else 'FAIL'
    (ROOT / 'pymol_script_check.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
    print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in out.items()}))
    for p in out['problems'][:20]:
        print('  ', p)


if __name__ == '__main__':
    main()
