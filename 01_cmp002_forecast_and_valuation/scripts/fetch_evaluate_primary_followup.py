"""Bounded public registry checks for the explicitly requested follow-up candidates."""
import urllib.request,urllib.parse,json,concurrent.futures
from pathlib import Path
P=Path(__file__).resolve().parents[1];S=P/'sources/evaluate_primary_followup_2026-11-18';S.mkdir(exist_ok=True)
names=['ACTUS-101','AES-103','AGT-181','AGT-182','BMN 307','BN82451','CHF6333','GLPG2451','GLPG2737','HepaStem','HS135','IPL344','MK-8892','NKTT120','PF-07209326','QR-313','aceneuramic acid','SAR443809','SCD-101','SHP623','SPK-3006','alidornase','AstroRx','BLS-M22','HG302','MBF-015','ORT247','PBGM01','Sanguinate','SLN124','PBML04','TSHA-121','AVR-RD-04','CTNS-RD-04','EGT-101','RDGT-101','RTT-1','OPK88001','ADVM-063','LB-301']
def get(n):
 p=S/('ctg_'+n.replace(' ','_')+'.json');url='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode({'query.intr':'"'+n+'"','pageSize':100,'countTotal':'true','format':'json'})
 try:
  if not p.exists():p.write_bytes(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Research/1.0'}),timeout=35).read())
  d=json.loads(p.read_text());return {'query':n,'url':url,'count':d.get('totalCount'),'file':p.name,'retrieved':'2026-11-18','next_page':bool(d.get('nextPageToken'))}
 except Exception as e:return {'query':n,'url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:res=list(ex.map(get,names))
(S/'ctg_manifest.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
