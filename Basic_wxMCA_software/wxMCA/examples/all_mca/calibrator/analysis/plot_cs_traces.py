import math
import json
import matplotlib.pyplot as plt
import emorpho_histo


def get_pulses(file_name, line_no):
 
    pulses = []
    dc = 103.75
    with open(file_name, 'r') as fin:
        for count, line in enumerate(fin):
            if count != line_no:
                continue
            data_dict = json.loads(line)
            for pulse in data_dict["pulses"]:
                bl = pulse[252]/32-dc  # baseline test
                norm = pulse[259]/32-dc  # Peak height test
                tail = [(pulse[n+2]-pulse[n])/32 for n in range(261,400)]
                re = max(tail)  # rising edge
                
                #print(norm)
                if 160<norm<220 and bl < 3 and re < 10:
                    pulses += [[p/32-dc for p in pulse]]
    N = len(pulse)
    t_data = [n/40 for n in range(N)]
    print("Temperature = ", data_dict["fpga_status"]["user"]["temperature"])
    return t_data, pulses

    
def line_plot(x_data, y_data, ctrl):
    line_plots = []
    fig, ax = plt.subplots()
    for ydat in y_data:
        lp = ax.plot(x_data, ydat)
        plt.setp(lp, **ctrl['line_ctrl'])
        line_plots += [lp]
    ctrl['line_ctrl']["color"] = "red"
    plt.setp(line_plots[-1], **ctrl['line_ctrl'])
    
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

import plot_controls as pc
slot = 15
idx = 0

t_data, pulses = get_pulses("./data/2021_10_31/pulses_eRC4624.json", slot)
line_plot(t_data, pulses, pc.pulse_plot_ctrl)



plt.show()
