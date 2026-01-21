import pandas as pd
import numpy as np
from typing import Dict, Tuple


def format_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Formatea la tabla para mejor presentación.
    
    Args:
        df: DataFrame con los datos de estudiantes
        
    Returns:
        DataFrame formateado
    """
    df_formatted = df.copy()
    
    # Formatear números decimales a 2 decimales
    numeric_columns = ['nem', 'ranking', 'm1', 'm2', 'language', 'history', 'science']
    for col in numeric_columns:
        if col in df_formatted.columns:
            # Convertir a numérico primero, manejar errores
            df_formatted[col] = pd.to_numeric(df_formatted[col], errors='coerce')
            # Formatear solo valores numéricos válidos
            df_formatted[col] = df_formatted[col].apply(
                lambda x: f"{float(x):.2f}" if pd.notna(x) else ""
            )
    
    # Renombrar columnas para mejor presentación
    column_mapping = {
        'full_name': 'Nombre Completo',
        'phone_number': 'Teléfono',
        'email': 'Email',
        'school_name': 'Colegio',
        'grade_name': 'Grado',
        'year_name': 'Año',
        'nem': 'NEM',
        'ranking': 'Ranking',
        'm1': 'M1',
        'm2': 'M2',
        'language': 'Lenguaje',
        'history': 'Historia',
        'science': 'Ciencias',
        'scienceMention': 'Mención Ciencias',
        'establishment_name': 'Universidad',
        'career_name': 'Carrera',
        'has_results': 'Tiene Resultados'
    }
    
    df_formatted = df_formatted.rename(columns=column_mapping)
    
    return df_formatted


def get_response_stats(df: pd.DataFrame, group_by: str = None) -> Dict:
    """
    Calcula estadísticas de respuesta por colegio o año.
    
    Args:
        df: DataFrame con los datos de estudiantes
        group_by: Columna por la cual agrupar ('school_name' o 'year_name')
        
    Returns:
        Diccionario con estadísticas de respuesta
    """
    stats = {}
    
    if group_by is None:
        # Estadísticas generales
        total_students = len(df)
        students_with_results = df['has_results'].sum() if 'has_results' in df.columns else 0
        stats['total'] = total_students
        stats['with_results'] = int(students_with_results)
        stats['without_results'] = total_students - int(students_with_results)
        stats['percentage'] = (students_with_results / total_students * 100) if total_students > 0 else 0
    else:
        # Estadísticas agrupadas
        grouped = df.groupby(group_by).agg({
            'has_results': ['count', 'sum']
        }).reset_index()
        
        grouped.columns = [group_by, 'total', 'with_results']
        grouped['without_results'] = grouped['total'] - grouped['with_results']
        grouped['percentage'] = (grouped['with_results'] / grouped['total'] * 100).round(2)
        
        stats = grouped.to_dict('records')
    
    return stats


def calculate_statistics(df: pd.DataFrame) -> Dict:
    """
    Calcula estadísticas descriptivas para las métricas PAES.
    
    Args:
        df: DataFrame con los datos de estudiantes (filtrado)
        
    Returns:
        Diccionario con estadísticas descriptivas
    """
    # Filtrar solo estudiantes con resultados
    df_with_results = df[df['has_results'] == True].copy()
    
    if len(df_with_results) == 0:
        return {}
    
    metrics = ['nem', 'ranking', 'm1', 'm2', 'language', 'history', 'science']
    stats = {}
    
    for metric in metrics:
        if metric in df_with_results.columns:
            # Convertir a numérico, los valores inválidos se convierten a NaN
            values = pd.to_numeric(df_with_results[metric], errors='coerce').dropna()
            if len(values) > 0:
                stats[metric] = {
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'count': int(len(values))
                }
    
    stats['total_students'] = len(df_with_results)
    stats['total_with_complete_results'] = len(df_with_results.dropna(subset=['nem', 'ranking', 'm1', 'm2', 'language', 'history', 'science']))
    
    return stats
