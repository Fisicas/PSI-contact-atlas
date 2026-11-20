"""Catch byte/identity corruption in offline scene-download payloads."""
from pathlib import Path
import importlib.util,json,shutil,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('payload_verifier',ROOT/'tools/verify_download_payloads.py');V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
class DownloadPayloadIntegrity(unittest.TestCase):
    def test_packaged_downloads_match_sources(self):
        r=V.verify(ROOT);self.assertEqual(r['scenes'],160);self.assertEqual(r['assets'],480)
    def fixture(self):
        temp=tempfile.TemporaryDirectory(prefix='psi_payload_test_');self.addCleanup(temp.cleanup);root=Path(temp.name);self.assertTrue(root.resolve().is_relative_to(Path(tempfile.gettempdir()).resolve()))
        key='9LUT_prot1_special_pair';file=ROOT/'data/views'/(key+'.js');source=file.read_text(encoding='utf-8');scene=json.loads(source[source.rfind(']=')+2:].strip().rstrip(';'))
        for rel in ['data/views/'+key+'.js','data/downloads/'+key+'.js',*scene['downloads'].values()]:
            dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest)
        self.assertEqual(V.verify(root)['assets'],3);return root,key
    def corrupt(self,root,key,fn):
        file=root/'data/downloads'/(key+'.js');lines=file.read_text(encoding='utf-8').splitlines();prefix='window.PSI_DOWNLOADS['+json.dumps(key)+']=';data=json.loads(lines[1][len(prefix):].rstrip(';'));fn(data)
        file.write_text(lines[0]+'\n'+prefix+json.dumps(data)+';\n',encoding='utf-8')
    def test_changed_download_bytes_rejected(self):
        root,key=self.fixture();self.corrupt(root,key,lambda data:data['assets']['pymol'].__setitem__('text',data['assets']['pymol']['text']+'changed'))
        with self.assertRaisesRegex(AssertionError,'content differs'):V.verify(root)
    def test_wrong_download_identity_rejected(self):
        root,key=self.fixture();self.corrupt(root,key,lambda data:data['assets']['cif'].__setitem__('filename','another_scene.cif'))
        with self.assertRaisesRegex(AssertionError,'download identity'):V.verify(root)
if __name__=='__main__':unittest.main()
