import streamlit as st
import feedparser
import requests
import pandas as pd
import plotly.express as px
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

ANALYZER = SentimentIntensityAnalyzer()

COLOR_MAP = {
    "Positivo": "#1DB954",
    "Neutral":  "#FFA500",
    "Negativo": "#FF4444",
}

FUENTES = {
    "Reddit — r/Music":         "https://www.reddit.com/r/Music/{tipo}.rss?limit={limite}",
    "Reddit — r/spotify":       "https://www.reddit.com/r/spotify/{tipo}.rss?limit={limite}",
    "Reddit — r/hiphopheads":   "https://www.reddit.com/r/hiphopheads/{tipo}.rss?limit={limite}",
    "Reddit — r/popheads":      "https://www.reddit.com/r/popheads/{tipo}.rss?limit={limite}",
    "Reddit — r/indieheads":    "https://www.reddit.com/r/indieheads/{tipo}.rss?limit={limite}",
    "Reddit — Búsqueda global": "https://www.reddit.com/search.rss?q={busqueda}&limit={limite}",
    "Pitchfork — Reseñas":      "https://pitchfork.com/rss/reviews/albums/",
    "NME — Noticias musicales": "https://www.nme.com/feed",
}


# ──────────────────────────────────────────────────────────────────────────────
def limpiar_html(texto: str) -> str:
    """Elimina etiquetas HTML y caracteres raros del texto."""
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


# ──────────────────────────────────────────────────────────────────────────────
def scrape_rss(url: str) -> list:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        feed = feedparser.parse(url, request_headers=headers)
        posts = []

        for entry in feed.entries:
            titulo  = limpiar_html(entry.get("title",   ""))
            resumen = limpiar_html(entry.get("summary", "") or
                                   entry.get("description", ""))
            resumen = resumen[:400]
            texto   = f"{titulo}. {resumen}" if resumen else titulo

            # Fecha
            fecha = ""
            if entry.get("published"):
                try:
                    from email.utils import parsedate_to_datetime
                    fecha = parsedate_to_datetime(
                        entry["published"]
                    ).strftime("%Y-%m-%d")
                except Exception:
                    fecha = entry["published"][:10]

            posts.append({
                "titulo":      titulo,
                "texto":       texto,
                "autor":       entry.get("author", "N/A"),
                "puntuacion":  0,
                "comentarios": 0,
                "fecha":       fecha,
                "permalink":   entry.get("link", ""),
            })

        return posts

    except Exception as e:
        st.error(f"Error al obtener el feed: {e}")
        return []


# ──────────────────────────────────────────────────────────────────────────────
def analizar_sentimientos(posts: list) -> pd.DataFrame:
    df = pd.DataFrame(posts)
    registros = []

    for texto in df["texto"]:
        sc   = ANALYZER.polarity_scores(str(texto))
        comp = sc["compound"]
        if comp >= 0.05:
            etiqueta = "Positivo"
        elif comp <= -0.05:
            etiqueta = "Negativo"
        else:
            etiqueta = "Neutral"

        registros.append({
            "neg":        round(sc["neg"], 4),
            "neu":        round(sc["neu"], 4),
            "pos":        round(sc["pos"], 4),
            "compound":   round(comp, 4),
            "sentimiento": etiqueta,
        })

    return pd.concat([df, pd.DataFrame(registros)], axis=1)


# ──────────────────────────────────────────────────────────────────────────────
def sentimientos():
    st.title("Análisis de Sentimientos y Scraping")
    st.caption("Lee opiniones de Reddit y medios musicales · Analiza su sentimiento con VADER")

    # ── Configuración ─────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        fuente = st.selectbox("Fuente:", list(FUENTES.keys()))

    with col2:
        tipo   = st.selectbox("Ordenar por:", ["hot", "top", "new"])

    with col3:
        limite = st.slider("Número de posts:", 10, 100, 40)

    busqueda = ""
    if "Búsqueda global" in fuente:
        busqueda = st.text_input(
            "Término de búsqueda:",
            value="spotify music",
            placeholder="Ej: Taylor Swift, playlist…",
        )
        if not busqueda.strip():
            st.warning("Escribe un término para la búsqueda global.")
            return

    if st.button("Obtener y Analizar Opiniones", type="primary"):

        # Construir URL
        url_template = FUENTES[fuente]
        url = url_template.format(
            tipo=tipo,
            limite=limite,
            busqueda=requests.utils.quote(busqueda) if busqueda else "",
        )

        with st.spinner(f"Conectando con {fuente}…"):
            posts = scrape_rss(url)

        # Limitar al número pedido
        posts = posts[:limite]

        if not posts:
            st.error(
                "No se obtuvieron publicaciones. "
                "Intenta con otra fuente o término de búsqueda."
            )
            return

        st.success(f"Se obtuvieron **{len(posts)}** publicaciones de **{fuente}**")

        df = analizar_sentimientos(posts)
        mostrar_resultados(df, fuente)


# ──────────────────────────────────────────────────────────────────────────────
def mostrar_resultados(df: pd.DataFrame, fuente: str):
    st.markdown("---")

    positivos = (df["sentimiento"] == "Positivo").sum()
    neutrales  = (df["sentimiento"] == "Neutral").sum()
    negativos  = (df["sentimiento"] == "Negativo").sum()
    avg_comp   = df["compound"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Positivos",  positivos,
              f"{positivos / len(df) * 100:.1f}%")
    c2.metric("Neutrales",  neutrales,
              f"{neutrales / len(df) * 100:.1f}%")
    c3.metric("Negativos",  negativos,
              f"{negativos / len(df) * 100:.1f}%")
    c4.metric(
        "Score Promedio", f"{avg_comp:+.3f}",
        "Positivo" if avg_comp >= 0.05 else
        ("Negativo" if avg_comp <= -0.05 else "Neutral"),
    )

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(
        ["Publicaciones", "Análisis", "Distribución"]
    )

    # ── Tab 1 ─────────────────────────────────────────────────────────────
    with tab1:
        st.subheader(f"Publicaciones de {fuente}")

        filtro = st.multiselect(
            "Filtrar por sentimiento:",
            ["Positivo", "Neutral", "Negativo"],
            default=["Positivo", "Neutral", "Negativo"],
        )
        df_f = df[df["sentimiento"].isin(filtro)] if filtro else df

        st.dataframe(
            df_f[["titulo", "autor", "fecha", "sentimiento", "compound"]]
            .rename(columns={
                "titulo":      "Título / Titular",
                "autor":       "Autor",
                "fecha":       "Fecha",
                "sentimiento": "Sentimiento",
                "compound":    "Score",
            }),
            use_container_width=True,
            hide_index=True,
        )

    # ── Tab 2 ─────────────────────────────────────────────────────────────
    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            vc = df["sentimiento"].value_counts()
            fig_pie = px.pie(
                values=vc.values, names=vc.index,
                title="Distribución de Sentimientos",
                template="plotly_white",
                color=vc.index,
                color_discrete_map=COLOR_MAP,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            fig_bar = px.bar(
                x=vc.index, y=vc.values,
                title="Cantidad por Sentimiento",
                labels={"x": "Sentimiento", "y": "Cantidad"},
                template="plotly_white",
                color=vc.index,
                color_discrete_map=COLOR_MAP,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("#### Más positivos")
            st.dataframe(
                df.nlargest(5, "compound")[["titulo", "compound"]]
                .rename(columns={"titulo": "Título", "compound": "Score"}),
                use_container_width=True, hide_index=True,
            )
        with col4:
            st.markdown("#### Más negativos")
            st.dataframe(
                df.nsmallest(5, "compound")[["titulo", "compound"]]
                .rename(columns={"titulo": "Título", "compound": "Score"}),
                use_container_width=True, hide_index=True,
            )

    # ── Tab 3 ─────────────────────────────────────────────────────────────
    with tab3:
        fig_hist = px.histogram(
            df, x="compound", nbins=20,
            title="Distribución de Scores de Sentimiento",
            labels={"compound": "Score (−1 a 1)"},
            template="plotly_white",
            color_discrete_sequence=["#1DB954"],
        )
        fig_hist.add_vline(x=0.05,  line_dash="dash",
                           line_color="green", annotation_text="↑ Positivo")
        fig_hist.add_vline(x=-0.05, line_dash="dash",
                           line_color="red",   annotation_text="↓ Negativo")
        st.plotly_chart(fig_hist, use_container_width=True)

        if df["fecha"].nunique() > 1:
            df_time = (
                df.groupby("fecha")["compound"]
                .mean().reset_index()
                .rename(columns={"compound": "Score Promedio", "fecha": "Fecha"})
            )
            fig_line = px.line(
                df_time, x="Fecha", y="Score Promedio",
                title="Sentimiento Promedio por Fecha",
                template="plotly_white", markers=True,
                color_discrete_sequence=["#1DB954"],
            )
            fig_line.add_hline(y=0, line_dash="dot", line_color="gray")
            st.plotly_chart(fig_line, use_container_width=True)

        df_stacked = (
            df.groupby(["fecha", "sentimiento"])
            .size().reset_index(name="cantidad")
        )
        fig_stack = px.bar(
            df_stacked, x="fecha", y="cantidad",
            color="sentimiento",
            title="Posts por Sentimiento y Fecha",
            labels={"fecha": "Fecha", "cantidad": "Cantidad"},
            template="plotly_white",
            color_discrete_map=COLOR_MAP,
            barmode="stack",
        )
        st.plotly_chart(fig_stack, use_container_width=True)


if __name__ == "__main__":
    sentimientos()
