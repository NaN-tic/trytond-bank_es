import csv
import requests
from xlrd import open_workbook

data = requests.get('http://www.bde.es/f/webbde/SGE/regis/ficheros/es/'
    'REGBANESP_CONESTAB_A.XLS')
book = open_workbook(file_contents=data.content)
# We filter by 'bancos, cajas de ahorro, cooperativas de credito, entidades
# de credito comunitarias y extracomunitarias'
bank_types = ['BP', 'CA', 'CC', 'CO', 'EFC', 'OR', 'SECC', 'SECE']
bic_codes = {}

with open('bic.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.reader(f)
    for code in reader:
        bic_codes[code[0]] = code[2]

# The bank info is in the first sheet
sheet = book.sheet_by_index(0)
headers = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]
headers.append('BIC')
with open('bank.csv', 'wt') as f:
    writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore',
        quoting=csv.QUOTE_NONNUMERIC, lineterminator="\n",
        delimiter=',', quotechar='"')
    writer.writeheader()
    for row_index in range(1, sheet.nrows):
        d = {headers[col_index]: sheet.cell(row_index, col_index).value
            for col_index in range(sheet.ncols)}
        if d['COD_TIPO'] in bank_types and d['FCHBAJA'] == '':
            for value in list(d):
                d['BIC'] = None
                if d['COD_BE'] in bic_codes:
                    d['BIC'] = bic_codes[d['COD_BE']]
            if d['TELEFONO'] != '':
                d['TELEFONO'] = '+34' + d['TELEFONO'].lstrip('0')
            if d['NUMFAX'] != '':
                d['NUMFAX'] = '+34' + d['NUMFAX'].lstrip('0')
            writer.writerow(d)
