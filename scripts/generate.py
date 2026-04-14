import json
from pathlib import Path
from html import escape

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "veille.json"
OUTPUT_HTML = BASE_DIR / "index.html"


def badge_class(priorite: str) -> str:
    mapping = {
        "rouge": "urgent",
        "orange": "watch",
        "vert": "context",
    }
    return mapping.get(priorite.lower(), "watch")


def render_link(url: str, label: str) -> str:
    if not url:
        return ""
    safe_url = escape(url, quote=True)
    safe_label = escape(label)
    return f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer">{safe_label}</a>'


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    updated_at = escape(data.get("updated_at", ""))
    items = data.get("items", [])

    cards = []
    for item in items:
        css_class = badge_class(item.get("priorite", "orange"))
        acheteur = escape(item.get("acheteur", ""))
        intitule = escape(item.get("intitule", ""))
        territoire = escape(item.get("territoire", ""))
        thematique = escape(item.get("thematique", ""))
        date_limite = escape(item.get("date_limite", ""))
        recommandation = escape(item.get("recommandation", ""))
        commentaire = escape(item.get("commentaire", ""))

        lien_ao = render_link(item.get("lien_ao", ""), "🔗 Voir l'appel d'offres")
        lien_plateforme = render_link(item.get("lien_plateforme", ""), "📂 Voir la plateforme")

        links = " | ".join([part for part in [lien_ao, lien_plateforme] if part])

        card = f"""
        <div class="card {css_class}">
          <h2>{intitule}</h2>
          <p><strong>Acheteur :</strong> {acheteur}</p>
          <p><strong>Territoire :</strong> {territoire}</p>
          <p><strong>Thématique :</strong> {thematique}</p>
          <p><strong>Date limite :</strong> {date_limite or "Non précisée"}</p>
          <p><strong>Recommandation :</strong> {recommandation}</p>
          <p>{commentaire}</p>
          <p>{links}</p>
        </div>
        """
        cards.append(card)

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Veille Marchés CAPS</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 20px;
      background: #f7f7f7;
      color: #222;
    }}
    h1 {{
      margin-bottom: 5px;
    }}
    .subtitle {{
      color: #555;
      margin-bottom: 24px;
    }}
    .card {{
      border: 1px solid #ddd;
      border-radius: 10px;
      padding: 16px;
      margin: 12px 0;
      background: white;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}
    .urgent {{
      border-left: 8px solid #d62828;
      background: #fff5f5;
    }}
    .watch {{
      border-left: 8px solid #f4a261;
      background: #fffaf3;
    }}
    .context {{
      border-left: 8px solid #2a9d8f;
      background: #f2fffb;
    }}
    a {{
      text-decoration: none;
      font-weight: bold;
    }}
    a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <h1>📊 Veille Marchés CAPS</h1>
  <p class="subtitle">Dernière mise à jour : {updated_at}</p>
  {''.join(cards)}
</body>
</html>
"""

    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print("index.html généré avec succès.")


if __name__ == "__main__":
    main()
