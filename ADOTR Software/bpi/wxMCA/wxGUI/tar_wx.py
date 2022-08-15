import math
import time
import wx
import os
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
# from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import json
import mca_io
import graph_ctrl_grid as gcd
import histo_analysis

class TarWindow(wx.Frame): 
    def __init__(self, parent, title): 
        super(TarWindow, self).__init__(parent, title = title)
        self.EMORPHO = 0x6001
        self.PMT1K = 0x101
        self.PMT3K = 0x103
        self.SIPM1K = 0x201
        self.SIPM3K = 0x203
        
        # Communication with the MCA
        self.MCA_IO = mca_io.MCA_IO()  # For communication with the MDS
        
        #-- Here we use the first mca in the MCA_IO.mca dictionary
        #self.sn = list(self.MCA_IO.mca)[0]
        #self.MCA = self.MCA_IO.mca[self.sn]  
        
        #-- Here we use the globally chosen sn:
        with open('chosen_sn.txt','r') as snfile:
        	fname = snfile.read()
        	snfile.close()
        self.sn = fname
        self.MCA = self.MCA_IO.mca[self.sn]
        
        self.mca_id = self.MCA["mca_id"]
        self.commands = self.MCA["commands"]
        
        self.disp_ctrl = self.MCA["display_controls"]["tar"]["data"]
        self.display_name = "tar"  # The name of the entry in the display_controls.json file; used by graph_ctrl_grid
        
        # Build the panel
        panel = wx.Panel(self, size = (5000, 3000)) 
        self.bck_color = panel.GetBackgroundColour()
        self.figure, self.axes = plt.subplots()  # figsize is in inch
        self.lp_names = ["tar", "fit"]
        self.init_line_plots(self.MCA["plot_controls"]["tar"])  # Set axes, labels and colors
        
        self.canvas = FigureCanvas(panel, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        
        self.cursor_text = wx.StaticText( self, wx.ID_ANY, "X,Y =", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.cursor_text.SetBackgroundColour(self.bck_color)
        self.cursor_text.Wrap( -1 )
        self.canvas.mpl_connect('motion_notify_event', self.onCursorMotion)
        
        self.box_local = wx.BoxSizer(wx.VERTICAL)
        self.box_graph = wx.BoxSizer(wx.VERTICAL)
        self.box_ctrl = wx.BoxSizer(wx.VERTICAL)
        
        self.box_graph.Add(self.canvas, 1, wx.TOP | wx.LEFT | wx.EXPAND, 1)
        self.box_graph.Add(self.toolbar, 0, wx.TOP | wx.LEFT, 1)
        self.box_graph.Add(self.cursor_text,0, wx.TOP | wx.LEFT, 1)
        
        self.count_rate_text = wx.StaticText( self, wx.ID_ANY, "CR:", wx.DefaultPosition, wx.DefaultSize, 10 )
        self.count_rate_text.SetBackgroundColour(self.bck_color)
        self.fit_text = wx.StaticText( self, wx.ID_ANY, "fit:", wx.DefaultPosition, wx.DefaultSize, 10 )
        self.fit_text.SetBackgroundColour(self.bck_color)
        self.msg_text = wx.StaticText( self, wx.ID_ANY, "msg:", wx.DefaultPosition, wx.DefaultSize, 10 )
        self.msg_text.SetBackgroundColour(self.bck_color)
        
        self.box_graph.Add(self.count_rate_text,0, wx.TOP | wx.LEFT, 1)
        self.box_graph.Add(self.fit_text,0, wx.TOP | wx.LEFT, 1)
        self.box_graph.Add(self.msg_text,0, wx.TOP | wx.LEFT, 1)
        
        
        # Make a list of action buttons
        self.button_list = []
        button = wx.Button(panel, id = wx.ID_ANY, label="New", name="start_tar")
        self.button_list += [button]

        button = wx.Button(panel, id = wx.ID_ANY, label="Refresh", name="refresh") 
        self.button_list += [button]
        
        button = wx.Button(panel, id = wx.ID_ANY, label="Fit", name="fit") 
        self.button_list += [button]
        
        button = wx.Button(panel, id = wx.ID_ANY, label="Save", name="save_histogram") 
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
        self.refresh()

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
        if name in ["refresh", "fit", "save_histogram"]:
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
            if name == "start_tar":
                time.sleep(1.2)
            self.refresh()

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
            
    def save_histogram(self):
        out_file = self.disp_ctrl["file"]["value"]
        splt_out_file = out_file.strip('.').rsplit('/', 1)
        data_dir_path = splt_out_file[0]
        file_name = splt_out_file[1]
        default_path = os.path.dirname(os.getcwd()) + data_dir_path
        try:
            data_path = self.last_saved_path
        except:
            data_path = default_path
        
        with wx.FileDialog(self, "Save arrival times data", wildcard="json files (*.json)|*.json", defaultDir = data_path, defaultFile = file_name,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return 
            pathname = fileDialog.GetPath()
            self.last_saved_path = os.path.dirname(pathname)
            try:
                with open(pathname, 'a+') as fout:
                    self.histogram["comment"] = self.disp_ctrl["comment"]["value"]
                    fout.write(json.dumps(self.histogram)+'\n')
            except IOError: 
                wx.LogError("Cannot save current data in file '%s'." % out_file)
            
    def refresh(self):
        self.msg_text.SetLabel("")
        self.fit_text.SetLabel("")
        
        # Read histogram and count rate data
        
        if self.mca_id in [0x6001, 0x103, 0x203]:
            count_rates = self.MCA_IO.submit_command(self.sn, self.commands["read_rates"])[self.sn]["user"]["bank_0"]
            run_time = count_rates["run_time"]
            count_rate = count_rates["event_rate"]
            count_rate_err = count_rates["event_rate_err"] / count_rate if count_rate > 0 else 0
        elif self.mca_id in [0x101, 0x201]:
            count_rates = self.MCA_IO.submit_command(self.sn, self.commands["read_rates"])[self.sn]["fields"]
            run_time = count_rates["run_time_sample"]
            count_rate = count_rates["count_rate"]
            count_rate_err = count_rates["count_rate_err"] / count_rate if count_rate > 0 else 0
        
        cmd = self.commands["read_mca"]
        cmd["num_items"] = 1024
        self.histogram = self.MCA_IO.submit_command(self.sn, cmd)[self.sn]
        
        if self.mca_id in [0x6001, 0x103, 0x203]:
            self.histo = self.histogram["registers"]
        elif self.mca_id in [0x101, 0x201]:
            self.histo = self.histogram["fields"]["histogram"]
        
        dt = 4.0/3.0
        y_data = [math.log10(h) if h>0 else 0 for h in self.histo]        
        x_data = [n*dt for n in range(len(self.histo))]
        
        self.lp_dict["tar"].set_xdata(x_data)
        self.lp_dict["tar"].set_ydata(y_data)
        self.axes.set(**{"xlim": [0, x_data[-1]]})
        self.axes.set(**{"ylim": [0, max(y_data)+0.1]})
        
        self.count_rate_text.SetLabelText("".format())
        
        self.canvas.draw()
       
    
    def fit(self):
        dt = 4.0/3.0  # Time step in milli-seconds
        fit_min = int(float(self.disp_ctrl["fit_xmin"]["value"])/dt)
        fit_max = int(float(self.disp_ctrl["fit_xmax"]["value"])/dt)
        imin = min(fit_min, fit_max)
        imax = max(fit_min, fit_max)
        histo_to_fit = [math.log10(h) if h>0 else 0 for h in self.histo[imin: imax]]
        x_data = [n*dt for n in range(len(histo_to_fit))]
        
        N = imax-imin
        sx = sum([x for x in x_data])
        sxx = sum([x*x for x in x_data])
        sy = sum(histo_to_fit)
        sxy = sum([x*h for x,h in zip(x_data, histo_to_fit)])
        
        off = -(sxx*sy-sx*sxy)/(sx*sx-N*sxx)
        slope = (sx*sy-N*sxy)/(sx*sx-N*sxx)

        msg = "Countrate fit: {:.3f}kcps".format(-slope*math.log(10)*1.0e3)
        self.fit_text.SetLabel(msg)
        
        y_data = [ slope*n*dt+off for n in range(len(histo_to_fit))]
        x_data = [(imin+n)*dt for n in range(len(histo_to_fit))]
        
        self.lp_dict["fit"].set_xdata(x_data)
        self.lp_dict["fit"].set_ydata(y_data)
        self.canvas.draw()
        
    
    def init_line_plots(self, ctrl):
        
        self.lp_dict = {}
        lp_colors = self.MCA["plot_controls"]["tar"]["colors"]
        self.plots = []  # line plots where we update the data with every refresh or fit
        for name, color in zip(self.lp_names, lp_colors):
            self.lp_dict[name] = self.axes.plot([], [])[0]
            if name=="fit":
                ctrl['fit_line_ctrl']["color"] = color
                plt.setp(self.lp_dict[name], **ctrl['fit_line_ctrl'])
            else:
                ctrl['line_ctrl']["color"] = color
                plt.setp(self.lp_dict[name], **ctrl['line_ctrl'])
            
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

   
def main():             
    app = wx.App() 
    panel = TarWindow(None,  'Arrival Times')
    panel.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    main()
    
    
"""
Notes:

https://wxpython.org/Phoenix/docs/html/sizers_overview.html#sizers-overview

"""
