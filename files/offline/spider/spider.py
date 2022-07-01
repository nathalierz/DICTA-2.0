import os
import datetime
from random import choice
from scrapy.item import Field, Item
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose 
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess
from pandas import read_csv
from os import remove
from conferenciaDB import get_nombres, insert_conferencia, insert_ponente, insert_conferencia_completa
from scripts.ponentes import get_ponentes, validate_entity
from scripts.segment import similar
from scripts.utils import format_date
from gensim.corpora.dictionary import Dictionary
# Este archivo requiere ejecución diaria de lunes a viernes

class Transcripcion(Item):
    
    fecha = Field()
    transcripcion = Field()

class TranscripcionSpider(Spider):
    name = 'SpiderTranscript'

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
        'LOG_ENABLED': False
    }

    allowed_domains = ['lopezobrador.org.mx']
 
    today = str(datetime.date.today()).replace('-','/')

    url = 'https://lopezobrador.org.mx/' + today + '/version-estenografica-de-la-conferencia' #-de-prensa-matutina-del-presidente-'
    start_urls = [url]

    def clean_data(self, text):
        output = text.replace('+', '').replace('–','').replace(u'\xa0', '').replace('\n', '').replace('\r', '').replace('-', '')
        return output

    def parse(self, response):
        sel = Selector(response)
        item = ItemLoader(Transcripcion(), sel)
        item.add_xpath('fecha', '//div[@class="tw-meta"]//span[@class="entry-date"]/a/text()')
        item.add_xpath('transcripcion', '//div[@class="single-padding"]//div[@class="entry-content"]//*/text()', MapCompose(self.clean_data))
        yield item.load_item()

if __name__ == "__main__":

    if datetime.date.today().weekday() == 5 or datetime.date.today().weekday() == 6 :
        exit()
    else:
        
        user_agents_list = [
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0', # Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',#Chrome
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/69.0.3686.49',#Opera
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58'#edge
        ]

        today = str(datetime.date.today().strftime('%d-%m-%Y'))
        output_file_path = '../../../Data/' + today + '.csv'
                
        user_agent = choice(user_agents_list)
        process = CrawlerProcess(
            settings={
                "FEEDS":{
                    output_file_path: {
                        'format': 'csv'
                    }
                },
                "USER_AGENT": user_agent
            }
        )
        process.crawl(TranscripcionSpider)
        process.start()

        df = read_csv(output_file_path, sep=',')
        remove(output_file_path)
        # Cargando datos a la base de datos
        # Para insertar la conferencia completa
        transcripcion_complet = (df.iloc[0]['transcripcion'])
        fecha = format_date(df.iloc[0]['fecha'])
        insert_conferencia_completa(fecha, transcripcion_complet)
        nombres_db = get_nombres()
        ponentes_csv = get_ponentes(df)

        for e in ponentes_csv:  # Para insertar en ponente
            if validate_entity(e.nombre) and len(e.content)>=5:
                flag = False
                for i in nombres_db:
                    ratio = similar(i[1], e.nombre)
                    if ratio > 0.75:
                        flag=True
                if flag == False:
                    insert_ponente(e.nombre)
            else:
                print(e.nombre+ "  no válido")
                print("******")
        nombres_db = get_nombres()

        for e in ponentes_csv:  # Para insertar en conferencia
            for j in nombres_db:
                ratio = similar(j[1], e.nombre)
                if ratio > 0.75:
                    if len(e.content)>=5: # Condición para no insertar contendido vacio
                        insert_conferencia(e.content, j[0], e.fecha) #conferenciaDB
                    else:
                        print("No es posible insertar con " +e.nombre)
                        print("----------")


