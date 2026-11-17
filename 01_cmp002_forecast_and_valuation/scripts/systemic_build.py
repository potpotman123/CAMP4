"""Rebuild finite systemic candidate map; no trial-status-to-failure inference.
Run from repository root. Input registry snapshot is preserved separately.
"""
import json, re, hashlib
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1]
Q=json.loads((P/'data/pos_nested/candidate_review_queue.json').read_text())
S={r['candidate_id']:r for r in json.loads((P/'data/pos_adjudication/full_screen.json').read_text())}
T={r['nct_id']:r for r in json.loads((P/'data/pos_nested/trial_inventory.json').read_text())}
ASOF='2026-11-16'
RAW={}
for f in (P/'sources/pos_nested').glob('broad_allphase_*.json'):
 for st in json.loads(f.read_text()).get('studies',[]):
  m=st.get('protocolSection',{});RAW[m.get('identificationModule',{}).get('nctId')]=m
EXTERNAL={}
for f in (P/'sources/pos_adjudication').glob('systemic_*_api.json'):
 v=json.loads(f.read_text());v=v.get('response',v)
 for st in v.get('studies',[]):
  m=st.get('protocolSection',{});n=m.get('identificationModule',{}).get('nctId');RAW[n]=m;EXTERNAL[n]=m
def norm(x): return re.sub(r'[^a-z0-9]','',x.lower())
def hp(c): return bool(re.search(r'angioedema|paroxysmal|\bpnh\b',' '.join(c['conditions']),re.I))
def priority(c): return S[c['candidate_id']]['disposition']=='priority_early_industry' and bool(set(c['families'])&{'hematology','systemic','immune'})
def supplemental(c): return hp(c) and c['entry_window_candidate'] and any(T[n]['sponsor']['class']=='INDUSTRY' for n in c['nct_ids'])
C=[c for c in Q if priority(c) or supplemental(c)]
# Explicit identity/dose rules; clinical meaning is adjudicated independently below.
RULES=[
 ('berotralstat','bcx7353|berotralstat'),('lanadelumab','dx2930|lanadelumab|tak743'),
 ('avoralstat','bcx4161|avoralstat'),('sebetralstat','kvd900|sebetralstat'),('KVD824','kvd824'),
 ('BMN331','bmn331'),('navenibart','star0215|navenibart'),('NTLA2002','ntla2002|lonvoguran'),
 ('ADX324','adx324'),('GNR038','gnr038'),('garadacimab','csl312|garadacimab'),
 ('donidalorsen','donidalorsen|isis721744|ionispkklrx'),('deucrictibant','deucrictibant|pha121'),
 ('CSL830','csl830'),('SHP623','shp623'),('C1INH established/formulation','c1esteraseinhibitor|c1inhibitor|cinryze|berinert|rhc1inh'),
 ('icatibant','icatibant|tak667'),('ecallantide','ecallantide'),
 ('TT30','alxn1102|alxn1103|^tt30$'),('ravulizumab','alxn1210|ravulizumab'),
 ('pegcetacoplan','pegcetacoplan|^apl2$'),('crovalimab','crovalimab'),('BCX9930','bcx9930'),
 ('BCX10013','bcx10013'),('KP104','kp104'),('ADX038','adx038'),('zaltenibart','oms906|zaltenibart'),
 ('LP005','lp005'),('lanoracopan','my008211a|lanoracopan'),('HRS5965','hrs5965'),
 ('ciprocopan','hsk39297|ciprocopan'),('SAR443809','humanizedantifactorbb|sar443809'),
 ('iptacopan','lnp023|iptacopan'),('danicopan','danicopan|ach0144471'),('vemircopan','alxn2050|vemircopan'),
 ('pozelimab','regn3918|pozelimab'),('cemdisiran','cemdisiran'),('nomacopan','coversin|rva576|nomacopan'),
 ('zilucoplan','zilucoplan|ra101495'),('eculizumab established/biosimilar','eculizumab|soliris|sb12|bcd148|elizaria'),
 ('Mim8','mim8|nnc03653769'),('concizumab','nnc017200002021|nnc1722021|concizumab'),
 ('sodium nitrite inhaled','sodiumnitrite'),('treprostinil formulation','treprostinil|ut15c'),
 ('tadalafil formulation','tadalafil'),('iloprost formulation','lloprost|iloprost'),('bosentan formulation','bosentan|tracleer|traclear'),
 ('riociguat formulation','riociguat|adempas'),('ticagrelor formulation','ticagrelor'),
 ('ivacaftor','^vx770$|^ivacaftor$'),('tezacaftor','^tez$|tezacaftor|vx661'),('elexacaftor','vx445|elexacaftor'),
 ('vanzacaftor','vx121|vanzacaftor'),('deutivacaftor','deutivacaftor'),
 ('A4250','a4250'),('AZD5634','azd5634'),('CHF6333','chf6333'),('GLPG2451','glpg2451'),
 ('BIA51058','bia51058'),('GMA301','gma301'),('ETD001','etd001'),('TPN171H','tpn171h'),
 ('FTX6058','ftx6058'),('IMR687','imr687|tovinontrine'),('voxelotor','gbt440|voxelotor'),
 ('osivelotor','gbt021601|osivelotor'),('etavopivat','etavopivat'),('EDIT301','edit301'),('CS101','^cs101'),
 ('EB101','lzrsecol7a1|prademagene|^eb101$'),('B-VEC','beremagene|bvec'),
 ('BB305','lentiglobinbb305|lovocel|beticel'),('BPX501','bpx501|rivogenlecleucel'),
 ('ALX009','alx009|^oscn$|^blf$'),('GLPG2737','glpg2737'),('GLPG3067','glpg3067'),
]
def identity(c):
 n=norm(c['intervention_name'])
 if c['nct_ids']==['NCT02663687'] and 'c1' in n:return 'SHP623','same_trial_explicit_recombinant_C1INH_alias'
 for a,pat in RULES:
  if re.search(pat,n): return a,'curated_alias_or_dose_rule'
 return c['intervention_name'],'unmerged_registry_identity'
def disease(c):
 x=' '.join(c['conditions']).lower()
 if 'angioedema' in x:return 'HAE'
 if 'paroxysmal' in x or re.search(r'\bpnh\b',x):return 'PNH'
 if 'primary immunodeficiency' in x and 'leukemia' in x:return 'Mixed transplantation indications including malignancy'
 if 'sickle' in x and ('thalassemia major' in x or 'sickle cell disease & thalassemia' in x or ('sickle cell disease;thalassemia' in x)):return 'SCD and beta-thalassemia mixed'
 if 'sickle' in x:return 'SCD'
 if 'thalassemia' in x or 'β-thalassemia' in x:return 'Beta-thalassemia'
 if 'epidermolysis' in x:return 'Epidermolysis bullosa'
 if ('non-cystic fibrosis' in x or 'noncystic fibrosis' in x) and not any(y.lower() in ['cystic fibrosis','cystic fibrosis (cf)'] for y in c['conditions']):return 'Non-CF bronchiectasis (panel mismatch)'
 if 'cystic fibrosis' in x:return 'Cystic fibrosis'
 if 'haemophilia' in x or 'hemophilia' in x:return 'Hemophilia A/B (subtype review)' if 'haemophilia a' in x and 'haemophilia b' in x else ('Hemophilia B' if 'haemophilia b' in x else 'Hemophilia A')
 if 'biliary' in x and ('alagille' in x or 'familial' in x):return 'Mixed cholestatic liver indications'
 if 'biliary' in x:return 'Primary biliary cholangitis'
 if 'hypertension' in x or 'hypertensi' in x:return 'Pulmonary arterial hypertension'
 if 'combined immunodeficiency' in x:return 'SCID'
 if 'granulomatous' in x:return 'Chronic granulomatous disease'
 return '; '.join(c['conditions'])
E={}
def ev(asset,status,eventdate,url,note,source_date=None,**kw):
 E[asset]={'status':status,'outcome_date':eventdate,'evidence':[{'url':url,'source_date':source_date or eventdate,'accessed_date':ASOF,'claim':note,'source_type':'primary_regulator_or_sponsor'}],**kw}
ev('berotralstat','approved','2020-12-03','https://www.accessdata.fda.gov/scripts/opdlisting/oopd/detailedIndex.cfm?cfgridkey=607617','FDA first approval for HAE prophylaxis.',jurisdiction='FDA')
ev('lanadelumab','approved','2018-08-23','https://www.fda.gov/media/173980/download','FDA original approval listing for lanadelumab/Takhzyro.',jurisdiction='FDA')
ev('sebetralstat','approved','2025-07-03','https://www.accessdata.fda.gov/drugsatfda_docs/appletter/2025/219301Orig1s000ltr.pdf','FDA approval for acute HAE attacks; July 7 announcement is not approval date.',jurisdiction='FDA')
ev('donidalorsen','approved','2025-08-21','https://www.accessdata.fda.gov/drugsatfda_docs/nda/2025/219407Orig1s000Approv.pdf','FDA approval package: HAE prophylaxis age 12+.',jurisdiction='FDA')
ev('garadacimab','approved','2025-06-16','https://www.accessdata.fda.gov/scripts/purplebooksearch/index.cfm?blaNo=761367&event=productdetails','FDA original approval for Andembry; HAE prophylaxis confirmed by label.',jurisdiction='FDA')
ev('BMN331','stopped','2024-04-24','https://investors.biomarin.com/news/news-details/2024/BioMarin-Reports-Record-Financial-Results-for-the-First-Quarter-2024/default.aspx','Sponsor terminated BMN331 in portfolio prioritization; reported no safety signal.',stop_reason='strategic')
ev('KVD824','stopped','2022-10','https://www.sec.gov/Archives/edgar/data/1348911/000119312522312718/d418283d424b5.htm','KOMPLETE discontinued following liver enzyme elevations; label is indication-program discontinuation, not proof of molecule never being repurposed.',source_date='2022-12',stop_reason='safety')
ev('avoralstat','stopped','2016','https://ir.biocryst.com/static-files/1fbd3b4e-272d-4267-8d66-6a4d020e8834','Sponsor filing: Phase 3 failed primary endpoint; alternative formulations failed exposure objectives, then further development stopped. Later DME repurposing does not change HAE fate.',source_date='2019',stop_reason='efficacy_and_exposure')
ev('BCX9930','stopped','2022-12-15','https://ir.biocryst.com/news-releases/news-release-details/biocryst-discontinues-development-bcx9930-and-shifts-focus','Sponsor discontinued because new competitor data made commercial competitiveness doubtful.',stop_reason='strategic_competitiveness')
ev('BCX10013','stopped','2024-08-05','https://ir.biocryst.com/static-files/42e13a74-a7eb-405f-b0f1-068d884b240b','Clinical activity below marketed competitors; potential partners declined higher-dose investment; sponsor plans discontinued development. Subsequent annual results confirm close-out.',source_date='2024-08-06',stop_reason='activity_and_financing')
ev('ravulizumab','approved','2018-12-21','https://www.accessdata.fda.gov/scripts/opdlisting/oopd/detailedIndex.cfm?cfgridkey=513015','FDA approval in adult PNH; C5 mechanism already validated by eculizumab.',jurisdiction='FDA')
ev('pegcetacoplan','approved','2021-05-14','https://www.accessdata.fda.gov/scripts/opdlisting/oopd/detailedIndex.cfm?cfgridkey=427614','FDA PNH approval, not later geographic-atrophy indication.',jurisdiction='FDA')
ev('crovalimab','approved','2024-06-20','https://purplebooksearch.fda.gov/index.cfm?blaNo=761388&event=productdetails','Original FDA approval; PNH label verified separately.',jurisdiction='FDA')
ev('iptacopan','approved','2023-12-06','https://www.novartis.com/news/media-releases/novartis-receives-fda-approval-fabhalta-iptacopan-offering-superior-hemoglobin-improvement-absence-transfusions-first-oral-monotherapy-adults-pnh','Sponsor announces FDA approval for adult PNH monotherapy.',jurisdiction='FDA')
ev('danicopan','approved','2024-03-29','https://www.fda.gov/drugs/drug-trials-snapshots/drug-trials-snapshots-voydeya','FDA approval as add-on for extravascular hemolysis in PNH receiving ravulizumab/eculizumab; not stand-alone first therapy.',jurisdiction='FDA')
ev('navenibart','ongoing',None,'https://biocryst.gcs-web.com/news-releases/news-release-details/biocryst-reports-third-quarter-2026-financial-results','Pivotal ALPHA-ORBIT ongoing and fully enrolled; results expected Q3 2027.',source_date='2026-11-04')
ev('NTLA2002','ongoing',None,'https://ir.intelliatx.com/node/13006/pdf','Ongoing HAE development following Phase 3; launch preparations are not approval.',source_date='2026-11-12')
ev('deucrictibant','ongoing',None,'https://ir.pharvaris.com/news-releases/news-release-details/pharvaris-reports-third-quarter-2026-financial-results-and','IR NDA under FDA review with April 2027 PDUFA; XR positive Phase 3 reported. Same molecule retained as one HAE asset cluster.',source_date='2026-11-12')
for a,claim in [('ADX324','Onvuzosiran PKK Phase 3 STOP-HAE ongoing; 2027 topline planned.'),('ADX038','Agazisiran CFB Phase 2 PNH ongoing; data planned 2H2027.')]:
 ev(a,'ongoing',None,'https://investors.adarx.com/news-releases/news-release-details/adarx-reports-third-quarter-2026-financial-results-and-provides',claim,source_date='2026-11-12')
ev('KP104','ongoing',None,'https://www.sec.gov/Archives/edgar/data/1788028/000121390026120161/ea0310332-10q_jasper.htm','Sponsor reports prior positive PNH data and planned pre-IND meeting/next steps in 2027; ongoing development, not currently confirmed recruiting PNH trial.',source_date='2026-11-13')
ev('zaltenibart','ongoing',None,'https://www.novonordisk.com/content/dam/nncorp/global/en/investors/pdfs/financial-results/2026/Q3-2026-Full-presentation.pdf','Slide78: PNH Phase3 expected mid2027 after Phase1/2; acquired from Omeros2025.',source_date='2026-11')
for a in ['pozelimab','cemdisiran']:
 ev(a,'ongoing',None,'https://www.regeneron.com/science/investigational-pipeline','Sponsor pipeline lists pozelimab plus cemdisiran for PNH. Molecules tracked separately with common combination cluster; do not count correlated combo as independent trials. Pozelimab CHAPLE approval does not count as PNH approval.',source_date='2026-10-30')
ev('nomacopan','stopped','2024-06','https://investor.akaritx.com/static-files/c1c965d2-0149-4d44-a56f-ebb8c56661db','Internal nomacopan development suspended June2024 with shift to ADCs; partnership sought. Commercial/strategic suspension, reversible, not efficacy failure.',source_date='2026-01-23',stop_reason='strategic_suspension',reversible=True)
ev('lanoracopan','ongoing',None,'https://www.createrna.com/en/news-activity/news-center/news/59','MY008211A Phase3 PNH met primary endpoint; sponsor active development. No FDA approval verified.',source_date='2026-02-13')
ev('HRS5965','ongoing',None,'https://static.cninfo.com.cn/finalpage/2026-01-10/1224927347.PDF','Sponsor exchange filing: Chinese PNH marketing application accepted January2026. This is acceptance, not marketing authorization. Later China approval not yet checked.',source_date='2026-01-10')
ev('ciprocopan','approved','2026-07','https://disc.static.szse.cn/disc/disk03/finalpage/2026-08-27/8ef41362-8592-467c-8fba-38d4f313eb45.PDF','Sponsor interim report confirms Chinese NMPA approval for previously untreated adult PNH in July2026. Not FDA approval.',source_date='2026-08-27',jurisdiction='NMPA',fda_endpoint_status='unknown_no_FDA_approval_verified')
ev('IMR687','stopped','2022-04','https://www.sec.gov/Archives/edgar/data/1672619/000156459022018458/imra-10q_20220331.htm','Sponsor ceased SCD/thalassemia development after interim Phase2b findings; later asset sale/other-indication research not an SCD success.',source_date='2022-05',stop_reason='efficacy')
ev('voxelotor','approved','2019-11-25','https://www.fda.gov/drugs/drug-alerts-and-statements/fda-alerting-patients-and-health-care-professionals-about-voluntary-withdrawal-oxbryta-market-due','Initial FDA approval in2019; voluntary withdrawal September2024 is a separate postapproval safety outcome.',source_date='2024-09-26',jurisdiction='FDA',postapproval_withdrawal='2024-09-26')
ev('EB101','approved','2025-04-28','https://www.fda.gov/vaccines-blood-biologics/zevaskyn','FDA approval prademagene zamikeracel for RDEB; encoded COL7A1 epidermal sheets.',jurisdiction='FDA')
ev('B-VEC','approved','2023-05-19','https://www.fda.gov/news-events/press-announcements/fda-approves-first-topical-gene-therapy-treatment-wounds-patients-dystrophic-epidermolysis-bullosa','FDA approval beremagene geperpavec for dystrophic EB.',jurisdiction='FDA')
ev('elexacaftor','approved','2019-10-21','https://www.accessdata.fda.gov/scripts/opdlisting/oopd/detailedIndex.cfm?cfgridkey=647618','FDA approval elexacaftor/tezacaftor/ivacaftor fixed combination for CF; not three independent new-drug successes.',jurisdiction='FDA')
ev('vanzacaftor','approved','2024-12-20','https://www.fda.gov/drugs/drug-approvals-and-databases/drug-trials-snapshot-alyftrek','FDA approval vanzacaftor/tezacaftor/deutivacaftor fixed combination. Count cluster, not components as independent outcomes.',jurisdiction='FDA')
ev('deutivacaftor','approved','2024-12-20','https://www.fda.gov/drugs/drug-approvals-and-databases/drug-trials-snapshot-alyftrek','Same Alyftrek combination success as vanzacaftor; correlated cluster, not an extra independent approval.',jurisdiction='FDA')
ev('MRT5005','stopped',None,'https://apps.cff.org/Trials/Pipeline/details/10157/MRT5005','CFF Therapeutics Development Network pipeline says no active CF development and discontinued. Program-level partner source; exact stop date not established.',source_date=None,stop_reason='not_specified')
E['MRT5005']['evidence'][0]['source_type']='trial_network_primary_program_tracker'
# Explicit non-outcome evidence/ambiguity; unknown preserved after targeted checks.
UNKNOWN={
 'TT30':('NCT01335165','ALXN1102 and ALXN1103 are formulations of TT30 per sponsor brief summary. Trial ended for enrollment; no primary global program-stop source retrieved.','ALXN1102 ALXN1103 TT30 discontinued'),
 'GNR038':('NCT04898309','Phase2/3 withdrawn before start due company pipeline revision. Retain unknown program fate; established recombinant C1INH target/follow-on.','GNR-038 hereditary 2026'),
 'SAR443809':('NCT06326814','Generic antibody name resolves via registry otherNames to SAR443809. Healthy study complete; no indication-specific PNH development outcome verified.','SAR443809 PNH 2026'),
 'zilucoplan':('NCT03078582','PNH Phase2 completed and EMA PNH orphan designation withdrawn February2022; neither proves global program termination. gMG approval must not be counted for PNH.','zilucoplan PNH discontinued'),
 'vemircopan':(None,'No primary indication-specific terminal outcome located in bounded search.','vemircopan PNH discontinued'),
 'LFG316':(None,'PNH program fate/earliest ocular human exposure needs reconciliation; later indication likely.','LFG316 PNH first human discontinued'),
 'EA5':('NCT07256301','Sponsor registry says recruiting on May14 2026; actual start2024-01-03 despite late registration. Supports current activity, not approval.','registry source review'),
 'LP005':('NCT07212426','Sponsor registry says active not recruiting January16 2026; Phase2 PNH active after completed healthy-volunteer study.','registry source review'),
}
for a,(n,claim,query) in UNKNOWN.items():
 if a not in E:
  E[a]={'status':'ongoing' if a in ['EA5','LP005'] else 'unknown','outcome_date':None,'evidence':[],'unresolved_checks':[{'date':ASOF,'query':query,'result':claim}]}
  if n:E[a]['evidence'].append({'url':'https://clinicaltrials.gov/study/'+n,'source_date':T.get(n,{}).get('last_update'),'accessed_date':ASOF,'claim':claim,'source_type':'sponsor_trial_registry'})
E['zilucoplan']['evidence'].append({'url':'https://www.ema.europa.eu/en/medicines/human/orphan-designations/eu-3-16-1762','source_date':'2022-02-01','accessed_date':ASOF,'claim':'PNH orphan designation withdrawn on sponsor request; approval in other disease is not PNH success.','source_type':'regulator'})
E['zilucoplan']['status']='stopped'
E['zilucoplan']['stop_reason']='indication_program_discontinued_reason_not_fully_specified'
E['zilucoplan']['evidence'].append({'url':'https://clinicaltrials.gov/study/NCT03225287','source_date':RAW['NCT03225287']['statusModule']['lastUpdatePostDateStruct']['date'],'accessed_date':ASOF,'claim':'Sponsor explicitly states UCB decided no longer to pursue PNH as a potential indication. This is direct indication-program abandonment, beyond a terminated-trial label. Exact decision date not established.','source_type':'sponsor_trial_registry'})
E['vemircopan']['evidence'].append({'url':'https://clinicaltrials.gov/study/NCT04170023','source_date':RAW['NCT04170023']['statusModule']['lastUpdatePostDateStruct']['date'],'accessed_date':ASOF,'claim':'PNH monotherapy trial stopped because IVH was not adequately controlled and BTH/LDH excursions exceeded ravulizumab. This verifies trial efficacy failure, but global PNH program fate remains unknown.','source_type':'sponsor_trial_registry'})
E['SHP623']={'status':'unknown','outcome_date':None,'evidence':[{'url':'https://clinicaltrials.gov/study/NCT02663687','source_date':'2021-07-07','accessed_date':ASOF,'claim':'Healthy-volunteer recombinant C1INH study; molecular/formulation distinction and subsequent fate unresolved.','source_type':'sponsor_trial_registry'}],'unresolved_checks':[{'date':ASOF,'query':'SHP623 intervention API complete result','result':'One Phase1 record; completion is not program discontinuation.'}]}
# Date corrections based on explicitly first-human primary publications.
FIRST={
 'garadacimab':{'date':'2016-10-28','basis':'explicit_first_in_human_study_start','trial':'ACTRN12616001438448','url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC8932690/','source_date':'2021','note':'Primary report states first-human study ran October28 2016 to September22 2017, before panel disease trial.'},
 'iptacopan':{'date':'2016-07','basis':'explicit_first_in_human_study_start','trial':'EudraCT2015-005567-16; NCT04820530','url':'https://bpspubs.onlinelibrary.wiley.com/doi/10.1111/bph.70339','source_date':'2026','note':'StudyCLNP023X2101 startedJuly2016. Earlier2015 date in combination panel trial does not establish iptacopan first dosing.'}
}
for a,n in {'ADX324':'NCT05691361','ADX038':'NCT05876312','navenibart':'NCT05477160','KP104':'NCT05490017','LP005':'NCT06294301','SAR443809':'NCT06326814','crovalimab':'NCT03157635','lanoracopan':'NCT05642585','BCX9930':'NCT04330534','vemircopan':'NCT05047458'}.items():
 m=RAW[n];FIRST[a]={'date':m['statusModule']['startDateStruct']['date'],'basis':'explicit_first_in_human_sponsor_registry','trial':n,'url':'https://clinicaltrials.gov/study/'+n,'source_date':m['statusModule']['lastUpdatePostDateStruct']['date'],'note':'Sponsor title or summary expressly identifies first-in-human study; study start is still not exact first active-drug dosing time.'}
FIRST['donidalorsen']={'date':'2017-08-28','basis':'regulator_identified_FIH_trial_plus_sponsor_registry_start','trial':'NCT03263507 / ISIS721744-CS1','url':'https://clinicaltrials.gov/study/NCT03263507','source_date':RAW['NCT03263507']['statusModule']['lastUpdatePostDateStruct']['date'],'corroboration_url':'https://www.ema.europa.eu/en/documents/assessment-report/dawnzera-epar-public-assessment-report_en.pdf','note':'EMA assessment identifies CS1 as first human; registry provides start date.'}
FIRST['zaltenibart']={'date':'2020-09','basis':'sponsor_reports_initial_dosing_month','trial':'OMS906 Phase1 healthy volunteers','url':'https://s21.q4cdn.com/975996899/files/doc_financials/2020/q3/0001558370-20-013359.pdf','source_date':'2020-11','note':'Sponsor reports first Phase1 enrollment/dosing September2020, before panel PNH2022 study.'}
EARLIER={'danicopan':'NCT04889677','ravulizumab':'NCT05288660','cemdisiran':'NCT02352493','pozelimab':'NCT03115996','pegcetacoplan':'NCT02461771','LFG316':'NCT01255462'}
OLD={'CSL830','C5 Inhibitor','treprostinil formulation','tadalafil formulation','iloprost formulation','bosentan formulation','riociguat formulation','ticagrelor formulation','ivacaftor','tezacaftor','sitaxentan','C1INH established/formulation','icatibant','ecallantide','eculizumab established/biosimilar','Rosuvastatin','Digoxin','Pantoprazole','eptacog alfa (activated)','Oral Hydroxyurea (100 mg/mL) Solution','Deferoxamine Product','Lefamulin','Teicoplanin Sandoz 200 mg powder and solvent for solution for injection or infusion or oral solution.'}
GENE={'EB101','B-VEC','BB305','BMN331','NTLA2002','donidalorsen','ADX324','ADX038','cemdisiran','EDIT301','ST-400 Investigational product','BIVV003','OTQ923','BEAM-101','CS101','CS-206','PM359','MRT5005','VX-522 mRNA therapy','ARCT-032','IONIS-ENaCRx','ARO-ENaC','QR-010','KB407 (Nebulization)','FCX-007','valoctocogene roxaparvovec','SLN124','BPX501'}
RESTORE={'EB101','B-VEC','BB305','BMN331','MRT5005','VX-522 mRNA therapy','ARCT-032','KB407 (Nebulization)','FCX-007','valoctocogene roxaparvovec','QR-010'}
VALIDATED={'ravulizumab','crovalimab','navenibart','berotralstat','sebetralstat','KVD824','avoralstat','deucrictibant','donidalorsen','NTLA2002','ADX324','eculizumab established/biosimilar','GNR038','CSL830','SHP623','elexacaftor','vanzacaftor','deutivacaftor','tezacaftor','Mim8'}
groups={}
for c in C:
 a,method=identity(c);d=disease(c);key=(a,d)
 if key not in groups:groups[key]={'asset':a,'indication':d,'candidate_ids':[],'aliases':[],'trial_ids':[],'mapping_methods':[],'priority_candidate_ids':[],'supplemental_candidate_ids':[]}
 g=groups[key];g['candidate_ids'].append(c['candidate_id']);g['aliases'].append(c['intervention_name']);g['trial_ids']+=c['nct_ids'];g['mapping_methods'].append(method)
 g['priority_candidate_ids' if priority(c) else 'supplemental_candidate_ids'].append(c['candidate_id'])
programs=[];dispositions=[]
for (a,d),g in groups.items():
 g['program_id']='sys_'+hashlib.sha1((a+'|'+d).encode()).hexdigest()[:12]
 for k in ['aliases','trial_ids','mapping_methods']:g[k]=sorted(set(g[k]))
 trials=[T[n] for n in g['trial_ids']];dates=sorted(t['start_date'] for t in trials if t['start_date']);first=dates[0] if dates else None
 g['entry_date']=FIRST.get(a,{}).get('date',first);g['entry_basis']=FIRST.get(a,{}).get('basis','earliest_observed_panel_trial_start_proxy')
 g['entry_window']='2010-2024';g['first_human_entry_verified']=a in FIRST;g['entry_date_type']='observed explicit FIH study start' if a in FIRST else 'proxy; may be subsequent formulation, later indication, amended protocol or healthy-volunteer study'
 g['entry_evidence']=FIRST.get(a,{'url':next((t['source'] for t in trials if t['start_date']==first),None),'source_date':next((t['last_update'] for t in trials if t['start_date']==first),None)})
 if a in EARLIER:
  n=EARLIER[a];m=RAW[n];g['entry_date']=m['statusModule']['startDateStruct']['date'];g['entry_basis']='earlier_asset_name_query_trial_start_proxy';g['entry_evidence']={'url':'https://clinicaltrials.gov/study/'+n,'source_date':m['statusModule']['lastUpdatePostDateStruct']['date'],'note':'Retrieved by asset/aliases independent of disease query; earlier than panel entry but not automatically first active human dosing.'};g['additional_history_trial_ids']=[n]
 if a=='BCX10013':
  g['entry_date']='2022';g['entry_basis']='sponsor_first_clinical_program_year';g['first_human_entry_verified']=False;g['entry_evidence']={'url':'https://www.sec.gov/Archives/edgar/data/882796/000162828022028463/bcrx-20220930.htm','source_date':'2022-11-01','note':'Sponsor announces new clinical program with ~90 healthy volunteers already exposed; exact first dose not recovered. This corrects2023 disease-trial proxy.'}
 if a=='avoralstat':g['entry_date']='2013-07-22';g['entry_basis']='upper_bound_first_human_trial_completed_by';g['entry_evidence']={'url':'https://ir.biocryst.com/news-releases/news-release-details/biocryst-successfully-completes-its-phase-1-clinical-trial','source_date':'2013-07-22','note':'First-human completed by this date, not actual entry. Historical first-dose date unresolved.'}
 g['trial_observations']=[{k:t.get(k) for k in ['nct_id','title','start_date','start_date_type','phases','registry_status','why_stopped','last_update','source']} for t in trials]
 for ob in g['trial_observations']:
  m=RAW.get(ob['nct_id'],{});ob['enrollment']=m.get('designModule',{}).get('enrollmentInfo');ob['zero_enrollment_withdrawn']=ob.get('registry_status')=='WITHDRAWN' and ob['enrollment'] is not None and ob['enrollment'].get('count')==0
 g['only_mapped_trials_zero_enrollment_withdrawn']=bool(g['trial_observations']) and all(x['zero_enrollment_withdrawn'] for x in g['trial_observations'])
 g['never_dosed_boundary']=g['only_mapped_trials_zero_enrollment_withdrawn'] and a not in OLD
 g['zero_enrollment_scope_note']='Mapped records only; not evidence this molecule never entered humans anywhere. Established drugs must remain prior-human exclusions.'
 outcome=dict(E.get(a,{'status':'unknown','outcome_date':None,'evidence':[]}));g.update(outcome)
 # FDA-only primary endpoint, even if another jurisdiction approved.
 g['ever_FDA_approved_in_this_indication']=True if g['status']=='approved' and g.get('jurisdiction')=='FDA' else (False if g['status']=='stopped' else None)
 g['outcome_last_checked']=ASOF;g['research_depth']=('bounded_external_and_registry_review_outcome_unresolved' if g['status']=='unknown' else 'primary_outcome_or_active_program_source') if g['evidence'] else 'registry_identity_and_entry_review_only'
 g['program_level_outcome_inferred_from_trial_status']=False
 g['eligibility']='pending_first_human_and_global_entry_verification';g['eligibility_reason']='Identified investigational asset/disease; registry panel date is not proof of first human exposure. Candidate for finite reference cohort, not yet a calibrated inception denominator.';g['eligibility_confidence']='medium'
 if a in FIRST:g['eligibility']='include';g['eligibility_reason']='Explicit first-human primary study report establishes 2010–2024 entry; clinical-indication linkage supported.';g['eligibility_confidence']='high'
 if a in OLD:g['eligibility']='exclude_prior_human_or_existing_agent';g['eligibility_reason']='Established molecule, formulation/routing study or comparator/probe; not a new de novo human-entry program. Primary historical date should be checked before reuse.';g['eligibility_confidence']='medium'
 if a=='CSL830':g['eligibility_reason']='NCT01760343 explicitly compares new formulation of marketed Berinert (CSL830); exclude as de novo first-human molecule.';g['eligibility_confidence']='high'
 if a=='C5 Inhibitor':g['eligibility_reason']='NCT04469465 identifies this as background eculizumab/ravulizumab in danicopan add-on trial, not another drug candidate.';g['eligibility_confidence']='high'
 if a in ['LFG316','pegcetacoplan']:
  g['eligibility']='exclude_later_indication_from_strict_first_human';g['eligibility_reason']='Earlier ocular clinical exposure found by asset-only query. Retain PNH indication outcome, exclude from strict first-human rare-indication cohort; could include only under a separately defined indication-entry denominator.'
 if d=='Non-CF bronchiectasis (panel mismatch)':g['eligibility']='exclude_condition_mismatch';g['eligibility_reason']='Non-CF bronchiectasis was captured by CF substring. Does not establish cystic-fibrosis indication or rare disease.';g['eligibility_confidence']='high'
 if a=='SAR443809':g['eligibility']='pending_indication_linkage';g['eligibility_reason']='Healthy-volunteer study names PNH as development context; actual PNH entry/development fate not verified.'
 if d.startswith('Mixed') or 'mixed' in d or a in ['ALX009','Enriched Hematopoetic Stem Cell Infusion','NiCord','CordIn']:
  g['eligibility']='pending_program_indication_split';g['eligibility_reason']='Shared construct/combination or multi-indication transplant intervention; cannot create multiple independent first-human successes from these buckets.'
 if a=='BB305':
  g['asset_cluster_id']='BB305_lentiviral_beta_globin';g['status']='approved';g['jurisdiction']='FDA';g['ever_FDA_approved_in_this_indication']=None;g['outcome_date']=None;g['evidence']=[{'url':'https://www.fda.gov/files/vaccines%2C%20blood%20%26%20biologics/published/December-8-2023-Approval-Letter-LYFGENIA.pdf','source_date':'2023-12-08','accessed_date':ASOF,'claim':'FDA letter confirms lovo-cel SCD approval Dec8 2023 and same active ingredient previously approved Aug17 2022 as beti-cel for beta-thalassemia. Cluster shared construct; do not treat as independent first-human assets.','source_type':'regulator'}]
  if d=='SCD':g['outcome_date']='2023-12-08';g['ever_FDA_approved_in_this_indication']=True;g['eligibility']='exclude_later_indication_from_strict_first_human';g['eligibility_reason']='BB305 entered human beta-thalassemia development before SCD indication; retain for indication-level sensitivity only.'
  elif d=='Beta-thalassemia':g['outcome_date']='2022-08-17';g['ever_FDA_approved_in_this_indication']=True
 if a in ['pozelimab','cemdisiran']:g['asset_cluster_id']='pozelimab_cemdisiran_PNH_combination'
 if a in ['vanzacaftor','deutivacaftor']:g['asset_cluster_id']='Alyftrek_fixed_combination';g['eligibility']='pending_component_and_prior_human_entry';g['eligibility_reason']='Shared approval of fixed triple combination; two components must not create independent approval observations.'
 if a=='elexacaftor':g['asset_cluster_id']='Trikafta_fixed_combination'
 if a=='concizumab':g['asset_cluster_id']='concizumab_hemophilia_A_B'
 if g['never_dosed_boundary']:g['eligibility']='exclude_never_dosed_boundary';g['eligibility_reason']='All mapped studies withdrawn with zero enrollment; no clinical-entry failure may be counted.'
 g['tier_flags']={'rare':None if d=='Non-CF bronchiectasis (panel mismatch)' or d.startswith('Mixed') else True,'geneticCNS':False,'geneticmedicine':True if a in GENE or re.search('gene therapy|genetically|β-globin restored|lentiviral|enriched cd34',a,re.I) else (None if g['research_depth']=='registry_identity_and_entry_review_only' else False),'noveltarget':False if a in VALIDATED or a in OLD else None,'intrathecal':False,'proteinrestoration':True if a in RESTORE else None}
 g['tier_flag_basis']='geneticCNS/intrathecal excluded by systemic target indications; geneticmedicine/proteinrestoration describe modality/mechanism, not clinical efficacy; novel target is novelty at clinical entry and left unknown when not verified.'
 g['in_finite_HAE_PNH_reference_frame']=d in ['HAE','PNH'] and not g['eligibility'].startswith('exclude_') and g['eligibility']!='pending_indication_linkage'
 g['reference_cohort_eligibility']='eligible_reference_pending_exact_entry' if g['in_finite_HAE_PNH_reference_frame'] else ('excluded' if g['eligibility'].startswith('exclude_') else 'pending')
 if g['eligibility']=='include':g['reference_cohort_eligibility']='eligible_reference'
 g['approval_probability_input_eligible']=False
 g['remaining_checks']=[] if g['first_human_entry_verified'] else ['Recover true first-human date, including healthy-volunteer trials outside disease search; check prior exposure before2010.']
 if a in ['GNR038','SHP623','TT30','vemircopan']:
  g.setdefault('unresolved_checks',[]).append({'date':ASOF,'query':a+' discontinued / pipeline / sponsor histories; asset-only ClinicalTrials.gov API where available','result':'No conclusive primary indication-program terminal status beyond evidence recorded here. See systemic_search17.json. Vemircopan has direct trial failure; TT30/GNR038 trial closures are not automatically program failures.'})
 if g['status']=='unknown':g['remaining_checks'].append('Primary indication-specific active/stopped/approved fate not established; do not classify as failure.')
 if g['research_depth']=='registry_identity_and_entry_review_only':g['remaining_checks'].append('External asset-history research still required; registry-only mapping is not outcome adjudication.')
 programs.append(g)
 for cid in g['candidate_ids']:
  dispositions.append({'candidate_id':cid,'program_id':g['program_id'],'asset':a,'indication':d,'disposition':g['eligibility'],'reason':g['eligibility_reason'],'confidence':g['eligibility_confidence'],'status':g['status'],'priority_bucket':cid in g['priority_candidate_ids'],'adjudication_date':ASOF})
programs.sort(key=lambda x:(x['indication'],x['asset']))
summary={'as_of':ASOF,'scope':'All272 priority_early_industry buckets assigned to systemic/hematology/immune plus all2010–2024 industry-linked HAE/PNH buckets, including later-phase discovery aliases. Finite panel subset, not whole drug-development universe.','candidate_bucket_count':len(C),'priority_bucket_count':sum(priority(c) for c in C),'program_identity_rows':len(programs),'status_counts':dict(Counter(g['status'] for g in programs)),'eligibility_counts':dict(Counter(g['eligibility'] for g in programs)),'HAE_PNH_frame_status':dict(Counter(g['status'] for g in programs if g['in_finite_HAE_PNH_reference_frame'])),'zero_enrollment_withdrawn_programs':sum(g['never_dosed_boundary'] for g in programs),'only_mapped_trials_zero_enrollment_rows':sum(g['only_mapped_trials_zero_enrollment_withdrawn'] for g in programs),'limits':['All candidate IDs have an auditable disposition; mapping completeness is not historical program-universe completeness.','Most non-HAE/PNH programs have registry identity review only; external outcome research unfinished.','Healthy-volunteer starts omitted by disease search and later-indication/combination entries can bias denominator.','Approval endpoint must be specified: China-only approval is not FDA success.','Closed-case success fractions would be upward biased by selective outcome resolution and right censoring.','No fitted lifetime probability or unbiased broad PoS estimate is claimed.']}
(P/'data/pos_adjudication/systemic_programs.json').write_text(json.dumps(programs,indent=2,ensure_ascii=False)+'\n')
(P/'data/pos_adjudication/systemic_dispositions.json').write_text(json.dumps(dispositions,indent=2,ensure_ascii=False)+'\n')
(P/'data/pos_adjudication/systemic_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
assert len(dispositions)==len(C)==len({r['candidate_id'] for r in dispositions})
assert all(any(r['candidate_id']==c['candidate_id'] for r in dispositions) for c in C if priority(c))
print(json.dumps(summary,indent=2))
