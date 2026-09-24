# Regime Macro — Taux, anticipations et grandes tendances ES/NQ

Recherche appliquée (jan-2022 → jan-2026) : la chaîne **taux ← anticipations
inflation/chômage ← seuils Fed + forward guidance** peut-elle suivre les grandes tendances
ES/NQ et filtrer des setups ? **Réponse mesurée : oui comme filtre de conviction/taille
(biais + sizing), non comme signal autonome.**

## Résultats en 30 secondes

- La stance Fed sépare les tendances : restrictif → ES 60j **+4,86 % (hit 84 %)** ;
  accommodant (*behind the curve*) → **−1,84 % (hit 46 %)**.
- Le 10Y discrimine dedans : R/down (soft landing) ES 60j **+7,20 % (hit 99 %)** ;
  R/up (tension late-cycle) +2,02 % (hit 56 %) ; A/up NQ 20j −2,36 % (VETO long).
- 31 décisions FOMC sur 33 exactement comme pricées ; hike/hold attendu → ES +0,5 %,
  10Y −4 bp ; cut attendu → 10Y +3 bp (les cuts ne font pas baisser le long).
- Filtre validé sur backtests : swingS1 PF 1,43 → **2,05** ; VP02 1,18 → 1,27 ;
  v03-paris 0,54 → 0,41 (le filtre nuit aux fadeurs — validation par stratégie obligatoire).
- Swing 100 % systématique : **refusé** (FULL OOS PF 1,13, DD −133 k$) / **ajourné**
  (biais seul OOS PF 2,59 mais DD −108 k$). L'edge est côté sélection, le chantier est risque.

## Entrer dans le projet

- **Comprendre** : [`bilan/ARTICLE_REGIME.md`](bilan/ARTICLE_REGIME.md) (question, méthode,
  résultats, limites) puis [`bilan/REGIME_MACRO.md`](bilan/REGIME_MACRO.md) (labo complet).
- **Utiliser** : [`donnees/regime/README.md`](donnees/regime/README.md) (rebuild, requêtes,
  fraîcheur) — ex : `python scripts/query_macro.py filtre --date 2026-01-28 --sens long`.
- **Données** : code + méthode + agrégés publics ; bruts Yahoo/Investing/NT8 re-téléchargeables,
  jamais redistribués (voir [`donnees/regime/LICENCES.md`](donnees/regime/LICENCES.md),
  empreintes : `donnees/regime/SHA256SUMS.txt`).

## État actuel (jan-26)

Stance **neutre** (real gap +23 bp), config N/flat → **x0,5 long / x0,5 short**.
Le modèle se tait quand il n'a rien à dire — c'est une fonction, pas un bug.

## Limites (lire avant usage)

Un seul cycle macro observé · petits N par case (N<5 = épisode, pas statistique) ·
labels = marqueurs d'époque, pas des signaux · guidance validée humainement le 2026-09-24 ·
3 fenêtres de données refusées au QC · consensus non-rafraîchissable sans nouveau scrape.

## Licence

MIT © 2026 johngitproject — voir [LICENSE](LICENSE).
