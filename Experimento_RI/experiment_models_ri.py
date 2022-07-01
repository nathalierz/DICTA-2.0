"""
Experimento de evaluación para modelos BM25, DFRee y PL2
Requiere de la existencia de documento datos_v2.xslx para cargar juicios de relevancia
Su ejecución solo es mediante la ejecución de cualquier script de python
"""
import pyterrier as pt
import pandas as pd
import os
import nltk
from nltk.stem import SnowballStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords



if not pt.started():
    pt.init()

index_ref = pt.IndexRef.of('./index_1/data.properties')
index = pt.IndexFactory.of(index_ref)

# Recuperación de documentos con modelos diferentes ****
BM25 = pt.BatchRetrieve(index, wmodel="BM25")
PL2 = pt.BatchRetrieve(index, wmodel="PL2")
DFRee = pt.BatchRetrieve(index, wmodel="DFRee")

# Consultas *****
topics = pd.DataFrame(
    [['1', "Reducción de delincuencia"],
    ['2', "Programas de Bienestar"],
    ['3', "Refuerzo de vacunas"],
    ['4', "Variante Ómicron"],
    ['5', "Regreso a clases"],
    ['6', "Ajustes al precio de gasolina y petróleo"],
    ['7', "Avances sobre Aeropuerto Internacional Felipe Ángeles"],
    ['8', "Llamado a médicos del Bienestar"],
    ['9', "Avance de vacunación contra COVID"],
    ['10', "Avances en Tren Interurbano México-Toluca"]],  columns=["qid", "query"]
    )


def get_qrels():
    qrels =pd.DataFrame()
    doc = pd.read_excel('datos_v2.xlsx', usecols=['qid', 'docno', 'label'], dtype={'qid': str, 'docno':object, 'label': object})
    is_relevante = doc.loc[:, 'label'] == 1
    qrels = qrels.append(doc.loc[is_relevante], ignore_index=True)
    qrels['iteration'] = 'Q0'
    return qrels

qrels = get_qrels()

print("topics:")
print(topics)
print("\nqrels")
print(qrels)

exp = pt.Experiment(
    [BM25, PL2, DFRee],
    topics,
    qrels,
    eval_metrics=["map"],
    names=["BM25", "PL2", "DFRee"],
    #perquery =True,  # Para obtener resultados por cada consulta
    filter_by_topics=False,
    filter_by_qrels=False,
    )

print("\nResultados de Experimento")
print(exp)
