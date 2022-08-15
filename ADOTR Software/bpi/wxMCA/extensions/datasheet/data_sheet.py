import math
import random
import matplotlib
import matplotlib.pyplot as plt
import random
import json
import histogram_fit

class DataSheet():
    def __init__(self, setup):
        self.setup = setup
        self.par = {}
        for item in setup["display"]:
            try:
                val = float(item["value"])  # interpret as a number
            except:
                val = item["value"]  # accept as a string
            self.par[item["name"]] = val
        
        # Sanitize user inpu:
        
        # Remove any leading/trailing white space from file and folder names
        path_keys = ["Template", "Data_File", "Data_Sheets"]
        for key in path_keys:
            self.par[key] = self.par[key].strip()
        
        # Users tend to not include the trailing '/' in the data sheets directory; so let's add it    
        if not self.par["Data_Sheets"].endswith("/"):
            self.par["Data_Sheets"] = self.par["Data_Sheets"]+"/"
                
        self.histogram = []
        self.settings = {}
        self.show_graph = True  # Set to False to avoid the pop-up graph; eg for batch processing
    
    def get_histo(self):
        """
            Read line number index (count starts at 1) and extract histogram
            index = -1 means last line in file
            Return histogram and all available settings information, such as voltage, DSP settings, etc.
        """
        with open(self.par["Data_File"], 'r') as fin:
            index = int(self.par["index"])
            if index > 0:
                for n in range(index):
                    line = fin.readline()
            else:  # get index's line from the end of the file
                num_lines = 0  # Find number of lines
                while True:
                    line = fin.readline()
                    if(len(line)==0):
                        break
                    num_lines += 1
                idx = num_lines + int(index)  # find absolute line index
                #print(num_lines, index)
                fin.seek(0)  # rewind
                for n in range(idx+1):
                    line = fin.readline()    
        #print(line)
        dd = json.loads(line)
        mca_id_str = dd["mca_id_str"]
        if mca_id_str in ["0x6001", "0x203", "0x103"]: 
            self.histogram = dd["histo"]["registers"]
        elif mca_id_str in ["0x201", "0x101"]: 
            self.histogram = dd["histo"]["fields"]["histogram"]
    
        # Retrieve settings data,depending on MCA type
        # Note that it is OK if the settings dictionary has keys that do not appear in the datasheet template.
        # We just go through the 5 product types explicitly, even though there are some similarities.
        mca_names = {
            "0x6001": "emorpho", 
            "0x101": "pmt1k", 
            "0x103": "pmt3k", 
            "0x201": "sipm1k", 
            "0x203": "sipm3k"
        }
        
        if mca_id_str == "0x6001":
            self.mca_data = {
                "SERIAL_NUMBER": dd["serial_number"],
                "SHORT_SN": dd["short_sn"],
                "MCA_ID_STR": dd["mca_id_str"],
                "HIGH_VOLTAGE": "{:.3f}V".format(dd["fpga_ctrl"]["user"]["high_voltage"]),
                "TEMPERATURE": "{:.2f}&deg;C".format(dd["fpga_status"]["user"]["temperature"]),
                "ADC_SPEED": "{:.0f}MHz".format(dd["fpga_status"]["user"]["adc_sr"]/1e6),
                "BUILD_NO": dd["fpga_status"]["fields"]["build"],
                "CUSTOM_NO": dd["fpga_status"]["fields"]["custom"],
                "TRIGGER_THRESHOLD": "{:.0f}mV".format(dd["fpga_ctrl"]["user"]["pulse_threshold"]*1000),
                "ELECTRONIC_GAIN": "{:.1f}&Omega;".format(dd["fpga_status"]["user"]["impedance"]),
                "INTEGRATION_TIME": "{:.2f}&micro;s".format(dd["fpga_ctrl"]["user"]["integration_time"]*1.0e6),
                "DIGITAL_GAIN": "{:.2f}".format(dd["fpga_ctrl"]["user"]["digital_gain"]),
                "TEMPERATURE": "{:.2f}&deg;C".format(dd["fpga_status"]["user"]["temperature"]),
                "LED_VALUE": "{:.0f}".format(dd["fpga_status"]["fields"]["roi_avg"])
            }
            if self.mca_data["CUSTOM_NO"] not in [4100]:
                self.mca_data["LED_VALUE"] = 0
        
        if mca_id_str in ["0x103", "0x203"]:
            self.mca_data = {
                "SERIAL_NUMBER": dd["serial_number"][0:8],
                "SHORT_SN": dd["short_sn"],
                "MCA_ID_STR": dd["mca_id_str"],
                "HIGH_VOLTAGE": "{:.3f}V".format(dd["arm_status"]["fields"]["voltage_target"]),
                "TEMPERATURE": "{:.2f}&deg;C".format(dd["arm_status"]["fields"]["x_temperature"]),
                "ADC_SPEED": "{:.0f}MHz".format(dd["fpga_status"]["user"]["adc_sr"]/1e6),
                "BUILD_NO": "{}/{}".format(dd["arm_version"]["fields"]["arm_build"], dd["fpga_status"]["fields"]["build"]),
                "CUSTOM_NO": "{}/{}".format(dd["arm_version"]["fields"]["arm_custom_0"], dd["fpga_status"]["fields"]["custom"]),
                "TRIGGER_THRESHOLD": "{:.0f}mV".format(dd["fpga_ctrl"]["user"]["pulse_threshold"]*1000),
                "ELECTRONIC_GAIN": "{:.1f}&Omega;".format(dd["fpga_status"]["user"]["impedance"]),
                "INTEGRATION_TIME": "{:.2f}&micro;s".format(dd["fpga_ctrl"]["user"]["integration_time"]*1.0e6),
                "DIGITAL_GAIN": "{:.2f}".format(dd["fpga_ctrl"]["user"]["digital_gain"]),  
            }
        
        if mca_id_str in ["0x101", "0x201"]:
            self.mca_data = {
                "SERIAL_NUMBER": dd["serial_number"][0:8],  # dd["serial_number"],
                "SHORT_SN": dd["short_sn"],
                "MCA_ID_STR": dd["mca_id_str"],
                "HIGH_VOLTAGE": "{:.3f}V".format(dd["arm_status"]["fields"]["voltage_target"]),
                "TEMPERATURE": "{:.2f}&deg;C".format(dd["arm_status"]["fields"]["x_temperature"]),
                "BUILD_NO": dd["arm_version"]["fields"]["arm_build"],
                "CUSTOM_NO": "{}/{}".format(dd["arm_version"]["fields"]["arm_custom_0"], dd["arm_version"]["fields"]["arm_custom_1"]),
                "TRIGGER_THRESHOLD": "{:.0f}mV".format(dd["arm_ctrl"]["fields"]["trigger_threshold"]*1000)
            }
        

    def mca_plot_fit(self):
        self.get_histo()
    
        serial_number = self.mca_data["SERIAL_NUMBER"]
        SN = self.mca_data["SERIAL_NUMBER"]

        lh = len(self.histogram)
        # off = 200
        # hmax = max(histo[off:])
        # idx_max = off + histo[off:].index(hmax)
    
        imin = int(self.par["fit_min"]/self.par["keV_bin"]+0.5)  
        imax = int(self.par["fit_max"]/self.par["keV_bin"]+0.5)
        results = histogram_fit.do_gauss_fit(self.histogram[imin:imax], bck_model=2, fwhm=50/self.par["keV_bin"])
        xmax, ymax, fwhm, counts, bck, yl, yr, net_histo, fit_histo = results
            
        peak_pos = xmax + float(imin)
        dE_E = fwhm/peak_pos * 100
        print("Peak: {:.2f}, fwhm: {:.2f}%".format(peak_pos, dE_E))
    
        # Plot it
        x_data = [n*self.par["keV_bin"] for n in range(lh)]
        fig, ax = plt.subplots(num=1, clear=True)
        if False:  
            # Bar graph
            lp1 = ax.bar(x_data, self.histogram, width=1)  # 
            plt.setp(lp1, alpha=0.5)
        else:
            # Line graph
            lp1 = ax.plot(x_data, self.histogram)
            ax.fill_between(x_data, self.histogram, 0, alpha=0.5, color="PowderBlue")
        ax.set_xlim(left=self.par["display_min"], right=self.par["display_max"])
        ax.set_ylim(bottom=0)
    
        lp2 = ax.plot(x_data[imin: imax], fit_histo, '-')    
        plt.setp(lp2, color="red")
    
        ax.set(ylabel="Counts / Bin", xlabel="Energy, bin")
        ax.set(title="Energy histogram, {}, fwhm={:.2f}%".format(SN, dE_E))
    
        bbox_args = dict(boxstyle="round", pad=0.5, ec="#FF4500", fc=(0.9, 0.9, 0.9, 0.8), linewidth=2)  # fill, bounds(l,b,w,h) are ignored
        ax.annotate('Cs-137\nfwhm={:.2f}%'.format(dE_E), fontsize=10,
                    xycoords='axes fraction', xy=(0.75, 0.7), ha="left", va="bottom", bbox=bbox_args)
    
        for item in self.setup["display"]:  # And replace the KEY_WORDS
            if item["name"] == "MCA_TYPE":
                mca_type = item["value"]
                    
        fig.savefig("./data_sheets/mca_{}_{}.png".format(mca_type, SN), dpi=300)
        fig.savefig("./data_sheets/mca_{}_{}.svg".format(mca_type, SN))
        
        self.mca_data["HISTOGRAM_IMAGE"] = "./mca_{}_{}.png".format(mca_type, SN)
    
        if self.show_graph:
            plt.show()
    
    def make_data_sheet(self):
        """
            Read template_data.json file to find the correct html template and the test setup data.
            Then replace all the KEY_WORDS with the correct values and write the data_sheet file.
            Note that mca_plot_fit() needs to run first to make the graphs used in the data sheet.
            
        """
        SN = self.mca_data["SERIAL_NUMBER"]
        mca_id_str = self.mca_data["MCA_ID_STR"]
        
        with open(self.par["Template"], "r") as fin:  # Load the html template
            ds_template = fin.read()
    
        for item in self.setup["display"]:  # And replace the KEY_WORDS
            if item["is_key"] == "yes":
                key = item["name"]
                ds_template = ds_template.replace(key, str(item["value"]))
                if key == "MCA_TYPE":
                    mca_type = item["value"]
                
        for key in self.mca_data:
            ds_template = ds_template.replace(key, str(self.mca_data[key]))

        with open(self.par["Data_Sheets"]+"ds_{}_{}.html".format(mca_type, SN), 'w') as fout:
            fout.write(ds_template)
        

    def mca_display(self, serial_number, index=-1):
        """
        Open a multi-line histogram file, extract the last histogram, and display.
        """
        self.get_histo(self.input_data_file, index)
        lh = len(self.histogram)
        xdat = [float(n) for n in range(lh)]
    
        fig, ax = plt.subplots(num=1, clear=True)
        if False:  
            # Bar graph
            lp1 = ax.bar(xdat, self.histogram, width=1)  # 
            plt.setp(lp1, alpha=0.5)
        else:
            # Line graph
            lp1 = ax.plot(xdat, self.histogram)
            ax.fill_between(range(lh), self.histogram, 0, alpha=0.5, color="PowderBlue")
            ax.set_xlim(left=0)
            ax.set_ylim(bottom=0)
    
        ax.set(ylabel="Counts / Bin", xlabel="Energy, bin")
        ax.set(title="Energy histogram, {}".format(serial_number))
    
        plt.show()




#mca_display(par['file_name'], par['serial_number'])   


if __name__ == "__main__":
    mca_plot_fit(**par)
