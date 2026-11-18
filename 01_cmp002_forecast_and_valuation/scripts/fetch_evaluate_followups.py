import urllib.request,json,concurrent.futures
from pathlib import Path
P=Path(__file__).resolve().parents[1];S=P/'sources/evaluate_2026-11-18'
ids=['NCT04201405','NCT03952637','NCT04693598','NCT02788721','NCT03540524','NCT01747980','NCT02107846']
def get(n):
 p=S/(n+'.json');u='https://clinicaltrials.gov/api/v2/studies/'+n
 try:
  if not p.exists():p.write_bytes(urllib.request.urlopen(u,timeout=30).read())
  d=json.loads(p.read_text())['protocolSection'];return dict(nct=n,url=u,start=d['statusModule'].get('startDateStruct'),status=d['statusModule'].get('overallStatus'),title=d['identificationModule']['briefTitle'],interventions=d.get('armsInterventionsModule',{}).get('interventions'),enrollment=d.get('designModule',{}).get('enrollmentInfo'))
 except Exception as e:return dict(nct=n,error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:r=list(ex.map(get,ids))
(S/'followup_manifest.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
