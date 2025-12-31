import numpy as np
import os
import matplotlib.pyplot as plt

from util.DataGen import nai_pulse, plastic_pulse
from util.Processing import trace_to_counts, threshold_nnlsr_deconvolve, threshold_listmode
from util.metrics import volts_counted_hist

mV_per_keV = 1000/4096

# Overall Parmeters:
sensor_type = 'NaI'

# Dense Thresholded NNLSR Parameters
dense_deconv_threshold = 1

# FPGA Algorithm Parameters...
thresh = 8.0  # units of mV  this is the pulse trigger threshold
int_i = 50  # integ.ration time = 1.25 microsecs = 50 samples at 40MHz sampling
dead_i = int_i  # deadtime = integration time
extend = 1  # extendable dead time parameter
escale = .63  # being used to scale the pulse integration value to energy in keV. experimentally determined.
baseline=0
dt = 1 / 40E6

# Load Spectra and Pulse Template/Kernels
assert sensor_type in ['plastic', 'NaI']
if sensor_type == 'plastic':
    _, decimal_kernel = plastic_pulse(1)
    spectrum = np.loadtxt('../original/LgPl_Response',usecols=(1), dtype=float)
    bin_edges = 1E3 * np.loadtxt('../original/LgPl_Response',usecols=(0), dtype=float) # KeV
    #bins = bin_edges[:-1] #+ np.diff(bin_edges)
else:
    _, decimal_kernel = nai_pulse(1, 101)
    spectrum = np.loadtxt('../original/NaI_Response',usecols=(1), dtype=float)
    bin_edges = 1E3 * np.loadtxt('../original/NaI_Response',usecols=(0), dtype=float) # KeV
    bins = bin_edges[:-1] + np.diff(bin_edges)

# Set Algorithm KWARGS
threshold_nnlsr_kwargs = {'threshold': dense_deconv_threshold, 'kernel':decimal_kernel}
fpga_kwargs= {'thresh':thresh, 'dt':0 , 'tstep':dt, 'int_i':int_i, 'dead_i':dead_i,
              'extend':extend, 'escale':escale, 'baseline':baseline}

trace_paths = []
for root, dirs, files in os.walk('Data'):
    for file in files:
        trace_paths.append(os.path.join(root, file))

# Load in Ground Truth Data
counts_by_algorithm = []
true_counts = np.zeros_like(bins)
for trace_path in trace_paths:
    data = []
    npz_dict = np.load(trace_path)
    for key in npz_dict.keys():
        data.append(npz_dict[key])

    trace, sample_t, sample_index, event_voltages, event_energies, event_times, total_time = data
    _, _, counts, _ = volts_counted_hist(event_voltages, event_voltages, bins=bin_edges)

    true_counts += counts
counts_by_algorithm.append(true_counts)

# Run Algorithms on Traces
for algorithm, kwargs in zip([threshold_nnlsr_deconvolve, trace_to_counts],
                                     [threshold_nnlsr_kwargs ,fpga_kwargs],):

    algorithm_counts = np.zeros_like(bins)

    for trace_path in trace_paths:

        # Load data for each trace
        data = []
        npz_dict = np.load(trace_path)
        for key in npz_dict.keys():
            data.append(npz_dict[key])

        trace, sample_t, sample_index, event_voltages, event_energies, event_times,total_time = data

        volts, indeces = algorithm(trace, **kwargs)
        _, _, counts, _ = volts_counted_hist(event_voltages, volts, bins=bin_edges)
        algorithm_counts += counts

    counts_by_algorithm.append(algorithm_counts)

fig, axes = plt.subplots(1, 1, figsize=(10, 8), dpi=200)

print(len(counts_by_algorithm))

label_strings = ['True Counts', 'Threshold NNLSR', 'FPGA']
ss = [100, 20, 10, 2]
colors = ['r','g','orange','b']
for counts, string, s, color in zip(counts_by_algorithm, label_strings, ss, colors):
    gt0 = np.where(counts > 0)[0]
    plt.scatter(bins[:-1][gt0], counts[gt0], label=string, facecolors='none',
                s=s, marker='.', edgecolors=color, alpha=1)


plt.xscale('log')
plt.yscale('log')

size = 20
ticksize = 15
plt.xlabel('mV', fontsize=size)
plt.title('KeV', fontsize=size)
plt.ylabel('Counts', fontsize=size)
plt.legend()
plt.xticks(fontsize=ticksize)
plt.yticks(fontsize=ticksize)

top_y = axes.twiny()
top_y.set_xscale('log')
xlim = axes.get_xlim()

top_y.set_xlim(xlim)
ticks = np.array(axes.get_xticks())
ticks_kev = ticks / mV_per_keV

ticks_kev = np.log10(ticks_kev)
ticks_kev = 10 ** (np.round(ticks_kev))

top_y.set_xticks(ticks_kev)
strings = []
for num in ticks_kev:
    strings.append("{:0.0e}".format(num))
top_y.set_xticklabels(strings, fontsize=ticksize)
plt.show()
# plt.savefig('Method_Comparison_{}_Counts'.format(sensor_type))



divisor = len(trace_paths) * total_time
for counts, string, s, color in zip(counts_by_algorithm, label_strings, ss, colors):
    counts = counts / divisor

    gt0 = np.where(counts > 0)[0]
    plt.scatter(bins[:-1][gt0], counts[gt0], label=string, facecolors='none',
                s=s, marker='.', edgecolors=color, alpha=1)

plt.xscale('log')
plt.yscale('log')

size = 20
ticksize = 15
plt.xlabel('mV', fontsize=size)
plt.title('KeV', fontsize=size)
plt.ylabel('Counts Per Second', fontsize=size)
plt.legend()
plt.xticks(fontsize=ticksize)
plt.yticks(fontsize=ticksize)

top_y = axes.twiny()
top_y.set_xscale('log')
xlim = axes.get_xlim()

top_y.set_xlim(xlim)
ticks = np.array(axes.get_xticks())
ticks_kev = ticks / mV_per_keV
ticks_kev = np.log10(ticks_kev)
ticks_kev = 10 ** (np.round(ticks_kev))
top_y.set_xticks(ticks_kev)
strings = []
for num in ticks_kev:
	strings.append("{:0.0e}".format(num))
top_y.set_xticklabels(strings, fontsize=ticksize)
plt.show()
# plt.savefig('Method_Comparison_{}_rate'.format(sensor_type))


# TODO need to filter for pulse type...
# TODO maybe re-organize trace generation so all traces of same group are in a npz file
