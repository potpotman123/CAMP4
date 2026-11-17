"""Bounded disease-panel discovery, not a claim to enumerate all rare disease programs."""
import json, urllib.parse, time, sys
from pathlib import Path
from fetch_pos_pilot import fetch
P=Path(__file__).resolve().parents[1]
groups={
'neurodevelopment':['Angelman syndrome','Dravet syndrome','Rett syndrome','Fragile X syndrome','SYNGAP1','CDKL5','Lennox-Gastaut syndrome'],
'genetic_neurodegeneration':['Huntington disease','spinocerebellar ataxia','Alexander disease','Batten disease','Lafora disease','adrenoleukodystrophy','metachromatic leukodystrophy'],
'neuromuscular':['spinal muscular atrophy','Duchenne muscular dystrophy','GNE myopathy','amyotrophic lateral sclerosis','Friedreich ataxia','myotonic dystrophy'],
'lysosomal':['Pompe disease','Fabry disease','Gaucher disease','Niemann-Pick','mucopolysaccharidosis','GM1 gangliosidosis','GM2 gangliosidosis'],
'metabolic':['phenylketonuria','urea cycle disorder','primary hyperoxaluria','Wilson disease','glycogen storage disease','hypophosphatasia'],
'hematology':['hemophilia A','hemophilia B','sickle cell disease','beta thalassemia','paroxysmal nocturnal hemoglobinuria'],
'systemic':['achondroplasia','hereditary angioedema','cystic fibrosis','pulmonary arterial hypertension','epidermolysis bullosa','primary biliary cholangitis'],
'immune':['Wiskott-Aldrich syndrome','severe combined immunodeficiency','chronic granulomatous disease','autoimmune pulmonary alveolar proteinosis']}
(P/'data/pos_nested/disease_panel.json').write_text(json.dumps({'frozen_before_broad_retrieval':'2026-11-16','selection':'Purposive disease-family coverage independent of specific drug outcomes; NOT a representative random sample or exhaustive rare-disease ontology. Some labels include heterogeneous subtypes.','groups':groups},indent=2))
fields='NCTId,BriefTitle,OfficialTitle,OverallStatus,WhyStopped,StartDate,StartDateType,CompletionDate,CompletionDateType,LastUpdatePostDate,StudyType,Phase,LeadSponsorName,LeadSponsorClass,Condition,InterventionType,InterventionName,InterventionOtherName,InterventionDescription,ArmGroupLabel,ArmGroupType,ArmGroupInterventionName,BriefSummary,EnrollmentCount,EnrollmentType'
manifest=[]
for group,terms in groups.items():
 token=None
 for page in range(1,9):
  params={'query.cond':' OR '.join('"'+x+'"' for x in terms),'filter.advanced':'AREA[StudyType]INTERVENTIONAL AND AREA[StartDate]RANGE[MIN,2024-12-31]','fields':fields,'pageSize':1000,'countTotal':'true','format':'json'}
  if token:params['pageToken']=token
  u='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode(params)
  name=f'broad_allphase_{group}_{page}.json';raw=fetch(name,u)
  if not raw:manifest.append({'group':group,'page':page,'error':True});break
  d=json.loads(raw);token=d.get('nextPageToken')
  manifest.append({'group':group,'page':page,'file':name,'total':d.get('totalCount'),'returned':len(d.get('studies',[])),'next_page':bool(token)})
  print(manifest[-1],flush=True)
  if not token:break
  time.sleep(.3)
(P/'data/pos_nested/broad_allphase_retrieval_manifest.json').write_text(json.dumps(manifest,indent=2))
