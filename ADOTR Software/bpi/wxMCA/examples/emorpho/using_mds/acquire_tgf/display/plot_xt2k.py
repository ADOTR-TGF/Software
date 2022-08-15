import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import math
import plot_controls_xt2k as pc
import json

def get_data(file_name, idx):
    """
        File structure: json strings, one per line; keys are "freeze" and "pulse"
        file_name: input file
        idx: index of pulse to display; use idx=-1 to display last trace in file
    """
    adc_sr = 80  # ADC Sampling rate in MHz
    pulse = []
    with open(file_name, 'r') as fin:
        lines = fin.readlines()
        
    dd = json.loads(lines[idx])
    pulse = dd["pulse"]
    
    N = len(pulse)
    x_data = [n/adc_sr for n in range(N)]  # Sample times in micro-seconds
    print(dd["freeze"])
    return x_data, pulse
    
def get_all_pulses(file_name):
    """
        File structure: json strings, one per line; keys are "freeze" and "pulse"
        file_name: input file
    """
    adc_sr = 80  # ADC Sampling rate in MHz
    pulses = []
    with open(file_name, 'r') as fin:
        lines = fin.readlines()
    
    for line in lines:   
        dd = json.loads(line)
        pulses += [dd["pulse"]]
    
    N = len(pulses[0])
    x_data = [n/adc_sr for n in range(N)]  # Sample times in micro-seconds
    return x_data, pulses

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
        
def line_plots(x_data, y_data, ctrl):
    """ here y_data is a list of pulses to be displayed """
    lp = []
    fig, ax = plt.subplots()
    for y_dat in y_data:
        lp += [ax.plot(x_data, y_dat)]
        plt.setp(lp[-1], **ctrl['line_ctrl'])
    
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
        

def plot_trace():
    file_name = "../data/list_mode_xtr2_10.dat"
    index = 0
    x_data, pulse = get_data(file_name, index)
    line_plot(x_data, pulse, pc.trace_plot_ctrl)
    
    x_data, pulses = get_all_pulses(file_name)
    line_plots(x_data, pulses, pc.trace_plot_ctrl)
    
    plt.show()
    
    
    
plot_trace()

