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

st.markdown("---")

# --- DATOS TOP 10 ZONAS (Coordenadas para Mapa) ---
top10_zones_info = {
    161: {"name": "Midtown Center", "lat": 40.7600, "lon": -73.9800},
    237: {"name": "Upper East Side South", "lat": 40.7685, "lon": -73.9588},
    236: {"name": "Upper East Side North", "lat": 40.7736, "lon": -73.9535},
    132: {"name": "JFK Airport", "lat": 40.6413, "lon": -73.7781},
    230: {"name": "Times Square", "lat": 40.7580, "lon": -73.9855},
    186: {"name": "Penn Station", "lat": 40.7506, "lon": -73.9935},
    162: {"name": "Midtown East", "lat": 40.7570, "lon": -73.9700},
    142: {"name": "Lincoln Square East", "lat": 40.7738, "lon": -73.9822},
    239: {"name": "Upper West Side South", "lat": 40.7830, "lon": -73.9780},
    163: {"name": "Midtown North", "lat": 40.7650, "lon": -73.9800}
}

# --- VISUALIZACIONES PRINCIPALES ---
tab1, tab2, tab3 = st.tabs(["Mapa Geoespacial", "Patrones Temporales", "Predicción de Demanda"])

# --- PESTAÑA 1: MAPA GEOESPACIAL ---
with tab1:
    st.subheader("Visualización Espacial de la Demanda")
    st.markdown("Visualiza la concentración física de viajes a través de Manhattan.")
    
    # Filtro específico para el mapa
    selected_hour = st.slider("Selecciona la hora del día:", min_value=0, max_value=23, value=18, step=1)
    
    try:
        res = requests.get(f"{API_URL}/trips/heatmap?hour={selected_hour}")
        if res.status_code == 200:
            heatmap_data = res.json()["data"]
            
            # Crear mapa Folium centrado en Manhattan
            m = folium.Map(location=[40.7580, -73.9855], zoom_start=11, tiles="CartoDB positron")
            
            # Agregar HeatMap
            if heatmap_data:
                HeatMap(heatmap_data, radius=12, blur=15, max_zoom=1).add_to(m)
                
            # Agregar marcadores de las Top 10 Zonas de Demanda
            for z_id, info in top10_zones_info.items():
                folium.Marker(
                    location=[info["lat"], info["lon"]],
                    popup=f"Zona {z_id}: {info['name']}",
                    icon=folium.Icon(color="orange", icon="info-sign")
                ).add_to(m)
            
            # Mostrar en Streamlit
            st_folium(m, width=1000, height=500)
            st.info("💡 **Insight de Negocio:** El mapa revela cómo a partir de las 18:00 hrs la concentración de viajes (hotspots) se expande masivamente hacia los puentes y las zonas comerciales, identificando los nodos exactos de mayor saturación de la flota.")
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
            
            # Gama de colores cálidos
            fig1 = px.bar(df_curve, x="Hora", y="Viajes Totales", color="Viajes Totales",
                         color_continuous_scale=px.colors.sequential.Oranges, 
                         title="Volumen Total de Viajes por Hora en Enero 2025")
            fig1.update_layout(xaxis=dict(tickmode='linear'), template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)
            st.info("💡 **Insight de Negocio:** Se evidencia una clara bimodalidad. Hay un pico de demanda matutino por viajes al trabajo y un pico vespertino mucho más agresivo hacia las 18:00 hrs, dictando el horario crítico para asignar a los conductores.")
    except:
        st.warning("No se pudo cargar la curva de demanda.")
        
    st.markdown("---")
    
    st.subheader("Concentración Temporal: Hora vs Día de la Semana")
    st.markdown("Identifica las diferencias de comportamiento entre días hábiles y fines de semana.")
    
    # Toggle Seaborn / Plotly
    tipo_grafico = st.radio("Elige el motor de visualización:", ["Plotly Express (Interactivo)", "Seaborn (Estático)"], horizontal=True)
    
    try:
        res = requests.get(f"{API_URL}/trips/heatmap_day_hour")
        if res.status_code == 200:
            data = res.json()
            df_pivot = pd.DataFrame(data["valores"], index=data["dias"], columns=data["horas"])
            
            if tipo_grafico == "Seaborn (Estático)":
                fig2, ax = plt.subplots(figsize=(15, 6))
                sns.heatmap(df_pivot, cmap="Oranges", ax=ax, linewidths=0.5)
                plt.xlabel("Hora del Día")
                plt.ylabel("Día de la Semana")
                st.pyplot(fig2)
            else:
                # Plotly Express
                fig_px = px.imshow(df_pivot, 
                                   labels=dict(x="Hora del Día", y="Día de la Semana", color="Viajes"),
                                   x=df_pivot.columns, y=df_pivot.index,
                                   color_continuous_scale="Oranges", aspect="auto")
                fig_px.update_layout(template="plotly_white")
                st.plotly_chart(fig_px, use_container_width=True)
                
            st.info("💡 **Insight de Negocio:** La matriz muestra cómo los Jueves y Viernes la demanda se prolonga dramáticamente hacia la madrugada (inicio del fin de semana), mientras que el Lunes es netamente laboral.")
    except:
        st.warning("No se pudo cargar la Matriz de Calor Temporal.")

# --- PESTAÑA 3: PREDICCIONES (IA) ---
with tab3:
    st.subheader(f"Predicción del Futuro: Zona {selected_zone} ({top10_zones[selected_zone]})")
    st.markdown("Utiliza modelos matemáticos para pronosticar la curva de demanda de las próximas horas/días.")
    
    if st.button("Ejecutar Entrenamiento y Generar Pronóstico"):
        if not selected_models:
            st.warning("Por favor, selecciona al menos un modelo predictivo.")
        else:
            with st.spinner(f"Entrenando modelos en tiempo real y prediciendo {forecast_horizon} horas..."):
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
                            
                            color = "blue" if model == "Prophet" else "red"
                            # Quitar puntos si es más de 1 semana para no saturar la vista
                            graf_mode = 'lines+markers' if forecast_horizon <= 168 else 'lines'
                            fig3.add_trace(go.Scatter(
                                x=df_pred["Fecha/Hora"],
                                y=df_pred["Viajes Predichos"],
                                mode=graf_mode,
                                name=f"{model} Forecast",
                                line=dict(color=color, width=2)
                            ))
                        else:
                            st.error(f"Error de la API para {model}: {res.text}")
                    except Exception as e:
                        st.error(f"Asegúrate de tener la API corriendo. Error conectando para {model}.")
                
                fig3.update_layout(
                    title=f"Comparativa Predictiva (Zona {selected_zone}): Próximas {forecast_horizon} horas",
                    xaxis_title="Fecha y Hora",
                    yaxis_title="Volumen de Viajes",
                    hovermode="x unified",
                    template="plotly_white",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig3, use_container_width=True)
                st.info("💡 **Insight de Negocio:** Prophet (Línea Azul) logra proyectar y adaptarse de manera más real a los picos atípicos de tráfico en las horas punta de las tardes, mientras que SARIMA (Línea Roja) suaviza excesivamente la curva apostando al promedio histórico. Recomendamos a la gerencia utilizar Prophet para la proyección del dimensionamiento de la flota a largo plazo.")
