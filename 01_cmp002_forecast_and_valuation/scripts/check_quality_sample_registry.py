"""Bounded registry linkage for a fixed 24-pair quality sample, never a PoS denominator."""
import concurrent.futures, hashlib, json, re, urllib.parse, urllib.request
from pathlib import Path

P = Path(__file__).resolve().parents[1]
S = P / 'sources/evaluate_expansion_2026-11-19/quality_sample_registry'
S.mkdir(exist_ok=True)
O = P / 'data/pos_all_drugs_expansion'
sample = json.loads((O / 'quality_sample_24.json').read_text())

def check(r):
    terms = set(r['names'])
    for field in ['generic_names', 'research_codes']:
        for value in r[field]:
            # Preserve fixed combinations as combinations; research-code lists are aliases.
            terms.update(value.split('; ') if field == 'research_codes' else [value])
    # A generic mixture label is not a useful identity-specific registry query.
    terms.discard('herbal extract')
    q = ' OR '.join('"' + t.replace('"', '') + '"' for t in sorted(terms))
    url = 'https://clinicaltrials.gov/api/v2/studies?' + urllib.parse.urlencode(
        {'query.intr': q, 'pageSize': 100, 'countTotal': 'true', 'format': 'json'})
    path = S / (r['candidate_pair_id'] + '.json')
    result = dict(candidate_pair_id=r['candidate_pair_id'], name=r['names'][0],
                  indication=r['vendor_indication'], sampling_stratum=r['sampling_stratum'],
                  query=q, url=url, retrieved='2026-11-19')
    try:
        if not path.exists():
            req = urllib.request.Request(url, headers={'User-Agent': 'Research/1.0'})
            path.write_bytes(urllib.request.urlopen(req, timeout=45).read())
        d = json.loads(path.read_text())
        records = []
        for s in d.get('studies', []):
            p = s['protocolSection']; st = p.get('statusModule', {})
            design = p.get('designModule', {})
            records.append(dict(nct=p['identificationModule']['nctId'],
                title=p['identificationModule'].get('briefTitle'),
                start=st.get('startDateStruct'), phases=design.get('phases'),
                study_type=design.get('studyType'), enrollment=design.get('enrollmentInfo'),
                conditions=p.get('conditionsModule', {}).get('conditions'),
                interventions=p.get('armsInterventionsModule', {}).get('interventions'),
                sponsor=p.get('sponsorCollaboratorsModule', {}).get('leadSponsor'),
                status=st.get('overallStatus')))
        records.sort(key=lambda x: (x['start'] or {}).get('date', '9999'))
        result.update(total_hits=d.get('totalCount'), truncated=bool(d.get('nextPageToken')),
                      raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), records=records)
    except Exception as e:
        result['error'] = str(e)
    result['limitation'] = ('Search hits are discovery leads, not verified pair histories. '
        'No hit does not establish no development. Truncated searches are not complete. '
        'Current study phase and study start do not establish phase-I entry or first dosing.')
    return result

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(check, sample))
(O / 'quality_sample_registry_links.json').write_text(json.dumps(results, indent=2) + '\n')
for r in results:
    print(json.dumps({k:v for k,v in r.items() if k in
        ['candidate_pair_id', 'name', 'indication', 'total_hits', 'truncated', 'error']}))
    for s in r.get('records', [])[:3]:
        print(json.dumps({k:v for k,v in s.items() if k not in ['interventions', 'sponsor']}))
