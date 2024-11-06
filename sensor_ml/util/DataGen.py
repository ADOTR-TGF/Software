import numpy as np
import numpy.random as ran
from matplotlib import rcParams
rcParams['figure.figsize'] = [15, 7]
import scipy.signal as signal
import gc


def summed_listmode_local(indeces, values):
    # idk if this is the best way but its easy
    # combine values and find non zero values
    vec = np.zeros(0, np.max(indeces))
    for i, v in zip(indeces, values):
        vec[i] += v

    new_indeces = np.where(vec)
    new_values = vec[new_indeces]
    return new_indeces, new_values


def plastic_pulse(a):
    sos = signal.butter(3, 0.66e7, btype='low', analog=False, output='sos', fs=40e6)
    t = np.arange(0., 0.5e-6, 25e-9)
    y = t * 0
    y[4] = 1.
    fil = signal.sosfilt(sos, y)
    fil = fil * a / np.max(fil)
    return t, fil


def nai_pulse(a, n=-1, sampling_ratio=1):
    sos1 = signal.butter(3, 0.25e7, btype='low', analog=False, output='sos', fs=40e6)
    sos2 = signal.butter(2, .145e7, btype='low', analog=False, output='sos', fs=40e6)
    sos3 = signal.butter(1, .053e7, btype='low', analog=False, output='sos', fs=40e6)

    dt = 25e-9 /sampling_ratio #TODO implement sampling ratio...
    start = 0
    if n == -1:
        stop = 2.5e-6
    else:
        stop = n * dt
    t = np.arange(start, stop, dt)
    # t = np.arange(0., 2.5e-6, 25e-9)
    y = t * 0
    y[4] = 1
    fil1 = signal.sosfilt(sos1, y)
    fil1 = fil1*a/np.max(fil1)
    fil2 = signal.sosfilt(sos2, y)
    fil2 = fil2*a/np.max(fil2)
    fil3 = signal.sosfilt(sos3, y)
    fil3 = fil3*a/np.max(fil3)
    fil = np.concatenate((fil1[0:11], fil2[11:17], fil3[17:]))
    return t, fil


# Trace with pulses scaled according to spectrum
def spectrum_trace(count_rate_, dt_, total_time_, pulse_, bin_energies_, spectrum_, mV_per_keV_, noise_std_, baseline_,
                   sampling_ratio_, discretize=True, bits_=12, seed_=None, clip=True, debug=False):

    #TODO add data generated at higher sampling rate, then downsample
    # issue is that it messes up the metrics.py if we dont have "true" values at integer indeces...
    # unless we also estimate an upsampled deconvolution s.t. its the same as original...?
    assert sampling_ratio_ > 0 and type(sampling_ratio_) is int

    # Freeze the random number seed for reproducibility:
    if seed_ is not None:
        ran.seed(seed_)

    time_vector = np.arange(0, total_time_, dt_ / sampling_ratio_)
    photon_time_indeces = np.sort(np.random.choice(
        np.arange(time_vector.size-len(pulse_)),
        size=int(count_rate_ * total_time_)))


    energies_list = np.random.choice(bin_energies_, p=spectrum_ / sum(spectrum_), size=photon_time_indeces.size)

    trace = np.zeros(time_vector.size)
    pulse_len = len(pulse_)
    mx_list_size_index = photon_time_indeces.size
    for i, t in enumerate(photon_time_indeces):
        # print(t, len(trace))
        if t + pulse_len < trace.size:
            trace[t:t + pulse_len] += pulse_ * energies_list[i]
            mx_list_size_index = t

    time_vector = time_vector[0: trace.size]
    # energies_list = energies_list[photon_time_indeces < mx_list_size_index]
    # energy_time_indeces = photon_time_indeces[photon_time_indeces < mx_list_size_index]
    energy_time_indeces = photon_time_indeces

    # # Sparse summed photon vector
    # summed_index_list, summed_volts_list = summed_listmode_local(energy_time_indeces, energies_list)

    # Downsample data
    if sampling_ratio_ != 1:
        trace = signal.decimate(trace, sampling_ratio_)

    # add baseline and noise, and clip:
    trace *= mV_per_keV_ # Trace in mV
    trace += baseline_
    trace += ran.randn(trace.size) * noise_std_

    if clip:
        trace[trace > 1000] = 1000

    volts_list = energies_list * mV_per_keV_ # now in mV
    volts_time_indeces = energy_time_indeces

    if discretize:
        # digitize:
        itrace = trace / 1000. * 2 ** bits_
        for i in range(len(itrace)):
            itrace[i] = float(int(itrace[i]))
        itrace = itrace * 1000. / 2 ** bits_
    else:
        itrace = trace

    return itrace, time_vector, volts_list, volts_time_indeces



# Trace with pulses of constant volts
def const_trace(count_rate_, n_trace, dt_, pulse_, volts_magnitude, baseline_, base_noise_,
                seed=None, quantize=False, bits=12):
    # Freeze the random number seed for reproducibility:
    if seed is not None:
        ran.seed(seed)

    n_pulse = len(pulse_)

    t1 = dt_ * n_trace
    time = np.linspace(0, t1, n_trace)
    total_time = time[-1]

    # Do not add a partial pulse to the end of the trace
    n_counts = round(count_rate_ * total_time * (n_trace - n_pulse) / n_trace)
    #TODO fix this: invalidates number of counts that coudl be used for metrics.py
    time_indeces = np.random.randint(0, n_trace - n_pulse, n_counts)

    # Vector of energies of photons at time indeces
    volts = np.zeros(time.shape)
    volts[time_indeces] += volts_magnitude  # in V,  ***( += not = )***

    # Convolve energies and pulse to produce desired trace signal
    fft_energies = np.fft.fft(volts)
    fft_pulse = np.fft.fft(pulse_, n=n_trace)
    trace = np.abs(np.fft.ifft(fft_energies * fft_pulse))

    # add in noise and base
    trace += baseline_
    if base_noise_ > 0:
        trace += np.random.normal(loc=0, scale=base_noise_, size=n_trace)

    return volts, trace, time_indeces


def make_trace(counts, fwhm, spectrum, binenergies, dt, tstep, trace_length, mV_per_ADC, keV_per_area,
               baseline, basenoise, bits, mean, std, pulse_function, sensor_type, seed=None):

    assert sensor_type in ['plastic', 'nai']

    # Freeze the random number seed for reproducibility:
    if seed:
        ran.seed(seed)

    # one trace file worth of data.
    sampletimes = np.linspace(-dt, tstep * trace_length + dt, trace_length + int(2 * dt / tstep), endpoint=False)

    # if running a statistical study using countrates Get in advance the number of counts that will be used to populate each trace.
    # poisson = ran.poisson(countrate*tstep*time_grid)  #why is time_grid used in this??
    # poisson = (np.floor(countrate*tstep*time_grid)).astype(int)

    # initialize a clear trace
    n = len(sampletimes)
    trace = np.zeros(sampletimes.size)

    sigma = (fwhm / 2.355) * 1e-6  # one standard deviation of the time distribution in units seconds

    # lognormal arguments: (mean, std, size) sigma is used to scale the output of lognormal to the width of a TGF trace
    # the mean and std can be adjusted to move the trace distribution left or right (mean) and adjust the asymetry (std)
    times = ran.lognormal(mean, std, counts) * sigma
    # times = ran.uniform(low=0,high=7.0,size=counts)*sigma
    # line = np.abs(ran.choice(len(spectrum),  p=spectrum/sum(spectrum), size = len(times))) #chooses energies from an input spectrum based on probabilites
    # energies = line*specscale_keV + 5.   #spectrum starts at 5keV
    energies = np.abs(ran.choice(binenergies, p=spectrum / sum(spectrum), size=len(times)))

    times = np.sort(times)
    if sensor_type == 'nal':
        times += 100e-6  # 100us of pre-TGF
    # print(times)

    # define the pulse shape once
    pulsetimes, pulse = pulse_function(1.)
    nsamples = len(pulse)

    area_per_peak = np.sum(pulse) / max(pulse)
    mV_per_keV = mV_per_ADC / (keV_per_area * area_per_peak)

    # For every incident count, create a pulse and add it to the trace:
    i = 0
    for t in times:
        t_index = (sampletimes > t - dt).nonzero()
        t_index0 = (t_index[0])[0]
        navailable = len(trace[t_index0:t_index0 + nsamples])
        if navailable == nsamples:
            trace[t_index0:t_index0 + nsamples] = trace[t_index0:t_index0 + nsamples] + pulse * energies[i]
        i = i + 1
        # print(i)

    # scale to mV, add baseline and noise, and clip:

    trace = trace * mV_per_keV
    trace += baseline
    trace += ran.randn(n) * basenoise

    w = (trace > 1000.).nonzero()
    trace[w] = 1000.

    # digitize:
    itrace = trace / 1000. * 2 ** bits
    for i in range(len(itrace)):
        itrace[i] = float(int(itrace[i]))
    itrace = itrace * 1000. / 2 ** bits

    return (itrace)