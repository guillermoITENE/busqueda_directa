# Generador de Etiquetas LinkedIn

Aplicación Streamlit que:
1. **Raspa** los detalles de una oferta de trabajo (título + descripción).
2. Envía esa información a **OpenAI** para obtener una lista de etiquetas/hashtags.
3. Muestra las etiquetas para copiar/pegar en LinkedIn Recruiter.

## Instalación
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración de la clave OpenAI
```bash
export OPENAI_API_KEY="sk-..."
```
O bien crea `.streamlit/secrets.toml`:
```toml
[default]
OPENAI_API_KEY = "sk-..."
```

## Ejecución
```bash
streamlit run app.py
```