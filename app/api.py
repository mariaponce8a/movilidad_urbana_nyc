from fastapi import FastAPI, Query, HTTPException
import pandas as pd
import numpy as np
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import os

warnings.filterwarnings('ignore')

app = FastAPI(
    title="NYC Taxi Mobility API",
    description="API REST para el análisis geoespacial y predictivo de la demanda de taxis en Nueva York (Caso 04).",
    version="1.0.0"
)

# --- CARGA DE DATOS EN MEMORIA ---
# Se cargan al iniciar la API para que las peticiones sean ultrarrápidas
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "datos", "procesados")

try:
    df_geo = pd.read_parquet(os.path.join(DATA_PATH, "demanda_geo_agregada.parquet"))
    df_ts = pd.read_parquet(os.path.join(DATA_PATH, "demanda_top10_series_tiempo.parquet"))
except FileNotFoundError:
    print("Error: No se encontraron los archivos Parquet en datos/procesados/")
    df_geo = pd.DataFrame()
    df_ts = pd.DataFrame()

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "NYC Taxi Mobility API is running"}

@app.get("/trips/heatmap", tags=["Geoespacial"])
def get_heatmap_data(hour: int = Query(..., ge=0, le=23, description="Hora del día (0-23)")):
    """
    Retorna la lista de coordenadas y pesos para el mapa de calor de Folium.
    La rúbrica exige que se entreguen los puntos de recogida de una hora específica.
    """
    if df_geo.empty:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Filtrar por hora
    df_hour = df_geo[df_geo['hora_dia'] == hour]
    
    # Agrupar por coordenada binificada para el heatmap
    heatmap_data = df_hour.groupby(['lat_bin', 'lon_bin'])['viajes'].sum().reset_index()
    
    # Formato requerido por Folium: [lat, lon, weight]
    points = heatmap_data[['lat_bin', 'lon_bin', 'viajes']].values.tolist()
    
    return {
        "hour": hour,
        "total_points": len(points),
        "data": points
    }

@app.get("/trips/demand_curve", tags=["Temporal"])
def get_demand_curve():
    """
    Serie de demanda por hora del día.
    Agrupa todos los viajes por cada una de las 24 horas.
    """
    if df_geo.empty:
        raise HTTPException(status_code=500, detail="Data not loaded")
        
    curve = df_geo.groupby('hora_dia')['viajes'].sum().reset_index()
    
    return {
        "x": curve['hora_dia'].tolist(),
        "y": curve['viajes'].tolist()
    }

@app.get("/trips/heatmap_day_hour", tags=["Temporal"])
def get_heatmap_day_hour():
    """
    Retorna los datos estructurados para crear el Heatmap de Seaborn (Día vs Hora).
    """
    if df_geo.empty:
        raise HTTPException(status_code=500, detail="Data not loaded")
        
    pivot = df_geo.pivot_table(index='dia_semana', columns='hora_dia', values='viajes', aggfunc='sum', fill_value=0)
    
    # Ordenar los días lógicamente
    dias_ordenados = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot = pivot.reindex(dias_ordenados)
    
    return {
        "dias": pivot.index.tolist(),
        "horas": pivot.columns.tolist(),
        "valores": pivot.values.tolist()
    }

@app.get("/trips/predict", tags=["Predicción (ML)"])
def predict_demand(
    zone_id: int = Query(237, description="ID de la zona de taxi (Ej: 237 para Upper East Side)"),
    hours: int = Query(24, ge=12, le=168, description="Horizonte de predicción en horas (12h a 7 días)"),
    model: str = Query("prophet", description="Modelo a usar: 'prophet' o 'sarima'")
):
    """
    Genera un pronóstico de la demanda de viajes para una zona específica.
    """
    if df_ts.empty:
        raise HTTPException(status_code=500, detail="Time series data not loaded")
        
    # Extraer data de la zona
    df_zone = df_ts[df_ts['PULocationID'] == zone_id][['hora', 'total_viajes']].copy()
    if df_zone.empty:
        raise HTTPException(status_code=404, detail=f"Zone ID {zone_id} not found in the Top 10 dataset")
        
    df_zone.set_index('hora', inplace=True)
    df_zone.sort_index(inplace=True)
    
    predictions = []
    future_dates = []
    
    if model.lower() == 'prophet':
        try:
            # Preparar data para Prophet
            df_p = df_zone.reset_index().rename(columns={'hora': 'ds', 'total_viajes': 'y'})
            m = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=True)
            m.fit(df_p)
            
            future = m.make_future_dataframe(periods=hours, freq='h')
            forecast = m.predict(future)
            
            # Extraer solo el futuro
            future_forecast = forecast.tail(hours)
            future_dates = future_forecast['ds'].astype(str).tolist()
            predictions = future_forecast['yhat'].clip(lower=0).round(0).tolist() # No viajes negativos
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            raise HTTPException(status_code=500, detail=f"Error Prophet: {str(e)}\n{error_details}")

        
    elif model.lower() == 'sarima':
        # SARIMA toma más tiempo, pero lo entrenamos on the fly
        try:
            m_sarima = SARIMAX(df_zone['total_viajes'], order=(1,0,1), seasonal_order=(1,0,1,24))
            res = m_sarima.fit(disp=False)
            
            pred = res.forecast(steps=hours)
            future_dates = pred.index.astype(str).tolist()
            predictions = pred.clip(lower=0).round(0).tolist()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error entrenando SARIMA: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Modelo no soportado. Usa 'prophet' o 'sarima'")
        
    return {
        "zone_id": zone_id,
        "model_used": model.lower(),
        "horizon_hours": hours,
        "future_dates": future_dates,
        "predictions": predictions
    }
