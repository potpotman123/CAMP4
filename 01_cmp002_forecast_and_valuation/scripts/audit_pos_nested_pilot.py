import json,hashlib
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1];S=P/'sources/pos_nested';D=P/'data/pos_nested'
def read(p):return json.loads(p.read_text())
configs=[
('nusinersen','SMA','NCT01494701','2011-11-30','approved','2016-12-23','pilot_fda_nusinersen.json','First-entry trial recovered; later delivery and postapproval studies must not create new programs.'),
('GTX102','Angelman syndrome','NCT04259281','2020-02-24','stopped_efficacy','2026-11-04','../pos_audit/source_registry.json:gtx_failure,gtx_winddown','Exclude NCT05531890: different GTX-102 drug in ataxia telangiectasia. Name alone is not identity.'),
('vosoritide','Achondroplasia','NCT01590446','2012-02','approved','2021-11-19','pilot_fda_vosoritide.json','Earliest recovered indication trial is not necessarily first human dosing; healthy-volunteer/pre-entry exposure still requires audit. Exclude later MPS/short-stature indications.'),
('olipudase','Acid sphingomyelinase deficiency','NCT00410566','2006-12','approved','2022-08-31','pilot_fda_olipudase.json','Initial search missed rhASM entry and began in2013. Corrected entry predates2010; exclude from2010+ inception denominator.'),
('ataluren','Duchenne muscular dystrophy','NCT00264888','2005-12','unresolved_for_this_pilot',None,None,'First recovered DMD study is Phase2; earlier Phase1 and global vs US outcomes need review. Pre2010, exclude. FDA no-hit does not establish failure.'),
('valoctocogene','Hemophilia A','NCT02576795','2015-09-28','approved','2023-06-29','https://www.fda.gov/news-events/press-announcements/fda-approves-first-gene-therapy-adults-severe-hemophilia','openFDA ingredient search no-hit; official CBER/FDA approval confirms success. Verify any later commercial withdrawal separately from first approval.'),
('aceer','GNE myopathy','NCT01359319','2011-07','sponsor_exit_not_global_terminal_failure','2017-08','https://ir.ultragenyx.com/node/11086/html','Alias SA-ER recovers Phase1 missed by modern names. Ultragenyx exit is not proof of global asset termination; Japan development continued. Do not hard-code competing failure without territorial/program scope.'),
('tominersen','Huntington disease','NCT02519036','2015-08-06','stopped_efficacy','2026-07-09','../pos_audit/source_registry.json:roche_letter','Initial dose arms must collapse to one asset; 2021 trial stopping was not final program termination because development resumed.')]
rows=[]
for name,ind,nct,entry,status,date,source,note in configs:
 raw=read(S/f'pilot_ctg_{name}.json');r={'asset_key':name,'indication':ind,'initial_search_trial_n':len(raw['studies']),'initial_search_complete':not raw.get('nextPageToken'),'entry_trial_after_review':nct,'entry_date_proxy_after_review':entry,'entry_date_precision':'month' if len(entry)==7 else 'day','entry_type':'study start; not proven first dose','program_outcome_adjudication':status,'event_date':date,'outcome_source':source,'note':note,'eligible_2010plus_by_recovered_indication_entry':entry>='2010','eligible_as_population_rate_observation':False,'eligibility_reason':'Purposive technical pilot; first-human exposure, registration intent and complete cohort ascertainment not established.'};rows.append(r)
prior=read(P/'data/pos_audit/program_ledger.json');allids={x['nct_id'] for x in read(D/'trial_inventory.json')};phaseids=set()
for p in S.glob('broad_*_1.json'):
 if 'allphase' in p.name:continue
 phaseids.update(x['protocolSection']['identificationModule']['nctId'] for x in read(p)['studies'])
reference=[]
for r in prior:
 reference.append({'asset':r['asset'],'indication':r['indication'],'entry_trial':r['entry_trial'],'phase1_query_recovered':r['entry_trial'] in phaseids,'allphase_query_recovered':r['entry_trial'] in allids,'source_ledger':'../pos_audit/program_ledger.json','outcome':r['status_asof'],'source_ids':r['status_sources'],'note':'Reference coverage check, not a new independent outcome observation or proof of complete recall.'})
audit={'pilot_programs':rows,'pilot_trial_results_total':sum(x['initial_search_trial_n'] for x in rows),'all_pilot_queries_paginated':all(x['initial_search_complete'] for x in rows),'phase_filter_false_negatives_recovered':[x for x in reference if not x['phase1_query_recovered'] and x['allphase_query_recovered']],'reference_crosswalk':reference,'api_findings':['FDA orphan POST returned search form rather than results; GET and repeat known-drug requests returned503. No designation cohort was extracted.','openFDA ingredient requests for valoctocogene,ataluren,tominersen returned404. These are lookup outcomes, not clinical failures.','Direct ClinicalTrials.gov retrieval repaired two missing pilot aliases.','Phase-only discovery misses studies whose current phase label differs from original entry stage.'],'rate_estimate':None}
(D/'pilot_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
hashes=[{'file':str(p.relative_to(P)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(S.iterdir()) if p.is_file()]
(D/'source_hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
assert audit['pilot_trial_results_total']==143
assert len(audit['phase_filter_false_negatives_recovered'])==3
assert all(any(x['asset']==a and x['allphase_query_recovered'] for x in reference) for a in ['zorevunersen','apazunersen','rugonersen','obudanersen'])
print('Pilot:8 programs,143 search records; 3 phase-filter misses repaired; all4 closest peers recovered; source hashes recorded.')
