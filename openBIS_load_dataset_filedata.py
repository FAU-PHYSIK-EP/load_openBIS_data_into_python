# -*- coding: utf-8 -*-
"""
Created on 09.03.2022
@author: Michael Krieger
"""

# Ein paar benötigte Bibliotheken einbinden
import numpy as np # NumPy
from pybis import Openbis # openBIS
import getpass # Passwortabfrage
from urllib.request import urlopen # Datei-Download
from io import StringIO # Heruntergeladene Daten als Datei für numpy.loadtxt zur Verfügung stellen

# Funktion zum Laden von Dateien aus openBIS Dataset-Objekten
# Parameter: permId = openBIS-PermId
#            filename = Dateiname der Datendatei im openBIS Dataset-Objekt (inkl. Dateiendung)
# Rückgabe:  StringIO Dateiobjekt (virtuelles Dateiobjekt, das z. B. in numpy.loadtxt verwendet werden kann)
def openBISGetDatasetFileIO(permId,filename):
    global o;
    try:
        # dataset von openBIS laden
        ds=o.get_dataset(permId)
        # Dateiinhalt vom openBIS Datastore Server herunterladen
        url=ds.file_links['original/DEFAULT/'+filename]
        filedata=urlopen(url).read()
        filedata=filedata.decode('utf-8') # Bytedaten dekodieren (utf-8 wird angenommen)
        fileIO=StringIO(filedata) # StringIO generiert ein virtuelles Dateiobjekt mit dem Inhalt filedata
    except:
        # irgendetwas lief schief; wir geben dann None zurück
        fileIO=None
    return fileIO

### BEISPIEL ###

# Anmelden bei openBIS
username=input() # Benutzername abfragen
password=getpass.getpass() # Passwort abfragen
o=Openbis('https://your.openbis.url')
o.login(username,password,save_token=True)
password=None
if (o.is_session_active()):
    print("Anmeldung bei openBIS erfolgreich")
    # Datei aus openBIS-Dataset-Objekt laden
    IO=openBISGetDatasetFileIO('your_permid','your_measurement_datafile.txt')
    data=np.loadtxt(IO,skiprows=1)
    print(data)
    # Abmelden von openBIS
    o.logout()
else:
    print("Fehler beim Anmelden bei openBIS")
    