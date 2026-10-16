# Référentiel des paramètres légaux de la page

Valeurs codées en dur dans `index.html` qui dépendent de textes susceptibles d'évoluer.
Pour retrouver un paramètre : `grep -n "<repère>" index.html`. Une même valeur figure souvent **aussi en clair**
dans les explications des calculateurs (objet `CALC`, champs `fm` / `x`) et dans les fiches :
après toute modification, cherche l'ancienne valeur sous ses formes écrites (`11600`, `11 600`, `11 600 €`, `11 600`) et mets à jour chaque occurrence qui désigne le même paramètre.

| Paramètre | Repère dans index.html | Source légale | Rythme habituel de révision |
|---|---|---|---|
| Taux de l'intérêt légal (créanciers particuliers / autres), par semestre | `const TXLEG=` (ajouter `[année,semestre,taux particuliers,taux autres]`) | C. mon. fin., art. L. 313-2 ; arrêté semestriel | Arrêté publié fin juin et fin décembre |
| Plafond annuel de la sécurité sociale | `PASS:` dans `const P26=` | CSS, art. L. 241-3 ; arrêté annuel | Arrêté en décembre |
| Barème de l'impôt sur le revenu, plafond du quotient familial, décote, abattement de 10 % | `const P26=` (`IR`, `QF`, `DEC1`, `DEC2`, `DECT`, `AB10`), champs `ir-qf`, `ir-dt`, texte « Barème 2026 par part » | CGI, art. 197, 158 ; loi de finances | Loi de finances (décembre) |
| Droits de succession et de donation (barèmes, abattements) | `const LD=`, `const FS=`, `const LD5=`, `const EPX=`, `const FS5=`, `const DONL=` | CGI, art. 777, 779, 790 B, 790 E, 790 F | Loi de finances (rare) |
| Barème de l'IFI | `const IFIB=` | CGI, art. 977 | Loi de finances (rare) |
| Droits de mutation à titre onéreux, émoluments des notaires | champs `fn-dep`, `fn-com`, `fn-fa`, `fn-t1` à `fn-t4`, `fn-csi` | CGI, art. 1594 D ; C. com., art. A. 444-91 | Loi de finances ; arrêté tarifaire (tous les 2 ans) |
| Saisie des rémunérations : seuils du barème, majoration par personne à charge | champs `sa-s0` à `sa-s5` (`[4480,8730,…]`), `sa-maj` | C. trav., art. R. 3252-2 et R. 3252-3 ; décret annuel | Décret en décembre (applicable au 1er janvier) |
| Montant forfaitaire du RSA (personne seule) : fraction insaisissable, minimum vital, solde bancaire insaisissable | champs `sa-rsa`, `pa-mv` ; textes « montant forfaitaire du RSA » | CASF, art. L. 262-2 ; décret de revalorisation | Revalorisation au 1er avril |
| Indemnité de licenciement (barème Macron) | `const MACRON=` | C. trav., art. L. 1235-3 | Loi seulement |
| Seuils des marchés publics et de la commande publique | `const SEUILS=` | CCP ; avis / règlements européens | Tous les 2 ans (1er janvier des années paires) |

Autres contenus à surveiller : fiches, procédures, délais et ressources qui citent un article de code. Si un article cité sur le site
change (`articles_modifies` dans `maj/travail/reformes.json`), cherche ses mentions (`grep -n "L. 1234-5" index.html`, avec et sans espace) et vérifie
que le texte du site reste exact au regard de la nouvelle rédaction.
