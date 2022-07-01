import csv
import re
import pandas as pd
from scripts.segment import segmentation, get_occurences, similar
from scripts.utils import format_date
from scripts.ponente import Ponente

def get_strings_to_ignore():
    ignore = []
    with open('scripts/ignore.txt', 'r') as f:
        lines = f.readlines()
        for p in lines: 
            ignore.append(p.strip(' \n'))
    return ignore       

def get_ponentes(df):

    ignore = get_strings_to_ignore()
    transcription_r = df.iloc[0]['transcripcion']
    fecha = format_date(df.iloc[0]['fecha']) # Formato de la fecha -> yyyy-mm-dd
    
    # Se obtienen  los participantes de la transcripcion
    patterns = ['[A-Z-Á-Ź][A-Z-Á-Ź, A-Z-Á-Ź]*']
    match = re.findall(patterns[0], transcription_r)
    lista_participantes = []
    #puestos = []
    for e in match: # Se obtienen los participantes apartir de la regexp
        e = e.strip(', ')
        if len(e) >= 10 and e not in ignore and e.isupper():
            if e not in ignore:
                nombre = ''
                if ',' in e:
                    nombre, _ = e.split(',', 1)
                    lista_participantes.append(nombre.strip()) # Lista de parcipantes (nombre y puesto) repetidos
                    #puestos.append(puesto.strip())
                else:
                    nombre = e 
                    lista_participantes.append(nombre.strip())

    # Segunda comprobacion para eliminar contenido no deseado
    nueva = []
    for e in lista_participantes:
        if e in ignore:
            pass
        else:
            nueva.append(e)

    lista_aux = [e.strip() for e in nueva if len(e)> 10 and 'AUDIO' not in e and 'INICIA' not in e and 'DECLARACI' not in e ]   
    nombres = set([e.strip() for e in nueva if len(e)> 10 and 'AUDIO' not in e and 'INICIA' not in e and 'DECLARACI' not in e])     
    personajes = []

    for e in set(nombres):
        contenido = segmentation(transcription_r, id=e)
        participaciones = get_occurences(e, lista_aux)
        p = Ponente(e, participaciones=participaciones, content=contenido)
        personajes.append(p)
    

    lis = [e for e in set(personajes)]
    lis_aux = [e for e in personajes]
    
    for e in personajes:
        for j in lis:
            ratio = similar(e.nombre, j.nombre)
            if ratio >= 0.75 and ratio < 1 :
                for o in personajes:
                    ratio = similar(j.nombre, o.nombre)
                    if ratio == 1:
                        personajes.remove(o)
                lis.remove(j)
    lista_final = []
    for e in lis:
        for j in lis_aux:
            ratio = similar(e.nombre, j.nombre)
            if ratio >= 0.75 and ratio < 1:
                e.content += ' ' + j.content
        else:
            lista_final.append(e) 

    for e in lista_final:# Asignacion de ultimos valores 
        e.fecha = fecha

    print(lista_final)
    
    return lista_final


if __name__ == "__main__":
    pass
 
