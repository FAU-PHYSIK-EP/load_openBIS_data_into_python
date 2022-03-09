# -*- coding: utf-8 -*-
"""
Created on 09.03.2022
@author: Michael Krieger
"""

# Ein paar benötigte Bibliotheken einbinden
import xml.etree.ElementTree as ET # xml-Verarbeitung
import base64 # base64-Codierung
import json # json-Verarbeitung
import numpy as np # NumPy
from pybis import Openbis # openBIS
import getpass # Passwortabfrage
   
# Funktion zur Abfrage von Spreadsheet-Daten aus openBIS Experimental-Step-Objekten
# Parameter: identifier = openBIS-Identifier des openBIS Experimental-Step-Objekts
# Rückgabe:  NumPy-Array mit den Tabellendaten (spaltenweise)
def openBISLoadSpreadsheetData(identifier):

    # Hilfsfunktion um string in float umzuwandeln und, falls das nicht geht, in None
    # dabei wird ein Dezimalkomma ggf. in einen Dezimalpunkt umgewandelt
    def toFloat(value):
        try:
            return float(value.replace(",","."))
        except ValueError:
            return None
    
    global o;
    try:
        # Objekt laden (Experimental Step)
        experimentalStep=o.get_object(identifier)
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
    
### BEISPIEL ###

# Anmelden bei openBIS
username=input() # Benutzername abfragen
password=getpass.getpass() # Passwort abfragen
o=Openbis('https://your.openbis.url')
o.login(username,password,save_token=True)
password=None
if (o.is_session_active()):
    print("Anmeldung bei openBIS erfolgreich")
    # Daten laden
    data=openBISLoadSpreadsheetData('your_openbis_experimental_step_identifier')
    print(data)
    # Abmelden von openBIS
    o.logout()
else:
    print("Fehler beim Anmelden bei openBIS")
