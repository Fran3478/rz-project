import os
import urllib.request
import json
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
    with open(path, "wb") as f:
        for line in urllib.request.urlopen(url):
            if "CORRIENTES".encode() in line: 
                f.write(line)
    f.close()
    print(path, " - Downloaded")

now = datetime.now()
dir = str(now.day) + str(now.month) + str(now.year) + "-" + str(now.hour) + str(now.minute)
folders = os.path.join(dir, "samples")
os.makedirs(folders, exist_ok=True)
for MONTH in MONTHS:
    year = MONTH.split("/")[1]
    month = MONTH.split("/")[0]
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
        url_list.append((path, full_url))

results = ThreadPool(9).imap_unordered(url_response, url_list)
for each in results: pass
average_list = []
for name_file, url in url_list:
    cont = 0
    average = 0
    with open(name_file, "r") as f:
        for row in f:
            cont+=1
            average = average + int(row.split()[3])
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
with open("data.dat") as file:
    for line in file:
        if "double data" in line:
            final.write(new_line)
        else:
            final.write(line)
final.close()