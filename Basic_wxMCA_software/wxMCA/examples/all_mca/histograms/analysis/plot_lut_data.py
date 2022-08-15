import json
import numpy
import matplotlib.pyplot as plt
import emorpho_histo

def get_peak_n_temp(file_name):
    degc_data = []
    hv_data = []
    led_data = []
    peak_data = []
    with open(file_name, 'r') as fin:
        for line in fin:
            data_dict = json.loads(line)
            
            degc = data_dict["arm_status"]["fields"]["x_temperature"]
            led = data_dict["arm_status"]["fields"]["led_val"]
            hv = data_dict["arm_ctrl"]["fields"]["cal_ov"]
            histo = data_dict["histo"]["fields"]["histogram"]
            y_max = max(histo[50:])
            x_max = 50+histo[50:].index(y_max)
            i_min = x_max-50
            i_max = x_max+50
            
            xmax, ymax, fwhm, net_counts, bck_counts, yl, yr, net_histo, fit_histo = emorpho_histo.do_gauss_fit(histo[i_min: i_max+1], bck_model=2, fwhm=22)
            
            #hx = [histo[n]*n for n in range(i_min, i_max+1)]
            #avg = sum(hx)/sum(histo[i_min: i_max+1])
            peak_data +=[xmax+i_min]
            degc_data += [degc]
            led_data += [led]
            hv_data += [hv]
            
    return degc_data, peak_data, led_data, hv_data
    
def line_plot(degc, y_data, ctrl):
    
    fig, ax = plt.subplots()
    lp = ax.plot(degc, y_data)
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
        
def line_plots(x_data, y_data_list, ctrl):
    colors = ["darkcyan", "deepskyblue"]
    fig, ax = plt.subplots()
    lp_list = []
    for n, y_data in enumerate(y_data_list):
        ctrl['line_ctrl']['color'] = colors[n]
        lp = ax.plot(x_data, y_data)
        plt.setp(lp, **ctrl['line_ctrl'])
        lp_list += [lp]
    
    ax.set_xlabel(ctrl['labels']['xlabel'] , **ctrl['labels']['xlabel_ctrl'])
    ax.set_ylabel(ctrl['labels']['ylabel'], **ctrl['labels']['ylabel_ctrl'])
    ax.set_title(ctrl['labels']['title'], **ctrl['labels']['title_ctrl'])
    ax.grid(**ctrl['grid_ctrl'])
    ax.set(**ctrl['axis_ctrl'])
        
    if ctrl['show']:
        plt.show()
        
def fit_data(degc, parameters, fit_range, degrees):
    a = fit_range[0]
    b = fit_range[1]
    coefficients = []
    parameter_fits = []
    for param, deg in zip(parameters, degrees):
        coeff = numpy.polynomial.polynomial.polyfit(degc[a:b], param[a:b], deg)
        par_fit = numpy.polynomial.polynomial.polyval(degc, coeff, tensor=False)
        coefficients += [coeff]
        parameter_fits += [par_fit]

        
    return coefficients, parameter_fits

import plot_controls as pc
wt = 0.7  # Weight for geometric averaging of the temperature
if 0:
    degc_raw, y_data, led_data, hv_data = get_peak_n_temp("histogram.json")
    with open("fit_data.txt", "w") as fout:
        fout.write(json.dumps({"degc": degc_raw, "peak": y_data, "led": led_data, "hv": hv_data}))
    
with open("fit_data.txt", "r") as fin:
    data = json.loads(fin.read())
degc_raw = data["degc"]
led_data = data["led"]
hv_data = data["hv"]
y_data = data["peak"]

N=len(degc_raw)
degc = [degc_raw[0]]
for n in range(1,N):
    degc += [degc[n-1] + wt*(degc_raw[n] - degc[n-1])]

# Fit the data
coeffs, par_fits = fit_data(degc, [led_data, hv_data], fit_range=[20, -200], degrees=[4,4])

# Compute LUT entries, normalized at 25degC
dt = 5 # degC
degc_min = dt*int((min(degc)//dt))
degc_max = dt*int((max(degc)//dt+1))
ndeg = (degc_max-degc_min)//dt+1
deg_lut = [degc_min + n*5 for n in range(ndeg)]
led_lut = numpy.polynomial.polynomial.polyval(deg_lut, coeffs[0], tensor=False)
hv_lut = numpy.polynomial.polynomial.polyval(deg_lut, coeffs[1], tensor=False)
idx_25 = deg_lut.index(25.0)
hv25 = hv_lut[idx_25]
led25 = led_lut[idx_25]
hv_lut = [hv/hv25 for hv in hv_lut]
led_lut = [led/led25 for led in led_lut]
print(deg_lut)

# Extend HV LUT to -30degC without extrapolation
N = (int(degc_min) + 30)//dt
hv0 = hv_lut[0]
hv_lut = [hv0]*N + hv_lut

# Extend LED LUT to -30degC with linear extrapolation
a_led = (led_lut[2]-led_lut[0])/(2*dt)
led0 = led_lut[0]
led_lut = [led0 - dt*n*a_led for n in range(N, 0, -1)] + led_lut

#extend LUT to +65degC via linear extrapolation
N = (70 - int(degc_max))//dt
hvm = hv_lut[-1]
a_hvm = (hv_lut[-1] - hv_lut[-3])/(2*dt)
hv_lut = hv_lut + [hvm+a_hvm*n*dt for n in range(1, N)]

ledm = led_lut[-1]
a_led = (led_lut[-1] - led_lut[-3])/(2*dt)
led_lut = led_lut + [ledm+a_led*n*dt for n in range(1, N)]

# Plot data and fits
line_plots(degc, [led_data, par_fits[0]], pc.led_plot_ctrl)
line_plots(degc, [hv_data, par_fits[1]], pc.hv_plot_ctrl)
line_plot([n/20 for n in range(len(degc))], y_data, pc.time_plot_ctrl)
line_plot([n/20 for n in range(len(degc))], degc, pc.degc_plot_ctrl)

print("DEG LUT:", ", ".join("{:.6f}".format(d) for d in range(-30, 70, dt)))
print("LED LUT:", ", ".join("{:.6f}".format(d) for d in led_lut))
print("HV LUT:", ", ".join("{:.6f}".format(d) for d in hv_lut))

# All must be 20 entries long
print(len(deg_lut), len(led_lut), len(hv_lut))

plt.show()
