import psycopg2
import pandas as pd
sql_insert = """insert into ponente (nombre) values (%s);"""
sql_insert2 = """insert into conferencia (transcripcion, id_ponente, fecha) values(%s, %s, %s);"""
sql_insert3 = """insert into participan(id_conferencia, id_ponente, fecha)values(%s, %s, %s);"""
sql_prueba = """insert into prueba (nombre, numero) values (%s, %s);"""

USER = 'larias'
PASSWORD = 'jk2bj6VbAz#'
BD = 'pt_larias'

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
    formated_transcription = transcription.strip(': .,').replace('.,', '. ').replace('.:,', '. ').replace(',, ', ', ').replace(' , ', ', ').replace(', ,','').replace(' , ', ', ')
    formated_transcription = formated_transcription.replace(' ; ', '; ').replace(' . ', '. ').replace(' : ', ': ').replace(' . : , ', '. ').replace(' : , ', '. ')
    try:
        conn = psycopg2.connect(user=USER, host='127.0.0.1', database=BD, password=PASSWORD)
        cursor = conn.cursor()
        cursor.execute(sql_insert2, (formated_transcription, int(id_ponente), date))
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
        result = cursor.execute("""select* from ponente;""")# Cambiar query
        records = cursor.fetchall()
        for r in records:
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
        for r in records:
            tuplas.append((r[0], r[1], r[2]))
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return tuplas


if __name__ == "__main__":
    pass