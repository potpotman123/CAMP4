"""Finite-panel approval horizons, preserving entry uncertainty and unresolved program fate.
This is not a lifetime approval estimator or a census of all rare-disease development.
"""
import json,re,calendar,math,collections,csv
from datetime import date
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/'data/pos_completion';CUTOFF=date(2026,11,16)
def load(f):return json.loads((P/f).read_text())
def interval(s,precision=None):
 if not s:return None
 s=str(s)[:10]
 try:
  if precision and ('proxy' in precision or 'registry' in precision) and re.match(r'^\d{4}',s):return [s[:4]+'-01-01',s[:4]+'-12-31']
  if len(s)==4:return [s+'-01-01',s+'-12-31']
  if len(s)==7:
   y,m=map(int,s.split('-'));return [s+'-01',s+f'-{calendar.monthrange(y,m)[1]:02}']
  date.fromisoformat(s)
  # Registry enrollment is not an exact dosing day: use its year for sensitivity.
  if precision and ('proxy' in precision or 'registry' in precision):return [s[:4]+'-01-01',s[:4]+'-12-31']
  return [s,s]
 except ValueError:return None
def anniversary(s,h):
 d=date.fromisoformat(s)
 try:return d.replace(year=d.year+h)
 except ValueError:return d.replace(year=d.year+h,day=28)
base=load('data/pos_adjudication/integrated_program_ledger.json');updates={};reviewfiles={}
for family in ['als','neuro','metabolic','systemic']:
 f=f'data/pos_completion/{family}_updates.json';x=load(f);x=list(x.values()) if isinstance(x,dict) else x
 for u in x:updates[u['id']]=u;reviewfiles[u['id']]=f
matches={r['id']:r for r in load('data/pos_completion/fda_inventory_matches.json')}
adjudication_file=D/'fda_hit_adjudication.json'
hit_adjudications=json.loads(adjudication_file.read_text()) if adjudication_file.exists() else []
if isinstance(hit_adjudications,dict):hit_adjudications=hit_adjudications.get('rows',list(hit_adjudications.values()))
hit_adjudications={r['id']:r for r in hit_adjudications}
status_audit_file=D/'six_program_status_audit.json'
status_audits={r['id']:r for r in json.loads(status_audit_file.read_text())} if status_audit_file.exists() else {}
rows=[]
for b in base:
 u=updates.get(b['id'],{});s=b['source_record'];disp=u.get('disposition','exclude' if b['reference_eligibility']=='excluded' else 'unknown')
 entry=u.get('first_human_date',u.get('entry_date',b['entry_proxy']))
 precision=u.get('first_human_precision',u.get('entry_precision','registry_start_proxy'))
 ints=u.get('first_human_interval') or u.get('first_human_date_interval') or u.get('entry_interval') or interval(entry,precision)
 if isinstance(ints,dict):ints=[ints.get('lower'),ints.get('upper')]
 if not ints or len(ints)!=2 or not all(ints):ints=None
 flags=dict(b['flags']);flags.update(u.get('flags',{}))
 outcome=u.get('outcome',b['status'])
 approved=u.get('FDA_ever_approved',u.get('ever_fda_approved'))
 appdate=u.get('FDA_approval_date',u.get('fda_approval_date'))
 if approved is None and outcome=='approved':approved=True
 if approved and not appdate:
  appdate=u.get('outcome_date',u.get('statusdate')) or s.get('outcome_date',s.get('status_date',s.get('event_date')))
 if isinstance(appdate,str):appdate=appdate[:10]
 # Historical target-indication approvals survive subsequent withdrawal; later indications do not qualify.
 hits=matches[b['id']]['matches']
 qualified=(disp=='include' and bool(ints) and ints[0]>='2010-01-01' and ints[1]<='2024-12-31')
 strict_entry=qualified and (u.get('entry_window_qualified') is True or u.get('first_human_verified') is True or u.get('first_human_entry_verified') is True or (precision in ['month','year','day','day_proxy','exact'] and bool(u.get('first_human_evidence',u.get('evidence')))))
 row={'id':b['id'],'asset':u.get('canonical_asset',b['asset']),'indication':b['indication'],'family':b['family'],'asset_cluster':u.get('asset_cluster',b['asset_cluster']),'disposition':disp,'disposition_reason':u.get('disposition_reason',b['eligibility_reason']),'entry_interval':ints,'entry_precision':precision,'entry_qualified':qualified,'strict_entry_qualified':strict_entry,'flags':flags,'closest4':u.get('closest_restoration_ASO4',s.get('closest_restoration_ASO4',False)),'outcome':outcome,'approval_date':appdate if approved else None,'observed_FDA_approval':bool(approved),'FDA_inventory_matches':len(hits),'FDA_approval_ascertainment':'indication_approval_primary_evidence' if approved else 'no_approval_identified_in_program_review_and_inventory' if not hits else 'inventory_hit_requires_target_indication_review','review_complete':u.get('review_complete',u.get('research_complete',bool(u.get('searches')))) if u else b['reference_eligibility']=='excluded','review_file':reviewfiles.get(b['id'],'data/pos_adjudication/integrated_program_ledger.json'),'remaining_uncertainty':u.get('remaining_uncertainty',[]),'last_verified_active_date':u.get('last_verified_active_date'),'original_entry_proxy':b['entry_proxy']}
 rows.append(row)
 if b['id'] in status_audits:
  audit=status_audits[b['id']]
  row['prior_review_outcome']=row['outcome'];row['outcome']=audit['outcome']
  row['latest_status_audit']=audit
  row['latest_status_audit_file']='data/pos_completion/six_program_status_audit.json'
  row['remaining_uncertainty']=[audit['uncertainty']]
 if b['id'] in hit_adjudications:row['FDA_approval_ascertainment']='inventory_hit_resolved_by_target_indication_review'
# No later indications or duplicate mixed-program rows may silently multiply independent assets.
def dedup(seq,latest=False):
 groups=collections.defaultdict(list)
 for r in seq:groups[r['asset_cluster']].append(r)
 out=[]
 for k,rs in groups.items():
  rs.sort(key=lambda r:(r['entry_interval'][0] if r['entry_interval'] else '9999',r['id']))
  # First approval among INCLUDED original/co-developed indications, never later excluded indications.
  # Shared combination clusters also get a latest-component clock sensitivity.
  chosen=dict(rs[-1] if latest else rs[0]);apps=sorted(r['approval_date'] for r in rs if r['observed_FDA_approval'] and r['approval_date'])
  chosen['observed_FDA_approval']=bool(apps);chosen['approval_date']=apps[0] if apps else None
  if apps:chosen['approval_event_source_id']=next(r['id'] for r in rs if r['approval_date']==apps[0] and r['observed_FDA_approval'])
  chosen['cluster_member_ids']=[r['id'] for r in rs]
  out.append(chosen)
 return out
def tiers(r):
 f=r['flags'];v=['R1 rare panel']
 if f.get('genetic_cns'):
  v+=['R2 genetic CNS']
  if f.get('genetic_medicine'):
   v+=['R3 genetic CNS genetic medicine']
   if f.get('intrathecal') and f.get('protein_restoration') and f.get('neurodevelopmental'):v+=['R4 intrathecal restoration neurodevelopment']
 if r['closest4']:v+=['R5 four closest ASO peers']
 return v
def wilson(a,n):
 if not n:return None
 z=1.95996398454;p=a/n;den=1+z*z/n;c=(p+z*z/(2*n))/den;rad=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return [c-rad,c+rad]
def calc(seq,h):
 mature=[r for r in seq if r['entry_interval'] and anniversary(r['entry_interval'][1],h)<=CUTOFF]
 boundary=[r for r in seq if r['entry_interval'] and anniversary(r['entry_interval'][0],h)<=CUTOFF<anniversary(r['entry_interval'][1],h)]
 certain=[];possible=[]
 for r in mature:
  if not r['observed_FDA_approval'] or not r['approval_date']:continue
  ad=date.fromisoformat(r['approval_date'])
  if ad<=anniversary(r['entry_interval'][0],h):certain.append(r['id'])
  if ad<=anniversary(r['entry_interval'][1],h):possible.append(r['id'])
 n=len(mature)
 ambiguous=[r['id'] for r in mature if r['FDA_approval_ascertainment']=='inventory_hit_requires_target_indication_review']
 bc=bp=0
 for r in boundary:
  if r['observed_FDA_approval'] and r['approval_date']:
   ad=date.fromisoformat(r['approval_date']);bc+=ad<=anniversary(r['entry_interval'][0],h);bp+=ad<=CUTOFF
 bn=n+len(boundary)
 event_sources=[{'denominator_id':r['id'],'approval_event_source_id':r.get('approval_event_source_id',r['id']),'approval_date':r['approval_date'],'cluster_member_ids':r.get('cluster_member_ids',[r['id']])} for r in mature if r['id'] in possible]
 return {'horizon_years':h,'mature_n':n,'approvals_certain':len(certain),'approvals_possible_with_entry_interval':len(possible),'observed_approval_fraction_interval':[len(certain)/n,len(possible)/n] if n else None,'approval_event_sources':event_sources,'unresolved_FDA_hit_ids':ambiguous,'approval_fraction_upper_if_all_unresolved_hits_succeed':(len(possible)+len(ambiguous))/n if n else None,'wilson95_descriptive':wilson(len(certain),n),'entry_boundary_n':len(boundary),'boundary_all_eligible_sensitivity':{'assumption':'Every entry-date boundary case entered early enough to complete the horizon; this is not established fact.','n':bn,'approval_fraction_interval':[(len(certain)+bc)/bn,(len(possible)+bp)/bn] if bn else None},'denominator_ids':[r['id'] for r in mature],'approval_ids':certain,'possible_approval_ids':possible,'entry_boundary_ids':[r['id'] for r in boundary],'immature_n':len(seq)-n-len(boundary)}
results=[]
for rule in ['entry_qualified','strict_entry_qualified','entry_uncertainty_sensitivity']:
 selected=[r for r in rows if r.get(rule)]
 if rule=='entry_uncertainty_sensitivity':
  selected=[]
  for r in rows:
   if r['disposition']=='exclude':continue
   q=dict(r)
   if not r['entry_qualified']:q['entry_interval']=interval(r['original_entry_proxy'],'registry_start_proxy')
   if q['entry_interval'] and q['entry_interval'][0]>='2010-01-01' and q['entry_interval'][1]<='2024-12-31':selected.append(q)
 for unit in ['drug_indication','asset_cluster','asset_cluster_latest_entry']:
  for tier in ['R1 rare panel','R2 genetic CNS','R3 genetic CNS genetic medicine','R4 intrathecal restoration neurodevelopment','R5 four closest ASO peers']:
   seq=[r for r in selected if tier in tiers(r)];seq=dedup(seq,latest=unit=='asset_cluster_latest_entry') if unit.startswith('asset_cluster') else seq
   for era in ['2010_2024','2010_2020','2015_2020']:
    years=(2010,2024) if era=='2010_2024' else (2010,2020) if era=='2010_2020' else (2015,2020)
    sub=[r for r in seq if int(r['entry_interval'][0][:4])>=years[0] and int(r['entry_interval'][1][:4])<=years[1]]
    results.append({'selection':rule,'unit':unit,'tier':tier,'entry_era':era,'n':len(sub),'approved_by_cutoff':sum(r['observed_FDA_approval'] for r in sub),'horizons':[calc(sub,h) for h in [5,8,10]]})
summary={'as_of':str(CUTOFF),'mapped_rows':len(rows),'updated_rows_including_prior_exclusions':len(updates),'assigned_nonexcluded_rows':len(load('data/pos_completion/frozen_assignment.json')['rows']),'assigned_reviewed_rows':sum(r['id'] in updates for r in load('data/pos_completion/frozen_assignment.json')['rows']),'dispositions':dict(collections.Counter(r['disposition'] for r in rows)),'entry_qualified':sum(r['entry_qualified'] for r in rows),'strict_entry_qualified':sum(r['strict_entry_qualified'] for r in rows),'review_incomplete_ids':[r['id'] for r in rows if not r['review_complete']],'outcomes':dict(collections.Counter(r['outcome'] for r in rows)),'nonapproved_inventory_hit_review':[r['id'] for r in rows if r['disposition']!='exclude' and r['FDA_approval_ascertainment']=='inventory_hit_requires_target_indication_review'],'approved_without_day_date':[r['id'] for r in rows if r['observed_FDA_approval'] and (not r['approval_date'] or len(r['approval_date'])!=10)],'limitations':['Finite 48-condition public-registry discovery frame, not a population census or all-drug rate.','No approval identified is an operational search result; alias and historical CBER coverage gaps remain.','Mature horizon rates are not lifetime PoS. Unknown development fate remains in denominator.','Strict entry evidence may select better-documented programs; compare inclusive and entry-uncertainty sensitivities.','Wilson intervals describe binomial sampling uncertainty only, not selection, ascertainment, correlated assets or missing programs.']}
(D/'completed_program_ledger.json').write_text(json.dumps(rows,indent=2)+'\n')
(D/'approval_horizon_results.json').write_text(json.dumps(results,indent=2)+'\n')
(D/'completion_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
