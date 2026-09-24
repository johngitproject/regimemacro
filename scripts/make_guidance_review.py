"""Genere le paquet de validation humaine du codage guidance.

Lit donnees/regime/fomc_guidance.csv (33 lignes draft) et produit
bilan/GUIDANCE_REVIEW.md : pour chaque meeting, decision, stance draft, score,
citation, dissents, URL + cases a cocher. La validation DOIT etre humaine
(corps complets : donnees/regime/sources/fomc_statements/YYYYMMDD_body.txt).

Une fois relu : mettre a jour la colonne statut (draft_a_valider -> valide_aaaa-mm-jj
ou corrige) et re-signer SHA256SUMS.

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/make_guidance_review.py
"""
import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIME = os.path.join(BASE, "donnees", "regime")
OUT = os.path.join(BASE, "bilan", "GUIDANCE_REVIEW.md")


def main():
    with open(os.path.join(REGIME, "fomc_guidance.csv"), newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    L = ["# Validation humaine — codage forward guidance FOMC (33 meetings)",
         "",
         "Protocole : pour chaque ligne, lire le corps complet "
         "(`donnees/regime/sources/fomc_statements/YYYYMMDD_body.txt`), vérifier que la citation "
         "existe et que la stance draft correspond au ton du statement, puis cocher. "
         "En cas de desaccord : barrer le draft et ecrire la stance retenue + motif.",
         "Une fois les 33 lignes traitees : statut -> `valide_aaaa-mm-jj`, re-signer SHA256SUMS.",
         ""]
    for i, r in enumerate(rows, 1):
        day = r["date_et"][:10].replace("-", "")
        L += [f"## {i:02d}. {r['date_et']} — decision {r['decision_bps']}bp ({r['action']})",
              f"- Stance draft : **{r['stance_draft']}** (score {r['score']}) — `{r['score_detail']}`",
              f"- Citation : _{r['quote']}_",
              f"- Dissents : {r['dissents']}",
              f"- Source : {r['source_url']} — corps : `donnees/regime/sources/fomc_statements/{day}_body.txt`",
              f"- Statut actuel : `{r['statut']}`",
              "- [ ] Stance validee telle quelle",
              "- [ ] Corrigee -> nouvelle stance : __________  Motif : __________",
              ""]
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"ecrit {OUT} : {len(rows)} meetings a relire")


if __name__ == "__main__":
    main()
