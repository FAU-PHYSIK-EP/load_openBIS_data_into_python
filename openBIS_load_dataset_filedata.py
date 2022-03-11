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
# Parameter: permId = openBIS-PermId, z. B. 20220307155803636-543
#            filename = Dateiname der Datendatei im openBIS Dataset-Objekt (inkl. Dateiendung und ggf. Unterverzeichnis)
#                       Beispiele: superdaten.txt, nur_das_beste/superdaten.txt
#                       Es wird die erste Datei geladen, die auf filename endet
# Rückgabe:  StringIO Dateiobjekt (virtuelles Dateiobjekt, das z. B. in numpy.loadtxt verwendet werden kann)
def openBISGetDatasetFileIO(permId,filename):
    global o;
    try:
        # dataset von openBIS laden
        ds=o.get_dataset(permId)
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
            filedata=filedata.decode('utf-8') # Bytedaten dekodieren (utf-8 wird angenommen)
            fileIO=StringIO(filedata) # StringIO generiert ein virtuelles Dateiobjekt mit dem Inhalt filedata
        else:
            # Die Datei gibt es nicht
            fileIO=None
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
    if (IO is not None):
        data=np.loadtxt(IO,skiprows=1)
        print(data)
    else:
        print("Datei wurde nicht gefunden")
    # Abmelden von openBIS
    o.logout()
else:
    print("Fehler beim Anmelden bei openBIS")
    
