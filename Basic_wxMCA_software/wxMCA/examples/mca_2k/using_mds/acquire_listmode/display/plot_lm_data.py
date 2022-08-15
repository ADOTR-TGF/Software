import json
import matplotlib.pyplot as plt
import math

def get_listmode(file_name):
    times = []
    energies = []
    number_of_events = 0
    with open(file_name, "r") as fin:
        for line in fin:
            dd = json.loads(line)
            num_events = dd["num_events"]
            #num_events = 500
            decimation = dd["decimation"]
            energies += dd["energies"][0:num_events]
            times += dd["times"][0:num_events]
            
            tt = dd["times"]
            dt = tt[num_events-1]-tt[0]
            if dt > 1e6:
                print("CR=", num_events/(dt))
            #print(num_events, dt)
    
    # histogram the energies    
    histo = [0]*4096
    for e in energies:
        histo[e] += 1
        
    return energies, times, histo

    
def line_plot(x_data, y_data, ctrl):
    
    fig, ax = plt.subplots()
    lp = ax.plot(x_data, y_data)    
    plt.setp(lp, **ctrl['line_ctrl'])
    
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

import plot_lm_controls as pc
energies, times, histo = get_listmode("../data/lm2b.dat")
x_histo = [x for x in range(4096)]
x_events = [x for x in range(len(energies))]
line_plot(x_events, energies, pc.energies_plot_ctrl)
line_plot(x_events, times, pc.times_plot_ctrl)
line_plot(x_histo, histo, pc.histo_plot_ctrl)


plt.show()
