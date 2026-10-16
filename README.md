# Droit au But

Site de révision et de pratique du droit français : fiches par année et par matière, quiz, sujets corrigés, procédures, outils de calcul, codes (Code civil, Code pénal, Code du travail…) et jurisprudence consultables hors ligne.

## Structure

```
index.html        la page (HTML, CSS et JS en un seul fichier)
codes/*.json      textes des codes, chargés à la demande
juris/*.json      décisions (Cour de cassation, Conseil d'État, CAA)
```

## Lancer en local

La page charge les fichiers JSON avec `fetch`, il faut donc la servir via HTTP (l'ouverture directe du fichier ne suffit pas) :

```bash
py -m http.server 8765
```

Puis ouvrir http://localhost:8765.

## Mise en ligne

Le dépôt peut être publié tel quel avec **GitHub Pages** (Settings → Pages → branche `main`, dossier `/`).

## Remarque

Cette page provient d'un artefact Claude. Les fonctions partagées (partage de partiels et de cas, génération d'exercices, téléchargements) utilisent les capacités propres aux artefacts et sont simplement masquées ici. Les préférences et la progression restent enregistrées dans le navigateur (`localStorage`).

## Mise à jour hebdomadaire

Chaque lundi, une routine Claude Code dans le cloud télécharge les nouveautés (Judilibre et Légifrance via PISTE, open data de la justice administrative, juridictions par commune), met à jour `juris/*.json` et les blocs de données de `index.html`, renouvelle le quiz de la semaine, vérifie la page puis pousse sur `main`. Le dossier `maj/` contient les scripts et les consignes ([maj/CONSIGNES.md](maj/CONSIGNES.md)).

Les identifiants PISTE ne sont jamais dans le dépôt : ils sont définis comme variables d'environnement (`PISTE_CLIENT_ID`, `PISTE_CLIENT_SECRET`) de l'environnement cloud de la routine.
