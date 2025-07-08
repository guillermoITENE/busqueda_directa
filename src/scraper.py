"""scraper.py — Extrae la descripción real de Bizneo/JobCenter y otros sitios.

Estrategia:
1. Descarga el HTML.
2. **Meta‑descripciones**: `<meta name="description">` y `<meta property="og:description">`.
3. **JSON embebido**: algunos Job Centers insertan un `<script type="application/json">` con la key
   `job.description`, `job.min_requirements`, etc. Lo detectamos y parseamos.
4. Devuelve un dict con las partes relevantes para el LLM:
   - `title`
   - `meta_description`
   - `og_description`
   - `job_description`   (desde JSON)
   - `job_requirements`  (desde JSON)
   - `text`              (texto plano completo)
   - `url`

Además imprime en consola cuáles de las fuentes encontró.
"""

from __future__ import annotations

import json
import re
import html as ihtml
from typing import Dict, Any

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

# -----------------------------------------------------------------------------
# Utilidades internas
# -----------------------------------------------------------------------------

def _first_non_empty(*values: str | None) -> str:
    for v in values:
        if v and v.strip():
            return v.strip()
    return ""


def _extract_json_in_script(soup: BeautifulSoup) -> dict[str, Any]:
    """Busca <script class="js-react-on-rails-component" ...> y devuelve el JSON."""
    script = soup.find("script", {"class": "js-react-on-rails-component"})
    if not script or not script.string:
        return {}
    try:
        raw_json = script.string.strip()
        data = json.loads(raw_json)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


# -----------------------------------------------------------------------------
# Función principal
# -----------------------------------------------------------------------------

def fetch_job_post(url: str, preview_chars: int = 300) -> Dict[str, str]:
    resp = requests.get(url, headers=HEADERS, timeout=25)
    resp.raise_for_status()

    raw_html = resp.text
    soup = BeautifulSoup(raw_html, "html.parser")

    # <title>
    title = _first_non_empty(soup.title.string if soup.title else "")

    # Meta description y OG description
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag.get("content", "").strip() if meta_desc_tag else ""

    og_desc_tag = soup.find("meta", attrs={"property": "og:description"})
    og_description = og_desc_tag.get("content", "").strip() if og_desc_tag else ""

    # JSON embebido (Bizneo / JobCenter)
    embedded_json = _extract_json_in_script(soup)
    job_description = ""
    job_requirements = ""
    if embedded_json:
        job = embedded_json.get("job") or {}
        job_description = ihtml.unescape(job.get("description", ""))
        job_requirements = ihtml.unescape(job.get("min_requirements", ""))

    # Texto plano completo
    full_text = soup.get_text(" ", strip=True)

    # ---------------------- DEBUG ---------------------- #
    print("=== [DEBUG] fetch_job_post ===")
    print("URL:", url)
    print("<title>", len(title), "chars")
    print("meta description", len(meta_description), "chars")
    print("og:description", len(og_description), "chars")
    print("job.description", len(job_description), "chars")
    print("job.min_requirements", len(job_requirements), "chars")
    print("Plain text length:", len(full_text))
    print("Preview plain text:")
    print(full_text[:preview_chars])
    print("=== [DEBUG END] ===")
    # --------------------------------------------------- #

    return {
        "url": url,
        "title": title,
        "meta_description": meta_description,
        "og_description": og_description,
        "job_description": job_description,
        "job_requirements": job_requirements,
        "text": full_text,
    }