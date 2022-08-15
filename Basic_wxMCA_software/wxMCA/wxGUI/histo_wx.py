import math
from sqlite3 import Timestamp
import time
from datetime import datetime
import wx
import os
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
# from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import json
import csv
import mca_io
import graph_ctrl_grid as gcd
import histo_analysis
import save_histo

class HistogramWindow(wx.Frame): 
    def __init__(self, parent, title, dev_ind = 0): 
        super(HistogramWindow, self).__init__(parent, title = title)
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
        
        self.disp_ctrl = self.MCA["display_controls"]["histogram"]["data"]
        self.display_name = "histogram"  # The name of the entry in the display_controls.json file; used by graph_ctrl_grid
        
        # Build the panel
        panel = wx.Panel(self, size = (5000, 3000)) 
        self.bck_color = panel.GetBackgroundColour()
        self.figure, self.axes = plt.subplots()  # figsize is in inch
        self.lp_names = ["histo", "fit"]
        self.lp_colors = ["DodgerBlue", "OrangeRed"]
        self.init_line_plots(self.MCA["plot_controls"]["histogram"])  # Set axes, labels and colors

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
        self.box_graph.Add(self.toolbar, 0,  wx.TOP | wx.LEFT, 1)
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

        # Add savebox and user can choose to save histogram as json or csv file
        self.save_box = wx.BoxSizer(wx.HORIZONTAL)
        button = wx.Button(panel, id = wx.ID_ANY, label="Save as", name="save_histogram") 
        button.Bind(wx.EVT_BUTTON, self.OnClicked)
        self.save_box.Add(button, 0, wx.RIGHT, 5)
        save_choices = ["json", "csv", "xml"]
        self.save_choice_box = wx.Choice(panel, choices = save_choices)
        self.save_choice_box.SetSelection(0)
        self.save_selected = 0
        self.save_box.Add(self.save_choice_box, 0, wx.RIGHT, 4)
        self.box_graph.Add(self.save_box, 0, wx.BOTTOM| wx.TOP, 0)
        self.save_choice_box.Bind(wx.EVT_CHOICE, self.OnSaveChoice)

        # Make a list of action buttons
        self.button_list = []
        button = wx.Button(panel, id = wx.ID_ANY, label="New", name="start_mca")
        self.button_list += [button]

        button = wx.Button(panel, id = wx.ID_ANY, label="Refresh", name="refresh") 
        self.button_list += [button]
        
        button = wx.Button(panel, id = wx.ID_ANY, label="Smooth", name="smooth") 
        self.button_list += [button]
        
        button = wx.Button(panel, id = wx.ID_ANY, label="Fit", name="fit") 
        self.button_list += [button]
        
        button = wx.Button(panel, id = wx.ID_ANY, label="Cal", name="cal_mca") 
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
    
    def OnSaveChoice(self, event):
        self.save_selected = self.save_choice_box.GetSelection()
            
    def OnClicked(self, event): 
        name = event.GetEventObject().GetName()
        if name in ["refresh", "fit", "smooth", "cal_mca", "save_histogram"]:
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
            
    def save_histogram(self):
        out_file = self.disp_ctrl["file"]["value"]
        comment = self.disp_ctrl["comment"]["value"]
        sn = self.sn
        if self.MCA["mca_id"] == 0x6001:
            fpga_ctrl = self.MCA_IO.submit_command(sn, {"name": "fpga_ctrl",  "dir": "read"})[sn]
            fpga_results = self.MCA_IO.submit_command(sn, {"name": "fpga_results",  "dir": "read"})[sn]
            count_rates = self.MCA_IO.submit_command(sn, {"name": "fpga_statistics",  "dir": "read"})[sn]
            histo = self.MCA_IO.submit_command(sn, {"name": "fpga_histogram",  "dir": "read", "num_items": 4096})[sn]
            out_dict = {"comment": comment, "serial_number": sn, "short_sn": sn, "mca_id_str":self.MCA["mca_id_str"], 
                        "fpga_status": fpga_results, "fpga_ctrl": fpga_ctrl, "rates": count_rates, "histo": histo}
        elif self.MCA["mca_id"] in  [ 0x203, 0x103]:
            arm_version = self.MCA_IO.submit_command(sn, {"name": "arm_version",  "dir": "read"})[sn]
            arm_status = self.MCA_IO.submit_command(sn, {"name": "arm_status",  "dir": "read"})[sn]
            fpga_ctrl = self.MCA_IO.submit_command(sn, {"name": "fpga_ctrl",  "dir": "read"})[sn]
            fpga_results = self.MCA_IO.submit_command(sn, {"name": "fpga_results",  "dir": "read"})[sn]
            count_rates = self.MCA_IO.submit_command(sn, {"name": "fpga_statistics",  "dir": "read"})[sn]
            histo = self.MCA_IO.submit_command(sn, {"name": "fpga_histogram",  "dir": "read", "num_items": 4096})[sn]
            out_dict = {"comment": comment, "serial_number": sn, "short_sn": arm_version["fields"]["short_sn"], 
                        "mca_id_str": self.MCA["mca_id_str"], "arm_version": arm_version, 
                        "arm_status": arm_status, "fpga_status": fpga_results, "fpga_ctrl": fpga_ctrl, 
                        "rates": count_rates, "histo": histo}
        elif self.MCA["mca_id"] in  [ 0x201, 0x101, 0x202, 0x102]:
            # To do: check for histo_2k, histo_4k bit to double num_bins
            nd = { 0x201: 1024, 0x101: 1024, 0x202: 2048, 0x102: 2048}
            num_bins = nd[self.MCA["mca_id"]]
            arm_version = self.MCA_IO.submit_command(sn, {"name": "arm_version",  "dir": "read"})[sn]
            arm_status = self.MCA_IO.submit_command(sn, {"name": "arm_status",  "dir": "read"})[sn]
            arm_ctrl = self.MCA_IO.submit_command(sn, {"name": "arm_ctrl",  "dir": "read"})[sn]
            histo = self.MCA_IO.submit_command(sn, {"name": "arm_histogram",  "dir": "read", "num_items": num_bins})[sn]
            out_dict = {"comment": comment, "serial_number": sn, "short_sn": arm_version["fields"]["short_sn"], 
                        "mca_id_str": self.MCA["mca_id_str"], "arm_version": arm_version, 
                        "arm_status": arm_status, "arm_ctrl": arm_ctrl, "histo": histo}
        
        timekey = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        if self.MCA["mca_id"] in  [ 0x6001]:
            short_sn = 'histogram_' + self.MCA["sn"] + '_' + timekey + '.json'
        else:
            short_sn = 'histogram_' + out_dict['arm_version']['user']['unique_sn'][:8] + '_' + timekey + '.json'
        splt_out_file = out_file.strip('.').rsplit('/', 1)
        data_dir_path = splt_out_file[0]
        file_name = splt_out_file[1]
        file_name_record = short_sn
        default_path = os.path.dirname(os.getcwd()) + data_dir_path
        try:
            data_path = self.last_saved_path
        except:
            data_path = default_path
        
        if self.save_selected == 0: 
            with wx.FileDialog(self, "Save histogram data as json", wildcard="json files (*.json)|*.json", defaultDir = data_path, defaultFile = file_name_record,
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
                
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return 
                pathname = fileDialog.GetPath()
                self.last_saved_path = os.path.dirname(pathname)
                try:
                    save_histo.export_to_files(self.mca_id, out_dict, self.save_selected, pathname, data_path, file_name)
                except IOError: 
                    wx.LogError("Cannot save current data in file {}.".format(out_file))
        elif self.save_selected == 1:
            with wx.FileDialog(self, "Save histogram data as csv", wildcard="csv files (*.csv)|*.csv", defaultDir = data_path, defaultFile = file_name_record.replace(".json", ".csv"),
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
                
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return 
                pathname = fileDialog.GetPath()
                self.last_saved_path = os.path.dirname(pathname)
                try:
                    save_histo.export_to_files(self.mca_id, out_dict, self.save_selected, pathname, data_path, file_name)
                except IOError: 
                    wx.LogError("Cannot save current data in file {}.".format(out_file))

        elif self.save_selected == 2:
            with wx.FileDialog(self, "Save histogram data as N42 xml", wildcard="xml files (*.xml)|*.xml", defaultDir = data_path, defaultFile = file_name_record.replace(".json", "_N42.xml"),
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
                
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return 
                pathname = fileDialog.GetPath()
                self.last_saved_path = os.path.dirname(pathname)
                try:
                    save_histo.export_to_files(self.mca_id, out_dict, self.save_selected, pathname, data_path, file_name)                    
                except IOError: 
                    wx.LogError("Cannot save current data in file {}.".format(out_file))

    def refresh(self):
        #self.msg_text.SetLabel("")
        #self.fit_text.SetLabel("")
        
        # Read histogram and count rate data
        
        if self.mca_id in [0x6001, 0x103, 0x203]:
            count_rates = self.MCA_IO.submit_command(self.sn, self.commands["read_rates"])[self.sn]["user"]["bank_0"]
            run_time = count_rates["run_time"]
            count_rate = count_rates["event_rate"]
            count_rate_err = count_rates["event_rate_err"] / count_rate if count_rate > 0 else 0
            min_it = 16  # Minimum and multiple of items to be read
            
        elif self.mca_id in [0x101, 0x201, 0x102, 0x202]:
            count_rates = self.MCA_IO.submit_command(self.sn, self.commands["read_rates"])[self.sn]["fields"]
            run_time = count_rates["run_time_sample"]
            count_rate = count_rates["count_rate"]
            count_rate_err = count_rates["count_rate_err"] / count_rate if count_rate > 0 else 0
            min_it = 32  # Minimum and multiple of items to be read
            
        cmd_histo = self.commands["read_mca"]
        ni = int(self.disp_ctrl["num_bins"]["value"])
        cmd_histo["num_items"] = min_it*((ni-1)//min_it+1)                
        self.histogram = self.MCA_IO.submit_command(self.sn, cmd_histo)[self.sn]
        
        if self.mca_id in [0x6001, 0x103, 0x203, 0x102, 0x202]:
            self.histo = self.histogram["registers"]
        elif self.mca_id in [0x101, 0x201]:
            self.histo = self.histogram["fields"]["histogram"]
            
        y_mag = 0
        self.histo_norm = 1.0
        biggest = max(self.histo)
        if biggest > 1.0e6: 
            self.histo_norm = 1e-6
            y_mag = 2
        elif biggest > 1.0e3: 
            self.histo_norm = 1e-3
            y_mag = 1
        
        y_data = [h*self.histo_norm for h in self.histo]
        
        # Determine keV/MCA_bin
        self.get_kev_bin()
        
        x_data = [n*self.kev_bin for n in range(len(self.histo))]
        
        self.lp_dict["histo"].set_xdata(x_data)
        self.lp_dict["histo"].set_ydata(y_data)
        self.axes.set(**{"xlim": [0, x_data[-1]]})
        self.axes.set(**{"ylim": [0, max(y_data)+0.1]})
        self.axes.set_ylabel(self.MCA["plot_controls"]["histogram"]["labels"]["ylabel"][y_mag])
        
        # Compute the dose rate
        mass = float(self.disp_ctrl["mass"]["value"])
        e_avg, dr_sv, dr_rem = histo_analysis.scint_doserate(self.histo, self.kev_bin, mass, count_rate)
        self.count_rate_text.SetLabelText("Run time {:.1f}s; Count rate= {:.3f} +/- {:.2f}%; E_avg= {:.2f}keV; Dose rate= {:.3f}uSv/hr".format(run_time, count_rate, 100*count_rate_err, e_avg, dr_sv*1e6))
        
        self.canvas.draw()

        
    
    def fit(self):
        fit_xmin = float(self.disp_ctrl["fit_xmin"]["value"])
        fit_xmax = float(self.disp_ctrl["fit_xmax"]["value"])
        imin = int(fit_xmin/self.kev_bin + 0.5)  # self.kev_bin is determined by self.refresh()
        imax = int(fit_xmax/self.kev_bin + 0.5)
        a = min(imin, imax)
        b = max(imin, imax)
        histo_to_fit = self.histo[a:b]
        #xmax, ymax, fwhm, net_counts, bck_counts, yl, yr, net_histo, fit_histo = histo_analysis.do_gauss_fit(histo_to_fit, bck_model=2, fwhm=50)
        res = histo_analysis.do_gauss_fit(histo_to_fit, bck_model=2, fwhm=0.07*(a+b)/2.0)
        
        self.get_kev_bin()
        peak_pos = self.kev_bin*(res["x_max"]+imin)
        energy_res = 100 * res["fwhm"] / (res["x_max"]+imin)
        msg = "Peak: {:.2f}, fwhm: {:.2f}%, Net counts: {:.0f}".format(peak_pos, energy_res, res["net_counts"])
        self.fit_text.SetLabel(msg)
        
        y_data = [h*self.histo_norm for h in res["fit_histo"]]
        x_data = [(imin+n)*self.kev_bin for n in range(len(y_data))]

        self.lp_dict["fit"].set_xdata(x_data)
        self.lp_dict["fit"].set_ydata(y_data)
        self.canvas.draw()
        
    def get_kev_bin(self):        
        self.kev_bin = float(self.disp_ctrl["kev_bin"]["value"])
        if self.mca_id in [0x6001, 0x103, 0x203]:
            fpga_ctrl = self.MCA_IO.submit_command(self.sn, self.commands["read_fpga_ctrl"])[self.sn]
            if self.mca_id in [0x103, 0x203]:  # Check for pulse height measurement
                ha_mode = fpga_ctrl["fields"]["ha_mode"]
            else:
                ha_mode = fpga_ctrl["fields"]["ha_run"]
            
        elif self.mca_id in [0x102, 0x202]:
            arm_ctrl = self.MCA_IO.submit_command(self.sn, self.commands["read_arm_ctrl"])[self.sn]
            ha_mode = arm_ctrl["user"]["amplitude"]
            
        elif self.mca_id in [0x101, 0x201]:    
            ha_mode = 0
            
        if ha_mode == 1:
                self.kev_bin = 1.0
    
    def cal_mca(self):
        par = self.get_op()
        cal_ov = par["ov"]
        ha_run = par["ha_run"] != 0
        kev_bin = float(self.disp_ctrl["kev_bin"]["value"])
        
        self.refresh()
        data = dict()
        if self.mca_id in [self.SIPM1K, self.PMT1K]:
            data["histogram"] = self.histo[0: min(len(self.histo), 850)]  # limit peak finding to the first 850 bins.
        else:
            data["histogram"] = self.histo
        data["desc"] = dict()
        data["desc"]["e_min"] = 0
        data["desc"]["keV_bin"] = kev_bin
        data["desc"]["fwhm_662"] = 0.08
        data["desc"]["is_back_sub"] = 0
        find_res = histo_analysis.find_peaks(data)
        peaks = []
        for peak in find_res:
            e = peak["fit_energy"]
            fwhm_expected = e*data["desc"]["fwhm_662"]*math.sqrt((30.0+662.0)/(30.0+e))
            ok = True
            ok &= peak["type"]==0
            ok &= peak["fit_fwhm"]<2*fwhm_expected
            ok &= peak["fit_chi_sqr"]<20
            #ok &= peak["fit_energy"]>150
            #ok &= peak["confidence"]>20
            #print(peak["fit_energy"], peak["fit_fwhm"], peak["confidence"], peak["fit_chi_sqr"])
            if ok:
                peaks += [peak]
        conf_max = 0
        for peak in peaks:
            if peak["confidence"]>conf_max:
                conf_max= peak["confidence"]
                p_max = peak
            #print(peak["fit_energy"], peak["fit_fwhm"], peak["confidence"], peak["fit_chi_sqr"])
        peak = p_max
        peak_pos = peak["fit_energy"]/kev_bin  # In MCA bins
        #print("Selected:", peak["fit_energy"], peak["fit_fwhm"], peak["confidence"], peak["fit_chi_sqr"])
        
        #res = histo_analysis.fit_cs_peak(self.histo)  # Fit to tallest peak > 50 MCA bins        
        #peak_pos = res["x_max"]  # In MCA bins
        
        cal_peak_height = float(self.disp_ctrl["cal_ph"]["value"])
        cal_peak_energy = float(self.disp_ctrl["cal_kev"]["value"])
        cal_update = float(self.disp_ctrl["cal_update"]["value"]) != 0
        inv_gain_exp = 1.0/float(self.disp_ctrl["gain_exp"]["value"])  # For use with PMT-based MCA when changing the voltage
        
        # Compute the correct ratio for the gain correction
        cal_ratio = cal_peak_energy/kev_bin/peak_pos if peak_pos > 0 else 1.0
        if self.mca_id in [self.EMORPHO, self.PMT2K, self.SIPM2K, self.PMT3K, self.SIPM3K] and ha_run:
            cal_ratio = cal_peak_height/peak_pos if peak_pos > 0 else 1.0
        
        # Voltage limits
        if self.mca_id in [self.EMORPHO, self.PMT1K, self.PMT2K, self.PMT3K]: # PMT-based MCA
            min_volt = 400
            max_volt = 1400
        else:  # SiPM-based MCA
            min_volt = 28
            max_volt = 40
   
        new_ov = cal_ov # Force voltage test to succeed
        
        new_dg = par["digital_gain"]
        
        if self.mca_id in [self.EMORPHO, self.PMT2K, self.SIPM2K, self.PMT3K, self.SIPM3K] and ha_run or self.mca_id in [self.PMT1K, self.SIPM1K]: # Adjust operating voltage
            new_ov = self.compute_new_ov(cal_ov, cal_ratio, inv_gain_exp) 
            
        if self.mca_id in [self.EMORPHO, self.PMT2K, self.SIPM2K, self.PMT3K, self.SIPM3K] and not ha_run: # We adjust the digital gain
            new_dg = par["digital_gain"] * cal_ratio
        
        if min_volt <= new_ov <= max_volt and cal_update:
            self.set_op(new_ov, new_dg)
            self.MCA_IO.submit_command(self.sn, self.commands["start_mca"])
            time.sleep(1.2)
            print("New OV:", new_ov)
        else:
            print("New OV not programmed:", new_ov)
        # Update the calibration message in the display
        if self.mca_id in [self.EMORPHO, self.PMT2K, self.SIPM2K, self.PMT3K, self.SIPM3K] and not ha_run:  # We have adjusted the digital gain
            self.msg_text.SetLabel("{}{:.2f}".format("New digital gain ", new_dg))
        else:  # We have adjusted the operating voltage
            self.msg_text.SetLabel("Previous peak: {:.2f}mV; New voltage: {:.2f}V".format(peak_pos, new_ov))
            
        self.refresh()
    
    def get_op(self):
        """
            Read programmed operating voltage and whether this is an amplitude measurement, 
            rather than an energy measurement.
            Also, read the digital gain, where applicable.
        """
        par={"ov": 0, "ha_run": 0, "digital_gain": 1.0}
        if self.mca_id in [0x6001, 0x103, 0x203]:
            fpga_ctrl = self.MCA_IO.submit_command(self.sn, {"name": "fpga_ctrl",  "dir": "read"})[self.sn]
            
        if self.mca_id in [0x101, 0x201, 0x102, 0x202, 0x103, 0x203]:
            arm_ctrl = self.MCA_IO.submit_command(self.sn, {"name": "arm_ctrl",  "dir": "read"})[self.sn]
   
        if self.mca_id == 0x6001:
            par["ov"] = fpga_ctrl["user"]["high_voltage"]
            par["ha_run"] = fpga_ctrl["fields"]["ha_run"]
            
        elif self.mca_id in [0x103, 0x203]:
            par["ha_run"] = fpga_ctrl["fields"]["ha_mode"]
            
        if self.mca_id in [0x102, 0x202]:
            par["ha_run"] = arm_ctrl["user"]["amplitude"]
       
        if self.mca_id in [0x101, 0x201, 0x102, 0x202, 0x103, 0x203]:
            par["ov"] = arm_ctrl["fields"]["cal_ov"]
                        
        if self.mca_id in [0x6001, 0x103, 0x203]:
            par["digital_gain"] = fpga_ctrl["user"]["digital_gain"]
        elif self.mca_id in [0x102, 0x202]:
            par["digital_gain"] = arm_ctrl["fields"]["cal_dg"]    
            
        return par
    
    def set_op(self, ov, dg): # Reprogram operating voltage and digital gain
        # Program a new operating voltage into the device
        if self.mca_id == 0x6001:
            self.MCA_IO.submit_command(self.sn, {"name": "fpga_ctrl",  "dir": "rmw", "data":{"user": {"high_voltage": ov, "digital_gain": dg}} })
       
        elif self.mca_id in [0x103, 0x203]:
            self.MCA_IO.submit_command(self.sn, {"name": "arm_ctrl",  "dir": "rmw", "data":{"fields": {"cal_ov": ov}}})
            self.MCA_IO.submit_command(self.sn, {"name": "fpga_ctrl",  "dir": "rmw", "data":{"user": {"digital_gain": dg}} })
            
        elif self.mca_id in [0x101, 0x201]:
            self.MCA_IO.submit_command(self.sn, {"name": "arm_ctrl",  "dir": "rmw", "data":{"fields": {"cal_ov": ov}}})
            
        elif self.mca_id in [0x102, 0x202]:
            self.MCA_IO.submit_command(self.sn, {"name": "arm_ctrl",  "dir": "rmw", "data":{"fields": {"cal_ov": ov, "cal_dg": dg}}})
            print("updated OV", ov)
    
    def compute_new_ov(self, ov_old, ratio=1.0, exp=1.0/5.6):  # ratio>1 => ov_new > ov_old
        if self.mca_id in [0x6001, 0x101, 0x102, 0x103]:  # PMT-based
            ov_new = ov_old * (ratio**exp)
        else:
            Vbr = {0x201: 30.0, 0x202: 28.6, 0x203: 28.6}[self.mca_id]
            dov = (Vbr - ov_old)*(1-ratio)
            ov_new = ov_old + dov*0.5  # 0.5 is a relaxation parameter to improve convergence.
            #ov_new = Vbr + ratio*(ov_old-Vbr)

        return ov_new

    
    def init_line_plots(self, ctrl):
        
        self.lp_dict = {}

        self.plots = []  # line plots where we update the data with every refresh or fit
        for name, color in zip(self.lp_names, self.lp_colors):
            self.lp_dict[name] = self.axes.plot([], [])[0]
            ctrl['line_ctrl']["color"] = color
            plt.setp(self.lp_dict[name], **ctrl['line_ctrl'])
            
        if ctrl['axis_ctrl']["xlim"] == []:
            ctrl['axis_ctrl']["xlim"] = None
        if ctrl['axis_ctrl']["ylim"] == []:
            ctrl['axis_ctrl']["ylim"] = None

        self.axes.set_xlabel(ctrl['labels']['xlabel'], **ctrl['labels']['xlabel_ctrl'])
        self.axes.set_ylabel(ctrl['labels']['ylabel'], **ctrl['labels']['ylabel_ctrl'])
        self.axes.set_title(ctrl['labels']['title'], **ctrl['labels']['title_ctrl'])
        self.axes.grid(**ctrl['grid_ctrl'])
        self.axes.set(**ctrl['axis_ctrl'])
        
        if 0:
            bbox_args = dict(boxstyle="round", pad=0.5, ec=colors[0], fc=(0.9, 0.9, 0.9, 0.9), linewidth=2)  # fill, bounds(l,b,w,h) are ignored
            comment = "Beta"  # Empty string nixes the display 
            self.axes.annotate(comment, fontsize=10,
                        xycoords='axes fraction', xy=(0.65, 0.90), ha="left", va="bottom", bbox=bbox_args)
            
    def smooth(self):
        nsm = int(self.disp_ctrl["smooth"]["value"])
        self.histo = histo_analysis.smooth(self.histo, nsm)
        y_data = [h*self.histo_norm for h in self.histo]       
        x_data = [n*self.kev_bin for n in range(len(self.histo))]
        
        self.lp_dict["histo"].set_xdata(x_data)
        self.lp_dict["histo"].set_ydata(y_data)

        self.canvas.draw()
   
def main(dev_sn = '', dev_ind = 0):             
    app = wx.App() 
    panel = HistogramWindow(None,  'Histogram ' + dev_sn, dev_ind)
    panel.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    main()
    
    
"""
Notes:

https://wxpython.org/Phoenix/docs/html/sizers_overview.html#sizers-overview

"""
