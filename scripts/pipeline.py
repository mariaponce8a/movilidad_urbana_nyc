import os
import pandas as pd
from utilidades import (
    cargar_configuracion,
    cargar_datos,
    limpiar_datos,
    enriquecer_datos,
    unir_zonas
)

def ejecutar_pipeline():
    print("Iniciando pipeline de datos...")
    
    # 1. Cargar configuración
    # Cambiamos al directorio del proyecto si es necesario, o asumimos que corremos desde él.
    ruta_base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ruta_config = os.path.join(ruta_base, "config", "parametros.yaml")
    
    config = cargar_configuracion(ruta_config)
    print("Configuración cargada.")
    
    # 2. Cargar datos
    ruta_viajes = os.path.join(ruta_base, config["archivos"]["viajes"])
    ruta_zonas = os.path.join(ruta_base, config["archivos"]["zonas"])
    
    print(f"Cargando datos desde:\n- {ruta_viajes}\n- {ruta_zonas}")
    df_viajes, df_zonas = cargar_datos(ruta_viajes, ruta_zonas)
    print(f"Datos originales: {len(df_viajes)} viajes.")
    
    # 3. Limpiar datos
    df_viajes = limpiar_datos(df_viajes, config)
    print(f"Datos post-limpieza: {len(df_viajes)} viajes.")
    
    # 4. Enriquecer con variables temporales
    df_viajes = enriquecer_datos(df_viajes)
    
    # 5. Unir con información de zonas
    df_viajes = unir_zonas(df_viajes, df_zonas)
    
    # 6. Guardar datos procesados
    ruta_salida = os.path.join(ruta_base, config["archivos"]["procesados"])
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    
    print(f"Guardando datos procesados en {ruta_salida}...")
    df_viajes.to_parquet(ruta_salida, index=False)
    
    # 7. Generar un CSV agregado de demanda por zona y hora (opcional para dashboard ligero)
    print("Generando agregado de demanda por zona...")
    if "PULocationID" in df_viajes.columns:
        demanda_zona = df_viajes.groupby(["PULocationID", "PU_Borough", "PU_Zone", "hora_dia"]).size().reset_index(name="total_viajes")
        ruta_demanda = os.path.join(ruta_base, config["archivos"]["agregados_zonas"])
        os.makedirs(os.path.dirname(ruta_demanda), exist_ok=True)
        demanda_zona.to_csv(ruta_demanda, index=False)
    
    print("¡Pipeline completado con éxito!")

if __name__ == "__main__":
    ejecutar_pipeline()
