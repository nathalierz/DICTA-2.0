import gensim
from gensim.corpora import Dictionary
from gensim.test.utils import datapath
from datetime import date, timedelta, datetime
from data_processor import get_nouns_from_document, COLOR_TEMPLATE
from data_extractor import get_transcription_set, get_last_speech_stored
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from os import remove
import sys
temp_file = datapath('LDA_MODEL')

MAIN_FILE_PATH = '../../../Data/data_chart.csv'
TEMPORAL_FILE_PATH = '../../../Data/temporal.csv'

#TODO: este script debe de ser configurado en crontab

def get_data(num_topics=33):
    matrix ={}
    trans_set = get_transcription_set() # Obtiene todas las conferencias en las que habla el presidente
    lda_model = gensim.models.LdaModel.load(temp_file)
    for i in range(trans_set.shape[0]):
        df_row = trans_set.iloc[[i]]
        document = [get_nouns_from_document(df_row.iloc[0]['transcripcion'])]
        dictionary = Dictionary(document)
        document_doc2bow = list([dictionary.doc2bow(text) for text in document])
        document_topics = lda_model.get_document_topics(document_doc2bow)
        x = []
        for j in range(num_topics):
            x.insert(i, 0.0)
        for t in document_topics[0]:
            del x[t[0]-1]
            x.insert(t[0]-1, t[1])
        matrix[df_row.iloc[0]['fecha']] = x
    columns = {}
    for i in range(1, num_topics+1):
        columns[i-1]=f'Tópico {i}'
    data_new_format = pd.DataFrame(matrix).T
    data_new_format.rename(columns=columns, inplace=True)
    data_new_format.to_csv(MAIN_FILE_PATH)


def save_new_data(num_topics=33):
    print("Save_new_data...")
    latest_transcription = get_last_speech_stored() # obtiene la ultima conferencia guardada
    print(latest_transcription)
    lda_model = gensim.models.LdaModel.load(temp_file)
    document = [get_nouns_from_document(latest_transcription.iloc[0]['transcripcion'])]
    print("document...\n")
    dictionary = Dictionary(document)
    document_doc2bow = list([dictionary.doc2bow(text) for text in document])
    document_topics = lda_model.get_document_topics(document_doc2bow)
    new_distribution = {}
    x = []
    
    for i in range(latest_transcription.shape[0]):
        for j in range(num_topics):
            x.insert(i, 0.0)
        for t in document_topics[0]:
            del x[t[0]-1]
            x.insert(t[0]-1, t[1])

        new_distribution[latest_transcription.iloc[0]['fecha']] = []

    d = pd.DataFrame(new_distribution).T
    columns = {}
    for i in range(1, num_topics+1):
        columns[i-1]=f'Tópico {i}'
    d.rename(columns=columns, inplace=True)

    data = pd.read_csv(MAIN_FILE_PATH)
    
    d.to_csv(TEMPORAL_FILE_PATH)
    d = pd.read_csv(TEMPORAL_FILE_PATH)
    remove(TEMPORAL_FILE_PATH)
    
    new_data = data.append(d, ignore_index=True)
    new_data.to_csv(MAIN_FILE_PATH)

if __name__ == "__main__":
    if sys.argv[1] == '-g':
        get_data()
        save_new_data()
    if sys.argv[1] == '-s':
        save_new_data()