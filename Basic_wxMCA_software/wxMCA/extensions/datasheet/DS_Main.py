#!/usr/bin/env python
import sys
import time
import os
import wx
import json
import status_ctrl_grid as scg
import io_manager
import data_sheet

"""
wx.ID_EXIT is 5006
wx.ID_ABOUT is 5014
wx.ITEM_NORMAL is 0
wx.ITEM_SEPARATOR is -1

"""

class MCA_Frame(wx.Frame):

    def __init__(self):
        super(MCA_Frame, self).__init__(None, id=wx.ID_ANY)
        # MCA communication
        self.iom = io_manager.io_controls()  # This object manages all data storage
                
        # Names and help strings for menu items        
        with open("./controls/main_menu.json", 'r') as fin:
            self.main_menu_items = json.loads(fin.read())
            
        self.SetTitle(self.main_menu_items["title"])
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
        for mnid in MB.menu_ids:
            self.Bind(wx.EVT_MENU, self.MenuSelect, id=mnid)

        self.Show()
        
    def on_quit_click(self, event):
        """Handle close event."""
        del event
        wx.CallAfter(self.Destroy)    
        
    # Methods

    def MenuSelect(self, event):
        
        evid = event.GetId()  # Receive the ID of the menu item the customer clicked on
        menu_item = self.menu_ids[evid]
        # print('L73 Selected item: {}\n'.format(menu_item))  # DEBUG
        try:
            self.status_panel.exists = 1
            st_panel_exists = True
        except:
            st_panel_exists = False
        
        need_new_grid = False
        json_filter = "JSON (*.json)|*.json|All files (*.*)|*.*"
        
        record = None
        if st_panel_exists:
            record = self.status_panel.stGrid.record  # Output data record
            data_ctrl = self.status_panel.data_ctrl  # The type of data
            
            if menu_item == "File_Save":
                self.iom.save_to_file(data_ctrl, record)
                self.setup_record = record
                
            if menu_item == "File_SaveAS":
                # def_dir = os.getcwd()+"/{}/".format(record["type"])
                def_dir = self.iom.file_paths[record["type"]]

                dlg = wx.FileDialog(self, message="Save {} as ...".format(data_ctrl), defaultDir=def_dir, 
                      defaultFile="{}.json".format(data_ctrl), wildcard=json_filter, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

                dlg.SetFilterIndex(0) # This sets the default filter that the user will initially see.
                # Show the dialog and retrieve the user response. If it is the OK response, process the data.
                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    self.iom.save_to_file(data_ctrl, record, file_name=path)
                    self.setup_record = record
                dlg.Destroy()  # Destroy dialog after saving the file.
        
        if menu_item == "File_Open":
            tipo = "setup"
            if record is not None:
                tipo = record["type"]
                
            # def_dir = os.getcwd()+"/{}/".format(record["type"])
            def_dir = self.iom.file_paths[tipo]    
            dlg = wx.FileDialog(
                self, message="Choose a {} file".format(tipo),
                defaultDir=def_dir,
                defaultFile="",
                wildcard=json_filter,
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)  # wx.FD_CHANGE_DIR | wx.FD_MULTIPLE

            if dlg.ShowModal() == wx.ID_OK:  # Show the dialog and retrieve the user response.
                path = dlg.GetPaths()[0] # This returns a list of files that were selected; here limited to 1
                with open(path, "r") as fin:
                    ret = json.loads(fin.read())
                    
                if ret["type"] == "setup":
                    record = ret
                    need_new_grid = True
                    record["path"] = path
                    self.setup_record = record

            dlg.Destroy() # Destroy dialog after reading the file.

            
        if menu_item == "make_ds":
            DS = data_sheet.DataSheet(self.setup_record)
            DS.mca_plot_fit()
            DS.make_data_sheet()  
            
        if menu_item == "Quit":
            self.Close()
                    
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
            self.status_panel = scg.StatusPanel(self, record)           
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.sizer.Add(self.status_panel)
            self.SetSizer(self.sizer)
            self.Layout()
            
        if menu_item == "About":
            win = TransientPopup(self, wx.SIMPLE_BORDER, self.main_menu_items["about_text"])
            win.Popup()
            
    def save_as_file(self, parent, file_extension):
        filter_str = "{0} (*.{0})|*.{0}|All files (*.*)|*.*".format(file_extension)
        dlg = wx.FileDialog(
            parent, message="Choose a {} file".format(file_extension),
            defaultDir=os.getcwd(),
            defaultFile=".{}".format(file_extension),
            wildcard=filter_str,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)  # wx.FD_CHANGE_DIR | wx.FD_MULTIPLE

        path = ""
        if dlg.ShowModal() == wx.ID_OK:  # Show the dialog and retrieve the user response.
            path = dlg.GetPaths()[0] # This returns a list of files that were selected; here limited to 1
        dlg.Destroy() # Destroy dialog 
        return path
        
    def open_a_file(self, parent, file_extension):
        filter_str = "{0} (*.{0})|*.{0}|All files (*.*)|*.*".format(file_extension)
        dlg = wx.FileDialog(
            parent, message="Choose a {} file".format(file_extension),
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=filter_str,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)  # wx.FD_CHANGE_DIR | wx.FD_MULTIPLE

        path = ""
        if dlg.ShowModal() == wx.ID_OK:  # Show the dialog and retrieve the user response.
            path = dlg.GetPaths()[0] # This returns a list of files that were selected; here limited to 1
        dlg.Destroy() # Destroy dialog 
        return path   

        

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

if __name__ == '__main__':
    mca_main = wx.App()
    main_frame = MCA_Frame()
    main_frame.Show()
    mca_main.MainLoop() 
    