"""Reconcile researched aliases with archived FDA product inventories; hits require indication review."""
import csv,io,json,re,zipfile,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/'data/pos_completion'
def norm(s):return re.sub('[^a-z0-9]','',str(s).lower())
def strings(x):
 if isinstance(x,str):return [x]
 if isinstance(x,list):return [s for v in x for s in strings(v)]
 return []
def variants(s):
 s=s.lower()
 out={s};out.update(re.split(r'[()/;,]|\s+plus\s+',s));out.add(s.replace('_',' '))
 # Biological suffix is four letters appended with a hyphen, not an asset code.
 out|={re.sub(r'-[a-z]{4}$','',v.strip()) for v in list(out)}
 out|={re.sub(r'\s+(sodium|calcium|hydrochloride|dihydrochloride|citrate|succinate|fumarate|maleate|bromide|besylate|tosylate)$','',v.strip()) for v in list(out)}
 return {norm(v.strip()) for v in out if len(norm(v.strip()))>=5}
zpath=P/'sources/pos_nested/drugsatfda_2026-11-16.zip';z=zipfile.ZipFile(zpath)
def table(n):return list(csv.DictReader(io.StringIO(z.read(n).decode('utf-8-sig',errors='replace')),delimiter='\t'))
dates={}
for s in table('Submissions.txt'):
 if s['SubmissionType']=='ORIG' and s['SubmissionStatus']=='AP':
  d=s['SubmissionStatusDate'][:10];a=s['ApplNo'];dates[a]=min(d,dates.get(a,d))
index={}
for p in table('Products.txt'):
 if p['ApplNo'] not in dates:continue
 for key in ['DrugName','ActiveIngredient']:
  for v in variants(p[key]):
   index.setdefault(v,[]).append({'source':'Drugs@FDA','application':p['ApplNo'],'brand':p['DrugName'],'ingredient':p['ActiveIngredient'],'original_approval_date':dates[p['ApplNo']]})
raw=json.loads((P/'sources/pos_completion/cber_current_lists.json').read_text())
text=raw if isinstance(raw,str) else str(raw.get('result',raw))
cber=[]
for line in text.splitlines():
 if ' | ' not in line or '†' not in line:continue
 cell=line.split(' | ')[0];m=re.search(r'†([^】]+)】',cell)
 if not m:continue
 name=m.group(1)
 if '(' not in name:continue
 cber.append(name)
 for v in variants(name):index.setdefault(v,[]).append({'source':'CBER current approved cellular/gene therapy products','product':name,'original_approval_date':None})
base=json.loads((P/'data/pos_adjudication/integrated_program_ledger.json').read_text())
updates={}
for f in ['als_updates.json','neuro_updates.json','metabolic_updates.json','systemic_updates.json']:
 if not (D/f).exists():continue
 x=json.loads((D/f).read_text());seq=x.values() if isinstance(x,dict) else x
 for r in seq:updates[r['id']]=r
out=[]
for b in base:
 u=updates.get(b['id'],{});src=b['source_record']
 aliases=[b['asset'],u.get('canonical_asset','')]
 for o in [src,u]:
  for k in ['aliases','FDA_aliases','fda_aliases','fda_search_aliases','search_aliases','approval_aliases','canonical_names']:aliases+=strings(o.get(k,[]))
 tokens=set(v for a in aliases for v in variants(a));hits={}
 for v in tokens:
  for hit in index.get(v,[]):hits[json.dumps(hit,sort_keys=True)]=dict(hit,matched_alias=v)
 out.append({'id':b['id'],'asset':b['asset'],'aliases':sorted(set(aliases)), 'matches':list(hits.values()),'finding':'approval_candidate_requires_indication_confirmation' if hits else 'no_alias_match_in_saved_FDA_inventories','negative_caveat':'A negative alias join can miss undiscovered names or historical CBER products; not independent proof of nonapproval.'})
(D/'fda_inventory_matches.json').write_text(json.dumps(out,indent=2)+'\n')
(D/'fda_inventory_metadata.json').write_text(json.dumps({'as_of':'2026-11-16','drugsatfda_zip_sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),'original_approval_applications':len(dates),'cber_product_names':cber,'historical_cber_supplemental_files':[str(f.relative_to(P)) for f in (P/'sources/pos_completion').glob('cber*.json')],'method':'Exact normalized aliases and biologic suffix variants; matching does not establish indication or inception eligibility. Current CBER list plus historical source review; archive gaps disclosed.'},indent=2)+'\n')
print('Reviewed',len(out),'rows;',sum(bool(r['matches']) for r in out),'with FDA inventory candidates;',len(cber),'CBER product names')
