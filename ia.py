import streamlit as st
import requests
import os
import pandas as pd


@st.cache_data
def leerDatos():
    df = pd.read_csv("dataset.csv", index_col=0)
    return df


def get_dataset_context(df: pd.DataFrame) -> str:
    top_generos = ", ".join(df["track_genre"].value_counts().head(10).index.tolist())
    return f"""
Dataset de Spotify con {len(df):,} canciones.
Géneros disponibles (top 10): {top_generos}... (114 géneros en total)
Columnas: {', '.join(df.columns.tolist())}

Estadísticas generales:
- Popularidad promedio: {df['popularity'].mean():.1f} / 100
- Energía promedio: {df['energy'].mean():.2f}
- Bailabilidad promedio: {df['danceability'].mean():.2f}
- Positividad promedio (valence): {df['valence'].mean():.2f}
- Tempo promedio: {df['tempo'].mean():.1f} BPM
- Loudness promedio: {df['loudness'].mean():.1f} dB
- Géneros únicos: {df['track_genre'].nunique()}
- Artistas únicos: {df['artists'].nunique():,}
- Canciones explícitas: {df['explicit'].sum():,} ({df['explicit'].mean()*100:.1f}%)
"""


SYSTEM_PROMPT = """Eres un asistente experto en análisis musical y ciencia de datos, 
especializado en el dataset de Spotify. Ayudas a estudiantes de Ingeniería en Sistemas 
a entender conceptos de análisis exploratorio de datos, machine learning y sistemas 
de recomendación aplicados a música.

Puedes:
- Explicar características de audio de Spotify (danceability, energy, valence, tempo, etc.)
- Interpretar resultados del análisis exploratorio
- Explicar algoritmos de ML: regresión lineal, árboles de decisión, random forest
- Clarificar métricas: R², MAE, RMSE
- Hablar sobre géneros musicales y sus tendencias
- Explicar cómo funciona el filtrado por contenido en sistemas de recomendación
- Responder preguntas sobre el dataset de Spotify

Responde siempre en español, de manera clara, educativa y amigable. 
Usa ejemplos concretos del dataset cuando sea posible.
Sé conciso pero completo. Usa emojis ocasionalmente para hacer la respuesta más dinámica.
"""

SUGERENCIAS = [
    "¿Qué significa el campo 'valence' en Spotify?",
    "¿Qué género musical es el más bailable según el dataset?",
    "Explícame qué es el R² y cómo interpretarlo",
    "¿Cómo funciona el sistema de recomendación por contenido?",
    "¿Por qué algunas canciones tienen alta energía pero baja popularidad?",
    "¿Qué diferencia hay entre MAE y RMSE?",
    "¿Qué es la regresión lineal y cómo se aplica a datos musicales?",
    "¿Qué hace que una canción sea popular en Spotify?",
]


# ──────────────────────────────────────────────────────────────────────────────
def ia_interface():
    st.title("🧠 Asistente Musical con IA")
    st.caption("Potenciado por Claude AI · Responde preguntas sobre música, datos y modelos")

    df = leerDatos()
    dataset_ctx = get_dataset_context(df)
    system = SYSTEM_PROMPT + f"\n\nContexto del dataset actual:\n{dataset_ctx}"

    # ── API Key ───────────────────────────────────────────────────────────
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        with st.expander("🔑 Configurar API Key de Anthropic", expanded=True):
            api_key = st.text_input(
                "Introduce tu API Key:",
                type="password",
                help="Obtén tu clave en console.anthropic.com · Se usa solo en esta sesión.",
            )
            if not api_key:
                st.info(
                    "Para usar el asistente, necesitas una API Key de Anthropic. "
                    "También puedes definir la variable de entorno `ANTHROPIC_API_KEY` "
                    "antes de iniciar la app."
                )
                return

    # ── Historial ─────────────────────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Botón limpiar
    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        if st.button("🗑️ Limpiar chat"):
            st.session_state.chat_history = []
            st.rerun()
    with col_info:
        st.caption(f"Mensajes en el historial: {len(st.session_state.chat_history)}")

    # ── Sugerencias (solo al inicio) ──────────────────────────────────────
    if len(st.session_state.chat_history) == 0:
        st.markdown("### 💡 Preguntas sugeridas")
        cols = st.columns(2)
        for i, sug in enumerate(SUGERENCIAS):
            with cols[i % 2]:
                if st.button(sug, key=f"sug_{i}", use_container_width=True):
                    st.session_state.chat_history.append(
                        {"role": "user", "content": sug}
                    )
                    respuesta = llamar_claude(
                        messages=st.session_state.chat_history,
                        system=system,
                        api_key=api_key,
                    )
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": respuesta}
                    )
                    st.rerun()

    st.markdown("---")

    # ── Mostrar historial ─────────────────────────────────────────────────
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Input del usuario ─────────────────────────────────────────────────
    prompt = st.chat_input("Pregunta algo sobre música, el dataset o los modelos...")

    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = llamar_claude(
                    messages=st.session_state.chat_history,
                    system=system,
                    api_key=api_key,
                )
            st.markdown(respuesta)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": respuesta}
        )


# ──────────────────────────────────────────────────────────────────────────────
def llamar_claude(messages: list, system: str, api_key: str) -> str:
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "system": system,
                "messages": [
                    {"role": m["role"], "content": m["content"]}
                    for m in messages
                ],
            },
            timeout=30,
        )

        data = response.json()

        if response.status_code == 200:
            return data["content"][0]["text"]
        elif response.status_code == 401:
            return "❌ API Key inválida. Verifica que sea correcta en console.anthropic.com"
        elif response.status_code == 429:
            return "⏳ Límite de solicitudes alcanzado. Espera un momento e intenta de nuevo."
        else:
            error_msg = data.get("error", {}).get("message", "Error desconocido")
            return f"❌ Error {response.status_code}: {error_msg}"

    except requests.exceptions.Timeout:
        return "⏳ La solicitud tardó demasiado. Intenta de nuevo."
    except Exception as e:
        return f"❌ Error de conexión: {str(e)}"


if __name__ == "__main__":
    ia_interface()
