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

S = []
E = []
T = []
P = []
D = []

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    for i in range(9):
        filename = 'AIRCRAFT_x100_6km_downward_gt_Slab0' + str(i)+'_Hits.out'
        file = np.loadtxt(filename, skiprows=1, usecols=(0,1,2,3,4), dtype=str)
        if np.ndim(file) == 2:
            s = file[0:, 0]
            S.append(s)
            e = file[0:, 1]
            E.append(e)
            t = file[0:, 2]
            T.append(t)
            p = file[0:, 3]
            P.append(p)
            d = file[0:, 4]
            D.append(d)
        else:
            s = np.array([file[0]])
            S.append(s)
            e = np.array([file[1]])
            E.append(e)
            t = np.array([file[2]])
            T.append(t)
            p = np.array([file[3]])
            P.append(p)
            d = np.array([file[4]])
            D.append(d)

    for i in range(10, 200):
        filename = 'AIRCRAFT_x100_6km_downward_gt_Slab' + str(i)+'_Hits.out'
        file = np.loadtxt(filename, skiprows=1, usecols=(0,1,2,3,4), dtype=str)
        if np.ndim(file) == 2:
            s = file[0:, 0]
            S.append(s)
            e = file[0:, 1]
            E.append(e)
            t = file[0:, 2]
            T.append(t)
            p = file[0:, 3]
            P.append(p)
            d = file[0:, 4]
            D.append(d)
        else:
            s = np.array([file[0]])
            S.append(s)
            e = np.array([file[1]])
            E.append(e)
            t = np.array([file[2]])
            T.append(t)
            p = np.array([file[3]])
            P.append(p)
            d = np.array([file[4]])
            D.append(d)


S = np.concatenate(S, axis=0)
particle = S.astype(str)
E = np.concatenate(E, axis=0)
energy = E.astype(float)/1e6  # units MeV
T = np.concatenate(T, axis=0)
time = T.astype(float)  # units ms
P = np.concatenate(P, axis=0)
D = np.concatenate(D, axis=0)

px = []
py = []
pz = []
for i in range(len(P)):
    p = re.split('[(),]', P[i])
    for j in range(len(p)):
        p_x = float(p[1])
        p_y = float(p[2])
        p_z = float(p[3])
    px.append(p_x)
    py.append(p_y)
    pz.append(p_z)

Px = np.array(px)  # units m
Py = np.array(py)  # units m
Pz = np.array(pz)  # units m

dx = []
dy = []
dz = []
for i in range(len(D)):
    d = re.split('[(),]', D[i])
    for j in range(len(d)):
        d_x = float(d[1])
        d_y = float(d[2])
        d_z = float(d[3])
    dx.append(d_x)
    dy.append(d_y)
    dz.append(d_z)

Dx = np.array(dx)  # unit vector
Dy = np.array(dy)  # unit vector
Dz = np.array(dz)  # unit vector

radius = np.sqrt(Px**2 + Py**2)
pos_z = len(np.where(Dz>0)[0])
neg_z = len(np.where(Dz<0)[0])
percent_from_above = 100*(neg_z/len(Dz))
percent_from_below = 100*(pos_z/len(Dz))


x = 100  # number of times each photon from Dwyer file is run in stage 1
y = 1  # number of times each neutron from stage1 is run in stage2
N = 698162  # number of photons above 1MeV in Dwyer file
TGF_brightness = 1e17  # intrinsic TGF photons above 1MeV
brightness_factor = TGF_brightness/(N*x*y)

#limit hit arrays using a max energy cutoff
energy_cutoff = 25 #units MeV (keeps energies below this cut value. 
                        #any value above 25 MeV won't cut anything out)
energy_cut = np.delete(energy, np.where(energy>energy_cutoff))
time_cut = np.delete(time, np.where(energy>energy_cutoff))
count_cut = len(energy_cut)
radius_cut = np.delete(radius,np.where(energy>energy_cutoff))
Pz_cut = np.delete(Pz,np.where(energy>energy_cutoff))
particle_cut = np.delete(particle,np.where(energy>energy_cutoff))


#Gaussian 'blur' of the radial distribution of hits
sigma = 1 #units meters
radius_cut_blurred = np.empty(len(radius_cut))
for i in range(len(radius_cut)-1):
    r = np.random.normal(radius_cut[i],sigma)
    radius_cut_blurred[i] = r

#histograming by annuli
bins = 30
Range = [0,3000]
h = np.histogram(radius_cut_blurred,bins=bins,density=False,range=Range)

annuli = []
for i in range(len(h[1])-1):
    area = np.pi*(h[1][i+1]**2-h[1][i]**2)*1E4  #converts from square meters to square cm
    annuli = np.append(annuli,area) #units cm^2
raw_flux_annuli = h[0]/annuli
flux_annuli = brightness_factor*raw_flux_annuli


index = np.where(energy<energy_cutoff)
fig = plt.figure(figsize=(20, 20))
 # syntax for 3-D projection
ax = plt.axes(projection='3d')
sc = ax.scatter(Px[index], Py[index], Pz[index], c=energy[index], s=50)
plt.colorbar(sc, label='Energy-MeV')
ax.set_xlabel('x axis-meters', fontsize=16)
ax.set_ylabel('y axis-meters', fontsize=16)
ax.set_zlabel('Altitude-meters', fontsize=16)
plt.tick_params(labelsize=14)
plt.tight_layout()
ax.set_zlim(0,10000)


fig = plt.figure(figsize=(20, 20))
 # syntax for 3-D projection
ax = plt.axes(projection='3d')
sc = ax.scatter(Px, Py, Pz, c=time, s=50, cmap='plasma')
plt.colorbar(sc, label='time-ms')
ax.set_xlabel('x axis-meters', fontsize=16)
ax.set_ylabel('y axis-meters', fontsize=16)
ax.set_zlabel('Altitude-meters', fontsize=16)
plt.tick_params(labelsize=14)
plt.tight_layout()
ax.set_zlim(0,10000)

fig = plt.figure(figsize=(20,10))
plt.hist(energy,bins=40,color='black')
plt.tick_params(labelsize=16)
plt.xlabel('Energy, MeV',fontsize=16)
plt.ylabel('Counts',fontsize=16)


'''
fig = plt.figure(figsize=(20,10))
plt.hist(time,bins=40,color='blue')
plt.tick_params(labelsize=16)
plt.xlabel('Microseconds',fontsize=16)
plt.ylabel('Counts',fontsize=16)

fig = plt.figure(figsize=(20,10))
plt.hist(Pz,bins=25,color='red')
plt.tick_params(labelsize=16)
plt.xlabel('Altitude, meters',fontsize=16)
plt.ylabel('Counts',fontsize=16)
# plt.xlim(0,1600)
'''

