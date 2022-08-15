import json
import matplotlib.pyplot as plt
import histo_analaysis

def get_peak_n_temp(file_name):
    hv_data = []
    dg_data = []
    degc_data = []
    peak_data = []
    fwhm_data = []
    led_data = []
    with open(file_name, 'r') as fin:
        for line in fin:
            data_dict = json.loads(line)
            
            degc = data_dict["fpga_status"]["user"]["temperature"]
            hv = data_dict["fpga_ctrl"]["user"]["high_voltage"]
            dg = data_dict["fpga_ctrl"]["user"]["digital_gain"]
            led = data_dict["fpga_status"]["fields"]["rr_10"]
            histo = data_dict["histo"]["registers"]
            y_max = max(histo[50:])
            x_max = 50+histo[50:].index(y_max)
            i_min = x_max-50
            i_max = x_max+50
            
            #xmax, ymax, fwhm, net_counts, bck_counts, yl, yr, net_histo, fit_histo = emorpho_histo.do_gauss_fit(histo[i_min: i_max+1], bck_model=2, fwhm=22)
            fit_results = histo_analysis.do_gauss_fit(histo[i_min: i_max+1], bck_model=2, fwhm=22)

            peak_data +=[fit_results["xmax"]+i_min]
            fwhm_data +=[fit_results["fwhm"]]
            degc_data += [degc]
            hv_data += [hv]
            dg_data += [dg]
            led_data += [led]
            
    with open("results.txt", 'w') as fout:
        fout.write(json.dumps({
            "hv_data": hv_data,
            "dg_data": dg_data,
            "degC_data": degc_data,
            "peak_data": peak_data,
            "fwhm_data": fwhm_data,
            "led_data": led_data,
        }))
        return degc_data, hv_data, dg_data, peak_data, fwhm_data, led_data

def get_template_diffs(template_file, histograms_file, xrange, yrange, xspan):
    differences = []
    with open(template_file, 'r') as fin:
        TH = json.loads(fin.read())["histo"]["registers"]  # Template histo
        
    with open(histograms_file, 'r') as fin:
        for line in fin:
            DH = json.loads(line)["histo"]["registers"]  # Data histo
            differences += [emorpho_histo.template_distance(TH, DH, xrange, yrange, xspan)]
    return differences
    
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
    line_plots = []
    fig, ax = plt.subplots()
    for xdat, ydat in zip(x_data, y_data):
        lp = ax.plot(xdat, ydat)
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
histo_file = "../user/emorpho/data/histograms_eRC4628.json"
template_file = "../user/emorpho/data/histo_662_template.json"

if 1:

    degc_data, hv_data, dg_data, peak_data, fwhm_data, led_data = get_peak_n_temp(histo_file)

    N = len(degc_data)
    t_data = [n/60 for n in range(N)]

    # Normalizations
    if 1:
        # find index of 25C
        for idx, x in enumerate(degc_data):
            if abs(x-25)<0.1:
                break

        # LED pulse height varies differently from LED energy; 
        # LED energy is multiplied by digital gain - which changes also.
        for n in range(N//2):
            led_data[2*n] = led_data[2*n+1]  # Replace LED_amplitude with LED_energy

        data_list = [hv_data, dg_data, led_data]
        N = len(hv_data)
        for data in data_list:
            x_22 = max(1, data[idx])  # When unused, LED = 0
            for n in range(N):
                data[n] /= x_22

    degc_lut, hv_lut, dg_lut, led_lut = get_lut(lut)


    # line_plot(degc_data, [peak_data], pc.peak_plot_ctrl)
    # line_plot(degc_data, [fwhm_data], pc.fwhm_plot_ctrl)

    line_plot([degc_data, degc_lut], [hv_data, hv_lut] , pc.hv_plot_ctrl)
    line_plot([degc_data, degc_lut], [dg_data, dg_lut], pc.dg_plot_ctrl)
    line_plot([degc_data, degc_lut], [led_data, led_lut], pc.led_plot_ctrl)
    
if 0:
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
