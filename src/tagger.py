"""tagger.py — Genera etiquetas optimizadas y bilingües para búsquedas de talento en LinkedIn.

Novedades
─────────
* **Salida bilingüe**: ahora `generate_tags()` devuelve cinco listas:
  `cargos_es`, `cargos_en`, `empresas`, `palabras_clave_es`, `palabras_clave_en`.
* **Prompt ampliado** para solicitar los dos idiomas y reforzar el uso de AND/OR.
* Logs y parser adaptados.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Union
import json
import sys
from openai import OpenAI
from src.config import get_openai_key

# -----------------------------------------------------------------------------
# Cliente OpenAI (singleton)
# -----------------------------------------------------------------------------

_client: Optional[OpenAI] = None


def _get_client() -> Optional[OpenAI]:
    global _client
    print("[DEBUG] _get_client: intentando obtener cliente OpenAI…", file=sys.stderr, flush=True)

    if _client is not None:
        return _client

    key = get_openai_key()
    if not key:
        print("[ERROR] OPENAI_API_KEY no encontrado", file=sys.stderr, flush=True)
        return None

    _client = OpenAI(api_key=key)
    return _client


def openai_key_status() -> bool:
    return _get_client() is not None

# -----------------------------------------------------------------------------
# Prompt pieces
# -----------------------------------------------------------------------------

PROMPT_HEADER = (
    "Eres un *Talent Sourcer* experto en LinkedIn Recruiter para el equipo de RR. HH. de ITENE. "
    "Se te proporciona la descripción de una vacante dentro de las etiquetas <vacante>…</vacante>.\n\n"
)

PROMPT_BLOCKS_TEMPLATE = (
    "Tu tarea es producir cinco bloques de términos que mejoren la búsqueda de candidatos en LinkedIn Recruiter:\n"
    "1. «cargos_es»: hasta {max_titles} títulos y sinónimos del puesto en **castellano**, de lo más específico a lo más general.\n"
    "2. «cargos_en»: los mismos títulos en **inglés** (equivalentes o traducciones comunes).\n"
    "3. «empresas»: hasta {max_companies} compañías relevantes donde suelan trabajar candidatos adecuados (mismo sector, tamaño o tecnologías).\n"
    "4. «palabras_clave_es»: hasta {max_keywords} keywords en **castellano** que describan habilidades, certificaciones y herramientas. Incluye booleanos usando **AND** / **OR** en mayúsculas cuando aporte valor.\n"
    "5. «palabras_clave_en»: las mismas keywords en **inglés**.\n\n"
)

RULES_AND_EXAMPLE = (
    "### Reglas de formato\n"
    "• Devuelve la información **exclusivamente** en un objeto JSON plano, sin espacios externos y en una sola línea.\n"
    "• Estructura exacta del objeto:\n"
    "{\"cargos_es\":\"…\",\"cargos_en\":\"…\",\"empresas\":\"…\",\"palabras_clave_es\":\"…\",\"palabras_clave_en\":\"…\"}\n"
    "• Usa comas para separar valores. No numeraciones, viñetas ni comentarios.\n"
    "• No utilices el carácter ‘#’.\n\n"
    "### Ejemplo mínimo\n"
    "{\"cargos_es\":\"Científico de Datos, Ingeniero de Machine Learning\",\"cargos_en\":\"Data Scientist, ML Engineer\",\"empresas\":\"Accenture, Deloitte, Capgemini\",\"palabras_clave_es\":\"Python AND TensorFlow, aprendizaje automático\",\"palabras_clave_en\":\"Python AND TensorFlow, machine learning\"}\n\n"
    "Genera la salida siguiendo estas reglas. A continuación se adjunta la vacante:\n"
)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _job_description(job_info: Dict[str, str]) -> str:
    return "\n".join(f"{k.title()}: {v}" for k, v in job_info.items() if v)


def _build_prompt(job_info: Dict[str, str], *, max_titles: int, max_companies: int, max_keywords: int) -> str:
    return (
        PROMPT_HEADER
        + PROMPT_BLOCKS_TEMPLATE.format(
            max_titles=max_titles,
            max_companies=max_companies,
            max_keywords=max_keywords,
        )
        + RULES_AND_EXAMPLE
        + "<vacante>\n" + _job_description(job_info) + "\n</vacante>"
    )


def _to_list(value: Union[str, List[str]]) -> List[str]:
    if isinstance(value, list):
        return [v.strip() for v in value if isinstance(v, str) and v.strip()]
    if isinstance(value, str):
        return [t.strip() for t in value.split(',') if t.strip()]
    return []

# -----------------------------------------------------------------------------
# generate_tags
# -----------------------------------------------------------------------------

def generate_tags(
    job_info: Dict[str, str],
    max_titles: int = 15,
    max_companies: int = 10,
    max_keywords: int = 20,
    model: str = "gpt-4o",
) -> Dict[str, List[str]]:
    client = _get_client()
    if client is None:
        raise RuntimeError("OPENAI_API_KEY no encontrado.")

    prompt = _build_prompt(job_info, max_titles=max_titles, max_companies=max_companies, max_keywords=max_keywords)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido: {raw}") from e

    return {
        "cargos_es": _to_list(data.get("cargos_es", [])),
        "cargos_en": _to_list(data.get("cargos_en", [])),
        "empresas": _to_list(data.get("empresas", [])),
        "palabras_clave_es": _to_list(data.get("palabras_clave_es", [])),
        "palabras_clave_en": _to_list(data.get("palabras_clave_en", [])),
    }



