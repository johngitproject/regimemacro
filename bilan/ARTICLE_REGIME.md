# Régime macro-taux et grandes tendances ES/NQ : du mandat dual au filtre de conviction

*Recherche appliquée, jan-2022 → jan-2026. Code + méthode + résultats agrégés publics ;
données brutes sous CGU re-téléchargeables (voir `donnees/regime/LICENCES.md`).*

## 1. Question

Les taux directeurs dépendent des anticipations d'inflation et de chômage relatives aux seuils
de la Fed ($r^*$, $u^*$, 2 %) et du forward guidance. Cette chaîne causale, une fois mesurée,
suit-elle les grandes tendances ES/NQ — et peut-elle filtrer des setups de trading ?

## 2. Méthode

**Données.** Calendrier macro US avec previous/forecast/actual/surprise (352 releases : CPI/PCE
headline+core, NFP, chômage, taux Fed ; ref appariée via métadonnée source, jamais inventée) ;
20 tables SEP (longer-run $r^*$ 2,4→3,1 %, $u^*$ 4,0→4,2 %, $\pi^*$=2 %) + dots individuels
(médianes recalculées, confrontées aux tables officielles) ; 33 statements FOMC codés
hawkish/neutre/dovish avec citations et dissents ; pricing quotidien (futures Fed funds,
T-bill, 5Y, 10Y, EFFR) ; front continu ES/NQ 2022-2025 en closes RTH (rollover J-8, trous
bouchés via Yahoo avec QC par saut de base, 3 fenêtres refusées, week-ends exclus).

**Mesures.** Stance réelle `real_gap = (taux − πe_SEP) − (r*−2)` + Taylor contemporain en
référence, anti-lookahead strict (target pré-décision, pricing veille, seuils du dernier SEP).
Forwards indices 5/20/60 séances, momentum 10Y 60j (seuil ±50 bp), dérives pré-news 20j/5j/1j,
moves jour J (close vs veille). Config = côté stance (R/A/N) × momentum 10Y (down/flat/up).

**Garde-fous.** Aucune valeur inventée (vide, jamais 0) ; N<5 = lecture épisode, pas statistique ;
forwards chevauchants (lire N/médiane/hit, pas les t-stats) ; coûts inclus aux backtests
(spread 1 tick + commission + slip) ; échecs publiés au même titre que les succès.

## 3. Résultats

**3.1. La stance sépare les tendances (1960 jours).** Restrictif : ES 60j +4,86 % hit 84 %,
NQ +6,90 % hit 83 %. Accommodant (*behind the curve*, bear 2022) : ES −1,84 % hit 46 %,
NQ −2,60 % hit 40 %. Avertissement : les labels sont des marqueurs d'époque (un seul cycle
observé), pas des signaux — « restrictif → acheter » serait naïf hors-échantillon.

**3.2. Le 10Y discrimine dans le régime.** R/down (soft landing) : ES 60j +7,20 % hit 99 %,
NQ +8,84 % hit 95 %. R/up (tension late-cycle) : ES +2,02 % hit 56 %. A/up : NQ 20j −2,36 %
hit 40 % (VETO long). Le 10Y devance le directeur (ex : −97 bp fin 2023 sans geste) et
l'infirme parfois : −100 bp de cuts fin 2024 avec 10Y **+93 bp** (*hawkish cuts*).

**3.3. Jours FOMC (33) : 31 décisions exactement comme pricées.** Hike/hold attendu : ES
+0,5 %, 10Y −4/−5 bp (« buy the hike »). Cut attendu : 10Y +3 bp, ES −0,3 % — un cut ne se
trade pas comme un signal dovish. Deux surprises (juin-22 +75 vs +50 ; sep-24 −50 vs −25)
concentrent le risque.

**3.4. Dérive pré-news (318 releases).** Le marché dérive souvent en mode dovish avant le
print ; les surprises paient contre la dérive (reversal juil-22 −1,2 %, explosion nov-22
+2,9 %), avec amplitude fonction de la stance (−0,3 % pour le même setup en régime R).
Seul le FOMC est proprement pré-pricé (concordance 10Y 64 % ; CPI/PCE ≈ pile ou face).
Chômage attendu en hausse (N=12) : haussier en poolé par composition 2023, mais trois destins
opposés par quadrant (nov-22 +6,7 % fin des hikes ; déc-24 −1,3 % avec 10Y +53 bp en dilemme
stagflation ; déc-25 chop) — d'où la lecture conditionnelle, pas la moyenne.

**3.5. Filtre validé sur backtests (exclusion + rapport).** VP02 : PF 1,18→1,27. swingS1 :
1,43→**2,05** (exclus à PF 0,70, −89 k$). mgi_q1 : 0,80→0,99. v03-paris : 0,54→0,41 —
le filtre **nuit aux fadeurs** : validation par stratégie obligatoire, jamais en aveugle.

**3.6. Swing autonome : refusé.** Biais + tactique events : PF OOS 1,13, DD −133 k$ (la couche
events fige le système : 567 séances bloquées). Biais seul : PF 2,18 (OOS 2,59) mais DD
−108 k$ (krach avr-25). V2 (vol targeting + urgences restreintes) : PF OOS 1,46 mais DD
−129 k$. Verdict : l'edge est côté sélection, le chantier restant est purement risque.

## 4. Limites (à lire avant usage)

Un seul cycle macro (pas d'easing-cycle haussier observé) ; petits N par case ; guidance
validée humainement le 2026-09-24 (relecture sans correction) ; 3 fenêtres de données
refusées au QC + 1 conflit ouvert (11-sep-24) ; consensus non-rafraîchissable sans nouveau
scrape (point de rupture du pipeline) ; données Yahoo/Investing non redistribuées
(rebuild documenté).

## 5. Conclusion opérationnelle

Le modèle livre exactement deux nombres par jour et par sens : **un biais** (LONG/SHORT/NEUTRE/
VETO par config) et **un sizing** (1,0/0,75/0,5/0,25/0). Commandes : `filtre`, `news`, `stance`,
`repricing`. Aujourd'hui (jan-26, N/flat) : neutre, x0,5 des deux côtés — le modèle se tait
quand il n'a rien à dire, et c'est une fonction, pas un bug.
