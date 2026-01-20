import psycopg2
import pandas as pd

# Configuración de la conexión
DB_HOST = "api.atrevetefundacion.org"
DB_NAME = "data"
DB_USER = "pedro"
DB_PASSWORD = "fjtyps"
DB_PORT = "5432"


def get_db_connection():
    """Establece y retorna una conexión a la base de datos PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        raise Exception(f"Error al conectar a la base de datos: {e}")


def fetch_students_data():
    """
    Obtiene todos los datos de estudiantes con sus resultados PAES y postulaciones.
    Incluye el año más reciente asociado a los cursos de cada alumno.
    
    Returns:
        pandas.DataFrame: DataFrame con todos los datos de estudiantes
    """
    query = """
        SELECT 
            u.id AS user_id,
            u."lastName" || ' ' || u."name" AS full_name,
            u."phone" AS phone_number,
            MAX(s."name") AS school_name,
            MAX(g."name") AS grade_name,
            MAX(y."name") AS year_name,
            MAX(e."name") AS establishment_name,
            MAX(c."name") AS career_name,
            MAX(r."nem") AS nem, 
            MAX(r."ranking") AS ranking, 
            MAX(r."m1") AS m1, 
            MAX(r."m2") AS m2, 
            MAX(r."language") AS language, 
            MAX(r."history") AS history, 
            MAX(r."science") AS science, 
            MAX(r."scienceMention") AS "scienceMention",
            CASE WHEN MAX(r."id") IS NOT NULL THEN TRUE ELSE FALSE END AS has_results
        FROM "Users" u
        JOIN "UserCourses" uc ON u.id = uc."UserId"
        JOIN "Courses" co ON uc."CourseId" = co.id
        JOIN "Schools" s ON co."SchoolId" = s.id
        JOIN "Grades" g ON co."GradeId" = g.id
        LEFT JOIN (
            SELECT DISTINCT ON ("UserId") 
                "UserId", 
                co2."YearId"
            FROM "UserCourses" uc2
            JOIN "Courses" co2 ON uc2."CourseId" = co2.id
            WHERE uc2."role" = 'student'
            ORDER BY "UserId", co2."YearId" DESC
        ) latest_year ON u.id = latest_year."UserId"
        LEFT JOIN "Years" y ON latest_year."YearId" = y.id
        LEFT JOIN "Results" r ON u.id = r."UserId"
        LEFT JOIN "Establishments" e ON r."EstablishmentId" = e.id
        LEFT JOIN "Careers" c ON r."CareerId" = c.id
        WHERE uc."role" = 'student'
        GROUP BY u.id, u."lastName", u."name", u."phone"
    """
    
    conn = None
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        raise Exception(f"Error al obtener datos de estudiantes: {e}")
    finally:
        if conn:
            conn.close()
