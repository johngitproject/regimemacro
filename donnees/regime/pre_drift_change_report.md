# Le marche price-t-il le changement attendu ? (20j / 5j / 1j)

Filtre : |forecast - previous| >= seuil (CPI/PCE 0.2, NFP 20K, UNEMP 0.1, FED 0.25).
Drifts ancrés veille (dernier close < J), sessions de trading, jamais interpolés.

## CPI (32 events avec changement attendu)
### attendu hausse : N=13
- ES 20j % : N=12 moy=+0.76 med=+1.69
- ES 5j % : N=13 moy=-0.22 med=+0.12
- ES 1j % : N=13 moy=+0.39 med=+0.08
- 10Y 20j bp : N=13 moy=+14.69 med=+8.00
- 10Y 5j bp : N=13 moy=+9.38 med=+8.00
- 10Y 1j bp : N=13 moy=+1.77 med=-1.00
### attendu baisse : N=19
- ES 20j % : N=19 moy=-0.35 med=+1.07
- ES 5j % : N=19 moy=-0.83 med=-0.08
- ES 1j % : N=19 moy=-0.12 med=+0.53
- 10Y 20j bp : N=19 moy=+6.05 med=+8.00
- 10Y 5j bp : N=19 moy=+1.89 med=+6.00
- 10Y 1j bp : N=19 moy=-0.53 med=+1.00
- concordance 10Y 20j (signe drift == sens taux attendu) : 12/22 = 55%

## PCE (24 events avec changement attendu)
### attendu hausse : N=7
- ES 20j % : N=7 moy=+3.41 med=+5.09
- ES 5j % : N=7 moy=+0.86 med=+1.78
- ES 1j % : N=7 moy=+0.30 med=+0.15
- 10Y 20j bp : N=7 moy=+9.43 med=+16.00
- 10Y 5j bp : N=7 moy=-5.43 med=-8.00
- 10Y 1j bp : N=7 moy=+0.14 med=-4.00
### attendu baisse : N=17
- ES 20j % : N=17 moy=+1.32 med=+1.84
- ES 5j % : N=17 moy=+0.90 med=+0.75
- ES 1j % : N=17 moy=+0.45 med=+0.44
- 10Y 20j bp : N=17 moy=-1.29 med=-4.00
- 10Y 5j bp : N=17 moy=+0.29 med=-1.00
- 10Y 1j bp : N=17 moy=+0.29 med=-2.00
- concordance 10Y 20j (signe drift == sens taux attendu) : 9/17 = 53%

## NFP (41 events avec changement attendu)
### attendu hausse : N=13
- ES 20j % : N=12 moy=+0.67 med=+1.57
- ES 5j % : N=13 moy=-0.87 med=-0.74
- ES 1j % : N=13 moy=-0.43 med=-0.11
- 10Y 20j bp : N=13 moy=-10.69 med=-17.00
- 10Y 5j bp : N=13 moy=-7.23 med=-5.00
- 10Y 1j bp : N=13 moy=-1.38 med=+0.00
### attendu baisse : N=28
- ES 20j % : N=28 moy=+0.56 med=+0.85
- ES 5j % : N=28 moy=+0.74 med=+0.72
- ES 1j % : N=28 moy=+0.10 med=+0.17
- 10Y 20j bp : N=28 moy=+12.36 med=+16.50
- 10Y 5j bp : N=28 moy=-1.21 med=-2.00
- 10Y 1j bp : N=28 moy=-0.11 med=-0.50
- concordance 10Y 20j (signe drift == sens taux attendu) : 7/28 = 25%

## UNEMP (12 events avec changement attendu)
### attendu hausse : N=7
- ES 20j % : N=7 moy=+1.55 med=+1.50
- ES 5j % : N=7 moy=+0.23 med=+0.10
- ES 1j % : N=7 moy=-0.31 med=+0.05
- 10Y 20j bp : N=7 moy=+4.14 med=+7.00
- 10Y 5j bp : N=7 moy=-6.86 med=-10.00
- 10Y 1j bp : N=7 moy=-0.43 med=-0.00
### attendu baisse : N=5
- ES 20j % : N=4 (insuffisant)
- ES 5j % : N=5 moy=+0.85 med=+0.07
- ES 1j % : N=5 moy=-0.43 med=-0.26
- 10Y 20j bp : N=5 moy=+22.00 med=+22.00
- 10Y 5j bp : N=5 moy=+15.80 med=+20.00
- 10Y 1j bp : N=5 moy=+4.80 med=+3.00
- concordance 10Y 20j (signe drift == sens taux attendu) : 5/8 = 62%

## FED (17 events avec changement attendu)
### attendu hausse : N=11
- ES 20j % : N=11 moy=-1.48 med=-0.53
- ES 5j % : N=11 moy=-0.45 med=+0.42
- ES 1j % : N=11 moy=-0.01 med=-0.37
- 10Y 20j bp : N=11 moy=+9.18 med=+16.00
- 10Y 5j bp : N=11 moy=+9.36 med=+6.00
- 10Y 1j bp : N=11 moy=+0.27 med=-2.00
### attendu baisse : N=6
- ES 20j % : N=6 moy=+1.72 med=+2.18
- ES 5j % : N=6 moy=+0.42 med=+0.38
- ES 1j % : N=6 moy=+0.13 med=-0.17
- 10Y 20j bp : N=6 moy=-5.00 med=-9.50
- 10Y 5j bp : N=6 moy=+6.50 med=+6.00
- 10Y 1j bp : N=6 moy=+2.33 med=+0.00
- concordance 10Y 20j (signe drift == sens taux attendu) : 9/14 = 64%

## Correlation drift x surprise signee (surprise signee : UNEMP inversee)
- CPI : driftTNX5: N=32 r=+0.26 | driftTNX1: N=32 r=-0.27 | driftES5: N=32 r=+0.19 | driftES1: N=32 r=+0.09
- PCE : driftTNX5: N=24 r=+0.00 | driftTNX1: N=24 r=-0.23 | driftES5: N=24 r=-0.16 | driftES1: N=24 r=+0.17
- NFP : driftTNX5: N=41 r=-0.13 | driftTNX1: N=41 r=-0.06 | driftES5: N=41 r=+0.35 | driftES1: N=41 r=+0.25
- UNEMP : driftTNX5: N=12 r=-0.36 | driftTNX1: N=12 r=-0.26 | driftES5: N=12 r=+0.03 | driftES1: N=12 r=-0.07
- FED : driftTNX5: N=17 r=+0.55 | driftTNX1: N=17 r=+0.24 | driftES5: N=17 r=-0.45 | driftES1: N=17 r=+0.11

## Amplitude jour J par alignement (sous-ensemble avec changement attendu)
### ES jour J (%)
- CONTRE : N=25 |J| moy=+0.88 med=+0.67 gros(>0.5)=56%
- AVEC : N=27 |J| moy=+1.12 med=+0.92 gros(>0.5)=74%
- n.d. : N=73 |J| moy=+1.01 med=+0.60 gros(>0.5)=59%

### NQ jour J (%)
- CONTRE : N=25 |J| moy=+1.06 med=+0.77 gros(>0.5)=72%
- AVEC : N=27 |J| moy=+1.44 med=+1.10 gros(>0.5)=74%
- n.d. : N=71 |J| moy=+1.38 med=+0.91 gros(>0.5)=72%

### 10Y jour J (bp)
- CONTRE : N=25 |J| moy=+7.04 med=+6.00 gros(>5)=52%
- AVEC : N=28 |J| moy=+7.07 med=+6.00 gros(>5)=57%
- n.d. : N=72 |J| moy=+6.43 med=+5.50 gros(>5)=50%

