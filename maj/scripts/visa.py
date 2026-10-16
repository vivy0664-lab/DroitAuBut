import os
import json,glob,re,unicodedata,html,collections
S=os.environ.get('SORTIE','/mnt/user-data/uploads/Truc/droit-au-but-piste/sortie/')
def nz(s):return unicodedata.normalize('NFD',s or '').encode('ascii','ignore').decode().lower()
CODEMAP={'code civil':'cciv','code de procedure civile':'cpc','code penal':'cpen','code de procedure penale':'cpp','code de commerce':'ccom','code du travail':'ctrav','code de la consommation':'cconso','code des assurances':'cassur','code de justice administrative':'cja','code general des impots':'cgi','livre des procedures fiscales':'lpf',"code de l'urbanisme":'curb',"code de l'environnement":'cenv',"code de l'entree et du sejour des etrangers et du droit d'asile":'cesa','code electoral':'celec',"code de l'organisation judiciaire":'coj',"code des procedures civiles d'execution":'cpce',"code de la construction et de l'habitation":'ccons','code de la securite sociale':'css','code de la propriete intellectuelle':'cpi','code monetaire et financier':'cmf','code de la commande publique':'ccp'}
MONTHS='janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre'
SRC=re.compile(r"\b(?:du|de la|de l'|des|au|a la)\s+("+"|".join(re.escape(k) for k in sorted(CODEMAP,key=len,reverse=True))+r"|(?:code|livre des procedures fiscales|loi|decret|reglement|ordonnance|directive|convention|traite|constitution|declaration|charte|arrete|accord|protocole|statut)\b[^,.;()]*?)(?=\s*(?:,|\.|;|\(|$|\set\s|\sdans\s|\stel\s|\sissu|\sen\s|\sapplicable|\sdevenu|\santerieur))")
ART=re.compile(r"(?:\b(lo|lp|l|r|d|a)\.\s?|\b(?<![\w-]))(\d+(?:-\d+)*)(?:\s(bis|ter|quater|quinquies|sexies|septies|octies|[a-z]{1,2})\b)?")
def parse(v):
  t=html.unescape(re.sub('<[^>]+>','',v)).replace('°',' DEG ').replace('§',' PARA ')
  t=nz(t)
  t=re.sub(r"\bn\s*deg\s*[\d\-/a-z.]+",' ',t);t=re.sub(r"\d+\s*deg\b",' ',t);t=re.sub(r"para\s*\d+",' ',t)
  t=re.sub(r"\b\d{1,2}(?:er)?\s+(?:%s)\s+\d{4}"%MONTHS,' ',t)
  t=re.sub(r"alineas?\s+\d+(?:er|e)?",' ',t);t=re.sub(r"§\s*\d+",' ',t);t=re.sub(r"\d+\s*°",' ',t);t=re.sub(r"\b(?:i|ii|iii|iv|v|vi|vii|viii|ix|x)\b(?=[,\s])",' ',t)
  out=[];srcs=[(m.start(),m.end(),m.group(1).strip()) for m in SRC.finditer(t)]
  # articles before each source
  prev=0
  for i,(a,b,name) in enumerate(srcs):
    seg=t[prev:a];prev=b
    nxt=srcs[i+1][0] if i+1<len(srcs) else len(t)
    tail=t[b:nxt][:160];ant=('anterieur' in tail) or ('ancien' in seg[-40:])
    code=None
    for k,v2 in CODEMAP.items():
      if name==k:code=v2
    if not code:continue
    for m in ART.finditer(seg):
      pre,num,suf=m.group(1),m.group(2),m.group(3)
      if pre=='lp':continue
      pre=(pre or '').upper()
      n=pre+num if pre else num
      if suf and suf not in ('et','du','de','la','le','a','en','au'):n+=' '+suf if suf in('bis','ter','quater','quinquies','sexies','septies','octies') else ' '+suf.upper()
      out.append((code,n,ant))
  return out
if __name__=='__main__':
  H=[]
  for f in glob.glob(S+'hist-*.json'):H+=json.load(open(f,encoding='utf-8-sig'))['results']
  c=collections.Counter();ex=0
  for h in H[:3000]:
    for v in h.get('visa') or []:
      r=parse(v['title']);c.update(x[0] for x in r)
      if ex<15:print(re.sub('<[^>]+>','',v['title'])[:160],'=>',r);ex+=1
  print(c.most_common())

def parse_ant(v,date=''):
  t=nz(html.unescape(re.sub('<[^>]+>','',v)))
  t0=t
  t=re.sub(r"n\s*°\s*[\d\-/a-z.]+",' ',t)
  t=re.sub(r"\b\d{1,2}(?:er)?\s+(?:%s)\s+\d{4}"%MONTHS,' ',t)
  t=re.sub(r"alineas?\s+\d+(?:er|e)?",' ',t);t=re.sub(r"§\s*\d+",' ',t);t=re.sub(r"\d+\s*°",' ',t);t=re.sub(r"\b(?:i|ii|iii|iv|v|vi|vii|viii|ix|x)\b(?=[,\s])",' ',t)
  srcs=[(m.start(),m.end(),m.group(1).strip()) for m in SRC.finditer(t)]
  out=[];prev=0
  for i,(a,b,name) in enumerate(srcs):
    seg=t[prev:a];prev=b
    nxt=srcs[i+1][0] if i+1<len(srcs) else len(t)
    tail=t[b:nxt]
    ant=('anterieur' in tail) or ('anterieur' in seg)
    code=CODEMAP.get(name)
    if not code:continue
    for m in ART.finditer(seg):
      pre,num,suf=m.group(1),m.group(2),m.group(3)
      if pre=='lp':continue
      if re.match(r'\s*,?\s*devenu',seg[m.end():m.end()+12]):continue
      pre=(pre or '').upper()
      n=pre+num if pre else num
      if suf and suf not in ('et','du','de','la','le','a','en','au'):n+=' '+suf if suf in('bis','ter','quater','quinquies','sexies','septies','octies') else ' '+suf.upper()
      newn='devenu' in seg[max(0,m.start()-9):m.start()]
      if code=='cciv' and n.isdigit() and 1100<=int(n)<=1386 and not newn and (ant or date<'2020-01-01'):continue
      if ant and code=='cconso':continue
      out.append((code,n,ant))
  return out
