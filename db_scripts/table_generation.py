import pandas as pd
import db_utils

def create_main_tables(conn, cur):
    # Create table alumno
    cur.execute("""CREATE TABLE alumno (
            alumno_id SERIAL PRIMARY KEY, 
            nombre_alumno VARCHAR(50) NOT NULL, 
            email VARCHAR(100) NOT NULL
        );""")
    conn.commit()

    # Create table campus
    cur.execute("""CREATE TABLE campus (
            campus_id SERIAL PRIMARY KEY,
            ciudad VARCHAR(50) NOT NULL
        );""")
    conn.commit()

    # Create table proyecto
    cur.execute("""CREATE TABLE proyecto (
            proyecto_id SERIAL PRIMARY KEY,
            nombre_proyecto VARCHAR(50) NOT NULL
        );""")
    conn.commit()

    # Create table bootcamp 
    cur.execute("""CREATE TABLE bootcamp (
            fotocopiad SERIAL PRIMARY KEY,
            nombre_bootcamp VARCHAR(50) NOT NULL
        );""")
    conn.commit()

    # Create table profesor 
    cur.execute("""CREATE TABLE profesor (
            profesor_id SERIAL PRIMARY KEY,
            nombre_profesor VARCHAR(50) NOT NULL
        );""")
    conn.commit()

    # Create table promocion
    cur.execute("""CREATE TABLE promocion (
            promocion_id SERIAL PRIMARY KEY,
            nombre_promocion VARCHAR(50) NOT NULL,
            fecha_inicio date NOT NULL
        );""")
    conn.commit()

    return None


def create_dependency_tables(conn, cur):
    # Create table curso
    cur.execute("""CREATE TABLE curso (
            curso_id SERIAL PRIMARY KEY,
            bootcamp_id integer NOT NULL REFERENCES bootcamp,
            promocion_id integer NOT NULL REFERENCES promocion,
            campus_id integer NOT NULL REFERENCES campus,
            modalidad VARCHAR(50)
        );""")
    conn.commit()

    # Create table prof_curso
    cur.execute("""CREATE TABLE prof_curso (
            prof_curso_id SERIAL PRIMARY KEY,
            profesor_id integer NOT NULL REFERENCES profesor,
            curso_id integer NOT NULL REFERENCES curso,
            rol VARCHAR(50) NOT NULL
        );""")
    conn.commit()

    # Create table alumno_proyecto
    cur.execute("""CREATE TABLE alumno_proyecto (
            alumno_proyecto_id SERIAL PRIMARY KEY,
            alumno_id integer NOT NULL REFERENCES alumno,
            proyecto_id integer NOT NULL REFERENCES proyecto,
            curso_id integer NOT NULL REFERENCES curso,
            apto BOOLEAN NOT NULL
        );""")
    conn.commit()

    # Create table alumno_curso
    cur.execute("""CREATE TABLE alumno_curso(
            alumno_curso_id SERIAL PRIMARY KEY,
            alumno_id integer NOT NULL REFERENCES alumno,
            curso_id integer NOT NULL REFERENCES curso
        );""")
    conn.commit()

    return None

def show_columns(conn, table_name):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = %s
        """, (table_name,))

        columns = cur.fetchall()

        print(f"Columns in {table_name}:")
        for col in columns:
            print(f"- {col[0]} ({col[1]})")


def create_all_tables(conn, cur):
    """ Creates all tables """
    create_main_tables(conn, cur)
    create_dependency_tables(conn, cur)

    return None


def delete_all_tables(conn, cur):
    """ Deletes all tables """
    cur.execute("DROP SCHEMA public CASCADE;")
    conn.commit()
    cur.execute("CREATE SCHEMA public;")
    conn.commit()

    return None

def show_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()

        print("Tables:")
        for t in tables:
            show_columns(conn=conn, table_name=t[0])

# conn, cur = db_utils.connect_to_db()  # Connection to db in render 

conn, cur = db_utils.connect_to_local_db()  # Connection to local db in postgres
# create_all_tables(conn, cur)

show_tables(conn)

db_utils.close_connection(conn, cur)
