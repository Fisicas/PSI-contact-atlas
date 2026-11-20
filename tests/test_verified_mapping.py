"""Ensure explicit intake exceptions are source-bound and do not loosen discovery."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import derive_scenes as DS
class MappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sources,structs,scenes=DS.load();get,cls.ref,_,_=DS.context(sources,structs,scenes);cls.get=staticmethod(get)
        cls.path=R/'build/provenance/expanded_mapping_gate_v01.json';cls.report=json.loads(cls.path.read_text(encoding='utf-8'))
    def load_changed(self,change):
        report=copy.deepcopy(self.report);change(report)
        with tempfile.TemporaryDirectory() as folder:
            f=Path(folder)/'changed.json';f.write_text(json.dumps(report),encoding='utf-8');return DS.verified_protomers(f,'9KZ9',self.get('9KZ9'))
    def test_four_verified_sources(self):
        for pdb in ['9UH3','9HYU','9KZ9','8XLS']:
            with self.subTest(pdb=pdb):self.assertEqual(len(DS.verified_protomers(self.path,pdb,self.get(pdb))),1)
    def test_wrong_source_hash_rejected(self):
        with self.assertRaises(SystemExit):self.load_changed(lambda r: next(x for x in r['entries'] if x['pdb']=='9KZ9').update(current_sha256='0'*64))
    def test_failed_gate_rejected(self):
        with self.assertRaises(SystemExit):self.load_changed(lambda r:r.update(status='FAIL'))
    def test_absent_role_rejected(self):
        with self.assertRaises(SystemExit):self.load_changed(lambda r:next(x for x in r['entries'] if x['pdb']=='9KZ9')['protomers'][0]['roles'].pop('A1_B'))
    def test_wrong_component_rejected(self):
        with self.assertRaises(SystemExit):self.load_changed(lambda r:next(x for x in r['entries'] if x['pdb']=='9KZ9')['protomers'][0]['roles'].update(P_A='PQN:A:841'))
    def test_absent_native_cofactor_rejected(self):
        with self.assertRaises(SystemExit):self.load_changed(lambda r:next(x for x in r['entries'] if x['pdb']=='9KZ9')['protomers'][0]['roles'].update(P_A='CL0:A:99999'))
    def test_automatic_cutoff_unchanged(self):
        with self.assertRaisesRegex(SystemExit,'3.0 Å'):DS.find_protomers(self.get('9KZ9'),'9KZ9',DS.Mapper(self.ref))
if __name__=='__main__':unittest.main()
