histo_plot_ctrl = {
    "axis_ctrl": {
        "xscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "yscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "xlim": None, # None or [xmin, xmax]
        "ylim": None, # None or [ymin, ymax] 
    },
    "grid_ctrl": {
        "alpha": 0.2,
        "linestyle": ":",  # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        "linewidth": 1.0,
        "color": "#0000AA"
    },    
    "line_ctrl": {
        "alpha": 0.9,
        "linestyle": "",  # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        "linewidth": 1.0,
        "color": "SteelBlue",
        "drawstyle": "default",  # {'default', 'steps', 'steps-pre', 'steps-mid', 'steps-post'}
        "fillstyle": 'full',  # {'full', 'left', 'right', 'bottom', 'top', 'none'}; fills the marker
        "markersize": 3,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "MCA bin (sqrt)",
        "xlabel_ctrl": {"fontsize":10, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Frequency",
        "ylabel_ctrl": {"fontsize":10, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Co-60 Spectrum; 1k events",
        "title_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.9}
        },
    "show": False
}

energy_plot_ctrl = {
    "axis_ctrl": {
        "xscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "yscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "xlim": None, # None or [xmin, xmax]
        "ylim": None, # None or [ymin, ymax] 
    },
    "grid_ctrl": {
        "alpha": 0.2,
        "linestyle": ":",  # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        "linewidth": 1.0,
        "color": "#0000AA"
    },    
    "line_ctrl": {
        "alpha": 0.9,
        "linestyle": "",  # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        "linewidth": 1.0,
        "color": "SteelBlue",
        "drawstyle": "default",  # {'default', 'steps', 'steps-pre', 'steps-mid', 'steps-post'}
        "fillstyle": 'full',  # {'full', 'left', 'right', 'bottom', 'top', 'none'}; fills the marker
        "markersize": 3,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Event no",
        "xlabel_ctrl": {"fontsize":10, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Energy",
        "ylabel_ctrl": {"fontsize":10, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Energy vs Event No.",
        "title_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.9}
        },
    "show": False
}

wc_plot_ctrl = {
    "axis_ctrl": {
        "xscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "yscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "xlim": None, # None or [xmin, xmax]
        "ylim": None, # None or [ymin, ymax] 
    },
    "grid_ctrl": {
        "alpha": 0.2,
        "linestyle": ":",  # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        "linewidth": 1.0,
        "color": "#0000AA"
    },    
    "line_ctrl": {
        "alpha": 0.9,
        "linestyle": "",  # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        "linewidth": 1.0,
        "color": "SteelBlue",
        "drawstyle": "default",  # {'default', 'steps', 'steps-pre', 'steps-mid', 'steps-post'}
        "fillstyle": 'full',  # {'full', 'left', 'right', 'bottom', 'top', 'none'}; fills the marker
        "markersize": 3,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Event no",
        "xlabel_ctrl": {"fontsize":10, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Time",
        "ylabel_ctrl": {"fontsize":10, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Wallclock Time vs Event No.",
        "title_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.9}
        },
    "show": False
}



psd_plot_ctrl = {
    "axis_ctrl": {
        "xscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "yscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "xlim": None, # None or [xmin, xmax]
        "ylim": None, # None or [ymin, ymax] 
    },
    "grid_ctrl": {
        "alpha": 0.2,
        "linestyle": ":",  # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        "linewidth": 1.0,
        "color": "#0000AA"
    },    
    "line_ctrl": {
        "alpha": 0.9,
        "linestyle": "",  # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        "linewidth": 1.0,
        "color": "#AA55FF",
        "drawstyle": "default",  # {'default', 'steps', 'steps-pre', 'steps-mid', 'steps-post'}
        "fillstyle": 'full',  # {'full', 'left', 'right', 'bottom', 'top', 'none'}; fills the marker
        "markersize": 3,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Energy, MCA bins",
        "xlabel_ctrl": {"fontsize":10, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Short sum, MCA bins",
        "ylabel_ctrl": {"fontsize":10, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Pulse Shape Discrimination Plot",
        "title_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.9}
        },
    "show": False
}

sample_ctrl = {
    "operations": {
        "rowColours": ["Gold", "DarkOrange"],
        "colColours": ["Chocolate"],
        "cellColours": [["Gold"], ["DarkOrange"]],
        "cellLoc": 'center'
    },
    "count_rates": {
        "rowColours": ["Gold", "DarkOrange"],
        "colColours": ["Chocolate"],
        "cellColours": [["Gold"], ["DarkOrange"]],
        "cellLoc": 'center'
    },
    "set_op_voltage": {
        "label_pad": 0.1, 
        "initial":'34.5', 
        "color": 'Linen', 
        "hovercolor": 'Ivory'
    }
}