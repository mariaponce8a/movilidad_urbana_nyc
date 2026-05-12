# Documentación: Modelado de Series de Tiempo (Predicción de Demanda)

Esta sección documenta la metodología, preparación de datos y algoritmos utilizados para predecir la demanda de viajes de los taxis amarillos en Nueva York, empleando modelos de Series de Tiempo.

## 1. Justificación del Enfoque
Para entender los "Hot spots" (puntos de alta concentración de demanda) no basta con un análisis estático. La movilidad urbana es altamente dinámica y presenta patrones (estacionalidad) muy marcados:
- **Estacionalidad Diaria:** Horas pico en las mañanas (viajes al trabajo) y tardes (regresos).
- **Estacionalidad Semanal:** Diferencia de comportamiento entre días laborables y fines de semana.

Por recomendación académica y para capturar estos patrones complejos, se optó por abordar el problema mediante **Series de Tiempo**, específicamente utilizando el modelo **Prophet**.

## 2. Preparación de los Datos Temporales
Para que un modelo predictivo funcione correctamente, los datos de viajes individuales tuvieron que ser transformados en una secuencia cronológica continua.

**Script responsable:** `scripts/preparar_series_tiempo.py`

### Proceso de Transformación:
1.  **Filtro del Top 10 Zonas:** Dado el volumen masivo de datos, el modelado inicial se concentra en las 10 zonas (`PULocationID`) con mayor número histórico de viajes.
2.  **Agregación Horaria (Resampling):** Se agruparon todos los viajes redondeando la fecha exacta de recogida (`tpep_pickup_datetime`) a la hora más cercana (`freq='h'`). La variable objetivo a predecir (`y`) es el conteo total de viajes en esa hora.
3.  **Relleno de Huecos (Imputación temporal):** Los modelos de series de tiempo fallan si hay "saltos" en el tiempo. Se construyó un índice continuo (MultiIndex) desde el primer hasta el último registro de enero 2025. Las horas en las que una zona no registró ningún viaje fueron rellenadas con un valor de `0`.

**Resultado:** Se generó el archivo estructurado `datos/procesados/demanda_top10_series_tiempo.parquet`.

## 3. Metodología de Modelado: Prophet

Se eligió **Prophet** (desarrollado por el equipo de Core Data Science de Meta/Facebook) por las siguientes razones clave en nuestro contexto de movilidad urbana:
- **Robustez ante valores atípicos:** Maneja bien los días festivos o eventos climáticos extremos que alteran temporalmente el tráfico de NYC.
- **Descomposición de Componentes:** Permite separar visualmente la "tendencia general" de los patrones diarios y semanales, lo cual genera *insights* de negocio muy interpretables.

### Fases en el Notebook (`05_modelado_series_tiempo.ipynb`):
1.  **Adaptación del Formato:** Renombrar la columna de tiempo a `ds` y la de viajes a `y`, como lo exige la librería.
2.  **Entrenamiento (Fit):** Se configuró el modelo para detectar explícitamente estacionalidades diarias y semanales (`daily_seasonality=True`, `weekly_seasonality=True`).
3.  **Pronóstico (Forecast):** Se instruyó al modelo para crear un *dataframe* futuro proyectando las próximas 168 horas (7 días).
4.  **Descomposición:** Generación de gráficos (`plot_components`) para analizar a qué horas específicas del día repunta la demanda en cada una de las zonas del Top 10.
5.  **Automatización:** Un bucle itera sobre la lista del Top 10 para entrenar de forma independiente un modelo optimizado para cada zona.

## 4. Validación del Modelo (Train / Test Split)

Para asegurar el rigor científico del proyecto y evitar el *Data Leakage* (fuga de datos, donde el modelo memoriza las respuestas correctas), se implementó una fase estricta de validación.

1.  **División Temporal (Split):** De las 744 observaciones (horas) correspondientes a enero de 2025, se tomó el ~80% inicial (primeros 24 días) como conjunto de **Entrenamiento (Train)** y el ~20% final (últimos 7 días) como conjunto de **Prueba (Test)**.
2.  **Aislamiento del Modelo:** Para esta prueba, se instanció un modelo de Prophet completamente nuevo (en blanco) y se entrenó **exclusivamente** con el set de Entrenamiento. Esto garantiza que el modelo evalúe la última semana "a ciegas", sin conocer la realidad de antemano.
3.  **Métricas de Error:** Al comparar las predicciones del modelo aislado con la realidad oculta en el set de Prueba, calculamos las métricas estadísticas **MAE** (Error Absoluto Medio) y **RMSE** (Raíz del Error Cuadrático Medio). Estas métricas cuantifican el margen de error real del pronóstico en términos de "viajes por hora".

## 5. Estructura de Salida y Presentación
Los hallazgos de este modelo alimentan directamente la Fase 4 del proyecto. Los componentes de tendencia diaria y semanal pueden ser utilizados en los "Dashboards" para recomendar a la flota de taxis a qué zonas dirigirse dependiendo de la hora del día.

---

## 6. Competencia de Modelos (Requisito Académico)
Para cumplir con el rigor analítico del proyecto y evaluar robustez, se implementó una evaluación cruzada contra dos de los algoritmos más fuertes de la estadística clásica: **SARIMA** (Seasonal ARIMA) y **Holt-Winters** (Suavización Exponencial Triple).

### Resultados del Backtesting (Predicción de los últimos 7 días de Enero 2025 en el Upper East Side):

| Modelo | Error Absoluto Medio (MAE) | Raíz del Error Cuadrático Medio (RMSE) |
| --- | --- | --- |
| **Prophet** | **56.49** | **67.98** |
| **SARIMA (1,0,1)x(1,0,1,24)** | 57.82 | 81.51 |
| **Holt-Winters** | 86.23 | 104.90 |

**Conclusión Científica:**
**Prophet se declara como el modelo ganador definitivo.** Logró predecir el volumen de viajes por hora con el margen de error más bajo (desviándose por alrededor de 56 viajes por hora en una zona que maneja picos altísimos). 

El modelo SARIMA demostró ser extremadamente competitivo y logró capturar muy de cerca la estacionalidad diaria (MAE de 57.82), pero fue penalizado fuertemente en el RMSE, lo que indica que SARIMA comete errores mucho más grandes cuando hay "picos" atípicos de tráfico, mientras que Prophet maneja mejor esos valores extremos (outliers). Holt-Winters resultó insuficiente para la extrema volatilidad de la ciudad de Nueva York.

## 7. Análisis Gráfico del Modelo Ganador (Prophet)

![Predicción Prophet](/Users/nathalyparedes/movilidad_urbana_nyc/movilidad_urbana_nyc/resultados/graficos/prediccion_prophet.png)

**Comentario Analítico:**  
A diferencia de la rigidez de los modelos estadísticos clásicos, Prophet (línea azul) brilla en su capacidad de adaptarse a la volatilidad extrema. Fíjate cómo logra predecir exitosamente los "picos" altísimos de las horas punta de la tarde (las cimas de las montañas negras), acercándose muchísimo más a la realidad. Esta flexibilidad matemática para asimilar comportamientos no lineales es lo que le dio a Prophet la victoria, convirtiéndolo en el algoritmo oficialmente recomendado para alimentar el sistema de despacho de la flota.
