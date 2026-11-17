"""Administrative-censoring subdistribution approval curves, NOT lifetime PoS.

Failed programs remain non-approvals to the known calendar cutoff. No censoring
at discontinuation, and no invented stop dates. Conditional on approval ascertainment
through cutoff and exchangeability across entry eras within each fitted cohort.
"""
import json, datetime as dt, hashlib
from pathlib import Path
from collections import Counter
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/pos_censoring_analysis'; OUT.mkdir(exist_ok=True)
CUTOFF=dt.date(2026,11,16)
SEED=20261117
HORIZONS=[3,5,8,10,12]
clusters=json.loads((ROOT/'data/pos_molecule_status/cluster_status.json').read_text())
original=json.loads((ROOT/'data/pos_completion/completed_program_ledger.json').read_text())
orig={r['id']:r for r in original}

def date(s): return dt.date.fromisoformat(s)
def years(d): return d.days/365.25
obs=[]
for r in clusters:
    lo,hi=map(date,r['entry_interval'])
    approvals=[date(m['approval_date']) for m in r['members'] if m['approval_date']]
    event=bool(approvals); end=min(approvals) if event else CUTOFF
    mid=lo+(hi-lo)//2
    assert lo<=hi<=end<=CUTOFF
    obs.append(dict(cluster=r['asset_cluster'],assets=r['assets'],status=r['status'],confidence=r['confidence'],flags=r['flags'],strict_entry=all(orig[k]['strict_entry_qualified'] for k in r['member_ids']),closest4=any(orig[k]['closest4'] for k in r['member_ids']),entry_interval=r['entry_interval'],entry_midpoint=mid.isoformat(),entry_year=mid.year,endpoint_date=end.isoformat(),approval=event,time=years(end-mid),time_early_entry=years(end-lo),time_late_entry=years(end-hi),unknown_types=r['unknown_types'],family=r['members'][0]['family']))

def estimate(rows,timekey='time',weights=None):
    t=np.array([r[timekey] for r in rows]); e=np.array([r['approval'] for r in rows]); n=len(rows)
    w=np.ones(n) if weights is None else np.array(weights)
    survival=1.; curve=[]
    for evtime in sorted(set(t[e & (w>0)])):
        risk=float(w[t>=evtime-1e-10].sum()); events=float(w[e & (np.abs(t-evtime)<1e-10)].sum())
        survival*=1-events/risk
        curve.append(dict(years=float(evtime),subdistribution_risk_set=risk,approvals=events,approval_probability=1-survival))
    result=[]
    max_time=float(max(t[w>0])) if sum(w)>0 else 0
    for h in HORIZONS:
        prior=[c for c in curve if c['years']<=h]
        supported=h<=max_time
        result.append(dict(years=h,estimate=(prior[-1]['approval_probability'] if prior else 0.) if supported else None,supported=supported,subdistribution_risk_set=int(w[t>=h].sum()),observed_approvals_by_horizon=int(w[e & (t<=h)].sum())))
    return dict(n=int(sum(w)),horizons=result,curve=curve)

def fit(rows,bootstrap=False):
    if not rows:return None
    result=estimate(rows)
    for h,early,late in zip(result['horizons'],estimate(rows,'time_early_entry')['horizons'],estimate(rows,'time_late_entry')['horizons']):
        h['earliest_entry_scenario']=early['estimate'];h['latest_entry_scenario']=late['estimate']
    if bootstrap:
        rng=np.random.default_rng(SEED)
        samples=[[] for _ in HORIZONS]
        if any(r['approval'] for r in rows):
            for _ in range(1000):
                weights=np.bincount(rng.integers(0,len(rows),len(rows)),minlength=len(rows))
                b=estimate(rows,weights=weights)
                for j,h in enumerate(b['horizons']):
                    if h['estimate'] is not None:samples[j].append(h['estimate'])
        for j,h in enumerate(result['horizons']):
            vals=samples[j]
            h['bootstrap_supported_replicates']=len(vals)
            h['descriptive_bootstrap_95']=list(map(float,np.quantile(vals,[.025,.975]))) if len(vals)>=800 and h['supported'] else None
            h['bootstrap_note']='Cluster resampling, not a population-valid CI; no zero-width interval for zero-event cohorts; unsupported tail replicates omitted.'
    return result

tiers={
 'R1_rare':lambda r:True,
 'R2_genetic_CNS':lambda r:r['flags']['genetic_cns'],
 'R3_genetic_medicine_CNS':lambda r:r['flags']['genetic_cns'] and r['flags']['genetic_medicine'],
 'R4_closest_restoration_ASO':lambda r:r['closest4'],
}
results={}
for tier,predicate in tiers.items():
    rs=[r for r in obs if predicate(r)]
    counts=Counter(r['status'] for r in rs); A=counts['approved'];D=counts['active'];U=counts['unknown'];F=counts['failed'];P=sum(r['confidence']=='probable' for r in rs);N=len(rs)
    results[tier]=dict(n=N,status_counts={s:counts[s] for s in ['approved','failed','active','unknown']},probable_failures=P,
      lifetime_identification_bounds=[A/N,(A+D+U)/N],strict_failure_lifetime_bounds=[A/N,(A+D+U+P)/N],
      active_future_success_required_for_25=[dict(unknown_future_success=q,required_active_future_success=(.25*N-A-q*U)/D if D else None) for q in [0,.25,.5,1]],
      lifetime_scenarios=[dict(active_future_success=p,unknown_future_success=q,eventual_fraction=(A+p*D+q*U)/N) for p in [.1,.25,.4] for q in [0,.25,1]],
      main=fit(rs,True),recent_2015_2024=fit([r for r in rs if r['entry_year']>=2015],True),recent_2020_2024=fit([r for r in rs if r['entry_year']>=2020],True),
      stronger_entry=fit([r for r in rs if r['strict_entry']]),exclude_unknown_DIAGNOSTIC=fit([r for r in rs if r['status']!='unknown']),exclude_unknown_and_probable_DIAGNOSTIC=fit([r for r in rs if r['status']!='unknown' and r['confidence']!='probable']))

bias=[]
for family in ['als','neuro','metabolic','systemic']:
    rs=[r for r in obs if r['family']==family];bias.append(dict(family=family,n=len(rs),unknown=sum(r['status']=='unknown' for r in rs),probable_failures=sum(r['confidence']=='probable' for r in rs)))
result=dict(analysis_date='2026-11-17',evidence_cutoff=str(CUTOFF),method='Administrative-censoring subdistribution product limit; discontinued candidates retained through cutoff, never censored at stop',formula='F(h)=1-product_over_approval_times_t<=h(1-approvals(t)/nonapproved_observed_through_t)',assumptions=['FDA qualifying-indication approval ascertainment complete through cutoff conditional on prior alias review','Within each fitted cohort, entry-calendar-derived observation time independent of latent time to approval','Entry midpoint is a proxy; earliest/latest scenarios supplied','No extrapolation from finite horizon to lifetime'],tiers=results,unknown_by_family=bias)

# Hand-calculated safeguards: retaining failures, censoring, ties and tail support.
toy=[dict(time=1,time_early_entry=1,time_late_entry=1,approval=True),dict(time=3,time_early_entry=3,time_late_entry=3,approval=False),dict(time=3,time_early_entry=3,time_late_entry=3,approval=False)]
assert abs(estimate(toy)['horizons'][0]['estimate']-1/3)<1e-12
toy2=toy+[dict(time=.5,time_early_entry=.5,time_late_entry=.5,approval=False)]
assert abs(estimate(toy2)['horizons'][0]['estimate']-1/3)<1e-12
assert estimate(toy)['horizons'][1]['estimate'] is None
assert len(obs)==310 and sum(r['approval'] for r in obs)==42
assert [results[k]['n'] for k in tiers]==[310,81,48,4]
for x in results.values():
    v=[h['estimate'] for h in x['main']['horizons'] if h['supported']]
    assert all(0<=a<=b<=1 for a,b in zip(v,v[1:]))
    assert sum(x['status_counts'].values())==x['n']
    for case in x['active_future_success_required_for_25']:
        if case['required_active_future_success'] is not None:
            c=x['status_counts'];assert abs((c['approved']+case['required_active_future_success']*c['active']+case['unknown_future_success']*c['unknown'])/x['n']-.25)<1e-12
for name,obj in [('observations',obs),('results',result)]:
    (OUT/(name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
inputs=[ROOT/'data/pos_molecule_status/cluster_status.json',ROOT/'data/pos_completion/completed_program_ledger.json',Path(__file__)]
(OUT/'validation.json').write_text(json.dumps(dict(passed=True,bootstrap_replicates=1000,seed=SEED,checks=['310 clusters,42 approvals','nested310/81/48/4','hand calculated retained-failure/censoring example','unsupported horizon excluded','monotone bounded curves','status sums','25 percent threshold identities'],input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}),indent=2)+'\n')
for tier,x in results.items():
    print(tier,x['n'],x['status_counts'])
    for scenario in ['main','recent_2015_2024','recent_2020_2024','stronger_entry','exclude_unknown_DIAGNOSTIC']:
        f=x[scenario]
        print(scenario,f['n'] if f else 0,[(h['years'],round(h['estimate']*100,1) if h['estimate'] is not None else None,h['subdistribution_risk_set']) for h in f['horizons']] if f else [])
    print('required',x['active_future_success_required_for_25'])
print('unknown by family',bias)
