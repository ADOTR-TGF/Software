import json
import matplotlib.pyplot as plt
import emorpho_histo

lut = [
20, -30, 5,
	# Operating voltage ratios
	1.10270, 1.08976, 1.07755, 1.06605, 1.05528, 1.04522, 1.03588, 1.02727, 1.01937, 1.01219, 
	1.00574, 1.00000, 0.99498, 0.99068, 0.98711, 0.98425, 0.98211, 0.98069, 0.97999, 0.98001,
	
    # Digital gain, or perhaps trigger threshold 
	0.60297, 0.63453, 0.66700, 0.70038, 0.73466, 0.76985, 0.80594, 0.84294, 0.88085, 0.91966, 
	0.95938, 1.00000, 1.04153, 1.08396, 1.12730, 1.17155, 1.21670, 1.26276, 1.30972, 1.35759,
 
	# LED brightness 
	1.29851, 1.27104, 1.24363, 1.21628, 1.18901, 1.16180, 1.13467, 1.10760, 1.08060, 1.05366, 
	1.02680, 1.00000, 0.97327, 0.94661, 0.92002, 0.89349, 0.86703, 0.84065, 0.81432, 0.78807,
  
	0  # Lock bit
];

def get_lut(lut):
    NLUT = lut[0]
    Tmin = lut[1]
    dT = lut[2]
    hv_ratios = [r for r in lut[3:23]]
    dg_ratios = [r for r in lut[23:43]]
    led_ratios = [r for r in lut[43:63]]
    degc = [Tmin +n*dT for n in range(NLUT)]
    
    return degc, hv_ratios, dg_ratios, led_ratios


    
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

import plot_controls as pc
degc_data, hv_ratios, dg_ratios, led_ratios = get_lut(lut)

N = len(degc_data)
t_data = [n/60 for n in range(N)]
pc.line_dot_ctrl["labels"]["xlabel"] = "Temperature, deg. C"
pc.line_dot_ctrl["labels"]["ylabel"] = "High voltage ratio"
pc.line_dot_ctrl["labels"]["title"] = "HV ratio vs deg. C"
line_plot(degc_data, hv_ratios, pc.line_dot_ctrl)
pc.line_dot_ctrl["labels"]["ylabel"] = "Digital gain ratio"
pc.line_dot_ctrl["labels"]["title"] = "DG ratio vs deg. C"
line_plot(degc_data, dg_ratios, pc.line_dot_ctrl)
pc.line_dot_ctrl["labels"]["ylabel"] = "LED ratio"
pc.line_dot_ctrl["labels"]["title"] = "LED ratio vs deg. C"
line_plot(degc_data, led_ratios, pc.line_dot_ctrl)


plt.show()
