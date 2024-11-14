#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 14:50:33 2023

@author: enp
"""

import pandas as pd
from util.DataGen import *
from util.Plotting import *
from util.Processing import *
from util.metrics import *

rcParams['figure.figsize'] = [15, 7]
import scipy.signal as signal
#import Response_matrix

#variables for creating the trace
countrate= 5e7
fwhm = 50.0 
# TGF_duration = fwhm*3e-6
TGF_duration = fwhm*3e-8
counts = int(countrate*TGF_duration) #total counts incident on the detector   
#fwhm = 50.0 #fwhm of the total TGF count distribution in units microseconds
#TGF_duration = fwhm*3e-6 #this is a really rough estimate to get a rough estimate of the count rate
#countrate = int(counts/TGF_duration)
mean = .7 #mean of the TGF trace distribution
std = .5 #detemines the amount of asymetry in the TGF trace distribution
dt = 1e-9 # seconds before pulse
tstep = 25e-9 #sampling rate in seconds. 40MHz
trace_length = 28000 #number of samples in a trace file (700us at 40MHz)
keV_per_area = .147 #determined by trial and error to match energy range of instrument 
mV_per_ADC = 1000./4096.
specscale_keV = 5.0  #spectrum scaling i.e. keV/line in the spectrum file
baseline = 110
basenoise = .01 #units mV
quantize = True
bits = 12  #use 12 for doing listmode but use 10 to compare traces to real trace files

#variables for integrating trace pulses into listmode events
thresh = 8.0     #units of mV  this is the pulse trigger threshold
int_i = 50      #integ.ration time = 1.25 microsecs = 50 samples at 40MHz sampling 
dead_i = int_i     #deadtime = integration time
extend = 1    #extendable dead time parameter
escale = .63  #being used to scale the pulse integration value to energy in keV. experimentally determined.

#example spectrum of TGF energy deposit in a detector
NaI_Response = np.loadtxt('original/NaI_Response',usecols=(1),dtype=float)
bins = np.loadtxt('original/NaI_Response',usecols=(0),dtype=float)
#s = np.genfromtxt('/home/enp//Desktop/Emorpho Analysis Software and Calibration data/Emorpho Simulations/alt5SFT_noaa_plane_rough.out', usecols = (2), skip_footer=2)

spectrum = NaI_Response
binenergies = bins*1e3 #units keV 
#spectrum[49]= 2000 #49 is 1000keV, 85 is 6800keV

#real NaI trace example data
tracedata = pd.read_csv('original/real_nai_trace.csv')

def nai_pulse(a):
    sos1 = signal.butter(3, 0.25e7, btype='low', analog=False, output='sos', fs=40e6)
    sos2 = signal.butter(2, .145e7, btype='low', analog=False, output='sos', fs=40e6)
    sos3 = signal.butter(1, .053e7, btype='low', analog=False, output='sos', fs=40e6)
    t = np.arange(0.,2.5e-6,25e-9)
    y = t*0
    y[4]=1
    fil1 = signal.sosfilt(sos1,y)
    fil1 = fil1*a/np.max(fil1)
    fil2 = signal.sosfilt(sos2,y)
    fil2 = fil2*a/np.max(fil2)
    fil3 = signal.sosfilt(sos3,y)
    fil3 = fil3*a/np.max(fil3)
    fil = np.concatenate((fil1[0:11],fil2[11:17],fil3[17:]))
    return(t,fil)

def make_nai_trace(counts,fwhm,spectrum,binenergies,dt,tstep,trace_length,mV_per_ADC,keV_per_area,specscale_keV,baseline,basenoise,bits,mean,std):

    #Freeze the random number seed for reproducibility:
    seed=101
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
    # the mean and std can be adjusted to move the trace distribution left or right (mean) and adjust the assymetry (std)
    times = ran.lognormal(mean,std,counts)*sigma

    #times = ran.uniform(low=0,high=7.0,size=counts)*sigma 
    #line = np.abs(ran.choice(len(spectrum),  p=spectrum/sum(spectrum), size = len(times))) #chooses energies from an input spectrum based on probabilites 
    #energies = line*specscale_keV + 5.   #spectrum starts at 5keV
    energies = np.abs(ran.choice(binenergies, p=spectrum/sum(spectrum), size=len(times)))
    times = np.sort(times)+100e-6 #100us of pre-TGF
    #print(times)
    
    #define the pulse shape once
    pulsetimes,pulse = nai_pulse(1.)
    nsamples = len(pulse)

    area_per_peak = np.sum(pulse)/max(pulse)
    mV_per_keV = mV_per_ADC/(keV_per_area*area_per_peak)

    # energy_time_indeces = np.zeros(times.shape)
    # #For every incident count, create a pulse and add it to the trace:
    # for i, t in enumerate(times):
    #     t_index = (sampletimes > t-dt).nonzero()
    #     t_index0 = (t_index[0])[0]
    #     energy_time_indeces[i] = t_index0
    #     navailable =  len(trace[t_index0:t_index0+nsamples])
    #     if navailable == nsamples:
    #         trace[t_index0:t_index0+nsamples] += pulse*energies[i]
    #     else:
    #         print('Make NAI Trace: N not available. Is the distribution lognornal or uniform')
    # print(energy_time_indeces)

    # TODO README -- below
    # Original method (above) and below code to make final trace are different because
    # of how the indeces are defined...
    # notice if printed they are off by one sometimes. I round to the nearest whereas the above is  rounding down.
    # This only shows up when using lognormal distribution with decimal indeces...

    stack_n = times.size
    stacked = np.tile(sampletimes, (1, stack_n))
    abs_diff = np.abs(stacked - times[:, None])
    energy_time_indeces = np.argmin(abs_diff, axis=1)

    # remove values with time index too large
    mask = energy_time_indeces < sampletimes.size - pulse.size
    energy_time_indeces = energy_time_indeces[mask]
    times = times[mask]
    energies = energies[mask]
    # print(energy_time_indeces)
    for i, t in enumerate(energy_time_indeces):
        trace[t:t+nsamples] += pulse * energies[i]

    #scale to mV, add baseline and noise, and clip:
    trace = trace*mV_per_keV
    trace += baseline
    trace += ran.randn(n)*basenoise
    trace[trace > 1000] = 1000

    print(trace)

    if quantize:
        #digitize:
        itrace = trace/1000.*2**bits
        for i in range(len(itrace)):
            itrace[i] = float(int(itrace[i]))
        itrace = itrace*1000./2**bits
    else:
        itrace = trace
    
    return itrace, times, energies, energy_time_indeces

def nai_trace_to_counts(trace,dt,tstep,thresh,baseline,extend,escale,int_i,dead_i):
    
    
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
                i += dead_i
              
                #Paralyzable deadtime:keep extending the window as long as the last sample of the last interval is still high.
                if (extend > 0):
                    while (trace[i-1] > thresh+baseline and i < n-di-extend):
                        i += extend                  
        else:
                i += 1
    
    return(energies, sample_times)

def trace_trigger(trace,trace_time):
    n = 30
    m = 10500
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
pulsetimes,pulse = nai_pulse(1.)
nsamples = len(pulse)
tdatatime = tracedata.Seconds[253:350]-tracedata.Seconds[253]
tdata = (tracedata.Tracesample[253:350]-27)/(max(tracedata.Tracesample)-27)

#calling the trace and listmode event functions  
trace, times, true_energies, energy_time_indeces = make_nai_trace(counts, fwhm, spectrum,binenergies, dt, tstep, trace_length, mV_per_ADC, keV_per_area, specscale_keV, baseline, basenoise, bits,mean,std)
energies, event_sample = nai_trace_to_counts(trace, dt, tstep, thresh, baseline, extend, escale, int_i, dead_i)
energies = np.array(energies)
event_time = np.array(event_sample)*tstep*1e6 #converts samples to time in microseconds
trace_time = np.arange(len(trace))*tstep*1e6 #converts samples to time in microseconds

#calling the trace triggering function
trigger_time, trigger_index = trace_trigger(trace, trace_time)


print('input counts = ',counts)
print('\nFPGA Algo')
print('integrated counts = ', len(energies))
print('percent counted = ',100*len(energies)/counts)
print('average countrate in',TGF_duration*1e6,'us window = ',countrate/1e5)
print('listmode countrate = ',len(energies)/TGF_duration/1e5)
if trigger_time.size > 0:
    print('trace triggered at ',trigger_time,'us')


# fit single trace plot
plt.figure(figsize=(5,5))
plt.plot(pulsetimes*1e6,pulse,color='black',label='modeled trace pulse')
#plt.scatter(tdatatime,tdata)
#plt.scatter(pulsetimes,pulse)
plt.plot(tdatatime*1e6,tdata,color='red',label='real trace pulse')
plt.xlabel('microseconds',fontsize=16)
plt.title('Modeled NaI pulse',fontsize=16)
#plt.xlim(-.5e-6,3.0e-6)
plt.tick_params(labelsize=12)
plt.legend(fontsize=12)

# Full trace
plt.figure(figsize=(10,5))
plt.plot(trace_time,trace,color='black')
#plt.xlim(0,700)
plt.xlim(110,175)
#plt.ylim(105,1100)
#plt.grid()
plt.ylabel('mV',fontsize=20)
plt.xlabel('microseconds',fontsize=20)
plt.title('Simulated NaI trace data',fontsize=20)
plt.tick_params(labelsize=18)
if trigger_time.size > 0:
    plt.vlines(trigger_time,110,max(trace),color='red')

# simulated listmode energy vs time plot
plt.figure(figsize=(10,5))
plt.scatter(event_time,energies,color='black',s=10.0)
plt.plot(times*1e6, true_energies, color='r', marker='.', linestyle='', label='Ground Truth')
#plt.grid(which='both')
#plt.xlim(0,700)
plt.xlim(110, 175)
#plt.ylim(55,10000)
plt.yscale('log')
plt.ylabel('Energy keV',fontsize=20)
plt.xlabel('microseconds',fontsize=20)
plt.title('Simulated NaI list-mode data',fontsize=20)
plt.tick_params(labelsize=18)
plt.show()


############################ new
print('\nDeconvolution')
print(len(trace))

energies_ts = np.zeros(trace.size)
for i in range(true_energies.shape[0]):
    e = true_energies[i]
    index = energy_time_indeces[i]
    energies_ts[int(index)] = e
area_per_peak = np.sum(pulse)/max(pulse)
mV_per_keV = mV_per_ADC/(keV_per_area*area_per_peak)

f_conv = fft_convolve(energies_ts, pulse)
f_conv *= mV_per_keV
f_conv += baseline

plt.figure(figsize=(10, 10), dpi=400)
deconv = fft_deconvolve(trace-baseline, pulse)
# deconv = wiener_deconvolve(trace-baseline, pulse, basenoise)

# w = np.where(deconv > 1)
# deconv_filt = deconv[w]
# trace_time_filt = trace_time[w]
trace_time_filt = trace_time

# scaled = deconv/mV_per_keV + baseline
scaled = deconv + baseline
true_volts = true_energies * mV_per_keV + baseline
true_energies = true_volts #TODO remove this and replace vars

plt.plot(trace_time, scaled, label='Deconvolution')
plt.ylabel('mV',fontsize=20)
plt.xlabel('microseconds',fontsize=20)
plt.title('Deconvoluted NaI list-mode data',fontsize=20)
plt.tick_params(labelsize=18)

plt.plot(times*1e6, true_energies, color='r', marker='.', linestyle='', label='Ground Truth')
plt.xlim([np.min(trace_time_filt), np.max(trace_time_filt)])
plt.xlim([100, 300])
# plt.xlim([150, 175])
# plt.ylim([110, 200])
plt.legend()
plt.show()

safety_factor = 1 #TODO fix this
threshold = baseline + safety_factor # const at end to stop noiseless trace from having too many
threshold = 120
thresh_volts, thresh_indeces = threshold_listmode(scaled, threshold)
thresh_times = trace_time[thresh_indeces]*1e6
print('Deconv Threshold Detected {}'.format(thresh_volts.size))
# print('SUM deconv values, true values', np.sum(scaled), np.sum(true_energies))
# print('SUM thresholded values, true values', np.sum(thresh_volts), np.sum(true_energies))

plt.figure(figsize=(10, 10), dpi=400)
plt.plot(thresh_times/1e6, thresh_volts, color='k', marker='.', linestyle='', label='Deconv Listmode')
plt.plot(times*1e6, true_energies, color='r', marker='o', linestyle='', label='Ground Truth', alpha=.25)
lim = [np.min(trace_time_filt), np.max(trace_time_filt)]
plt.plot(lim, [threshold, threshold], 'r--', label='Baseline')
plt.plot(lim, [threshold, threshold], 'r-', label='Detection Threshold')
plt.title('FD Deconvolution List-mode')
plt.xlim(lim)
plt.xlim([100, 300])
# plt.xlim([150, 175])
plt.ylabel('mV',fontsize=20)
plt.xlabel('microseconds',fontsize=20)
plt.legend()
plt.show()

