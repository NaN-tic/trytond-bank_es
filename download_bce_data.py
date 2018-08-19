import csv
import tempfile

import urllib.request, urllib.parse, urllib.error
from xlrd import open_workbook

urlfile = urllib.request.URLopener()
with tempfile.NamedTemporaryFile() as banks:
    urlfile.retrieve('http://www.bde.es/f/webbde/SGE/regis/ficheros/es/'
        'REGBANESP_CONESTAB_A.XLS', banks.name)
    book = open_workbook(banks.name)
    # We filter by 'bancos, cajas de ahorro, cooperativas de credito, entidades
    # de credito comunitarias y extracomunitarias'
    bank_types = ['BP', 'CA', 'CC', 'CO', 'EFC', 'OR', 'SECC', 'SECE']
    bic_codes = {}

    with open('bic.csv', 'rt') as bic:
        reader = csv.reader(bic, delimiter=',')
        for code in reader:
            bic_codes[code[0]] = code[2]
    # The bank info is in the first sheet
    sheet = book.sheet_by_index(0)
    headers = [sheet.cell(0, col_index).value
        for col_index in range(sheet.ncols)]
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
                        # Encode all the values to prevent an import crash
                        d[value] = d[value].encode('utf-8')
                        d['BIC'] = None
                        if d['COD_BE'] in bic_codes:
                            d['BIC'] = bic_codes[d['COD_BE']]
                    writer.writerow(d)
