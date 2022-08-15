import time
import json
import wx
import wx.grid as wxgrid  # Why can't I use wx.grid directly?

"""
class StatusPanel(wx.Panel):  # Editable data display
    
    def __init__(self, parent):
        super(StatusPanel, self).__init__(parent)
        
        self.stGrid = StatusGrid(self, parent)
        sizer = wx.BoxSizer() # (orientation = wx.VERTICAL or wx.HORIZONTAL)
        sizer.Add(self.stGrid)
        self.SetSizer(sizer)
"""
class StatusGrid(wxgrid.Grid):
    def __init__(self, parent, caller):
        """ 
            parent: is the parent window into which this widget is going to be inserted
        """
        super(wxgrid.Grid, self).__init__(parent, id=wx.ID_ANY)
        self.parent = parent
        self.caller = caller  # Event functions can not be passed the argument 'caller'
        self.controls = caller.MCA["display_controls"][caller.display_name]
        
        # self.Create(parent, id=wx.ID_ANY)
        self.num_rows = len(self.controls["data"]) 
        self.CreateGrid(self.num_rows - 2, 3) # cols: name, value, help
        
        cdc = self.controls["data"]
        for rc, key in enumerate(cdc):
            if rc <= self.num_rows - 3:
                self.SetCellValue(rc, 0, key)  # Name col
                self.SetCellValue(rc, 1, cdc[key]["value"]) # value col
                self.SetCellValue(rc, 2, cdc[key]["help"])  # help col
            
        self.AutoSize()
        try:
            self.SetCornerLabelValue("Controls")
        except:
            pass
        col_labels = ["Name", "Value", "Help"]
        for num_col, label in enumerate(col_labels):
            self.SetColLabelValue(num_col, label)
        
        # https://en.wikipedia.org/wiki/List_of_colors_(compact)
        for n in range(rc):
            colors = self.controls["colors"]
            for m in range(num_col+1):
                self.SetCellBackgroundColour(n, m, colors[n%2])
        #self.ForceRefresh()
        
        self.Bind(wxgrid.EVT_GRID_CELL_CHANGED, self.OnCellChange)
        
    def OnCellChange(self, event):  # Update the content of data with the user edit
        """
            The function responds to a change of the cell value at event.Row, event.Col.
            
            It saves the changes into the "display_controls.json" file.
        """
        # print(event.Row, event.Col)  # Show which cell the user changed
            
        if event.Col == 1:
            keys = list(self.controls["data"])
            self.controls["data"][keys[event.Row]]["value"] = self.GetCellValue(event.Row, 1)
            if 0:
                with open(self.ctrl_out_file, "w") as fout:
                    fout.write(json.dumps(self.caller.display_controls, indent=4))
            
                
