"""Reconcile user-authorized Evaluate UI exports. No service/API access in this script."""
import csv,json,re,collections,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]; O=P/'data/evaluate_audit'; O.mkdir(exist_ok=True)
def norm(s):return re.sub('[^a-z0-9]','',re.sub(r'\b(sodium|hydrochloride)\b','',s.lower()))
rows=[]
for f in ['orphan_all_status.csv','disease_all_status.csv']:
 for r in csv.DictReader((P/'sources/evaluate_2026-11-18'/f).open()):r['export_file']=f;rows.append(r)
products=collections.defaultdict(list)
for r in rows:
 if r['Product ID']:products[r['Product ID']].append(r)
idx=collections.defaultdict(set)
for pid,rs in products.items():
 for r in rs:
  for v in [r['Product'],r['Generic Name'],*r['Research Codes'].split(';')]:
   if len(norm(v))>3:idx[norm(v)].add(pid)
manual={'aavrh10cln2':['LX1004'],'bn82451b':['BN82451'],'apazunersen':['GTX-102'],'aav9cln7':['CLN7 gene therapy program'],'geneticallycorrectedculturedepidermalautograftatmp':['Hologene 7'],'prx112':['PRX-112'],'glpg2451':['GLPG2451'],'glpg2737':['GLPG2737'],'saer':['Ace-ER'],'ptw00210mgggel':['QR-313'],'globinrestoredautologoushsc':[]}
clusters=json.loads((P/'data/pos_molecule_status/cluster_status.json').read_text()); ledger=json.loads((P/'data/pos_completion/completed_program_ledger.json').read_text())
def match(c):
 terms=[c['asset_cluster'],*c.get('assets',[c.get('asset','')]),*manual.get(c['asset_cluster'],[])]
 for v in terms[:]:terms+=re.split(r'[()/]',v)
 ids=set().union(*(idx.get(norm(t),set()) for t in terms))
 # Reviewed collisions: different sponsor/molecule or successor aggregated by vendor.
 reject={'abo101':{'208643'},'apazunersen':{'62080'},'isis333611':{'40790'},'glpg2451':{'57224'},'ap101':{'1557','215183'}}
 if c['asset_cluster']=='ap101':
  ids={i for i in ids if not any(r['Product']=='Filsuvez' for r in products[i])}
 return sorted(ids-reject.get(c['asset_cluster'],set()))
audit=[];matched=set()
for c in clusters:
 ids=match(c);matched.update(ids)
 rs=list({(r['Products|Record Id'],r['Indication Summary']):r for pid in ids for r in products[pid]}.values())
 audit.append(dict(cluster=c['asset_cluster'],assets=c['assets'],indications=c['indications'],old_status=c['status'],old_confidence=c['confidence'],flags=c['flags'],evaluate_product_ids=ids,matched_rows=rs))
priorids=set()
for c in ledger:priorids.update(match(c))
new=[]
for pid,rs in products.items():
 if pid in matched:continue
 disease=sorted({r.get('Indication Level 3','') for r in rs}-{''})
 if not disease:continue
 new.append(dict(evaluate_product_id=pid,product=rs[0]['Product'],generic=rs[0]['Generic Name'],technology=rs[0]['Technology'],prior_518_match=pid in priorids,indications=disease,rows=list({(r['Products|Record Id'],r['Indication Summary']):r for r in rs}.values())))
for name,data in [('matched_310',audit),('discovery_queue',new)]: (O/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
summary=dict(export_rows=len(rows),unique_products=len(products),matched_clusters=sum(bool(x['evaluate_product_ids']) for x in audit),coverage={s:dict(matched=sum(x['old_status']==s and bool(x['evaluate_product_ids']) for x in audit),total=sum(x['old_status']==s for x in audit)) for s in ['approved','failed','active','unknown']},discovery_candidates=len(new),note='Discovery queue is NOT qualified clinical entrants; includes preclinical, pre-2010, post-2024, repurposed and false-positive indication matches. A name match is not final indication-level adjudication.')
(O/'coverage.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2))
for a in audit:
 if a['old_status']=='unknown':
  print('\n',a['cluster'],a['indications'])
  for r in a['matched_rows']:print(r['Product ID'],r['Company'],r['Product'],r['Indication Summary'],r['Termination Date'])
