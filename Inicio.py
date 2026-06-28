import streamlit as st
import base64
import os
from eda import eda
from ml import ml
from recomendacion import recomendacion
from ia import ia_interface
from carga_archivos import carga_archivos
from sentimientos import sentimientos

NOMBRE      = "José Angel Arias Ramírez"
CARRERA     = "Ingenieria en Sistemas y Redes Informaticas"
UNIVERSIDAD = "Universidad Gerardo Barrios"
CURSO       = "Tecnica Electiva I - Ciencia de Datos - Ciclo I-2026"
VIDEO_URL   = "https://youtu.be/fn82E1ppwXU"
FOTO_PATH   = "foto.jpg"       


def get_avatar_html() -> str:
    """Devuelve el HTML del avatar: imagen real si existe, emoji si no."""
    if FOTO_PATH and os.path.exists(FOTO_PATH):
        with open(FOTO_PATH, "rb") as f:
            datos = base64.b64encode(f.read()).decode()
        ext = FOTO_PATH.rsplit(".", 1)[-1].lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
        return f'<img src="data:{mime};base64,{datos}" style="width:100%;height:100%;object-fit:cover;" />'
    return "&#129489;"   
BIO = """
Estudiante de Ingenieria en Sistemas y Redes Informaticas apasionado por la ciencia de datos
y el analisis de informacion. Este portafolio presenta un analisis completo de mas de 114,000
canciones de Spotify, abarcando exploracion de datos, modelos de aprendizaje automatico,
sistemas de recomendacion musical, analisis de sentimientos y una interfaz de inteligencia
artificial. El objetivo es demostrar competencias en Python, Streamlit, scikit-learn y
visualizacion de datos aplicadas a un problema real del mundo musical.
"""


def aplicar_estilos():
    st.markdown("""
    <style>
    .hero-wrap {
        display: flex; align-items: center; gap: 2.5rem; padding: 1.5rem 0 2rem;
    }
    .avatar-ring {
        width: 160px; height: 160px; border-radius: 50%;
        border: 4px solid #1DB954; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        background: #1E1E1E; font-size: 4.5rem; overflow: hidden;
    }
    .hero-text h1 { font-size: 2.4rem; font-weight: 800; margin: 0 0 .25rem; color: #FFFFFF; }
    .hero-text .green { color: #1DB954; font-size: 1rem; font-weight: 600; }
    .hero-text .gray  { color: #B3B3B3; font-size: .88rem; margin-top: .2rem; }
    .bio-box {
        background: #1E1E1E; border-left: 4px solid #1DB954;
        border-radius: 0 10px 10px 0; padding: 1.1rem 1.4rem;
        color: #CCCCCC; line-height: 1.75; font-size: .96rem; margin: 1.1rem 0;
    }
    .badge {
        display: inline-block; background: #121212;
        color: #1DB954; border: 1px solid #1DB954;
        border-radius: 20px; padding: .18rem .8rem;
        font-size: .77rem; margin: .2rem .12rem;
    }
    .mod-card {
        background: #1E1E1E; border: 1px solid #282828;
        border-radius: 14px; padding: 1.3rem 1.1rem;
        height: 100%; margin-bottom: .5rem;
    }
    .mod-card h4 { color: #1DB954; margin: .4rem 0 .35rem; font-size: .98rem; }
    .mod-card p  { color: #B3B3B3; font-size: .84rem; margin: 0; line-height: 1.5; }
    .video-ph {
        background: #1E1E1E; border: 2px dashed #1DB954;
        border-radius: 14px; padding: 3rem 2rem;
        text-align: center; color: #B3B3B3;
    }
    .video-ph h3 { color: #FFFFFF; margin: 0 0 .5rem; }
    .sp-hr { border: none; border-top: 1px solid #282828; margin: 2rem 0; }
    .port-footer {
        text-align: center; color: #535353;
        font-size: .8rem; padding: 2rem 0 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title=f"Portafolio DS - {NOMBRE}",
        page_icon="🎵",
        layout="wide",
    )
    aplicar_estilos()

    with st.sidebar:
        st.markdown(
            "<div style='text-align:center;padding:.5rem 0 .2rem'>"
            "<span style='font-size:1.8rem'>🎵</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='text-align:center;font-weight:700;color:#FFFFFF;"
            f"font-size:.92rem'>{NOMBRE}</div>"
            f"<div style='text-align:center;color:#1DB954;font-size:.76rem;"
            f"margin-bottom:1rem'>Portafolio - Ciencia de Datos</div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        menu = st.selectbox(
            "Navegar a:",
            ("INICIO", "EDA", "ML", "RECOMENDACION",
             "CARGA DE ARCHIVOS", "SENTIMIENTOS", "IA"),
        )
        st.markdown("---")
        st.markdown(
            f"<div style='color:#535353;font-size:.74rem;line-height:1.6'>"
            f"{UNIVERSIDAD}<br>{CARRERA}<br>{CURSO}</div>",
            unsafe_allow_html=True,
        )

    if menu == "INICIO":
        pagina_inicio()
    elif menu == "EDA":
        eda()
    elif menu == "ML":
        ml()
    elif menu == "RECOMENDACION":
        recomendacion()
    elif menu == "CARGA DE ARCHIVOS":
        carga_archivos()
    elif menu == "SENTIMIENTOS":
        sentimientos()
    elif menu == "IA":
        ia_interface()


def mod_card(titulo, desc):
    return f"""
    <div class="mod-card">
        <h4>{titulo}</h4>
        <p>{desc}</p>
    </div>
    """


def pagina_inicio():
    # ── HERO ─────────────────────────────────────────────────────────────
    avatar = get_avatar_html()
    st.markdown(f"""
    <div class="hero-wrap">
        <div class="avatar-ring">{avatar}</div>
        <div class="hero-text">
            <h1>{NOMBRE}</h1>
            <div class="green">{UNIVERSIDAD}</div>
            <div class="gray">{CARRERA} &nbsp;|&nbsp; {CURSO}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── BIO ───────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="bio-box">{BIO.strip()}</div>',
        unsafe_allow_html=True,
    )

    tecnologias = [
        "Python", "Streamlit", "Pandas", "NumPy", "Plotly",
        "scikit-learn", "VADER NLP", "Reddit API", "Claude AI",
    ]
    badges = "".join(f'<span class="badge">{t}</span>' for t in tecnologias)
    st.markdown(
        f"<div style='margin:.5rem 0 1.5rem'>{badges}</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="sp-hr">', unsafe_allow_html=True)

    # ── VIDEO ─────────────────────────────────────────────────────────────
    st.markdown("## Demo - Data Storytelling")
    if VIDEO_URL:
        st.video(VIDEO_URL)
    else:
        st.markdown("""
        <div class="video-ph">
            <h3>Video de demostracion proximamente</h3>
            <p>Pega tu URL de YouTube en la variable <code>VIDEO_URL</code>
            al inicio de <code>Inicio.py</code>.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="sp-hr">', unsafe_allow_html=True)

    # ── MODULOS ──── sin loop, columnas explícitas ─────────────────────────
    st.markdown("## Modulos del Portafolio")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(mod_card(
            "Analisis Exploratorio de Datos",
            "Estadisticas, distribuciones, graficador dinamico e hipotesis "
            "validadas sobre el dataset de Spotify."
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(mod_card(
            "Aprendizaje Automatico",
            "Regresion Lineal, Arbol de Decision y Random Forest con "
            "seleccion de variables, split de datos y metricas en tiempo real."
        ), unsafe_allow_html=True)

    with col3:
        st.markdown(mod_card(
            "Recomendacion Musical",
            "Filtrado por contenido basado en similitud del coseno: "
            "recomienda canciones por cancion elegida o preferencias del usuario."
        ), unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(mod_card(
            "Carga de Archivos",
            "Analisis automatico de cualquier CSV, Excel o JSON: "
            "estadisticas, tipos de columna y 6 tipos de grafico interactivos."
        ), unsafe_allow_html=True)

    with col5:
        st.markdown(mod_card(
            "Analisis de Sentimientos",
            "Scraping de HackerNews y Reddit con VADER NLP: clasifica "
            "opiniones como Positivo, Neutral o Negativo con visualizaciones."
        ), unsafe_allow_html=True)

    with col6:
        st.markdown(mod_card(
            "Interfaz IA",
            "Asistente musical potenciado por Claude AI: responde preguntas "
            "sobre el dataset, los modelos y conceptos de ciencia de datos."
        ), unsafe_allow_html=True)

    st.markdown('<hr class="sp-hr">', unsafe_allow_html=True)

    # ── METRICAS ──────────────────────────────────────────────────────────
    st.markdown("## Dataset Analizado")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Canciones", "114,000+")
    c2.metric("Generos", "114")
    c3.metric("Caracteristicas de Audio", "13")
    c4.metric("Artistas Unicos", "31,000+")

    # ── FOOTER ────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="port-footer">'
        f'2026 {NOMBRE} &nbsp;|&nbsp; {UNIVERSIDAD} &nbsp;|&nbsp; '
        f'Construido con Streamlit y Python'
        f'</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
