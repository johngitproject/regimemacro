"""Fige l'empreinte SHA256 des datasets testes (tracabilite, pas redistribution).

Couvre donnees/regime/*.csv + sources JSON/CSV. A relancer apres chaque mise a jour
validee (ex : validation guidance -> re-signer).

Sortie : donnees/regime/SHA256SUMS.txt

Lancer avec le venv du projet :
  .\\venv\\Scripts\\python.exe scripts/sign_release.py
"""
import glob
import hashlib
import os
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIME = os.path.join(BASE, "donnees", "regime")
SRC_DIR = os.path.join(REGIME, "sources")
OUT = os.path.join(REGIME, "SHA256SUMS.txt")


def main():
    files = sorted(glob.glob(os.path.join(REGIME, "*.csv")) +
                   glob.glob(os.path.join(SRC_DIR, "*.json")) +
                   glob.glob(os.path.join(SRC_DIR, "*.csv")))
    lines = [f"# Empreintes SHA256 des datasets testes — fige le {date.today().isoformat()}",
             "# (tracabilite de la version validee ; les fichiers marques EXCLU dans",
             "#  LICENCES.md ne sont pas redistribues, leurs hashes prouvent quoi tester)",
             ""]
    for f in files:
        h = hashlib.sha256(open(f, "rb").read()).hexdigest()
        lines.append(f"{h}  {os.path.relpath(f, BASE)}")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"ecrit {OUT} : {len(files)} fichiers")


if __name__ == "__main__":
    main()
