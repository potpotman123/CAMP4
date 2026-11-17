"""Reproducible completion layer; frozen adjudication is not overwritten.
Dates below are exposure intervals, not automatic conversions of enrollment dates.
"""
import json, re, calendar
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parents[1]
Q = json.loads((ROOT/'data/pos_completion/metabolic_research_queue.json').read_text())
SRC = ROOT/'sources/pos_completion'
CUTOFF='2026-11-16'
ENTRY={}; STATUS={}; EXCLUDE={}; EXTRA={}

def entry(slug, lo, hi, note, url=None, confidence='documented_exposure_interval'):
    ENTRY[slug]={'interval':[lo,hi], 'note':note, 'url':url, 'confidence':confidence}
def status(slug, state, date, note, url=None):
    STATUS[slug]={'state':state,'date':date,'note':note,'url':url}
def exclude(slug,reason): EXCLUDE[slug]=reason
def extra(slug,**kw): EXTRA.setdefault(slug,{}).update(kw)

# Earliest human exposure / first clinical series. Month and year precision
# deliberately remain intervals. Trial dates only bound actual dosing when
# a publication, results report or sponsor statement establishes exposure.
entry('gc1111','2010-05','2011-03','First phase I/II study treated 31 patients in the 2010–2011 registry interval; original subsequent trial report identifies the early treated study. Exact first dose not established.','https://www.gimjournal.org/article/S1098-3600%2825%2900107-8/fulltext')
entry('rhhns','2010-08','2010-12','Sponsor describes first phase I/II initiation August 2010; completed treated early trial supports 2010 entry, without an exact day.','https://www.sec.gov/Archives/edgar/data/936402/000095010315001422/dp53559_10k.htm','first_trial_year_supported')
entry('idursulfase_it','2010-08','2010-12','Intrathecal first clinical series began 2010; this is a new route of a molecule already FDA approved intravenously in 2006.','https://www.clinicaltrialsregister.eu/ctr-search/trial/2011-000212-25/results')
entry('bmn701','2011-01','2011-12','Sponsor reports initial phase I/II beginning January 2011 and subsequent treated patient results.','https://investors.biomarin.com/files/doc_financials/2014/q4/Fourth-Quarter-2014-10K.pdf','first_trial_year_supported')
entry('saer','2010-11','2011-12','PMDA review documents Japanese first clinical development beginning November 2010, predating US phase I 2011. Prior supplement/free sialic-acid exposure is a formulation sensitivity.','https://www.pmda.go.jp/files/000273006.pdf')
entry('saf301','2011-08','2011-12','Four-child initial intracerebral clinical series is documented in the research-funder 2011 annual report; distinguish SAF301 from later SAF302 vector.','https://fondation-sanfilippo.ch/wp-content/uploads/2023/12/Rapport-Annuel-2011.pdf')
entry('hepastem','2012-03','2012-03','Sponsor presentation hosted by Belgian regulator states first patient March 2012 in mixed UCD/Crigler-Najjar pediatric program.','https://www.afmps.be/sites/default/files/content/WTA/4_vinciane_wouters_-_promethera_biosciences_-_experience_of_a_belgian_sme.pdf')
entry('prx102','2012-12','2012-12','Sponsor SEC disclosure places initial PRX102 clinical treatment in December 2012 rather than registry October initiation.','https://www.sec.gov/Archives/edgar/vprr/1300/13003490.pdf')
entry('gc1119',None,None,'Registry shows completed 2012–2015 early study but no independent dosing history or identity successor was recovered after registry/alias/sponsor searches. Enrollment is not a first-dose date.',confidence='unresolved_after_research')
entry('pro045','2013-01','2015-12','Original EU trial results and CORDIS final report establish treated first phase I/II cohort in this bounded trial interval; precise initial dose remains unknown.','https://cordis.europa.eu/project/id/601573/reporting/es')
entry('vts270','2013-01','2013-12','Initial NIH intrathecal adrabetadex study treated patients in 2013. Hydroxypropyl-beta-cyclodextrin compassionate-use/product identity before this formulation is a sensitivity, not silently ignored.','https://clinicaltrials.gov/study/NCT01747135','first_trial_year_supported')
entry('prx112','2013-03','2013-04-04','Sponsor April 2013 report documents initial oral PRX112 clinical treatment.','https://www.sec.gov/Archives/edgar/data/1006281/000114420413019478/v340222_ex99-1.htm')
entry('ht100','2001-08','2004-02','Original halofuginone oncology phase I treated patients August 2001–February 2004, before the DMD formulation.','https://pubmed.ncbi.nlm.nih.gov/16815702/')
entry('pro053','2013-06','2015-12','First dose-escalation treated subjects established in EU results; calendar interval conservatively spans initial trial through treated-study follow-up.','https://www.clinicaltrialsregister.eu/ctr-search/trial/2011-005042-35/results')
entry('viltolarsen','2013','2013','FDA clinical pharmacology review identifies Japanese initial phase I study NS-065/NCNP-01 in 2013.','https://www.accessdata.fda.gov/drugsatfda_docs/nda/2020/212154Orig1s000ClinPharmR.pdf','first_trial_year_supported')
entry('vp20629','2005-12-01','2005-12-01','Intellect SEC history explicitly states OX1 entered human phase I December 1, 2005; later 2013 Friedreich trial is not inception.','https://www.sec.gov/Archives/edgar/data/1337905/000114420411057726/v237158_10k.htm','explicit_first_human_date')
entry('avalglucosidase','2013-08','2015','Original NEO1 treated first clinical study begins 2013; FDA review/early trial results bound exposure rather than imply precise enrollment day was dosing.','https://clinicaltrials.gov/study/NCT01898364')
entry('raav25naglu','2013-10','2013-10','uniQure SEC first-human AMT110 / rAAV2/5-hNAGLU history places first treatment October 2013.','https://www.sec.gov/Archives/edgar/data/1590560/000104746914000006/a2217855zex-10_1.htm')
entry('ezutromid','2010-01','2010-01-11','BioMarin announcement January 11, 2010 states first subject initiated BMN195 treatment; Summit formulation studied in 2013 is the same asset.','https://www.biospace.com/biomarin-pharmaceutical-inc-initiates-phase-1-clinical-study-of-bmn-195-for-duchenne-muscular-dystrophy')
entry('ux003','2013','2013','First UX003 clinical/compassionate exposure occurred in 2013; do not treat dates of animal toxicology as human dosing.','https://clinicaltrials.gov/study/NCT01856218','first_trial_year_supported')
entry('oxabact',None,'2006','Sponsor protocol documents OC2 and OC3 clinical experience before OC5, including the original nine-patient study published in 2006. OC5 is process/formulation development of the same bacterial product lineage.','https://cdn.clinicaltrials.gov/large-docs/85/NCT03116685/Prot_000.pdf')
entry('dmpkrx','2014-06','2014-06-09','Sponsor June 9 announcement reports first-in-human dosing in healthy volunteers, preceding December DM1 patient trial.','https://www.prnewswire.com/news-releases/isis-pharmaceuticals-initiates-phase-1-study-of-isis-dmpk-rx-to-treat-myotonic-dystrophy-type-1-262356081.html')
entry('golodirsen','2015-01','2015','FDA review documents treated initial 4053-101 clinical study starting January 2015.','https://www.accessdata.fda.gov/drugsatfda_docs/nda/2019/211970Orig1s000OtherR.pdf','first_trial_year_supported')
entry('sbc103','2015-01','2015','First clinical treated cohort in NCT02350816 began 2015; registry completion/termination is not itself a permanent program failure.','https://clinicaltrials.gov/study/NCT02350816','first_trial_year_supported')
entry('lucerastat','2002-10','2002-12','Retrospectively registered FIH SAD NCT02944487 ran October–December 2002 (39 actual participants); original paper confirms administration. Later 2015 Fabry study is not inception.','https://clinicaltrials.gov/study/NCT02944487')
entry('agt182','2015-04','2015-06','First-in-human treating center Emory reports study underway and first patient in June 2015.','https://news.emory.edu/stories/2015/06/first-man-clinical-trial-hunter-syndrome-underway-emory')
entry('agt181','2015-07','2015-09-02','ArmaGen first patient dosed announcement September 2, 2015 bounds the actual exposure date.','https://www.prnewswire.com/news-releases/armagen-announces-first-patient-dosed-in-phase-12a-clinical-trial-of-agt-181-for-the-treatment-of-hurler-syndrome-300136944.html')
entry('rt001','2015-08','2016','Original RT001 trial presentation reports treated first phase I/II FA cohort in the initial 2015–2016 study. Not Revance botulinum product RT001.','https://www.fagofar.org/wp-content/uploads/2017/10/IARC2017-ABSTRACT-AF1.pdf')
entry('ds5141b','2015-10','2016','First renadirsen / DS5141b clinical study has treated follow-up within 2015–2016; exact dosing date not recovered.','https://clinicaltrials.gov/study/NCT02667483')
entry('casimersen','2015-10','2015','FDA clinical pharmacology review identifies the treated first 4045-101 study in 2015.','https://www.accessdata.fda.gov/drugsatfda_docs/nda/2021/213026Orig1s000ClinPharmR.pdf','first_trial_year_supported')
entry('lumasiran','2016-03','2016','Original first-in-human study paper confirms treated healthy volunteers and PH1 patients in study begun 2016.','https://pmc.ncbi.nlm.nih.gov/articles/PMC8425611/','first_trial_year_supported')
entry('atb200','2016-04','2016','ATB200-02 is initial treated clinical study begun 2016. Miglustat is previously exposed but cipaglucosidase alfa is a new protein active ingredient; retain novel-component combination.','https://cdn.clinicaltrials.gov/large-docs/65/NCT02675465/Prot_000.pdf','first_trial_year_supported')
entry('ax250','2016-04','2016','AX250/BMN250 initial treated MPSIIIB clinical series began 2016.','https://clinicaltrials.gov/study/NCT02754076','first_trial_year_supported')
entry('edasalonexent','2011','2011','SEC identifies CAT1004-101 first-in-human healthy trial (NCT01440166) and subsequent type 2 diabetes trial before DMD.','https://www.sec.gov/Archives/edgar/data/1454789/000091205715000013/filename1.htm','first_trial_year_supported')
entry('abo102','2016-04','2016','ABO102 / UX111 first MPSIIIA treated clinical series began 2016; asset distinct from both Abeona ABO101 and Arbor ABO101.','https://clinicaltrials.gov/study/NCT02716246','first_trial_year_supported')
entry('dcrph1','2016-04','2016-08','Dicerna SEC 2016 update confirms initial clinical dosing by Q2 2016; distinct from successor DCR-PHXC/nedosiran.','https://www.sec.gov/Archives/edgar/data/1399529/000119312516671791/d230319dex991.htm')
entry('aeb1102','2015-10','2015-12','SEC S1 documents seven treated solid-tumor patients after October 2015 initiation, predating 2016 ARG1 study despite later FDA ARG1 review calling that indication study first-in-human.','https://www.sec.gov/Archives/edgar/data/1636282/000119312516518824/d50169ds1a.htm')
entry('mossagal','2016-11','2017','Original first-in-human paper reports actual recombinant moss-aGal treatment in initial 2016–2017 trial.','https://onlinelibrary.wiley.com/doi/full/10.1002/jimd.12052')
entry('jr141','2017-03','2017','First pabinafusp alfa phase I/II Japanese patient study began in 2017; Japanese approval is not FDA approval.','https://clinicaltrials.gov/study/NCT03128593','first_trial_year_supported')
entry('sb913','2017-11-13','2017-11-13','Sponsor explicitly dates first in-vivo genome editing patient treatment November 13, 2017.','https://www.prnewswire.com/news-releases/sangamo-therapeutics-presents-initial-safety-data-from-champions-genome-editing-study-for-mps-ii-at-worldsymposium-300594628.html','explicit_first_human_date')
entry('sb318','2018-01','2018-07-23','Sangamo first-patient announcement July 23, 2018 establishes actual exposure in 2018; 2017 registry initiation precedes dosing.','https://investor.sangamo.com/news-releases/news-release-details/sangamo-announces-treatment-first-patient-phase-12-clinical')
entry('synb1020','2017-06','2017','Initial healthy volunteer exposure 2017, followed by cirrhosis hyperammonemia trial; no verified UCD patient trial.','https://clinicaltrials.gov/study/NCT03179878','first_trial_year_supported')
entry('val1221','2017-06','2017','First treated Pompe study began in 2017; later Lafora compassionate use is a different indication, not continued Pompe development.','https://clinicaltrials.gov/study/NCT02898753','first_trial_year_supported')
entry('dtx301','2017-07','2017','Initial treated OTC deficiency phase I/II began 2017.','https://clinicaltrials.gov/study/NCT02991144','first_trial_year_supported')
entry('abo101','2017-10','2018','Abeona initial MPSIIIB trial NCT03315182 establishes first treated series 2017–2018. Do not conflate Arbor CRISPR drug with the same code (first dosed 2025).','https://clinicaltrials.gov/study/NCT03315182')
entry('nedosiran_ph1','2017-12','2018','Initial DCR-PHXC healthy-volunteer/PH trial PHYOX1 has treated results; bound inception by first study interval.','https://www.clinicaltrialsregister.eu/ctr-search/trial/2017-003534-89/results')
entry('sgt001','2018-02-14','2018-02-14','Sponsor explicitly identifies February 14, 2018 as first SGT001 administration; registry December 2017 is enrollment/setup.','https://investors.solidbio.com/news-releases/news-release-details/solid-biosciences-announces-clinical-hold-sgt-001-phase-iii','explicit_first_human_date')
entry('srp9001','2018-01','2018','FDA briefing and original study 101 results establish first four treated patients in 2018.','https://www.fda.gov/media/169105/download','first_trial_year_supported')
entry('pf06939926','2018-01','2018','Initial Pfizer DMD gene transfer phase Ib treated patients in 2018.','https://clinicaltrials.gov/study/NCT03362502','first_trial_year_supported')
entry('suvodirsen','2018-01','2018','Initial WVE210201 phase I treated cohort in 2018; failed early trials retained.','https://clinicaltrials.gov/study/NCT03508947','first_trial_year_supported')
entry('srp5051','2018-02','2018','2017 SEC statement says study commenced, not patients dosed; actual patient-study start and 2018 treated follow-up support 2018, with 2017–2018 timing sensitivity.','https://www.sec.gov/Archives/edgar/data/873303/000156459018020534/srpt-10q_20180630.htm','first_trial_year_supported')
entry('avrrd01','2017','2017','Avrobio S1 describes earlier Canadian academic treated Fabry cohort in 2017 before 2018 commercial phase II.','https://www.sec.gov/Archives/edgar/data/1681087/000119312518188630/d562006ds1a.htm','first_trial_year_supported')
entry('synb1618','2018-04','2018-04-18','Sponsor announces first subject dosed April 18, 2018. SYNB1934 is a distinct optimized strain, not an alias.','https://investor.synlogictx.com/news-releases/news-release-details/synlogic-doses-first-subject-phase-12a-trial-synb1618-treatment')
entry('idua_lvv','2018-05','2019','Initial OTL203 autologous IDUA-LVV treated eight children in 2018–2019; academic-to-commercial transfer retained as one asset.','https://clinicaltrials.gov/study/NCT03488394')
entry('dtx401','2018-05','2018-07-26','Ultragenyx first patient dosed announcement July 26, 2018.','https://ir.ultragenyx.com/news-releases/news-release-details/ultragenyx-announces-first-patient-dosed-phase-12-study-dtx401')
entry('sobi003','2018-06','2018-08-09','Sponsor announced first patient dosed August 9, 2018.','https://www.sobi.com/sites/sobi/files/pr/201808095897-1.pdf')
entry('actus101','2019-01-22','2019-01-22','AskBio first patient release specifies January 22, 2019 dose, rather than registry December 2018 start.','https://www.askbio.com/first-patient-dosed-with-gene-therapy-in-phase-1-2-study-of-actus-101-in-patients-with-pompe-disease/','explicit_first_human_date')
entry('lyssaf302','2019-01','2019-02-14','Lysogene/Sarepta first patient announcement February 14, 2019 supersedes December 2018 registry start.','https://investorrelations.sarepta.com/news-releases/news-release-details/lysogene-and-sarepta-therapeutics-announce-dosing-first-patient')
entry('rgx111','2020','2020','Earlier single-patient IND treated in 2020 precedes December main-trial first patient.','https://pmc.ncbi.nlm.nih.gov/articles/PMC13239742/','first_trial_year_supported')
entry('trappsol','2009','2009','Sponsor family letter states first compassionate supply/use in 2009, expanded 2010. Formal 2017/2019 trials are not inception.','https://nnpdf.org/wp-content/uploads/2023/06/Cyclo-Letter-to-the-NPC-Community-06.09.2023.pdf','first_trial_year_supported')
entry('avrrd02','2020-01','2020-06','Avrobio June 2020 SEC update establishes first treated patient, later than May 2019 registry opening.','https://www.sec.gov/Archives/edgar/data/1681087/000156459020031761/avro-ex991_6.htm')
entry('cdx6114','2018-07','2018-07-09','Codexis first-subject announcement July 9, 2018; healthy volunteer FIH precedes later registry frame.','https://d1io3yog0oux5.cloudfront.net/_bada3bc6dd3caf7aca66045023b68acc/codexis/news/2018-07-09_Codexis_Doses_First_Subjects_in_Phase_1a_Trial_of__59.pdf')
entry('blsm22','2019-06','2020-03-26','Sponsor report describes first clinical study approved November 2018 and last patient March 2020; registry June 2019 bounds first exposure, original paper confirms treated cohort.','https://www.kobia.kr/uploaded/company_member/276/intro_20251205094941_088.pdf')
entry('hmi102','2019-06','2019','Homology initial pheNIX treated clinical cohort reported in 2019.','https://clinicaltrials.gov/study/NCT03952156','first_trial_year_supported')
entry('erx963',None,'1991','ERX963 reported as flumazenil in sponsor-linked review. This is repurposing of long-approved anesthetic reversal drug; identity confidence is qualified because public sponsor trial uses code only.','https://pmc.ncbi.nlm.nih.gov/articles/PMC8372527/')
entry('flt190','2019-08','2019-08','Freeline SEC explicitly dates first MARVEL1 patient dosing August 2019.','https://www.sec.gov/Archives/edgar/data/1810031/000095017023011688/frln-20221231.htm')
entry('st920','2020-08','2020-08','Sangamo SEC reports first two patients dosed August and September 2020, superseding July 2019 registry opening.','https://www.sec.gov/Archives/edgar/data/1001233/000162828021003069/sgmo-20201231.htm')
entry('cti1601','2019-12','2019-12-18','First CTI1601 patient dosing announced December 18, 2019.','https://www.sec.gov/Archives/edgar/data/1374690/000119312519316829/d845901dex993.htm')
entry('rtx134','2020-01','2020-01-30','Rubius announces first patient dose by January 30, 2020.','https://www.sec.gov/Archives/edgar/data/1709401/000110465920009345/tm206327d1_ex99-1.htm')
entry('arct810','2020-06','2020-06-05','Arcturus announces first healthy volunteer dosed June 5, 2020.','https://ir.arcturusrx.com/news-releases/news-release-details/arcturus-therapeutics-announces-first-healthy-volunteer-dosed')
entry('dnl310','2020-07','2020','First treated DNL310 phase I/II study began 2020; exact screening date is not asserted as first dose.','https://clinicaltrials.gov/study/NCT04251026','first_trial_year_supported')
entry('four_d310','2021-03','2021-03-29','4D SEC first patient release places dosing March 2021, not registry September 2020.','https://www.sec.gov/Archives/edgar/data/1650648/000119312521094446/d118367dex991.htm')
entry('jr171','2020-09','2020-10-30','JCR first patient dosed release October 30, 2020.','https://www.jcrpharm.co.jp/en/assets/uploads/docs/2020-10-30_JCRAnnouncesFirstPatientDosedinPhase12GlobalClinicalTrialofJR-171forMPSI.pdf')
entry('bmn307','2020-09','2020-09-24','BioMarin first patient dosing announcement September 24, 2020.','https://www.biomarin.com/news/press-releases/biomarin-pioneer-in-phenylketonuria-pku-and-gene-therapy-doses-first-participant-in-global-phearless-phase-1-2-study-of-bmn-307-gene-therapy/')
entry('spk3006','2021-01','2021-02-01','Spark first patient dosed release February 1, 2021; registry October 2020 precedes actual exposure.','https://www.globenewswire.com/news-release/2021/02/01/2167191/35287/en/spark-therapeutics-announces-first-participant-dosed-in-phase-1-2-study-of-investigational-gene-therapy-for-late-onset-pompe-disease.html')
entry('at845','2021-01','2021-04-05','Astellas first FORTIS patient treated in 2021; registry October 2020 was earlier. Subsequent original safety results establish dosing.','https://newsroom.astellas.com/2023-02-22-Astellas-Announces-Update-on-Preliminary-Safety-and-Efficacy-Data-from-FORTIS-Study-of-Investigational-AT845-in-Adults-with-Late-Onset-Pompe-Disease')
entry('bocidelpar','2018','2018','Original first-in-human healthy volunteer ASP0367 study NCT03682484 began 2018, intended for mitochondrial/myopathy indications.','https://pmc.ncbi.nlm.nih.gov/articles/PMC9298414/','first_trial_year_supported')
entry('pbgm01','2021-03','2021-03','Passage SEC states first patient March 2021.','https://www.sec.gov/Archives/edgar/data/1787297/000155837022012042/pasg-20220630x10q.htm')
entry('lysgm101','2021-05','2022-02-07','Initial 2021 trial start to third patient dosed by February 7, 2022 bounds exposure; first exact month not recovered.','https://www.businesswire.com/news/home/20220206005034/en/Lysogene-Provides-Medical-Update')
entry('pr001_gd2','2019','2020-01-09','Prevail January 9, 2020 SEC release reports recently dosed compassionate-use GD2 patient, earlier than 2021 trial. The broad 2019-to-announcement interval avoids inventing a December dose. Sequence versus Parkinson PR001 clinical exposure remains an explicit indication sensitivity.','https://www.sec.gov/Archives/edgar/data/1714798/000119312520004748/d861073dex991.htm')
entry('vtx801','2021-09','2022','Initial GATEWAY actual trial start and subsequent treated reports establish 2021–2022 exposure interval; exact first dose unresolved.','https://clinicaltrials.gov/study/NCT04537377')
entry('ux701','2022-01','2022-02-17','Ultragenyx February 17, 2022 letter announces first patient dosed, replacing September 2021 registry opening.','https://wilsondisease.org/wp-content/uploads/2021/08/Ultragenyx-Wilson-Disease-Update-Feb-2022.pdf')
entry('alxn1850','2021-09','2022-08-24','Sponsor first-human clinical study report confirms treated subjects in September 2021–August 2022 study.','https://s3.amazonaws.com/ctr-med-7111/ALXN1850-HPP-101/8682c152-0932-4dfb-af33-423a6345591f/4d5822ec-a920-4b34-aaa0-a5e2e8763904/CSR_Synopsis_alxn1850hpp101_Redacted-v1.pdf')
entry('wven531','2021-09','2021','Wave initial dosing announcement confirms first phase Ib/II dosing in 2021.','https://ir.wavelifesciences.com/news-releases/news-release-details/wave-life-sciences-announces-initiation-dosing-phase-1b2a','first_trial_year_supported')
entry('ux053','2021-10','2023-03','Sponsor patient summary establishes eight actually dosed participants in first study conducted October 2021–March 2023; first exact dose not given.','https://www.ultragenyx.com/wp-content/uploads/2024/07/UX053-CL101-Plain-Language-Summary-MRCC-UX053-00018_Final-w-Cover-Sheet-wTranslations.pdf')
entry('aoc1001','2021-10','2021-11-04','Avidity first patient dosed November 4, 2021.','https://www.myotonic.org/sites/default/files/pages/files/2021-11-04_Avidity-MARINA-First-Patient-In-Release_FINAL.pdf')
entry('en001','2022-01','2022','Original DMD paper establishes seven actually treated patients in first 2022 phase I. Parallel CMT phase I begins February 2022; do not assume CMT first without dose chronology.','https://pmc.ncbi.nlm.nih.gov/articles/PMC11711273/','first_trial_year_supported')
entry('dt216','2022-03','2022-03','Design SEC history states first clinical study initiated March 2022; subsequent dosing results confirm exposure. P2 is formulation improvement of same active substance.','https://www.sec.gov/Archives/edgar/data/1807120/000119312526447258/dsgn-20260930.htm','first_trial_month_supported')
entry('flt201','2023-01','2023-06','Sponsor ESGCT timeline states clinical first patient H1 2023, correcting registry April 2022.','https://spurtherapeutics.com/wp-content/uploads/Spur-Therapeutics-ESGCT-Rome-2024-FLT201-Presentation-10-23-24.pdf')
entry('mrna3745','2022-06','2022-09-08','Moderna R&D presentation September 8, 2022 reports two patients treated.','https://irp.cdn-website.com/0a71bb4f/files/uploaded/Moderna-Final-R-D-Day-Slides_PDF-%2809.08.22%29.pdf')
entry('hmi103','2022-06','2022-12','July 26, 2023 cutoff reports first patient at 31 weeks post-dose, placing exposure no later than late December 2022; do not equate June enrollment with dosing.','https://www.globenewswire.com/news-release/2023/07/27/2712667/0/en/Homology-Medicines-Announces-Encouraging-Initial-Data-from-First-Dose-Level-in-the-pheEDIT-Trial-Evaluating-Gene-Editing-Candidate-HMI-103-in-Adults-with-Classical-PKU.html')
entry('can103','2022-07','2022-07','Sponsor first patient July 2022; initial phase I type 1 Gaucher, not direct CNS type 3 therapy.','https://canbridgepharma.com/en/media-news/press-release/22020720/')
entry('dyne251','2022-08','2022-09-06','Sponsor first DELIVER patient dosed announcement September 6, 2022.','https://investors.dyne-tx.com/news-releases/news-release-details/dyne-therapeutics-announces-first-patient-dosed-phase-12-deliver/')
entry('lx2006','2022-08','2023-06-13','Initial SUNRISE study start August 2022; sponsor confirms cohort 1 complete and cohort 2 dosed by June 13, 2023. Exact first-dose year not forced.','https://ir.lexeotx.com/news-releases/news-release-details/lexeo-therapeutics-announces-completion-first-cohort-and-dosing')
entry('dyne101','2022-09','2023','September 2022 release forecasts first dose rather than confirms it; later treated ACHIEVE results establish actual exposure by 2023.','https://investors.dyne-tx.com/news-releases/news-release-details/dyne-therapeutics-announces-initiation-phase-12-achieve-clinical')
entry('gc1123','2016','2016-10-26','Original JCR/Green Cross first ICV patient study began 2016, before later GC1123B formulation. Same idursulfase-beta protein as systemic GC1111.','https://www.prnewswire.com/news-releases/national-center-for-child-health-and-development-initiates-phase-12-trial-of-green-cross-idursulfase-beta-icv-for-the-treatment-of-hunter-syndrome-with-neurocognitive-decline-300351319.html')
entry('jnt517','2022-10','2023','ANZCTR first-in-human JNT517-101 and later sponsor healthy-volunteer results establish initial 2022–2023 exposure; registry enrollment is not dose date.','https://anzctr.org.au/Trial/Registration/TrialReview.aspx?ACTRN=12622001222730')
entry('aoc1044','2022-11','2023','Initial healthy volunteer EXPLORE44 study begins November 2022 and later clinical results establish treatment in 2022–2023.','https://filecache.investorroom.com/mr5ir_aviditybiosciences/231/download/FINAL%20Avidity%20Vol%2010%20AOC%201044%20Webcast%20Deck%2008-09-24.pdf')
entry('verenafusp','2023-04','2023','Original first-in-human study reports 18 actually treated healthy volunteers in 2023. Distinct GENERIUM fusion protein, not ArmaGen valanafusp/AGT181.','https://pubmed.ncbi.nlm.nih.gov/41705613/','first_trial_year_supported')
entry('isp001','2023-04','2023-12-15','Initial trial start April 2023 and sponsor December 15, 2023 first engineered B-cell patient dosed announcement bound actual exposure.','https://www.biospace.com/immusoft-administers-the-first-engineered-b-cell-in-a-human-clinical-trial')
entry('ilofotase','2013-09','2013','AM Pharma FIH healthy study started 2013 for acute kidney injury; 2023 HPP trial is later indication.','https://www.am-pharma.com/wp-content/uploads/2019/06/AM-Pharma-start-P1-AKI-ENG.pdf','first_trial_year_supported')
entry('gc301','2023-06','2024','Original infantile Pompe gene-therapy paper confirms initial treated children in the 2023–2024 series, preceding later adult commercial trial.','https://www.nejm.org/doi/full/10.1056/NEJMoa2407766')
entry('sar444836',None,None,'Sponsor explicitly stopped program, but registry still estimates enrollment and public plain-language-results link returns 404. Actual dosing not independently recovered; preserve registration sensitivity without assuming clinical inception.',confidence='unresolved_after_research')
entry('jr441','2023-10','2023-10-27','JCR first patient dosed release October 27, 2023.','https://www.jcrpharm.co.jp/en/assets/uploads/docs/2023-10-27_JCRPharmaceuticalsAnnouncesFirstPatientDosedinaGlobalPhaseI_IIClinicalTrialofJR-441fortheTreatmentofMPSIIIA.pdf')
entry('abx1100','2023-10','2024','First healthy-volunteer clinical study and subsequent phase I reports establish 2023–2024 exposure; no precise first-dose day recovered.','https://www.arobiotx.com/newsroom')
entry('dnl126','2024-01','2024-01','Denali SEC explicitly states first dosing January 2024, rather than December 2023 enrollment start.','https://www.sec.gov/Archives/edgar/data/1714899/000171489925000066/dnli-20241231.htm')
entry('pgnedodm1','2023-12','2023-12-18','PepGen first patient dosed announcement December 18, 2023.','https://investors.pepgen.com/news-releases/news-release-details/pepgen-announces-first-patient-dosed-phase-1-freedom-dm1')
entry('bmn351','2024-01','2024-12','First study began January 2024; sponsor 10-K states first and second dose cohorts enrolled by late 2024. Escalation to a second cohort plus later treated data supports 2024 exposure as an inference, not an explicit dated first-dose announcement. Nearby December 2024 dosing statement concerns BMN349 and must not be assigned to BMN351.','https://www.sec.gov/Archives/edgar/data/1048477/000104847725000007/bmrn-20241231.htm','first_trial_year_supported')
entry('vx670','2024-02','2024-08-02','Vertex August 2, 2024 10-Q explicitly reports enrolling and dosing DM1 patients.','https://investors.vrtx.com/static-files/bb2d04e0-a3f0-4f79-a050-34692fb2ac27')
entry('srp1003','2024-03','2024-03','Arrowhead first ARO-DM1 patient dosing in March 2024; transferred to Sarepta as SRP1003.','https://arrowheadpharma.com/en-us/newsroom/arrowhead-pharmaceuticals-initiates-phase-12a-study-aro-dm1')
entry('sgt003','2024-04','2024-06','Solid annual report explicitly first patient dosed Q2 2024.','https://www.sec.gov/Archives/edgar/data/1707502/000119312525096730/d795176dars.pdf')
entry('amt191','2024-06','2024-08-15','uniQure August 15, 2024 first patient announcement.','https://www.sec.gov/Archives/edgar/data/1590560/000155837024012295/qure-20240815xex99d1.htm')
entry('lym001','2023-11','2024-08','Original ASH IIT report describes three treated adults screened/enrolled November 2023–August 2024; separate commercial trial August 2024 is not necessarily FIH.','https://ashpublications.org/blood/article/146/Supplement%201/6098/553689/Safety-and-activity-of-gene-therapy-with-AAV8-GBA1')
entry('nggt002','2023-03','2024-02','Earlier China IIT NCT06061614 starts March 2023; sponsor November 2024 reports up to 40 weeks post-dose, confirming exposure by early 2024.','https://www.prnewswire.com/news-releases/next-generation-gene-therapeutics-nggt-announces-positive-new-data-on-nggt002-for-the-treatment-of-phenylketonuria-pku-302300911.html')
entry('sat3247','2024-09','2024-09-18','Satellos September 18 first healthy participant dosing announcement.','https://s203.q4cdn.com/439234936/files/doc_news/Satellos-Announces-Dosing-of-First-Participant-in-Phase-1-Clinical-Study-of-SAT-3247-2024.pdf')
entry('ns050',None,None,'Japanese registry confirms first enrollment September 18, 2024 and current FIH study, but separate actual dosing timing could not be established; preserve 2024 registry sensitivity.','https://jrct.mhlw.go.jp/en-latest-detail/jRCT2041240060','unresolved_after_research')
entry('atx01','2024-10','2024-10-18','ARTHEX first patient dosed October 18, 2024.','https://www.arthexbiotech.com/post/arthex-biotech-announces-first-patient-dosed-in-phase-i-iia-arthemir-tm-trial-for-myotonic-dystrophy-type-1-dm1')
entry('jr446','2024-11','2024-12-03','Japanese first patient announced December 3, 2024; 2026 global trial first patient is later phase/territory.','https://www.jcrpharm.co.jp/en/assets/uploads/docs/2024-12-03_MEDIPALHOLDINGSCORPORATIONandJCRPharmaceuticalsAnnounceInitiationofFirstDosinginPhaseI_IIClinicalTrialofJR-446forMPSIIIB.pdf')
entry('hg302','2024-11','2024-12','HuidaGene first-patient release establishes dosing late 2024; later fatal SAE does not itself establish program cessation.','https://www.huidagene.com/new/news/72')
entry('gc1130a','2024-11','2024-11-25','GC Biopharma first patient release November 25, 2024.','https://www.gcbiopharma.com/eng/news_view.do?idx=1388')
entry('beam301','2025-01','2025-05','Beam SEC reports first patient dosing announced May 2025; December 2024 registry start precedes drug administration.','https://www.sec.gov/Archives/edgar/data/1745999/000095017025102393/beam-20250630.htm')

# Curated indication-specific fate. A sponsor stop is not assumed absorbing.
status('sobi003','sponsor_discontinued','2020-03','Sobi Q1 report explicitly states program discontinued when no partner found; existing patient follow-up continued.','https://www.sobi.com/sites/sobi/files/pr/202004281040-1.pdf')
status('sb913','sponsor_discontinued','2021-01','Sangamo 2021 annual report explicitly confirms ending MPSII program in January 2021.','https://www.sec.gov/Archives/edgar/data/1001233/000162828022003819/sgmo-20211231.htm')
status('sb318','sponsor_discontinued','2021','Same annual report confirms MPSI genome-editing program discontinued; exact decision date not recovered.','https://www.sec.gov/Archives/edgar/data/1001233/000162828022003819/sgmo-20211231.htm')
status('cdx6114','sponsor_discontinued','2023-12-05','Codexis abandoned patent estate December 5, 2023 after Nestle declined assumption. Strong sponsor exit evidence; not proof no conceivable successor.','https://www.sec.gov/Archives/edgar/data/1200375/000120037524000009/R15.htm')
status('rtx134','sponsor_discontinued','2020-03','Rubius halted further RTX134 development amid manufacturing/cost and oncology prioritization.','https://www.sec.gov/Archives/edgar/data/1709401/000110465920032144/tm2012386d1_ex99-1.htm')
status('flt190','sponsor_discontinued','2023-04','Freeline explicitly halted further FLT190 development to prioritize Gaucher gene therapy.','https://www.sec.gov/Archives/edgar/data/1810031/000095017023042621/frln-20230630.htm')
status('bocidelpar','sponsor_discontinued','2024-03','Astellas FY2023 results (year ending March 2024) report ASP0367 PMM phase II and DMD phase I discontinued based on clinical data.','https://www.astellas.com/content/dam/astellas-com/global/en/documents/financial-results/supplementary-documents-%28fy2023%29-q4-2023.pdf')
status('ux053','trial_terminated_program_fate_unknown','2023-03','Sponsor patient summary states study ended March 2023 after eight treated patients; later SEC report confirms cessation. No clinical failure reason inferred.','https://www.ultragenyx.com/wp-content/uploads/2024/07/UX053-CL101-Plain-Language-Summary-MRCC-UX053-00018_Final-w-Cover-Sheet-wTranslations.pdf')
status('mrna3745','sponsor_discontinued','2025','Moderna 2025 analyst day says not progressing mRNA3745 to phase II and annual report lists discontinuation.','https://www.sec.gov/Archives/edgar/data/1682852/000162828025053318/exhibit9912025analystday.htm')
status('sar444836','sponsor_discontinued','2024','Sanofi 2024 annual report lists SAR444836 development discontinued. Trial follow-up record persists; actual first dosing unresolved.','https://dotcom.prod.accelerator.sanofi/assets/dotcom/content-app/publications/annual-report-on-form-20-f/2024-01-01-form-20-f-2024-en.pdf')
status('ux701','sponsor_discontinued','2026-11-03','Ultragenyx Q3 update explicitly terminated UX701 after failure to meet the dose-finding response criterion. Overrides earlier ongoing designation.','https://ir.ultragenyx.com/node/19346/ixbrl-viewer')
status('at845','active_development','2026-11','Astellas FY2026 Q2 pipeline/script still lists AT845. Nearby discontinuation legend referred to ASP5541/ASP6554, not AT845.','https://www.astellas.com/content/dam/astellas-com/global/en/confidential-documents/financial-results/2q2026_script_en.pdf')
status('rgx111','clinical_hold','2026-11','2026 SEC report discusses January 23 hold after CNS neoplasm and efforts to continue development under Nippon collaboration. Hold is not a permanent stop.','https://www.sec.gov/Archives/edgar/data/1590877/000119312526448581/rgnx-20260930.htm')
status('st920','active_development_transferred','2026','PTC completed acquisition of ST920 for continued Fabry development/BLA; earlier Sangamo resource constraints are not permanent failure.','https://ir.ptcbio.com/news-releases/news-release-details/ptc-completes-acquisition-st-920-fabry-disease-gene-therapy')
status('cti1601','active_BLA_submitted','2026-11-16','Larimar announced completed BLA submission; submission is not FDA approval.','https://larimar.gcs-web.com/node/12796/pdf')
status('arct810','active_development','2026-11','Arcturus current quarterly report continues ARCT810 phase II; ARCT2601 is a distinct candidate.','https://www.sec.gov/Archives/edgar/data/1768224/000119312526449901/arct-20260930.htm')
status('four_d310','deprioritized_current_fate_unknown','2025-03','Sponsor reduced investment and described 4D310 as noncore while phase I follow-up remained. No explicit permanent stop recovered.','https://www.sec.gov/Archives/edgar/data/1650648/000095017025030056/fdmt-20241231.htm')
status('spk3006','unknown_after_research',None,'Roche pipeline/registry still lists SPK3006/RG6359 but current substantive sponsor advancement statement not recovered. Do not infer failure from Spark restructuring.','https://www.rocheplus.ro/Pipeline.html')
status('bmn307','clinical_hold_current_fate_unknown','2025-11','2021 clinical hold and November 2025 EU orphan withdrawal established; orphan designation withdrawal does not establish program termination.','https://www.ema.europa.eu/en/medicines/human/orphan-designations/eu-3-19-2229')
status('pbgm01','transferred_current_fate_unknown','2026-11','Gemma license continued in SEC disclosure, with overdue milestone/financial uncertainty. Asset transfer is not automatically a stop.','https://www.sec.gov/Archives/edgar/data/1787297/000110465926124783/R13.htm')
status('vtx801','trial_terminated_program_fate_unknown','2024-10','Wilson patient organization reports four treated and trial terminated October 2024; Vivet/registry follow-up continues, no definitive global asset abandonment found.','https://wilsondisease.org/living-with-wilson-disease/treatment/genetic-therapies/')
status('actus101','active_followup_no_new_enrollment','2026-01','AskBio/Bayer says ACTUS101 remains active with no further enrollment while next program AB1009 advances.','https://www.bayer.com/media/download/75964e0c-af43-4c30-8781-bde50e5e506f/2026-0006e.pdf')
status('raav25naglu','deprioritized_current_fate_unknown','2016-11','uniQure explicitly deprioritized AMT110 and sought partners. Termination-cost language in same filing concerns workforce, not permanent drug abandonment.','https://www.sec.gov/Archives/edgar/data/1590560/000110465916158478/a16-21899_1ex99d2.htm')
status('avrrd01','sponsor_discontinued','2023','Avrobio annual report confirms no ongoing development of AVR-RD-01 after clinical halt/strategic changes.','https://www.sec.gov/Archives/edgar/data/1681087/000095017024031635/avro-20231231.htm')
status('avrrd02','sponsor_discontinued','2023','Avrobio annual report confirms no ongoing development of AVR-RD-02; separate AVR-RD-04 cystinosis sale does not revive Gaucher asset.','https://www.sec.gov/Archives/edgar/data/1681087/000095017024031635/avro-20231231.htm')
status('synb1618','superseded_by_distinct_asset','2022-11','Sponsor selected distinct optimized strain SYNB1934 for phase III. Later SYNB1934 trial failure is not an observed SYNB1618 phase III outcome.','https://www.sec.gov/Archives/edgar/data/1527599/000095017022024120/sybx-20220930.htm')
status('wven531','active_development','2026-08','Wave quarterly report describes continued clinical/extension development.','https://www.sec.gov/Archives/edgar/data/1631574/000119312526324949/wve-20260630.htm')
status('aoc1001','active_development','2026','Ongoing phase III/open-label program under subsequent ownership; original AOC1001 is delpacibart etedesiran.','https://euclinicaltrials.eu/ctis-public/view/2025-520766-22-00')
status('dt216','active_development','2026-11-04','Design reports ongoing DT216P2 clinical development; formulation switch is not a second asset or terminal failure.','https://investors.designtx.com/news-releases/news-release-details/design-therapeutics-announces-third-quarter-2026-financial/')
status('flt201','active_development','2026-07-07','Spur confirms phase III first patient dosed.','https://www.globenewswire.com/news-release/2026/07/07/3323089/0/en/spur-therapeutics-announces-first-patient-dosed-in-galileo-3-pivotal-clinical-trial-of-flt201-for-the-treatment-of-gaucher-disease-type-1.html')
status('dyne251','active_BLA_review','2026-11','Dyne reports BLA review and intended Q1 2027 launch; not FDA-approved by research cutoff.','https://investors.dyne-tx.com/news-releases/news-release-details/dyne-therapeutics-reports-third-quarter-2026-financial-results')
status('dyne101','active_development','2026','Dyne continues DM1 program/registrational development.','https://www.sec.gov/Archives/edgar/data/1818794/000181879426000013/dyn-ex99_1.htm')
status('lx2006','active_development','2026-11','Lexeo current filing reports ongoing pivotal development and follow-up.','https://www.sec.gov/Archives/edgar/data/1907108/000119312526462020/lxeo-20260930.htm')
status('jnt517','active_development','2026','Otsuka/Jnana phase III program registered in Japan; not an FDA approval.','https://jrct.mhlw.go.jp/en-latest-detail/jRCT2051250120')
status('aoc1044','active_development','2026-10','Novartis Q3 pipeline lists delpacibart zotadirsen clinical development.','https://www.novartis.com/sites/novartis_com/files/q3-2026-investor-presentation.pdf')
status('isp001','active_development','2026','Sponsor describes phase I/II and redosed first patient; B-cell gene product remains investigational.','https://www.immusoft.com/faqs/')
status('abx1100','active_development','2026-03-17','Aro reports positive phase Ib Pompe patient results, distinct from earlier healthy-volunteer dosing.','https://www.arobiotx.com/newsroom')
status('dnl126','active_development','2026-11','Denali current data show ongoing investigational MPSIIIA ETV program.','https://investors.denalitherapeutics.com/static-files/37f7ea27-934d-4aba-bc6f-a40765f3d0b9')
status('pgnedodm1','partial_clinical_hold','2026-11-10','PepGen reports ongoing DM1 program with partial FDA hold; do not transfer stopped PGN-EDO51 DMD outcome to PGN-EDODM1.','https://investors.pepgen.com/static-files/804d6245-584a-4c0c-a3bf-1c39f9bc8867')
status('bmn351','active_development','2026-05-04','BioMarin reports clinical data and extension development.','https://www.sec.gov/Archives/edgar/data/1048477/000104847726000006/earningsrelease-4may26ex991.htm')
status('vx670','active_development','2026-11','Entrada/Vertex quarterly disclosure reports ongoing multiple-dose clinical development.','https://www.sec.gov/Archives/edgar/data/1689375/000168937526000064/trda-20260930.htm')
status('srp1003','active_development','2026-03-25','Sarepta DM1 development update confirms ongoing SRP1003/ARO-DM1.','https://www.sarepta.com/community-letter-update-dm1-clinical-development-program')
status('sgt003','active_development','2026-11-04','Solid current report states 53 patients dosed; distinguish discontinued SGT001.','https://solidbio.gcs-web.com/news-releases/news-release-details/solid-biosciences-reports-third-quarter-2026-financial-results')
status('amt191','active_development','2026-11','uniQure quarterly update reports clinical dosing resumed August 2026.','https://www.sec.gov/Archives/edgar/data/1590560/000110465926122362/tm2628930d1_ex99-1.htm')
status('nggt002','active_development','2026','Sponsor pipeline describes eight patients dosed and further development.','https://nggtbio.com/pipeline/')
status('sat3247','active_development','2026-11','Current sponsor disclosure describes phase Ib DMD treated patients.','https://www.sec.gov/Archives/edgar/data/1421642/000117184326005503/exh_992.htm')
status('ns050','ongoing_registered_trial','2026-06-12','Japanese registry documents recruiting trial and actual first enrollment; dose timing still unresolved.','https://jrct.mhlw.go.jp/en-latest-detail/jRCT2041240060')
status('atx01','active_development','2026','ARTHEMIR initial patient trial remains ongoing under EU registry.','https://euclinicaltrials.eu/ctis-public/view/2023-505363-37-00')
status('jr446','active_development','2026-10','JCR Q2 presentation confirms ongoing JR446 clinical development.','https://www.jcrpharm.co.jp/en/assets/uploads/docs/FY2026-Q2_Results_Briefing_Session_EN.pdf')
status('hg302','serious_safety_event_development_uncertain','2026-10-27','Sponsor disclosed August 2025 fatal SAE on August 5, 2026; October 2026 company publication discusses further development. Death alone does not prove permanent cessation.','https://www.huidagene.com/new/news/82')
status('gc1130a','ongoing_registered_trial','2026','Current treating-site registry lists ongoing Sanfilippo A study.','https://clinicaltrials.ucsf.edu/trial/NCT06567769')
status('beam301','active_development','2026-11','Beam SEC continues BEAM301 clinical development following first human exposure in 2025.','https://www.sec.gov/Archives/edgar/data/1745999/000119312526444455/beam-20260930.htm')
status('en001','trial_terminated_program_fate_unknown','2024-05-20','ENCell annual filing says repeat-dose DMD phase I/II terminated early May 20, 2024; CMT remains active. Do not carry CMT status into DMD.','https://kind.krx.co.kr/external/2026/03/20/001219/20260320004527/11011.htm')
status('val1221','trial_terminated_program_fate_unknown','2020-01-24','Direct patient organization reported trial stopped/company funding closure; later Lafora exposure does not establish Pompe continuation.','https://agsd.org.uk/news/valerions-trial-pompe-stopped/')
status('rt001','discontinued_per_research_foundation',None,'FARA research-funder tracker identifies inactive/discontinued program following unsuccessful trial. No exact global termination decision date recovered.','https://www.curefa.org/drug-development/rt001/')
status('vp20629','discontinued_per_research_foundation',None,'FARA program tracker states OX1 discontinued; SEC establishes much earlier 2005 human entry.','https://www.curefa.org/drug-development/oxigon-ox1-aka-shp622-vp20629/')
status('trappsol','active_NDA_planned','2026-09-30','Sponsor reports pivotal primary endpoint miss but planned Q4 NDA, so failure of primary endpoint is not permanent program stop.','https://www.globenewswire.com/news-release/2026/09/30/3371740/0/en/rafael-holdings-announces-topline-results-from-the-pivotal-phase-3-transportnpc-study-of-trappsol-cyclo-in-niemann-pick-disease-type-c-npc.html')
status('vts270','active_NDA_review','2026-06-10','Beren reports FDA accepted NDA with November 17, 2026 action target; still investigational at November 16 cutoff.','https://www.berentx.com/news/community-update-building-long-term-support-for-families/')
status('saer','non_US_approved_US_outcome_unresolved','2024','Japan approved Acenobel; Ultragenyx US development stop does not imply global program failure. FDA indication outcome needs separate ascertainment.','https://www.pmda.go.jp/files/000273006.pdf')
status('gc1111','non_US_approved_US_outcome_unresolved','2012','Hunterase South Korean approval verified; do not count as FDA approval.','https://global-greencross.com/eng/research/global_project.html')
status('verenafusp','non_US_development_US_outcome_unresolved','2026','Original phase I publication confirms distinct GENERIUM protein. Non-US use reported but no FDA approval evidence established by this investigation.','https://pubmed.ncbi.nlm.nih.gov/41705613/')
status('saf301','superseded_by_distinct_asset',None,'Later LYS-SAF302 is a modified vector, not merely another name for SAF301. No ongoing standalone SAF301 development was recovered.')
status('sbc103','trial_terminated_program_fate_unknown',None,'Registry stop and older sponsor discontinuation context exist; full worldwide successor/asset fate not independently established in completion searches.')
status('lyssaf302','owner_liquidated_successor_unknown','2023-05','Lysogene liquidation is established in frozen primary evidence; no current successor development recovered. Do not call company liquidation an observed scientific failure.')
status('lysgm101','owner_liquidated_successor_unknown','2023-05','Lysogene liquidation is established; no successor clinical development found after alias/sponsor searches.')
status('ax250','active_BLA_planned','2026-11-09','Spruce quarterly release says tralesinidase alfa BLA submission on track for December 2026. Transfer from BioMarin/Allievex has not ended development.','https://www.sec.gov/Archives/edgar/data/1683553/000119312526452707/sprb-ex99_1.htm')
status('mossagal','active_development','2026-06-24','Eleva company presentation at BIO 2026 retains aGal/RPV001 pipeline; February 2025 manufacturing alliance explicitly supports continued Fabry development.','https://convention.bio.org/2026-sessions-and-courses/eleva-gmbh')
status('jr141','active_development_non_US_approved','2026-10','JCR FY2026 Q2 report describes October 2026 Italfarmaco licensing for US/Europe/Latin America and ongoing global program. Prior Japanese approval is separate from FDA outcome.','https://jcrpharm.com/wp-content/uploads/2026/10/FY2026-Q2_Financial_Report_EN.pdf')
status('dtx301','active_development','2026-11-04','Ultragenyx current quarterly report continues DTX301 OTC gene therapy program; not the newly approved DTX401 GSDIa program.','https://ir.ultragenyx.com/static-files/83f1b349-cb50-417a-8195-c53c514af23d')
status('idua_lvv','active_development','2026-11-02','Kyowa Kirin current pipeline lists OTL203 registrational MPSI development through 2027.','https://ir.kyowakirin.com/en/library/earnings/earnings0/main/0118/teaserItems1/00/linkList/01/link/presentation_2024_q4_en.pdf')
status('jr171','active_development','2026-10','JCR current quarterly report describes completed initial study and ongoing next-phase strategy for lepunafusp alfa.','https://jcrpharm.com/wp-content/uploads/2026/10/FY2026-Q2_Financial_Report_EN.pdf')
status('jr441','active_development','2026-07-30','JCR dated pipeline explicitly lists German phase I/II and Japanese phase I.','https://www.jcrpharm.co.jp/en/ir/pipeline/')
status('alxn1850','active_BLA_review','2026-09-18','AstraZeneca announces FDA priority review of efzimfotase alfa/ALXN1850 with H1 2027 action target; review is not approval.','https://www.astrazeneca.com/media-centre/press-releases/2026/efzimfotase-alfa-granted-priority-review-us-as-treatment-for-patients-with-hypophosphatasia-aged-2-years-and-older.html')
status('can103','non_US_approved_US_outcome_unresolved','2025-12-08','CANbridge HKEX filing reports first commercial prescription July 2, 2025 and inclusion on China innovative-drug insurance list. Website NDA-pending pipeline is stale; no FDA approval inferred.','https://www.hkexnews.hk/listedco/listconews/sehk/2025/1208/2025120800806.pdf')
status('gc301','active_development','2024-08','GeneCradle first adult registrational patient dosed August 2024 after infantile IIT; 2025 registry continues study. No later substantive company update recovered.','https://en.bj-genecradle.com/news/262')
status('lym001','active_development','2025-11-03','Original investigator report of treated IIT and subsequent commercial phase I/II results support ongoing clinical investigation in 2025; no dated 2026 sponsor advancement found.','https://ashpublications.org/blood/article/146/Supplement%201/6098/553689/Safety-and-activity-of-gene-therapy-with-AAV8-GBA1')

exclude('idursulfase_it','Novel-route reformulation of idursulfase already administered/approved intravenously before 2010; retain separate intrathecal-route sensitivity, not new-molecule inception.')
exclude('ht100','Prior halofuginone human oncology exposure 2001–2004; DMD reformulation is not new clinical inception.')
exclude('vp20629','OX1/VP20629 first human exposure 2005, outside 2010–2024; Friedreich disease is a later indication.')
exclude('oxabact','OC5 is reformulation/process evolution of earlier Oxabact OC2/OC3 treated before 2010. Can enter formulation-sensitivity set only.')
exclude('lucerastat','Original FIH OGT923 trial in 2002, outside entry window; 2015 Fabry study is later patient development.')
exclude('edasalonexent','CAT1004 first entered humans in 2011 for a metabolic/type 2 diabetes program; later DMD clinical trial is not initial rare-indication inception. Eligible broad all-drug 2011 sensitivity, not strict rare-first cohort.')
exclude('aeb1102','AEB1102 treated oncology patients in 2015 before ARG1 phase I. FDA ARG1 success retained, but strict initial rare-nononcology cohort excludes later indication.')
exclude('synb1020','Initial healthy study targeted hyperammonemia, followed by cirrhosis; UCD-specific clinical inception never established. Retain intended-rare-development sensitivity only.')
exclude('trappsol','Compassionate human use began 2009, outside 2010–2024 inception window.')
exclude('erx963','Available sponsor-linked identity evidence identifies old drug flumazenil; strict novel-molecule cohort excludes repurposing, with identity-confidence sensitivity.')
exclude('gc1123','GC1123 is ICV idursulfase beta, same protein as earlier GC1111. Keep distinct novel CNS delivery sensitivity but not another new molecule.')
exclude('ilofotase','First recAP human exposure 2013 for acute kidney injury; HPP clinical development is a later indication.')
exclude('beam301','Actual first human dosing in 2025; 2024 registry start is pre-dose enrollment. Exclude 2010–2024 dosed cohort, retain registered pre-dose sensitivity.')

extra('blsm22',canonical_asset='BLS-M22',modality_correction='Genetically modified Lactobacillus casei oral myostatin immunization; not a small molecule',aliases_add=['BLSM22','BLS-M22'],identity_note='Do not equate PMGC EL22 without a verified transfer/identity source.')
extra('lucerastat',aliases_add=['OGT923','OGT 923','CDP923','CDP 923','ACT-434964'],additional_nct_ids=['NCT02944487','NCT02944474'])
extra('ezutromid',aliases_add=['BMN195','BMN 195','SMT C1100','SMTC1100'])
extra('vp20629',aliases_add=['OX1','Oxigon','SHP622','indole-3-propionic acid'])
extra('raav25naglu',aliases_add=['AMT110','AMT-110','rAAV2/5-hNAGLU'])
extra('aeb1102',aliases_add=['Loargys','pegzilarginase'])
extra('prx102',aliases_add=['Elfabrio','pegunigalsidase alfa-iwxj'])
extra('ux003',aliases_add=['Mepsevii','vestronidase alfa-vjbk'])
extra('atb200',aliases_add=['Pombiliti','cipaglucosidase alfa-atga'])
extra('abo102',aliases_add=['UX111','Fayuvi','rebisufligene etisparvovec'])
extra('dtx401',aliases_add=['GenGlycos','pariglasgene brecaparvovec'])
extra('dnl310',aliases_add=['tividenofusp alfa'])
extra('bocidelpar',aliases_add=['ASP0367','MA0211','MA-0211'],indication_note='Healthy FIH was broad mitochondrial/myopathy development; DMD vs primary mitochondrial myopathy ordering remains sensitivity.')
extra('cti1601',aliases_add=['nomlabofusp'])
extra('st920',aliases_add=['isaralgagene civaparvovec','ST-920'])
extra('at845',aliases_add=['zocaglusagene nuzaparvovec'])
extra('flt201',aliases_add=['avigbagene samoparvovec'])
extra('spk3006',aliases_add=['RG6359'])
extra('dt216',aliases_add=['DT-216','DT-216P2','DT216P2'])
extra('dyne251',aliases_add=['zeleciment rostudirsen','zelecimentrostudirsen'])
extra('dyne101',aliases_add=['zeleciment basivarsen','zelecimentbasivarsen'])
extra('aoc1001',aliases_add=['delpacibart etedesiran','del-desiran'])
extra('aoc1044',aliases_add=['delpacibart zotadirsen','del-zota'])
extra('gc1123',aliases_add=['GC1123B','idursulfase beta ICV'])
extra('verenafusp',aliases_add=['Clotilia','verenafusp alfa'],identity_note='Not valanafusp alfa (AGT181).')
extra('hepastem',indication_note='Mixed UCD/Crigler-Najjar initial study; retain one asset program, do not create multiple independent successes from shared initial development.')
extra('can103',indication='Gaucher disease type 1',indication_note='Sponsor Nov2022 design: first phase I cohort GD1 only; type3 included later efficacy portion. Systemic ERT not demonstrated CNS restoration.')
extra('pr001_gd2',aliases_add=['PR001','LY3884961'],indication_note='Compassionate GD2 first-dose window straddles 2019–2020; prior Parkinson dose sequence unresolved, retain indication sensitivity.')
extra('nggt002',additional_nct_ids=['NCT06061614'])
extra('ns050',registered_predose_sensitivity=True)
extra('ax250',aliases_add=['BMN250','BMN 250','AX 250','TA-ERT','tralesinidase alfa'])
extra('mossagal',aliases_add=['RPV001','RPV-001','aGal'])
extra('alxn1850',aliases_add=['efzimfotase alfa'])
extra('can103',aliases_add=['Gaurunning'])
extra('gc301',indication_note='Initial infantile-onset Pompe IIT and later late-onset cohort are retained as one disease program; age/phenotype expansion is not a second inception.')

def day(s,end=False):
    if not s:return None
    if len(s)==4:return s+('-12-31' if end else '-01-01')
    if len(s)==7:
        y,m=map(int,s.split('-'));return s+('-'+str(calendar.monthrange(y,m)[1]) if end else '-01')
    return s

def source_info(path):
    d=json.loads(path.read_text()); raw=d.get('result','')
    if not isinstance(raw,str):return d,[]
    found=[]
    for block in raw.split('--------------------------------------------------------------------------------'):
        m=re.search(r'^([^\n]*)\s+\((https?://[^\n]+)\)',block.strip())
        if m:
            found.append({'title':m.group(1).strip(),'url':m.group(2),'source_file':str(path.relative_to(ROOT)), 'retrieved_date':CUTOFF})
    return d,found

updates={}; catalog={}
for row in Q:
    p=row['prior_source_record']; s=row['slug']; x=EXTRA.get(s,{})
    evidence=list(p.get('evidence',[])); searches=[]; files=[]
    for f in sorted(SRC.glob('metabolic_'+s+'_*.json')):
        d,refs=source_info(f); files.append(str(f.relative_to(ROOT)))
        for ref in refs:catalog[ref['url']]=ref
        for query in d.get('queries',[]):
            searches.append({'query':query,'result':'Completed and manually reconciled with registry, identity, entry and status evidence; not every returned hit refers to the correct asset. See adjudicated fields and remaining uncertainty.','source_file':str(f.relative_to(ROOT)),'retrieved_date':CUTOFF,'returned_source_count':len(refs)})
    oldexcluded=p.get('eligibility_status')=='excluded'
    en=ENTRY.get(s)
    if en is None:
        en={'interval':[None,None],'note':p.get('eligibility',{}).get('reason','Frozen prior exclusion retained.'),'url':None,'confidence':'previous_exclusion_retained' if oldexcluded else 'unresolved_after_research'}
    lo,hi=map(lambda t: t,en['interval'])
    interval=[day(lo),day(hi,True)]
    qualifies=bool(interval[0] and interval[1] and '2010-01-01'<=interval[0]<=interval[1]<='2024-12-31')
    reason=EXCLUDE.get(s)
    if reason:disposition='exclude'
    elif oldexcluded:
        disposition='exclude';reason=p.get('eligibility',{}).get('reason','Frozen prior exclusion retained.')
    elif qualifies:
        disposition='include';reason='Novel program with reviewed initial clinical exposure inside 2010–2024. Entry precision and indication/formulation sensitivities remain explicit; no proprietary exhaustive inception census is claimed.'
    else:
        disposition='unknown';reason='Actual first-human exposure window not established after targeted registry, alias, primary sponsor/regulator and publication research.'
    st=STATUS.get(s)
    approval=p.get('us_approval')
    if approval:
        st={'state':'FDA_approved','date':approval['date'],'note':'First indication-specific FDA approval established in primary regulator/sponsor evidence; later full approval is not a second event.','url':approval.get('url')}
    if st is None:
        if p.get('outcome')=='stopped':
            st={'state':'sponsor_discontinued','date':p.get('outcome_date'),'note':'Previously adjudicated explicit sponsor/regulator stop retained after new alias/status search; subsequent clinical restart not recovered. See frozen evidence for decision scope.','url':next((v['url'] for v in reversed(evidence) if 'clinicaltrials.gov' not in v.get('url','')),None)}
        elif p.get('outcome')=='ongoing':
            st={'state':'active_development','date':p.get('outcome_date'),'note':'Previously adjudicated current sponsor activity retained; new current and alias queries reviewed.','url':next((v['url'] for v in reversed(evidence) if 'clinicaltrials.gov' not in v.get('url','')),None)}
        else:
            st={'state':'unknown_after_research','date':None,'note':'No defensible current program-fate determination recovered after targeted registry/alias, sponsor/regulator, and publication searches. Trial status is preserved separately, not converted into a program stop.','url':None}
    def ev(url,claim,date=None):return {'url':url,'claim':claim,'date':date,'retrieved_date':CUTOFF}
    if en.get('url'):evidence.append(ev(en['url'],en['note'],None))
    if st.get('url'):evidence.append(ev(st['url'],st['note'],st['date']))
    active=st['state'] in ['active_development','active_development_transferred','active_development_non_US_approved','active_BLA_submitted','active_BLA_review','active_BLA_planned','active_NDA_review','active_NDA_planned','active_followup_no_new_enrollment','ongoing_registered_trial']
    neverdosed=s in ['mrt5201','hmi203','mrna3210','asp2016']
    uncertainty=[]
    if not approval:uncertainty.append('FDA approval absence requires central Drugs@FDA plus CBER alias matching; lack of an isolated web hit is not coded as a negative.')
    if en['confidence'] in ['unresolved_after_research','first_trial_year_supported','first_trial_month_supported']:uncertainty.append('Exact first dosing day not recovered; use stated interval/proxy sensitivity, not the registry date as a dose date.')
    if st['state'] in ['unknown_after_research','deprioritized_current_fate_unknown','transferred_current_fate_unknown','owner_liquidated_successor_unknown','trial_terminated_program_fate_unknown','superseded_by_distinct_asset','serious_safety_event_development_uncertain','clinical_hold_current_fate_unknown']:uncertainty.append(st['note'])
    if x.get('indication_note'):uncertainty.append(x['indication_note'])
    if x.get('identity_note'):uncertainty.append(x['identity_note'])
    if s=='blsm22':uncertainty.append('Original trial and 2026 publication establish exposure; searches for BLS-M22/BioLeaders current DMD program, approvals and purported EL22 transfer did not establish successor identity or current development fate.')
    if s in ['agt181','agt182','prx112','dmpkrx','hepastem','gc1119','ucmsc']:
        uncertainty.append('Registry code and molecular/product aliases were searched against sponsor/regulator and publication sources. Historical treatment was recovered where recorded, but explicit current indication-specific program continuation or permanent stop was not recovered; unrelated later indications and similar codes were rejected.')
    if s=='sar444836':uncertainty.append('UCSF linked Sanofi DFI17545 plain-language results endpoint returned HTTP404; ClinicalTrials.gov actual study start with estimated32 enrollment does not verify anyone was dosed.')
    if s=='ns050':uncertainty.append('Japanese jRCT explicitly labels 2024-09-18 first enrollment, not first administration; first-dose queries returned registry/pipeline material only.')
    year=interval[0][:4] if interval[0] and interval[1] and interval[0][:4]==interval[1][:4] else None
    precise=bool(lo and hi and lo==hi and len(lo)==10)
    fhdate=lo if lo==hi else year
    aliases=sorted(set([p['asset'],row['asset']]+p.get('aliases',[])+x.get('aliases_add',[])))
    ncts=sorted(set(p.get('nct_ids',[])+x.get('additional_nct_ids',[])))
    flags=p.get('filters',{}).copy()
    if s=='blsm22':flags['genetic_medicine']=True;flags['protein_restoration']=False
    if s=='can103':flags['genetically_defined_cns']=False;flags['intrathecal_protein_restoration_neurodevelopment']=False
    out={'id':row['id'],'family':'metabolic','canonical_asset':x.get('canonical_asset',p['asset']),'indication':x.get('indication',p['indication']),'aliases':aliases,'asset_cluster':s,'candidate_ids':p['candidate_ids'],'nct_ids':ncts,
         'disposition':disposition,'disposition_reason':reason,'first_human_date':fhdate,'first_human_year':int(year) if year else None,'first_human_precision':'day' if precise else ('month' if lo==hi and lo and len(lo)==7 else ('year' if year else 'interval' if lo and hi else 'unknown')),'first_human_interval':interval,'first_human_evidence':[ev(en['url'],en['note'])] if en.get('url') else [],'first_human_entry_note':en['note'],'first_human_confidence':en['confidence'],'first_human_exact_dose_verified':precise,'entry_window_qualified':qualifies and disposition=='include','global_first_human_exhaustively_verified':False,
         'prior_indication_entry_proxy':p.get('entry_date_proxy'),'prior_human_exposure':'documented_prior_exposure_or_later_indication' if s in EXCLUDE and s!='beam301' else ('none_dosed' if neverdosed else 'no_disqualifying_exposure_recovered_subject_to_notes'),
         'outcome':st['state'],'outcome_date':st['date'],'outcome_date_precision':'day' if st['date'] and len(st['date'])==10 else 'month' if st['date'] and len(st['date'])==7 else 'year' if st['date'] else 'unknown','outcome_note':st['note'],'outcome_evidence':[ev(st['url'],st['note'],st['date'])] if st.get('url') else [],'last_verified_active_date':st['date'] if active else None,'FDA_ever_approved':True if approval else None,'FDA_ever_approved_scope':'this drug-indication; not all indications','FDA_approval_date':approval['date'] if approval else None,'FDA_approval_pathway':('accelerated' if approval.get('accelerated') else 'traditional') if approval else None,'FDA_approval_evidence':[ev(approval.get('url'),'Indication-specific first FDA approval',approval['date'])] if approval else [],'FDA_negative_ascertainment':'awaiting_central_alias_matched_FDA_and_CBER' if not approval else None,'non_US_approval':p.get('non_us_approval'),
         'permanent_stop_is_absorbing_assumption':False,'registered_predose_sensitivity':neverdosed or s=='beam301' or x.get('registered_predose_sensitivity',False),'registered_entry_proxy':p.get('entry_date_proxy') if neverdosed or s in ['beam301','sar444836','ns050'] else None,'never_dosed_confirmed':neverdosed,
         'filters':flags,'flags':{'rare':flags.get('rare_nononcology'),'genetic_cns':flags.get('genetically_defined_cns'),'genetic_medicine':flags.get('genetic_medicine'),'novel_target':flags.get('novel_target_at_entry'),'intrathecal':flags.get('intrathecal'),'protein_restoration':flags.get('protein_restoration')},'modality':x.get('modality_correction',p.get('modality')),
         'registry_evidence':row.get('registry_review',[]),'evidence':evidence,'searches':searches,'source_files':files,'research_complete':True,'research_completion_date':CUTOFF,'research_completion_scope':'Finite assigned program history review; remaining uncertainty is explicit, not an untouched queue. Prior 17 excluded cases retain their documented frozen exclusion.','remaining_uncertainty':uncertainty,'frozen_source_record':'data/pos_adjudication/metabolic_program_ledger.json#'+p['program_id']}
    if s in ['ucmsc','gc1119','sar444836','ns050']:
        out['unresolved_search_summary']=en['note']
    if oldexcluded and not files:
        out['searches']=[{'query':'Frozen prior exclusion identity and earliest-human/zero-enrollment check','result':'Previously resolved exclusion retained; full primary citations in frozen record. Not silently assigned a new clinical entry date.','source_file':'data/pos_adjudication/metabolic_program_ledger.json#'+p['program_id']}]
    out['review_complete']=True
    if s=='lucerastat':
        out['source_files'].append('sources/pos_completion/metabolic_registry_supplement.json')
        out['searches'].append({'query':'ClinicalTrials.gov API exact NCT02944487/NCT02944474','result':'Primary registry records confirm SAD October–December2002 and MAD December2003–May2004; original publication confirms administration.','source_file':'sources/pos_completion/metabolic_registry_supplement.json','retrieved_date':CUTOFF})
    updates[row['id']]=out

(ROOT/'data/pos_completion/metabolic_updates.json').write_text(json.dumps(updates,indent=2)+'\n')
(ROOT/'sources/pos_completion/metabolic_source_catalog.json').write_text(json.dumps(list(catalog.values()),indent=2)+'\n')
summary={'cutoff':CUTOFF,'assigned_total':len(Q),'newly_researched':sum(bool(r['source_files']) for r in updates.values()),'prior_excluded_retained':sum(r['prior_source_record'].get('eligibility_status')=='excluded' for r in Q),'counts_by_disposition':dict(Counter(r['disposition'] for r in updates.values())),'counts_by_outcome':dict(Counter(r['outcome'] for r in updates.values())),'qualified_entry_intervals':sum(r['entry_window_qualified'] for r in updates.values()),'source_catalog_unique_returned_urls':len(catalog),'source_catalog_note':'Discovery inventory includes irrelevant returned hits; accepted claims are the adjudicated evidence fields, not every catalog URL.','candidate_ids_covered':len(set(c for r in updates.values() for c in r['candidate_ids'])),'unresolved_entry_assets':[r['canonical_asset'] for r in updates.values() if r['disposition']=='unknown'],'warning':'No lifetime approval-rate estimate is computed here. Fixed-horizon approval ascertainment is separate from sponsor/program fate. Entry intervals require boundary sensitivity.'}
(ROOT/'data/pos_completion/metabolic_completion_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
