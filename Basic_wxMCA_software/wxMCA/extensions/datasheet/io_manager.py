import math
import json

class io_controls():
    """
        A class to store and retrieve op_ctrl data from any MCA-0K, -1K, -2K or -3K, from its non-volatile memory or from a settings file.
        The class is meant to be transient.  Data are always refreshed from the source.  
        Only immutable data such as serial numbers and mca_id are kept as class attributes.
    """

    def __init__(self):
        with open("./controls/file_paths.json", "r") as fin:
            self.file_paths = json.loads(fin.read())
       
    def select_sn_idx(self, idx):
        """  Select a device by its index in the serial number list """
        if idx>=0:
            idx = min(len(self.sn_list)-1, idx)
        else:
            idx = max(-len(self.sn_list), idx)
        self.sn = self.sn_list[idx]
       

    # The functions below are being used by the wxGUI
    
    def save_backup(self, ctrl):
         # Save a copy to the backup file in the settings directory    
        with open(self.settings_dir+"{}_op_ctrl_backup.json".format(self.sn), 'w') as fout:
            fout.write(json.dumps(ctrl, indent=4))
            
    def save_to_file(self, ctrl, record, file_name=""):
        if file_name == "":
            file_name = record["path"]
        with open(file_name, "w") as fout:
            path = record["path"]
            record.pop("path")
            fout.write(json.dumps(record, indent=4))
            record["path"] = path
            
    def load_from_file(self, file_name):
        with open(file_name, "r") as fin:
            ret = json(loads(fin.read()))
        return ret
        

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

