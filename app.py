import streamlit as st
import pandas as pd
import plotly.express as px
from database import fetch_students_data
from utils import format_table, get_response_stats, calculate_statistics

# Configuración de la página
st.set_page_config(
    page_title="Resultados PAES - Fundación Atrévete",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Resultados PAES y Postulación Universitaria")
st.markdown("**Fundación Atrévete**")

# Cargar datos
@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data():
    """Carga los datos de estudiantes desde la base de datos."""
    try:
        return fetch_students_data()
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

# Cargar datos
with st.spinner("Cargando datos..."):
    df = load_data()

if df.empty:
    st.warning("No se pudieron cargar los datos. Por favor, verifica la conexión a la base de datos.")
    st.stop()

# Sidebar con filtros (compartido entre pestañas)
with st.sidebar:
    st.header("🔍 Filtros")
    
    # Filtro por año
    years = sorted(df['year_name'].dropna().unique().tolist(), reverse=True)
    selected_year = st.selectbox(
        "Año",
        options=years,
        index=0 if years else None
    )
    
    # Filtro por colegio
    schools = sorted(df['school_name'].dropna().unique().tolist())
    selected_schools = st.multiselect(
        "Colegio",
        options=schools,
        default=schools if schools else []
    )
    
    # Checkbox para mostrar solo con resultados (solo para Vista General)
    show_only_with_results = st.checkbox("Mostrar solo alumnos con resultados completos", value=False)

# Crear pestañas
tab1, tab2 = st.tabs(["📋 Vista General", "📈 Estadísticas"])

# ==================== PESTAÑA 1: VISTA GENERAL ====================
with tab1:
    st.header("Vista General de Alumnos")
    
    # Aplicar filtros
    df_filtered = df.copy()
    
    if selected_year:
        df_filtered = df_filtered[df_filtered['year_name'] == selected_year]
    
    if selected_schools:
        df_filtered = df_filtered[df_filtered['school_name'].isin(selected_schools)]
    
    if show_only_with_results:
        df_filtered = df_filtered[df_filtered['has_results'] == True]
    
    # Contadores de respuesta
    st.subheader("📊 Estadísticas de Respuesta")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_students = len(df_filtered)
    students_with_results = df_filtered['has_results'].sum() if 'has_results' in df_filtered.columns else 0
    students_without_results = total_students - students_with_results
    response_percentage = (students_with_results / total_students * 100) if total_students > 0 else 0
    
    with col1:
        st.metric("Total Alumnos", total_students)
    
    with col2:
        st.metric("Con Resultados", students_with_results)
    
    with col3:
        st.metric("Sin Resultados", students_without_results)
    
    with col4:
        st.metric("Porcentaje Respuesta", f"{response_percentage:.1f}%")
    
    # Desglose por colegio si hay filtro de colegio activo
    if selected_schools and len(selected_schools) > 1:
        st.subheader("📊 Desglose por Colegio")
        school_stats = get_response_stats(df_filtered, group_by='school_name')
        if isinstance(school_stats, list):
            school_df = pd.DataFrame(school_stats)
            st.dataframe(
                school_df[['school_name', 'total', 'with_results', 'without_results', 'percentage']],
                column_config={
                    'school_name': 'Colegio',
                    'total': 'Total',
                    'with_results': 'Con Resultados',
                    'without_results': 'Sin Resultados',
                    'percentage': st.column_config.NumberColumn('Porcentaje', format="%.1f%%")
                },
                hide_index=True
            )
    
    
    # Tabla de datos
    st.subheader("📋 Datos de Alumnos")
    
    # Seleccionar columnas para mostrar
    display_columns = [
        'full_name', 'phone_number', 'email', 'school_name', 'grade_name', 'year_name',
        'nem', 'ranking', 'm1', 'm2', 'language', 'history', 'science', 'scienceMention',
        'establishment_name', 'career_name'
    ]
    
    available_columns = [col for col in display_columns if col in df_filtered.columns]
    df_display = df_filtered[available_columns].copy()
    
    # Formatear tabla
    df_formatted = format_table(df_display)
    
    # Mostrar tabla
    st.dataframe(
        df_formatted,
        use_container_width=True,
        hide_index=True
    )
    
    # Botón para descargar CSV
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv,
        file_name=f"resultados_paes_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ==================== PESTAÑA 2: ESTADÍSTICAS ====================
with tab2:
    st.header("Estadísticas y Análisis")
    
    # Aplicar filtros (usando los filtros compartidos del sidebar)
    df_filtered_stats = df.copy()
    
    if selected_year:
        df_filtered_stats = df_filtered_stats[df_filtered_stats['year_name'] == selected_year]
    
    if selected_schools:
        df_filtered_stats = df_filtered_stats[df_filtered_stats['school_name'].isin(selected_schools)]
    
    # Filtrar solo estudiantes con resultados para estadísticas
    df_with_results = df_filtered_stats[df_filtered_stats['has_results'] == True].copy()
    
    if len(df_with_results) == 0:
        st.warning("No hay estudiantes con resultados para mostrar estadísticas con los filtros seleccionados.")
    else:
        # Métricas descriptivas
        st.subheader("📊 Métricas Descriptivas")
        
        stats = calculate_statistics(df_with_results)
        
        if stats:
            # Crear tabla de métricas
            metrics_data = []
            metric_names = {
                'nem': 'NEM',
                'ranking': 'Ranking',
                'm1': 'M1',
                'm2': 'M2',
                'language': 'Lenguaje',
                'history': 'Historia',
                'science': 'Ciencias',
                'scienceMention': 'Mención Ciencias'
            }
            
            for metric_key, metric_label in metric_names.items():
                if metric_key in stats:
                    metrics_data.append({
                        'Métrica': metric_label,
                        'Promedio': f"{stats[metric_key]['mean']:.2f}",
                        'Desviación Estándar': f"{stats[metric_key]['std']:.2f}",
                        'Mínimo': f"{stats[metric_key]['min']:.2f}",
                        'Máximo': f"{stats[metric_key]['max']:.2f}",
                        'N': stats[metric_key]['count']
                    })
            
            metrics_df = pd.DataFrame(metrics_data)
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            
            # Información adicional
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Estudiantes con Resultados", stats.get('total_students', 0))
            with col2:
                st.metric("Estudiantes con Resultados Completos", stats.get('total_with_complete_results', 0))
        
        # Gráficos
        st.subheader("📈 Visualizaciones")
        
        # Top 10 Universidades
        if 'establishment_name' in df_with_results.columns:
            universities = df_with_results['establishment_name'].dropna().value_counts().head(10)
            if len(universities) > 0:
                st.markdown("### Top 10 Universidades")
                fig_uni = px.bar(
                    x=universities.values,
                    y=universities.index,
                    orientation='h',
                    labels={'x': 'Cantidad de Estudiantes', 'y': 'Universidad'},
                    title="Universidades más comunes"
                )
                fig_uni.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_uni, use_container_width=True)
        
        # Top 10 Carreras
        if 'career_name' in df_with_results.columns:
            careers = df_with_results['career_name'].dropna().value_counts().head(10)
            if len(careers) > 0:
                st.markdown("### Top 10 Carreras")
                fig_career = px.bar(
                    x=careers.values,
                    y=careers.index,
                    orientation='h',
                    labels={'x': 'Cantidad de Estudiantes', 'y': 'Carrera'},
                    title="Carreras más comunes"
                )
                fig_career.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_career, use_container_width=True)
        
        # Histogramas de distribución
        col1, col2 = st.columns(2)
        
        with col1:
            if 'nem' in df_with_results.columns:
                nem_values = pd.to_numeric(df_with_results['nem'], errors='coerce').dropna()
                if len(nem_values) > 0:
                    st.markdown("### Distribución de NEM")
                    fig_nem = px.histogram(
                        nem_values,
                        nbins=20,
                        labels={'value': 'NEM', 'count': 'Frecuencia'},
                        title="Distribución de puntajes NEM"
                    )
                    st.plotly_chart(fig_nem, use_container_width=True)
        
        with col2:
            if 'ranking' in df_with_results.columns:
                ranking_values = pd.to_numeric(df_with_results['ranking'], errors='coerce').dropna()
                if len(ranking_values) > 0:
                    st.markdown("### Distribución de Ranking")
                    fig_ranking = px.histogram(
                        ranking_values,
                        nbins=20,
                        labels={'value': 'Ranking', 'count': 'Frecuencia'},
                        title="Distribución de Ranking"
                    )
                    st.plotly_chart(fig_ranking, use_container_width=True)
        
        # Box plots para pruebas PAES
        st.markdown("### Distribución de Puntajes por Prueba PAES")
        
        paes_tests = ['m1', 'm2', 'language', 'history', 'science']
        paes_labels = ['M1', 'M2', 'Lenguaje', 'Historia', 'Ciencias']
        
        paes_data = []
        for test, label in zip(paes_tests, paes_labels):
            if test in df_with_results.columns:
                # Convertir a numérico antes de usar
                values = pd.to_numeric(df_with_results[test], errors='coerce').dropna()
                if len(values) > 0:
                    for val in values:
                        paes_data.append({'Prueba': label, 'Puntaje': val})
        
        if paes_data:
            df_paes = pd.DataFrame(paes_data)
            fig_box = px.box(
                df_paes,
                x='Prueba',
                y='Puntaje',
                title="Distribución de puntajes por prueba PAES"
            )
            st.plotly_chart(fig_box, use_container_width=True)
