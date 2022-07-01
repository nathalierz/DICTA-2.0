import gensim
from gensim.corpora import Dictionary
from gensim.test.utils import datapath
from datetime import date, timedelta, datetime
from data_processor import get_nouns_from_document, COLOR_TEMPLATE
from data_extractor import get_transcription_set
import pandas as pd
import numpy as np
import plotly.graph_objects as go

temp_file = datapath('LDA_MODEL')

def generate_trace(x, y, hex_color, i):
    scatter = None
    trace_color = hex_color.strip('#')
    trace_color = f'rgb{str(tuple(int(trace_color[i:i+2], 16) for i in (0, 2, 4)))}' 
    if i == 1:
        scatter = go.Scatter(
            x=x, y=y,
            mode='lines', 
            name=f'Tópico {i}',
            line=dict(width=0.5, color=trace_color),
            stackgroup='one',
            groupnorm='percent'
        )
    else:
        scatter = go.Scatter(
            x=x, y=y,
            mode='lines', 
            name=f'Tópico {i}',
            line=dict( width=0.5, color=trace_color),
            stackgroup='one',
        )
    return scatter

def get_area_chart(num_topics):

    data = pd.read_csv('../../Data/data_chart.csv')
    data.rename(columns={'Unnamed: 0':'fechas'}, inplace=True)
    x = list(data['fechas'].tolist())
    figure = go.Figure()
    
    for i in range(1, num_topics+1):
        x = x 
        y = list(data[f'Tópico {i}'].tolist())
        figure.add_trace(generate_trace(x, y, COLOR_TEMPLATE[i-1], i)) 

    figure.update_layout(
        showlegend=True,
        xaxis_type='category',
        yaxis=dict(type='linear', range=[1, 100], ticksuffix='%')
    )
    return figure 
    figure.show()

if __name__ == "__main__":
    get_area_chart(num_topics=33)
    