# Stance x ES/NQ — le regime suit-il les tendances ?

Base : 1960 jours (2022-2025, rollovers J-8, trous 6j/roll absorbes par offsets en seances).
Forwards 5/20/60 seances sur close RTH. Momentum 10Y : tnx[t]-tnx[t-60] en bp, seuil +/-50.
Stats : t indicatif (forwards chevauchants -> autocorrelation), lire d'abord N, mediane, hit rate.

## ES (983 j)

### forward 5j
- tous jours : N=983 moy=+0.25% med=+0.38% hit=58% sd=2.34 t=+3.4
- stance R : N=675 moy=+0.42% med=+0.54% hit=62% sd=2.07 t=+5.2
- stance A : N=233 moy=-0.16% med=-0.01% hit=50% sd=3.11 t=-0.8
- stance N : N=75 moy=+0.04% med=+0.21% hit=55% sd=1.48 t=+0.3
- par config (stance/mom60) :
  - A/flat : N=107 moy=-0.23% med=+0.03% hit=50% sd=2.62 t=-0.9
  - A/up : N=126 moy=-0.10% med=-0.07% hit=49% sd=3.49 t=-0.3
  - N/flat : N=75 moy=+0.04% med=+0.21% hit=55% sd=1.48 t=+0.3
  - R/down : N=80 moy=+1.03% med=+0.60% hit=69% sd=2.17 t=+4.2
  - R/flat : N=479 moy=+0.44% med=+0.61% hit=64% sd=2.00 t=+4.8
  - R/up : N=116 moy=-0.08% med=-0.23% hit=47% sd=2.17 t=-0.4

### forward 20j
- tous jours : N=983 moy=+1.01% med=+1.58% hit=66% sd=4.24 t=+7.4
- stance R : N=675 moy=+1.58% med=+2.03% hit=72% sd=3.63 t=+11.3
- stance A : N=233 moy=-0.48% med=-0.03% hit=49% sd=5.79 t=-1.3
- stance N : N=75 moy=+0.44% med=+0.52% hit=59% sd=1.72 t=+2.2
- par config (stance/mom60) :
  - A/flat : N=107 moy=-0.14% med=-0.03% hit=49% sd=5.88 t=-0.2
  - A/up : N=126 moy=-0.76% med=-0.09% hit=50% sd=5.71 t=-1.5
  - N/flat : N=75 moy=+0.44% med=+0.52% hit=59% sd=1.72 t=+2.2
  - R/down : N=80 moy=+3.05% med=+3.12% hit=90% sd=2.77 t=+9.8
  - R/flat : N=479 moy=+1.49% med=+2.14% hit=72% sd=3.80 t=+8.6
  - R/up : N=116 moy=+0.92% med=+0.61% hit=60% sd=3.16 t=+3.1

### forward 60j
- tous jours : N=981 moy=+3.03% med=+3.67% hit=75% sd=6.61 t=+14.4
- stance R : N=675 moy=+4.86% med=+5.08% hit=84% sd=5.94 t=+21.3
- stance A : N=233 moy=-1.84% med=-0.71% hit=46% sd=6.86 t=-4.1
- stance N : N=73 moy=+1.74% med=+1.93% hit=82% sd=1.89 t=+7.9
- par config (stance/mom60) :
  - A/flat : N=107 moy=-2.85% med=-2.76% hit=30% sd=4.45 t=-6.6
  - A/up : N=126 moy=-0.99% med=+2.11% hit=60% sd=8.30 t=-1.3
  - N/flat : N=73 moy=+1.74% med=+1.93% hit=82% sd=1.89 t=+7.9
  - R/down : N=80 moy=+7.20% med=+6.84% hit=99% sd=4.48 t=+14.4
  - R/flat : N=479 moy=+5.15% med=+5.19% hit=89% sd=5.36 t=+21.1
  - R/up : N=116 moy=+2.02% med=+1.90% hit=56% sd=7.83 t=+2.8

## NQ (977 j)

### forward 5j
- tous jours : N=977 moy=+0.32% med=+0.47% hit=58% sd=3.03 t=+3.3
- stance R : N=675 moy=+0.63% med=+0.72% hit=63% sd=2.69 t=+6.0
- stance A : N=227 moy=-0.44% med=-0.47% hit=48% sd=3.95 t=-1.7
- stance N : N=75 moy=-0.09% med=+0.09% hit=52% sd=2.20 t=-0.4
- par config (stance/mom60) :
  - A/flat : N=107 moy=-0.10% med=-0.38% hit=49% sd=3.52 t=-0.3
  - A/up : N=120 moy=-0.74% med=-0.63% hit=47% sd=4.30 t=-1.9
  - N/flat : N=75 moy=-0.09% med=+0.09% hit=52% sd=2.20 t=-0.4
  - R/down : N=80 moy=+1.45% med=+1.07% hit=68% sd=3.10 t=+4.2
  - R/flat : N=479 moy=+0.62% med=+0.79% hit=65% sd=2.60 t=+5.2
  - R/up : N=116 moy=+0.07% med=-0.08% hit=49% sd=2.63 t=+0.3

### forward 20j
- tous jours : N=977 moy=+1.25% med=+1.76% hit=66% sd=5.64 t=+6.9
- stance R : N=675 moy=+2.33% med=+2.53% hit=76% sd=4.88 t=+12.4
- stance A : N=227 moy=-1.52% med=-1.83% hit=43% sd=7.20 t=-3.2
- stance N : N=75 moy=-0.07% med=+0.09% hit=53% sd=2.73 t=-0.2
- par config (stance/mom60) :
  - A/flat : N=107 moy=-0.58% med=-0.49% hit=47% sd=7.64 t=-0.8
  - A/up : N=120 moy=-2.36% med=-1.86% hit=40% sd=6.71 t=-3.9
  - N/flat : N=75 moy=-0.07% med=+0.09% hit=53% sd=2.73 t=-0.2
  - R/down : N=80 moy=+3.85% med=+3.15% hit=91% sd=3.63 t=+9.5
  - R/flat : N=479 moy=+2.21% med=+2.83% hit=75% sd=5.23 t=+9.2
  - R/up : N=116 moy=+1.79% med=+1.31% hit=66% sd=3.88 t=+5.0

### forward 60j
- tous jours : N=975 moy=+4.24% med=+4.94% hit=71% sd=9.25 t=+14.3
- stance R : N=675 moy=+6.90% med=+7.05% hit=83% sd=8.06 t=+22.3
- stance A : N=227 moy=-2.60% med=-2.16% hit=40% sd=10.03 t=-3.9
- stance N : N=73 moy=+0.88% med=+0.60% hit=53% sd=2.83 t=+2.7
- par config (stance/mom60) :
  - A/flat : N=107 moy=-3.75% med=-5.52% hit=26% sd=9.16 t=-4.2
  - A/up : N=120 moy=-1.57% med=+0.38% hit=52% sd=10.68 t=-1.6
  - N/flat : N=73 moy=+0.88% med=+0.60% hit=53% sd=2.83 t=+2.7
  - R/down : N=80 moy=+8.84% med=+8.23% hit=95% sd=6.06 t=+13.0
  - R/flat : N=479 moy=+7.43% med=+7.15% hit=86% sd=7.57 t=+21.5
  - R/up : N=116 moy=+3.38% med=+4.37% hit=60% sd=10.04 t=+3.6

## Lecture (ne pas lire les labels au premier degre)

- Les labels sont des MARQUEURS D'EPOQUE, pas des signaux directionnels : A = 2022
  (bear, Fed en retard sur la courbe), R = 2023-2025 (plateau restrictif + bull).
  'Restrictif -> acheter' serait une lecture naive et dangereuse hors-echantillon.
- Ce que le regime fait bien : SEPARER les grandes tendances. A vs R ont des
  distributions forward opposees sur les deux indices et les trois horizons.
- Meilleure config : R/down (restrictif + 10Y en baisse >50bp/60j = desinflation,
  la politique mord, pivot anticipe) : ES60 +7.20% hit 99, NQ60 +8.84% hit 95.
  C'est la config 'soft landing' (fin 2023, ete 2024).
- Pire config court terme : A/up (retard + 10Y qui flambe) : NQ20 -2.36% hit 40.
  Pire config 60j : A/flat (bear qui saigne) : ES med -2.76% hit 30, NQ med -5.52% hit 26.
  A/down n'est jamais observe (10Y 60j jamais < -50bp en stance A sur 2022-25).
- R/up (restrictif + 10Y qui monte = tension late-cycle) reste positif mais faible :
  ES60 +2.02% hit 56 vs +7.20% en R/down. Le 10Y discrimine DANS le regime.
- Limites : un seul cycle (pas de vrai easing-cycle haussier observe), forwards
  chevauchants (quelques episodes independants : T4-2023, S2-2024), drift haussier
  2023-25 qui gonfle la baseline. Usage recommande : FILTRE de conviction/taille,
  pas signal autonome. Anticipation = transitions R/up -> R/down (pivot price),
  a tester en walk-forward.

