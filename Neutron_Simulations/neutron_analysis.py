#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 12:22:19 2023

@author: enp
"""

import numpy as np
import matplotlib.pyplot as plt
import re
import matplotlib.gridspec as gridspec
import scipy.stats
from matplotlib.colors import LogNorm, Normalize
import warnings

E=[]
T=[]
P=[]
D=[]

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    for i in range(10):
        filename = 'x100_6km_downward_gt_Slab0'+ str(i)+'_Hits.out'
        file = np.loadtxt(filename,skiprows=1,usecols=(1,2,3,4),dtype=str)
        if np.ndim(file) == 2:
            e = file[0:,0]
            E.append(e)
            t = file[0:,1]
            T.append(t)
            p = file[0:,2]
            P.append(p)
            d = file[0:,3]
            D.append(d)
        else:
            e = np.array([file[0]])
            E.append(e)
            t = np.array([file[1]])
            T.append(t)
            p = np.array([file[2]])
            P.append(p)
            d = np.array([file[3]])
            D.append(d)
            
    for i in range(10,200):
        filename = 'x100_6km_downward_gt_Slab'+ str(i)+'_Hits.out'
        file = np.loadtxt(filename,skiprows=1,usecols=(1,2,3,4),dtype=str)
        if np.ndim(file) == 2:
            e = file[0:,0]
            E.append(e)
            t = file[0:,1]
            T.append(t)
            p = file[0:,2]
            P.append(p)
            d = file[0:,3]
            D.append(d)
        else:
            e = np.array([file[0]])
            E.append(e)
            t = np.array([file[1]])
            T.append(t)
            p = np.array([file[2]])
            P.append(p)
            d = np.array([file[3]])
            D.append(d)

E = np.concatenate( E, axis=0 )
energy = E.astype(float)/1e6 #units MeV
T = np.concatenate(T,axis=0)
time = T.astype(float) #units ms
P = np.concatenate(P,axis=0)
D = np.concatenate(D,axis=0)

px = []
py = []
pz = []
for i in range(len(P)):
    p = re.split('[(),]',P[i])
    for j in range(len(p)):
        p_x = float(p[1])
        p_y = float(p[2])
        p_z = float(p[3])
    px.append(p_x)
    py.append(p_y)
    pz.append(p_z)

Px = np.array(px)  #units m
Py = np.array(py)  #units m
Pz = np.array(pz)  #units m

dx = []
dy = []
dz = []
for i in range(len(D)):
    d = re.split('[(),]',D[i])
    for j in range(len(d)):
        d_x = float(d[1])
        d_y = float(d[2])
        d_z = float(d[3])
    dx.append(d_x)
    dy.append(d_y)
    dz.append(d_z)

Dx = np.array(dx)  #unit vector
Dy = np.array(dy)  #unit vector
Dz = np.array(dz)  #unit vector


x = 100 #number of times each photon from Dwyer file is run
N = 698162 #number of photons above 1MeV in Dwyer file
TGF_brightness = 1e17 #number of intrinsic TGF photons above 1MeV
counts_correction_factor = TGF_brightness/(N*x)

raw_neutron_counts = len(energy)
ave_energy = round(np.mean(energy),3)
ave_alt = round(np.mean(Pz),3)

corrected_neutron_counts = raw_neutron_counts*counts_correction_factor



fig = plt.figure(figsize=(20,20))
 # syntax for 3-D projection
ax = plt.axes(projection ='3d')
sc=ax.scatter(Px,Py,Pz,c=energy,s=50)
plt.colorbar(sc,label='Energy-MeV')
ax.set_xlabel('x axis-meters',fontsize=16)
ax.set_ylabel('y axis-meters',fontsize=16)
ax.set_zlabel('Altitude-meters',fontsize=16)
plt.tick_params(labelsize=14)
plt.tight_layout()

fig = plt.figure(figsize=(20,20))
 # syntax for 3-D projection
ax = plt.axes(projection ='3d')
sc=ax.scatter(Px,Py,Pz,c=time,s=50,cmap='plasma')
plt.colorbar(sc,label='time-$\mu$s')
ax.set_xlabel('x axis-meters',fontsize=16)
ax.set_ylabel('y axis-meters',fontsize=16)
ax.set_zlabel('Altitude-meters',fontsize=16)
plt.tick_params(labelsize=14)
plt.tight_layout()


fig = plt.figure(figsize=(20,10))
plt.hist(energy,bins=50,color='black')
plt.tick_params(labelsize=16)
plt.xlabel('Energy, MeV',fontsize=16)
plt.ylabel('Counts',fontsize=16)

'''
fig = plt.figure(figsize=(20,10))
plt.hist(time,bins=40,color='blue')
plt.tick_params(labelsize=16)
plt.xlabel('Milliseconds',fontsize=16)
plt.ylabel('Counts',fontsize=16)

fig = plt.figure(figsize=(20,10))
plt.hist(Pz,bins=25,color='red')
plt.tick_params(labelsize=16)
plt.xlabel('Altitude, meters',fontsize=16)
plt.ylabel('Counts',fontsize=16)
#plt.xlim(0,1600)
'''