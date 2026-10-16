"""Téléchargement hebdomadaire des données officielles (équivalent cloud de mensuel.ps1, synchro-piste.ps1,
admin-ce.ps1 et admin-caa.ps1 de l'ordinateur).
Usage : python3 telecharger.py <dossier de sortie>
Identifiants PISTE lus dans les variables d'environnement PISTE_CLIENT_ID et PISTE_CLIENT_SECRET (jamais écrits sur disque).
Le dossier de sortie ne contient que des données publiques. Code de retour 0 même si une source échoue :
le journal sortie/mensuel.txt et sortie/etat.json disent ce qui a fonctionné."""
import os, sys, json, time, io, re, zipfile, datetime, urllib.request, urllib.parse, urllib.error

OUT = sys.argv[1].rstrip('/') + '/'
ICI = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT + 'admin', exist_ok=True); os.makedirs(OUT + 'admin-caa', exist_ok=True)
UA = {'User-Agent': 'DroitAuBut/1.0 (mise a jour hebdomadaire)'}
etat = {}
journal = open(OUT + 'mensuel.txt', 'w', encoding='utf-8')
def log(m):
    l = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '  ' + m
    print(l, flush=True); journal.write(l + '\n'); journal.flush()

def req(url, data=None, headers=None, timeout=120, method=None):
    h = dict(UA); h.update(headers or {})
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    with urllib.request.urlopen(r, timeout=timeout) as resp: return resp.read()

def err(e):
    if isinstance(e, urllib.error.HTTPError):
        try: corps = e.read().decode('utf-8', 'replace')[:800]
        except Exception: corps = ''
        return 'HTTP %s : %s' % (e.code, corps)
    return str(e)

def ecrire(nom, texte): open(OUT + nom, 'w', encoding='utf-8').write(texte)

auj = datetime.date.today()
log('Début de la mise à jour')

# 1. PISTE : Judilibre et Légifrance (120 derniers jours)
def piste():
    cid, sec = (os.environ.get(v, '').strip().strip('"\'').strip() for v in ('PISTE_CLIENT_ID', 'PISTE_CLIENT_SECRET'))
    if not cid or not sec:
        log('PISTE : variables PISTE_CLIENT_ID / PISTE_CLIENT_SECRET absentes de l\'environnement cloud'); return False
    try:
        corps = urllib.parse.urlencode({'grant_type': 'client_credentials', 'client_id': cid, 'client_secret': sec, 'scope': 'openid'}).encode()
        tok = json.loads(req('https://oauth.piste.gouv.fr/api/oauth/token', corps, {'Content-Type': 'application/x-www-form-urlencoded'}))['access_token']
    except Exception as e:
        log('PISTE : échec de l\'authentification : ' + err(e)); return False
    H = {'Authorization': 'Bearer ' + tok, 'Accept': 'application/json'}
    def appel(url, js=None):
        if js is None: return req(url, headers=H).decode('utf-8')
        return req(url, json.dumps(js, ensure_ascii=False).encode('utf-8'), dict(H, **{'Content-Type': 'application/json; charset=utf-8'})).decode('utf-8')
    log('PISTE : jeton obtenu')
    fin, debut = auj.isoformat(), (auj - datetime.timedelta(days=120)).isoformat()
    ecrire('parametres.json', json.dumps({'date_synchro': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), 'debut': debut, 'fin': fin}))
    # Judilibre : arrêts de la Cour de cassation publiés au Bulletin
    jb = 'https://api.piste.gouv.fr/cassation/judilibre/v1.0'
    nJ = 0
    for b in range(20):
        u = f'{jb}/export?batch={b}&batch_size=50&jurisdiction=cc&publication=b&date_start={debut}&date_end={fin}&date_type=creation&order=desc'
        try: t = appel(u)
        except Exception as e: log(f'Judilibre, lot {b} : ' + err(e)); break
        ecrire(f'judilibre-{b}.json', t); nJ += 1
        if not re.search(r'"results"\s*:\s*\[\s*\{', t) or re.search(r'"next_batch"\s*:\s*null', t): break
    log(f'Judilibre : {nJ} lot(s)')
    # Légifrance : lois, ordonnances et décrets publiés au JO
    lf = 'https://api.piste.gouv.fr/dila/legifrance/lf-engine-app'
    nP = 0
    for pg in range(1, 11):
        q = {'fond': 'JORF', 'recherche': {'champs': [{'typeChamp': 'TITLE', 'criteres': [{'typeRecherche': 'UN_DES_MOTS', 'valeur': 'loi ordonnance décret', 'operateur': 'OU'}], 'operateur': 'ET'}],
             'filtres': [{'facette': 'NATURE', 'valeurs': ['LOI', 'ORDONNANCE', 'DECRET']}, {'facette': 'DATE_PUBLICATION', 'dates': {'start': debut, 'end': fin}}],
             'pageNumber': pg, 'pageSize': 100, 'operateur': 'ET', 'sort': 'PUBLICATION_DATE_DESC', 'typePagination': 'DEFAUT'}}
        try: t = appel(lf + '/search', q)
        except Exception as e: log(f'Légifrance JORF, page {pg} : ' + err(e)); break
        ecrire(f'jorf-{pg}.json', t); nP += 1
        if '"titles"' not in t: break
        time.sleep(0.2)
    log(f'Légifrance JORF : {nP} page(s)')
    # Légifrance : version en vigueur des articles cités sur le site
    lignes, ep, ok, ko = [], None, 0, 0
    for l in open(os.path.join(ICI, '..', 'articles.txt'), encoding='utf-8-sig'):
        if not l.strip(): continue
        p = l.strip().split('|'); t, e_ = None, ''
        for e in ([ep] if ep else ['/consult/getArticleWithIdandNum', '/consult/getArticleWithIdAndNum']):
            try: t = appel(lf + e, {'id': p[0], 'num': p[1]}); ep = e; break
            except Exception as x: e_ = err(x)
        if t: lignes.append(p[0] + '|' + p[1] + '|' + re.sub(r'\r?\n', ' ', t)); ok += 1
        else: lignes.append(p[0] + '|' + p[1] + '|ERREUR ' + re.sub(r'\r?\n', ' ', e_)); ko += 1
        time.sleep(0.15)
    ecrire('articles.jsonl', '\n'.join(lignes) + '\n')
    log(f'Articles : {ok} trouvé(s), {ko} en erreur')
    return nJ > 0

# 2. Justice administrative : archives mensuelles open data (mois en cours et deux mois précédents)
def mois():
    y, m = auj.year, auj.month - 2
    while m < 1: y, m = y - 1, m + 12
    while (y, m) <= (auj.year, auj.month):
        yield f'{y}', f'{m:02d}'
        m += 1
        if m > 12: y, m = y + 1, 1

def admin(nom, dossier, urls, garder):
    n_ok = 0
    for y, m in mois():
        data, e_ = None, ''
        for u in urls(y, m):
            try: data = req(u, timeout=600); break
            except Exception as e: e_ = err(e)
        if data is None: log(f'{nom} {y}-{m} : archive indisponible ({e_[:200]})'); continue
        n = k = 0; parts = []
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for e in z.namelist():
                if not e.endswith('.xml'): continue
                x = z.read(e).decode('utf-8-sig', 'replace'); n += 1
                mm = re.search(r'<Code_Publication>\s*([A-Z]\+?)', x)
                p = mm.group(1) if mm else '?'
                if p in garder: parts.append(x + '\n<!--FIN-->\n'); k += 1
        if k: open(OUT + f'{dossier}/{"CE" if dossier == "admin" else "CAA"}-{y}{m}.xml', 'w', encoding='utf-8').write(''.join(parts)); n_ok += 1
        log(f'{nom} {y}-{m} : {n} décisions, {k} retenues')
    return n_ok > 0

def ce_urls(y, m): return [f'https://opendata.justice-administrative.fr/DCE/{y}/{m}/CE_{y}{m}.zip']
def caa_urls(y, m): return [f'https://opendata.justice-administrative.fr/{d}/{y}/{m}/CAA_{y}{m}.zip' for d in ('DCA', 'DCAA', 'CAA')]

for nom, f in (('piste', piste),
               ('ce', lambda: admin("Conseil d'État", 'admin', ce_urls, ('A', 'B'))),
               ('caa', lambda: admin("Cours administratives d'appel", 'admin-caa', caa_urls, ('A', 'B', 'R', 'C+')))):
    try: etat[nom] = bool(f())
    except Exception as e: log(f'{nom} : erreur {err(e)}'); etat[nom] = False

# 3. Juridictions compétentes par commune (data.gouv.fr)
try:
    csv = req('https://www.data.gouv.fr/api/1/datasets/r/56423a8b-be50-4e96-acf1-23283e44bf85', timeout=300)
    if len(csv) < 100000 or b';' not in csv[:2000]: raise ValueError(f'fichier inattendu ({len(csv)} octets)')
    open(OUT + 'juridictions.csv', 'wb').write(csv)
    log('Juridictions compétentes par commune : téléchargées'); etat['juridictions'] = True
except Exception as e:
    log('Juridictions : erreur ' + err(e)); etat['juridictions'] = False

json.dump(etat, open(OUT + 'etat.json', 'w'))
log('Fin : ' + json.dumps(etat))
