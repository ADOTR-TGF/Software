import json
import mca_io

class MCA_Controls():
    def __init__(self, max_mca=1):  # By default we accept one MCA
        """
            Read in all the json control files needed by wxMCA.
            Create one instance of MCA_IO to perform communication with the MCA or Counter.
        """
        
        with open("./controls/gui_controls.json", 'r') as fin:
            self.gui_controls = json.loads(fin.read())
        
        self.io = mca_io.MCA_IO(self.gui_controls)
        self.all_mca = self.io.mca  # self.all_mca is a dictionary of objects to perform the data I/O with each MCA or Counter
        
        # For now we only use the first device in the dictionary
        sn = list(self.all_mca)[0]
        self.mca = self.all_mca[sn]
        
        mca_type = self.gui_controls["device_type"][self.mca["mca_id_str"]]
        cr = self.gui_controls["controls_root"]
        
        for item in ["main_menu", "device_controls", "commands", "display_controls", "plot_controls"]:
            fp = "{}{}/{}.json".format(cr, mca_type, item)
            try:
                with open(fp, 'r') as fin:
                    self.mca[item] = json.loads(fin.read())
            except:
                print("init_wxMCA, Line 31: Error when loading {}".format(fp))
                a = 1/0
                
        self.mca.update(self.gui_controls[self.mca["mca_id_str"]])  # Report mca_name, mca_type, ctrl_list, ctrl_to_mca_list, displays

        
if __name__ == '__main__':
    mca_ctrl = MCA_Controls()
    with open("test.json", "w") as fout:
        fout.write(json.dumps(mca_ctrl.mca, indent=2))
    