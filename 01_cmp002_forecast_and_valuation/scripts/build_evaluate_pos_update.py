"""Audited overlay; preserves all frozen public-source datasets. Finite horizons only."""
import json,datetime as dt,collections,hashlib,runpy,contextlib,io,ast
from pathlib import Path
P=Path(__file__).resolve().parents[1]; O=P/'data/evaluate_audit'
def read(f):return json.loads((P/f).read_text())
old=read('data/pos_censoring_analysis/observations.json'); matches=read('data/evaluate_audit/matched_310.json'); mi={r['cluster']:r for r in matches}
failed='actus101 aes103 agt181 agt182 bmn307 bn82451b chf6333 glpg2451 glpg2737 hepastem hs135 ipl344 mk8892 nktt120 pf07209326 ptw00210mgggel saer sar443809 scd101 shp623 spk3006'.split()
active='airdnase astrorx blsm22 hg302 mbf015 ort247 pbgm01 sanguinate sln124'.split()
unknown_notes={
'bay1237592':'Evaluate confirms Phase III pulmonary hypertension, not the original PAH subtype. Preserve indication-scope uncertainty.',
'frespaciguat':'Phase III pulmonary hypertension does not itself establish continued PAH development; preserve original subtype question.',
'can103':'Marketed WW does not establish FDA approval or an active US registration pathway.',
'ciprocopan':'Approved WW but no established FDA approval/pathway in export. Foreign approval is not FDA success.',
'gc1111':'Hunterase is marketed outside USA; USA endpoint and pathway uncertainty remains.',
'verenafusp':'Phase III vendor status does not resolve original geographic/FDA-path uncertainty.',
'prx112':'Conflicting vendor WW Marketed / USA Abandoned Phase II. Oral PRX112 must not inherit injectable taliglucerase approval. Preserve unknown molecule fate.',
'cellavitahd':'No accepted Evaluate identity match in two exports. No-match is not failure.',
'geneticallycorrectedculturedepidermalautograftatmp':'No accepted Evaluate identity match. Do not substitute a different epidermal-cell construct.',
'globinrestoredautologoushsc':'No accepted Evaluate identity match for the specific Bioray construct.'}
changes=[]; obs=json.loads(json.dumps(old))
for r in obs:
 c=r['cluster']; st=r['status']; reason=None
 if c in failed:r['status']='failed';reason='Evaluate indication-specific abandoned status, after consolidating sponsor transfers. Vendor-supported disposition; not independently dated biological failure.'
 if c in active:r['status']='active';reason='Evaluate retains an active clinical phase for the qualifying indication under at least one continuing holder. Vendor status, not evidence of recent patient dosing.'
 if c=='abo101':r['status']='active';reason='Sangrail May 2026 launch identifies SNG-101 as former ABO-101; same original molecule revived, not a distinct successor. Prior terminal-failure classification corrected.'
 if c=='glpg3067':r['status']='active';reason='Sionna 2025 annual report and 2024 licensing release explicitly retain SION-3067/ABBV-3067. Old regimen termination did not establish molecule failure.'
 if c=='glpg2451':r['assets']=['GLPG2451'];reason+=' Prior asset label navocaftor was wrong: navocaftor is GLPG3067/SION-3067. NCT02788721 and NCT03540524 confirm the 2451 identity.'
 if c in unknown_notes:reason=unknown_notes[c]
 if reason:
  if st!=r['status']:r['confidence']='primary_corroborated' if c in ['abo101','glpg3067'] else 'vendor_supported'
  changes.append(dict(cluster=c,old_status=st,new_status=r['status'],reason=reason,evaluate_product_ids=mi[c]['evaluate_product_ids'],evidence_level=r['confidence'],source_rows='matched_310.json#'+c))
# Explicit source-linked additions. Broad date intervals are retained, not fabricated exact dosing days.
base='https://clinicaltrials.gov/study/'
adds=[
 dict(cluster='otl201',assets=['OTL-201'],pid='33103',indication='MPS IIIA',entry=['2019-01-01','2019-12-31'],status='active',strict=True,cns=True,sources=['https://ir.orchard-tx.com/static-files/d5ef6271-34a9-4556-9e4d-40847bd0f0ff',base+'NCT04201405'],note='2019 Specials-license first treated child predates 2020 formal study. Same technology/procedures per sponsor; formal trial clock shown separately in source.'),
 dict(cluster='axoaavgm1',assets=['AXO-AAV-GM1 / AAV9-GLB1'],pid='65569',indication='GM1 gangliosidosis',entry=['2019-05-01','2019-05-16'],status='active',strict=True,cns=True,sources=['https://www.clinicalleader.com/doc/axovant-dosing-first-patient-clinical-program-axo-aav-gm-a-novel-gene-therapy-gm-gangliosidosis-0001',base+'NCT03952637'],note='Sponsor first-dose May 2019 release overrides later formal registry start. Academic trial continues despite sponsor exit; distinct from LYS-GM101/PBGM01.'),
 dict(cluster='rgx181',assets=['RGX-181 / TTX-181'],pid='64653',indication='CLN2 Batten CNS',entry=['2022-01-01','2022-12-20'],status='active',strict=True,cns=True,sources=['https://www.prnewswire.com/news-releases/regenxbio-reports-update-on-advancement-of-programs-for-cln2-disease-301707881.html'],note='Sponsor confirms first treated child in Brazil by Dec20 2022; year interval rather than release date as dosing day. Vendor identifies Tern continuation.'),
 dict(cluster='pbkr03',assets=['PBKR03'],pid='200250',indication='Krabbe disease',entry=['2022-03-01','2022-03-10'],status='unknown',strict=True,cns=True,sources=['https://www.sec.gov/Archives/edgar/data/1787297/000110465922032216/tm228752d1_8k.htm',base+'NCT04771416'],note='First dosing March2022; current registry suspended/company-strategy stop despite Gemma transfer and vendor PhaseII. Restart versus terminal exit unresolved; not automatically active or failed.'),
 dict(cluster='tsha101',assets=['TSHA-101'],pid='201222',indication='GM2 gangliosidosis',entry=['2021-03-12','2021-12-31'],status='active',strict=False,cns=True,sources=[base+'NCT04798235','https://ir.tayshagtx.com/news-releases/news-release-details/taysha-gene-therapies-announces-positive-initial-biomarker-data/','https://ir.tayshagtx.com/news-releases/news-release-details/taysha-gene-therapies-provides-update-deprioritized-pipeline'],note='Registry actual start lower bound, treated-patient data establish exposure2021. Rights returned to Queens2024; ongoing clinical follow-up does not prove new dosing/commercial advancement.'),
 dict(cluster='fbx101',assets=['FBX-101'],pid='204820',indication='Krabbe disease',entry=['2021-01-04','2022-03-03'],status='failed',strict=False,cns=True,sources=['https://www.forgebiologics.com/press-fda-clearance-of-investigational-new-drug-for-patients-with-krabbe-disease/','https://www.forgebiologics.com/forge-reports-positive-clinical-data-on-brain-development-and-motor-function-from-the-reskue-novel-phase-1-2-gene-therapy-trial-in-patients-with-krabbe-disease-at-the-ssiem-annual-symposium/','https://alextlc.org/wp-content/uploads/2025/03/2025-Forge-Update-to-the-Krabbe-Community.pdf',base+'NCT06308718'],note='Bound between IND clearance and180days before Aug30 2022 data release. Jan28 2025 sponsor discontinuation overrides vendor PhaseII. Exact first-dose date unknown.'),
 dict(cluster='tsha118',assets=['TSHA-118 / ABO-202'],pid='47134',indication='CLN1 Batten',entry=['2021-12-16','2024-02-15'],status='unknown',strict=False,cns=True,sources=['https://ir.tayshagtx.com/news-releases/news-release-details/taysha-gene-therapies-announces-initiation-clinical-development/','https://bdfa-uk.org.uk/node/447','https://ir.tayshagtx.com/news-releases/news-release-details/taysha-gene-therapies-provides-update-deprioritized-pipeline','https://investors.abeonatherapeutics.com/sec-filings/all-sec-filings/content/0001493152-26-019156/0001493152-26-019156.pdf'],note='Treatment confirmed by Feb2024;2021 clinical-start announcement is NOT dosing. Feb2026 license termination, but potential academic continuation uncertain. Broad date interval; exclude in stronger-entry sensitivity.'),
 dict(cluster='rgx381',assets=['RGX-381 / TTX-381'],pid='210653',indication='CLN2 ocular manifestations',entry=['2023-01-01','2023-08-02'],status='active',strict=True,cns=False,sources=['https://regenxbio.gcs-web.com/news-releases/news-release-details/regenxbio-reports-second-quarter-2023-financial-results-and/'],note='Subretinal ocular therapy: include broad rare tier only, not CNS-directed comparator. Shared vector/gene with RGX181; combined-cluster sensitivity required.')]
cut=dt.date(2026,11,16)
def make(a):
 lo,hi=map(dt.date.fromisoformat,a['entry']);mid=lo+(hi-lo)//2
 return dict(cluster=a['cluster'],assets=a['assets'],status=a['status'],confidence='source_reviewed',flags=dict(rare=True,genetic_cns=a['cns'],genetic_medicine=True,intrathecal=False,protein_restoration=True,neurodevelopmental=False),strict_entry=a['strict'],closest4=False,entry_interval=a['entry'],entry_midpoint=str(mid),entry_year=mid.year,endpoint_date=str(cut),approval=False,time=(cut-mid).days/365.25,time_early_entry=(cut-lo).days/365.25,time_late_entry=(cut-hi).days/365.25,unknown_types=['restart_or_continuation_uncertain'] if a['status']=='unknown' else [],family='neuro',evidence=a)
# Same AAV9/TPP1 pair delivered to different tissues: conservatively one cluster
# until distinct construct identity is demonstrated. Keep split-program sensitivity.
obs+=list(map(make,[a for a in adds if a['cluster']!='rgx381']))
# Reuse only the prior estimator functions (AST), avoiding execution/mutation of frozen outputs.
code=ast.parse((P/'scripts/analyze_censoring_adjusted_pos.py').read_text()); keep=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name in ['estimate','fit']]
import numpy as np
ns={'np':np,'HORIZONS':[3,5,8,10,12],'SEED':20261118};exec(compile(ast.Module(body=keep,type_ignores=[]),'prior_estimator_functions','exec'),ns)
tiers={'R1_rare':lambda r:True,'R2_genetic_CNS':lambda r:r['flags']['genetic_cns'],'R3_genetic_medicine_CNS':lambda r:r['flags']['genetic_cns'] and r['flags']['genetic_medicine'],'R4_closest_restoration_ASO':lambda r:r['closest4']}
def results(rows):
 out={}
 for k,pred in tiers.items():
  rs=[r for r in rows if pred(r)];out[k]=dict(n=len(rs),status_counts=dict(collections.Counter(r['status'] for r in rs)),main=ns['fit'](rs,True),recent_2015plus=ns['fit']([r for r in rs if r['entry_year']>=2015]),stronger_entry=ns['fit']([r for r in rs if r['strict_entry']]))
 return out
res=results(obs);res_merge=results(obs+[make(next(a for a in adds if a['cluster']=='rgx381'))])
# Registry-observed entrants previously outside qualified panel: sensitivity only; not newly proven first dosing.
proxy=[]
for c,d in [('anb004','2023-02-02'),('skg0201','2023-06-25'),('er2001','2023-04-04')]:
 a=dict(cluster=c,assets=[c.upper()],entry=[d,d],status='active',strict=False,cns=True,note='Registry actual initial observed entry proxy; earlier exposure/construct uncertainty remains. Previously among43 outside qualified panel.')
 proxy.append(make(a))
res_proxy=results(obs+proxy)
for name,data in [('status_decisions',changes),('qualified_additions',adds),('updated_observations',obs),('updated_results',dict(evidence_review_date='2026-11-18',comparison_cutoff='2026-11-16',baseline=results(old),updated=res,separate_rgx181_rgx381_programs=res_merge,include_three_registry_entry_proxies=res_proxy,limitations=['Targeted high-relevance expansion, not complete census of9515vendorproducts','Vendor dispositions separated from primary corroboration','Unresolved identities and dates not forced into denominator','No automatic classification of vendor PhaseI as dosed','Finite-horizon cumulative FDA approval, not lifetime or preclinical PoS']))]: (O/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
assert len(obs)==317 and len({r['cluster'] for r in obs})==317
assert sum(r['approval'] for r in obs)==42
assert [res[k]['n'] for k in tiers]==[317,88,55,4]
assert len([r for r in changes if r['old_status']=='unknown'])==40
assert all(mi[c]['matched_rows'] for c in failed+active)
for r in obs:assert 0<=r['time'] and r['time_late_entry']<=r['time']<=r['time_early_entry']
# Status updates alone cannot alter finite-horizon nonapproval observations.
for k,p in tiers.items():assert ns['estimate']([r for r in old if p(r)])==ns['estimate']([r for r in obs[:310] if p(r)])
(O/'validation.json').write_text(json.dumps(dict(passed=True,checks=['317unique/42approvals','nested317/88/55/4','all40unknowns assigned explicit decisions','all accepted status updates have source rows','entry bounds ordered','status-only finite-horizon invariance','RGXshared-construct and three entry-proxy sensitivities'],source_sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (P/'sources/evaluate_2026-11-18').glob('*.csv')}),indent=2)+'\n')
for k,r in res.items():print(k,r['n'],r['status_counts'],[(x['years'],round(x['estimate']*100,2) if x['estimate'] is not None else None) for x in r['main']['horizons']])
print('oldunknown decisions',collections.Counter(r['new_status'] for r in changes if r['old_status']=='unknown'))
