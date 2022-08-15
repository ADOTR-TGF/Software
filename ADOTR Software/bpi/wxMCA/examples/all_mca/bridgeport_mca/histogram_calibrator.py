import time
import json
import bridgeport_mca.mca_portal
import bridgeport_mca.histogram_analysis

class HistogramCalibrator():
    def __init__(self, idx, op_ctrl):
        """
            idx: logic unit number of the selected MCA; counting starts at 0
            The MCA_PORTAL reports a sorted list MCA serial numbers
        """
        self.EMORPHO = 0x6001
        self.PMT1K = 0x101
        self.PMT2K = 0x102
        self.PMT3K = 0x103
        self.SIPM1K = 0x201
        self.SIPM2K = 0x202
        self.SIPM3K = 0x203

        # Calibrator controls
        self.op_ctrl = dict(op_ctrl)

        # Communication with the MCA
        self.MCA_IO = bridgeport_mca.mca_portal.MCA_PORTAL()  # For communication with the MDS
        print(self.MCA_IO.sn_list, idx)

        # sn_list is a sorted list of serial numbers.
        self.sn = self.MCA_IO.sn_list[idx]
        self.MCA = self.MCA_IO.mca[self.sn]
        self.mca_id = self.MCA["mca_id"]
        self.commands = self.MCA["commands"]

        self.printed_histo = False
        self.printed_pulse = False

    def save_histogram(self, out_file=None, comment="", mode=""):
        # In io_dict we name all the quantities to be saved
        if self.MCA["mca_id"] == 0x6001:
            io_dict = {"fpga_ctrl": "read_fpga_ctrl", "fpga_status": "fpga_results", "rates": "rates", "histogram": "histogram"}

        elif self.MCA["mca_id"] in  [ 0x203, 0x103]:
            io_dict = {"arm_version": "arm_version", "arm_status": "arm_status", "arm_ctrl": "read_arm_ctrl",
                       "fpga_status": "fpga_results", "fpga_ctrl": "read_fpga_ctrl",
                       "rates": "rates", "histogram": "histogram"}

        elif self.MCA["mca_id"] in  [ 0x201, 0x101, 0x202, 0x102]:
            io_dict = {"arm_version": "arm_version", "arm_status": "arm_status",
                       "arm_ctrl": "read_arm_ctrl", "histogram": "histogram"}

        out_dict = {"comment": comment, "serial_number": self.sn, "short_sn": self.MCA["short_sn"],
                    "mca_id_str": self.MCA["mca_id_str"]}
        for key in io_dict:  # Read al data to be saved and assemble the output dictionary
            out_dict[key] = self.MCA_IO.submit_command(self.sn, self.commands[io_dict[key]])[self.sn]

        if not out_file:
            data_path = self.op_ctrl["data_root"].rstrip("/")
            if mode:
                mode = "_{}".format(mode)
            file_name = "histograms_{}{}.json".format(out_dict["short_sn"],mode)
            out_file = "{}/{}".format(data_path, file_name)

        if not self.printed_histo:
            print("Output file name: ", out_file)
            self.printed_histo = True
        with open(out_file, 'a') as fout:
            fout.write("{}\n".format(json.dumps(out_dict)))


    def save_pulses(self, num_pulses, out_file=None, comment=""):
        """
            Acquire num_pulses pulses and save to file, together with supporting information
            that contains at least the temperature.
        """
        if self.MCA["mca_id"] in [ 0x201, 0x101]:  # These have no pulse capture capability
            return

        if self.MCA["mca_id"] == 0x6001:
            io_dict = {"fpga_results": "fpga_results", "pulse": "pulse"}

        elif self.MCA["mca_id"] in  [ 0x202, 0x102, 0x203, 0x103]:
            io_dict = io_dict = {"arm_status": "arm_status", "pulse": "pulse"}

        out_dict = {"comment": comment, "serial_number": sn, "short_sn": self.MCA["short_sn"],
                    "mca_id_str": self.MCA["mca_id_str"]}
        for key in io_dict:
            out_dict[key] = self.MCA.submit_command(self.sn, self.commands[io_dict[key]])[self.sn]

        # acquire requested number of pulses
        pulses = []
        for n in range(num_pulses):
            self.MCA_IO.submit_command(self.sn, self.commands["start_pulse"])
            time.sleep(0.02)  # We expect a calibration source to make >1kcps => no need to wait long.
            pulse = self.MCA_IO.submit_command(self.sn, self.commands["pulse"])[self.sn]
            pulses += [pulse["fields"]["trace"]]

        out_dict["pulses"] = pulses
        if not out_file:
            data_path = self.op_ctrl["data_root"].rstrip("/")
            file_name = "pulses_{}.json".format(out_dict["short_sn"])
            out_file = "{}/{}".format(data_path, file_name)

        if not self.printed_pulse:
            print("Output file name: ", out_file)
            self.printed_pulse = True
        with open(out_file, 'a') as fout:
            fout.write("{}\n".format(json.dumps(out_dict)))


    def refresh(self):

        # Read histogram
        self.histogram = self.MCA_IO.submit_command(self.sn, self.commands["histogram"])[self.sn]
        if self.mca_id in [0x6001, 0x103, 0x203]:
            self.histo = self.histogram["registers"]
        elif self.mca_id in [0x101, 0x201, 0x102, 0x202]:
            self.histo = self.histogram["fields"]["histogram"]


    def cal_mca(self):
        par = self.get_op()
        cal_ov = par["ov"]
        ha_mode = par["ha_mode"] != 0

        self.refresh()

        # Now recalibrate
        res = bridgeport_mca.histogram_analysis.fit_cs_peak(self.histo)  # Fit to tallest peak > 50 MCA bins
        peak_pos = res["x_max"]  # In MCA bins
        if self.mca_id == self.EMORPHO:
            kev_bin = float(self.op_ctrl["emorpho_keV_bin"])
        elif self.mca_id == self.PMT1K:
            kev_bin = float(self.op_ctrl["pmt1k_keV_bin"])
        elif self.mca_id == self.PMT2K:
            kev_bin = float(self.op_ctrl["pmt2k_keV_bin"])
        elif self.mca_id == self.PMT3K:
            kev_bin = float(self.op_ctrl["pmt3k_keV_bin"])

        cal_peak_height = float(self.op_ctrl["ph"])
        cal_peak_energy = float(self.op_ctrl["keV"])
        cal_update = float(self.op_ctrl["update"]) != 0
        inv_gain_exp = 1.0/float(self.op_ctrl["gain_exp"])  # For use with PMT-based MCA when changing the voltage

        # Compute the correct ratio for the gain correction
        cal_ratio = cal_peak_energy/kev_bin/peak_pos if peak_pos > 0 else 1.0
        if self.mca_id in [self.EMORPHO, self.PMT3K, self.SIPM3K] and ha_mode:
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

        if self.mca_id in [self.EMORPHO, self.PMT3K, self.SIPM3K] and ha_mode or self.mca_id in [self.PMT1K, self.SIPM1K]: # Adjust operating voltage
            new_ov = self.compute_new_ov(cal_ov, cal_ratio, inv_gain_exp)

        if self.mca_id in [self.EMORPHO, self.PMT3K, self.SIPM3K] and not ha_mode: # We adjust the digital gain
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

    def get_temp_led(self):
        """
            Read temperature from all MCA.
            Read led_value for those MCA which may have an LED.
        """
        par = {}
        if self.mca_id in [0x6001]:
            res = self.MCA_IO.submit_command(self.sn, self.commands["fpga_results"])[self.sn]
            par["temperature"] = res["user"]["temperature"]
        if self.mca_id in [0x6001, 0x103]:
            par["led_value"] = res["fields"]["rr_10"]

        if self.mca_id in [0x101, 0x201, 0x102, 0x202, 0x103, 0x203]:
            res = self.MCA_IO.submit_command(self.sn, self.commands["read_arm_status"])[self.sn]
            par["temperature"] = res["fields"]["avg_temperature"]
        if self.mca_id in [0x101, 0x102]:
            par["led_value"] = res["fields"]["led_val"]

        return par


    def get_op(self):
        """
            Read programmed operating voltage and whether this is an amplitude measurement,
            rather than an energy measurement.
            Also, read the digital gain, where applicable.
        """
        par = {"ov": 0, "ha_mode": 0, "digital_gain": 1.0}
        if self.mca_id in [0x6001, 0x103, 0x203]:
            fpga_ctrl = self.MCA_IO.submit_command(self.sn, self.commands["read_fpga_ctrl"])[self.sn]

        if self.mca_id == 0x6001:
            par["ov"] = fpga_ctrl["user"]["high_voltage"]
            par["ha_mode"] = fpga_ctrl["fields"]["ha_run"]

        if self.mca_id in [0x103, 0x203]:
            par["ha_mode"] = fpga_ctrl["fields"]["ha_mode"]

        if self.mca_id in [0x101, 0x201, 0x102, 0x202, 0x103, 0x203]:
            arm_ctrl = self.MCA_IO.submit_command(self.sn, self.commands["read_arm_ctrl"])[self.sn]
            par["ov"] = arm_ctrl["fields"]["cal_ov"]

        if self.mca_id in [0x6001, 0x103, 0x203]:
            par["digital_gain"] = fpga_ctrl["user"]["digital_gain"]

        if self.mca_id in [0x102, 0x202]:
            par["digital_gain"] = arm_ctrl["fields"]["digital_gain"]

        return par

    def set_op(self, ov, dg): # Reprogram operating voltage and digital gain
        # Program a new operating voltage into the device
        if self.mca_id == 0x6001:
            self.MCA_IO.submit_command(self.sn, self.commands["write_fpga_ctrl"], {"user": {"high_voltage": ov, "digital_gain": dg}})

        if self.mca_id in [0x101, 0x201, 0x102, 0x202, 0x103, 0x203]:
            self.MCA_IO.submit_command(self.sn, self.commands["write_arm_ctrl"], {"fields": {"cal_ov": ov}})

        if self.mca_id in [0x103, 0x203]:
            self.MCA_IO.submit_command(self.sn, self.commands["write_fpga_ctrl"], {"user": {"digital_gain": dg}})

        if self.mca_id in [0x102, 0x202]:
            self.MCA_IO.submit_command(self.sn, self.commands["write_arm_ctrl"], {"fields": {"digital_gain": dg}})


    def compute_new_ov(self, ov_old, ratio=1.0, exp=1.0/5.6):  # ratio>1 => ov_new > ov_old
        if self.mca_id in [0x6001, 0x101, 0x102, 0x103]:  # PMT-based
            ov_new = ov_old * ratio**exp
        else:  # SiPM-based
            Vbr = {0x201: 30.0, 0x203: 28.6}[self.mca_id]
            dov = (Vbr - ov_old)*(1-ratio)
            ov_new = ov_old + dov*0.5  # 0.5 is a relaxation parameter to improve convergence.
            #ov_new = Vbr + ratio*(ov_old-Vbr)

        return ov_new

    def calibrator_loop(self):
        """
            Perform calibrations over a temperature cycle for detector number idx (logic unit number)
            and for a given time (max_time in seconds)

            The calibrator_loop() function illustrates how to use the HistogramCalibrator class.
            It is a client to the MCA data server and operates one MCA. It works for any
            eMorpho, MCA-1000, MCA-2000, and MCA-3000.
            For eMorpho, MCA-2000, and MCA-3000, it is possible to also record pulses during
            the temperature cycle.

        """
        pulse_skipper = self.op_ctrl["pulse_skips"]
        # Can the MCA measure amplitude and energy separately?
        amplitude_energy = self.mca_id in [self.EMORPHO, self.PMT2K, self.SIPM2K, self.PMT3K, self.SIPM3K]
        energy_only = self.mca_id in [self.PMT1K, self.SIPM1K]
        pulse_capture = self.mca_id in [self.EMORPHO, self.PMT2K, self.SIPM2K, self.PMT3K, self.SIPM3K]
        """
            Step 1) Acquire pulse height histogram to adjust operating voltage.
            Step 2) Acquire energy histogram to adjust digital gain.
        """
        if self.mca_id in [self.EMORPHO, self.PMT3K, self.SIPM3K]:
            cmd_histo_mode = dict(self.commands["write_fpga_ctrl"])
        if self.mca_id in [self.PMT2K, self.SIPM2K]:
            cmd_histo_mode = dict(self.commands["write_arm_ctrl"])

        mode_energy = "energy"
        mode_amplitude = "amplitude"
        if self.mca_id == self.EMORPHO:
            data_amplitude = {"fields": {"ha_run": 1}}
            data_energy = {"fields": {"ha_run": 0}}
        if self.mca_id in [self.PMT2K, self.SIPM2K]:
            data_amplitude = {"user": {"ha_mode": 1}}
            data_energy = {"user": {"ha_mode": 0}}
        if self.mca_id in [self.PMT3K, self.SIPM3K]:
            data_amplitude = {"fields": {"ha_mode": 1}}
            data_energy = {"fields": {"ha_mode": 0}}
        if self.mca_id in [self.PMT1K, self.SIPM1K]:
            data_amplitude = {}
            data_energy = {}
            mode_energy = "energy"
            mode_amplitude = "energy"

        then = time.time()
        time.sleep(0.1)
        while time.time()-then < self.op_ctrl["max_time"]:
            data = [data_amplitude, data_energy]
            mode = [mode_amplitude, mode_energy]
            for dat, mod in zip(data, mode):
                if amplitude_energy:
                    self.MCA_IO.submit_command(self.sn, cmd_histo_mode, dat)  # Prepare for measurement
                self.MCA_IO.submit_command(self.sn, self.commands["start_mca"])  # Start new histogram
                time.sleep(self.op_ctrl["dwell_time"])
                self.cal_mca()
                # Record results
                self.MCA_IO.submit_command(self.sn, self.commands["start_mca"])  # Start new histogram
                time.sleep(self.op_ctrl["dwell_time"])
                self.refresh()
                self.save_histogram(mode=mod)


            # Record pulses
            pulse_skipper += 1
            if pulse_capture and self.op_ctrl["num_pulses"]>0 and pulse_skipper >= self.op_ctrl["pulse_skips"]:
                pulse_skipper = 0
                self.save_pulses(self.op_ctrl["num_pulses"])

            time.sleep(self.op_ctrl["wait_time"])


    def lut_get_correction(self, lut, quantity, cal_temperature, temperature, mode="ratio"):
        tmin = lut["tmin"]
        dt = lut["dt"]  # temperature step size
        nm1 = lut["len"]-1
        data = lut[quantity]  # List of parameter values
        x = (temperature - tmin)/dt
        if x < 0:
            correction_t = lut[quantity][0]
        elif x > nm1:
            correction_t = lut[quantity][nm1]
        else:
            x0 = int(x)
            delta_t = temperature - (tmin + dt*x0)
            d0 = data[x0]
            d1 = data[x0+1]
            correction_t = ( d0 + (d1 - d0)*delta_t/dt)

        x = (cal_temperature - tmin)/dt
        if x < 0:
            correction_cal = lut[quantity][0]
        elif x > nm1:
            correction_cal = lut[quantity][nm1]
        else:
            x0 = int(x)
            delta_t = cal_temperature - (tmin + dt*x0)
            d0 = data[x0]
            d1 = data[x0+1]
            correction_cal = ( d0 + (d1 - d0)*delta_t/dt)

        if mode == "ratio":
            return correction_t/correction_cal
        else:
            return correction_t - correction_cal

    def stabilizer_loop(self):
        """
            Read the MCA temperature and current operating parameters.
            Depending on the mode "ov_lut" or "led_lut" the function then
            compute updated high voltage, digital gain, and save back to the MCA.

            The stabilizer is necessary only for the eMorpho MCA of the usbBase
            and oemBase type devices.  All others have an embedded ARM processor
            that can perform the gain-stabilization.

            mode="ov":  Use temperature look up to compute new operating voltage
            and new digital_gain, where applicable.
            mode="led":  Use temperature look up and a measure of the LED
            brightness to compute the new operating voltage, and a new
            digital_gain, where applicable.
            par["mode"]: Gain stabilization mode
            par["dwell_time"]: Time between high voltage updates
            par["cal_ov"]: Calibration voltage
            par["cal_dg"]: Calibration digital_gain
            par["cal_led"]: LED response at calibration time
            par["cal_temperature"]: Calibration temperature
            par["lut"]: Lookup table for operating voltage, digital_gain and
            expected LED brightness vs temperature
            par["gain_exp"]: PMT gain exponent; 8-dynode PMT=>5.6, 10-dynode PMT=>7.5            
        """
        self.led_old = 0
        par = self.op_ctrl
        if self.mca_id != self.EMORPHO:
            return
        while True:
            op_par = self.get_op()
            temp_led = self.get_temp_led()
            led_value = temp_led["led_value"]
            temperature = temp_led["temperature"]
            lut = par["lut"]
                
            self.led_old = led_value
            dg = par["cal_dg"]*self.lut_get_correction(lut, "dg", par["cal_temperature"], temperature)
            if par["mode"] == "ov":
                ov = op_par["ov"]*\
                self.lut_get_correction(lut, "ov", par["cal_temperature"], temperature)

            if par["mode"] == "led":
                led_cal = \
                    self.lut_get_correction(lut, "led", par["cal_temperature"], temperature)

                led_ratio = led_cal * par["cal_led"] / led_value
                ov = op_par["ov"] * led_ratio **(0.25/par["gain_exp"])
                

            print(led_value, dg, ov, par["cal_led"])
            self.set_op(ov, dg)
            time.sleep(par["dwell_time"])
