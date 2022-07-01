import psycopg2
from scripts.test import get_ponentes
import pandas as pd
from scripts.ponente import Ponente
from hermetrics.levenshtein import Levenshtein
from difflib import SequenceMatcher
from scripts.database.conferenciaDB import insert_conferencia, insert_participan, insert_ponente, get_nombres, get_fechas
from tqdm import tqdm
def similar(a, b, mode=0):
    if mode == 0:
        s = SequenceMatcher(None, a, b).ratio()
        return s
    else:
        lev = Levenshtein()
        return lev.similarity(a, b)

def get_participantes():
    data = pd.read_csv('/home/tecnologias/Dicta/Data/data.csv', sep=',')
    
    shape = data.shape[0]
    ponentes = []
    for i in tqdm(range(shape)):
        df = data.iloc[[i]]
        # print(f"Procesando: {i}")
        ponentes.append(get_ponentes(df))

    return ponentes

#################################################3
def get_participante():
    data = pd.read_csv('/home/tecnologias/Dicta/Data/data.csv', sep=',')
    ponentes = []
    for i in range(data.shape[0]):
        df = data.iloc[[i]]
        fecha = df.iloc[0]['fecha']
        if fecha == 'octubre 23, 2020':
            ponentes.append(get_ponentes(df))
            print("Encontrado!!")
    return ponentes
#################################################3

def main():
    #ratio > 8
    lista_participantes = get_participantes()
    # lista_participantes = get_participante()
    nombres = []

    for e in lista_participantes:
        for w in e:
            nombres.append(w.nombre)
    nombres_set = [e for e in set(nombres)]
    nombres_aux = [e for e in nombres_set]
    for e in nombres_set:
        for i in nombres_aux:
            ratio = similar(e, i)
            if ratio > 0.75 and ratio != 1:
                for o in nombres_set:
                    ratio = similar(i, o)
                    if ratio == 1:
                        nombres_set.remove(o)
                nombres_aux.remove(i)
    
    for e in nombres_aux:
        for i in lista_participantes:
            for j in i:
                ratio = similar(e, j.nombre)
                if ratio > 0.75 and ratio != 1:
                    j.nombre = e

    print("Insertando nombres en tabla ponentes...")
    for e in nombres_aux:# se insertan los participantes en la base de datos
        insert_ponente(e)
    print("Insertando conferencias...")
    nombres_db = get_nombres()
    for e in nombres_db:
        for w in lista_participantes:
            for i in w:
                if e[1] == i.nombre:
                    insert_conferencia( i.content, e[0], i.fecha)
    
if __name__ == "__main__":
    main()
    
