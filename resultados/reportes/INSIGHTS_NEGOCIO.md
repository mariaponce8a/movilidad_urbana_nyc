# Insights Iniciales del Negocio - Yellow Tripdata (Enero 2025)

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
