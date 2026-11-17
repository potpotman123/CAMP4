"""Reproduce the public-source PoS cohort audit. No network; no fitted approval probability."""
from pathlib import Path
import json,csv,hashlib,html
from collections import Counter
from datetime import date
R=Path(__file__).resolve().parents[1]; S=R/'sources/pos_audit'; D=R/'data/pos_audit'; D.mkdir(exist_ok=True)
CUT=date(2026,11,16)
# Primary disclosures and regulatory references; discovery/search snapshots are retained separately.
sources={
'camp_q3':('2026-11-05','CAMP4 Q3 2026 update','https://investors.camp4tx.com/news-releases/news-release-details/camp4-reports-third-quarter-2026-financial-results-and-corporate','Regulatory clearance; first patient expected by year-end, not yet human efficacy.'),
'camp_uk':('2026-09-10','CAMP4 UK clearance','https://investors.camp4tx.com/news-releases/news-release-details/camp4-therapeutics-receives-authorization-united-kingdom-phase','UK permission predates Needham initiation.'),
'camp_10q':('2026-11-05','CAMP4 Q3 10-Q','https://www.sec.gov/Archives/edgar/data/1736730/000162828026071054/camp-20260930.htm','Drug-specific mouse rescue and human dosing plan; sponsor claims, not independent human validation.'),
'needham':('2026-10-15','Needham initiation','../../sources/user-provided/sellside/2026-10-15-CAMP.OQ-Needham  Company In-Summit Push Begins in SYNGAP1 - Initiating Coverage with a B...-124964472.pdf','pp.7-8 preclinical; p.28 DCF 25%; p.29 peak multiple 25%; no matched-cohort derivation identified.'),
'bio':('2021-02','BIO/Informa/QLS 2011-2020 study','https://go.bio.org/rs/490-EHZ-999/images/ClinicalDevelopmentSuccessRates2011_2020.pdf','Executive summary: Phase-I-to-approval 7.9% all; 17.0% rare disease; distinct stage-transition methodology, not our cohort.'),
'spinraza':('2016-12-23','Biogen FDA approval announcement','https://investors.biogen.com/news-releases/news-release-details/us-fda-approves-biogens-spinrazatm-nusinersen-first-treatment','First US approval; genetically defined motor-neuron disease.'),
'qalsody':('2023-04-25','FDA Qalsody approval','https://www.fda.gov/drugs/news-events-human-drugs/fda-approves-treatment-amyotrophic-lateral-sclerosis-associated-mutation-sod1-gene','Accelerated approval based on NfL; not proof of a transferable SYNGAP1 surrogate.'),
'zilganersen':('2026-09-03','FDA Zanvastro approval','https://www.fda.gov/news-events/press-announcements/fda-approves-first-drug-treat-alexander-disease','First approved Alexander disease therapy; pediatric and adult; toxic-protein lowering.'),
'gtx_failure':('2026-09-02','Ultragenyx Aspire result','https://ir.ultragenyx.com/news-releases/news-release-details/ultragenyx-announces-phase-3-aspire-results-angelman-syndrome','Primary cognition and key secondary MDRI endpoints missed; failure known before Needham initiation.'),
'gtx_winddown':('2026-11-04','Ultragenyx Q3 10-Q','https://ir.ultragenyx.com/static-files/83f1b349-cb50-417a-8195-c53c514af23d','GTX-102 discussion: winding down program after failed pivotal trial.'),
'stk_q3':('2026-10-29','Stoke Q3 2026 update','https://www.sec.gov/Archives/edgar/data/1623526/000119312526437775/stok-ex99_1.htm','EMPEROR ongoing; planned readout Q3 2027, not approved.'),
'stk_entry':('2026-08','Stoke Q2 10-Q','https://www.sec.gov/Archives/edgar/data/1623526/000119312526330557/stok-20260630.htm','First patient dosed August 2020, later than registered June 2020 study start.'),
'stk_trial':('2026-03','Zorevunersen clinical publication','https://www.nejm.org/doi/10.1056/NEJMoa2506295','Uncontrolled early clinical data; closer restoration/DEE evidence, not randomized proof.'),
'ionis_q3':('2026-11-09','Ionis Q3 2026 update','https://ir.ionis.com/news-releases/news-release-details/ionis-reports-third-quarter-2026-financial-results-and','Obudanersen REVEAL enrolled, approval unresolved.'),
'fusion':('2026-09-22','Ionis FUSION result','https://ir.ionis.com/news-releases/news-release-details/ionis-announces-positive-topline-results-phase-3-fusion-study','Positive pivotal clinical result, not approval.'),
'fus_early':('2022-01-24','FUS ASO original clinical/preclinical study','https://www.nature.com/articles/s41591-021-01615-z','Individualized human use preceded 2021 group trial; prevents treating Phase 3 entry as first exposure.'),
'rugo_trial':('2025-07-11','Rugonersen TANGELO original trial','https://www.nature.com/articles/s41591-025-03784-7','Open-label pediatric restoration ASO, distinct silencing mechanism from CAMP.'),
'rugo_phase3':('2026-11-06','BEACON registry','https://clinicaltrials.gov/study/NCT07605429','OHB Pediatrics sponsor; ongoing Phase III, not Roche exit equals failure.'),
'wave_old':('2021-03-29','Wave PRECISION-HD sponsor results','https://www.globenewswire.com/news-release/2021/03/29/2201081/0/en/wave-life-sciences-provides-update-on-phase-1b-2a-precision-hd-trials.html','Two separate compounds discontinued; shared platform/target dependence.'),
'wave004':('2023-05-23','Wave C9 program community letter','https://wavelifesciences.com/wp-content/uploads/2023/12/C9-Community-Letter-5-23-23.pdf','Biomarker reduction without clinical benefit; discontinuation.'),
'wave003':('2026-10-27','Wave Q3 10-Q','https://ir.wavelifesciences.com/static-files/0f63ab1b-ace4-4948-90e8-3843756cf762','WVE-003 remains clinical-stage; efficacy approval unresolved.'),
'biib078':('2022-03-28','Biogen/Ionis BIIB078 results','https://ir.ionis.com/news-releases/news-release-details/biogen-and-ionis-announce-topline-phase-1-study-results','No clinical benefit, program discontinued.'),
'biib105':('2024-05-16','Ionis BIIB105 results','https://ir.ionispharma.com/node/31256','ATXN2 reduced without NfL/clinical benefit; terminated.'),
'biib132':('2023-04-25','Biogen Q1 2023 results','https://www.sec.gov/Archives/edgar/data/875045/000087504523000012/exhibit991-q12023pressrele.htm','BIIB132 discontinued under prioritization; do not infer proven biological failure.'),
'biib_exit':('2025-02-12','Biogen Q4 2024 results','https://www.sec.gov/Archives/edgar/data/875045/000087504525000004/exhibit991-q42024pressrele.htm','BIIB094 and BIIB101 sponsor discontinuation; verify asset continuation separately.'),
'ionis_pipeline':('2026-11-09','Ionis current pipeline','https://ionis.com/science-and-innovation/pipeline','ION464 remains listed; registry HORIZON recruiting after Biogen exit.'),
'biib080':('2026-07-29','Biogen Q2 10-Q','https://investors.biogen.com/static-files/df3bc6ca-39dc-48b6-abd1-e1ebca444582','CELIA primary dose-response missed; sponsor plans continued registrational development.'),
'roche_letter':('2026-07-09','Roche HD sponsor community letter','https://ehdn.org/wp-content/uploads/2026/07/Roche-GENERATION-HD2-_-POINT-HD-global-patient-community-letter-July2026.pdf','HD2 and POINT-HD stopped; clinical translation versus chronic animal toxicity, respectively.'),
'nio':('2026-10-15','Novartis PRESERVE trial','https://www.novartis.com/clinicaltrials/study/nct07498426','Phase III PSP trial ongoing; separate from AD indication.'),
'lafora':('2025-02-20','ION283 first patients sponsor-community announcement','https://chelseashope.org/wp-content/uploads/2025/02/Safety-Study-Press-Release-February-2025.pdf','Investigator-led safety study; first dosing December 2024.'),
'adult_rescue':('2019-04-26','SYNGAP1 adult genetic rescue original study','https://elifesciences.org/articles/46752','Mouse genetic restoration improved selected phenotypes; not CMP-002 human drug evidence.'),
'legacy':('2021','ASO developer review of first SOD1 candidate','https://pmc.ncbi.nlm.nih.gov/articles/PMC8682074/','ISIS333611 superseded by more potent screening/delivery strategy; supporting historical account, not primary adjudication.'),
}
src={k:dict(id=k,date=v[0],title=v[1],url=v[2],supports=v[3],accessed='2026-11-16') for k,v in sources.items()}
# All registry records saved from discovery and named/alias retrievals. Registry start is enrollment proxy, not assumed dose date.
trials={}; loc={}
for f in sorted(S.glob('*.json')):
 x=json.loads(f.read_text())
 if not isinstance(x,dict) or 'data' not in x:continue
 d=x['data'];rows=d.get('studies',[]) if 'studies' in d else [d] if 'protocolSection' in d else []
 for z in rows:
  n=z['protocolSection']['identificationModule']['nctId'];trials[n]=z;loc[n]=str(f.relative_to(R))
rows=[]
def add(asset,indication,nct,target,action,genetic,tier,status,cites,note,event_date='',approval_type='',novel=True):
 p=trials[nct]['protocolSection'];s=p['statusModule'];start=s.get('startDateStruct',{}); regdate=start.get('date'); end=event_date or CUT.isoformat()
 last=s.get('lastUpdatePostDateStruct',{}).get('date')
 # Same registry record for multi-indication studies; common start is a trial proxy, not proof each subgroup dosed then.
 row=dict(id=asset+'|'+indication,asset=asset,indication=indication,entry_trial=nct,entry_date_proxy=regdate,entry_date_type=start.get('type','legacy_not_specified'),entry_definition='registered study start; may precede first dose or indication-specific enrollment',first_human_dose_date=None,prior_human_data_before_entry=False,registry_last_update=last,registry_current_status=s['overallStatus'],registry_why_stopped=s.get('whyStopped'),registry_source='https://clinicaltrials.gov/study/'+nct,local_registry_snapshot=loc[nct],route='intrathecal',modality='ASO',target=target,action=action,genetically_defined_population=genetic,cmp_relevance=tier,novel_target_at_entry=novel,status_asof=status,status_event_date=event_date or None,status_sources=cites.split(';') if cites else [],approval_type=approval_type or None,interpretation=note,independent_observation_cluster=asset,as_of=CUT.isoformat())
 if asset=='zorevunersen':row['first_human_dose_date']='2020-08';row['status_sources'].append('stk_entry')
 if asset=='ulefnersen':row['prior_human_data_before_entry']=True;row['interpretation']+=' Earlier individualized exposure predates this group-trial entry; exclude from strict no-prior-human-data entry sensitivity.'
 if regdate and len(regdate)==10:row['potential_followup_years']=round((CUT-date.fromisoformat(regdate)).days/365.25,2)
 else:row['potential_followup_years']=None
 rows.append(row)
add('nusinersen','SMA','NCT01494701','SMN2','productive splicing / protein increase',True,'restoration_support','approved','spinraza','Restores SMN from a paralog; motor-neuron biology and endpoints differ from synaptic neurodevelopment.','2016-12-23','traditional')
add('tofersen','SOD1-ALS','NCT02623699','SOD1','toxic protein lowering',True,'genetic_CNS_support','approved','qalsody','NfL accelerated pathway; not a validated surrogate for SYNGAP1.','2023-04-25','accelerated')
add('tominersen','Huntington disease','NCT02519036','HTT','nonallele-selective lowering',True,'genetic_CNS_support','stopped_efficacy','roche_letter','2021 pivotal failure was not permanent termination; 2026 HD2 failure and study stop is the current negative event. No assumption that future resurrection is impossible.','2026-07-09')
for a,n in [('WVE-120101','NCT03225833'),('WVE-120102','NCT03225846')]:add(a,'Huntington disease',n,'mutant HTT','allele-selective lowering',True,'genetic_CNS_support','stopped_efficacy','wave_old','Separate compounds but strongly dependent sponsor/target/chemistry; collapse pair in sensitivity.','2021-03-29')
add('WVE-003','Huntington disease','NCT05032196','mutant HTT','allele-selective lowering',True,'genetic_CNS_support','ongoing','wave003','Completed early study is not approval or discontinuation.')
for ind in ['C9-ALS','C9-FTD']:add('WVE-004',ind,'NCT04931862','C9orf72 repeat transcripts','toxic transcript lowering',True,'genetic_CNS_support','stopped_efficacy','wave004','Shared trial and compound; indications retained separately but not independent outcomes.','2023-05-23')
add('BIIB078','C9-ALS','NCT03626012','C9orf72 repeat transcripts','toxic transcript lowering',True,'genetic_CNS_support','stopped_efficacy','biib078','Completed first trial but program and extension discontinued.','2022-03-28')
add('BIIB105','ALS','NCT04494256','ATXN2','protein lowering',False,'broader_CNS','stopped_efficacy','biib105','Includes broad ALS; risk-gene relevance not equivalent to monogenic eligibility. Alias ION541.','2024-05-16')
add('BIIB132','SCA3','NCT05160558','ATXN3','protein lowering',True,'genetic_CNS_support','stopped_strategic','biib132','Eight enrolled; sponsor prioritization disclosed. Biological failure not established.','2023-04-25')
add('BIIB094','Parkinson disease','NCT03976349','LRRK2','protein lowering',False,'broader_CNS','sponsor_exit_unresolved','biib_exit','Includes patients with and without LRRK2 mutation. Biogen exit established; complete asset abandonment not independently established.','2025-02-12')
add('ION464','Multiple system atrophy','NCT04165486','SNCA','protein lowering',False,'broader_CNS','ongoing_after_partner_exit','biib_exit;ionis_pipeline','Alias BIIB101. Current Ionis listing and recruiting HORIZON contradict treating partner exit as asset failure.')
add('diranersen','Alzheimer disease','NCT03186989','MAPT','tau lowering',False,'broader_CNS','ongoing_after_negative_endpoint','biib080','Alias BIIB080. Primary Phase II dose-response miss, sponsor pursuing development; not counted as terminated.')
add('zorevunersen','Dravet syndrome','NCT04442295','SCN1A','productive splicing / protein increase',True,'closest_pediatric_restoration','ongoing','stk_q3;stk_trial','Closest DEE/haploinsufficiency peer; early clinical signals do not equal approval.')
add('apazunersen','Angelman syndrome','NCT04259281','UBE3A-ATS','unsilence paternal UBE3A',True,'closest_pediatric_restoration','stopped_efficacy','gtx_failure;gtx_winddown','Alias GTX-102. Sept pivotal miss known at Needham date; November wind-down is later confirmation. Earlier dose-related hold was subsequently lifted.','2026-11-04')
add('rugonersen','Angelman syndrome','NCT04428281','UBE3A-ATS','unsilence paternal UBE3A',True,'closest_pediatric_restoration','ongoing','rugo_trial;rugo_phase3','Alias RO7248824. Phase III with OHB; program continuation despite original sponsor change.')
add('obudanersen','Angelman syndrome','NCT05127226','UBE3A-ATS','unsilence paternal UBE3A',True,'closest_pediatric_restoration','ongoing','ionis_q3','Aliases ION582/BIIB121. Biogen option declined, Ionis Phase III continues; do not count partner decision as failure.')
add('zilganersen','Alexander disease','NCT04849741','GFAP','toxic protein lowering',True,'genetic_CNS_support','approved','zilganersen','Recent pediatric/adult CNS success; lowers toxic GFAP rather than restoring deficient synaptic protein.','2026-09-03','traditional')
add('ulefnersen','FUS-ALS','NCT04768972','FUS','protein lowering',True,'genetic_CNS_support','ongoing_positive_pivotal','fusion;fus_early','Aliases ION363/jacifusen; positive Phase III is not approval.')
add('ION717','Symptomatic prion disease','NCT06153966','PRNP','prion protein lowering',False,'broader_CNS','ongoing','','Genetic and sporadic forms; no uniform monogenic selection. Trial active, approval unresolved.')
for ind in ['Huntington disease','SCA1','SCA3']:add('VO659',ind,'NCT05822908','expanded CAG transcripts','repeat-targeting antisense',True,'genetic_CNS_support','ongoing','','One multi-disease trial; common entry is proxy, not three independent platform outcomes.')
add('ION283','Lafora disease','NCT06609889','GYS1','glycogen synthase lowering',True,'pediatric_genetic_adjacent','ongoing','lafora','Gene-deficiency disease treated by substrate reduction, not protein restoration; investigator-led development may differ commercially.')
add('NIO752','Progressive supranuclear palsy','NCT04539041','MAPT','tau lowering',False,'broader_CNS','ongoing','nio','Phase III progressing; no monogenic selection.')
add('NIO752','Alzheimer disease','NCT05469360','MAPT','tau lowering',False,'broader_CNS','ongoing','','Separate indication; earlier PSP exposure means not a first-human-data landmark.',novel=False)
rows[-1]['prior_human_data_before_entry']=True
add('salanersen','SMA','NCT05575011','SMN2','productive splicing / protein increase',True,'validated_target_followon','ongoing','','Aliases BIIB115/ION306; target/mechanism already validated by nusinersen. Exclude from novel-target matching.',novel=False)
# Trials updated after cutoff cannot silently enter an as-of cohort.
for row in rows:
 assert row['registry_last_update']<=CUT.isoformat(),row['id']
 assert all(k in src for k in row['status_sources'])
 assert row['entry_date_proxy'][:4]>='2010' and row['entry_date_proxy'][:4]<='2024'
assert len({x['id'] for x in rows})==len(rows)
# Detailed raw screen dispositions: every generic-search result remains visible.
screen=[]
used={x['entry_trial'] for x in rows}
for z in json.loads((S/'registry_discovery.json').read_text())['data']['studies']:
 p=z['protocolSection'];n=p['identificationModule']['nctId'];t=p['identificationModule']['briefTitle'];st=p['statusModule'].get('startDateStruct',{}).get('date')
 if n in used:disp='included_core_entry'
 elif any(v in t.lower() for v in ['ultrasound','landmark','nusinersen']):disp='exclude_administration_or_postapproval_study'
 elif any(v in t for v in ['VCA-894A','GNAO1','Ataxia-Telangiectasia']):disp='individualized_nonregistration_boundary'
 elif p.get('designModule',{}).get('studyType')=='EXPANDED_ACCESS':disp='expanded_access_not_independent_program'
 elif st and st[:4]>='2025':disp='recent_entry_or_later_trial_watchlist'
 else:disp='followup_duplicate_or_boundary_review'
 screen.append(dict(nct=n,title=t,start=st,disposition=disp,source='https://clinicaltrials.gov/study/'+n))
boundaries=[
 dict(asset='ISIS333611',disposition='legacy_superseded_uncertain',source='https://clinicaltrials.gov/study/NCT01041222',reason='Retain excluded sensitivity: older SOD1 compound superseded; start month legacy/unspecified and primary termination documentation incomplete. Not silently erased as an approval.'),
 dict(asset='RG6496',disposition='2025_2026_entry_watchlist_negative',source=src['roche_letter']['url'],reason='POINT-HD stopped after chronic animal toxicity. Outside core entry window; reinforces risk remaining after first-dose clearance. Entry date not yet independently reconciled.'),
 dict(asset='RC001; LTX-002; AMX0114; TRCN-1023; TS1-ASO',disposition='2025_2026_entry_watchlist',source='sources/pos_audit/registry_discovery.json',reason='Recent discovery leads retained with registry records, not yet full program adjudication; do not infer resolved success.'),
 dict(asset='milasen; afinersen; atipeksen; VCA-894A; tianasen',disposition='individualized_boundary',source='sources/pos_audit/registry_discovery.json',reason='Single-patient or mutation-specific use does not have comparable commercial-approval intent; separate safety/feasibility evidence, not zero-approval failures. Some aliases are literature leads not fully verified.'),
 dict(asset='STK-002',disposition='ocular_route_boundary',source=src['stk_q3']['url'],reason='Protein upregulation relevant, ocular delivery differs; excluded from direct intrathecal reference denominator.'),
 dict(asset='DMD ASOs; systemic TTR ASOs; IL-17 me-too drugs',disposition='excluded_modality_route_or_biology',source='protocol/pos_audit_design_2026-11-16.txt',reason='Not direct CNS delivery and mechanism matching. Can inform broad priors only.'),
 dict(asset='CNS viral gene therapies / enzyme replacement',disposition='adjacent_not_pooled',source='../../02_first_entry_dmt_forecast_study/data/independent/analogue_matrix.csv',reason='Distinct dose persistence, delivery, immunology and manufacturing. Separate causal comparisons possible; no pooled PoS denominator.'),
]
def tally(rs):return dict(Counter(x['status_asof'] for x in rs))
assets=list({x['asset']:x for x in rows}.values())
closest=[x for x in rows if x['cmp_relevance']=='closest_pediatric_restoration']
summary=dict(as_of=CUT.isoformat(),core_asset_n=len(assets),core_drug_indication_n=len(rows),asset_status_counts=tally(assets),pair_status_counts=tally(rows),closest_pediatric_restoration=tally(closest),closest_n=len(closest),genetic_pair_n=sum(x['genetically_defined_population'] for x in rows),asset_vintages={v:tally([x for x in assets if lo<=x['entry_date_proxy'][:4]<=hi]) for v,lo,hi in [('2010_2016','2010','2016'),('2017_2020','2017','2020'),('2021_2024','2021','2024')]},pooled_approval_probability=None,reason_no_rate='Purpose-built, incomplete public-source cohort; right-censoring, stage mismatch, correlated programs and unresolved exits. Raw outcome proportions are not lifetime PoS.',recommended_working_model=dict(central=0.20,downside=0.10,needham=0.25,upside=0.35,classification='Judgmental valuation scenarios, NOT empirical estimates or confidence interval; central is provisional and not statistically preferred to 25%.'))
# Completed five-year follow-up subset; observed approval by five years is a different estimand, not lifetime success.
# Month-only legacy and prior-human-entry exceptions excluded from this diagnostic.
for horizon in [5,10]:
 mature=[x for x in assets if x['potential_followup_years']>=horizon and not x['prior_human_data_before_entry']]
 success=[x for x in mature if x['status_asof']=='approved' and (date.fromisoformat(x['status_event_date'])-date.fromisoformat(x['entry_date_proxy'])).days/365.25<=horizon]
 summary[f'{horizon}y_complete_calendar_followup_diagnostic']={'n':len(mature),'approval_within_horizon_n':len(success),'assets':[x['asset'] for x in mature],'successful_assets':[x['asset'] for x in success],'interpretation':'Descriptive selected-cohort calendar horizon only; no survival estimate or independence assumption; unresolved asset status remains a limitation.'}
for name,obj in [('program_ledger',rows),('source_registry',src),('discovery_screen',screen),('boundaries_and_exclusions',boundaries),('summary',summary)]:
 (D/(name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
with (D/'program_ledger.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in x.items()} for x in rows)
manifest=[dict(file=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(S.glob('*')) if p.is_file()]
(D/'source_hashes.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(summary,indent=2))
