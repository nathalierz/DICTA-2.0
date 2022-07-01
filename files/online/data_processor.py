import re
from datetime import date, datetime, timedelta
from os import remove
import nltk
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import spacy
from nltk.corpus import stopwords
from gensim.corpora.dictionary import Dictionary
from nltk.tokenize import word_tokenize
from difflib import SequenceMatcher

from data_extractor import get_transcription, get_transcription_set

AREA_CHART = '../../Data/data_chart.csv'

COLOR_TEMPLATE = [
    '#a4c639', '#ffbf00', '#cd9575', '#7fffd4', '#e9d66b', '#b2beb5', '#87a96b', '#ff9966', '#ffe135', '#848482', '#fe6f5e', '#ace5ee',
    '#a2a2d0', '#de5d83', '#b5a642', '#66ff00', '#bf94e4', '#cd7f32', '#ffc1cc', '#f0dc82', '#deb887' ,'#e97451', '#a3c1ad', '#e4717a', 
    '#00cc99', '#ffa6c9', '#ed9121', '#ace1af', '#7fff00', '#ffb7c5', '#ffa700', '#e4d00a', '#fbcce7', '#9bddff', '#8c92ac', '#8c92ac', 
    '#fbec5d', '#bdb76b', '#ff8c00', '#ffa812'
]

def get_data(num_topics, lda_model):
    matrix ={}
    trans_set = get_transcription_set()
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
    data_format = pd.DataFrame(matrix).T
    data_format.rename(columns=columns, inplace=True)
    return data_format

def generate_trace(x, y, hex_color, i):
    scatter = None
    trace_color = hex_color.strip('#')
    trace_color = f'rgb{str(tuple(int(trace_color[i:i+2], 16) for i in (0, 2, 4)))}' 
    if i == 1:
        scatter = go.Scatter(
            name=f'Tópico {i}',
            x=x, y=y,
            mode='lines', 
            line=dict(width=0.5, color=trace_color),
            stackgroup='one',
            groupnorm='percent'
        )
    else:
        scatter = go.Scatter(
            name=f'Tópico {i}',
            x=x, y=y,
            mode='lines', 
            line=dict(width=0.5, color=trace_color),
            stackgroup='one',
        )
    return scatter

def get_area_chart(num_topics, lda_model, custom_model_opt):
    data = None

    if custom_model_opt == 'No':
        data = pd.read_csv(AREA_CHART) 
        # data = pd.read_csv('resources/data/data_chart.csv') 
    else:
        data = get_data(num_topics, lda_model)
    data.to_csv('resources/data/temporal.csv')
    data = pd.read_csv('resources/data/temporal.csv')
    remove('resources/data/temporal.csv')
    data.rename(columns={'Unnamed: 0':'fechas'}, inplace=True)
    x = list(data['fechas'].tolist())
    figure = go.Figure()
    
    for i in range(1, num_topics+1):
        x = x 
        y = list(data[f'Tópico {i}'].tolist())
        figure.add_trace( generate_trace(x, y, COLOR_TEMPLATE[i-1], i)) 

    figure.update_layout(
        title='Evolución de los tópicos.',
        showlegend=True,
        xaxis_type='category',
        yaxis=dict(type='linear', range=[1, 100], ticksuffix='%')
    )
    return figure 

def get_nouns_from_document(text):
    nlp=spacy.load('es_core_news_sm')
    nouns = [w.text for w in nlp(text) if w.is_stop != True and w.is_punct != True and w.pos_ == 'NOUN']
    stop_words = set(stopwords.words('spanish'))
    lista = [ i for i in nouns if i not in stop_words]
    return lista

def topic_tuples(topics):
    color_iterator = 0
    topic_num = 1
    tuples = []
    for e in topics:
        for t in e:
            tuples.append((t, f"Tópico {topic_num}", COLOR_TEMPLATE[color_iterator]))
        color_iterator += 1
        topic_num += 1
    return tuples 

def string_and_tuples(doc, topics):
    tokenize_doc = word_tokenize(doc)

    for term in topics:
        positions = [i for i, x in enumerate(tokenize_doc) if x == term[0]]
        if len(positions) >= 1:
            for i in positions:
                del tokenize_doc[i]
                tokenize_doc.insert(i, term)
    new_format_doc = []
    aux_list = []
    for w in tokenize_doc:
        if isinstance(w, str):
            aux_list.append(w)
        else:
            a = ' '.join(aux_list)
            # a = a.replace(' . ', '. ').replace(' ; ', '; ').replace(' , ', ', ').replace(' ,', ', ').replace(' : ', ': ')
            # a = a.replace(' ?', '?').replace(' :, ', ': ').replace(" ’. ", "’. ").replace(" ‘ ", " ‘").replace(" ’ ", "’ ")
            # a = a.replace(" ‘, ", "‘, ")
            new_format_doc.append(a)
            new_format_doc.append(w)
            aux_list = []
    else:
        new_format_doc.append(' '.join(aux_list))
    return new_format_doc


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def change_element(tuplas, term):
    tuplaN = None
    v = False
    for i, tupla in enumerate(tuplas):
        if tupla[1] == 'ponente':
            if similar(tupla[0], term) > 0.9:
                v = True
                tuplaN = tupla
        else:
            if similar(tupla[0].capitalize(), term.capitalize()) > 0.75 or similar(tupla[0].lower(), term.lower()) > 0.75:
                tuplaN = (term, '', tupla[2])
                v = True
    return tuplaN, v

def string_and_tuples_s(doc, tuplas):
    tokenize_doc = word_tokenize(doc)

    for i, w in enumerate(tokenize_doc):
        if len(w)>3:
            word = change_element(tuplas, w)
            if word[1] == True:
                del tokenize_doc[i]
                tokenize_doc.insert(i, word[0])
    new_format_doc = []
    aux_list = []
    for w in tokenize_doc:
        if isinstance(w, str):
            aux_list.append(w)
        else:
            a = ' '.join(aux_list)
            new_format_doc.append(a)
            new_format_doc.append(w)
            aux_list = []
    else:
        new_format_doc.append(' '.join(aux_list))
    return new_format_doc

def search_tuples(ponentes, query):
    tuples = []
    query = word_tokenize(query)
    for p in ponentes:
        for w in word_tokenize(p):
            tuples.append((w, "ponente", '#bf94e4'))
    for w in query:
        tuples.append((w, "", '#66ff00'))
    return tuples 

if __name__ == "__main__":
    pass
