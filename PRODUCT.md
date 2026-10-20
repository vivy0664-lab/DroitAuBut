# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Two primary audiences, weighted equally:

- **Law students** (L1 to M2, exam and competitive-exam preparation) who revise by year and subject, train on case studies, essays and case commentaries, and quiz themselves.
- **Legal practitioners** (lawyers, in-house counsel and other legal professions) who use the "Mon métier" space: practice-oriented subject sheets, procedures, deadlines, calculation tools, deeds and case law.

Both audiences use the site in four situations, all confirmed:

- long revision or work sessions on a computer;
- short sessions on a phone (quiz, a sheet) in transit or during a break;
- a quick lookup of an article, a decision, a procedure or a deadline;
- downloading, printing and annotating sheets (PDF and Word export).

## Product Purpose

A free, French-language legal library that takes a reader from understanding a rule to applying it: subject sheets at three reading depths (Synthèse, Développé, Détaillé), quizzes, exam-style subjects with separate model answers, procedures, calculators, legal codes and case law, and current legal news. Success means a student or practitioner finds the rule, its sources and its traps quickly, and can rely on it.

## Positioning

One place where revision material and practice material sit side by side, sourced to official texts and decisions (Légifrance, Judilibre, Conseil d'État and administrative courts open data), with reforms, case law and the weekly quiz refreshed automatically every Monday.

## Operating Context

- Published as a static site on GitHub Pages (https://vivy0664-lab.github.io/DroitAuBut/), originally built as a claude.ai artifact that still exists in parallel.
- A cloud routine updates the data every Monday and only replaces marked data blocks inside `index.html` (PISTE data, WEEKLY quiz) plus `juris/*.json`; the rest of the page is hand-maintained. See `maj/CONSIGNES.md`.
- Legal codes (`codes/*.json`) and case law (`juris/*.json`) load on demand; progress, preferences and the error notebook are stored in the browser (`localStorage`).
- Navigation is organised as a library: floors are years (L1 to M2), a shelf holds the subjects as book spines, and an opened volume shows tabs (fiche, quiz, cas pratiques, dissertations, commentaires, outils, procédures).

## Capabilities and Constraints

- Single self-contained `index.html` (HTML, CSS, JS) with JSON data files; no build step, no framework.
- Must work at phone width and on desktop, in light and dark themes.
- Content is legal and must stay accurate: wording of rules, article numbers and decision references are not to be changed for design reasons.
- Shared features that relied on artifact capabilities (sharing partiels and cases, exercise generation) are hidden outside claude.ai.
- Undecided: whether users can add their own document models (templates/actes), and if so whether they stay private or are shared.

## Brand Commitments

- The library metaphor is binding: floors (years), a shelf of subjects shown as book spines, and opening a volume.
- The name "Droit au But", the teal and navy palette and the current typography are not binding and may evolve.

## Evidence on Hand

- 86 subject sheets, quizzes, case studies, essays and commentaries with model answers, in `index.html`.
- 22 legal codes in `codes/`, case law from the Cour de cassation, Conseil d'État and administrative courts of appeal in `juris/`.
- No testimonials, user numbers, endorsements or institutional partnerships exist; do not invent any.

## Product Principles

1. Accuracy before appearance: every rule points to its text or decision, and the disclaimer about verifying on Légifrance and Judilibre stays.
2. Depth on demand: the short answer comes first, the detail is one step away, never forced.
3. Students and practitioners are equal citizens: neither audience's path is buried behind the other's.
4. Fast to find, comfortable to stay: quick lookup and long reading sessions are both first-class.
5. Works offline from paper too: exports must remain faithful and complete.

## Accessibility & Inclusion

Long reading sessions and phone use make legibility a core need: WCAG AA contrast in both themes, comfortable line length and line height, no motion that competes with reading (respect `prefers-reduced-motion`).
