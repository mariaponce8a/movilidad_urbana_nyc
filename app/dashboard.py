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
st.set_page_config(page_title="NYC Taxi Mobility Dashboard", layout="wide")

API_URL = "http://localhost:8000"

st.title("Análisis de Demanda y Predicción de Movilidad - NYC")
st.markdown("Dashboard interactivo para visualizar puntos de calor espaciales y predecir demanda futura mediante modelos econométricos y de Inteligencia Artificial (Prophet y SARIMA).")

# --- PANEL LATERAL ---
st.sidebar.header("Controles Globales")

st.sidebar.subheader("Filtros Geoespaciales")
selected_hour = st.sidebar.slider("Selecciona la hora del día (Mapa):", min_value=0, max_value=23, value=8, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("Configuración de Predicción")
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
selected_models = st.sidebar.multiselect("Selecciona Algoritmo(s) Predictivo(s):", options=["Prophet", "SARIMA"], default=["Prophet", "SARIMA"])
forecast_horizon = st.sidebar.slider("Horizonte de predicción (Horas al futuro):", min_value=12, max_value=168, value=24, step=12)

# --- VISUALIZACIONES PRINCIPALES ---
tab1, tab2, tab3 = st.tabs(["Mapa Geoespacial", "Patrones Temporales", "Inteligencia Artificial"])

# --- PESTAÑA 1: MAPA GEOESPACIAL ---
with tab1:
    st.subheader(f"Mapa de Calor (Demanda a las {selected_hour}:00)")
    st.markdown("Visualiza la concentración física de viajes a través de Manhattan según la hora seleccionada en el panel lateral.")
    
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
            
            # Mostrar en Streamlit (más ancho gracias a las tabs)
            st_folium(m, width=1000, height=500)
        else:
            st.error("Error al cargar los datos del mapa desde la API.")
    except Exception as e:
        st.error(f"Asegúrate de tener la API corriendo (uvicorn api:app --reload). Error: {e}")

# --- PESTAÑA 2: PATRONES TEMPORALES ---
with tab2:
    st.subheader("Demanda Agregada a lo largo del día")
    try:
        res = requests.get(f"{API_URL}/trips/demand_curve")
        if res.status_code == 200:
            curve_data = res.json()
            df_curve = pd.DataFrame({"Hora": curve_data["x"], "Viajes Totales": curve_data["y"]})
            
            fig1 = px.bar(df_curve, x="Hora", y="Viajes Totales", color="Viajes Totales",
                         color_continuous_scale="Viridis", 
                         title="Volumen Total de Viajes por Hora en Enero 2025")
            fig1.update_layout(xaxis=dict(tickmode='linear'), template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)
    except:
        st.warning("No se pudo cargar la curva de demanda.")
        
    st.markdown("---")
    
    st.subheader("Concentración Temporal: Hora vs Día de la Semana")
    st.markdown("*(Gráfico estático de Seaborn exigido por la rúbrica para identificar diferencias entre días hábiles y fines de semana)*")
    try:
        res = requests.get(f"{API_URL}/trips/heatmap_day_hour")
        if res.status_code == 200:
            data = res.json()
            df_pivot = pd.DataFrame(data["valores"], index=data["dias"], columns=data["horas"])
            
            fig2, ax = plt.subplots(figsize=(15, 6))
            sns.heatmap(df_pivot, cmap="YlOrRd", ax=ax, linewidths=0.5)
            plt.xlabel("Hora del Día")
            plt.ylabel("Día de la Semana")
            st.pyplot(fig2)
    except:
        st.warning("No se pudo cargar el Heatmap de Seaborn.")

# --- PESTAÑA 3: PREDICCIONES (IA) ---
with tab3:
    st.subheader(f"Predicción del Futuro: Zona {selected_zone} ({top10_zones[selected_zone]})")
    st.markdown("Utiliza modelos matemáticos para pronosticar la curva de demanda de las próximas horas/días.")
    
    if st.button("Generar Pronóstico Multimodelo"):
        if not selected_models:
            st.warning("Por favor, selecciona al menos un modelo predictivo en el panel lateral.")
        else:
            with st.spinner(f"Entrenando modelos y prediciendo {forecast_horizon} horas..."):
                fig3 = go.Figure()
                
                for model in selected_models:
                    try:
                        res = requests.get(f"{API_URL}/trips/predict?zone_id={selected_zone}&hours={forecast_horizon}&model={model.lower()}")
                        if res.status_code == 200:
                            pred_data = res.json()
                            df_pred = pd.DataFrame({
                                "Fecha/Hora": pd.to_datetime(pred_data["future_dates"]),
                                "Viajes Predichos": pred_data["predictions"]
                            })
                            
                            # Prophet en azul, SARIMA en rojo
                            color = "blue" if model == "Prophet" else "red"
                            fig3.add_trace(go.Scatter(
                                x=df_pred["Fecha/Hora"],
                                y=df_pred["Viajes Predichos"],
                                mode='lines+markers',
                                name=f"{model} Forecast",
                                line=dict(color=color, width=2)
                            ))
                        else:
                            st.error(f"Error de la API para {model}: {res.text}")
                    except Exception as e:
                        st.error(f"Asegúrate de tener la API corriendo. Error conectando para {model}.")
                
                fig3.update_layout(
                    title=f"Comparativa de Modelos Predictivos: Próximas {forecast_horizon} horas",
                    xaxis_title="Fecha y Hora",
                    yaxis_title="Volumen de Viajes",
                    hovermode="x unified",
                    template="plotly_white",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Configura los parámetros en el panel lateral y presiona el botón para entrenar los modelos y generar el pronóstico.")
