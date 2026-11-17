"""Deliberate-corruption tests: tools/verify_public.py must PASS on the repository and FAIL on each corruption.

    python -m unittest discover -s tests -v
"""
import gzip, json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COPY = ['data', 'downloads', 'build', 'tools', 'MANIFEST.json']


class VerifierCatchesCorruption(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix='atlas_verify_'))
        for name in COPY:
            src = ROOT / name
            (shutil.copytree if src.is_dir() else shutil.copyfile)(src, cls.tmp / name)
        # files outside the copied set are listed in the manifest; keep only what was copied
        man = json.loads((cls.tmp / 'MANIFEST.json').read_text(encoding='utf-8'))
        man = {k: v for k, v in man.items() if k.split('/')[0] in COPY}
        (cls.tmp / 'MANIFEST.json').write_text(json.dumps(man, indent=1), encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_verifier(self):
        return subprocess.run([sys.executable, str(self.tmp / 'tools' / 'verify_public.py')], capture_output=True, text=True).returncode

    def corrupt(self, rel, change, binary=False):
        p = self.tmp / rel
        orig = p.read_bytes()
        try:
            if binary:
                p.write_bytes(change(orig))
            else:
                p.write_text(change(orig.decode('utf-8')), encoding='utf-8', newline='')
            return self.run_verifier()
        finally:
            p.write_bytes(orig)

    def test_0_clean_copy_passes(self):
        self.assertEqual(self.run_verifier(), 0)

    def test_csv_distance(self):
        def f(t):
            lines = t.split('\n')
            cells = lines[1].split(',')
            i = lines[0].split(',').index('distance_A')
            cells[i] = f'{float(cells[i]) + 0.001:.5f}'
            lines[1] = ','.join(cells)
            return '\n'.join(lines)
        self.assertNotEqual(self.corrupt('downloads/all_contacts.csv', f), 0)

    def test_class_label(self):
        self.assertNotEqual(self.corrupt('downloads/all_contacts.csv', lambda t: t.replace(',acceptor_pair,', ',polar,', 1)), 0)

    def test_duplicate_row(self):
        self.assertNotEqual(self.corrupt('downloads/all_contacts.csv', lambda t: t + t.split('\n')[1] + '\n'), 0)

    def test_compare_value(self):
        def f(t):
            lines = t.split('\n')
            for k, line in enumerate(lines[1:], 1):
                cells = line.split(',')
                if len(cells) > 13 and cells[13]:
                    cells[13] = f'{float(cells[13]) + 0.01:.4f}'
                    lines[k] = ','.join(cells)
                    break
            return '\n'.join(lines)
        self.assertNotEqual(self.corrupt('downloads/compare_matrix.csv', f), 0)

    def test_crop_coordinate(self):
        crop = sorted((self.tmp / 'downloads' / 'cif').glob('*.cif'))[0].relative_to(self.tmp).as_posix()
        def f(t):
            out, done = [], False
            for line in t.split('\n'):
                if not done and line.startswith(('ATOM', 'HETATM')):
                    parts = line.split()
                    for k, x in enumerate(parts):
                        if '.' in x and k > 8:
                            parts[k] = f'{float(x) + 0.5:.3f}'
                            break
                    line, done = ' '.join(parts), True
                out.append(line)
            return '\n'.join(out)
        self.assertNotEqual(self.corrupt(crop, f), 0)

    def test_archived_input(self):
        rel = 'build/inputs/structures/1JB0.cif.gz'
        self.assertNotEqual(self.corrupt(rel, lambda b: gzip.compress(gzip.decompress(b) + b'#\n', mtime=0), binary=True), 0)

    def test_manifest(self):
        self.assertNotEqual(self.corrupt('downloads/README.md', lambda t: t + '\nchanged\n'), 0)


if __name__ == '__main__':
    unittest.main()
