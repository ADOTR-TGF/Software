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
import pulse_analysis

class PulseCaptureWindow(wx.Frame): 
    def __init__(self, parent, title, dev_ind = 0): 
        super(PulseCaptureWindow, self).__init__(parent, title = title)
        self.EMORPHO = 0x6001
        self.PMT1K = 0x101
        self.PMT2K = 0x102
        self.PMT3K = 0x103
        self.SIPM1K = 0x201
        self.SIPM2K = 0x202
        self.SIPM3K = 0x203
        
        # Communication with the MCA
        self.MCA_IO = mca_io.MCA_IO()  # For communication with the MDS
        
        #-- Here we use the first mca in the MCA_IO.mca dictionary
        self.sn = list(self.MCA_IO.mca)[dev_ind]
        self.MCA = self.MCA_IO.mca[self.sn]  
        
        self.mca_id = self.MCA["mca_id"]
        self.commands = self.MCA["commands"]
        
        self.disp_ctrl = self.MCA["display_controls"]["pulse"]["data"]
        self.display_name = "pulse"  # The name of the entry in the display_controls.json file; used by graph_ctrl_grid
        
        self.overlay = 20  # Maximum number of pulses to overlay in the display
        
        # Build the panel
        panel = wx.Panel(self, size = (5000, 3000)) 
        self.bck_color = panel.GetBackgroundColour()
        self.figure, self.axes = plt.subplots()  # figsize is in inch
        self.init_line_plots(self.MCA["plot_controls"]["pulse"])  # Set axes, labels and colors

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
        
        self.msg_text = wx.StaticText( self, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.msg_text.SetBackgroundColour(self.bck_color)
        
        self.box_graph.Add(self.msg_text,0, wx.RIGHT)
        
        # Make a list of action buttons
        self.button_list = []
        button = wx.Button(panel, id = wx.ID_ANY, label="New", name="start_pulse")
        self.button_list += [button]
        
        button = wx.Button(panel, id = wx.ID_ANY, label="Save", name="save_pulse")
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
        if name in ["start_pulse", "save_pulse"]:
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
            
    def start_pulse(self):
        for n in range(len(self.lp_list)):
            self.lp_list[n].set_xdata(0)
            self.lp_list[n].set_ydata(0)
            
        num_pulses = max(1, int(self.disp_ctrl["num_pulses"]["value"]))
        pulse_list = []
        out_file = self.disp_ctrl["file"]["value"]
        time_out = 1.0
        for n in range(num_pulses):
            self.MCA_IO.submit_command(self.sn, self.commands["start_pulse"])
            then = time.time()
            while True:
                time.sleep(0.01)
                if self.mca_id in [self.PMT3K, self.SIPM3K, self.EMORPHO]:                
                    status = self.MCA_IO.submit_command(self.sn, self.commands["fpga_results"])[self.sn]
                    if status["user"]["trace_done"]:
                        break
                elif self.mca_id in [self.PMT2K, self.SIPM2K]:
                    status = self.MCA_IO.submit_command(self.sn, self.commands["arm_status"])[self.sn]
                    if status["user"]["trace_done"]:
                        break
                
                if time.time()-then > time_out:
                    break;
                    
            with open("log.txt", "a") as fout:
                fout.write("Trace Done: {}\n".format(status["user"]["trace_done"]))
                now = time.time()
            pulse = self.MCA_IO.submit_command(self.sn, self.commands["read_pulse"])[self.sn]
            if len(pulse_list) < self.overlay:
                pulse_list += [pulse["fields"]["trace"]]
                
            if num_pulses > self.overlay:
                with open(out_file, 'a') as fout:
                    pulse["comment"] = self.disp_ctrl["comment"]["value"]
                    fout.write(json.dumps(pulse)+'\n')
        
        self.pulse = pulse
        dt = 1.0e6/self.MCA["adc_sr"]
        plen = len(pulse["fields"]["trace"])
        x_data = [ n*dt for n in range(plen)] 
        max_list = []
        min_list = []
        for n in range(len(pulse_list)):
            self.lp_list[n].set_xdata(x_data)
            self.lp_list[n].set_ydata(pulse_list[n])
            max_list += [max(pulse_list[n])]
            min_list += [min(pulse_list[n])]
        
        lowest = min(min_list)
        highest = max(max_list)
        self.axes.set(**{"xlim": [0, x_data[-1]]})
        self.axes.set(**{"ylim": [lowest-10, highest+10]})
        
        t_min = int(float(self.disp_ctrl["t_min"]["value"])*self.MCA["adc_sr"] + 0.5)
        t_max = int(float(self.disp_ctrl["t_max"]["value"])*self.MCA["adc_sr"] + 0.5)
        ps = pulse_analysis.pulse_summary(pulse["fields"]["trace"], [t_min, t_max], adc_sr=self.MCA["adc_sr"])
        
        if ps["pulse_found"] == 0:
            msg = "Min, Max: {:.1f}mV, {:.1f}mV; Average, std_dev: {:.2f}mV, {:.2f}mV".format(ps["mini"], ps["maxi"], ps["avg"], ps["std_dev"])
        elif ps["pulse_found"] == 1:
            msg = "Rise, peak, fall time, fwhm: {:.3f}, {:.3f}us Peaking time, fwhm {:.3f}, {:.3f}us\nAmplitude, DC-val: {:.1f}mV, {:.2f}mV ".format(ps["rise_time"], ps["peaking_time"], ps["fall_time"], ps["fwhm"], ps["amplitude"], ps["dc_val"])
        else:
            msg = ""

        self.msg_text.SetLabel(msg)
        self.canvas.draw()

    def save_pulse(self):
        out_file = self.disp_ctrl["file"]["value"]
        splt_out_file = out_file.strip('.').rsplit('/', 1)
        data_dir_path = splt_out_file[0]
        file_name = splt_out_file[1]
        default_path = os.path.dirname(os.getcwd()) + data_dir_path
        try:
            data_path = self.last_saved_path
        except:
            data_path = default_path
        
        with wx.FileDialog(self, "Save pulses data", wildcard="json files (*.json)|*.json", defaultDir = data_path, defaultFile = file_name,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return 
            pathname = fileDialog.GetPath()
            self.last_saved_path = os.path.dirname(pathname)
            try:
                with open(pathname, 'a+') as fout:
                    self.pulse["comment"] = self.disp_ctrl["comment"]["value"]
                    fout.write(json.dumps(self.pulse)+'\n')
            except IOError: 
                wx.LogError("Cannot save current data in file '%s'." % out_file)
                
    def init_line_plots(self, ctrl):
        
        self.lp_list = []

        self.plots = []  # line plots where we update the data with every refresh or fit
        for n in range(self.overlay):
            self.lp_list += [self.axes.plot([], [])[0]]
            plt.setp(self.lp_list[-1], **ctrl['line_ctrl'])
            
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
    panel = PulseCaptureWindow(None,  'Pulse Capture ' + dev_sn, dev_ind)
    panel.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    main()
    
    
"""
Notes:

https://wxpython.org/Phoenix/docs/html/sizers_overview.html#sizers-overview

"""