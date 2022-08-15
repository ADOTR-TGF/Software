import time
import json
import bridgeport_mca.mca_portal

class MCA_DAQ():
    def __init__(self, MCA_IO=None):
        """
            MCA_IO is an MCA_PORTAL object for communication with the MDS
        """
        self.EMORPHO = 0x6001
        self.PMT1K = 0x101
        self.PMT2K = 0x102
        self.PMT3K = 0x103
        self.SIPM1K = 0x201
        self.SIPM2K = 0x202
        self.SIPM3K = 0x203

        # Communication with the MCA
        if type(MCA_IO) is None:
            self.MCA_IO = bridgeport_mca.mca_portal.MCA_PORTAL()  # For communication with the MDS
        else:
            self.MCA_IO = MCA_IO

        self.init(self.MCA_IO.sn_list[0])  # Initialize defaults with first MCA in the list
        self.printed_file_name = False

    def init(self, sn):
        """
            Initialize the MCA-related class attributes, given the
            serial number
        """
        # sn_list is a sorted list of serial numbers.

        self.MCA = self.MCA_IO.mca[sn]
        self.mca_id = self.MCA["mca_id"]
        self.commands = self.MCA["commands"]
        
    def requested_sn_list(self, lun_sn):
        """
            lun_sn can be:
            *) a single item; integer or string
            *) a list of items, each being an integer or a string
            -) A string is interpreted as a serial number
            -) An integer is considered to be a logical unit number if the integer is less than the number of attached MCA,
               else it is a numerical serial number.
               
            Note: In almost all cases the serial number will be a string.
        """
        self.sn_list = []
        if type(lun_sn) != list:
            lun_sn = [lun_sn]
        for item in lun_sn:
            if type(item)==str:
                self.sn_list += [item]
            elif type(item)==int and item < len(self.MCA_IO.sn_list):
                self.sn_list += [self.MCA_IO.sn_list[item]]


    def save_histogram(self, par):  # For all MCA
        # In requested_data we name all the quantities to be saved
        mode_list = ["all", "rate_histogram", "histogram"]

        requested_data = {
            "emorpho": {
                "all": {"fpga_ctrl": "read_fpga_ctrl", "fpga_results": "fpga_results", "rates": "rates", "histogram": "histogram"},
                "rate_histogram": {"rates": "rates", "histogram": "histogram"},
                "histogram": {"histogram": "histogram"}
            },
            "mca_3k": {
                "all": {"arm_version": "arm_version", "arm_status": "arm_status", "arm_ctrl": "read_arm_ctrl",
                       "fpga_status": "fpga_results", "fpga_ctrl": "read_fpga_ctrl",
                       "rates": "rates", "histogram": "histogram"},
                "rate_histogram": {"rates": "rates", "histogram": "histogram"},
                "histogram": {"histogram": "histogram"}
            },
            "mca_1k": {
                "all": {"arm_version": "arm_version", "arm_status": "arm_status",
                       "arm_ctrl": "read_arm_ctrl", "histogram": "histogram"},
                "rate_histogram": {"arm_status": "arm_status", "histogram": "histogram"},
                "histogram": {"histogram": "histogram"}
            }
        }

        par["mode_list"] = mode_list
        par["requested_data"] = requested_data
        self.save_requested_data(par)


    def save_background(self, par):  # For mca_1k, mca_2k
        # In requested_data we name all the quantities to be saved
        mode_list = ["all", "rate_histogram", "histogram"]

        requested_data = {
            "mca_1k": {
                "all": {"arm_version": "arm_version", "arm_status": "arm_status",
                       "arm_ctrl": "read_arm_ctrl", "histogram": "arm_bck"},
                "rate_histogram": {"arm_status": "arm_status", "histogram": "arm_bck"},
                "histogram": {"histogram": "arm_bck"}
            },
            "mca_1k": {
                "all": {"arm_version": "arm_version", "arm_status": "arm_status",
                       "arm_ctrl": "read_arm_ctrl", "histogram": "arm_bck"},
                "rate_histogram": {"arm_status": "arm_status", "histogram": "arm_bck"},
                "histogram": {"histogram": "arm_bck"}
            }
        }

        par["mode_list"] = mode_list
        par["requested_data"] = requested_data
        self.save_requested_data(par)


    def save_difference(self, par):  # For mca_1k, mca_2k
        # In requested_data we name all the quantities to be saved
        mode_list = ["all", "rate_histogram", "histogram"]

        requested_data = {
            "mca_1k": {
                "all": {"arm_version": "arm_version", "arm_status": "arm_status",
                       "arm_ctrl": "read_arm_ctrl", "histogram": "arm_diff"},
                "rate_histogram": {"arm_status": "arm_status", "histogram": "arm_diff"},
                "histogram": {"histogram": "arm_diff"}
            },
            "mca_1k": {
                "all": {"arm_version": "arm_version", "arm_status": "arm_status",
                       "arm_ctrl": "read_arm_ctrl", "histogram": "arm_diff"},
                "rate_histogram": {"arm_status": "arm_status", "histogram": "arm_diff"},
                "histogram": {"histogram": "arm_diff"}
            }
        }

        par["mode_list"] = mode_list
        par["requested_data"] = requested_data
        self.save_requested_data(par)


    def save_pulse(self, par): # For emorpho, mca_2k, mca_3k
        # In requested_data we name all the quantities to be saved
        mode_list = ["all", "status_pulse", "pulse"]

        requested_data = {
            "emorpho": {
                "all": {"fpga_ctrl": "read_fpga_ctrl", "fpga_results": "fpga_results", "rates": "rates", "pulse": "pulse"},
                "status_pulse": {"fpga_results": "fpga_results", "pulse": "pulse"},
                "pulse": {"pulse": "pulse"}
            },
            "mca_3k": {
                "all": {"arm_status": "arm_status", "fpga_ctrl": "read_fpga_ctrl", "fpga_results": "fpga_results", "rates": "rates", "pulse": "pulse"},
                "status_pulse": {"arm_status": "arm_status", "fpga_results": "fpga_results", "pulse": "pulse"},
                "pulse": {"pulse": "pulse"}
            },
            "mca_2k": {
                "all": {"arm_status": "arm_status", "arm_ctrl": "read_arm_ctrl", "pulse": "pulse"},
                "status_pulse": {"arm_status": "arm_status", "pulse": "pulse"},
                "pulse": {"pulse": "pulse"}
            }
        }
        par["mode_list"] = mode_list
        par["requested_data"] = requested_data
        self.save_requested_data(par)


    def save_listmode(self, par):  # For emorpho, mca_3k
        # In requested_data we name all the quantities to be saved
        mode_list = ["all", "status_listmode", "listmode"]

        requested_data = {
            "emorpho": {
                "all": {"fpga_ctrl": "read_fpga_ctrl", "fpga_results": "fpga_results", "rates": "rates", "listmode": "listmode"},
                "status_listmode": {"fpga_results": "fpga_results", "listmode": "listmode"},
                "listmode": {"listmode": "listmode"}
            },
            "mca_3k": {
                "all": {"arm_status": "arm_status", "fpga_ctrl": "read_fpga_ctrl", "fpga_results": "fpga_results", "rates": "rates", "listmode": "listmode"},
                "status_pulse": {"arm_status": "arm_status", "fpga_results": "fpga_results", "listmode": "listmode"},
                "listmode": {"listmode": "listmode"}
            }
        }
        par["mode_list"] = mode_list
        par["requested_data"] = requested_data
        self.save_requested_data(par)


    def save_logger(self, par):  # For mca_1k, mca_2k
        # In requested_data we name all the quantities to be saved
        mode_list = ["all", "status_logger", "logger"]

        requested_data = {
            "mca_1k": {
                "all": {"arm_version": "arm_version", "arm_status": "arm_status",
                       "arm_ctrl": "read_arm_ctrl", "arm_logger": "arm_logger"},
                "status_logger": {"arm_status": "arm_status", "logger": "arm_logger"},
                "logger": {"logger": "arm_logger"}
            },
            "mca_2k": {
                "all": {"arm_version": "arm_version", "arm_status": "arm_status",
                       "arm_ctrl": "read_arm_ctrl", "logger": "logger"},
                "status_logger": {"arm_status": "arm_status", "logger": "arm_logger"},
                "logger": {"logger": "arm_logger"}
            }
        }
        par["mode_list"] = mode_list
        par["requested_data"] = requested_data
        self.save_requested_data(par)


    def save_requested_data(self, par):

        # In requested_data we name all the quantities to be saved
        if par["mode"] not in par["mode_list"]:
            print("{} is not in {} => Selected {}.".format(par["mode"], mode_list, mode_list[0]))
            par["mode"] = par["mode_list"][0]

        self.requested_sn_list(par["lun_sn"])
        for sn in self.sn_list:
            self.init(sn)
            io_dict = par["requested_data"][self.MCA["mca_type"]][par["mode"]]

            out_dict = {"comment": par["comment"], "serial_number": sn, "short_sn": self.MCA["short_sn"],
                        "mca_id_str": self.MCA["mca_id_str"]}
            for key in io_dict:  # Read all data to be saved and assemble the output dictionary
                ret = self.MCA_IO.submit_command(sn, self.commands[io_dict[key]])[sn]
                ret_dict = {}
                for item in par["items"]:  # select the items to save
                    ret_dict[item] = ret[item]
                if key == "histogram" and self.MCA["mca_type"]=="emorpho":
                    ret_dict["registers"] = ret["registers"]  # emorpho histogram is only in registers.
                out_dict[key] = ret_dict

            out_file = par["prefix"]
            if not par["prefix"].endswith(".json"):
                data_path = "../data"
                file_name = "{}_{}.json".format(par["prefix"], out_dict["short_sn"])
                out_file = "{}/{}".format(data_path, file_name)

            if not self.printed_file_name:
                print("Output file name: ", out_file)
                self.printed_file_name = True

            with open(out_file, 'a') as fout:
                fout.write("{}\n".format(json.dumps(out_dict)))
