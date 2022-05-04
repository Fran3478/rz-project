import os
import sys
import urllib.request
import json
import time
import requests
from calendar import monthrange
from datetime import datetime
from multiprocessing.pool import ThreadPool
#TODO: Covertir en .exe
MONTHS = []
url_base = "https://ssl.smn.gob.ar/dpd/descarga_opendata.php?file=observaciones/datohorario"
url_list = []

def testconecction():
    try:
        request = requests.get("http://www.google.com", timeout=5)
    except (requests.ConnectionError, requests.Timeout):
        print("ERROR - No se pudo realizar la coneccion a internet")
        close()
def close():
    input("Presione enter para salir...")
    sys.exit()

def url_response(url):
    path, url = url
    with open(path, "wb") as p:
        for line in urllib.request.urlopen(url):
            if "CORRIENTES".encode() in line: 
                p.write(line)
    p.close()
    print(path, " - Downloaded")

now = datetime.now()
dir = str(now.day) + str(now.month) + str(now.year) + "-" + str(now.hour) + str(now.minute)
folders = os.path.join(dir, "samples")
try:
    if os.stat("fechas.txt").st_size == 0:
        print('ERROR - El archivo fechas.txt esta vacio.')
        close()
    os.makedirs(folders, exist_ok=True)
    with open("fechas.txt") as ff:
        for line in ff:
            if ("#" in line):
                 continue
            for Month in line.split():
                MONTHS.append(Month)
        for MONTH in MONTHS:
            try: 
                if (len(MONTH) != 8):
                    raise Exception()
            except:
                print("ERROR - Las fechas debe tener una estructura de 8 caracteres: DDMMAAAA y estar separadas por 1 espacio o en la siguiente linea")
                close()
            try: 
                int(MONTH)
            except:
                print("ERROR - La lista de fechas debe estar conformada solo por numeros")
                close()
            try:
                format = '%d%m%Y'
                datetime.strptime(MONTH,format)
            except ValueError:
                print("ERROR - La fecha ", MONTH, " tiene un formato invalido")
                close()
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
            
    testconecction()
    results = ThreadPool(9).imap_unordered(url_response, url_list)
    for each in results: pass
    average_list = []
    for name_file, url in url_list:
        cont = 0
        average = 0
        with open(name_file, "r") as f:
            for row in f:
                try:
                    if (int(row.split()[3]) <= 100):
                        cont+=1
                        average = average + int(row.split()[3])
                except:
                    print("Dia: ", int(row.split()[0]), " - ", int(row.split()[1]) ,"hs, no registra valor de humedad")
        f.close()
        date_file = os.path.split(name_file)[-1]
        if average > 0:
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
        close()
    close()    
except FileNotFoundError:
    print("ERROR - No se encontro el archivo fechas.txt")
    print("Verifique que este mismo se encuentre en la carpeta raiz del programa y que su nombre este correctamente")
    close()
else:
    print('Ocurrio un ERROR inesperado')
    close()