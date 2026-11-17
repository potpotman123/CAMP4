import json,re
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/'data/pos_adjudication'
load=lambda p:json.loads((P/p).read_text());screen=load('data/pos_adjudication/full_screen.json');b={x['candidate_id']:x for x in load('data/pos_nested/candidate_review_queue.json')};trials={x['nct_id']:x for x in load('data/pos_nested/trial_inventory.json')};prior=load('data/pos_audit/program_ledger.json')
# Named trial-level identity adjudication. Genotype and modality are not inferred from outcome.
spec='''NCT01041222|ISIS333611|ASO|SOD1
NCT01051882|NurOwn|cell|mixed
NCT01082653|autologous_BM_stem_cells_Corestem_2010|cell|mixed
NCT01091142|NP001_sodium_chlorite|small_molecule|mixed
NCT01363401|HYNR-CS|cell|mixed
NCT01424163|dexpramipexole|small_molecule|mixed
NCT01424176|dexpramipexole|small_molecule|mixed
NCT01536249|dexpramipexole|small_molecule|mixed
NCT02039401|VM202|plasmid_gene_therapy|mixed
NCT02269436|sNN0029|protein|mixed
NCT02286011|MNC_Hanyang|cell|mixed
NCT02588807|Spirit1|unknown|mixed
NCT02655614|GDC-0134|small_molecule|mixed
NCT02714036|ibudilast|small_molecule|mixed
NCT02870634|CuATSM|small_molecule|mixed
NCT03136809|CuATSM|small_molecule|mixed
NCT03237741|GDC-0134|small_molecule|mixed
NCT03334786|FLX-787|small_molecule|mixed
NCT03338114|FLX-787|small_molecule|mixed
NCT03482050|AstroRx|cell|mixed
NCT03487263|IC14|antibody|mixed
NCT03520517|BHV-0223_riluzole|small_molecule|mixed
NCT03626012|BIIB078|ASO|C9orf72
NCT03651349|HK-001|unknown|mixed
NCT03652805|IPL344|peptide|mixed
NCT03757351|DNL747|small_molecule|mixed
NCT03828123|MSC3P|cell|mixed
NCT03945279|BIIB100|small_molecule|mixed
NCT03981536|AP-101|antibody|mixed
NCT04090684|PrimeC|small_molecule_combination|mixed
NCT04326283|trametinib|small_molecule|mixed
NCT04494256|BIIB105|ASO|mixed
NCT04651855|Whartons_jelly_MSCs|cell|mixed
NCT04894240|monepantel|small_molecule|mixed
NCT04931862|WVE-004|ASO|C9orf72
NCT04987671|AMX0035|small_molecule_combination|mixed
NCT05279755|prosetin|small_molecule|mixed
NCT05395624|18F-OP-801|diagnostic|mixed
NCT05542576|AMDX2011P|unknown|mixed
NCT05633459|QRL-201|ASO|mixed
NCT05683860|WVE-004|ASO|C9orf72
NCT05695521|CK0803|cell|mixed
NCT05795907|SAR443820|small_molecule|mixed
NCT05797701|SAR443820|small_molecule|mixed
NCT05797753|SAR443820|small_molecule|mixed
NCT05882695|SPG302|small_molecule|mixed
NCT05889572|MaaT033|microbiome|mixed
NCT05949294|ARO-SOD1|siRNA|SOD1
NCT05995782|FB418|unknown|mixed
NCT06100276|AMT-162|gene_therapy|SOD1
NCT06215755|VRG50635|small_molecule|mixed
NCT06351592|ALN-SOD|siRNA|SOD1
NCT06453668|TCD601|antibody|mixed
NCT06454682|RJK002|gene_therapy|unknown
NCT06493279|RJK002|gene_therapy|unknown
NCT06671236|NP001_regulatory_Tcells|cell|mixed
NCT06714396|QRL-101|small_molecule|mixed
NCT06769620|ORT247|unknown|mixed
NCT06782958|FHND1002|unknown|mixed'''
mp={z.split('|')[0]:z.split('|')[1:] for z in spec.splitlines()}
exclusions={'dexpramipexole':'Later PK/renal/drug-interaction studies, not clean first entry; earlier ALS development known; exclude from de-novo entry set pending reconstruction.','BHV-0223_riluzole':'Riluzole formulation follow-on; not novel molecule/target entry.','ibudilast':'Repurposed previously human-tested drug; not de-novo molecule entry.','trametinib':'Repurposed oncology drug, not de-novo molecule entry.','AMX0035':'2021 study is later human work; earlier CENTAUR entry needs separate reconstruction. FDA approval2022 and later withdrawal do not make this2021 first entry.','18F-OP-801':'Diagnostic radiotracer; outside therapeutic program denominator.'}
rows={};dispositions=[]
for x in screen:
 if x['disposition']!='priority_early_industry' or 'ALS' not in x['structured_disease_matches']:continue
 z=b[x['candidate_id']]
 if x['name'] in ['Rabeprazole','Midazolam','Caffeine']:
  dispositions.append({'candidate_id':x['candidate_id'],'decision':'exclude_background_or_PK_probe','evidence':'NCT02655614 arms and brief summary identify GDC-0134 as investigational drug; these are coadministered in active and placebo arms.'});continue
 match=next((mp[n] for n in z['nct_ids'] if n in mp),None)
 if not match:dispositions.append({'candidate_id':x['candidate_id'],'decision':'unresolved_identity'});continue
 asset,modality,genotype=match;key=asset+'|ALS'
 if key not in rows:
  rows[key]={'program_id':key,'asset':asset,'indication':'ALS' if genotype in ['mixed','unknown'] else genotype+'-ALS','candidate_ids':[],'aliases':[],'nct_ids':[],'entry_date_proxy':None,'entry_is_first_human_verified':False,'entry_definition':'earliest observed assigned trial; not automatically first human dosing','cohort_disposition':'exclude_de_novo_entry' if asset in exclusions else 'candidate_registry_entry','eligibility_note':exclusions.get(asset,'Identity mapped; full earliest-human/registration-intent verification remains incomplete.'),'status':'unknown','event_date':None,'event_date_precision':None,'status_sources':[],'modality':modality,'rare_nononcology':True,'genetic_cns':genotype not in ['mixed','unknown'],'genotype':genotype,'genetic_medicine':modality in ['ASO','siRNA','gene_therapy','plasmid_gene_therapy'],'novel_target_at_entry':None,'intrathecal':None,'protein_restoration':True if asset=='QRL-201' else None,'neurodevelopmental':False,'last_verified_active_date':None,'status_is_inferred_from_trial_status':False}
 r=rows[key];r['candidate_ids'].append(x['candidate_id']);r['aliases'].append(x['name']);r['nct_ids']+=z['nct_ids']
 d=z['earliest_observed_panel_trial_date'];r['entry_date_proxy']=min(r['entry_date_proxy'] or d,d)
 dispositions.append({'candidate_id':x['candidate_id'],'decision':rows[key]['cohort_disposition'],'program_id':key})
for r in rows.values():
 r['aliases']=sorted(set(r['aliases']));r['nct_ids']=sorted(set(r['nct_ids']));r['identity_sources']=['https://clinicaltrials.gov/study/'+n for n in r['nct_ids']]
 for old in prior:
  if old['asset']==r['asset'] and 'ALS' in old['indication']:
   r.update(status=old['status_asof'],event_date=old['status_event_date'],status_sources=[{'inherited_source_id':s,'registry':'../pos_audit/source_registry.json'} for s in old['status_sources']],novel_target_at_entry=old['novel_target_at_entry'],intrathecal=True)
# Add known mixed-phase entries missed by phase1-only initial screen; not silently count as a phase1 screen hit.
for asset in ['tofersen','ulefnersen']:
 old=next(x for x in prior if x['asset']==asset)
 rows[asset+'|ALS']={'program_id':asset+'|ALS','asset':asset,'indication':old['indication'],'candidate_ids':[],'aliases':[asset],'nct_ids':[old['entry_trial']],'entry_date_proxy':old['entry_date_proxy'],'entry_is_first_human_verified':False,'entry_definition':old['entry_definition'],'cohort_disposition':'candidate_registry_entry' if asset=='tofersen' else 'exclude_de_novo_entry','eligibility_note':'Mixed-phase entry coverage correction; individualized earlier exposure for ulefnersen.','status':old['status_asof'],'event_date':old['status_event_date'],'status_sources':[{'inherited_source_id':s,'registry':'../pos_audit/source_registry.json'} for s in old['status_sources']],'modality':'ASO','rare_nononcology':True,'genetic_cns':True,'genetic_medicine':True,'novel_target_at_entry':old['novel_target_at_entry'],'intrathecal':True,'protein_restoration':False,'neurodevelopmental':False,'last_verified_active_date':None,'status_is_inferred_from_trial_status':False}
updates={
'BIIB100':('stopped_strategic','2022-06','https://investors.biogen.com/static-files/da2a28e6-8165-4a82-9e88-12a1363851cd','Biogen2022 Form10K confirms development discontinued June2022 as part of strategic review; not an efficacy failure.'),
'VRG50635':('stopped_efficacy','2025-12','https://www.vergelabs.blog/p/what-we-learned-from-the-trial-of','Sponsor CEO May27,2026 explicitly says not advancing in ALS after late2025 trial; month proxy from registry, not precise decision date.'),
'GDC-0134':('stopped_safety',None,'https://pmc.ncbi.nlm.nih.gov/articles/PMC8791798/','Original Phase1 trial publication states unacceptable safety profile and discontinuation of development; exact discontinuation date not established.'),
'DNL747':('stopped_safety','2020-07-29','https://www.sanofi.com/assets/dotcom/content-app/events/quaterly-results/2020/Q2-2020-EN/2020_07_29_Q2_2020_PR_EN_v3.pdf','Sponsor confirms SAR443060/DNL747 development discontinued; this is disclosure date, not exact internal decision date.'),
'SAR443820':('stopped',None,'https://www.sanofi.com/assets/dotcom/content-app/publications/annual-report-on-form-20-f/2024-01-01-form-20-f-2024-en.pdf','2024 development table lists ALS/MS development discontinued; exact day not established.'),
'AMX0035':('approved_then_withdrawn','2022-09-29','https://www.fda.gov/drugs/drug-trials-snapshots/drug-trials-snapshots-relyvrio','Count first FDA approval as approval event if eligible; later withdrawal is separate commercial/durability outcome. Entry remains excluded pending earlier-history reconstruction.')}
for asset,(status,date,url,note) in updates.items():
 r=rows[asset+'|ALS'];r.update(status=status,event_date=date,event_date_precision='disclosure_date' if asset=='DNL747' else ('month' if len(date)==7 else 'day') if date else None);r['status_sources']=[{'url':url,'note':note,'accessed':'2026-11-16'}]
active={
'AP-101':('2026-06-24','https://al-spharma.com/news/'),
'PrimeC':('2026-11-16','https://www.neurosense-tx.com/'),
'NurOwn':('2026-08-14','https://ir.brainstorm-cell.com/2026-08-14-BrainStorm-Cell-Therapeutics-Announces-Second-Quarter-2026-Financial-Results-and-Provides-Corporate-Update'),
'QRL-201':('2026-11-15','https://www.quralis.com/news/quralis-receives-fda-clearance-for-ind-application-of-qrl-201-for-the-treatment-of-als-clearing-a-path-to-initiation-of-pivotal-clinical-trial-in-the-u-s/')}
for asset,(date,url) in active.items():
 r=rows[asset+'|ALS'];r['status']='ongoing';r['last_verified_active_date']=date;r['status_sources']=[{'url':url,'evidence_date':date,'note':'Sponsor confirms continued clinical development; no approval inferred.'}]

for asset in ['ARO-SOD1','AMT-162','ALN-SOD']:
 if asset+'|ALS' in rows:rows[asset+'|ALS']['novel_target_at_entry']=False;rows[asset+'|ALS']['target_validation_note']='SOD1 target had prior human tofersen evidence/approval before these later entries; modality differences remain.'
# Supplement all unresolved named assets with retrieved records, preserving proxy confidence.
manifest_path=P/'data/pos_adjudication/als_followup_manifest.json'
if manifest_path.exists():
 for m in json.loads(manifest_path.read_text()):
  r=rows.get(m['asset']+'|ALS')
  if not r:continue
  studies=json.loads((P/m['file']).read_text()).get('studies',[])
  # NP001 is a known collision; never import the unrelated regulatory-T-cell study.
  if m['asset']=='NP001_sodium_chlorite':studies=[x for x in studies if x['protocolSection']['identificationModule']['nctId']!='NCT06671236']
  notes=[]
  for x in studies:
   p=x['protocolSection'];st=p['statusModule'];n=p['identificationModule']['nctId']
   notes.append({'trial':n,'status':st.get('overallStatus'),'update':st.get('lastUpdatePostDateStruct',{}).get('date'),'start':st.get('startDateStruct',{}),'why_stopped':st.get('whyStopped')})
  r['followup_registry_search']={'file':m['file'],'total_returned':m['count'],'records_after_identity_guard':notes,'interpretation':'Registry study status is a source observation, NOT independently confirmed program fate or continuous active follow-up.'}
  r['outcome_search_performed']=True
  early=[n['start'].get('date') for n in notes if n['start'].get('date')]
  if early and min(early)<r['entry_date_proxy']:
   r['earlier_record_discovered']=min(early)
   if min(early)<'2010':r['cohort_disposition']='exclude_pre2010_exposure';r['eligibility_note']+=' Follow-up query found pre2010 study.'
  if r['status']=='unknown':
   recent=[n for n in notes if n['status'] in ['RECRUITING','ACTIVE_NOT_RECRUITING','ENROLLING_BY_INVITATION'] and (n['update'] or '')>='2025-01-01']
   if recent:r['registry_reported_ongoing']=recent # Do not promote to confirmed ongoing.
rows['ARO-SOD1|ALS']['cohort_disposition']='exclude_never_dosed'
rows['ARO-SOD1|ALS']['eligibility_note']='NCT05949294 WITHDRAWN, enrollment0 ACTUAL, start2024-01 ESTIMATED; pre-doseattrition boundary, not a clinical entrant.'
rows['FLX-787|ALS']['status']='stopped_formulation'
rows['FLX-787|ALS']['status_sources']=[{'url':'https://clinicaltrials.gov/study/NCT03334786','note':'WhyStopped explicitly: Development of Current Formulation has Ceased. Scope is formulation, not proof all possible reformulations ended.','evidence_date':'2018-08-29'}]
rows['FLX-787|ALS']['status_sources'].append({'url':'https://www.sec.gov/Archives/edgar/data/1615219/000161521919000008/flks2018123110-k.htm','note':'Sponsor2018 Form10K says ongoing trials ended June2018 for oral tolerability; supports discontinuation of tested formulation, no assertion no future reformulation.'})
rows['PrimeC|ALS']['cohort_disposition']='exclude_de_novo_entry'
rows['PrimeC|ALS']['eligibility_note']='Fixed combination of already approved ciprofloxacin and celecoxib; separate repurposing sensitivity, excluded strict novel-molecule entry.'
rows['IPL344|ALS']['status']='suspended_supply'
rows['IPL344|ALS']['status_sources']=[{'url':'https://clinicaltrials.gov/study/NCT03652805','note':'Suspended due drugshortage; may resume. NOT permanent failure.','evidence_date':'2025-01-10'}]

for r in rows.values():
 if r.get('novel_target_at_entry') is True:
  r['legacy_novel_target_at_entry']=True
  r['novel_target_at_entry']=None
  r['target_novelty_correction']='Inherited flag did not verify absence of earlier human target exposure; retain unknown for literal novel-target filter.'

(D/'als_program_ledger.json').write_text(json.dumps(list(rows.values()),indent=2)+'\n');(D/'als_candidate_dispositions.json').write_text(json.dumps(dispositions,indent=2)+'\n')
assert len(dispositions)==len({x['candidate_id'] for x in dispositions})
print('ALS priority buckets:',len(dispositions),'programs incl coverage corrections:',len(rows),'unknown:',sum(x['status']=='unknown' for x in rows.values()))
