================================================================================
PROMPT PARA AGENTE - ETAPA 1: EXPLORACIÓN Y DIAGNÓSTICO DE DATOS
CASO 04: MOVILIDAD URBANA NYC - YELLOW TRIPDATA 2025-01
================================================================================

OBJETIVO GENERAL
================================================================================
Realizar un análisis exploratorio completo del dataset Yellow Tripdata 2025-01
para identificar la calidad de datos, anomalías, patrones iniciales e insights
de negocio que preparen el terreno para limpieza y análisis posterior.

ENTREGABLES ESPERADOS
================================================================================
1. REPORTE DE CALIDAD DE DATOS (HTML/Markdown)
   - Diagnóstico completo de cada variable
   - Problemas identificados con cuantificación
   - Recomendaciones de acción

2. VISUALIZACIONES EXPLORATORIAS (PNG)
   - Distribuciones de variables clave
   - Mapas de valores nulos
   - Gráficos de anomalías

3. TABLA DE ACCIONES CORRECTIVAS (CSV/JSON)
   - Qué problema
   - Cuántos registros afecta
   - Recomendación de acción
   - Prioridad

4. INSIGHTS INICIALES DE NEGOCIO (Markdown)
   - Hallazgos sobre demanda, patrones, rentabilidad


================================================================================
PASO 1: CARGA Y EXPLORACIÓN BÁSICA
================================================================================

INSTRUCCIÓN:
Carga el archivo yellow_tripdata_2025-01.parquet y realiza un diagnóstico
inicial de su estructura y contenido.

ESPECÍFICAMENTE:

A) Estructura del Dataset
   - Total de filas y columnas
   - Nombres de todas las columnas
   - Tipos de datos de cada columna
   - Tamaño en memoria

B) Cobertura Temporal
   - Fecha/hora mínima y máxima de pickup
   - Fecha/hora mínima y máxima de dropoff
   - ¿Todos los días de enero están representados?
   - ¿Hay brechas temporales?
   - Distribución de viajes por día de la semana
   - Distribución de viajes por hora del día

C) Variables Clave
   - Listar las 10 variables más importantes para negocio
   - Rango de valores (mín, máx, media, mediana, std)
   - Tipo de dato adecuado


================================================================================
PASO 2: ANÁLISIS DE CALIDAD - VALORES NULOS Y DUPLICADOS
================================================================================

INSTRUCCIÓN:
Analiza exhaustivamente los datos faltantes y duplicados.

ESPECÍFICAMENTE:

A) Valores Nulos
   Para CADA columna:
   - Cantidad de nulos
   - Porcentaje de nulos
   - Tipo de nulo (NaN, None, campos vacíos)
   - ¿Es aceptable el porcentaje?
   
   VISUALIZACIÓN:
   - Gráfico de barras: % nulos por columna
   - Mapa de calor: patrón de nulos (¿correlacionados?)

B) Duplicados
   - ¿Hay filas completamente duplicadas?
   - ¿Hay duplicados en combinaciones de: (VendorID, pickup_datetime, DOLocationID)?
   - Cantidad y porcentaje de duplicados
   - ¿Son viajes legítimos repetidos o errores de registro?

C) Identificación de Patrones en Nulos
   - ¿Todos los nulos en una columna coinciden con un vendor específico?
   - ¿Todos los nulos están en un período de tiempo?
   - ¿Hay patrón que explique los nulos?


================================================================================
PASO 3: ANÁLISIS DE INTEGRIDAD - RANGOS Y COHERENCIA
================================================================================

INSTRUCCIÓN:
Verifica que los valores estén dentro de rangos razonables y sean coherentes
entre sí.

ESPECÍFICAMENTE:

A) Tarifa (fare_amount)
   - Rango: mín, máx, media, mediana
   - ¿Hay tarifas negativas? (¿cuántas?, ¿qué %)
   - ¿Hay tarifas extremadamente altas? (>$500)
   - ¿Hay tarifas = 0?
   - Distribución: histograma, boxplot
   - DECISIÓN: ¿Qué rango es aceptable?

B) Distancia (trip_distance)
   - Rango: mín, máx, media, mediana
   - ¿Hay distancias negativas?
   - ¿Hay distancias = 0? (¿cuántas?)
   - ¿Hay distancias imposibles? (>100 millas)
   - Relación distancia vs tarifa (¿son proporcionales?)
   - DECISIÓN: ¿Qué rango es aceptable?

C) Duración del Viaje (tpep_dropoff_datetime - tpep_pickup_datetime)
   - ¿Hay viajes con duración negativa?
   - ¿Hay viajes con duración 0?
   - ¿Hay viajes > 3 horas? (¿son excepciones o errores?)
   - Relación duración vs distancia (¿coherente con velocidad urbana?)
   - DECISIÓN: ¿Qué rango es aceptable?

D) Propina (tip_amount)
   - ¿Hay propinas negativas?
   - Cuando method_pago=CASH, ¿hay propinas registradas? (raro)
   - % viajes con propina por método de pago
   - Relación propina vs tarifa
   - DECISIÓN: ¿Propinas negativas son errores o reembolsos?

E) Pasajeros (passenger_count)
   - Rango: mín, máx, moda, media
   - ¿Hay viajes con 0 pasajeros?
   - ¿Hay viajes con >6 pasajeros?
   - Distribución por cantidad
   - DECISIÓN: ¿Qué rango es válido?

F) Cargos Adicionales (mta_tax, congestion_surcharge, airport_fee)
   - ¿Cuántos viajes tienen cada cargo?
   - ¿Son coherentes con el tipo de viaje?
   - ¿Hay cargos negativos?
   - ¿Hay cargos duplicados?

G) Coherencia entre Variables
   - total_amount = fare + extra + mta_tax + tip + tolls + surcharge + airport_fee
     ¿La suma es correcta para cada viaje?
   - Cuando distancia=0, ¿tarifa también debería ser ~0?
   - Cuando duración es muy corta, ¿tarifa debería ser mínima?
   - Cuando passenger_count=0, ¿es error o viaje prepagado?


================================================================================
PASO 4: ANÁLISIS DE DISTRIBUCIONES
================================================================================

INSTRUCCIÓN:
Visualiza la distribución de variables numéricas clave para identificar
patrones, outliers y comportamiento normal.

ESPECÍFICAMENTE:

A) Tarifa (fare_amount)
   GRÁFICOS:
   - Histograma (con bins=50)
   - Boxplot
   - KDE plot
   - Scatter: tarifa vs distancia (para ver correlación)
   
   ANÁLISIS:
   - ¿Es distribución normal o sesgada?
   - ¿Hay múltiples picos (bimodal)?
   - Percentiles: 1%, 5%, 25%, 50%, 75%, 95%, 99%

B) Propina (tip_amount)
   GRÁFICOS:
   - Histograma
   - Boxplot
   - % viajes con propina
   - Propina vs Tarifa (scatter)
   
   ANÁLISIS:
   - ¿Cuál es la propina típica?
   - ¿Qué % de viajes NO tienen propina?
   - ¿Propina está correlacionada con tarifa?

C) Distancia (trip_distance)
   GRÁFICOS:
   - Histograma (escala normal y log)
   - Boxplot
   - Scatter: distancia vs duración
   
   ANÁLISIS:
   - ¿Dónde se concentran los viajes? (0-5, 5-10, 10+ millas)
   - ¿Hay cluster de viajes cortos?

D) Pasajeros (passenger_count)
   GRÁFICOS:
   - Gráfico de barras (conteo por cantidad)
   - Pie chart de distribución
   
   ANÁLISIS:
   - % viajes con 1 pasajero vs múltiples

E) Temporal
   GRÁFICOS:
   - Viajes por hora del día (línea)
   - Viajes por día de semana (barras)
   - Heatmap: día de semana × hora
   
   ANÁLISIS:
   - ¿Cuándo hay picos de demanda?
   - ¿Diferencias hábiles vs fines de semana?
   - ¿Hora valle vs punta?


================================================================================
PASO 5: VALIDACIÓN GEOGRÁFICA
================================================================================

INSTRUCCIÓN:
Valida que las coordenadas y zonas sean coherentes con Nueva York.

ESPECÍFICAMENTE:

A) Límites Geográficos NYC
   BOUNDING BOX correcto:
   - Latitud: [40.4774, 40.9176]
   - Longitud: [-74.2591, -73.7004]
   
   ANÁLISIS:
   - ¿Hay coordenadas FUERA de estos límites?
   - ¿Cuántos viajes están fuera?
   - ¿A dónde van las coordenadas malas? (otra ciudad, error obvio)

B) Validación con Lookup Table
   Cargar taxi_zone_lookup.csv y verificar:
   - ¿PULocationID existen en el lookup?
   - ¿DOLocationID existen en el lookup?
   - ¿Hay IDs no mapeados?
   - ¿Hay zonas del lookup no usadas en los datos?

C) Análisis Espacial
   GRÁFICOS:
   - Scatter plot: pickup (longitud vs latitud)
   - Mapa de calor: densidad de pickups
   - Top 10 zonas de pickup (barras)
   - Top 10 zonas de dropoff (barras)
   
   ANÁLISIS:
   - ¿Dónde está concentrada la demanda?
   - ¿Hay zonas que parecen datos incorrectos?


================================================================================
PASO 6: VALIDACIÓN DE VENDORS Y MÉTODOS DE PAGO
================================================================================

INSTRUCCIÓN:
Analiza la distribución y consistencia de vendors y métodos de pago.

ESPECÍFICAMENTE:

A) Vendors (VendorID)
   - Distribución: % de viajes por vendor
   - ¿Hay vendors inesperados?
   - ¿Características diferentes por vendor?
     (tarifa promedio, % con propina, distancia promedio)

B) Métodos de Pago (payment_type)
   - Distribución: % de viajes por tipo
   - Tipos esperados: 1=Credit card, 2=Cash, 3=No charge, 4=Dispute
   - ¿Hay tipos inesperados o inválidos?
   - ¿Hay inconsistencias?
     (ej: payment_type=2 (cash) pero tip_amount>0)

C) RateCode (RatecodeID)
   - Distribución de rate codes
   - Relación: rate code vs tarifa (¿son coherentes?)
   - Relación: rate code vs distancia


================================================================================
PASO 7: IDENTIFICACIÓN DE OUTLIERS Y ANOMALÍAS
================================================================================

INSTRUCCIÓN:
Identifica y cuantifica valores extremos que pueden ser errores.

ESPECÍFICAMENTE:

A) Método: IQR (Interquartile Range)
   Para cada variable numérica:
   - Calcular Q1, Q3, IQR
   - Lower bound = Q1 - 1.5*IQR
   - Upper bound = Q3 + 1.5*IQR
   - Contar valores fuera de estos bounds
   
   REPORTAR:
   - Variable: [columna]
     Outliers: [N] ([%])
     Ejemplos: [valores extremos]

B) Anomalías Lógicas (casos especiales)
   - Viajes con distancia=0 pero tarifa>0
   - Viajes con duración=0 pero distancia>0
   - Viajes con passenger_count=0
   - Viajes con duración>3 horas
   - Viajes con tarifa negativa
   - Viajes con propina > tarifa
   - Método pago = cash + propina registrada (raro)

C) Patrón de Anomalías
   - ¿Las anomalías vienen de un vendor específico?
   - ¿Están concentradas en un período?
   - ¿Hay patrón que las explique?


================================================================================
PASO 8: ANÁLISIS DE COMPLETITUD POR SEGMENTO
================================================================================

INSTRUCCIÓN:
Analiza cómo varía la calidad de datos en diferentes segmentos.

ESPECÍFICAMENTE:

A) Por Vendor
   Para cada VendorID:
   - % de nulos en cada columna
   - Diferencias de tarifa promedio
   - Diferencias de distancia promedio
   - Diferencias de % con propina
   - Conclusión: ¿Un vendor tiene mejor calidad?

B) Por Método de Pago
   Para cada payment_type:
   - Tarifa promedio
   - % con propina
   - % de nulos en cada columna
   - Conclusión: ¿Hay patrones sospechosos?

C) Por Período Temporal
   - Primeros 7 días vs últimos 7 días (¿hay diferencia en calidad?)
   - Horas punta (8-9am, 5-7pm) vs horas valle
   - Hábiles vs fines de semana
   - Conclusión: ¿La calidad varía con el tiempo?

D) Por Zona Geográfica
   - Top 5 zonas: ¿qué % de nulos?
   - Bottom 5 zonas: ¿qué % de nulos?
   - Conclusión: ¿Hay zonas problemáticas?


================================================================================
PASO 9: TABLA DE ACCIONES CORRECTIVAS
================================================================================

INSTRUCCIÓN:
Crea una tabla detallada de problemas encontrados y cómo resolverlos.

FORMATO:

ID | Problema | Cantidad | % | Severidad | Acción Recomendada | Prioridad
---|----------|----------|---|-----------|-------------------|----------
1  | passenger_count nulo | 540,149 | 15.5% | ALTA | Eliminar fila o imputar moda (1) | P0
2  | fare_amount negativo | XXX | X% | ALTA | Eliminar | P0
3  | trip_distance = 0 | XXX | X% | MEDIA | Investigar patrón, eliminar si error | P1
4  | Coordenadas fuera NYC | XXX | X% | ALTA | Aplicar bounding box | P0
5  | ... | ... | ... | ... | ... | ...

SEVERIDAD:
- CRÍTICA: Invalida el viaje completamente
- ALTA: Afecta análisis, debe ser limpiado
- MEDIA: Puede afectar ciertos análisis, considerar
- BAJA: Anotado, pero puede dejarse

PRIORIDAD:
- P0: AHORA (bloquea análisis)
- P1: Muy importante (primer paso de limpieza)
- P2: Importante (segundo paso de limpieza)
- P3: Nice to have (refinamiento)


================================================================================
PASO 10: INSIGHTS DE NEGOCIO INICIALES
================================================================================

INSTRUCCIÓN:
Extrae hallazgos sobre el negocio de Yellow Taxi basándote en los datos
explorados.

RESPONDE:

A) Volumen y Escala
   - ¿Cuántos viajes reales tenemos (después de estimar qué % son errores)?
   - ¿Ingresos totales estimados en enero?
   - ¿Promedio de ingresos por viaje?

B) Demanda
   - ¿Cuándo es la demanda máxima? (hora, día de semana)
   - ¿Cuándo es la demanda mínima?
   - ¿Cómo varía entre hábiles y fines de semana?
   - ¿Cuál es la zona de mayor demanda?

C) Rentabilidad
   - ¿Cuál es el viaje típico (distancia, tarifa, duración)?
   - ¿Qué % de viajes incluyen propina? (=satisfacción)
   - ¿Diferencias de tarifas por zona?
   - ¿Diferencias de propinas por vendor?

D) Calidad de Servicio
   - ¿Qué % de datos están completos y válidos?
   - ¿Un vendor tiene mejor calidad que otro?
   - ¿Qué % de viajes tienen anomalías?
   - ¿Qué problemas críticos hay que resolver antes de análisis profundo?

E) Implicaciones para Planificación Urbana
   - ¿Las zonas geográficas tienen cobertura uniforme?
   - ¿Hay zonas sub-atendidas?
   - ¿El cargo de congestión aparece en qué % de viajes?
   - ¿Cómo impacta en la demanda?

F) Recomendaciones Iniciales
   - ¿Qué necesita limpieza urgente?
   - ¿Qué pasos siguen en el análisis?
   - ¿Hay riesgos o sesgos en los datos?


================================================================================
FORMATO DE SALIDA
================================================================================

1. REPORTE HTML/MARKDOWN
   Estructura:
   ├─ Resumen ejecutivo (1 página)
   ├─ 1. Exploración básica
   ├─ 2. Calidad de datos (valores nulos, duplicados)
   ├─ 3. Integridad (rangos, coherencia)
   ├─ 4. Distribuciones (histogramas, boxplots)
   ├─ 5. Validación geográfica
   ├─ 6. Vendors y métodos de pago
   ├─ 7. Outliers y anomalías
   ├─ 8. Análisis por segmento
   ├─ 9. Tabla de acciones correctivas
   ├─ 10. Insights de negocio
   └─ Conclusiones y próximos pasos

2. VISUALIZACIONES (PNG)
   - 01_distribucion_tarifas.png
   - 02_distribucion_propinas.png
   - 03_distribucion_distancia.png
   - 04_distribucion_pasajeros.png
   - 05_nulos_por_columna.png
   - 06_temporal_viajes_hora.png
   - 07_temporal_viajes_dia.png
   - 08_heatmap_dia_hora.png
   - 09_mapa_pickup_density.png
   - 10_top_zonas.png
   - 11_boxplot_tarifas.png
   - 12_scatter_distancia_vs_tarifa.png

3. TABLA DE ACCIONES (CSV)
   - acciones_correctivas.csv

4. DOCUMENTO DE INSIGHTS (Markdown)
   - insights_negocio.md

GUARDAR TODO EN:
1_exploracion/
├─ notebooks/
│  └─ 01_diagnostico.ipynb (código ejecutable)
├─ reportes/
│  └─ diagnostico_datos.html
├─ graficos/
│  └─ *.png
└─ datos/
   └─ acciones_correctivas.csv


================================================================================
CRITERIOS DE ÉXITO
================================================================================

✅ Completitud
   - Todas las columnas analizadas
   - Todos los problemas identificados y cuantificados
   - Todos los tipos de anomalías cubertos

✅ Profundidad
   - No solo números, sino contexto e implicaciones
   - Análisis por segmento (vendor, zona, tiempo)
   - Hipótesis sobre causas de problemas

✅ Accionabilidad
   - Tabla de acciones clara y priorizada
   - Decisiones recomendadas para cada problema
   - Siguiente paso definido (limpieza en Etapa 2)

✅ Visualización
   - Gráficos claros y informativos
   - Cada gráfico responde una pregunta
   - Fácil de interpretar

✅ Comunicación
   - Reporte ejecutivo claro para no-técnicos
   - Detalles técnicos en secciones posteriores
   - Recomendaciones concretas


================================================================================
NOTAS PARA EL AGENTE
================================================================================

1. TRABAJAR CON DATOS GRANDES
   - El dataset es 3.47M de filas = ~57MB en memoria
   - Usar chunking si necesario
   - Reportar tiempo de ejecución

2. CONTEXTO DE NEGOCIO
   - NYC Taxi es un negocio real regulado
   - Datos pueden tener problemas reales (sistemas defectuosos)
   - No es SÓLO análisis técnico, es diagnóstico de operación

3. ÉNFASIS EN DECISIONES
   - Para cada problema, qué HACER
   - No solo identificar, sino resolver
   - Siguiente etapa es limpieza = necesita roadmap claro

4. SOSPECHAS INICIALES (validar)
   - ~15.5% de datos sin passenger_count (probablemente vendor específico)
   - Puede haber datos de enero + primeros días de febrero
   - Algunos cargos (airport_fee, congestion_surcharge) son nuevos
   - Algunos viajes con distancia=0 pueden ser preparados/cancelados

5. VALIDACIONES ESPECÍFICAS
   - Verificar: sum(tarifas y cargos) = total por cada viaje
   - Verificar: duración > 0 para viajes con distancia > 0
   - Verificar: coordenadas dentro de bounding box
   - Verificar: IDs de zona existen en lookup table

================================================================================
¡ADELANTE!
Realiza el análisis completo y genera los entregables.
================================================================================