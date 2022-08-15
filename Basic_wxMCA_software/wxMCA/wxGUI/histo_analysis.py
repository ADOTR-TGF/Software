from __future__ import division
import math
import time


def find_peaks(data):
    histogram = data["histogram"]  # histo
        
    e_min = data["desc"]["e_min"]
    keV_bin = data["desc"]["keV_bin"]
    fwhm_662 = data["desc"]["fwhm_662"]  # relative energy resolution; 7%->0.07
    is_back_sub = data["desc"]["is_back_sub"]  # background subtracted?
    x_min = e_min/keV_bin

    # compute fwhm (absolute) as a function of energy
    fwhm_e = [(x+x_min)*fwhm_662*math.sqrt((30.0+662.0)/(30.0+(x+x_min)*keV_bin)) for x, val in enumerate(histogram)]
    # first smooth the histogram; smooth-length is fwhm/4
    
    L4 = [int(f//4) for f in fwhm_e]
    l_histo = len(histogram)
        
    sm4 = [0]*l_histo
    for x in range(l_histo):
        if ((x-L4[x]) < 0) or ((x+L4[x])>= l_histo):
            continue
        LL = L4[x]
        sm4[x] = sum(histogram[x-LL:x+LL+1]) / (2*LL+1)
    
    # secondly smooth the histogram; smooth-length is fwhm/8
    L8 = [int(f//8) for f in fwhm_e]
    sm8 = [0]*l_histo
    for x in range(l_histo):
        if ((x-L8[x]) < 0) or ((x+L8[x]) >= l_histo):
            continue
        LL = L8[x]
        sm8[x] = sum(histogram[x-LL:x+LL+1]) / (2*LL+1) 
    
    # filter with L = fwhm/2
    L2 = [int(f//2) for f in fwhm_e]
    filt = [0]*l_histo
    for x in range(l_histo):
        LL = L2[x]
        if ((x-LL) < 0) or ((x+LL) >= l_histo):
            continue
        filt[x] = (sum(histogram[x+1:x+LL+1]) - sum(histogram[x-LL:x])) / (2*LL+1)

    # Now call every zero crossing a peak and assess the confidence level
    # Then we have to decide if it is a peak or a corner or a large structure
    
    # Check for filt changing signs with one but not both values being equal to zero
    len_f = len(filt)-1
    rf = [0]*len_f
    for nf in range(1,len_f):
        if filt[nf] > 0:
            rf[nf] = 1
        if filt[nf] == 0:
            rf[nf] = rf[nf-1]
        if filt[nf] < 0:
            rf[nf] = -1
    
    xp = [n for n in range(len_f-1) if (rf[n] > 0) and (rf[n+1] < 0)]
    xv = [n for n in range(len_f-1) if (rf[n] < 0) and (rf[n+1] > 0)]
    
    # merge the peak and valley lists into a guaranteed sequence of v,p,v,p,...,p,v
    if len(xp) == 0:
        return []
    
    nxvp = min(len(xp), len(xv))  
    if len(xp) == 1 and len(xv) == 0:
        pv_lst = [0,xp[0], l_histo-1]
    elif xv[0] > xp[0]:
        pv_lst = [0]
        for n in range(nxvp):
            pv_lst += [xp[n], xv[n]]
        if len(xp)>len(xv):
            pv_lst += [xp[-1], xp[-1]+xp[-1]-xv[-1]]
    else:
        pv_lst = []
        for n in range(nxvp):
            pv_lst += [xv[n], xp[n]]
        pv_lst += [l_histo-1]
        
    if len(pv_lst)<3:
        return[]    
    
    
    peaks = []
    np_candidates = (len(pv_lst)-1)//2
    
    for n in range(np_candidates):  # np = number of peak candidate
        
        x_p = pv_lst[2*n+1]
        xl = pv_lst[2*n]
        xr = pv_lst[2*n+2]

        try:
            yl = sm8[xl]
            yp = sm8[x_p]
            yr = sm8[xr]
        except:
            continue
            
        if not (xl < x_p < xr):
            continue
        if yp < 5:
            continue

        if (xr-xl) < 6:  # need six points for the fit
            continue
        
        fit_res = do_gauss_fit(histogram[xl: xr+1], bck_model=2, fwhm=50)      
        
        if fit_res["x_max"] == 0:
            continue

        peak = dict()
        
        if not is_back_sub:
            peak["net"] = fit_res["net_counts"]
            peak["back"] = fit_res["bck_counts"]
        else:
            peak["net"] = fit_res["net_counts"]
            peak["back"] = 0
        if is_back_sub:  # background subtraction means there is no peak[BACK]
            peak["counts"] = peak["net"]
        else:
            peak["counts"] = sum(histogram[xl:xr+1])
        
        yl = fit_res["yl"]
        yr = fit_res["yr"]
        peak["type"] = 0  # default value indicating a peak
        peak["P2VL"] = yp/yl if (yl > 0) else 1000
        peak["P2VR"] = yp/yr if (yr > 0) else 1000
        if (peak["P2VL"] < 1.25) and (peak["P2VR"] > 1.5):
            peak["type"] = 1  # Compton shoulder
        if (peak["P2VR"] < 1.25) and (peak["P2VL"] > 1.5):
            peak["type"] = 2  # Left shoulder
        
        peak["pos"] = fit_res["x_max"] + xl + x_min  
        peak["energy"] = peak["pos"] * keV_bin
        peak["left"] = xl+x_min
        peak["right"] = xr+x_min
        
        pp = fit_res["x_max"]+x_min + xl  
        peak["fit_pos"] = pp
        peak["fit_energy"] = pp * keV_bin
        peak["fit_fwhm"] = fit_res["fwhm"]/pp
        peak["fit_height"] = fit_res["y_max"]
        peak["fit_net"] = fit_res["net_counts"]   
        peak["fit_offset"] = (yl+yr)/2.0  
        
        peak["fit_back"] = fit_res["bck_counts"]  
        peak["fit_chi_sqr"] = fit_res["chi_sqr"] 
        peak["fit_std_dev"] = 0  
        peak["fit_max_dev"] = 0  

        # for spectra without background subtraction we can compute a confidence level
        if is_back_sub == 0:
            peak["confidence"] = peak["fit_net"]/math.sqrt(max(1, abs(peak["fit_back"])))
       
        peaks.append(peak)  # make a list of lists
    return peaks

def fit_cs_peak(histo):
    """
    Find the Cs-137 (662keV) peak in a 1K histogram.
    We expect the peak to be between 50 and 1000 bins, and the Ba-137 K_alpha to be below 30 bins
    """
    fwhm = 50
    y_max = max(histo[50:1000])
    x_max = 50 + histo[50:1000].index(y_max)
    i_min = max(int(x_max - 1.3*fwhm), 0)
    i_max = int(x_max + 1.3*fwhm)
    
    res = do_gauss_fit(histo[i_min: i_max], bck_model=2, fwhm=50)
    res["x_max"] += i_min
    return res
    
    
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
    if sigma > 0:
        fit_histo = [b+ymax*math.exp(-0.5*((x-xmax)/sigma)**2) for b,x in zip(bck_histo, range(lh))]
    else:
        fit_histo = [0]*lh
    net_counts = sum(net_histo)
    bck_counts = sum(histo) - net_counts
    
    diff = [(h-f)**2/max(1.0, abs(h)) for h, f in zip(histo, fit_histo)]
    chi_sqr = sum(diff)/len(histo)
        
    #return xmax, ymax, fwhm, net_counts, bck_counts, yl, yr, net_histo, fit_histo
    return {"x_max": xmax, "y_max": ymax, "fwhm": fwhm, "net_counts": net_counts, "bck_counts": bck_counts,
            "yl": yl, "yr": yr, "net_histo": net_histo, "fit_histo": fit_histo, "chi_sqr": chi_sqr}
    
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
    else:
        imin=0
    for imax in range(xmax, len(histo)):
        if histo[imax] <= level:
            break
    else:
        imax=len(histo)
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


def scint_doserate(histo, keV_bin, mass, count_rate):
    """
        Compute dose rate deposited on average in the volume of the scintillator.
        A 38mm-diameter, 38mm tall NaI crystal weighs 0.157kg
        A 50mm-diameter, 50mm tall NaI crystal weighs 0.358kg
        
        Inputs are
        histo: Energy histogram
        keV_bin: Scale of the energy histo gram in keV/bin
        mass: Mass (Weight) of the scintillator crystal
        count_rate: Measured count rate corrected for dead time.
        
        Returns: Average energy in keV, the dose rate in Sv/hr and in rem/hr
    """
    N = sum(histo)
    if N<= 0:
        return 0, 0, 0
    nmax = len(histo)
    esum = 0
    for n in range(nmax):
        esum += n*histo[n]
    sv_factor = 5.76e-13  # 3600s/hr*1.9e-16J/keV
    e_avg = esum/N*keV_bin
    
    dr_sv = sv_factor * e_avg * count_rate / mass  # in Sv/hr
    dr_rem = dr_sv * 100  # In rem/hr
    
    return e_avg, dr_sv, dr_rem


def smooth(histo, nsm):
    """
        Smooth a histogram using a box averager.  
        The smoothed bin is the center bin, with the smoothing interval extending equally to both sides.
        The first and last nsm // 2 bins are not smoothed.
        histo: the histogram array
        nsm:   Number of bins to smooth.  If nsm is even it will be incremented by 1.
        return: the smoothed histogram
    """
    nsm = (nsm - (int(nsm) & 1)) + 1
    nsm2 = nsm // 2
    norm = 1.0/float(nsm)
    sm_histo = list(histo)  # Get a fresh copy
    nh = len(histo)
    for n in range(nsm,nh-nsm2-1):
        sm_histo[n] = sum(histo[n-nsm2: n+nsm2+1])*norm
        
    return sm_histo
    
def template_distance(template, histo, xrange, yrange, xspan=0):
    """
        Compute the distance between a histogram and a template as the sum 
        of nearest-neighbor distances between each histogram point and
        any member of the template.
        
        xrange and yrange define the x-y coordinates of the enclosing 
        rectangle in the x-y plane.
        
        if xspan>=0 it defines a +/-xspan for searching for the next neighbor
        around any point x in histo.  For xspan=0 we only measure the y-distance
        at each single x-position.
        
        Here the template and histo histograms need to have the same 
        keV/bin gain for a meaningful comparison.
        
        The algorithm normalizes the area to the unit square [0,0] to [1,1]
        before it performs the measurement.
    """
    xr0 = xrange[0]
    xr1 = xrange[1]
    # xr = [x for x in range(xr0, xr1)]
    xn = [(x-xr0)/(xr1-xr0) for x in range(xr0, xr1)]
    NH = []
    
    # Normalized template and histo
    for hist in [template, histo]:
        y0 = min(hist[xr0: xr1])
        y1 = max(hist[xr0: xr1])
        dy = y1-y0
        dy = dy if dy > 0 else 1
        NH += [ [ (y-y0)/dy for y in hist[xr0: xr1] ] ]

    summe = 0
    
    for x in range(xr1-xr0):
        x0 = max(0, x-xspan)
        x1 = min(xr1-xr0, x+xspan)
        ds = [ (NH[0][xx]-NH[1][x])**2 + (xn[xx]-xn[x])**2 for xx in range(x0, x1)]
        summe += math.sqrt(min(ds))
        
    return summe/(xr1-xr0)   
    