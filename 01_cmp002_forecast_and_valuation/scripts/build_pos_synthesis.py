"""Frozen peer membership and assumption-driven sensitivity; no fitted posterior."""
import json, hashlib
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1]
D=P/'data/pos_synthesis'
ledger=P/'data/pos_audit/program_ledger.json'
rows=json.loads(ledger.read_text())
closest_names={'zorevunersen','apazunersen','rugonersen','obudanersen'}
rationale={
'zorevunersen':('SCN1A haploinsufficiency in Dravet; pediatric DEE, seizure burden, protein restoration and intrathecal ASO delivery.','Splicing-based restoration rather than regRNA modulation; different neuronal target and endpoints.'),
'apazunersen':('UBE3A restoration in Angelman; pediatric neurodevelopment, intrathecal dosing, cognition/function assessment. Failed pivotal provides disconfirming evidence.','Imprinted paternal allele unsilencing; three Angelman assets share disease/target and are correlated.'),
'rugonersen':('Same pediatric protein-restoration and clinical measurement problems; distinct ASO provides molecule-level contrast.','Angelman/UBE3A correlation; EEG biomarker is not established SYNGAP1 efficacy surrogate.'),
'obudanersen':('Protein restoration in Angelman with repeated intrathecal dosing; relevant functional and developmental trial design.','Angelman/UBE3A correlation; positive early uncontrolled signals are not demonstrated pivotal success.')}
closest=[]
for r in rows:
 if r['asset'] in closest_names:
  x=dict(r);x['why_selected'],x['key_mismatch']=rationale[r['asset']]
  x['biological_cluster']='SCN1A_Dravet' if r['asset']=='zorevunersen' else 'UBE3A_Angelman'
  closest.append(x)
# Preserve indication rows; collapse only for explicitly asset-level descriptive diagnostics.
eligible=[r for r in rows if r['genetically_defined_population'] and r['novel_target_at_entry'] and not r['prior_human_data_before_entry']]
outer=[r for r in eligible if r['asset'] not in closest_names]
def diagnostic(rs):
 assets={r['asset']:r for r in rs}
 counts=Counter(r['status_asof'] for r in assets.values())
 a=counts['approved']; stopped=sum(v for k,v in counts.items() if k.startswith('stopped_')); u=len(assets)-a-stopped
 return {'asset_n':len(assets),'indication_pair_n':len(rs),'asset_status_counts':dict(counts),'approved':a,'stopped':stopped,'unresolved':u,'eventual_approval_fraction_bounds_if_stops_permanent':[a/len(assets),(a+u)/len(assets)],'interpretation':'Selected-sample outcome bounds, NOT population PoS or confidence intervals; stops assumed permanent; no independence assumed.'}
bench=[{'name':'All indications','p':.079,'location':'Figure 5b, printed p11; observation period 2011–2020'}, {'name':'Neurology','p':.059,'location':'Figure 5b, printed p11; observation period 2011–2020'}, {'name':'Non-oncology rare disease','p':.17,'location':'Figure 8b, printed p14; observation period 2011–2020'}]
def adjust(p,m):return p*m/(1-p+p*m)
for b in bench:
 b['source']='https://go.bio.org/rs/490-EHZ-999/images/ClinicalDevelopmentSuccessRates2011_2020.pdf'
 b['odds_multiplier_to_25pct']=(.25/.75)/(b['p']/(1-b['p']))
 b['sensitivity']=[{'assumed_net_odds_multiplier':m,'probability':adjust(b['p'],m)} for m in [.5,.75,1,1.5,2,3,4]]
output={'as_of':'2026-11-16','input_sha256':hashlib.sha256(ledger.read_bytes()).hexdigest(),'target':'Eventual US approval in SYNGAP1 from current cleared/pre-first-human-data stage; additional territorial approvals require separate conditional assumptions.','closest_four':closest,'middle_including_closest':eligible,'middle_incremental_excluding_closest':outer,'middle_rules':'Intrathecal ASO; genetically defined CNS indication; novel target at entry; no earlier human exposure. Limited to v1 discovered ledger, not exhaustive inception cohort.','middle_exclusions':{'salanersen':'Validated-target follow-on','ulefnersen':'Individualized human treatment preceded group-trial entry; retain as supporting sensitivity evidence'},'diagnostics':{'closest':diagnostic(closest),'middle_inclusive':diagnostic(eligible),'middle_incremental':diagnostic(outer)},'benchmarks':bench,'model':'p_adjusted = p0*M / (1-p0+p0*M). M is an assumed net odds multiplier, NOT an estimated likelihood ratio. Benchmarks are alternative anchors, not independent observations.','fitted_posterior':None,'reason':'Incomplete selected cohorts; unresolved outcomes; correlated disease/target clusters; stage mismatch. No valid numerical incremental likelihood identified.','recency':'Recent close peers primary mechanistic evidence; older successes supporting delivery/platform evidence only. No arbitrary date-weighting of unresolved outcomes. No verified current-regime broad probability obtained.'}
D.mkdir(parents=True,exist_ok=True)
(D/'three_tier_synthesis_2026-11-16.json').write_text(json.dumps(output,indent=2)+'\n')
(D/'closest_biological_clinical_peers_2026-11-16.json').write_text(json.dumps({'as_of':output['as_of'],'selection':'Biological/clinical rationale set, NOT exhaustive preclinical inception cohort','members':closest,'status_summary':diagnostic(closest),'sources':'../pos_audit/source_registry.json; member registry and status source references preserved'},indent=2)+'\n')
assert len(closest)==4
assert not ({r['asset'] for r in outer}&closest_names)
assert {r['id'] for r in eligible}==({r['id'] for r in outer}|{r['id'] for r in closest})
assert all(abs(adjust(b['p'],b['odds_multiplier_to_25pct'])-.25)<1e-12 for b in bench)
assert all(abs(adjust(b['p'],1)-b['p'])<1e-12 for b in bench)
print(json.dumps(output['diagnostics'],indent=2))
print('Membership, overlap, identity and 25% hurdle checks passed.')
