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

class SampleBckWindow(wx.Frame): 
    def __init__(self, parent, title, dev_ind = 0):  
        super(SampleBckWindow, self).__init__(parent, title = title)
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
        
        # Build the panel
        panel = wx.Panel(self, size = (5000, 3000)) 
        self.bck_color = panel.GetBackgroundColour()
        self.figure, self.axes = plt.subplots()  # figsize is in inch
        self.lp_names = ["sample", "bck", "diff", "sample_roi", "bck_roi", "diff_roi", "fit"]
        #self.lp_colors = ["DodgerBlue", "SlateGreen", "Grey", "OrangeRed", "OrangeRed", "OrangeRed", "Yellow"]
        self.init_line_plots(self.MCA["plot_controls"]["sample_bck"])  # Set axes, labels and colors
        
        self.disp_ctrl = self.MCA["display_controls"]["sample_bck"]["data"]
        self.display_name = "sample_bck"  # The name of the entry in the display_controls.json file
        
        self.canvas = FigureCanvas(panel, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        
        self.cursor_text = wx.StaticText( self, wx.ID_ANY, "X,Y =", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.cursor_text.SetBackgroundColour(self.bck_color)
        self.cursor_text.Wrap( -1 )
        self.canvas.mpl_connect('motion_notify_event', self.onCursorMotion)
        
        self.sample_rate_text = wx.StaticText( self, wx.ID_ANY, "Sample: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.sample_rate_text.SetBackgroundColour(self.bck_color)
        self.bck_rate_text = wx.StaticText( self, wx.ID_ANY, "Bck: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.bck_rate_text.SetBackgroundColour(self.bck_color)
        self.diff_rate_text = wx.StaticText( self, wx.ID_ANY, "Diff: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.diff_rate_text.SetBackgroundColour(self.bck_color)
        self.statistics_text = wx.StaticText( self, wx.ID_ANY, "Statistics: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.statistics_text.SetBackgroundColour(self.bck_color)
        self.fit_text = wx.StaticText( self, wx.ID_ANY, "Fit: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.fit_text.SetBackgroundColour(self.bck_color)
        
        self.box_local = wx.BoxSizer(wx.VERTICAL)
        self.box_graph = wx.BoxSizer(wx.VERTICAL)
        self.box_ctrl = wx.BoxSizer(wx.VERTICAL)
        
        self.box_graph.Add(self.canvas, 1, wx.TOP | wx.LEFT| wx.EXPAND, 1 )
        self.box_graph.Add(self.toolbar, 0, wx.TOP | wx.LEFT, 1 )
        self.box_graph.Add(self.cursor_text,0, wx.TOP | wx.LEFT, 1 )
        self.box_graph.Add(self.sample_rate_text,0, wx.TOP | wx.LEFT, 1 )
        self.box_graph.Add(self.bck_rate_text,0, wx.TOP | wx.LEFT, 1 )
        self.box_graph.Add(self.diff_rate_text,0, wx.TOP | wx.LEFT, 1 )
        self.box_graph.Add(self.statistics_text,0, wx.TOP | wx.LEFT, 1 )
        self.box_graph.Add(self.fit_text,0, wx.TOP | wx.LEFT, 1 )
        
        # Make a list of action buttons and put all buttons in a horizontal sizer
        # Then add the buttonbox to the vertical stack
        self.button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_pars = [{"label": "Toggle Alarm", "name": "toggle_alarm"}, 
                       {"label": "Sample", "name": "start_mca"}, {"label": "Background", "name": "start_bck"}, 
                       {"label": "Refresh", "name": "refresh"}, 
                       {"label": "Fit", "name": "fit"}, {"label": "Save", "name": "save_histogram"}]       
        for par in button_pars:
            button = wx.Button(panel, id = wx.ID_ANY, **par)
            button.Bind(wx.EVT_BUTTON, self.OnClicked)
            self.button_box.Add(button, 0, wx.RIGHT, 10)   
        self.switch = wx.Button(panel, id = wx.ID_ANY, label="Figure only", name="graph_ctrl_on_off") 
        self.switch.Bind(wx.EVT_BUTTON, self.OnClicked)
        self.button_box.Add(self.switch, 0)

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
        if name in ["toggle_alarm", "save_histogram", "refresh", "fit"]:
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
            if name == "start_mca":
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
            
    def toggle_alarm(self):
        """
            Read the use->sample_alarm value, toggle between 0 and 1, and write it back
        """
        self.arm_ctrl = self.MCA_IO.submit_command(self.sn, self.commands["read_arm_ctrl"])[self.sn]
        sample_alarm = self.arm_ctrl["user"]["sample_alarm"]
        sample_alarm = 0 if sample_alarm else 1  # Toggle
        cmd = dict(self.commands["write_arm_ctrl"])  # Get a fresh copy
        cmd.update({"data": {"user": {"sample_alarm": sample_alarm}}})

        self.MCA_IO.submit_command(self.sn, cmd)
            
    def save_histogram(self):
        out_file = self.disp_ctrl["file"]["value"]
        items = [self.arm_ctrl, self.arm_status, self.histo, self.bck, self.diff]
        comment = self.MCA["display_controls"]["sample_bck"]["data"]["comment"]["value"]
        
        splt_out_file = out_file.strip('.').rsplit('/', 1)
        data_dir_path = splt_out_file[0]
        file_name = splt_out_file[1]
        default_path = os.path.dirname(os.getcwd()) + data_dir_path
        try:
            data_path = self.last_saved_path
        except:
            data_path = default_path
        
        with wx.FileDialog(self, "Save sample background data", wildcard="json files (*.json)|*.json", defaultDir = data_path, defaultFile = file_name,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return 
            pathname = fileDialog.GetPath()
            self.last_saved_path = os.path.dirname(pathname)
            try:
                with open(pathname, 'a+') as fout:
                    for item in items:
                        item["comment"] = comment
                        fout.write(json.dumps(item)+'\n')
            except IOError: 
                wx.LogError("Cannot save current data in file '%s'." % out_file)
            
            
    def refresh(self):
        #self.msg_text.SetLabel("")
        #self.fit_text.SetLabel("")
        
        self.arm_ctrl = self.MCA_IO.submit_command(self.sn, self.commands["read_arm_ctrl"])[self.sn]
        roi_low = int(self.arm_ctrl["fields"]["roi_low"])
        roi_high = int(self.arm_ctrl["fields"]["roi_high"])
        active_bank = int(self.arm_ctrl["user"]["active_bank"])
        sample_alarm = int(self.arm_ctrl["user"]["sample_alarm"])
        
        self.kev_bin = int(self.MCA["display_controls"]["sample_bck"]["data"]["kev_bin"]["value"])
        
        if active_bank == 0:
        
            # Read histogram and count rate data
            self.arm_status = self.MCA_IO.submit_command(self.sn, self.commands["read_rates"])[self.sn]
            run_time_sample = self.arm_status["fields"]["run_time_sample"]
            run_time_bck = self.arm_status["fields"]["run_time_bck"]
            
            count_rate = self.arm_status["fields"]["count_rate"]
            count_rate_err = self.arm_status["fields"]["count_rate_err"] / count_rate if count_rate > 0 else 0            
            count_rate_bck = self.arm_status["fields"]["count_rate_bck"]
            count_rate_bck_err = self.arm_status["fields"]["count_rate_bck_err"] / count_rate_bck if count_rate_bck > 0 else 0
            count_rate_diff = self.arm_status["fields"]["count_rate_diff"]
            count_rate_diff_err = self.arm_status["fields"]["count_rate_diff_err"] / count_rate_diff if count_rate_diff > 0 else 0
            
            roi_rate = self.arm_status["fields"]["roi_rate"]
            roi_rate_err = self.arm_status["fields"]["roi_rate_err"] / roi_rate if roi_rate > 0 else 0            
            roi_rate_bck = self.arm_status["fields"]["roi_rate_bck"]
            roi_rate_bck_err = self.arm_status["fields"]["roi_rate_bck_err"] / roi_rate_bck if roi_rate_bck > 0 else 0
            roi_rate_diff = self.arm_status["fields"]["roi_rate_diff"]
            roi_rate_diff_err = self.arm_status["fields"]["roi_rate_diff_err"] / roi_rate_diff if roi_rate_diff > 0 else 0
            
            bck_probability = self.arm_status["fields"]["bck_probability"]
            bck_alarmist = self.arm_status["fields"]["bck_low_probability"]
            bck_cautious = self.arm_status["fields"]["bck_high_probability"]
            
            sample_events =  count_rate * run_time_sample
            bck_events =  count_rate_bck * run_time_bck
            ratio = sample_events/bck_events if bck_events>0 else 1.0  # Scale the previously measured background in proportion to the new sample measurement.
            
            self.histo = self.MCA_IO.submit_command(self.sn, self.commands["read_mca"])[self.sn]
            self.bck = self.MCA_IO.submit_command(self.sn, self.commands["read_bck"])[self.sn]
            self.diff = self.MCA_IO.submit_command(self.sn, self.commands["read_diff"])[self.sn]

            histo = self.histo["fields"]["histogram"]
            bck = self.bck["fields"]["histogram"]
            diff = self.diff["fields"]["histogram"]
            
            biggest = max(max(histo), max(bck), max(diff))

            self.norm = 1.0   
            y_mag = 0
            if biggest > 1.0e6: 
                self.norm = 1e-6
                y_mag = 2
            elif biggest > 1.0e3:
                self.norm = 1e-3
                y_mag = 1

            histo_data = [h*self.norm for h in histo]
            bck_data = [h*self.norm*ratio for h in bck]
            diff_data = [h*self.norm for h in diff]
            num_bins = len(histo_data)
            x_data = [n*self.kev_bin for n in range(num_bins)]

            roi_high = min(roi_high, num_bins)

            histo_roi = histo_data[roi_low: roi_high]
            bck_roi = bck_data[roi_low: roi_high]
            diff_roi = diff_data[roi_low: roi_high]
            num_roi = roi_high - roi_low
            x_roi = [(roi_low + n)*self.kev_bin for n in range(num_roi)]

            xdat_list = [x_data, x_data, x_data, x_roi, x_roi, x_roi]
            ydat_list = [histo_data, bck_data, diff_data, histo_roi, bck_roi, diff_roi]

            for name, xd, yd in zip(self.lp_names, xdat_list, ydat_list):
                self.lp_dict[name].set_xdata(xd)
                self.lp_dict[name].set_ydata(yd)

            # Limits=None should cause auto-scale, but here it does not.
            self.axes.set(**{"xlim": [0, x_data[-1]]})
            self.axes.set(**{"ylim": [0, max(max(histo_data), max(bck_data), max(diff_data))+1]})

            self.axes.set_ylabel(self.MCA["plot_controls"]["histogram"]["labels"]["ylabel"][y_mag])
            
            self.sample_rate_text.SetLabelText("Sample: Run time= {:.1f}s; Count rate= {:.3f}+/-{:.3f}%".format(run_time_sample, roi_rate, 100*roi_rate_err))
            self.bck_rate_text.SetLabelText("Bck: Run time= {:.1f}s; Count rate= {:.3f}+/-{:.3f}%".format(run_time_bck, roi_rate_bck, 100*roi_rate_bck_err))
            self.diff_rate_text.SetLabelText("Diff: Run time= {:.1f}s; Count rate= {:.3f}+/-{:.3f}%".format(run_time_sample, roi_rate_diff, 100*roi_rate_diff_err))
            
            strength = -math.log10(bck_probability) if bck_probability>0 else 0
            strength_low = -math.log10(bck_cautious) if bck_cautious>0 else 0
            strength_high = -math.log10(bck_alarmist) if bck_alarmist>0 else 0
            self.statistics_text.SetLabelText("Sample Strength: {:.2f} < {:.2f} < {:.2f} ".format(strength_low, strength, strength_high))
            
        else:
            # Read background histogram and count rate data
            self.arm_status = self.MCA_IO.submit_command(self.sn, self.commands["read_rates"])[self.sn]
            
            run_time_bck = self.arm_status["fields"]["run_time_bck"]
            count_rate_bck = self.arm_status["fields"]["count_rate_bck"]
            count_rate_bck_err = self.arm_status["fields"]["count_rate_bck_err"] / count_rate_bck if count_rate_bck > 0 else 0

            self.bck = self.MCA_IO.submit_command(self.sn, self.commands["read_bck"])[self.sn]

            bck = self.bck["fields"]["histogram"]

            biggest = max(bck)

            self.norm = 1.0   
            y_mag = 0
            if biggest > 1.0e6: 
                self.norm = 1e-6
                y_mag = 2
            elif biggest > 1.0e3:
                self.norm = 1e-3
                y_mag = 1

            bck_data = [h*self.norm for h in bck]
            num_bins = len(bck_data)
            x_data = [n*self.kev_bin for n in range(num_bins)]

            roi_high = min(roi_high, num_bins)

            bck_roi = bck_data[roi_low: roi_high]
            num_roi = roi_high - roi_low
            x_roi = [(roi_low + n)*self.kev_bin for n in range(num_roi)]

            xdat_list = [x_data, x_roi]
            ydat_list = [bck_data, bck_roi]

            for name, xd, yd in zip(["bck", "bck_roi"], xdat_list, ydat_list):
                self.lp_dict[name].set_xdata(xd)
                self.lp_dict[name].set_ydata(yd)

            # Limits=None should cause auto-scale, but here it does not.
            self.axes.set(**{"xlim": [0, x_data[-1]]})
            self.axes.set(**{"ylim": [0, max(max(bck_data), max(bck_roi))+1]})
            self.axes.set_ylabel(self.MCA["plot_controls"]["histogram"]["labels"]["ylabel"][y_mag])
            
            self.bck_rate_text.SetLabelText("BCK: Run time= {:.1f}s; Count rate= {:.3f}+/-{:.3f}%".format(run_time_bck, count_rate_bck, count_rate_bck_err))
        
        self.canvas.draw()
        
    
    def fit(self):
        fit_xmin = float(self.MCA["display_controls"]["sample_bck"]["data"]["fit_xmin"]["value"])
        fit_xmax = float(self.MCA["display_controls"]["sample_bck"]["data"]["fit_xmax"]["value"])
        imin = int(fit_xmin/self.kev_bin + 0.5)  # self.kev_bin is determined by self.refresh()
        imax = int(fit_xmax/self.kev_bin + 0.5)
        a = min(imin, imax)
        b = max(imin, imax)
        fit_bins = b-a
        histo_to_fit = self.diff["fields"]["histogram"][a:b]
        #xmax, ymax, fwhm, net_counts, bck_counts, yl, yr, net_histo, fit_histo = histo_analysis.do_gauss_fit(histo_to_fit, bck_model=2, fwhm=50)
        res = histo_analysis.do_gauss_fit(histo_to_fit, bck_model=2, fwhm=0.07*(a+b)/2.0)
        
        peak_pos = self.kev_bin*(res["x_max"]+imin)
        energy_res = 100 * res["fwhm"] / (res["x_max"]+imin)
        msg = "Peak: {:.2f}fwhm: {:.2f}%Net counts: {:.0f}".format(peak_pos, energy_res, res["net_counts"])
        self.fit_text.SetLabel(msg)
        
        y_data = [h*self.norm for h in res["fit_histo"]]
        x_data = [(imin+n)*self.kev_bin for n in range(fit_bins)]

        self.lp_dict["fit"].set_xdata(x_data)
        self.lp_dict["fit"].set_ydata(y_data)
        self.canvas.draw()

        
    def init_line_plots(self, ctrl):
        
        self.lp_dict = {}
        lp_colors = self.MCA["plot_controls"]["sample_bck"]["colors"]

        self.plots = []  # line plots where we update the data with every refresh or fit
        for name, color in zip(self.lp_names, lp_colors):
            self.lp_dict[name] = self.axes.plot([], [])[0]
            ctrl['line_ctrl']["color"] = color
            plt.setp(self.lp_dict[name], **ctrl['line_ctrl'])
        
        # From the JSON file we can receive an empty list [], but not a None.
        # aLSO: None should cause auto-scale, but here it does not.
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
    panel = SampleBckWindow(None,  'Sample - Bck ' + dev_sn, dev_ind)
    panel.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    main()
    
    
"""
Notes:

https://wxpython.org/Phoenix/docs/html/sizers_overview.html#sizers-overview

"""