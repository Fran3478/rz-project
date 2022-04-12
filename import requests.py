import os

import requests

from time import time

from multiprocessing.pool import ThreadPool

urls = [('20200128.txt', 'https://ssl.smn.gob.ar/dpd/descarga_opendata.php?file=observaciones/datohorario20200128.txt'), ('20200129.txt', 'https://ssl.smn.gob.ar/dpd/descarga_opendata.php?file=observaciones/datohorario20200129.txt'), ('20200130.txt', 'https://ssl.smn.gob.ar/dpd/descarga_opendata.php?file=observaciones/datohorario20200130.txt')]



def url_response(url):

    path, url = url

    r = requests.get(url, stream = True)

    with open(path, 'wb') as f:

        for ch in r:

            f.write(ch)

start = time()

for x in urls:

    url_response (x)

print(f"Time to download: {time() - start}")