"""Installe le quiz de la semaine écrit dans maj/travail/weekly.js (à lancer depuis la racine du dépôt).
Contrôle le format, remplace le bloc WEEKLY de index.html et met à jour maj/etat/weekly.js."""
import os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mise_a_jour import ETAT, TRAV, lire, ecrire, remplacer_bloc

nouveau = lire(os.path.join(TRAV, 'weekly.js'))
if not nouveau.endswith('\n'): nouveau += '\n'
CHECK = r"""
const fs=require('fs');let WEEKLY;eval(fs.readFileSync(process.argv[1],'utf8'));
const W=WEEKLY,err=[];const re=/^\d{4}-\d{2}-\d{2}$/;
if(!W||typeof W!=='object')err.push('WEEKLY absent');
else{
  if(!/^\d{4}-W\d{2}$/.test(W.sem))err.push('sem invalide');
  if(!re.test(W.du)||!re.test(W.au))err.push('du/au invalides');
  for(const k of ['reformes','jurisprudence']){const L=W[k];
    if(!Array.isArray(L)||L.length<6||L.length>12){err.push(k+' : 6 à 12 questions attendues');continue}
    L.forEach((x,i)=>{const t=k+'['+i+'] ';
      if(typeof x.q!=='string'||!x.q)err.push(t+'q');
      if(!Array.isArray(x.o)||x.o.length!==4||x.o.some(o=>typeof o!=='string'||!o))err.push(t+'o : 4 options');
      if(!Number.isInteger(x.a)||x.a<0||x.a>3)err.push(t+'a');
      if(typeof x.e!=='string'||!x.e)err.push(t+'e');
      if(!re.test(x.d))err.push(t+'d');
      if(typeof x.dom!=='string'||!x.dom)err.push(t+'dom');});
    const pos=new Set(L.map(x=>x.a));if(pos.size<3)err.push(k+' : bonnes réponses pas assez variées');}
}
if(err.length){console.error(err.join('\n'));process.exit(1)}
console.log('Quiz valide :',W.sem,W.reformes.length,'+',W.jurisprudence.length,'questions');
"""
r = subprocess.run(['node', '-e', CHECK, os.path.join(TRAV, 'weekly.js')])
if r.returncode: sys.exit('Format du quiz incorrect : rien n\'a été remplacé')
remplacer_bloc(lire(os.path.join(ETAT, 'weekly.js')), nouveau, 'Quiz de la semaine')
ecrire(os.path.join(ETAT, 'weekly.js'), nouveau)
print('Quiz installé dans index.html')
