"""Mise à jour hebdomadaire de Droit au But, à lancer depuis la racine du dépôt.
  python3 maj/mise_a_jour.py                  télécharge les données (telecharger.py) puis reconstruit
  python3 maj/mise_a_jour.py --sortie DOSSIER   reconstruit à partir d'un dossier « sortie » déjà rempli
Met à jour juris/*.json, maj/etat/ce_refs.json, maj/etat/piste_data.js et le bloc des données PISTE dans index.html,
puis prépare maj/travail/weekly_src.json pour le quiz de la semaine (voir maj/CONSIGNES.md).
Seuls les blocs de données de index.html sont remplacés : le reste de la page n'est jamais régénéré."""
import os, sys, json, glob, shutil, subprocess, tempfile

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
    print('BILAN', json.dumps(bilan, ensure_ascii=False))

    # Matière du quiz de la semaine
    os.makedirs(TRAV, exist_ok=True)
    if piste_ok and shutil.which('node'):
        if subprocess.run(['node', 'dumpweek.cjs'], cwd=P).returncode == 0:
            shutil.copy(os.path.join(P, 'weekly_src.json'), TRAV)
            print('Quiz : source prête dans maj/travail/weekly_src.json')
    elif piste_ok:
        print('!! node introuvable : weekly_src.json non produit')
    shutil.rmtree(W, ignore_errors=True)
    print('Terminé.')
