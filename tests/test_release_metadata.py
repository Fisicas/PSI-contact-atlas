"""Reject metadata drift and invented publication identifiers before packaging."""
from pathlib import Path
import sys,json,copy,unittest
import yaml
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from verify_release_metadata import validate_objects
class ReleaseMetadataTests(unittest.TestCase):
    def setUp(self):
        self.r=json.loads((ROOT/'build/config/release.json').read_text(encoding='utf-8'));self.m=json.loads((ROOT/'build/config/citation.json').read_text(encoding='utf-8'));self.c=yaml.safe_load((ROOT/'CITATION.cff').read_text(encoding='utf-8'));self.z=json.loads((ROOT/'.zenodo.json').read_text(encoding='utf-8'));self.a=json.loads((ROOT/'data/atlas.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
    def check(self):validate_objects(self.r,self.m,self.c,self.z,self.a)
    def test_consistent_review_metadata(self):self.check()
    def test_prior_version_DOI_rejected(self):
        self.c['doi']=self.r['previous_release']['version_doi']
        with self.assertRaises(AssertionError):self.check()
    def test_zenodo_version_drift_rejected(self):
        self.z['version']='1.0.0'
        with self.assertRaises(AssertionError):self.check()
    def test_invented_release_date_rejected(self):
        self.z['publication_date']='1900-01-01'
        with self.assertRaises(AssertionError):self.check()
    def test_creator_drift_rejected(self):
        self.z['creators'][0]['name']='Unverified Author'
        with self.assertRaises(AssertionError):self.check()
if __name__=='__main__':unittest.main()
