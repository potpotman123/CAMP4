import json,sys,urllib.parse,time
from pathlib import Path
from fetch_pos_pilot import fetch
P=Path(__file__).resolve().parents[1]
# Use same fetch primitive; it saves in pos_nested, preserving metadata/hash.
rows=json.loads((P/'data/pos_adjudication/als_program_ledger.json').read_text())
aliases={'NurOwn':['NurOwn','MSC-NTF'],'NP001_sodium_chlorite':['NP001'],'HYNR-CS':['HYNR-CS','lenzumestrocel'],'CuATSM':['Cu(II)ATSM','CuATSM'],'GDC-0134':['GDC-0134'],'BHV-0223_riluzole':['BHV-0223'],'PrimeC':['PrimeC','Ciprofloxacin/Celecoxib'],'DNL747':['DNL747','SAR443060'],'SAR443820':['SAR443820','DNL788'],'ARO-SOD1':['ARO-SOD1'],'ALN-SOD':['ALN-SOD'],'QRL-201':['QRL-201'],'QRL-101':['QRL-101'],'AMT-162':['AMT-162','APB-102']}
exclude={'autologous_BM_stem_cells_Corestem_2010','MNC_Hanyang','MSC3P','Whartons_jelly_MSCs','NP001_regulatory_Tcells','Spirit1','HK-001'}
manifest=[]
for r in rows:
 if r['status']!='unknown' or r['asset'] in exclude or r['cohort_disposition'].startswith('exclude'):continue
 terms=aliases.get(r['asset'],[r['asset']]);q=' OR '.join('"'+x+'"' for x in terms)
 params={'query.intr':q,'query.cond':'amyotrophic lateral sclerosis','pageSize':100,'countTotal':'true','fields':'NCTId,BriefTitle,OfficialTitle,OverallStatus,WhyStopped,StartDate,StartDateType,LastUpdatePostDate,CompletionDate,CompletionDateType,LeadSponsorName,Phase,Condition,BriefSummary,InterventionName,InterventionOtherName,InterventionDescription','format':'json'}
 name='als_followup_'+r['asset'].replace('/','_')+'.json';u='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode(params);raw=fetch(name,u)
 if raw:
  d=json.loads(raw);manifest.append({'asset':r['asset'],'file':'sources/pos_nested/'+name,'count':d.get('totalCount'),'truncated':bool(d.get('nextPageToken'))});print(r['asset'],d.get('totalCount'),flush=True)
 time.sleep(.25)
(P/'data/pos_adjudication/als_followup_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
