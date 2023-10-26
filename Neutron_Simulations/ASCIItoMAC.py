#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 16:56:28 2020

@author: jeffreychaffin
"""

import numpy as np

gammalist = np.loadtxt('joeAltdown_6.txt')
EnergyMeV = gammalist[0:,0]
AltitudeKm = gammalist[0:,1]
ZenithRad = gammalist[0:,2]
AzimuthalRad = []


index = np.where(EnergyMeV>10)
EnergyMeV = EnergyMeV[index]
AltitudeKm = AltitudeKm[index]
ZenithRad = ZenithRad[index]

print('number of photons:')
print(len(EnergyMeV))

for i in range(len(EnergyMeV)):
    angle = 2*np.pi*np.random.random()
    AzimuthalRad.append(angle)

xpos = 0
ypos = 0
zpos = AltitudeKm

xdir = []
ydir = []
zdir = []

for i in range(len(EnergyMeV)):
    x = np.sin(ZenithRad[i])*np.cos(AzimuthalRad[i])
    y = np.sin(ZenithRad[i])*np.sin(AzimuthalRad[i])
    z = np.cos(ZenithRad[i])
    xdir.append(x)
    ydir.append(y)
    zdir.append(z)

outF = open('x100_6km_downward_gt_10MeV.mac','w')
for i in range(len(EnergyMeV)):
    outF.write('/gps/particle gamma')
    outF.write('\n')
    outF.write('/gps/energy' + ' ')
    outF.write(str(EnergyMeV[i]) + ' ' + 'MeV')
    outF.write('\n')
    outF.write('/gps/position'+ ' ')
    outF.write(str(xpos) +' '+ str(ypos) +' '+ str(zpos[i])+ ' ' + 'km')
    outF.write('\n')
    outF.write('/gps/direction' + ' ')
    outF.write(str(xdir[i]) +' '+ str(ydir[i]) +' '+ str(zdir[i]))
    outF.write('\n')
    outF.write('/run/beamOn 100')
    outF.write('\n')
    outF.write('\n')
outF.close() 
 
