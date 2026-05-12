# Análisis Geoespacial de Movilidad Urbana en New York - Caso 04

## Descripción del Proyecto
Este proyecto tiene como objetivo identificar los "Hot spots" (puntos calientes) de mayor demanda de transporte en la ciudad de New York para los taxis amarillos (Yellow Taxi). Adicionalmente, analizamos cómo varía esta actividad a lo largo del día y de la semana. El análisis se apoya en visualizaciones cartográficas y modelos predictivos de Machine Learning y Estadística Clásica (Prophet, SARIMA, Holt-Winters).

## Estructura del Proyecto Actualizada

```text
proyecto_caso04/
│
├── datos/
│   ├── raw/                    Parquet y GeoJSON originales (taxi_zones)
│   ├── interim/                Datos intermedios y de diagnóstico
│   └── procesados/             Datos finales limpios y agregados (Top 10, Geo)
│
├── notebooks/
│   ├── 01_diagnostico.ipynb    Diagnóstico inicial de los datos
│   ├── 02_limpieza.ipynb       Limpieza de tarifas negativas, nulos y outliers
│   ├── 03_analisis_rutas.ipynb Identificación del Top 10 de rutas y congestión
│   ├── 04_geometria_zonas.ipynb Mapeo de polígonos a centroides (Lat/Lon)
│   ├── 05_modelado_series_tiempo.ipynb Entrenamiento y evaluación de Prophet
│   ├── 06_modelo_sarima.ipynb          Entrenamiento y evaluación de SARIMA
│   ├── 07_modelo_holt_winters.ipynb    Entrenamiento y evaluación de Holt-Winters
│   └── 08_comparacion_modelos.ipynb    Gráfico y competencia final de Prophet vs SARIMA vs Holt-Winters
│
├── resultados/
│   ├── graficos/               
│   │   ├── exploracion/        Gráficos exploratorios iniciales
│   │   └── comparacion_modelos.png, rutas_tiempos_viaje.png
│   └── reportes/               Reporte de Calidad de Datos, Análisis de Congestión
│
├── app/                        (PRÓXIMAMENTE)
│   ├── api/                    API FastAPI para servir los datos
│   └── dashboard.py            Dashboard interactivo en Streamlit y Folium
│
├── docs/
│   ├── README.md               Esta guía
│   ├── CONTEXTO_NEGOCIO.md     Métricas operativas y hallazgos analíticos consolidados
│   ├── MODELADO_SERIES_TIEMPO.md Documentación teórica y fallas de Prophet
│   ├── MODELO_SARIMA.md          Documentación teórica y fallas de SARIMA
│   ├── MODELO_HOLT_WINTERS.md    Documentación teórica y fallas de Holt-Winters
│   ├── DICCIONARIO.md          Definición de variables
│   └── ARCHIVED_prompt_diagnostico.md Registro del prompt inicial de diagnóstico
│
└── requirements.txt            Librerías del proyecto
```

## Estado Actual y Próximos Pasos
**Fases Completadas (1 al 5):**
1. **Diagnóstico:** Detección de nulos, tarifas negativas y valores atípicos.
2. **Limpieza:** Imputación y filtrado riguroso del mes de Enero 2025.
3. **Análisis Exploratorio:** Identificación de las rutas de mayor congestión y demora.
4. **Ingeniería Geoespacial:** Extracción de coordenadas estandarizadas con Geopandas.
5. **Modelado Predictivo:** Competencia oficial entre Prophet, SARIMA y Holt-Winters para proyectar la demanda horaria.

**Siguiente Fase:**
- **Fase 6 (Despliegue):** Construcción del backend (`FastAPI`) para exponer la tabla de demanda, y desarrollo del frontend (`Streamlit`) para mostrar el mapa de calor de densidad en tiempo real.
