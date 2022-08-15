import json
import matplotlib.pyplot as plt
import emorpho_histo
import math

def get_buffers(file_name, num_buffers):
    # dwell_time = 10
    energies_0 = []
    energies_1 = []
    with open(file_name, 'r') as fin:
        for nbuf, line in enumerate(fin):
            if nbuf == num_buffers:
                break
            data_dict = json.loads(line)
            if nbuf ==0:
                sn_list = list(data_dict)
            energies_0 += data_dict[sn_list[0]]["energies"]
            energies_1 += data_dict[sn_list[1]]["energies"]

    return energies_0, energies_1


def line_plot(x_data, y_data, ctrl):

    fig, ax = plt.subplots()
    lp = ax.plot(x_data, y_data)

    plt.setp(lp, **ctrl["line_ctrl"])

    ax.set_xlabel(ctrl['labels']['xlabel'] , **ctrl['labels']['xlabel_ctrl'])
    ax.set_ylabel(ctrl['labels']['ylabel'], **ctrl['labels']['ylabel_ctrl'])
    ax.set_title(ctrl['labels']['title'], **ctrl['labels']['title_ctrl'])
    ax.grid(**ctrl['grid_ctrl'])
    ax.set(**ctrl['axis_ctrl'])

    #bbox_args = dict(boxstyle="round", pad=0.5, ec="#555555", fc=(0.9, 0.9, 0.9, 0.9), linewidth=2)  # fill, bounds(l,b,w,h) are ignored
    #comment = ""  # Empty string nixes the display
    #ax.annotate(comment, fontsize=10,
    #            xycoords='axes fraction', xy=(0.35, 0.90), ha="left", va="bottom", bbox=bbox_args)

    if ctrl['show']:
        plt.show()

import plot_coinc_lm_controls as pc
energies_0, energies_1 = get_buffers("../data/coinc_bck.dat", 10)
line_plot(energies_0, energies_1, pc.lm_plot_ctrl)

plt.show()
