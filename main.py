import os
from calendar import monthrange
from datetime import datetime
import requests
from multiprocessing.pool import ThreadPool
from clint.textui import progress
MONTHS = ["08/2021", "09/2020"]
url_base = "https://ssl.smn.gob.ar/dpd/descarga_opendata.php?file=observaciones/datohorario"
url_list = []

def url_response(url):
    path, url = url
    r = requests.get(url, stream = True)
    with open(path, 'wb') as f:
        for ch in r:
            f.write(ch)
        f.close()
        print(path, ' - Downloaded')

now = datetime.now()
dir = str(now.day) + str(now.month) + str(now.year) + '-' + str(now.hour) + str(now.minute)
os.mkdir(dir)
for MONTH in MONTHS:
    year = MONTH.split('/')[1]
    month = MONTH.split('/')[0]
    adapted = year + month
    num_days = monthrange(int(year), int(month))[1]
    for i in range(num_days):
        if i + 1 < 10:
            day = '0' + str(i + 1)
        else:
            day = str(i + 1)
        full_date = adapted + day + ".txt"
        full_url = url_base + full_date
        path = dir + '\\' + full_date
        url_list.append((path, full_url))

results = ThreadPool(9).imap_unordered(url_response, url_list)
for each in results: pass