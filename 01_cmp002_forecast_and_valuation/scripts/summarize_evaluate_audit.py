import json,re,collections,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];O=P/'data/evaluate_audit';S=P/'sources/evaluate_2026-11-18'
a=json.loads((O/'matched_310.json').read_text()); original={r['asset_cluster']:r for r in json.loads((P/'data/pos_molecule_status/cluster_status.json').read_text())};dec={r['cluster']:r for r in json.loads((O/'status_decisions.json').read_text())};reviews=[]
scope={'imr687','nomacopan','pr001_gd2','qbw251','zilucoplan'}
for r in a:
 if r['old_status']!='failed':continue
 live=[x for x in r['matched_rows'] if re.match(r'^(Phase|Marketed|Approved|Filed)',x['WW Phase (Current)'])]
 if r['cluster'] in ['abo101','glpg3067']:category='corrected_to_active_primary_corroboration'
 elif not r['matched_rows']:category='no_accepted_vendor_match_prior_evidence_retained'
 elif live and r['cluster'] in scope:category='other_indication_activity_not_original_indication_success'
 elif live:category='vendor_current_phase_conflicts_prior_stop_evidence_retained_with_flag'
 else:category='vendor_nonactive_record_consistent_with_prior_failure'
 o=original[r['cluster']]
 reviews.append(dict(cluster=r['cluster'],prior_confidence=o['confidence'],category=category,decision=dec.get(r['cluster'],{}).get('new_status','failed'),evaluate_product_ids=r['evaluate_product_ids'],prior_stop_evidence=[dict(reason=m['reason'],claims=m['accepted_prior_claims'],sources=m['sources']) for m in o['members']],vendor_rows=r['matched_rows'],note='Vendor nonactive status alone does not establish reason/date or irreversibility. Reversible probable failures remain separately flagged. Where explicit dated sponsor stop conflicts with a current vendor phase, retain original source decision; no evidence of restart established except the two documented corrections.'))
(O/'failed_113_audit.json').write_text(json.dumps(reviews,indent=2)+'\n')
q=json.loads((O/'discovery_queue.json').read_text()); chosen=[]
for r in q:
 if r['technology'] not in ['Gene therapy','DNA & RNA therapeutics','Gene-Modified Cell Therapy']:continue
 if not any(re.search('Angelman|Rett|Dravet|Huntington|Spinal muscular|Batten|lysosomal|leukodystrophy|Friedreich|Sanfilippo|Fragile X|Krabbe',d,re.I) for d in r['indications']):continue
 if not any(re.search(r'\[.*Phase [IV]',x['Indication Summary']) for x in r['rows']):continue
 chosen.append(dict(evaluate_product_id=r['evaluate_product_id'],product=r['product'],indications=r['indications'],prior_518_match=r['prior_518_match'],disposition='not_yet_qualified; do not count vendor phase as dosing'))
addids={x['pid'] for x in json.loads((O/'qualified_additions.json').read_text())}
post={'40918','206595','231254','1049534','1198924','1253374','1321486'}
no_dose={'40919','233530'};scopewrong={'38477','11738','32241','205303'}
for r in chosen:
 id=r['evaluate_product_id']
 if id in addids:r['disposition']='reviewed_addition; RGX381 grouped with RGX181 in main calculation'
 elif id in post:r['disposition']='post_2024_entry_or_not_yet_dosed; preserve recent watchlist, outside frozen entry window'
 elif id in no_dose:r['disposition']='zero_actual_enrollment; predose attrition only'
 elif id in scopewrong:r['disposition']='clinical phase in another indication; target indication preclinical/no verified exposure'
 elif id in {'226609','228565','1377324'}:r['disposition']='previously among43 entry-uncertain; registry-exposure sensitivity only'
 elif id=='29091':r['disposition']='possible existing AAVrh10_ARSA alias; no duplicate addition pending exact construct resolution'
 elif id=='41223':r['disposition']='EGT101 treated history identified but first-dose interval unresolved; retain priority for EU registry/clinical-report extraction'
(O/'genetic_cns_discovery_screen.json').write_text(json.dumps(chosen,indent=2)+'\n')
manifest=dict(retrieved='2026-11-18',method='User-authorized Chrome UI Create Report -> Products -> CSV export; no private API/scraping',source='https://app.evaluate.com/ux/WebReport/ViewReport.aspx',reports=[dict(file='orphan_all_status.csv',filter='Orphan Drug (Any Designation)=YES; all companies/statuses',rows=14599),dict(file='disease_all_status.csv',filter='51 indication classes matched with partial-name import; no orphan restriction; all statuses',rows=10246)],requested_disease_terms=['Angelman','Dravet','Rett','Fragile X','SYNGAP','CDKL5','Lennox','Huntington','Spinocerebellar','Alexander','Batten','Lafora','Adrenoleukodystrophy','Metachromatic','Spinal muscular','Duchenne','GNE','Amyotrophic','Friedreich','Myotonic','Pompe','Fabry','Gaucher','Niemann','Mucopolysaccharidosis','Lysosomal','Gangliosidosis','Phenylketonuria','Urea cycle','Hyperoxaluria','Wilson','Glycogen','Hypophosphatasia','Haemophilia','Sickle','Thalassaemia','Paroxysmal nocturnal','Achondroplasia','Angioedema','Cystic fibrosis','Pulmonary hypertension','Epidermolysis','Biliary','Wiskott','Severe combined','Granulomatous','Alveolar proteinosis','Krabbe'],unmatched_terms=['SYNGAP','CDKL5','Alexander','Lafora','Adrenoleukodystrophy','Gangliosidosis','Hyperoxaluria','Glycogen'],known_false_positive_classes=['Biliary cancer','Poisoning neutralization','Tourette\'s syndrome','Barrett\'s oesophagus'],limitations=['Orphan designation includes oncology and drugs with nonrare co-indications; not identical to rare disease definition','Disease taxonomy coarser than genetic diagnosis; generic buckets and unmatched names prevent exhaustive coverage','PhaseI can mean regulatory stage before actual dosing','Company abandonment/transfer is not global molecule death','Unique Product ID does not guarantee our construct-level independence; known alias aggregation errors','Standard exports lack reliable first-human dates for the full candidate universe; Omnium risk upgrade unavailable','No purchase, new subscription, outreach or account modification'],hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in S.glob('*.csv')})
(S/'export_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('failed audit',collections.Counter(x['category'] for x in reviews));print('discovery',len(chosen),collections.Counter(x['disposition'] for x in chosen))
