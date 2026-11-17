"""Render a concise decision memo and searchable, self-contained evidence ledger."""
import json,html,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/'data/pos_adjudication';R=P/'reports'
s=json.loads((D/'nested_reference_results.json').read_text());rows=json.loads((D/'integrated_program_ledger.json').read_text());tiers=s['nested_reference_results'];R.mkdir(exist_ok=True)
lines=['CMP-002 PoS audit: expanded public-source adjudication','As of 16 November 2026 | Project 1 | Decision memo','',
'CONCLUSION',
'The program-history audit is materially expanded, but a calibrated set of three lifetime approval probabilities is NOT completed. Needham\'s25% remains a plausible valuation assumption; this research does not establish that it is conservative, too high, or statistically preferable to20%. The earlier20% central case and10–35% range remain judgmental scenarios, not empirical estimates. Do not blend overlapping reference sets as if they supplied independent probabilities.',
'',
'What is completed: all606 prioritized early-industry registry buckets were assigned an auditable disposition; supplemental alias/stage searches increased reviewed buckets to952. These yielded518 provisional program–indication records, not518 verified clinical entrants. The integrated reference view retains418 provisionally eligible records, excludes69 and leaves31 unresolved for entry/identity. Outcome research is uneven:233 of418 retained rows have targeted/reused outcome review;185 remain registry-only.267 retained rows have unknown program fate. These limitations are measured in the saved records, not hidden in a fitted number.',
'',
'WHAT THE NESTED COMPARISONS ACTUALLY SHOW',
'All counts below describe a selected public-source reference set. They are not population PoS estimates. Unresolved includes both known ongoing programs and programs whose fate could not be established. Program stops include non-biological reasons; they are not all efficacy failures.',
'',
'Group | Records | FDA approvals | Observed program stops | Unresolved']
for t in tiers:lines.append(f"{t['tier']} {t['label']} | {t['n']} | {t['FDA_approved']} | {t['program_stop_observed']} | {t['unresolved']}")
lines += ['',
'R1 starts from a purposive48-disease panel, not all rare diseases or all drugs. R2 requires a genetically defined CNS disease and intended neurologic treatment; a systemic metabolic disease is not automatically CNS because untreated patients can develop brain injury. R3 requires a nucleic-acid or gene-modified modality: ASO, siRNA, in-vivo gene therapy or ex-vivo genetically modified cells. Recombinant enzymes and small-molecule splice modifiers are outside that modality definition, even when they restore a missing protein. These mechanisms remain in R1/R2 and the complete ledger.',
'',
'R4 is the prespecified mechanistic anchor subset: zorevunersen/Dravet, apazunersen/Angelman, rugonersen/Angelman and obudanersen/Angelman. It is not an exhaustive result of route/restoration filters. All are intrathecal ASOs intended to raise a deficient neuronal protein in developmental disease. They are closer to CMP-002 on delivery, biology and efficacy-measurement challenges, but three share Angelman/UBE3A biology and are correlated. They do not use the same CAMP regulatory-RNA platform or establish SYNGAP1 reversibility. Zero approvals, one efficacy stop and three ongoing programs is not0% PoS.',
'',
'Unknown filter membership remains explicit:11 additional R1 records have insufficient CNS classification; four records potentially qualify for R3 but lack a required flag. The table does not count missing as false. Indication-family aggregation and combination programs remain further record-granularity limitations. Counts should not be read as independent Bernoulli trials.',
'',
'ARITHMETIC CHECKS, NOT PROBABILITY ESTIMATES',
'For each reference set, let A=approved, F=observed program stops and U=unresolved. A/N is approvals observed to date. Conditional on all current stops remaining stopped, the possible eventual fraction lies between A/N and(A+U)/N. These are finite-record completion envelopes, not confidence intervals, not statistical identification bounds for the drug population, and not CMP-specific estimates. Restarts can invalidate the upper-end assumption.',
'']
for t in tiers:
 lo,hi=t['conditional_completion_envelope'];lines.append(f"{t['tier']}: observed approvals{100*lo:.1f}%; conditional completion envelope{100*lo:.1f}–{100*hi:.1f}%.")
lines += ['',
'All four envelopes admit25%; this demonstrates how little the incomplete records constrain the answer. For R3, seven additional approvals among39 unresolved records would produce14/54=25.9%. That is a completion scenario, not a prediction. In the closest four, one eventual approval among the three ongoing programs would produce1/4=25%. Small-sample arithmetic does not validate Needham.',
'',
'WHY THE ANSWER CAN CHANGE WITH THE DENOMINATOR',
'The more fully researched HAE/PNH reference slice has34 observations across33 clusters:9 FDA approvals,6 observed program stops and19 unresolved US outcomes. The latter includes13 ongoing, one China-only approval, one reversible suspension and four unknowns. The observed FDA fraction is26.5%, but the indications, mechanisms, prior target validation and endpoint measurability differ substantially from CMP-002. Only13 of those rows have explicit first-human evidence. It is useful evidence against a universal claim that25% is implausible for any rare-disease program; it is not a25% calibration for a pre-dose CNS platform.',
'',
'The metabolic/neuromuscular slice also provides a better-researched maturity check: every one of56 pre-2019 reference rows received targeted external review. Its stricter terminal-outcome coding finds13 FDA approvals,11 documented discontinuations and32 other/unknown outcomes. The23.2% observed approval fraction is not lifetime PoS. This slice uses a stricter permanent-stop gate than the integrated table; the original and integrated definitions are both retained, rather than silently combining incompatible failure definitions.',
'',
'RECENCY AND STAGE MATCHING',
'The user prioritizes recent experience and CMP-002\'s pre-first-dose stage. We preserve calendar cohorts instead of applying an arbitrary recency multiplier. Within R3:',
'Observed entry vintage | Records | Approvals | Stops | Unresolved']
for yr,t in tiers[2]['entry_vintage'].items():lines.append(f"{yr} | {t['n']} | {t['FDA_approved']} | {t['program_stop_observed']} | {t['unresolved']}")
lines += ['',
'The recent2021–2024 set has27/30 unresolved records. Comparing its1/30 observed approval fraction with6/13 among2010–2016 records would confound follow-up time, discovery completeness and biological differences with changes in success rates. Older successful modalities are useful evidence that delivery can work, with less direct weight on current SYNGAP1 development. The recent close peers remain central for mechanistic judgment, despite not supplying mature outcomes.',
'',
'Clinical entry is another boundary. A trial\'s posted start date can refer to enrollment rather than dosing, and an actual start date can coexist with zero actual enrollment. We found never-enrolled programs such as ARO-SOD1, VY-HTT01, MRT5201 and HMI203. These cannot enter a first-dose denominator. They are relevant to CMP-002\'s pre-dose stage, but the ascertainment here does not supply a complete population of cleared-but-never-dosed assets from which to estimate that extra attrition. No numerical pre-dose haircut is therefore fitted.',
'',
'EVIDENCE THAT MATTERS FOR CMP-002',
'Favorable: successful genetically directed CNS development is real. R3 includes FDA approvals for nusinersen, onasemnogene abeparvovec, tofersen, atidarsagene autotemcel, elivaldogene autotemcel, zilganersen and UX111. The set spans protein restoration, toxic-protein reduction and cell-mediated enzyme delivery; these are mechanisms with different translational and regulatory risks. Approval type and later safety/withdrawal events must remain separate from the endpoint ever approved. Representative regulator records:',
'https://www.fda.gov/vaccines-blood-biologics/zolgensma',
'https://www.fda.gov/news-events/press-announcements/fda-approves-first-gene-therapy-children-metachromatic-leukodystrophy',
'https://www.fda.gov/media/194921/download',
'',
'Unfavorable: convincing rationale and target engagement do not ensure a clinically meaningful response or acceptable safety. The ASO peer set retains the apazunersen, BIIB078, WVE-004 and WVE-120101/120102 efficacy failures. Beyond ASOs, GDC-0134 development stopped for safety, while VRG50635 reached the brain and engaged its pathway but did not deliver the intended efficacy result. Those ALS programs are weaker biological matches to SYNGAP1; they are useful disconfirming evidence against treating CNS exposure or a biomarker change as sufficient proof. Primary sources:',
'https://pmc.ncbi.nlm.nih.gov/articles/PMC8791798/',
'https://www.vergelabs.blog/p/what-we-learned-from-the-trial-of',
'',
'Program-fate errors can bias either direction. Adrabetadex continued under a new sponsor after Mallinckrodt\'s discontinuation; lucerastat restarted PhaseIII after an earlier failure. UX111\'s terminated advanced-disease study did not prevent subsequent FDA approval in a different severity window within MPSIIIA. A completed or terminated study is not itself an asset-level terminal outcome. Conversely, negative efficacy followed by explicit program abandonment is retained as a stop. Every case\'s source and scope are in the ledger.',
'',
'IMPORTANT CORRECTION TO EARLIER WORK',
'The prior ASO audit used novel_target_at_entry without consistently checking earlier human target exposure. That flag cannot support the claimed literal never-tested-in-humans filter. Tofersen followed earlier SOD1 human work; later HTT and UBE3A programs also followed earlier target exposure. We preserved legacy flags and reset unsupported literal novelty to unknown. No approved target-directed treatment is a separate concept from no prior human exposure or no prior clinical efficacy. The earlier16-asset/19-pair description as a uniformly verified novel-target cohort is superseded. This correction does not erase the documented clinical outcomes.',
'',
'COMPUTATION, ACCESS AND STOPPING RULE',
'The existing ClinicalTrials.gov APIv2 inventory supplies6,407 distinct trials and4,352 exact-name/condition buckets. The new screen uses actual structured condition matches, date windows, sponsor/stage and FDA ingredient flags. Ingredient matches only identify review candidates: they do not establish indication-specific approvals. Named searches and original regulator, sponsor, SEC, trial-publication and sponsor-submitted registry statements resolve aliases and outcomes. FDA Drugs@FDA and CBER sources are complementary; the latter matters for gene therapies. Public source snapshots and request metadata are preserved.',
'',
'A local merge then standardizes source-specific schemas, separates FDA outcomes from non-US approvals, retains failures/unknowns, preserves shared asset clusters and applies nested filters.19 integration checks validate counts, nesting, entry exclusions, jurisdiction and shared-source collisions; offline rebuilds reproduce all four input ledgers byte-for-byte. These checks validate arithmetic/provenance, not representativeness. Additional family-specific checks are saved. Three parallel reviewers were explicitly authorized by the user; the final merge and interpretation received a separate read-only review.',
'',
'No paid database, outreach or black-box predictive fitting was used. The previously identified Parker2017-designation cohort remained unavailable beyond metadata/abstract; full-text endpoints returned401/403/406 or no usable paper. No unseen results were imported. Public registry expansion is cheap computationally but does not solve identity, entry chronology, silent abandonment or missing historical eligibility. A commercial history database could improve ascertainment but would still require indication and stage adjudication.',
'',
'WHAT IS STILL UNFINISHED / WHAT MAY ENTER THE MODEL',
'Case evidence, sources, named comparator membership and scenario sensitivities can inform the model now. These pooled observed fractions cannot enter as estimated CMP-002 lifetime PoS. The broad row set includes185 registry-only records and many histories still lack true first-human dates. Only14 of418 currently carry explicit first-human verification. This is an evidence-qualification count, not a claim that the others were never dosed.',
'',
'The remaining work is in data/pos_adjudication/remaining_work_queue.json: recover earlier healthy-volunteer/other-indication exposure, resolve registration intent and disease subtypes, verify endpoints for untouched rows, and qualify time-to-event follow-up. Recent active programs will still require censoring even after those tasks. A competing-risk estimator already exists, but fitting it now would mislabel ignorance about program fate as independent right censoring. Lifetime extrapolation would require further assumptions even after a valid fixed-horizon analysis.',
'',
'The study should stay marked partial rather than claiming the requested broad PoS calculation is done. Further expansion into more unreviewed trials is stopped here because it would enlarge the proxy denominator without resolving the measurement problem. The highest-value continuation is closure of entry/outcome histories for a frozen, auditable cohort, with completeness diagnostics; not another raw search expansion or an arbitrary blend of the ratios above.',
'',
'DELIVERABLES AND REPRODUCTION',
'data/pos_adjudication/integrated_program_ledger.json: full records with source-specific evidence retained.',
'data/pos_adjudication/nested_reference_results.json: membership, calendar strata, arithmetic and input hashes.',
'data/pos_adjudication/remaining_work_queue.json: explicit unfinished qualification/outcome work.',
'data/pos_adjudication/integration_validation.json: checks and exclusions.',
'reports/pos_adjudication_2026-11-16.html: searchable human-readable ledger.',
'Run scripts/adjudicate_als.py, neuro_adjudication.py, metabolic_build.py, systemic_build.py; then integrate_pos_adjudication.py and render_pos_adjudication.py. All operate from saved inputs without fresh network access. The raw screening and retrieval scripts are retained separately.',
'']
# Restore readability in compact manually recorded prose without changing numbers.
text='\n'.join(lines)
for a,b in [('Needham\'s25%','Needham\'s 25%'),('all606','all 606'),('to952','to 952'),('yielded518','yielded 518'),('not518','not 518'),('retains418','retains 418'),('excludes69','excludes 69'),('leaves31','leaves 31'),('review:233','review: 233'),('of418','of 418'),('rows:233','rows: 233'),('records.267','records. 267'),('purposive48','purposive 48'),('not0%','not 0%'),('explicit:11','explicit: 11'),('admit25%','admit 25%'),('among39','among 39'),('produce14','produce 14'),('produce1/4','produce 1/4'),('has34','has 34'),('across33','across 33'),('clusters:9','clusters: 9'),('includes13','includes 13'),('Only13','Only 13'),('a25%','a 25%'),('that25%','that 25%'),('one of56','one of 56'),('finds13','finds 13'),('fraction is26','fraction is 26'),('The23','The 23'),('recent2021','recent 2021'),('has27','has 27'),('its1/30','its 1/30'),('with6/13','with 6/13'),('among2010','among 2010'),('earlier16','earlier 16'),('supplies6','supplies 6'),('APIv2','API v2'),('PhaseIII','Phase III'),('Parker2017','Parker 2017'),('returned401','returned 401'),('includes185','includes 185'),('Only14','Only 14'),('further20','further 20'),('preferable to20','preferable to 20'),('earlier20','earlier 20'),('case and10','case and 10')]:text=text.replace(a,b)
(R/'pos_expanded_adjudication_2026-11-16.txt').write_text(text)
# Compact HTML report with text-searchable ledger; no external scripts or resources.
esc=html.escape
trs=[]
for r in rows:
 src=[]
 for e in r['sources']:
  u=e if isinstance(e,str) else e.get('url')
  if u:src.append(f'<a href="{esc(u,quote=True)}" target="_blank" rel="noopener">source</a>')
 evidence=' '.join(src[:4]) or '<span class="muted">See inherited evidence in JSON</span>'
 note=r['eligibility_reason']
 trs.append('<tr data-text="'+esc(' '.join([r['asset'],r['indication'],r['family'],r['status'],r['reference_eligibility']]).lower(),quote=True)+'">'+''.join('<td>'+x+'</td>' for x in [esc(r['asset']),esc(r['indication']),esc(r['entry_proxy'] or 'unknown'),esc(r['status']),esc(r['reference_eligibility']),esc(r['outcome_review']),evidence+'<details><summary>Entry limitation</summary>'+esc(note)+'</details>'])+'</tr>')
css='body{font:16px/1.55 system-ui;margin:0;color:#172b41;background:#f5f7fa}main{max-width:1400px;margin:auto;padding:32px}h1{font-size:32px}header{border-bottom:4px solid #147d92}section{background:white;padding:24px;margin:24px 0;border-radius:8px}pre{white-space:pre-wrap;font:16px/1.6 system-ui;max-width:1000px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:10px;border-bottom:1px solid #dbe2ea;vertical-align:top}th{background:#172b41;color:white;position:sticky;top:0}a{color:#066a8d}input{padding:12px;width:min(650px,90%);font-size:16px}.notice{background:#fff1c7;padding:18px;border-left:5px solid #aa7800}.muted{color:#617080}details{margin-top:8px}summary{cursor:pointer}@media print{input{display:none}main{padding:0}section{padding:8px}tr{break-inside:avoid}}'
page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CMP-002 PoS — expanded adjudication</title><style>'+css+'</style></head><body><main><header><h1>CMP-002 PoS: expanded evidence audit</h1><p>Project 1 · 16 November 2026 · Public sources</p></header><p class="notice"><strong>Partial study, not a calibrated PoS estimate.</strong> 518 mapped histories; 418 provisional reference records. The counts below cannot establish a lifetime approval probability.</p><section><pre>'+esc(text)+'</pre></section><section><h2>Searchable program ledger</h2><p>Includes exclusions and unknowns. Filter by asset, disease, status, research group or eligibility.</p><input id="q" placeholder="Search the evidence ledger" aria-label="Search the evidence ledger"><p id="count">518 records</p><div style="overflow:auto"><table><thead><tr><th>Asset</th><th>Indication</th><th>Entry proxy</th><th>Observed status</th><th>Reference eligibility</th><th>Review depth</th><th>Evidence</th></tr></thead><tbody>'+''.join(trs)+'</tbody></table></div></section></main><script>const q=document.querySelector("#q"),rr=[...document.querySelectorAll("tbody tr")];q.addEventListener("input",()=>{let n=0;for(const r of rr){const show=r.dataset.text.includes(q.value.toLowerCase());r.hidden=!show;n+=show;}document.querySelector("#count").textContent=n+" records";});</script></body></html>'
(R/'pos_adjudication_2026-11-16.html').write_text(page)
print('Wrote decision memo and searchable ledger:',len(rows),'records')
