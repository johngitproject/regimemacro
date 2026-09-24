# Régime macro-taux → filtre directionnel ES/NQ

## 1. Objectif

Transformer la chaîne causale **taux ← anticipations inflation/chômage ← seuils Fed + forward
guidance** en données mesurables, prouver qu'elle suit les grandes tendances ES/NQ, et finir en
**filtre directionnel des résultats backtestés** : dire chaque jour si on est short ou long, et
supprimer du backtest les trades pris contre le biais (mode exclusion + rapport avant/après).

Ce n'est pas un signal autonome. C'est un filtre de conviction et de sens.

## 2. Chaîne causale → données

| Étage | Fichier | Contenu |
|---|---|---|
| Surprises macro | `donnees/regime/calendar_macro_2022_2026.csv` (352 lignes) | CPI/PCE headline+core, NFP, chômage, taux Fed — previous/forecast/actual/surprise/direction, jan-22 → jan-26 |
| Seuils Fed | `donnees/regime/fed_thresholds.csv` (430 lignes, 20 SEP déc-21→sep-26) + `fed_dots.csv` (103 horizons) | $r^*$ (2,4→3,1 %), $u^*$ (4,0→4,2 %), $\pi^*$=2 %, médianes annuelles des dots (table officielle fait foi) |
| Forward guidance | `donnees/regime/fomc_guidance.csv` (33 statements, statut `draft_a_valider`) | Stance hawkish/neutre/dovish + citation + dissents (Bullard, George, Bowman, Hammack, Miran…) — **validation humaine requise** |
| Pricing marché | `donnees/regime/sources/market_pricing_daily.csv` (1441 j) | ZQ=F (futures Fed funds), T-bill 3M, 5Y, 10Y, EFFR (Yahoo + NY Fed, sans clé) |
| Stance | `donnees/regime/fed_stance.csv` (332 events) | Target prevailing, gaps vs seuils, Taylor, stance réelle, dots année en cours, guidance, pricing veille — anti-lookahead strict |

Stance réelle : `real_gap = (target_mid − πe_SEP) − (r* − 2)`, avec $\pi_e$ = médiane SEP PCE
année en cours. Taylor contemporain en référence : `r* + π + 0,5·(π−2) + (u*−u)`
(montre le retard/avance vs la règle, ex : prescription ~9 % mi-2022 = *behind the curve*).

Requêtes : `scripts/query_macro.py` — `direction`, `surprise`, `trend`, `recap`, `next`,
`stance`, `repricing`, `filtre`, `news --date X [--event CPI|PCE|NFP|UNEMP|FED]` (plan de trade :
attente + drifts 20j/5j/1j + stance + scénarios hot/cool/inline taillés par la matrice +
précédents mesurés + réalisé si publié).

## 3. Lexique : R, A, et les configs

- **R = restrictif** : taux au-dessus du neutre (real gap > +25 bp). 2023-2025.
- **A = accommodant** : taux en dessous du neutre. Sur 2022-2025 cela veut dire **Fed en retard
  sur la courbe** (target 0,25-1,75 % quand Taylor prescrit ~9 %), pas « soutien au marché ».
- **N = neutre** (|real gap| ≤ 25 bp). Échantillon mince (75 j).
- **/down / /flat / /up** : momentum du 10Y sur 60 séances (seuil ±50 bp). Le 10Y devance le
  directeur : la lettre dit le régime de fond, le suffixe dit si le marché y croit et où il va.

**Avertissement central** : les labels sont des **marqueurs d'époque** (A = bear 2022, R = bull
2023-25), pas des ordres d'achat/vente. Le hit rate ci-dessous = part de fenêtres forward
positives, **pas un taux de bonnes prédictions**. « Restrictif → acheter » serait naïf et
dangereux hors-échantillon (un easing-cycle récessif inverserait le tableau).

## 4. Résultats : le régime suit les tendances (1960 jours, ES+NQ, forwards 5/20/60j RTH)

| Stance | ES 60j | NQ 60j |
|---|---|---|
| R (N≈675) | +4,86 % hit 84 % | +6,90 % hit 83 % |
| A (N≈230) | −1,84 % hit 46 % | −2,60 % hit 40 % |
| Baseline | +3,03 % hit 75 % | +4,24 % hit 71 % |

Le 10Y discrimine **dans** le régime :

| Config | ES 60j | NQ 60j | Lecture |
|---|---|---|---|
| **R/down** (soft landing) | **+7,20 % hit 99 %** (N=80) | **+8,84 % hit 95 %** | Restrictif + 10Y qui baisse : désinflation, pivot anticipé (fin 2023, été 2024) |
| R/flat | +5,15 % hit 89 % | +7,43 % hit 86 % | Plateau qui tient |
| R/up (tension late-cycle) | +2,02 % hit 56 % | +3,38 % hit 60 % | Restrictif + 10Y qui monte : positif mais faible |
| A/flat (bear qui saigne) | méd −2,76 % hit 30 % | méd −5,52 % hit 26 % | Pire à 60j |
| A/up | −0,99 % hit 60 %* | −1,57 % hit 52 %* | Pire en court terme : NQ 20j −2,36 % hit 40 % |
| A/down | — | — | Jamais observé 2022-25 |

\* Moyennes A/up 60j faussées par des rebonds violents (médianes ES +2,11 / NQ +0,38).

Limites : un seul cycle observé ; forwards chevauchants (lire N, médiane, hit rate, pas les
t-stats) ; baseline gonflée par le drift 2023-25.

## 5. Biais LONG / SHORT par config (cœur opérationnel)

| Config | Biais | Règle d'exclusion sur `trades.csv` |
|---|---|---|
| R/down | **LONG** | Supprimer les shorts (sauf fade documenté) |
| R/flat | Long prudent | Supprimer les shorts |
| R/up | **NEUTRE tendu** | Garder les deux (tension late-cycle, pas de sens imposé) |
| N/* | **NEUTRE** | Garder les deux |
| A/down | Neutre prudent | Garder les deux (jamais observé : pas de règle) |
| A/up | **SHORT** | Supprimer les longs (**VETO**) |
| A/flat | Short prudent | Supprimer les longs |
| **Actuel (jan-26, N/flat)** | **NEUTRE** | Garder les deux, taille réduite des deux côtés |

Tailles associées (filtre live) : R/down long 1,0 / short 0,25 ; R/up 0,5/0,5 ; R/flat 0,75/0,5 ;
N/* 0,5/0,5 ; A/up long 0,0 VETO / short 1,0 ; A/flat long 0,25 / short 0,75.

## 6. Protocole d'application aux backtests

Script : `scripts/apply_regime_filter.py` (détails §8).

1. **Jointure** : chaque trade (`market,date,dir` avec dir=±1) reçoit la config du jour —
   **config de la veille** (dernier event strictement avant le jour du trade), jamais celle du
   jour même : un CPI 8h30 ne doit pas filtrer un trade 8h31 (anti-lookahead).
2. **Exclusion** : tout trade dont le sens contredit le biais du §5 est marqué `exclu`
   (VETO A/up-long, shorts en R/down et R/flat, longs en A/up et A/flat) ; le reste est `gardé`.
3. **Rapport avant/après** par fichier `trades*.csv` : N trades, winrate, profit factor,
   expectancy, P&L net — global + par config + comparatif gardés vs exclus (les exclus doivent
   sous-performer, sinon la règle est mauvaise).
4. Applicable en boucle : VP02, S1-S5, v04, swings… — même règle, même rapport, comparaison
   des stratégies entre elles **après** filtre (terrain neutre). Premiers résultats :
   voir `bilan/FILTRE_BACKTESTS.md` (VP02 PF 1,18→1,27 ; swingS1 PF 1,43→2,05 ; mgi_q1 PF
   0,80→0,99 ; v03-paris dégradé 0,54→0,41 — le filtre n'est pas universel, il se valide
   par stratégie).

## 7. Épisodes 2022-2025 (ce que chaque cas enseigne)

- **Liftoff + été 2022 (A/up)** : hikes +25→+75, CPI 9,1 %, 10Y 1,6→4,2. Shorts pleins, longs VETO.
  Deux surprises de décision sur tout le cycle : +75 au lieu de +50 en juin-22, −50 au lieu
  de −25 en sep-24 — les deux jours au repricing violent.
- **Pivot déc-2023 (naissance R/down)** : hold 5,5 % mais dots 2024 5,1→4,6 ; 10Y −97 bp sans
  geste. Les taux qui comptent bougent avant le directeur.
- **2024, *hawkish cuts*** : −100 bp de directeur et 10Y **+93 bp**. Un cut ne se trade pas comme
  un signal dovish pur (seul nov-24, cut « propre », a 10Y et ES dans le bon sens).
- **2025, choc tarifs (cas 3 textbook)** : π et u attendus en hausse ensemble → 7 holds, guidance
  floue volontaire (« extent and timing »), dissidents bilatéraux ; puis easing **contraint par
  le chômage** (4,3→4,6 %), pas par l'inflation (~2,8 %). Stance R→N en décembre.
- **Règle des 20 jours avant les chiffres** (`pre_drift_20j.csv`, 318 releases) : le marché dérive
  le plus souvent en mode dovish avant le print ; les surprises paient quand elles vont CONTRE
  la dérive (reversal juil-22 −1,2 %, explosion nov-22 +2,9 %), avec une amplitude fonction de la
  stance (−0,3 % seulement pour le même setup en régime R, fév-25). En amplitude pure, AVEC
  la dérive bouge légèrement plus (continuations) — l'analyse du signe reste à faire.

## 8. Scripts et fichiers (carte)

- `scripts/build_calendar_macro.py` → `calendar_macro_2022_2026.csv` (+ `sources/` : snapshots,
  `SOURCES.md` = bible des sources, trous et flags ouverts).
- `scripts/fetch_sep_tables.py`, `fetch_fomc_statements.py`, `fetch_market_pricing.py`,
  `build_fed_thresholds.py`, `code_guidance.py`, `build_fed_layer.py` → seuils, dots, guidance,
  pricing, `fed_stance.csv`.
- `scripts/build_index_daily.py` (+ `patch_index_yahoo.py`, QC saut de base, colonne `source`) →
  `index_daily.csv` (2229 lignes ES+NQ 2022 → avr-26 ; 3 fenêtres refusées : sep-24 ES+NQ avec
  FOMC 18 sep, mar-22 NQ avec FOMC 16 mar ; conflit ouvert 11-sep-24 ; week-ends exclus).
- `scripts/join_stance_index.py` → `stance_index_fwd.csv` + `stance_index_report.md`.
- `scripts/build_predrift.py` → `pre_drift_20j.csv` + `pre_drift_report.md`.
- `scripts/build_predrift_change.py` → `pre_drift_change.csv` (126 events avec changement
  attendu, seuils CPI/PCE 0.2, NFP 20K, UNEMP 0.1, FED 0.25) + `pre_drift_change_report.md`
  (drifts 20j/5j/1j, concordance, corrélations drift×surprise, amplitude jour J).
- `scripts/regime_filter.py` + `query_macro.py filtre` → conviction live par date et par sens.
- `scripts/build_conditional_regime.py` → `conditional_regime.csv` (48 rapports emploi :
  paires u×pi as-of, quadrant, régime, surprise, forwards + 10Y) + rapport : uH poolé haussier
  mais par composition 2023 ; par quadrant, même signal uH, trois destins (nov-22 +6,68 % 20j
  fin des hikes ; déc-24 −1,28 % avec 10Y +53 bp en dilemme stagflation ; déc-25 chop).
- `scripts/apply_regime_filter.py` → exclusion des trades contre-biais + rapport avant/après
  (voir §6).

## 9. Reste à faire

1. ~~Validation humaine des 33 lignes `fomc_guidance.csv`~~ — faite le 2026-09-24
   (relue sans correction, statuts `valide_2026-09-24`, SHA256SUMS re-signé).
2. Ré-exports NT8 ciblés (~15 séances : 10-17 mar 2022 NQ, 12-23 sep 2024 ES+NQ).
3. Test « surprises × config alignée » sur les trades news. Fait partiellement :
   `pre_drift_change.csv` (126 events avec changement attendu) montre que le **FOMC est le
   seul event proprement pré-pricé** (hausse attendue : ES 20j −0,53 %, 10Y +16 bp ; baisse :
   ES +2,18 %, 10Y −9,5 bp ; concordance 64 %), CPI/PCE ≈ pile ou face, NFP inversé par
   confusion d'époque. Reste : le signe du move jour J (reversal vs continuation).
4. Walk-forward sur les transitions R/up → R/down (le versant anticipation).
5. Recalibrage périodique des seuils (50 bp momentum, seuils surprise) et de la matrice de taille.
