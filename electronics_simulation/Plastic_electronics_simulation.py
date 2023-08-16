#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:17:41 2023

@author: enp
"""

import numpy as np
import numpy.random as ran
import matplotlib.pyplot as plt
import pylab as pl
import pandas as pd
import scipy
import time
from matplotlib import rcParams
rcParams['figure.figsize'] = [15, 7]
import scipy.signal as signal

#variables for creating the trace
countrate= 10e6
fwhm = 50.0 
TGF_duration = fwhm*3e-6
counts = int(countrate*TGF_duration)
#counts = 300 #total counts incident on the detector   
#fwhm = 100 #fwhm of the total TGF count distribution in units microseconds
#TGF_duration = fwhm*3e-6
#countrate = int(counts/TGF_duration)  
mean = .7 #mean of the TGF trace distribution
std = .5 #detemines the amount of asymetry in the TGF trace distribution
dt = 100e-9 # seconds before pulse
tstep = 25e-9 #sampling rate in seconds. 40MHz
trace_length = 28000 #number of samples in a trace file (700us at 40MHz)
keV_per_area = 1.6 #determined by trial and error to match energy range of instrument 
mV_per_ADC = 1000./4096.
baseline = 105
basenoise = 0.
bits = 12  #use 12 for doing listmode but use 10 to compare traces to real trace files

#variables for integrating trace pulses into listmode events
thresh = 0.5      #units of mV  this is the pulse trigger threshold
int_i = 14      #integration time = 0.35 microsecs = 14 samples at 40MHz sampling 
dead_i = int_i     #deadtime = integration time
extend = 1    #extendable dead time parameter
escale = 6.63  #being used to scale the pulse integration value to energy in keV

#example spectrum of TGF energy deposit in a plastic detector
LgPl_Response = np.loadtxt('LgPl_Response',usecols=(1),dtype=float)
bins = np.loadtxt('LgPl_Response',usecols=(0),dtype=float)
#s = np.genfromtxt('/home/enp//Desktop/Emorpho Analysis Software and Calibration data/Emorpho Simulations/alt5SFT_noaa_plane_rough.out', usecols = (2), skip_footer=2)

spectrum = LgPl_Response
binenergies = bins*1e3 #units keV 
#spectrum[49]= 2000 #49 is 1000keV, 85 is 6800keV

#real plastic trace data
tracedata = pd.read_csv('real_plastic_trace.csv')

def plastic_pulse(a):
    sos = signal.butter(3, 0.66e7, btype='low', analog=False, output='sos', fs=40e6)
    t = np.arange(0.,0.5e-6,25e-9)
    y = t*0
    y[4]=1.
    fil = signal.sosfilt(sos,y)
    fil = fil*a/np.max(fil)
    return(t,fil)

def make_plastic_trace(counts,fwhm,spectrum,binenergies,dt,tstep,trace_length,mV_per_ADC,keV_per_area,baseline,basenoise,bits,mean,std):

    #Freeze the random number seed for reproducibility:
    seed=49
    ran.seed(seed)
    #ran.seed()

    #one trace file worth of data.
    sampletimes = np.linspace(-dt,tstep*trace_length+dt,trace_length+int(2*dt/tstep),endpoint=False) 

    
    #if running a statistical study using countrates Get in advance the number of counts that will be used to populate each trace.
    #poisson = ran.poisson(countrate*tstep*time_grid)  #why is time_grid used in this??
    #poisson = (np.floor(countrate*tstep*time_grid)).astype(int)

    #initialize a clear trace
    n = len(sampletimes)
    trace = np.zeros(sampletimes.size)
    
    sigma = (fwhm/2.355)*1e-6  #one standard deviation of the time distribution in units seconds    
    
    #lognormal arguments: (mean, std, size) sigma is used to scale the output of lognormal to the width of a TGF trace
    # the mean and std can be adjusted to move the trace distribution left or right (mean) and adjust the asymetry (std)
    times = ran.lognormal(mean,std,counts)*sigma 
    #times = ran.uniform(low=0,high=7.0,size=counts)*sigma 
    #line = np.abs(ran.choice(len(spectrum),  p=spectrum/sum(spectrum), size = len(times))) #chooses energies from an input spectrum based on probabilites 
    #energies = line*specscale_keV + 5.   #spectrum starts at 5keV
    energies = np.abs(ran.choice(binenergies, p=spectrum/sum(spectrum), size = len(times)))
    
    times = np.sort(times)+100e-6 #100us of pre-TGF  
    
    
    #define the pulse shape once
    pulsetimes,pulse = plastic_pulse(1.)
    nsamples = len(pulse)


    area_per_peak = np.sum(pulse)/max(pulse)
    mV_per_keV = mV_per_ADC/(keV_per_area*area_per_peak)

    #For every count, create a pulse and add it to the trace:
    i=0
    for t in times:
        t_index = (sampletimes > t-dt).nonzero()
        t_index0 = (t_index[0])[0]
        navailable =  len(trace[t_index0:t_index0+nsamples])
        if navailable == nsamples:
            trace[t_index0:t_index0+nsamples] = trace[t_index0:t_index0+nsamples] + pulse*energies[i]
        i=i+1  
        #print(i)
    
    #scale to mV, add baseline and noise, and clip:
    
    trace = trace*mV_per_keV
    trace += baseline
    trace += ran.randn(n)*basenoise
    
    w=(trace > 1000.).nonzero()
    trace[w]=1000.
    
    #digitize:
    itrace = trace/1000.*2**bits
    for i in range(len(itrace)):
        itrace[i] = float(int(itrace[i]))
    itrace = itrace*1000./2**bits
    
    return(itrace)

def plastic_trace_to_counts(trace,dt,tstep,thresh,baseline,extend,escale,int_i,dead_i):
    
    
    energies = []
    sample_times = []
    n = trace.size
    
    di=int(dt/tstep)
    
    i=di
    
    while (i< n-dead_i-1):
        if (trace[i] > thresh+baseline):               #find a value above trigger threshold.
                energy = np.sum(trace[i-5:i-6+int_i]-baseline) #Integrate pulse over int_i samples starting with first above threshold.
                norm_energy = energy*escale     #Convert energy into channels to compare to real data spectrum
                
                energies.append(norm_energy)
                sample_times.append(i)
                i+=dead_i
              
                #Paralyzable deadtime:keep extending the window as long as the last sample of the last interval is still high.
                if (extend > 0):
                    while (trace[i-1] > thresh+baseline and i < n-di-extend):
                        i += extend                  
        else:
                i += 1
    
    return(energies, sample_times)

def trace_trigger(trace,trace_time):
    n = 100
    m = 10000
    counter = 0
    for i in range(len(trace)):
        if counter < 0:
            counter = 0
        if trace[i]> 110.:
            counter+=n
        else:
            counter -= 1.
        if counter >= m:
            trigger_time = trace_time[i]
            trigger_index = i
            break
        else:
            trigger_time = np.array([])
            trigger_index = np.array([])
    return(trigger_time,trigger_index)


#calling the sample trace pulse and real trace data
pulsetimes,pulse = plastic_pulse(1.)
nsamples = len(pulse)
tdatatime = tracedata.Seconds[261:281]-tracedata.Seconds[261]
tdata = (tracedata.Tracesample[261:281]-25)/(max(tracedata.Tracesample)-25)

#calling the trace and listmode event functions  
trace = make_plastic_trace(counts, fwhm, spectrum,binenergies, dt, tstep, trace_length, mV_per_ADC, keV_per_area, baseline, basenoise, bits,mean,std)
energies, event_sample = plastic_trace_to_counts(trace, dt, tstep, thresh, baseline, extend, escale, int_i, dead_i)
energies = np.array(energies)
event_time = np.array(event_sample)*tstep*1e6 #converts samples to time in microseconds
trace_time = np.arange(len(trace))*tstep*1e6 #converts samples to time in microseconds

#calling the trace triggering function
trigger_time, trigger_index = trace_trigger(trace, trace_time)

print('input counts = ',counts)                  
print('integrated counts = ', len(energies))
print('percent counted = ',100*len(energies)/counts)
print('average countrate in',TGF_duration*1e6,'us window = ',countrate/1e5,'e5')
print('listmode countrate = ',len(energies)/TGF_duration/1e5,'e5')
if trigger_time.size > 0:
    print('trace triggered at ',trigger_time,'us')

'''
#fit single trace plot
plt.figure(figsize=(15,5))
plt.plot(pulsetimes*1e6,pulse,color='black',label='modeled trace pulse')
#plt.scatter(pulsetimes,pulse)
plt.plot(tdatatime*1e6,tdata,color='red',label='real trace pulse')
#plt.scatter(tdatatime,tdata)
#plt.xlim(-.5e-6,1.3e-6)
plt.xlim(-.2,.6)
plt.xlabel('microseconds',fontsize=16)
plt.title('Modeled plastic pulse',fontsize=16)
plt.tick_params(labelsize=12)
plt.legend(fontsize=10)
'''
#full trace
plt.figure(figsize=(10,5))
plt.plot(trace_time,trace,color='black')
#plt.xlim(0,300)
plt.xlim(100,300)
plt.ylim(90,500)
#plt.grid()
plt.ylabel('mV',fontsize=20)
plt.xlabel('microseconds',fontsize=20)
plt.title('Simulated plastic trace data',fontsize=20)
plt.tick_params(labelsize=18)
if trigger_time.size > 0:
    plt.vlines(trigger_time,105,max(trace),color='red')

# simulated listmode energy vs time plot
plt.figure(figsize=(10,5))
plt.scatter(event_time,energies,color='black',s=10.0)
#plt.grid(which='both')
plt.xlim(100,300)
#plt.xlim(100,120)
plt.ylim(10,25000)
plt.yscale('log')
plt.ylabel('Energy keV',fontsize=20)
plt.xlabel('microseconds',fontsize=20)
plt.title('Simulated plastic list-mode data',fontsize=20)
plt.tick_params(labelsize=18)
