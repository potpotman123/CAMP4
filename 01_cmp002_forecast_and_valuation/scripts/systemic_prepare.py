import json,re,urllib.request,urllib.parse,concurrent.futures,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/'data/pos_completion';S=P/'sources/pos_completion';D.mkdir(parents=True,exist_ok=True);S.mkdir(parents=True,exist_ok=True)
rows=[r for r in json.loads((P/'data/pos_adjudication/integrated_program_ledger.json').read_text()) if r['family']=='systemic' and r['reference_eligibility']!='excluded']
Q={'AIR DNase':'AIR DNase OR PRX-110 OR alidornase','BIA51058':'BIA 5-1058 OR zamicastat','POL6014':'POL6014 OR lonodelestat','N91115':'N91115 OR cavosonstat','EDIT301':'EDIT-301 OR reni-cel OR renizgamglogene','deutivacaftor':'deutivacaftor OR VX-561 OR CTP-656','elexacaftor':'elexacaftor OR VX-445','vanzacaftor':'vanzacaftor OR VX-121','FTX6058':'FTX-6058 OR pociredir','Pociredir oral capsule(s)':'FTX-6058 OR pociredir','BRL-101':'BRL-101','CS101':'CS-101','BB305':'BB305 OR betibeglogene OR lovotibeglogene','Frespaciguat':'Frespaciguat OR MK-5475','9MW3011':'9MW3011 OR MWTX-003','ETD001':'ETD001','Mim8':'Mim8 OR denecimig OR NNC0365-3769','concizumab':'concizumab OR NNC172-2021 OR NNC0172-0000-2021','N9-GP':'N9-GP OR nonacog beta pegol','turoctocog alfa pegol':'turoctocog alfa pegol OR N8-GP','A4250':'A4250 OR odevixibat','CRC (A3384)':'A3384','Seladelpar':'seladelpar OR MBX-8025','golexanolone':'golexanolone OR GR3027','CNP-104':'CNP-104','FFP104':'FFP104','AER-901 Solution for Nebulization':'AER-901','KAR5585 Capsules':'KAR5585','L608 Inhalation Solution':'L608','LTP':'LTP001','PB1046 Subcutaneous Injection':'PB1046 OR pemziviptadil','TPN171H':'TPN171H OR simmerafil','AG-946':'AG-946 OR tebapivat','Aes-103':'AES-103','etavopivat':'etavopivat OR FT-4202','osivelotor':'osivelotor OR GBT021601','voxelotor':'voxelotor OR GBT440','nula-cel Drug Product':'nula-cel OR GPH101','ST-400 Investigational product':'ST-400','Vebeglogene autotemcel':'Vebeglogene autotemcel','Inhaled AR-501':'AR-501 OR Gallium Citrate','Inhaled SNSP113':'SNSP113','KB407 (Nebulization)':'KB407','VX-522 mRNA therapy':'VX-522','Diacerein 1% Ointment':'CCP-020 OR diacerein','PTW-002 10 mg/g gel':'PTW-002','B-VEC':'beremagene OR KB103','EB101':'EB-101 OR prademagene','BPX501':'BPX-501 OR rivogenlecleucel','Rimiducid':'rimiducid OR AP1903','GNR038':'GNR-038','ADX324':'ADX-324','NTLA2002':'NTLA-2002 OR lonvoguran','BMN331':'BMN331 OR BMN-331','ADX038':'ADX-038','BCX10013':'BCX10013','BCX9930':'BCX9930','LP005':'LP-005','SAR443809':'SAR443809','TT30':'TT30 OR ALXN1102 OR ALXN1103','HRS5965':'HRS-5965','lanoracopan':'lanoracopan OR MY008211A','ciprocopan':'ciprocopan OR HSK39297','KP104':'KP104','ALX009':'ALX-009','SANGUINATE™':'SANGUINATE','sodium nitrite inhaled':'sodium nitrite','TBX-1400':'TBX-1400'}
generic={'β-globin restored autologous HSC','β-globin restored autologous hematopoietic stem cells','Autologous enriched CD34+ cell fraction that contains CD34+ cells transduced with lentiviral vector encoding human γ-globinG16D and short-hairpin RNA734','Genetically corrected cultured epidermal autograft (ATMP)','Gene therapy','AMB new formulation (1 mg)','Reference AMB (5 mg)','Prostacyclin Receptor Agonist','[11C]-GSK2256098 500 MBq'}
Q['Autologous enriched CD34+ cell fraction that contains CD34+ cells transduced with lentiviral vector encoding human γ-globinG16D and short-hairpin RNA734']='CSL200'
def fetch(r):
 asset=r['asset'];key=r['id'].split(':')[1];path=S/f'systemic_{key}_registry.json'
 if path.exists():return key,'cached'
 query=Q.get(asset,re.sub(r'\([^)]*\)','',asset).strip())
 params={'format':'json','pageSize':100}
 if asset in generic and asset not in Q:params['query.id']=' OR '.join(r['trial_ids'])
 else:params['query.intr']=query
 url='https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode(params)
 try:
  with urllib.request.urlopen(url,timeout=45) as resp:data=json.load(resp)
  path.write_text(json.dumps({'integrated_id':r['id'],'asset':asset,'retrieved_date':'2026-11-16','query_url':url,'response':data},indent=2))
  return key,len(data.get('studies',[])),bool(data.get('nextPageToken'))
 except Exception as e:return key,type(e).__name__,str(e)
(D/'systemic_assignment.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  out=list(ex.map(fetch,rows))
 (D/'systemic_registry_fetch_log.json').write_text(json.dumps(out,indent=2))
 print('retrieved',len(out),'errors',[x for x in out if len(x)>2 and isinstance(x[2],str)],'pagination',[x for x in out if len(x)>2 and x[2] is True])
