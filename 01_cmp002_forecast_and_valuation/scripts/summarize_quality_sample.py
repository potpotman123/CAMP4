"""Record the fixed sample's linkage audit; no outcome estimate is calculated."""
import collections, gzip, json
from pathlib import Path
P = Path(__file__).resolve().parents[1]
O = P / 'data/pos_all_drugs_expansion'
sample = json.loads((O/'quality_sample_24.json').read_text())
links = {r['candidate_pair_id']:r for r in json.loads((O/'quality_sample_registry_links.json').read_text())}
# Human review of source records; first observed study is not assumed to be first worldwide entry.
# Fields: gate, linked study, review finding.
notes = {
 'EV-60826-51fb019d7178': ('indication_intent_needs_verification', 'NCT04521738', 'Explicit first-in-human trial began 2019-04-25 in healthy/overweight participants. Molecule linkage is credible; type-2-diabetes programme intent needs separate evidence. Completed trial does not independently verify vendor abandonment.'),
 'EV-9801-722ff5aa7a0a': ('dated_trial_lead', 'NCT02558140', 'RO6874813 alias matches a phase-I solid-tumour trial starting 2015-10-11. Earlier worldwide entry and programme-level discontinuation remain unverified.'),
 'EV-11113-5bde44aaf50c': ('unresolved_identity_or_history', None, 'No ClinicalTrials.gov hit on supplied name. Vendor abandonment retained as vendor evidence only. No entry date inferred from absence of a registry match.'),
 'EV-26802-985ba83223d1': ('formulation_specific_history_needed', None, 'Generic galantamine query retrieves 118 studies, truncated at 100. Oral galantamine and rivastigmine-patch studies are not NAL8801 history. Do not inherit oral-drug approval or trial dates for this patch.'),
 'EV-216558-51fb019d7178': ('dated_trial_lead', 'NCT06333977', 'LC542019 alias matches a phase-I healthy/type-2-diabetes trial starting 2022-03-25. Earlier entry and whole-programme failure remain unverified.'),
 'EV-202218-38e48b392aa4': ('vendor_registry_status_conflict', 'NCT05023551;NCT06636162', 'Vendor says abandoned-phase-I. Registry lists industry trial active-not-recruiting from 2021-09-08 and Washington University glioma study recruiting from 2025-04-03. Keep disagreement visible; neither a stale registry label nor sponsor abandonment settles global molecule-indication failure.'),
 'EV-26049-3fb3d4cce682': ('subtype_and_arm_entry_needed', 'NCT06500702', 'Phase-II multi-drug trial began 2024-12-19 in FSGS/minimal-change disease. These are narrower than glomerulonephritis. Current rilzabrutinib arm presence does not prove that arm was present at the initial study start. Healthy-volunteer or pemphigus dates cannot substitute for renal-programme entry.'),
 'EV-1227964-a18f659b2adc': ('earlier_history_and_era_unresolved', 'NCT07604974', 'Only retrieved study is phase II starting 2026-05-12 in hypertriglyceridaemia. This is a later-era lead, not proof that development began in 2026; prior codes/phase-I history need verification.'),
 'EV-226260-722ff5aa7a0a': ('dated_trial_lead', 'NCT05598151', 'Molecule and solid-tumour phase-I trial match, start 2023-01-11. First worldwide entry and current programme ascertainment need corroboration.'),
 'EV-1286374-6e7ec145d7fc': ('unresolved_identity_or_history', None, 'Descriptive CD117 CAR-T label yields no exact-name registry hit. Sponsor/product identity must precede broader target searches; do not merge all CD117 CAR-T products.'),
 'EV-9878-7f771a3466dd': ('subtype_entry_needs_verification', 'NCT02279433', 'DS-6051b first-in-human solid-tumour trial started 2014-09. Broad trial condition alone does not establish when neuroendocrine patients entered. Later approval in another indication cannot become a neuroendocrine approval.'),
 'EV-1243575-99aef4cde68f': ('routine_bioequivalence_lead', 'NCT06920719;NCT07265167', 'Two exact-code phase-I studies are bioequivalence studies beginning in 2025. Exclude these trials from novel-drug clinical-entry ascertainment; original programme/ingredient remains undisclosed.'),
 'EV-12659-7030379348a0': ('false_positive_generic_linkage', 'NCT06056947;NCT05361369', 'Returned fenticonazole studies test EVEGYN fixed combinations, not this Gynoxin product. Generic ingredient overlap is insufficient for product-history linkage.'),
 'EV-3047-090df441d982': ('legacy_or_duplicate_identity', 'NCT00236730', 'Topiramate epilepsy trials precede 2010 (one retrieved study starts 1988). Arasid is not automatically another molecule-indication sample. Current regional brand row cannot establish a new 2010-2024 programme.'),
 'EV-10858-1b6c2d7776c2': ('wrong_study_purpose_or_indication', 'NCT02582736;NCT02435095', 'Search retrieves observational safety and later psychiatric studies. These do not establish first development in generalised anxiety or a US approval outcome.'),
 'EV-54011-8e6cbb9b069f': ('unresolved_identity_or_history', None, 'No brand-specific registry hit. Vendor generic field is herbal extract although product name includes codeine. Composition and programme identity require verification.'),
 'EV-53725-c27b36f3f67d': ('unresolved_identity_or_history', None, 'No hit for brand/fixed-combination query. Separate cefepime or amikacin programmes cannot be used as this combination history.'),
 'EV-1419529-6728b99339ad': ('biosimilar_separate_analysis', None, 'EMA medicine-overview search result identifies Enwylma as biosimilar to Xgeva. Generic denosumab search is truncated and includes originator programmes. Verify biosimilar development separately; exclude from novel/unapproved-at-entry CMP sensitivity.'),
 'EV-2168-e4aa73967d13': ('pre_window_vendor_date', None, 'Vendor indication approval date is 1974-04-29, predating the 2010 entry window. FDA date needs regulator reconciliation before final exclusion; modern iron-dextran studies do not establish new inception.'),
 'EV-26049-31d44a2d9c32': ('approval_verified_phase_entry_unresolved', 'NCT03395210', 'FDA confirms rilzabrutinib approval for persistent/chronic ITP in 2025. Retrieved ITP trial starts 2018-03-22 in phase II. Do not place it in a phase-I-entry denominator using 2016 pemphigus history. FDA approval is not in dispute; entry-stage attribution still matters.'),
 'EV-102394-a8cd8f89a65e': ('pre_window_vendor_date', None, 'Vendor indication approval dates are 1987-03-27 and 1987-11-02. Preserve both; regulator/application reconciliation needed. Broad dopamine query returns many unrelated interventions and indications.'),
 'EV-3171-cf3ad3c122a1': ('pre_window_vendor_date', None, 'Vendor date is 1997-06-30. Vaccine/formulation identity and exact indication need checking; modern booster trials must not reset entry.'),
 'EV-6997-f3c26ed3a5f2': ('formulation_specific_history_needed', None, 'Vendor approval is 2014-06-04, but that does not prove 2010-2024 first clinical entry. Broad testosterone search retrieves 1,039 studies and is truncated. Need USL240-specific history and reformulation/prior-approval flags.'),
 'EV-6201-51f512c44f9d': ('pre_window_vendor_date', None, 'Vendor indication approval date is 1949-05-18. Broad vitamin-A search is not brand-specific history. Regulator verification and canonical molecule mapping needed before final exclusion.')
}
assert set(notes) == {r['candidate_pair_id'] for r in sample}
review=[]
for r in sample:
    gate,ncts,note = notes[r['candidate_pair_id']]
    q=links[r['candidate_pair_id']]
    sources=[q['url']]
    if ncts:
        sources += ['https://clinicaltrials.gov/study/'+n for n in ncts.split(';')]
    if gate=='approval_verified_phase_entry_unresolved':
        sources += ['https://www.fda.gov/drugs/news-events-human-drugs/fda-approves-drug-treat-adults-persistent-or-chronic-immune-thrombocytopenia']
    if gate=='biosimilar_separate_analysis':
        sources += ['https://www.ema.europa.eu/en/documents/overview/enwylma-epar-medicine-overview_en.pdf']
    review.append(dict(candidate_pair_id=r['candidate_pair_id'], name=r['names'][0],
        indication=r['vendor_indication'], stratum=r['sampling_stratum'],
        vendor_status=r['ww_statuses'], query_hits=q.get('total_hits'),
        query_truncated=q.get('truncated'), gate=gate, review=note,
        sources=sources, clinical_inception_verified=False, rare_status='not_adjudicated',
        eligible_for_pos=False, review_scope='Initial registry linkage and identity/entry screening only; not complete programme-history adjudication.'))
(O/'quality_sample_review.json').write_text(json.dumps(review,indent=2)+'\n')
summary=dict(sample_size=len(review),sampling='Six deterministic hash-ranked candidates per current-status/FDA-date stratum; oncology not separately balanced.',
    query_hits_any=sum((r['query_hits'] or 0)>0 for r in review),
    query_no_hits=sum(r['query_hits']==0 for r in review),
    query_truncated=sum(r['query_truncated'] for r in review),
    query_errors=sum('error' in r for r in links.values()),
    complete_eligibility_adjudications=0,rare_classifications_complete=0,
    vendor_ind_dates_present=sum(bool(r['ind_dates']) for r in sample),
    gates=dict(collections.Counter(r['gate'] for r in review)),
    pos=None,reason='Quality-control sample, with incomplete programme histories and unequal sampling weights; no approval rate should be computed.')
(O/'quality_sample_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
