import json
import matplotlib.pyplot as plt
import emorpho_histo
import math

def get_peaks(file_name):
    # dwell_time = 10
    p43 = []
    p121 = []
    p243 = []
    with open(file_name, 'r') as fin:
        for line in fin:
            data_dict = json.loads(line)
            histo = data_dict["histogram"]
            i_min = 30
            i_max = 70
            p43 +=[sum([n*histo[n] for n in range(i_min, i_max)])/sum(histo[i_min:i_max])]
            
            i_min = 120
            i_max = 160
            p121 +=[sum([n*histo[n] for n in range(i_min, i_max)])/sum(histo[i_min:i_max])]
            
            i_min = 320
            i_max = 420
            p243 +=[sum([n*histo[n] for n in range(i_min, i_max)])/sum(histo[i_min:i_max])]
            
            
    r32 = [p3/p2 for p2, p3 in zip(p121, p243)]
    r21 = [p3/p2 for p2, p3 in zip(p43, p121)]
    
    d32 = [p3-p2 for p2, p3 in zip(p121, p243)]
    d21 = [p3-p2 for p2, p3 in zip(p43, p121)]
    
    #statistics
    avg_sigma(p43)
    avg_sigma(p121)
    avg_sigma(p243)
    avg_sigma(r32)
    avg_sigma(r21)
    avg_sigma(d32)
    avg_sigma(d21)
        
    x_data = [x for x in range(len(p43))]
    return x_data, [p43, p121, p243, r32, r21]
    
def avg_sigma(data):
    lp = len(data)
    avg = sum(data)/lp
    var_list = [(p-avg)**2 for p in data]
    std_dev = math.sqrt(sum(var_list)/(lp-1))
    print("Avg, std_dev:", avg, std_dev)

    
def line_plot(x_data, y_data, ctrl):
    
    fig, ax = plt.subplots()
    
    for data in y_data:
        lp_list = ax.plot(x_data, data)
    
    #plt.setp(lp1, **ctrl['line_ctrl'])
    
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

import plot_histo_log_controls as pc
x_data, y_data = get_peaks("../data/histo_log.json")
line_plot(x_data, y_data[0:3], pc.peak_plot_ctrl)

line_plot(x_data, y_data[3:], pc.peak_plot_ctrl)


plt.show()
