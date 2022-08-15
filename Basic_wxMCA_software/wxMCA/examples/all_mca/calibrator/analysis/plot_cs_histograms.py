import json
import matplotlib.pyplot as plt
import emorpho_histo

def get_histo(file_name, line_no):

    with open(file_name, 'r') as fin:
        for count, line in enumerate(fin):
            pass
    print("Number of histograms:", count)
 
    with open(file_name, 'r') as fin:
        for count, line in enumerate(fin):
            if count != line_no:
                continue
            data_dict = json.loads(line)
            histo = data_dict["histogram"]["registers"]

    N = len(histo)
    e_data = [n for n in range(N)]
    return e_data, histo

    
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
slot = 250
e_data, histo = get_histo("./data/histograms_eRC4632_energy.json", slot)  # Substitute your data file

line_plot(e_data, histo, pc.histo_plot_ctrl)



plt.show()
