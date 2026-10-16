"""Mise à jour hebdomadaire de Droit au But, à lancer depuis la racine du dépôt.
  python3 maj/mise_a_jour.py                  télécharge les données (telecharger.py) puis reconstruit
  python3 maj/mise_a_jour.py --sortie DOSSIER   reconstruit à partir d'un dossier « sortie » déjà rempli
Met à jour juris/*.json, maj/etat/ce_refs.json, maj/etat/piste_data.js et le bloc des données PISTE dans index.html,
puis prépare maj/travail/weekly_src.json pour le quiz de la semaine (voir maj/CONSIGNES.md).
Seuls les blocs de données de index.html sont remplacés : le reste de la page n'est jamais régénéré."""
import os, sys, json, glob, re, shutil, subprocess, tempfile

REPO = os.getcwd()
MAJ = os.path.join(REPO, 'maj')
ETAT = os.path.join(MAJ, 'etat')
TRAV = os.path.join(MAJ, 'travail')
if not os.path.exists(os.path.join(REPO, 'index.html')) or not os.path.isdir(MAJ):
    sys.exit('À lancer depuis la racine du dépôt DroitAuBut')

def lire(p): return open(p, encoding='utf-8', newline='').read()
def ecrire(p, s): open(p, 'w', encoding='utf-8', newline='').write(s)

def remplacer_bloc(ancien, nouveau, quoi):
    """Remplace dans index.html un bloc présent mot pour mot une seule fois."""
    page = lire(os.path.join(REPO, 'index.html'))
    n = page.count(ancien)
    if n != 1: sys.exit(f'{quoi} : bloc actuel trouvé {n} fois dans index.html (attendu : 1). Rien n\'a été remplacé.')
    if ancien != nouveau: ecrire(os.path.join(REPO, 'index.html'), page.replace(ancien, nouveau))

def ids_juris():
    out = {}
    for n in ('cass', 'ce', 'caa'):
        L = json.load(open(os.path.join(REPO, 'juris', n + '.json'), encoding='utf-8'))
        out[n] = {json.dumps(r[:3] if n == 'caa' else r[:2], ensure_ascii=False) for r in L}
    return out

if __name__ == '__main__':
    W = tempfile.mkdtemp(prefix='dab-')
    if '--sortie' in sys.argv:
        S = os.path.abspath(sys.argv[sys.argv.index('--sortie') + 1])
    else:
        S = os.path.join(W, 'sortie')
        r = subprocess.run([sys.executable, os.path.join(MAJ, 'scripts', 'telecharger.py'), S])
        if r.returncode: sys.exit('telecharger.py a échoué')
    S = S.rstrip('/\\') + '/'
    P = os.path.join(W, 'partiels')
    os.makedirs(os.path.join(P, 'piste')); os.makedirs(os.path.join(P, 'juris'))
    for f in glob.glob(os.path.join(MAJ, 'scripts', '*')): shutil.copy(f, P)
    for f in glob.glob(os.path.join(REPO, 'juris', '*.json')): shutil.copy(f, os.path.join(P, 'juris'))
    for f in ('piste_data.js', 'news.js'): shutil.copy(os.path.join(ETAT, f), P)
    shutil.copy(os.path.join(ETAT, 'ce_refs.json'), W)
    env = dict(os.environ, SORTIE=S, PYTHONUTF8='1')
    def run(f):
        print('==', f, flush=True)
        if subprocess.run([sys.executable, f], cwd=P, env=env).returncode: sys.exit(f + ' a échoué')

    avant = ids_juris()
    piste_ok = bool(glob.glob(S + 'judilibre-*.json')) and os.path.exists(S + 'parametres.json') and os.path.exists(S + 'articles.jsonl')
    if piste_ok:
        for pat in ('judilibre-*.json', 'jorf-*.json', 'articles.jsonl', 'parametres.json'):
            for f in glob.glob(S + pat): shutil.copy(f, os.path.join(P, 'piste'))
    else:
        print('!! Pas de nouvelles données PISTE (Judilibre/Légifrance) : bloc PISTE de la page conservé')
    if glob.glob(S + 'admin/CE-*.xml') or glob.glob(S + 'admin-caa/CAA-*.xml'): run('admin.py')
    if piste_ok: run('piste_build.py')
    run('juris_build.py')
    if os.path.exists(S + 'juridictions.csv') and os.path.getsize(S + 'juridictions.csv') > 100000: run('juridictions_build.py')
    else: print('!! juridictions.csv absent : juris/communes.json conservé')

    # Report dans le dépôt
    for f in glob.glob(os.path.join(P, 'juris', '*.json')): shutil.copy(f, os.path.join(REPO, 'juris'))
    shutil.copy(os.path.join(W, 'ce_refs.json'), ETAT)
    ancien, nouveau = lire(os.path.join(ETAT, 'piste_data.js')), lire(os.path.join(P, 'piste_data.js')).replace('\r\n', '\n')
    remplacer_bloc(ancien, nouveau, 'Données PISTE')
    ecrire(os.path.join(ETAT, 'piste_data.js'), nouveau)

    apres = ids_juris()
    bilan = {n: len(apres[n] - avant[n]) for n in apres}
    old_p = json.loads(ancien[ancien.index('=') + 1:].rstrip().rstrip(';'))
    new_p = json.loads(nouveau[nouveau.index('=') + 1:].rstrip().rstrip(';'))
    bilan['textes_jo'] = len({x['cid'] for x in new_p['jo']} - {x['cid'] for x in old_p['jo']})
    bilan['piste'] = piste_ok
    bilan['synchro'] = new_p['date']
    if os.path.exists(S + 'etat.json'): bilan['sources'] = json.load(open(S + 'etat.json'))
    # Réformes à examiner : textes nouveaux (JO + veille ciblée) et articles cités sur le site dont le texte a changé
    os.makedirs(TRAV, exist_ok=True)
    vus_f = os.path.join(ETAT, 'reformes_vues.json')
    vus = set(json.load(open(vus_f, encoding='utf-8'))) if os.path.exists(vus_f) else set()
    old_cids = {x['cid'] for x in old_p['jo']}
    textes = [dict(x, src='jo') for x in new_p['jo'] if x['cid'] not in old_cids and x['cid'] not in vus]
    for f in sorted(glob.glob(S + 'veille-*.json')):
        for r in json.load(open(f, encoding='utf-8-sig')).get('results', []):
            for t in r.get('titles') or []:
                c = t.get('cid')
                if c and c not in vus and all(c != x['cid'] for x in textes):
                    textes.append({'cid': c, 't': re.sub(r'</?mark>', '', t.get('title') or ''), 'nat': r.get('nature'),
                                   'd': (r.get('datePublication') or '')[:10], 'src': 'veille'})
    noms = {}
    for l in open(os.path.join(MAJ, 'articles.txt'), encoding='utf-8-sig'):
        p = l.strip().split('|')
        if len(p) >= 4: noms[p[0] + '|' + p[1]] = p[2] + ' ' + p[1]
    norm = lambda s: re.sub(r'\s+', ' ', s or '').strip()
    arts = [{'ref': noms.get(k, k), 'cle': k, 'id': a.get('id'), 'vigueur': a.get('d'), 'ancien': old_p['arts'].get(k, {}).get('t'), 'nouveau': a.get('t')}
            for k, a in new_p['arts'].items() if norm(a.get('t')) != norm(old_p['arts'].get(k, {}).get('t')) and old_p['arts'].get(k)]
    json.dump({'textes': textes, 'articles_modifies': arts}, open(os.path.join(TRAV, 'reformes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(sorted(vus | {x['cid'] for x in textes}), open(vus_f, 'w', encoding='utf-8'))
    bilan['reformes_a_examiner'] = {'textes': len(textes), 'articles_modifies': len(arts)}
    print('BILAN', json.dumps(bilan, ensure_ascii=False))

    # Matière du quiz de la semaine
    if piste_ok and shutil.which('node'):
        if subprocess.run(['node', 'dumpweek.cjs'], cwd=P).returncode == 0:
            shutil.copy(os.path.join(P, 'weekly_src.json'), TRAV)
            print('Quiz : source prête dans maj/travail/weekly_src.json')
    elif piste_ok:
        print('!! node introuvable : weekly_src.json non produit')
    shutil.rmtree(W, ignore_errors=True)
    print('Terminé.')
