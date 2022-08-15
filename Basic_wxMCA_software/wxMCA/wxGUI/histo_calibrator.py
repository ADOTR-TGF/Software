import time
import wx
import os
import json
import mca_io
import histo_analysis

class HistogramCalibrator(): 
    def __init__(self): 
        self.EMORPHO = 0x6001
        self.PMT1K = 0x101
        self.PMT3K = 0x103
        self.SIPM1K = 0x201
        self.SIPM3K = 0x203
        
        # Communication with the MCA
        self.MCA_IO = mca_io.MCA_IO()  # For communication with the MDS
        
        #-- Here we use the first mca in the MCA_IO.mca dictionary
        self.sn = list(self.MCA_IO.mca)[0]
        self.MCA = self.MCA_IO.mca[self.sn]  
        
        self.mca_id = self.MCA["mca_id"]
        self.commands = self.MCA["commands"]
        
        self.disp_ctrl = self.MCA["display_controls"]["histogram"]["data"]
        
        self.printed = False
            
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
            short_sn = '_' + out_dict['short_sn'] + '.'
            
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
            short_sn = '_' + out_dict['arm_version']['user']['unique_sn'][:8]+ '.'
            
        elif self.MCA["mca_id"] in  [ 0x201, 0x101]:
            arm_version = self.MCA_IO.submit_command(sn, {"name": "arm_version",  "dir": "read"})[sn]
            arm_status = self.MCA_IO.submit_command(sn, {"name": "arm_status",  "dir": "read"})[sn]
            arm_ctrl = self.MCA_IO.submit_command(sn, {"name": "arm_ctrl",  "dir": "read"})[sn]
            histo = self.MCA_IO.submit_command(sn, {"name": "arm_histogram",  "dir": "read", "num_items": 1024})[sn]
            out_dict = {"comment": comment, "serial_number": sn, "short_sn": arm_version["fields"]["short_sn"], 
                        "mca_id_str": self.MCA["mca_id_str"], "arm_version": arm_version, 
                        "arm_status": arm_status, "arm_ctrl": arm_ctrl, "histo": histo}
            short_sn = '_' + out_dict['arm_version']['user']['unique_sn'][:8]+ '.'
        
        
        splt_out_file = out_file.strip('.').rsplit('/', 1)
        data_dir_path = splt_out_file[0]
        file_name = splt_out_file[1]
        file_name_record = short_sn.join(splt_out_file[1].split('.'))
        default_path = os.path.dirname(os.getcwd()) + data_dir_path
        
        if not self.printed:
            print("Output file name: ", default_path + '/' + file_name)
            self.printed = True
        with open(default_path + '/' + file_name, 'a+') as fout:
            fout.write(json.dumps(out_dict)+'\n')

            
    def refresh(self):
        
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
        cmd["num_items"] = int(self.disp_ctrl["num_bins"]["value"])
        self.histogram = self.MCA_IO.submit_command(self.sn, cmd)[self.sn]
        
        if self.mca_id in [0x6001, 0x103, 0x203]:
            self.histo = self.histogram["registers"]
        elif self.mca_id in [0x101, 0x201]:
            self.histo = self.histogram["fields"]["histogram"]
 
    
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
            if ha_mode == 1:
                self.kev_bin = 1.0
    
    def cal_mca(self):
        par = self.get_op()
        cal_ov = par["ov"]
        ha_run = par["ha_run"] != 0
        
        self.refresh()
        
        # Now recalibrate
        res = histo_analysis.fit_cs_peak(self.histo)  # Fit to tallest peak > 50 MCA bins
        peak_pos = res["x_max"]  # In MCA bins
        kev_bin = float(self.disp_ctrl["kev_bin"]["value"])
        cal_peak_height = float(self.disp_ctrl["cal_ph"]["value"])
        cal_peak_energy = float(self.disp_ctrl["cal_kev"]["value"])
        cal_update = float(self.disp_ctrl["cal_update"]["value"]) != 0
        inv_gain_exp = 1.0/float(self.disp_ctrl["gain_exp"]["value"])  # For use with PMT-based MCA when changing the voltage
        
        # Compute the correct ratio for the gain correction
        cal_ratio = cal_peak_energy/kev_bin/peak_pos if peak_pos > 0 else 1.0
        if self.mca_id in [self.EMORPHO, self.PMT3K, self.SIPM3K] and ha_run:
            cal_ratio = cal_peak_height/peak_pos if peak_pos > 0 else 1.0
        
        # Voltage limits
        if self.mca_id in [self.EMORPHO, self.PMT1K, self.PMT3K]: # PMT-based MCA
            min_volt = 400
            max_volt = 1400
        else:  # SiPM-based MCA
            min_volt = 28
            max_volt = 40
   
        new_ov = cal_ov # Force voltage test to succeed
        new_dg = par["digital_gain"]
        
        if self.mca_id in [self.EMORPHO, self.PMT3K, self.SIPM3K] and ha_run or self.mca_id in [self.PMT1K, self.SIPM1K]: # Adjust operating voltage
            new_ov = self.compute_new_ov(cal_ov, cal_ratio, inv_gain_exp)
            
        if self.mca_id in [self.EMORPHO, self.PMT3K, self.SIPM3K] and not ha_run: # We adjust the digital gain
            new_dg = par["digital_gain"] * cal_ratio
        
        # Apply the new operating voltage and new digital gain, as appropriate 
        if min_volt <= new_ov <= max_volt and cal_update:
            self.set_op(new_ov, new_dg)
 
    def record(self, dwell_time):
        """
            Run an acquisition for a dwell time and record histogram and settings
        """
        self.MCA_IO.submit_command(self.sn, self.commands["start_mca"])  # Start new histogram
        time.sleep(dwell_time)
        self.refresh()
        self.save_histogram()
           
    
    def get_op(self):
        """
            Read programmed operating voltage and whether this is an amplitude measurement, 
            rather than an energy measurement.
            Also, read the digital gain, where applicable.
        """
        par={"ov": 0, "ha_run": 0, "digital_gain": 1.0}
        if self.mca_id in [0x6001, 0x103, 0x203]:
            fpga_ctrl = self.MCA_IO.submit_command(self.sn, {"name": "fpga_ctrl",  "dir": "read"})[self.sn]
   
        if self.mca_id == 0x6001:
            par["ov"] = fpga_ctrl["user"]["high_voltage"]
            par["ha_run"] = fpga_ctrl["fields"]["ha_run"]
            
        if self.mca_id in [0x103, 0x203]:
            par["ha_run"] = fpga_ctrl["fields"]["ha_mode"]
       
        if self.mca_id in [0x101, 0x201, 0x103, 0x203]:
            arm_ctrl = self.MCA_IO.submit_command(self.sn, {"name": "arm_ctrl",  "dir": "read"})[self.sn]
            par["ov"] = arm_ctrl["fields"]["cal_ov"]
            
        if self.mca_id in [0x6001, 0x103, 0x203]:
            par["digital_gain"] = fpga_ctrl["user"]["digital_gain"]
            
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

    
    def compute_new_ov(self, ov_old, ratio=1.0, exp=1.0/5.6):  # ratio>1 => ov_new > ov_old
        if self.mca_id in [0x6001, 0x101, 0x103]:  # PMT-based
            ov_new = ov_old * ratio**exp
        else:
            Vbr = {0x201: 30.0, 0x203: 28.6}[self.mca_id]
            dov = (Vbr - ov_old)*(1-ratio)
            ov_new = ov_old + dov*0.5  # 0.5 is a relaxation parameter to improve convergence.
            #ov_new = Vbr + ratio*(ov_old-Vbr)

        return ov_new

            
    def smooth(self):
        nsm = int(self.disp_ctrl["smooth"]["value"])
        self.histo = histo_analysis.smooth(self.histo, nsm)
        y_data = [h*self.histo_norm for h in self.histo]       
        x_data = [n*self.kev_bin for n in range(len(self.histo))]
        
        self.lp_dict["histo"].set_xdata(x_data)
        self.lp_dict["histo"].set_ydata(y_data)

        self.canvas.draw()
   
def main():
    """
        The main()function illustrates how to use the HistogramCalibrator class.
    """
    Cal = HistogramCalibrator()
    par = {
        "wait_time": 60,  # Time to wait before performing a new calibration
        "dwell_time": 60,  # Time to acquire fresh data for a calibration step
    }
    
    if Cal.mca_id in [Cal.PMT1K, Cal.SIPM1K]:
        while True:       
            time.sleep(par["wait_time"])
            Cal.MCA_IO.submit_command(Cal.sn, Cal.commands["start_mca"])  # Start new histogram
            time.sleep(par["dwell_time"])
            Cal.cal_mca()
            # Record results
            Cal.MCA_IO.submit_command(Cal.sn, Cal.commands["start_mca"])  # Start new histogram
            time.sleep(par["dwell_time"])
            Cal.refresh()
            Cal.save_histogram()
            
    if Cal.mca_id in [Cal.EMORPHO, Cal.PMT3K, Cal.SIPM3K]:
        if Cal.mca_id == Cal.EMORPHO:
            cmd_histo_amplitude = {"name": "fpga_ctrl",  "dir": "rmw", "data": {"fields": {"ha_run": 1}, "user":{}}}
            cmd_histo_energy = {"name": "fpga_ctrl",  "dir": "rmw", "data": {"fields": {"ha_run": 0}, "user":{}}}
        if Cal.mca_id in [Cal.PMT3K, Cal.SIPM3K]:
            cmd_histo_amplitude = {"name": "fpga_ctrl",  "dir": "rmw", "data": {"fields": {"ha_mode": 1}, "user":{}}}
            cmd_histo_energy = {"name": "fpga_ctrl",  "dir": "rmw", "data": {"fields": {"ha_mode": 0}, "user":{}}}
        while True:
            # First adjust operating voltage to keep the pulse height constant
            time.sleep(par["wait_time"])
            Cal.MCA_IO.submit_command(Cal.sn, cmd_histo_amplitude)  # Prepare for amplitude measurement
            Cal.MCA_IO.submit_command(Cal.sn, Cal.commands["start_mca"])  # Start new histogram
            time.sleep(par["dwell_time"])
            Cal.cal_mca()
            # Record results
            Cal.MCA_IO.submit_command(Cal.sn, Cal.commands["start_mca"])  # Start new histogram
            time.sleep(par["dwell_time"])
            Cal.refresh()
            Cal.save_histogram()
            
            # Now adjust digital gain to keep the keV/MCA_bin calibration constant
            time.sleep(par["wait_time"])
            Cal.MCA_IO.submit_command(Cal.sn, cmd_histo_energy)  # Prepare for amplitude measurement
            Cal.MCA_IO.submit_command(Cal.sn, Cal.commands["start_mca"])  # Start new histogram
            time.sleep(par["dwell_time"])
            Cal.cal_mca()
            # Record results
            Cal.MCA_IO.submit_command(Cal.sn, Cal.commands["start_mca"])  # Start new histogram
            time.sleep(par["dwell_time"])
            Cal.refresh()
            Cal.save_histogram()
        
        
        
    
if __name__ == '__main__':
    main()
    
    
