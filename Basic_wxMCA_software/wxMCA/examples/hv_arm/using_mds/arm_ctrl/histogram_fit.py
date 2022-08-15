import math

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