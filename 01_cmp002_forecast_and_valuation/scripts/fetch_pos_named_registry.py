import urllib.request,urllib.parse,json,concurrent.futures
from pathlib import Path
R=Path(__file__).resolve().parents[1] / 'sources/pos_audit'
names=['nusinersen','tofersen','tominersen','WVE-120101','WVE-120102','WVE-003','WVE-004','BIIB078','BIIB105','BIIB132','BIIB094','BIIB101','BIIB080','STK-001','GTX-102','RO7248824','ION582','ION373','ION363','ION717','VO659','ION283','NIO752','BIIB115','ISIS 333611']
def get(n):
 u='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode({'query.intr':n,'pageSize':100,'countTotal':'true','format':'json'})
 try:
  d=json.load(urllib.request.urlopen(u,timeout=30));(R/('registry_'+n.replace(' ','_')+'.json')).write_text(json.dumps({'url':u,'retrieved':'2026-11-16','data':d},indent=2))
  rows=[]
  for x in d.get('studies',[]):
   p=x['protocolSection'];s=p['statusModule'];de=p.get('designModule',{});date=s.get('startDateStruct',{});v=p.get('armsInterventionsModule',{}).get('interventions',[])
   if de.get('studyType')!='INTERVENTIONAL':continue
   rows.append((date.get('date','9999'),p['identificationModule']['nctId'],date.get('type'),s['overallStatus'],de.get('enrollmentInfo',{}).get('count'),';'.join(y['name'] for y in v),s.get('whyStopped','')))
  return n,d.get('totalCount'),sorted(rows)[:3]
 except Exception as e:return n,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for x in ex.map(get,names):print(x)
