import os
import pandas as pd
import db_utils 
from psycopg import sql
from datetime import datetime

os.chdir("Proyecto_SQL_grupo")

def insert_query(conn, cur,  table, columns, values):
    """ Psycopg query composition: https://www.psycopg.org/psycopg3/docs/api/sql.html 
        table: string with the table name
        columns: list with the column strings
        values: list with column values
    """
    query = sql.SQL("""INSERT INTO {} ({}) VALUES ({})""").format(
        sql.Identifier(table),  # Insert table name safely
        sql.SQL(', ').join(map(sql.Identifier, columns)),  # Insert column names separated by comas safely
        sql.SQL(', ').join(sql.Placeholder() * len(values))  # Insert %s where there are going to be values
    )
    cur.execute(query, values)  # Insert values where there are %s
    conn.commit()

    return None

def truncate_all_tables(conn, cur):
    cur.execute("""TRUNCATE TABLE alumno_proyecto, alumno_curso, prof_curso, curso, alumno, proyecto, profesor, promocion, campus, bootcamp
        RESTART IDENTITY CASCADE;
    """)
    conn.commit()

def insert_data_main_tables(conn, cur):
    # Read CSVs
    clase_1 = pd.read_csv("data/clase_1.csv", sep=";")   
    clase_2 = pd.read_csv("data/clase_2.csv", sep=";")   
    clase_3 = pd.read_csv("data/clase_3.csv", sep=";")   
    clase_4 = pd.read_csv("data/clase_4.csv", sep=";")   
    claustro = pd.read_csv("data/claustro.csv", sep=";")

    all_classes = pd.concat([clase_1, clase_2, clase_3, clase_4], ignore_index=True)

    # ══════════════════════════════════════════════════════════════════════════════
    # 1. BOOTCAMP 
    # ══════════════════════════════════════════════════════════════════════════════
    unique_verticales = claustro["Vertical"].unique()
    table = "bootcamp"
    columns = ["nombre_bootcamp"]
    for u_v in unique_verticales:
        insert_query(conn, cur, table=table, columns=columns, values=[u_v])

    # ══════════════════════════════════════════════════════════════════════════════
    # 2. CAMPUS
    # ══════════════════════════════════════════════════════════════════════════════
    unique_campus = claustro["Campus"].unique()
    table = "campus"
    columns = ["ciudad"]
    for u_c in unique_campus:
        insert_query(conn, cur, table=table, columns=columns, values=[u_c])

    # ══════════════════════════════════════════════════════════════════════════════
    # 3. PROMOCION
    # ══════════════════════════════════════════════════════════════════════════════
    unique_promocion = all_classes[["Promoción", "Fecha_comienzo"]].drop_duplicates()
    table = "promocion"
    columns = ["nombre_promocion", "fecha_inicio"]
    for _, u_p in unique_promocion.iterrows():
        fecha = datetime.strptime(u_p["Fecha_comienzo"], "%d/%m/%Y").date()
        insert_query(conn, cur, table=table, columns=columns, values=[u_p["Promoción"], fecha])

    # ══════════════════════════════════════════════════════════════════════════════
    # 4. ALUMNO
    # ══════════════════════════════════════════════════════════════════════════════
    table = "alumno"
    columns = ["nombre_alumno", "email"]
    for _, row in all_classes.iterrows():
        insert_query(conn, cur, table=table, columns=columns, values=[row["Nombre"], row["Email"]])

    # ══════════════════════════════════════════════════════════════════════════════
    # 5. PROYECTO
    # ══════════════════════════════════════════════════════════════════════════════
    ds_projects = ["Proyecto_HLF", "Proyecto_EDA", "Proyecto_BBDD", "Proyecto_ML", "Proyecto_Deployment"]
    fs_projects = ["Proyecto_WebDev", "Proyecto_FrontEnd", "Proyecto_Backend", "Proyecto_React", "Proyecto_FullSatck"]
    all_projects = ds_projects + fs_projects

    table = "proyecto"
    columns = ["nombre_proyecto"]
    for project in all_projects:
        insert_query(conn, cur, table=table, columns=columns, values=[project])

    # ══════════════════════════════════════════════════════════════════════════════
    # 6. PROFESOR
    # ══════════════════════════════════════════════════════════════════════════════
    table = "profesor"
    columns = ["nombre_profesor"]
    for _, row in claustro.iterrows():
        insert_query(conn, cur, table=table, columns=columns, values=[row["Nombre"]])
    

def insert_data_depency_tables(conn, cur):
    # Read CSVs
    clase_1 = pd.read_csv("data/clase_1.csv", sep=";")   
    clase_2 = pd.read_csv("data/clase_2.csv", sep=";")   
    clase_3 = pd.read_csv("data/clase_3.csv", sep=";")   
    clase_4 = pd.read_csv("data/clase_4.csv", sep=";")   
    claustro = pd.read_csv("data/claustro.csv", sep=";")

    # Manually add a column to each df so it is easier to operate later
    clase_1["_vertical"] = "DS"
    clase_2["_vertical"] = "DS"
    clase_3["_vertical"] = "FS"
    clase_4["_vertical"] = "FS"
    
    all_classes = pd.concat([clase_1, clase_2, clase_3, clase_4], ignore_index=True)

    # We need to get the ids that the DB assigned when creating the base tables
    # We also need to get the field associated with the IDs (ej: get the id and the name associated with a professor)
    # A name:id dict is needed to match data in the .csv and insert it into the tables a FKs

    cur.execute("SELECT bootcamp_id, nombre_bootcamp FROM bootcamp")
    bootcamp_ids = {nombre: bid for bid, nombre in cur.fetchall()}

    cur.execute("SELECT campus_id, ciudad FROM campus")
    campus_ids = {ciudad: cid for cid, ciudad in cur.fetchall()}

    cur.execute("SELECT promocion_id, nombre_promocion FROM promocion")
    promocion_ids = {nombre: pid for pid, nombre in cur.fetchall()}

    cur.execute("SELECT profesor_id, nombre_profesor FROM profesor")
    profesor_ids = {nombre: pid for pid, nombre in cur.fetchall()}
    
    # ══════════════════════════════════════════════════════════════════════════════
    # 7. CURSO
    # ══════════════════════════════════════════════════════════════════════════════
    # unique combination of bootcamp + promocion + campus + modalidad
    unique_cursos = claustro[["Vertical", "Promocion", "Campus", "Modalidad"]].drop_duplicates()

    table = "curso"
    columns = ["bootcamp_id", "promocion_id", "campus_id", "modalidad"]
    for _, row in unique_cursos.iterrows():
        insert_query(conn, cur, table=table, columns=columns, values=[
            bootcamp_ids[row["Vertical"]],
            promocion_ids[row["Promocion"]],
            campus_ids[row["Campus"]],
            row["Modalidad"]
        ])

    # Gett the ids that define a curso
    cur.execute("SELECT curso_id, bootcamp_id, promocion_id, campus_id FROM curso")
    curso_ids = {(bid, pid, cid): curso_id for curso_id, bid, pid, cid in cur.fetchall()}

    # ══════════════════════════════════════════════════════════════════════════════
    # 8. PROF_CURSO
    # ══════════════════════════════════════════════════════════════════════════════
    table = "prof_curso"
    columns = ["profesor_id", "curso_id", "rol"]
    for _, row in claustro.iterrows():
        # Match the curso_id with the row that matches the nombre_bootcamp, ciudad, and nombre_profesor
        # Given the vertical, promocion and campus of this profesor, which curso do they belong to
        curso_key = (bootcamp_ids[row["Vertical"]], promocion_ids[row["Promocion"]], campus_ids[row["Campus"]])
        insert_query(conn, cur, table=table, columns=columns, values=[
            profesor_ids[row["Nombre"]],
            curso_ids[curso_key],
            row["Rol"]
        ])

    # ══════════════════════════════════════════════════════════════════════════════
    # 9. ALUMNO_CURSO
    # ══════════════════════════════════════════════════════════════════════════════
    cur.execute("SELECT alumno_id, nombre_alumno FROM alumno")
    alumno_ids = {nombre: aid for aid, nombre in cur.fetchall()}

    table = "alumno_curso"
    columns = ["alumno_id", "curso_id"]
    for _, row in all_classes.iterrows():
        # Again, find the curso_key that matches. This time its "_bootcamp" instead of "Vertical".
        curso_key = (
            bootcamp_ids[row["_vertical"]],
            promocion_ids[row["Promoción"]],
            campus_ids[row["Campus"]]
        )
        insert_query(conn, cur, table=table, columns=columns, values=[
            alumno_ids[row["Nombre"]],
            curso_ids[curso_key]
        ])
    
    # ══════════════════════════════════════════════════════════════════════════════
    # 10. ALUMNO_PROYECTO
    # ══════════════════════════════════════════════════════════════════════════════
    cur.execute("SELECT proyecto_id, nombre_proyecto FROM proyecto")
    proyecto_ids = {nombre: pid for pid, nombre in cur.fetchall()}

    ds_projects = ["Proyecto_HLF", "Proyecto_EDA", "Proyecto_BBDD", "Proyecto_ML", "Proyecto_Deployment"]
    fs_projects = ["Proyecto_WebDev", "Proyecto_FrontEnd", "Proyecto_Backend", "Proyecto_React", "Proyecto_FullSatck"]

    table = "alumno_proyecto"
    columns = ["alumno_id", "proyecto_id", "curso_id", "apto"]
    for _, row in all_classes.iterrows():
        curso_key = (
            bootcamp_ids[row["_vertical"]],
            promocion_ids[row["Promoción"]],
            campus_ids[row["Campus"]]
        )
        curso_id = curso_ids[curso_key]
        alumno_id = alumno_ids[row["Nombre"]]

        # Since each row has multiple project values ("Apto", "No apto"), we need to do an insert for each project
        # First we choose which project list we need to check (based on the Vertical)
        if row["_vertical"] == "DS":
            projects = ds_projects
        else:
            projects = fs_projects

        for project in projects:  # Transform "Apto" into boolean value
            if row[project] == "Apto":
                apto = True
            else:
                apto = False

            insert_query(conn, cur, table=table, columns=columns, values=[
                alumno_id,
                proyecto_ids[project],
                curso_id,
                apto
            ])


def dump_all_tables(cur):
    tables = [
        "bootcamp", "campus", "promocion", "proyecto", "profesor",
        "curso", "prof_curso", "alumno_curso", "alumno_proyecto", "alumno"
    ]
    with open("dump.txt", "w", encoding="utf-8") as f:
        for table in tables:
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()
            f.write(f"\n=== {table} ({len(rows)} rows) ===\n")
            for row in rows:
                f.write(str(row) + "\n")
    print("dump.txt created")


# Create connection with DB
# conn, cur = db_utils.connect_to_db()
# conn, cur = db_utils.connect_to_local_db()
# truncate_all_tables(conn, cur)
# insert_data_main_tables(conn, cur)
# insert_data_depency_tables(conn, cur)
# dump_all_tables(cur)
# db_utils.close_connection(conn, cur)