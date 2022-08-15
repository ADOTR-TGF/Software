import json
import matplotlib.pyplot as plt
import emorpho_histo
import math

def get_peaks(file_name):
    # dwell_time = 10
    peak_data = []
    baselines = []
    count = 0
    with open(file_name, 'r') as fin:
        for line in fin:
            count += 1
            data_dict = json.loads(line)
            histo = data_dict["histogram"]
            i_min = 100
            i_max = 900
            if True:
                summe = sum(histo[i_min:i_max])
                if summe > 0:
                    avg = sum([n*histo[n] for n in range(i_min, i_max)])/summe
                    peak_data +=[avg]
                    baselines += [data_dict["lt_ratio"]]
                else:
                    print(count, sum(histo))
            else:
                res = emorpho_histo.do_gauss_fit(histo[i_min:i_max], bck_model=2, fwhm=23)
                peak_data +=[res[0]+i_min]
            
            
    
    #statistics
    lp = len(peak_data)
    avg = sum(peak_data)/lp
    var_list = [(p-avg)**2 for p in peak_data]
    std_dev = math.sqrt(sum(var_list)/(lp-1))
    print("Avg, std_dev:", avg, std_dev)
    
    x_data = [x for x in range(len(peak_data))]
    return x_data, [peak_data, baselines]
    
def line_plot(x_data, y_data, ctrl):
    
    fig, ax = plt.subplots()
    lp1 = ax.plot(x_data, y_data[0])
    plt.setp(lp1, **ctrl['line_ctrl'])
    
    lp2 = ax.plot(x_data, y_data[1])
    plt.setp(lp1, **ctrl['line_ctrl'])
    
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
x_data, y_data = get_peaks("../data/pulser_log.json")
line_plot(x_data, y_data, pc.peak_plot_ctrl)


plt.show()
