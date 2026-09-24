"""Backtest Markov-switching — réaction de NQ aux surprises macro (CPI).

Méthodologie : proche de Davig & Gerlach, "State-Dependent Stock Market
Reactions to Monetary Policy" (SSRN 882151). Modèle à 2 régimes cachés qui
identifie lui-même les périodes où la réaction du marché à une surprise
donnée est cohérente ("régime réactif") vs bruitée ("régime bruité").

Usage :
    python3 backtest_regime_markov.py --csv tes_donnees.csv --seuil 0.7

CSV attendu (colonnes) :
    date, event_type, consensus, actual, market_implied, surprise,
    reaction_nq, reaction_rate

Logique :
  1. Split chronologique in-sample / out-of-sample (jamais de shuffle).
  2. Markov à 2 régimes sur l'in-sample uniquement
     (statsmodels MarkovRegression, k_regimes=2, switching_variance=True).
  3. Filtre de Hamilton (probabilités FILTREES, pas lissées) sur toute la
     série avec les paramètres figés de l'in-sample -> proba en t n'utilise
     que l'info disponible jusqu'à t (aucun lookahead).
  4. Règle de trading : en t, on utilise la proba de régime réactif connue
     en t-1 ; si elle dépasse le seuil, on trade dans le sens prédit par
     beta_reactif * surprise.
  5. 3 courbes de PnL cumulé : sans filtre (baseline) / réactif uniquement /
     bruité uniquement (contrôle).

Garde-fous :
  - Le régime "réactif" = celui avec le |beta| sur `surprise` le plus grand.
  - Échantillon minimum requis pour estimer (défaut 30 obs in-sample) :
    en dessous, le script s'arrête avec un message clair au lieu de
    produire des chiffres instables. NFP+CPI mensuels => plusieurs années
    d'historique nécessaires (cf. limites du brief).
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd


def parse_args():
    p = argparse.ArgumentParser(description="Backtest Markov-switching régime CPI->NQ")
    p.add_argument("--csv", required=True, help="CSV d'entrée (cf. colonnes attendues)")
    p.add_argument("--seuil", type=float, default=0.7,
                   help="Seuil de proba filtrée du régime réactif en t-1 (défaut 0.7)")
    p.add_argument("--split", type=float, default=0.7,
                   help="Part in-sample chronologique (défaut 0.7)")
    p.add_argument("--surprise-col", default="surprise")
    p.add_argument("--reaction-col", default="reaction_nq")
    p.add_argument("--min-in-sample", type=int, default=30,
                   help="Obs in-sample minimales pour estimer (défaut 30)")
    p.add_argument("--out", default=None, help="Préfixe de sortie (PNG + CSV PnL)")
    return p.parse_args()


def main():
    args = parse_args()
    df = pd.read_csv(args.csv, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    for c in (args.surprise_col, args.reaction_col):
        if c not in df.columns:
            sys.exit(f"ERREUR: colonne '{c}' absente de {args.csv} "
                     f"(colonnes: {list(df.columns)})")
    df = df.dropna(subset=[args.surprise_col, args.reaction_col]).reset_index(drop=True)
    n = len(df)
    if n < 10:
        sys.exit(f"ERREUR: {n} observations exploitables — insuffisant même pour un smoke test.")
    n_in = int(n * args.split)
    if n_in < args.min_in_sample:
        sys.exit(
            f"ARRET PROPRE: in-sample={n_in} obs < minimum {args.min_in_sample}. "
            f"Le modèle à 2 régimes a besoin de plusieurs dizaines d'observations par régime "
            f"(NFP/CPI mensuels => plusieurs années). Total actuel: {n} obs. "
            f"Relancez avec --min-in-sample plus bas pour forcer un smoke test (résultat non interprétable)."
        )

    try:
        from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
    except ImportError:
        sys.exit("ERREUR: statsmodels manquant (pip install statsmodels)")

    endog_in = df.loc[:n_in - 1, args.reaction_col].to_numpy(float)
    exog_in = df.loc[:n_in - 1, [args.surprise_col]].to_numpy(float)
    endog_all = df[args.reaction_col].to_numpy(float)
    exog_all = df[[args.surprise_col]].to_numpy(float)

    # 2. Estimation in-sample
    try:
        mod_in = MarkovRegression(endog_in, k_regimes=2, trend="c",
                                  exog=exog_in, switching_variance=True)
        res_in = mod_in.fit(disp=False, maxiter=1000)
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ERREUR: non-convergence du modèle in-sample ({e}). "
                 f"Élargissez l'historique, ne forcez pas l'interprétation.")

    # 3. Régime réactif = |beta_surprise| max ; filtre de Hamilton figé sur toute la série
    # Noms de paramètres portés par le MODÈLE (ex: 'x1[0]', 'x1[1]' avec trend='c', 1 exogène)
    params = np.asarray(res_in.params)
    names = list(mod_in.param_names)
    betas = {}
    for j, nm in enumerate(names):
        if nm.startswith("x1["):
            reg = int(nm[nm.index("[") + 1:nm.index("]")])
            betas[reg] = params[j]
    if len(betas) < 2:
        sys.exit(f"ERREUR: impossible d'identifier les betas surprise (params={names})")
    reactive = max(betas, key=lambda r: abs(betas[r]))
    beta_r = betas[reactive]
    print(f"in-sample: n={n_in} | beta_reg0={betas[0]:+.4f} beta_reg1={betas[1]:+.4f} "
          f"-> régime réactif={reactive} (beta={beta_r:+.4f})")

    mod_all = MarkovRegression(endog_all, k_regimes=2, trend="c",
                               exog=exog_all, switching_variance=True)
    try:
        res_all = mod_all.filter(res_in.params)  # params figés : aucun lookahead
        filt = np.asarray(res_all.filtered_marginal_probabilities)[:, reactive]
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ERREUR: filtre de Hamilton ({e})")

    # 4. Signaux (proba t-1) et PnL
    surprise = df[args.surprise_col].to_numpy(float)
    reaction = df[args.reaction_col].to_numpy(float)
    signal_dir = np.sign(beta_r * surprise)
    proba_prev = np.concatenate([[np.nan], filt[:-1]])
    take_reactive = proba_prev > args.seuil
    take_noisy = ~take_reactive

    pnl_base = signal_dir * reaction
    pnl_react = np.where(take_reactive, signal_dir * reaction, 0.0)
    pnl_noisy = np.where(take_noisy & ~np.isnan(proba_prev), signal_dir * reaction, 0.0)

    out = pd.DataFrame({
        "date": df["date"], "surprise": surprise, "reaction": reaction,
        "p_reactive_t-1": proba_prev,
        "pnl_baseline": np.cumsum(pnl_base),
        "pnl_reactif": np.cumsum(pnl_react),
        "pnl_bruite": np.cumsum(pnl_noisy),
    })
    n_tr_react = int(np.nansum(take_reactive))
    n_tr_noisy = int(np.nansum(take_noisy[1:]))
    win_react = float(np.mean((signal_dir * reaction > 0)[1:][take_reactive[1:]])) if n_tr_react else float("nan")
    print(f"out-of-sample: n={n - n_in} | seuil={args.seuil}")
    print(f"  trades réactif: {n_tr_react} (winrate {win_react:.1%}) | "
          f"trades bruité: {n_tr_noisy}")
    print(f"  PnL final baseline={out['pnl_baseline'].iloc[-1]:+.2f} "
          f"réactif={out['pnl_reactif'].iloc[-1]:+.2f} bruité={out['pnl_bruite'].iloc[-1]:+.2f} "
          f"(unités de {args.reaction_col})")

    prefix = args.out or os.path.splitext(args.csv)[0] + "_markov"
    out.to_csv(prefix + "_pnl.csv", index=False)
    print(f"écrit {prefix}_pnl.csv")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(out["date"], out["pnl_baseline"], label="baseline (sans filtre)")
        ax.plot(out["date"], out["pnl_reactif"], label=f"régime réactif (seuil {args.seuil})")
        ax.plot(out["date"], out["pnl_bruite"], label="régime bruité (contrôle)")
        ax.axvline(df["date"].iloc[n_in - 1], color="k", ls="--", lw=1, label="fin in-sample")
        ax.set_title("PnL cumulé — filtre Markov-switching")
        ax.legend()
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(prefix + "_pnl.png", dpi=120)
        print(f"écrit {prefix}_pnl.png")
    except Exception as e:  # noqa: BLE001
        print(f"figure non générée ({e})")


if __name__ == "__main__":
    main()
