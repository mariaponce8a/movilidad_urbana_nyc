# Reporte de Calidad de Datos - Yellow Tripdata (Enero 2025)

## 1. Resumen Ejecutivo
El presente reporte detalla los resultados del diagnóstico de calidad de datos realizado sobre el dataset `yellow_tripdata_2025-01.parquet`.
El dataset cuenta con **3,475,226 registros** y **20 variables**, abarcando viajes registrados en enero de 2025. Se han identificado problemas críticos de datos nulos en ciertas variables y anomalías lógicas en los valores de tarifas y distancias que requieren acciones de limpieza previas al análisis profundo.

## 2. Estructura y Cobertura
- **Total de filas:** 3,475,226
- **Total de columnas:** 20
- **Tamaño en memoria:** 638.70 MB
- **Cobertura Temporal:** 
  - Fecha mínima: 2024-12-31 20:47:55
  - Fecha máxima: 2025-02-01 00:00:44
  *(Nota: Se observan registros en los límites del mes que podrían descartarse si el enfoque es estrictamente enero 2025).*

## 3. Análisis de Valores Nulos y Duplicados
- **Duplicados exactos:** 0 registros (No se encontraron filas idénticas).
- **Valores Nulos:** Se identificó un patrón de bloques de nulos del **15.54% (540,149 registros)** simultáneamente en las siguientes variables:
  - `passenger_count`
  - `RatecodeID`
  - `store_and_fwd_flag`
  - `congestion_surcharge`
  - `Airport_fee`

## 4. Integridad de los Datos (Outliers y Anomalías)

### A. Tarifas (`fare_amount`)
- **Promedio:** $17.08 USD
- **Tarifas negativas:** 144,118 registros (4.15% del total). *Estos representan posibles reembolsos, cancelaciones o errores de sistema.*
- **Tarifas excesivas (>$500):** 55 registros.

### B. Distancias (`trip_distance`)
- **Promedio:** 5.85 millas
- **Distancias en cero:** 90,893 registros (2.62%). *Requieren evaluación para determinar si la tarifa cobrada también fue $0.*
- **Distancias imposibles (>100 millas):** 162 registros.

## 5. Tabla de Acciones Correctivas Recomendadas

| Problema Identificado | Cantidad Afectada | % | Severidad | Acción Recomendada | Prioridad |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Nulos simultáneos (pasajeros, cargos, etc.) | 540,149 | 15.54% | Alta | Imputar `passenger_count` a la moda (1) y evaluar qué hacer con los cargos, o eliminar si la tarifa total es inconsistente. | P0 |
| Tarifas negativas | 144,118 | 4.15% | Alta | Eliminar registros (o separarlos para análisis de devoluciones) para que no afecten los cálculos de ingresos netos. | P0 |
| Viajes con distancia cero | 90,893 | 2.62% | Media | Eliminar si la duración también es 0, o imputar según tarifa y duración promedio si es factible. | P1 |
| Tarifas excesivamente altas (>$500) | 55 | <0.01% | Media | Evaluar relación con distancia, considerar limpieza como outliers. | P2 |
| Distancias irreales (>100 millas) | 162 | <0.01% | Media | Recortar (trim) a un percentil lógico de máxima distancia en NYC. | P2 |
