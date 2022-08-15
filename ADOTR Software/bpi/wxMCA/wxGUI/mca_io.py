import math
import json
import wx
import communication as com

class MCA_IO():
    """
        A class to store and retrieve controls and data from any MCA-0K, -1K, -2K or -3K, 
        from its non-volatile memory or from a settings file.
        The class is meant to be transient.  Data are always refreshed from the source.  
        Only immutable data such as serial numbers and mca_id are kept as class attributes.
        It also stores lists of menu and display components used by the various windows that make up the wxGUI.
    """

    def __init__(self, using_GUI=True):
        
        with open("./controls/gui_controls.json", 'r') as fin:
            self.gui_controls = json.loads(fin.read())
        
        self.mds_client = com.zmq_device(self.gui_controls["mds_ip"], "client")  # Communicate with MDS

        cmd = {"type": "server_cmd", "name": "identify"}
        msg = self.mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        self.identities = json.loads(msg)['mca_id']  # List of {sn: mca_id_str} dictionaries
        
        self.mca = {}
        for identity in self.identities:
            sn = list(identity)[0]
            self.mca[sn] = {"sn": sn}
            self.mca[sn].update(mca_id_str = identity[sn])
            self.mca[sn].update(mca_id = int(self.mca[sn]["mca_id_str"], 16))
            self.mca[sn].update(SN = sn[0:min(8, len(sn))])
            self.mca[sn].update(has_fpga = self.mca[sn]["mca_id"] in [0x6001, 0x103, 0x203, 0x104, 0x204])
            self.mca[sn].update(has_arm = self.mca[sn]["mca_id"] in [0x100, 0x200, 0x101, 0x201, 0x103, 0x203, 0x104, 0x204])
            self.mca[sn].update(mca_type = self.gui_controls["device_type"][self.mca[sn]["mca_id_str"]])
   
            user_root = self.gui_controls["user_root"]
            self.mca[sn].update(settings_dir = "{}{}/settings/".format(user_root, self.mca[sn]["mca_type"]))
            self.mca[sn].update(data_dir = "{}{}/data/".format(user_root, self.mca[sn]["mca_type"]))
            
            self.mca[sn].update(cmd = {"type": "mca_cmd", "dir": "read", "memory": "ram", "sn": sn})  # Default command
            self.mca[sn].update(adc_sr = 40e6)
            if self.mca[sn]["mca_id"] in [0x6001, 0x103, 0x203, 0x104, 0x204]:
                fpga_results = self.submit_command(sn, {"type": "mca_cmd", "name": "fpga_results", "dir": "read", "memory": "ram", "sn": sn})[sn]
                self.mca[sn]["adc_sr"] = fpga_results["fields"]["adc_sr"]*1.0e6
 
            if using_GUI:  # These are only used by the GUI
                cr = self.gui_controls["controls_root"]
                mca_type = self.gui_controls["device_type"][self.mca[sn]["mca_id_str"]]
                for item in ["main_menu", "device_controls", "commands", "display_controls", "plot_controls"]:
                    fp = "{}{}/{}.json".format(cr, mca_type, item)
                    try:
                        with open(fp, 'r') as fin:
                            self.mca[sn][item] = json.loads(fin.read())
                    except:
                        print("init_wxMCA, Line 31: Error when loading {}".format(fp))
                        a = 1/0
                # Report mca_name, mca_type, ctrl_list, ctrl_to_mca_list, displays
                self.mca[sn].update(self.gui_controls[self.mca[sn]["mca_id_str"]]) 
                
    # The functions below are being used by the wxGUI
    
    def program_arm_cal(self, sn, arm_cal_fields):
        """
            Read ARM calibration settings from a json file, the ARM calibration file has 64 entries.
        """
        cmd = {"type": "mca_cmd", "name": "arm_cal", "dir": "rmw", "sn": sn,
           "data": {"fields": arm_cal_fields}}
        arm_cal = self.submit_command(sn, cmd)[sn]
               
    def controls_to_nvmem(self, sn):
        """
            Store in non-volatile memory what is already stored in the device.
        """
        mca = self.mca[sn]
        backup = {}
        if mca["has_arm"]:
            cmd = {"name": "arm_ctrl",  "dir": "read", "memory": "ram"}
            arm_ctrl = self.submit_command(sn, cmd)[sn]
            cmd = {"name": "arm_ctrl",  "dir": "write", "memory": "flash", "data": {"registers": arm_ctrl["registers"]} }
            arm_ctrl = self.submit_command(sn, cmd)[sn]
            backup.update(arm_ctrl)
            
        if mca["has_fpga"]:
            cmd = {"name": "fpga_ctrl", "dir": "read", "memory": "ram"}
            fpga_ctrl = self.submit_command(sn, cmd)[sn]
            cmd = {"name": "fpga_ctrl", "dir": "write", "memory": "flash", "data": {"registers": fpga_ctrl["registers"]}}
            fpga_ctrl = self.submit_command(sn, cmd)[sn]
            backup.update(fpga_ctrl)
            
        with open(mca["settings_dir"]+"{}_all_ctrl_backup.json".format(sn), 'w') as fout:
            fout.write(json.dumps(backup))
        
    
    def controls_from_nvmem(self, sn, ctrl, memory):
        """
            Read the non-volatile memory of the MCA, then write those settings back to the MCA.
        """
        # Read from nv_mem; 
        # Then update arm RAM in the MCA
        mca = self.mca[sn]
        if mca["has_arm"]:
            cmd = {"name": "arm_ctrl", "dir": "read", "memory": memory} 
            arm_ctrl = self.submit_command(sn, cmd)[sn]
            cmd = {"name": "arm_ctrl", "dir": "write", "memory": "ram", "data": arm_ctrl}
            self.submit_command(sn, cmd)
        
        if mca["has_fpga"]:
            cmd = {"name": "fpga_ctrl", "dir": "read", "memory": memory}
            fpga_ctrl = self.submit_command(sn, cmd)[sn]
            cmd = {"name": "fpga_ctrl", "dir": "write", "memory": "ram", "data": fpga_ctrl }
            self.submit_command(sn, cmd)
            
        cmd = {"name": ctrl, "dir": "read", "memory": "ram"}    
        ret = self.submit_command(sn, cmd)[sn]
        return ret
    


    def controls_to_file(self, sn, file_path=None):
        """
            Store in a file what is already stored in the arm on the MCA;
            ie read from MCA and write to file.
        """
        mca = self.mca[sn]
        out_dict = {}

        if mca["has_arm"]:
            cmd = {"name": "arm_ctrl", "dir": "read"} 
            arm_ctrl = self.submit_command(sn, cmd)[sn]
            out_dict.update({'arm_ctrl': arm_ctrl})
        
        if mca["has_fpga"]:
            cmd = {"name": "fpga_ctrl", "dir": "read"} 
            fpga_ctrl = self.submit_command(sn, cmd)[sn]
            out_dict.update({'fpga_ctrl': fpga_ctrl})
            
        fp = file_path if file_path else mca["settings_dir"]+"{}_all_ctrl.json".format(sn) 
        with open(fp, 'w') as fout:
            fout.write(json.dumps(out_dict, indent=4))


    def controls_from_file(self, sn):
        """
            Read controls from a file and send them to the MCA.  
        """
        with open(self.daq_par[sn]["settings_dir"]+"{}_all_ctrl.json".format(sn), 'r') as fin:
            new_data = json.loads(fin.read())  # The settings file can legally be incomplete
        
        for ctrl in new_data:
            self.submit_command({"name": ctrl, "dir": "rmw", "data": new_data[ctrl]}, sn)
        
        
    def save_to_mca(self, sn, ctrl, data):
        cmd = {"name": ctrl, "dir": "rmw", "data": data, "sn": sn}
        self.submit_command(sn, cmd)
        
    def load_from_mca(self, sn, ctrl):
        cmd = {"name": ctrl, "dir": "read"}
        return self.submit_command(sn, cmd)[sn]
            

    def val_to_si(val):
        """
            Turn any number into an SI value between 1 and 1000 and the appropriate SI suffix
        """
        boundaries = [10**(n) for n in range(-15, 18, 3)]
        prefixes = ['a', 'f', 'p', 'n', 'u', 'm', '', 'k', 'M', 'G', 'P']
        sign = 1.0 if val>0  else -1.0
        val = abs(val)
        for b, p in zip(boundaries, prefixes):
            if val < b:
                return sign*val*b*1000, p
   
    def submit_command(self, sn, command):
        """
            To submit a command provide a partial command dictionary.  The function uses 
            a fresh copy of the default command for the MCA and updates that with 'command'.
            The function returns a dictionary containing the answer from the MCA Data Server. 
            """
        cmd = dict(self.mca[sn]["cmd"])  # Get a fresh copy of the default command
        cmd.update(command)
        msg = self.mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        return json.loads(msg)

