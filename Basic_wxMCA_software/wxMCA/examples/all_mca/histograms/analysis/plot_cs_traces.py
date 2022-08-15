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

def get_avg_pulse(file_name, line_no):
    dc = 103.75
    avg_pulse = [0]*1024
    
    with open(file_name, 'r') as fin:
        for count, line in enumerate(fin):
            if count != line_no:
                continue
            data_dict = json.loads(line)
            num_pulses = 0
            for pulse in data_dict["pulses"]:
                bl = pulse[252]/32-dc  # baseline test
                norm = pulse[259]/32-dc  # Peak height test
                tail = [(pulse[n+2]-pulse[n])/32 for n in range(261,400)]
                re = max(tail)  # rising edge
                
                #print(norm)
                if 160<norm<220 and bl < 3 and re < 10:
                    num_pulses += 1
                    avg_pulse = [a+p/32-dc for a,p in zip(avg_pulse, pulse)]
    
    avg_pulse = [ a/num_pulses for a in avg_pulse]
    N = len(pulse)
    t_data = [n/40 for n in range(N)]
    print("Temperature = ", data_dict["fpga_status"]["user"]["temperature"])
    return t_data, avg_pulse

def single_exp(off, A, tau):
    pulse = [0]*1024
    for n in range(off, 1024):
        pulse[n] += A*math.exp(-(n-off)/tau)
    
    #return pulse
    # Simulate effect of the electronic: 3 consecutive first order filters
    tau_list = [2.0, 0.5, 2.0]  # in units of 25ns
    pulse_out = pulse[:]
    M=10
    dt = 1/M
    for tau in tau_list:       
        for n in range(1024):
            v_out = pulse[n-1]
            for m in range(M):
                v_out += (pulse[n]-v_out)*dt/tau
            pulse[n] = v_out
    
    print(187/max(pulse)*A)
    return pulse
    
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

if 0:
    t_data, pulses = get_pulses("./data/2021_10_31/pulses_eRC4624.json", slot)
    line_plot(t_data, pulses, pc.pulse_plot_ctrl)

if 1:
    t_data, pulse_0 = get_avg_pulse("./data/2021_10_31/pulses_eRC4623.json", 0)
    t_data, pulse_1 = get_avg_pulse("./data/2021_10_31/pulses_eRC4623.json", 15)

    one_exp = single_exp(255, 375, 4.5)
    first_exp = single_exp(255, 240, 4.0)
    second_exp = single_exp(255, 90, 19)
    
    double_exp = [f+s for f,s in zip(first_exp, second_exp)]
    diff_pulse = [p1-p0 for p1, p0 in zip(pulse_1, one_exp)]
    #line_plot(t_data, [pulse_1, one_exp, double_exp], pc.pulse_plot_ctrl)
    line_plot(t_data, [pulse_0, pulse_1, one_exp], pc.pulse_plot_ctrl)
    #line_plot(t_data, [one_exp], pc.pulse_plot_ctrl)



plt.show()
