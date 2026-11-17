"""Rebuild the finite metabolic/neuromuscular adjudication slice from saved sources.
No network calls. Manual decisions are explicit below; unverified is not failure.
"""
import json, re
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1]
OUT=P/'data/pos_adjudication'
ASOF='2026-11-16'
cs={x['candidate_id']:x for x in json.load(open(P/'data/pos_nested/candidate_review_queue.json'))}
screen=json.load(open(P/'data/pos_adjudication/full_screen.json'))
trials={x['nct_id']:x for x in json.load(open(P/'data/pos_nested/trial_inventory.json'))}
selected=[cs[x['candidate_id']] for x in screen if x['disposition']=='priority_early_industry' and (set(cs[x['candidate_id']]['families'])&{'lysosomal','metabolic'} or set(x['structured_disease_matches'])&{'DMD','GNE','DM1','Friedreich'})]
priority_ids={c['candidate_id'] for c in selected}
supplemental_ids={'e77c8406824cdfcc','acf16e0a66162379','f40d938aa1d4d9c9','535921071899fe1e','785264a929bc578b','9d7d0fee150fe2ee'}
selected += [cs[i] for i in sorted(supplemental_ids-priority_ids)]
raw={}
for f in (P/'sources/pos_nested').glob('broad_allphase_*.json'):
    if f.name.endswith('.meta.json'): continue
    d=json.load(open(f))
    for s in d.get('studies',[]):
        ps=s.get('protocolSection',{}); n=ps.get('identificationModule',{}).get('nctId')
        if n: raw[n]=ps
# Canonical program|name|indication|modality|panel trials identifying the program.
# Cross-indication trials are held as mixed-indication, not multiplied into independent outcomes.
CONFIG='''
rhhns|rhHNS (SHP610/HGT-1410)|MPS IIIA|ERT|NCT01155778,NCT01299727
isu302|ISU302 (imiglucerase/Abcertin)|Gaucher type 1|ERT_followon|NCT01161914,NCT01881633
bmn701|Reveglucosidase alfa (BMN701)|Pompe|ERT|NCT01230801,NCT01435772
bmn110|Elosulfase alfa (BMN110)|MPS IVA|ERT|NCT01242111,NCT01515956,NCT01609062,NCT01697319
gc1111|Idursulfase beta (GC1111/Hunterase)|MPS II somatic|ERT_followon|NCT01301898
saer|Aceneuramic acid ER (SA-ER/Ace-ER)|GNE myopathy|small_molecule|NCT01359319
ambroxol|Ambroxol|Gaucher|repurposed_small_molecule|NCT01463215
saf301|SAF301|MPS IIIA|AAV|NCT01474343,NCT02053064
migalastat|Migalastat (AT1001/GR181413A)|Fabry|small_molecule|NCT01489995,NCT01730469,NCT01730482,NCT01853852,NCT02082327
idursulfase_it|Idursulfase intrathecal|MPS II neurologic|ERT_route_extension|NCT01506141,NCT02055118,NCT02412787,NCT06031259
ucmsc|Human umbilical cord mesenchymal stem cells|DMD|nonengineered_cell|NCT01610440
gc1119|GC1119|Fabry|ERT|NCT01653444
prx102|Pegunigalsidase alfa (PRX102)|Fabry|ERT|NCT01678898,NCT02921620,NCT01981720,NCT02795676,NCT03018730
vts270|Adrabetadex (VTS270)|Niemann-Pick C1|cyclodextrin_intrathecal|NCT01747135,NCT03887533
prx112|PRX112 oral glucocerebrosidase|Gaucher|ERT|NCT01747980,NCT02107846
givinostat|Givinostat (ITF2357)|DMD|repurposed_small_molecule|NCT01761292,NCT04821063
hepastem|HepaStem|Urea-cycle disorders and Crigler-Najjar (mixed)|nonengineered_cell|NCT01765283
pro045|PRO045/BMN045|DMD exon 45|ASO|NCT01826474
ht100|HT100 (halofuginone)|DMD|small_molecule|NCT01847573,NCT01978366,NCT02525302
ux003|Vestronidase alfa (UX003)|MPS VII|ERT|NCT01856218
trientine|Trientine dihydrochloride|Wilson disease|repurposed_small_molecule|NCT01874028
avalglucosidase|Avalglucosidase alfa (GZ402666)|Pompe|ERT|NCT01898364
vp20629|VP20629/SHP622|Friedreich ataxia|small_molecule|NCT01898884
pro053|PRO053/BMN053|DMD exon 53|ASO|NCT01957059
olipudase|Olipudase alfa|Acid sphingomyelinase deficiency|ERT|NCT02004691,NCT02292654
oxabact|Oxabact OC5|Primary hyperoxaluria|nonengineered_biotic|NCT02012985
ezutromid|Ezutromid (SMTC1100)|DMD|small_molecule|NCT02056808
agt182|AGT182|MPS II|BBB_ERT|NCT02262338
golodirsen|Golodirsen (SRP4053)|DMD exon 53|ASO|NCT02310906,NCT02500381
dmpkrx|Baliforsen (IONIS-DMPKRx)|DM1|ASO|NCT02312011
sbc103|SBC103|MPS IIIB|ERT|NCT02324049,NCT02618512
agt181|Valanafusp alfa (AGT181)|MPS I|BBB_ERT|NCT02371226,NCT02597114,NCT03053089,NCT03071341
eliglustat|Eliglustat|Gaucher type 1|small_molecule|NCT02422654,NCT02536911,NCT02536937
edasalonexent|Edasalonexent|DMD|small_molecule|NCT02439216,NCT03703882
rt001|RT001|Friedreich ataxia|small_molecule|NCT02445794
aeb1102|Pegzilarginase (AEB1102)|Arginase 1 deficiency|ERT|NCT02488044,NCT03378531
casimersen|Casimersen (SRP4045)|DMD exon 45|ASO|NCT02500381,NCT02530905
ds5141b|DS5141b|DMD exon 45|ASO|NCT02667483,NCT04433234
atb200|Cipaglucosidase alfa plus miglustat (ATB200/AT2221)|Late-onset Pompe|ERT_combination|NCT02675465
sb318|SB318|MPS I|in_vivo_gene_editing|NCT02702115
lumasiran|Lumasiran|Primary hyperoxaluria type 1|siRNA|NCT02706886,NCT03681184
ax250|Tralesinidase alfa (AX250)|MPS IIIB|ICV_ERT|NCT02754076,NCT03784287
dcrph1|DCR-PH1|Primary hyperoxaluria type 1|siRNA|NCT02795325
val1221|VAL1221|Pompe|ERT|NCT02898753
lucerastat|Lucerastat|Fabry|small_molecule|NCT02930655,NCT03425539,NCT03737214
dtx301|DTX301 (scAAV8OTC)|Ornithine transcarbamylase deficiency|AAV|NCT02991144
mossagal|Moss-aGal|Fabry|ERT|NCT02995993
sb913|SB913|MPS II|in_vivo_gene_editing|NCT03041324
jr141|Pabinafusp alfa (JR141)|MPS II neurologic|BBB_ERT|NCT03128593,NCT03359213,NCT03568175,NCT03708965,NCT04348136,NCT04573023,NCT05594992
synb1020|SYNB1020|Hyperammonemia (UCD intended; human development included cirrhosis)|engineered_biotic|NCT03179878
rvx000222|Apabetalone (RVX000222)|Fabry|repurposed_small_molecule|NCT03228940
raav25naglu|rAAV2/5-hNAGLU|MPS IIIB|AAV|NCT03300453
abo101|ABO101 (rAAV9.CMV.hNAGLU)|MPS IIIB|AAV|NCT03315182
pf06939926|Fordadistrogene movaparvovec (PF06939926)|DMD|AAV|NCT03362502
sgt001|SGT001|DMD|AAV|NCT03368742
srp9001|Delandistrogene moxeparvovec (SRP9001)|DMD|AAV|NCT03375164,NCT04626674,NCT05096221,NCT05881408,NCT05967351,NCT06128564,NCT06241950,NCT06597656,NCT03769116
srp5051|Vesleteplirsen (SRP5051)|DMD exon 51|peptide_ASO|NCT03375255,NCT03675126
nedosiran_ph1|Nedosiran (DCR-PHXC)|Primary hyperoxaluria type 1 (early study included PH2)|siRNA|NCT03392896
sobi003|SOBI003|MPS IIIA|ERT|NCT03423186,NCT03811028
avrrd01|AVR-RD-01|Fabry|HSC_gene_therapy|NCT03454893
idua_lvv|IDUA-LVV genetically modified autologous HSPCs (OTL203)|MPS I Hurler|HSC_gene_therapy|NCT03488394
suvodirsen|Suvodirsen (WVE210201)|DMD exon 51|ASO|NCT03508947
synb1618|SYNB1618|Phenylketonuria|engineered_biotic|NCT03516487
actus101|ACTUS101|Late-onset Pompe|AAV|NCT03533673
rgx111|RGX111|MPS I|AAV|NCT03580083
mrt5201|MRT5201|Ornithine transcarbamylase deficiency|mRNA|NCT03767270
blsm22|BLS-M22|DMD|small_molecule|NCT03789734
trappsol|Trappsol Cyclo (hydroxypropyl beta cyclodextrin)|Niemann-Pick C|cyclodextrin_IV|NCT03893071
hmi102|HMI102|Phenylketonuria|AAV|NCT03952156
erx963|ERX963|DM1|small_molecule|NCT03959189
flt190|FLT190|Fabry|AAV|NCT04040049,NCT04455230
st920|Isaralgagene civaparvovec (ST920)|Fabry|AAV|NCT04046224
cdx6114|CDX6114|Phenylketonuria|oral_enzyme|NCT04085666,NCT04256655
abo102|Rebisufligene etisparvovec (UX111/ABO102)|MPS IIIA|AAV|NCT04088734,NCT02716246
dtx401|Pariglasgene brecaparvovec (DTX401)|Glycogen storage disease Ia|AAV|NCT03517085,NCT05139316
viltolarsen|Viltolarsen (NS065/NCNP01)|DMD exon 53|ASO|NCT02081625,NCT02740972,NCT03167255,NCT04060199,NCT04768062,NCT04956289
lyssaf302|LYS-SAF302|MPS IIIA|AAV|NCT03612869
spk3006|SPK3006|Pompe|AAV|NCT04093349
rtx134|RTX134|Phenylketonuria|engineered_cell|NCT04110496
avrrd02|AVR-RD-02|Gaucher type 1|HSC_gene_therapy|NCT04145037
at845|Zocaglusagene nuzaparvovec (AT845)|Pompe|AAV|NCT04174105
cti1601|Nomlabofusp (CTI1601)|Friedreich ataxia|protein_replacement|NCT04176991,NCT04519567,NCT05579691,NCT06447025,NCT06681766
bocidelpar|Bocidelpar|DMD|small_molecule|NCT04184882
jr171|Lepunafusp alfa (JR171)|MPS I|BBB_ERT|NCT04227600,NCT04453085
dnl310|Tividenofusp alfa (DNL310)|MPS II neurologic|BBB_ERT|NCT04251026,NCT05371613,NCT06075537
lysgm101|LYS-GM101|GM1 gangliosidosis|AAV|NCT04273269
pr001_gd2|LY3884961 (PR001)|Gaucher type 2 neuronopathic|AAV|NCT04411654
arct810|ARCT810|Ornithine transcarbamylase deficiency|mRNA|NCT04416126,NCT04442347
bmn307|BMN307|Phenylketonuria|AAV|NCT04480567
four_d310|4D310|Fabry|AAV|NCT04519749,NCT05629559
vtx801|VTX801|Wilson disease|AAV|NCT04537377
nedosiran_ph3|Nedosiran (DCR-PHXC)|Primary hyperoxaluria type 3|siRNA|NCT04555486
pbgm01|PBGM01|GM1 gangliosidosis|AAV|NCT04713475
ux701|UX701|Wilson disease|AAV|NCT04884815
wven531|WVE-N531|DMD exon 53|ASO|NCT04906460
alxn1850|ALXN1850|Hypophosphatasia|ERT|NCT04980248,NCT06079281,NCT06079359,NCT06079372
ux053|UX053|Glycogen storage disease III|mRNA|NCT04990388
aoc1001|Delpacibart etedesiran (AOC1001)|DM1|antibody_siRNA|NCT05027269
mrna3745|mRNA3745|Glycogen storage disease Ia|mRNA|NCT05095727
hmi103|HMI103|Phenylketonuria|gene_editing|NCT05222178
hmi203|HMI203|MPS II|AAV|NCT05238324
dt216|DT216|Friedreich ataxia|small_molecule|NCT05285540,NCT05573698
flt201|FLT201|Gaucher type 1|AAV|NCT05324943,NCT06545136
en001|EN001|DMD|nonengineered_cell|NCT05338099
biosidus_agalsidase|Agalsidase beta (Biosidus)|Fabry|ERT_followon|NCT05343715
gc1123|GC1123|MPS II|ERT|NCT05422482
lx2006|LX2006|Friedreich ataxia cardiomyopathy|AAV|NCT05445323
can103|CAN103|Gaucher type 1/3 mixed|ERT|NCT05447494
dyne101|DYNE101|DM1|antibody_ASO|NCT05481879
pr001_gd1|LY3884961 (PR001)|Gaucher type 1|AAV|NCT05487599
dyne251|DYNE251|DMD exon 51|antibody_ASO|NCT05524883
aoc1044|AOC1044|DMD exon 44|antibody_ASO|NCT05670730
isp001|ISP001 autologous engineered plasmablasts|MPS I|engineered_cell|NCT05682144
jnt517|JNT517|Phenylketonuria|small_molecule|NCT05781399
gc301|GC301|Pompe (infantile and late-onset)|AAV|NCT05793307,NCT06391736
ilofotase|Ilofotase alfa|Hypophosphatasia|ERT|NCT05890794
sar444836|SAR444836|Phenylketonuria|AAV|NCT05972629
ns050|NS-050/NCNP-03|DMD exon 50|ASO|NCT06053814
jr441|JR441|MPS IIIA|BBB_ERT|NCT06095388
abx1100|ABX1100|Late-onset Pompe|ERT|NCT06109948
teta4hcl|Trientine tetrahydrochloride once daily|Wilson disease|repurposed_small_molecule|NCT06128954
sgt003|SGT003|DMD|AAV|NCT06138639
srp1003|SRP1003 (ARO-DM1)|DM1|siRNA|NCT06138743
mrna3210|mRNA3210|Phenylketonuria|mRNA|NCT06147856
dnl126|DNL126|MPS IIIA|BBB_ERT|NCT06181136
vx670|VX670|DM1|oligonucleotide_conjugate|NCT06185764
pgnedodm1|PGN-EDODM1|DM1|peptide_ASO|NCT06204809
amt191|AMT191|Fabry|AAV|NCT06270316
bmn351|BMN351|DMD exon 51|ASO|NCT06280209
atx01|ATX01|DM1|ASO|NCT06300307
verenafusp|Verenafusp alfa|MPS II|BBB_ERT|NCT06475404
asp2016|ASP2016|Friedreich ataxia cardiomyopathy|AAV|NCT06483802
jr446|JR446|MPS IIIB|BBB_ERT|NCT06488924
sat3247|SAT3247|DMD|small_molecule|NCT06565208
gc1130a|GC1130A|MPS IIIA|ERT|NCT06567769
hg302|HG302|DMD|AAV|NCT06594094
nggt002|NGGT002|Phenylketonuria|AAV|NCT06687733
beam301|BEAM301|Glycogen storage disease Ia|gene_editing|NCT06735755
lym001|LY-M001|Gaucher type 1|AAV|NCT06818838
'''
configs=[]
for line in CONFIG.strip().splitlines():
    slug,asset,indication,modality,ncts=line.split('|')
    configs.append(dict(program_id='metabolic_'+slug,slug=slug,asset=asset,indication=indication,modality=modality,config_ncts=ncts.split(',')))
exclude_names={'hematopoietic stem cell infusion':'Generic transplant intervention, not a defined commercial drug product.', 'Reactive Corticosteroid Taper Regimen':'Supportive immunosuppression in gene-therapy trial.', 'Prophylactic Corticosteroid Taper Regimen':'Supportive immunosuppression in gene-therapy trial.', 'Standard of Care (SOC)':'Comparator/background treatment.', 'H1 Blocker':'Premedication, not investigational disease-modifying program.', 'Prophylactic immunomodulatory therapy':'Supportive immunosuppression in gene-therapy trial.', 'imlifidase':'Adjunct to enable Elevidys dosing, not independent DMD disease-modifying program.'}
programs=[]; dispositions=[]
for c in selected:
    if c['intervention_name'] in exclude_names:
        dispositions.append(dict(candidate_id=c['candidate_id'],intervention_name=c['intervention_name'],disposition='excluded_background_or_not_defined_drug_program',program_id=None,reason=exclude_names[c['intervention_name']],nct_ids=c['nct_ids']))
        continue
    matches=[z for z in configs if set(z['config_ncts'])&set(c['nct_ids'])]
    # ESSENCE contains two distinct drugs; do not collapse by shared trial identifier.
    if c['intervention_name']=='SRP-4053': matches=[z for z in configs if z['slug']=='golodirsen']
    if c['intervention_name']=='SRP-4045': matches=[z for z in configs if z['slug']=='casimersen']
    assert len(matches)==1,(c,matches)
    m=matches[0];m.setdefault('candidates',[]).append(c)
    dispositions.append(dict(candidate_id=c['candidate_id'],intervention_name=c['intervention_name'],disposition='mapped_canonical_program',program_id=m['program_id'],reason='Explicit asset/indication mapping; doses and spelling variants consolidated.',nct_ids=c['nct_ids']))

def evidence(url,claim,date=None,source_type='primary_regulator_or_sponsor'):
    return dict(url=url,claim=claim,source_date=date,retrieved_date=ASOF,source_type=source_type)

for m in configs:
    candidates=m.pop('candidates',[])
    if not candidates: continue
    ncts=sorted({n for c in candidates for n in c['nct_ids']})
    ts=[trials[n] for n in ncts if n in trials]
    ss=[]
    for t in ts:
        ss.append(evidence('https://clinicaltrials.gov/study/'+t['nct_id'],'Sponsor-submitted registry record: identity, indication, trial start, trial status; a trial status is not program outcome.',t.get('last_update'),'primary_trial_registry'))
    genetic=m['modality'] in {'ASO','AAV','in_vivo_gene_editing','siRNA','peptide_ASO','HSC_gene_therapy','mRNA','engineered_cell','gene_editing','antibody_siRNA','antibody_ASO','oligonucleotide_conjugate'}
    cns=any(s in m['indication'] for s in ['MPS III','MPS I Hurler','MPS II neurologic','GM1','Gaucher type 2','Friedreich ataxia']) and 'cardiomyopathy' not in m['indication']
    if m['indication'] in {'MPS I','MPS II','MPS VII','Gaucher','Gaucher type 1/3 mixed'}:cns=None
    protein=m['modality'] in {'ERT','ERT_followon','ERT_route_extension','BBB_ERT','ICV_ERT','ERT_combination','oral_enzyme','protein_replacement','AAV','HSC_gene_therapy','in_vivo_gene_editing','gene_editing','mRNA','engineered_cell'} or ('DMD' in m['indication'] and genetic)
    route_text=' '.join(json.dumps(raw.get(n,{}).get('armsInterventionsModule',{})) for n in ncts).lower()
    it=bool(re.search(r'\bintrathecal\b',route_text))
    icv=bool(re.search(r'intracerebroventricular|intra.?cerebro.?ventricular',route_text))
    fihtext=[]
    for n in ncts:
        text=json.dumps(raw.get(n,{}).get('descriptionModule',{}))+' '+trials.get(n,{}).get('title','')
        if re.search('first.in.human|first.in.man',text,re.I):fihtext.append(n)
    p={k:v for k,v in m.items() if k not in {'config_ncts','slug'}}
    p.update(slug=m['slug'],candidate_ids=sorted(c['candidate_id'] for c in candidates),aliases=sorted({c['intervention_name'] for c in candidates}),nct_ids=ncts,sponsors=sorted({s for c in candidates for s in c['sponsors']}),entry_date_proxy=min(c['earliest_observed_panel_trial_date'] for c in candidates),entry_date_type='earliest_observed_panel_trial_start_not_first_dose',first_human_entry_date=None,first_human_entry_confidence='registry_first_in_human_language_date_is_study_start_proxy' if fihtext else 'unresolved_global_first_exposure',first_human_registry_language_nct_ids=fihtext,eligibility={'registry_entry_reference_cohort':True,'verified_first_human_2010_2024':None,'indication_specific_inception_confirmed':None,'repurposed_or_prior_human_exposure':None,'mixed_indication_requires_split':False,'reason':'Named investigational asset in industry-associated early-phase registry frame; global first-human and registration intent require independent validation.'},outcome='unknown',outcome_scope='US indication-specific development',outcome_date=None,outcome_date_precision=None,us_approval=None,non_us_approval=None,terminal_failure_for_lifetime_pos=False,search_status='registry_reviewed_no_targeted_outcome_search',filters={'rare_nononcology':True,'genetically_defined_cns':cns,'genetic_medicine':genetic,'novel_target_at_entry':None,'intrathecal':it,'intracerebroventricular':icv,'protein_restoration':protein,'intrathecal_protein_restoration_neurodevelopment':bool(it and protein and cns)},filter_notes='Genetic medicine means nucleic-acid/gene-modified therapy delivered to patient; recombinant ERT production does not qualify. CNS flag requires intended direct neurologic disease treatment; systemic metabolic prevention is not automatically CNS. Novel target requires separate historical validation and remains null.',trial_evidence=[{k:t.get(k) for k in ['nct_id','title','start_date','start_date_type','phases','registry_status','why_stopped','last_update']} for t in ts],evidence=ss,notes=[])
    programs.append(p)
by={p['slug']:p for p in programs}

def note(slug,text):by[slug]['notes'].append(text)
def status(slug,outcome,claim,url,date=None,scope=None,terminal=False):
    p=by[slug];p.update(outcome=outcome,outcome_date=date,outcome_date_precision='day' if date and len(date)==10 else 'partial_or_unknown',search_status='targeted_primary_outcome_evidence',terminal_failure_for_lifetime_pos=terminal)
    if scope:p['outcome_scope']=scope
    e=evidence(url,claim,date if outcome in {'approved','ongoing'} else None)
    e['event_or_observation_date']=date
    p['evidence'].append(e);p['notes'].append(claim)
    if outcome=='ongoing':
        p['last_primary_program_observation_date']=date
        p['outcome_date']=None
        p['outcome_date_precision']='not_terminal_event'
def approval(slug,date,url,accelerated=False):
    status(slug,'approved','FDA approval for this indication; approval is an observed endpoint, not proof of initial-entry eligibility.',url,date)
    by[slug]['us_approval']={'date':date,'accelerated':accelerated,'url':url}

approval('prx102','2023-05-09','https://www.fda.gov/drugs/drug-approvals-and-databases/drug-trials-snapshots-elfabrio')
approval('avalglucosidase','2021-08-06','https://content.govdelivery.com/accounts/USFDA/bulletins/2eb9f27')
approval('ux003','2017-11-15','https://www.accessdata.fda.gov/scripts/opdlisting/oopd/detailedIndex.cfm?cfgridkey=359811')
approval('atb200','2023-09-28','https://www.fda.gov/drugs/drug-trials-snapshots/drug-trials-snapshots-pombiliti')
approval('bmn110','2014-02-14','https://www.accessdata.fda.gov/drugsatfda_docs/nda/2014/125460Orig1s000Approv.pdf')
approval('givinostat','2024-03-21','https://www.fda.gov/news-events/press-announcements/fda-approves-nonsteroidal-treatment-duchenne-muscular-dystrophy')
approval('lumasiran','2020-11-23','https://www.accessdata.fda.gov/drugsatfda_docs/nda/2020/214103Orig1s000IntegratedR.pdf')
approval('nedosiran_ph1','2023-09-29','https://downloads.regulations.gov/FDA-2024-E-0439-0002/attachment_1.pdf')
approval('srp9001','2023-06-22','https://www.fda.gov/news-events/press-announcements/fda-approves-first-gene-therapy-treatment-certain-patients-duchenne-muscular-dystrophy',True)
approval('dnl310','2026-03-24','https://www.accessdata.fda.gov/drugsatfda_docs/appletter/2026/761485Orig1s000correctedltr.pdf',True)
approval('aeb1102','2026-02-23','https://www.accessdata.fda.gov/drugsatfda_docs/appletter/2026/761211Orig1s000ltr.pdf',True)
approval('golodirsen','2019-12-12','https://investorrelations.sarepta.com/news-releases/news-release-details/sarepta-therapeutics-announces-fda-approval-vyondys-53tm',True)
approval('casimersen','2021-02-25','https://content.govdelivery.com/accounts/USFDA/bulletins/2c3e83d',True)
approval('abo102','2026-09-17','https://www.fda.gov/media/194921/download',False)
approval('dtx401','2026-08-19','https://www.fda.gov/news-events/press-announcements/fda-approves-first-therapy-patients-aged-8-years-and-older-glycogen-storage-disease-type-ia',True)
approval('viltolarsen','2020-08-12','https://www.accessdata.fda.gov/drugsatfda_docs/appletter/2020/212154Orig1s000ltr.pdf',True)
note('abo102','FDA approval restricted to pediatric patients with preserved neurodevelopmental function. Adding documented early mixed-phase NCT02716246 corrects captured 2019 later-severity trial; first study start proxy is now 2016.')
note('dtx401','Supplemental deterministic discovery repair: GSD1 condition string failed automated condition match; registry establishes GSDIa Phase I/II entry.')
note('viltolarsen','Supplemental academic-origin commercial development program. Earliest phase I sponsor was NCNP; later NS Pharma commercial program. Analyze separately if requiring industry sponsor at first exposure.')
by['viltolarsen']['eligibility']['industry_at_first_exposure']=False

status('rhhns','stopped','EMA sponsor notification: Shire terminated SHP610 on 2016-08-10; no longer candidate for divestment. This is explicit program discontinuation, not inferred from completed trial.','https://www.ema.europa.eu/en/documents/pip-discontinuation/recombinant-human-heparan-n-sulfatase-rhhns-shp610-hgt-1410-sulfamidase-san-notification-discontinuation-paediatric-development-which-covered-agreed-pip-decision_en.pdf','2016-08-10',terminal=True)
status('dcrph1','stopped','Dicerna discontinued DCR-PH1 in Q3 2016 and prioritized a distinct molecule, DCR-PHXC. Do not merge subsequent nedosiran approval into this program.','https://www.sec.gov/Archives/edgar/data/1399529/000119312516761661/d249794dex991.htm','2016',terminal=True)
status('suvodirsen','stopped','Wave discontinued development after no dystrophin increase in interim analysis.','https://ir.wavelifesciences.com/node/8361/html','2019-12-16',terminal=True)
status('ezutromid','stopped','Summit discontinued ezutromid after PhaseOut DMD failed its primary and secondary endpoints.','https://www.sec.gov/Archives/edgar/data/1599298/000159929821000011/smmt-20201231.htm','2018-06',terminal=True)
status('edasalonexent','stopped','Catabasis ceased all edasalonexent development after Phase III failed; indication-specific program stop.','https://www.sec.gov/Archives/edgar/data/1454789/000110465921102114/catb-20210630x10q.htm','2020-10',terminal=True)
for slug in ['pro045','pro053']:
    status(slug,'stopped','BioMarin discontinued BMN045 and BMN053 in May 2016; reported in contemporaneous public SEC filing.','https://www.sec.gov/Archives/edgar/data/873303/000156459016027821/srpt-10q_20160930.htm','2016-05',terminal=True)
status('pf06939926','stopped','Pfizer discontinued clinical development following negative CIFFREO efficacy findings.','https://cdn.pfizer.com/pfizercom/product-pipeline/Pipeline_Update_30JUL2024.pdf','2024-07-30',terminal=True)
status('synb1020','stopped','Synlogic explicitly discontinued SYNB1020 August 20, 2019; negative hyperammonemia result was in cirrhosis, not a UCD efficacy trial.','https://www.sec.gov/Archives/edgar/data/1527599/000156459021027177/sybx-10q_20210331.htm','2019-08-20',terminal=True)
status('srp5051','stopped','Sarepta reports decision in Q3 2024 to discontinue SRP5051; positive interim dystrophin findings did not establish favorable benefit-risk.','https://www.sec.gov/Archives/edgar/data/873303/000095017025058003/srpt-20250424.htm','2024',terminal=True)
status('sgt001','stopped','Solid 2026 SEC filing explicitly states SGT001 is no longer being developed; original pause September 2022. SGT003 is a distinct program.','https://investors.solidbio.com/node/12296/html',None,terminal=True)
status('vts270','ongoing','Adrabetadex was acquired after former sponsor cessation. Current sponsor Beren reports NDA under review with November 17, 2026 PDUFA; not terminal failure as of November 16.','https://www.berentx.com/faq',None,scope='Current sponsor US regulatory review; not approved as of review')
by['vts270']['evidence'].append(evidence('https://cdn.clinicaltrials.gov/large-docs/42/NCT04958642/Prot_000.pdf','Historical sponsor discontinued due negative benefit-risk; later transfer/redevelopment means this historical stop is not final outcome.',None,'primary_sponsor_protocol'))
status('lucerastat','ongoing','Idorsia initiated new pivotal FAB-KLEAR in October 2026 after 2021 trial failed primary endpoint; failure of one trial was not terminal program discontinuation.','https://www.idorsia.com/our-innovation/portfolio/lucerastat.html','2026-10',scope='Current sponsor clinical development evidence')
status('dtx301','ongoing','November 2026 sponsor filing reports positive Phase III ammonia endpoint; second endpoint follow-up continues into 2027.','https://ir.ultragenyx.com/static-files/83f1b349-cb50-417a-8195-c53c514af23d','2026-11-04',scope='Current sponsor clinical development evidence')
status('ux701','ongoing','Current Ultragenyx clinical pipeline and 2026 development catalysts include UX701.','https://ir.ultragenyx.com/static-files/50d9ee53-214f-4b1b-ac72-29c86e484e73','2026-11',scope='Current sponsor clinical development evidence')
status('ax250','ongoing','Spruce acquired and advances tralesinidase; November 9, 2026 sponsor update targets December 2026 BLA submission.','https://investors.sprucebio.com/node/9346/pdf','2026-11-09',scope='Current sponsor development evidence')
status('sobi003','unknown','Sobi announced intent to divest SOBI003, but a later permanent program-termination statement was not retrieved; secondary reports say discontinued.','https://www.sobi.com/en/press-releases/sobi-strengthens-focus-and-increases-investments-late-stage-development-haematology',None,scope='Sponsor divestment plan; final fate unresolved')
status('oxabact','unknown','Sponsor page describes ongoing Oxabact development but is undated/stale, referring to Phase III before known later readout. Current program state cannot be established from this page.','https://oxthera.com/clinical/',None,scope='Historical development, current outcome unresolved')
by['oxabact']['search_status']='targeted_search_unresolved_primary_program_endpoint'
note('oxabact','Sponsor explicitly describes prior Oxabact formulations before OC5 (used from late 2013); earliest molecule exposure predates captured OC5 and needs reconstruction.')
status('idursulfase_it','unknown','Sponsor-affiliated original study publication reports data insufficient for regulatory filings while OLE access continues. Registration-directed program cessation date is not established by this sentence.','https://onlinelibrary.wiley.com/doi/full/10.1002/jimd.12790',None,scope='Regulatory development barrier with continued treatment access')
by['idursulfase_it']['search_status']='targeted_search_unresolved_primary_program_endpoint'
by['idursulfase_it']['evidence'][-1]['source_type']='primary_clinical_publication'
by['synb1020']['eligibility']['mixed_indication_requires_split']=True
by['synb1020']['eligibility']['indication_specific_inception_confirmed']=False
by['synb1020']['eligibility']['registry_entry_reference_cohort']=None
by['synb1020']['eligibility']['reason']='Healthy-volunteer hyperammonemia platform program subsequently tested in cirrhosis. Rare UCD-specific inception is unresolved; do not count as clean UCD failure.'
status('bmn701','stopped','BioMarin ceased its own program for competing corporate priorities and left external development possible; sponsor exit is not irreversible worldwide biological failure.','https://www.worldpompe.org/images/pdfs/2016-06-22_Biomarin_Pompe_Community_Update.pdf','2016-06-22',scope='Sponsor development cessation; external development not ruled out',terminal=False)

# Registry reasons that explicitly concern the PROGRAM are accepted; status alone is never used.
for slug,n in [('sbc103','NCT02618512'),('abo101','NCT03315182'),('hmi102','NCT03952156'),('hmi103','NCT05222178'),('hmi203','NCT05238324'),('mrt5201','NCT03767270'),('avrrd02','NCT04145037')]:
    t=trials[n]
    status(slug,'stopped','Explicit sponsor registry statement: '+t['why_stopped'],'https://clinicaltrials.gov/study/'+n,None,scope='Sponsor program discontinuation; event date unavailable',terminal=False)
    by[slug]['evidence'][-1]['source_date']=t.get('last_update')
    by[slug]['evidence'][-1]['source_type']='primary_trial_registry_explicit_program_statement'
    note(slug,'Do not use registry last-update date as discontinuation date. No complete global successor/license search; stopped remains sponsor-scoped, not a forced terminal lifetime failure.')
for slug,n,label in [('val1221','NCT02898753','Company closure/lack of funding'),('avrrd01','NCT03454893','Sponsor deprioritized Fabry'),('flt190','NCT04040049','Sponsor paused program to prioritize FLT201'),('lysgm101','NCT04273269','Sponsor ceased activities')]:
    t=trials[n];status(slug,'unknown',label+'; '+t['why_stopped'],'https://clinicaltrials.gov/study/'+n,None,scope='Sponsor exit/pause; global program fate unresolved')
    by[slug]['evidence'][-1]['source_date']=t.get('last_update')
for slug,n in [('rgx111','NCT03580083'),('rtx134','NCT04110496'),('ux053','NCT04990388'),('asp2016','NCT06483802'),('mrna3210','NCT06147856')]:
    note(slug,'Trial cessation/hold/withdrawal is not sufficient to classify the whole program: '+trials[n].get('why_stopped',''))

jcr='https://www.jcrpharm.co.jp/en/assets/uploads/docs/FY2026-Q2_Results_Briefing_Session_EN.pdf'
for slug in ['jr141','jr171','jr441','jr446']:
    status(slug,'ongoing','Sponsor October 2026 pipeline identifies active development/partnering; no US approval asserted.',jcr,'2026-10-29',scope='Sponsor current development evidence; future outcome censored')
by['jr141']['non_us_approval']={'jurisdiction':'Japan','date':'2021-03','url':'https://www.jcrpharm.co.jp/en/assets/uploads/docs/ir_library_annual_171261_00.pdf'}
by['gc1111']['non_us_approval']={'jurisdiction':'South Korea','date':'2012','url':'https://global-greencross.com/eng/research/global_project.html'}
by['saer']['non_us_approval']={'jurisdiction':'Japan','date':'2024-03-26','url':'https://www.nobelpharma.co.jp/en/news/20240326-p1309/'}
for slug in ['gc1111','saer']:
    x=by[slug]['non_us_approval'];by[slug]['search_status']='targeted_primary_non_US_approval_US_outcome_unresolved';by[slug]['evidence'].append(evidence(x['url'],'Non-US approval verified; never count this as FDA approval.',x['date']))

# First-human exclusions and precise eligibility distinctions.
def prior(slug,reason,url=None,date=None):
    p=by[slug];p['eligibility'].update(registry_entry_reference_cohort=False,verified_first_human_2010_2024=False,repurposed_or_prior_human_exposure=True,reason=reason);p['first_human_entry_confidence']='earlier_exposure_evidence_excludes_de_novo_inception';p['notes'].append(reason)
    if url:p['evidence'].append(evidence(url,reason,date))
prior('bmn110','BioMarin announced Phase 1/2 initiation April 21, 2009. Captured 2010+ studies are not first clinical entry.','https://www.biomarin.com/news/press-releases/biomarin-initiates-phase-1-2-clinical-trial-for-galns-for-morquio-a-syndrome/','2009-04-21')
prior('migalastat','FDA review documents AT1001 Phase I healthy-volunteer study in 2004; post-2010 PK trials are not new program entry.','https://www.accessdata.fda.gov/drugsatfda_docs/nda/2018/208623Orig1s000MultidisciplineR.pdf','2018')
prior('olipudase','Earlier clinical study NCT00410566 predates 2010; registry-panel first observation is left-truncated.','https://clinicaltrials.gov/study/NCT00410566')
prior('eliglustat','Already approved for Gaucher disease before the captured 2015 formulation/PK studies; these are later-stage observations.','https://www.accessdata.fda.gov/drugsatfda_docs/nda/2014/205494Orig1s000Approv.pdf','2014-08-19')
for slug in ['ambroxol','trientine','teta4hcl','rvx000222','givinostat']:
    by[slug]['eligibility'].update(registry_entry_reference_cohort=False,verified_first_human_2010_2024=None,repurposed_or_prior_human_exposure=True,reason='Existing drug or previous development outside this indication; not a clean new-molecule first-human inception. Exact original exposure date requires separate validation.')
for slug in ['isu302','biosidus_agalsidase']:
    by[slug]['eligibility'].update(registry_entry_reference_cohort=False,reason='Follow-on version of established replacement enzyme; excluded from novel-asset calibration, retained for comparator sensitivity.')
for slug in ['hepastem','can103']:
    by[slug]['eligibility'].update(registry_entry_reference_cohort=None,mixed_indication_requires_split=True,reason='Mixed rare-disease cohort; separate indication entry/outcome cannot be assumed. Retain, do not multiply sample size.')
for slug in ['ucmsc','en001']:
    by[slug]['eligibility'].update(registry_entry_reference_cohort=None,reason='Cell-product identity and registration-directed development insufficiently resolved.')
for slug in ['mrt5201','asp2016','mrna3210']:
    by[slug]['eligibility']['verified_first_human_2010_2024']=None
    note(slug,'Withdrawal/non-recruitment may mean no human exposure. Registry start date alone cannot prove clinical entry; check enrollment and first-dose announcement.')
note('idursulfase_it','Route extension of established IV idursulfase: eligible only as a new CNS-delivery program, not new molecule. Captured lead study is extension; first intrathecal entry needs reconstruction.')
note('abo102','Captured NCT04088734 concerns advanced MPS IIIA and was stopped for lack of efficacy in that group. It does not establish whole UX111 program failure; earlier NCT02716246 exists. Do not infer first entry from 2019 advanced-disease trial.')
note('nedosiran_ph1','FDA approval applies to PH1; early trial also included PH2. PH2 cannot inherit the PH1 approval. Original mixed-indication cohort not two independent trials.')
note('nedosiran_ph3','Later indication expansion of same molecule, not independent first-human program. PH1 approval is not PH3 approval.')
by['nedosiran_ph3']['eligibility'].update(registry_entry_reference_cohort=False,verified_first_human_2010_2024=False,repurposed_or_prior_human_exposure=True,reason='Later indication trial of nedosiran already exposed in humans in PH1/2.')
by['pr001_gd1']['eligibility'].update(registry_entry_reference_cohort=False,verified_first_human_2010_2024=False,repurposed_or_prior_human_exposure=True,reason='Later indication program for PR001 after neuronopathic Gaucher/Parkinson development.')
note('pr001_gd2','PR001 also developed in Parkinson disease; global first-human versus Gaucher entry needs independent sequencing.')
note('gc301','Infantile and late-onset Pompe retained as a single molecular program, with phenotype-extension flag; do not count as independent genetic therapies.')
note('atb200','One development regimen: enzyme plus stabilizer. Miglustat has prior human use, but new enzyme program is retained; avoid two successes for combination.')
note('rt001','FARA (research funder/participant-support organization) reports sponsor notification of negative Phase II/III and inactive program. Targeted source search did not retrieve sponsor/regulator discontinuation; outcome remains unknown under strict primary endpoint rule.')
by['rt001']['search_status']='targeted_search_unresolved_primary_program_endpoint'
by['rt001']['evidence'].append(evidence('https://www.curefa.org/drug-development/rt001/','FARA directly funded research and reports notification by Retrotope of negative February 2022 result; inactive designation. Retained as contextual, not strict sponsor stop adjudication.',None,'research_funder_and_patient_organization'))

# Record unsuccessful targeted searches; no silence-to-failure conversions.
searched_unknown={
 'dmpkrx':'Ionis DMPK discontinued; MDA reports program stopped but no sponsor/regulator source retrieved in bounded pass.',
 'ht100':'HT100 discontinued; secondary reviews and trial dosing stop found, insufficient primary program-level endpoint.',
 'vp20629':'VP20629/SHP622 development Shire; historical clinical evidence retrieved but current disposition unresolved.',
 'synb1618':'Synlogic SYNB1618 discontinued: primary filings explicitly address SYNB1934 successor; do not transfer failure without asset-specific statement.',
 'sb318':'SB318 no further development Sangamo; rollover into long-term follow-up does not prove asset death.',
 'sb913':'SB913 discontinued Sangamo; long-term follow-up is not program termination.',
 'agt181':'AGT181 AGT182 discontinued; no primary terminal statement retrieved.',
 'agt182':'AGT182 development 2025; no primary terminal statement retrieved.',
 'prx112':'PRX112 discontinued Protalix; primary 2014 phase II initiation found, current fate unresolved.',
 'isu302':'ISU302 Abcertin approved; sponsor exchange filing and trial publication support identity, exact regulatory endpoint remains unverified in this slice.'}
for slug,txt in searched_unknown.items():
    if by[slug]['outcome']=='unknown':by[slug]['search_status']='targeted_search_unresolved_primary_program_endpoint'
    note(slug,txt)

# Final assertions and deterministic outputs.
status('ds5141b','stopped','Daiichi FY2022 Q4 reference data explicitly lists renadirsen/DS5141 as discontinued at Phase II: difficult to advance with available data.','https://www.daiichisankyo.com/files/investors/library/quarterly_result/2022/FY2022_Q4_ReferenceData_E4.pdf','2023',terminal=True)
by['ds5141b']['aliases'].append('Renadirsen sodium')
status('idua_lvv','ongoing','Kyowa Kirin November 2, 2026 presentation identifies OTL203 Hurler registrational trial as ongoing.','https://ir.kyowakirin.com/en/library/earnings/earnings0/main/0118/teaserItems1/00/linkList/01/link/presentation_2026_q3_en.pdf','2026-11-02',scope='Sponsor registrational development evidence')
status('mossagal','ongoing','Eleva/manufacturing-partner February 2025 release identifies aGal/RPV001 Fabry program in development with Phase Ib data; latest primary evidence is 2025, not a verified 2026 milestone.','https://3pbiovian.com/wp-content/uploads/2025/02/Press-release_-Eleva-and-3PBIOVIAN_-04022025.pdf','2025-02-04',scope='Last observed sponsor development, subsequent outcome unverified')
status('actus101','unknown','Bayer 2025 annual report states ACTUS101 no longer recruits and will complete with enrolled patients; AB1009 is a distinct successor. Do not call primary program permanently stopped on trial closure alone.','https://reports.bayer.com/annual-report-2025/en/_assets/downloads/entire-bayer-ar25.pdf',None,scope='Sponsor trial wind-down; exact program endpoint unresolved')
by['actus101']['search_status']='targeted_search_unresolved_primary_program_endpoint'
for slug in ['saf301','lyssaf302','lysgm101']:
    by[slug]['evidence'].append(evidence('https://www.amf-france.org/sites/institutionnel/files/private/2025-05/san-2025-04.pdf','French market regulator records Lysogene judicial liquidation May 25, 2023. Corporate failure alone does not establish no later licensing/revival of each molecule.','2025-05','primary_financial_regulator'))
    if by[slug]['outcome']=='unknown':by[slug]['search_status']='targeted_search_unresolved_primary_program_endpoint'
    note(slug,'Sponsor judicial liquidation is verified; no definitive global successor ownership or program-revival resolution in this bounded audit.')
for slug,claim in {
    'gc1119':'GC1119 Fabry Green Cross query returned registry and historical sponsor pipeline; no primary current endpoint found.',
    'hepastem':'HepaStem urea-cycle development query returned primary patent and long-term follow-up; no distinct UCD versus Crigler-Najjar outcome established.',
    'raav25naglu':'uniQure Sanfilippo B/AMT110 discontinued query located secondary discontinuation report but no sponsor/regulator terminal source retrieved. Remains unknown.'
}.items():
    by[slug]['search_status']='targeted_search_unresolved_primary_program_endpoint';note(slug,claim)
by['raav25naglu']['aliases'].append('AMT110 (secondary alias lead; further primary verification needed)')
by['dt216']['filters']['protein_restoration']=True
by['rhhns']['evidence'].append(evidence('https://cdn.clinicaltrials.gov/large-docs/27/NCT01299727/SAP_001.pdf','Sponsor SAP states Phase IIb did not meet efficacy criteria or demonstrate clinical proof of concept and all MPS IIIA program studies discontinued.','2016-10-31','primary_sponsor_statistical_analysis_plan'))
for p in programs:
    p['priority_candidate_ids']=[i for i in p['candidate_ids'] if i in priority_ids]
    p['supplemental_candidate_ids']=[i for i in p['candidate_ids'] if i in supplemental_ids]
    p['trial_enrollment_evidence']=[]
    for n in p['nct_ids']:
        ps=raw.get(n,{}); e=ps.get('designModule',{}).get('enrollmentInfo',{}); st=ps.get('statusModule',{})
        p['trial_enrollment_evidence'].append({'nct_id':n,'enrollment_count':e.get('count'),'enrollment_type':e.get('type'),'status':st.get('overallStatus'),'start':st.get('startDateStruct')})
    zero=[e for e in p['trial_enrollment_evidence'] if e['enrollment_count']==0 and e['enrollment_type']=='ACTUAL' and e['status']=='WITHDRAWN']
    if zero:
        note(p['slug'],'At least one withdrawn study enrolled zero participants; never use that trial as actual first human dosing.')
    if len(zero)==len(p['nct_ids']):
        p['eligibility'].update(registry_entry_reference_cohort=False,verified_first_human_2010_2024=False,reason='All captured studies withdrawn with ACTUAL enrollment zero. Preserve pre-dose attrition separately; not eligible clinical-inception denominator without other dosing evidence.')
        p['first_human_entry_confidence']='no_dosing_in_captured_program_trials'
        p['entry_date_proxy_valid_for_human_exposure']=False
    else:p['entry_date_proxy_valid_for_human_exposure']=None
    p['eligibility_status']='reference_eligible' if p['eligibility']['registry_entry_reference_cohort'] is True else ('excluded' if p['eligibility']['registry_entry_reference_cohort'] is False else 'unresolved')
    p['endpoint_bucket']='FDA_approved' if p['us_approval'] else ('confirmed_permanent_stop' if p['terminal_failure_for_lifetime_pos'] else 'all_others')
    p['first_human_confidence_reason']='Specific global first-dose announcement was not retrieved. '+p['first_human_entry_confidence']
    if p['first_human_registry_language_nct_ids']:
        p['first_human_confidence_reason']='Registry explicitly describes first-in-human study; trial start is still not independently proven first dosing and earlier global exposure has not been excluded.'
for d in dispositions:
    d['frame']='priority_early_industry' if d['candidate_id'] in priority_ids else 'supplemental_discovery_repair'
assert len(dispositions)==len(selected)
assert len({d['candidate_id'] for d in dispositions})==len(selected)
assert sum(len(p['candidate_ids']) for p in programs)+sum(d['program_id'] is None for d in dispositions)==len(selected)
for p in programs:
    p['approved_in_US']=p['us_approval'] is not None
    p['filters']['novel_target_genetic_medicine']=None if p['filters']['novel_target_at_entry'] is None else bool(p['filters']['novel_target_at_entry'] and p['filters']['genetic_medicine'])
    p['evidence_urls']=list(dict.fromkeys(e['url'] for e in p['evidence']))
programs.sort(key=lambda p:(p['entry_date_proxy'],p['program_id']))
coverage={'as_of':ASOF,'selection':'Every priority_early_industry bucket with lysosomal/metabolic family or structured DMD/GNE/DM1/Friedreich disease match; SMA/ALS excluded. Six explicit supplemental discovery repairs for mixed-phase/condition-screen/academic-origin programs. Not the complete worldwide drug-development denominator.','candidate_count':len(selected),'priority_candidate_count':len(priority_ids),'supplemental_candidate_count':len(supplemental_ids),'mapped_program_count':len(programs),'excluded_candidate_count':sum(d['program_id'] is None for d in dispositions),'outcomes':dict(Counter(p['outcome'] for p in programs)),'search_status_counts':dict(Counter(p['search_status'] for p in programs)),'reference_eligibility_counts':dict(Counter(str(p['eligibility']['registry_entry_reference_cohort']) for p in programs)),'limitations':['Canonicalized finite discovery frame, not a census of all clinical entrants.','First-human dates remain mostly study-start proxies and cannot be used as independently validated clinical inception.','US approval endpoint kept separate from non-US approvals.','Explicit sponsor program stops retained separately from irreversible lifetime failures; unknown is not failure.','Current pipeline/trial activity cannot by itself identify eventual approval probability; recent entrants are right-censored.','CNS and genetic-medicine flags operationally distinct; recombinant enzyme manufacture is not gene therapy.','Untargeted outcome rows are explicitly distinguishable from researched-but-unresolved rows.'],'model_ready_lifetime_pos':False}
OUT.mkdir(exist_ok=True)
for name,obj in [('metabolic_program_ledger.json',programs),('metabolic_candidate_dispositions.json',dispositions),('metabolic_coverage.json',coverage)]:
    (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(coverage,indent=2))
