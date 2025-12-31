#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 21:16:35 2024

@author: enp
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.signal as signal
from Processing import td_nnlsr_deconvolve

# Load real trace data
trace_file_path = 'data/NaI_trace_filtered_220726_045157_buffer_0.txt'
real_trace = np.loadtxt(trace_file_path, skiprows=1)
# Extract time and voltage columns
real_trace_time = real_trace[:, 0]  # Relative time in µs
real_trace_ADC = real_trace[:, 1]  # ADC amplitudes

# load real listmode data
# Load NaI listmode data from the text file
nai_listmode_file = "data/NaI_listmode_filtered_220726_045157.txt"  # Use the saved file name
nai_listmode_data = np.loadtxt(nai_listmode_file, skiprows=1)  # Skip header row

# Extract time and energy
nai_listmode_time = nai_listmode_data[:, 0]  # Time in seconds of the day
nai_listmode_energy = nai_listmode_data[:, 1]  # Energy in keV

# Constants
mV_per_ADC = 1000. / 4096.
tstep = 12e-9  # Sampling rate in seconds (80 MHz)
trace_length = len(real_trace)  # Use real trace length
dt = 1e-9  # Delay parameter
thresh = 5 / mV_per_ADC  # Pulse trigger threshold in ADC using mV conversion
baseline = 109 / mV_per_ADC  # Estimate baseline from data in ADC using mV conversion
extend = 1
Ch_per_int = 0.499  # got this from Dr. Smith
E_per_ch = 0.251  # keV got this from Dr. Smith
E_per_int = E_per_ch * Ch_per_int  # keV
int_i = 96  # Integration time (samples)
dead_i = int_i  # Dead time

# Load the real pulse data for the kernal
file_path = 'data/NaI_trace_pulse_220726_045157_buffer_0.txt'
pulse_data = np.loadtxt(file_path, skiprows=1)  # Skip the header row

# Extract time and amplitude
pulsetimes = pulse_data[:, 0]  # Time column (in µs)
pulse = pulse_data[:, 1]  # Amplitude column (normalized)
pulse = pulse[1:250]

# Normalize the pulse
pulse /= np.max(pulse)  # Ensures the peak is at 1.0
print(pulse.shape, np.argmax(pulse), np.max(pulse), np.min(pulse))

# pulsetimes and pulse are now equivalent to nai_pulse(1.)
nsamples = len(pulse)


# Pulse Integration Method that was used with simulated traces
def nai_trace_to_counts(trace, dt, tstep, thresh, baseline, extend, E_per_int, int_i, dead_i):
    energies = []
    sample_times = []
    n = trace.size
    di = int(dt / tstep)  # Delay in samples
    i = di

    while i < n - dead_i - 1:
        if trace[i] > thresh + baseline:  # Detect pulse above threshold
            # Integrate pulse over int_i samples starting with the first sample above threshold
            clip = trace[i - 5:i - 6 + int_i]
            energy = np.sum(clip - baseline)
            # energy = np.sum(trace[i:i + int_i] - baseline)
            norm_energy = energy * E_per_int  # Convert energy into keV
            energies.append(norm_energy)
            sample_times.append(i)
            i += dead_i  # Apply dead time

            # Paralyzable dead time extension
            if extend > 0:
                while trace[i - 1] > thresh + baseline and i < n - di - extend:
                    i += extend
        else:
            i += 1

    return np.array(energies), np.array(sample_times)


# Perform pulse integration
energies, event_sample = nai_trace_to_counts(real_trace_ADC, dt, tstep, thresh, baseline, extend, E_per_int, int_i,
                                             dead_i)
event_time = event_sample * tstep * 1e6  # Convert samples to time in microseconds

# Prepare the real trace for NNLSR
trace = real_trace_ADC.copy()
base_est, _ = scipy.stats.mode(trace, keepdims=True)
trace -= base_est

# NNLSR Deconvolution
threshold = 40  # keeps the deconvolution energy output above the real lower limit of the detector # 40
nnlsr_size = min(1000, trace.size)
blocks = (trace.size + nnlsr_size - 1) // nnlsr_size
nnlsr_deconv = []

for i in range(blocks):
    data = trace[i * nnlsr_size:(i + 1) * nnlsr_size]
    nnlsr_deconv.append(td_nnlsr_deconvolve(data, pulse))
nnlsr_deconv = np.concatenate(nnlsr_deconv, axis=0)

nnlsr_energy = nnlsr_deconv * 5.  # Convert channels to energy using real list mode data for calibration
mtime = np.arange(
    trace.size) * tstep * 1e6 + 1.7  # The 1.7 adjustment aligns the timing of the listmode data and deconvolved data by eye for the isolated pulses at 100us and ~130us
mask = nnlsr_energy > threshold

''' #uncomment to print out statitics
print('NNLSR Count = ',len(nnlsr_energy[mask]))
print('Listmode Count = ',len(nai_listmode_energy))
print('mean NNLSR = ',np.mean(nnlsr_energy[mask]))
print('mean Listmode = ',np.mean(nai_listmode_energy))
print('std NNLSR = ',np.std(nnlsr_energy[mask]))
print('std Listmode = ',np.std(nai_listmode_energy))
print('mean NNLSR time = ',np.mean(mtime[mask]))
print('mean Listmode time = ',np.mean(nai_listmode_time*0.96))
print('std NNLSR time = ',np.std(mtime[mask]))
print('std Listmode time = ',np.std(nai_listmode_time*0.96))
'''

# Plot 1: Real Trace
figure = plt.figure(figsize=(12, 6), dpi=300)
ax1 = figure.add_subplot()
ax2 = ax1.twinx()
trace_time = np.arange(len(real_trace)) * tstep * 1e6
ax1.plot(trace_time, real_trace_ADC * mV_per_ADC, color='blue', alpha=0.8, label='Real Trace')
ax2.scatter(event_time, energies, color='black', marker='.', s=100, label='Synthetic Pulse Integration (FPGA)')
ax2.plot(mtime[mask], nnlsr_energy[mask], 'r.', markersize=20, label='NNLSR Deconvolution', alpha=.5)
ax1.set_xlabel('Time (µs)', fontsize=18)
ax1.set_ylabel('mV', fontsize=18)
# ax1.set_ylim(100,140)
ax2.set_ylabel('Energy (keV)', fontsize=18)
plt.title('Real NaI Trace from THOR Observation Campaign', fontsize=20)
# plt.ylim(100,230)
# ax1.set_xlim(10,15)
ax1.set_xlim(0, 290)
# ax1.set_xlim(15, 35)
# ax1.set_xlim(30, 70)
ax2.set_yscale('log')
ax2.set_ylim(10, 10000)
ax2.tick_params(axis='y', labelsize=12)

# Add listmode data to the plot
ax2.scatter(
    nai_listmode_time * 0.96,
    # there is a bug in the timing alignment for the THOR listmode data causing it to be slighly out of alignment with the trace. multiplying by 0.96 fixes the issue (temporarily until I can fix it at the source)
    nai_listmode_energy,
    color='purple',
    marker='x',
    s=125,
    label='NaI Real Listmode Data',
    alpha=1.0
)

plt.legend(loc=2, fontsize=12)
plt.show()

