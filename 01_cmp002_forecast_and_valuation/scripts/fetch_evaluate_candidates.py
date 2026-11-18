import urllib.request,urllib.parse,json,concurrent.futures
from pathlib import Path
P=Path(__file__).resolve().parents[1];S=P/'sources/evaluate_2026-11-18';
names=['OTL-201','EGT-101','TSHA-118','AXO-AAV-GM1','RGX-181','PBKR03','TSHA-101','FBX-101','PBML04','RGX-381','TSHA-121','ADVM-063','OPK88001','NBIB-223','AVR-RD-04','VY-HTT01','RC001','SGT-212','ASP2016','ANB-004','SKG0201','MVX-220','RTT-1','ION337','RDGT-101','SRP-1005','GB221','ER-2001']
def get(n):
 p=S/('ctg_'+n+'.json');url='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode({'query.intr':'"'+n+'"','pageSize':100,'countTotal':'true','format':'json'})
 try:
  if not p.exists():p.write_bytes(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Research/1.0'}),timeout=35).read())
  d=json.loads(p.read_text());return {'query':n,'url':url,'count':d.get('totalCount'),'file':p.name,'retrieved':'2026-11-18','next_page':bool(d.get('nextPageToken'))}
 except Exception as e:return {'query':n,'url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:res=list(ex.map(get,names))
(S/'ctg_manifest.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
