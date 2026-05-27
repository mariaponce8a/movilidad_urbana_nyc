import os
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

# En producción, definir la variable de entorno API_URL con la URL de Render
# En local, usa http://localhost:8000 automáticamente
API_URL = "http://localhost:8000" #"https://movilidad-urbana-nyc-oue1.onrender.com"

st.title("Análisis de Demanda y Predicción de Movilidad - NYC")
st.markdown(
    "Dashboard interactivo para visualizar puntos de calor espaciales y predecir demanda futura mediante modelos econométricos y de Inteligencia Artificial (Prophet y SARIMA)."
)

# --- KPIs GENERALES ---
st.markdown("---")
try:
    kpi_res = requests.get(f"{API_URL}/trips/kpis", timeout=5)
    if kpi_res.status_code == 200:
        kpi = kpi_res.json()

        st.subheader("Indicadores Clave — Enero 2025")
        k1, k2, k3, k4 = st.columns(4)
        k5, k6, k7, k8 = st.columns(4)

        k1.metric(
            label="Total de Viajes",
            value=f"{kpi['total_viajes']:,}",
            help="Suma total de viajes de taxi registrados en enero 2025.",
        )
        k2.metric(
            label="Promedio Diario",
            value=f"{kpi['promedio_diario']:,}",
            help="Número promedio de viajes por día durante el mes.",
        )
        k3.metric(
            label="Hora Pico",
            value=f"{kpi['hora_pico']}:00 h",
            delta=f"{kpi['viajes_hora_pico']:,} viajes",
            delta_color="normal",
            help="Hora del día con mayor volumen de viajes en el período completo.",
        )
        k4.metric(
            label="Hora Valle",
            value=f"{kpi['hora_valle']}:00 h",
            help="Hora del día con menor actividad registrada.",
        )
        k5.metric(
            label="Ratio Pico / Valle",
            value=f"{kpi['ratio_pico_valle']}x",
            help="Cuántas veces más viajes hay en la hora pico vs la hora de menor demanda.",
        )
        finde_delta = f"{'+' if kpi['variacion_finde_pct'] >= 0 else ''}{kpi['variacion_finde_pct']}%"
        k6.metric(
            label="Fin de Semana vs Hábil",
            value=finde_delta,
            delta=finde_delta,
            delta_color="normal",
            help="Variación porcentual del volumen de viajes en fin de semana respecto a días hábiles.",
        )
        k7.metric(
            label="Zona Más Demandada",
            value=kpi["zona_top_nombre"],
            delta=f"ID {kpi['zona_top_id']}",
            delta_color="off",
            help="Zona con el mayor número de recogidas acumuladas en enero 2025.",
        )
        k8.metric(
            label="Zonas Geoespaciales Activas",
            value=f"{kpi['zonas_activas']:,}",
            help="Número de celdas geográficas únicas (lat/lon binificadas) con al menos un viaje registrado.",
        )
except Exception:
    st.warning("KPIs no disponibles. Asegúrate de que la API esté corriendo.")
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
    163: {"name": "Midtown North", "lat": 40.7650, "lon": -73.9800},
}

# --- VISUALIZACIONES PRINCIPALES ---
tab1, tab2, tab3 = st.tabs(
    ["Mapa Geoespacial", "Patrones Temporales", "Predicción de Demanda"]
)


# --- FUNCIONES CACHEADAS (evitan re-peticiones HTTP en cada rerun) ---
@st.cache_data(ttl=300)
def fetch_heatmap(hour: int):
    try:
        res = requests.get(f"{API_URL}/trips/heatmap?hour={hour}", timeout=5)
        if res.status_code == 200:
            return res.json()["data"]
    except Exception:
        pass
    return []


@st.cache_data(ttl=300)
def fetch_top_zones(hour: int, n: int = 5):
    try:
        res = requests.get(f"{API_URL}/trips/top_zones?hour={hour}&n={n}", timeout=5)
        if res.status_code == 200:
            return res.json()["zones"]
    except Exception:
        pass
    return []


# --- PESTAÑA 1: MAPA GEOESPACIAL ---
with tab1:
    # --- FILTROS GEOESPACIALES EMBEBIDOS ---
    st.markdown("**Filtros Geoespaciales**")
    selected_hour = st.slider(
        "Selecciona la hora del día (Mapa):", min_value=0, max_value=23, value=8, step=1
    )
    st.markdown("---")

    st.subheader(f"Mapa de Calor (Demanda a las {selected_hour}:00)")
    st.markdown(
        "Visualiza la concentración física de viajes a través de Manhattan según la hora seleccionada."
    )

    # --- Session state para posición del mapa ---
    if "map_center" not in st.session_state:
        st.session_state.map_center = [40.7580, -73.9855]
        st.session_state.map_zoom = 11
    # Resetear vista si el usuario cambia de hora
    if st.session_state.get("last_hour") != selected_hour:
        st.session_state.map_center = [40.7580, -73.9855]
        st.session_state.map_zoom = 11
        st.session_state.last_hour = selected_hour

    # --- Fetch de datos (cacheado) ---
    heatmap_data = fetch_heatmap(selected_hour)
    top_zones_data = fetch_top_zones(selected_hour)
    colores = ["gold", "silver", "#cd7f32", "orange", "red"]
    emojis_rank = ["🥇", "🥈", "🥉", "🟠", "🔴"]

    # --- Layout: mapa ancho completo ---
    if not heatmap_data:
        st.error(
            "Error al cargar datos del mapa. Asegúrate de que la API esté corriendo."
        )
    else:
        try:
            m = folium.Map(
                location=st.session_state.map_center,
                zoom_start=st.session_state.map_zoom,
                tiles="CartoDB positron",
            )
            HeatMap(heatmap_data, radius=12, blur=15, max_zoom=1).add_to(m)

            for zona in top_zones_data:
                rank = zona["rank"]
                color = colores[rank - 1] if rank <= len(colores) else "red"
                folium.CircleMarker(
                    location=[zona["lat"], zona["lon"]],
                    radius=12 + (5 - rank) * 1.5,
                    color="white",
                    weight=2,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.85,
                    popup=folium.Popup(
                        f"""
                        <b>#{rank} Zona más demandada</b><br>
                        Lat: {zona["lat"]:.4f} | Lon: {zona["lon"]:.4f}<br>
                        <b>{zona["viajes"]:,} viajes</b> a las {selected_hour}:00h
                        """,
                        max_width=220,
                    ),
                    tooltip=f"#{rank} · {zona['viajes']:,} viajes",
                ).add_to(m)

            st_folium(m, use_container_width=True, height=500)
        except Exception as e:
            st.error(f"Error al renderizar el mapa: {e}")

    # --- LEYENDA HORIZONTAL (tarjetas debajo del mapa) ---
    if top_zones_data:
        st.markdown("**Zonas con mayor demanda**")
        zona_cols = st.columns(len(top_zones_data))
        for i, zona in enumerate(top_zones_data):
            rank = zona["rank"]
            nombre = zona.get("nombre", f"Zona #{rank}")
            with zona_cols[i]:
                st.markdown(
                    f"<div style='text-align:center; padding:8px; border:1px solid #ddd; border-radius:8px;'>"
                    f"<b>#{rank}</b><br>"
                    f"<span style='font-size:0.85rem'>{nombre}</span><br>"
                    f"<small>{zona['viajes']:,} viajes</small>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # --- INSIGHT MAPA ---
    if selected_hour in range(7, 10):
        st.info(
            "**Hora pico matutina (7–9 AM):** La demanda se concentra en Midtown y el Upper East Side, reflejando los desplazamientos hacia oficinas y el centro financiero. Las zonas cercanas a Penn Station y Grand Central muestran la mayor saturación."
        )
    elif selected_hour in range(17, 20):
        st.info(
            "**Hora pico vespertina (5–7 PM):** El flujo se invierte: Midtown sigue siendo un núcleo, pero aparecen focos en el Upper West Side y zonas residenciales. Es el momento de mayor volumen total del día."
        )
    elif selected_hour in range(22, 24) or selected_hour in range(0, 3):
        st.info(
            "**Horario nocturno (10 PM–2 AM):** La actividad se desplaza hacia zonas de entretenimiento como Hell's Kitchen y el Village. JFK muestra actividad constante por vuelos nocturnos."
        )
    elif selected_hour in range(3, 7):
        st.info(
            "**Madrugada (3–6 AM):** Volumen mínimo del día. Los viajes existentes corresponden principalmente a trabajadores de turno nocturno y pasajeros con vuelos muy tempranos en JFK."
        )
    else:
        st.info(
            "**Lectura del mapa:** Cada punto de calor representa la coordenada binificada (redondeada a 2 decimales) de una zona de recogida. La intensidad del color indica el volumen de viajes. Usa el slider superior para comparar cómo cambia la distribución espacial a lo largo del día."
        )

# --- PESTAÑA 2: PATRONES TEMPORALES ---
with tab2:
    st.subheader("Demanda Agregada a lo largo del día")
    try:
        res = requests.get(f"{API_URL}/trips/demand_curve")
        if res.status_code == 200:
            curve_data = res.json()
            df_curve = pd.DataFrame(
                {"Hora": curve_data["x"], "Viajes Totales": curve_data["y"]}
            )

            fig1 = px.bar(
                df_curve,
                x="Hora",
                y="Viajes Totales",
                color="Viajes Totales",
                color_continuous_scale="Viridis",
                title="Volumen Total de Viajes por Hora en Enero 2025",
            )
            fig1.update_layout(xaxis=dict(tickmode="linear"), template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)

            # --- INSIGHT CURVA DE DEMANDA ---
            hora_pico = df_curve.loc[df_curve["Viajes Totales"].idxmax(), "Hora"]
            hora_min = df_curve.loc[df_curve["Viajes Totales"].idxmin(), "Hora"]
            st.info(
                f"**Interpretación de la curva diaria:** La demanda sigue un patrón bimodal clásico en ciudades metropolitanas: "
                f"un primer pico entre las **6–9 AM** (hora de entrada al trabajo) y un segundo pico más pronunciado entre las **17–19 PM** "
                f"(salida de oficinas). La hora de mayor demanda en enero 2025 fue las **{hora_pico}:00 h**, "
                f"mientras que el punto de menor actividad se registró a las **{hora_min}:00 h**. "
                f"Este patrón es estable semana a semana y es la variable más importante para los modelos predictivos."
            )
    except:
        st.warning("No se pudo cargar la curva de demanda.")

    st.markdown("---")

    st.subheader("Concentración Temporal: Hora vs Día de la Semana")
    st.markdown(
        "Identifica las diferencias de comportamiento entre días hábiles y fines de semana."
    )

    # Toggle Seaborn / Plotly
    tipo_grafico = st.radio(
        "Elige el motor de visualización:",
        ["Plotly Express (Interactivo)", "Seaborn (Estático)"],
        horizontal=True,
    )

    try:
        res = requests.get(f"{API_URL}/trips/heatmap_day_hour")
        if res.status_code == 200:
            data = res.json()
            df_pivot = pd.DataFrame(
                data["valores"], index=data["dias"], columns=data["horas"]
            )

            if tipo_grafico == "Seaborn (Estático)":
                fig2, ax = plt.subplots(figsize=(15, 6))
                sns.heatmap(df_pivot, cmap="Oranges", ax=ax, linewidths=0.5)
                plt.xlabel("Hora del Día")
                plt.ylabel("Día de la Semana")
                st.pyplot(fig2)
            else:
                # Plotly Express
                fig_px = px.imshow(
                    df_pivot,
                    labels=dict(x="Hora del Día", y="Día de la Semana", color="Viajes"),
                    x=df_pivot.columns,
                    y=df_pivot.index,
                    color_continuous_scale="Oranges",
                    aspect="auto",
                )
                fig_px.update_layout(template="plotly_white")
                st.plotly_chart(fig_px, use_container_width=True)
                # --- INSIGHT HEATMAP DÍA×HORA ---
            st.info(
                "**Interpretación del Heatmap Día × Hora:** Las celdas más oscuras (rojo intenso) indican las combinaciones "
                "de mayor demanda. Se observan tres patrones clave:\n\n"
                "- **Días laborales (Lun–Vie):** Dos franjas rojas claras en la mañana (7–9 AM) y tarde (5–7 PM), "
                "confirmando el patrón commuter.\n"
                "- **Viernes y Sábado noche (9 PM–1 AM):** Alta demanda nocturna asociada al ocio y entretenimiento.\n"
                "- **Domingo:** Patrón más plano y suave, con un leve repunte al mediodía. Es el día de menor demanda "
                "en horas pico laborales pero con actividad nocturna moderada.\n\n"
                "Esta segmentación es fundamental para ajustar los modelos predictivos con estacionalidad semanal."
            )

    except:
        st.warning("No se pudo cargar la Matriz de Calor Temporal.")

# --- PESTAÑA 3: PREDICCIONES (IA) ---
with tab3:
    import datetime as dt

    st.markdown("**Configuración de la Predicción**")

    # Diccionario auxiliar {zone_id: nombre} construido desde top10_zones_info
    top10_zones = {zid: info["name"] for zid, info in top10_zones_info.items()}

    col_ctrl1, col_ctrl2 = st.columns([2, 2])

    with col_ctrl1:
        selected_zone_name = st.selectbox(
            "Zona de análisis:",
            options=list(top10_zones.values()),
            index=0,
        )
        selected_zone = next(
            zid for zid, name in top10_zones.items() if name == selected_zone_name
        )

    with col_ctrl2:
        selected_models = st.multiselect(
            "Modelos predictivos:",
            options=["Prophet", "SARIMA"],
            default=["Prophet", "SARIMA"],
        )

    # --- FILTRO DE RANGO DE FECHAS ---
    st.markdown("**Rango de fechas para la predicción**")
    hoy = dt.date.today()
    fecha_min = dt.date(2025, 2, 1)  # primer día predicible tras datos de enero 2025
    fecha_max = hoy + dt.timedelta(days=365)
    col_fecha1, col_fecha2 = st.columns(2)
    with col_fecha1:
        fecha_inicio = st.date_input(
            "Fecha de inicio del pronóstico:",
            value=hoy,
            min_value=fecha_min,
            max_value=fecha_max,
            key="pred_fecha_inicio",
        )
    with col_fecha2:
        fecha_fin = st.date_input(
            "Fecha de fin del pronóstico:",
            value=hoy + dt.timedelta(days=7),
            min_value=fecha_min + dt.timedelta(days=1),
            max_value=fecha_max,
            key="pred_fecha_fin",
        )

    # Validar rango y calcular horizonte en horas
    if fecha_fin <= fecha_inicio:
        st.warning("⚠️ La fecha de fin debe ser posterior a la fecha de inicio.")
        forecast_horizon = 24
        fecha_valida = False
    else:
        delta_dias = (fecha_fin - fecha_inicio).days
        forecast_horizon = delta_dias * 24  # horas totales del rango
        fecha_valida = True
        st.caption(
            f"📅 Rango seleccionado: **{fecha_inicio.strftime('%d %b %Y')}** → **{fecha_fin.strftime('%d %b %Y')}** "
            f"({delta_dias} día{'s' if delta_dias != 1 else ''} · {forecast_horizon} horas)"
        )

    st.markdown("---")

    st.subheader(f"Predicción: Zona {selected_zone} ({top10_zones[selected_zone]})")
    st.markdown(
        "Utiliza modelos matemáticos para pronosticar la curva de demanda de las próximas horas/días."
    )
    with st.expander("¿Cómo interpretar los modelos?", expanded=False):
        st.markdown(
            "**Prophet (Meta/Facebook):**\n"
            "Modelo aditivo diseñado para series temporales con estacionalidades múltiples (diaria, semanal). "
            "Captura automáticamente los picos de commuters y la diferencia fin de semana/día hábil. "
            "Es robusto ante datos faltantes y tiende a ser más suave en sus predicciones.\n\n"
            "**SARIMA (Seasonal ARIMA):**\n"
            "Modelo econométrico clásico que modela la autocorrelación de la serie (cada hora depende de las anteriores) "
            "con una componente estacional de 24 horas. Es más reactivo a cambios bruscos recientes pero requiere "
            "que la serie sea estacionaria.\n\n"
            "**¿Cuándo confiar más en cada uno?**\n"
            "- Usa **Prophet** para horizontes largos (+48h) donde la estacionalidad semanal importa.\n"
            "- Usa **SARIMA** para horizontes cortos (12–24h) donde el patrón reciente domina.\n"
            "- Si ambas curvas coinciden, la predicción es más confiable."
        )

    if st.button("Generar Pronóstico de Demanda"):
        if not selected_models:
            st.warning("Por favor, selecciona al menos un modelo predictivo.")
        elif not fecha_valida:
            st.warning("Por favor, corrige el rango de fechas antes de continuar.")
        else:
            with st.spinner(
                f"Cargando modelos pre-entrenados y generando pronóstico del {fecha_inicio} al {fecha_fin} ({forecast_horizon} h)..."
            ):
                # Los modelos predicen DESDE el fin de los datos de entrenamiento (31 ene 2025)
                fin_entrenamiento = dt.date(2025, 1, 31)
                # Calcular horas desde fin de entrenamiento hasta fecha_fin del usuario
                horas_totales = max(
                    int((dt.datetime.combine(fecha_fin, dt.time(23, 0)) - dt.datetime.combine(fin_entrenamiento, dt.time())).total_seconds() / 3600),
                    24,
                )

                fig3 = go.Figure()

                for model in selected_models:
                    try:
                        res = requests.get(
                            f"{API_URL}/trips/predict?zone_id={selected_zone}&hours={horas_totales}&model={model.lower()}",
                            timeout=120,
                        )
                        if res.status_code == 200:
                            pred_data = res.json()
                            df_pred = pd.DataFrame(
                                {
                                    "Fecha/Hora": pd.to_datetime(
                                        pred_data["future_dates"]
                                    ),
                                    "Viajes Predichos": pred_data["predictions"],
                                }
                            )

                            # Filtrar al rango de fechas seleccionado
                            fecha_inicio_dt = pd.Timestamp(fecha_inicio)
                            fecha_fin_dt = pd.Timestamp(fecha_fin) + pd.Timedelta(
                                hours=23
                            )
                            df_pred = df_pred[
                                (df_pred["Fecha/Hora"] >= fecha_inicio_dt)
                                & (df_pred["Fecha/Hora"] <= fecha_fin_dt)
                            ]

                            if df_pred.empty:
                                st.warning(
                                    f"No hay datos predichos en el rango para {model}."
                                )
                                continue

                            color = "blue" if model == "Prophet" else "red"
                            graf_mode = (
                                "lines+markers" if forecast_horizon <= 168 else "lines"
                            )
                            fig3.add_trace(
                                go.Scatter(
                                    x=df_pred["Fecha/Hora"],
                                    y=df_pred["Viajes Predichos"],
                                    mode=graf_mode,
                                    name=f"{model} Forecast",
                                    line=dict(color=color, width=2),
                                )
                            )
                        else:
                            st.error(f"Error de la API para {model} (HTTP {res.status_code}): {res.text[:500]}")
                    except Exception as e:
                        st.error(
                            f"Error conectando con la API para {model}: {str(e)}"
                        )

                fig3.update_layout(
                    title=f"Pronóstico {fecha_inicio.strftime('%d %b')} – {fecha_fin.strftime('%d %b %Y')} · Zona {selected_zone} ({top10_zones[selected_zone]})",
                    xaxis_title="Fecha y Hora",
                    yaxis_title="Volumen de Viajes",
                    hovermode="x unified",
                    template="plotly_white",
                    xaxis=dict(
                        range=[
                            pd.Timestamp(fecha_inicio),
                            pd.Timestamp(fecha_fin) + pd.Timedelta(hours=23),
                        ]
                    ),
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                    ),
                )
                st.plotly_chart(fig3, use_container_width=True)
                st.info(
                    "**Insight de Negocio:** Prophet (Línea Azul) logra proyectar y adaptarse de manera más real a los picos atípicos de tráfico en las horas punta de las tardes, mientras que SARIMA (Línea Roja) suaviza excesivamente la curva apostando al promedio histórico. Recomendamos a la gerencia utilizar Prophet para la proyección del dimensionamiento de la flota a largo plazo."
                )
