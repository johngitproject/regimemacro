# Filtre regime sur backtests

## trades.csv -> trades_regime.csv
- P&L utilise : `net_Conservateur-2ticks_$` | config = dernier event < jour du trade
- AVANT : N=797 WR=45% PF=1.18 exp=+52.99 ($) tot=+42235.00 ($)
- APRES (gardes) : N=528 WR=47% PF=1.27 exp=+74.49 ($) tot=+39331.25 ($)
- EXCLUS : N=269 WR=41% PF=1.03 exp=+10.79 ($) tot=+2903.75 ($)
- gardes: 528/797 (66%) | skipped parsing: {'date': 0, 'dir': 0, 'pnl': 0, 'inst': 0, 'sans_config': 0}

## trades.csv -> trades_regime.csv
- P&L utilise : `NetTicks` | config = dernier event < jour du trade
- AVANT : N=88 WR=41% PF=0.80 exp=-7.75 (ticks) tot=-682.00 (ticks)
- APRES (gardes) : N=62 WR=47% PF=0.99 exp=-0.48 (ticks) tot=-30.00 (ticks)
- EXCLUS : N=26 WR=27% PF=0.46 exp=-25.08 (ticks) tot=-652.00 (ticks)
- gardes: 62/88 (70%) | skipped parsing: {'date': 0, 'dir': 0, 'pnl': 0, 'inst': 0, 'sans_config': 0}

## trades_s1.csv -> trades_s1_regime.csv
- P&L utilise : `net_Conservateur-2ticks_$` | config = dernier event < jour du trade
- AVANT : N=1287 WR=30% PF=1.43 exp=+217.84 ($) tot=+280356.06 ($)
- APRES (gardes) : N=750 WR=32% PF=2.05 exp=+493.13 ($) tot=+369850.18 ($)
- EXCLUS : N=537 WR=28% PF=0.70 exp=-166.66 ($) tot=-89494.12 ($)
- gardes: 750/1287 (58%) | skipped parsing: {'date': 0, 'dir': 0, 'pnl': 0, 'inst': 0, 'sans_config': 0}

## trades.csv -> trades_regime.csv
- P&L utilise : `net_Conservateur-2ticks_$` | config = dernier event < jour du trade
- AVANT : N=207 WR=24% PF=0.54 exp=-112.62 ($) tot=-23312.50 ($)
- APRES (gardes) : N=112 WR=17% PF=0.41 exp=-151.32 ($) tot=-16947.50 ($)
- EXCLUS : N=95 WR=33% PF=0.71 exp=-67.00 ($) tot=-6365.00 ($)
- gardes: 112/207 (54%) | skipped parsing: {'date': 0, 'dir': 0, 'pnl': 0, 'inst': 0, 'sans_config': 0}

# Filtre regime sur backtests

## trades_macro.csv -> trades_macro_regime.csv
- P&L utilise : `net_dollar` | config = dernier event < jour du trade
- AVANT : N=83 WR=83% PF=1.59 exp=+3831.77 tot=+318037.07
- APRES (gardes) : N=83 WR=83% PF=1.59 exp=+3831.77 tot=+318037.07
- EXCLUS : N=0
- gardes: 83/83 (100%) | skipped parsing: {'date': 0, 'dir': 0, 'pnl': 0, 'inst': 0, 'sans_config': 0}

## trades_macro.csv -> trades_macro_regime.csv
- P&L utilise : `net_dollar` | config = dernier event < jour du trade
- AVANT : N=114 WR=62% PF=0.63 exp=-3554.87 tot=-405255.27
- APRES (gardes) : N=21 WR=62% PF=0.46 exp=-5710.12 tot=-119912.44
- EXCLUS : N=93 WR=62% PF=0.68 exp=-3068.20 tot=-285342.83
- gardes: 21/114 (18%) | skipped parsing: {'date': 0, 'dir': 0, 'pnl': 0, 'inst': 0, 'sans_config': 0}

## trades_macro.csv -> trades_macro_regime.csv
- P&L utilise : `net_dollar` | config = dernier event < jour du trade
- AVANT : N=1359 WR=65% PF=0.82 exp=-1605.72 tot=-2182167.46
- APRES (gardes) : N=334 WR=66% PF=0.76 exp=-2265.33 tot=-756621.30
- EXCLUS : N=1025 WR=65% PF=0.84 exp=-1390.78 tot=-1425546.16
- gardes: 334/1359 (25%) | skipped parsing: {'date': 0, 'dir': 0, 'pnl': 0, 'inst': 0, 'sans_config': 0}

## trades_macro.csv -> trades_macro_regime.csv
- P&L utilise : `net_dollar` | config = dernier event < jour du trade
- AVANT : N=48 WR=79% PF=1.19 exp=+1330.50 tot=+63863.95
- APRES (gardes) : N=48 WR=79% PF=1.19 exp=+1330.50 tot=+63863.95
- EXCLUS : N=0
- gardes: 48/48 (100%) | skipped parsing: {'date': 0, 'dir': 0, 'pnl': 0, 'inst': 0, 'sans_config': 0}

## trades_macro.csv -> trades_macro_regime.csv
- P&L utilise : `net_dollar` | config = dernier event < jour du trade
- AVANT : N=29 WR=59% PF=0.50 exp=-6614.41 tot=-191818.02
- APRES (gardes) : N=8 WR=62% PF=0.46 exp=-5968.90 tot=-47751.21
- EXCLUS : N=21 WR=57% PF=0.51 exp=-6860.32 tot=-144066.81
- gardes: 8/29 (28%) | skipped parsing: {'date': 0, 'dir': 0, 'pnl': 0, 'inst': 0, 'sans_config': 0}

## trades_macro.csv -> trades_macro_regime.csv
- P&L utilise : `net_dollar` | config = dernier event < jour du trade
- AVANT : N=737 WR=67% PF=0.99 exp=-97.47 tot=-71834.49
- APRES (gardes) : N=189 WR=68% PF=1.01 exp=+42.89 tot=+8105.59
- EXCLUS : N=548 WR=67% PF=0.98 exp=-145.88 tot=-79940.08
- gardes: 189/737 (26%) | skipped parsing: {'date': 0, 'dir': 0, 'pnl': 0, 'inst': 0, 'sans_config': 0}

# Filtre regime sur backtests

## trades_macro.csv -> trades_macro_regime.csv
- P&L utilise : `net_dollar` | config = dernier event < jour du trade
- AVANT : N=33 WR=85% PF=3.07 exp=+6430.87 tot=+212218.68
- APRES (gardes) : N=7 WR=57% PF=0.87 exp=-1051.50 tot=-7360.52
- EXCLUS : N=26 WR=92% PF=5.57 exp=+8445.35 tot=+219579.20
- gardes: 7/33 (21%) | skipped parsing: {'date': 0, 'dir': 0, 'pnl': 0, 'inst': 0, 'sans_config': 0}

