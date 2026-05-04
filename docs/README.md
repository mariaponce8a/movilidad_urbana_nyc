# Análisis Geoespacial de Movilidad Urbana en New York - Caso 04

## Descripción del Proyecto
Este proyecto tiene como objetivo identificar los "Hot spots" (puntos calientes) de mayor demanda de transporte en la ciudad de New York. Adicionalmente, analizaremos cómo varía esta actividad a lo largo del día y de la semana. El análisis se apoyará en visualizaciones cartográficas interactivas que no dependerán de tokens o APIs externas (por ejemplo, usando Folium, Kepler.gl offline, o Plotly).

## Estructura del Proyecto (Memoria)
Esta estructura es el estándar mínimo requerido (CASO 04) y debe mantenerse en todo momento:

```text
proyecto_caso04/
│
├── datos/
│   ├── raw/                    Parquet y CSV originales
│   ├── interim/                Datos intermedios y de diagnóstico
│   └── procesados/             Datos finales limpios y agregaciones
│
├── notebooks/
│   ├── 01_diagnostico.ipynb    Diagnóstico inicial de los datos
│   ├── 02_analisis.ipynb       Patrones espaciales y temporales
│   └── 03_visualizacion.ipynb  Mapas y gráficos
│
├── scripts/
│   ├── pipeline.py             Carga, filtro, validación, enriquecimiento
│   └── utilidades.py           Funciones reutilizables
│
├── config/
│   └── parametros.yaml         Límites geográficos, umbrales
│
├── resultados/
│   ├── graficos/               Mapas y gráficos estáticos
│   └── reportes/               Hallazgos en HTML/Markdown y PDF
│
├── app/
│   └── app.py                  Aplicación principal (Streamlit o FastAPI)
│
├── docs/
│   ├── README.md               Cómo reproducir
│   ├── diccionario.md          Variables
│   ├── NOTAS.md                Requisitos seminario
│   └── CONTEXTO_NEGOCIO.md     Información clave del negocio Yellow Taxi 2025
│
└── requirements.txt            Librerías
```

## Próximos Pasos
1. **Datos:** Colocar o descargar los datos crudos en `datos/raw/`.
2. **Exploración:** Usar `notebooks/01_diagnostico.ipynb` para diagnosticar y limpiar los datos.
3. **Análisis:** Identificar patrones espaciales y temporales en `notebooks/02_analisis.ipynb`.
4. **Visualización:** Generar los mapas interactivos en `notebooks/03_visualizacion.ipynb`.
5. **Dashboard:** Integrar los mapas en una aplicación Streamlit en `app/app.py`.
