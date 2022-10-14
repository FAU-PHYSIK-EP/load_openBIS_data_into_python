# -*- coding: utf-8 -*-
"""
Created on 29.03.2022, update on 14.10.2022
@author: Michael Krieger
"""

# Ein paar benötigte Bibliotheken einbinden
import xml.etree.ElementTree as ET # xml-Verarbeitung
import base64 # base64-Codierung
import json # json-Verarbeitung
import numpy as np # NumPy
from pybis import Openbis # openBIS
import getpass # Passwortabfrage
from urllib.request import urlopen # Datei-Download
from io import StringIO # Heruntergeladene Daten als Datei für numpy.loadtxt zur Verfügung stellen

openbisSession=None

def login(url,username=None,password=None):
# Anmelden bei openBIS
# Parameter: url = Serveradresse
#            username = Benutzername (wenn nicht explizit übergeben, dann erfolgt eine Eingabeaufforderung)
#            password = Passwort (wenn nicht explizit übergeben, dann erfolgt eine Eingabeaufforderung)
    global openbisSession
    print('Login to openBIS: '+url)
    if (username is None):
        username=input('Username: ') # Benutzername abfragen
    if (password is None):
        password=getpass.getpass('Password: ') # Passwort abfragen
    openbisSession=Openbis(url)
    openbisSession.login(username,password,save_token=True)
    password=None
    if (openbisSession.is_session_active()):
        print("Login successful")
    else:
        print("Login failed")
        openbisSession=None
    
def logout():
    global openbisSession
    openbisSession.logout()

def getDatasetFileIO(permId,filename,decode='utf-8'):
# Funktion zum Laden von Dateien aus openBIS Dataset-Objekten
# Parameter: openbisSession = aktuelle Session (Rückgabe von login)
#            permId = openBIS-PermId
#            filename = Dateiname der Datendatei im openBIS Dataset-Objekt (inkl. Dateiendung und ggf. Unterverzeichnis)
#                       Beispiele: superdaten.txt, nur_das_beste/superdaten.txt
#                       Es wird die erste Datei geladen, die auf filename endet
#            decode = Kodierung des Dateiinhalts (optional, Standard: utf-8)
# Rückgabe:  StringIO Dateiobjekt (virtuelles Dateiobjekt, das z. B. in numpy.loadtxt verwendet werden kann)
    global openbisSession
    try:
        # dataset von openBIS laden
        ds=openbisSession.get_dataset(permId)
        # url zur Datei rausfinden
        fileLinks=ds.file_links
        url=''
        for key in fileLinks.keys():
            if (key.endswith(filename)):
                url=fileLinks[key]
                break
        if (len(url)>0):
            # Dateiinhalt vom openBIS Datastore Server herunterladen
            filedata=urlopen(url).read()
            if (decode is not None):
                filedata=filedata.decode(decode) # Bytedaten dekodieren
            fileIO=StringIO(filedata) # StringIO generiert ein virtuelles Dateiobjekt mit dem Inhalt filedata
        else:
            # Die Datei gibt es nicht
            fileIO=None
    except:
        # irgendetwas lief schief; wir geben dann None zurück
        fileIO=None
    return fileIO
   
def getSpreadsheetData(permId):
# Funktion zur Abfrage von Spreadsheet-Daten aus openBIS Experimental-Step-Objekten
# Parameter: permId = openBIS-PermId des openBIS Experimental-Step-Objekts
# Rückgabe:  NumPy-Array mit den Tabellendaten (spaltenweise)

    # Hilfsfunktion um string in float umzuwandeln und, falls das nicht geht, in None
    # dabei wird ein Dezimalkomma ggf. in einen Dezimalpunkt umgewandelt
    def toFloat(value):
        try:
            return float(value.replace(",","."))
        except ValueError:
            return None
    
    global openbisSession
    try:
        # Objekt laden (Experimental Step)
        experimentalStep=openbisSession.get_object(permId)
        # Spreadsheet-Daten extrahieren
        spreadsheetXml=experimentalStep.props['experimental_step.spreadsheet']
        spreadsheetEncoded=ET.fromstring(spreadsheetXml).text
        spreadsheet=base64.b64decode(spreadsheetEncoded)
        spreadsheet=spreadsheet.decode('unicode_escape')
        dataStr=json.loads(spreadsheet)['data']
        # Zelleninhalte in float bzw. None umwandeln
        data=np.array([[toFloat(j) for j in i] for i in dataStr])
        # Leere Zeilen und Spalten entfernen
        data=np.transpose(data[~np.all(data==None,axis=1)])
        data=data[~np.all(data==None,axis=1)]
    except:
        # irgendetwas lief schief; wir geben dann None zurück
        data=None
    return data;
