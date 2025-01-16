# Benchmark the sparse vs dense NNLSR algorithms
# for t in total_trace_time:
#    new Process:
#       sparse vs dense
#       metrics: runtime (specify cutoff), memory used
#
# for t in total_trace_time:
#    for r in count_rates
#        runtime, error metrics

# metrics: log(abs(energy_trace-deconvolution)) - still misses problem of measured response shifting in time -
#                                            but if this normalized error is lower than comparing spectra,
#                                            I would trust this more...
#          mean, std, var of above
#          % photons measured
#          % energy counted
#          % KL Divergence between true spectrum, measured spectrum
#          % Error in Spectrum (logspace)
