import os
import re
from datetime import date, timedelta

import pandas as pd
import psycopg2
import spacy

USER = 'larias'
PASSWORD = 'jk2bj6VbAz#'
DB = 'pt_larias'

ID = 1

def get_connection():
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(user=USER, host='127.0.0.1', database=DB, password=PASSWORD)
        cursor = conn.cursor()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    return (conn, cursor)

def get_transcription_set():
    conn, cursor = get_connection()
    
    try:
        cursor.execute(f"select fecha, transcripcion from conferencia where id_ponente={ID} order by id_conferencia asc;")
        records = cursor.fetchall()
        df = pd.DataFrame(records, columns=['fecha', 'transcripcion'])
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return df

def get_transcription_training(): 
    conn, cursor = get_connection()
    try:
        result = cursor.execute(f'select fecha, transcripcion from conferencia where id_ponente = {ID};')
        records = cursor.fetchall()
        df = pd.DataFrame(records, columns=['Fecha', 'Transcripción'])
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return df

def get_last_date_stored():
    conn, cursor = get_connection()
    latest_date = date.today()
    flag = False
    if latest_date.weekday() == 0:
        flag = True
    try:
        cursor.execute(f"select fecha from conferencia where id_ponente={ID} order by id_conferencia desc limit 1;")
        records = cursor.fetchall()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return records[0][0]

def get_last_speech_stored():
    conn, cursor = get_connection()
    try:
        cursor.execute(f"select fecha, transcripcion from conferencia where id_ponente={ID} order by id_conferencia desc limit 1;")
        records = cursor.fetchall()
        df = pd.DataFrame(records, columns=['fecha', 'transcripcion'])
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return df
    
def get_transcription(fecha):
    conn, cursor = get_connection()
    try:
        cursor.execute(f"select id_conferencia, fecha, transcripcion from conferencia where fecha = '{fecha}' and id_ponente={ID};")# Cambiar query
        records = cursor.fetchall()
        df = pd.DataFrame(records, columns=['ID', 'Fecha', 'Transcripción'])
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return df

def get_transcriptions(initial_date, final_date):
    conn, cursor = get_connection()
    transcripciones = []
    try:
        cursor.execute(f"select id_conferencia, fecha, transcripcion from conferencia where fecha between '{initial_date}' and '{final_date}' and id_ponente = {ID};")
        records = cursor.fetchall()
        for row in records:
            transcripciones.append(row[2])
        df = pd.DataFrame(records, columns=['ID', 'Fecha', 'Transcripción'])
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return (df, transcripciones)

def get_speakers(fecha):
    conn, cursor = get_connection()
    df = None
    try:
        cursor.execute(f"select nombre from ponente inner join conferencia on ponente.id_ponente = conferencia.id_ponente and fecha = '{fecha}';")
        records = cursor.fetchall()
        df = pd.DataFrame(records, columns=['Nombre'])
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return df

def is_stored(fecha):
    conn, cursor = get_connection()
    flag = True
    try:
        cursor.execute(f"select id_conferencia from conferencia where fecha = '{fecha}' and id_ponente = {ID};")
        records = cursor.fetchall()
        if records == []:
            flag = False
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)    
    conn.close()
    return flag

def get_corpus_coferencia_completa(): # Conferencias completas
    conn, cursor = get_connection()
    try:
        cursor.execute(f"select * from conferencia_completa order by fecha asc;")
        records = cursor.fetchall()
        df = pd.DataFrame(records, columns=['fecha', 'transcripcion'])
        df['fecha'] = df['fecha'].astype('string')
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return df

def get_fecha(ID):
    conn, cursor = get_connection()
    try:
        cursor.execute(f"select fecha from conferencia where id_conferencia={ID};")
        records = cursor.fetchall()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return records[0][0]

if __name__ == "__main__":
    some = get_last_transcription_stored()
    print(some, type(some))
