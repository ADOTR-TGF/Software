import time
import subprocess
import wx
import os
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
# from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import json
import mca_io
import graph_ctrl_grid as gcd

class LoggerWindow(wx.Frame): 
    def __init__(self, parent, title, dev_ind = 0): 
        super(LoggerWindow, self).__init__(parent, title = title)
        self.EMORPHO = 0x6001
        self.PMT1K = 0x101
        self.PMT3K = 0x103
        self.SIPM1K = 0x201
        self.SIPM3K = 0x203
        self.PMTN3K = 0x104
        
        # Communication with the MCA
        self.MCA_IO = mca_io.MCA_IO()  # For communication with the MDS
        
        #-- Here we use the first mca in the MCA_IO.mca dictionary
        self.sn = list(self.MCA_IO.mca)[dev_ind]
        self.MCA = self.MCA_IO.mca[self.sn]  
        
        self.mca_id = self.MCA["mca_id"]
        self.commands = self.MCA["commands"]
        
        self.disp_ctrl = self.MCA["display_controls"]["logger"]["data"]
        self.display_name = "logger"  # The name of the entry in the display_controls.json file; used by graph_ctrl_grid
        
        self.overlay = 20  # Maximum number of pulses to overlay in the display
        
        # Build the panel
        panel = wx.Panel(self, size = (5000, 3000)) 
        self.bck_color = panel.GetBackgroundColour()
        self.figure, self.axes = plt.subplots()  # figsize is in inch
        self.init_line_plots(self.MCA["plot_controls"]["logger"])  # Set axes, labels and colors

        self.canvas = FigureCanvas(panel, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        
        self.cursor_text = wx.StaticText( self, wx.ID_ANY, "X,Y =", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.cursor_text.SetBackgroundColour(self.bck_color)
        self.cursor_text.Wrap( -1 )
        self.canvas.mpl_connect('motion_notify_event', self.onCursorMotion)
        
        self.box_local = wx.BoxSizer(wx.VERTICAL)
        self.box_graph = wx.BoxSizer(wx.VERTICAL)
        self.box_ctrl = wx.BoxSizer(wx.VERTICAL)
        
        self.box_graph.Add(self.canvas, 1, wx.TOP | wx.LEFT | wx.EXPAND, 1 )
        self.box_graph.Add(self.toolbar, 0, wx.TOP | wx.LEFT, 1)
        self.box_graph.Add(self.cursor_text,0, wx.TOP | wx.LEFT, 1)
        
        # Make a list of action buttons
        self.button_list = []
        button = wx.Button(panel, id = wx.ID_ANY, label="New", name="start_logger")
        self.button_list += [button]
        
        button = wx.Button(panel, id = wx.ID_ANY, label="Read", name="read_logger")
        self.button_list += [button]
        
        button = wx.Button(panel, id = wx.ID_ANY, label="Save", name="save_logger")
        self.button_list += [button]
        
        self.switch = wx.Button(panel, id = wx.ID_ANY, label="Figure only", name="graph_ctrl_on_off") 
        self.button_list += [self.switch]
        
        # Put all buttons in a horizontal sizer
        self.button_box = wx.BoxSizer(wx.HORIZONTAL)
        for button in self.button_list:
            button.Bind(wx.EVT_BUTTON, self.OnClicked)
            self.button_box.Add(button, 0, wx.RIGHT, 4)
        # Add buttonbox to the vertical stack
        self.box_graph.Add(self.button_box, 0, wx.BOTTOM| wx.TOP, 10)
        
        # Make the editable controls
        self.graph_ctrl = gcd.StatusGrid(panel, self)
        self.box_ctrl.Add(self.graph_ctrl, 0, wx.TOP, 4)
        self.box_local.Add(self.box_graph, 1, wx.TOP | wx.EXPAND)
        self.box_local.Add(self.box_ctrl, 0, wx.LEFT | wx.TOP, 1)
        
        self.SetSizer(self.box_local)
        self.box_local.SetSizeHints(self)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        
    def OnSize(self, event):
        self.SetSizeHints(minW = 580, minH = 550)
        self.Layout()
        self.box_graph.ShowItems(False)
        self.box_graph.ShowItems(True)
        if self.switch.GetLabel() == "Figure only":
            self.box_ctrl.ShowItems(False)
            self.box_ctrl.ShowItems(True)
            
    def OnClicked(self, event): 
        name = event.GetEventObject().GetName()
        if name in ["start_logger", "read_logger", "save_logger"]:
            getattr(self, name)()  # Call the function that bears the button's name
        elif name == "graph_ctrl_on_off":
            switch_name = self.switch.GetLabel()
            if switch_name == "Figure only":
                self.switch.SetLabel("Show ctrl")
            else:
                self.switch.SetLabel("Figure only")
            time.sleep(0.1)
            getattr(self, name)()
        else:
            self.MCA_IO.submit_command(self.sn, self.commands[name])

    def graph_ctrl_on_off(self):
        switch_name = self.switch.GetLabel()
        if switch_name == "Figure only":
            self.box_ctrl.ShowItems(True)
        elif switch_name == "Show ctrl":
            self.box_ctrl.ShowItems(False)
        self.SetSizer(self.box_local)
        self.box_local.SetSizeHints(self)
                
    def onCursorMotion(self, event):
        """
            Ideally this event will carry the cursor x/y coordinates in units of the Matplotlib axes.
        """
        
        if event.xdata is None or event.ydata is None:
            pass
        else:
            self.cursor_text.SetLabelText("X,Y = {:.4f}, {:.4f}".format(event.xdata, event.ydata))

    def read_logger(self):
        self.arm_logger = self.MCA_IO.submit_command(self.sn, self.commands["read_arm_logger"])[self.sn]
        
        par_1_data = self.arm_logger["user"]["var_0"]
        par_2_data = self.arm_logger["user"]["var_1"]
        dwell_time = self.arm_logger["fields"]["dt"]
        ch_0 = str(int(self.arm_logger["fields"]["ch_0"]))
        ch_1 = str(int(self.arm_logger["fields"]["ch_1"]))
        draw_line = int(self.disp_ctrl["draw_line"]["value"])
        draw_item = int(self.disp_ctrl["draw_item"]["value"])
        plot_ctrl = self.MCA["plot_controls"]["logger"]
        
        time_data = [n*dwell_time for n in range(len(par_1_data))]
        label_ctrl = self.MCA["display_controls"]["logger"]["labels"]
        
        if draw_item == 0:
            x_data = time_data
            y_data = par_1_data
            plot_ctrl["labels"]["xlabel"] = "Time in seconds"
            plot_ctrl["labels"]["ylabel"] = label_ctrl[ch_0]
        elif draw_item == 1:
            x_data = time_data
            y_data = par_2_data
            plot_ctrl["labels"]["xlabel"] = "Time in seconds"
            plot_ctrl["labels"]["ylabel"] = label_ctrl[ch_1]
        elif draw_item == 2:
            x_data = par_2_data
            y_data = par_1_data
            plot_ctrl["labels"]["xlabel"] = label_ctrl[ch_1]
            plot_ctrl["labels"]["ylabel"] = label_ctrl[ch_0]
        else:
            x_data = par_1_data
            y_data = par_2_data
            plot_ctrl["labels"]["xlabel"] = label_ctrl[ch_0]
            plot_ctrl["labels"]["ylabel"] = label_ctrl[ch_1]
            
        self.line_plot.set_xdata(x_data)
        self.line_plot.set_ydata(y_data)
        
        rat = 0.02
        min_x = min(x_data)
        max_x = max(x_data)
        x_min = min_x - abs(max_x-min_x)*0.1
        x_max = max_x + abs(max_x-min_x)*0.1
        
        min_y = min(y_data)
        max_y = max(y_data)
        if min_y != max_y:
            y_min = min_y - abs(max_y-min_y)*0.5
            y_max = max_y + abs(max_y-min_y)*0.5
        elif min_y != 0:
            y_min = 0.9*min_y
            y_max = 1.1*max_y
        else:
            y_min = -1.0
            y_max = 1.0
        
        self.axes.set(**{"xlim": [x_min, x_max]})
        self.axes.set(**{"ylim": [y_min, y_max]})
        self.axes.set_xlabel(plot_ctrl['labels']['xlabel'], **plot_ctrl['labels']['xlabel_ctrl'])
        self.axes.set_ylabel(plot_ctrl['labels']['ylabel'], **plot_ctrl['labels']['ylabel_ctrl'])
        
        if draw_line:
            plot_ctrl["line_ctrl"]["linestyle"] = "-"
            plt.setp(self.line_plot, **plot_ctrl['line_ctrl'])
        else:
            plot_ctrl["line_ctrl"]["linestyle"] = ""
            plt.setp(self.line_plot, **plot_ctrl['line_ctrl'])
        
        self.canvas.draw()
        
    def start_logger(self):
        par_1 = int(self.disp_ctrl["parameter_1"]["value"]) & 0xFF
        par_2 = int(self.disp_ctrl["parameter_2"]["value"]) & 0xFF
        dwell_time = int(float(self.disp_ctrl["dwell_time"]["value"])) & 0xFF
        
        xctrl_0 = dwell_time + 256*par_1 + 65536*par_2
        cmd = dict(self.commands["write_arm_ctrl"])
        cmd["data"] = {"fields": {"xctrl_0": xctrl_0}, "user": {"clear_logger": 1}}
        self.MCA_IO.submit_command(self.sn, cmd)

    def save_logger(self):
        out_file = self.disp_ctrl["file"]["value"]
        splt_out_file = out_file.strip('.').rsplit('/', 1)
        data_dir_path = splt_out_file[0]
        file_name = splt_out_file[1]
        default_path = os.path.dirname(os.getcwd()) + data_dir_path
        try:
            data_path = self.last_saved_path
        except:
            data_path = default_path
        
        self.arm_logger["comment"] = self.disp_ctrl["comment"]["value"]
        with wx.FileDialog(self, "Save logger data", wildcard="json files (*.json)|*.json", defaultDir = data_path, defaultFile = file_name,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return 
            pathname = fileDialog.GetPath()
            self.last_saved_path = os.path.dirname(pathname)
            try:
                with open(pathname, 'a+') as fout:
                    fout.write(json.dumps(self.arm_logger)+'\n')
            except IOError: 
                wx.LogError("Cannot save current data in file '%s'." % out_file)
    
    def init_line_plots(self, ctrl):
        
        self.line_plot = self.axes.plot([], [])[0]
        plt.setp(self.line_plot, **ctrl['line_ctrl'])
            
        if ctrl['axis_ctrl']["xlim"] == []:
            ctrl['axis_ctrl']["xlim"] = None
        if ctrl['axis_ctrl']["ylim"] == []:
            ctrl['axis_ctrl']["ylim"] = None

        self.axes.set_xlabel(ctrl['labels']['xlabel'] , **ctrl['labels']['xlabel_ctrl'])
        self.axes.set_ylabel(ctrl['labels']['ylabel'], **ctrl['labels']['ylabel_ctrl'])
        self.axes.set_title(ctrl['labels']['title'], **ctrl['labels']['title_ctrl'])
        self.axes.grid(**ctrl['grid_ctrl'])
        self.axes.set(**ctrl['axis_ctrl'])
        
        if 0:
            bbox_args = dict(boxstyle="round", pad=0.5, ec=colors[0], fc=(0.9, 0.9, 0.9, 0.9), linewidth=2)  # fill, bounds(l,b,w,h) are ignored
            comment = "Beta"  # Empty string nixes the display 
            self.axes.annotate(comment, fontsize=10,
                        xycoords='axes fraction', xy=(0.65, 0.90), ha="left", va="bottom", bbox=bbox_args)
   
def main(dev_sn = '', dev_ind = 0):             
    app = wx.App() 
    panel = LoggerWindow(None,  'List Mode ' + dev_sn, dev_ind)
    panel.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    main()
    
    
"""
Notes:

https://wxpython.org/Phoenix/docs/html/sizers_overview.html#sizers-overview

"""