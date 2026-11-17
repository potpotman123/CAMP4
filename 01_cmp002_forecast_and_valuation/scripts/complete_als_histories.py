"""Source-backed second-pass ALS updates; frozen first-pass records are untouched."""
import json,re
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/'data/pos_completion';D.mkdir(exist_ok=True)
base=json.loads((P/'data/pos_adjudication/integrated_program_ledger.json').read_text())
rows={r['asset']:{'id':r['id'],'canonical_asset':r['asset'],'disposition':'provisional','disposition_reason':'First clinical study identified; global first exposure and commercial-program qualification still reviewed individually.','entry_date':r['entry_proxy'],'entry_precision':'registry_start_proxy','outcome':r['status'],'outcome_date':r['source_record'].get('event_date'),'last_verified_active_date':r['source_record'].get('last_verified_active_date'),'evidence':list(r['sources']),'searches':[],'remaining_uncertainty':[],'review_complete':False} for r in base if r['family']=='als' and r['reference_eligibility']!='excluded'}
def upd(a,**kw):rows[a].update(kw)
def ev(a,url,claim,date=None):rows[a]['evidence'].append({'url':url,'claim':claim,'source_date':date})
def qualify(a,date,url,claim):upd(a,disposition='include',disposition_reason='Primary first-human/initial clinical-program evidence establishes2010–2024 entry window; exact dosing day may remain approximate.',entry_date=date,entry_precision='month' if len(date)==7 else 'year' if len(date)==4 else 'day_proxy');ev(a,url,claim)
def exclude(a,why,url):upd(a,disposition='exclude',disposition_reason=why);ev(a,url,why)
def active(a,date,url,claim='Sponsor confirms ongoing development; no approval implied.'):
 upd(a,outcome='ongoing',last_verified_active_date=date);ev(a,url,claim,date)
# Correct inaccurate inferred product labels from the first pass.
upd('autologous_BM_stem_cells_Corestem_2010',canonical_asset='TCA Cellular Therapy autologous bone-marrow cells',outcome='suspended_funding')
ev('autologous_BM_stem_cells_Corestem_2010','https://clinicaltrials.gov/study/NCT01082653','Sponsor is TCA Cellular Therapy, not Corestem. Suspended for lack of funding; enrolled-patient and registration-intent evidence unresolved.','2014-05-09')
rows['autologous_BM_stem_cells_Corestem_2010']['remaining_uncertainty'].append('FDA2011 warning letter indicates off-protocol cell administration; cannot presume clean commercial first-dose inception.')
exclude('Spirit1','Food-supplement combination; WITHDRAWN with actual enrollment0. Not a clinical therapeutic-drug entrant.','https://clinicaltrials.gov/study/NCT02588807')
exclude('AMDX2011P','Investigational retinal diagnostic tracer, not a therapeutic program.','https://clinicaltrials.gov/study/NCT05542576')
exclude('VM202','Prior human critical-limb-ischemia trial began March2007; ALS2014 is a later indication.','https://cdn.clinicaltrials.gov/large-docs/86/NCT01475786/Prot_000.pdf')
exclude('IC14','Human endotoxin study published2001; laterALS study is not novel-molecule inception.','https://pubmed.ncbi.nlm.nih.gov/11207321/')
exclude('TCD601','Siplizumab/MEDI507 had phaseII psoriasis human results by2001; ALS2024 is repurposing.','https://www.sec.gov/Archives/edgar/data/873591/000087359101500044/f8kclinicaltrialenrollment.htm')
exclude('monepantel','Monepantel/PPL1 first-in-man cancer study completed2015 before ALS2022; retain only later-indication sensitivity.','https://pharmaust.com/wp-content/uploads/2016/01/160129_Appendix-4C-Quarterly-Report-Company-Update.pdf')
exclude('MaaT033','First treated AML patient reported November2020; ALS2023 is later indication.','https://www.maatpharma.com/maat-pharma-treats-first-acute-myeloid-leukemia-patient-in-phase-1-clinical-trial-to-evaluate-capsule-formulation-of-microbiome-restoration-biotherapeutic/')
exclude('HK-001','Same active moiety(Z)-n-butylidenephthalide was clinically administered as Cerebraca wafer in glioma from November2017; ALS oral formulation is a later exposure.','https://pmc.ncbi.nlm.nih.gov/articles/PMC8870243/')
ev('HK-001','https://clinicaltrials.gov/study/NCT03651349','HK001 active ingredient explicitly(Z)-n-butylidenephthalide; formulation/route differs from glioma wafer.')
qualify('ISIS333611','2010-03','https://pmc.ncbi.nlm.nih.gov/articles/PMC3712285/','Original first-in-human SOD1-ASO trial enrolled March2010–December2011; molecule distinct from later tofersen.')
rows['ISIS333611']['remaining_uncertainty'].append('Secondary review says discontinued but no primary explicit cessation date found; do not use tofersen approval as this molecule success.')
qualify('NurOwn','2011-06','https://www.sec.gov/Archives/edgar/data/1137883/000114420419017041/tv512716_10k.htm','Sponsor10K explicitly identifies first-in-human trial initiated June2011.')
qualify('NP001_sodium_chlorite','2010','https://pmc.ncbi.nlm.nih.gov/articles/PMC5524125/','Original PhaseI trial publication confirms32participants received NP001/placebo in2010.')
active('NP001_sodium_chlorite','2025-07-28','https://www.neuvivo.com/news','Sponsor announces FDA-aligned development pathway;2024 NDA submission is not approval.')
qualify('GDC-0134','2016-05-31','https://pmc.ncbi.nlm.nih.gov/articles/PMC8791798/','Original first-in-human publication linksNCT02655614; actual clinical trial start proxyMay2016. Safety development discontinuation explicit.')
qualify('DNL747','2018-03','https://www.sec.gov/Archives/edgar/data/1714899/000119312518086714/d518262dex991.htm','Sponsor confirms first-in-human dosingMarch2018 healthy volunteers, earlier than ALS-specific trial.')
qualify('AP-101','2019-10','https://tvm-capital.com/neurimmune-and-tvm-capital-life-science-announce-the-initiation-of-al-s-pharmas-phase-1-study-of-ap-101-for-the-treatment-of-als/','Joint developer announcement identifies initial PhaseI first patientOctober2019.')
qualify('ORT247','2022-06-06','https://clinicaltrials.gov/study/NCT06769620','Sponsor record explicitly first-in-human; actual44enrolled, trial2022–2023. Current asset fate not inferred from completion.')
qualify('SPG302','2023-07','https://spinogenix.com/press-release/spinogenix-announces-second-grant-award-from-u-s-department-of-defense-to-further-advance-spg302-the-first-synaptic-regenerative-drug-to-treat-amyotrophic-lateral-sclerosis-als/','Sponsor first human clinical studies initiatedJuly2023; healthy volunteers precede patients.')
ev('SPG302','https://clinicaltrials.gov/study/NCT05882695','Explicit first-in-human registry trial; actualcompleted2025.')
active('prosetin','2026-06-16','https://projenx.com/projenx-announces-a-development-update-for-prosetin-a-first-in-class-cns-penetrant-map4k-inhibitor/','Fully enrolled41patient PhaseIb; continuing development confirmed.')
active('CK0803','2026-08-25','https://www.prnewswire.com/news-releases/cellenkos-receives-fda-fast-track-designation-for-ck0803-in-amyotrophic-lateral-sclerosis-als-302859365.html','Sponsor states trial continues, six evaluable patients; FastTrack is notapproval.')
active('AstroRx','2026-11-15','https://www.sec.gov/Archives/edgar/data/1783036/000121390026101419/ea030514101ex99-2.htm','NewCelX sponsor filing retains AstroRx clinical-stage ALS platform-validation asset. Website-crawl date is not event date; current clinical enrollment not asserted.')
rows['AstroRx']['last_verified_active_date']=None
rows['AstroRx']['outcome']='retained_asset_activity_unclear'
upd('AMT-162',outcome='stopped_safety_efficacy',outcome_date='2026',outcome_date_precision='year_disclosure_upper_bound')
ev('AMT-162','https://cdn.craft.cloud/fe68e1a2-b284-4f69-ba29-921f065edf17/assets/uploads/uniQure-2026-Proxy-Statement.pdf','Sponsor2026proxy explicitly discontinued followingEPISOD1 efficacy/safety review. Five treated patients remain in safetyfollowup; active registry status does not mean development continues.','2026')
ev('FLX-787','https://www.sec.gov/Archives/edgar/data/1615219/000161521916000118/flks2015123110-k.htm','Sponsor reports human volunteer exposure2015, earlier than2017ALS trial. Prior benigncramp studies and naturalcompound/formulation history make de-novo ALS entry boundary uncertain.','2016')
upd('FLX-787',entry_date='2015',entry_precision='year',disposition='provisional')
ev('IPL344','https://immunitypharma.com/images/publications/muscle_and_nerve_-_2025_-_gotkine_-_akt_activation_with_ipl344_treatment_for_amyotrophic_lateral_sclerosis_first_in_human_1.pdf','Original first-in-human paper includes prior compassionate use; preserve earlier exposure boundary and supply-suspended followup rather than permanentfailure.','2025')
ev('CuATSM','https://www.als-mnd.org/support-for-pals-cals/drugs-no-longer-development/cuatsm/','Patient alliance directly reports unsuccessful attempts to obtain trialresults and relabels no-longer-development. This is direct operational observation of silence, not sponsor-confirmed terminal outcome.')
upd('CuATSM',outcome='unresolved_lost_followup')
ev('MNC_Hanyang','https://pmc.ncbi.nlm.nih.gov/articles/PMC7105864/','NCT02286011 is Spanish intramuscular bone-marrow mononuclearcell research, not Hanyang product. Registry name collision withNCT04849065 requires separate study/product identity.')
upd('MNC_Hanyang',canonical_asset='Unresolved mononuclear-cell product grouping',disposition='unknown',disposition_reason='Generic MNC term combined distinct programs; no independent commercial product denominator until split and qualified.')
ev('MSC3P','https://www.clinicaltrialsregister.eu/ctr-search/search?query=2011-000362-35','Bioinova AMSC-ALS001 initial study registered2012; actual26enrolled inNCT03828123. Current commercial program fate not established.')
ev('Whartons_jelly_MSCs','https://clinicaltrials.gov/study/NCT04651855','ALSTEM actual20enrollment, sponsorPBKM, currentrecordstaleMay2022; no productwide terminal conclusion.')
ev('RJK002','https://stcsm.sh.gov.cn/cmsres/f3/f3866e591bb94f689bc93866d06bc52d/5cde4bccb7e07a4a330f8ea50e63233e.pdf','Shanghai government2024funding identifies sponsorRJKALS PhaseI program2024–2027; supports registration-directed development but not approval.','2024')
active('FHND1002','2026-04-29','https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0429/2026042901635.pdf','Sponsorannualreport retains FHND1002 ALS underresearch; separateHV study2024start vs regulatoryDecember2024preIND label requires entry-date check.')
# Further entry corrections from sponsor first-human reports and original publications.
qualify('prosetin','2022','https://projenx.com/projenx-announces-first-person-dosed-in-phase-1-study-of-prosetin/','March1,2022 first-dose announcement plus actual February2022 registry start; retain year precision rather than equate announcement with dosing day.')
qualify('VRG50635','2022-10','https://vergelabs.com/resources/news/','Sponsor timeline states first-in-human dosing October31,2022; registry-only2024 dates missed European trial.')
ev('VRG50635','https://www.isrctn.com/ISRCTN14792372','Independent registry describes first-in-human study2022-002747-22.')
qualify('QRL-101','2022-12','https://www.quralis.com/news/','January5,2023 initial human dosing announcement; actual December22,2022 initial-study start supports December entry.')
ev('QRL-101','https://clinicaltrials.gov/study/NCT05667779','Initial healthy-volunteer single ascending dose trial precedes ALS-specific studies.')
qualify('SAR443820','2020-12','https://www.sec.gov/Archives/edgar/data/1714899/000171489921000033/dnli-20201231.htm','Sponsor explicitly first patient dosed December2020, not November registry enrollment.')
qualify('BIIB100','2019','https://www.hopkinsmedicine.org/neurology-neurosurgery/clinical-trials/als-clinical-trials/completed-trials','Investigator identifies study as first-in-human;2019 registry start. Sponsor transferred IND-ready KPT350 to Biogen in2018.')
qualify('AstroRx','2018','https://pmc.ncbi.nlm.nih.gov/articles/PMC9927047/','Original first-in-human report plus actual2018 initial study; three-month run-in means enrollment date is not first injection.')
qualify('IPL344','2014-12-01','https://immunitypharma.com/news/5-immunity-pharma-announces-passing-a-two-year-mark-for-treating-an-als-patient-with-ipl344-under-a-compassionate-treatment-protocol','Sponsor explicitly dates initial compassionate human treatment December1,2014, before formal2018 study.')
rows['IPL344']['remaining_uncertainty'].append('Compassionate first exposure used for primary first-human clock; formal trial-entry sensitivity is2018.')
qualify('AMT-162','2024-10','https://www.sec.gov/Archives/edgar/data/1590560/000155837024013276/qure-20241015xex99d1.htm','Sponsor first-patient-dosing announcement October2024; earlier registry start measured enrollment.')
qualify('ALN-SOD','2024','https://clinicaltrials.gov/study/NCT06351592','Explicit first-in-human trial, actual August2024 start; exact injection day not separately established.')
for a in ['MSC3P','Whartons_jelly_MSCs','FB418','RJK002','NP001_regulatory_Tcells','CK0803','FHND1002','CuATSM','FLX-787','autologous_BM_stem_cells_Corestem_2010']:
 rows[a]['disposition']='unknown'
 rows[a]['disposition_reason']='Named human-study history reviewed, but global first exposure, product identity, or original rare-indication development intent is not sufficiently established for strict inclusion; retained in entry-uncertainty sensitivity.'
 rows[a]['remaining_uncertainty'].append(rows[a]['disposition_reason'])
for a in ['FB418','RJK002','NP001_regulatory_Tcells','CK0803']:
 rows[a]['entry_precision']='registry_start_proxy'
# Independent second review of six critical ALS histories.
support=D/'neuro_als_support.json'
if support.exists():
 for v in json.loads(support.read_text()):
  a=next(k for k,r in rows.items() if r['id']==v['id']);r=rows[a]
  for k in ['disposition','disposition_reason','outcome','outcome_date','aliases','flags']:
   if k in v:r[k]=v[k]
  r['entry_date']=v.get('first_human_date',r['entry_date']);r['entry_precision']=v.get('first_human_date_precision',r['entry_precision'])
  iv=v.get('first_human_interval')
  if isinstance(iv,dict):r['entry_interval']=[iv['lower'],iv['upper']]
  r['entry_window_qualified']=r['disposition']=='include'
  r['evidence']+=v.get('first_human_evidence',[])+v.get('outcome_evidence',[])
  r['searches']+=v.get('searches',[])
# Search provenance references retrieved packets. Never label a completed search as a resolved fact.
for a,r in rows.items():
 r['prior_registry_sources']=['https://clinicaltrials.gov/study/'+n for b in base if b['id']==r['id'] for n in b['trial_ids']]
 r['prior_record_file']='data/pos_adjudication/als_program_ledger.json'
 raw=P/'sources/pos_completion'/('als_history_'+a+'.json')
 if raw.exists():
  q=json.loads(raw.read_text()); r['searches'].append({'type':'all_indications_alias_registry_search','source_file':str(raw.relative_to(P)),'studies':len(q.get('studies',[])),'next_page':bool(q.get('nextPageToken'))})
  r['registry_snapshot_files']=[str(raw.relative_to(P))]
 r['searches'].append({'type':'primary_source_and_outcome_review','source_files':['sources/pos_completion/completion_als_*.json'],'note':'Queries and retrieved results retained in numbered packets; claim-specific sources are in evidence.'})
 r['review_complete']=True
 r['FDA_ever_approved']=True if a=='tofersen' else None
 r['FDA_approval_date']='2023-04-25' if a=='tofersen' else None
 r['FDA_ascertainment_basis']='Central FDA inventory reconciliation required; absent approval is not presumed from unknown development status.'
(D/'als_updates.json').write_text(json.dumps(list(rows.values()),indent=2)+'\n')
print('Saved',len(rows),'ALS reviewed histories; unresolved facts remain explicitly marked')
