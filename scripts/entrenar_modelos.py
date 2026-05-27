import os
import pandas as pd
import numpy as np
import pickle
import json
import warnings
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")

def entrenar_y_evaluar_modelos():
    print("=== INICIANDO ENTRENAMIENTO Y EVALUACION DE MODELOS (80/20 SPLIT) ===")
    
    # Rutas absolutas resolviendo a la raíz del proyecto
    ruta_base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ruta_datos = os.path.join(ruta_base, "datos", "procesados", "demanda_top10_series_tiempo.parquet")
    ruta_modelos = os.path.join(ruta_base, "modelos")
    os.makedirs(ruta_modelos, exist_ok=True)
    
    if not os.path.exists(ruta_datos):
        print(f"[ERROR] No se encontro el archivo en {ruta_datos}")
        return
        
    print(f"Cargando series de tiempo desde: {ruta_datos}")
    df_ts = pd.read_parquet(ruta_datos)
    
    # Identificar zonas únicas
    zonas = df_ts["PULocationID"].unique().tolist()
    print(f"Zonas a procesar ({len(zonas)}): {zonas}")
    
    metricas_globales = {}
    
    for zone_id in zonas:
        print(f"\n--- Procesando Zona ID: {zone_id} ---")
        df_zone = df_ts[df_ts["PULocationID"] == zone_id][["hora", "total_viajes"]].copy()
        df_zone.sort_values("hora", inplace=True)
        df_zone.reset_index(drop=True, inplace=True)
        
        n_total = len(df_zone)
        n_train = int(n_total * 0.8)
        n_test = n_total - n_train
        
        print(f"Total registros: {n_total} | Train (80%): {n_train} | Test (20%): {n_test}")
        
        df_train = df_zone.iloc[:n_train].copy()
        df_test = df_zone.iloc[n_train:].copy()
        
        # --- 1. PROPHET ---
        print("  [Prophet] Evaluando con 80% train / 20% test...")
        df_p_train = df_train.rename(columns={"hora": "ds", "total_viajes": "y"})
        m_prophet_eval = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=True,
        )
        m_prophet_eval.fit(df_p_train)
        
        # Generar future dataframe para predecir sobre el test set
        future_eval = m_prophet_eval.make_future_dataframe(periods=n_test, freq="h")
        forecast_eval = m_prophet_eval.predict(future_eval)
        pred_p = forecast_eval.tail(n_test)["yhat"].clip(lower=0).round(0).values
        true_p = df_test["total_viajes"].values
        
        # Calcular métricas Prophet
        mae_p = float(np.mean(np.abs(true_p - pred_p)))
        rmse_p = float(np.sqrt(np.mean((true_p - pred_p) ** 2)))
        print(f"  [Prophet] Metricas de Validacion -> MAE: {mae_p:.2f} | RMSE: {rmse_p:.2f}")
        
        # --- 2. SARIMA ---
        print("  [SARIMA] Evaluando con 80% train / 20% test...")
        train_series = df_train.set_index("hora")["total_viajes"]
        train_series.index = pd.DatetimeIndex(train_series.index)
        train_series = train_series.asfreq("h")
        
        m_sarima_eval = SARIMAX(
            train_series, order=(1, 0, 1), seasonal_order=(1, 0, 1, 24)
        )
        res_sarima_eval = m_sarima_eval.fit(disp=False)
        pred_s = res_sarima_eval.forecast(steps=n_test).clip(lower=0).round(0).values
        
        mae_s = float(np.mean(np.abs(true_p - pred_s)))
        rmse_s = float(np.sqrt(np.mean((true_p - pred_s) ** 2)))
        print(f"  [SARIMA] Metricas de Validacion -> MAE: {mae_s:.2f} | RMSE: {rmse_s:.2f}")
        
        # Registrar métricas
        metricas_globales[str(zone_id)] = {
            "prophet": {"mae": round(mae_p, 4), "rmse": round(rmse_p, 4)},
            "sarima": {"mae": round(mae_s, 4), "rmse": round(rmse_s, 4)}
        }
        
        # --- 3. ENTRENAMIENTO FINAL (100% de los datos) ---
        print("  [Prophet] Entrenando modelo final (100% de datos)...")
        df_p_full = df_zone.rename(columns={"hora": "ds", "total_viajes": "y"})
        m_prophet_final = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=True,
        )
        m_prophet_final.fit(df_p_full)
        
        print("  [SARIMA] Entrenando modelo final (100% de datos)...")
        full_series = df_zone.set_index("hora")["total_viajes"]
        full_series.index = pd.DatetimeIndex(full_series.index)
        full_series = full_series.asfreq("h")
        m_sarima_final = SARIMAX(
            full_series, order=(1, 0, 1), seasonal_order=(1, 0, 1, 24)
        )
        res_sarima_final = m_sarima_final.fit(disp=False)
        
        # Guardar modelos
        file_prophet = os.path.join(ruta_modelos, f"prophet_{zone_id}.pkl")
        file_sarima = os.path.join(ruta_modelos, f"sarima_{zone_id}.pkl")
        
        with open(file_prophet, "wb") as f:
            pickle.dump(m_prophet_final, f)
        
        # remove_data() elimina los datos de entrenamiento del objeto serializado
        # Reduce el tamaño de ~76 MB a ~1 MB. El modelo sigue pudiendo hacer forecast().
        res_sarima_final.remove_data()
        res_sarima_final.save(file_sarima)
        
        print(f"  [OK] Modelos para Zona {zone_id} guardados exitosamente.")
        
    # Guardar métricas de validación en JSON
    ruta_metricas = os.path.join(ruta_modelos, "metricas_evaluacion.json")
    with open(ruta_metricas, "w") as f:
        json.dump(metricas_globales, f, indent=4)
        
    print("\n=== PROCESO COMPLETADO CON EXITO ===")
    print(f"Metricas guardadas en: {ruta_metricas}")

if __name__ == "__main__":
    entrenar_y_evaluar_modelos()
