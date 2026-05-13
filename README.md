# Movilidad Urbana NYC - Yellow Taxi (Enero 2025)

## Título
Análisis geoespacial, temporal y predictivo de demanda de transporte en la ciudad de Nueva York.

## Caso elegido
Caso 04 · Movilidad Urbana Nueva York

## Integrantes
- Maria de Lourdes Ponce Ochoa
- Nathaly Noelia Paredes
- Aaron Sebastian Spin

## Descripción
Este proyecto tiene como objetivo identificar los "Hot spots" (puntos calientes) de mayor demanda de transporte en la ciudad de Nueva York. Hemos limpiado una base de datos masiva de 3.4 millones de viajes, asignado coordenadas geográficas precisas a las zonas, y entrenado algoritmos avanzados de predicción de series de tiempo (Prophet, SARIMA) para proyectar la demanda.

## Documentación
Toda la documentación detallada del proyecto, la estructura de carpetas actualizada y los resultados de los modelos se encuentran en la carpeta [`docs/`](docs/).

- 📖 [Ver estructura de carpetas y próximos pasos (docs/README.md)](docs/README.md)
- 📊 [Ver contexto de negocio consolidado (docs/CONTEXTO_NEGOCIO.md)](docs/CONTEXTO_NEGOCIO.md)
- 🤖 [Ver la competencia de modelos de IA (docs/MODELADO_SERIES_TIEMPO.md)](docs/MODELADO_SERIES_TIEMPO.md)

## Configuración del Entorno
Para instalar las dependencias necesarias y reproducir este proyecto, ejecuta:

```bash
pip install -r requirements.txt
```

## Ejecución del Proyecto (Fase 6)
El producto analítico está diseñado bajo una arquitectura cliente-servidor real.

**1. Levantar la API (Backend):**
En una terminal, ubícate en la carpeta del proyecto y ejecuta:
```bash
cd app
uvicorn api:app --reload
```
*(Puedes ver la documentación interactiva Swagger en `http://localhost:8000/docs`)*

**2. Levantar el Dashboard (Frontend):**
Abre una **segunda terminal**, ubícate en la carpeta del proyecto y ejecuta:
```bash
cd app
streamlit run dashboard.py
```
*(El dashboard interactivo se abrirá en tu navegador web automáticamente).*
