"""Offline official CFF-schema and cross-format release-state verification."""
from pathlib import Path
import json,hashlib,sys,argparse,re
from importlib.metadata import version
import yaml,jsonschema
ROOT=Path(__file__).resolve().parents[1]
def validate_objects(r,m,cff,zen,a):
    assert cff['version']==zen['version']==a['version']==r['version']
    assert cff['title']==zen['title']==m['title'] and cff['type']==zen['upload_type']==m['type']=='dataset'
    assert cff['license']==m['licenses'] and zen['license']==m['zenodo_primary_license']
    assert cff['authors']==[{'family-names':x['family_names'],'given-names':x['given_names'],'orcid':'https://orcid.org/'+x['orcid']} for x in m['authors']]
    assert zen['creators']==[{'name':x['family_names']+', '+x['given_names'],'orcid':x['orcid']} for x in m['authors']]
    for author in m['authors']:
        ident=author['orcid'].replace('-','');total=0
        for d in ident[:15]:total=(total+int(d))*2
        digit=(12-total%11)%11;assert ident[-1]==('X' if digit==10 else str(digit)),'ORCID checksum'
    if r['status']=='published':
        assert r['publication_authorized'] and r['release_date']
        assert r['version_doi'] or r.get('doi_workflow') == 'zenodo-github'
        assert cff.get('doi') == zen.get('doi') == a['doi'] == r['version_doi']
        if not r['version_doi']:
            assert 'doi' not in cff and 'doi' not in zen
        assert cff['date-released'] == zen['publication_date'] == a['release_date'] == r['release_date']
        assert cff['url'] == r['release_url'] == m['repository_code'] + '/releases/tag/v' + r['version']
        assert r['version_doi'] not in [r['concept_doi'],r['previous_release']['version_doi']]
    else:
        assert not r['publication_authorized'] and r['release_date'] is None and r['version_doi'] is None
        assert 'doi' not in cff and 'date-released' not in cff and 'doi' not in zen and 'publication_date' not in zen
        assert a['doi'] is None and a['release_date'] is None
        assert 'Unpublished' in cff['message'] and 'Unpublished' in zen['description']
    assert cff['keywords']==zen['keywords']==m['keywords']
def main(root=ROOT,out=None):
    r=json.loads((root/'build/config/release.json').read_text(encoding='utf-8'));m=json.loads((root/'build/config/citation.json').read_text(encoding='utf-8'));cff=yaml.safe_load((root/'CITATION.cff').read_text(encoding='utf-8'));zen=json.loads((root/'.zenodo.json').read_text(encoding='utf-8'));text=(root/'data/atlas.js').read_text(encoding='utf-8');a=json.loads(text.split('=',1)[1].strip().rstrip(';'))
    source=json.loads((root/'build/inputs/metadata/sources.json').read_text(encoding='utf-8'))['cff_schema'];schema=root/'build/inputs/metadata'/source['file'];assert hashlib.sha256(schema.read_bytes()).hexdigest()==source['sha256']
    jsonschema.Draft7Validator(json.loads(schema.read_text(encoding='utf-8')),format_checker=jsonschema.FormatChecker()).validate(cff)
    validate_objects(r,m,cff,zen,a)
    for name in ['CITATION.bib','CITATION.ris','CITATION.csl.json']:
        t=(root/name).read_text(encoding='utf-8');assert r['version'] in t and m['title'] in t
        if r['status']!='published':assert 'Unpublished' in t and r['previous_release']['version_doi'] not in t and r['concept_doi'] not in t
    csl=json.loads((root/'CITATION.csl.json').read_text(encoding='utf-8'))[0];assert csl['version']==r['version']
    if r['status']!='published':assert 'issued' not in csl and 'DOI' not in csl
    else:
        assert csl['URL'] == r['release_url'] and csl.get('DOI') == r['version_doi']
        assert csl['issued']['date-parts'] == [[int(n) for n in r['release_date'].split('-')]]
        for name in ['CITATION.bib', 'CITATION.ris']:
            text = (root/name).read_text(encoding='utf-8')
            assert r['release_url'] in text and r['previous_release']['version_doi'] not in text
            assert r['concept_doi'] not in text
        if not r['version_doi']:
            assert 'DOI' not in csl
            assert not re.search(r'^  doi\s*=', (root/'CITATION.bib').read_text(encoding='utf-8'), re.M)
            assert not re.search(r'^DO  -', (root/'CITATION.ris').read_text(encoding='utf-8'), re.M)
    assert json.loads((root/'build/provenance/scientific_disposition_acceptance.json').read_text(encoding='utf-8'))['publication_authorized'] is False
    if r['status']!='published':assert r['version']+' · UNPUBLISHED' in (root/'index.html').read_text(encoding='utf-8')
    result=dict(status='PASS',version=r['version'],publication_status=r['status'],citation_formats=['CFF 1.2.0','BibTeX','RIS','CSL-JSON','Zenodo JSON'],official_CFF_schema_sha256=source['sha256'],authors_ORCID_licenses_counts_consistent=True,scientific_dispositions_accepted=True,release_date=r['release_date'],version_doi=r['version_doi'],concept_doi_context_only=r['concept_doi'],versions={x:version(x) for x in ['PyYAML','jsonschema']},limitations='Official CFF schema validated offline. Zenodo JSON checked for selected fields/cross-format consistency, not against a complete Zenodo server schema; no upload, DOI reservation, release or remote CI is claimed.')
    if out:Path(out).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2));return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--json',type=Path);v=p.parse_args();main(v.repo,v.json)
