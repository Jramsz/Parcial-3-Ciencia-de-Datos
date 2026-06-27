import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


@st.cache_data
def leerDatos():
    df = pd.read_csv("dataset.csv", index_col=0)
    return df


FEATURES = [
    "danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness",
    "valence", "tempo", "popularity",
]

ETIQUETAS = {
    "popularity": "Popularidad",
    "energy": "Energía",
    "danceability": "Bailabilidad",
    "valence": "Positividad",
    "tempo": "Tempo (BPM)",
    "loudness": "Volumen (dB)",
    "acousticness": "Acústica",
    "speechiness": "Palabras Habladas",
    "instrumentalness": "Instrumental",
    "liveness": "En Vivo",
}


# ──────────────────────────────────────────────────────────────────────────────
def ml():
    st.title("Aprendizaje Automático")
    st.caption("Entrena y compara modelos predictivos con el dataset de Spotify")

    df = leerDatos()
    df_ml = df[FEATURES].dropna()

    # ── Sidebar configuración ─────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Configuración del Modelo")

    algoritmo = st.sidebar.selectbox(
        "Algoritmo:",
        ["Regresión Lineal", "Árbol de Decisión", "Random Forest"],
    )

    variable_y = st.sidebar.selectbox(
        "Variable a predecir (Y):",
        ["popularity", "energy", "danceability", "valence", "tempo"],
        format_func=lambda x: ETIQUETAS.get(x, x),
    )

    vars_x_disponibles = [f for f in FEATURES if f != variable_y]
    variables_x = st.sidebar.multiselect(
        "Variables independientes (X):",
        vars_x_disponibles,
        default=vars_x_disponibles[:4],
        format_func=lambda x: ETIQUETAS.get(x, x),
    )

    test_pct = st.sidebar.slider("% Datos de Prueba:", 10, 40, 20, step=5)
    train_pct = 100 - test_pct

    # Hiperparámetros por algoritmo
    if algoritmo == "Árbol de Decisión":
        max_depth = st.sidebar.slider("Profundidad máxima:", 2, 20, 5)
    elif algoritmo == "Random Forest":
        n_estimators = st.sidebar.slider("Número de árboles:", 10, 200, 100, step=10)
        max_depth_rf = st.sidebar.slider("Profundidad máxima:", 2, 20, 5)

    if len(variables_x) < 1:
        st.warning("Selecciona al menos una variable independiente en el menú lateral.")
        return

    # ── Datos ─────────────────────────────────────────────────────────────
    df_sample = df_ml.sample(min(10000, len(df_ml)), random_state=42)
    X = df_sample[variables_x].values
    y = df_sample[variable_y].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_pct / 100, random_state=42
    )

    # ── Entrenar modelo ───────────────────────────────────────────────────
    if algoritmo == "Regresión Lineal":
        modelo = LinearRegression()
    elif algoritmo == "Árbol de Decisión":
        modelo = DecisionTreeRegressor(max_depth=max_depth, random_state=42)
    else:
        modelo = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth_rf,
            random_state=42,
            n_jobs=-1,
        )

    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    y_pred_train = modelo.predict(X_train)

    # ── Métricas ──────────────────────────────────────────────────────────
    r2_test = r2_score(y_test, y_pred)
    r2_train = r2_score(y_train, y_pred_train)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # ── Layout ────────────────────────────────────────────────────────────
    st.markdown(f"### Modelo: **{algoritmo}** · Prediciendo: **{ETIQUETAS.get(variable_y, variable_y)}**")
    st.markdown("---")

    col_izq, col_der = st.columns([1, 2])

    # ── Métricas panel izquierdo ──────────────────────────────────────────
    with col_izq:
        st.markdown("#### Métricas de Desempeño")

        st.metric("R² — Prueba", f"{r2_test:.4f}",
                  delta=f"{r2_test - r2_train:+.4f} vs entrenamiento",
                  delta_color="inverse" if (r2_train - r2_test) > 0.15 else "normal")
        st.metric("R² — Entrenamiento", f"{r2_train:.4f}")
        st.metric("MAE (Error Abs. Medio)", f"{mae:.4f}")
        st.metric("RMSE (Raíz Error Cuad.)", f"{rmse:.4f}")

        st.markdown("#### Datos del Entrenamiento")
        st.metric("Registros entrenamiento", f"{len(X_train):,}")
        st.metric("Registros prueba", f"{len(X_test):,}")
        st.metric("Split entrenamiento / prueba", f"{train_pct}% / {test_pct}%")

        # Coeficientes o importancias
        if algoritmo == "Regresión Lineal":
            st.markdown("#### Coeficientes")
            coef_df = pd.DataFrame({
                "Variable": [ETIQUETAS.get(v, v) for v in variables_x],
                "Coeficiente": modelo.coef_.round(6),
            }).sort_values("Coeficiente", key=abs, ascending=False)
            st.dataframe(coef_df, use_container_width=True, hide_index=True)
            st.metric("Intercepto (β₀)", f"{modelo.intercept_:.4f}")

        else:
            st.markdown("#### Importancia de Variables")
            imp_df = pd.DataFrame({
                "Variable": [ETIQUETAS.get(v, v) for v in variables_x],
                "Importancia": modelo.feature_importances_.round(4),
            }).sort_values("Importancia", ascending=False)
            st.dataframe(imp_df, use_container_width=True, hide_index=True)

            fig_imp = px.bar(
                imp_df, x="Importancia", y="Variable",
                orientation="h",
                title="Importancia de variables",
                template="plotly_white",
                color="Importancia",
                color_continuous_scale="Viridis",
            )
            st.plotly_chart(fig_imp, use_container_width=True)

    # ── Gráficos panel derecho ────────────────────────────────────────────
    with col_der:
        st.markdown("#### Visualización del Modelo")

        var_vis = st.selectbox(
            "Variable del eje X para visualizar:",
            variables_x,
            format_func=lambda x: ETIQUETAS.get(x, x),
        )
        idx_vis = variables_x.index(var_vis)

        # Gráfico principal: scatter entrenamiento + predicciones prueba
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=X_train[:, idx_vis], y=y_train,
            mode="markers",
            name="Datos Entrenamiento",
            marker=dict(color="#1DB954", size=4, opacity=0.4),
        ))
        fig.add_trace(go.Scatter(
            x=X_test[:, idx_vis], y=y_test,
            mode="markers",
            name="Datos Reales (Prueba)",
            marker=dict(color="#FFA500", size=5, opacity=0.6),
        ))
        fig.add_trace(go.Scatter(
            x=X_test[:, idx_vis], y=y_pred,
            mode="markers",
            name="Predicciones (Prueba)",
            marker=dict(color="#FF4444", size=5, opacity=0.7, symbol="x"),
        ))

        # Línea de regresión (solo para regresión lineal)
        if algoritmo == "Regresión Lineal":
            x_rng = np.linspace(X[:, idx_vis].min(), X[:, idx_vis].max(), 100)
            x_line = np.tile(df_sample[variables_x].mean().values, (100, 1))
            x_line[:, idx_vis] = x_rng
            y_line = modelo.predict(x_line)
            fig.add_trace(go.Scatter(
                x=x_rng, y=y_line,
                mode="lines",
                name="Línea de Regresión",
                line=dict(color="#1447e6", width=2),
            ))

        fig.update_layout(
            title=f"Predicción de {ETIQUETAS.get(variable_y, variable_y)} usando {ETIQUETAS.get(var_vis, var_vis)}",
            xaxis_title=ETIQUETAS.get(var_vis, var_vis),
            yaxis_title=ETIQUETAS.get(variable_y, variable_y),
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Gráfico real vs predicho
        st.markdown("#### Valores Reales vs Predicciones")
        n_show = min(300, len(y_test))
        min_v = float(min(y_test.min(), y_pred.min()))
        max_v = float(max(y_test.max(), y_pred.max()))

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=y_test[:n_show], y=y_pred[:n_show],
            mode="markers",
            marker=dict(color="#1DB954", opacity=0.6, size=6),
            name="Predicciones",
        ))
        fig2.add_trace(go.Scatter(
            x=[min_v, max_v], y=[min_v, max_v],
            mode="lines",
            line=dict(color="red", dash="dash"),
            name="Predicción Perfecta",
        ))
        fig2.update_layout(
            title="Valores Reales vs Predichos (muestra)",
            xaxis_title=f"{ETIQUETAS.get(variable_y, variable_y)} (Real)",
            yaxis_title=f"{ETIQUETAS.get(variable_y, variable_y)} (Predicho)",
            template="plotly_white",
        )
        st.plotly_chart(fig2, use_container_width=True)


if __name__ == "__main__":
    ml()
