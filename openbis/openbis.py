# -*- coding: utf-8 -*-
"""
Created on 29.03.2022, update on 14.10.2022
@author: Michael Krieger
"""

# Ein paar benötigte Bibliotheken einbinden
import xml.etree.ElementTree as ET  # xml-Verarbeitung
import base64  # base64-Codierung
import json  # json-Verarbeitung
import numpy as np  # NumPy
from pybis import Openbis  # openBIS
import getpass  # Passwortabfrage
from urllib.request import urlopen  # Datei-Download
from io import StringIO  # Heruntergeladene Daten als Datei für numpy.loadtxt zur Verfügung stellen

openbisSessionID = None


def login(url, username=None, password=None):
    """
    Anmelden bei openBIS

    Parameter
    ---------
    url: string
        Serveradresse
    username: string (optional)
        Benutzername (wenn nicht explizit übergeben, dann erfolgt eine Eingabeaufforderung)
    password: string (optional)
        Passwort (wenn nicht explizit übergeben, dann erfolgt eine Eingabeaufforderung)
    Return
    ------
    openBIS-Session (oder None, falls Login nicht erfolgreich)
    """
    global openbisSessionID
    print('Login to openBIS: ' + url)
    if (username is None):
        username = input('Username: ')  # Benutzername abfragen
    if (password is None):
        password = getpass.getpass('Password: ')  # Passwort abfragen
    openbisSessionID = Openbis(url)
    openbisSessionID.login(username, password, save_token=False)
    password = None
    if (openbisSessionID.is_session_active()):
        print("Login successful")
    else:
        print("Login failed")
        openbisSessionID = None


def logout():
    global openbisSessionID
    openbisSessionID.logout()


def getDatasetFileIO(permId, filename, decode='utf-8'):
    """
    Funktion zum Laden von Dateien aus openBIS Dataset-Objekten

    Parameter
    ---------
    openbisSession: Openbis
        aktuelle Session (Rückgabe von login)
    permId: string
        openBIS-PermId
    filename: string
        Dateiname der Datendatei im openBIS Dataset-Objekt (inkl. Dateiendung und ggf. Unterverzeichnis)
        Beispiele: superdaten.txt, nur_das_beste/superdaten.txt
        Es wird die erste Datei geladen, die auf filename endet
    decode: string (default: utf-8)
        Kodierung des Dateiinhalts
    Return
    ------
    StringIO Dateiobjekt (virtuelles Dateiobjekt, das z. B. in numpy.loadtxt verwendet werden kann)
    """
    global openbisSessionID
    try:
        # dataset von openBIS laden
        ds = openbisSessionID.get_dataset(permId)
        # url zur Datei rausfinden
        fileLinks = ds.file_links
        url = ''
        for key in fileLinks.keys():
            if (key.endswith(filename)):
                url = fileLinks[key]
                break
        if (len(url) > 0):
            # Dateiinhalt vom openBIS Datastore Server herunterladen
            filedata = urlopen(url).read()
            if (decode is not None):
                filedata = filedata.decode(decode)  # Bytedaten dekodieren
            fileIO = StringIO(
                filedata
            )  # StringIO generiert ein virtuelles Dateiobjekt mit dem Inhalt filedata
        else:
            # Die Datei gibt es nicht
            fileIO = None
    except:
        # irgendetwas lief schief; wir geben dann None zurück
        fileIO = None
    return fileIO


def getDatasetData(permId, filename, decode='utf-8', skiprows=0, usecols=None):
    """
    Funktion zum Laden von Daten aus openBIS Dataset-Objekten via numpy.loadtxt

    Parameter
    ---------
    openbisSession = aktuelle Session (Rückgabe von login)
    permId = openBIS-PermId
    filename = Dateiname der Datendatei im openBIS Dataset-Objekt (inkl. Dateiendung und ggf. Unterverzeichnis)
               Beispiele: superdaten.txt, nur_das_beste/superdaten.txt
               Es wird die erste Datei geladen, die auf filename endet
    decode: string (default: utf-8)
        Kodierung des Dateiinhalts
    skiprows: int
        Anzahl Zeilen in Datei überspringen (siehe numpy.loadtxt)
    usecols: 
        Liste mit zu berücksichtigen Spalten (siehe numpy.loadtxt)
    Return
    ------
    np.array 
        Daten
    """
    global openbisSessionID
    try:
        # fileio von openBIS laden
        fileio = getDatasetFileIO(permId, filename, decode)
        # Daten laden
        data = np.loadtxt(fileio, skiprows=skiprows, usecols=usecols)
    except:
        # irgendetwas lief schief; wir geben dann None zurück
        data = None
    return data


def getSpreadsheetData(permId, skiprows=0, usecols=None):
    """
    Funktion zur Abfrage von Spreadsheet-Daten aus openBIS Experimental-Step-Objekten

    Hilfsfunktion um string in float umzuwandeln und, falls das nicht geht, in None
    dabei wird ein Dezimalkomma ggf. in einen Dezimalpunkt umgewandelt

    Parameter
    ---------
    permId = openBIS-PermId des openBIS Experimental-Step-Objekt
    skiprows = Anzahl Zeilen der Tabelle überspringen
    usecols = Liste mit zu berücksichtigen Spalten
    
    Return
    ------
    np.array
        Tabellendaten (spaltenweise)

    """
    def toFloat(value):
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return None

    global openbisSessionID
    try:
        # Objekt laden (Experimental Step)
        experimentalStep = openbisSessionID.get_object(permId)
        # Spreadsheet-Daten extrahieren
        spreadsheetXml = experimentalStep.props[
            'experimental_step.spreadsheet']
        spreadsheetEncoded = ET.fromstring(spreadsheetXml).text
        spreadsheet = base64.b64decode(spreadsheetEncoded)
        spreadsheet = spreadsheet.decode('unicode_escape')
        dataStr = json.loads(spreadsheet)['data']
        # Zelleninhalte in float bzw. None umwandeln
        data = np.array([[toFloat(j) for j in i] for i in dataStr])
        # skiprows und leere Zeilen und Spalten entfernen
        data = data[skiprows:]
        data = np.transpose(data[~np.all(data == None, axis=1)])
        data = data[~np.all(data == None, axis=1)]
        if (usecols is not None):
            # wenn usecols angegeben ist, dann diese Spalten extrahieren
            data = np.transpose(data[usecols])
            data = np.transpose(data[~np.all(data == None, axis=1)])
            # bei Verwendung von usecols gehen wir davon aus, dass keine None mehr in den
            # Daten sind und legen den Typ auf float fest (hilft z. B. für numpy.polyfit)
            data = np.array(data, dtype=float)
    except:
        # irgendetwas lief schief; wir geben dann None zurück
        data = None
    return data
