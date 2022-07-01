import re
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer 
from gensim.test.utils import datapath
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel
# from gensim.models.ldamulticore import LdaMulticore
from data_extractor import get_transcription_training

nlp=spacy.load('es_core_news_sm')
temp_file = datapath('LDA_MODEL') # Default model

DOC_PATH = '../../Data/nouns.txt'

def train_model_session(topics):
    documents = []
    print("Obtención del archivo del corpus")
    with open(DOC_PATH, 'r') as f:
        lines = f.readlines()
        for p in lines:
            documents.append(p.strip('\n'))
    texts = [document.split() for document in documents]
    dictionary = Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    print("Representación de término, frecuencia")
    for (token, uid) in dictionary.token2id.items():
        dictionary.id2token[uid] = token
    print(dictionary)

    lda_model = LdaModel(corpus=corpus, 
        id2word=dictionary,
        num_topics=topics,
        chunksize=10,
        iterations=5,
        alpha='auto',
        eta='auto',
        passes=50,
        random_state=100,
    )
    return lda_model

def train_default_model():
    documents = []
    with open(DOC_PATH, 'r') as f:
        lines = f.readlines()
        for p in lines:
            documents.append(p.strip('\n'))
    texts = [document.split() for document in documents]
    dictionary = Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    for (token, uid) in dictionary.token2id.items():
        dictionary.id2token[uid] = token

    lda_model = LdaModel(corpus=corpus, 
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

if __name__ == "__main__":
    train_default_model(33) #TODO: Este script debera ejecutarse cada sabado, por lo que hay que configurarlo en crontab 
    
