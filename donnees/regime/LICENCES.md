# Licences et statut de publication des données

Principe : on publie le **code + la méthode + les résultats agrégés**, jamais les bruts
sous CGU restrictives. Tout fichier exclu est reconstructible en une commande
(`scripts/fetch_*.py`, voir `README.md`). Vérifié le 2026-09-24.

| Source | Fichiers | Statut | Base |
|---|---|---|---|
| Code du projet (`scripts/`, requêtes) | — | **À licencier (MIT recommandé)** | Décision auteur en attente |
| Federal Reserve (statements, tables SEP) | `sources/fomc_statements/`, `sources/sep_tables/` | **Publiable** (domaine public US) | federalreserve.gov |
| BLS (index CPI SA) | `sources/bls_cpi_sa_2021_2026.json` | **Publiable** (données publiques US, sans clé) | api.bls.gov |
| NY Fed (EFFR, via API sans clé) | reconstruit dans `market_pricing_daily.csv` | **Publiable à la source**, re-fetch uniquement | markets.newyorkfed.org |
| palewire/fed-dot-plot-scraper | `sources/dotplot.csv` | **Publiable avec attribution** | MIT + source Fed (github.com/palewire/fed-dot-plot-scraper) |
| FRED (séries DGS/VIX/SPX/T5YIE…) | `fred_*.csv` | **Publiable avec attribution** | « Source: FRED, Federal Reserve Bank of St. Louis » ; CGU : fred.stlouisfed.org/legal/terms/ |
| superpilot69/fred-us-macro-open-data (code + annotations) | — (non vendored) | **Publiable** (licence repo : usage public du code) | github.com/superpilot69/fred-us-macro-open-data |
| Idem, snapshot Investing (previous/forecast/actual) | `investing-us-macro-consensus.json`, `calendar_macro_2022_2026.csv` + toute la chaîne dérivée | **EXCLU (.gitignore)** — faits publics retraités par nos soins, mais CGU Investing d'origine restrictives (collecte systématique interdite) ; provenance tracée, usage recherche | investing.com (via snapshot tiers) |
| Yahoo Finance (ZQ, IRX, FVX, TNX, ES=F, NQ=F) | `market_pricing_daily.csv`, `yahoo_index_daily.csv`, closes `yahoo_bridge` dans `index_daily.csv` | **EXCLU (.gitignore)** — ToS : collecte automatisée et redistribution interdites sans autorisation (legal.yahoo.com, help « Do not redistribute ») ; scripts de fetch publiés, pas les données | finance.yahoo.com |
| Exports NinjaTrader personnels | `donnees/market/`, `donnees/backtest*/`, `backtest_out/`, `*_regime.csv` associés | **EXCLU (.gitignore)** — données personnelles de trading ; à l'auteur de décider | — |
| Nos analytics agrégés (rapports, bilans, matrices, stats) | `bilan/`, `*_report.md`, `SHA256SUMS.txt` | **Publiables** (œuvre propre ; chiffres agrégés, pas de lignes brutes tierces) | — |

Notes :
- Les rapports `.md` publiés ne contiennent que des statistiques agrégées et des épisodes
  ponctuels (valeurs publiques de releases macro), jamais de dumps de séries tierces.
- `SHA256SUMS.txt` fige l'empreinte des datasets testés le 2026-09-24 (traçabilité, pas redistribution).
- Journalier/paper/recap/cours : données de travail personnelles, exclues par défaut.
- Si un ayant-droit demande un retrait, le design le permet en une ligne de `.gitignore`
  (fetch scripts inchangés).
