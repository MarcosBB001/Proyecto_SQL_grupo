import psycopg

def connect_to_db():
    DATABASE_URL = ""
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("SELECT version();")
    print(cur.fetchone())

    return conn, cur

def close_connection(conn, cur):
    cur.close()
    conn.close()


def connect_to_local_db():
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="postgres",
        user="postgres",
        password="meaburro")

    cur = conn.cursor()

    print("Local db version: ")
    cur.execute("SELECT version();")
    print(cur.fetchone())

    return conn, cur