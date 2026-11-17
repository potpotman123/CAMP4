import urllib.request,json,concurrent.futures
from pathlib import Path
R=Path(__file__).resolve().parents[1] / 'sources/pos_audit'
ids=['NCT02519036','NCT03186989','NCT04165486','NCT07605429','NCT06617429','NCT05469360','NCT04539041']
def get(n):
 u='https://clinicaltrials.gov/api/v2/studies/'+n
 try:
  d=json.load(urllib.request.urlopen(u,timeout=25));(R/(n+'.json')).write_text(json.dumps({'url':u,'retrieved':'2026-11-16','data':d},indent=2))
  p=d['protocolSection'];s=p['statusModule'];de=p.get('designModule',{});return n,p['identificationModule']['briefTitle'],s.get('startDateStruct'),s.get('lastUpdatePostDateStruct'),s['overallStatus'],s.get('whyStopped'),de.get('enrollmentInfo'),p.get('conditionsModule')
 except Exception as e:return n,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for x in ex.map(get,ids):print(x)
