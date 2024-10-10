import numpy as np
from matplotlib import rcParams
rcParams['figure.figsize'] = [15, 7]
from scipy.linalg import circulant
from scipy.optimize import nnls, lsq_linear
import gc


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

def trace_by_addition(N, kernel, energies, indeces):
    # indeces need to be sorted beforehand...
    ts = np.zeros(N)
    n = kernel.size
    assert energies.size == indeces.size
    for i, index in enumerate(indeces):
        i0 = index
        if i0 + n <= ts.size:
            i1 = i0 + n
            ts[i0:i1] += kernel * energies[i]
        else:
            # m = 0
            print('end pulse')
            ts[i0:ts.size+1] += kernel[kernel.size-(ts.size-index):] * energies[i]
    return ts

#TODO get from scripts
# def photon_list_to_vec()
# time or index input?
def td_convolve(x, kernel, A=None):
    #TODO may be able to strcture A s.t. doesnt wrap around ends. Take the circulant matrix and zero out indeces s.t.
    #TODO partial kernels on ends are independent. Note that this will now not make a square matrix. for kernel length
    #TODO N, (n=100, really 101) there should be ~2N "partial" kernels...
    # Y = Ax
    if A is None:  # optionally pre-specify for speed
        c = np.concatenate((kernel, np.zeros(x.size - kernel.size)), axis=0)
        A = circulant(c)
    y = A * x
    return np.sum(y, axis=1)

def td_deconvolve(y, kernel, A_inv=None):
    #TODO see above
    if A_inv is None: # optionally prespecify for speed
        c = np.concatenate((kernel, np.zeros(y.size - kernel.size)), axis=0)
        A = circulant(c)
        A_inv = np.linalg.inv(A)
    x = A_inv @ y
    return x

def td_nnlsr_deconvolve(y, kernel, C=None):
    if C is None:  # optionally prespecify for speed
        c = np.concatenate((kernel, np.zeros(y.size - kernel.size)), axis=0)
        C = circulant(c)
    x, _ = nnls(C, y)
    return x


def fft_convolve(s, kernel, extra_pad=0):
    n = len(s) + extra_pad
    r = np.fft.fft(s, n=n) * np.fft.fft(kernel, n=n)
    return np.abs(np.fft.ifft(r))


def fft_deconvolve(s, kernel, extra_pad=0, signal_fft_ax=None, signal_label=None, kernel_fft_ax=None, kernel_label=None):
    n = len(s) + extra_pad
    signal_fft = np.fft.fft(s, n=n)
    kernel_fft = np.fft.fft(kernel, n=n)
    r = signal_fft / kernel_fft

    if kernel_fft_ax is not None:
        kernel_fft = np.fft.fft(kernel, n=n)
        half = np.abs((kernel_fft[:len(kernel_fft) // 2]))
        f = np.arange(len(half))
        kernel_fft_ax.plot(f, half / np.max(half), label=kernel_label)
        # kernel_fft_ax.set_title('Kernel FFT Spectrum')

    if signal_fft_ax is not None:
        half = np.abs((signal_fft[:len(signal_fft) // 2]))
        f = np.arange(len(half))
        signal_fft_ax.plot(f, half / np.max(half), label=signal_label)
        # signal_fft_ax.set_title('Signal FFT Spectrum')

    return np.abs(np.fft.ifft(r))


def wiener_deconvolve(s, kernel, K):
    kernel_norm = kernel
    kernel_norm = np.fft.fft(kernel_norm, n=s.size)
    kernel_norm = np.conj(kernel_norm) / (np.abs(kernel_norm) ** 2 + K)
    trace_fd = np.fft.fft(s)
    dummy = trace_fd * kernel_norm
    return np.abs(np.fft.ifft(dummy))


def threshold_listmode(timeseries, threshold):
    assert timeseries.size > 0
    assert threshold >= 0

    valid = timeseries > threshold
    indeces = np.where(valid)[0]
    volts = timeseries[indeces]

    return volts, indeces


def summed_listmode(indeces, values, time):
    # idk if this is the best way but its easy
    # combine values and find non zero values
    vec = np.array(np.zeros(time.size))
    for i, v in zip(indeces, values):
        vec[i] += v

    new_indeces = np.where(vec)[0]
    new_values = vec[new_indeces]
    return new_indeces, new_values


def discretize(data, bits):
    int_trace = data/1000.*2**bits
    for i in range(len(int_trace)):
        int_trace[i] = float(int(int_trace[i]))
    int_trace *= 1000./2**bits
    return int_trace


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