import os
import re,glob,html,json,unicodedata,collections
from visa import CODEMAP,nz
S=os.environ.get('SORTIE','/mnt/user-data/uploads/Truc/droit-au-but-piste/sortie/')+'admin/'
KEYS=sorted(CODEMAP,key=len,reverse=True)
NUM=r"(?:(?:lo|l|r|d|a)\.?\s?)?\d+(?:-\d+)*(?:\s(?:bis|ter|quater|quinquies|[b-df-z])\b)?"
RX=re.compile(r"\barticles?\s+("+NUM+r"(?:\s*(?:,|et|a)\s*"+NUM+r")*)(?:,\s*[^,]{0,40},)?\s+(?:du|de la|de l')\s+(code[a-z' ]{3,90}|livre des procedures fiscales)")
def tag(x,t):
    m=re.search(r'<'+t+r'>(.*?)</'+t+r'>',x,re.S);return html.unescape(m.group(1)).strip() if m else ''
def norm_num(s):
    s=s.strip();m=re.match(r"(lo|l|r|d|a)\.?\s?(.*)",s)
    if m and m.group(2)[:1].isdigit():return m.group(1).upper()+m.group(2).replace(' ','')
    m=re.match(r"(\d[\d-]*)\s(bis|ter|quater|quinquies|[a-z])$",s)
    if m:return m.group(1)+' '+(m.group(2) if len(m.group(2))>1 else m.group(2).upper())
    return s
out=[];cnt=collections.Counter()
for f in sorted(glob.glob(S+'CE-*.xml'))+sorted(glob.glob(S.replace('/admin/','/admin-caa/')+'CAA-*.xml')):
  for x in open(f,encoding='utf-8-sig').read().split('<!--FIN-->'):
    if '<Numero_Dossier>' not in x:continue
    num=tag(x,'Numero_Dossier');cj=tag(x,'Code_Juridiction');nj=tag(x,'Nom_Juridiction')
    jur='CE' if cj=='CE' else 'CAA '+re.sub(r"(?i)^cour administrative d'appel de\s*",'',nj).strip()
    if jur=='CAA ':
        mm=re.match(r'\d{2}([A-Z]{2})',num);jur='CAA '+{'DA':'Douai','LY':'Lyon','NC':'Nancy','PA':'Paris','VE':'Versailles','MA':'Marseille','BX':'Bordeaux','NT':'Nantes','TL':'Toulouse'}.get(mm.group(1) if mm else '','')
    jur=jur.strip()
    if jur.startswith('CAA '):jur='CAA '+jur[4:].title()
    date=tag(x,'Date_Lecture');pub=tag(x,'Code_Publication')
    form=re.sub(r'(\d)(ème|er|ère)',r'\1e',tag(x,'Formation_Jugement')).strip()
    ti=tag(x,'Texte_Integral')
    paras=[html.unescape(re.sub('<[^>]+>','',p)).strip() for p in re.findall(r'<p>(.*?)</p>',ti,re.S)]
    paras=[re.sub(r'\s+',' ',p) for p in paras if p.strip()]
    # motifs : après la mention des conclusions du rapporteur public
    st=0
    for i,p in enumerate(paras):
        if re.search(r'conclusions de .{0,60}rapporteu',p,re.I) or p.lower().startswith('considérant'):st=i+1
        if re.match(r'^1\.\s',p):st=i;break
    mot=paras[st:]
    intro=paras[1][:420] if len(paras)>1 else ''
    refs={}
    for p in mot:
        np_=nz(p)
        for m in RX.finditer(np_):
            name=m.group(2).strip();code=None
            for k in KEYS:
                if name.startswith(k):code=CODEMAP[k];break
            if not code:continue
            for n in re.findall(NUM,m.group(1)):
                n=norm_num(n)
                if (code,n) in (('cja','L761-1'),('cja','R761-1')):continue
                if (code,n) not in refs:
                    i=m.start();a=max(0,i-350);exc=(('…' if a>0 else '')+p[a:i+650]+('…' if i+650<len(p) else ''))
                    refs[(code,n)]=exc
    for (c,n) in refs:cnt[c]+=1
    out.append({'jur':jur,'num':num,'d':date,'pub':pub,'f':form,'tr':tag(x,'Type_Recours'),'sol':tag(x,'Solution'),'ecli':tag(x,'Numero_ECLI'),'intro':intro,'refs':[[c,n,e] for (c,n),e in refs.items()]})
# fusion avec les décisions déjà connues (les mises à jour hebdomadaires ne portent que sur les derniers mois)
try:
  old=json.load(open('../ce_refs.json',encoding='utf-8'))
except FileNotFoundError: old=[]
K=lambda o:(o.get('jur','CE'),o['num'],o['d'])
M={K(o):o for o in old};n0=len(M)
for o in out: M[K(o)]=o
out=sorted(M.values(),key=lambda o:o['d'])
print('ce_refs :',n0,'->',len(out))
json.dump(out,open('../ce_refs.json','w',encoding='utf-8'),ensure_ascii=False)
print(len(out),sum(1 for o in out if o['refs']),cnt.most_common())
import random;random.seed(2)
for o in random.sample(out,3):print(o['num'],o['d'],o['f'],o['pub'],[(c,n) for c,n,e in o['refs']][:8])
