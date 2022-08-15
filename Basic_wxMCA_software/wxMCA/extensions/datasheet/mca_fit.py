import math
import random
import matplotlib
import matplotlib.pyplot as plt
import random
import json

def mca_display(file_name, serial_number, index=-1):
    """
    Open a multiline histogram file, extract the last histogram, and display.
    """
    histo, settings = get_histo(file_name, index)
    lh = len(histo)
    xdat = [float(n) for n in range(lh)]
    
    fig, ax = plt.subplots(num=1, clear=True)
    if False:  
        # Bar graph
        lp1 = ax.bar(xdat, histo, width=1)  # 
        plt.setp(lp1, alpha=0.5)
    else:
        # Line graph
        lp1 = ax.plot(xdat, histo)
        ax.fill_between(range(lh), histo, 0, alpha=0.5, color="PowderBlue")
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
    
    ax.set(ylabel="Counts / Bin", xlabel="Energy, bin")
    ax.set(title="Energy histogram, {}".format(serial_number))
    
    plt.show()

def mca_plot_fit(file_name="./data/test_histo.json", setup={}, index=-1, imin=560, imax=760, keV_bin = 2.0):
    histo, settings = get_histo(file_name, index)
    serial_number = settings["SERIAL_NUMBER"]
    lh = len(histo)
    # off = 200
    # hmax = max(histo[off:])
    # idx_max = off + histo[off:].index(hmax)
    
    imin = int(imin/keV_bin+0.5)
    imax = int(imax/keV_bin+0.5)
    results = do_gauss_fit(histo[imin:imax], bck_model=2, fwhm=50/keV_bin)
    xmax, ymax, fwhm, counts, bck, yl, yr, net_histo, fit_histo = results
            
    peak_pos = xmax + float(imin)
    dE_E = fwhm/peak_pos * 100
    print("Peak: {:.2f}, fwhm: {:.2f}%".format(peak_pos, dE_E))
    
    # Plot it
    x_data = [n*keV_bin for n in range(lh)]
    fig, ax = plt.subplots(num=1, clear=True)
    if False:  
        # Bar graph
        lp1 = ax.bar(x_data, histo, width=1)  # 
        plt.setp(lp1, alpha=0.5)
    else:
        # Line graph
        lp1 = ax.plot(x_data, histo)
        ax.fill_between(x_data, histo, 0, alpha=0.5, color="PowderBlue")
        ax.set_xlim(left=0, right=1000)
        ax.set_ylim(bottom=0)
    
    lp2 = ax.plot(x_data[imin: imax], fit_histo, '-')    
    plt.setp(lp2, color="red")
    
    ax.set(ylabel="Counts / Bin", xlabel="Energy, bin")
    ax.set(title="Energy histogram, {}, fwhm={:.2f}%".format(serial_number, dE_E))
    
    bbox_args = dict(boxstyle="round", pad=0.5, ec="#FF4500", fc=(0.9, 0.9, 0.9, 0.8), linewidth=2)  # fill, bounds(l,b,w,h) are ignored
    ax.annotate('Cs-137\nfwhm={:.2f}%'.format(dE_E), fontsize=10,
                xycoords='axes fraction', xy=(0.75, 0.7), ha="left", va="bottom", bbox=bbox_args)
    
    fig.savefig("./data_sheets/mca_{}.png".format(serial_number), dpi=300)
    fig.savefig("./data_sheets/mca_{}.svg".format(serial_number))
    
    
    make_data_sheet(setup, settings)
    
    plt.show()

def get_histo(file_name, index=-1):
    """
        Read line number index (count starts at 1) and extract histogram
        index = -1 means last line in file
    """
    with open(file_name, 'r') as fin:
        if index > 0:
            for n in range(index):
                line = fin.readline()
        else:  # get index's line from the end of the file
            num_lines = 0  # Find number of lines
            while True:
                line = fin.readline()
                if(len(line)==0):
                    break
                num_lines += 1
            index = num_lines + index  # find absolute line index
            #print(num_lines, index)
            fin.seek(0)  # rewind
            for n in range(index+1):
                line = fin.readline()    
    #print(line)
    dd = json.loads(line)
    histo = dd["histo"]["registers"]
    num_bins = len(histo)
    
    SN = dd["serial_number"]
    if dd["mca_id_str"] == 0x6001:
        hv = dd["fpga_ctrl"]["user"]["high_voltage"]
        temperature = dd["fpga_status"]["user"]["temperature"]
    else:
        hv = dd["arm_status"]["fields"]["voltage_target"]
        temperature = dd["arm_status"]["fields"]["x_temperature"]
        
    # FPGA settings
    adc_speed = dd["fpga_status"]["user"]["adc_sr"]
    build_no = dd["fpga_status"]["fields"]["build"]
    custom_no = dd["fpga_status"]["fields"]["build"]
        
    thr = dd["fpga_ctrl"]["user"]["pulse_threshold"]
    gain = dd["fpga_status"]["user"]["impedance"]
    integration_time = dd["fpga_ctrl"]["user"]["integration_time"]
    digital_gain = dd["fpga_ctrl"]["user"]["digital_gain"]
    
    settings = {
        "SERIAL_NUMBER": SN[0:min(8, len(SN))],
        "SHORT_SN": SN[0:min(8, len(SN))],
        "BUILD_NO": build_no,
        "CUSTOM_NO": custom_no,
        "TEMPERATURE": "{:.2f}".format(temperature),
        "NV-MEM": "OK",
        "TRIGGER_THRESHOLD": "{:.0f} mV".format(thr*1000),
        "INTEGRATION_TIME": "{:.2f}&micro;s".format(integration_time*1e6),
        "ELECTRONIC_GAIN": "{:.0f}&Omega;".format(gain),
        "DIGITAL_GAIN": "{:.2f}".format(digital_gain),
        "HIGH_VOLTAGE": "{:.2f} V".format(hv),
        "ADC_SPEED": "{:.0f} MHz".format(int(adc_speed/1e6))
    }
    return histo, settings


def make_data_sheet(test_setup, settings):
    SN = settings["SERIAL_NUMBER"]
    template_dict = {
        "PMT-1K": "./html/data_sheet_template_pmt1k.html",
        "PMT-3K": "./html/data_sheet_template_pmt3k.html",
        "SiPM-1K": "./html/data_sheet_template_sipm1k.html",
        "SiPM-3K": "./html/data_sheet_template_sipm3k.html",
        "eMorpho": "./html/data_sheet_template_emorpho.html"
    }
    fin = open(template_dict[test_setup["MCA_TYPE"]], 'r')
    ds_template = fin.read()
    fin.close()
    for key in test_setup:
        ds_template = ds_template.replace(key, str(test_setup[key]))
    for key in settings:
        ds_template = ds_template.replace(key, str(settings[key]))
    
    ds_template = ds_template.replace("HISTOGRAM_IMAGE", "mca_{}.svg".format(SN))
    fout = open("./data_sheets/ds_{}.html".format(SN), 'w')
    fout.write(ds_template)
    fout.close()

def do_gauss_fit(histo, bck_model=0, fwhm=50):
    """The histo array only contains one peak;
    Left and right ends may be minima of a smoothed version of the histogram
    fwhm is an estimate in bins, not % . 
    bck_model = 0, 1, or 2: 0=>no background, 1=>sloped background, 2=> low-angle scatter background
    For bck_model=2, the count rate difference yr-yl is attributed to low-angle scattering, not a background slope.
    An abrupt scatter corner, softened by energy resolution, is described well by a yl*(1-tanh((x-x_peak)/(1.175*sigma))) function, 
    cf mca_corner.png and test_corner().
    x_peak is the corner edge.  For a full-energy peak, the low-angle scatter corner occurs exactly at x_peak.
    Set bck_model=1 to use a linear sloped background instead of scatter background.
    """
    lh = len(histo)
    if lh <= 6:
        xmax = int(lh/2.0)
        return xmax, histo[xmax], 0, 0, 0, 0
    yl = sum(histo[0:5])/5.0
    yr = sum(histo[-5:])/5.0
    
    
    if bck_model==1:
        num_it = 1
    else:
        num_it = 3
    
    xmax = histo.index(max(histo))    
    for n_it in range(num_it):
        if fwhm <= 0:
            fwhm = 60.0
        sigma = fwhm / math.sqrt(8.0*math.log(2))
        if bck_model==0:  # Constant background
            y_avg = (yl+yr)/2.0
            bck_histo = [y_avg for h in histo]  # background histogram
            net_histo = [h-y_avg for h in histo]  # background-subtracted histogram
        elif bck_model==1:  # sloped background
            slope = (yr-yl)/float(lh-5)
            bck_histo = [(yl + slope*n) for n, h in enumerate(histo)]  # background histogram
            net_histo = [h-b for h, b in zip(histo, bck_histo)]  # background-subtracted histogram
        else:
            bck_histo = [yr + (yl-yr)*(1-math.tanh((n-xmax)/(1.175*sigma)))/2.0 for n in range(lh)]  # constant background plus low-angle scattering
            net_histo = [h-b for h, b in zip(histo, bck_histo)]  # background-subtracted histogram
        
        ymax, xmax, sigma = stable_fit(net_histo)
        fwhm = math.sqrt(8.0*math.log(2)) * sigma
    
    fit_histo = [b+ymax*math.exp(-0.5*((x-xmax)/sigma)**2) for b,x in zip(bck_histo, range(lh))]
    net_counts = sum(net_histo)
    bck_counts = sum(histo) - net_counts
        
    return xmax, ymax, fwhm, net_counts, bck_counts, yl, yr, net_histo, fit_histo
    
def stable_fit(histo):
    """
    histo is supposed to be a simple Gaussian; all background has been subtracted
    """
    # quick estimates
    
    ymax = max(histo)
    xmax = histo.index(ymax)
    level = ymax/2
    for imin in range(xmax):
        if histo[imin] >= level:
            break
    for imax in range(xmax, len(histo)):
        if histo[imax] <= level:
            break
    fwhm = imax-imin
    sigma = fwhm / math.sqrt(8.0*math.log(2))
    
    # We will always have three Chi-Square values Fl, Fm, Fr for par-dp, par, par+dp
    # Then we compute a new iteration of par as: par += -0.5*(Fr-Fl)/(Fr+Fl-2*Fm)  (after some range checks)
    Fm = compute_chi_sqr(histo, ymax, xmax, sigma)

    F_list = [Fm]
    steps = [math.sqrt(ymax), 2.0, 0.1*sigma]
    for iteration in range(8):
        
        dy = steps[0]
        ymax_l = ymax-dy
        ymax_r = ymax+dy
        Fl = compute_chi_sqr(histo, ymax_l, xmax, sigma)
        Fr = compute_chi_sqr(histo, ymax_r, xmax, sigma)
        try:
            dy_max = -0.5*(Fr-Fl)/(Fr+Fl-2*Fm)*dy
        except:
            dy_max = 0
        ynew = max(0.5, ymax + dy_max)
        F = compute_chi_sqr(histo, max(0.5, ynew), xmax, sigma)
        if F < Fm:
            Fm = F
            ymax = ynew
            steps[0] = abs(dy_max)/2.0
            
        
        dx = steps[1]
        xmax_l = xmax-dx
        xmax_r = xmax+dx
        Fl = compute_chi_sqr(histo, ymax, xmax_l, sigma)
        Fr = compute_chi_sqr(histo, ymax, xmax_r, sigma)
        try:
            dx_max = -0.5*(Fr-Fl)/(Fr+Fl-2*Fm)*dx
        except:
            dx_max = 0
        xnew = xmax + dx_max
        F = compute_chi_sqr(histo, ymax, xnew, sigma)
        if F < Fm:
            Fm = F
            xmax = xnew
            steps[1] = abs(dx_max)/2.0
        
        ds = steps[2]
        sigma_l = sigma-ds
        sigma_r = sigma+ds
        Fl = compute_chi_sqr(histo, ymax, xmax, sigma_l)
        Fr = compute_chi_sqr(histo, ymax, xmax, sigma_r)
        try:
            ds_max = -0.5*(Fr-Fl)/(Fr+Fl-2*Fm)*ds
        except:
            ds_max = 0
        sigma_new = sigma + ds_max
        F = compute_chi_sqr(histo, ymax, xmax, sigma_new)
        if F < Fm:
            Fm = F
            sigma = sigma_new
            steps[2] = abs(ds_max)/2.0
            
        F_list += [Fm]
        
        #print('{:.4g}, {:.4g}, {:.4g} || {:.4g}, {:.4g}, {:.4g}'.format( dy_max, dx_max, ds_max, ymax, xmax, sigma))
    #print(' '.join('{:.2f}'.format(f) for f in F_list))
    return ymax, xmax, sigma
        

def compute_chi_sqr(histo, ymax, xmax, sigma):
    """
    Compute Chi-squared for a Gaussian; weights are not Poisson weights.  
    For regions with small counts, we also have less precise knowledge of what the error is.  
    It is a combination of statistical and systematic errors inherent in the model.
    """
    chi_sqr = 0
    for x,h in enumerate(histo):
        chi_sqr += (h-ymax*math.exp(-0.5*((x-xmax)/sigma)**2))**2/math.sqrt(h) if h>1.0 else 0.0
    return chi_sqr


def make_test_histo():
    xmax = 662
    fwhm = 40
    sigma = fwhm/math.sqrt(8.0*math.log(2.0))
    histo = [0]*3000
    for n in range(1000000):
        x = random.gauss(xmax, sigma)
        idx = int(x+0.5)
        histo[idx] += 1
    return histo


test_setup_81T = {
        "PART_NUMBER": "PMT-3K-40-N81T",
        "MCA_TYPE": "PMT-3K",
        "HV_BASE_TYPE": "HV_CPLD Rev F",
        "DETECTOR": "NaI(Tl), 32x2 inch",  # NaI(Tl), 2x2 inch, B380 38x38mm
        "PMT_TYPE": "R6231",
        "TESTER": "Jay Score",
        "DATE": "Aug. 12, 2020"
    }  
    
test_setup_sipm3k = {
        "PART_NUMBER": "SiPM-3K-40",
        "MCA_TYPE": "SiPM-3K",
        "DETECTOR": "NaI(Tl), 32x2 inch",  # NaI(Tl), 2x2 inch, B380 38x38mm
        "SiPM_TYPE": "Broadcom S4N44",
        "TESTER": "Jay Score",
        "TEST_DATE": "Aug. 12, 2020"
    }  
par = {
    "file_name": "./data/histogram.json",
    "setup": test_setup_sipm3k,
    "index": -1,
    "imin": 560,
    "imax": 780,
    "keV_bin": 1.0
}
#mca_display(par['file_name'], par['serial_number'])   

#test_corner()

if __name__ == "__main__":
    mca_plot_fit(**par)
