import os
import sys
import urllib.request
import json
from calendar import monthrange
from datetime import datetime
from multiprocessing.pool import ThreadPool
from clint.textui import progress
MONTHS = []
url_base = "https://ssl.smn.gob.ar/dpd/descarga_opendata.php?file=observaciones/datohorario"
url_list = []

def url_response(url):
    path, url = url
    try:
        with open(path, "wb") as p:
            for line in urllib.request.urlopen(url):
                if "CORRIENTES".encode() in line: 
                    p.write(line)
        p.close()
        print(path, " - Downloaded")
    except:
        print("ERROR - Falla en la conexion con el servidor")
        sys.exit()

now = datetime.now()
dir = str(now.day) + str(now.month) + str(now.year) + "-" + str(now.hour) + str(now.minute)
folders = os.path.join(dir, "samples")
error = False
try:
    if os.stat("fechas.txt").st_size == 0:
        print('ERROR - El archivo fechas.txt esta vacio.')
        sys.exit()
    os.makedirs(folders, exist_ok=True)
    with open("fechas.txt") as ff:
        for line in ff:
            for Month in line.split():
                MONTHS.append(Month)
        for MONTH in MONTHS:
            try: 
                if (len(MONTH) != 8):
                    raise Exception()
            except:
                error = True
                print("ERROR - Las fechas debe tener una estructura de 8 caracteres: DDMMAAAA y estar separadas por 1 espacio")
                sys.exit()
            try: 
                int(MONTH)
            except:
                error = True
                print("ERROR - La lista de fechas debe estar conformada solo por numeros")
                sys.exit()
            year = MONTH[4:]
            month = MONTH[2:4]
            adapted = year + month
            num_days = monthrange(int(year), int(month))[1]
            for i in range(num_days):
                if i + 1 < 10:
                    day = "0" + str(i + 1)
                else:
                    day = str(i + 1)
                full_date = adapted + day + ".txt"
                full_url = url_base + full_date
                path = os.path.join(dir, "samples", full_date)
                if ((path, full_url) not in url_list):
                    url_list.append((path, full_url))

    results = ThreadPool(9).imap_unordered(url_response, url_list)
    for each in results: pass
    average_list = []
    for name_file, url in url_list:
        cont = 0
        average = 0
        with open(name_file, "r") as f:
            for row in f:
                try:
                    (int(row.split()[3]) <= 100)
                    cont+=1
                    average = average + int(row.split()[3])
                except:
                    print("Dia: ", int(row.split()[0]), " no registra valor de humedad")
        f.close()
        date_file = os.path.split(name_file)[-1]
        average_list.append((round(average/cont, 2)))
    os.makedirs(dir, exist_ok=True)
    average_dir = os.path.join(dir, "average.txt")
    with open(average_dir, "w") as a:
        json.dump(average_list, a)
    a.close()

    folder_arduino = "control_leds"
    os.makedirs(os.path.join(dir, folder_arduino), exist_ok=True)
    arduino = os.path.join(dir, folder_arduino, "control_leds.ino")
    final = open(arduino, "w")
    new_line = "double data [] = {" + str(average_list)[1:-1] + "};"
    print("Archivo .ino creado...", end="")
    try:
        with open("data.dat") as file:
            for line in file:
                if "double data" in line:
                    final.write(new_line)
                else:
                    final.write(line)
        final.close()
        print(" OK")
    except:
        print(" FAIL")
        print("ERROR - No se encuentra el archivo data.dat")

    sys.exit()    
except FileNotFoundError:
    print("ERROR - No se encontro el archivo fechas.txt")
    print("Verifique que este mismo se encuentre en la carpeta raiz del programa y que su nombre este correctamente")
else:
    print('Ocurrio un ERROR inesperado')