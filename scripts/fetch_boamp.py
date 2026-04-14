import requests
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "veille.json"


def fetch_boamp():
    url = "https://www.boamp.fr/api/explore/v2.1/catalog/datasets/boamp/records?limit=3"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json().get("results", [])


def load_data():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_data(data):
    DATA_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def main():
    records = fetch_boamp()
    print(records[:1])

    data = load_data()

    for i, r in enumerate(records, start=1):
        data["items"].append({
            "date_detection": datetime.today().strftime("%Y-%m-%d"),
            "statut": "nouveau",
            "priorite": "orange",
            "acheteur": f"BOAMP test {i}",
            "intitule": f"Annonce test BOAMP {i}",
            "territoire": "",
            "thematique": "formation",
            "date_limite": "",
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
