"""Exhaustive auditable screening of the saved discovery panel. Not outcome adjudication."""
import json,re,hashlib,unicodedata
from pathlib import Path
from collections import Counter,defaultdict
P=Path(__file__).resolve().parents[1];D=P/'data/pos_adjudication';D.mkdir(exist_ok=True)
load=lambda f:json.loads((P/f).read_text())
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s.lower()).encode('ascii','ignore').decode())
# Only structured condition fields are screened; query match alone is insufficient.
rules={
'Angelman':r'angelman','Dravet':r'dravet','Rett':r'rett','Fragile_X':r'fragile.?x','SYNGAP1':r'syngap1','CDKL5':r'cdkl5','Lennox_Gastaut':r'lennox.?gastaut',
'Huntington':r'huntington','SCA':r'spinocerebellar','Alexander':r'alexander','NCL':r'batten|ceroid|cln[1235678]|jansky','Lafora':r'lafora','ALD':r'adrenoleuko|adrenomyelo','MLD':r'metachromatic',
'SMA':r'spinal muscular|muscular atrophy, spinal','DMD':r'duchenne','GNE':r'gne myopathy|hereditary inclusion|nonaka|rimmed vacuol','ALS':r'amyotrophic|\bals\b|motor neuron','Friedreich':r'friedreich','DM1':r'myotonic dystrophy',
'Pompe':r'pompe|glycogen storage.*(?:ii\b|type 2)|acid maltase','Fabry':r'fabry','Gaucher':r'gaucher','Niemann_Pick_ASMD':r'niemann|sphingomyelin|sphingomyelinase',
'MPS':r'mucopolysaccharid|\bmps\b|hunter|hurler|sanfilippo|morquio|sly syndrome','GM1':r'gm1','GM2':r'gm2|tay.?sachs|sandhoff',
'PKU':r'phenylketon|\bpku\b','UCD':r'urea cycle|ornithine|hyperargin|arginase.*deficien','PH':r'primary hyperoxal','Wilson':r'wilson','GSD':r'glycogen storage','HPP':r'hypophosphatasia',
'Hemophilia':r'h[ae]emophilia','SCD':r'sickle|\bhb.?sc\b','Thalassemia':r'thalass[ae]mia','PNH':r'paroxysmal.*(?:hemoglobin|haemoglobin)|paroxysmal hemoglobinuria|\bpnh\b',
'Achondroplasia':r'achondroplasia','HAE':r'hereditary angioedema|\bhae\b','CF':r'cystic fibrosis|\bcf\b','PAH':r'pulmonary arterial hypertension|hypertension, pulmonary','EB':r'epidermolysis','PBC':r'primary biliary',
'WAS':r'wiskott','SCID':r'severe combined immun|\bscid\b','CGD':r'chronic granulomatous','aPAP':r'autoimmune pulmonary alveolar|pulmonary alveolar proteinosis'}
trials={x['nct_id']:x for x in load('data/pos_nested/trial_inventory.json')};cs=load('data/pos_nested/candidate_review_queue.json');prior=load('data/pos_audit/program_ledger.json')
core_by_nct=defaultdict(list)
for r in prior:core_by_nct[r['entry_trial']].append(r)
out=[]
for b in cs:
 t=[trials[n] for n in b['nct_ids']];condition=' | '.join(b['conditions']).lower();matches=[k for k,v in rules.items() if re.search(v,condition)]
 x={'candidate_id':b['candidate_id'],'name':b['intervention_name'],'conditions':b['conditions'],'nct_ids':b['nct_ids'],'structured_disease_matches':matches,'disposition':None,'reason':None,'rule_evidence':{},'program_outcome':None,'approval_probability_input_eligible':False}
 if not matches:
  x['disposition']='review_condition_mismatch';x['reason']='No structured-condition match to explicit panel dictionary; query expansion/healthy subjects/rare synonyms require review, not automatic exclusion.'
 elif re.search(r'placebos?|\bnormal saline\b|\bnacl\b|matched.*control',b['intervention_name'],re.I):
  x['disposition']='exclude_control_name';x['reason']='Control-specific name; preserved for audit.'
 elif not b['entry_window_candidate']:
  x['disposition']='outside_proposed_entry_window';x['reason']='Earliest observed same-name/condition record before2010 or unknown; not necessarily true first human entry.'
 else:
  first=b['earliest_observed_panel_trial_date'];first_trials=[q for q in t if q['start_date']==first]
  early=any(set(q['phases']) & {'PHASE1','EARLY_PHASE1'} for q in first_trials)
  industry=any(q['sponsor'].get('class')=='INDUSTRY' for q in first_trials)
  prior_ap=[f for f in b['fda_matches'] if f['original_approval_date'] and f['original_approval_date']<first]
  x['rule_evidence']={'earliest_observed_trial_date':first,'earliest_trials':[q['nct_id'] for q in first_trials],'early_phase_label_now':early,'industry_led_earliest_record':industry,'prior_approval_name_matches':prior_ap}
  if prior_ap:x['disposition']='review_prior_approval';x['reason']='Prior ingredient/brand approval may indicate repurposing, background treatment or follow-on formulation; indication/identity not automatically resolved.'
  elif early and industry:x['disposition']='priority_early_industry';x['reason']='Candidate commercial early-phase entry, subject to alias/first-human/indication/outcome adjudication.'
  elif early:x['disposition']='review_early_nonindustry';x['reason']='Academic/public-led trials may initiate commercial drugs; retained, not discarded.'
  else:x['disposition']='review_entry_stage';x['reason']='First found study is not currently Phase1; could be mixed-phase relabeling, missed earlier trial or later-stage entry.'
 # Attach references, but an NCT co-occurrence never proves intervention identity.
 x['prior_reference_links']=[{'asset':r['asset'],'indication':r['indication'],'status':r['status_asof'],'entry_trial':r['entry_trial']} for n in b['nct_ids'] for r in core_by_nct[n]]
 out.append(x)
# Group obvious dose variants into SUGGESTIONS, not automatic merges.
suggestions=defaultdict(list)
for x in out:
 n=x['name'].lower();n=re.sub(r'\b\d+(?:\.\d+)?\s*(?:mg|mcg|ug|µg|ml)(?:/kg)?\b','',n);n=re.sub(r'\b(low|high|medium|higher|lower|single|multiple)\s+dose\b','',n);n=re.sub(r'\s+',' ',n).strip()
 k=norm(n)+'|'+'|'.join(sorted(x['structured_disease_matches']))
 if len(norm(n))>4:suggestions[k].append(x['candidate_id'])
merge=[{'suggestion_key':k,'candidate_ids':v,'decision':'unadjudicated'} for k,v in suggestions.items() if len(v)>1]
summary={'input_candidate_buckets':len(cs),'screened':len(out),'disposition_counts':dict(Counter(x['disposition'] for x in out)),'suggested_identity_groups':len(merge),'new_outcome_adjudications':0,'full_empirical_pos_analysis_complete':False,'rate_estimate':None}
(D/'full_screen.json').write_text(json.dumps(out,indent=2)+'\n');(D/'identity_review_suggestions.json').write_text(json.dumps(merge,indent=2)+'\n');(D/'screen_summary.json').write_text(json.dumps(summary,indent=2)+'\n');(D/'structured_condition_rules.json').write_text(json.dumps(rules,indent=2)+'\n')
assert len({x['candidate_id'] for x in out})==len(cs)
assert sum(summary['disposition_counts'].values())==len(cs)
assert all(x['program_outcome'] is None for x in out)
print(json.dumps(summary,indent=2))
