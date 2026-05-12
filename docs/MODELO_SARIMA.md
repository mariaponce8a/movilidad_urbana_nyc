# Modelado con SARIMA (Seasonal ARIMA)

El modelo **SARIMA** (*Seasonal Autoregressive Integrated Moving Average*) es una de las metodologías clásicas más potentes para el análisis de series temporales que presentan patrones repetitivos (estacionalidad).

## 1. Fundamentos Matemáticos en nuestro Caso (NYC Taxi)
SARIMA se compone de varios parámetros `(p, d, q) x (P, D, Q, s)`:
* **Autoregresión (p, P):** El modelo asume que el tráfico de la hora actual depende directamente de las horas anteriores.
* **Diferenciación (d, D):** Resta valores para estabilizar la media y eliminar tendencias a largo plazo.
* **Medias Móviles (q, Q):** Corrige el modelo basándose en los errores de predicción pasados.
* **Estacionalidad (s):** Para nuestro caso, establecimos `s = 24`, obligando al modelo a buscar patrones que se repiten cada 24 horas exactas (el ciclo diario de la ciudad).

## 2. Ventajas del Modelo SARIMA
1. **Rigor Matemático Estricto:** A diferencia de Prophet (que usa curvas flexibles), SARIMA usa relaciones lineales probabilísticas. Es el estándar de oro en econometría académica.
2. **Excelente Captura de Estacionalidad Regular:** Tal como se demostró en el *backtesting*, SARIMA fue capaz de dibujar casi a la perfección la "forma" de las olas diarias del tráfico en Nueva York (logró un Error Absoluto Medio de 57.82, compitiendo de cerca con Prophet).
3. **Caja Blanca:** Sus ecuaciones permiten entender exactamente qué peso tiene el pasado reciente sobre el futuro.

## 3. Desventajas y Fallas Identificadas
1. **Sensibilidad a Extremos (Falla Principal):** Su debilidad crítica quedó expuesta en el `RMSE` (Raíz del Error Cuadrático Medio), el cual penaliza errores grandes. Cuando la ciudad de Nueva York experimentó "picos" atípicos de tráfico por encima de 550 viajes en horas punta, **SARIMA falló miserablemente**. La línea de predicción roja se distorsionó severamente en esos puntos.
2. **Inflexibilidad Multi-Estacional:** SARIMA solo nos permitió configurar un patrón estacional (`s=24` horas). No es capaz de asimilar fácilmente que existe *otra* estacionalidad superpuesta de 7 días (la diferencia entre martes y domingo). 
3. **Lentitud Computacional:** Requiere mucho más tiempo de procesamiento para optimizar sus parámetros matemáticos en comparación con los algoritmos modernos.

## Conclusión para el Negocio
SARIMA es excelente para predecir el comportamiento **promedio** de un día normal, pero es demasiado rígido para reaccionar al caótico y extremo entorno de la ciudad de Nueva York.

---

## 4. Análisis Gráfico y Evidencia

### Predicción vs Realidad (Picos y Valles)
![Predicción SARIMA](/Users/nathalyparedes/movilidad_urbana_nyc/movilidad_urbana_nyc/resultados/graficos/prediccion_sarima.png)

**Comentario Analítico:**  
Observa la línea roja punteada frente a la línea negra real. SARIMA hace un trabajo fenomenal prediciendo los "valles" (las horas de la madrugada donde los viajes caen casi a cero). Sin embargo, su limitación teórica queda expuesta en las cimas: el modelo sistemáticamente *subestima* los picos de tráfico extremo, quedándose muy corto en las horas pico. 

### Diagnóstico Matemático (Residuales)
![Diagnóstico SARIMA](/Users/nathalyparedes/movilidad_urbana_nyc/movilidad_urbana_nyc/resultados/graficos/diagnostico_sarima.png)

**Comentario Analítico:**  
Este panel de 4 gráficas es la prueba reina en econometría. El correlograma (abajo a la derecha) demuestra que la mayoría de los puntos azules están dentro de la zona celeste permitida, lo que indica que el modelo sí logró exprimir matemáticamente la serie de tiempo. Pero el histograma (arriba a la derecha) revela "colas pesadas"; esto confirma que los eventos anómalos de Nueva York no siguen una distribución normal tradicional, y por eso SARIMA se confunde en los extremos.
