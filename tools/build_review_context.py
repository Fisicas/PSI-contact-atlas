"""Generate inspectable validation context from the source-bound review configuration."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    cfg=json.loads((ROOT/'build/config/scientific_review.json').read_text(encoding='utf-8'))
    out=ROOT/'downloads/validation';out.mkdir(parents=True,exist_ok=True)
    (out/'cofactor_geometry.json').write_text(json.dumps(cfg,indent=1,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    (out/'source_snapshot_check.json').write_text(json.dumps(dict(date=cfg['date'],scope='Atom identity, XYZ, occupancy and B; archived sources retained',entries=cfg['current_snapshot_audit']),indent=1)+'\n',encoding='utf-8',newline='\n')
    fields=['pdb','protomer','role','identity','carbonyl_bonds_A','ring_plane_RMS_A','max_abs_reported_bond_Z','Q_score','residue_inclusion','coordinate_source_sha256','validation_xml_sha256']
    with (out/'cofactor_geometry.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
        for r in cfg['cofactors']:
            attrs=r['validation'][0]['attributes'] if r['validation'] else {}
            w.writerow(dict(pdb=r['pdb'],protomer=r['protomer'],role=r['role'],identity=r['identity'],carbonyl_bonds_A='; '.join('-'.join(b['atoms'])+':'+format(b['distance_A'],'.8f') for b in r['carbonyl_bonds']),ring_plane_RMS_A=format(r['ring_plane_RMS_A'],'.8f') if 'ring_plane_RMS_A' in r else '',max_abs_reported_bond_Z=r['max_abs_reported_bond_Z'],Q_score=attrs.get('Q_score',''),residue_inclusion=attrs.get('residue_inclusion',''),coordinate_source_sha256=cfg['validation_sources'][r['pdb']]['coordinate_source_sha256'],validation_xml_sha256=cfg['validation_sources'][r['pdb']]['sha256']))
    diagnostic=cfg.get('diagnostic_density_samples',[])
    if diagnostic:
        with (out/'diagnostic_density_samples.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(diagnostic[0]),lineterminator='\n');w.writeheader();w.writerows(diagnostic)
        (out/'axial_geometry.json').write_text(json.dumps(cfg['axial_geometry_review'],indent=1)+'\n',encoding='utf-8',newline='\n')
    rows=[dict(pdb=r['pdb'],protomer=r['protomer'],role=r['role'],identity=r['identity'],**o) for r in cfg['cofactors'] for v in r['validation'] for o in v['outliers'] if o['type']=='mog-bond-outlier']
    with (out/'bond_outliers.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=sorted({k for r in rows for k in r}),lineterminator='\n');w.writeheader();w.writerows(rows)
    print('Scientific review context:',len(cfg['cofactors']),'cofactor roles;',len(rows),'reported bond outliers')
if __name__=='__main__':main()
