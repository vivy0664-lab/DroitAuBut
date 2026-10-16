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
os.makedirs('juris', exist_ok=True)
names = [n.replace('de Nouvelle-Calédonie', 'de la Nouvelle-Calédonie').replace('de Polynésie', 'de la Polynésie').replace("d'Wallis", 'de Wallis') for n in names]
out = {'src': 'Ministère de la Justice, « Liste des juridictions compétentes pour les communes de France » (data.gouv.fr, licence ouverte)', 'n': names, 'c': rows}
s = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
open('juris/communes.json', 'w', encoding='utf-8').write(s)
print('communes', len(rows), 'juridictions', len(names), round(len(s.encode()) / 1e6, 2), 'Mo ; départements sans TA :', dict(miss))
