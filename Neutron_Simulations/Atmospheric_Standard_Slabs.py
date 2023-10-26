#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 12:28:32 2020

@author: jeffreychaffin
"""

import numpy as np

R_e = 6.3781E6 # radius of the earth in meters
R = 8.31432 #universal gas constant N m / mol K 
R_sp = 287.052 #specific gas constant J/kg K
g = 9.80665 #gravitational acceleration m/s**2
M = 0.0289644 #molar mass of air kg/mol
AltitudeMax = 20000.0 # units meters
SlabHeight = 100.0 # units meters
Altitude = np.arange(SlabHeight/2,AltitudeMax,SlabHeight)
half_height = np.full(len(Altitude),str(SlabHeight/2)+'*m, ')
Nslabs = len(Altitude)

Temp = [] # Kelvin
Pres = [] # Pa
Dens = [] # kg/m**3
for i in range(len(Altitude)):
    H = (R_e*Altitude[i])/(R_e + Altitude[i]) #conversion from geometric height to geopotential height
    if H < 11000.0:   #geopotential altitude range 0-11km
        T_b = 288.15 #base Temp of geopotential altitude range
        L_b = -.0065 #Temp lapse rate per meter from base temp of geopotential altitude range
        H_b = 0.0    #base altitude of geopotential altitude range
        P_b = 101325 #base pressure of geopotential altitude range
    elif H < 20000.0:
        T_b = 216.65
        L_b = 0.0
        H_b = 11000.0
        P_b = 22632.06
    elif H < 32000.0:
        T_b = 216.65
        L_b = 0.001
        H_b = 20000.0
        P_b = 5474.889
    elif H < 47000.0:
        T_b = 228.65
        L_b = 0.0028
        H_b = 32000.0
        P_b = 868.0187
    elif H < 51000.0:
        T_b = 270.65
        L_b = 0.0
        H_b = 47000.0
        P_b = 110.9063
    elif H < 71000.0:
        T_b = 270.65
        L_b = -0.0028
        H_b = 51000.0
        P_b = 66.93887
    elif H < 85000.0:
        T_b = 214.65
        L_b = -0.002
        H_b = 71000.0
        P_b = 3.956420
    else:
        print("equations not valid above 85km")
    T = T_b + L_b*(H - H_b)
    if L_b < 0:
        P = P_b*(T_b/T)**((g*M)/(R*L_b))
    elif L_b > 0:
        P = P_b*(T_b/T)**((g*M)/(R*L_b))
    else:
        P = P_b*np.exp((-g*M*(H - H_b))/(R*T_b))
    rho = P/(R_sp*T)    
    Temp.append(T)
    Pres.append(P)
    Dens.append(rho)

    
outF = open('Slabs_standard_atmosphere_20km.txt','w')
outF.write('Nslabs = ' + str(Nslabs) + '\n\n')
outF.write('slabs_z = \n')
for i in range(len(Altitude)):
    outF.write(str(int(Altitude[i]))+'*m, ')        
outF.write('\n\n')
outF.write('slabs_pDz = \n')
for i in range(len(half_height)):
    outF.write(half_height[i])
outF.write('\n\n')
outF.write('slabs_rho = \n')
for i in range(len(Dens)):
    outF.write(str(round(Dens[i],12))+'*kg/m3, ') 
outF.write('\n\n')
outF.write('slabs_P = \n')
for i in range(len(Pres)):
    outF.write(str(round(Pres[i],6))+'*pascal, ')
outF.write('\n\n')
outF.write('slabs_T = \n')
for i in range(len(Temp)):
    outF.write(str(round(Temp[i],3))+'*kelvin, ')
    
outF.close()

