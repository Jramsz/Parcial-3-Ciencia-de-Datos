import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ──────────────────────────────────────────────────────────────────────────────
def carga_archivos():
    st.title("📂 Análisis de Datos por Carga de Archivos")
    st.caption("Sube un CSV, Excel o JSON y la app genera el análisis automáticamente")

    uploaded_file = st.file_uploader(
        "Selecciona un archivo desde tu computadora:",
        type=["csv", "xlsx", "xls", "json"],
        help="Formatos soportados: CSV, Excel (.xlsx / .xls), JSON",
    )

    if uploaded_file is None:
        st.info("👆 Arrastra o selecciona un archivo para comenzar el análisis")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**CSV**\nArchivos separados por comas o punto y coma")
        with col2:
            st.markdown("**Excel**\nArchivos .xlsx o .xls")
        with col3:
            st.markdown("**JSON**\nArreglos o registros JSON")
        return

    df = leer_archivo(uploaded_file)
    if df is None:
        return

    st.success(
        f"**{uploaded_file.name}** cargado — "
        f"{len(df):,} filas × {len(df.columns)} columnas"
    )
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Vista de Datos", "Estadísticas", "Graficador"])

    with tab1:
        mostrar_datos(df)
    with tab2:
        mostrar_estadisticas(df)
    with tab3:
        mostrar_graficos(df)


# ──────────────────────────────────────────────────────────────────────────────
def leer_archivo(uploaded_file):
    nombre = uploaded_file.name.lower()
    try:
        if nombre.endswith(".csv"):
            # Detectar separador automáticamente
            muestra = uploaded_file.read(2048).decode("utf-8", errors="ignore")
            uploaded_file.seek(0)
            sep = ";" if muestra.count(";") > muestra.count(",") else ","
            df = pd.read_csv(uploaded_file, sep=sep, encoding="utf-8", on_bad_lines="skip")
        elif nombre.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        elif nombre.endswith(".json"):
            df = pd.read_json(uploaded_file)
        else:
            st.error("Formato no soportado.")
            return None
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return None


# ──────────────────────────────────────────────────────────────────────────────
def mostrar_datos(df):
    st.subheader("Vista del Dataset")

    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Filas", f"{len(df):,}")
    c2.metric("Columnas", len(df.columns))
    c3.metric("Cols. Numéricas", len(num_cols))
    c4.metric("Cols. Categóricas", len(cat_cols))

    n_filas = st.slider("Filas a mostrar:", 5, min(500, len(df)), min(50, len(df)))
    st.dataframe(df.head(n_filas), use_container_width=True)

    # Nulos
    nulls = df.isnull().sum()
    if nulls.sum() > 0:
        st.warning(f"Valores nulos en {(nulls > 0).sum()} columna(s)")
        null_df = pd.DataFrame(
            {"Columna": nulls[nulls > 0].index, "Valores Nulos": nulls[nulls > 0].values}
        )
        st.dataframe(null_df, use_container_width=True, hide_index=True)
    else:
        st.success("Sin valores nulos")


# ──────────────────────────────────────────────────────────────────────────────
def mostrar_estadisticas(df):
    st.subheader("Estadísticas del Dataset")

    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()

    if num_cols:
        st.markdown("#### Columnas Numéricas — describe()")
        st.dataframe(df[num_cols].describe().round(4), use_container_width=True)

    if cat_cols:
        st.markdown("#### Columnas Categóricas")
        campo = st.selectbox("Ver valores únicos de:", cat_cols)
        vc = df[campo].value_counts()
        vc_df = pd.DataFrame({"Valor": vc.index, "Cantidad": vc.values})

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Valores únicos", df[campo].nunique())
            st.dataframe(vc_df.head(20), use_container_width=True, hide_index=True)
        with col2:
            if len(vc_df) <= 10:
                fig = px.pie(
                    vc_df, names="Valor", values="Cantidad",
                    title=f"Distribución de {campo}", template="plotly_white",
                )
            else:
                fig = px.bar(
                    vc_df.head(20), x="Valor", y="Cantidad",
                    title=f"Top 20 valores de {campo}", template="plotly_white",
                    color_discrete_sequence=["#1DB954"],
                )
                fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
def mostrar_graficos(df):
    st.subheader("Graficador Automático")

    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    todas_cols = df.columns.tolist()

    tipo = st.selectbox(
        "Tipo de gráfico:",
        ["Histograma", "Dispersión (Scatter)", "Barras", "Box Plot",
         "Línea", "Correlación (Heatmap)"],
    )

    # ── Histograma ────────────────────────────────────────────────────────
    if tipo == "Histograma":
        if not num_cols:
            st.warning("No hay columnas numéricas.")
            return
        campo = st.selectbox("Campo:", num_cols)
        nbins = st.slider("Bins:", 5, 100, 30)
        fig = px.histogram(
            df, x=campo, nbins=nbins,
            title=f"Distribución de {campo}", template="plotly_white",
            color_discrete_sequence=["#1DB954"],
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Scatter ───────────────────────────────────────────────────────────
    elif tipo == "Dispersión (Scatter)":
        if len(num_cols) < 2:
            st.warning("Necesitas al menos 2 columnas numéricas.")
            return
        c1, c2 = st.columns(2)
        with c1:
            eje_x = st.selectbox("Eje X:", num_cols)
        with c2:
            eje_y = st.selectbox("Eje Y:", [c for c in num_cols if c != eje_x])
        color_col = st.selectbox("Color (opcional):", ["—"] + cat_cols)
        fig = px.scatter(
            df.sample(min(5000, len(df)), random_state=42),
            x=eje_x, y=eje_y,
            color=color_col if color_col != "—" else None,
            title=f"{eje_x} vs {eje_y}",
            template="plotly_white",
            trendline="ols" if color_col == "—" else None,
            opacity=0.6,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Barras ────────────────────────────────────────────────────────────
    elif tipo == "Barras":
        if not cat_cols:
            st.warning("No hay columnas categóricas.")
            return
        campo_cat = st.selectbox("Campo categórico (X):", cat_cols)
        campo_num = st.selectbox("Campo numérico (Y):", ["Conteo"] + num_cols)
        top_n = st.slider("Top N categorías:", 5, 30, 10)

        if campo_num == "Conteo":
            vc = df[campo_cat].value_counts().head(top_n)
            fig = px.bar(
                x=vc.index, y=vc.values,
                labels={"x": campo_cat, "y": "Conteo"},
                title=f"Conteo de {campo_cat}", template="plotly_white",
                color_discrete_sequence=["#1DB954"],
            )
        else:
            grouped = df.groupby(campo_cat)[campo_num].mean().nlargest(top_n)
            fig = px.bar(
                x=grouped.index, y=grouped.values,
                labels={"x": campo_cat, "y": f"Promedio {campo_num}"},
                title=f"Promedio de {campo_num} por {campo_cat}",
                template="plotly_white", color_discrete_sequence=["#1DB954"],
            )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    # ── Box Plot ──────────────────────────────────────────────────────────
    elif tipo == "Box Plot":
        if not num_cols:
            st.warning("No hay columnas numéricas.")
            return
        campo = st.selectbox("Campo numérico:", num_cols)
        grupo = st.selectbox("Agrupar por (opcional):", ["—"] + cat_cols)
        if grupo != "—":
            top_cats = df[grupo].value_counts().head(10).index
            df_p = df[df[grupo].isin(top_cats)]
            fig = px.box(df_p, x=grupo, y=campo,
                         title=f"Box Plot de {campo} por {grupo}",
                         template="plotly_white", color=grupo)
        else:
            fig = px.box(df, y=campo, title=f"Box Plot de {campo}",
                         template="plotly_white",
                         color_discrete_sequence=["#1DB954"])
        st.plotly_chart(fig, use_container_width=True)

    # ── Línea ─────────────────────────────────────────────────────────────
    elif tipo == "Línea":
        if not num_cols:
            st.warning("No hay columnas numéricas.")
            return
        eje_x = st.selectbox("Eje X:", todas_cols)
        eje_y = st.selectbox("Eje Y:", num_cols)
        fig = px.line(
            df.head(500), x=eje_x, y=eje_y,
            title=f"{eje_y} a lo largo de {eje_x}",
            template="plotly_white", color_discrete_sequence=["#1DB954"],
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Heatmap ───────────────────────────────────────────────────────────
    elif tipo == "Correlación (Heatmap)":
        if len(num_cols) < 2:
            st.warning("Necesitas al menos 2 columnas numéricas.")
            return
        corr = df[num_cols].corr()
        fig = px.imshow(
            corr, title="Matriz de Correlación",
            template="plotly_white",
            color_continuous_scale="RdBu_r",
            text_auto=".2f",
        )
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    carga_archivos()
