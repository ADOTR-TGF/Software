import json
import matplotlib.pyplot as plt
import math

def get_pulses(file_name, index=0):
    # dwell_time = 10
    peak_data = []
    baselines = []
    num_pulses = 0
    with open(file_name, 'r') as fin:
        for line in fin:
            num_pulses += 1
    print("Number of pulses in file:", num_pulses)
    
    if type(index)==list:
        index_list = [idx for idx in range(index[0], index[1])]
    else:
        index_list = [index]

    pulse_list = []
    count = 0
    with open(file_name, 'r') as fin:
        for line in fin:
            if count in index_list:
                data = json.loads(line)
                pulse = data["pulse"]["fields"]["trace"]  # Scaled and sign-corrected pulses
                pulse_list += [pulse]
            count += 1
        
    x_data = [x for x in range(len(pulse))]
    return x_data, pulse_list
    
def line_plot(x_data, y_data_list, ctrl):
    
    fig, ax = plt.subplots()
    lp_list = []
    for y_data in y_data_list:
        lp_list += ax.plot(x_data, y_data)
        plt.setp(lp_list[-1], **ctrl['line_ctrl'])
        
    ax.set_xlabel(ctrl['labels']['xlabel'], **ctrl['labels']['xlabel_ctrl'])
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

import plot_pulse_controls as pc
x_data, pulse_list = get_pulses("../data/pulses_303.json", index=[0,10])
line_plot(x_data, pulse_list, pc.pulse_plot_ctrl)


plt.show()
