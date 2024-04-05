import time
from functions import *
import numpy as np
import matplotlib.pyplot as plt
import joblib
import gc
import os


n_trace = 1000
dt = 25e-9 #sampling rate in seconds. 40MHz
_, pulse_ = nai_pulse(1)
baseline = 100  #  mV
# base_noise = 0.01  # add in during testing for flexibility...

vmin = 1  # mV
vmax = 3  # mV
v_n = 100
voltage_magnitudes = np.logspace(vmin, vmax, v_n)
rmin = 6
rmax = 9
r_n = 100
count_rates = np.logspace(rmin, rmax, r_n)

# metadata per "trace", voltage and countrate
V = np.tile(voltage_magnitudes, (count_rates.size, 1)).T
R = np.tile(count_rates, (voltage_magnitudes.size, 1))
photons = []

X = np.zeros((voltage_magnitudes.size, count_rates.size, n_trace))
Y = np.zeros(X.shape)

pt = True
for i in range(X.shape[0]):
    photon_row = []
    for j in range(X.shape[1]):
        t = time.time()
        v = V[i, j]
        r = R[i, j]
        y, x, photon_indeces = const_trace(r, n_trace, dt, pulse_, v, baseline, base_noise_=0)
        photon_row.append(photon_indeces)
        X[i, j, :] = x
        Y[i, j, :] = y
        del x, y
        if pt:
            pt = False
            print('Build EST:', (time.time() - t) * X.shape[0] * X.shape[1])
    photons.append(photon_row)
    gc.collect()

# print(V.shape, R.shape, X.shape, Y.shape)
assert V.shape == R.shape == X.shape[0:2] == Y.shape[0:2] == (len(photons), len(photons[0]))

dir = 'data'
if not os.path.exists(os.path.join(os.getcwd(), dir)):
    os.mkdir(os.path.join(os.getcwd(), dir))
trace_type = 'const'
pulse_type = 'nai'
base = ('data_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}_'
        .format(n_trace, dt, trace_type, pulse_type, baseline,
                vmin, vmax, v_n, rmin, rmax, r_n))
joblib.dump(X, 'data/' + base + 'X.pkl')
joblib.dump(Y, 'data/' + base + 'Y.pkl')
joblib.dump(V, 'data/' + base + 'V.pkl')
joblib.dump(R, 'data/' + base + 'R.pkl')
joblib.dump(photons, 'data/' + base + 'photons.pkl')

indeces = np.arange(X.shape[0])[::20]
print(indeces)
plot_max = 500
# plot_max = X.shape[2]

# Compare Different Magnitudes
fig = plt.figure(figsize=(10, 8), dpi=400)
j = 40
for i in indeces:
    plt.plot(X[i, j, 0:plot_max], label='mV: {:.1f}'.format(V[i, j]), alpha=.25)
plt.legend()
plt.plot([0, n_trace], [1000, 1000], 'r')
plt.title('Response of Diff Const Traces, at a Rate of {:.1E}'.format(R[0, j]))
plt.xlim([0, plot_max])
plt.show()

# Compare Different Rates
fig = plt.figure(figsize=(10, 8), dpi=400)
i = X.shape[0] // 2
for j in indeces:
    plt.plot(X[i, j, 0:plot_max], label='Rate: {:.1E}'.format(R[i, j]), alpha=.25)
plt.legend()
plt.plot([0, n_trace], [1000, 1000], 'r')
plt.title('Response of Diff Const Traces, at {number:.1f} mV'.format(number=V[i, 0]))
plt.xlim([0, plot_max])
# plt.xlim([100, 200])
plt.show()

# Compare Different Noise values
n_plots = 3
fix, axes = plt.subplots(n_plots, 1, figsize=(10, 8), dpi=400)
base_noises = np.logspace(0 - n_plots, -1, n_plots)
i = 70
j = 40
v = V[i, j]
for ax, noise in zip(axes, base_noises):

    data = X[i, j] + np.random.normal(loc=0, scale=noise*v, size=X.shape[2])
    ax.plot(data, label='Noise: {:.1E}*mV'.format(noise), alpha=.25)
    ax.set_xlim([0, plot_max])
    ax.legend()
    ax.set_ylim([0, np.max(data[:plot_max])])
    ax.plot([0, n_trace], [1000, 1000], 'r')

    # slow, so lets not plot too many since we are cutting off the plot anyway
    ps = photons[i][j]
    ps = ps[ps < plot_max]
    plot_photons(ax, ps, magnitude=Y[i, j])

axes[0].set_title('Example Signal and OG Photon Voltages')
plt.show()

