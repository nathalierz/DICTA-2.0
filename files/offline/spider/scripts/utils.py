def format_month(month):
    meses = [
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ]
    mes = 0
    for i in range(len(meses)):
        if month == meses[i]:
            mes = str(i + 1)
            break
    return mes

def format_date(date):
    new_date = ''
    month = ''
    day = ''
    flag = False
    for i in range(len(date)-1):
        if date[i] != ' ' and flag == False:
            month += date[i]
        else:
            break
    date = date[len(month):].replace(' ', '')
    for i in range(len(date)-1):
        if date[i] !=',':
            day += date[i]
        else:
            break
    year = date[len(day):].replace(',', '')
    month = format_month(month)
    date = year + '-' + month + '-' +day
    return date

