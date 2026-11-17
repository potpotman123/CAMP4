"""Reproducible screening universe. All unadjudicated program flags remain unknown."""
import json,re,hashlib,zipfile,csv,io,sqlite3
from pathlib import Path
from collections import defaultdict,Counter
P=Path(__file__).resolve().parents[1];S=P/'sources/pos_nested';D=P/'data/pos_nested';D.mkdir(exist_ok=True)
def norm(x): return re.sub(r'[^a-z0-9]','',x.lower())
def read(p):return json.loads(p.read_text())
def write(n,x):(D/n).write_text(json.dumps(x,indent=2)+'\n')
manifest=read(D/'broad_allphase_retrieval_manifest.json');studies={};families=defaultdict(set)
for m in manifest:
 if m.get('error'):continue
 for r in read(S/m['file'])['studies']:
  n=r['protocolSection']['identificationModule']['nctId'];studies[n]=r;families[n].add(m['group'])
# FDA exact ingredient/brand matches are screening flags, NOT indication approvals.
z=zipfile.ZipFile(S/'drugsatfda_2026-11-16.zip')
def table(name):return list(csv.DictReader(io.StringIO(z.read(name).decode('utf-8-sig',errors='replace')),delimiter='\t'))
submissions=table('Submissions.txt');originals={}
for r in submissions:
 if r['SubmissionType']=='ORIG' and r['SubmissionStatus']=='AP':
  k=r['ApplNo'];d=r['SubmissionStatusDate'][:10]
  if d and d<originals.get(k,'9999'):originals[k]=d
idx=defaultdict(list)
for r in table('Products.txt'):
 for name in [r['DrugName'],r['ActiveIngredient']]:
  key=norm(name)
  if key:
   v={'application':r['ApplNo'],'brand':r['DrugName'],'ingredient':r['ActiveIngredient'],'original_approval_date':originals.get(r['ApplNo'])}
   if v not in idx[key]:idx[key].append(v)
trials=[];mentions=[];excluded=[]
for n,r in sorted(studies.items()):
 p=r['protocolSection'];d=p.get('designModule',{});s=p['statusModule'];a=p.get('armsInterventionsModule',{});conds=p.get('conditionsModule',{}).get('conditions',[])
 start=s.get('startDateStruct',{}).get('date');year=int(start[:4]) if start else None
 t={'nct_id':n,'title':p['identificationModule']['briefTitle'],'conditions':conds,'families':sorted(families[n]),'start_date':start,'start_date_type':s.get('startDateStruct',{}).get('type'),'phases':d.get('phases',[]),'registry_status':s.get('overallStatus'),'why_stopped':s.get('whyStopped'),'sponsor':p.get('sponsorCollaboratorsModule',{}).get('leadSponsor',{}),'last_update':s.get('lastUpdatePostDateStruct',{}).get('date'),'source':f'https://clinicaltrials.gov/study/{n}','entry_window_candidate':year is not None and 2010<=year<=2024}
 trials.append(t)
 for i in a.get('interventions',[]):
  name=i['name'];roles={g.get('type') for g in a.get('armGroups',[]) if any(norm(x.split(':',1)[-1])==norm(name) for x in g.get('interventionNames',[]))}
  reason=None
  if i.get('type') not in ['DRUG','BIOLOGICAL','GENETIC']:reason='not_drug_biological_or_genetic'
  elif re.search(r'\b(placebo|saline|vehicle)\b',name,re.I):reason='control_name'
  elif roles and 'EXPERIMENTAL' not in roles:reason='only_nonexperimental_arm'
  if reason:excluded.append({'nct_id':n,'name':name,'reason':reason});continue
  names=[name]+i.get('otherNames',[]);matches=[]
  for alias in names:
   for f in idx.get(norm(alias),[]):
    if f not in matches:matches.append(f)
  mentions.append({'nct_id':n,'intervention_name':name,'aliases':i.get('otherNames',[]),'intervention_type':i['type'],'arm_roles':sorted(x for x in roles if x),'conditions':conds,'families':t['families'],'start_date':start,'entry_window_candidate':t['entry_window_candidate'],'sponsor':t['sponsor'].get('name'),'description':i.get('description'),'exact_fda_name_matches':matches,'match_interpretation':'Ingredient/brand match only; indication, formulation, dates and original-versus-supplement require review. No match is NOT failure.'})
# Conservative exact-name + exact-condition-set buckets. Not assertively merged across aliases.
buckets={}
for m in mentions:
 key=norm(m['intervention_name'])+'|'+'|'.join(sorted(norm(x) for x in m['conditions']))
 if key not in buckets:buckets[key]={'candidate_id':hashlib.sha256(key.encode()).hexdigest()[:16],'intervention_name':m['intervention_name'],'conditions':m['conditions'],'nct_ids':[],'families':set(),'aliases':set(),'dates':[],'fda_matches':[],'sponsors':set()}
 b=buckets[key];b['nct_ids'].append(m['nct_id']);b['families'].update(m['families']);b['aliases'].update(m['aliases']);b['sponsors'].add(m['sponsor'] or '')
 if m['start_date']:b['dates'].append(m['start_date'])
 for f in m['exact_fda_name_matches']:
  if f not in b['fda_matches']:b['fda_matches'].append(f)
candidates=[]
for b in buckets.values():
 for k in ['families','aliases','sponsors']:b[k]=sorted(b[k])
 b['nct_ids']=sorted(set(b['nct_ids']));b['earliest_observed_panel_trial_date']=min(b.pop('dates'),default=None)
 y=int(b['earliest_observed_panel_trial_date'][:4]) if b['earliest_observed_panel_trial_date'] else None
 b['entry_window_candidate']=y is not None and 2010<=y<=2024
 b['entry_vintage_candidate']='2010-2020' if y is not None and 2010<=y<=2020 else '2021-2024' if y is not None and 2021<=y<=2024 else 'outside_or_unknown'
 b['verified_program_id']=None;b['verified_program_outcome']=None;b['verified_first_human_entry']=None
 b['filters']={k:None for k in ['rare_nononcology','genetically_defined_cns','novel_target_genetic_medicine','intrathecal_protein_restoration_neurodevelopment']}
 b['review_required']=['identity_and_aliases','condition_subtype_and_rarity','prior_human_exposure_and_earlier_trials','experimental_vs_background_agent','registration_intent','program_outcome_and_date']
 candidates.append(b)
write('trial_inventory.json',trials);write('intervention_mentions.json',mentions);write('excluded_interventions.json',excluded);write('candidate_review_queue.json',candidates)
# Rebuildable relational workspace, not committed (JSON inputs are authoritative).
db=P/'work/pos_nested.sqlite';db.parent.mkdir(exist_ok=True);c=sqlite3.connect(db)
for name,items in [('trials',trials),('candidate_programs',candidates),('intervention_mentions',mentions)]:
 c.execute(f'DROP TABLE IF EXISTS {name}');c.execute(f'CREATE TABLE {name} (id INTEGER PRIMARY KEY, record_json TEXT NOT NULL)');c.executemany(f'INSERT INTO {name}(record_json) VALUES (?)',[(json.dumps(x),) for x in items])
c.commit();c.close()
summary={'as_of':'2026-11-16','disease_search_terms':sum(map(len,read(D/'disease_panel.json')['groups'].values())),'unique_trials':len(trials),'query_returned_rows_including_overlap':sum(m.get('returned',0) for m in manifest),'all_queries_paginated_to_end':all(not ms[-1].get('error') and not ms[-1].get('next_page') for g in {m['group'] for m in manifest} for ms in [[m for m in manifest if m['group']==g]]),'trial_status_counts':dict(Counter(t['registry_status'] for t in trials)),'eligible_intervention_mentions':len(mentions),'excluded_intervention_mentions':len(excluded),'provisional_exact_name_condition_buckets':len(candidates),'buckets_with_candidate_entry_2010_2024':sum(b['entry_window_candidate'] for b in candidates),'entry_vintages':dict(Counter(b['entry_vintage_candidate'] for b in candidates)),'buckets_with_exact_fda_name_match':sum(bool(b['fda_matches']) for b in candidates),'verified_broad_program_denominator':None,'estimated_broad_approval_probability':None,'why_no_pos':'Search panel is purposive, aliases/subtypes and background agents remain unadjudicated; trial status is not program outcome; FDA matches are not indication approvals. No denominator or independent outcome rate is claimed.'}
assert len({t['nct_id'] for t in trials})==len(trials)
assert len({b['candidate_id'] for b in candidates})==len(candidates)
assert all(set(b['nct_ids'])<=set(studies) for b in candidates)
assert all(b['verified_program_outcome'] is None for b in candidates)
assert all(all(v is None for v in b['filters'].values()) for b in candidates)
summary['validation']='Unique trial/candidate IDs, provenance joins, unknown-outcome and unknown-filter safeguards passed.'
write('broad_summary.json',summary)
print(json.dumps(summary,indent=2))
