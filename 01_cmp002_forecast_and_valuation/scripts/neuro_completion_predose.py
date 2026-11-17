import json
from pathlib import Path
P=Path(__file__).resolve().parents[1];allrows=json.loads((P/'data/pos_adjudication/integrated_program_ledger.json').read_text());out=[]
for r in allrows:
 if r['family']!='neuro' or 'predose' not in r['status']:continue
 a=r['asset'];slug=''.join(c if c.isalnum() else '_' for c in a);f=P/'sources/pos_completion'/f'neuro_registry_extra_{slug}.json';d=json.loads(f.read_text());trials=[]
 for x in d['response'].get('studies',[]):
  p=x['protocolSection'];n=p['identificationModule']['nctId'];st=p['statusModule'];en=p.get('designModule',{}).get('enrollmentInfo',{})
  if n not in r['trial_ids']:continue
  trials.append({'trial_id':n,'first_registration_submitted':st.get('studyFirstSubmitDate'),'first_registration_posted':st.get('studyFirstPostDateStruct'),'planned_start':st.get('startDateStruct'),'enrollment':en,'status':st['overallStatus'],'never_dosed_at_trial':st['overallStatus']=='WITHDRAWN' and en.get('type')=='ACTUAL' and en.get('count')==0,'why_stopped':st.get('whyStopped'),'withdrawal_known_by':st.get('lastUpdatePostDateStruct',{}).get('date'),'url':'https://clinicaltrials.gov/study/'+n})
 reason={'VY-HTT01':'Clean first registered clinical study of novel first-generation HTT gene therapy, zero enrollment, withdrawn for strategic switch of vector program. No human exposure identified.','CAD-1883':'Already exposed in essential tremor2019 (and prior healthy volunteers); zero-dose SCA trial is later indication, not novel molecule attrition.','PXL065':'Prior NASH trial actual2020 with treated participants; zero-dose ALD trial is later indication.','PXL770':'Prior actual2017 healthy-human Phase I and NASH development; zero-dose ALD trial is later indication.','sobetirome':'Prior human lipid-lowering studies before2010; both ALD trials withdrew with zero participants. Not novel molecule attrition.'}[a]
 out.append({'id':r['id'],'canonical_asset':a,'indication':r['indication'],'clinical_inception_eligible':False,'registered_predose_sensitivity_eligible':a=='VY-HTT01','reason':reason,'trials':trials,'source_snapshot':str(f.relative_to(P)),'as_of':'2026-11-16','limitation':'Withdrawal update is an upper bound on decision date. This is registered prospective-trial attrition, not a population of all preclinical candidates.'})
(P/'data/pos_completion/neuro_predose_sensitivity.json').write_text(json.dumps(out,indent=2)+'\n');print('predose',len(out),'eligible',sum(x['registered_predose_sensitivity_eligible'] for x in out))
