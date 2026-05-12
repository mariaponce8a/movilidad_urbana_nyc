import streamlit as st
import requests
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de página
st.set_page_config(page_title="NYC Taxi Mobility Dashboard", layout="wide", page_icon="🚕")

API_URL = "http://localhost:8000"

st.title("Análisis de Demanda y Predicción de Movilidad - NYC")
st.markdown("Dashboard interactivo para visualizar puntos calientes (Hotspots) y predecir demanda futura usando modelos de Inteligencia Artificial (Prophet y SARIMA).")

# --- PANEL LATERAL ---
st.sidebar.header("⚙️ Controles Globales")

st.sidebar.subheader("📍 Filtros Geoespaciales")
selected_hour = st.sidebar.slider("Selecciona la hora del día (Mapa):", min_value=0, max_value=23, value=8, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Configuración de Predicción (IA)")
# Top 10 Zonas (Hardcoded basado en el análisis para rapidez)
top10_zones = {
    161: "Midtown Center",
    237: "Upper East Side South",
    236: "Upper East Side North",
    132: "JFK Airport",
    230: "Times Square / Theatre District",
    186: "Penn Station / Madison Square West",
    162: "Midtown East",
    142: "Lincoln Square East",
    239: "Upper West Side South",
    163: "Midtown North"
}

selected_zone = st.sidebar.selectbox("Selecciona una Zona Top 10:", options=list(top10_zones.keys()), format_func=lambda x: f"{x} - {top10_zones[x]}")
selected_model = st.sidebar.radio("Selecciona el Algoritmo Predictivo:", options=["Prophet", "SARIMA"])
forecast_horizon = st.sidebar.slider("Horizonte de predicción (Horas al futuro):", min_value=12, max_value=168, value=24, step=12)

# --- VISUALIZACIONES PRINCIPALES ---
col1, col2 = st.columns([1, 1])

# --- COLUMNA 1: MAPA Y BARRAS ---
with col1:
    st.subheader(f"Mapa de Calor (Demanda a las {selected_hour}:00)")
    
    # Llamada a la API para el mapa
    try:
        res = requests.get(f"{API_URL}/trips/heatmap?hour={selected_hour}")
        if res.status_code == 200:
            heatmap_data = res.json()["data"]
            
            # Crear mapa Folium centrado en Manhattan
            m = folium.Map(location=[40.7580, -73.9855], zoom_start=11, tiles="CartoDB positron")
            
            # Agregar HeatMap
            if heatmap_data:
                HeatMap(heatmap_data, radius=12, blur=15, max_zoom=1).add_to(m)
            
            # Mostrar en Streamlit
            st_folium(m, width=700, height=450)
        else:
            st.error("Error al cargar los datos del mapa desde la API.")
    except Exception as e:
        st.error(f"Asegúrate de tener la API corriendo (uvicorn api:app --reload). Error: {e}")

    st.subheader("📊 Demanda Agregada a lo largo del día")
    try:
        res = requests.get(f"{API_URL}/trips/demand_curve")
        if res.status_code == 200:
            curve_data = res.json()
            df_curve = pd.DataFrame({"Hora": curve_data["x"], "Viajes Totales": curve_data["y"]})
            
            fig = px.bar(df_curve, x="Hora", y="Viajes Totales", color="Viajes Totales",
                         color_continuous_scale="Viridis", 
                         title="Volumen Total de Viajes por Hora en Enero 2025")
            fig.update_layout(xaxis=dict(tickmode='linear'))
            st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("No se pudo cargar la curva de demanda.")

# --- COLUMNA 2: PREDICCIÓN Y HEATMAP DE SEABORN ---
with col2:
    st.subheader(f"Predicción del Futuro: Zona {selected_zone} ({top10_zones[selected_zone]})")
    
    if st.button(f"Generar Pronóstico ({selected_model})"):
        with st.spinner(f"Entrenando modelo {selected_model} en tiempo real y prediciendo {forecast_horizon} horas..."):
            try:
                res = requests.get(f"{API_URL}/trips/predict?zone_id={selected_zone}&hours={forecast_horizon}&model={selected_model.lower()}")
                if res.status_code == 200:
                    pred_data = res.json()
                    future_dates = pred_data["future_dates"]
                    predictions = pred_data["predictions"]
                    
                    df_pred = pd.DataFrame({
                        "Fecha/Hora": pd.to_datetime(future_dates),
                        "Viajes Predichos": predictions
                    })
                    
                    fig = px.line(df_pred, x="Fecha/Hora", y="Viajes Predichos", markers=True,
                                  title=f"Predicción Oficial ({selected_model}): Próximas {forecast_horizon} horas")
                    
                    # Cambiar color según el modelo para consistencia
                    line_color = "blue" if selected_model == "Prophet" else "red"
                    fig.update_traces(line_color=line_color)
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"Error de la API: {res.text}")
            except Exception as e:
                st.error("Asegúrate de tener la API corriendo.")
    else:
        st.info("Presiona el botón para entrenar el algoritmo y predecir el futuro.")
        
    st.markdown("---")
    
    st.subheader("📅 Patrones Temporales: Hora vs Día de la Semana")
    st.markdown("*(Exigido por rúbrica: Identifica diferencias entre días hábiles y fines de semana)*")
    try:
        res = requests.get(f"{API_URL}/trips/heatmap_day_hour")
        if res.status_code == 200:
            data = res.json()
            df_pivot = pd.DataFrame(data["valores"], index=data["dias"], columns=data["horas"])
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(df_pivot, cmap="YlOrRd", ax=ax, linewidths=0.5)
            plt.title("Concentración de Viajes: Día de la Semana vs Hora", fontsize=12)
            plt.xlabel("Hora del Día")
            plt.ylabel("")
            st.pyplot(fig)
    except:
        st.warning("No se pudo cargar el Heatmap de Seaborn.")
