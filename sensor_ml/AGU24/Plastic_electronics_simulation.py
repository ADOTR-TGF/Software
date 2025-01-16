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

from util.Processing import *

#variables for creating the trace
countrate= 1e7
fwhm = 5 # 65 originally
TGF_duration = fwhm*3e-6
#print(TGF_duration)
counts = int(countrate*TGF_duration)
#counts = 300 #total counts incident on the detector   
#fwhm = 100 #fwhm of the total TGF count distribution in units microseconds
#TGF_duration = fwhm*3e-6
#countrate = int(counts/TGF_duration)  
mean = .7 #mean of the TGF trace distribution
std = .5 #detemines the amount of asymetry in the TGF trace distribution
dt = 1e-9 # seconds before pulse
tstep = 25e-9 #sampling rate in seconds. 40MHz
#tstep = 2e-9 #sampling rate in seconds. 500MHz
trace_length = 2000 #number of samples in a trace file (700us at 40MHz=28000)
keV_per_area = 1.6 #determined by trial and error to match energy range of instrument 
mV_per_ADC = 1000./4096.
baseline = 105
basenoise = 1
bits = 10  #use 12 for doing listmode but use 10 to compare traces to real trace files

#variables for integrating trace pulses into listmode events
thresh =  9.5     #units of mV  this is the pulse trigger threshold
int_i = 14      #integration time = 0.35 microsecs = 14 samples at 40MHz sampling or 10 samples at 500MHz = 20ns
dead_i = int_i     #deadtime = integration time
extend = 1    #extendable dead time parameter
escale = 6.63  #being used to scale the pulse integration value to energy in keV

#example spectrum of TGF energy deposit in a plastic detector
LgPl_Response = np.loadtxt('../original/LgPl_Response',usecols=(1),dtype=float)
bins = np.loadtxt('../original/LgPl_Response',usecols=(0),dtype=float)
#s = np.genfromtxt('/home/enp//Desktop/Emorpho Analysis Software and Calibration data/Emorpho Simulations/alt5SFT_noaa_plane_rough.out', usecols = (2), skip_footer=2)

spectrum = LgPl_Response
binenergies = bins*1e3 #units keV 
#spectrum[49]= 2000 #49 is 1000keV, 85 is 6800keV

#real plastic trace data
tracedata = pd.read_csv('../original/real_plastic_trace.csv')

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
    print(mean, std, counts, sigma)
    energies_bin = np.abs(ran.choice(binenergies, p=spectrum/sum(spectrum), size = len(times)))
    energies = np.empty(len(energies_bin))
    sigma_blur = 3
    for i in range(len(energies_bin)-1):
        r = np.random.normal(energies_bin[i],sigma_blur)
        energies[i] = r
    times = np.sort(times)#+100e-6 #100us of pre-TGF  
    
    
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
    return(itrace,energies,times)

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
pulsetimes, pulse = plastic_pulse(1.)
nsamples = len(pulse)
tdatatime = tracedata.Seconds[261:281]-tracedata.Seconds[261]
tdata = (tracedata.Tracesample[261:281]-25)/(max(tracedata.Tracesample)-25)

#calling the trace and listmode event functions  
trace,TGF_energies,TGF_Times = make_plastic_trace(counts, fwhm, spectrum,binenergies, dt, tstep, trace_length, mV_per_ADC, keV_per_area, baseline, basenoise, bits,mean,std)
energies, event_sample = plastic_trace_to_counts(trace, dt, tstep, thresh, baseline, extend, escale, int_i, dead_i)
energies = np.array(energies)
event_time = np.array(event_sample)*tstep*1e6 #converts samples to time in microseconds
trace_time = np.arange(len(trace))*tstep*1e6 #converts samples to time in microseconds

#calling the trace triggering function
trigger_time, trigger_index = trace_trigger(trace, trace_time)

# #array slicing the original TGF energies and time to match real detector constraints
TGF_Times=TGF_Times*1e6
# TGF_times = np.delete(TGF_Times,np.where(TGF_energies<140))
# TGF_energies = np.delete(TGF_energies,np.where(TGF_energies<140))


print('input counts = ',counts)                  
print('integrated counts = ', len(energies))
print('percent counted = ',100*len(energies)/counts)
print('average countrate in',TGF_duration*1e6,'us window = ',countrate/1e5,'e5')
print('listmode countrate = ',len(energies)/TGF_duration/1e5,'e5')
if trigger_time.size > 0:
    print('trace triggered at ',trigger_time,'us')


#fit single trace plot
plt.figure(figsize=(15,5))
plt.plot(pulsetimes*1e9,pulse,color='black',label='modeled trace pulse')
plt.scatter(pulsetimes*1e9,pulse)
plt.plot(tdatatime*1e9,tdata,color='red',label='real trace pulse')
plt.scatter(tdatatime*1e9,tdata)
#plt.xlim(-.5e-6,1.3e-6)
#plt.xlim(-.2,.6)
plt.xlabel('nanoseconds',fontsize=16)
plt.title('Modeled plastic pulse',fontsize=16)
plt.tick_params(labelsize=12)
plt.legend(fontsize=10)
plt.show()

#full trace
plt.figure(figsize=(10,5))
plt.plot(trace_time,trace,color='black')
plt.xlim(0,15)
#plt.xlim(100,110)
plt.ylim(50,600)
#plt.grid()
plt.ylabel('mV',fontsize=20)
plt.xlabel('microseconds',fontsize=20)
plt.title('Simulated plastic trace data',fontsize=20)
#plt.tick_params(labelsize=18)
#if trigger_time.size > 0:
#    plt.vlines(trigger_time,105,max(trace),color='red')
plt.show()

# simulated listmode energy vs time plot
plt.figure(figsize=(10,5))
plt.scatter(event_time,energies,color='black',s=5.0,label='List-Mode_Data')
plt.scatter(TGF_Times,TGF_energies,color='green',s=5.0,alpha=.2,label='Incident TGF Photons')
#plt.grid(which='both')
#plt.xlim(-10,500)
plt.xlim(0,15)
plt.ylim(120,20000)
plt.yscale('log')
plt.ylabel('Energy keV',fontsize=20)
plt.xlabel('microseconds',fontsize=20)
plt.title('Simulated plastic list-mode data',fontsize=20)
plt.tick_params(labelsize=18)
plt.legend()
plt.show()


# NNLSR Deconvolution Listmode
print(trace.size)
threshold = 1
nnlsr_size = 2000

base_est, _ = scipy.stats.mode(trace)
trace -= base_est

area_per_peak = np.sum(pulse) / max(pulse)
mV_per_keV = mV_per_ADC / (keV_per_area * area_per_peak)
trace /= mV_per_keV

if trace.size <= nnlsr_size:
    blocks = 1
else:
    blocks = trace.size // nnlsr_size
    if blocks * nnlsr_size != trace.size:
        blocks += 1
nnlsr_deconv = []
for i in range(blocks):
    data = trace[i * nnlsr_size:(i + 1) * nnlsr_size]
    print(data.shape, pulse.shape)
    nnlsr_deconv.append(td_nnlsr_deconvolve(data, pulse))
nnlsr_deconv = np.concatenate(nnlsr_deconv, axis=0)

mtime = np.arange(trace.size) * tstep * 1E6
mask = nnlsr_deconv > threshold

TGF_Times = np.array(TGF_Times)
TGF_energies = np.array(TGF_energies)
print(np.max(TGF_Times))

fig, axis = plt.subplots(1,1, figsize=(5, 5), dpi=200)
plt.scatter(event_time, energies, color='r', alpha=.25, label='FPGA Algo')
axis.plot(mtime[mask], nnlsr_deconv[mask], 'g', marker='.', markersize=10, linestyle='', label='NNLSR', alpha=.5)
axis.plot(TGF_Times, TGF_energies, 'k', marker='.', markersize=3, linestyle='', label='Events')
axis.legend()
plt.xlim([0, 50])
plt.ylim([1, 1E3])
plt.yscale('log')
plt.title('Plastic Scintillator FPGA vs NNLSR')
plt.show()