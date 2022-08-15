import json
import matplotlib.pyplot as plt
import histo_analysis

"""
    This is a data quality monitoring tool.
    We compare calibrator histograms to a template to ensure that no algorithmic or 
    communication errors occurred while acquiring calibration data.
"""
def get_template_diffs(template_files, histograms_file, alternating = False):
    """
    For usbBase, MCA-2000 and MCA-3000 use alternating = True:
    The calibrator.py program generates histogram json files with ha_mode=1 followed by ha_mode=0.
    Hence, we have pulse_height spectra followed by energy spectra in alternating lines.
    
    For MCA-1000 use alternating = False:
    All spectra are of the same type.  Only the first entry in the template list will be used.
    
    The algorithm normalizes the template and the histogram to a unit square in the counts vs bin plane.
    The distance between a histogram and the template is defined as the sum over the minimal x-y distance
    between a point on the histogram and a search range of points on the template.
    
    x +/- search is the region on the template in which the algorithm looks for the minimum difference 
    between histogram and template

    """
    differences = []
    
    # load the pulse_height and the energy template histograms
    TH = {}  # Template histograms
    for key in ["energy", "amplitude"]
    with open(par[key]["template"], "r") as fin:
        TH[key] = json.loads(fin.read())["histo"]["registers"] # Template histograms 
    
    count = 0    
    with open(histograms_file, 'r') as fin:
        for line in fin:
            DH = json.loads(line)["histo"]["registers"]  # Data histo
            if alternating and count == 0: # amplitude histogram comes first, followed by energy histogram            
                # pulse_height spectrum
                p = par["amplitude"]
                t = TH["amplitude"]
            else:
                p = par["energy"]
                t = TH["energy"]
            count = (count+1)%2
            differences += [histo_analysis.template_distance(t, DH, p["roi"], [], p["search"])]
    return differences
    

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

par = {
    "energy": {
        "template": "../user/emorpho/data/templates/histo_662_template.json",
        "roi": [50, 1000],  # MCA bins to compare
        "search": 50        # +/- search range
    },
    "amplitude": {
        "template": "../user/emorpho/data/templates/histo_187_template.json",
        "roi": [20, 250],  # MCA bins to compare
        "search": 12       # +/- search range
    }
}
 
histo_file = "../user/emorpho/data/histograms_eRC4624.json"
    
diffs = get_template_diffs(template_files, histo_file)
xd = [x for x in range(len(diffs))]

pc.scatter_plot_ctrl["labels"]["xlabel"] = "Temperature, deg. C"
pc.scatter_plot_ctrl["labels"]["ylabel"] = "Template diff"
pc.scatter_plot_ctrl["labels"]["title"] = "Template sep vs deg. C"

line_plot([xd], [diffs], pc.scatter_plot_ctrl)     


plt.show()
