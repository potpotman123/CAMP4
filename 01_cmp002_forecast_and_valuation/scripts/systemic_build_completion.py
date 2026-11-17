import json,re
from pathlib import Path
P=Path(__file__).resolve().parents[1]; D=P/'data/pos_completion'; S=P/'sources/pos_completion'; DAY='2026-11-16'
A=json.load(open(D/'systemic_assignment.json')); U={}
def norm(x):return re.sub('[^a-z0-9]','',x.lower())
for a in A:
 s=a['source_record']; reg=json.load(open(S/f"systemic_{a['source_record_id']}_registry.json")); trials=[]
 aliases=[x for x in s.get('aliases',[]) if len(norm(x))>=4 and len(x)<60]+[a['asset']]
 for st in reg['response'].get('studies',[]):
  q=st['protocolSection']; im=q['identificationModule']; sm=q['statusModule']; des=q.get('designModule',{}); ints=q.get('armsInterventionsModule',{}).get('interventions',[])
  names=' '.join(i['name']+' '+' '.join(i.get('otherNames',[])) for i in ints)
  matched=im['nctId'] in a['trial_ids'] or any(norm(x) in norm(names) for x in aliases if norm(x) not in ['cd34cells','genetherapy'])
  if not matched:continue
  trials.append({'nct_id':im['nctId'],'title':im['briefTitle'],'sponsor':q['sponsorCollaboratorsModule']['leadSponsor']['name'],'study_type':des.get('studyType'),'start':sm.get('startDateStruct',{}),'enrollment':des.get('enrollmentInfo',{}),'status':sm['overallStatus'],'completion':sm.get('completionDateStruct',{}),'last_update':sm.get('lastUpdatePostDateStruct',{}).get('date'),'why_stopped':sm.get('whyStopped'),'conditions':q.get('conditionsModule',{}).get('conditions',[]),'interventions':names,'fih_explicit':bool(re.search(r'first.in.human|first time.{0,50}human',json.dumps(q.get('descriptionModule',{}))+' '+im['briefTitle'],re.I))})
 trials.sort(key=lambda x:x['start'].get('date','9999'))
 dosed=[t for t in trials if t['study_type']=='INTERVENTIONAL' and t['start'].get('type')!='ESTIMATED' and not(t['status']=='WITHDRAWN' and t['enrollment'].get('count')==0)]
 first=dosed[0] if dosed else None
 evidence=[{'url':s.get('entry_evidence',{}).get('url'),'date':s.get('entry_evidence',{}).get('source_date'),'claim':'Original panel trial entry proxy; reviewed against alias-expanded histories.'}]+s.get('evidence',[])
 out=s.get('status','unknown');out='unknown_after_search' if out=='unknown' else out
 u={'id':a['id'],'canonical_asset':a['asset'],'indication':a['indication'],'candidate_ids':a['candidate_ids'],'asset_cluster':a['asset_cluster'],'disposition':'include' if first else 'unknown','disposition_reason':'Observed novel candidate in 2010–2024 trial frame; expanded public histories reviewed. Entry date remains earliest matched trial proxy unless explicit first-human evidence is recorded.','first_human_date': first['start'].get('date') if first else None,'first_human_precision':'trial_start_proxy' if first else 'unknown','first_human_verified':bool(first and first['fih_explicit']),'first_human_evidence': [{'url':'https://clinicaltrials.gov/study/'+first['nct_id'],'date':first['last_update'],'claim':'Earliest matched interventional trial in public alias history; actual enrollment/start are not necessarily the dosing date.'}] if first else [],'outcome':out,'outcome_date':s.get('outcome_date'),'outcome_date_precision':'source_reported' if s.get('outcome_date') else 'unknown','last_verified_active_date':None,'evidence':evidence,'searches':[{'query':reg['query_url'],'result':str(len(trials))+' matched trial histories saved; study status is not treated as the program outcome.','source_file':str((S/f"systemic_{a['source_record_id']}_registry.json").relative_to(P))}],'trial_history':trials,'remaining_uncertainty':['Global first dosing may precede the earliest observed registry start; retained as sensitivity unless explicit first-human evidence resolves it.'],'research_complete':False,'ever_fda_approved':s.get('ever_FDA_approved_in_this_indication'),'as_of':DAY}
 if first and first['start'].get('date','')<'2010':u.update(disposition='exclude',disposition_reason='Matched human exposure before the 2010 inception window; requires molecule-specific alias review recorded below.')
 U[a['id']]=u
# CFF is an operational trial-network/funder source, not a trial-status extrapolation.
C=json.load(open(S/'systemic_cff_details.json'))
cm={'AIR DNase':None,'POL6014':'Lonodelestat','GLPG2222':'SION-2222','GLPG3067':'ABBV-2222','IONIS-ENaCRx':'IONIS-ENaC','Inhaled AR-501':'AR-501','Inhaled SNSP113':'SNSP113','KB407 (Nebulization)':'KB407','Molgramostim':'Inhaled-Molgramostim','N91115':'Cavosonstat','PTI-428':'Nesolicaftor','PTI-801':'Posenacaftor','PTI-808':'Dirocaftor','QR-010':'Eluforsen','VX118':None,'VX440':'VX-440','VX659':'VX-659','VX828':'VX-828','VX522 mRNA':'VX-522','elexacaftor':'Trikafta','vanzacaftor':'Alyftrek','deutivacaftor':'Alyftrek','AeroVanc':'AeroVanc'}
for u in U.values():
 if u['indication']!='Cystic fibrosis':continue
 key=cm.get(u['canonical_asset'],u['canonical_asset'].replace(' ',''))
 matches=[c for c in C if key and norm(key) in norm(c['url'].split('/')[-1])]
 if not matches:continue
 c=matches[0];t=c.get('text','');a=t.find('Status ');b=t.find('Sponsor',a);ex=t[a:b];short=re.sub(r'\s+',' ',ex)
 status= 'stopped' if 'Status Discontinued' in ex and u['outcome']!='approved' else ('approved' if 'Status To Patients' in ex or 'has been approved' in ex else 'ongoing')
 u['outcome']=status;u['evidence'].append({'url':c['url'],'date':None,'retrieved_date':DAY,'claim':short[-600:],'source_type':'CFF trial-network program tracker'})
 u['searches'].append({'query':'CFF Drug Development Pipeline: '+key,'result':status+' at program level, not inferred from trial completion','source_file':'sources/pos_completion/systemic_cff_details.json'})
 if status=='stopped':u['outcome_date']=None;u['outcome_date_precision']='undated_stop_observed_by_cutoff';u['outcome_date_interval']=[None,DAY];u['remaining_uncertainty'].append('CFF confirms no active CF development but most stop dates are undated; cannot use retrieval day as an exact event date.')
 if status=='ongoing':u['last_verified_active_date']=DAY;u['active_date_basis']='CFF current page retrieved; source publication date unknown'
 u['research_complete']=True
# Curated rows keyed by integrated id, maintained separately from frozen datasets.
curfile=D/'systemic_curation.json'
if curfile.exists():
 for k,c in json.load(open(curfile)).items():
  u=U[k]
  for f,v in c.items():
   if f in ['evidence','searches','remaining_uncertainty']:u[f].extend(v)
   else:u[f]=v
# Attach recorded targeted query logs. Matching is name/alias only; adjudication always manual.
for f in sorted(S.glob('systemic_search*.json')):
 raw=json.load(open(f));qs=raw.get('queries',[]) if isinstance(raw,dict) else []
 for u in U.values():
  an=[u['canonical_asset']]+u.get('search_aliases',[])
  for q in qs:
   if any(norm(x) and norm(x) in norm(q) for x in an):
    u['searches'].append({'query':q,'result':'Targeted sponsor/regulator/publication search reviewed. Accepted evidence is listed separately; unaccepted or absent leads do not establish an outcome.','source_file':str(f.relative_to(P))})
# Standard date fields and explicit unresolved-after-search states.
for u in U.values():
 if u['first_human_date'] and u['first_human_date'][:4].isdigit():u['first_human_year']=int(u['first_human_date'][:4])
 if u['outcome']=='approved':u['ever_fda_approved']=True
 if u['research_complete'] and u['outcome']=='unknown_after_search':u['remaining_uncertainty'].append('No primary indication-specific approval, explicit program exit or current development confirmation found in logged searches; missing follow-up is not administrative censoring.')
 # Both flags are supplied for consumers; completed bounded review is not complete factual ascertainment.
 u['review_complete']=u['research_complete']
 u['research_completion_definition']='Assigned row reviewed against alias-expanded registry and targeted primary-source/operational-tracker evidence, including logged unresolved results. This does not mean entry or FDA status is known.'
 u['fda_search_aliases']=list(dict.fromkeys(u.get('fda_search_aliases',[])+[u['canonical_asset']]+u.get('search_aliases',[])))
 u['first_human_qualification']='documented_first_human_year_or_FIH_trial' if u['first_human_verified'] else 'earliest_observed_registry_proxy_or_unresolved'
 u['strict_entry_qualified']=bool(u['first_human_verified'] and u['disposition']=='include')
 u['entry_evidence_note']='The original registry evidence is retained as a historical proxy. Dated curated evidence below supersedes it wherever first_human_date was revised.'
 u['first_human_evidence']+= [e for e in u['evidence'] if any(w in (e.get('claim') or '').lower() for w in ['first','exposure','dosed','clinical entry','human trial','2013; registration'])]
 # Index the original saved search evidence by accepted source URLs without inventing lost query wording.
 u['source_snapshot_files']=[]
 for sf in list(S.glob('systemic_search*.json'))+list((P/'sources/pos_adjudication').glob('systemic_search*.json')):
  rawtext=sf.read_text()
  if any(e.get('url') and e['url'] in rawtext for e in u['evidence']):
   u['source_snapshot_files'].append(str(sf.relative_to(P)))
 if u['source_snapshot_files']:
  u['searches'].append({'query':'Prior and current primary-source evidence search; see original saved results (query wording not retained for early frozen batches).','result':'Accepted evidence source URLs matched to archived raw search output. This is a provenance index, not a new negative FDA assertion.','source_files':u['source_snapshot_files']})
(D/'systemic_updates.json').write_text(json.dumps(U,indent=2,ensure_ascii=False)+'\n')
(D/'systemic_research_log.json').write_text(json.dumps([{'id':u['id'],'asset':u['canonical_asset'],'disposition':u['disposition'],'outcome':u['outcome'],'searches':u['searches'],'remaining_uncertainty':u['remaining_uncertainty'],'research_complete':u['research_complete']} for u in U.values()],indent=2,ensure_ascii=False)+'\n')
from collections import Counter
print(len(U),Counter(u['outcome'] for u in U.values()),Counter(u['research_complete'] for u in U.values()))
