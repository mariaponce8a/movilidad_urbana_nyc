import pandas as pd
import geopandas as gpd
import yaml
from pathlib import Path

def cargar_configuracion(ruta_config="config/parametros.yaml"):
    """Carga los parámetros de configuración desde un archivo YAML."""
    with open(ruta_config, "r") as file:
        config = yaml.safe_load(file)
    return config

def cargar_datos(ruta_parquet, ruta_zonas):
    """Carga los viajes en parquet y las zonas en CSV."""
    df_viajes = pd.read_parquet(ruta_parquet)
    df_zonas = pd.read_csv(ruta_zonas)
    return df_viajes, df_zonas

def limpiar_datos(df, config):
    """Limpia los datos basándose en la configuración definida."""
    filtros = config.get("filtros", {})
    
    # Asegurar tipo datetime
    if "tpep_pickup_datetime" in df.columns and "tpep_dropoff_datetime" in df.columns:
        df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
        df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
        
        # Filtro de fechas
        if "fecha_inicio" in filtros and "fecha_fin" in filtros:
            mask_fechas = (df["tpep_pickup_datetime"] >= filtros["fecha_inicio"]) & \
                          (df["tpep_pickup_datetime"] <= filtros["fecha_fin"])
            df = df.loc[mask_fechas].copy()
            
        # Calcular duración
        df["duracion_min"] = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60.0
        
        # Filtros de viaje
        if "viaje_minimo_minutos" in filtros:
            df = df[df["duracion_min"] >= filtros["viaje_minimo_minutos"]]
        if "viaje_maximo_minutos" in filtros:
            df = df[df["duracion_min"] <= filtros["viaje_maximo_minutos"]]
            
    if "tarifa_minima" in filtros and "fare_amount" in df.columns:
        df = df[df["fare_amount"] >= filtros["tarifa_minima"]]
        
    return df

def enriquecer_datos(df):
    """Añade variables temporales útiles para el análisis."""
    if "tpep_pickup_datetime" in df.columns:
        df["hora_dia"] = df["tpep_pickup_datetime"].dt.hour
        df["dia_semana"] = df["tpep_pickup_datetime"].dt.dayofweek # 0=Lunes, 6=Domingo
        df["es_fin_de_semana"] = df["dia_semana"].isin([5, 6]).astype(int)
    return df

def unir_zonas(df_viajes, df_zonas):
    """Une la información de la zona de inicio y fin a los viajes."""
    # Renombrar columnas de df_zonas para evitar sufijos _x _y
    zonas_pu = df_zonas.copy().add_prefix("PU_")
    zonas_do = df_zonas.copy().add_prefix("DO_")
    
    # Merge para PickUp (PU)
    if "PULocationID" in df_viajes.columns:
        df_viajes = df_viajes.merge(
            zonas_pu, 
            left_on="PULocationID", 
            right_on="PU_LocationID", 
            how="left"
        )
    
    # Merge para DropOff (DO)
    if "DOLocationID" in df_viajes.columns:
        df_viajes = df_viajes.merge(
            zonas_do, 
            left_on="DOLocationID", 
            right_on="DO_LocationID", 
            how="left"
        )
        
    return df_viajes
