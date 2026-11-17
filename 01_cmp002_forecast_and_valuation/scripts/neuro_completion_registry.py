"""Bounded molecule alias registry follow-up; never treats earliest hit as verified FIH."""
import json,urllib.request,urllib.parse,concurrent.futures,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/'sources/pos_completion';D.mkdir(parents=True,exist_ok=True)
rows=[x for x in json.loads((P/'data/pos_adjudication/integrated_program_ledger.json').read_text()) if x['family']=='neuro' and x['reference_eligibility']!='excluded']
aliases={'atidarsagene_autotemcel':'OTL-200','elivaldogene_autotemcel':'Lenti-D','onasemnogene_abeparvovec':'AVXS-101','AAVrh10_ARSA':'AAVrh.10cuARSA','AAVrh10_CLN2':'AAVrh.10CUhCLN2','AAV9_CLN7':'AAV9/CLN7','Cabaletta_trehalose':'Cabaletta','Cellavita_HD':'Cellavita','SHP611_IT':'HGT-1110 OR SHP611','BPN14770':'BPN14770 OR zatolmilast','apitegromab':'SRK-015','RO7204239':'RO7204239','risdiplam':'risdiplam OR RO7034067 OR RG7916','RG7800':'RO6885247','branaplam':'LMI070','ganaxolone':'ganaxolone','zorevunersen':'STK-001','apazunersen':'GTX-102','obudanersen':'ION582','rugonersen':'RO7248824','salanersen':'BIIB115','zilganersen':'ION373','tominersen':'ISIS 443139 OR RO7234292','bexicaserin':'LP352','blarcamesine':'ANAVEX2-73','clemizole':'EPX-100','votoplam':'PTC518','MG01CI':'MG01CI','latrepirdine':'Dimebon','cysteamine_RP103':'RP103','deutetrabenazine':'SD-809','cerliponase_alfa':'BMN 190','vesemnogene_lantuparvovec':'vesemnogene lantuparvovec','AT-GTX-501':'AT-GTX-501 OR scAAV9.CB.CLN6','CLN-301':'CLN-301 OR AT-GTX-502','AMT-130':'AMT-130 OR rAAV5-miHTT','taldefgrobep_alfa':'taldefgrobep OR RO7239361 OR BMS-986089','leriglitazone':'MIN-102','selisistat':'SEN0014196','sarizotan':'sarizotan','olesoxime':'olesoxime OR TRO19622','mavoglurant':'AFQ056','basimglurant':'RO4917523','arbaclofen':'STX209 OR arbaclofen'}
assets=sorted({x['asset'] for x in rows})
def run(asset):
 q=aliases.get(asset,asset); slug=''.join(c if c.isalnum() else '_' for c in asset);f=D/('neuro_registry_'+slug+'.json')
 if f.exists():return asset,'cached'
 u='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode({'query.intr':q,'pageSize':100,'format':'json'})
 try:
  d=json.loads(urllib.request.urlopen(u,timeout=45).read());o={'asset':asset,'query':q,'url':u,'retrieved_at':'2026-11-16','response':d};f.write_text(json.dumps(o,indent=2));return asset,len(d.get('studies',[]))
 except Exception as e:
  o={'asset':asset,'query':q,'url':u,'retrieved_at':'2026-11-16','error':str(e)};f.write_text(json.dumps(o,indent=2));return asset,'error'
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for asset,n in pool.map(run,assets):print(asset,n,flush=True)
