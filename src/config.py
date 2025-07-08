from __future__ import annotations
import os
from typing import Optional

_OPENAI_KEY_CACHE: Optional[str] = None

def get_openai_key() -> str | None:
    """Devuelve la clave de OpenAI leyendo únicamente desde el .env."""
    global _OPENAI_KEY_CACHE
    if _OPENAI_KEY_CACHE is not None:
        return _OPENAI_KEY_CACHE

    _OPENAI_KEY_CACHE = os.getenv("OPENAI_API_KEY", "").strip()
    return _OPENAI_KEY_CACHE or None
