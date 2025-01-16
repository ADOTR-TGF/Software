import numpy as np
from matplotlib import rcParams
rcParams['figure.figsize'] = [15, 7]
import scipy.stats as st
import matplotlib.pyplot as plt
import matplotlib.figure as f
import matplotlib.axes._axes as ma
def plot_photons(structure, photons_, magnitude, vertical_offset=0, color='r', label_='', alpha=1):
    if alpha == -1:
        num_mode = st.mode(photons_)[1]
        alpha = 1/2/num_mode

    caller = None
    labeled = False
    if type(structure) is f.Figure:
        caller = plt
    elif type(structure) is ma.Axes:
        caller = structure
    else:
        print('Unhandled type:', str(type(structure)))
        assert False

    ys = None
    if type(magnitude) in [float, int, np.float64]:
        ys = [vertical_offset, magnitude+vertical_offset]
        for p in photons_:
            if not labeled:
                caller.plot([p, p], ys, color, alpha=alpha,
                            label=label_)
                labeled = True
            else:
                caller.plot([p, p], ys, color, alpha=alpha)
    elif type(magnitude) is np.ndarray:
        for p, m in zip(photons_, magnitude):
            ys = [0, m]
            if not labeled:
                caller.plot([p, p], ys, color, alpha=alpha,
                            label=label_)
                labeled = True
            else:
                caller.plot([p, p], ys, color, alpha=alpha)
    else:
        print('Unhandled type:', str(type(magnitude)))
        assert False
