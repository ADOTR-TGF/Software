from sensor_ml.util.DataGen import *
from sensor_ml.util.Processing import *
from sensor_ml.util.Plotting import *

import numpy as np
import matplotlib.pyplot as plt

# Trace
sensor_type = 'NaI'
seed = 3
countrate = 5e6
total_time = 5e-5
noise_stdev = 1  # mV
bits = 8  # 8 bits is

repeat = 10

print('{} Photons'.format(countrate * total_time))

dt = np.float64(25e-9)  # sampling rate in seconds. 40MHz
sampling_ratio = 1

assert sensor_type in ['plastic', 'NaI']
if sensor_type == 'plastic':
	_, decimal_kernel = plastic_pulse(1)
	spectrum = np.loadtxt('../original/LgPl_Response', usecols=(1), dtype=float)
	bins = 1E3 * np.loadtxt('../original/LgPl_Response', usecols=(0), dtype=float)  # in kev
else:
	_, decimal_kernel = nai_pulse(1, 101, sampling_ratio)
	spectrum = np.loadtxt('../original/NaI_Response', usecols=(1), dtype=float)
	bins = 1E3 * np.loadtxt('../original/NaI_Response', usecols=(0), dtype=float)  # in kev

plt.figure(figsize=(3,3))
plt.plot(decimal_kernel)

keV_per_area = .147  # determined by trial and error to match energy range of instrument
mV_per_ADC = 1000. / 4096.
area_per_peak = np.sum(decimal_kernel) / max(decimal_kernel)
mV_per_keV = mV_per_ADC / (keV_per_area * area_per_peak)
print('mV_per_keV', mV_per_keV)

#########################################################################################################################
# Spectrum trace
trace, time_vector, volts_list, volts_time_index = spectrum_trace(
	count_rate_=countrate, dt_=dt, total_time_=total_time,
	pulse_=decimal_kernel, bin_energies_=bins, spectrum_=spectrum,
	mV_per_keV_=mV_per_keV, noise_std_=noise_stdev, baseline_=0,
	sampling_ratio_=sampling_ratio, discretize=True, bits_=bits,
	seed_=seed, clip=False, debug=False)

print(
	trace.shape,
	time_vector.shape,
	volts_list.shape,
	volts_time_index.shape,
)

##########################################################################################################################

N = trace.size
trace_fft_noise = trace

fig, axes = plt.subplots(1, 1, figsize=(8,6), dpi=400)
plot_photons(axes, volts_time_index, volts_list, label_='{} Photons'.format(len(volts_list)), color='r', alpha=.5)
xlim = [0, 2000]
axes.set_xlim(xlim)
axes.set_ylabel('Discretized mV')
axes.set_xlabel('Time Index')
plt.show()


fig, axes = plt.subplots(1, 1, figsize=(8,6), dpi=400)
axes.plot(trace_fft_noise, label='Noise stdev={}, bits={}: Trace'.format(noise_stdev, bits), alpha=.8)
axes.set_xlim(xlim)
axes.legend(loc=1)
axes.set_ylabel('Discretized mV')
axes.set_xlabel('Time Index')
axes.grid()
axes.legend()
plt.show()



plt.figure(figsize=(8,3), dpi=200)
times, pulse = nai_pulse(1)

shifts = np.array([10, 20, 45, 50, 80, 81, 82, 125])
scale = np.array([1, 1, 1, 1, 1, 1, 2, 2])
energies = np.zeros(N)
energies[shifts] = scale

for i, pair in enumerate(zip(shifts, scale)):
	shift, energy = pair
	if i == 0:
		plt.plot([shift, shift], [0, energy], 'r', label='Photons')
	else:
		plt.plot([shift, shift], [0, energy], 'r')

plt.plot(pulse+2.5, label='Response Kernel')
conv = fft_convolve(energies, pulse, 10000)[0:len(energies)]
plt.plot(conv, label='Convolved Trace')
plt.xlim([0, np.max(shifts) + 100])
plt.legend(loc=7)
plt.show()
plt.xlabel('Microseconds')
plt.ylabel('')