"""Four named engineering checks, not a representative PoS sample."""
import concurrent.futures, datetime, json, urllib.parse, urllib.request
from pathlib import Path
P=Path(__file__).resolve().parents[1]
S=P/'sources/evaluate_expansion_2026-11-19';S.mkdir(exist_ok=True)
QUERIES={
 'asundexian_allaliases':'"asundexian" OR "BAY2433334" OR "BAY 2433334" OR "BAY-2433334"',
 'evobrutinib_allaliases':'"evobrutinib" OR "M2951" OR "MSC2364447C" OR "MSC 2364447"',
 'naporafenib':'"naporafenib" OR "LXH254"',
 'rgx121':'"RGX-121" OR "clemidsogene"',
}
def get(item):
 name,q=item;f=S/('registry_'+name+'.json')
 url='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode({'query.intr':q,'pageSize':100,'countTotal':'true','format':'json'})
 try:
  if not f.exists():
   f.write_bytes(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Research/1.0'}),timeout=30).read())
  d=json.loads(f.read_text());matches=[]
  for s in d.get('studies',[]):
   p=s['protocolSection']; st=p.get('statusModule',{});design=p.get('designModule',{})
   matches.append(dict(nct=p['identificationModule']['nctId'],start=st.get('startDateStruct'),phases=design.get('phases'),conditions=p.get('conditionsModule',{}).get('conditions'),interventions=p.get('armsInterventionsModule',{}).get('interventions'),status=st.get('overallStatus')))
  matches.sort(key=lambda x:(x['start'] or {}).get('date','9999'))
  return dict(query=name,url=url,total=d.get('totalCount'),next_page=bool(d.get('nextPageToken')),records=matches,limitation='Earliest returned trial is only a discovery lead; verify identity, indication, prior worldwide studies, and actual dosing.')
 except Exception as e:return dict(query=name,url=url,error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: out=list(ex.map(get,QUERIES.items()))
(S/'registry_linkage_checks.json').write_text(json.dumps(out,indent=2)+'\n')
for x in out:
 print(json.dumps({k:v for k,v in x.items() if k not in ['records','url']}))
 print(json.dumps(x.get('records',[])[:2]))
