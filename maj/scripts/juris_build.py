"""juris/cass.json, juris/ce.json, juris/caa.json : toute la jurisprudence, chargée à la demande."""
import json, glob, re, os
src = open('piste_build.py', encoding='utf-8').read()
exec(src[:src.index('# --- Judilibre')])  # nz, RULES, classify, CHB
S = os.environ.get('SORTIE','/mnt/user-data/uploads/Truc/droit-au-but-piste/sortie/')
os.makedirs('juris', exist_ok=True)
def cut(s, n):
    s = re.sub(r'\s+', ' ', s or '').strip()
    return s if len(s) <= n else s[:n - 10].rsplit(' ', 1)[0] + '…'
H = {}
for f in sorted(glob.glob(S + 'hist-*.json')) + sorted(glob.glob(S + 'judilibre-*.json')) + sorted(glob.glob('piste/judilibre-*.json')):
    for r in json.load(open(f, encoding='utf-8-sig')).get('results', []):
        H[r['id']] = r
cass = []
for r in H.values():
    tas = r.get('titlesAndSummaries') or []
    titles = [t for x in tas for t in (x.get('titles') or [])]
    head = ' – '.join(titles[:3]).capitalize() if titles else (', '.join(r.get('themes') or [])[:120].capitalize() or 'Arrêt publié')
    summ = r.get('summary') or (tas[0].get('summary') if tas else '') or ''
    ch = r.get('chamber') or ''
    dom = classify(' '.join(titles) + ' ' + ' '.join(r.get('themes') or []) + ' ' + summ[:300], ch)
    p = ''.join(sorted(set(r.get('publication') or []) - {'b'}))
    cass.append([r['id'], r.get('decision_date') or '', r.get('number') or '', ch, r.get('solution') or '', p, cut(head, 260), cut(summ, 700), dom])
try:
    prev = {r[0]: r for r in json.load(open('juris/cass.json', encoding='utf-8'))}
except FileNotFoundError:
    prev = {}
for r in cass: prev[r[0]] = r
cass = list(prev.values())
cass.sort(key=lambda x: x[1], reverse=True)
CD = {'cja':'public','curb':'urbenv','cenv':'urbenv','cesa':'etrangers','cgi':'fiscal','lpf':'fiscal','ccp':'public','css':'travail','ctrav':'travail','celec':'public','ccom':'affaires','cciv':'civil','cmf':'banque','ccons':'immo','cpen':'penal','cpp':'penal','cassur':'banque','cconso':'conso','cpi':'numpi','cpc':'procedure','coj':'procedure','cpce':'procedure'}
ce, caa = [], []
for o in json.load(open('../ce_refs.json', encoding='utf-8')):
    cs = [c for c, n, e in o['refs'] if c != 'cja'] or [c for c, n, e in o['refs']]
    dom = list(dict.fromkeys(CD.get(c, 'public') for c in cs))[:3] or ['public']
    arts = ', '.join(dict.fromkeys('art. ' + n for c, n, e in o['refs']))[:160]
    row = [o['num'], o['d'], o['f'] or '', o['pub'], (o['sol'] or '').strip(), cut(o['tr'] or '', 120), cut(o['intro'], 600), dom, arts]
    if o.get('jur', 'CE') == 'CE': ce.append(row)
    else: caa.append([o['jur'][4:]] + row)
for L in (ce, caa): L.sort(key=lambda x: x[-8], reverse=True)
for name, L in (('cass', cass), ('ce', ce), ('caa', caa)):
    s = json.dumps(L, ensure_ascii=False, separators=(',', ':'))
    open('juris/' + name + '.json', 'w', encoding='utf-8').write(s)
    print(name, len(L), round(len(s.encode()) / 1e6, 2), 'Mo', L[0][:6] if L else '')
import collections
print(collections.Counter(x[3] for x in cass)); print(collections.Counter(x[0] for x in caa)); print(collections.Counter(x[3] for x in ce))
