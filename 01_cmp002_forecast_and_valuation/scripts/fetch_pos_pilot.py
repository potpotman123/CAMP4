import urllib.request, urllib.parse, json, time, hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]; S=P/'sources/pos_nested'
def fetch(name,url,data=None):
 path=S/name
 if path.exists(): return path.read_bytes()
 req=urllib.request.Request(url,data=data,headers={'User-Agent':'CMP-research/1.0','Accept':'application/json,text/html'})
 try:
  r=urllib.request.urlopen(req,timeout=45); raw=r.read()
  path.write_bytes(raw)
  (S/(name+'.meta.json')).write_text(json.dumps({'url':url,'post':data.decode() if data else None,'retrieved':'2026-11-16','content_type':r.headers.get('Content-Type'),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},indent=2))
  return raw
 except Exception as e:
  print(name,type(e).__name__,str(e));return None
if __name__=='__main__':
 params={'Product_name':'','sponsor_name':'','Designation':'','Designation_Start_Date':'01/01/2010','Designation_End_Date':'12/31/2010','Search_param':'DESDATE','Output_Format':'Detailed','Sort_order':'GENERIC_NAME','RecordsPerPage':'500','newSearch':'Run Search'}
 raw=fetch('fda_orphan_2010.html','https://www.accessdata.fda.gov/scripts/opdlisting/oopd/OOPD_Results.cfm',urllib.parse.urlencode(params).encode())
 if raw: print('FDA pilot bytes',len(raw),raw[:150])
 pilots={'nusinersen':['nusinersen','ISIS 396443','Spinraza'],'GTX102':['GTX-102','apazunersen'],'vosoritide':['vosoritide','BMN 111'],'olipudase':['olipudase alfa'],'ataluren':['ataluren','PTC124'],'valoctocogene':['valoctocogene roxaparvovec','BMN 270'],'aceer':['aceneuramic acid','Ace-ER'],'tominersen':['tominersen','IONIS-HTTRx','RG6042']}
 for name,aliases in pilots.items():
  q=' OR '.join('"'+x+'"' for x in aliases)
  u='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode({'query.intr':q,'pageSize':100,'countTotal':'true','format':'json'})
  raw=fetch('pilot_ctg_'+name+'.json',u)
  if raw:
   d=json.loads(raw);print(name,d.get('totalCount'),len(d.get('studies',[])),bool(d.get('nextPageToken')))
  time.sleep(.2)
 for term in ['NUSINERSEN','VOSORITIDE','OLIPUDASE','VALOCTOCOGENE','ATALUREN','TOMINERSEN']:
  u='https://api.fda.gov/drug/drugsfda.json?'+urllib.parse.urlencode({'search':'products.active_ingredients.name:"'+term+'"','limit':10})
  raw=fetch('pilot_fda_'+term.lower()+'.json',u)
  if raw: print(term,json.loads(raw).get('meta',{}).get('results'))
  time.sleep(.2)
