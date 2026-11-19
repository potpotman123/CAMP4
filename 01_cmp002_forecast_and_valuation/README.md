# Project 1 — CMP-002 worldwide revenue forecast and valuation

**Question:** What is CMP-002 in SYNGAP1 independently worth, and how do our revenue expectations compare with Street assumptions and expectations implied by the market?

## Workstreams and status

| Workstream | Status / starting point |
|---|---|
| Sell-side context and assumption audit | 15 original reports saved (eight with extracted text); seven LSEG initiations/pivot and valuation reports added November 17; inherited Street data available |
| Reverse DCF | To build: observed EV, development/operating costs, timeline, financing context and sales implied by valuation |
| Independent worldwide revenue forecast | To build: epidemiology, diagnosis, eligibility, uptake, paid exposure, net pricing and country access |
| KPI and PoS comparator research | Primary-source follow-up expands the selected panel to 319 molecule clusters; explicit nested ASO/restoration filters saved. Of 30 vendor-only statuses checked, 21 remain unresolved at the selected-indication level. This is not yet a comprehensive drug–indication panel or all-drugs census. CMP-002 lifetime PoS remains judgmental; other KPI audits pending |
| Post-LOE / terminal-value analysis | Needham arithmetic decomposition recorded; independent durability assumptions still to research |
| Explain the valuation gap | Pending independent model and reverse DCF |

## Start here

- **[Retrospective PoS methods review and expansion feasibility](reports/pos_methodology_review_2026-11-18.txt)**: distinguishes phase-transition LOA from finite-horizon approval estimates; published time-to-approval precedent; limitations of the selected panel. [Expanded cohort protocol](protocol/pos_all_drugs_expansion_2026-11-18.txt) adds all drugs → all rare diseases (including oncology) → non-oncology rare → closer CMP peers. Evaluate indication-specific fields confirmed, but the unrestricted report became unresponsive before extraction; no new population PoS or completed validation sample is claimed.

- **Latest: [45-candidate primary-source follow-up and pair-unit clarification](reports/evaluate_primary_followup_2026-11-18.txt)**. All 15 remaining discovery candidates and 30 vendor-only statuses checked; two additions, with EGT-101 entry-date sensitivity. Selected molecule funnel **319 → 89 → 56 → 18 → 6 → 4**. [Browse the funnel and every member](reports/pos_peer_funnel_2026-11-18.html), [results and sensitivities](data/evaluate_primary_followup/funnel_results.json), [handoff](context/evaluate_primary_followup_handoff_2026-11-18.txt). Current calculations are clinical-entry finite-horizon FDA approval estimates, not preclinical lifetime PoS. A comprehensive molecule–indication expansion remains separate work.

- **[Evaluate-assisted PoS audit — 18 November](reports/evaluate_pos_audit_2026-11-18.txt)**: two source exports; all 40 unresolved and 113 failed records audited, two failed-to-active corrections corroborated, seven new molecule clusters. Nested panel **317 → 88 → 55 → 4**; ten-year estimates **21.6% / 20.3% / 20.9%**, not lifetime PoS. Vendor-only dispositions remain provisional; broader discovery is not a completed census. [Results and sensitivities](data/evaluate_audit/updated_results.json), [current handoff](context/evaluate_pos_handoff_2026-11-18.txt).

- **[Censoring-adjusted nested peer analysis and Needham's 25%](reports/pos_censoring_adjusted_findings_2026-11-17.txt)** — all 310 retained; failed candidates are not censored at discontinuation. Ten-year approval estimates: 21.8% broad, 21.1% genetic CNS, 22.2% genetic CNS medicines. Recent-cohort, date, missingness and descriptive uncertainty scenarios saved in [results](data/pos_censoring_analysis/results.json). These are finite horizons, not lifetime PoS; 25% remains a plausible but uncalibrated CMP-002 assumption.
- **Previous: [all 310 candidates classified](reports/pos_all_310_status_findings_2026-11-16.txt)** — 42 FDA approved, 113 failed (94 supported + 19 probable), 115 active, 40 unresolved. [Full readable ledger](reports/pos_all_310_status_ledger_2026-11-16.txt), [source-linked records](data/pos_molecule_status/cluster_status.json), and [strict sensitivity / era splits](data/pos_molecule_status/summary.json). Original candidate and qualifying indication retained; distinct successors do not rescue failed candidates. Recent entrants remain included. These status counts are not lifetime PoS.
- **[Six unapproved mature genetic-medicine peers: actual development status](reports/pos_six_program_status_audit_2026-11-16.txt).** Distinguishes efficacy failure, replacement by a successor, sponsor exit, and unresolved continuation. ISIS333611 and CLN2/LX1004 classifications are materially improved; approval arithmetic is unchanged.
- **Interpretation update: [denominator and recency audit](reports/pos_denominator_and_recency_audit_2026-11-16.txt).** The 310-to-74 reduction is 209 newer entrants plus 27 uncertain entry-date boundary cases. Fifty-four of the 74 entered in 2010–2014; the ten-year result should not be foregrounded as the contemporary CMP-002 benchmark. [Every asset's disposition](data/pos_completion/ten_year_denominator_audit.json).
- **Previous: [completed panel findings and PoS interpretation](reports/pos_completed_panel_findings_2026-11-16.txt)**, [calculated approval horizons and every denominator](data/pos_completion/approval_horizon_results.json), [reviewed ledger](data/pos_completion/completed_program_ledger.json), and [method](protocol/pos_completed_panel_method_2026-11-16.txt). All 449 assigned histories reviewed. Included asset clusters tighten **310 → 81 → 48 → four closest ASOs**. Ten-year mature samples give 21/74, 5/20 and 3/10 approvals; these are horizon observations, **not CMP-002 lifetime PoS**. [Current handoff](context/pos_completion_handoff_2026-11-16.txt).
- **Historical preliminary inventory:** [expanded adjudication](reports/pos_expanded_adjudication_2026-11-16.txt) and its [source-linked ledger](reports/pos_adjudication_2026-11-16.html) remain frozen. Their 418 retained / 333 unresolved presentation is superseded by the completed review and separate entry, development-status and approval fields.
- **Correction:** the old `novel_target_at_entry` flag did not establish absence of prior human target exposure. Unsupported flags are now unknown; the earlier uniform novel-target characterization is superseded. The earlier 20% central case remains judgmental, with no evidence here that it is statistically preferable to Needham’s 25%.

- **[Public-source pilot and broader discovery results](reports/pos_pilot_and_broad_universe_2026-11-16.txt)**: eight-program linkage pilot; 6,407-trial inventory across 48 rare-disease search terms; FDA local matching; [review queue](data/pos_nested/candidate_review_queue.json). This is not yet an adjudicated program denominator or an empirical PoS estimate.


- **Historical design: [independent nested-cohort rebuild](protocol/pos_nested_cohort_reset_2026-11-16.txt).** The latest completed-panel method above implements finite-horizon calculations; the earlier odds sensitivity remains a scenario tool.


- **[Three-tier PoS synthesis](reports/pos_three_tier_synthesis_2026-11-16.txt)**: frozen [four closest biological/clinical peers](data/pos_synthesis/closest_biological_clinical_peers_2026-11-16.json), broader 16-asset genetic CNS set, published benchmark anchors and explicit odds sensitivities. No fitted posterior or empirically calibrated blend claimed.


- **[PoS audit decision memo](reports/pos_audit_findings_2026-11-16.txt)** and [full evidence report](reports/pos_audit_2026-11-16.html).
- [PoS peer ledger (CSV)](data/pos_audit/program_ledger.csv), [source registry](data/pos_audit/source_registry.json), [scope/limitations](protocol/pos_audit_design_2026-11-16.txt), and [97 internal checks](data/pos_audit/validation.json).
- Current conclusion: Needham's 25% remains a plausible assumption, not an empirically calibrated estimate. This expanded audit does not establish that it is too high or conservative. Earlier 20% central / 10–35% scenarios are retained as historical judgment, not estimated probabilities.


- [KPI, PoS and post-LOE audit research prompt](protocol/cmp002_kpi_audit_research_prompt_2026-11-16.txt).
- [Current handoff and corrections](context/kpi_audit_prompt_handoff_2026-11-16.txt).
- [Original CAMP sell-side reports](sources/user-provided/sellside/) and [searchable extracted text](sources/extracted/).
- [Source manifest with original hashes](sources/source_manifest.json).
- [Inherited Street reference snapshot](data/street_reference_snapshot.json): historical reported inputs, not an independent forecast or fresh market valuation.
- [Project 2 comparator dossiers](../02_first_entry_dmt_forecast_study/data/independent/analogue_matrix.csv) and [full candidate library](../02_first_entry_dmt_forecast_study/data/independent/candidate_universe.json).

## Important interpretation notes

Keep product sales conditional on approval separate from probability-adjusted valuation and company-attributable economics. Needham's detailed model peaks at approximately $2.106bn in 2046, while its peak-multiple table uses $1.843bn in 2043; that mismatch remains unresolved. Its 50/50 collaboration discussion refers to Stoke/Acadia, not CMP-002.

The existing historical comparator library is useful for commercial discovery but is approval-selected. Build new KPI-specific peer groups, particularly an inception-based PoS cohort including failures, discontinuations and unresolved programs. Prefer relevant recent experience and stage-matched pre-human-data evidence without treating immature outcomes as known.

## Where new work belongs

Use this project's `protocol/` for research plans, `data/` for evidence and model inputs, `sources/` for provenance/originals, and `context/` for concise handoffs. Add `models/`, `reports/` and `scripts/` as actual deliverables are created. Do not store the independent forecast under Project 2 or treat a bullish narrative as a required result.

[Back to both projects](../README.md)
