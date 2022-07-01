import pyterrier as pt
import pandas as pd
import os
import nltk
from nltk.stem import SnowballStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
from data_extractor import get_document_complet, get_speakers

if not pt.started():
    pt.init()

def retrive_documents(query):
	index_ref = pt.IndexRef.of('../offline/generate_data_chart/index_completo/data.properties')
	index = pt.IndexFactory.of(index_ref)
	DFRee =pt.BatchRetrieve(index, num_results=50, wmodel="DFRee", verbose=True)
	r = DFRee.search(query)
	documents = pd.DataFrame(columns=['Fecha', 'Transcripción'])
	
	for ind, row in r.iterrows():
		document = get_document_complet(row["docno"])
		documents = documents.append(document, ignore_index=True)
	return documents

def documents_whit_ponentes(documents, lista_ponentes):
	id_documents = []
	for index, row in documents.iterrows():
		date = documents.loc[index, 'Fecha']
		ponentes = get_speakers(date)
		for i, row in ponentes.iterrows():
			if ponentes.loc[i,"Nombre"] in lista_ponentes:
				if documents.loc[index, 'Fecha'] not in id_documents:
					id_documents.append(documents.loc[index, 'Fecha'])
	return id_documents


