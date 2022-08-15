import time
import subprocess
import wx
import os
import json
import mca_io
import status_ctrl_grid as scg

class CounterWindow(wx.Frame): 
    def __init__(self, parent, title): 
        super(CounterWindow, self).__init__(parent, title = title)
        self.EMORPHO = 0x6001
        self.PMT1K = 0x101
        self.PMT3K = 0x103
        self.SIPM1K = 0x201
        self.SIPM3K = 0x203
        self.PMTN3K = 0x104
        self.SIPMN3K = 0x204
        
        
        # Communication with the MCA
        self.MCA_IO = mca_io.MCA_IO()  # For communication with the MDS
        
        #-- Here we use the first mca in the MCA_IO.mca dictionary
        #self.sn = list(self.MCA_IO.mca)[0]
        #self.MCA = self.MCA_IO.mca[self.sn]  
        
        #-- Here we use the globally chosen sn:
        with open('chosen_sn.txt','r') as snfile:
        	fname = snfile.read()
        	snfile.close()
        self.sn = fname
        self.MCA = self.MCA_IO.mca[self.sn]
        
        self.mca_id = self.MCA["mca_id"]
        self.disp_ctrl = self.MCA["display_controls"]["counter"]["data"]
        self.commands = self.MCA["commands"]
        
        # Build the panel
        self.panel = wx.Panel(self, size = (5000, 3000)) 
        self.box_local = wx.BoxSizer(wx.VERTICAL)

        # Make a list of action buttons
        self.button_list = []
        button = wx.Button(self.panel, id = wx.ID_ANY, label="Sample", name="sample_counter")
        self.button_list += [button]

        button = wx.Button(self.panel, id = wx.ID_ANY, label="Background", name="bck_counter") 
        self.button_list += [button]
        
        button = wx.Button(self.panel, id = wx.ID_ANY, label="Refresh", name="read_show_counts") 
        self.button_list += [button]
        
        button = wx.Button(self.panel, id = wx.ID_ANY, label="Save", name="save_counter") 
        self.button_list += [button]
        
        # Put all buttons in a horizontal sizer
        self.button_box = wx.BoxSizer(wx.HORIZONTAL)
        for button in self.button_list:
            button.Bind(wx.EVT_BUTTON, self.OnClicked)
            self.button_box.Add(button, 0, wx.RIGHT, 4)
        # Add buttonbox to the vertical stack
        self.box_local.Add(self.button_box, 0, wx.LEFT| wx.TOP| wx.BOTTOM, 10)
        
        # Read and display count rates
        self.read_show_counts()

        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        self.SetSizeHints(minW = 600, minH = 400)
        self.Layout()
        self.box_local.ShowItems(False)
        self.box_local.ShowItems(True)
            
    def OnClicked(self, event): 
        name = event.GetEventObject().GetName()
        if name in self.commands:
            self.MCA_IO.submit_command(self.sn, self.commands[name])
            self.read_show_counts()
        else:
            getattr(self, name)()  # Call the function that bears the button's name
            
    def read_show_counts(self):
        # display count rates status panel
        self.data = self.MCA_IO.load_from_mca(self.sn, "arm_status")
        try:
            self.count_rates.Destroy()
        except:
            pass
        self.count_rates = scg.StatusGrid(self.panel, self.MCA["device_controls"]["count_rates"], self.data)
        self.box_local.Add(self.count_rates, 0, wx.LEFT| wx.BOTTOM, 1)
        self.SetSizer(self.box_local)
        self.box_local.SetSizeHints(self)
        self.Layout()
        
    def save_counter(self):
        out_file = self.disp_ctrl["file"]["value"]
        splt_out_file = out_file.strip('.').rsplit('/', 1)
        data_dir_path = splt_out_file[0]
        file_name = splt_out_file[1]
        default_path = os.path.dirname(os.getcwd()) + data_dir_path
        try:
            data_path = self.last_saved_path
        except:
            data_path = default_path
            
        out_dict = self.data["fields"]
        with wx.FileDialog(self, "Save counter rates data", wildcard="json files (*.json)|*.json", defaultDir = data_path, defaultFile = file_name,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return 
            pathname = fileDialog.GetPath()
            self.last_saved_path = os.path.dirname(pathname)
            try:
                with open(pathname, 'a+') as fout:
                    fout.write(json.dumps(out_dict)+'\n')
            except IOError: 
                wx.LogError("Cannot save current data in file '%s'." % out_file)
        
def main():             
    app = wx.App() 
    panel = CounterWindow(None,  'Counter')
    panel.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    main()
    

        
        
