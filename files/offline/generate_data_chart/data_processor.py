import re
from collections import Counter
from datetime import date, datetime, timedelta

import nltk
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from data_extractor import get_transcription, get_transcription_set

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
    data_new_format = pd.DataFrame(matrix).T
    data_new_format.rename(columns=columns, inplace=True)
    return data_new_format

def generate_trace(x, y, hex_color, i):
    scatter= None
    color = hex_color.strip('#')
    if i == 0:
        scatter = go.Scatter(
            name=f'Tópico {i}',
            x=x, y=y,
            mode='lines', 
            line=dict(width=0.5, color=f'rgb{str(tuple(int(color[i:i+2], 16) for i in (0, 2, 4)))}' ),
            stackgroup='one',
            groupnorm='percent'
        )
    else:
        scatter = go.Scatter(
            name=f'Tópico {i}',
            x=x, y=y,
            mode='lines', 
            line=dict(width=0.5, color=f'rgb{str(tuple(int(color[i:i+2], 16) for i in (0, 2, 4)))}' ),
            stackgroup='one',
        )
    return scatter

def get_area_chart(num_topics, lda_model):
    data = get_data(num_topics, lda_model)
    data.to_csv('../../../Data/data_chart.csv')
    x = data.index.values 
    figure = go.Figure()
    
    for i in range(num_topics):
        x = x 
        y = list(data[f'Tópico {i}'].tolist())
        figure.add_trace( generate_trace(x, y, COLOR_TEMPLATE[i]), i) 

    figure.update_layout(
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
            a = a.replace(' . ', '. ').replace(' ; ', '; ').replace(' , ', ', ').replace(' ,', ', ').replace(' : ', ': ')
            a = a.replace(' ?', '?').replace(' :, ', ': ').replace(" ’. ", "’. ").replace(" ‘ ", " ‘").replace(" ’ ", "’ ")
            a = a.replace(" ‘, ", "‘, ")
            new_format_doc.append(a)
            new_format_doc.append(w)
            aux_list = []
    else:
        new_format_doc.append(' '.join(aux_list))
    return new_format_doc

if __name__ == "__main__":
    pass
