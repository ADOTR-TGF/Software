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
from Processing import td_nnlsr_deconvolve, td_convolve
from util.DataGen import nai_pulse

########################################################################### Test Repeated NNLSR on sim

# Load real trace data
trace_file_path = 'NaI_trace_filtered_220726_045157_buffer_0.txt'
real_trace = np.loadtxt(trace_file_path, skiprows=1)
# Extract time and voltage columns
real_trace_time = real_trace[:, 0]  # Relative time in µs
real_trace_ADC = real_trace[:, 1]  # ADC amplitudes

# load real listmode data
# Load NaI listmode data from the text file
nai_listmode_file = "NaI_listmode_filtered_220726_045157.txt"  # Use the saved file name
nai_listmode_data = np.loadtxt(nai_listmode_file, skiprows=1)  # Skip header row

# Extract time and energy
nai_listmode_time = nai_listmode_data[:, 0]  # Time in seconds of the day
nai_listmode_energy = nai_listmode_data[:, 1]  # Energy in keV


########################################################################### Constants
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
file_path = 'NaI_trace_pulse_220726_045157_buffer_0.txt'
pulse_data = np.loadtxt(file_path, skiprows=1)  # Skip the header row

# Extract time and amplitude
pulsetimes = pulse_data[:, 0]  # Time column (in µs)
pulse = pulse_data[:, 1]  # Amplitude column (normalized)
pulse = pulse[83:170]

# Normalize the pulse
pulse -= np.min(pulse)
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


trace = real_trace_ADC.copy() * mV_per_ADC
base_est, _ = scipy.stats.mode(trace, keepdims=True)
trace -= base_est

fig, axes = plt.subplots(1,1, figsize=(10, 6), dpi=200)
axes.plot(trace)


# Segment trace into sections #############################################################################
bound = 5
desired_pad = 2 * pulse.size

valid = np.logical_and(-bound < trace, trace < bound)
invalid = np.logical_not(valid)
index = np.arange(trace.size)

invalid_index = index[invalid]
invalid_spacing = np.diff(invalid_index)
# axes.plot(invalid_index[:-1], invalid_spacing)
# axes.plot(index[invalid], trace[invalid], marker='*', color='blue', linestyle='', alpha=.05)

optimal = invalid_spacing > desired_pad
a = invalid_index[:-1][optimal]
segment_bounds = np.concatenate((a+desired_pad//2, a + invalid_spacing[optimal]-desired_pad//2))
segment_bounds = np.sort(segment_bounds)
# axes.plot(segment_bounds, np.zeros_like(segment_bounds), marker='*', color='red', linestyle='', alpha=1)
plt.show()


# Seperate segments
no_event_traces =[]
event_traces = []
for i in range(segment_bounds.size-1):
    sub_trace = trace[segment_bounds[i]:segment_bounds[i+1]]

    if np.any(np.logical_or(sub_trace < -bound, bound < sub_trace)):
        event_traces.append((sub_trace, (segment_bounds[i], segment_bounds[i+1])))
    else:
        no_event_traces.append((sub_trace))

plt.figure(figsize=(8,4), dpi=200)
for sub_trace in no_event_traces:
    plt.plot(sub_trace, alpha=.2)
plt.title('Segments without Events')
plt.show()

plt.figure(figsize=(8,4), dpi=200)
for sub_trace, bounds in event_traces:
    plt.plot(sub_trace, alpha=.5)
plt.title('Segments With Events')
plt.show()

# NNLSR on Segments ##########################################################################

for sub_trace, bounds in event_traces:
    plt.figure(figsize=(8, 4), dpi=200)
    t = np.arange(bounds[0], bounds[1])
    plt.plot(t, sub_trace, alpha=1, label='Trace', zorder=0)

    # Dense NNLSR Deconv
    threshold = 2
    deconv = td_nnlsr_deconvolve(sub_trace, pulse)
    mask = deconv > threshold

    diff = np.diff(t[mask])
    print(bounds, diff)
    plt.plot(t[mask], deconv[mask], marker='.', linestyle='', label='Dense TD NNLSR Deconv', zorder=2)

    # Sum nearby events
    # Notide for the 12800 trace 2 does poorly. Need more...
    for n in range(2,6):
        summed = np.convolve(deconv, np.ones(n), mode='same')
        peaks,_ = scipy.signal.find_peaks(summed, prominence=3)
        if peaks.size > 0:
            plt.plot(t[peaks], summed[peaks],
                     marker='*', linestyle='', alpha=.3,
                     label='Conv [1]*{} Peaks '.format(n), zorder=1)
        else:
            plt.plot(t, summed,
                     marker='*', linestyle='', alpha=.3,
                     label='Conv [1]*{} Peaks '.format(n), zorder=1)

    plt.title('Trace [{}, {}]'.format(bounds[0], bounds[1]))
    plt.legend()
    plt.xlabel('Whole Trace Index')
    plt.show()

