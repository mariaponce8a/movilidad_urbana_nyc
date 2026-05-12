import json

path = '../notebooks/05_modelado_series_tiempo.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 4.5 Validación del Modelo (Train / Test Split)\n",
            "\n",
            "Para validar rigurosamente la precisión del modelo, dividiremos el mes de Enero en dos partes:\n",
            "- **Train (Entrenamiento):** Primeros 24 días para que el modelo aprenda.\n",
            "- **Test (Prueba):** Últimos 7 días para evaluar qué tan precisas fueron las predicciones comparadas con la realidad."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import numpy as np\n",
            "\n",
            "# Definir el punto de corte (24 de Enero de 2025)\n",
            "fecha_corte = df_prophet['ds'].min() + pd.Timedelta(days=24)\n",
            "\n",
            "train = df_prophet[df_prophet['ds'] < fecha_corte].copy()\n",
            "test = df_prophet[df_prophet['ds'] >= fecha_corte].copy()\n",
            "\n",
            "print(f\"Datos de Entrenamiento: {len(train)} horas\")\n",
            "print(f\"Datos de Prueba: {len(test)} horas\")\n",
            "\n",
            "# Entrenar modelo solo con Train\n",
            "m_val = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=False)\n",
            "m_val.fit(train)\n",
            "\n",
            "# Predecir para el periodo de Test\n",
            "future_val = m_val.make_future_dataframe(periods=len(test), freq='h')\n",
            "forecast_val = m_val.predict(future_val)\n",
            "\n",
            "# Unir predicciones con valores reales para calcular el error\n",
            "resultados = test.merge(forecast_val[['ds', 'yhat']], on='ds')\n",
            "\n",
            "# Calcular Métricas de Error\n",
            "mae = np.mean(np.abs(resultados['y'] - resultados['yhat']))\n",
            "rmse = np.sqrt(np.mean((resultados['y'] - resultados['yhat'])**2))\n",
            "\n",
            "print(f\"\\nMétricas de Error en el set de Prueba (Test):\")\n",
            "print(f\"MAE (Error Absoluto Medio): {mae:.2f} viajes por hora\")\n",
            "print(f\"RMSE (Raíz del Error Cuadrático Medio): {rmse:.2f} viajes por hora\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "Visualizamos la predicción (naranja) vs la realidad (azul) durante la última semana de Enero:"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "plt.figure(figsize=(15, 5))\n",
            "plt.plot(resultados['ds'], resultados['y'], label='Realidad (Test)', color='blue', alpha=0.6)\n",
            "plt.plot(resultados['ds'], resultados['yhat'], label='Predicción Prophet', color='orange', linestyle='--')\n",
            "plt.title(f\"Validación del Modelo: Real vs Predicho (Zona {zona_principal})\")\n",
            "plt.xlabel(\"Fecha\")\n",
            "plt.ylabel(\"Total de Viajes\")\n",
            "plt.legend()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---"
        ]
    }
]

# Insert the new cells after cell index 9 (which is the training of the full model, 4. Entrenar el Modelo Prophet)
# Let's find the index of "### 5. Predicción (Forecast) para la siguiente semana"
insert_index = 0
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown' and '### 5. Predicción' in str(cell['source']):
        insert_index = i
        break

if insert_index > 0:
    nb['cells'] = nb['cells'][:insert_index] + new_cells + nb['cells'][insert_index:]
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Notebook actualizado con la validación de Train/Test.")
else:
    print("No se encontró el punto de inserción.")
