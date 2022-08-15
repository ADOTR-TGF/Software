import time
import subprocess
import wx
import os
import platform
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
# from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import json
import mca_io
import graph_ctrl_grid as gcd

linux_python = "python3.7"
windows_python = "C:/BPISoft_V3/Python37/python.exe "

print(platform.system())
if "Windows" in platform.system():
    python_exe = windows_python
else:
    python_exe = linux_python


class ListModeWindow(wx.Frame): 
    def __init__(self, parent, title, dev_ind = 0): 
        super(ListModeWindow, self).__init__(parent, title = title)
        self.EMORPHO = 0x6001
        self.PMT1K = 0x101
        self.PMT3K = 0x103
        self.SIPM1K = 0x201
        self.SIPM3K = 0x203
        
        # Communication with the MCA
        self.MCA_IO = mca_io.MCA_IO()  # For communication with the MDS
        
        #-- Here we use the first mca in the MCA_IO.mca dictionary
        self.sn = list(self.MCA_IO.mca)[dev_ind]
        self.MCA = self.MCA_IO.mca[self.sn]  
        
        self.mca_id = self.MCA["mca_id"]
        self.commands = self.MCA["commands"]
        
        self.disp_ctrl = self.MCA["display_controls"]["list_mode"]["data"]
        self.display_name = "list_mode"  # The name of the entry in the display_controls.json file; used by graph_ctrl_grid
        
        self.overlay = 20  # Maximum number of pulses to overlay in the display
        
        # Build the panel
        panel = wx.Panel(self, size = (5000, 3000)) 
        self.bck_color = panel.GetBackgroundColour()
        self.figure, self.axes = plt.subplots()  # figsize is in inch
        self.init_line_plots(self.MCA["plot_controls"]["list_mode"])  # Set axes, labels and colors

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
        self.box_graph.Add(self.cursor_text, 0, wx.TOP | wx.LEFT, 1)
        
        # Make a list of action buttons
        self.button_list = []
        button = wx.Button(panel, id = wx.ID_ANY, label="New", name="start_list_mode")
        self.button_list += [button]
        
        button = wx.Button(panel, id = wx.ID_ANY, label="Weights", name="load_psd_weights")
        self.button_list += [button]
        
        button = wx.Button(panel, id = wx.ID_ANY, label="Save", name="save_list_mode")
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
        if name in ["start_list_mode", "save_list_mode", "load_psd_weights"]:
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
            
    def start_list_mode(self):
        num_buffers = max(1, int(self.disp_ctrl["num_buffers"]["value"]))
        self.energies = []
        self.data_two = [] # Will be times or psd values
        out_file = self.disp_ctrl["file"]["value"]
        for n in range(num_buffers):
            self.MCA_IO.submit_command(self.sn, self.commands["start_list_mode"])
            while True:
                time.sleep(0.01)
                fpga_results = self.MCA_IO.submit_command(self.sn, self.commands["fpga_results"])[self.sn]
                if fpga_results["user"]["lm_done"]:
                    break
            buffer = self.MCA_IO.submit_command(self.sn, self.commands["read_list_mode"])[self.sn]
            self.lm_mode = buffer["fields"]["mode"]
            if n < self.overlay:
                self.energies += buffer["user"]["energies"]
                if self.lm_mode == 0:
                    self.data_two += buffer["user"]["times"]
                else:
                    self.data_two += buffer["user"]["short_sums"]
            
            if num_buffers > self.overlay:
                with open(out_file, 'a') as fout:
                    comment = self.disp_ctrl["comment"]["value"]
                    if self.lm_mode == 0:
                        fout.write(json.dumps({"comment": comment, "energies": buffer["user"]["energies"], "times": buffer["user"]["times"]})+'\n')
                    else:
                        fout.write(json.dumps({"comment": comment, "energies": buffer["user"]["energies"], "psd": buffer["user"]["short_sums"]})+'\n')
                        
        kev_bin = float(self.disp_ctrl["kev_bin"]["value"])

        self.line_plot.set_xdata(self.energies)
        self.line_plot.set_ydata(self.data_two)

        lowest = min(self.data_two)
        highest = max(self.data_two)

        self.axes.set(**{"xlim": [0, max(self.energies)]})
        self.axes.set(**{"ylim": [lowest, highest]})
        
        if self.lm_mode == 0:
            self.axes.set_ylabel("Times, in seconds")
        else:
            self.axes.set_ylabel("Short sum, in keV")
        
        self.canvas.draw()
        
    def save_list_mode(self):
        out_file = self.disp_ctrl["file"]["value"]
        splt_out_file = out_file.strip('.').rsplit('/', 1)
        data_dir_path = splt_out_file[0]
        file_name = splt_out_file[1]
        default_path = os.path.dirname(os.getcwd()) + data_dir_path
        try:
            data_path = self.last_saved_path
        except:
            data_path = default_path
        
        with wx.FileDialog(self, "Save list mode data", wildcard="json files (*.json)|*.json", defaultDir = data_path, defaultFile = file_name,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return 
            pathname = fileDialog.GetPath()
            self.last_saved_path = os.path.dirname(pathname)
            try:
                with open(pathname, 'a+') as fout:
                    comment = self.disp_ctrl["comment"]["value"]
                    if self.lm_mode == 0:
                        fout.write(json.dumps({"comment": comment, "energies": self.energies, "times": self.data_two})+'\n')
                    else:
                        fout.write(json.dumps({"comment": comment, "energies": self.energies, "psd": self.data_two})+'\n')
            except IOError: 
                wx.LogError("Cannot save current data in file '%s'." % out_file)
                
    def load_psd_weights(self):
        """
            Weights should be floats between -1 and 1.
        """
        load_file = self.disp_ctrl["weights"]["value"]
        splt_load_file = load_file.strip('.').rsplit('/', 1)
        weights_dir_path = splt_load_file[0]
        file_name = splt_load_file[1]
        default_path = os.path.dirname(os.getcwd()) + weights_dir_path
        default_name = file_name

        try:
            weights_path = self.last_weights_path
            weights_file = self.last_weights_file
        except:
            weights_path = default_path
            weights_file = default_name
            
        with wx.FileDialog(self, "Load pulse shape discrimination weights", wildcard="weights file (*.py/*.json)|*.py; *.json", 
                        defaultDir = weights_path, defaultFile = weights_file, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            pathname = fileDialog.GetPath()
            self.last_weights_path = os.path.dirname(pathname)
            self.last_weights_file = os.path.basename(pathname)
            weights_file = pathname.strip()
            
            try: 
                if weights_file.endswith(".json"):
                    with open(weights_file, 'r') as fin:
                        weights = json.loads(fin.read())["weights"]
                else:  # Treat it as python code                
                    ret = subprocess.run([python_exe, weights_file], capture_output=True)
                    weights = json.loads(ret.stdout)
                
                # The json file will have integers from 0 to at least 32767
                # But the *.py files makes floats between -1.0 and 1.0 (-1.0, 1.0]
                if max(weights)<2:  
                    for n in range(len(weights)):  # Convert the weights to a 2's complement 16-bit number
                        w = weights[n]
                        if w >= 0:
                            weights[n] = min(32767, int(w*32767))
                        else:
                            weights[n] = max(32768, min(65535, 65536 + int(w*32768)))
            
                nw = 32*(len(weights)//32)  # Must be multiples of 32 items; incomplete blocks will not be written
                cmd = self.MCA["commands"]["write_fpga_weights"]
                cmd["data"] = {"registers": weights[0: nw]}
                cmd["num_items"] = nw
                self.MCA_IO.submit_command(self.sn, cmd)
                if weights_file.endswith(".py"):
                    fragments = weights_file.split(".")
                    concat_frag = ".".join(fragments[0:-1])
                    out_file = "{}.json".format(concat_frag)
                    print('A json file with the new weights is generated at {0}'.format(out_file))
                    with open(out_file, "w") as fout:
                        fout.write(json.dumps({"weights": weights[0: nw]}))
                    
            except:
                wx.LogError("Cannot open file {}.".format(out_file))

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
    panel = ListModeWindow(None,  'List Mode ' + dev_sn, dev_ind)
    panel.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    main()
    
    
"""
Notes:

https://wxpython.org/Phoenix/docs/html/sizers_overview.html#sizers-overview

"""