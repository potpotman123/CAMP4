# Project 1 — CMP-002 worldwide revenue forecast and valuation

**Question:** What is CMP-002 in SYNGAP1 independently worth, and how do our revenue expectations compare with Street assumptions and expectations implied by the market?

## Workstreams and status

| Workstream | Status / starting point |
|---|---|
| Sell-side context and assumption audit | Eight original reports and extracted text saved; inherited Street data available |
| Reverse DCF | To build: observed EV, development/operating costs, timeline, financing context and sales implied by valuation |
| Independent worldwide revenue forecast | To build: epidemiology, diagnosis, eligibility, uptake, paid exposure, net pricing and country access |
| KPI and PoS comparator research | Completed second review of all 449 assigned histories; 316 included records / 310 asset clusters. Five-, eight- and ten-year approval calculations and sensitivities saved. CMP-002 lifetime PoS remains judgmental; other KPI audits pending |
| Post-LOE / terminal-value analysis | Needham arithmetic decomposition recorded; independent durability assumptions still to research |
| Explain the valuation gap | Pending independent model and reverse DCF |

## Start here

- **Interpretation update: [denominator and recency audit](reports/pos_denominator_and_recency_audit_2026-11-16.txt).** The 310-to-74 reduction is 209 newer entrants plus 27 uncertain entry-date boundary cases. Fifty-four of the 74 entered in 2010–2014; the ten-year result should not be foregrounded as the contemporary CMP-002 benchmark. [Every asset's disposition](data/pos_completion/ten_year_denominator_audit.json).
- **Latest: [completed panel findings and PoS interpretation](reports/pos_completed_panel_findings_2026-11-16.txt)**, [calculated approval horizons and every denominator](data/pos_completion/approval_horizon_results.json), [reviewed ledger](data/pos_completion/completed_program_ledger.json), and [method](protocol/pos_completed_panel_method_2026-11-16.txt). All 449 assigned histories reviewed. Included asset clusters tighten **310 → 81 → 48 → four closest ASOs**. Ten-year mature samples give 21/74, 5/20 and 3/10 approvals; these are horizon observations, **not CMP-002 lifetime PoS**. [Current handoff](context/pos_completion_handoff_2026-11-16.txt).
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
