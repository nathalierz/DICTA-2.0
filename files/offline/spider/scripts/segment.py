import pandas as pd
from difflib import SequenceMatcher
import re
def delete_comma_espace(string):
    name = string
    if string[:2] == ', ':
        name = string.replace(', ', '', 1)
    elif string[0] == ',':
        name = string.replace(',', '', 1)
    if string[-1:] == ',':
        name = string[:-1]
    return name
    
def get_strings_to_ignore():
    ignore = []
    with open('scripts/ignore.txt', 'r') as f:
        lines = f.readlines()
        for p in lines: 
            ignore.append(p.strip('\n'))
    return ignore

def get_participants(text):
    patterns = ['^[A-Z-Á-Ź][A-Z-Á-Ź, A-Z-Á-Ź]*']
    match = re.findall(patterns[0], text)
    ignore = get_strings_to_ignore()
    participantes = []
    for e in match:
        if len(e) > 10:
            e = delete_comma_espace(e)
            if e in ignore:
                e = ''
                continue
            else:
                participantes.append(e)
    return participantes

def segmentation(text, id='', participantes=False):
    size_identifier = len(id) - 1 # Si se debe restar uno a este contador
    size_identifier = size_identifier
    aux_cont = 0
    mayus_char = ''
    copy_flag = False
    new_content = ''
    name_list = []
    name = ''
    personas = []
    
    if participantes != False:
        personas = get_participants(text)
    if id != '' and len(id) >= 2:
        for c in range(len(text)):
                
            if copy_flag == False: 
                if text[c] == id[aux_cont]:
                    mayus_char += text[c]
                    if(aux_cont == size_identifier):
                        copy_flag = True
                        aux_cont = 0
                        new_content += mayus_char[:-1] # Se puede borrar esta linea
                        mayus_char = ''
                    aux_cont += 1
                else:
                    aux_cont = 0
                    mayus_char = ''

            try: # detecta una cadena diferente a la que se pasa por parametro 
                if text[c] == ',' and (text[c+1].isupper() or text[c+1] == ' ') and (text[c+2].isupper() or text[c+2] == None) and (text[c+3].isupper() or text[c+3] == None) and (text[c-1].isupper() == False):# and (text[c+4].isupper() or text[c+4] == None) and (text[c+5].isupper() or text[c+5] == None): 
                    comma = c
                    comma_c = 0
                    capital_c = 0
                    for k in range(8):
                        if (text[c+k].isupper() or text[c+k] == ' ' or text[c+k] == ','):
                            capital_c += 1
                        else:
                            capital_c = 0
                    if capital_c > 7:
                        capital_c = 0
                        copy_flag = False
            except IndexError as error:
                pass
            if copy_flag:
                new_content += text[c]

        new_content = new_content.replace(id, '')

    if participantes == False:
        return new_content
    else:
        return (new_content, personas)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_occurences(name, list_name):
    contador = 0
    for p in list_name:
        ratio = similar(name, p)
        if ratio == 1:
            contador += 1
        if ratio != 1 and ratio > 0.9:
            contador += 1
    return contador

def main():
    pass
if __name__ == '__main__':
    main()
