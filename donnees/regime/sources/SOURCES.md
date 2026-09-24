# Sources — régime macro 2022-2026

## Fichiers bruts (`sources/`)

| Fichier | Origine | Contenu | Licence / attribution |
|---|---|---|---|
| `fred-us-macro-history.json` (1,4 Mo) | https://github.com/superpilot69/fred-us-macro-open-data | Observations FRED brutes, 15 séries (niveaux mensuels/quotidiens) | Données FRED, Federal Reserve Bank of St. Louis. Citer : « Source: Original series owner via FRED » |
| `investing-us-macro-consensus.json` (3,1 Mo) | même repo (snapshot Investing.com Economic Calendar) | Occurrences avec `previous / forecast / actual` par release | Snapshot tiers (Investing.com) — usage recherche/backtest, vérifier les CGU d'origine avant redistribution publique |

Téléchargés le 2026-09-17. Pour régénérer : relancer le téléchargement depuis le repo ci-dessus
(`data/fred-us-macro-history.json`, `data/investing-us-macro-consensus.json`).

## Couverture réelle constatée (fenêtre jan 2022 → jan 2026)

| Série | Event | Variante | Releases | Avec forecast | Avec actual |
|---|---|---|---|---|---|
| CPIAUCNS | CPI | headline_yoy (%) | 48 | 48 | 48 |
| CPILFENS | CPI | core_yoy (%) | 48 | 48 | 48 |
| PCEPI | PCE | headline_yoy (%) | 48 | 36 | 48 |
| PCEPILFE | PCE | core_yoy (%) | 48 | 47 | 48 |
| PAYEMS | NFP | change_K (milliers) | 49 | 48 | 49 |
| UNRATE | UNEMP | rate (%) | 48 | 48 | 48 |
| DFEDTARU | FED | target_upper (%) | 33 meetings | 33 | 33 |

## Trous et cas particuliers (tous vérifiés, pas des bugs)

1. **CPI d'octobre 2025 absent** : shutdown fédéral US automne 2025 — le BLS a décalé le CPI de sept.
   au 24/10 puis sauté la publication d'octobre. La série saute de ref `2025-09` à `2025-11`.
2. **Doubles publications de rattrapage (shutdown)** : deux refs distinctes le même jour, conservées
   en lignes séparées —
   - NFP `2025-12-16 08:29` ref `2025-10` (actual **-105 K**, sans forecast) + `2025-12-16 08:30`
     ref `2025-11` (F 51 / A 64) ;
   - NFP `2025-11-20 08:30` ref `2025-09` (publication retardée) ;
   - PCE `2026-01-22` : ref `2025-10` à 09:59 (sans forecast) + ref `2025-11` à 10:00 (F 2.8 / A 2.8) ;
   - PCE `2025-12-05 10:00` ref `2025-09` (retardée).
3. **Chômage d'octobre 2025 absent** : le rapport partiel de déc. 2025 ne donne que le NFP (-105 K),
   pas le taux. UNEMP compte donc 48 lignes contre 49 pour NFP.
4. **PCE headline : 11 forecasts manquants** (10× 2022 + `2023-04`), couverture Investing partielle.
   PCE core : 1 seul manquant (`2026-01-22` ref `2025-10`, donnée de rattrapage).
5. **MoM** : le snapshot ne fournit que le YoY/levels. Seul le CPI headline 2025 a des MoM temps
   réel (`../calendar_cpi_2025.csv`, 10 lignes). **Aucun MoM recalculé** : les index SA/BEA révisés
   (ex : CPI déc. 2024 révisé de +0,4 à +0,04) ne reproduisent pas les prints temps réel —
   recalculer fabriquerait de faux « actual ». `bls_cpi_sa_2021_2026.json` est conservé pour
   d'éventuels travaux sur niveaux/tendances, pas pour les surprises.
6. `referencePeriod` du snapshot = mois de référence en chinois (十二月=déc. …) ; mappage explicite
   dans `build_calendar_macro.py` (`ZH_MONTH`). DFEDTARU n'a pas de ref (mois du meeting).
7. `previous` = valeur pré-release du snapshot (peut différer du FRED révisé) ;
   `previousRevisedFrom` conservé dans la colonne `note` quand présent.

## Étage Fed / taux (scripts `fetch_sep_tables.py`, `fetch_fomc_statements.py`,
## `fetch_market_pricing.py`, `build_fed_thresholds.py`, `code_guidance.py`, `build_fed_layer.py`)

| Fichier brut | Origine | Contenu |
|---|---|---|
| `sep_tables/fomcprojtable*.htm` (20) | federalreserve.gov `monetarypolicy/fomcprojtable\|tablYYYYMMDD.htm` (préfixe variable selon vintage) | Tables SEP déc-21 → sep-26 : médianes GDP/chômage/PCE/core PCE/Fed funds + longer-run. Le core PCE n'a PAS de longer-run (cellule vide officielle) |
| `fomc_statements/*_statement.htm` + `.txt` (33) | federalreserve.gov `newsevents/pressreleases/monetaryYYYYMMDDa.htm` | Statements 2022-01-26 → 2026-01-28. `*_body.txt` = corps nettoyé (relecture) |
| `dotplot.csv` | github.com/palewire/fed-dot-plot-scraper (`data/dotplot.csv`) | Dots individuels : `midpoint` = niveau, cellules = nb de participants par année. Médianes recalculées et confrontées aux tables SEP |
| `market_pricing_daily.csv` (1441 j) | Yahoo Finance v8 (`ZQ=F`, `^IRX`, `^FVX`, `^TNX`, 2021-12 → 2026-02) + NY Fed Markets API (`EFFR`) | Closes quotidiens. ZQ coté `100 - taux` (inversion faite côté requête) |
| `bls_cpi_sa_2021_2026.json` | api.bls.gov (sans clé) `CUUR0000SA0` + `CUUR0000SA0L1E` | Index CPI SA — NON utilisé pour les surprises (révisions saisonnières), conservé pour travaux sur niveaux |

Fichiers construits : `fed_thresholds.csv` (430 lignes, format long meeting/var/horizon),
`fed_dots.csv` (103 horizons : médiane/min/max/n), `fomc_guidance.csv` (33 lignes, **statut
`draft_a_valider` — validation humaine obligatoire**), `fed_stance.csv` (332 lignes/event :
target prevailing, r*/u*, gaps, Taylor, real_gap, dots année en cours, guidance, pricing veille).

Points connus :
- Dots vs table SEP : la table (publication officielle) fait foi ; écart > 1 cran = erreur sauf
  2026-09-16 LR (table 3.2 vs dots 3.25, arrondi Fed ou dot déplacé — noté, non bloquant).
- Stance = `(target_mid - pi_exp) - (r* - 2)` avec `pi_exp` = médiane SEP PCE année en cours
  (repli : dernier core PCE, flaggé `core_actual_repli`). Taylor contemporain gardé en référence
  (montre le retard/avance vs la règle, ex : prescription ~9 % mi-2022).
- ZQ=F continu (roll mensuel, petit bruit) ; EFFR tel quel NY Fed ; Yahoo peut ajuster l'historique.
- fred.stlouisfed.org direct (fredgraph.csv) injoignable depuis le sandbox (testé, retries OK
  pour les autres hôtes) → contourné par Fed direct + NY Fed + Yahoo + BLS, sans clé API.

## Backfill index Yahoo (scripts `fetch_yahoo_index.py`, `check_yahoo_align.py`, `patch_index_yahoo.py`)

- `yahoo_index_daily.csv` : closes daily continus `ES=F` / `NQ=F` (Yahoo v8, déc-21 → juin-26),
  dates = séances Yahoo (barres horodatées minuit ET). **Les closes Yahoo suivent la fin de
  journée (corr retours vs NT8-ETH 0.93-0.94), PAS le close RTH 15h00** (corr 0.50) :
  écart médian vs RTH 0.4-0.5 %, p95 ~2 %.
- Méthode : `index_daily.csv` gagne la colonne `source` (`nt8`|`yahoo_bridge`). Seuls les jours
  manquants NT8 sont bouchés, avec les closes Yahoo bruts (shape réelle) ; les marches aux
  ancres NT8 absorbent la base. Snapshot pré-patch : `index_daily_nt8_only.csv`.
- QC par fenêtre = **saut de base** Yahoo/NT8 entre les ancres (détecte un roll divergent) :
  > 2 % = fenêtre NON bouchée ; > 0.5 % = `qa=roll_suspect` (conservée, bornée par les ancres) ;
  jour à > 8 % = `qa=spike`. Queue déc-25 → avr-26 : `qa=tail_no_anchor` (dérive ~1 % possible).
- Refusés (restent manquants) : ES+NQ sep-24 (saut 2.6/3.7 %, FOMC 18 sep dedans) et NQ mar-22 (2.0 %,
  FOMC 16 mar) → seul un ré-export NT8 ciblé peut les combler.
- Flags ouverts : conflit NT8/Yahoo le 2024-09-11 (RTH 5424 vs Yahoo 5561, cause indéterminée —
  session CPI très volatile, arbitrage CME requis) ; lignes samedi/dimanche des exports
  (barres parasites, ex : 2023-09-17) **exclues** de `index_daily` (RTH inexistant le week-end).

## Dérive pré-news 20j (script `build_predrift.py`)

- `pre_drift_20j.csv` (318 releases avec surprise) : drifts ES/NQ (%) et 10Y (bp) sur 20 séances
  avant la veille, sens hawkish/dovish/inline (seuils CPI/PCE 0.1, UNEMP 0.1 inversé, NFP 30K,
  FED 0.1), dérive via tnx (bande plate ±15 bp), alignement AVEC/CONTRE/n.d., moves jour J
  (close J vs veille, RTH ; J manquant = vide, jamais interpolé — ex : FOMC 18 sep 2024).
- `pre_drift_report.md` : amplitude jour J par alignement. Résultat : AVEC légèrement plus ample
  que CONTRE (ES |J| méd 0.91 vs 0.67, NQ 1.10 vs 0.78, 10Y 6 vs 5 bp) — les surprises dans le
  sens de la dérive prolongent le move. L'analyse du SIGNE (reversal vs continuation) reste à faire.

## Dérive pré-news et changement attendu (script `build_predrift_change.py`)

- Filtre : |forecast − previous| ≥ seuil de matérialité (CPI/PCE 0.2 pt, NFP 20 K, UNEMP 0.1 pt,
  FED 0.25 pt), sinon exclu (bruit de consensus). 142 lignes, 126 events uniques.
- `pre_drift_change.csv` : drifts ES/NQ (%) et 10Y (bp) sur 20j/5j/1j avant la veille (sessions,
  jamais interpolés) + sens attendu + surprise + alignement AVEC/CONTRE + moves jour J.
- `pre_drift_change_report.md` : (1) drift moyen par sens attendu — le plus propre sur FED
  (hausse attendue : ES 20j méd −0.53 %, 10Y +16 bp ; baisse : ES +2.18 %, 10Y −9.5 bp ;
  concordance 64 %) ; CPI/PCE ≈ pile ou face (53-55 %) ; NFP inversé 25 % (confusion d'époque :
  les « baisse attendue » concentrent l'ère des hikes 2022 où le 10Y montait pour d'autres
  raisons). (2) corrélations drift×surprise faibles sauf FED tnx5j +0.55 (N=17) et NFP ES5j
  +0.35. (3) amplitude jour J : AVEC > CONTRE, comme sur l'échantillon complet.

## Lecture conditionnelle u×π×régime (script `build_conditional_regime.py`)

- `conditional_regime.csv` (48 rapports emploi) : jambe chômage (écart, sens H/B/S seuil 0.1)
  + jambe inflation = dernier écart CPI headline YoY connu AVANT le rapport (as-of strict,
  seuil 0.2) → quadrant uH/uB/uS × piH/piB/piS ; stance/side/phase Fed/guidance à la veille ;
  surprise (UNEMP inversée) ; forwards ES/NQ 5/20/60j depuis close RTH J (J manquant = vide)
  + 10Y 20/60j.
- `conditional_regime_report.md` : uH poolé (N=12) haussier — ES20 méd +3,40 vs +1,15,
  NQ20 +4,09 vs +0,55 — MAIS composition 2023 (soft-landing hope), pas une loi. Par quadrant :
  uH+piS/A nov-22 +6,68 % 20j (fin des hikes, creux d'octobre) vs uH+piH/R déc-24 −1,28 %
  avec 10Y +53 bp (dilemme stagflation en plein easing) vs uH+piH/A déc-25 chop (−1,42 % 60j).
  Même signal uH, trois destins selon pi et le régime : c'est exactement l'objet demandé.
- Toutes les cases quadrant×side à N<5 sont en lecture épisode uniquement.
- Bug trouvé et corrigé : soustractions flottantes aux seuils exacts (3.8−3.7=0.0999… < 0.1,
  classait jan-24 et déc-25 en « stable » à tort) → arrondi à 4 décimales partout.

## Règles

- `forecast` manquant = cellule vide, jamais 0.
- `actual` fait foi côté snapshot ; `ref_period` vient de `referencePeriod` (mois en chinois,
  mappé en MM + année déduite), vérifié par valeur FRED sur séries stables (CPI NSA, UNRATE)
  et par veille==previous sur FED.
- Heures converties UTC → America/New_York (règle DST US : 2e dimanche de mars → 1er dimanche de nov.).
