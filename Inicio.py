import streamlit as st
from eda import eda
from ml import ml
from recomendacion import recomendacion
from ia import ia_interface
from carga_archivos import carga_archivos
from sentimientos import sentimientos

# ── Constantes personalizables ────────────────────────────────────────────────
NOMBRE        = "Tu Nombre Completo"          # ← cambia esto
CARRERA       = "Ingeniería en Sistemas y Redes Informáticas"
UNIVERSIDAD   = "Universidad Gerardo Barrios"
CURSO         = "Técnica Electiva I — Ciencia de Datos · Ciclo I-2026"
VIDEO_URL     = ""                            
FOTO_PATH     = ""                            
BIO = """
Estudiante de Ingeniería en Sistemas y Redes Informáticas apasionado por la ciencia de datos
y el análisis de información. Este portafolio presenta un análisis completo de más de 114,000
canciones de Spotify, abarcando exploración de datos, modelos de aprendizaje automático,
sistemas de recomendación musical, análisis de sentimientos y una interfaz de inteligencia
artificial. El objetivo es demostrar competencias en Python, Streamlit, scikit-learn y
visualización de datos aplicadas a un problema real del mundo musical.
"""

# ─────────────────────────────────────────────────────────────────────────────
def aplicar_estilos():
    st.markdown("""
    <style>
    /* ── Fuente ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── Hero ── */
    .hero-wrap {
        display: flex; align-items: center; gap: 2.5rem;
        padding: 1.5rem 0 2rem;
    }
    .avatar-ring {
        width: 170px; height: 170px; border-radius: 50%;
        border: 4px solid #1DB954; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        background: #1E1E1E; font-size: 5rem; overflow: hidden;
    }
    .avatar-ring img { width: 100%; height: 100%; object-fit: cover; }
    .hero-text h1 {
        font-size: 2.6rem; font-weight: 800;
        margin: 0 0 .25rem; color: #FFFFFF;
    }
    .hero-text .green { color: #1DB954; font-size: 1.05rem; font-weight: 600; }
    .hero-text .gray  { color: #B3B3B3; font-size: .9rem;  margin-top: .2rem; }

    /* ── Bio ── */
    .bio-box {
        background: #1E1E1E; border-left: 4px solid #1DB954;
        border-radius: 0 10px 10px 0; padding: 1.2rem 1.5rem;
        color: #CCCCCC; line-height: 1.75; font-size: .97rem;
        margin: 1.2rem 0;
    }

    /* ── Badges ── */
    .badge {
        display: inline-block; background: #121212;
        color: #1DB954; border: 1px solid #1DB954;
        border-radius: 20px; padding: .2rem .85rem;
        font-size: .78rem; margin: .2rem .15rem;
    }

    /* ── Tarjetas de módulo ── */
    .mod-card {
        background: #1E1E1E; border: 1px solid #282828;
        border-radius: 14px; padding: 1.4rem 1.2rem;
        transition: border-color .25s, transform .2s;
        height: 100%; cursor: default;
    }
    .mod-card:hover { border-color: #1DB954; transform: translateY(-3px); }
    .mod-card .icon { font-size: 2rem; }
    .mod-card h4 { color: #1DB954; margin: .6rem 0 .4rem; font-size: 1rem; }
    .mod-card p  { color: #B3B3B3; font-size: .85rem; margin: 0; line-height: 1.5; }

    /* ── Video placeholder ── */
    .video-ph {
        background: #1E1E1E; border: 2px dashed #1DB954;
        border-radius: 14px; padding: 3.5rem 2rem;
        text-align: center; color: #B3B3B3;
    }
    .video-ph .icon { font-size: 3.5rem; display: block; margin-bottom: .8rem; }
    .video-ph h3 { color: #FFFFFF; margin: 0 0 .5rem; }

    /* ── Separador ── */
    .sp-hr { border: none; border-top: 1px solid #282828; margin: 2rem 0; }

    /* ── Footer ── */
    .port-footer {
        text-align: center; color: #535353;
        font-size: .8rem; padding: 2rem 0 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title=f"Portafolio DS — {NOMBRE}",
        page_icon="🎵",
        layout="wide",
    )

    aplicar_estilos()

    # ── Sidebar ───────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            "<div style='text-align:center;padding:.5rem 0 .2rem'>"
            "<span style='font-size:2rem'>🎵</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='text-align:center;font-weight:700;"
            f"color:#FFFFFF;font-size:.95rem'>{NOMBRE}</div>"
            f"<div style='text-align:center;color:#1DB954;font-size:.78rem;"
            f"margin-bottom:1rem'>Portafolio · Ciencia de Datos</div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        menu = st.selectbox(
            "Navegar a:",
            (
                "INICIO",
                "EDA",
                "ML",
                "RECOMENDACIÓN",
                "CARGA DE ARCHIVOS",
                "SENTIMIENTOS",
                "IA",
            ),
        )

        st.markdown("---")
        st.markdown(
            f"<div style='color:#535353;font-size:.75rem;line-height:1.6'>"
            f"{UNIVERSIDAD}<br>{CARRERA}<br>{CURSO}</div>",
            unsafe_allow_html=True,
        )

    # ── Routing ──────────────────────────────────────────────────────────
    if "INICIO" in menu:
        pagina_inicio()
    elif "EDA" in menu:
        eda()
    elif "ML" in menu:
        ml()
    elif "RECOMENDACIÓN" in menu:
        recomendacion()
    elif "CARGA" in menu:
        carga_archivos()
    elif "SENTIMIENTOS" in menu:
        sentimientos()
    elif "IA" in menu:
        ia_interface()


# ─────────────────────────────────────────────────────────────────────────────
def pagina_inicio():

    
    if FOTO_PATH:
        avatar_html = f'<img src="{FOTO_PATH}" alt="foto"/>'
    else:
        avatar_html = "🧑‍💻"

    st.markdown(f"""
    <div class="hero-wrap">
        <div class="avatar-ring">{avatar_html}</div>
        <div class="hero-text">
            <h1>{NOMBRE}</h1>
            <div class="green">📍 {UNIVERSIDAD}</div>
            <div class="gray">{CARRERA} &nbsp;|&nbsp; {CURSO}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── BIO ───────────────────────────────────────────────────────────────
    st.markdown(f'<div class="bio-box">{BIO.strip()}</div>', unsafe_allow_html=True)

    # ── BADGES ───────────────────────────────────────────────────────────
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
    st.markdown("## Demo — Data Storytelling")

    if VIDEO_URL:
        st.video(VIDEO_URL)
    else:
        st.markdown("""
        <div class="video-ph">
            <span class="icon">🎥</span>
            <h3>Video de demostración próximamente</h3>
            <p>Aquí se incrustará el video de Data Storytelling (5–7 min).<br>
            Para agregarlo, pega tu URL de YouTube en la variable <code>VIDEO_URL</code>
            al inicio de <code>Inicio.py</code>.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="sp-hr">', unsafe_allow_html=True)

    # ── MÓDULOS ───────────────────────────────────────────────────────────
    st.markdown("## Módulos del Portafolio")

    modulos = [
        ("EDA",
         "Análisis exploratorio completo: estadísticas, distribuciones, "
         "graficador dinámico e hipótesis validadas sobre el dataset de Spotify."),
        ("Aprendizaje Automático",
         "Modelos predictivos (Regresión Lineal, Árbol de Decisión, Random Forest) "
         "con selección de variables, split de datos y métricas en tiempo real."),
        ("Recomendación Musical",
         "Sistema de filtrado por contenido basado en similitud coseno: "
         "recomienda canciones por canción elegida o por preferencias del usuario."),
        ("Carga de Archivos",
         "Análisis automático de cualquier CSV, Excel o JSON: "
         "estadísticas, tipos de columna y 6 tipos de gráfico interactivos."),
        ("Sentimientos",
         "Scraping de Reddit con análisis de sentimiento VADER: "
         "clasifica posts como Positivo, Neutral o Negativo con visualizaciones."),
        ("Interfaz IA",
         "Asistente musical potenciado por Claude AI: responde preguntas "
         "sobre el dataset, los modelos y conceptos de ciencia de datos."),
    ]

    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]

    for i, (icon, titulo, desc) in enumerate(modulos):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="mod-card">
                <div class="icon">{icon}</div>
                <h4>{titulo}</h4>
                <p>{desc}</p>
            </div>
            <br>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="sp-hr">', unsafe_allow_html=True)

    # ── DATASET ──────────────────────────────────────────────────────────
    st.markdown("## Dataset Analizado")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Canciones", "114,000+")
    c2.metric("Géneros", "114")
    c3.metric("Características", "13")
    c4.metric("Artistas", "31,000+")

    # ── FOOTER ───────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="port-footer">'
        f'© 2026 {NOMBRE} &nbsp;·&nbsp; {UNIVERSIDAD} &nbsp;·&nbsp; '
        f'Construido con Streamlit & Python'
        f'</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
