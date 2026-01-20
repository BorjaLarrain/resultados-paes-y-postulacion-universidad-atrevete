# Resultados PAES y Postulación Universitaria - Fundación Atrévete

Aplicación Streamlit para visualizar los resultados de la prueba PAES y las postulaciones universitarias de los alumnos de la fundación Atrévete.

## Características

- **Vista General**: Tabla interactiva con información completa de cada alumno, filtros por año, colegio y grado, y contadores de respuesta al formulario
- **Estadísticas**: Métricas descriptivas (promedios, desviación estándar, mínimos, máximos) y visualizaciones gráficas (distribuciones, top universidades y carreras)

## Instalación

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecutar la aplicación:
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## Estructura del Proyecto

- `app.py`: Aplicación principal Streamlit con dos pestañas (Vista General y Estadísticas)
- `database.py`: Módulo de conexión a PostgreSQL y queries de datos
- `utils.py`: Funciones auxiliares para formateo y cálculos estadísticos
- `requirements.txt`: Dependencias del proyecto

## Uso

### Vista General
- Utiliza los filtros en el sidebar para filtrar por año, colegio o grado
- Visualiza contadores de respuesta al formulario
- Explora la tabla completa de datos de alumnos
- Descarga los datos filtrados como CSV

### Estadísticas
- Aplica los mismos filtros para analizar subconjuntos de datos
- Revisa métricas descriptivas de todas las pruebas PAES
- Explora visualizaciones de distribución y rankings de universidades y carreras