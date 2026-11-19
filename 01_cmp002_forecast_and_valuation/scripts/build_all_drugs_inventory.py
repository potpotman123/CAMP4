"""Audit unrestricted Evaluate inventory; no PoS inferred from cross-sectional data."""
import collections,csv,gzip,hashlib,io,json,re
from pathlib import Path
P=Path(__file__).resolve().parents[1]
S=P/'sources/evaluate_expansion_2026-11-19'
O=P/'data/pos_all_drugs_expansion';O.mkdir(exist_ok=True)
source=S/'all_status_all_indications.csv.gz'
def missing(v):return not v or v=='-'
fields={'names':'Product','generic_names':'Generic Name','research_codes':'Research Codes',
 'technologies':'Technology','mechanisms':'Mechanism of Action','ww_statuses':'WW Indication Status (Current)',
 'us_statuses':'USA Indication Status (Current)','fda_product_dates':'FDA Approval Date',
 'fda_indication_dates':'FDA Approval Date (Indication)','ind_dates':'US IND Filing Date'}
inventory={};raw_count=0;raw_status=collections.Counter();raw_date_counts=collections.Counter()
with gzip.open(source,'rt',encoding='utf-8-sig',newline='') as f:
 for line,r in enumerate(csv.DictReader(f),2):
  raw_count+=1;key=(r['Unique Product Records|Record Id'],r['Indication Level 3'])
  if key not in inventory:
   inventory[key]={k:set() for k in fields}|{'source_rows':[],'company_record_ids':set(),'vendor_indication_record_ids':set()}
  x=inventory[key];x['source_rows'].append(line);x['company_record_ids'].add(r['Products|Record Id']);x['vendor_indication_record_ids'].add(r['Indications|Record Id'])
  raw_status[r['WW Indication Status (Current)']]+=1
  for target,col in fields.items():
   if not missing(r[col]):x[target].add(r[col])
  for c in ['FDA Approval Date','FDA Approval Date (Indication)','US IND Filing Date']:
   raw_date_counts[c]+=not missing(r[c])
records=[]
for (pid,disease),x in sorted(inventory.items()):
 r={k:sorted(v) if isinstance(v,set) else v for k,v in x.items()}
 r.update(candidate_pair_id='EV-'+pid+'-'+hashlib.sha256(disease.encode()).hexdigest()[:12],vendor_product_id=pid,vendor_indication=disease)
 statuses=x['ww_statuses']
 r['clinical_stage_signal']=any(re.search(r'Phase (?:III|II|I)\b|Filed|Approved|Marketed|Withdrawn',s) for s in statuses)
 r['active_clinical_signal']=any(s in ['Phase I','Phase II','Phase III','Filed'] for s in statuses)
 r['abandoned_clinical_signal']=any(s.startswith('Abandoned') and re.search(r'Phase (?:III|II|I)\b|Filed',s) for s in statuses)
 r['active_abandoned_disagreement']=r['active_clinical_signal'] and r['abandoned_clinical_signal']
 r['date_conflict_fields']=[k for k in ['fda_product_dates','fda_indication_dates','ind_dates'] if len(x[k])>1]
 r['clinical_entry_verified']=False
 r['rare_indication']=None;r['cns_indication']=None;r['aso_verified']=None;r['intrathecal_verified']=None
 r['eligible_for_pos']=False
 records.append(r)
with (O/'candidate_pairs.jsonl.gz').open('wb') as out:
 with gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0) as z:
  for r in records:z.write((json.dumps(r,separators=(',',':'),ensure_ascii=False)+'\n').encode())
clinical=[r for r in records if r['clinical_stage_signal']]
def coverage(rs):
 return {'n':len(rs),'with_ind_date':sum(bool(r['ind_dates']) for r in rs),
  'with_indication_fda_date':sum(bool(r['fda_indication_dates']) for r in rs),
  'with_product_fda_date':sum(bool(r['fda_product_dates']) for r in rs),
  'conflicting_ind_dates':sum(len(r['ind_dates'])>1 for r in rs),
  'conflicting_indication_fda_dates':sum(len(r['fda_indication_dates'])>1 for r in rs)}
summary=dict(retrieved='2026-11-19',scope='Unrestricted Evaluate company/product/indication/current-status inventory; no clinical-entry date restriction yet',
 raw_rows=raw_count,vendor_products=len({r['vendor_product_id'] for r in records}),vendor_indication_labels=len({r['vendor_indication'] for r in records}),
 all_candidates=coverage(records),clinical_signal_candidates=coverage(clinical),
 blank_ww_status_pairs=sum(not r['ww_statuses'] for r in records),
 active_abandoned_disagreements=sum(r['active_abandoned_disagreement'] for r in records),
 raw_status_counts=dict(raw_status),raw_date_counts=dict(raw_date_counts),
 rare_disease_count=None,pos=None,reason_no_pos='No first-dosing or dated phase-transition history field; IND dates are sparse and not dosing dates; indication rarity and canonical identities not yet adjudicated.')
# Fixed, reproducible coverage sample; NOT an outcome-rate denominator.
strata=collections.defaultdict(list)
for r in clinical:
 if r['fda_indication_dates']:group='vendor_fda_date_present'
 elif r['active_clinical_signal'] and not r['abandoned_clinical_signal']:group='active_clinical_no_fda_date'
 elif r['abandoned_clinical_signal'] and not r['active_clinical_signal']:group='abandoned_clinical_no_fda_date'
 else:group='other_or_disputed_clinical'
 strata[group].append(r)
sample=[]
for group,rows in sorted(strata.items()):
 rows.sort(key=lambda r:hashlib.sha256(('20261119-pos-quality-'+r['candidate_pair_id']).encode()).hexdigest())
 for r in rows[:6]:sample.append(dict(r,sampling_stratum=group,review_status='pending'))
assert len(sample)==24 and len({r['candidate_pair_id'] for r in sample})==24
assert sum(len(v) for v in strata.values())==len(clinical)
assert raw_count==350769
assert len(records)==199342
assert sum(len(r['source_rows']) for r in records)==raw_count
summary['pilot_strata_sizes']={k:len(v) for k,v in strata.items()}
(O/'coverage_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(O/'quality_sample_24.json').write_text(json.dumps(sample,indent=2)+'\n')
(O/'indication_labels.json').write_text(json.dumps(dict(collections.Counter(r['vendor_indication'] for r in records)),indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['raw_status_counts']},indent=2))
for r in sample:print(r['sampling_stratum'],r['names'][0],r['generic_names'],r['vendor_indication'])
