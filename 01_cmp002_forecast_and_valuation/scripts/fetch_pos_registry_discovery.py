import urllib.request,urllib.parse,json
from pathlib import Path
r=Path(__file__).resolve().parents[1]
q='(antisense OR oligonucleotide) AND (intrathecal OR intraventricular)'
u='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode({'query.term':q,'pageSize':100,'countTotal':'true','format':'json'})
d=json.load(urllib.request.urlopen(u,timeout=35))
(r/'sources/pos_audit/registry_discovery.json').write_text(json.dumps({'url':u,'retrieved':'2026-11-16','data':d},indent=2))
print('Total',d.get('totalCount'),'returned',len(d['studies']),'nextPage?',bool(d.get('nextPageToken')))
for x in d['studies']:
 p=x['protocolSection'];a=p['identificationModule'];b=p['statusModule'];v=p.get('armsInterventionsModule',{}).get('interventions',[])
 print(a['nctId'],b.get('startDateStruct',{}).get('date'),b['overallStatus'],'|',','.join(y['name'] for y in v),'|',a['briefTitle'][:100])
