"""Streamlit app — Generador de etiquetas para búsquedas avanzadas en LinkedIn."""

import streamlit as st
from src.scraper import fetch_job_post
from src.tagger import generate_tags, openai_key_status

st.set_page_config(page_title="Generador de etiquetas LinkedIn", page_icon="🔖")
st.title("🔖 Generador de etiquetas para búsqueda directa")

st.markdown(
    "Ingresa el **enlace** a una oferta de trabajo y obtén una lista optimizada de etiquetas/hashtags para afinar tu búsqueda de candidatos en LinkedIn."
)

if not openai_key_status():
    st.error(
        "OPENAI_API_KEY no configurada. Añádela como variable de entorno o en `.streamlit/secrets.toml`."
    )
    st.stop()

# ----------------------------- UI principal ------------------------------ #
with st.form("form-url"):
    url = st.text_input("Enlace de la oferta", placeholder="https://…")
    max_titles = st.number_input(
        "Máximo de títulos y sinónimos",
        min_value=1,
        max_value=30,
        value=15,
        help="Número máximo de títulos y sinónimos del puesto a generar.",
    ) 
    max_companies = st.number_input(
        "Máximo de empresas relevantes",
        min_value=1,
        max_value=20,
        value=10,
        help="Número máximo de empresas relevantes donde suelen trabajar candidatos adecuados.",
    )
    max_keywords = st.number_input(
        "Máximo de palabras clave",
        min_value=1,
        max_value=50,
        value=20,
        help="Número máximo de keywords que describan habilidades, certificaciones y herramientas.",
    )

    submitted = st.form_submit_button("Generar etiquetas ✨")

if submitted and url:
    try:
        with st.spinner("Descargando y analizando la oferta…"):
            job_info = fetch_job_post(url)

        if not any(job_info.values()):
            st.warning("No se pudo extraer información relevante de la oferta.")
            st.stop()

        st.success("Información extraída correctamente ✔️")
        st.write("**Resumen extraído:**")
    

        with st.spinner("Solicitando etiquetas a OpenAI…"):
            tags = generate_tags(job_info, 
                                 max_titles=max_titles, 
                                 max_companies=max_companies, 
                                 max_keywords=max_keywords)

        if tags:
           
            st.subheader("Cargos (ES)")
            st.write(", ".join(tags["cargos_es"]))

            st.subheader("Cargos (EN)")
            st.write(", ".join(tags["cargos_en"]))

            st.subheader("Empresas")
            st.write(", ".join(tags["empresas"]))

            st.subheader("Palabras clave (ES)")
            st.write(", ".join(tags["palabras_clave_es"]))

            st.subheader("Palabras clave (EN)")
            st.write(", ".join(tags["palabras_clave_en"]))

            st.success("¡Listo! Usa estas etiquetas en búsqueda directa.")
        else:
            st.warning("No se generaron etiquetas. Revisa los parámetros o los límites del modelo.")

    except Exception as e:
        st.error(f"Ocurrió un problema: {e}")