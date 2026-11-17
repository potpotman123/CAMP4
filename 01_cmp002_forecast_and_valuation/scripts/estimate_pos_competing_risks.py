"""Fixed-horizon approval cumulative incidence; no lifetime extrapolation.
Input: adjudicated program records with entry_date, end_date, event
(approval/discontinuation/censor), nested filters and eligibility_verified.
Unknown outcome must have a verified last-observed end_date, not today's date.
"""
import json,sys,datetime
from collections import defaultdict

def estimate(rows,horizons=(5,8,10)):
 if not rows:raise ValueError('Empty cohort')
 times=defaultdict(lambda:{'approval':0,'discontinuation':0,'censor':0})
 for r in rows:
  if not r.get('eligibility_verified'):raise ValueError('Unverified cohort eligibility')
  if not r.get('followup_verified'):raise ValueError('Unverified follow-up')
  if r['event'] not in ['approval','discontinuation','censor']:raise ValueError('Unknown event type')
  entry=datetime.date.fromisoformat(r['entry_date']);end=datetime.date.fromisoformat(r['end_date'])
  t=(end-entry).days/365.25
  if t<0:raise ValueError('Outcome precedes entry')
  times[t][r['event']]+=1
 n=len(rows);risk=n;survival=1.;approval=0.;stop=0.;curve=[]
 for t,counts in sorted(times.items()):
  a=counts['approval'];d=counts['discontinuation'];c=counts['censor']
  if a+d+c>risk:raise ValueError('Invalid risk set')
  approval+=survival*a/risk;stop+=survival*d/risk
  survival*=1-(a+d)/risk
  curve.append({'years':t,'at_risk_before':risk,'approval_cif':approval,'discontinuation_cif':stop,'event_free_survival':survival,'events':counts})
  risk-=a+d+c
 out=[]
 for h in horizons:
  observed=[x for x in curve if x['years']<=h]
  # No estimate beyond observed support unless all probability mass resolved.
  supported=h<=max(times) or abs(survival)<1e-12
  out.append({'years':h,'supported':supported,'approval_cif':(observed[-1]['approval_cif'] if observed else 0) if supported else None,'interpretation':'Selected cohort, conditional on ascertainment/censoring assumptions; NOT lifetime PoS.'})
 return {'n':n,'curve':curve,'horizons':out,'lifetime_approval_probability':None,'uncertainty_interval':None,'limitations':'Independent censoring may fail; model does not correct missing programs, selection, date errors or correlated assets. No CI supplied without cluster-aware uncertainty analysis.'}

def self_test():
 def r(end,event):return {'entry_date':'2020-01-01','end_date':end,'event':event,'eligibility_verified':True,'followup_verified':True}
 # Five complete observations: two approvals, two failures, one censor.
 x=estimate([r('2021-01-01','approval'),r('2021-01-01','discontinuation'),r('2022-01-01','approval'),r('2022-01-01','discontinuation'),r('2023-01-01','censor')],(2.5,10))
 assert abs(x['horizons'][0]['approval_cif']-.4)<1e-12
 assert x['horizons'][1]['approval_cif'] is None
 assert all(abs(z['approval_cif']+z['discontinuation_cif']+z['event_free_survival']-1)<1e-12 for z in x['curve'])
 # One early censor changes the subsequent risk set: 1 approval out of remaining 2.
 y=estimate([r('2020-06-01','censor'),r('2021-01-01','approval'),r('2022-01-01','discontinuation')],(1.5,3))
 assert abs(y['horizons'][0]['approval_cif']-.5)<1e-12
 bad=r('2021-01-01','approval');bad['eligibility_verified']=False
 try:estimate([bad]);raise AssertionError('Gate failed')
 except ValueError:pass
 print('Passed hand-calculated competing-risk, censoring, unsupported-horizon and eligibility-gate tests; no empirical PoS estimated.')
if __name__=='__main__':
 if len(sys.argv)==1:self_test()
 else:print(json.dumps(estimate(json.load(open(sys.argv[1]))),indent=2))
