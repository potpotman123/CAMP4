import json,urllib.request,urllib.parse,time,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];S=P/'sources/pos_completion';S.mkdir(exist_ok=True)
base=json.load(open(P/'data/pos_adjudication/integrated_program_ledger.json'))
ali={'ISIS333611':['ISIS 333611','ISIS333611'],'NP001_sodium_chlorite':['NP001','sodium chlorite'],'HYNR-CS':['HYNR-CS','lenzumestrocel','Neuronata'],'GDC-0134':['GDC-0134','GDC0134'],'DNL747':['DNL747','SAR443060'],'BIIB100':['BIIB100','KPT-350'],'SAR443820':['SAR443820','DNL788'],'AMT-162':['AMT-162','APB-102'],'QRL-101':['QRL-101','QRL101'],'QRL-201':['QRL-201','QRL201'],'tofersen':['tofersen','BIIB067','ISIS666853'],'CuATSM':['CuATSM','Cu(II)ATSM'],'prosetin':['prosetin','PRO-101'],'NurOwn':['NurOwn','MSC-NTF'],'HK-001':['HK-001','butylidenephthalide']}
generic={'autologous_BM_stem_cells_Corestem_2010','MNC_Hanyang','MSC3P','Whartons_jelly_MSCs','NP001_regulatory_Tcells'}
manifest=[]
for r in base:
 if r['family']!='als' or r['reference_eligibility']=='excluded':continue
 a=r['asset'];q=' OR '.join(r['trial_ids']) if a in generic else ' OR '.join('"'+s+'"' for s in ali.get(a,[a]))
 params={'query.term':q,'pageSize':100,'countTotal':'true','format':'json'}
 u='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode(params)
 path=S/('als_history_'+a+'.json')
 try:
  if path.exists():raw=path.read_bytes()
  else:
   raw=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'CMP-research/1.0'}),timeout=30).read();path.write_bytes(raw)
   path.with_suffix('.meta.json').write_text(json.dumps({'url':u,'retrieved':'2026-11-16','sha256':hashlib.sha256(raw).hexdigest(),'condition_filter':None},indent=2)+'\n')
  d=json.loads(raw);manifest.append({'asset':a,'file':str(path.relative_to(P)),'count':d.get('totalCount'),'truncated':bool(d.get('nextPageToken'))})
  print(a,d.get('totalCount'),flush=True)
 except Exception as e:manifest.append({'asset':a,'url':u,'error':str(e)});print(a,str(e),flush=True)
 time.sleep(.2)
(P/'data/pos_completion/als_history_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
