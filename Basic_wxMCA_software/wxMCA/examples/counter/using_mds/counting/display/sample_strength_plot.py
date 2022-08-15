import math
import json
import matplotlib.pyplot as plt

def collect_probability_data():
    """
        Read the 'sample_records.json' data file and plot alarm probabilities
    """
    all_data = []
    with open("../data/sample_records.json", 'r') as fin:
        for line in fin:
            all_data += [json.loads(line)]
    
    num_records = len(all_data)
    y_prob_low = [-math.log10(all_data[n]["fields"]["bck_low_probability"]) for n in range(num_records)]
    y_prob = [-math.log10(all_data[n]["fields"]["bck_probability"]) for n in range(num_records)]
    y_prob_high = [-math.log10(all_data[n]["fields"]["bck_high_probability"]) for n in range(num_records)]
    
    x_data = [all_data[n]["fields"]["run_time_sample"] for n in range(num_records)]

    return x_data, [y_prob_low, y_prob, y_prob_high]
    
def collect_count_rate_data():
    """
        Read the 'sample_records.json' data file and plot difference count rates and errors
    """
    all_data = []
    with open("../data/sample_records.json", 'r') as fin:
        for line in fin:
            all_data += [json.loads(line)]
    
    num_records = len(all_data)
    y_diff_low = [all_data[n]["fields"]["roi_rate_diff"]-all_data[n]["fields"]["roi_rate_diff_err"] for n in range(num_records)]
    y_diff = [all_data[n]["fields"]["roi_rate_diff"] for n in range(num_records)]
    y_diff_high = [all_data[n]["fields"]["roi_rate_diff"]+all_data[n]["fields"]["roi_rate_diff_err"] for n in range(num_records)]
    
    x_data = [all_data[n]["fields"]["run_time_sample"] for n in range(num_records)]

    return x_data, [y_diff_low, y_diff, y_diff_high]
    
def line_plots(x_data, y_sets, ctrl):
    
    fig, ax = plt.subplots()
    lp = []
    num_lines = len(y_sets)
    colors = ["DarkOrange", "SeaGreen", "DodgerBlue"]
    for n in range(num_lines):
        lp += [ax.plot(x_data, y_sets[n])]
        plt.setp(lp[-1], **ctrl['line_ctrl'])
        plt.setp(lp[-1], color=colors[n])
        
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

import sample_strength_plot_controls as pc
x_data, y_data = collect_probability_data()
line_plots(x_data, y_data, pc.prob_plot_ctrl)

x_data, y_data = collect_count_rate_data()
line_plots(x_data, y_data, pc.diff_rate_plot_ctrl)


plt.show()
