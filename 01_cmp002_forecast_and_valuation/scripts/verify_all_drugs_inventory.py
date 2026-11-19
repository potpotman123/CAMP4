"""Independent source-row/identity/hash reconciliation; not clinical validation."""
import collections, csv, gzip, hashlib, json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
S=P/'sources/evaluate_expansion_2026-11-19'
O=P/'data/pos_all_drugs_expansion'
manifest=json.loads((S/'export_manifest.json').read_text())
digest=hashlib.sha256();byte_count=0
with gzip.open(S/'all_status_all_indications.csv.gz','rb') as f:
    for b in iter(lambda:f.read(1024*1024),b''):
        digest.update(b);byte_count+=len(b)
assert digest.hexdigest()==manifest['uncompressed_sha256']
assert byte_count==manifest['uncompressed_bytes']
source_keys={}
with gzip.open(S/'all_status_all_indications.csv.gz','rt',encoding='utf-8-sig',newline='') as f:
    for row,r in enumerate(csv.DictReader(f),2):
        assert r['Unique Product Records|Record Id']
        source_keys[row]=(r['Unique Product Records|Record Id'],r['Indication Level 3'])
expected=collections.Counter(source_keys.values());seen=collections.Counter();ids=set()
with gzip.open(O/'candidate_pairs.jsonl.gz','rt') as f:
    for line in f:
        r=json.loads(line);key=(r['vendor_product_id'],r['vendor_indication'])
        assert r['candidate_pair_id'] not in ids
        ids.add(r['candidate_pair_id'])
        assert len(r['source_rows'])==expected[key]
        for row in r['source_rows']:
            assert source_keys[row]==key
            seen[row]+=1
        assert r['eligible_for_pos'] is False
assert set(seen)==set(source_keys) and set(seen.values())=={1}
assert len(ids)==len(expected)==199342 and len(source_keys)==350769
sample=json.loads((O/'quality_sample_24.json').read_text())
reviews=json.loads((O/'quality_sample_review.json').read_text())
assert len(sample)==len(reviews)==24
assert {r['candidate_pair_id'] for r in sample}=={r['candidate_pair_id'] for r in reviews}
assert set(collections.Counter(r['sampling_stratum'] for r in sample).values())=={6}
result=dict(check='Source reconciliation only, not outcome/eligibility validation',
    uncompressed_sha256=digest.hexdigest(),uncompressed_bytes=byte_count,
    source_rows=len(source_keys),candidate_pairs=len(ids),
    every_source_row_mapped_exactly_once=True,pair_keys_match_original_rows=True,
    sample_members_all_reviewed_at_initial_linkage_level=True,
    no_candidates_promoted_to_pos_without_adjudication=True)
(O/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
