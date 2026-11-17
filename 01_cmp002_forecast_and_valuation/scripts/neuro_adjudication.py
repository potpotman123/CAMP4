"""Neuro panel identity/disposition audit; no population probability inferred."""
import json,re,hashlib
from pathlib import Path
from collections import Counter,defaultdict
P=Path(__file__).resolve().parents[1];D=P/'data/pos_adjudication';D.mkdir(exist_ok=True)
def load(f):return json.loads((P/f).read_text())
cs={x['candidate_id']:x for x in load('data/pos_nested/candidate_review_queue.json')};trials={x['nct_id']:x for x in load('data/pos_nested/trial_inventory.json')}
prior=load('data/pos_audit/program_ledger.json');sources=load('data/pos_audit/source_registry.json')
tags={'Angelman','Dravet','Rett','Fragile_X','SYNGAP1','CDKL5','Lennox_Gastaut','Huntington','SCA','Alexander','NCL','Lafora','ALD','MLD','SMA'}
rows=[x for x in load('data/pos_adjudication/full_screen.json') if tags.intersection(x['structured_disease_matches']) and cs[x['candidate_id']]['entry_window_candidate']]
# Canonical aliases are specific identity decisions; ambiguous generic interventions are not merged.
# tuple canonical, regex, modality, molecular mechanism action (unverified where null)
M=[
('deutetrabenazine',r'^SD-809$','small_molecule','VMAT2'),('BN82451B',r'bn82451b','small_molecule',None),('DUOC-01',r'duoc.?01','cell_therapy',None),
('nusinersen',r'nusinersen','ASO','SMN2_splicing'),('tominersen',r'443139|tominersen|ro7234292|rg6042','ASO','HTT_lowering'),
('zorevunersen',r'stk.?001|zorevunersen','ASO','SCN1A_restoration'),('apazunersen',r'gtx.?102|apazunersen','ASO','UBE3A_unsilencing'),('rugonersen',r'ro7248824|rugonersen','ASO','UBE3A_unsilencing'),('obudanersen',r'ion582|obudanersen','ASO','UBE3A_unsilencing'),
('WVE-120101',r'wve.?120101','ASO','HTT_lowering'),('WVE-120102',r'wve.?120102','ASO','HTT_lowering'),('WVE-003',r'wve.?003','ASO','HTT_lowering'),('BIIB132',r'biib132','ASO','ATXN3_lowering'),('salanersen',r'biib115|salanersen','ASO','SMN2_splicing'),('zilganersen',r'zilganersen|ion373','ASO','GFAP_lowering'),('ION283',r'ion283','ASO','GYS1_lowering'),('VO659',r'vo659','ASO','CAG_repeat_RNA'),
('atidarsagene_autotemcel',r'otl.?200','ex_vivo_gene_therapy','ARSA_restoration'),('elivaldogene_autotemcel',r'lenti.?d|eli.?cel','ex_vivo_gene_therapy','ABCD1_restoration'),('onasemnogene_abeparvovec',r'avxs.?101|onasemnogene|oav101','in_vivo_gene_therapy','SMN1_replacement'),
('AAVrh10_CLN2',r'aavrh.?10c[uU](?:h)?cln2','in_vivo_gene_therapy','TPP1_replacement'),('AAVrh10_ARSA',r'aavrh.?10cuarsa','in_vivo_gene_therapy','ARSA_replacement'),('AT-GTX-501',r'at.?gtx.?501','in_vivo_gene_therapy','CLN6_replacement'),('CLN-301',r'cln.?301','in_vivo_gene_therapy','CLN3_replacement'),('AAV9_CLN7',r'aav9/cln7','in_vivo_gene_therapy','CLN7_replacement'),('NGN-101',r'ngn.?101','in_vivo_gene_therapy','CLN5_replacement'),
('AMT-130',r'raav5.mihtt','in_vivo_gene_therapy','HTT_lowering'),('AB-1001',r'ab.?1001','in_vivo_gene_therapy','CYP46A1_increase'),('VY-HTT01',r'raav1.*rna htt','in_vivo_gene_therapy','HTT_lowering'),('TSHA-102',r'tsha.?102','in_vivo_gene_therapy','MECP2_replacement'),('NGN-401',r'ngn.?401','in_vivo_gene_therapy','MECP2_replacement'),('ETX101',r'etx101','in_vivo_gene_therapy','SCN1A_transcription_increase'),
('EXG001-307',r'exg001.?307','gene_therapy_candidate',None),('ANB-004',r'anb.?004','gene_therapy_candidate',None),('GC101',r'gc101','gene_therapy_candidate',None),('SKG0201',r'skg0201','gene_therapy_candidate',None),('vesemnogene_lantuparvovec',r'vesemnogene','gene_therapy_candidate',None),('NKG001',r'nkg001','gene_therapy_candidate',None),('TTX-381',r'ttx.?381','gene_therapy_candidate',None),('ER2001',r'er2001','gene_therapy_candidate',None),('ALN-HTT02',r'aln.?htt02','siRNA','HTT_lowering'),('ARO-ATXN2',r'aro.?atxn2','siRNA','ATXN2_lowering'),
('cerliponase_alfa',r'bmn.?190|cerliponase','enzyme_replacement','TPP1_replacement'),('SHP611_IT',r'hgt.?1110|shp611|recombinant human arylsulfatase','enzyme_replacement','ARSA_replacement'),
('risdiplam',r'risdiplam','small_molecule','SMN2_splicing'),('branaplam',r'branaplam|lmi070','small_molecule','splicing_modifier'),('RG7800',r'ro6885247|rg7800','small_molecule','SMN2_splicing'),('apitegromab',r'srk.?015|apitegromab','antibody','myostatin'),('RO7204239',r'ro7204239','antibody','myostatin'),('taldefgrobep_alfa',r'taldefgrobep','protein','myostatin'),
('trofinetide',r'nnz.?2566|trofinetide','small_molecule',None),('soticlestat',r'soticlestat|tak.?935','small_molecule','CH24H'),('ganaxolone',r'ganaxolone','small_molecule','GABA_A'),('gaboxadol',r'ov101|gaboxadol','small_molecule','GABA_A'),
('olesoxime',r'olesoxime','small_molecule',None),('mavoglurant',r'afq056|mavoglurant','small_molecule','mGluR5'),('basimglurant',r'ro4917523|basimglurant','small_molecule','mGluR5'),('arbaclofen',r'arbaclofen','small_molecule','GABA_B'),('selisistat',r'sen0014196|selisistat','small_molecule','SIRT1'),('GSK356278',r'gsk356278','small_molecule','PDE4'),('PBT2',r'pbt2','small_molecule',None),('PF-02545920',r'pf.?02545920','small_molecule','PDE10A'),('pridopidine',r'pridopidine','small_molecule','sigma1'),('sobetirome',r'sobetirome|nv1205','small_molecule','THRbeta'),('OMS643762',r'oms643762','small_molecule',None),('cysteamine_RP103',r'rp103','small_molecule',None),('MG01CI',r'mg01ci','small_molecule',None),
('pepinemab',r'vx15/2503|pepinemab','antibody','SEMA4D'),('SRX246',r'srx246','small_molecule','V1a'),('reldesemtiv',r'reldesemtiv','small_molecule','troponin'),('Cellavita_HD',r'cellavita|nestacell','cell_therapy',None),('sarizotan',r'sarizotan','small_molecule',None),('PBF-999',r'pbf.?999','small_molecule',None),('troriluzole',r'troriluzole|bhv.?4157','small_molecule',None),('AZD7325',r'azd7325','small_molecule','GABA_A'),('tideglusib',r'tideglusib','small_molecule',None),('tadalafil_investigational',r'^tadalafil','small_molecule',None),
('tideglusib_AMO2',r'amo.?02','small_molecule',None),('BPN14770',r'bpn14770','small_molecule','PDE4D'),('SOM3355',r'som3355','small_molecule',None),('ZYN002',r'zyn002','small_molecule','cannabinoid'),('CKD-504',r'ckd.?504','small_molecule','HDAC6'),('carisbamate',r'carisbamate','small_molecule',None),('blarcamesine',r'anavex2.?73','small_molecule','sigma1'),('SAGE-718',r'sage.?718','small_molecule','NMDA'),('neflamapimod',r'neflamapimod','small_molecule','p38alpha'),('clemizole',r'epx.?100|clemizole','small_molecule',None),('CAD-1883',r'cad.?1883','small_molecule','SK_channel'),('ANX005',r'anx005','antibody','C1q'),('leriglitazone',r'min.?102|leriglitazone','small_molecule','PPARgamma'),('VK0214',r'vk0214','small_molecule','THRbeta'),('NNZ-2591',r'nnz.?2591','small_molecule',None),('PXL770',r'pxl770','small_molecule','AMPK'),('PXL065',r'pxl065','small_molecule',None),('LPM3770164',r'lpm3770164','small_molecule',None),('votoplam',r'ptc518|votoplam','small_molecule','HTT_splicing'),('bexicaserin',r'lp352|bexicaserin','small_molecule','5HT2C'),('VYNT-0126',r'vynt.?0126','small_molecule',None),('alogabat',r'alogabat','small_molecule','GABA_A'),('NMD670',r'nmd670','small_molecule',None),('BMB-101',r'bmb.?101','small_molecule','5HT2C'),('MBF-015',r'mbf.?015','small_molecule',None),('CTH120',r'cth120','small_molecule',None),('NTI164',r'nti164','cannabinoid_extract',None),('GCB-002',r'gcb.?002','unknown',None),('bionetide',r'bionetide','unknown',None),('KPS-0373',r'kps.?0373','small_molecule',None),('latrepirdine',r'dimebon|latrepirdine','small_molecule',None),('Cabaletta_trehalose',r'cabaletta|sls.?005','small_molecule',None),
]
# All remaining entries are explicitly retained as separate review dispositions.
background=re.compile(r'blood sample|biocollection|vaccine|preparative|conditioning|imaging|pet|\[18f\]|18f-|flumazenil|palliative|education|midazolam|omeprazole|itraconazole|albumin solution',re.I)
repurposed=re.compile(r'clobazam|laquinimod|miglustat|^NAC$|coq10|minocycline|lithium|phenylbutyrate|rufinamide|bezafibrate|levodopa|ivig|immune globulin|epigallocatechin|sertraline|acetylcysteine|lipoic|vitamin|tetrahydrocannabinol|cannabidiol|gwp42003|glatiramer|fingolimod|dalfampridine|tetrabenazine|triheptanoin|lovastatin|perampanel|celecoxib|pyridostigmine|md1003|acamprosate|baclofen|tridecanoic|riluzole|thiotepa|ketamine|metformin|nilotinib|amifampridine|dextromethorphan|pioglitazone|cannabis|haloperidol|risperidone|zoloft|idebenone|valbenazine|taltirelin|thiamine|biotin|5.hydroxytryptophan|ergoloid|memantine|roflumilast|psilocybin|esketamine|dimethyl fumarate|fenfluramine|zx008|rhigf|rolipram',re.I)
prog={};dispositions=[]
for x in rows:
 n=x['name'];match=next((m for m in M if re.search(m[1],n,re.I)),None);conditions=sorted(tags.intersection(x['structured_disease_matches']))
 if match:
  asset,pat,mod,action=match
  for indication in conditions:
   key=asset+'|'+indication
   if key not in prog:prog[key]={'program_id':key,'asset':asset,'indication':indication,'candidate_ids':[],'aliases':[],'trial_ids':[],'modality':mod,'action':action,'genetically_defined_cns':indication!='Lennox_Gastaut','rare_nononcology':True,'genetic_medicine':mod in ['ASO','siRNA','ex_vivo_gene_therapy','in_vivo_gene_therapy','gene_therapy_candidate'],'novel_target_at_entry':None,'intrathecal':True if mod=='ASO' else None,'protein_restoration':action in ['SMN2_splicing','SCN1A_restoration','UBE3A_unsilencing','ARSA_restoration','ABCD1_restoration','SMN1_replacement','TPP1_replacement','ARSA_replacement','CLN6_replacement','CLN3_replacement','CLN7_replacement','CLN5_replacement','MECP2_replacement','SCN1A_transcription_increase'],'status':'unknown','status_date':None,'outcome_sources':[],'entry_confidence':'earliest observed indication trial proxy; NOT independently verified first human entry','cohort_eligibility':'pending_pre_entry_exposure_and_registration_intent','notes':[]}
   p=prog[key];p['candidate_ids'].append(x['candidate_id']);p['aliases'].append(n);p['trial_ids']+=x['nct_ids']
  dispositions.append({'candidate_id':x['candidate_id'],'name':n,'disposition':'mapped_program_identity','program_ids':[asset+'|'+i for i in conditions],'identity_confidence':'curated alias / registry naming; novel-target and initial-human-stage separately unresolved'})
 elif background.search(n):dispositions.append({'candidate_id':x['candidate_id'],'name':n,'disposition':'exclude_background_diagnostic_or_nontherapeutic','reason':'Not a distinct investigational therapeutic program for the stated disease; inspect original trial if broader scope changes.'})
 elif repurposed.search(n):dispositions.append({'candidate_id':x['candidate_id'],'name':n,'disposition':'previously_human_tested_or_repurposed_review','reason':'Separate from de novo pre-human clinical-entry universe. Indication-specific development may still be relevant to broad sensitivity; not classified as failure.'})
 else:dispositions.append({'candidate_id':x['candidate_id'],'name':n,'disposition':'unresolved_identity_or_commercial_intent','reason':'No safe canonical mapping; retained visibly rather than forced into program/outcome count.'})
# Restore subtype information that broad search matching cannot distinguish.
for p in prog.values():
 p['candidate_ids']=sorted(set(p['candidate_ids']));p['aliases']=sorted(set(p['aliases']));p['trial_ids']=sorted(set(p['trial_ids']))
 dates=[trials[n]['start_date'] for n in p['trial_ids'] if trials[n]['start_date']]
 p['entry_date_proxy']=min(dates,default=None);p['entry_trial_candidates']=[n for n in p['trial_ids'] if trials[n]['start_date']==p['entry_date_proxy']]
 p['registry_sources']=['https://clinicaltrials.gov/study/'+n for n in p['entry_trial_candidates']]
 p['registry_statuses']={n:trials[n]['registry_status'] for n in p['trial_ids']}
 p['verified_last_program_followup']=None
 if p['indication'] in ['NCL','SCA']:p['notes'].append('Disease-family label requires subtype verification; supplied trial conditions remain in source ledger.')
 if p['asset']=='onasemnogene_abeparvovec':p['notes'].append('IV first approval distinguished from later intrathecal OAV101 route/label expansion; do not count route expansion as independent first approval.')
 if p['modality']=='gene_therapy_candidate':p['notes'].append('Modality is provisional from program context; target and route need confirmation.')
 # Reuse existing ASO evidence only when identity matches.
 old=next((r for r in prior if r['asset'].lower()==p['asset'].lower()),None)
 if old:
  p['status']=old['status_asof'];p['status_date']=old['status_event_date'];p['entry_date_proxy']=old['entry_date_proxy'];p['entry_trial_candidates']=[old['entry_trial']];p['novel_target_at_entry']=old['novel_target_at_entry'];p['prior_human_data_before_entry']=old['prior_human_data_before_entry'];p['cohort_eligibility']='inherited_v1_reference_cohort_not_exhaustive';p['outcome_sources']=[sources[s]['url'] for s in old['status_sources'] if s in sources];p['notes'].append('Status/entry adjudication reused from data/pos_audit/program_ledger.json; not independently revalidated.')
  p['registry_sources']=['https://clinicaltrials.gov/study/'+old['entry_trial']]
  p['latest_program_status_evidence_date']=max((sources[s].get('date','') for s in old['status_sources'] if s in sources),default=None)
outcomes={
'atidarsagene_autotemcel|MLD':('approved','2024-03-18','https://www.fda.gov/news-events/press-announcements/fda-approves-first-gene-therapy-children-metachromatic-leukodystrophy','traditional'),
'elivaldogene_autotemcel|ALD':('approved','2022-09-16','https://www.fda.gov/media/161665/download?attachment=','accelerated'),
'onasemnogene_abeparvovec|SMA':('approved','2019-05-24','https://www.fda.gov/vaccines-blood-biologics/zolgensma','traditional'),
'branaplam|SMA':('stopped_strategic','2021-07-21','https://assets.sma-europe.eu/21072021_Branaplam_in_SMA_Community_Update_July_2021_FINAL_PDF_827fc25697.pdf',None),
'trofinetide|Rett':('approved','2023-03-10','https://www.fda.gov/drugs/news-events-human-drugs/fda-approves-first-treatment-rett-syndrome','traditional'),
'ganaxolone|CDKL5':('approved','2022-03-18','https://www.fda.gov/drugs/drug-approvals-and-databases/drug-trials-snapshots-ztalmy','traditional'),
'gaboxadol|Angelman':('stopped_efficacy','2021','https://www.sec.gov/Archives/edgar/data/1636651/000095017022003668/ovid-20211231.htm',None),
}
for ind in ['Dravet','Lennox_Gastaut','CDKL5']:outcomes['soticlestat|'+ind]=('stopped_efficacy','2025-01-30','https://www.takeda.com/newsroom/statements/2025/takeda-provides-update-on-soticlestat/',None)
for key,(status,date,url,approvaltype) in outcomes.items():
 if key in prog:
  p=prog[key];p['status']=status;p['status_date']=date;p['outcome_sources']=[url];p['approval_type']=approvaltype;p['notes'].append('Outcome separately verified from primary regulator/sponsor; entry eligibility still independently unresolved.')
 if key=='ganaxolone|CDKL5' and key in prog:prog[key]['notes'].append('Earlier human development in epilepsy predates CDKL5 indication; not a clean first-human molecule entry.')
 if key=='trofinetide|Rett' and key in prog:prog[key]['notes'].append('Earlier development in other indications must be audited; no assumption of pre-human-data stage at Rett trial.')
# Primary-source updates are kept in a separate human-readable evidence file.
for update in load('data/pos_adjudication/neuro_primary_adjudications.json'):
 if update['program_id'] in prog:prog[update['program_id']].update(update)
# Registry dates are enrollment proxies, never assumed dosing dates. Detect zero-entry attrition.
raw={}
for f in (P/'sources/pos_nested').glob('*allphase*.json'):
 d=json.loads(f.read_text())
 if isinstance(d,dict):
  for s in d.get('studies',[]):
   m=s.get('protocolSection',{}); raw[m.get('identificationModule',{}).get('nctId')]=m
closest={'zorevunersen','apazunersen','rugonersen','obudanersen'}
for p in prog.values():
 p['neurodevelopmental']=p['indication'] in {'Angelman','Dravet','Rett','Fragile_X','SYNGAP1','CDKL5','Lennox_Gastaut'}
 p['genetic_medicine']=p['modality'] in {'ASO','siRNA','ex_vivo_gene_therapy','in_vivo_gene_therapy','gene_therapy_candidate'}
 if p['asset']=='SHP611_IT':p['intrathecal']=True
 p['closest_restoration_ASO4']=p['asset'] in closest
 p['verified_last_program_followup']=None
 p.setdefault('first_human_entry_verified',False)
 p['clinical_entry_evidence']=[]
 if p['action'] is None:p['protein_restoration']=None
 for n in p['trial_ids']:
  m=raw.get(n,{});st=m.get('statusModule',{});e=m.get('designModule',{}).get('enrollmentInfo',{})
  p['clinical_entry_evidence'].append({'trial_id':n,'start':st.get('startDateStruct'),'enrollment':e,'status':st.get('overallStatus'),'why_stopped':st.get('whyStopped'),'source':'https://clinicaltrials.gov/study/'+n})
 es=p['clinical_entry_evidence']
 if es and all(x['enrollment'].get('count')==0 and x['enrollment'].get('type')=='ACTUAL' for x in es):
  p['cohort_eligibility']='exclude_no_indication_patient_enrollment'
  p['status']='predose_indication_attrition'
  p['status_date']=None
  p['entry_confidence']='All identified indication trials report actual enrollment zero; clinical inception not established.'
  p['notes'].append('Preserve as a pre-dose boundary case, not a failure after clinical inception. Prior human use in other indications may exist.')
 elif not any(x.get('start',{}).get('type')=='ACTUAL' for x in es if x.get('start')):
  p['cohort_eligibility']='pending_actual_clinical_entry'
  p['notes'].append('No actual start date found in panel. Estimated enrollment/start is not evidence of dosing.')
 p['entry_date_type']='registry enrollment proxy; does not prove first administration'
 p['outcome_confidence']=('primary_source' if p['status']!='unknown' else 'primary_source_for_existence_only') if p.get('outcome_sources') else 'unresolved'
 if p['cohort_eligibility']=='inherited_v1_reference_cohort_not_exhaustive':p['outcome_confidence']='inherited_source_adjudication'
 if p['asset']=='SHP611_IT':p['notes'].append('Generic rhASA candidate mapped using NCT01510028 intervention description naming HGT-1110. This is intrathecal HGT-1110, not intravenous HGT-1111.')
 if p['asset']=='AB-1001':p['notes'].append('CYP46A1 gene delivery, not HTT silencing. Kept separate from withdrawn VY-HTT01.')
 sub={'AT-GTX-501':'CLN6','CLN-301':'CLN3','AAV9_CLN7':'CLN7','AAVrh10_CLN2':'CLN2','cerliponase_alfa':'CLN2','NGN-101':'CLN5','ARO-ATXN2':'SCA2','BIIB132':'SCA3'}
 if p['asset'] in sub:p['indication_subtype']=sub[p['asset']]
 if p['asset'] in {'ganaxolone','trofinetide'}:
  p['cohort_eligibility']='exclude_first_human_before_2010_later_indication'
  p['prior_human_data_before_entry']=True
  p['first_human_on_or_before']='1997' if p['asset']=='ganaxolone' else '2007-02-13'
  p['first_human_sources']=['https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/j.1528-1157.1997.tb01486.x' if p['asset']=='ganaxolone' else 'https://www.neurenpharma.com/PDF/9d4b66d5-dade-4e5f-bbbb-d4155137b8f1/FurtherValidationofNNZ2566asTBITreatment']
  p['notes'].append('Primary pre-2010 human exposure evidence excludes this molecule from a strict 2010-2024 novel-entry frame. Retained only for indication-development sensitivity.')
# Each query is logged even when it did not resolve program fate. Search hits are not automatically evidence.
research=[]
for p in prog.values():
 pattern=next((m[1] for m in M if m[0]==p['asset']),re.escape(p['asset']))
 searched=[]
 for f in (P/'sources/pos_adjudication').glob('neuro_primary_search_*.json'):
  d=json.loads(f.read_text())
  if not isinstance(d,dict):continue
  for q in d.get('queries',[]):
   query=q['q']
   if re.search(pattern,query,re.I) or re.sub(r'[^a-z0-9]','',p['asset'].lower()) in re.sub(r'[^a-z0-9]','',query.lower()):searched.append({'query':query,'source_file':str(f.relative_to(P))})
 inherited=any('reused from data/pos_audit' in n for n in p['notes'])
 p['legacy_novel_target_at_entry']=p.get('novel_target_at_entry')
 p['novel_target_at_entry']=None
 p['target_previously_tested_in_humans_at_entry']=None
 p['target_clinical_efficacy_established_at_entry']=None
 p['reference_implied_no_approved_target_therapy']=p['legacy_novel_target_at_entry'] if inherited else None
 p['no_approved_target_directed_treatment_at_entry']=True if p['asset']=='nusinersen' else False if p['asset']=='salanersen' else None
 p['target_validation_flag_basis']='Nusinersen first SMA approval in December2016 precedes salanersen entry and follows nusinersen entry.' if p['asset'] in {'nusinersen','salanersen'} else 'Not independently adjudicated; the legacy reference implication is not treated as established history.'
 p['target_validation_sources']=['https://investors.biogen.com/news-releases/news-release-details/us-fda-approves-biogens-spinrazatm-nusinersen-first-treatment'] if p['asset'] in {'nusinersen','salanersen'} else []
 if inherited:p['notes'].append('The legacy novel-target flag does not establish that the target had never been treated in humans. Literal target novelty is reset to unknown; approval validation is a separate reference-derived field.')
 research.append({'program_id':p['program_id'],'queries':searched,'inherited_prior_source_audit':inherited,'primary_adjudication':bool(p.get('outcome_sources')),'result':'outcome_resolved_or_current_evidence' if p['status']!='unknown' else 'fate_unresolved_after_public_review' if searched or p.get('outcome_sources') else 'not_individually_searched','limitation':'One bounded public pass; no search result is proof of absence. Registry and secondary sources may establish existence without establishing program fate.'})
 p['research_log_key']=p['program_id']
 p['entry_evidence_class']='inherited_reference_cohort' if inherited else 'registry_proxy_pending_first_human_validation'
 p['independent_program_outcome']=False if p['asset'] in {'DUOC-01','BMB-101','bexicaserin','soticlestat','VO659'} else None
# Preserve full mapping coverage and explicit unknowns.
# Preserve full mapping coverage and explicit unknowns.
ledger=sorted(prog.values(),key=lambda x:x['program_id'])
summary={'as_of':'2026-11-16','scope':'Neurodevelopment/genetic neurodegeneration/SMA candidates with observed panel date2010–2024','candidate_buckets':len(rows),'all_candidates_dispositioned':len(dispositions)==len(rows),'dispositions':dict(Counter(x['disposition'] for x in dispositions)),'canonical_program_indication_records':len(ledger),'status_counts':dict(Counter(x['status'] for x in ledger)),'novel_program_entry_denominator_verified':False,'approval_probability':None,'limitation':'Canonical mapping and outcome review do not prove exhaustive ascertainment or first-human entry. Unknown fate retained. Broad NCL/SCA subtype mapping requires refinement; these rows are not final independently countable observations.'}
summary['entry_gate_counts']=dict(Counter(x['cohort_eligibility'] for x in ledger))
summary['research_dispositions']=dict(Counter(x['result'] for x in research))
summary['closest_restoration_ASO4']=[{'program_id':x['program_id'],'status':x['status']} for x in ledger if x['closest_restoration_ASO4']]
(D/'neuro_program_ledger.json').write_text(json.dumps(ledger,indent=2)+'\n');(D/'neuro_candidate_dispositions.json').write_text(json.dumps(dispositions,indent=2)+'\n');(D/'neuro_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(D/'neuro_research_log.json').write_text(json.dumps(research,indent=2)+'\n')
assert len({x['candidate_id'] for x in dispositions})==len(rows)
assert all(x['candidate_id'] in cs for x in dispositions)
assert all(set(x['candidate_ids'])<=set(cs) for x in ledger)
print(json.dumps(summary,indent=2))
