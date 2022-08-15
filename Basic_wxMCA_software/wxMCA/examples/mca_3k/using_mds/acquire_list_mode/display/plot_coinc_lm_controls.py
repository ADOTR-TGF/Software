lm_plot_ctrl = {
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
        "markersize": 5,
        "markeredgewidth": 0,
        "markeredgecolor": "#3355AA",
        "markerfacecolor": "#AA00AA",
        "markerfacecoloralt": "#00AA00", # Fills opposite of fillstyle
        "marker": "o",
        "markevery": None
    },
    "labels":
        {
        "xlabel": "MCA bin, detector 1",
        "xlabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "ylabel": "MCA bin, detector 2",
        "ylabel_ctrl": {"fontsize":12, "fontweight": "normal", "color": "#AA0000", "alpha": 0.8},
        "title": "Coincidence Energy Plot",
        "title_ctrl": {"fontsize":14, "fontweight": "bold", "color": "#AA00AA", "alpha": 0.9}
        },
    "show": False
}
