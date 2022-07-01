import re
import nltk
import sys
import spacy
import gensim
import psycopg2
import pandas as pd
from nltk.corpus import stopwords
from gensim.test.utils import datapath
from nltk.tokenize import RegexpTokenizer
from gensim.corpora.dictionary import Dictionary
from gensim.models import CoherenceModel

temp_file = datapath('LDA_MODEL')

PASSWORD = 'jk2bj6VbAz#'
USER = 'larias'
BD = 'pt_larias'
ID = 1 # Nuevo ID de presidente
  
SUSTANTIVOS_PATH = '../../../Data/nouns.txt'

def get_nouns(text):
    nlp=spacy.load('es_core_news_sm')
    nouns = [w.text for w in nlp(text) if w.is_stop!=True and w.is_punct != True and w.pos_ == 'NOUN']
    stop_words = list(set(stopwords.words('spanish')))
    lista = [ i for i in nouns if i not in stop_words]
    return lista

def get_data_from_db(): 
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(user=USER, host='127.0.0.1', database=BD, password=PASSWORD)
        cursor = conn.cursor()
        result = cursor.execute(f'select fecha, transcripcion from conferencia where id_ponente = {ID};')
        records = cursor.fetchall()
        df = pd.DataFrame(records, columns=['Fecha', 'Transcripción'])
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    conn.close()
    return df

def get_corpus():
    print("Getting data...", end=' ')
    data = get_data_from_db()
    print('Done!')
    transcriptions = []
    tokenizer = RegexpTokenizer(r'\w+')
    print('(Corpus): Getting nouns...', end=' ')
    for i in range(data.shape[0]):
        df = data.iloc[[i]]
        string_transcription = ' '.join(get_nouns( df.iloc[0]['Transcripción'] ))
        transcriptions.append(string_transcription)
        string_transcription = ''
    print('Done!')
    f  = open(SUSTANTIVOS_PATH, 'w') #------------------
    print("(Corpus):Creating file...", end=' ')
    for e in transcriptions:
        string = e.lower()
        string = re.sub(r'\d+', '', string)
        aux = tokenizer.tokenize(string)
        f.write(' '.join(aux))
        f.write('\n')
    f.close()
    print('Done!')
    print("(Corpus): Corpus generado.")

def train_lda():
    documents = []
    print("(LDA): Training...", end=' ' )
    with open(SUSTANTIVOS_PATH, 'r') as f:
        lines = f.readlines()
        for p in lines:
            documents.append(p.strip('\n'))
    texts = [document.split() for document in documents]
    dictionary = Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts] #** lista de pares (idt, ft)
    for (token, uid) in dictionary.token2id.items():
        dictionary.id2token[uid] = token
    lda_model = gensim.models.LdaModel(corpus=corpus, 
        id2word=dictionary,
        num_topics=33,
        chunksize=10,
        iterations=5,
        alpha='auto',
        eta='auto',
        passes=50,
        random_state=100,
    )
    lda_model.save(temp_file)
    print('Done!')


if __name__ == "__main__":
    if sys.argv[1] == '-g':
        get_corpus()
        train_lda()
    if sys.argv == '-t':
        train_lda()
