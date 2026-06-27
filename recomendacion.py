import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity


@st.cache_data
def leerDatos():
    df = pd.read_csv("dataset.csv", index_col=0)
    return df


AUDIO_FEATURES = [
    "danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo",
]

ETIQUETAS = {
    "danceability":     "Bailabilidad",
    "energy":           "Energía",
    "loudness":         "Volumen",
    "speechiness":      "Palabras Habladas",
    "acousticness":     "Nivel Acústico",
    "instrumentalness": "Instrumental",
    "liveness":         "En Vivo",
    "valence":          "Positividad",
    "tempo":            "Tempo (BPM)",
}


@st.cache_data
def preparar_genero(genero: str):
    """Devuelve el sub-dataframe del género y su matriz de similitud (coseno)."""
    df = leerDatos()
    sub = (
        df[df["track_genre"] == genero]
        .drop_duplicates(subset="track_name")
        .dropna(subset=AUDIO_FEATURES)
        .reset_index(drop=True)
    )
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(sub[AUDIO_FEATURES])
    sim_matrix = cosine_similarity(scaled)
    return sub, sim_matrix, scaler


# ──────────────────────────────────────────────────────────────────────────────
def recomendacion():
    st.title("Sistema de Recomendación Musical")
    st.caption("Basado en filtrado por contenido — características de audio de Spotify")

    modo = st.radio(
        "Modo:",
        ["Por canción similar", "Por mis preferencias"],
        horizontal=True,
    )
    st.markdown("---")

    if "Por canción similar" in modo:
        por_cancion()
    else:
        por_preferencias()


# ──────────────────────────────────────────────────────────────────────────────
def por_cancion():
    st.subheader("Canciones similares a una canción elegida")

    df = leerDatos()

    col1, col2 = st.columns(2)
    with col1:
        genero = st.selectbox(
            "Selecciona un género:",
            sorted(df["track_genre"].unique()),
        )
    sub, sim_matrix, _ = preparar_genero(genero)

    with col2:
        cancion = st.selectbox(
            "Selecciona una canción:",
            sub["track_name"].tolist(),
        )

    n = st.slider("Número de recomendaciones:", 5, 20, 10)

    if st.button("🔍 Buscar canciones similares", type="primary"):
        idx = sub[sub["track_name"] == cancion].index[0]
        scores = list(enumerate(sim_matrix[idx]))
        scores = sorted(
            [(i, s) for i, s in scores if i != idx],
            key=lambda x: x[1],
            reverse=True,
        )[:n]

        indices = [s[0] for s in scores]
        similitudes = [round(s[1], 4) for s in scores]

        recomendadas = sub.iloc[indices][
            ["track_name", "artists", "popularity",
             "danceability", "energy", "valence", "tempo"]
        ].copy()
        recomendadas.insert(0, "Similitud", similitudes)
        recomendadas = recomendadas.reset_index(drop=True)

        # Datos de la canción seleccionada
        info = sub.iloc[idx]
        st.markdown(f"### 🎧 Analizando: **{cancion}** — {info.get('artists', '')}")

        colA, colB, colC, colD = st.columns(4)
        with colA:
            st.metric("Bailabilidad", f"{info['danceability']:.2f}")
        with colB:
            st.metric("Energía", f"{info['energy']:.2f}")
        with colC:
            st.metric("Positividad", f"{info['valence']:.2f}")
        with colD:
            st.metric("Tempo", f"{info['tempo']:.0f} BPM")

        st.markdown(f"### 🎶 Top {n} canciones similares")
        st.dataframe(recomendadas, use_container_width=True, hide_index=True)

        # Radar del perfil de audio
        radar_features = [
            "danceability", "energy", "speechiness",
            "acousticness", "valence", "liveness",
        ]
        fig = px.line_polar(
            r=[info[f] for f in radar_features],
            theta=[ETIQUETAS.get(f, f) for f in radar_features],
            line_close=True,
            title=f"Perfil de Audio: {cancion}",
        )
        fig.update_traces(fill="toself", line_color="#1DB954")
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
def por_preferencias():
    st.subheader("Recomendaciones según mis preferencias")
    st.markdown("Ajusta los controles para describir el tipo de música que quieres escuchar:")

    col1, col2, col3 = st.columns(3)

    with col1:
        danceability = st.slider("Bailabilidad", 0.0, 1.0, 0.70, 0.05)
        energy = st.slider("Energía", 0.0, 1.0, 0.65, 0.05)
        valence = st.slider("Positividad", 0.0, 1.0, 0.55, 0.05)

    with col2:
        acousticness = st.slider("Nivel Acústico", 0.0, 1.0, 0.25, 0.05)
        instrumentalness = st.slider("Instrumental", 0.0, 1.0, 0.05, 0.05)
        speechiness = st.slider("Palabras Habladas", 0.0, 1.0, 0.10, 0.05)

    with col3:
        tempo = st.slider("Tempo (BPM)", 60, 220, 120, 5)
        min_pop = st.slider("Popularidad mínima", 0, 100, 30)
        n_rec = st.slider("Número de recomendaciones", 5, 20, 10)

    generos_filter = st.multiselect(
        "Filtrar por género (opcional, deja vacío para todos):",
        sorted(leerDatos()["track_genre"].unique()),
    )

    if st.button("🎵 Obtener Recomendaciones", type="primary"):
        df = leerDatos()

        df_f = df[df["popularity"] >= min_pop].dropna(subset=AUDIO_FEATURES).copy()
        df_f = df_f.drop_duplicates(subset="track_name")
        if generos_filter:
            df_f = df_f[df_f["track_genre"].isin(generos_filter)]

        if len(df_f) == 0:
            st.warning("No hay canciones con esos filtros. Ajusta los parámetros.")
            return

        if len(df_f) > 15000:
            df_f = df_f.sample(15000, random_state=42)

        df_f = df_f.reset_index(drop=True)

        # Vector de preferencias del usuario (en el espacio original)
        # Loudness: valor típico medio ~-9 dB; liveness: ~0.15
        user_row = pd.DataFrame([{
            "danceability": danceability,
            "energy": energy,
            "loudness": -9.0,
            "speechiness": speechiness,
            "acousticness": acousticness,
            "instrumentalness": instrumentalness,
            "liveness": 0.15,
            "valence": valence,
            "tempo": float(tempo),
        }])

        combined = pd.concat(
            [df_f[AUDIO_FEATURES], user_row], ignore_index=True
        )
        scaler = MinMaxScaler()
        combined_scaled = scaler.fit_transform(combined)

        songs_scaled = combined_scaled[:-1]
        user_scaled = combined_scaled[-1:].reshape(1, -1)

        sims = cosine_similarity(user_scaled, songs_scaled)[0]
        df_f["similitud"] = sims

        top = df_f.nlargest(n_rec, "similitud")[
            ["track_name", "artists", "track_genre", "popularity",
             "danceability", "energy", "valence", "tempo", "similitud"]
        ].reset_index(drop=True)
        top["similitud"] = top["similitud"].round(4)

        st.markdown(f"### Top {n_rec} canciones para ti")
        st.dataframe(top, use_container_width=True, hide_index=True)

        # Radar del perfil del usuario
        radar_feats = ["danceability", "energy", "speechiness",
                       "acousticness", "valence", "liveness", "instrumentalness"]
        radar_vals = [danceability, energy, speechiness,
                      acousticness, valence, 0.15, instrumentalness]

        fig = px.line_polar(
            r=radar_vals,
            theta=[ETIQUETAS.get(f, f) for f in radar_feats],
            line_close=True,
            title="Tu perfil de preferencias musicales",
        )
        fig.update_traces(fill="toself", line_color="#1DB954")
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        # Bar chart de las top canciones
        fig2 = px.bar(
            top.sort_values("similitud"),
            x="similitud", y="track_name",
            orientation="h",
            title="Similitud con tu perfil",
            template="plotly_white",
            color="popularity",
            color_continuous_scale="Viridis",
            labels={"track_name": "Canción", "similitud": "Similitud"},
        )
        st.plotly_chart(fig2, use_container_width=True)


if __name__ == "__main__":
    recomendacion()
