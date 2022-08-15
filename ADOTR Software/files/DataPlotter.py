#! /usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas as pd
import DataReader as DR

files = sorted(glob.glob("/Detector1/data/*.txt"))
trace_files = sorted(glob.glob("/Detector1/data/*.xtr"))

#note that depending on if you want to use the PPS derived time or not you need to modify the code to reflect this.
def CountRateHist(fileName,binsize,tmin,tmax):
    data = DR.DataTable(fileName)
    Range = [tmin,tmax]
    num_bins = int((tmax-tmin)/binsize)
    h = np.histogram(data.SecondsofDayNoPPS,bins=num_bins,range=Range)
    plt.figure(figsize=(15,5))
    plt.hist(h[1][:-1],h[1],weights=h[0],color='black')
    plt.ylim(0,1.5*max(h[0]))
    plt.xlabel('Seconds of Day')
    plt.ylabel('Counts/'+str(binsize)+' seconds')
    plt.title(fileName.split('/')[-1])
    plt.show()

#note that depending on if you want to use the PPS derived time or not you need to modify the code to reflect this.
def EnergyvsTimeScatter(fileName,tmin,tmax,maxenergy=66000,markersize=.01):
    data = DR.DataTable(fileName)
    plt.figure(figsize=(15,5))
    plt.scatter(data.SecondsofDayNoPPS,data.energies,color='black',s=markersize)
    plt.xlim(tmin,tmax)
    plt.ylim(0,maxenergy)
    plt.xlabel('Seconds of Day')
    plt.ylabel('Energy (ADC)')
    plt.title(fileName.split('/')[-1])
    plt.show()


#This function will gather energy data from the most recent sequential files and plot an energy histogram. The argument num_files indicates how many files back from the most recent to plot. det_type should either be 'nai' or 'pla'.  
def EnergySpectrum(num_files,det_type,binsize,Emin=0,Emax=66000,log=False):
    data = np.array([x for x in DR.files if det_type in x])
    E = []
    for i in range(num_files,0,-1):
    	d = DR.DataTable(data[-i])
    	E.append(d.energies)
    Energies = pd.concat(E,ignore_index=True)
    Range = [Emin,Emax]
    num_bins = int((Emax-Emin)/binsize)
    h = np.histogram(Energies,bins=num_bins,range=Range)
    plt.figure(figsize=(15,5))
    plt.hist(h[1][:-1],h[1],weights=h[0],color='black',log=log)
    #plt.ylim(0,1.5*max(h[0]))
    plt.xlabel('Energy (ADC)')
    plt.ylabel('Counts')
    plt.title(det_type + ' Spectrum')
    plt.show()

#To only plot a specific files energy histogram 
def SingleFileEnergySpectrum(fileName,binsize,Emin=0,Emax=66000,log=False):
    data = DR.DataTable(FileName)
    Range = [Emin,Emax]
    num_bins = int((Emax-Emin)/binsize)
    h = np.histogram(Energies,bins=num_bins,range=Range)
    plt.figure(figsize=(15,5))
    plt.hist(h[1][:-1],h[1],weights=h[0],color='black',log=log)
    #plt.ylim(0,1.5*max(h[0]))
    plt.xlabel('Energy (ADC)')
    plt.ylabel('Counts')
    plt.title(fileName.split('/')[-1])
    plt.show()

#plots the trace data. Buffer is either 0,1,2,3,4 where 0 indicates the longest buffer. 
def Traceplot(fileName,Buffer,tmin,tmax):
    data = DR.TraceDataTable(fileName)[Buffer]
    plt.figure(figsize=(15,5))
    plt.plot(data.SecondsofDayNoPPS,data.Tracesample,color='black')
    plt.xlim(tmin,tmax)
    plt.xlabel('Seconds of Day')
    plt.ylabel('Trace amplitude')
    plt.title(fileName.split('/')[-1])
    plt.show()


