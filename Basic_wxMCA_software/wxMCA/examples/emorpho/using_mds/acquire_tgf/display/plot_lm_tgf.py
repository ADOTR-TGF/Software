import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import math
import plot_controls_lm as pc
import time

def get_data(file_name):
    adc_sr = 80.0e6
    peak = []
    tbnt = []
    energy = []
    psd = []
    wc = []
    with open(file_name, 'r') as fin:
        for line in fin:
            lm_dd = json.loads(line)
            peak += lm_dd["lm_data"]["peak"] 
            tbnt += lm_dd["lm_data"]["tbnt"] 
            energy += lm_dd["lm_data"]["energies"]
            psd += lm_dd["lm_data"]["psd"]
            wc += [d/adc_sr for d in lm_dd["lm_data"]["wc"]]
    
    N=len(energy)
    x_data = [n for n in range(N)]
    return x_data, peak, tbnt, energy, psd, wc  # peak, tbnt, energies, short_sums and wall_clock data

def line_plot(x_data, y_data, ctrl):
    
    fig, ax = plt.subplots()
    lp1 = ax.plot(x_data, y_data)
    plt.setp(lp1, **ctrl['line_ctrl'])
    
    #lp2 = ax.plot(x_data, y_data[1])
    #plt.setp(lp2, **ctrl[1]['line_ctrl'])
    
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
        

def plot_listmode():
    file_name = "../data/list_mode_tgf_1.json"
    x_data, peak, tbnt, energy, psd, wc = get_data(file_name)
    line_plot(x_data, peak, pc.energy_plot_ctrl)
    line_plot(x_data, tbnt, pc.energy_plot_ctrl)
    line_plot(x_data, energy, pc.energy_plot_ctrl)
    line_plot(x_data, psd, pc.energy_plot_ctrl)
    line_plot(x_data, wc, pc.wc_plot_ctrl)
    plt.show()
    
plot_listmode()

