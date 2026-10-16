"""Vérifie la page avant envoi (à lancer depuis la racine du dépôt) :
aucune erreur JavaScript au chargement, l'onglet Jurisprudence s'affiche et la jurisprudence complète se charge.
Prérequis : pip install playwright && python3 -m playwright install --with-deps chromium"""
import sys, threading, functools, http.server, re, subprocess, tempfile, os
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    # Repli : contrôle de syntaxe des scripts de la page avec node --check
    page = open('index.html', encoding='utf-8').read()
    ko = 0
    for i, s in enumerate(re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', page, re.S)):
        f = os.path.join(tempfile.gettempdir(), f'dab-script-{i}.js'); open(f, 'w', encoding='utf-8').write(s)
        r = subprocess.run(['node', '--check', f], capture_output=True, text=True)
        if r.returncode: ko += 1; print(f'Script {i} : erreur de syntaxe\n{r.stderr[:1500]}')
    if ko: sys.exit(1)
    print('Vérification PARTIELLE (Playwright absent) : syntaxe JavaScript correcte, affichage non testé'); sys.exit(0)

class Silencieux(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Silencieux, directory='.'))
threading.Thread(target=srv.serve_forever, daemon=True).start()
url = f'http://127.0.0.1:{srv.server_address[1]}/'

erreurs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()
    page.on('pageerror', lambda e: erreurs.append('JS : ' + str(e)))
    page.on('console', lambda m: m.type == 'error' and 'fonts.g' not in m.text and erreurs.append('console : ' + m.text))
    page.goto(url, wait_until='load', timeout=120000)
    page.wait_for_timeout(2000)
    # panneau qui contient la jurisprudence
    panneau = page.evaluate("(()=>{const e=document.getElementById('jv-rec');const p=e&&e.closest('[id^=\"p-\"]');return p?p.id.slice(2):null})()")
    if not panneau: erreurs.append('Onglet Jurisprudence introuvable')
    else:
        page.evaluate(f"showPanel({panneau!r},false)")
        page.wait_for_timeout(500)
        if not page.is_visible('#jv-rec'): erreurs.append('Onglet Jurisprudence non affiché')
        elif len(page.inner_text('#jv-rec').strip()) < 200: erreurs.append('Jurisprudence récente vide')
        page.click('[data-jv="all"]')
        try:
            page.wait_for_function("(()=>{const a=document.getElementById('jv-all');return a&&!/Chargement/.test(a.innerText)&&a.innerText.length>200})()", timeout=60000)
            if page.query_selector('#jv-all .warn'): erreurs.append('Jurisprudence complète : échec du chargement')
        except Exception: erreurs.append('Jurisprudence complète : pas chargée en 60 s')
    page.wait_for_timeout(500)
    b.close()
srv.shutdown()
if erreurs:
    print('ÉCHEC de la vérification :'); [print(' -', e) for e in erreurs]; sys.exit(1)
print('Vérification OK : aucune erreur JavaScript, onglet Jurisprudence affiché, jurisprudence complète chargée')
