# Documentación de Procesamiento y Preparación de Datos

Este documento detalla las metodologías aplicadas durante las fases de limpieza de datos tabulares y la preparación geoespacial del proyecto **Movilidad Urbana Nueva York** (Dataset de Taxis Amarillos, Enero 2025), garantizando que el set de datos cumple con los más altos estándares de calidad y con los requerimientos técnicos de la rúbrica del proyecto.

---

## 1. Fase de Limpieza de Datos Tabulares (Data Cleaning)

El objetivo de esta fase fue purgar anomalías, corregir la ausencia de datos y crear variables temporales/físicas clave para el análisis de la movilidad.

### 1.1 Filtrado Temporal Estricto
* **Acción:** Se eliminaron todos los registros cuyas fechas de recogida o dejada (`tpep_pickup_datetime`, `tpep_dropoff_datetime`) cayeran fuera de enero de 2025. Los errores en los relojes de los taxis generan fechas anómalas (ej. año 2002 o 2026).
* **Impacto:** Asegura que el análisis temporal sea 100% fiel al periodo de estudio.

### 1.2 Imputación de Valores Nulos (15.5% del Dataset)
En lugar de eliminar más de medio millón de viajes que carecían de información secundaria, se aplicaron reglas de negocio para retener los datos de tarifas y trayectos:
* `passenger_count` (Cantidad de pasajeros): Se imputó con la moda estadística (**1 pasajero**) asumiendo que al menos una persona viajó en el vehículo.
* `RatecodeID` (Tipo de tarifa): Se imputó con **1** (Tarifa estándar).
* `congestion_surcharge` y `Airport_fee`: Se imputaron con **0** asumiendo que la ausencia de registro indicaba que no se aplicó el recargo.

### 1.3 Eliminación de Anomalías (Outliers) y Lógica de Negocio
* **Tarifas Negativas:** Se filtraron todos los viajes con `fare_amount <= 0`, los cuales usualmente representan disputas o reembolsos que distorsionan el cálculo de ingresos.
* **Distancias Imposibles:** Se eliminaron los viajes con distancias de **0 millas** (errores de GPS) y aquellos que excedían las **100 millas** (viajes irreales para un taxi amarillo operando en NYC).

### 1.4 Ingeniería de Características (Feature Engineering)
Se construyeron nuevas métricas esenciales para el análisis y los modelos posteriores:
* `duracion_minutos`: Calculada restando el tiempo de bajada y de subida (filtrando errores de duración <=0 o mayores a 3 horas).
* `velocidad_mph`: Calculada dividiendo distancia sobre horas. Se filtraron velocidades ilógicas (> 80 mph sostenidas en NYC).
* `hora_dia`, `dia_semana`, `es_fin_de_semana`: Variables extraídas del timestamp para habilitar el análisis de patrones temporales.

---

## 2. Fase de Preparación Geoespacial (Reto Técnico)

Para poder graficar mapas de calor (`HeatMaps` en Folium) y cumplir con la rúbrica del profesor, se resolvió la ausencia de columnas de Latitud y Longitud en el dataset moderno mediante un cruce geométrico.

### 2.1 Mapeo de Coordenadas (Centroides)
* **Acción:** Se utilizó la librería `geopandas` para leer el archivo oficial `taxi_zones.geojson`. 
* **Técnica:** Las geometrías de las zonas fueron proyectadas al Sistema Plano Estatal (EPSG:2263) para calcular el centro exacto (centroide) de manera precisa. Luego, estos puntos se volvieron a proyectar al estándar WGS84 (EPSG:4326) para extraer `pickup_latitude` y `pickup_longitude`.
* **Cruce:** Se unieron estas coordenadas con nuestro dataset tabular a través de la llave `PULocationID`.

### 2.2 Aplicación del "Bounding Box" de Nueva York
Para limpiar errores residuales de GPS y garantizar que el análisis se limite a la ciudad, se aplicó el filtro geoespacial estricto dictado en los requerimientos:
* **Latitud permitida:** `40.4774` a `40.9176`
* **Longitud permitida:** `-74.2591` a `-73.7004`
Cualquier viaje cuyo origen cayera fuera de este rectángulo fue descartado.

### 2.3 Binificación Espacial
* **Acción:** Se crearon las columnas `lat_bin` y `lon_bin` redondeando las coordenadas a **2 decimales**.
* **Propósito:** Esta técnica agrupa puntos que están geográficamente muy cerca entre sí, lo cual es vital para el rendimiento y la agregación del Mapa de Calor.

### 2.4 Agregación y Optimización
* **Acción:** Se agrupó el inmenso dataset de 3.25 millones de viajes contando las ocurrencias basadas en la Hora del Día, Día de la Semana, y Coordenadas Binificadas.
* **Resultado:** Se generó el archivo maestro `demanda_geo_agregada.parquet`. Este dataset extremadamente ligero (~27,600 filas) contiene toda la densidad y el volumen necesario para alimentar las APIs y los Dashboards en tiempo real sin consumir memoria excesiva.
