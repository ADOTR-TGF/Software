import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['figure.figsize'] = [15, 7]

plt.figure()

#example spectrum of TGF energy deposit in a detector
NaI_Response = np.loadtxt('original/NaI_Response',usecols=(1),dtype=float)
bins = np.loadtxt('original/NaI_Response',usecols=(0), dtype=float)

binenergies = bins*1e3 #units keV
plt.loglog(binenergies, NaI_Response, marker='.', linestyle='', label='NaI')

plastic_response = np.loadtxt('original/LgPl_Response', usecols=(1), dtype=float)
bins = np.loadtxt('original/LgPl_Response',usecols=(0), dtype=float)

binenergies = bins*1e3 #units keV
plt.loglog(binenergies, plastic_response, marker='.', linestyle='', label='Plastic')

plt.title('Sensor Responses')
plt.xlabel('KeV')
plt.ylabel('Spectrum Response')
plt.legend()
plt.show()