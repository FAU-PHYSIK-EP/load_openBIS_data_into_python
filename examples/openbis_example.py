import numpy as np
import matplotlib.pyplot as plt
import openbis

# Connect to openBIS
openbis.login('https://physics.openbis.data.fau.de')

# Example: load data from file in dataset object
data=openbis.getDatasetData('20220315142624274-1716','tiefpass_bode2.txt',skiprows=1)
print(data)
plt.semilogx(data[0],data[1])

# Example: load data from spreadsheet in experimental_step object
data=openbis.getSpreadsheetData('20220429111324303-4328',usecols=[0,1])
print(data)
plt.plot(data[0],data[1])

# Disconnect
openbis.logout()
