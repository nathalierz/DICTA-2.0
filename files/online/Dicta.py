from datetime import date
import gensim
import matplotlib.pyplot as plt
import nltk
import numpy as np
import pandas as pd
import spacy
import streamlit as st
from gensim.corpora.dictionary import Dictionary
from gensim.test.utils import datapath
from nltk import FreqDist
from PIL import Image
import time
import streamlit.components.v1
from retrive_docs import retrive_documents, documents_whit_ponentes # un módulo nuevo
import pandas as pd


from data_extractor import (get_last_date_stored, get_speakers,
                            get_transcription, get_transcriptions, is_stored, get_ponentes)
from data_processor import (COLOR_TEMPLATE, get_nouns_from_document,
                            string_and_tuples, topic_tuples,
                            get_area_chart, search_tuples, string_and_tuples_s) #dos modulos nuevos
from model_training import train_model_session
from tagger import annotated_text

nlp=spacy.load('es_core_news_sm')


def set_model(model):
    global lda_model
    lda_model = model

def get_vector(distribution):
    vector = [e[1] for e in distribution]
    return vector

def LDA_docs_representation(dictionary, documents):
    document_distribution_vector = []
    for (i, doc) in enumerate(documents):
        document_distribution_vector.append(get_vector(lda_model[dictionary[i]]))
    return np.array(document_distribution_vector)

def get_doc_topics(corpus):
    topics = [sorted(e, key=lambda topic: topic[1], reverse=True) for e in lda_model.get_document_topics(corpus)]
    topic_list = []
    color_iter = 0
    for e in topics: 
        for i in e:
            terms = lda_model.show_topic(i[0], topn=15)
            topic_terms = [j[0] for j in terms]
            st.markdown(f'<p style="background-color: {COLOR_TEMPLATE[color_iter]}; border-radius: 5px; text-align:center" >Tópico: {i[0]}</p>', unsafe_allow_html=True)
            st.markdown(", ".join(topic_terms))
            topic_list.append(topic_terms)
            color_iter+=1
    x = [x[0] for x in topics[0]]
    y = [y[1] for y in topics[0]]
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.bar(x, y, color=COLOR_TEMPLATE)
    ax.set_title('Presencia de cada tópico en la conferencia.', fontweight='bold')
    ax.set_ylabel('Presencia')
    ax.set_xlabel('Tópicos')
    
    st.pyplot(fig)
    return topic_list

def get_most_freq_terms(doc, top=15):
    doc_tok = [w.text for w in nlp(doc) if w.is_stop!=True and w.is_punct != True and (w.pos_ == 'NOUN' or w.pos_== 'VERB') ]
    freqDist = FreqDist(doc_tok)
    terms_top = freqDist.most_common(top)
    x = [x[0] for x in terms_top]
    y = [y[1] for y in terms_top]
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    ax.bar(x, y)
    ax.set_title('Frecuencia de palabras en la conferencia.', fontweight='bold')
    ax.set_ylabel('Frecuencia')
    ax.set_xlabel('Palabras')
    ax.tick_params(axis='x', labelrotation=90)
    st.pyplot(fig)

def display_topics_conference(conference_ui, topics):
    topics = topic_tuples(topics)
    formated_document = string_and_tuples(conference_ui, topics)
    st.markdown('### **Transcripción:**')
    annotated_text(*formated_document)

def display_transcription_elements(conference_ui, corpus, fecha):
    load_state = st.text('Generando vizualización...')
    st.markdown(f'## **Tópicos en la conferencia del dia: {fecha}**')
    load_state.text('Generando vizualización...Hecho!!!')
    topics = get_doc_topics(corpus)          # Muestra los topicos en forma de lista y grafica los topicos de acuerdo a su nivel de presencia en la conferencia
    display_topics_conference(conference_ui, topics)    # Muestra los topicos de la conferencia con colores en el texto
    get_most_freq_terms(conference_ui, top=35)          # Muestra la grafica con los terminos con mas frecuencia
    st.markdown(f'### Participantes en la conferencia del dia {fecha} :')
    df_participant = get_speakers(fecha)            # Muestra los participantes
    st.table(df_participant)
    st.write('')

def individual_conference(fecha):
    load_state = st.text("Cargando datos de la conferencia...")
    df = get_transcription(fecha)
    load_state.text("Cargando conferencia...Hecho!!")
    load_state = st.text('Procesando Conferencia...')
    document_list = [get_nouns_from_document(df.iloc[0]['Transcripción'])]
    dictionary = Dictionary(document_list)
    corpus = [dictionary.doc2bow(text) for text in document_list]
    load_state.text('Procesando Conferencia...Hecho!!!')
    display_transcription_elements(df.iloc[0]['Transcripción'], corpus, df.iloc[0]['Fecha'])

def multiple_conference(initial_date, final_date):
    state_load = st.text("Cargando conferencias...")
    data, transcripciones = get_transcriptions(initial_date, final_date)
    state_load.text("Cargando conferencias...Hecho!!")
    fechas = []
    for i in range(data.shape[0]):
        df = data.iloc[[i]]
        fechas.append(str(df.iloc[0]['Fecha'])) 
    document_list = [get_nouns_from_document(d) for d in transcripciones]
    dictionary = Dictionary(document_list)
    corpus = [dictionary.doc2bow(text) for text in document_list]
    # document_vector = LDA_docs_representation(corpus, lda_model, document_list)# Topic tracking
    datos = []
    for f, i, k in zip(fechas, corpus, transcripciones):
        l = k.replace(':', '').replace(',,', '. ').replace('.,,', '. ').replace('..,','. ').replace('..','. ')
        datos.append((f, i, l.strip(', ')))
    st.markdown('### **Transcripciones:**')
    st.markdown('')
    w=0
    for i in datos:
        topics = lda_model.get_document_topics(i[1])
        max_topic_pert = 0.0
        max_topic = None
        for index, topic in enumerate(topics):
            if topic[1] > max_topic_pert:
                max_topic_pert = topic[1]
                max_topic = topic
        with st.container():
            st.markdown(f'**Fecha: {i[0]}**')
            st.markdown('Tópico con más presencia en la conferencia:')
            annotated_text((f'Tópico: {max_topic[0]}', f'{max_topic[1]}', COLOR_TEMPLATE[w] ), height_iframe=40)
            a = [j[0] for j in lda_model.show_topic(max_topic[0])]
            st.markdown(', '.join(a))
            if st.button('Analizar conferencia.', key= str(i[0])):
                display_transcription_elements(i[2], [i[1]], i[0])
            st.markdown('**----------------------------------------------------------------------------------------------------------------**')
        w+=1
#----------------------------

def page_configuration():
    top_image = Image.open('resources/img/log_n.bmp.png')
    st.set_page_config(
    
         page_title='Dicta',
         page_icon='resources/img/favicon/favicon-ico.ico',
         layout='centered'
    )
    st.image(top_image, use_column_width=True)

def dispĺay_main_content():
    # Main Content
    st.markdown('# **DICTA**')
    st.markdown('**Introducción.**')
    st.markdown(
    '''
    Esta herramienta tiene como objetivo el análisis de las transcripciones estenográficas de las conferencias de prensa matutinas del actual Presidente de México, Andrés Manuel López Obrador.
    Este análisis, permite por un lado la obtención de distintos tópicos que son discutidos a lo largo de cada conferencia de prensa.
    Por otro lado, recupera una serie de conferencias relevantes a través de una consulta de información tomando en cuenta todas las conferencias desde la fecha de inicio hasta la fecha actual.
	'''
    )
 
def model_configuration(num_topics=15, new_instance=False): 
    lda = None
    if new_instance == False:
        lda = gensim.models.LdaModel.load(datapath('LDA_MODEL'))
    else:
        training_state = st.text('Entrenando modelo...')
        lda = train_model_session(num_topics)
        training_state.text('Entrenando modelo... Hecho!')
    set_model(lda)

# RI ---------------------
def display_result(texto, date, ponentes, query, key):
    f = str(date).replace('-', '/')
    f2 = date.strftime('%d-%m-%Y')
    f3 = str(f2).replace('-', '/')
    title = "Posición "+str(key)+": Transcripción de la conferencia de prensa matutina del presidente Andrés Manuel López Obrador del día "+str(f3)+"."
    with st.container():
        with st.expander(title, expanded=False):
            url = 'https://lopezobrador.org.mx/' + f + '/version-estenografica-de-la-conferencia' #-de-prensa-matutina-del-presidente-'
            components = search_tuples(ponentes, query)
            format_t = string_and_tuples_s(texto, components)
            annotated_text(*format_t)
            st.write("Tambien puedes consultar la transcripción en el siguiente [Sitio]("+url+")")

def box_result(documents, ponentes, query):
    for index, row in documents.iterrows():
        date = documents.loc[index, 'Fecha']
        texto = documents.loc[index, 'Transcripción']
        display_result(texto, date,ponentes, query, index+1)

def display_simple_search(ponentes,query):
    if query != "":
        with st.spinner("Buscando .."):
            documents = retrive_documents(query)
            st.session_state.buscar = True
            if documents.empty:
                st.error("No se encontraron resultados para: "+query+".")
            else:
                st.markdown("#### A continuación se enlistan las conferencias en las que puedes encontrar información acerca de:  "+query+".")

                if st.session_state.buscar:
                    box_result(documents, ponentes, query)
                st.success("Listo!")

def display_search(query, lista_ponentes):
    if query != "":
        with st.spinner("Buscando .."):
            print("Buscando")
            documents = retrive_documents(query)
            id_doc = documents_whit_ponentes(documents, lista_ponentes) #lista de fechas
            st.session_state.buscar = True

            if id_doc == []:
                st.error("No se encontraron resultados para: '"+query+"'' con los ponentes seleccionados.")
            else:
                st.markdown("#### A continuación se enlistan las conferencias en las que puedes encontrar información acerca de:  "+query+".")
                
                documents_ponentes = pd.DataFrame(columns=['Fecha', 'Transcripción'])

                for date in id_doc: # obtiene un dataframe
                    v = documents.loc[:,'Fecha'] == date
                    doc = documents.loc[v]
                    documents_ponentes = documents_ponentes.append(doc, ignore_index=False)

                if st.session_state.buscar:
                    lista_ponentes.append("PRESIDENTE ANDRÉS MANUEL LÓPEZ OBRADOR")
                    box_result(documents_ponentes, lista_ponentes, query)
                    st.session_state.buscar = False
                st.success("Listo!")
def clean():
    st.session_state['ponente'] = []
    st.session_state['lista_ponentes'] = get_ponentes()
    st.session_state.lista_ponentes = st.session_state.lista_ponentes.drop(0)

#--------------------------------
def display_sidebar_content():
    
    st.sidebar.header("Herramientas")
    action = st.sidebar.radio("Elija la acción a realizar", ("Búsqueda de tópicos", "Búsqueda en transcripciones"), index=1)
    if "buscar" not in st.session_state:
        st.session_state["buscar"] = False
    if action == "Búsqueda de tópicos":
        st.markdown('**Indicaciones**')
        st.markdown('Para realizar el análisis de las conferencias puedes indicar la fecha de una conferencia en particular, o bien, puedes indicar dos fechas una inicial y una final para poder realizar el análisis de múltiples conferencias dentro de un rango especifico.')
        st.markdown("Únicamente puedes seleccionar fechas de conferencias que tienen lugar de **lunes a viernes**.")
        st.markdown('Por defecto, la aplicación esta configurada para encontrar 33 tópicos dentro de las transcripciones. Si deseas cambiar esto puedes indicarlo en el menu deslizante de la izquierda. Ten en cuenta que este proceso puede demorar **varios minutos**.')
        #st.sidebar.subheader("Aqui se realizan las acciones de tópicos")
        custom_model_opt = st.sidebar.radio('¿Deseas analizar un determinado número de tópicos?', ('No', 'Si'))
        num_topics = 0
        if custom_model_opt == 'Si':
            num_topics = st.sidebar.number_input('Indica cuántos tópicos deseas analizar.', min_value=2, max_value=33)
            model_configuration(num_topics=num_topics, new_instance=True)
        else:
            num_topics = 33
            model_configuration(new_instance=False)
        
        # Carga de la grafica inicial
        topic_distribution_state = st.text('Obteniendo distribucion de los tópicos...')
        st.markdown("## **Evolución de los tópicos a través del tiempo.**")
        figure = get_area_chart(num_topics, lda_model, custom_model_opt)
        st.plotly_chart(figure)
        topic_distribution_state.text('Obteniendo distribución de los tópicos... Hecho!')

        #--- Hasta este punto se muestra información inicial
        
        # Sidebar Content
        conference_type = st.sidebar.radio('¿Qué tipo de conferencia deseas analizar?', ('Individual', 'Múltiple'))
        max_date = get_last_date_stored()
        print("fecha de ultima conferencia.......")
        print(max_date) 
        if conference_type == 'Individual':
            conference_date = st.sidebar.date_input('Ingresa la fecha de una de las conferencias.', 
                min_value=date(2018, 12, 4), 
                max_value=max_date,
                value=max_date
            )
            if conference_date.weekday() == 5 or conference_date.weekday() == 6:
                st.sidebar.warning('Elige una fecha que no corresponda con un sábado o domingo.')
                st.stop()
            if is_stored(str(conference_date)) == False:
                st.sidebar.warning('No hay registro de una conferencia en la fecha indicada, probablemente fue un dia festivo.')
                st.stop()
            individual_conference(str(conference_date))
        else:
            first_date = st.sidebar.date_input('Ingresa una fecha de inicio:', min_value=date(2018, 12, 4), max_value=max_date )
            if first_date.weekday() == 5 or first_date.weekday() == 6:
                st.sidebar.warning('Elige una fecha que no corresponda con un sábado o domingo.')
                st.stop()
            last_date = st.sidebar.date_input('Ingresa una fecha final:', min_value=first_date, max_value=max_date )
            if last_date.weekday() == 5 or last_date.weekday() == 6:
                st.sidebar.warning('Elige una fecha que no corresponda con un sábado o domingo.')
                st.stop()
            if first_date > last_date:
                st.sidebar.warning('La fecha de inicio que indicaste esta despues de la fecha final.')
                st.stop()
            multiple_conference(str(first_date), str(last_date))
    else:
        
        text1 = "<span style=color:purple;> morado </span>"
        text2 = "<span style=color:green;> verde </span>"
        st.markdown('**--- Indicaciones ---**')
        st.markdown('Para realizar la recuperación de información solo debes seguir los **PASOS** que se indican en la selección izquierda. La búsqueda se realizará de acuerdo a las conferencias desde su **fecha de inicio** 4 de diciembre de 2018 hasta la **fecha actual**, tomando en cuenta **sólo las conferencias de lunes a viernes**.')
        st.markdown("Podrá realizar una búsqueda general dentro de todas las conferencias completas y obtener los **primeros 50 mejores resultados** de acuerdo a su consulta, mostrándose en un **orden por relevancia**. También puede configurar la herramienta para indicar si desea que algunos de los ponentes participantes se encuentren dentro de los resultados obtenidos. Esto permitirá un filtrado de conferencias y mostrará un número menor de resultados para hacer más ágil su búsqueda.")
        st.markdown("Cada resultado indica la **Posición de Relevancia** de la conferencia obtenida junto con la fecha de  dicha conferencia. Incluye el contenido total de la conferencia resaltando en color **"+text1+"** los nombres de los **ponentes participantes** sobre los que se realiza la búsqueda, y de color**"+text2+"**, partes del documento que incluye **palabras de la consulta realizada**.", unsafe_allow_html=True)
        st.markdown("Puede realizar su búsqueda una vez ingresada la consulta y posteriormente presionando el botón de **BUSCAR**. Esto puede tardar unos segundos.")
        st.sidebar.warning("PASO 1: Escribe tu consulta")
        consulta = st.sidebar.text_input("Escribe la consulta que deseas realizar")
        
        st.sidebar.info("Por defecto, en todas las conferencias encontrarás a PRESIDENTE ANDRÉS MANUEL LÓPEZ OBRADOR")
        selection = st.sidebar.radio("¿Deseas especificar el nombre de algún otro ponente que participe en la conferencia?", ("No", "Si"), index=0)
        if selection == "No":
            st.session_state.buscar = False
            if consulta != "":
                st.sidebar.success("ADELANTE. Puedes realizar tu búsqueda con el botón de BUSCAR")
                print("busqueda normal")
                if st.sidebar.button("BUSCAR") or st.session_state.buscar:
                    st.session_state.buscar = True
                    print("entra a buscar...")
                    display_simple_search(["PRESIDENTE ANDRÉS MANUEL LÓPEZ OBRADOR"], consulta)

            clean()

        else:
            print("busqueda con ponentes")
            if 'ponente' not in st.session_state:
                st.session_state['ponente'] = []
            if 'lista_ponentes' not in st.session_state:
                st.session_state['lista_ponentes'] = get_ponentes()
                st.session_state.lista_ponentes = st.session_state.lista_ponentes.drop(0)

            st.sidebar.warning("PASO 2: Elije el nombre del ponente")
            ponente = st.sidebar.selectbox("Escriba el nombre del ponente ", st.session_state.lista_ponentes.loc[:, "Nombre"], key=st.session_state.lista_ponentes.loc[:, "Nombre"], help="Puede escribir o seleccionar el nombre del ponente")

            st.sidebar.info("Una vez seleccionado el nombre del ponente, presiona el botón de AGREGAR PONENTE.")
            if st.sidebar.button("AGREGAR PONENTE") and selection == "Si":
                st.session_state.ponente.append(ponente)
                elimina = st.session_state.lista_ponentes[st.session_state.lista_ponentes['Nombre'] == ponente].index
                st.session_state.lista_ponentes = st.session_state.lista_ponentes.drop(elimina)
            st.sidebar.warning("PASO 3: Confirma tu selección")
            p = st.sidebar.multiselect(
                'Buscar con:',
                options= st.session_state.ponente,
                default= st.session_state.ponente,
                help = "De las opciones preseleccionadas puede eliminar o volver a mantener las opciones."
                )
            st.sidebar.info("Al terminar de seleccionar tus opciones, presiona el botón de BUSCAR. Si deseas agregar más ponentes, vuelve a seleccionar el el PASO 2 ")

            st.session_state.buscar = False
            if st.session_state.ponente != [] and p!=[]:
                if st.sidebar.button("BUSCAR")  or st.session_state.buscar:
                    st.session_state.buscar = True
                    display_search(consulta, p)
            else:
                st.sidebar.error("Debe seleccionar algún ponente para realizar su búsqueda.")


def gui_content():
    page_configuration()
    dispĺay_main_content()
    display_sidebar_content()

if __name__ == '__main__':
    gui_content()
