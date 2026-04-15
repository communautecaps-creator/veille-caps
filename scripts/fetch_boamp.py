import json
import requests
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "veille.json"

BOAMP_URL = "https://www.boamp.fr/api/explore/v2.1/catalog/datasets/boamp/records"

# Nombre d'avis récupérés à chaque exécution
LIMIT = 100

# Mots-clés de base pour repérer les marchés potentiellement utiles
KEYWORDS = [
    "formation",
    "insertion",
    "compétences",
    "compétence",
    "numérique",
    "illettrisme",
    "illectronisme",
    "remise à niveau",
    "français langue étrangère",
    "fle",
    "savoirs de base",
    "apprentissage"
]


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def safe_str(value):
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def pick_first(record, keys, default=""):
    """
    Cherche la première clé non vide parmi plusieurs possibilités.
    Permet d'être robuste si les noms de champs varient.
    """
    for key in keys:
        value = record.get(key)
        if value not in (None, "", [], {}):
            return value
    return default


def parse_date(value):
    """
    Essaie de convertir une date BOAMP en ISO simple.
    Retourne une chaîne vide si échec.
    """
    if not value:
        return ""

    value = safe_str(value)

    # Quelques formats fréquents possibles
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.date().isoformat()
        except ValueError:
            pass

    # Tentative légère si format ISO avec Z
    try:
        value2 = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(value2)
        return dt.date().isoformat()
    except ValueError:
        return ""


def build_text_blob(raw):
    """
    Construit un gros texte exploitable pour recherche mots-clés.
    """
    parts = []

    for key, value in raw.items():
        if value is None:
            continue

        if isinstance(value, list):
            parts.extend([safe_str(v) for v in value if v is not None])
        elif isinstance(value, dict):
            parts.append(json.dumps(value, ensure_ascii=False))
        else:
            parts.append(safe_str(value))

    return " ".join(parts).lower()


def classify_notice_type(raw):
    """
    Repérage simple du type d'avis.
    """
    text = build_text_blob(raw)

    if "avis d'attribution" in text:
        return "attribution"
    if "avis rectificatif" in text or "rectificatif" in text:
        return "rectificatif"
    if "avis de marché" in text:
        return "marche"
    return "autre"


def extract_departments(raw):
    """
    Prépare déjà un champ département exploitable.
    Pour l'instant on fait simple : on repère 76 et 27 dans le texte.
    Le filtrage précis viendra à l'étape suivante.
    """
    text = build_text_blob(raw)
    found = []

    for dep in ["76", "27"]:
        if dep in text:
            found.append(dep)

    return found


def keyword_matches(raw):
    text = build_text_blob(raw)
    found = [kw for kw in KEYWORDS if kw.lower() in text]
    return found


def normalize_record(raw):
    """
    Produit une structure stable, même si BOAMP renvoie des champs variables.
    """
    record_id = pick_first(raw, [
        "id",
        "idweb",
        "reference",
        "reference_avis",
        "no_annonce",
        "numero_annonce"
    ], "")

    title = pick_first(raw, [
        "objet",
        "intitule",
        "libelle",
        "titre"
    ], "")

    buyer = pick_first(raw, [
        "nomacheteur",
        "acheteur",
        "organisme",
        "nom_organisme"
    ], "")

    publication_date = parse_date(pick_first(raw, [
        "dateparution",
        "date_publication",
        "datepublication",
        "publication_date"
    ], ""))

    deadline_date = parse_date(pick_first(raw, [
        "datelimite",
        "date_limite",
        "date_limite_reception_offres",
        "date_limite_reception",
        "date_reception_offres"
    ], ""))

    url = pick_first(raw, [
        "url",
        "source_url",
        "permalink"
    ], "")

    notice_type = classify_notice_type(raw)
    matched_keywords = keyword_matches(raw)
    departments = extract_departments(raw)

    normalized = {
        "source": "BOAMP",
        "source_id": safe_str(record_id),
        "title": safe_str(title),
        "buyer": safe_str(buyer),
        "publication_date": publication_date,
        "deadline_date": deadline_date,
        "url": safe_str(url),
        "notice_type": notice_type,
        "matched_keywords": matched_keywords,
        "departments_detected": departments,
        "raw": raw
    }

    return normalized


def fetch_boamp():
    params = {
        "limit": LIMIT
    }

    response = requests.get(BOAMP_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    records = payload.get("results", [])
    normalized_records = []

    for item in records:
        normalized_records.append(normalize_record(item))

    return normalized_records


def load_existing():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"updated_at": "", "items": []}


def save_data(items):
    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": items
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    ensure_data_dir()
    items = fetch_boamp()
    save_data(items)
    print(f"{len(items)} avis BOAMP enregistrés dans {DATA_FILE}")
