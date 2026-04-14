import requests
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "veille.json"

KEYWORDS = ["formation", "insertion", "numérique", "compétences"]

def fetch_boamp():
    url = "https://www.boamp.fr/api/explore/v2.1/catalog/datasets/avis/records?limit=20"
    response = requests.get(url)
    return response.json().get("results", [])

def filter_records(records):
    results = []
    for r in records:
        text = (r.get("objet", "") or "").lower()
        if any(k in text for k in KEYWORDS):
            results.append(r)
    return results

def load_data():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def main():
    records = fetch_boamp()
    print(records[:1])s

    data = load_data()

    for r in filtered[:3]:
        data["items"].append({
            "date_detection": datetime.today().strftime("%Y-%m-%d"),
            "statut": "nouveau",
            "priorite": "orange",
            "acheteur": r.get("nom_organisme", ""),
            "intitule": r.get("objet", ""),
            "territoire": "",
            "thematique": "formation",
            "date_limite": r.get("date_limite", ""),
            "lien_ao": "",
            "lien_plateforme": "https://www.boamp.fr",
            "recommandation": "À analyser",
            "mode": "à définir",
            "commentaire": "Ajout automatique BOAMP"
        })

    save_data(data)
    print("BOAMP intégré")

if __name__ == "__main__":
    main()
