# Este programa permite la indexación del un conjunto de transcripciones
# recuperadas de la base de datos, por lo que ocupa archivos de conexión y obtención
# de datos de dicha base.
# ../Dicta/files/offline/generate_data_chart/
#Ejecución periódica
#

import pyterrier as pt
import pandas as pd
import multiprocessing
import time
import os
from data_extractor import get_corpus_coferencia_completa # NUEVO
import nltk
from nltk.stem import SnowballStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
from shutil import rmtree

if not pt.started():
    pt.init()
from pyterrier.measures import *

class Tokenizer:
  def __init__(self):
    from spacy.lang import es
    self._tokenizer = es.Spanish()

  def __call__(self, text):
    return ' '.join(
      str(t) for t in self._tokenizer(text.strip())
      if not (t.is_stop or t.is_punct or t.is_space)
    )

def corpus_generate(dataframe):
    tok = Tokenizer()
    for index, row in dataframe.iterrows():
        id = row['fecha']
        text = tok(row['transcripcion'])
        yield {'docno' : id, 'text':text}


path = "./index_completo"
print("Eliminando index existente..")
rmtree(path)

if not os.path.exists(path):
    print("Colección de documentos...")
    documents = get_corpus_coferencia_completa() #recuperación de transcripciones de base de datos
    print('Creando index...') #crea un indice en el directorio
    inicio = time.time()
    indexer = pt.IterDictIndexer(path)
    indexer.setProperty("termpipelines","")
    indexer.setProperty("tokeniser", "UTFTokeniser")
    index_ref = indexer.index(corpus_generate(documents), fields=('text',), meta=['docno','text'])
    fin = time.time()
    print(fin-inicio)
else:
    print('Leyendo index pre-existente...')
    index_ref = pt.IndexRef.of('./index_completo/data.properties')
#obtiene el index
index = pt.IndexFactory.of(index_ref)
print(index.getCollectionStatistics().toString())

