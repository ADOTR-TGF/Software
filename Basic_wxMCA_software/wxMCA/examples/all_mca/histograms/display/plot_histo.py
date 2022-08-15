import json
import matplotlib.pyplot as plt
import emorpho_histo
import math

def get_histo(file_name, index=0):
    # dwell_time = 10
    peak_data = []
    baselines = []
    num_histo = 0
    with open(file_name, 'r') as fin:
        for line in fin:
            num_histo += 1
    
    nh = index if index>=0 else num_histo+index
    count = 0
    with open(file_name, 'r') as fin:
        for line in fin:
            if count!= nh:
                count += 1
                continue
            
            data = json.loads(line)
            try:
                histo = data["histogram"]["fields"]["histogram"]  # MCA-1000, MCA-2000 histograms are here
            except:
                histo = data["histogram"]["registers"]  # eMorpho, MCA-3000 histograms are here
            break
        
    x_data = [x for x in range(len(histo))]
    return x_data, histo
    
def line_plot(x_data, y_data, ctrl):
    
    fig, ax = plt.subplots()
    lp1 = ax.plot(x_data, y_data)
    plt.setp(lp1, **ctrl['line_ctrl'])
        
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

import plot_histo_controls as pc
x_data, y_data = get_histo("../data/histogram_2banks_303.json", index=4)
line_plot(x_data, y_data, pc.histogram_plot_ctrl)


plt.show()
