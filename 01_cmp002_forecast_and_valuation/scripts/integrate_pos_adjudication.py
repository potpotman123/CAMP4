"""Integrate independently reviewed slices without converting incomplete histories into PoS."""
import json, re, hashlib, math
from collections import Counter, defaultdict
from pathlib import Path
P=Path(__file__).resolve().parents[1]
D=P/'data/pos_adjudication'
load=lambda f:json.loads((D/f).read_text())
put=lambda f,v:(D/f).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
files={'als':'als_program_ledger.json','neuro':'neuro_program_ledger.json','metabolic':'metabolic_program_ledger.json','systemic':'systemic_programs.json'}
rows=[]
for family,f in files.items():
 for z in load(f):
  r={'id':family+':'+z['program_id'],'source_file':f,'source_record_id':z['program_id'],'family':family,'asset':z['asset'],'indication':z['indication'],'candidate_ids':z.get('candidate_ids',[]),'trial_ids':z.get('nct_ids',z.get('trial_ids',[])),'entry_proxy':z.get('entry_date_proxy',z.get('entry_date')),'first_human_verified':bool(z.get('entry_is_first_human_verified',z.get('first_human_entry_verified',False))),'status':z.get('status',z.get('outcome')),'flags':{},'source_record':z}
  if family=='als':
   e=z['cohort_disposition'];r['reference_eligibility']='excluded' if e.startswith('exclude') else 'provisional_reference'
   r['eligibility_reason']=z['eligibility_note'];r['flags']={k:z.get(v) for k,v in {'rare':'rare_nononcology','genetic_cns':'genetic_cns','genetic_medicine':'genetic_medicine','novel_target':'novel_target_at_entry','intrathecal':'intrathecal','protein_restoration':'protein_restoration','neurodevelopmental':'neurodevelopmental'}.items()}
   r['sources']=z.get('status_sources',[]);r['outcome_review']='targeted' if r['sources'] or z.get('outcome_search_performed') else 'registry_only'
  elif family=='neuro':
   e=z['cohort_eligibility'];r['reference_eligibility']='excluded' if e.startswith('exclude') else 'unresolved_entry' if e=='pending_actual_clinical_entry' else 'provisional_reference'
   # Known later-human-use cases cannot silently enter a de-novo first-human reference.
   if z.get('prior_human_data_before_entry') is True and z['asset'] in ['ganaxolone','trofinetide','sarizotan','gaboxadol','basimglurant','olesoxime','branaplam']:
    r['reference_eligibility']='excluded';e+='; prior human evidence before this indication entry'
   r['eligibility_reason']=e;r['flags']={k:z.get(v) for k,v in {'rare':'rare_nononcology','genetic_cns':'genetically_defined_cns','genetic_medicine':'genetic_medicine','novel_target':'novel_target_at_entry','intrathecal':'intrathecal','protein_restoration':'protein_restoration','neurodevelopmental':'neurodevelopmental'}.items()}
   r['sources']=z.get('outcome_sources',[]);r['outcome_review']='targeted' if r['sources'] or z.get('research_log_key') else 'registry_only'
  elif family=='metabolic':
   e=z['eligibility'];v=e['registry_entry_reference_cohort'];r['reference_eligibility']='provisional_reference' if v is True else 'excluded' if v is False else 'unresolved_entry'
   r['eligibility_reason']=e['reason'];r['first_human_verified']=e.get('verified_first_human_2010_2024') is True
   ff=z['filters'];r['flags']={k:ff.get(v) for k,v in {'rare':'rare_nononcology','genetic_cns':'genetically_defined_cns','genetic_medicine':'genetic_medicine','novel_target':'novel_target_at_entry','intrathecal':'intrathecal','protein_restoration':'protein_restoration'}.items()};r['flags']['neurodevelopmental']=False
   r['sources']=z.get('evidence',[]);r['outcome_review']='registry_only' if z.get('search_status','').startswith('registry') else 'targeted'
  else:
   e=z['eligibility'];r['reference_eligibility']='excluded' if e.startswith('exclude') else 'unresolved_entry' if e in ['pending_program_indication_split','pending_indication_linkage','pending_component_and_prior_human_entry'] else 'provisional_reference'
   if z.get('never_dosed_boundary'):r['reference_eligibility']='excluded'
   r['eligibility_reason']=z['eligibility_reason'];ff=z['tier_flags'];r['flags']={k:ff.get(v) for k,v in {'rare':'rare','genetic_cns':'geneticCNS','genetic_medicine':'geneticmedicine','novel_target':'noveltarget','intrathecal':'intrathecal','protein_restoration':'proteinrestoration'}.items()};r['flags']['neurodevelopmental']=False
   r['sources']=z['evidence'];r['outcome_review']='registry_only' if z['research_depth'].startswith('registry') else 'targeted'
  # FDA-specific endpoint; China-only ciprocopan and other-country approvals remain unresolved for US.
  approved=(z.get('ever_FDA_approved_in_this_indication') is True) if family=='systemic' else (z.get('approved_in_US') is True) if family=='metabolic' else r['status'] in ['approved','approved_then_withdrawn']
  stop=r['status'].startswith('stopped')
  # Reversible suspension, sponsor exit while seeking partners, or formulation-only cessation are not global program cessation.
  if family=='systemic' and z['asset']=='nomacopan':stop=False
  if family=='metabolic' and z.get('slug')=='bmn701':stop=False
  if r['status'] in ['stopped_formulation','stopped_regulatory_strategy']:stop=False
  r['endpoint']='FDA_approved' if approved else 'program_stop_observed' if stop else 'unresolved'
  r['endpoint_note']='Observed program stop is conditional on no later restart; not proof of irreversible biological failure.' if stop else None
  r['asset_cluster']=z.get('asset_cluster_id') or re.sub('[^a-z0-9]','',z['asset'].lower())
  if family=='systemic' and z['asset'] in ['pozelimab','cemdisiran'] and z['indication']=='PNH':r['asset_cluster']='pozelimab_cemdisiran_PNH_combination'
  r['strict_inception_estimator_eligible']=False # No combined first-entry + exhaustive follow-up qualification has been completed.
  rows.append(r)
# No cross-slice candidate or trial overlaps are silently resolved. Multi-indication observations stay correlated.
cross=[]
for key in ['candidate_ids','trial_ids']:
 idx=defaultdict(list)
 for r in rows:
  for n in r[key]:idx[n].append(r)
 for n,rr in idx.items():
  if len({x['family'] for x in rr})>1:cross.append({'key':key,'value':n,'records':[x['id'] for x in rr]})
if cross:raise ValueError('Cross-slice identity collision needs adjudication: '+str(cross))
# Exclude later-era inherited ASO references if the broad date window is violated.
for r in rows:
 if r['entry_proxy'] and not ('2010'<=r['entry_proxy'][:4]<='2024'):
  r['reference_eligibility']='excluded';r['eligibility_reason']+='; outside2010–2024 observed-entry window'
# Branaplam had human SMA exposure before the later Huntington program.
for r in rows:
 if r['asset']=='branaplam' and r['indication']=='Huntington':
  r['reference_eligibility']='excluded';r['eligibility_reason']+='; earlier human SMA exposure in2015 before2021 HD entry'
base=[r for r in rows if r['reference_eligibility']=='provisional_reference']
closest={'zorevunersen','apazunersen','rugonersen','obudanersen'}
filters=[('R1','Broad mapped rare-disease reference',['rare']),('R2','Genetically defined CNS indication',['rare','genetic_cns']),('R3','CNS + nucleic-acid / gene-modified therapy',['rare','genetic_cns','genetic_medicine']),('R4','Closest four intrathecal restoration ASOs',['rare','genetic_cns','genetic_medicine','intrathecal','protein_restoration','neurodevelopmental'])]
def stats(rr):
 n=len(rr);a=sum(r['endpoint']=='FDA_approved' for r in rr);f=sum(r['endpoint']=='program_stop_observed' for r in rr);u=n-a-f
 # These are finite-reference completion envelopes, NEVER population CIs/PoS.
 return {'n':n,'unique_asset_clusters':len({r['asset_cluster'] for r in rr}),'FDA_approved':a,'program_stop_observed':f,'unresolved':u,'reported_ongoing':sum(r['status'].startswith('ongoing') for r in rr),'unknown_program_fate':sum(r['status']=='unknown' for r in rr),'first_human_verified_count':sum(r['first_human_verified'] for r in rr),'targeted_review_count':sum(r['outcome_review']=='targeted' for r in rr),'observed_approval_fraction':a/n if n else None,'conditional_completion_envelope':[a/n,(n-f)/n] if n else None,'remaining_approvals_needed_for_at_least_25pct':max(0,math.ceil(.25*n)-a),'required_fraction_of_unresolved_for_at_least_25pct':max(0,math.ceil(.25*n)-a)/u if u else None,'member_ids':[r['id'] for r in rr],'not_a_PoS_estimate':True}
summaries=[]
for code,label,flags in filters:
 rr=[r for r in base if all(r['flags'].get(k) is True for k in flags)]
 if code=='R4':rr=[r for r in rr if r['asset'] in closest]
 possible=[r for r in base if all(r['flags'].get(k) is not False for k in flags) and any(r['flags'].get(k) is None for k in flags)]
 if code=='R4':possible=[r for r in possible if r['asset'] in closest]
 s={'tier':code,'label':label,'membership_definition':flags,'unresolved_filter_membership_count':len(possible),**stats(rr)}
 s['entry_vintage']={lo+'–'+hi:stats([r for r in rr if r['entry_proxy'] and lo<=r['entry_proxy'][:4]<=hi]) for lo,hi in [('2010','2016'),('2017','2020'),('2021','2024')]};summaries.append(s)
# Systemic completion benchmark, kept separate from CNS biological matching.
hae=[r for r in base if r['source_record'].get('in_finite_HAE_PNH_reference_frame')]
# Explicit record-granularity imperfections remain in the master ledger.
checks=[]
def ck(name,test):
 assert test,name
 checks.append({'check':name,'passed':True})
ck('Unique integrated IDs',len(rows)==len({r['id'] for r in rows}))
ck('No cross-slice identity collisions',not cross)
ck('All four closest included',set(r['asset'] for r in base if r['id'] in summaries[-1]['member_ids'])==closest)
for i,s in enumerate(summaries):
 ck('Status counts reconcile '+s['tier'],s['n']==s['FDA_approved']+s['program_stop_observed']+s['unresolved'])
 if i:ck('Nested membership '+s['tier'],set(s['member_ids'])<=set(summaries[i-1]['member_ids']))
 ck('Bounds correct '+s['tier'],0<=s['conditional_completion_envelope'][0]<=s['conditional_completion_envelope'][1]<=1)
ck('No unqualified empirical PoS rows',not any(r['strict_inception_estimator_eligible'] for r in rows))
ck('Zero enrollment ARO-SOD1 excluded',next(r for r in rows if r['asset']=='ARO-SOD1')['reference_eligibility']=='excluded')
ck('China-only ciprocopan not FDA success',all(r['endpoint']!='FDA_approved' for r in rows if r['asset']=='ciprocopan'))
ck('Suspensions not permanent failures',all(r['endpoint']=='unresolved' for r in rows if r['asset'] in ['nomacopan','IPL344','FLX-787']))
# All606 priority buckets must have a disposition, not necessarily a canonical eligible program.
dispfiles=['als_candidate_dispositions.json','neuro_candidate_dispositions.json','metabolic_candidate_dispositions.json','systemic_dispositions.json']
disp=[]
for f in dispfiles:
 d=load(f)
 if isinstance(d,dict):d=d.get('dispositions',d.get('candidates',[]))
 disp+=d
allids={d['candidate_id'] for d in disp};priority={r['candidate_id'] for r in load('full_screen.json') if r['disposition']=='priority_early_industry'}
missing=sorted(priority-allids)
ck('Every priority bucket has a disposition',not missing)
output={'as_of':'2026-11-16','scope':'Purposive48-disease panel; finite reference set after identity review, NOT all rare-disease development','integrated_rows':len(rows),'reference_eligibility_counts':dict(Counter(r['reference_eligibility'] for r in rows)),'mapped_candidate_ids':len({i for r in rows for i in r['candidate_ids']}),'all_dispositioned_candidate_ids':len(allids),'priority_buckets_dispositioned':len(priority-set(missing)),'priority_buckets_total':len(priority),'all_row_status_counts':dict(Counter(r['status'] for r in rows)),'all_row_endpoint_counts':dict(Counter(r['endpoint'] for r in rows)),'nested_reference_results':summaries,'HAE_PNH_reference':stats(hae),'HAE_PNH_verified_first_human_subset':stats([r for r in hae if r['first_human_verified']]),'empirical_lifetime_PoS':None,'estimator_run':False,'reason_estimator_not_run':'First-human inception, complete program ascertainment, per-indication identity and continuous outcome follow-up are not jointly verified; current unknowns are not valid independent right-censoring times.','interpretation':'A/N is observed approvals to date among selected proxy-entry records. Envelopes assume all observed stops stay stopped and unresolved rows can either approve or not. They ignore sampling uncertainty and do not estimate CMP-002 PoS. The25% hurdle is arithmetic, not a calibrated forecast.','input_hashes':{f:hashlib.sha256((D/f).read_bytes()).hexdigest() for f in [*files.values(),*dispfiles]}}
put('integrated_program_ledger.json',rows);put('nested_reference_results.json',output);put('integration_validation.json',{'checks':checks,'passed':len(checks),'cross_slice_collisions':cross,'missing_priority_candidate_ids':missing})
put('remaining_work_queue.json',[{'id':r['id'],'asset':r['asset'],'indication':r['indication'],'reference_eligibility':r['reference_eligibility'],'first_human_verified':r['first_human_verified'],'outcome_review':r['outcome_review'],'status':r['status'],'missing_flags':[k for k,v in r['flags'].items() if v is None],'source_file':r['source_file']} for r in rows if r['reference_eligibility']!='excluded' and (r['status']=='unknown' or not r['first_human_verified'])])
print(json.dumps({k:v for k,v in output.items() if k not in ['input_hashes','nested_reference_results','HAE_PNH_reference','HAE_PNH_verified_first_human_subset']},indent=2))
for s in summaries:print(s['tier'],s['n'],s['FDA_approved'],s['program_stop_observed'],s['unresolved'],'missingflags',s['unresolved_filter_membership_count'])
print('HAE_PNH', {k:v for k,v in stats(hae).items() if k!='member_ids'})
print('CHECKS',len(checks))
