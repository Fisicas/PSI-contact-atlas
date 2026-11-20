"""Generate consistent, publication-state-aware citations from explicit config."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[1]
def main(root=ROOT):
    r=json.loads((root/'build/config/release.json').read_text(encoding='utf-8'));m=json.loads((root/'build/config/citation.json').read_text(encoding='utf-8'));text=(root/'data/atlas.js').read_text(encoding='utf-8');a=json.loads(text.split('=',1)[1].strip().rstrip(';'));c=a['counts'];version=r['version'];published=r['status']=='published'
    automatic_archive = published and r.get('doi_workflow') == 'zenodo-github'
    if published:
        assert r.get('publication_authorized') and r.get('release_date')
        assert r.get('release_url') == m['repository_code'] + '/releases/tag/v' + version
        assert automatic_archive or r.get('version_doi'), 'A version DOI is required for a manually deposited release'
        assert r['version_doi'] not in (r['previous_release']['version_doi'], r['concept_doi'])

    else:assert r.get('release_date') is None and r.get('version_doi') is None,'Review metadata must not assert publication'
    citation_url = r['release_url'] if published else m['url']
    status='Released version' if published else 'Unpublished release-review package'
    message=f'{status} {version}. Cite the version actually used, together with the individual PDB entries and their primary papers.'
    abstract=f"Heavy-atom separations around the photosystem I special pair, the P_A chlorophyll network and both A1 quinone sites in {c['structures']} deposited PDB structures ({c['protomers']} protomers, {c['views']} scenes, {c['contacts']:,} selected scene rows and {c['unique_contacts']} unique atom pairs). Includes an offline interactive viewer, homologous comparisons, coordinate crops, CSV tables, PyMOL scripts, archived inputs and reproducible checks. Optional unmasked sections and interactive experimental density cover 39 protomers and 156 scenes, with 208 clickable mesh previews and static image fallbacks. Experimental data for 1JB0 are unavailable. Deposited-model geometry, local-density, preparation and selection-scope qualifications remain explicit. This is a selected PSI contact atlas; the structural census is separate."
    authors=[{'family-names':x['family_names'],'given-names':x['given_names'],'orcid':'https://orcid.org/'+x['orcid']} for x in m['authors']]
    cff={'cff-version':'1.2.0','message':message,'title':m['title'],'type':m['type'],'version':version,'authors':authors,'repository-code':m['repository_code'],'url':citation_url,'license':m['licenses'],'abstract':abstract,'keywords':m['keywords']}
    # JSON scalar/list/object values are valid YAML 1.2; avoid a build-time YAML dependency.
    if published: cff['date-released'] = r['release_date']
    if r['version_doi']: cff['doi'] = r['version_doi']
    (root/'CITATION.cff').write_text('\n'.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in cff.items())+'\n',encoding='utf-8',newline='\n')
    description=('<p>'+html.escape(message)+'</p>' if not published else '')+'<p>'+html.escape(abstract)+'</p><p>'+html.escape(m['license_scope'])+'</p>'
    zen={'title':m['title'],'upload_type':m['type'],'creators':[{'name':x['family_names']+', '+x['given_names'],'orcid':x['orcid']} for x in m['authors']],'description':description,'version':version,'license':m['zenodo_primary_license'],'access_right':'open','keywords':m['keywords'],'related_identifiers':[{'identifier':m['repository_code'],'relation':'isSupplementTo','resource_type':'software'}]}
    if published: zen['publication_date'] = r['release_date']
    if r['version_doi']: zen['doi'] = r['version_doi']
    zen['related_identifiers'].extend({'identifier': s['pdb_doi'], 'relation': 'references', 'resource_type': 'dataset'} for s in a['structures'])
    (root/'.zenodo.json').write_text(json.dumps(zen,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    note=message+(' Published '+r['release_date']+'.' if published else ' Prepared '+r['build_date']+'; no release date or new version DOI assigned.')
    def bib(s):return s.replace('\\','\\textbackslash{}').replace('&','\\&').replace('_','\\_').replace('%','\\%')
    fields={'author':' and '.join(x['family_names']+', '+x['given_names'] for x in m['authors']),'title':'{'+m['title']+'}','howpublished':'Dataset with interactive viewer','version':version,'url':citation_url,'note':note}
    if published: fields['year'] = r['release_date'][:4]
    if r['version_doi']: fields['doi'] = r['version_doi']
    (root/'CITATION.bib').write_text('@misc{nelson_psi_contact_atlas_'+version.replace('.','_')+',\n'+',\n'.join('  '+k+' = {'+bib(v)+'}' for k,v in fields.items())+'\n}\n',encoding='utf-8',newline='\n')
    ris=['TY  - DATA']+['AU  - '+x['family_names']+', '+x['given_names'] for x in m['authors']]+['TI  - '+m['title'],'ET  - '+version,'UR  - '+citation_url,'N1  - '+note]
    if published: ris.extend(['PY  - '+r['release_date'][:4], 'DA  - '+r['release_date'].replace('-','/')])
    if r['version_doi']: ris.append('DO  - '+r['version_doi'])
    (root/'CITATION.ris').write_text('\n'.join(ris+['ER  - '])+'\n',encoding='utf-8',newline='\n')
    csl={'id':'psi-contact-atlas-'+version,'type':'dataset','title':m['title'],'author':[{'family':x['family_names'],'given':x['given_names'],'ORCID':'https://orcid.org/'+x['orcid']} for x in m['authors']],'version':version,'URL':citation_url,'note':note}
    if published: csl['issued'] = {'date-parts': [[int(n) for n in r['release_date'].split('-')]]}
    if r['version_doi']: csl['DOI'] = r['version_doi']
    (root/'CITATION.csl.json').write_text(json.dumps([csl],indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    refs=['# Structure and primary-paper references','', 'Generated from the retained atlas metadata. Cite the particular PDB entries and primary papers used, alongside the atlas version. Titles/citations retain their existing source verification; this generation does not establish a new literature search.','']
    for s in a['structures']:
        refs.extend(['## '+s['pdb']+' — '+s['organism'],'', '[PDB record]('+s['pdb_url']+') · [PDB DOI](https://doi.org/'+s['pdb_doi']+')',''])
        for ref in s['citations']:
            refs.append(ref['author_short']+' ('+str(ref['year'])+'). '+ref['title']+'. [Primary source](https://doi.org/'+ref['doi']+').')
        if not s['citations']:refs.append('No primary-paper DOI is established in the retained metadata.')
        refs.append('')
    (root/'docs/STRUCTURE_REFERENCES.md').write_text('\n'.join(refs)+'\n',encoding='utf-8',newline='\n')
    print('Citation formats and Zenodo metadata generated:',version,status)
if __name__=='__main__':main()
