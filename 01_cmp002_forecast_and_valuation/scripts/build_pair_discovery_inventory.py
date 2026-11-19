"""Reconstruct candidate indication records from the frozen Evaluate exports.

Discovery inventory only: vendor identities/statuses are not adjudicated clinical
programmes. Never calculates PoS from current phases or missing entry dates.
"""
import collections
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

P = Path(__file__).resolve().parents[1]
S = P / 'sources/evaluate_2026-11-18'
O = P / 'data/pos_pair_expansion'
O.mkdir(exist_ok=True)
pair_pattern = re.compile(r'(?:^|;\s*)(.*?)\s*\[([^\]]+)\]')
pairs = {}
issues = []
sources = []
input_count = 0
for source in sorted(S.glob('*.csv')):
    count = 0
    with source.open(encoding='utf-8-sig', newline='') as f:
        for line, row in enumerate(csv.DictReader(f), 2):
            count += 1
            product_id = row['Unique Product Records|Record Id'].strip()
            summary = row['Indication Summary'].strip()
            parsed = list(pair_pattern.finditer(summary))
            remainder = pair_pattern.sub('', summary).strip(' ;')
            if remainder or not parsed or not product_id:
                issues.append(dict(file=source.name, line=line, reason='unparsed_or_missing', text=summary))
            for m in parsed:
                disease, status = (x.strip() for x in m.groups())
                key = product_id, disease
                if key not in pairs:
                    pairs[key] = dict(vendor_product_id=product_id, vendor_indication=disease,
                        names=set(), generic_names=set(), research_codes=set(), technologies=set(),
                        routes=set(), mechanisms=set(), statuses=set(), orphan_any_designation=set(),
                        provenance=set(), source_product_rows=set())
                x = pairs[key]
                for target, col in [('names','Product'),('generic_names','Generic Name'),
                                    ('research_codes','Research Codes'),('technologies','Technology'),
                                    ('routes','Routes of Admin.'),('mechanisms','Mechanism of Action')]:
                    value = row.get(col, '').strip()
                    if value and value != '-':
                        x[target].add(value)
                x['statuses'].add(status)
                x['orphan_any_designation'].add(row.get('Orphan Drug (Any Designation)', ''))
                x['provenance'].add((source.name, line))
                x['source_product_rows'].add(row['Products|Record Id'])
    input_count += count
    sources.append(dict(file=str(source.relative_to(P)), rows=count,
                        sha256=hashlib.sha256(source.read_bytes()).hexdigest()))

def status_signals(statuses):
    # Preserve disagreements across sponsors; never promote one sponsor's exit
    # to a global programme failure or equate WW marketed with FDA approval.
    a = any(s in {'Phase I','Phase II','Phase III','Filed'} for s in statuses)
    market = any(s in {'Approved','Marketed','Withdrawn'} for s in statuses)
    abandoned = any(s.startswith('Abandoned') for s in statuses)
    clinical = any(re.search(r'Phase (?:III|II|I)\b|Filed|Approved|Marketed|Withdrawn',s) for s in statuses)
    conflicts = a and abandoned
    return dict(vendor_clinical_stage_signal=clinical, vendor_current_active_signal=a,
                vendor_market_or_approval_signal=market, vendor_abandonment_signal=abandoned,
                active_and_abandoned_across_rows=conflicts)

records=[]
for key,x in sorted(pairs.items()):
    r={k:sorted(v) if isinstance(v,set) else v for k,v in x.items()}
    r['candidate_pair_id']='EV-'+x['vendor_product_id']+'-'+hashlib.sha256(x['vendor_indication'].encode()).hexdigest()[:12]
    r.update(status_signals(x['statuses']))
    r['clinical_entry_date']=None
    r['fda_indication_approval_date']=None
    r['rare_indication_adjudicated']=None
    r['cns_indication_adjudicated']=None
    r['molecule_identity_adjudicated']=False
    r['analysis_eligible']=False
    r['eligibility_reason']='Discovery only; entry, disease taxonomy and FDA outcome not adjudicated for this pair'
    records.append(r)

assert len({r['candidate_pair_id'] for r in records})==len(records)
assert not any(r['analysis_eligible'] for r in records)
assert all(r['provenance'] and r['statuses'] for r in records)
clinical=[r for r in records if r['vendor_clinical_stage_signal']]
summary=dict(created='2026-11-19', source_retrieved='2026-11-18',
    scope='Union of orphan-any-designation and selected-disease exports; NOT all drugs or all rare indications',
    source_rows=input_count, candidate_pairs=len(records),
    vendor_product_ids=len({r['vendor_product_id'] for r in records}),
    vendor_indication_labels=len({r['vendor_indication'] for r in records}),
    vendor_clinical_stage_candidate_pairs=len(clinical),
    simultaneous_active_and_abandoned_signals=sum(r['active_and_abandoned_across_rows'] for r in records),
    analysis_eligible_pairs=0, parsing_issues=len(issues), sources=sources,
    limitations=['All indications of orphan-designated products are included; many are not rare.',
                 'Vendor product IDs require construct/alias reconciliation before molecule clustering.',
                 'Indication summary supplies status but not indication-specific first dosing or FDA approval dates.',
                 'Clinical stage is a discovery signal, not proof of actual dosing within 2010–2024.',
                 'M&A/disposal and sponsor-specific abandonment do not establish terminal global failure.',
                 'Do not calculate approval rates from this discovery inventory.'])
with (O/'candidate_pairs.jsonl.gz').open('wb') as raw:
    with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as f:
        for record in records:
            f.write((json.dumps(record,ensure_ascii=False,separators=(',',':'))+'\n').encode())
(O/'inventory_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(O/'parsing_issues.json').write_text(json.dumps(issues,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['sources','limitations']},indent=2))
