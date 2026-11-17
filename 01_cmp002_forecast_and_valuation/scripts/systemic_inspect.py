import json,re,sys
from pathlib import Path
p=Path(__file__).resolve().parents[1];a=json.load(open(p/'data/pos_completion/systemic_assignment.json'))
for r in a:
 if len(sys.argv)>1 and not any(x.lower() in (r['asset']+' '+r['indication']).lower() for x in sys.argv[1:]): continue
 d=json.load(open(p/f"sources/pos_completion/systemic_{r['source_record_id']}_registry.json"))
 print('\n',r['source_record_id'],r['asset'],r['indication'])
 ss=sorted(d['response'].get('studies',[]),key=lambda s:s['protocolSection']['statusModule'].get('startDateStruct',{}).get('date','9999'))
 for s in ss[:4]+(ss[-2:] if len(ss)>4 else []):
  q=s['protocolSection'];st=q['statusModule'];de=q.get('designModule',{});im=q['identificationModule'];ints=q.get('armsInterventionsModule',{}).get('interventions',[])
  print(im['nctId'],st.get('startDateStruct'),st['overallStatus'],st.get('lastUpdatePostDateStruct'),de.get('enrollmentInfo'),im['briefTitle'],q['sponsorCollaboratorsModule']['leadSponsor']['name']);print(' WHY',st.get('whyStopped'),'INT',[(i['name'],i.get('otherNames')) for i in ints]);
