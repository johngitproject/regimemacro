# Régime macro-taux ES/NQ — point d'entrée

**Question** : la chaîne taux ← anticipations inflation/chômage ← seuils Fed + forward guidance
peut-elle suivre les grandes tendances ES/NQ et filtrer des setups ? **Réponse mesurée : oui
comme filtre de conviction/taille (biais + sizing), non comme signal autonome.**
Détail : `../../bilan/ARTICLE_REGIME.md`, labo : `../../bilan/REGIME_MACRO.md`.

## Carte

- **Données brutes** (`sources/`) : voir `SOURCES.md` (origine, trous, flags) et `LICENCES.md`
  (quoi publier / quoi re-télécharger — Yahoo et consensus Investing : scripts, jamais les fichiers).
- **Données construites** (`*.csv` à la racine) : calendrier macro, seuils SEP, dots, guidance,
  stance, index continu, forwards, dérives pré-news, paires conditionnelles.
- **Code** (`../../scripts/`) : `fetch_*` (téléchargement), `build_*` (construction),
  `query_macro.py` (interrogation), `regime_filter.py` (conviction),
  `apply_regime_filter.py` (filtre backtests), `backtest_regime_swing.py` (walk-forward).
- **Résultats** (`*.md`, `../../bilan/`) : rapports par analyse + bilans + article.

## Reconstruction complète (venv du projet, dans l'ordre)

```bash
.\venv\Scripts\python.exe scripts/fetch_sep_tables.py
.\venv\Scripts\python.exe scripts/fetch_fomc_statements.py
.\venv\Scripts\python.exe scripts/fetch_market_pricing.py
.\venv\Scripts\python.exe scripts/fetch_yahoo_index.py
.\venv\Scripts\python.exe scripts/build_calendar_macro.py
.\venv\Scripts\python.exe scripts/build_fed_thresholds.py
.\venv\Scripts\python.exe scripts/code_guidance.py        # draft -> validation humaine requise !
.\venv\Scripts\python.exe scripts/build_fed_layer.py
.\venv\Scripts\python.exe scripts/build_index_daily.py
.\venv\Scripts\python.exe scripts/patch_index_yahoo.py
.\venv\Scripts\python.exe scripts/join_stance_index.py
.\venv\Scripts\python.exe scripts/build_predrift.py
.\venv\Scripts\python.exe scripts/build_predrift_change.py
.\venv\Scripts\python.exe scripts/build_conditional_regime.py
.\venv\Scripts\python.exe scripts/sign_release.py
```

## Usage quotidien

```bash
.\venv\Scripts\python.exe scripts/query_macro.py filtre --date 2026-01-28 --sens long
.\venv\Scripts\python.exe scripts/query_macro.py news --date 2026-01-28
.\venv\Scripts\python.exe scripts/query_macro.py stance --date 2026-01-28
.\venv\Scripts\python.exe scripts/apply_regime_filter.py "donnees\backtest\vp02\trades.csv" --report bilan\FILTRE_BACKTESTS.md
```

## Fraîcheur (quoi re-fetcher, quand, point de rupture)

| Donnée | Fréquence | Commande | Rupture connue |
|---|---|---|---|
| Statements/tables SEP, dots palewire | Après chaque FOMC/SEP | `fetch_fomc_statements.py`, `fetch_sep_tables.py`, re-vendor dotplot | — |
| Pricing (Yahoo, NY Fed EFFR) | Hebdo | `fetch_market_pricing.py`, `fetch_yahoo_index.py` | Yahoo : trous fériés, rolls mensuels |
| Consensus previous/forecast | **BLOQUÉ** : dépend du snapshot tiers (Investing via repo open-data) — au-delà de sa couverture, plus de forecasts sans re-scrape à construire | — | **C'est le point de rupture du pipeline** |
| Actuals FRED/BLS | Mensuel | `fred-us-macro-history.json` (re-vendor) ou BLS/FRED direct | Révisions (previous vs révisé tracé en `note`) |
| Index NT8 | Par contrat | Exports `donnees/market/` + `build_index_daily.py` + `patch_index_yahoo.py` | — |

Après toute mise à jour : rebuild dans l'ordre + `sign_release.py` + date dans `SHA256SUMS.txt`.
