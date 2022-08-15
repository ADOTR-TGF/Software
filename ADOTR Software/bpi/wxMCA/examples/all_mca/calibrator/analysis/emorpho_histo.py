from __future__ import division
import math
import time

# Helper functions connected to IGOR


def save_wave(w_name, wave):
    with open(w_name+".itx",'w') as f:
        f.write("IGOR\nWAVES "+w_name+"\nBEGIN\n")
        f.write("\n".join(map(str, wave)))
        f.write("\nEND\n")


# Helper functions to manage records
def get_rec_from_list(n_rec, data):
    off = 0
    for n in range(n_rec):
        n = int(data[off])
        off += int(n+1)
    n = int(data[off])
    return data[int(off): int(off+n+1)]


def find_peaks(data):
    fp_desc = get_rec_from_list(0, data)  # algorithm selector (ignored in this code version)
    desc = get_rec_from_list(1, data)  # mca_descriptor
    rates = get_rec_from_list(2, data)  # rates
    cal = get_rec_from_list(3, data)  # status
    histo = get_rec_from_list(4, data)  # histo
        
    e_min = desc[2]
    kev_bin = desc[3]
    fwhm_662 = desc[4]
    is_back_sub = desc[5]  # background subtracted?
    x_min = e_min/kev_bin
    
    histogram = histo[2:]  # skip the first 2 value in the histo_data record;
    # compute fwhm (absolute) as a function of energy
    fwhm_e = [(x+x_min)*fwhm_662*math.sqrt((30.0+662.0)/(30.0+(x+x_min)*kev_bin)) for x, val in enumerate(histo[2:])]
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
    
    # offsets
    POS = 1
    ENERGY = 2
    LEFT = 3
    RIGHT = 4
    P2VL = 5
    P2VR = 6
    TYPE = 7
    COUNTS = 8
    NET = 9
    BACK = 10
    FIT_POS = 12
    FIT_ENERGY = 13
    FIT_HEIGHT = 14
    FIT_FWHM = 15
    FIT_OFFSET = 16
    FIT_SLOPE = 17
    FIT_POS_2 = 18
    FIT_ENERGY_2 = 19
    FIT_HEIGHT_2 = 20
    FIT_FWHM_2 = 21
    FIT_NET = 22
    FIT_NET_2 = 23
    FIT_BACK = 24
    FIT_CHI_SQR = 25
    FIT_STD_DEV = 26
    FIT_MAX_DEV = 27
    off_confidence = 28
    
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
        
        res = do_gauss_fit(histo[xl: xr+1], bck_model=2, fwhm=50)
        xmax, ymax, fwhm, net_counts, bck_counts, yl, yr, net_histo, fit_histo = res
        if xmax == 0:
            continue

        peak = [0]*29
        peak[0] = len(peak)-1  # number of data entries in this record
        
        if not is_back_sub:
            peak[NET] = net_counts
            peak[BACK] = bck_counts
        else:
            peak[NET] = net_counts
            peak[BACK] = 0
        if is_back_sub:  # background subtraction means there is no peak[BACK]
            peak[COUNTS] = peak[NET]
        else:
            peak[COUNTS] = sum(histogram[xl:xr+1])
            
        peak[P2VL] = yp/yl if (yl > 0) else 1000
        peak[P2VR] = yp/yr if (yr > 0) else 1000
        if (peak[P2VL] < 1.25) and (peak[P2VR] > 1.5):
            peak[TYPE] = 1  # Compton shoulder
        if (peak[P2VR] < 1.25) and (peak[P2VL] > 1.5):
            peak[TYPE] = 2  # Left shoulder
        
        peak[POS] = xmax + xl + x_min  # x_p+x_min
        peak[ENERGY] = peak[POS] * kev_bin
        peak[LEFT] = xl+x_min
        peak[RIGHT] = xr+x_min
        
        pp = xmax+x_min + xl  # p[1]+xl+x_min
        peak[FIT_POS] = pp
        peak[FIT_ENERGY] = pp * kev_bin
        peak[FIT_FWHM] = fwhm/pp
        peak[FIT_HEIGHT] = ymax
        peak[FIT_NET] = peak[NET]   # p[0] * p[2] * math.sqrt(math.pi/(4.0 * math.log(2)))
        peak[FIT_OFFSET] = (yl+yr)/2.0  # p[3]
        
        peak[FIT_BACK] = peak[BACK]  # p[3] * (xr-xl)
        peak[FIT_CHI_SQR] = 0  # fit[2]
        peak[FIT_STD_DEV] = 0  # fit[3]
        peak[FIT_MAX_DEV] = 0  # fit[4]

        # for spectra without background subtraction we can compute a confidence level
        if is_back_sub == 0:
            peak[off_confidence] = peak[NET]/math.sqrt(peak[COUNTS])
       
        peaks.append(peak)  # make a list of lists
    return peaks


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
        """
        ds = []
        for xx in range(x0,x1):
            try:
                ds += [(NH[0][xx]-NH[1][x])**2 + (xn[xx]-xn[x])**2] 
            except:
                print(x, xx, len(xn))
        """
        summe += math.sqrt(min(ds))
        
    return summe/(xr1-xr0)
   