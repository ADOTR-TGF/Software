peak_plot_ctrl = {
    "axis_ctrl": {
        "xscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "yscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "xlim": None, # None or [xmin, xmax]
        "ylim": None # [0, 2000] # None or [ymin, ymax] 
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
        "markersize": 2,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Temperature, degc",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Peak pos",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Cs-137 peak vs operating voltage",
        "title_ctrl": {"fontsize":14, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}
fwhm_plot_ctrl = {
    "axis_ctrl": {
        "xscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "yscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "xlim": None, # None or [xmin, xmax]
        "ylim": None # [0, 2000] # None or [ymin, ymax] 
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
        "markersize": 2,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Temperature, degc",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "fwhm",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Cs-137 fwhm vs time",
        "title_ctrl": {"fontsize":14, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}

led_plot_ctrl = {
    "axis_ctrl": {
        "xscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "yscale": "linear",  # {"linear", "log", "symlog", "logit", ...}
        "xlim": None, # None or [xmin, xmax]
        "ylim": None # [0, 2000] # None or [ymin, ymax] 
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
        "markersize": 2,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Temperature, degc",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "LED value",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "LED value vs Temperature",
        "title_ctrl": {"fontsize":14, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}

hv_plot_ctrl = {
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
        "markersize": 2,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Time, hrs",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "High voltage in V",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Gamma-detector high voltage",
        "title_ctrl": {"fontsize":14, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}

time_plot_ctrl = {
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
        "markersize": 2,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Time, hrs",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Peak pos",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Peak position vs time",
        "title_ctrl": {"fontsize":14, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}
degc_plot_ctrl = {
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
        "markersize": 2,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Time, hrs",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Temperature, degC",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Gamma-detector temperature",
        "title_ctrl": {"fontsize":14, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}

dg_plot_ctrl = {
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
        "markersize": 2,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Temperature, deg. C",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Digital gain",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Digital gain vs time",
        "title_ctrl": {"fontsize":12, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}

pulse_plot_ctrl = {
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
        "linestyle": "-",  # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        "linewidth": 1.0,
        "color": "#AA55FF",
        "drawstyle": "default",  # {'default', 'steps', 'steps-pre', 'steps-mid', 'steps-post'}
        "fillstyle": 'full',  # {'full', 'left', 'right', 'bottom', 'top', 'none'}; fills the marker
        "markersize": 2,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Time, us",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Pulse height",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "662keV pulse",
        "title_ctrl": {"fontsize":12, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}

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
        "linestyle": "-",  # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        "linewidth": 1.0,
        "color": "#AA55FF",
        "drawstyle": "default",  # {'default', 'steps', 'steps-pre', 'steps-mid', 'steps-post'}
        "fillstyle": 'full',  # {'full', 'left', 'right', 'bottom', 'top', 'none'}; fills the marker
        "markersize": 2,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Energy, keV",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Counts",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Cs-137 Energy Spectrum",
        "title_ctrl": {"fontsize":12, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}

line_plot_ctrl = {
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
        "linestyle": "-",  # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        "linewidth": 1.0,
        "color": "#AA55FF",
        "drawstyle": "default",  # {'default', 'steps', 'steps-pre', 'steps-mid', 'steps-post'}
        "fillstyle": 'full',  # {'full', 'left', 'right', 'bottom', 'top', 'none'}; fills the marker
        "markersize": 2,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Energy, keV",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Counts",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Cs-137 Energy Spectrum",
        "title_ctrl": {"fontsize":12, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}

line_dot_ctrl = {
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
        "linestyle": "-",  # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        "linewidth": 1.0,
        "color": "#AA55FF",
        "drawstyle": "default",  # {'default', 'steps', 'steps-pre', 'steps-mid', 'steps-post'}
        "fillstyle": 'full',  # {'full', 'left', 'right', 'bottom', 'top', 'none'}; fills the marker
        "markersize": 2,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Energy, keV",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Counts",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Cs-137 Energy Spectrum",
        "title_ctrl": {"fontsize":12, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}

scatter_plot_ctrl = {
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
        "markersize": 2,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",    
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels": 
        {
        "xlabel": "Energy, keV",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "Counts",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Cs-137 Energy Spectrum",
        "title_ctrl": {"fontsize":12, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}