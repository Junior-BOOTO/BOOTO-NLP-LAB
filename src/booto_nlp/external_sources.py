"""Chargement de textes depuis des PDF et l'API publique Wikimedia."""
from __future__ import annotations
import io
from typing import Callable
from urllib.parse import quote
import pandas as pd
import requests
from pypdf import PdfReader

MAX_PDF_BYTES = 5 * 1024 * 1024
MAX_PDF_PAGES = 1000
MAX_API_TEXT_CHARS = 3500
SUPPORTED_LANGUAGES = {"fr", "en", "es"}

def load_pdf(
    source: bytes | io.BytesIO,
    filename: str = "document.pdf",
    progress_callback: Callable[[int, int], None] | None = None,
) -> pd.DataFrame:
    """Extrait le texte sélectionnable d'un PDF, une page par document.

    Le callback facultatif reçoit (page_traitée, nombre_total_de_pages).
    """
    data = source if isinstance(source, bytes) else source.getvalue()
    if len(data) > MAX_PDF_BYTES:
        raise ValueError("Fichier PDF trop volumineux : limite 5 Mo.")
    if not data.startswith(b"%PDF"):
        raise ValueError("Le fichier sélectionné n'est pas un PDF valide.")
    try:
        reader = PdfReader(io.BytesIO(data), strict=False)
        if reader.is_encrypted:
            raise ValueError("Ce PDF est protégé par mot de passe et ne peut pas être lu.")
        total_pages = len(reader.pages)
        if total_pages > MAX_PDF_PAGES:
            raise ValueError("Le PDF dépasse la limite de 1000 pages.")
        records = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                records.append({"document_id": f"pdf-page-{page_number}", "text": text,
                                "source": filename, "page": page_number})
            if progress_callback is not None:
                progress_callback(page_number, total_pages)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Impossible de lire ce PDF. Vérifiez que le fichier n'est pas endommagé.") from exc
    if not records:
        raise ValueError("Aucun texte sélectionnable n'a été trouvé. Ce PDF est peut-être scanné ; la reconnaissance OCR n'est pas encore disponible.")
    return pd.DataFrame(records)

def fetch_wikipedia(query: str, language: str = "fr", limit: int = 5) -> pd.DataFrame:
    """Recherche et récupère des extraits d'articles Wikipedia via l'API Wikimedia."""
    query = query.strip()
    if not query:
        raise ValueError("Saisissez un sujet à rechercher.")
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError("La langue doit être français, anglais ou espagnol.")
    limit = max(1, min(int(limit), 10))
    endpoint = f"https://{language}.wikipedia.org/w/api.php"
    params = {"action": "query", "generator": "search", "gsrsearch": query,
              "gsrnamespace": 0, "gsrlimit": limit, "prop": "extracts",
              "explaintext": 1, "exchars": MAX_API_TEXT_CHARS,
              "format": "json", "formatversion": 2, "redirects": 1}
    headers = {"User-Agent": "BOOTO-NLP-LAB/0.2 (educational text analysis)"}
    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise ValueError("La connexion à Wikipedia a échoué. Réessayez dans un instant.") from exc
    except ValueError as exc:
        if exc.__class__.__name__ == "JSONDecodeError":
            raise ValueError("L'API Wikipedia a renvoyé une réponse illisible.") from exc
        raise
    pages = payload.get("query", {}).get("pages", [])
    records = []
    for page in pages:
        text = (page.get("extract") or "").strip()
        title = page.get("title", "").strip()
        if not text or not title:
            continue
        page_url = f"https://{language}.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
        records.append({"document_id": f"wiki-{language}-{page.get('pageid', len(records) + 1)}",
                        "text": text, "language": language, "title": title,
                        "source": "Wikimedia Wikipedia API", "source_url": page_url,
                        "license": "Wikipedia — CC BY-SA (voir la page source)"})
    if not records:
        raise ValueError("Aucun extrait trouvé. Essayez un autre sujet ou une autre langue.")
    return pd.DataFrame(records)
