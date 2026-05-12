# Modelado con Holt-Winters (Suavización Exponencial Triple)

El modelo de **Holt-Winters** es una técnica estadística clásica basada en medias móviles ponderadas exponencialmente.

## 1. Fundamentos Matemáticos en nuestro Caso (NYC Taxi)
El modelo descompone la serie de tiempo en tres componentes, actualizando sus pesos a medida que avanza el tiempo:
1. **Nivel (Alpha):** El valor base o promedio actual del tráfico.
2. **Tendencia (Beta):** Si el tráfico está subiendo o bajando de manera general.
3. **Estacionalidad (Gamma):** El patrón repetitivo. En nuestro caso, lo forzamos a aprender ciclos de 24 horas.

Se llama "exponencial" porque le da muchísima más importancia (peso matemático) a lo que pasó ayer, y hace que la importancia de los datos de semanas anteriores caiga exponencialmente hacia cero.

## 2. Ventajas del Modelo Holt-Winters
1. **Simplicidad y Velocidad:** Es computacionalmente baratísimo. El entrenamiento toma fracciones de segundo porque no resuelve sistemas matriciales complejos como SARIMA.
2. **Adaptabilidad a Corto Plazo:** Dado que le da más peso a los datos recientes, si hay un cambio brusco en el tráfico, el modelo se adapta más rápido a la "nueva normalidad" que un modelo ARIMA tradicional.
3. **Fácil Interpretación:** Sus parámetros (alpha, beta, gamma) son intuitivos de explicar a *stakeholders* no técnicos.

## 3. Desventajas y Fallas Identificadas
1. **Rendimiento Deficiente (Falla Principal):** En nuestro *backtesting*, fue el peor modelo de los tres. Logró un Error Absoluto Medio (MAE) de 86.23 viajes y un RMSE de 104.90. **Falló por un margen casi 50% mayor que Prophet**.
2. **Demasiada Simplicidad:** Al igual que SARIMA, solo soporta un tipo de estacionalidad a la vez (diaria). No entiende que los fines de semana se comportan distinto a los días hábiles.
3. **Mala Proyección a Largo Plazo:** Sus predicciones tienden a volverse "planas" si se le pide predecir muchos días en el futuro, ya que la incertidumbre de la suavización exponencial crece rápidamente.

## Conclusión para el Negocio
Holt-Winters es una buena herramienta empírica para *forecasting* de ventas minoristas a nivel mensual, pero carece de la sofisticación necesaria para modelar la altísima volatilidad minuto a minuto del transporte en una metrópoli de la escala de Nueva York.

---

## 4. Análisis Gráfico y Evidencia

### Predicción vs Realidad
![Predicción Holt-Winters](/Users/nathalyparedes/movilidad_urbana_nyc/movilidad_urbana_nyc/resultados/graficos/prediccion_hw.png)

**Comentario Analítico:**  
La debilidad de Holt-Winters queda en evidencia de manera casi dramática en este gráfico. Observa cómo la línea verde pierde fuerza a medida que pasan los días en el futuro. A diferencia de Prophet y SARIMA, Holt-Winters sufre severamente para mantener la agresividad de las olas. Al depender tanto del pasado inmediato, sus pronósticos terminan "aplanándose". En lugar de alertar a los taxistas de que habrá 500 viajes a las 6:00 PM, el modelo predice valores mediocres que llevarían a una sub-asignación catastrófica de vehículos en las zonas de mayor rentabilidad.
