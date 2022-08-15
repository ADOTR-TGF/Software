#!/usr/bin/env python
import sys
import time
import os
import wx
import json
import status_ctrl_grid as scg
import mca_io

# import the graphics displays
import histo_wx
import sample_bck_wx
import tar_wx
import pulse_wx
import list_mode_wx
import logger_wx
import counter_wx
import coin_wx

"""
wx.ID_EXIT is 5006
wx.ID_ABOUT is 5014
wx.ITEM_NORMAL is 0
wx.ITEM_SEPARATOR is -1

"""

class MCA_Frame(wx.Frame):

    def __init__(self, dev_ind = 0):
        super(MCA_Frame, self).__init__(None, id=wx.ID_ANY)
        
        # Communication with the MCA
        self.MCA_IO = mca_io.MCA_IO()  # For communication with the MDS
        
        self.dev_ind = dev_ind
        self.sn = list(self.MCA_IO.mca)[self.dev_ind]
        self.MCA = self.MCA_IO.mca[self.sn]  
        
        self.mca_id = self.MCA["mca_id"]
        self.commands = self.MCA["commands"]
        
       
        self.display_function = {
            0x100: {"counter_wx": counter_wx.main, "logger_wx": logger_wx.main},
            0x200: {"counter_wx": counter_wx.main, "logger_wx": logger_wx.main},
            0x101: {"histo_wx": histo_wx.main, "sample_bck_wx": sample_bck_wx.main, "tar_wx": tar_wx.main, "logger_wx": logger_wx.main, "coin_wx": coin_wx.main},
            0x201: {"histo_wx": histo_wx.main, "sample_bck_wx": sample_bck_wx.main, "tar_wx": tar_wx.main, "logger_wx": logger_wx.main, "coin_wx": coin_wx.main},
            0x102: {"histo_wx": histo_wx.main, "sample_bck_wx": sample_bck_wx.main, "tar_wx": tar_wx.main, "logger_wx": logger_wx.main, "pulse_wx": pulse_wx.main},
            0x202: {"histo_wx": histo_wx.main, "sample_bck_wx": sample_bck_wx.main, "tar_wx": tar_wx.main, "logger_wx": logger_wx.main, "pulse_wx": pulse_wx.main},
            0x103: {"histo_wx": histo_wx.main, "pulse_wx": pulse_wx.main, "list_mode_wx": list_mode_wx.main, "coin_wx": coin_wx.main},
            0x203: {"histo_wx": histo_wx.main, "pulse_wx": pulse_wx.main, "list_mode_wx": list_mode_wx.main, "coin_wx": coin_wx.main},
            0x6001: {"histo_wx": histo_wx.main, "pulse_wx": pulse_wx.main, "list_mode_wx": list_mode_wx.main, "coin_wx": coin_wx.main},
            0x104: {"logger_wx": logger_wx.main, "counter_wx": counter_wx.main},
            0x204: {"logger_wx": logger_wx.main, "counter_wx": counter_wx.main}
        }
        
        self.main_menu_items = self.MCA["main_menu"]  # Names and help strings for menu items
        self.ctrl_to_mca_list = self.MCA["ctrl_to_mca_list"]  # To shorten the expressions
        
        self.SetTitle(self.main_menu_items["title"]+' '+self.sn)
        self.SetSize(800, 600)
                
        self.CenterOnScreen()

        self.CreateStatusBar()
        self.SetStatusText(self.main_menu_items["status_bar"])
        
        self.hello_panel = HelloPanel(self)
        self.hello_panel.Show()
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.hello_panel)
        self.SetSizer(self.sizer)

        MB = MenuBar(self.main_menu_items)
        self.SetMenuBar(MB)
        self.menu_ids = MB.menu_ids

        # Menu events        
        for id in MB.menu_ids:
            self.Bind(wx.EVT_MENU, self.MenuSelect, id=id)
        
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.on_X_button)
        
        # instance for fpga_weights
        if self.MCA["mca_id"] in  [ 0x6001, 0x203, 0x103]:
            self.list_mode_wx = list_mode_wx.ListModeWindow(None,  'List Mode ' + self.sn, self.dev_ind)
        
        # for save and open all_ctrl
        self.previous_save_path = ''

    def OnSize(self, event):
        self.SetSizeHints(minW = 580, minH = 400)
        self.Layout()

    def on_X_button(self, event):
        quit()

    def on_quit_click(self, event):
        """Handle close event."""
        del event
        wx.CallAfter(self.Destroy)    
        
    # Methods

    def MenuSelect(self, event):
        
        id = event.GetId()  # Receive the ID of the menu item the customer clicked on
        menu_item = self.menu_ids[id]
        # print('Selected item: {}\n'.format(menu_item))  # DEBUG
        try:
            self.status_panel.exists = 1
            st_panel_exists = True
        except:
            st_panel_exists = False
        
        need_new_grid = False
        json_filter = "JSON (*.json)|*.json|All files (*.*)|*.*"
        
        if st_panel_exists:
            data = self.status_panel.stGrid.data  # Output data
            data_ctrl = self.status_panel.data_ctrl
            display_ctrl = self.status_panel.display_ctrl

            if menu_item == "File_Save":
                self.MCA_IO.controls_to_file(self.sn)
                
            if menu_item == "File_SaveAS":
                curr_path = os.getcwd()
                save_path = os.path.dirname(curr_path) + self.MCA['settings_dir'].strip('.')
                if self.previous_save_path:
                    save_path = self.previous_save_path
                dlg = wx.FileDialog(self, message="Save {} as ...".format(data_ctrl), defaultDir=save_path, 
                      defaultFile="{}_all_ctrl.json".format(self.sn), wildcard=json_filter, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

                dlg.SetFilterIndex(2) # This sets the default filter that the user will initially see.
                # Show the dialog and retrieve the user response. If it is the OK response,process the data.
                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    self.MCA_IO.controls_to_file(self.sn, file_path=path)
                    self.previous_save_path = path
                dlg.Destroy()  # Destroy dialog after saving the file.
                
            if menu_item == "File_Open":
                open_path = os.getcwd()
                if self.previous_save_path:
                    open_path = self.previous_save_path
                dlg = wx.FileDialog(
                    self, message="Choose a {} file".format(data_ctrl),
                    defaultDir=open_path,
                    defaultFile="",
                    wildcard=json_filter,
                    style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)  # wx.FD_CHANGE_DIR | wx.FD_MULTIPLE

                if dlg.ShowModal() == wx.ID_OK:  # Show the dialog and retrieve the user response.
                    path = dlg.GetPaths()[0] # This returns a list of files that were selected; here limited to 1
                    with open(path, "r") as fin:
                        ret = json.loads(fin.read())
                    if data_ctrl in list(ret):
                        data = ret[data_ctrl]
                        need_new_grid = True
                
                dlg.Destroy() # Destroy dialog after reading the file.
                
                
            if menu_item == "from_MCA":  
                if self.status_panel.data_ctrl in self.MCA["ctrl_list"]:
                    data = self.MCA_IO.load_from_mca(self.sn, data_ctrl)
                    if self.status_panel.data_ctrl == "fpga_statistics":
                        data = data["user"]
                    need_new_grid = True
            
            if menu_item == "to_MCA":  
                if data_ctrl in self.ctrl_to_mca_list:
                    self.MCA_IO.save_to_mca(self.sn, data_ctrl, data)
                
            if menu_item == "Factory_Reset":  
                if data_ctrl in self.ctrl_to_mca_list:
                    data = self.MCA_IO.controls_from_nvmem(self.sn, data_ctrl, memory="reset")
                    need_new_grid = True
                    
            if menu_item == "from_NVMEM":  
                if data_ctrl in self.ctrl_to_mca_list:
                    data = self.MCA_IO.controls_from_nvmem(self.sn, data_ctrl, memory="flash")
                    need_new_grid = True
            
            if menu_item == "to_NVMEM":  
                if self.status_panel.data_ctrl in self.ctrl_to_mca_list:
                    self.MCA_IO.controls_to_nvmem(self.sn)

        # ARM calibration
        if menu_item == 'arm_cal':
            path = os.getcwd()

            open_path = os.path.dirname(path) + "/user/{}/data".format(self.MCA['mca_type'])
            dlg = wx.FileDialog(
                self, message="Choose a {} file".format(menu_item),
                defaultDir=open_path,
                defaultFile="",
                wildcard=json_filter,
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)  # wx.FD_CHANGE_DIR | wx.FD_MULTIPLE

            if dlg.ShowModal() == wx.ID_OK:  # Show the dialog and retrieve the user response.
                path = dlg.GetPaths()[0] # This returns a list of files that were selected; here limited to 1
                with open(path, "r") as fin:
                    ret = json.loads(fin.read())
                ok = True
                for key in ["lut_len", "lut_tmin", "lut_dt", "lut_ov", "lut_dg", "lut_led", "lut_mode"]:  # required keys
                    ok = ok and key in ret
                if ok:
                    dlg.Destroy()
                    self.MCA_IO.program_arm_cal(self.sn, ret)
                else:
                    wx.LogError('The file you choose is not in a correct form for ARM calibration')
                
        # Graphics displays
        if menu_item in self.display_function[self.mca_id]:
            if menu_item == 'list_mode_wx':
                try:
                    self.list_mode_wx.Show()
                except:
                    self.display_function[self.mca_id][menu_item](self.sn, self.dev_ind)
            else:
                self.display_function[self.mca_id][menu_item](self.sn, self.dev_ind)
           
        if menu_item == "Quit":
            self.Close()
            
        if menu_item in self.MCA["ctrl_list"]:
            display_ctrl = menu_item
            data_ctrl = self.MCA["device_controls"][menu_item]["source"]
            data = self.MCA_IO.load_from_mca(self.sn, data_ctrl)
            need_new_grid = True
                        
        if menu_item == "count_rates":
            if self.MCA["mca_id"] in [0x6001, 0x103, 0x203]:
                data = self.MCA_IO.load_from_mca(self.sn, "fpga_statistics")["user"]
            else:
                data = self.MCA_IO.load_from_mca(self.sn, "arm_status")
            need_new_grid = True
            display_ctrl = menu_item
                
        if menu_item == "fpga_weight":
            try:
                self.list_mode_wx.load_psd_weights()
            except:
                self.list_mode_wx = list_mode_wx.ListModeWindow(None,  'List Mode ' + self.sn, self.dev_ind)
                self.list_mode_wx.load_psd_weights()
                
        if need_new_grid:
            main_frame = wx.GetTopLevelParent(self) # The frame at the top owns the panel
            try: 
                main_frame.hello_panel.Destroy() # Delete if it still exists
            except:
                pass
            try:
                main_frame.status_panel.Destroy()
            except:
                pass

            self.status_panel = scg.StatusPanel(self, self.MCA["device_controls"][display_ctrl], data)           
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.sizer.Add(self.status_panel)
            self.SetSizer(self.sizer)
            self.sizer.SetSizeHints(self)
            self.Layout()
            
        if menu_item == "About":
            win = TransientPopup(self, wx.SIMPLE_BORDER, self.main_menu_items["about_text"])
            win.Popup()
            
class MenuBar(wx.MenuBar):
    """Create the menu bar."""
    def __init__(self, main_menu_items):
        super(MenuBar, self).__init__(0)  # style=0
        
        # Dictionary of menu ids
        self.menu_ids={}  # We need these outside the MenuBar object
        
        # Create the menus from the data in the main_widgets.json file
        for mnu in main_menu_items["menus"]:
            menu_name = mnu["menu_name"]
            new_menu = wx.Menu()
            for item in mnu["menu_items"]:
                if item["name"] == "Quit":
                    id = wx.ID_EXIT
                elif item["name"] == "About":
                    id = wx.ID_ABOUT
                else:
                    id = wx.Window.NewControlId()
                item["id"] = id
                self.menu_ids.update({id: item["name"]})
                new_menu.Append(id, **item["kw"])
            self.Append(new_menu, mnu["menu_name"])

class HelloPanel(wx.Panel):  # Non-editable data display
    """Panel class to contain frame widgets."""
    def __init__(self, parent):
        super(HelloPanel, self).__init__(parent)

        """Create and populate main sizer."""
        self.tc = wx.TextCtrl(self, wx.ID_ANY, "Select a Menu Item to Begin.", style=wx.TE_READONLY|wx.TE_MULTILINE)
        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.tc)
        self.SetSizer(self.sizer, deleteOld=True)   
            
class TransientPopup(wx.PopupTransientWindow):
    """Adds a bit of text and mouse movement to the wx.PopupWindow"""
    def __init__(self, parent, style, text):
        wx.PopupTransientWindow.__init__(self, parent, style)
        panel = wx.Panel(self)
        panel.SetBackgroundColour("Moccasin")

        st = wx.StaticText(panel, -1, text)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(st, 100, wx.ALL, 5)  # Undocumented function
        panel.SetSizer(sizer)
        sizer.Fit(panel)
        sizer.Fit(self)
        self.Layout()

    

def mds():
    self.call_proc("mds", "./cmd/mds.cmd")
    om = operations_manager.operation_controls()  # This object has all arm_ctrl data storage links  
    now = datetime.datetime.now().strftime('%m-%d-%y %H:%M:%S')
    self.msg_text.set_text("{}: MCA: {}".format(now, om.sn[0:8]))

def call_proc(title, cmd):
    """
        Windows:  Launch a process and return before process has finished.
        A command window with title 'title' will open.  
        That title is also used to close that window, if it already exists.
        
    """
    proc = 'taskkill /FI "WINDOWTITLE eq {0} - {1}\nstart "{0}" /min {1}'.format(title, cmd)
    with open("command.cmd", 'w') as fout:
        fout.write(proc)
    sub = subprocess.Popen("command.cmd")

def main(dev_ind = 0):
    mca_main = wx.App()
    main_frame = MCA_Frame(dev_ind)
    main_frame.Show()
    mca_main.MainLoop() 
    
if __name__ == '__main__':
    main()