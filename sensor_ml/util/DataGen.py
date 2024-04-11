import numpy as np
import numpy.random as ran
from matplotlib import rcParams
rcParams['figure.figsize'] = [15, 7]
import scipy.signal as signal
import gc

def plastic_pulse(a):
    sos = signal.butter(3, 0.66e7, btype='low', analog=False, output='sos', fs=40e6)
    t = np.arange(0., 0.5e-6, 25e-9)
    y = t * 0
    y[4] = 1.
    fil = signal.sosfilt(sos, y)
    fil = fil * a / np.max(fil)
    return t, fil


def nai_pulse(a, n=-1):
    sos1 = signal.butter(3, 0.25e7, btype='low', analog=False, output='sos', fs=40e6)
    sos2 = signal.butter(2, .145e7, btype='low', analog=False, output='sos', fs=40e6)
    sos3 = signal.butter(1, .053e7, btype='low', analog=False, output='sos', fs=40e6)

    dt = 25e-9
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
def spectrum_trace(count_rate_, length_, pulse_function_, spectrum_, noise_level_, seed=None):
    # Freeze the random number seed for reproducibility:
    if seed:
        ran.seed(seed)



# Trace with pulses of constant volts
def const_trace(count_rate_, n_trace, dt_, pulse_, volts_magnitude, baseline_, base_noise_, seed=None):
    # Freeze the random number seed for reproducibility:
    if seed is not None:
        ran.seed(seed)

    n_pulse = len(pulse_)

    t1 = dt_ * n_trace
    time = np.linspace(0, t1, n_trace)
    total_time = time[-1]

    # Do not add a partial pulse to the end of the trace
    n_counts = round(count_rate_ * total_time * (n_trace - n_pulse) / n_trace)
    #TODO fix this: invalidates number of counts that coudl be used for metrics
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


def trace_to_counts(trace, dt, tstep, thresh, baseline, extend, escale, int_i, dead_i):
    # note dt here is seconds before pulse
    # tstep is conventional "dt"

    energies = []
    sample_times = []
    n = trace.size

    di = int(dt / tstep)

    i = di

    while i < n - dead_i - 1:
        if trace[i] > thresh + baseline:  # find a value above trigger threshold.
            energy = np.sum(trace[
                            i - 5:i - 6 + int_i] - baseline)  # Integrate pulse over int_i samples starting with first above threshold.
            norm_energy = energy * escale  # Convert energy into channels to compare to real data spectrum

            energies.append(norm_energy)
            sample_times.append(i)
            i += dead_i

            # Paralyzable deadtime:keep extending the window as long as the last sample of the last interval is still high.
            if (extend > 0):
                while (trace[i - 1] > thresh + baseline and i < n - di - extend):
                    i += extend
        else:
            i += 1

    energies = np.array(energies)
    sample_times = np.array(sample_times)
    gc.collect()
    return (energies, sample_times)


def trace_trigger(trace, trace_time):
    n = 30
    m = 10500
    counter = 0
    for i in range(len(trace)):
        if counter < 0:
            counter = 0
        if trace[i] > 110.:  # mV
            counter += n
        else:
            counter -= 1.
        if counter >= m:
            trigger_time = trace_time[i]
            trigger_index = i
            break
        else:
            trigger_time = np.array([])
            trigger_index = np.array([])

    return trigger_time, trigger_index