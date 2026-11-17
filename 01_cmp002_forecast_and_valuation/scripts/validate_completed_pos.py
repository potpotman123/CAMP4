"""Numerical/coverage checks, including adversarial censoring and cluster examples."""
import contextlib,io,json,runpy,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/'data/pos_completion'
with contextlib.redirect_stdout(io.StringIO()):ns=runpy.run_path(str(P/'scripts/analyze_completed_pos_panel.py'))
rows=ns['rows'];results=ns['results'];checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
check('All frozen nonexcluded assignments reviewed',ns['summary']['assigned_reviewed_rows']==449)
check('No unfinished assigned review',not ns['summary']['review_incomplete_ids'])
check('All mapped IDs unique',len({r['id'] for r in rows})==518)
check('No unresolved retained FDA inventory matches',not ns['summary']['nonapproved_inventory_hit_review'])
for r in rows:
 if r['observed_FDA_approval']:
  check(r['id']+' approval not future',bool(r['approval_date']) and r['approval_date']<='2026-11-16')
  if r['entry_qualified']:check(r['id']+' approval after entry lower bound',r['approval_date']>=r['entry_interval'][0])
for i,r in enumerate(results):
 for h in r['horizons']:
  k=f'{i}:{h["horizon_years"]}'
  check(k+' denominator distinct',len(h['denominator_ids'])==len(set(h['denominator_ids']))==h['mature_n'])
  check(k+' numerator subset',set(h['approval_ids'])<=set(h['possible_approval_ids'])<=set(h['denominator_ids']))
  check(k+' bounds ordered',0<=h['approvals_certain']<=h['approvals_possible_with_entry_interval']<=h['mature_n'])
  check(k+' maturity counts reconcile',h['mature_n']+h['entry_boundary_n']+h['immature_n']==r['n'])
def mock(i,lo,hi,app=None,cluster=None):return {'id':i,'entry_interval':[lo,hi],'approval_date':app,'observed_FDA_approval':bool(app),'asset_cluster':cluster or i,'FDA_approval_ascertainment':'test'}
calc=ns['calc'];dedup=ns['dedup']
t=calc([mock('stopped','2010-01-01','2010-01-01'),mock('approved','2010-01-01','2010-01-01','2014-01-01'),mock('immature','2024-01-01','2024-01-01')],5)
check('Stopped nonapproval retained and immature excluded',t['mature_n']==2 and t['approvals_certain']==1 and t['immature_n']==1)
t=calc([mock('interval','2010-01-01','2010-12-31','2015-06-01')],5)
check('Entry interval changes horizon numerator',t['approvals_certain']==0 and t['approvals_possible_with_entry_interval']==1)
t=calc([mock('boundary','2016-01-01','2016-12-31','2020-01-01')],10)
check('Maturity boundary does not silently enter primary denominator',t['mature_n']==0 and t['entry_boundary_n']==1 and t['boundary_all_eligible_sensitivity']['approval_fraction_interval']==[1,1])
t=dedup([mock('a_laterapproval','2013-01-01','2013-12-31','2023-12-08','shared'),mock('z_earlierapproval','2013-01-01','2013-12-31','2022-08-17','shared')])
check('Cluster event is earliest approval not lexical indication',len(t)==1 and t[0]['approval_date']=='2022-08-17' and t[0]['approval_event_source_id']=='z_earlierapproval')
manifest=[]
for directory in ['sources/pos_completion','data/pos_completion']:
 for f in sorted((P/directory).glob('*')):
  if not f.is_file() or f.name in ['validation.json','source_manifest.json']:continue
  manifest.append({'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(D/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(D/'validation.json').write_text(json.dumps({'checks_passed':len(checks),'checks':checks,'files_hashed':len(manifest),'independent_review_files':['data/pos_completion/neuro_analysis_review.json','data/pos_completion/neuro_final_qa.json'],'scope':'Arithmetic, identity linkage, date handling, review coverage, and reproducibility checks; not external validation of population representativeness or completeness.'},indent=2)+'\n')
print(f'{len(checks)} checks passed; {len(manifest)} files hashed')
