"""Four-way as-of status overlay; preserves the frozen inception panel and horizons."""
import json
import hashlib
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/pos_completion'
OUT = ROOT / 'data/pos_molecule_status'
OUT.mkdir(exist_ok=True)
rows = json.loads((BASE / 'completed_program_ledger.json').read_text())
detail = {}
for family in ['als', 'neuro', 'metabolic', 'systemic']:
    d = json.loads((BASE / (family + '_updates.json')).read_text())
    detail.update({r['id']: r for r in (d.values() if isinstance(d, dict) else d)})

# Every override below is an adjudication, not a keyword-derived clinical conclusion.
overrides = {}
def set_status(key, status, confidence, reason, urls=(), scope='original_indication'):
    overrides[key] = dict(status=status, confidence=confidence, reason=reason,
                          additional_sources=list(urls), uncertainty_type=scope)

set_status('als:SPG302|ALS', 'active', 'supported', 'Current sponsor pipeline retains SPG302/tazbentetol ALS development after Phase 2a.', ['https://spinogenix.com/pipeline/'])
set_status('als:ALN-SOD|ALS', 'active', 'supported', 'Sponsor pipeline dated October 2026 includes ALN-SOD for SOD1-ALS.', ['https://www.alnylam.com/alnylam-rnai-pipeline'])
set_status('als:QRL-101|ALS', 'active', 'supported', 'January 2026 corporate presentation and December 2025 ALS results support continued candidate development.', ['https://www.quralis.com/wp-content/uploads/2026/01/QurAlis-Corporate-Presentation-January-2026-UPDATED.pdf','https://www.quralis.com/news/'])
set_status('neuro:AAVrh10_ARSA|MLD', 'failed', 'probable', 'Original clinical candidate did not demonstrate efficacy; classify probable attrition, not a documented permanent discontinuation. Biochemical activity was not clinical success.')
set_status('neuro:AAVrh10_CLN2|NCL', 'failed', 'probable', 'Sponsor exited and returned license/IND to Cornell in October 2026; no verified continuing successor-owner program. Possible revival remains a sensitivity.')
set_status('metabolic:metabolic_raav25naglu', 'failed', 'probable', 'Original AMT110 candidate deprioritized and partner sought; no verified resumption. Strategic attrition, not proof that the target cannot work.')
set_status('neuro:VK0214|ALD', 'failed', 'probable', 'Development mothballed pending partner: sponsor says additional clinical studies require a licensing arrangement. Potential revival is not an active funded program.')
set_status('neuro:reldesemtiv|SMA', 'failed', 'probable', 'Sponsor terminated reldesemtiv dosing after ALS futility; no verified SMA continuation. ALS efficacy result is not attributed to SMA.', ['https://www.sec.gov/Archives/edgar/data/1061983/000095017023011143/cytk-20230331.htm'])
set_status('metabolic:metabolic_dmpkrx', 'failed', 'probable', 'Sponsor reported inadequate muscle potency; patient-research organization documented non-advancement and replacement-technology plan. Exact formal stop date not established.', ['https://www.sec.gov/Archives/edgar/data/874015/000114036117015262/formdef14a.htm','https://www.mda.org/quest/article/progress-now-spring-2017'])
set_status('metabolic:metabolic_sbc103', 'failed', 'supported', 'Sponsor-submitted registry explicitly says the SBC103 PROGRAM was terminated after review of all interventional studies; hypothetical revival does not make this unknown.', ['https://clinicaltrials.gov/study/NCT02618512'])
set_status('metabolic:metabolic_rt001', 'failed', 'supported', 'Research-funder tracker reports inactive/discontinued development following unsuccessful trial; exact stop date uncertain.')
set_status('metabolic:metabolic_val1221', 'failed', 'probable', 'Pompe study and funding stopped per directly involved patient organization; later Lafora development does not rescue the original indication.')
for key in ['metabolic:metabolic_lyssaf302','metabolic:metabolic_lysgm101']:
    set_status(key, 'failed', 'probable', 'Owner liquidated; no verified successor development. Commercial/organizational attrition inferred, not scientific failure.', ['https://www.amf-france.org/sites/institutionnel/files/private/2025-05/san-2025-04.pdf'])
set_status('metabolic:metabolic_four_d310', 'failed', 'probable', 'Sponsor reduced investment and designated candidate noncore; continuing participant follow-up does not establish investment in advancement. Revival remains possible.')
set_status('metabolic:metabolic_rgx111', 'active', 'supported', 'Temporarily on clinical hold, with sponsor explicitly pursuing continued development under collaboration. Active includes paused development; it does not imply dosing.')
set_status('metabolic:metabolic_pgnedodm1', 'active', 'supported', 'Ongoing sponsor DM1 program under partial hold; distinct from discontinued EDO51.')
set_status('metabolic:metabolic_ux053', 'failed', 'probable', 'Sponsor terminated original trial and patient summary had no future-study timeline. Probable attrition; original ledger assertion of later SEC cessation lacks a precise linked passage and is not promoted to confirmed.', ['https://www.ultragenyx.com/wp-content/uploads/2024/05/UX053-CL101_GSD_III_MRCC-UX053-00018.pdf'])
set_status('metabolic:metabolic_vtx801', 'failed', 'probable', 'Original clinical trial terminated; no verified advancement beyond follow-up. Program-level attrition inferred, not proven by trial termination alone.')
set_status('metabolic:metabolic_en001', 'failed', 'probable', 'Original DMD trial terminated early; CMT activity is a different indication. No verified continued DMD development.')
set_status('metabolic:metabolic_pr001_gd2', 'failed', 'probable', 'Lilly Q1 2024 pipeline update removes GD2; later Parkinson development does not rescue original GD2 indication.', ['https://investor.lilly.com/static-files/d0789b60-5579-415e-9461-8b8130413dd6'])
set_status('metabolic:metabolic_actus101', 'unknown', 'unresolved', 'Sponsor calls original program active but no further enrollment while AB1009 advances. Follow-up alone does not resolve whether original candidate is still being advanced.', scope='followup_versus_advancement')
for key in ['systemic:sys_aa3c33ebf3a7','systemic:sys_4e9bd4187b6b','systemic:sys_1f84df4ebcba']:
    set_status(key, 'failed', 'probable', 'Sponsor suspended/deprioritized internal development or material investment; partner option remains. Classify strategic attrition with explicit revival sensitivity.')
set_status('systemic:sys_c501aa9d5fbd', 'failed', 'supported', 'Clinical-investigator account explicitly describes sponsor discontinuation due to short duration of inhibition; no requirement for impossible proof against future revival.')
set_status('systemic:sys_a6c4ba839e4e', 'failed', 'probable', 'HAE trial withdrawn for sponsor pipeline change after prior human exposure. Program attrition inferred; future revival not excluded.')
set_status('systemic:sys_fd673d394db0', 'failed', 'probable', 'Original PNH study stopped for inadequate intravascular hemolysis control; no verified continuing original-indication program. Not proof of global molecule abandonment.')
set_status('systemic:sys_6857678a3992', 'active', 'supported', 'Explicitly temporary SAE-related study suspension; retain paused development rather than infer permanent failure.')

foreign = {'metabolic:metabolic_gc1111','metabolic:metabolic_saer','metabolic:metabolic_can103','systemic:sys_e238494c1732'}
other_indication = {'systemic:sys_ae0b7e566b9a','systemic:sys_2406594fa25f','systemic:sys_52eb95e839f9','systemic:sys_8bff64f7fa28'}
members = []
for r in rows:
    if not r['entry_qualified']:
        continue
    d = detail[r['id']]
    o = r['outcome']
    evidence = (d.get('outcome_evidence') or []) + (d.get('evidence') or []) + (d.get('registry_evidence') or []) + (d.get('first_human_evidence') or [])
    audit = r.get('latest_status_audit') or {}
    sources = sorted(set(e.get('url') for e in evidence if isinstance(e,dict) and e.get('url')) | set(audit.get('sources',[])))
    accepted_claims = [e.get('claim') or e.get('note') for e in ((d.get('outcome_evidence') or []) + (d.get('evidence') or [])) if isinstance(e,dict) and (e.get('claim') or e.get('note'))]
    note = d.get('outcome_note') or audit.get('development_status') or d.get('last_verified_active_basis') or ('Prior completed review: '+o)
    if r['observed_FDA_approval']:
        result = dict(status='approved', confidence='supported', reason='FDA approval in an included qualifying indication; historical success remains even if later withdrawn.', uncertainty_type=None)
    elif o.startswith('stopped') or o in {'sponsor_discontinued','superseded_by_distinct_asset'}:
        result = dict(status='failed', confidence='supported', reason=note, uncertainty_type=None)
    elif o.startswith(('ongoing','active_')):
        result = dict(status='active', confidence='supported', reason=note, uncertainty_type=None)
    else:
        result = dict(status='unknown', confidence='unresolved', reason=note, uncertainty_type='insufficient_program_fate_evidence')
    if r['id'] in overrides:
        result.update(overrides[r['id']])
    if r['id'] in foreign:
        result.update(status='unknown', confidence='unresolved', reason='Known non-US approval/commercialization; FDA development path unresolved. This is NOT a globally dead or wholly untraceable molecule.', uncertainty_type='geography_scope')
    elif r['id'] in other_indication:
        result.update(uncertainty_type='indication_scope', reason=note+' Current activity in another indication does not resolve the original program.')
    elif r['id']=='metabolic:metabolic_verenafusp':
        result.update(uncertainty_type='geography_scope', reason=note+' FDA pathway and current advancement not resolved by publication date alone.')
    sources = sorted(set(sources + result.pop('additional_sources',[])))
    members.append(dict(id=r['id'], asset=r['asset'], indication=r['indication'], asset_cluster=r['asset_cluster'], family=r['family'], entry_interval=r['entry_interval'], flags=r['flags'], original_outcome=o, approval_date=r['approval_date'], last_verified_active_date=r['last_verified_active_date'], **result, sources=sources, accepted_prior_claims=accepted_claims, source_record=r['review_file'], known_foreign_approval=r['id'] in foreign or bool(d.get('non_US_approval')), inherited_uncertainty=r['remaining_uncertainty'], as_of='2026-11-16'))

groups = defaultdict(list)
for r in members:
    groups[r['asset_cluster']].append(r)
clusters = []
for key, group in sorted(groups.items()):
    statuses = {x['status'] for x in group}
    status = 'approved' if 'approved' in statuses else 'active' if 'active' in statuses else 'failed' if statuses=={'failed'} else 'unknown'
    decisive = [x for x in group if x['status']==status]
    confidence = 'probable' if status=='failed' and any(x['confidence']=='probable' for x in decisive) else 'unresolved' if status=='unknown' else 'supported'
    flags = {k:any(x['flags'].get(k) is True for x in group) for k in group[0]['flags']}
    clusters.append(dict(asset_cluster=key, assets=sorted(set(x['asset'] for x in group)), member_ids=[x['id'] for x in group], indications=sorted(set(x['indication'] for x in group)), status=status, confidence=confidence, strict_status='unknown' if confidence=='probable' else status, entry_interval=min(x['entry_interval'] for x in group), flags=flags, unknown_types=sorted(set(x['uncertainty_type'] for x in decisive if x['uncertainty_type'])) if status=='unknown' else [], members=group))

def counts(seq, field='status'):
    c=Counter(x[field] for x in seq)
    return {k:c[k] for k in ['approved','failed','active','unknown']}
summary = dict(as_of='2026-11-16', unit='Existing asset/combination clusters, original qualifying indications, FDA approval endpoint', clusters=len(clusters), member_records=len(members), counts=counts(clusters), strict_counts=counts(clusters,'strict_status'), probable_failures=sum(x['confidence']=='probable' for x in clusters), unknown_types=dict(Counter(t for x in clusters if x['status']=='unknown' for t in x['unknown_types'])), era_counts={}, nested_counts={})
for lo,hi in [(2010,2014),(2015,2019),(2020,2024)]:
    subset=[x for x in clusters if lo<=int(x['entry_interval'][0][:4])<=hi]
    summary['era_counts'][f'{lo}-{hi}']=dict(n=len(subset),**counts(subset))
for name,pred in [('all',lambda x:True),('genetic_cns',lambda x:x['flags']['genetic_cns']),('genetic_medicine_cns',lambda x:x['flags']['genetic_cns'] and x['flags']['genetic_medicine'])]:
    subset=[x for x in clusters if pred(x)]
    summary['nested_counts'][name]=dict(n=len(subset),**counts(subset),probable_failures=sum(x['confidence']=='probable' for x in subset))
assert len(members)==316 and len(clusters)==310
assert summary['counts']['approved']==42
assert sum(summary['counts'].values())==310
assert len({x['id'] for x in members})==316
assert all(x['sources'] for x in members), 'Missing evidence pointers'
assert all(x['status'] in {'approved','failed','active','unknown'} for x in members)
assert set(overrides).issubset({x['id'] for x in members})
assert sum(v['n'] for v in summary['era_counts'].values())==310
assert summary['strict_counts']['failed']+summary['probable_failures']==summary['counts']['failed']
assert sum(len(x['member_ids']) for x in clusters)==316
assert all(x['status']=='approved' for x in members if x['approval_date'])
for name,obj in [('cluster_status',clusters),('member_status',members),('summary',summary),('adjudication_overrides',overrides)]:
    (OUT/(name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')

lines=['MOLECULE STATUS AUDIT — 16 NOVEMBER 2026','',json.dumps(summary,indent=2),'','ALL 310 CLUSTERS — includes all original qualifying indications; detailed claims/URLs in JSON.']
for x in clusters:
    lines += ['',f"{'; '.join(x['assets'])} | {x['status'].upper()} | {x['confidence']} | {'; '.join(x['indications'])}"]
    for r in x['members']:
        lines += [f"  {r['id']}: {r['reason']}",f"  Evidence: {' ; '.join(r['sources'])}"]
(ROOT/'reports/pos_all_310_status_ledger_2026-11-16.txt').write_text('\n'.join(lines)+'\n')
inputs=[BASE/'completed_program_ledger.json']+[BASE/(f+'_updates.json') for f in ['als','neuro','metabolic','systemic']]+[BASE/'six_program_status_audit.json',Path(__file__)]
validation=dict(result='passed', checks=['316 unique qualified rows','310 unique clusters','42 approval clusters preserved','four exhaustive mutually exclusive buckets','every row has source pointers','all override IDs belong to panel','all era totals reconcile','probable-failure sensitivity reconciles','cluster membership covers all records','approval dates consistent with status'], input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}, limitation='Structural and arithmetic validation, not independent confirmation of every source claim or exhaustive universe coverage.')
(OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
print(json.dumps(summary,indent=2))
