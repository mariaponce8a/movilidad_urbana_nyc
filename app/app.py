"""
Dashboard — Movilidad Urbana NYC
==================================
Visualiza los patrones de demanda de taxis amarillos en Nueva York
consumiendo la API FastAPI local.

Componentes:
  1. 🗺️  Mapa de calor interactivo (Folium) con slider de hora
  2. 📊  Gráfico de barras — viajes totales por hora del día
  3. 🔥  Heatmap Seaborn — demanda por hora × día de semana

Uso:
  # Terminal 1 — API:
  uvicorn app.api:app --reload --port 8000

  # Terminal 2 — Dashboard:
  streamlit run app/app.py

  (ambos se ejecutan desde la raíz del proyecto)
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="🚕 Movilidad Urbana NYC",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
API_BASE = "http://localhost:8000"
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Coordenadas centradas en Manhattan para el mapa base
NYC_CENTER = [40.7128, -74.0060]

# ---------------------------------------------------------------------------
# Helpers para consumir la API
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300)  # caché de 5 minutos
def obtener_heatmap(hour: int) -> list:
    """Obtiene los puntos de calor para una hora específica desde la API."""
    try:
        r = requests.get(f"{API_BASE}/trips/heatmap", params={"hour": hour}, timeout=10)
        r.raise_for_status()
        return r.json().get("puntos", [])
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return []


@st.cache_data(ttl=300)
def obtener_curva_demanda() -> pd.DataFrame:
    """Obtiene la curva de demanda por hora del día desde la API."""
    try:
        r = requests.get(f"{API_BASE}/trips/demand_curve", timeout=10)
        r.raise_for_status()
        datos = r.json().get("datos", [])
        return pd.DataFrame(datos)
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def obtener_heatmap_temporal() -> pd.DataFrame:
    """Obtiene la tabla hora × día de semana desde la API."""
    try:
        r = requests.get(f"{API_BASE}/trips/demand_heatmap", timeout=10)
        r.raise_for_status()
        datos = r.json().get("datos", [])
        return pd.DataFrame(datos)
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return pd.DataFrame()


def verificar_api() -> bool:
    """Comprueba si la API está disponible."""
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/NYC_taxi_logo.svg/320px-NYC_taxi_logo.svg.png", width=100)
    st.markdown("## 🚕 Movilidad Urbana NYC")
    st.markdown(
        "Dashboard de análisis geoespacial de patrones de demanda "
        "de taxis amarillos en Nueva York — **Enero 2025**."
    )
    st.divider()

    # Estado de la API
    api_ok = verificar_api()
    if api_ok:
        st.success("✅ API conectada")
    else:
        st.error("❌ API no disponible")
        st.code("uvicorn app.api:app --reload --port 8000", language="bash")
        st.caption("Ejecuta este comando desde la raíz del proyecto en otra terminal.")

    st.divider()
    st.markdown("### ℹ️ Acerca de")
    st.markdown(
        "- **Dataset**: Yellow Taxi TLC, enero 2025\n"
        "- **Viajes**: ~3 M registros\n"
        "- **Variable objetivo**: `total_viajes` por zona y hora\n"
        "- **Técnica**: Análisis geoespacial\n"
        "- **Mapa**: OpenStreetMap (sin token)"
    )

# ---------------------------------------------------------------------------
# Título principal
# ---------------------------------------------------------------------------
st.title("🚕 Análisis de Movilidad Urbana — Nueva York")
st.markdown(
    "Identificación de **hotspots de demanda** de transporte y variación "
    "de actividad por hora del día y día de la semana."
)
st.divider()

if not api_ok:
    st.warning(
        "⚠️ La API FastAPI no está corriendo. "
        "Inicia el servidor con el comando mostrado en la barra lateral.",
        icon="⚠️",
    )
    st.stop()

# ---------------------------------------------------------------------------
# SECCIÓN 1 — Mapa de calor interactivo
# ---------------------------------------------------------------------------
st.header("🗺️ Mapa de calor interactivo — Recogidas por hora")
st.markdown(
    "El mapa muestra la **densidad de recogidas** de taxi en cada zona de NYC "
    "para la hora seleccionada. Las zonas más calientes (rojo) concentran "
    "mayor demanda."
)

col_slider, col_info = st.columns([3, 1])

with col_slider:
    hora_seleccionada = st.slider(
        "🕐 Hora del día",
        min_value=0,
        max_value=23,
        value=8,
        step=1,
        format="%d:00 h",
        help="Desliza para ver cómo cambia la demanda a lo largo del día",
    )

with col_info:
    # Clasificar la hora en franjas horarias
    if 6 <= hora_seleccionada <= 9:
        franja = "🌅 Hora punta mañana"
        color_franja = "orange"
    elif 17 <= hora_seleccionada <= 20:
        franja = "🌆 Hora punta tarde"
        color_franja = "orange"
    elif 22 <= hora_seleccionada or hora_seleccionada <= 4:
        franja = "🌙 Noche / madrugada"
        color_franja = "blue"
    else:
        franja = "☀️ Hora valle"
        color_franja = "green"
    st.metric("Franja horaria", franja)

# Cargar puntos desde la API
with st.spinner(f"Cargando datos para las {hora_seleccionada}:00 h..."):
    puntos = obtener_heatmap(hora_seleccionada)

if puntos is None:
    st.error("No se pudo conectar con la API.")
elif len(puntos) == 0:
    st.warning("No hay datos para esta hora.")
else:
    # Construir mapa Folium
    mapa = folium.Map(
        location=NYC_CENTER,
        zoom_start=11,
        tiles="OpenStreetMap",
    )

    # Normalizar pesos para el HeatMap (0–1)
    pesos = [p[2] for p in puntos]
    max_peso = max(pesos) if pesos else 1
    puntos_norm = [[p[0], p[1], p[2] / max_peso] for p in puntos]

    HeatMap(
        puntos_norm,
        radius=20,
        blur=15,
        min_opacity=0.3,
        gradient={0.2: "blue", 0.5: "lime", 0.8: "orange", 1.0: "red"},
    ).add_to(mapa)

    # Título del mapa
    folium.map.Marker(
        [40.91, -74.02],
        icon=folium.DivIcon(
            html=f'<div style="font-size:14px;font-weight:bold;color:#333;'
                 f'background:rgba(255,255,255,0.8);padding:5px 10px;border-radius:5px;">'
                 f'🕐 {hora_seleccionada:02d}:00 h — {len(puntos)} zonas activas</div>',
            icon_size=(280, 36),
        ),
    ).add_to(mapa)

    st_folium(mapa, width="100%", height=500, returned_objects=[])

    st.caption(
        f"📍 Mostrando {len(puntos)} zonas con actividad a las "
        f"{hora_seleccionada:02d}:00 h. "
        "Mapa base: © OpenStreetMap contributors."
    )

st.divider()

# ---------------------------------------------------------------------------
# SECCIÓN 2 — Gráfico de barras: demanda por hora del día
# ---------------------------------------------------------------------------
st.header("📊 Demanda total por hora del día")
st.markdown(
    "Número de viajes iniciados en cada hora del día (agregado de todo enero 2025). "
    "Permite identificar las **horas punta** y los **valles de demanda**."
)

with st.spinner("Cargando curva de demanda..."):
    df_demanda = obtener_curva_demanda()

if df_demanda is None:
    st.error("No se pudo conectar con la API.")
elif df_demanda.empty:
    st.warning("No hay datos de demanda disponibles.")
else:
    # Añadir columna de color según franja horaria
    def clasificar_hora(h):
        if 6 <= h <= 9:
            return "Hora punta mañana"
        elif 17 <= h <= 20:
            return "Hora punta tarde"
        elif h >= 22 or h <= 4:
            return "Noche / madrugada"
        else:
            return "Hora valle"

    df_demanda["franja"] = df_demanda["hora"].apply(clasificar_hora)
    df_demanda["hora_str"] = df_demanda["hora"].apply(lambda h: f"{h:02d}:00")

    color_map = {
        "Hora punta mañana": "#FF6B35",
        "Hora punta tarde": "#F7931E",
        "Noche / madrugada": "#4A90D9",
        "Hora valle": "#7BC67E",
    }

    fig_barras = px.bar(
        df_demanda,
        x="hora_str",
        y="total_viajes",
        color="franja",
        color_discrete_map=color_map,
        labels={
            "hora_str": "Hora del día",
            "total_viajes": "Total de viajes",
            "franja": "Franja horaria",
        },
        title="Viajes totales por hora del día — Enero 2025",
    )
    fig_barras.update_layout(
        xaxis_title="Hora del día",
        yaxis_title="Total de viajes",
        legend_title="Franja horaria",
        plot_bgcolor="white",
        height=400,
    )
    fig_barras.update_xaxes(tickangle=-45)

    st.plotly_chart(fig_barras, use_container_width=True)

    # Métricas clave
    col1, col2, col3, col4 = st.columns(4)
    hora_pico = df_demanda.loc[df_demanda["total_viajes"].idxmax()]
    hora_valle = df_demanda.loc[df_demanda["total_viajes"].idxmin()]

    with col1:
        st.metric("🏆 Hora pico", f"{int(hora_pico['hora']):02d}:00 h")
    with col2:
        st.metric("📈 Viajes en hora pico", f"{int(hora_pico['total_viajes']):,}")
    with col3:
        st.metric("📉 Hora valle", f"{int(hora_valle['hora']):02d}:00 h")
    with col4:
        st.metric("📊 Total viajes (mes)", f"{int(df_demanda['total_viajes'].sum()):,}")

st.divider()

# ---------------------------------------------------------------------------
# SECCIÓN 3 — Heatmap Seaborn: hora × día de semana
# ---------------------------------------------------------------------------
st.header("🔥 Patrón de demanda: Hora × Día de semana")
st.markdown(
    "Este mapa de calor revela cómo varía la demanda según el **día de la semana** "
    "y la **hora del día**. Las celdas más oscuras indican mayor actividad. "
    "Permite comparar días hábiles (lunes–viernes) con fines de semana."
)

with st.spinner("Cargando datos temporales..."):
    df_temporal = obtener_heatmap_temporal()

if df_temporal is None:
    st.error("No se pudo conectar con la API.")
elif df_temporal.empty:
    st.warning("No hay datos temporales disponibles.")
else:
    # Construir tabla pivote hora × día
    pivot = df_temporal.pivot_table(
        index="hora",
        columns="dia_semana",
        values="total_viajes",
        aggfunc="sum",
        fill_value=0,
    )

    # Reordenar columnas y asignar nombres de días
    cols_ordenadas = sorted(pivot.columns)
    pivot = pivot[cols_ordenadas]
    pivot.columns = [DIAS_SEMANA[d] for d in cols_ordenadas]
    pivot.index = [f"{h:02d}:00" for h in pivot.index]

    # Normalizar por columna para ver patrones relativos
    col_raw, col_norm = st.columns(2)

    with col_raw:
        st.subheader("Valores absolutos")
        fig_raw, ax_raw = plt.subplots(figsize=(8, 9))
        sns.heatmap(
            pivot,
            ax=ax_raw,
            cmap="YlOrRd",
            fmt=",d",
            annot=pivot.applymap(lambda x: f"{x//1000}k" if x >= 1000 else str(x)),
            annot_kws={"size": 7},
            linewidths=0.3,
            cbar_kws={"label": "Total viajes"},
        )
        ax_raw.set_title("Viajes totales por hora y día", fontsize=13, pad=12)
        ax_raw.set_xlabel("Día de la semana", fontsize=11)
        ax_raw.set_ylabel("Hora del día", fontsize=11)
        ax_raw.tick_params(axis="x", rotation=30)
        plt.tight_layout()
        st.pyplot(fig_raw, use_container_width=True)

    with col_norm:
        st.subheader("Normalizado por día")
        pivot_norm = pivot.div(pivot.max())  # 0–1 por columna

        fig_norm, ax_norm = plt.subplots(figsize=(8, 9))
        sns.heatmap(
            pivot_norm,
            ax=ax_norm,
            cmap="Blues",
            vmin=0,
            vmax=1,
            linewidths=0.3,
            cbar_kws={"label": "Intensidad relativa (0–1)"},
        )
        ax_norm.set_title("Intensidad relativa de demanda", fontsize=13, pad=12)
        ax_norm.set_xlabel("Día de la semana", fontsize=11)
        ax_norm.set_ylabel("Hora del día", fontsize=11)
        ax_norm.tick_params(axis="x", rotation=30)
        plt.tight_layout()
        st.pyplot(fig_norm, use_container_width=True)

    # Interpretación automática
    st.markdown("### 💡 Interpretación")

    max_hora = pivot.sum(axis=1).idxmax()
    max_dia = pivot.sum(axis=0).idxmax()
    min_hora = pivot.sum(axis=1).idxmin()

    st.info(
        f"📌 **Hora de mayor demanda global**: {max_hora} — "
        f"mayor actividad acumulada en todos los días.\n\n"
        f"📌 **Día de mayor demanda**: {max_dia} — "
        f"concentra la mayor cantidad de viajes del mes.\n\n"
        f"📌 **Hora de menor demanda**: {min_hora} — "
        f"valle de actividad donde la flota puede redistribuirse."
    )

st.divider()

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.85em; padding: 20px 0;'>
        🚕 <strong>Movilidad Urbana NYC</strong> — Análisis geoespacial de taxis amarillos<br>
        Datos: NYC Taxi & Limousine Commission (TLC) · Enero 2025<br>
        Mapa base: © OpenStreetMap contributors · Sin dependencia de tokens de API
    </div>
    """,
    unsafe_allow_html=True,
)
