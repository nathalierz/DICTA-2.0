# Dicta
Este documento contiene las instrucciones para la construcción de la aplicación denominada Dicta.

### Preliminares

Esta aplicación se desarrollo usando Ubuntu 18.04 (las instrucciones contenidas en este documento funcionan de igual manera para Ubuntu 20.04).

Para que la aplicación puede funcionar correctamente es necesario utilizar una versión de Python >3.7 Además de la instalación de Java >11 para poder utilizar la plataforma PyTerrier y tener conconfigurada la variable de entorno JAVA_HOME.

### 1. Creación de un entorno virtual

Para crear un entorno virtual primero es necesario instalar `virtualenv`.  Para realizar esta instalación es necesario utilizar el siguiente comando:

    $ pip3 install virtualenv
 Una vez instalado podemos proceder a crear el entorno virtual con el siguiente comando:

    $ virtualenv DictaEnv
El comando anterior creará un entorno virtual llamado `DictaEnv` (es recomendable que este entorno sea creado dentro del directorio `Dicta`). Para activarlo podemos utilizar el siguiente comando:

    $ source DictaEnv/bin/activate

### 2. Instalación de dependencias

Para realizar la instalación de las múltiples dependencias es necesario utilizar el siguiente comando sobre el archivo `requirements.txt`.

    $ pip3 install -r requirements.txt
Una vez instaladas las múltiples librerías utilizadas por la aplicación, procederemos a instalar algunos otros paquetes de determinadas librerías. El primero de ellos es `es_core_news_sm`. Para instalarlo es necesario introducir el siguiente comando:

    $ python -m spacy download es_core_news_sm
Para el segundo y tercer paquete es necesario iniciar un interprete de Python desde la terminal.

    $ python

Después, introducimos lo siguiente:

    >>> import nltk
    >>> nltk.download('stopwords')
    >>> nltk.download('punkt')

Así, todas las dependencias estarán instaladas.

### 3. Creación de la base datos
Para realizar realizar este paso tendremos que restaurar el backup del archivo `dicta_database_v2.sql`. El primer paso para la restauración es abrir una terminal e introducir el siguiente comando:

    $ sudo -i -u postgres

Ingresamos la contraseña que nos solicita.

Para realizar la restauración necesitaremos importar el archivo donde se encuentra guardada la base de datos con el nombre `pt_larias`(se llamó así debido a que cuando se creó la base de datos la aplicación aún no tenía un nombre asignado). Antes de acceder a la consola de postgres se eingresa el siguiente comando donde incluye el archivo desde donde se crea la base de datos y hace la importación de los datos.

    $ psql < dicta_database_v2.sql

### 4. Preparaciones finales para la construcción de la aplicación
Lo primero que se debe de hacer en este apartado es el entrenamiento del modelo utilizado para la detección de tópicos. Para realizar este paso es necesario ejecutar el script denominado `train_model.py`, que está dentro del directorio `.../files/offline/train_model/train_model.py`. Se puede utilizar el siguiente comando:

    $ python train_model.py -g

Además, también es necesario ejecutar el archivo que está dentro del directorio `.../files/offline/generate_data_chart/data_chart_generator.py`.

    $ python data_chart_generator.py -g

Para la creación de base documental para la recuperación de información también es necesario ejecutar el archivo que está dentro del directorio `.../files/offline/generate_data_chart/document_indexing.py`.

    $ python document_indexing.py

Una vez hecho esto, la aplicación estará construida, para ejecutarla es necesario situarse dentro del directorio `.../files/online/`. Una vez dentro de este directorio, se ejecuta el siguiente comando:

    $ streamlit run Dicta.py

**IMPORTANTE**: Para que la aplicación trabaje con datos actualizados es necesario la ejecución periódica de algunos scripts. Para realizar estas tareas periódicas es necesario configurarlas dentro de crontab. Para realizar esto primero debemos de abrir una terminal y teclear:

    $ crontab -e

Si es la primera vez que se ejecuta crontab, entonces solicitará que se le indique un editor de textos para poder trabajar. Simplemente, hay que indicar el número del editor más cómodo para nosotros (sugiero utilizar la primera opción que corresponde con el editor nano) y posteriormente, mostrará el contenido del archivo y al final tendremos que poner las tres configuraciones siguientes:

    0 0 * * 6 /usr/bin/python3 .../offline/train_model/train_model.py -t
    30 14 * * 1-5 /usr/bin/python3 .../offline/spider/spider.py
    35 14 * * 1-5 /usr/bin/python3 .../offline/generate_data_chart/data_chart_generator.py -s
    0 15 * * 1-5 /usr/bin/python3 .../offline/generate_data_chart/document_indexing.py

El intérprete de Python que debe de ser configurado en crontab es el del entorno virtual, ya que en ese entorno se instalaron las dependencias de la aplicación. La ruta de este intérprete es:

    .../DictaEnv/bin/python
Por lo que se tendría que reemplazar `/usr/bin/python3` por `.../DictaEnv/bin/python`. Esto en caso de que si se realizó la instalación de dependencias dentro de un entorno virtual. Si no fue el caso, entonces no hay reemplazar nada.

Las rutas de los archivos, así como la del intérprete, deben de ser **absolutas** (no relativas). Por lo que es necesario complementarlas de acuerdo al directorio en donde se coloquen estos archivos.
