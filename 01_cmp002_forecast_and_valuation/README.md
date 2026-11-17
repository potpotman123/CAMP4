# Project 1 — CMP-002 worldwide revenue forecast and valuation

**Question:** What is CMP-002 in SYNGAP1 independently worth, and how do our revenue expectations compare with Street assumptions and expectations implied by the market?

## Workstreams and status

| Workstream | Status / starting point |
|---|---|
| Sell-side context and assumption audit | Eight original reports and extracted text saved; inherited Street data available |
| Reverse DCF | To build: observed EV, development/operating costs, timeline, financing context and sales implied by valuation |
| Independent worldwide revenue forecast | To build: epidemiology, diagnosis, eligibility, uptake, paid exposure, net pricing and country access |
| KPI and PoS comparator research | PoS public-source v1 complete: 24 assets / 28 drug–indication pairs; no statistically calibrated PoS claimed. Other KPI audits pending |
| Post-LOE / terminal-value analysis | Needham arithmetic decomposition recorded; independent durability assumptions still to research |
| Explain the valuation gap | Pending independent model and reverse DCF |

## Start here

- **[PoS audit decision memo](reports/pos_audit_findings_2026-11-16.txt)** and [full evidence report](reports/pos_audit_2026-11-16.html).
- [PoS peer ledger (CSV)](data/pos_audit/program_ledger.csv), [source registry](data/pos_audit/source_registry.json), [scope/limitations](protocol/pos_audit_design_2026-11-16.txt), and [97 internal checks](data/pos_audit/validation.json).
- Current conclusion: Needham's 25% is defensible as an optimistic assumption, not demonstrated conservative or empirically calibrated. Provisional 20% central / 10–35% scenarios are explicit judgment, not estimated probabilities.


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
