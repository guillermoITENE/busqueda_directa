from __future__ import annotations
import os
from typing import Optional
import streamlit as st

_OPENAI_KEY_CACHE: Optional[str] = None


def get_openai_key() -> str | None:
    """Devuelve la clave de OpenAI buscando primero en st.secrets y después en env."""
    global _OPENAI_KEY_CACHE
    if _OPENAI_KEY_CACHE is not None:
        return _OPENAI_KEY_CACHE

    if "OPENAI_API_KEY" in st.secrets:
        _OPENAI_KEY_CACHE = st.secrets["OPENAI_API_KEY"].strip()
    else:
        _OPENAI_KEY_CACHE = os.getenv("OPENAI_API_KEY", "").strip()

    return _OPENAI_KEY_CACHE or None