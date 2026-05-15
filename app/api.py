from fastapi import FastAPI, Query, HTTPException
import pandas as pd
import numpy as np
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import os

warnings.filterwarnings("ignore")

app = FastAPI(
    title="NYC Taxi Mobility API",
    description="API REST para el análisis geoespacial y predictivo de la demanda de taxis en Nueva York (Caso 04).",
    version="1.0.0",
)

# --- CARGA DE DATOS EN MEMORIA ---
# Se cargan al iniciar la API para que las peticiones sean ultrarrápidas
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "datos", "procesados")
DATA_PATH = os.path.abspath(DATA_PATH)  # resolver a ruta absoluta

print(f"[STARTUP] Buscando datos en: {DATA_PATH}")
print(f"[STARTUP] ¿Existe el directorio? {os.path.isdir(DATA_PATH)}")
if os.path.isdir(DATA_PATH):
    print(f"[STARTUP] Archivos encontrados: {os.listdir(DATA_PATH)}")
else:
    print(f"[STARTUP] Contenido de app/: {os.listdir(os.path.dirname(__file__))}")
    project_root = os.path.join(os.path.dirname(__file__), "..")
    print(f"[STARTUP] Contenido de raíz: {os.listdir(project_root)}")

try:
    df_geo = pd.read_parquet(os.path.join(DATA_PATH, "demanda_geo_agregada.parquet"))
    df_ts = pd.read_parquet(
        os.path.join(DATA_PATH, "demanda_top10_series_tiempo.parquet")
    )
    print(f"[STARTUP] ✅ Datos cargados: df_geo={df_geo.shape}, df_ts={df_ts.shape}")
except FileNotFoundError as e:
    print(f"[STARTUP] ❌ Error FileNotFoundError: {e}")
    print(f"[STARTUP] ❌ No se encontraron los archivos Parquet en {DATA_PATH}")
    df_geo = pd.DataFrame()
    df_ts = pd.DataFrame()

# Cargar lookup de zonas para nombres
RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "datos", "raw")
try:
    df_lookup = pd.read_csv(os.path.join(RAW_PATH, "taxi_zone_lookup.csv"))
except Exception:
    df_lookup = pd.DataFrame()


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "NYC Taxi Mobility API is running"}


@app.get("/trips/kpis", tags=["KPIs"])
def get_kpis():
    """
    Calcula y retorna los KPIs generales del dataset de enero 2025.
    """
    if df_geo.empty or df_ts.empty:
        raise HTTPException(status_code=500, detail="Data not loaded")

    # --- KPI 1: Total de viajes en el período ---
    total_viajes = int(df_geo["viajes"].sum())

    # --- KPI 2: Promedio diario (enero = 31 días) ---
    promedio_diario = round(total_viajes / 31, 0)

    # --- KPI 3: Hora pico (mayor volumen agregado) ---
    by_hour = df_geo.groupby("hora_dia")["viajes"].sum()
    hora_pico = int(by_hour.idxmax())
    viajes_hora_pico = int(by_hour.max())

    # --- KPI 4: Hora valle (menor volumen) ---
    hora_valle = int(by_hour.idxmin())
    viajes_hora_valle = int(by_hour.min())

    # --- KPI 5: Ratio pico/valle ---
    ratio_pico_valle = round(viajes_hora_pico / max(viajes_hora_valle, 1), 1)

    # --- KPI 6: Variación fin de semana vs día hábil ---
    dias_habiles = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    dias_finde = ["Saturday", "Sunday"]
    avg_habiles = df_geo[df_geo["dia_semana"].isin(dias_habiles)]["viajes"].sum() / 5
    avg_finde = df_geo[df_geo["dia_semana"].isin(dias_finde)]["viajes"].sum() / 2
    variacion_finde_pct = round(((avg_finde - avg_habiles) / avg_habiles) * 100, 1)

    # --- KPI 7: Zona más demandada (top 10 series) ---
    zona_top = int(df_ts.groupby("PULocationID")["total_viajes"].sum().idxmax())
    top_zones_names = {
        161: "Midtown Center",
        237: "Upper East Side S.",
        236: "Upper East Side N.",
        132: "JFK Airport",
        230: "Times Sq/Theatre",
        186: "Penn Station",
        162: "Midtown East",
        142: "Lincoln Square E.",
        239: "Upper West Side S.",
        163: "Midtown North",
    }
    zona_top_nombre = top_zones_names.get(zona_top, str(zona_top))

    # --- KPI 8: Zonas únicas activas ---
    zonas_activas = int(df_geo[["lat_bin", "lon_bin"]].drop_duplicates().shape[0])

    return {
        "total_viajes": total_viajes,
        "promedio_diario": int(promedio_diario),
        "hora_pico": hora_pico,
        "viajes_hora_pico": viajes_hora_pico,
        "hora_valle": hora_valle,
        "ratio_pico_valle": ratio_pico_valle,
        "variacion_finde_pct": variacion_finde_pct,
        "zona_top_id": zona_top,
        "zona_top_nombre": zona_top_nombre,
        "zonas_activas": zonas_activas,
    }


@app.get("/trips/heatmap", tags=["Geoespacial"])
def get_heatmap_data(
    hour: int = Query(..., ge=0, le=23, description="Hora del día (0-23)"),
):
    """
    Retorna la lista de coordenadas y pesos para el mapa de calor de Folium.
    La rúbrica exige que se entreguen los puntos de recogida de una hora específica.
    """
    if df_geo.empty:
        raise HTTPException(status_code=500, detail="Data not loaded")

    # Filtrar por hora
    df_hour = df_geo[df_geo["hora_dia"] == hour]

    # Agrupar por coordenada binificada para el heatmap
    heatmap_data = df_hour.groupby(["lat_bin", "lon_bin"])["viajes"].sum().reset_index()

    # Formato requerido por Folium: [lat, lon, weight]
    points = heatmap_data[["lat_bin", "lon_bin", "viajes"]].values.tolist()

    return {"hour": hour, "total_points": len(points), "data": points}


@app.get("/trips/top_zones", tags=["Geoespacial"])
def get_top_zones(
    hour: int = Query(..., ge=0, le=23, description="Hora del día (0-23)"),
    n: int = Query(5, ge=1, le=20, description="Número de zonas top a retornar"),
):
    """
    Retorna las N coordenadas con mayor volumen de viajes para la hora dada.
    Se usa para pintar marcadores sobre el heatmap de Folium.
    """
    if df_geo.empty:
        raise HTTPException(status_code=500, detail="Data not loaded")

    df_hour = df_geo[df_geo["hora_dia"] == hour]
    top = (
        df_hour.groupby(["lat_bin", "lon_bin"])["viajes"]
        .sum()
        .reset_index()
        .sort_values("viajes", ascending=False)
        .head(n)
    )

    # Mapa de zonas conocidas lat/lon aproximado para nearest-neighbor simple
    known_zones = {
        161: ("Midtown Center", 40.755, -73.987),
        237: ("Upper East Side South", 40.765, -73.958),
        236: ("Upper East Side North", 40.775, -73.953),
        132: ("JFK Airport", 40.641, -73.778),
        230: ("Times Sq / Theatre District", 40.758, -73.990),
        186: ("Penn Station / Madison Sq W", 40.750, -73.994),
        162: ("Midtown East", 40.752, -73.974),
        142: ("Lincoln Square East", 40.774, -73.983),
        239: ("Upper West Side South", 40.776, -73.981),
        163: ("Midtown North", 40.760, -73.982),
    }

    zonas = []
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lat = round(float(row["lat_bin"]), 4)
        lon = round(float(row["lon_bin"]), 4)
        # Nearest-neighbor: zona conocida más cercana
        zona_nombre = "Zona desconocida"
        min_dist = float("inf")
        for _, (nombre, zlat, zlon) in known_zones.items():
            dist = ((lat - zlat) ** 2 + (lon - zlon) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                zona_nombre = nombre
        zonas.append(
            {
                "rank": rank,
                "lat": lat,
                "lon": lon,
                "viajes": int(row["viajes"]),
                "nombre": zona_nombre,
            }
        )

    return {"hour": hour, "top_n": n, "zones": zonas}


@app.get("/trips/demand_curve", tags=["Temporal"])
def get_demand_curve():
    """
    Serie de demanda por hora del día.
    Agrupa todos los viajes por cada una de las 24 horas.
    """
    if df_geo.empty:
        raise HTTPException(status_code=500, detail="Data not loaded")

    curve = df_geo.groupby("hora_dia")["viajes"].sum().reset_index()

    return {"x": curve["hora_dia"].tolist(), "y": curve["viajes"].tolist()}


@app.get("/trips/heatmap_day_hour", tags=["Temporal"])
def get_heatmap_day_hour():
    """
    Retorna los datos estructurados para crear el Heatmap de Seaborn (Día vs Hora).
    """
    if df_geo.empty:
        raise HTTPException(status_code=500, detail="Data not loaded")

    pivot = df_geo.pivot_table(
        index="dia_semana",
        columns="hora_dia",
        values="viajes",
        aggfunc="sum",
        fill_value=0,
    )

    # Ordenar los días lógicamente
    dias_ordenados = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    pivot = pivot.reindex(dias_ordenados)

    return {
        "dias": pivot.index.tolist(),
        "horas": pivot.columns.tolist(),
        "valores": pivot.values.tolist(),
    }


@app.get("/trips/predict", tags=["Predicción (ML)"])
def predict_demand(
    zone_id: int = Query(
        237, description="ID de la zona de taxi (Ej: 237 para Upper East Side)"
    ),
    hours: int = Query(
        24,
        ge=12,
        le=17520,
        description="Horizonte de predicción en horas (12h a 17520h = 2 años)",
    ),
    model: str = Query("prophet", description="Modelo a usar: 'prophet' o 'sarima'"),
):
    """
    Genera un pronóstico de la demanda de viajes para una zona específica.
    """
    import traceback

    print(f"[PREDICT] Iniciando: zone_id={zone_id}, hours={hours}, model={model}")

    if df_ts.empty:
        print("[PREDICT] ❌ df_ts está vacío")
        raise HTTPException(status_code=500, detail="Time series data not loaded")

    # Extraer data de la zona
    df_zone = df_ts[df_ts["PULocationID"] == zone_id][["hora", "total_viajes"]].copy()
    print(f"[PREDICT] Filas para zona {zone_id}: {len(df_zone)}")
    if df_zone.empty:
        raise HTTPException(
            status_code=404, detail=f"Zone ID {zone_id} not found in the Top 10 dataset"
        )

    df_zone.set_index("hora", inplace=True)
    df_zone.sort_index(inplace=True)
    print(f"[PREDICT] Rango de datos: {df_zone.index.min()} → {df_zone.index.max()}")

    predictions = []
    future_dates = []

    if model.lower() == "prophet":
        try:
            print("[PREDICT] Prophet: preparando datos...")
            df_p = df_zone.reset_index().rename(
                columns={"hora": "ds", "total_viajes": "y"}
            )
            print(f"[PREDICT] Prophet: df_p shape={df_p.shape}, dtypes={df_p.dtypes.to_dict()}")

            m = Prophet(
                yearly_seasonality=False,
                weekly_seasonality=True,
                daily_seasonality=True,
            )
            print("[PREDICT] Prophet: entrenando (fit)...")
            m.fit(df_p)
            print("[PREDICT] Prophet: fit completado ✅")

            print(f"[PREDICT] Prophet: generando future dataframe ({hours} horas)...")
            future = m.make_future_dataframe(periods=hours, freq="h")
            print(f"[PREDICT] Prophet: future shape={future.shape}")

            print("[PREDICT] Prophet: prediciendo...")
            forecast = m.predict(future)
            print(f"[PREDICT] Prophet: forecast shape={forecast.shape}")

            future_forecast = forecast.tail(hours)
            future_dates = future_forecast["ds"].astype(str).tolist()
            predictions = (
                future_forecast["yhat"].clip(lower=0).round(0).tolist()
            )
            print(f"[PREDICT] Prophet: ✅ {len(predictions)} predicciones generadas")
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"[PREDICT] Prophet ❌ ERROR: {str(e)}")
            print(f"[PREDICT] Prophet ❌ TRACEBACK:\n{error_details}")
            raise HTTPException(
                status_code=500, detail=f"Error Prophet: {str(e)}\n{error_details}"
            )

    elif model.lower() == "sarima":
        try:
            print("[PREDICT] SARIMA: configurando modelo...")
            m_sarima = SARIMAX(
                df_zone["total_viajes"], order=(1, 0, 1), seasonal_order=(1, 0, 1, 24)
            )
            print("[PREDICT] SARIMA: entrenando (fit)...")
            res = m_sarima.fit(disp=False)
            print("[PREDICT] SARIMA: fit completado ✅")

            print(f"[PREDICT] SARIMA: pronosticando {hours} pasos...")
            pred = res.forecast(steps=hours)
            future_dates = pred.index.astype(str).tolist()
            predictions = pred.clip(lower=0).round(0).tolist()
            print(f"[PREDICT] SARIMA: ✅ {len(predictions)} predicciones generadas")
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"[PREDICT] SARIMA ❌ ERROR: {str(e)}")
            print(f"[PREDICT] SARIMA ❌ TRACEBACK:\n{error_details}")
            raise HTTPException(
                status_code=500, detail=f"Error SARIMA: {str(e)}\n{error_details}"
            )
    else:
        raise HTTPException(
            status_code=400, detail="Modelo no soportado. Usa 'prophet' o 'sarima'"
        )

    return {
        "zone_id": zone_id,
        "model_used": model.lower(),
        "horizon_hours": hours,
        "future_dates": future_dates,
        "predictions": predictions,
    }
