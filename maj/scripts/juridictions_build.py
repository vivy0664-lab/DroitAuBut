"""juris/communes.json : juridictions compétentes pour chaque commune (fichier du ministère de la Justice, data.gouv.fr)
+ tribunal administratif et cour administrative d'appel déduits du département (CJA, art. R. 221-3 et R. 221-7)."""
import csv, json, os, collections
S = os.environ.get('SORTIE', '/mnt/user-data/uploads/Truc/droit-au-but-piste/sortie/')
TA = {'Amiens':'02 60 80','Bastia':'2A 2B','Besançon':'25 39 70 90','Bordeaux':'24 33 47','Caen':'14 50 61','Cergy-Pontoise':'92 95',
 'Châlons-en-Champagne':'08 10 51 52','Clermont-Ferrand':'03 15 43 63','Dijon':'21 58 71 89','Grenoble':'26 38 73 74','Lille':'59 62',
 'Limoges':'19 23 36 87','Lyon':'01 07 42 69','Marseille':'04 05 13','Melun':'77 94','Montpellier':'11 34 66','Montreuil':'93',
 'Nancy':'54 55 88','Nantes':'44 49 53 72 85','Nice':'06','Nîmes':'30 48 84','Orléans':'18 28 37 41 45','Paris':'75','Pau':'32 40 64 65',
 'Poitiers':'16 17 79 86','Rennes':'22 29 35 56','Rouen':'27 76','Strasbourg':'57 67 68','Toulon':'83','Toulouse':'09 12 31 46 81 82',
 'Versailles':'78 91','Basse-Terre':'971','Fort-de-France':'972','Cayenne':'973','La Réunion':'974','Saint-Pierre-et-Miquelon':'975','Mayotte':'976','Saint-Barthélemy':'977','Saint-Martin':'978','Wallis-et-Futuna':'986','Polynésie française':'987','Nouvelle-Calédonie':'988'}
CAA = {'Bordeaux':'Bordeaux Limoges Pau Poitiers Basse-Terre Fort-de-France Cayenne La_Réunion Mayotte Saint-Pierre-et-Miquelon Saint-Barthélemy Saint-Martin',
 'Douai':'Amiens Lille Rouen','Lyon':'Clermont-Ferrand Dijon Grenoble Lyon','Marseille':'Bastia Marseille Nice Toulon',
 'Nancy':'Besançon Châlons-en-Champagne Nancy Strasbourg','Nantes':'Caen Nantes Rennes','Paris':'Melun Montreuil Paris Wallis-et-Futuna Polynésie_française Nouvelle-Calédonie',
 'Toulouse':'Montpellier Nîmes Toulouse','Versailles':'Cergy-Pontoise Orléans Versailles'}
D2TA = {d: t for t, ds in TA.items() for d in ds.split()}
TA2CAA = {t.replace('_', ' '): c for c, ts in CAA.items() for t in ts.split()}
names = []; idx = {}
def I(n):
    n = (n or '').strip()
    if not n: return -1
    if n not in idx: idx[n] = len(names); names.append(n)
    return idx[n]
rows = []; miss = collections.Counter()
with open(S + 'juridictions.csv', encoding='utf-8-sig', newline='') as f:
    r = csv.reader(f, delimiter=';'); head = next(r)
    for x in r:
        if len(x) < 14 or not x[0]: continue
        ins = x[0].strip(); dep = ins[:3] if ins[:2] in ('97', '98') else ins[:2]
        ta = D2TA.get(dep)
        if not ta: miss[dep] += 1
        rows.append([ins, x[1].strip(), I(x[4]), I(x[7]), I(x[10]), I(x[13]), I(('Tribunal administratif de ' if ta[0] not in 'AEIOUÉ' else "Tribunal administratif d'") + ta.replace('La Réunion', 'la Réunion')) if ta else -1, I("Cour administrative d'appel de " + TA2CAA[ta]) if ta else -1])
# Tribunaux de commerce (ou des activités économiques) et coordonnées : annuaire de l'administration (service-public.fr).
# Le téléchargement de la semaine (annuaire_justice.json brut) rafraîchit la copie compacte gardée dans maj/etat/.
import unicodedata, re
ETAT = 'maj/etat/annuaire_justice.json'
TYPES = ('tribunal_commerce', 'tae', 'tgi', 'ti', 'prudhommes', 'cour_appel')
if os.path.exists(S + 'annuaire_justice.json'):
    try:
        raw = json.load(open(S + 'annuaire_justice.json', encoding='utf-8')); comp = []
        for x in raw:
            for p in json.loads(x.get('pivot') or '[]'):
                t = p.get('type_service_local')
                if t not in TYPES: continue
                a = (json.loads(x.get('adresse') or '[]') or [{}])[0]
                rue = re.sub(r"(?<=\w )(?:(?:Du|De|Des|La|Le|Les|Et|Aux|Au|En|Sur|Sous)(?= )|(?:D'|L')(?=\w))", lambda m: m.group(0).lower(), (a.get('numero_voie') or '').strip().title())
                ad = ', '.join(v for v in (rue, ((a.get('code_postal') or '').strip().zfill(5) + ' ' + (a.get('nom_commune') or '').strip().title()).strip()) if v)
                tel = ((json.loads(x.get('telephone') or '[]') or [{}])[0].get('valeur') or '').strip()
                comp.append([x['nom'].strip(), t, (p.get('code_insee_commune') or []) if t in ('tribunal_commerce', 'tae') else [], ad, tel, x.get('url_service_public') or ''])
        if len(comp) > 300: json.dump(comp, open(ETAT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        else: print('!! annuaire_justice.json incomplet : copie précédente conservée')
    except Exception as e: print('!! annuaire illisible :', e)
ANN = json.load(open(ETAT, encoding='utf-8')) if os.path.exists(ETAT) else []
def K(n): return ' '.join(unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower().replace('’', "'").replace('-', ' ').split())
TC = {}
for nom, t, cs, ad, tel, url in ANN:
    for c in cs: TC.setdefault(c, nom)
nmiss = collections.Counter()
for row in rows:
    ins = row[0]; dep = ins[:3] if ins[:2] in ('97', '98') else ins[:2]; tj = names[row[3]] if row[3] >= 0 else ''
    if ins in TC: row.append(I(TC[ins]))
    elif dep in ('57', '67', '68') and tj: row.append(I('Chambre commerciale du ' + tj[0].lower() + tj[1:]))
    elif dep in ('971', '972', '973', '974', '976') and tj.startswith('Tribunal judiciaire'): row.append(I('Tribunal mixte de commerce' + tj[len('Tribunal judiciaire'):]))
    else: row.append(-1); nmiss[dep] += 1
INFO = {K(nom): [ad, tel, url] for nom, t, cs, ad, tel, url in ANN}
os.makedirs('juris', exist_ok=True)
names = [n.replace('de Nouvelle-Calédonie', 'de la Nouvelle-Calédonie').replace('de Polynésie', 'de la Polynésie').replace("d'Wallis", 'de Wallis') for n in names]
def siege(n):
    for pre in ('Chambre commerciale du tribunal judiciaire', 'Tribunal mixte de commerce'):
        if n.startswith(pre): return 'Tribunal judiciaire' + n[len(pre):]
    return n
coords = {i: INFO.get(K(n)) or INFO[K(siege(n))] for i, n in enumerate(names) if K(n) in INFO or K(siege(n)) in INFO}
print('tribunal de commerce absent :', dict(nmiss), '; coordonnées :', len(coords), '/', len(names))
out = {'src': 'Ministère de la Justice, « Liste des juridictions compétentes pour les communes de France » (data.gouv.fr, licence ouverte) ; tribunaux de commerce et coordonnées : annuaire de l\'administration (service-public.fr)', 'n': names, 'c': rows, 'a': coords}
s = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
open('juris/communes.json', 'w', encoding='utf-8').write(s)
print('communes', len(rows), 'juridictions', len(names), round(len(s.encode()) / 1e6, 2), 'Mo ; départements sans TA :', dict(miss))
