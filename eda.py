import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


@st.cache_data
def leerDatos():
    df = pd.read_csv("dataset.csv", index_col=0)
    return df


# ──────────────────────────────────────────────────────────────────────────────
def eda():
    st.title("Análisis Exploratorio de Datos")
    st.caption("Dataset: Spotify Tracks – más de 114,000 canciones")

    df = leerDatos()

    submenu = st.selectbox(
        "Selecciona una sección:",
        [
            "Descripción del Dataset",
            "Descripción de Campos",
            "Navegador del Dataset",
            "Buscador de Canciones (Bonus)",
            "Graficador Exploratorio",
            "Hipótesis",
        ],
    )

    st.markdown("---")

    if submenu == "Descripción del Dataset":
        descripcion_dataset(df)
    elif submenu == "Descripción de Campos":
        descripcion_campos(df)
    elif submenu == "Navegador del Dataset":
        navegador(df)
    elif submenu == "Buscador de Canciones (Bonus)":
        buscador(df)
    elif submenu == "Graficador Exploratorio":
        graficador(df)
    elif submenu == "Hipótesis":
        hipotesis(df)


# ──────────────────────────────────────────────────────────────────────────────
def descripcion_dataset(df):
    st.subheader("Descripción General del Dataset")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Registros", f"{len(df):,}")
    with col2:
        st.metric("Total de Columnas", len(df.columns))
    with col3:
        st.metric("Géneros Únicos", df["track_genre"].nunique())
    with col4:
        st.metric("Artistas Únicos", df["artists"].nunique())

    st.markdown("### Diccionario de Datos")

    descripciones = {
        "track_id": ("ID único de Spotify para cada canción", "object"),
        "artists": ("Nombre del artista o artistas", "object"),
        "album_name": ("Nombre del álbum al que pertenece la canción", "object"),
        "track_name": ("Nombre de la canción", "object"),
        "popularity": (
            "Popularidad (0–100). Se calcula con base en reproducciones recientes.",
            "int",
        ),
        "duration_ms": ("Duración de la canción en milisegundos", "int"),
        "explicit": (
            "Si la canción contiene contenido explícito (True/False)",
            "bool",
        ),
        "danceability": (
            "Qué tan adecuada es la canción para bailar (0 = poco bailable, 1 = muy bailable)",
            "float",
        ),
        "energy": (
            "Medida de intensidad y actividad perceptiva (0 = tranquila, 1 = muy enérgica)",
            "float",
        ),
        "key": ("Clave musical de la canción (0=Do, 1=Do#, … 11=Si)", "int"),
        "loudness": ("Volumen promedio en decibelios (dB). Suele ser negativo.", "float"),
        "mode": ("Modalidad: Mayor (1) o Menor (0)", "int"),
        "speechiness": (
            "Presencia de palabras habladas. >0.66 = probablemente hablada.",
            "float",
        ),
        "acousticness": (
            "Nivel de confianza de que la canción es acústica (0–1)",
            "float",
        ),
        "instrumentalness": (
            "Predicción de si la canción no contiene voces (>0.5 = probablemente instrumental)",
            "float",
        ),
        "liveness": (
            "Detecta presencia de audiencia. >0.8 = probablemente en vivo.",
            "float",
        ),
        "valence": (
            "Positividad musical (0 = triste/enojada, 1 = alegre/eufórica)",
            "float",
        ),
        "tempo": ("Tempo estimado en pulsaciones por minuto (BPM)", "float"),
        "time_signature": (
            "Compás de la canción (número de tiempos por compás)",
            "int",
        ),
        "track_genre": ("Género musical de la canción", "object"),
    }

    desc_df = pd.DataFrame(
        [
            {"Columna": col, "Descripción": desc, "Tipo": tipo}
            for col, (desc, tipo) in descripciones.items()
            if col in df.columns
        ]
    )
    st.dataframe(desc_df, use_container_width=True, hide_index=True)

    st.markdown("### Valores Nulos")
    nulls = df.isnull().sum()
    nulls_df = pd.DataFrame(
        {"Columna": nulls.index, "Valores Nulos": nulls.values}
    )
    nulls_df = nulls_df[nulls_df["Valores Nulos"] > 0]
    if len(nulls_df) == 0:
        st.success("El dataset no presenta valores nulos.")
    else:
        st.dataframe(nulls_df, use_container_width=True, hide_index=True)

    st.markdown("### Distribución por Género (Top 20)")
    top_generos = df["track_genre"].value_counts().head(20)
    fig = px.bar(
        x=top_generos.index,
        y=top_generos.values,
        labels={"x": "Género", "y": "Canciones"},
        title="Top 20 géneros con más canciones",
        template="plotly_white",
        color=top_generos.values,
        color_continuous_scale="Viridis",
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
def descripcion_campos(df):
    st.subheader("Descripción de Campos")

    campos_cuantitativos = [
        "popularity", "duration_ms", "danceability", "energy",
        "loudness", "speechiness", "acousticness", "instrumentalness",
        "liveness", "valence", "tempo",
    ]
    campos_categoricos = ["track_genre", "explicit", "key", "mode", "time_signature"]

    tipo = st.radio("Tipo de campo:", ["Cuantitativo", "Categórico"], horizontal=True)

    if tipo == "Cuantitativo":
        campo = st.selectbox("Selecciona un campo:", campos_cuantitativos)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"#### Estadísticas de `{campo}`")
            st.dataframe(df[[campo]].describe().round(4))
        with col2:
            stats = df[campo].describe()
            skew = df[campo].skew()
            if abs(skew) < 0.5:
                skew_desc = "distribución aproximadamente simétrica"
            elif skew > 0:
                skew_desc = "distribución sesgada a la derecha (cola larga hacia valores altos)"
            else:
                skew_desc = "distribución sesgada a la izquierda (cola larga hacia valores bajos)"

            st.markdown("#### Interpretación")
            st.write(f"- **Promedio:** {stats['mean']:.4f}")
            st.write(f"- **Mediana (50%):** {stats['50%']:.4f}")
            st.write(f"- **Mínimo:** {stats['min']:.4f}")
            st.write(f"- **Máximo:** {stats['max']:.4f}")
            st.write(f"- **Desviación estándar:** {stats['std']:.4f}")
            st.write(f"- **Asimetría:** {skew:.4f} → {skew_desc}")

    else:
        campo = st.selectbox("Selecciona un campo:", campos_categoricos)
        vc = df[campo].value_counts()
        vc_df = pd.DataFrame({"Valor": vc.index, "Cantidad": vc.values})

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Valores únicos", df[campo].nunique())
            if campo == "track_genre":
                st.markdown("**Top 20 géneros:**")
                st.dataframe(vc_df.head(20), use_container_width=True, hide_index=True)
            else:
                st.dataframe(vc_df, use_container_width=True, hide_index=True)

        with col2:
            if campo == "explicit":
                fig = px.pie(
                    vc_df,
                    names="Valor",
                    values="Cantidad",
                    title="Contenido Explícito",
                    template="plotly_white",
                    color_discrete_sequence=["#1DB954", "#FF4444"],
                )
            elif campo == "track_genre":
                fig = px.bar(
                    vc_df.head(20),
                    x="Valor",
                    y="Cantidad",
                    title="Top 20 Géneros",
                    template="plotly_white",
                    color="Cantidad",
                    color_continuous_scale="Viridis",
                )
                fig.update_xaxes(tickangle=45)
            else:
                fig = px.bar(
                    vc_df,
                    x="Valor",
                    y="Cantidad",
                    title=f"Distribución de {campo}",
                    template="plotly_white",
                    color_discrete_sequence=["#1DB954"],
                )
            st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
def navegador(df):
    st.subheader("Navegador del Dataset")

    col1, col2 = st.columns(2)
    with col1:
        genero_filter = st.multiselect(
            "Filtrar por género:",
            sorted(df["track_genre"].unique()),
            default=[],
        )
    with col2:
        pop_range = st.slider("Rango de popularidad:", 0, 100, (0, 100))

    df_filtrado = df.copy()
    if genero_filter:
        df_filtrado = df_filtrado[df_filtrado["track_genre"].isin(genero_filter)]
    df_filtrado = df_filtrado[
        (df_filtrado["popularity"] >= pop_range[0])
        & (df_filtrado["popularity"] <= pop_range[1])
    ]

    st.markdown(f"**Mostrando {len(df_filtrado):,} de {len(df):,} registros**")

    columnas = [
        "track_name", "artists", "album_name", "track_genre",
        "popularity", "danceability", "energy", "valence", "tempo",
    ]
    st.dataframe(
        df_filtrado[columnas].reset_index(drop=True),
        use_container_width=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
def buscador(df):
    st.subheader("Buscador de Canciones (Bonus)")
    st.caption("Busca por nombre de canción o artista")

    busqueda = st.text_input("Escribe el nombre de la canción o artista:")

    if busqueda:
        mascara = df["track_name"].str.contains(
            busqueda, case=False, na=False
        ) | df["artists"].str.contains(busqueda, case=False, na=False)

        resultados = df[mascara]

        if len(resultados) > 0:
            st.success(f"Se encontraron **{len(resultados)}** resultados para '{busqueda}'")
            columnas = [
                "track_name", "artists", "album_name", "track_genre",
                "popularity", "danceability", "energy", "valence",
                "tempo", "explicit",
            ]
            st.dataframe(
                resultados[columnas].reset_index(drop=True),
                use_container_width=True,
            )
        else:
            st.warning(f"No se encontraron resultados para '{busqueda}'")
    else:
        st.info("Escribe algo en el buscador para comenzar.")


# ──────────────────────────────────────────────────────────────────────────────
def graficador(df):
    st.subheader("Graficador Exploratorio")
    st.caption("Se usa una muestra de 5,000 registros para mayor velocidad")

    df_sample = df.sample(min(5000, len(df)), random_state=42)

    campos_cuantitativos = [
        "popularity", "danceability", "energy", "loudness",
        "speechiness", "acousticness", "instrumentalness",
        "liveness", "valence", "tempo", "duration_ms",
    ]
    campos_categoricos = ["track_genre", "explicit", "key", "mode", "time_signature"]

    tipo = st.radio("Tipo de campo:", ["Cuantitativo", "Categórico"], horizontal=True)

    if tipo == "Cuantitativo":
        campo = st.selectbox("Selecciona campo:", campos_cuantitativos)
        tipo_grafico = st.radio(
            "Tipo de gráfico:", ["Histograma", "Box Plot", "Violin Plot"], horizontal=True
        )

        if tipo_grafico == "Histograma":
            fig = px.histogram(
                df_sample, x=campo, nbins=30,
                title=f"Distribución de {campo}",
                template="plotly_white",
                color_discrete_sequence=["#1DB954"],
            )
        elif tipo_grafico == "Box Plot":
            fig = px.box(
                df_sample, y=campo,
                title=f"Box Plot de {campo}",
                template="plotly_white",
                color_discrete_sequence=["#1DB954"],
            )
        else:
            fig = px.violin(
                df_sample, y=campo,
                title=f"Violin Plot de {campo}",
                template="plotly_white",
                color_discrete_sequence=["#1DB954"],
                box=True,
            )
        st.plotly_chart(fig, use_container_width=True)

    else:
        campo = st.selectbox("Selecciona campo:", campos_categoricos)
        vc = df[campo].value_counts()
        vc_df = pd.DataFrame({"Valor": vc.index, "Cantidad": vc.values})

        if campo == "track_genre":
            top_n = st.slider("Mostrar top N géneros:", 5, 30, 15)
            fig = px.bar(
                vc_df.head(top_n),
                x="Valor", y="Cantidad",
                title=f"Top {top_n} géneros musicales",
                template="plotly_white",
                color="Cantidad",
                color_continuous_scale="Viridis",
            )
            fig.update_xaxes(tickangle=45)
        elif campo == "explicit":
            fig = px.pie(
                vc_df,
                names="Valor", values="Cantidad",
                title="Contenido Explícito vs No Explícito",
                template="plotly_white",
                color_discrete_sequence=["#1DB954", "#FF4444"],
            )
        else:
            fig = px.bar(
                vc_df,
                x="Valor", y="Cantidad",
                title=f"Distribución de {campo}",
                template="plotly_white",
                color_discrete_sequence=["#1DB954"],
            )
        st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
def hipotesis(df):
    st.subheader("Hipótesis")

    df_sample = df.sample(min(5000, len(df)), random_state=42)

    hip = st.selectbox(
        "Selecciona una hipótesis:",
        [
            "H1: Las canciones con mayor energía son más populares",
            "H2: El género musical influye en la bailabilidad",
            "H3: Las canciones explícitas tienen mayor popularidad",
        ],
    )

    st.markdown("---")

    # ── H1 ──────────────────────────────────────────────────────────────────
    if "H1" in hip:
        st.markdown("### H1: ¿Las canciones con mayor energía son más populares?")
        st.markdown(
            "**Análisis:** Evaluamos la correlación entre la energía (`energy`) "
            "y la popularidad (`popularity`) de las canciones."
        )

        fig = px.scatter(
            df_sample, x="energy", y="popularity",
            trendline="ols",
            title="Energía vs. Popularidad",
            template="plotly_white",
            opacity=0.4,
            color_discrete_sequence=["#1DB954"],
            labels={"energy": "Energía", "popularity": "Popularidad"},
        )
        st.plotly_chart(fig, use_container_width=True)

        corr = df["energy"].corr(df["popularity"])
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Correlación de Pearson", f"{corr:.4f}")
        with col2:
            avg_alta = df[df["energy"] >= 0.7]["popularity"].mean()
            st.metric("Popularidad prom. (energía ≥ 0.7)", f"{avg_alta:.2f}")
        with col3:
            avg_baja = df[df["energy"] < 0.4]["popularity"].mean()
            st.metric("Popularidad prom. (energía < 0.4)", f"{avg_baja:.2f}")

        st.markdown("#### Conclusión")
        if abs(corr) < 0.1:
            nivel = "muy débil"
        elif abs(corr) < 0.3:
            nivel = "débil"
        else:
            nivel = "moderada"
        direction = "positiva" if corr > 0 else "negativa"
        valida = "parcialmente valida" if abs(corr) > 0.05 else "no se valida"

        st.info(
            f"La correlación entre energía y popularidad es **{corr:.4f}**, lo que representa "
            f"una relación **{nivel} {direction}**. La hipótesis **{valida}**: la energía "
            f"tiene una influencia {'pequeña pero' if abs(corr) < 0.2 else ''} "
            f"{'medible' if abs(corr) > 0.05 else 'no significativa'} en la popularidad."
        )

    # ── H2 ──────────────────────────────────────────────────────────────────
    elif "H2" in hip:
        st.markdown("### H2: ¿El género musical influye en la bailabilidad?")
        st.markdown(
            "**Análisis:** Comparamos el promedio de `danceability` entre los "
            "géneros más representados del dataset."
        )

        top_generos = df["track_genre"].value_counts().head(12).index
        df_top = df[df["track_genre"].isin(top_generos)]

        fig_box = px.box(
            df_top, x="track_genre", y="danceability",
            title="Bailabilidad por Género (Top 12 géneros)",
            template="plotly_white",
            color="track_genre",
            labels={"track_genre": "Género", "danceability": "Bailabilidad"},
        )
        fig_box.update_xaxes(tickangle=45)
        st.plotly_chart(fig_box, use_container_width=True)

        avg = (
            df_top.groupby("track_genre")["danceability"]
            .mean()
            .sort_values(ascending=False)
        )
        avg_df = pd.DataFrame(
            {"Género": avg.index, "Bailabilidad Promedio": avg.values.round(4)}
        )

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(avg_df, use_container_width=True, hide_index=True)
        with col2:
            fig_bar = px.bar(
                avg_df,
                x="Género", y="Bailabilidad Promedio",
                title="Bailabilidad Promedio por Género",
                template="plotly_white",
                color="Bailabilidad Promedio",
                color_continuous_scale="Viridis",
            )
            fig_bar.update_xaxes(tickangle=45)
            st.plotly_chart(fig_bar, use_container_width=True)

        max_g = avg.index[0]
        min_g = avg.index[-1]
        diferencia = avg.iloc[0] - avg.iloc[-1]

        st.markdown("#### Conclusión")
        st.info(
            f"Existe una diferencia clara en bailabilidad entre géneros. "
            f"**{max_g}** es el género más bailable ({avg.iloc[0]:.4f}) y "
            f"**{min_g}** el menos bailable ({avg.iloc[-1]:.4f}), "
            f"con una diferencia de **{diferencia:.4f}**. "
            f"La hipótesis **se valida**: el género musical sí influye significativamente "
            f"en la bailabilidad de las canciones."
        )

    # ── H3 ──────────────────────────────────────────────────────────────────
    elif "H3" in hip:
        st.markdown("### H3: ¿Las canciones explícitas son más populares?")
        st.markdown(
            "**Análisis:** Comparamos la distribución de `popularity` entre "
            "canciones explícitas y no explícitas."
        )

        df_h3 = df.copy()
        df_h3["explicit"] = df_h3["explicit"].astype(str).map(
            {"True": "Explícita", "False": "No Explícita",
             "true": "Explícita", "false": "No Explícita"}
        )

        fig = px.box(
            df_h3, x="explicit", y="popularity",
            title="Popularidad: Canciones Explícitas vs No Explícitas",
            template="plotly_white",
            color="explicit",
            color_discrete_map={"Explícita": "#FF4444", "No Explícita": "#1DB954"},
            labels={"explicit": "Tipo", "popularity": "Popularidad"},
        )
        st.plotly_chart(fig, use_container_width=True)

        avg_exp = df_h3[df_h3["explicit"] == "Explícita"]["popularity"].mean()
        avg_no = df_h3[df_h3["explicit"] == "No Explícita"]["popularity"].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Popularidad prom. Explícita", f"{avg_exp:.2f}")
        with col2:
            st.metric("Popularidad prom. No Explícita", f"{avg_no:.2f}")
        with col3:
            st.metric("Diferencia", f"{avg_exp - avg_no:.2f}")

        diff = avg_exp - avg_no
        st.markdown("#### Conclusión")
        if diff > 3:
            concl = "**se valida**: las canciones explícitas tienen mayor popularidad promedio"
        elif diff < -3:
            concl = "**no se valida**: las canciones no explícitas son más populares"
        else:
            concl = "**es inconclusa**: la diferencia no es estadísticamente significativa"

        st.info(
            f"La diferencia en popularidad promedio entre canciones explícitas ({avg_exp:.2f}) "
            f"y no explícitas ({avg_no:.2f}) es de **{diff:.2f} puntos**. "
            f"La hipótesis {concl}."
        )


if __name__ == "__main__":
    eda()
