import json
import matplotlib.pyplot as plt
import emorpho_histo
import numpy

def get_peak_n_temp(file_name):
    hv_data = []
    dg_data = []
    degc_data = []
    peak_data = []
    fwhm_data = []
    led_data = []
    with open(file_name, 'r') as fin:
        for line_count, line in enumerate(fin):
            data_dict = json.loads(line)
            mca_id_str = data_dict["mca_id_str"]
            
            if mca_id_str in ["0x6001"]:
                degc_data += [data_dict["fpga_status"]["user"]["temperature"]]
                hv_data += [data_dict["fpga_ctrl"]["user"]["high_voltage"]]
                dg_data += [data_dict["fpga_ctrl"]["user"]["digital_gain"]]
                led_data += [data_dict["fpga_status"]["fields"]["rr_10"]]
                histo = data_dict["histogram"]["registers"]
            elif mca_id_str in ["0x103", "0x203"]:
                degc_data += [data_dict["fpga_status"]["user"]["temperature"]]
                hv_data += [data_dict["arm_ctrl"]["fields"]["cal_ov"]]
                dg_data += [data_dict["fpga_ctrl"]["user"]["digital_gain"]]
                led_data += [data_dict["fpga_status"]["fields"]["rr_10"]]
                histo = data_dict["histogram"]["registers"]
            elif mca_id_str in ["0x101", "0x201", "0x102", "0x202"]:
                degc_data += [data_dict["arm_status"]["fields"]["x_temperature"]]
                hv_data += [data_dict["arm_ctrl"]["fields"]["cal_ov"]]
                led_data += [data_dict["arm_status"]["fields"]["led_val"]]
                histo = data_dict["histogram"]["fields"]["histogram"]
            
            if mca_id_str in ["0x101", "0x201", "0x102", "0x202"]: 
                dg_data = [0]*len(degc_data)
            y_max = max(histo[50:])
            x_max = 50+histo[50:].index(y_max)
            i_min = x_max-50
            i_max = x_max+50
            
            xmax, ymax, fwhm, net_counts, bck_counts, yl, yr, net_histo, fit_histo = emorpho_histo.do_gauss_fit(histo[i_min: i_max+1], bck_model=2, fwhm=22)
            
            #hx = [histo[n]*n for n in range(i_min, i_max+1)]
            #avg = sum(hx)/sum(histo[i_min: i_max+1])
            peak_data +=[xmax+i_min]
            fwhm_data +=[fwhm]
            if line_count>0 and line_count % 100 == 0:
                print("Number of spectra processed: {}".format(line_count))
    
        if mca_id_str in ["0x6001", "0x103", "0x203"]:
            print("Integration_time=", data_dict["fpga_ctrl"]["user"]["integration_time"])
            
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

def get_template_diffs(th_file_idx, histograms_file, xrange, yrange, xspan):
    """
        th_file_idx: Either the file name of the template or the index 
        of the histogram we are going to use as a template.
    """
    differences = []
    if type(th_file_idx)==int:
        idx = th_file_idx
        with open(histograms_file, 'r') as fin:
            for n, line in enumerate(fin):
                if n == idx:
                    break
    else:
        with open(th_file_idx, 'r') as fin:
            for line in fin:
                break
    data_dict = json.loads(line)
    mca_id_str = data_dict["mca_id_str"]           
    if mca_id_str in ["0x6001", "0x103", "0x203"]:
        TH = data_dict["histogram"]["registers"]  # Template histo
    elif mca_id_str in ["0x101", "0x201", "0x102", "0x202"]:
        TH = data_dict["histogram"]["fields"]["histogram"]    # Template histo     
        
    with open(histograms_file, 'r') as fin:
        for line in fin:
            data_dict = json.loads(line)
            if mca_id_str in ["0x6001", "0x103", "0x203"]:
                DH = data_dict["histogram"]["registers"]  # Data histo
            elif mca_id_str in ["0x101", "0x201", "0x102", "0x202"]:
                DH = data_dict["histogram"]["fields"]["histogram"]    # Data histo 
                
            differences += [emorpho_histo.template_distance(TH, DH, xrange, yrange, xspan)]
    return differences

def get_lut(lut_file, mca_id_str):
    with open(lut_file, 'r') as fin:
        lut_dict = json.loads(fin.read())
    lut = lut_dict[mca_id_str]
    lut_len = lut["len"]
    Tmin = lut["tmin"]
    dT = lut["dt"]
    hv_ratios = lut["ov"]
    dg_ratios = lut["dg"]
    led_ratios = lut["led"]
    degc = [Tmin +n*dT for n in range(lut_len)]
    
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
        
def line_plots(x_data, y_data, ctrl):
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

def extend_lut(degc_data, degc_lut, new_lut, coeffs, extrapolate=[1,1]):
    """
        The function modifies new_lut in place by applying linear extrapolation
        beyond the range that was measured and fitted.
        degc_data is the list of measured temperatures.
    """
    dt = 10
    degc_min = min(degc_data)
    degc_max = max(degc_data)
    
    if extrapolate[0]:  # Extrapolate to the left
        two_dat = numpy.polynomial.polynomial.polyval([degc_min,degc_min+dt] , coeffs, tensor=False) 
        slope = (two_dat[1]-two_dat[0])/dt
        for idx,t in enumerate(degc_lut):
            if t<degc_min:
               new_lut[idx] = two_dat[0] + (t-degc_min)*slope 
            
    if extrapolate[1]:  # Extrapolate to the right
        two_dat = numpy.polynomial.polynomial.polyval([degc_max-dt,degc_max] , coeffs, tensor=False) 
        slope = (two_dat[1]-two_dat[0])/dt
        for idx,t in enumerate(degc_lut):
            if t>degc_max:
               new_lut[idx] = two_dat[1] + (t-degc_max)*slope 

def print_lut(degc_lut, new_hv_lut, new_dg_lut, new_led_lut):  # print in the format used in the C-code  
    t_min = degc_lut[0]
    dt = degc_lut[1] - degc_lut[0]
    n_lut = len(degc_lut)
    lut_str_list = []
    for lut in [new_hv_lut, new_dg_lut, new_led_lut]:
        if len(lut) == 0:
            lut = [1]*n_lut
        lut_str_list += [", ".join(["{:.6f}".format(d) for d in lut])+","]
    
    
    out_str = "{{ {}, {}, {},\n    {}\n    {}\n    {}\n    1 }};".format(n_lut, t_min, dt, lut_str_list[0], lut_str_list[1], lut_str_list[2])
    print(out_str)
    
def store_lut(file_name, degc_lut, new_hv_lut, new_dg_lut, new_led_lut):  # print in the format used in the C-code
    lut = {}
    t_min = degc_lut[0]
    dt = degc_lut[1] - degc_lut[0]
    n_lut = len(degc_lut)
    
    lut["tmin"] = t_min
    lut["dt"] = dt
    lut["len"] = n_lut
    lut["ov"] = [x for x in new_hv_lut]
    lut["dg"] = [x for x in new_dg_lut] if len(new_dg_lut)>0 else [1.0]*n_lut
    lut["led"] = [x for x in new_led_lut] if len(new_led_lut)>0 else [1.0]*n_lut
    lut["mode"] = 0
    
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(lut))

import plot_controls as pc


histograms_file = "./data/histograms_eRC4630_energy.json"  # Substitute your data file

template_index = 10

# Learn what type of MCA the histograms came from
with open(histograms_file, 'r') as fin:
    data_dict = json.loads(fin.readline())
    mca_id_str = data_dict["mca_id_str"]

if mca_id_str in ["0x6001", "0x103"]:
    keV_bin = 1    
elif mca_id_str in ["0x101"]:
    keV_bin = 2

diff_x_range = [int(50/keV_bin),int(1000/keV_bin)]

READ_SPECTRA = 1  # read energy spectra and perform peak fits; store peak summaries as raw results
CHECK_DATA_QUALITY = 1  # Compute energy spectrum differences to the template

    
if READ_SPECTRA:  # read energy spectra and perform peak fits; store peak summaries as raw results

    deg_data, hv_data, dg_data, peak_data, fwhm_data, led_data = get_peak_n_temp(histograms_file)
    fwhm_data = [f/p*100 for f, p in zip(fwhm_data, peak_data)]
    
    with open("raw_results.json", 'w') as fout:
        fout.write(json.dumps({"deg_data": deg_data, "hv_data":hv_data, "dg_data":dg_data, 
                               "peak_data":peak_data,"fwhm_data":fwhm_data, "led_data":led_data}))

if 1:  # read raw results, apply thermal relaxation correction and compute normalized LUT data. 
    with open("raw_results.json", 'r') as fin:
        dd = json.loads(fin.read())
    deg_data = dd["deg_data"]
    hv_data = dd["hv_data"]
    dg_data = dd["dg_data"]
    peak_data = dd["peak_data"]
    fwhm_data = dd["fwhm_data"]
    led_data = dd["led_data"]
    
    N = len(deg_data)
    t_data = [n/60 for n in range(N)]
    
    # wt = 0.075 for HV and R6233 PMT, and 1 measurement every 2 minutes (=> 27min time constant)
    # wt = 0.15 for 76mm NaI, and 1 measurement every 2 minutes (=> 13min time constant) 
    wt = 1
    
    degc_data = [deg_data[0]]
    for n in range(1,N):
        degc_data += [degc_data[n-1] + wt*(deg_data[n] - degc_data[n-1])]

    # Normalization

    # find index of 25C
    for idx, x in enumerate(degc_data):
        if abs(x-25)<0.1:
            break

    # Note that the LED amplitude response will be different from the LED_energy response.
    # The latter includes the effects of the digital gain, which also changes with temperature.
    data_list = [hv_data, dg_data, led_data]
    N = len(hv_data)
    for data in data_list:
        if len(data) == 0:
            continue
        x_25 = max(1, data[idx])  # When unused, LED = 0
        for n in range(N):
            data[n] /= x_25
            
    indices = [n for n in range(len(degc_data))]
            
    with open("raw_data_lut.csv", 'w') as fout:
        fout.write("no.,degc,hv,dg,led\n")
        for zt in zip(indices,degc_data,hv_data, dg_data, led_data):
            fout.write("{},{:.2f},{:.6f},{:.6f},{:.6f}\n".format(*zt))

    degc_lut, hv_lut, dg_lut, led_lut = get_lut("lookup_tables.json", "eRC4631")    


if 1:  # Plot existing LUT and new measured LUT
    pc.line_dot_ctrl["labels"]["xlabel"] = "Temperature, deg. C"
    pc.line_dot_ctrl["labels"]["ylabel"] = "High voltage ratio"
    pc.line_dot_ctrl["labels"]["title"] = "HV ratio vs deg. C"
    line_plots([degc_data, degc_lut], [hv_data, hv_lut] , pc.line_dot_ctrl)
    
    pc.line_dot_ctrl["labels"]["ylabel"] = "Digital gain ratio"
    pc.line_dot_ctrl["labels"]["title"] = "DG ratio vs deg. C"
    line_plots([degc_data, degc_lut], [dg_data, dg_lut], pc.line_dot_ctrl)
    
    pc.line_dot_ctrl["labels"]["ylabel"] = "LED ratio"
    pc.line_dot_ctrl["labels"]["title"] = "LED ratio vs deg. C"
    line_plots([degc_data, degc_lut], [led_data, led_lut], pc.line_dot_ctrl)
    
    pc.line_dot_ctrl["labels"]["ylabel"] = "fwhm, %"
    pc.line_dot_ctrl["labels"]["title"] = "Energy resolution vs deg. C"
    line_plot(degc_data, fwhm_data, pc.line_dot_ctrl)
    
    pc.line_dot_ctrl["labels"]["ylabel"] = "peak pos."
    pc.line_dot_ctrl["labels"]["title"] = "Peak position vs deg. C"
    line_plot(degc_data, peak_data, pc.line_dot_ctrl)
    
    pc.line_dot_ctrl["labels"]["xlabel"] = "Measurement no."
    pc.line_dot_ctrl["labels"]["ylabel"] = "Temperature."
    pc.line_dot_ctrl["labels"]["title"] = "Temperature vs time"
    line_plot([n for n in range(len(deg_data))], degc_data, pc.line_dot_ctrl)
    
if 0:  # Plot existing LUT only
    pc.line_dot_ctrl["labels"]["xlabel"] = "Temperature, deg. C"
    pc.line_dot_ctrl["labels"]["ylabel"] = "High voltage ratio"
    pc.line_dot_ctrl["labels"]["title"] = "HV ratio vs deg. C"
    line_plot(degc_data, hv_data, pc.line_dot_ctrl)
    
    pc.line_dot_ctrl["labels"]["ylabel"] = "Digital gain ratio"
    pc.line_dot_ctrl["labels"]["title"] = "DG ratio vs deg. C"
    line_plot(degc_data, dg_data, pc.line_dot_ctrl)
    
    pc.line_dot_ctrl["labels"]["ylabel"] = "LED ratio"
    pc.line_dot_ctrl["labels"]["title"] = "LED ratio vs deg. C"
    line_plot(degc_data, led_data, pc.line_dot_ctrl)

if CHECK_DATA_QUALITY:  # Compute energy spectrum differences to the the template
    if histograms_file.split('.', 1)[0].endswith("amplitude"):
        diffs = get_template_diffs(10, histograms_file, [20, 250], [], 12)
    else:
        diffs = get_template_diffs(10, histograms_file, diff_x_range, [], 50)

    xd = [x for x in range(len(diffs))]

    pc.scatter_plot_ctrl["labels"]["xlabel"] = "Temperature, deg. C"
    pc.scatter_plot_ctrl["labels"]["ylabel"] = "Template diff"
    pc.scatter_plot_ctrl["labels"]["title"] = "Template separation vs deg. C"

    line_plot([xd], [diffs], pc.scatter_plot_ctrl)    
    
if 1: # Fit the data and extract new LUT information
       
    if mca_id_str in ["0x6001", "0x103"]:
        coeffs, par_fits = fit_data(degc_data, [hv_data, dg_data, led_data], fit_range=[20, -1], degrees=[4,4,4])
        new_hv_lut = numpy.polynomial.polynomial.polyval(degc_lut, coeffs[0], tensor=False) 
        new_dg_lut = numpy.polynomial.polynomial.polyval(degc_lut, coeffs[1], tensor=False) 
        new_led_lut = numpy.polynomial.polynomial.polyval(degc_lut, coeffs[2], tensor=False) 
        
        extend_lut(degc_data, degc_lut, new_hv_lut, coeffs[0], extrapolate=[1,1])
        extend_lut(degc_data, degc_lut, new_dg_lut, coeffs[1], extrapolate=[1,1])
        extend_lut(degc_data, degc_lut, new_led_lut, coeffs[2], extrapolate=[1,1])
        
        print_lut(degc_lut, new_hv_lut, new_dg_lut, new_led_lut)  # print in the format used in the C-code
        store_lut("new_lut.json", degc_lut, new_hv_lut, new_dg_lut, new_led_lut)  # Store in the format used in the Python code
             
        pc.line_dot_ctrl["labels"]["xlabel"] = "Temperature, deg. C"
        pc.line_dot_ctrl["labels"]["ylabel"] = "High voltage ratio"
        pc.line_dot_ctrl["labels"]["title"] = "HV ratio vs deg. C"
        line_plots([degc_data, degc_lut, degc_data, degc_lut], [hv_data, hv_lut, par_fits[0], new_hv_lut] , pc.line_dot_ctrl)
        
        pc.line_dot_ctrl["labels"]["ylabel"] = "Digital gain ratio"
        pc.line_dot_ctrl["labels"]["title"] = "DG ratio vs deg. C"
        line_plots([degc_data, degc_lut, degc_data, degc_lut], [dg_data, dg_lut, par_fits[1], new_dg_lut] , pc.line_dot_ctrl)
        
        pc.line_dot_ctrl["labels"]["ylabel"] = "LED ratio"
        pc.line_dot_ctrl["labels"]["title"] = "LED ratio vs deg. C"
        line_plots([degc_data, degc_lut, degc_data, degc_lut], [led_data, led_lut, par_fits[2], new_led_lut] , pc.line_dot_ctrl)
                
        
    elif mca_id_str in ["0x101"]:
        coeffs, par_fits = fit_data(degc_data, [hv_data, led_data], fit_range=[20, -1], degrees=[4,4])
        new_hv_lut = numpy.polynomial.polynomial.polyval(degc_lut, coeffs[0], tensor=False)
        new_led_lut = numpy.polynomial.polynomial.polyval(degc_lut, coeffs[1], tensor=False)
        extend_lut(degc_data, degc_lut, new_hv_lut, coeffs[0], extrapolate=[1,1])
        extend_lut(degc_data, degc_lut, new_led_lut, coeffs[1], extrapolate=[1,1])
        print_lut(degc_lut, new_hv_lut, [], [])  # print in the format used in the C-code
        store_lut("new_lut.json", degc_lut, new_hv_lut, [], new_led_lut)  # Store in the format used in the Python code

        
        pc.line_dot_ctrl["labels"]["xlabel"] = "Temperature, deg. C"
        pc.line_dot_ctrl["labels"]["ylabel"] = "High voltage ratio"
        pc.line_dot_ctrl["labels"]["title"] = "HV ratio vs deg. C"
        line_plots([degc_data, degc_lut, degc_data, degc_lut], [hv_data, hv_lut, par_fits[0], new_hv_lut] , pc.line_dot_ctrl)
        
        pc.line_dot_ctrl["labels"]["ylabel"] = "LED ratio"
        pc.line_dot_ctrl["labels"]["title"] = "LED ratio vs deg. C"
        line_plots([degc_data, degc_lut, degc_data, degc_lut], [led_data, led_lut, par_fits[1], new_led_lut] , pc.line_dot_ctrl)
        
        print_lut(degc_lut, new_hv_lut, [1.0]*len(degc_lut), new_led_lut)  # print in the format used in the C-code
           
    

plt.show()
