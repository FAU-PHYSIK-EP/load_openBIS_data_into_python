import numpy as np
import matplotlib.pyplot as plt
import openbis

# Connect to openBIS
openbis.login('https://my-openbis-url')

# Example: load data from file in dataset object
file=openbis.getDatasetFileIO('myPermId','superdaten.txt')
data=np.loadtxt(file,skiprows=1).T
print(data)
plt.semilogx(data[0],data[1])

# Example: load data from spreadsheet in experimental_step object
data=openbis.getSpreadsheetData('myPermId')
print(data)
plt.plot(data[0],data[1])

# Disconnect
openbis.logout()
