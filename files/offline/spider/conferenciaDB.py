import psycopg2
import pandas as pd
sql_insert0 = """insert into conferencia_completa (fecha, transcripcion) values (%s, %s);""" 
sql_insert = """insert into ponente (nombre) values (%s);"""
sql_insert2 = """insert into conferencia (transcripcion, id_ponente, fecha) values(%s, %s, %s);"""
sql_insert3 = """insert into participan(id_conferencia, id_ponente, fecha)values(%s, %s, %s);"""
sql_prueba = """insert into prueba (nombre, numero) values (%s, %s);"""

USER = 'larias'
PASSWORD = 'jk2bj6VbAz#'
BD = 'pt_larias'

def insert_conferencia_completa(date, transcription):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(user=USER, host='127.0.0.1', database=BD, password=PASSWORD)
        cursor = conn.cursor()
        cursor.execute(sql_insert0, (date, transcription))
        conn.commit()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()

def insert_ponente(nombre):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(user=USER, host='127.0.0.1', database=BD, password=PASSWORD)
        cursor = conn.cursor()
        cursor.execute(sql_insert, (nombre,))
        conn.commit()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()

def insert_conferencia(transcription, id_ponente, date):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(user=USER, host='127.0.0.1', database=BD, password=PASSWORD)
        cursor = conn.cursor()
        cursor.execute(sql_insert2, (transcription, int(id_ponente), date))
        conn.commit()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()

def insert_participan(id_conferencia, id_ponente, date):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(user=USER, host='127.0.0.1', database=BD, password=PASSWORD)
        cursor = conn.cursor()
        cursor.execute(sql_insert3,(int(id_conferencia), int(id_ponente), date))
        conn.commit()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()

def insert_prueba(nombre, numero):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(user=USER, host='127.0.0.1', database=BD, password=PASSWORD)
        cursor = conn.cursor()
        cursor.execute(sql_prueba, (nombre, int(numero)))
        conn.commit()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    
def get_nombres():
    conn = None
    cursor = None
    tuplas = []
    try:
        conn = psycopg2.connect(user=USER, host='127.0.0.1', database=BD, password=PASSWORD)
        cursor = conn.cursor()
        result = cursor.execute("select * from ponente;")# Cambiar query
        records = cursor.fetchall()
        for r in records:# Cada resultado se recibe en forma de tupla
            tuplas.append((r[0], r[1]))
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return tuplas
    
def get_fechas():
    conn = None
    cursor = None
    tuplas = []
    try:
        conn = psycopg2.connect(user=USER, host='127.0.0.1', database=BD, password=PASSWORD)
        cursor = conn.cursor()
        result = cursor.execute("""select id_conferencia, fecha, id_ponente from conferencia;""")# Cambiar query
        records = cursor.fetchall()
        for r in records:# Cada resultado se recibe en forma de tupla
            tuplas.append((r[0], r[1], r[2]))
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return tuplas


if __name__ == "__main__":
    conn = None
    cursor = None
    id=31
    try:
        conn = psycopg2.connect(user=USER, host='127.0.0.1', database=BD, password=PASSWORD)
        cursor = conn.cursor()
        result = cursor.execute(f'select id_conferencia, fecha, transcripcion from conferencia where id_ponente = {id};')# Cambiar query
        records = cursor.fetchall()
        df = pd.DataFrame(records, columns=['ID', 'Fecha', 'Transcripción'])
        print(df.head(2))
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
