import os
import math
import json
import bridgeport_mca.communication as com

class MCA_PORTAL():
    """
        A class to collect information about the MCA from the server.
        Only immutable data such as serial numbers and mca_id are kept as class attributes.

        In addition, it loads directory information for data storage
        as well a set of known commands from file.

        It can store and retrieve controls and data from any MCA-0K, -1K, -2K or -3K,
        from its non-volatile memory or from a settings file.
    """

    def __init__(self, cmd_root="", ctrl_root="", mds_ip=""):
        self.EMORPHO = 0x6001
        self.PMT1K = 0x101
        self.PMT2K = 0x102
        self.PMT3K = 0x103
        self.SIPM1K = 0x201
        self.SIPM2K = 0x202
        self.SIPM3K = 0x203

        if not cmd_root:
            cmd_root = "../../bridgeport_mca/commands/"
        if not mds_ip:
            mds_ip = "tcp://127.0.0.1:5507"

        if not ctrl_root:
            ctrl_root = "../../bridgeport_mca/controls/"        
        with open("{}mca_portal.json".format(ctrl_root), 'r') as fin:
            self.mca_controls = json.loads(fin.read())

        self.mds_client = com.zmq_device(mds_ip, "client")  # Communicate with MDS

        cmd = {"type": "server_cmd", "name": "details"}
        msg = self.mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        self.details = json.loads(msg)['mca_details']  # List of {sn: mca_id_str} dictionaries

        self.sn_list = []
        self.mca = {}
        for detail in self.details:  # Collect MCA id's and ADC speed
            sn = list(detail)[0]
            self.sn_list += [sn]
            self.mca[sn] = {"sn": sn}
            self.mca[sn].update(detail[sn])
            mca_id = self.mca[sn]["mca_id"]
            mca_id_str = self.mca[sn]["mca_id_str"]
            self.mca[sn].update(SN = sn[0:min(8, len(sn))])
            self.mca[sn].update(has_fpga = mca_id in [0x6001, 0x103, 0x203, 0x104, 0x204])
            self.mca[sn].update(has_arm = mca_id in [0x100, 0x200, 0x101, 0x201, 0x102, 0x202, 0x103, 0x203, 0x104, 0x204])
            self.mca[sn].update(mca_type = self.mca_controls["device_types"][mca_id_str])

            self.mca[sn]["cmd"] = {"type": "mca_cmd", "dir": "read", "memory": "ram"}  #default cmd
            cmd_file = self.mca_controls["command_files"][mca_id_str]
            with open("{}{}".format(cmd_root, cmd_file), "r") as fin:
                self.mca[sn].update(commands = json.loads(fin.read()))

        self.sn_list = sorted(self.sn_list)
    
    def init(self, lun_sn):
        """
            Initialize the MCA-related class attributes, given the
            logic unit number or serial number.  Serial numbers are always
            greater than 100.
        """
        # sn_list is a sorted list of serial numbers.
        self.sn = self.sn_list[lun_sn] if lun<len(self.MCA_IO.sn_list) else lun_sn

        self.MCA = self.mca[self.sn]
        self.mca_id = self.MCA["mca_id"]
        self.commands = self.MCA["commands"]
        

    def controls_to_nvmem(self, sn):
        """
            Store in non-volatile memory what is already stored in the device.
        """
        mca = self.mca[sn]
        if mca["has_arm"]:
            arm_ctrl = self.submit_command(sn, mca.commands["read_arm_ctrl"])[sn]
            arm_ctrl = self.submit_command(sn, mca.commands["write_arm_ctrl_flash"], {"registers": arm_ctrl["registers"]})[sn]

        if mca["has_fpga"]:
            fpga_ctrl = self.submit_command(sn, mca.commands["read_fpga_ctrl"])[sn]
            self.submit_command(sn, mca.commands["write_fpga_ctrl_flash"], {"registers": fpga_ctrl["registers"]})[sn]


    def controls_from_nvmem(self, sn, ctrl):
        """
            Read the non-volatile memory of the MCA, then write those settings back to the MCA.
        """
        # Read from nv_mem;
        # Then update arm RAM in the MCA
        mca = self.mca[sn]
        if mca["has_arm"]:
            arm_ctrl = self.submit_command(sn, mca.commands["read_arm_ctrl_flash"])[sn]
            self.submit_command(sn, mca.commands["write_arm_ctrl"], arm_ctrl)

        if mca["has_fpga"]:
            fpga_ctrl = self.submit_command(sn, mca.commands["read_fpga_ctrl_flash"])[sn]
            self.submit_command(sn, mca.commands["write_fpga_ctrl"], fpga_ctrl)


    def controls_from_reset(self, sn, ctrl):
        """
            Read factory reset memory of the MCA, then write those settings back to the MCA.
        """
        # Read from nv_mem;
        # Then update arm RAM in the MCA
        mca = self.mca[sn]
        if mca["has_arm"]:
            arm_ctrl = self.submit_command(sn, mca.commands["read_arm_ctrl_reset"])[sn]
            self.submit_command(sn, mca.commands["write_arm_ctrl"], arm_ctrl)

        if mca["has_fpga"]:
            fpga_ctrl = self.submit_command(sn, mca.commands["read_fpga_ctrl_reset"])[sn]
            self.submit_command(sn, mca.commands["write_fpga_ctrl"], fpga_ctrl)


    def controls_to_file(self, sn, file_path=None):
        """
            Store in a file what is already stored in the arm on the MCA;
            ie read from MCA and write to file.
        """
        mca = self.mca[sn]
        out_dict = {}

        if mca["has_arm"]:
            arm_ctrl = self.submit_command(sn, mca.commands["read_arm_ctrl"])[sn]
            out_dict.update({'arm_ctrl': arm_ctrl})

        if mca["has_fpga"]:
            fpga_ctrl = self.submit_command(sn, mca.commands["read_fpga_ctrl"])[sn]
            out_dict.update({'fpga_ctrl': fpga_ctrl})

        fp = file_path
        if not file_path:
            sr = self.mca_controls["settings_root"].rstrip("/")
            fp = "{}/{}_all_ctrl.json".format(sr, sn)
        with open(fp, 'w') as fout:
            fout.write(json.dumps(out_dict, indent=4))


    def controls_from_file(self, sn, file_path=None):
        """
            Read controls from a file and send them to the MCA.
        """
        fp = file_path
        if not file_path:
            sr = self.mca_controls["settings_root"].rstrip("/")
            fp = "{}/{}_all_ctrl.json".format(sr, sn)

        with open(fp, 'r') as fin:
            new_data = json.loads(fin.read())  # The settings file can legally be incomplete

        for ctrl in new_data:
            self.submit_command({"name": ctrl, "dir": "rmw", "data": new_data[ctrl]}, sn)


    def save_to_mca(self, sn, ctrl, memory="ram", data={}):
        """
            Usage: To write for instance arm_ctrl call
            .save_to_mca(sn, "arm_ctrl", data={"fields": { ... }})
            This is a read-modify-write action; hence you need to only submit
            those fields entries that you want to change.
            return None
        """
        self.submit_command(sn, {"name": ctrl, "dir": "rmw", "memory": memory, "data": data, "sn": sn})


    def load_from_mca(self, sn, ctrl, memory="ram"):
        """
            Usage: To read for instance arm_ctrl call
            .load_from_mca(sn, "arm_ctrl")
            return the arm_ctrl dictionary
        """
        return self.submit_command(sn, {"name": ctrl, "dir": "read", "memory": memory})[sn]


    def submit_command(self, lun_sn, command, data={}, memory="", dir=""):
        """
            This function sends a command to all requested devices.
            Unlike the MDS it can use command_names and pick the appropriate command
            from the command list specific to each MCA type.
            
            lun_sn: Logical unit number or serial number, or list thereof
                    For lun_sn <= 100 it is treated as a logical unit number, with counting starting at 0.
                    For example lun_sn=1 will address the 2nd attached MCA
                    
                    lun_sn can also be a list of lun or serial numbers
                    If the list is empty, the command will be applied to no MCA.
                    If lun_sn=None the command will be applied to all attached MCA
                    
            command: This parameter is either a command dictionary, with or without the data section
                     or the name of a command.
                     
                     In many cases there is a common name; eg "start_mca" for which there is an implementation
                     for all MCA.  In such a case a command_name can be used to independent of the type of MCA.
                     
                     Explicit command dictionaries are specific to a particular MCA type 
                     and should then be used only if all attached MCA are of the same type.
        """
        lun_sn_list = []
        if type(lun_sn) is None:  # None => Send command to all MCA
            lun_sn_list = self.sn_list
        elif type(lun_sn)==list:    # list => Send command to all MCA in the list
            lun_sn_list = [s for s in lun_sn]
        else:
            lun_sn_list = [lun_sn]  # number => Send command to one MCA

        for lun_sn in lun_sn_list:
            if type(lun_sn)==str:
                sn = lun_sn
            else:
                sn = self.sn_list[int(lun_sn)]
            
            if type(command)==str:  # Replace the short-hand name with the actual command
                command = self.mca[sn]["commands"][command]
               
            cmd = dict(self.mca[sn]["cmd"])  # Get a fresh copy of the default command
            
            cmd.update(command)
            if data:  # default is no data
                self.update_data(cmd, data)
            if memory:  # default memory is ram
                cmd["memory"] = memory
            if dir: # default direction is read or rmw
                cmd["dir"] = dir
                
            cmd["sn"] = sn

            msg = self.mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        return json.loads(msg)
        
    def update_data(self, cmd, data):
        """
            Update a command dictionary with the data dictionary by creating a new
            "data" key in cmd if it did not exist.
            Similarly, create a new "fields" or "user" key inside the cmd["data"] dictionary
            as necessary.
            In all cases, preserve any existing keys cmd and sub dictionaries, and overwrite 
            values only as explicitly required.
            
            Note that the input cmd dictionary is being altered; no return statement necessary
        """
        if "data" not in cmd:
            cmd["data"] = data
        else:
            for fld in ["fields", "user"]:
                if fld in data:
                    if fld not in cmd["data"]:
                        cmd["data"][fld] = data[fld]
                    else:
                        for key in data[fld]:
                            cmd["data"][fld][key] = data[fld][key]

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
