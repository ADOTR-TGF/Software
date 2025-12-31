import numpy as np
import os
import matplotlib.pyplot as plt
import copy

from util.DataGen import nai_pulse, plastic_pulse, continuous_time_trace
from util.Processing import trace_to_counts, threshold_nnlsr_deconvolve, iterated_subtraction
from util.metrics import volts_counted_hist, volts_counted_pct, events_counted

def generate_trace_set(count_rate, trace_kwargs, N_TRACES_PER_PARAM):

    assert sensor_type in ['plastic', 'NaI']

    kwargs_copy = copy.deepcopy(trace_kwargs)
    kwargs_copy['count_rate'] = count_rate

    traces = []
    for i in range(N_TRACES_PER_PARAM):
        out = continuous_time_trace(**kwargs_copy)
        traces.append(out)

    return traces


def process_trace_set(tracedatas, algorithm, algorithm_kwargs, title=False):
    results = []
    for j, tracedata in enumerate(tracedatas):
        listmode = algorithm(tracedata.trace, **algorithm_kwargs)

        plt.figure(figsize=(14,4), dpi=200)
        plt.plot(tracedata.trace, label='trace')
        plt.plot(listmode['indeces'], listmode['volts'], '*', label='Deconv')
        if title:
            plt.title(title)
        plt.xlim(0,250)
        # plt.show()

        results.append(listmode)
    return results

def fine_countrate_eval(countrates:list, algorithm_list:list, algorithm_kwarg_list:list,
                        common_trace_kwargs:list, N_TRACES_PER_COUNTRATE:int, labels:list):

    markersize = 10

    fig, axes = plt.subplots(2,1,figsize=(10,6), dpi=200)

    # TODO need to pre-create traces, plot ground truth,
    # then loop through algirthms and calcualte statistcs...

    true_counts = np.zeros((countrates.size, N_TRACES_PER_COUNTRATE))
    true_volts = np.zeros((countrates.size, N_TRACES_PER_COUNTRATE))

    tracedatas = []

    for i, count_rate in enumerate(countrates.tolist()):
        trace_countrate_set = generate_trace_set(count_rate, common_trace_kwargs, N_TRACES_PER_COUNTRATE)
        tracedatas.append(trace_countrate_set)

        for j, td in enumerate(trace_countrate_set):
            true_counts[i, j] = td.event_voltages.size
            true_volts[i, j] = np.sum(td.event_voltages)

    axes[0].plot(countrates, np.sum(true_counts, axis=1), label='Truth',
                 marker='.', markersize=4, linestyle='', alpha=.5)
    axes[1].plot(countrates, np.sum(true_volts, axis=1), label='Truth',
                 marker='.', markersize=4, linestyle='', alpha=.5)

    for i, (algorithm, algorithm_kwargs, label) in enumerate(zip(algorithm_list, algorithm_kwarg_list, labels)):

        algo_events_counted = np.zeros((countrates.size, N_TRACES_PER_COUNTRATE))
        algo_volts_counted = np.zeros((countrates.size, N_TRACES_PER_COUNTRATE))

        for i, (trace_countrate_set, count_rate) in enumerate(zip(tracedatas, countrates.tolist())):

            listmode_result_list = process_trace_set(trace_countrate_set, algorithm, algorithm_kwargs, label+' '+str(np.log10(count_rate)))

            for j, listmode in enumerate(listmode_result_list):
                algo_events_counted[i, j] = listmode['volts'].size
                algo_volts_counted[i, j] = np.sum(listmode['volts'])

        axes[0].plot(countrates, np.sum(algo_events_counted, axis=1), label=label,
                     marker='.', markersize=2*(i+4),linestyle='', alpha=.5)

        axes[1].plot(countrates, np.sum(algo_volts_counted, axis=1), label=label,
                     marker='.', markersize=2*(i+4), linestyle='', alpha=.5)

    axes[0].set_xlabel('Count Rate')
    axes[0].set_ylabel('Counts')
    axes[0].set_xscale('log')
    axes[0].legend()
    # axes[0].text(1E5, 200, 'Note NNLSR asymptotic at end because of convsum limit...')

    axes[1].set_xlabel('Count Rate')
    axes[1].set_ylabel('Volts Measured (To energy?)')
    axes[1].set_xscale('log')
    axes[1].legend()
    plt.show()

# Too many issues with showing error when values mising or bins shifting... not enough bins...
# def course_countrate_eval(countrates:list, algorithm_list:list, algorithm_kwarg_list:list,
#                         common_trace_kwargs:list, N_TRACES_PER_COUNTRATE:int, labels:list):
#
#     for algorithm, algorithm_kwargs, label in zip(algorithm_list, algorithm_kwarg_list, labels):
#
#         fig, axes = plt.subplots(1, 1, figsize=(10, 6), dpi=200)
#
#         markersize = 10
#
#         for i, count_rate in enumerate(countrates.tolist()):
#
#             true_spectrum = np.zeros(bins.size-1)
#
#             trace_countrate_set = generate_trace_set(count_rate, common_trace_kwargs, N_TRACES_PER_COUNTRATE)
#
#             for j, tracedata in enumerate(trace_countrate_set):
#                 hist, edges = np.histogram(tracedata.event_voltages, bins=bins)
#                 true_spectrum += hist
#
#                 counts_per_energy = np.zeros(bins.size-1)
#
#                 listmode_result_list = process_trace_set(trace_countrate_set, algorithm, algorithm_kwargs,
#                                                          label + ' ' + str(np.log10(count_rate)))
#
#                 for j, listmode in enumerate(listmode_result_list):
#                     hist, edges = np.histogram(listmode['volts'], bins=bins)
#                     counts_per_energy += hist
#
#                 pct_error = (counts_per_energy - true_spectrum) / true_spectrum
#                 pct_error[np.isnan(pct_error)] = 0
#                 pct_error[np.isinf(pct_error)] = 0
#
#                 axes.plot(bins[:-1], pct_error, label= 'Rate: {:.2e}'.format(count_rate),
#                              marker='.', markersize=markersize, linestyle='', alpha=.5)
#
#         axes.set_title(label)
#         axes.set_xscale('log')
#         axes.legend()
#     plt.show()

# Simulation Parameters ###################################################################
###########################################################################################

sensor_type = 'plastic'
assert sensor_type in ['NaI', 'plastic']

N_TRACES_PER_COUNTRATE=1

# Trace Parameters
keV_per_area = .147
mV_per_ADC = 1000/4096
baseline = 0 # mV
basenoise= 0 # mV
bits = 10
clip = 1000 # mV
fs = 40E6 # new HERA sampling rate
total_time = 5E-5
# for Lognormal traces
fwhm = 50 #50.0 #fwhm of the total TGF count distribution in units microseconds
mean = .007, #.7 #mean of the TGF trace distribution
std = 0 #.5 #determines the amount of assymetry in the TGF trace distribution

if sensor_type == 'plastic':
    _, kernel = plastic_pulse(1)
    spectrum = np.loadtxt('../original/LgPl_Response', usecols=(1), dtype=float)
    bins = 1E3 * np.loadtxt('../original/LgPl_Response', usecols=(0), dtype=float)  # in kev
else:
    _, kernel = nai_pulse(1, 101)
    spectrum = np.loadtxt('../original/NaI_Response', usecols=(1), dtype=float)
    bins = 1E3 * np.loadtxt('../original/NaI_Response', usecols=(0), dtype=float)  # in kev


# Algorithm Parameters ####################################################################
###########################################################################################

common_trace_kwargs = {
    'trace_type': 'constant',
    'keV_per_area' : keV_per_area,
    'mV_per_ADC' : mV_per_ADC,
    'baseline' : baseline, # mV
    'basenoise': basenoise, # mV
    'bits' : bits,
    'clip_magnitude' : clip, # mV
    'fs' : fs, # new HERA sampling rate
    'total_time' : total_time,
    'spectrum_hist': spectrum,
    'detector_response_kernel': kernel,
    'spectrum_bin_energies':bins,
    # for Lognormal traces
    'lognormal_fwhm' : fwhm, #50.0 #fwhm of the total TGF count distribution in units microseconds
    'lognormal_mean' : mean, #.7 #mean of the TGF trace distribution
    'lognormal_std' : std, #.5 #determines the amount of assymetry in the TGF trace distribution
    'return_object':True
}

# FPGA Algorithm Parameters...
fpga_kwargs = {
    'thresh' : 8.0,  # units of mV  this is the pulse trigger threshold
    'int_i' : 50,  # integ.ration time = 1.25 microsecs = 50 samples at 40MHz sampling
    'dead_i' : 50,  # deadtime = integration time
    'extend' : 1,  # extendable dead time parameter
    'escale' : .085, #.63,  # being used to scale the pulse integration value to energy in keV. experimentally determined.
    'baseline' : baseline,
    'dt' : 1 / 40E6,
    'tstep' : 1 / 40E6,
    'return_dict':True
}

# Iterated Subtraction Parameters
iterated_sutraction_kwargs = {
    'kernel': kernel,
    'threshold': 5,
}

# Dense Thresholded NNLSR Parameters
threshold_nnlsr_kwargs = {
    'threshold' : 1,
    'kernel': kernel,
    'return_dict':True
}

# Dense Thresholded NNLSR with CONVUSM Parameters
tnnlsr_consum_kwargs = {
    'threshold' : 1,
    'kernel': kernel,
    'nsum': 5,
    'sigma': 1,
    'distance': 3,
    'return_dict':True
}

# labels = ['FPGA Algo.', 'Iterated Subtraction', 'Thresholded NNLSR', 'TNNLSR Conv Sum']
# algorithm_list = [trace_to_counts, iterated_subtraction, threshold_nnlsr_deconvolve, threshold_nnlsr_deconvolve]
# algorithm_kwarg_list = [fpga_kwargs, iterated_sutraction_kwargs, threshold_nnlsr_kwargs, tnnlsr_consum_kwargs]

labels = ['Thresholded NNLSR', 'TNNLSR Conv Sum']
algorithm_list = [threshold_nnlsr_deconvolve, threshold_nnlsr_deconvolve]
algorithm_kwarg_list = [threshold_nnlsr_kwargs, tnnlsr_consum_kwargs]

# Analysis Parameters #####################################################################
###########################################################################################


# Main ####################################################################################
###########################################################################################

count_rates = np.logspace(6,8, 5)
fine_countrate_eval(count_rates, algorithm_list=algorithm_list,
                    algorithm_kwarg_list=algorithm_kwarg_list,
                    common_trace_kwargs=common_trace_kwargs,
                    N_TRACES_PER_COUNTRATE=N_TRACES_PER_COUNTRATE,
                    labels=labels)


"""
Experiments:
Compare Methods across different countrates by

    Fine countrate sweep:
        Total Counts error per countrate
        Total Energy Error per countrate

    Course countrate sweep:
        per countrate:
            Counts Error by energy bin for a few countrates...
            Energy Error by energy bin for a few countrates...

Methods to Add
    NNLSR,CONVSUM,smoothing,argpeaks
    Iterated Subtraction
    TODO: Iterated M-event estimation

analysis: Poisson Statistics for different countrates...

Statistics of Match Filter... extended to generalized NNLSR...

Further improvements in lognormal simulator:
    Generate far large number of incoming photons and then re-sample at realistic interaction probablities
    Suspect that this will significantly "randomize" the locally time density stats 
    Account for Compton/PE/Pair porbabilites... Does compton generate significant noise?
    
Code TODO beyond this file
- CONVSUM gaussian scale space smoothing? Optimize local sums? Could be a good candidate for machine learning...
  One issue with ML output is outputting a varaible sized list... this requires an iterated time domain style model...
- Frequency domain comparison of Event seperation times. Can filtering aid in event detection? Does filtering Distort
  foudn event magnitudes...? Filtering assumes periodicity...? but system is LTI... General electronics deconvolution
  should not work if this would not work...?
- Markov MC methods
  Accounting for electronics noise as well as "low energy noise" from compton scatters might help deconv, especially for plastic?
  What is the response curve rates for compton scatters vs PE and pair production? Can compton scatters be a signficatn source of noise?
- MKMC on individual clusters...
  
- Upsampling might still help in producing finer "convsum" estimates"
- Is there a way to say statistically the ptobablity that sets of non-zero deconvs should be grouped vs seperate? Noise?
       - LSR already found "best" solution by error. Need another source of estimation. Countrate?
       
- Deconvolution as a  PDF... except probabilities dont normalize to one?

read: https://en.wikipedia.org/wiki/Matched_filter
      
TODO plots and captions example to Manfredi as a "paper story"
CV normalized cross corr. If big enough... maybe should take that over NNLSR...
Review papers that Manfredi sent to me
Plots of real data...
Try filtering of frequencies...?

Metric Idea: Error  as XY distance on Voltage-time Deconvolution. Need to weight voltage much more heavily than time...
- similar to do a bins-counts XY distance weighted towards counts (aka distribution shift less important than time shift)
  Eath-movers distance - KL diveregnce, Wasserstein distance... But these take less into account that ability of indivudal
  events to be missclassified and be mzsked out in the statistics...
  
Stats analysis: Given range of TGF power and TGF-Aircraft distances, what are the extremes high and low countrates that we would like to see
                measured. Given scintillaotr properties, what are the likely countrates that will occurr there? Design sensor array
                around having enough scintillaotro volume for low countrate while enough channels to manage high countrate...
      
"""
