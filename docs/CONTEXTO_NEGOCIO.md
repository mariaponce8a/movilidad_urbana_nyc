# Contexto de Negocio - Yellow Tripdata 2025-01

Este documento contiene la información de negocio clave para interpretar el dataset de viajes de taxis amarillos (Yellow Taxi) en New York para enero de 2025.

## 1. Qué es el negocio
El Yellow Taxi de Nueva York es un servicio de transporte urbano icónico. Los taxis amarillos tienen licencia de la NYC Taxi & Limousine Commission (TLC) para prestar servicio en toda la ciudad. Este dataset contiene 3.47 millones de viajes realizados en enero de 2025.

**Stakeholders principales:**
- **Taxistas:** generan ingresos
- **Empresas/Floristas:** poseen los taxis
- **TLC:** regula y supervisa
- **Pasajeros:** demandan servicio
- **Ciudad:** planificación urbana

## 2. Volumen y Escala
| Métrica | Valor |
| --- | --- |
| Total viajes enero | 3,475,226 |
| Viajes por día (promedio) | 108,601 |
| Ingresos totales enero | $89,005,026.80 |
| Período cubierto | 31 días (Dec 31 - Feb 1) |

**Interpretación:**
- Nueva York tiene una demanda de taxi MASIVA.
- Cada día se transportan ~109k pasajeros.
- Genera casi $89 millones mensuales en ingresos totales.

## 3. Economía del Viaje Típico
**Tarifa base:**
- Tarifa promedio: $17.08 USD
- Tarifa mediana: $12.11 USD (el 50% de viajes cuesta menos de esto)
- Rango: -$900 a $863,372 (datos sucios con anomalías)

**Propinas:**
- Promedio: $2.96 USD
- 67.8% de viajes incluyen propina (métrica clave de satisfacción)
- Rango: -$86 a $400

**Monto total por viaje:**
- Promedio: $25.61 USD (tarifa + extra + impuestos + propina)
- La mayoría de viajes cuesta entre $12-30 USD

**Cargos adicionales:**
- Impuesto MTA (metrobús): $0.48 USD promedio
- Cargo de congestión: $2.23 USD promedio (new policy para descongestionar Manhattan)
- Cargo aeropuerto: $0.12 USD promedio (cuando hay viajes a/desde aeropuertos)

*Modelo de ingresos por viaje: Total = Tarifa + Extra + Impuesto MTA + Cargo congestión + Cargo aeropuerto + Propina*

## 4. Distancia y Duración
| Métrica | Valor |
| --- | --- |
| Distancia promedio | 5.86 millas |
| Duración promedio | 15 minutos |
| Rango distancia | 0 - 276,423 millas (anomalía obvia) |

**Interpretación:**
- Viajes típicos: 5-6 millas (desde Midtown a otro barrio)
- Duración típica: 10-20 minutos
- PROBLEMA: hay muchos viajes con distancia=0 (se suben y bajan en mismo lugar)
- PROBLEMA: hay viajes con distancias imposibles (276k millas = al espacio)

## 5. Estructura de Pasajeros
| Métrica | Valor |
| --- | --- |
| Promedio pasajeros | 1.3 por viaje |
| Moda (más común) | 1 pasajero |
| Máximo registrado | 9 pasajeros |

**Interpretación:**
- Mayoría viajes = 1 pasajero (persona viajando sola)
- Algunos viajes compartidos (2-3 pasajeros)
- Muy pocos viajes de grupos (4+ pasajeros)
- 540k viajes sin datos de pasajeros (15.5% son datos sucios)

## 6. Métodos de Pago
- **Tarjeta de crédito (Tipo 1):** 70.3% ← DOMINANTE
- **Efectivo (Tipo 2):** 11.2%
- **Sin datos (Tipo 0):** 15.5% ← PROBLEMA
- **Otros (Tipo 3, 4):** 2.2%

**Implicaciones de negocio:**
- 70% de ingresos son rastreables (tarjeta crédito = auditoría, impuestos, disputas)
- 11% en efectivo = no rastreable (riesgo de evasión fiscal)
- 15.5% sin datos = viajes problemáticos (transacciones incompletas)

## 7. Distribución Geográfica
**Top 5 zonas de recogida:**
1. Zona 161 (Manhattan center): 169,977 viajes (4.9%)
2. Zona 237 (Queens): 163,703 viajes (4.7%)
3. Zona 236 (Queens): 155,647 viajes (4.5%)
4. Zona 132 (Manhattan): 146,137 viajes (4.2%)
5. Zona 230 (Bronx): 125,829 viajes (3.6%)

**Interpretación:**
- Manhattan es EL centro (zonas 161, 132 son Midtown/Downtown)
- Queens es segundo (residencial, pero genera mucha demanda)
- Concentración geográfica: top 5 zonas = ~22% de todos los viajes
- 261 zonas diferentes de recogida = demanda distribuida pero con hotspots

## 8. Competencia de Vendedores
- **Vendedor 2:** 78.3% ← Mayoritario
- **Vendedor 1:** 21.7%
- **Vendedor 6:** 0.01% ← Marginal
- **Vendedor 7:** 0.03% ← Marginal

**Implicaciones:**
- Vendor 2 domina el mercado (probablemente Uber/Lyft o consorcio grande)
- Vendor 1 es el competidor de escala (21.7% es significativo)
- Hay poco espacio para vendors pequeños

## 9. Problemas de Calidad de Datos
Datos sucios detectados:

| Problema | Cantidad | % |
| --- | --- | --- |
| Sin datos de pasajeros | 540,149 | 15.5% |
| Sin RateCode | 540,149 | 15.5% |
| Tarifas negativas | Variable | ? |
| Distancias imposibles (>276k) | Variable | ? |
| Viajes duración negativa | Variable | ? |
| Viajes sin propina pero pagan tarjeta | Variable | ? |

**Causa probable:** Los 540k viajes sin datos son del Vendor 6 y 7 (sistemas defectuosos)


## 10. Hallazgos Analíticos Posteriores a la Exploración

*(Este contenido fue fusionado desde el reporte original de insights para consolidar la visión de negocio en un solo lugar)*

## 1. Volumen y Escala Operativa
El volumen de viajes supera los **3.47 millones** en un solo mes, demostrando la alta densidad de la operación de taxis amarillos en NYC. Con un monto total promedio por viaje de ~$25.61 USD, los **ingresos totales** (que incluyen tarifa base, extras, propinas e impuestos) alcanzan aproximadamente los **$89 millones de dólares**. De este total, la facturación correspondiente *exclusivamente a las tarifas base* (promedio de ~$17.08 USD por viaje) representa alrededor de **$59 millones de dólares**. Esta escala masiva refleja un mercado de gran resiliencia económica.

## 2. Demanda y Concentración
La principal zona de recolección de pasajeros se concentra en Manhattan y los principales aeropuertos de la ciudad (JFK y LaGuardia). Existe una demanda cíclica con horas punta en la tarde-noche (entre las 17:00 y las 19:00 horas), coincidiendo con la finalización del horario laboral y la vida nocturna. Esto sugiere la necesidad de asegurar disponibilidad de la flota en estos nodos neurálgicos.

## 3. Calidad de Servicio y Satisfacción
Los datos crudos muestran que el **4.15% (más de 144 mil viajes)** registran tarifas negativas, lo que probablemente corresponda a viajes cancelados, disputas o problemas en el sistema de pago. Para el negocio, este volumen de fallas o cancelaciones representa un margen de fricción que debe ser minimizado, ya que impacta directamente en la experiencia del usuario o del conductor.

## 4. Tipología del Viaje Promedio
- El usuario típico realiza un trayecto corto-medio, con una distancia promedio de **5.85 millas** y pagando tarifas que se concentran entre los **$8.60 y $19.50 USD**.
- Existen viajes (2.6%) registrados con una distancia de 0 millas, lo cual sugiere recogidas fallidas o problemas en la conexión del GPS del vehículo.

## 5. Recomendaciones Estratégicas Iniciales
1. **Auditoría de Sistemas (VendorID):** Dado que el 15.5% de los datos perdió de manera simultánea la información sobre la cantidad de pasajeros y cargos adicionales, es imperativo investigar con el proveedor de los dispositivos para prevenir la pérdida de estos datos, esenciales para proyecciones de recaudación y dimensionamiento de demanda.
2. **Control de Viajes Nulos/Cancelados:** Investigar los picos geográficos y horarios donde se registran las tarifas negativas y viajes de distancia cero, a fin de identificar si existen problemas operativos sistemáticos en ciertos lugares (ej. aeropuertos) o si son casos de fraude.
3. **Optimización de Flota en Horas Pico:** Utilizar el mapa de calor de recogidas para recomendar a los conductores los puntos ciegos de la ciudad con alta demanda potencial durante los picos de las 17:00 a 19:00 horas.
