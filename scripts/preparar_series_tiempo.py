import pandas as pd
import os

def preparar_datos_series_tiempo():
    print("Cargando datos limpios...")
    ruta_datos = '../datos/procesados/yellow_tripdata_2025-01_clean.parquet'
    
    if not os.path.exists(ruta_datos):
        print(f"Error: No se encontró el archivo en {ruta_datos}")
        print("Asegúrate de ejecutar este script desde la carpeta 'scripts/'.")
        return

    # Leer datos
    df = pd.read_parquet(ruta_datos, columns=['tpep_pickup_datetime', 'PULocationID'])
    
    print("Identificando las 10 zonas más populares...")
    top_10_zones = df['PULocationID'].value_counts().nlargest(10).index.tolist()
    print(f"Top 10 Zonas (PULocationID): {top_10_zones}")
    
    # Filtrar solo por el top 10
    df = df[df['PULocationID'].isin(top_10_zones)].copy()
    
    # Redondear la hora
    df['hora'] = df['tpep_pickup_datetime'].dt.floor('h')
    
    print("Agregando demanda por zona y hora...")
    demanda = df.groupby(['hora', 'PULocationID']).size().reset_index(name='total_viajes')
    
    print("Rellenando horas faltantes (huecos en el tiempo)...")
    # Crear un rango completo de horas para enero 2025
    min_hora = demanda['hora'].min()
    max_hora = demanda['hora'].max()
    rango_completo = pd.date_range(start=min_hora, end=max_hora, freq='h')
    
    # Crear un MultiIndex con todas las horas y las top 10 zonas
    multi_idx = pd.MultiIndex.from_product([rango_completo, top_10_zones], names=['hora', 'PULocationID'])
    
    # Reindexar para rellenar vacíos
    demanda = demanda.set_index(['hora', 'PULocationID'])
    demanda_completa = demanda.reindex(multi_idx, fill_value=0).reset_index()
    
    # Ordenar por zona y luego por hora
    demanda_completa = demanda_completa.sort_values(['PULocationID', 'hora']).reset_index(drop=True)
    
    ruta_salida = '../datos/procesados/demanda_top10_series_tiempo.parquet'
    demanda_completa.to_parquet(ruta_salida, index=False)
    print(f"¡Listo! Dataset de series de tiempo guardado en: {ruta_salida}")
    print(f"Total de registros generados: {len(demanda_completa)}")

if __name__ == "__main__":
    preparar_datos_series_tiempo()
