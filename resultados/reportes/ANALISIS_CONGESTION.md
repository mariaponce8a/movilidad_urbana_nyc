# Análisis de Tiempos de Viaje y Congestión (Top 10 Rutas)

Este reporte resume los hallazgos tras procesar los tiempos de viaje de las 10 rutas más frecuentes de taxis amarillos en Nueva York durante enero de 2025. Se utilizaron los nombres reales de las zonas geográficas para mayor legibilidad.

## 1. El Top 10 de Rutas Más Frecuentes
De los más de 3.25 millones de viajes en enero, las 10 rutas más transitadas son trayectos cortos o medianos, casi exclusivamente concentrados dentro de Manhattan. Esta muestra agrupó un total de **136,477 viajes**.

Las rutas dominantes son:
1. **Upper East Side South -> Upper East Side North** (24,368 viajes)
2. **Upper East Side North -> Upper East Side South** (21,324 viajes)
3. **Upper East Side North -> Upper East Side North** (17,106 viajes)
4. **Upper East Side South -> Upper East Side South** (16,232 viajes)
5. **Midtown Center -> Upper East Side South** (11,152 viajes)
6. **Upper East Side South -> Midtown Center** (9,893 viajes)
7. **Midtown Center -> Upper East Side North** (9,575 viajes)
8. **Upper West Side South -> Upper West Side North** (9,324 viajes)
9. **Lincoln Square East -> Upper West Side South** (8,935 viajes)
10. **Upper West Side South -> Lincoln Square East** (8,568 viajes)

*Insight clave:* La altísima frecuencia de viajes intra-zona (origen y destino en la misma zona) resalta que los taxis amarillos siguen siendo el medio preferido de transporte para distancias muy cortas o "micro-movilidad" para residentes y trabajadores de alto nivel adquisitivo en el Upper East Side y Midtown.

## 2. Fluctuaciones y Tiempos de Demora
Al graficar la duración promedio de estos trayectos según la hora del día, el comportamiento de congestión vehicular se vuelve evidente:

* **Valle de Madrugada (03:00 - 05:00 hrs):** En este periodo, los tiempos de viaje alcanzan su punto mínimo. Un trayecto de Midtown Center al Upper East Side puede tomar poco más de la mitad del tiempo en comparación con el pico de tráfico.
* **Hora Pico Matutina (08:00 - 09:00 hrs):** Se observa el primer pico fuerte del día, coincidiendo con el horario de ingreso a las oficinas (Midtown) y escuelas.
* **Gran Pico de la Tarde/Noche (16:00 - 18:00 hrs):** Este es el **momento de máxima congestión en toda la ciudad**. Durante estas horas, el tiempo promedio de todos los trayectos experimenta un incremento de hasta un 50%-70% en el tiempo de viaje debido a la combinación del fin del horario laboral, compras, cena e inicio de la vida nocturna.

## 3. Conclusiones para la Gestión de la Flota
- **Optimización de Tiempos:** El pasajero promedio en el Upper East Side gasta gran parte de su tiempo atrapado en el tráfico entre las 16:00 y las 18:00. Las políticas de tarifa de congestión y de precios dinámicos están plenamente justificadas bajo estos datos.
- **Micro-viajes:** El mercado de "distancias caminables" en Manhattan sigue prefiriendo pagar por confort.
- **Gráfica Adjunta:** Se puede visualizar el detalle exacto en `resultados/graficos/rutas_tiempos_viaje.png`.
