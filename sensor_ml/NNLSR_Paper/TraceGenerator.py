import numpy as np
from util.DataGen import nai_pulse, continuous_time_trace, nai_pulse, plastic_pulse
import matplotlib.pyplot as plt
import os

# pulse_times, pulse = nai_pulse(1)
# pulse_times = pulse_times[:-1]
# pulse = pulse[:-1]

# peak_offset_samples = np.argmax(pulse)
# peak_offset_time = pulse_times[peak_offset_samples]

N_TRACES_PER_PARAM = 2

#determined by trial and error to match energy range of instrument on THOR data.
# modified for sampling rate difference with HERA
keV_per_area = .147
mV_per_ADC = 1000/4096
baseline = 0 # mV
basenoise = 1 # mV
bits = 10
clip = 1000 # mV
fs = 40E6 # new HERA sampling rate
total_time = 1E-5

count_rates = np.logspace(6,8,3)
sensor_types = ['NaI', 'plastic']

# for Lognormal traces
fwhm = 50 #50.0 #fwhm of the total TGF count distribution in units microseconds
mean = .007 #.7 #mean of the TGF trace distribution
std = 0 #.5 #determines the amount of assymetry in the TGF trace distribution

for sensor_type in sensor_types:
    for count_rate in count_rates.tolist():
        assert sensor_type in ['plastic', 'NaI']
        if sensor_type == 'plastic':
            _, decimal_kernel = plastic_pulse(1)
            spectrum = np.loadtxt('../original/LgPl_Response', usecols=(1), dtype=float)
            bins = 1E3 * np.loadtxt('../original/LgPl_Response', usecols=(0), dtype=float) # in kev
        else:
            _, decimal_kernel = nai_pulse(1, 101)
            spectrum = np.loadtxt('../original/NaI_Response',usecols=(1), dtype=float)
            bins = 1E3 * np.loadtxt('../original/NaI_Response',usecols=(0), dtype=float) # in kev

        for i in range(N_TRACES_PER_PARAM):
        # 2000E6 seems right at the moment, but why?
            out = continuous_time_trace(decimal_kernel, bins, spectrum, mV_per_ADC, keV_per_area,
                                        fs=fs, count_rate=count_rate, total_time=total_time, trace_type='constant', spectrum_interp_bins=4,
                                        lognormal_mean=mean, lognormal_std=std, lognormal_fwhm=fwhm,
                                        baseline=baseline, basenoise=basenoise, bits=bits, clip_magnitude=clip,
                                        seed=1,)

            trace, sample_t, sample_index, event_voltages, event_energies, event_times = out

            path = os.path.join('Data', '{}_ConstantTrace_{}_n{}_.npz'.format(sensor_type, count_rate, i))
            np.savez(path,
                     trace=trace,
                     sample_t=sample_t,
                     sample_index=sample_index,
                     event_voltages=event_voltages,
                     event_energies=event_energies,
                     event_times=event_times,
                     total_time=total_time)

            # if i == 0:
            #     trace_gt0 = trace[trace > 0]
            #     fig = plt.figure(figsize=(10, 4), dpi=200)
            #     plt.plot(1E6*pulse_times + 1.8, np.max(trace) * pulse)
            #     plt.plot(1E6 * sample_t, trace, label='Trace Pulse')
            #     if event_voltages.size < 20:
            #         microseconds = 1E6 * (event_times + peak_offset_time)
            #         plt.plot(microseconds, event_voltages, 'r.', label='Ground Truth Peaks')
            #         for i in range(event_times.size):
            #             t = microseconds[i] + 1
            #             v = event_voltages[i]
            #             plt.text(t, v, 'T={:.3f}'.format(t))
            #     else:
            #         microseconds = 1E6 * (event_times + peak_offset_time)
            #         plt.plot(microseconds, event_voltages, 'r.', label='Ground Truth Peaks')
            #     plt.xlabel('Microseconds')
            #     plt.legend()
            #     plt.xlim(0, 20)
            #     plt.show()