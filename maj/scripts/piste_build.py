import json,glob,re,unicodedata,datetime,collections,os
D='piste/'
def nz(s):return unicodedata.normalize('NFD',s or '').encode('ascii','ignore').decode().lower()
def clean(s):return re.sub(r'</?mark>','',s or '').strip()
RULES=[('etrangers',['etranger','sejour des etrangers','asile','eloignement']),
('corporel',['accident de la circulation','dommage corporel','indemnisation des victimes','fonds de garantie','responsabilite medicale','sante publique']),
('conso',['protection des consommateurs','consommation','surendettement','clause abusive','credit a la consommation','pratiques commerciales']),
('numpi',['propriete industrielle','marque','brevet','propriete litteraire','droit d\'auteur','dessins et modeles','donnees a caractere personnel','informatique','presse','communication audiovisuelle']),
('fiscal',['impots et taxes','impot','taxe','douane','enregistrement','tva','fiscal']),
('famille',['divorce','mariage','filiation','succession','regimes matrimoniaux','regime matrimonial','autorite parentale','mineur','majeur protege','protection des majeurs','adoption','pacs','donation','liberalites','partage']),
('urbenv',['urbanisme','environnement','expropriation','permis de construire','installations classees']),
('immo',['copropri','bail commercial','bail rural','bail d\'habitation','baux','bail','construction','vente immobili','servitude','propriete','voisinage','publicite fonciere']),
('banque',['banque','credit','cautionnement','surete','hypotheque','effet de commerce','paiement','instruments financiers','assurance']),
('affaires',['entreprise en difficulte','liquidation judiciaire','redressement judiciaire','sauvegarde','societe','concurrence','fonds de commerce','agent commercial','transports','commercant','vente']),
('travail',['securite sociale','contrat de travail','statut collectif','representation des salaries','conventions et accords collectifs','prud\'hommes','syndicat professionnel','comite social','travail','licenciement','salarie','employeur','retraite']),
('constit',['question prioritaire','constitution']),
('public',['separation des pouvoirs','administration','fonction publique','collectivites']),
('procedure',['procedure civile','appel civil','cassation','procedures civiles d\'execution','expert judiciaire','conflit de juridictions','action en justice','prescription civile','referes','jugements et arrets','arbitrage','avocat','officiers publics']),
]
CHB={'civ1':'civil','civ2':'procedure','civ3':'immo','comm':'affaires','soc':'travail','cr':'penal','pl':'civil','mi':'civil','cm':'civil'}
CHN={'civ1':'1re chambre civile','civ2':'2e chambre civile','civ3':'3e chambre civile','comm':'Chambre commerciale','soc':'Chambre sociale','cr':'Chambre criminelle','pl':'Assemblée plénière','mi':'Chambre mixte'}
def classify(txt,ch):
  if ch=='cr':return ['penal']
  t=nz(txt);out=[d for d,ks in RULES if any(k in t for k in ks)]
  b=CHB.get(ch,'civil')
  if ch=='soc' and 'travail' not in out: out.insert(0,'travail')
  return (out[:3] or [b]) if out else [b]
# --- Judilibre
J=[]
for f in sorted(glob.glob(D+'judilibre-*.json')):J+=json.load(open(f,encoding='utf-8-sig'))['results']
jp=[]
for r in J:
  tas=r.get('titlesAndSummaries') or []
  titles=[t for x in tas for t in (x.get('titles') or [])]
  head=titles[0].capitalize() if titles else (', '.join(r.get('themes') or [])[:80] or 'Arrêt publié')
  summ=(r.get('summary') or (tas[0].get('summary') if tas else '') or '').strip()
  summ=re.sub(r'\s+',' ',summ)
  if len(summ)>900: summ=summ[:880].rsplit(' ',1)[0]+'…'
  dom=classify(' '.join(titles)+' '+' '.join(r.get('themes') or [])+' '+summ[:300],r['chamber'])
  jp.append({'id':r['id'],'d':r['decision_date'],'n':r.get('number'),'ch':CHN.get(r['chamber'],r['chamber']),'sol':r.get('solution'),'p':''.join(sorted(set(r.get('publication') or [])-{'b'})),'h':head,'s':summ,'dom':dom,'v':[clean(x.get('title','')) for x in (r.get('visa') or [])][:3] if isinstance(r.get('visa'),list) else []})

CD={'cja':'public','curb':'urbenv','cenv':'urbenv','cesa':'etrangers','cgi':'fiscal','lpf':'fiscal','ccp':'public','css':'travail','ctrav':'travail','celec':'public','ccom':'affaires','cciv':'civil','cmf':'banque','ccons':'immo','cpen':'penal','cpp':'penal','cassur':'banque','cconso':'conso','cpi':'numpi','cpc':'procedure','coj':'procedure','cpce':'procedure'}
try:
  for o in json.load(open('../ce_refs.json',encoding='utf-8')):
    if o['d']<'2026-01-01':continue
    cs=[c for c,n,e in o['refs'] if c!='cja'] or [c for c,n,e in o['refs']]
    dom=list(dict.fromkeys(CD.get(c,'public') for c in cs))[:3] or ['public']
    arts=', '.join(dict.fromkeys(('art. '+n) for c,n,e in o['refs']))[:160]
    isce=o.get('jur','CE')=='CE'
    jp.append({'id':'CE:'+o['num'],'src':'ce','jur':o.get('jur','CE'),'lk':('https://www.conseil-etat.fr/fr/arianeweb/CE/decision/'+o['d']+'/'+o['num']) if isce else ('https://www.legifrance.gouv.fr/search/cetat?tab_selection=cetat&query='+o['num']),'d':o['d'],'n':o['num'],'ch':o['f'] or "Conseil d'État",'sol':o['sol'],'p':'A' if o['pub']=='A' else ('B' if o['pub']=='B' else 'C+'),'h':(o['tr'] or 'Décision')+(' · '+arts if arts else ''),'s':o['intro'],'dom':dom,'v':[]})
except FileNotFoundError: pass
jp.sort(key=lambda x:x['d'],reverse=True)
JRULES=[('penal',['code penal','procedure penale','infraction','casier judiciaire','detention provisoire','peine','classement sans suite','travail d\'interet general','delinquan','victime']),
('procedure',['code de procedure civile','organisation judiciaire','procedure civile','commissaires? de justice','aide juridictionnelle','avocat','greffe','juridiction','tribunal','mediation','execution des decisions']),
('civil',['code civil','droit des contrats','responsabilite civile','prescription']),
('famille',['divorce','mariage','filiation','succession','regimes? matrimonia','autorite parentale','mineurs?\\b','majeurs? proteges?','protection juridique des majeurs','pacte civil','pension alimentaire','prestations familiales']),
('travail',['code du travail','securite sociale','salarie','licenciement','apprentissage','formation professionnelle','arret de travail','retraite','assurance chomage','maladies? professionnelles?','artistes-auteurs','syndicats? professionnels?','conventions? collectives?','frais de sante','indemnites journalieres']),
('fiscal',['code general des impots','impots?\\b','taxe','tva','fiscal','douane','droits d\'enregistrement']),
('immo',['bail','baux','copropriete','logement','habitation','construction','notari','notaire','publicite fonciere','loyer']),
('urbenv',['urbanisme','environnement','code de l\'environnement','permis de construire','littoral','eau\\b','energie','climat']),
('affaires',['code de commerce','societes?\\b','entreprises? en difficulte','procedures? collectives?','commercant','registre du commerce','concurrence','commande publique']),
('banque',['code monetaire','credit a la consommation','etablissements? de credit','services de paiement','assurances?\\b','instruments financiers','epargne']),
('conso',['consommat','pratiques commerciales','accessibilite des produits']),
('numpi',['numerique','donnees','propriete intellectuelle','reseaux sociaux','cybersecurite','intelligence artificielle','plateformes?\\b','audiovisuel']),
('etrangers',['etrangers','droit d\'asile','sejour']),
('corporel',['victimes d\'accidents','dommage corporel','indemnisation des victimes']),
('constit',['loi organique','constitution']),
('public',['fonction publique','collectivites','administration','service public','fonctionnaires','ordre public'])]
# --- JORF
EXCL=['portant maintien','reconduction','affectation d','echelonnement indiciaire','avancement','statut particulier','sous-prefet','officier general','emploi de prefet','emplois de direction','corps des','ambassadeur','portant designation','acceptation d\'une donation','annulation de credits','ouverture de credits','virement de credits','repartition du produit','portant adoption de la strategie','autorisation environnementale relative','declarant d\'interet','portant approbation de la convention','publication de l\'accord','publication de la convention','publication de l\'amendement','publication du protocole','naturalisation','nomination','acces protege','cessation de fonctions','admission','promotion','elevation','legion d\'honneur','ordre national','tableau d\'avancement','portant delegation','delegation de signature','aux fonctions','charge de mission','renouvellement','reintegration','detachement','titularisation','mise a disposition','radiation','agrement','habilitation de','portant convocation','attribution de la','classement en','declarant d\'utilite publique','modificatif de decrets portant','portant attribution','composition du','portant creation de l\'aire','situation administrative']
JR={}
for f in sorted(glob.glob(D+'jorf-*.json'),key=lambda x:int(re.findall(r'\d+',x)[-1])):
  for x in json.load(open(f,encoding='utf-8-sig')).get('results',[]):
    for t in x.get('titles') or []:
      title=clean(t.get('title'));cid=t.get('cid')
      if not cid or cid in JR:continue
      JR[cid]={'cid':cid,'t':title,'nat':x.get('nature'),'d':(x.get('datePublication') or '')[:10],'jo':x.get('jorfText')}
jo=[];drop=collections.Counter()
for v in JR.values():
  tt=nz(v['t'])
  if any(e in tt for e in EXCL):drop['excl']+=1;continue
  dom=[d for d,ks in JRULES if any(re.search(r'\b'+k,tt) for k in ks)]
  if 'code civil' in tt and 'civil' not in dom:dom.insert(0,'civil')
  if any(k in tt for k in ['code de procedure civile','organisation judiciaire','juridictions','procedure civile','commissaires de justice','huissier','greffe']):dom.insert(0,'procedure')
  if any(k in tt for k in ['notari','notaire']):dom.append('immo')
  if not dom:
    if v['nat'] in ('LOI','ORDONNANCE'):dom=['public']
    else:drop['nodom']+=1;continue
  v['dom']=list(dict.fromkeys(dom))[:3];jo.append(v)
jo.sort(key=lambda x:x['d'],reverse=True)
# --- articles
arts={}
for line in open(D+'articles.jsonl',encoding='utf-8-sig'):
  line=line.rstrip('\n')
  if not line.strip():continue
  lt,num,js=line.split('|',2)
  try:a=json.loads(js).get('article') or {}
  except Exception as e:continue
  if not a:continue
  ms=a.get('dateDebut');deb=datetime.datetime.utcfromtimestamp(ms/1000).strftime('%Y-%m-%d') if isinstance(ms,(int,float)) and ms>0 else None
  txt=re.sub(r'\s+',' ',a.get('texte') or '').strip()
  if len(txt)>2500:txt=txt[:2450].rsplit(' ',1)[0]+'…'
  arts[lt+'|'+num]={'id':a.get('id'),'e':a.get('etat'),'d':deb,'t':txt}
par=json.load(open(D+'parametres.json',encoding='utf-8-sig'))
out={'date':par['date_synchro'],'debut':par['debut'],'fin':par['fin'],'jp':jp,'jo':jo,'arts':arts}
s='/* Lot 7 : données officielles PISTE (Judilibre, Légifrance), synchronisées le '+par['date_synchro']+' */\nconst PISTE='+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';\n'
open('piste_data.js','w',encoding='utf-8').write(s)
print('jp',len(jp),collections.Counter(d for x in jp for d in x['dom'][:1]))
print('jo',len(jo),drop,collections.Counter(d for x in jo for d in x['dom'][:1]))
print('arts',len(arts),collections.Counter(a['e'] for a in arts.values()),sum(1 for a in arts.values() if a['d'] and a['d']>='2024-10-04'))
print(len(s)//1024,'KB')
for x in jo[:40]:print(x['d'],x['nat'],x['dom'],x['t'][:140])
