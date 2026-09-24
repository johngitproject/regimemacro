# Backtest REGIME SWING — ES+NQ daily, walk-forward 2022-2025

## Design testé

- **Couche 1 (biais de fond)** : R/down long 1,0 · R/flat long 0,75 · R/up FLAT · N/* long 0,5 ·
  A/down FLAT · A/flat short 0,5 · A/up short 1,0 (NQ ÷ 1,4). Rebalance au close RTH sur
  changement de config.
- **Couche 2 (tactique events)** : blackout nouvelles entrées 2 séances avant CPI/FOMC ;
  renfort +0,5 (cap 1,5) sur surprise alignée, expire J+20 ; sortie d'urgence au close suivant
  sur surprise contre ≥ seuil, ré-entrée seulement sur nouvelle config.
- Sorties : flip/neutralisation, stop temporel 60 séances/lot, stop technique −3 %/lot.
  Kill-switch : A + tendance 60j positive 40 séances → FLAT forcé (déclenché 16 j, déc-25).
- **Coûts** : ES $15 / NQ $7,50 par transaction et par contrat (1 tick spread+slip + $2,50
  commission). Notionnel $100k (CAGR indicative). Script : `scripts/backtest_regime_swing.py`.

## Résultats (coûts inclus)

| Version | Total | CAGR | Sharpe | maxDD | PF | WR | Trades |
|---|---|---|---|---|---|---|---|
| FULL (couches 1+2) | +95 k$ | +16,5 % | 0,37 | **−133 k$** | 1,17 | 54 % | 123 |
| CONFIG (couche 1 seule) | +357 k$ | +41,6 % | 1,12 | −108 k$ | 2,18 | 53 % | 93 |
| B&H ES 1 contrat | +131 k$ | +21,2 % | 0,70 | −62 k$ | — | — | 1 |

Walk-forward (FULL) : IS 22-23 PF 2,01 · OOS 24-25 **PF 1,13**. (CONFIG : IS 2,31 · OOS **2,59**.)
Par année (FULL / CONFIG en PF) : 2022 : 0,79 / 1,24 · 2023 : 4,58 / 16,42 · 2024 : 2,38 / 5,48 ·
2025 : 0,60 / 1,59. CONFIG positive les 4 ans, FULL négative en 2022 et 2025.
Sensibilités (FULL) : mom30 PF 1,28 · mom70 PF 1,39 · **sans jours bridges PF 1,49**
(vs 1,17 : le patch Yahoo ajoute du bruit d'entrée, comme anticipé).

## Diagnostic : pourquoi la couche 2 détruit de la valeur

Compteurs FULL : 51 sorties d'urgence, 42 renforts, 151 séances de blackout,
**567 séances bloquées en ré-entrée** (sur ~1050). Le seuil « toute surprise non-inline »
déclenche trop souvent, et le blocage « jusqu'à nouvelle config » fige le système des
semaines (les flips de biais sont rares : 3-4 sur la période). Résultat : expo 45 % vs 85 %,
tendances 2023 et 2025 manquées en partie, whipsaw sur les exits.

## Verdict vs critères (PF OOS > 1,3 ET maxDD < 50 % du B&H)

- **FULL : REFUSÉ** (OOS 1,13 < 1,3 ; DD −133 k$). La couche 2 telle que spécifiée est rejetée
  par les données — ce qui est aussi un résultat : la tactique events systématique nuit.
- **CONFIG : AJOURNÉ** (PF 2,18 full / 2,31 IS / 2,59 OOS, 4/4 ans positifs — mais DD −108 k$,
  dont le krach d'avril-25 en pleine exposition longue ; le stop −3 %/lot ne contient ni les
  gaps ni les ré-entrées en boucle).
- **Recommandations structurelles (pas d'overfit)** : abandonner la couche 2 en l'état ;
  ajouter du **vol targeting** (taille inverse à la vol réalisée) ; urgences seulement sur
  grosses surprises (|mag| ≥ 2-3) avec reblocage borné (ex : 5 séances, pas « nouvelle config ») ;
  re-tester. Ne PAS tuner les seuils mom/taille sur cet échantillon (un seul cycle macro).

## V2 : CONFIG + vol targeting + urgences restreintes (|mag| ≥ 2, reblocage 5 j)

| Version | Total | Sharpe | maxDD | PF (full / IS / OOS) |
|---|---|---|---|---|
| V2 (vol 1 %/j) | +267 k$ | 0,90 | −129 k$ | 1,67 / 2,71 / **1,46** |
| V2 vol 0,75 % | +244 k$ | 0,96 | −110 k$ | 1,79 |
| V2 vol 1,5 % | +284 k$ | 0,85 | −143 k$ | 1,61 |
| V2 mag≥3 (urgences extrêmes seules) | +334 k$ | 1,06 | −120 k$ | 1,92 |
| CONFIG v1 (rappel) | +357 k$ | 1,12 | −108 k$ | 2,18 / 2,31 / 2,59 |

- Le critère PF OOS passe désormais (1,46 > 1,3), stable sur les variantes (1,61-1,92) :
  pas un optimum en lame de couteau. Le reblocage borné supprime le gel (94 j bloqués
  vs 567 en v1) et les urgences ne se déclenchent que sur vraies surprises.
- Le critère maxDD **échoue toujours** (−129 k$ vs B&H −62 k$) : le vol targeting atténue
  dans le bon sens (−143 k$ → −110 k$ quand la cible baisse) mais ne contient pas les gaps
  overnight (krach avr-25 en pleine exposition longue). Baisser le levier jusqu'à passer le
  critère serait circulaire, pas une validation.
- **Verdict V2 : AJOURNÉ aussi.** L'edge est confirmé côté sélection de tendance (PF stables
  IS/OOS sur toutes les variantes), le chantier restant est purement risque : vol targeting
  plus réactif (vol courte, floor overnight), voire exposition réduite la veille des events
  à gap historique — à tester comme V3, sans toucher aux règles de sens.
