#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 21:16:35 2024

@author: enp
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import scipy
import scipy.signal as signal
from Processing import td_nnlsr_deconvolve, td_convolve
from util.DataGen import nai_pulse

figures = '/home/vaunclagett/chaffin/Software/sensor_ml/THOR/figures/THORDeconvolve1_out'

########################################################################### Test Repeated NNLSR on sim

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
file_path = 'data/NaI_trace_pulse_220726_045157_buffer_0.txt'
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

# Seperate segments
no_event_traces =[]
event_traces = []
for i in range(segment_bounds.size-1):
    sub_trace = trace[segment_bounds[i]:segment_bounds[i+1]]

    if np.any(np.logical_or(sub_trace < -bound, bound < sub_trace)):
        event_traces.append((sub_trace, (segment_bounds[i], segment_bounds[i+1])))
    else:
        no_event_traces.append((sub_trace))

for bounds in event_traces:
    plt.plot(bounds[1], np.zeros(2), marker='*', linestyle='')

filename = 'Trace.png'
path = os.path.join(figures, filename)
plt.savefig(path)
plt.close()

plt.figure(figsize=(8,4), dpi=200)
for sub_trace in no_event_traces:
    plt.plot(sub_trace, alpha=.2)
plt.title('Segments without Events')
filename = 'TraceSegmnetsWithoutEvents.png'
path = os.path.join(figures, filename)
plt.savefig(path)
plt.close()

plt.figure(figsize=(8,4), dpi=200)
for sub_trace, bounds in event_traces:
    plt.plot(sub_trace, alpha=.5)
plt.title('Segments With Events')
filename = 'TraceSegmnetsWithEvents.png'
path = os.path.join(figures, filename)
plt.savefig(path)
plt.close()

# NNLSR on Segments ##########################################################################
# unnecessaryliy complex, but more robust...
bit_width = scipy.stats.mode(np.diff(np.sort(np.unique(trace))))[0]
print('Bit width =', bit_width)

for sub_trace, bounds in event_traces:
    fig, axes = plt.subplots(1,1, figsize=(16,10), dpi=200)
    axes = [axes]

    t = np.arange(bounds[0], bounds[1])
    time = tstep * t * 1E6
    axes[0].plot(time, sub_trace, alpha=1, label='Trace', zorder=0)

    # Dense NNLSR Deconv
    threshold = 2
    deconv = td_nnlsr_deconvolve(sub_trace, pulse)
    mask = deconv > threshold

    diff = np.diff(t[mask])
    # print()
    # print(bounds, sub_trace.size, pulse.size)
    # axes[0].plot(t[mask], deconv[mask], marker='.', linestyle='', label='Dense TD NNLSR Deconv', zorder=2)

    # Sum nearby events
    # Notice for the 12800 trace 2 does poorly. Need more...
    # for n in range(2,8):
    for n in range(6,7):
        summed = np.convolve(deconv, np.ones(n), mode='same')
        peaks,_ = scipy.signal.find_peaks(summed, prominence=3)
        if peaks.size > 0:
            axes[0].plot(time[peaks], summed[peaks],
                     marker='*', linestyle='', alpha=1,
                     label='Moving Sum [{}] Peaks'.format(n), zorder=1)
        else:
            axes[0].plot(time, summed,
                     marker='*', linestyle='', alpha=1,
                     label='Moving Sum [{}] Peaks'.format(n), zorder=1)

    axes[0].set_title('Trace [{}, {}]'.format(bounds[0], bounds[1]), fontsize=15)
    axes[0].legend(fontsize=15)
    axes[0].set_xlabel('Microseconds', fontsize=15)
    axes[0].set_ylabel('mV', fontsize=15)
    # axes[0].plot(np.arange(pulse.size)+bounds[0],pulse*100)

    # # Try an upsampled trace
    # upsample_factor = 2
    #
    # if sub_trace.size % 2 == 1:
    #     sub_trace = np.concatenate((sub_trace, np.array([0])))
    #
    # a = scipy.fft.fft(sub_trace)
    # b = np.zeros(upsample_factor * sub_trace.size).astype(np.complex128)
    # # b[:a.size] = scipy.fft',.fftshift(a)
    # # print('a,b', a.size, b.size)
    # b[:a.size//2] = a[:a.size//2]
    # b[b.size - a.size // 2:] = a[a.size // 2:]
    # upsampled_subtrace = upsample_factor * np.abs(np.fft.ifft(b))
    # print(upsampled_subtrace.size)
    #
    # # re-Quantize trace - we dnt need to do this... this is a processing, not sim step
    # # bit_index = np.arange(int(2 * np.max(trace) // bit_width)) # more bins than needed
    # # bins = bit_width * bit_index
    # # bin_choice_index = np.digitize(upsampled_subtrace, bins=bins)
    # # upsampled_subtrace = bins[bin_choice_index]
    #
    # if pulse.size % 2 == 1:
    #     pulse = np.concatenate((pulse, np.array([0])))
    # # print(pulse.size)
    # a = scipy.fft.fft(pulse, n=sub_trace.size)
    # b = np.zeros(upsample_factor * sub_trace.size).astype(np.complex128)
    # # print('a,b', a.size, b.size)
    # b[:a.size//2] = a[:a.size//2]
    # b[b.size - a.size // 2:] = a[a.size // 2:]
    # upsampled_pulse = upsample_factor * np.abs(np.fft.ifft(b))
    #
    # # print(upsampled_subtrace.size, upsampled_pulse.size, pulse.size)
    # upsampled_pulse = upsampled_pulse[:pulse.size * upsample_factor]
    # # print(upsampled_pulse.size, pulse.size * upsample_factor)
    #
    # upsampled_time = np.arange(upsampled_subtrace.size) / upsample_factor + bounds[0]
    #
    # axes[1].plot(upsampled_time, upsampled_subtrace)
    # axes[1].plot(upsampled_time[:upsampled_pulse.size], upsampled_pulse*np.max(upsampled_subtrace), label='Scaled Upsampled Pulse')
    #
    # threshold = 2
    # upsampled_deconv = td_nnlsr_deconvolve(upsampled_subtrace, upsampled_pulse)
    # mask = upsampled_deconv > threshold
    #
    # axes[1].plot(upsampled_time[mask], upsampled_deconv[mask], marker='.', linestyle='',
    #          label='TD NNLSR Deconv'.format(upsample_factor), zorder=1)
    # axes[1].legend()
    # axes[1].set_title('Trace [{}, {}] at {}x Upsampling'.format(bounds[0], bounds[1], upsample_factor))

    filename = 'Segment_{}_{}.png'.format(bounds[0], bounds[1])
    path = os.path.join(figures, filename)
    plt.savefig(path)
    plt.close()



