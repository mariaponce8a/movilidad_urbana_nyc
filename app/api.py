"""
API FastAPI — Movilidad Urbana NYC
===================================
Expone los datos procesados de viajes de taxi amarillo de NYC
para ser consumidos por el dashboard de Streamlit.

Endpoints:
  GET /trips/heatmap?hour=8      → Puntos de calor para una hora específica
  GET /trips/demand_curve        → Serie de demanda agregada por hora del día
  GET /trips/demand_heatmap      → Tabla pivote hora × día de semana
  GET /health                    → Estado de la API

Uso:
  uvicorn app.api:app --reload --port 8000
  (ejecutar desde la raíz del proyecto)
"""

import os
import json
import logging
from pathlib import Path
from functools import lru_cache
from typing import List

import pandas as pd
import geopandas as gpd
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rutas de datos (relativas a la raíz del proyecto)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_VIAJES = BASE_DIR / "datos" / "procesados" / "viajes_procesados.parquet"
RUTA_DEMANDA = BASE_DIR / "datos" / "procesados" / "demanda_por_zona.csv"
RUTA_GEOJSON = BASE_DIR / "datos" / "raw" / "taxi_zones.geojson"

# Columnas mínimas que necesitamos del parquet (ahorra memoria)
COLUMNAS_PARQUET = ["PULocationID", "hora_dia", "dia_semana"]

# Nombres legibles de días de la semana
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# ---------------------------------------------------------------------------
# Inicialización de FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="🚕 Movilidad Urbana NYC — API",
    description=(
        "API para análisis de patrones de movilidad urbana en Nueva York "
        "basada en datos de taxis amarillos (Yellow Cab TLC)."
    ),
    version="1.0.0",
)

# CORS: permite que Streamlit (en otro puerto) consuma esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Carga de datos al iniciar la aplicación (se hace una sola vez)
# ---------------------------------------------------------------------------
_viajes: pd.DataFrame = None
_centroides: dict = {}     # {LocationID: [lat, lon]}


@app.on_event("startup")
async def cargar_datos():
    """Carga los datasets al arrancar la API para evitar lecturas repetidas."""
    global _viajes, _centroides

    # 1. Datos de viajes procesados
    if not RUTA_VIAJES.exists():
        logger.warning(f"Archivo no encontrado: {RUTA_VIAJES}. "
                       "Ejecuta el pipeline primero: python scripts/pipeline.py")
    else:
        logger.info("Cargando viajes procesados...")
        _viajes = pd.read_parquet(RUTA_VIAJES, columns=COLUMNAS_PARQUET)
        # Aseguramos tipos correctos
        _viajes["hora_dia"] = _viajes["hora_dia"].astype(int)
        _viajes["dia_semana"] = _viajes["dia_semana"].astype(int)
        logger.info(f"✅ Viajes cargados: {len(_viajes):,} registros")

    # 2. Centroides de zonas TLC desde GeoJSON
    if not RUTA_GEOJSON.exists():
        logger.warning(f"GeoJSON no encontrado: {RUTA_GEOJSON}")
    else:
        logger.info("Cargando zonas TLC...")
        gdf = gpd.read_file(RUTA_GEOJSON)

        # Calcular centroide de cada zona en CRS geográfico (lat/lon)
        gdf = gdf.to_crs(epsg=4326)
        gdf["centroid"] = gdf.geometry.centroid
        gdf["lat"] = gdf["centroid"].y
        gdf["lon"] = gdf["centroid"].x

        # Guardar en dict {LocationID: [lat, lon]}
        # El GeoJSON de TLC usa la columna "LocationID"
        id_col = "LocationID" if "LocationID" in gdf.columns else "objectid"
        for _, row in gdf.iterrows():
            try:
                loc_id = int(row[id_col])
                _centroides[loc_id] = [float(row["lat"]), float(row["lon"])]
            except (ValueError, KeyError):
                continue
        logger.info(f"✅ Centroides cargados: {len(_centroides)} zonas")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _verificar_datos():
    """Lanza HTTPException si los datos no están cargados."""
    if _viajes is None or _viajes.empty:
        raise HTTPException(
            status_code=503,
            detail=(
                "Datos no disponibles. "
                "Ejecuta el pipeline primero: python scripts/pipeline.py"
            ),
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Status"])
def health_check():
    """Verifica que la API está en línea y los datos están cargados."""
    return {
        "status": "ok",
        "viajes_cargados": _viajes is not None,
        "total_viajes": len(_viajes) if _viajes is not None else 0,
        "zonas_con_centroide": len(_centroides),
    }


@app.get("/trips/heatmap", tags=["Mapas"])
def heatmap_por_hora(
    hour: int = Query(
        default=8,
        ge=0,
        le=23,
        description="Hora del día (0–23) para filtrar los viajes",
    )
):
    """
    Retorna los puntos de calor (lat, lon, peso) para una hora específica.

    Cada punto representa una zona TLC con su centroide geográfico y el
    número de viajes en esa zona durante la hora indicada como peso.
    El mapa de calor de Folium usa esta lista directamente.

    Ejemplo: GET /trips/heatmap?hour=8
    """
    _verificar_datos()

    if not _centroides:
        raise HTTPException(
            status_code=503,
            detail="Centroides de zonas no disponibles. Verifica taxi_zones.geojson."
        )

    # Filtrar viajes de la hora solicitada y contar por zona
    df_hora = _viajes[_viajes["hora_dia"] == hour]
    conteo = df_hora.groupby("PULocationID").size().reset_index(name="viajes")

    # Construir lista de puntos [lat, lon, peso]
    puntos: List[List[float]] = []
    for _, row in conteo.iterrows():
        loc_id = int(row["PULocationID"])
        if loc_id in _centroides:
            lat, lon = _centroides[loc_id]
            peso = float(row["viajes"])
            puntos.append([lat, lon, peso])

    return {
        "hora": hour,
        "total_puntos": len(puntos),
        "puntos": puntos,  # [[lat, lon, peso], ...]
    }


@app.get("/trips/demand_curve", tags=["Análisis temporal"])
def curva_de_demanda():
    """
    Retorna la demanda total de viajes agregada por hora del día (0–23).

    Útil para el gráfico de barras que muestra los picos de actividad
    durante el día (horas punta de mañana y tarde/noche).

    Ejemplo: GET /trips/demand_curve
    """
    _verificar_datos()

    demanda = (
        _viajes.groupby("hora_dia")
        .size()
        .reset_index(name="total_viajes")
        .sort_values("hora_dia")
    )

    return {
        "datos": [
            {"hora": int(row["hora_dia"]), "total_viajes": int(row["total_viajes"])}
            for _, row in demanda.iterrows()
        ]
    }


@app.get("/trips/demand_heatmap", tags=["Análisis temporal"])
def heatmap_hora_dia_semana():
    """
    Retorna la demanda agregada en una tabla pivote hora × día de semana.

    Permite construir el heatmap de Seaborn que identifica:
    - Picos horarios (mañana/tarde-noche)
    - Diferencias entre días hábiles (0–4) y fines de semana (5–6)

    Ejemplo: GET /trips/demand_heatmap
    """
    _verificar_datos()

    demanda = (
        _viajes.groupby(["hora_dia", "dia_semana"])
        .size()
        .reset_index(name="total_viajes")
    )

    # Convertir a lista de registros
    registros = [
        {
            "hora": int(r["hora_dia"]),
            "dia_semana": int(r["dia_semana"]),
            "nombre_dia": DIAS_SEMANA[int(r["dia_semana"])],
            "total_viajes": int(r["total_viajes"]),
        }
        for _, r in demanda.iterrows()
    ]

    return {
        "dias_semana": DIAS_SEMANA,
        "datos": registros,
    }
