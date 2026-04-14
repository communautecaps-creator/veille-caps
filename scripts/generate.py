import json
from pathlib import Path
from html import escape

from openpyxl import Workbook


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "veille.json"
OUTPUT_HTML = BASE_DIR / "index.html"
OUTPUT_XLSX = BASE_DIR / "veille-marches-caps.xlsx"


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


def generate_html(data: dict) -> None:
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

    excel_link = ""
    if OUTPUT_XLSX.exists():
        excel_link = '<p><a href="veille-marches-caps.xlsx" download>📊 Télécharger le fichier Excel</a></p>'

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
      margin-bottom: 10px;
    }}
    .download {{
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
  <div class="download">{excel_link}</div>
  {''.join(cards)}
</body>
</html>
"""

    OUTPUT_HTML.write_text(html, encoding="utf-8")


def generate_excel(data: dict) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Veille"

    headers = [
        "Date détection",
        "Statut",
        "Priorité",
        "Acheteur",
        "Intitulé",
        "Territoire",
        "Thématique",
        "Date limite",
        "Lien AO",
        "Lien plateforme",
        "Recommandation",
        "Mode",
        "Commentaire",
    ]
    ws.append(headers)

    for item in data.get("items", []):
        ws.append([
            item.get("date_detection", ""),
            item.get("statut", ""),
            item.get("priorite", ""),
            item.get("acheteur", ""),
            item.get("intitule", ""),
            item.get("territoire", ""),
            item.get("thematique", ""),
            item.get("date_limite", ""),
            item.get("lien_ao", ""),
            item.get("lien_plateforme", ""),
            item.get("recommandation", ""),
            item.get("mode", ""),
            item.get("commentaire", ""),
        ])

    for column_cells in ws.columns:
        max_length = 0
        column_letter = column_cells[0].column_letter
        for cell in column_cells:
            value = str(cell.value) if cell.value is not None else ""
            if len(value) > max_length:
                max_length = len(value)
        ws.column_dimensions[column_letter].width = min(max_length + 2, 40)

    wb.save(OUTPUT_XLSX)


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    generate_excel(data)
    generate_html(data)
    print("index.html et veille-marches-caps.xlsx générés avec succès.")


if __name__ == "__main__":
    main()
