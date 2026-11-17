from pathlib import Path
import json,csv,hashlib
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
R=Path(__file__).resolve().parents[1];D=R/'data/pos_audit';checks=[]
def check(name,ok):
 assert ok,name
 checks.append(name)
r=json.loads((D/'program_ledger.json').read_text());s=json.loads((D/'summary.json').read_text());src=json.loads((D/'source_registry.json').read_text())
check('28 unique asset-indication records',len(r)==len({x['id'] for x in r})==28)
check('24 unique assets',len({x['asset'] for x in r})==s['core_asset_n']==24)
check('Asset outcome tally reconciles',sum(s['asset_status_counts'].values())==24)
check('Pair outcome tally reconciles',sum(s['pair_status_counts'].values())==28)
check('No pooled probability invented',s['pooled_approval_probability'] is None)
check('Closest set is immature, not a zero rate',s['closest_n']==4 and s['closest_pediatric_restoration']=={'ongoing':3,'stopped_efficacy':1})
check('Three verified approvals',len([x for x in r if x['status_asof']=='approved'])==3)
check('Accelerated approval distinguished',next(x for x in r if x['asset']=='tofersen')['approval_type']=='accelerated')
check('Partner exit not mistaken for ION464 failure',next(x for x in r if x['asset']=='ION464')['status_asof']=='ongoing_after_partner_exit')
check('Biogen option decline not mistaken for ION582 failure',next(x for x in r if x['asset']=='obudanersen')['status_asof']=='ongoing')
check('Negative endpoint not mistaken for diranersen termination',next(x for x in r if x['asset']=='diranersen')['status_asof']=='ongoing_after_negative_endpoint')
check('Positive pivotal not mistaken for ulefnersen approval',next(x for x in r if x['asset']=='ulefnersen')['status_asof']=='ongoing_positive_pivotal')
check('Prior human exposure flagged',next(x for x in r if x['asset']=='ulefnersen')['prior_human_data_before_entry'])
check('No post-cutoff registry updates used',all(x['registry_last_update']<='2026-11-16' for x in r))
check('All numerical entry proxies have preserved snapshots',all((R/x['local_registry_snapshot']).is_file() for x in r))
for x in r:
 blob=json.loads((R/x['local_registry_snapshot']).read_text())['data']; trials=blob['studies'] if 'studies' in blob else [blob]
 t=next(a for a in trials if a['protocolSection']['identificationModule']['nctId']==x['entry_trial'])
 check('entry trace '+x['id'],t['protocolSection']['statusModule']['startDateStruct']['date']==x['entry_date_proxy'])
check('All source identifiers resolve',all(k in src for x in r for k in x['status_sources']))
check('Generic query fully screened',len(json.loads((D/'discovery_screen.json').read_text()))==25)
for item in json.loads((D/'source_hashes.json').read_text()):
 check('source hash '+item['file'],hashlib.sha256((R/item['file']).read_bytes()).hexdigest()==item['sha256'])
with (D/'program_ledger.csv').open() as f:check('CSV count reconciles',len(list(csv.DictReader(f)))==28)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.links.append(dict(attrs).get('href',''))
p=R/'reports/pos_audit_2026-11-16.html';parser=Links();parser.feed(p.read_text())
check('Local report links resolve',all((p.parent/unquote(urlsplit(u).path)).is_file() for u in parser.links if u and not urlsplit(u).scheme))
check('Report has balanced tables',p.read_text().count('<table>')==p.read_text().count('</table>'))
(D/'validation.json').write_text(json.dumps({'as_of':'2026-11-16','checks_passed':len(checks),'checks':checks,'limitations':'Internal data/provenance checks, not external validation of clinical conclusions. No browser visual inspection claimed.'},indent=2)+'\n')
print(len(checks),'checks passed')
