import json
import wx
import wx.grid as wxgrid  # Why can't I use wx.grid directly?

class StatusPanel(wx.Panel):  # Editable data display
    """Panel class to contain frame widgets."""
    def __init__(self, parent, record):
        super(StatusPanel, self).__init__(parent)
        self.data_ctrl = record["type"]
        #self.display_ctrl = row_format["self"]
        """Create and populate main sizer."""
        self.stGrid = StatusGrid(self, record)
        sizer = wx.BoxSizer() # (orientation = wx.VERTICAL or wx.HORIZONTAL)
        sizer.Add(self.stGrid)
        self.SetSizer(sizer)

class StatusGrid(wxgrid.Grid):
    def __init__(self, parent, record):
        """ 
            parent: is the parent window into which this widget is going to be inserted
            row_format: Names, min_max boundaries and help strings for fields and user data; This may be a subset of all available data
            data: are the actual version or status data read from the MCA
        """
        super(wxgrid.Grid, self).__init__(parent, id=wx.ID_ANY)
        self.record = record
        self.parent = parent

        # self.Create(parent, id=wx.ID_ANY)
        self.num_rows = len(record["display"])
            
        self.CreateGrid(self.num_rows, 3) # cols: name, value, help
        
        rc = 0  # row count
        for item in record["display"]:
            self.SetCellValue(rc, 0, item["name"])  # Name col
            self.SetCellValue(rc, 1, item["format"].format(item["value"]))  # value col
            self.SetCellValue(rc, 2, item["help"])  # help col
            rc += 1
            
        self.AutoSize()
        try:
            self.SetCornerLabelValue(parent.data_ctrl)  # This appears only in wxPyton 4.1.0
        except:
            pass
        col_labels = ["Name", "Value", "Help"]
        for n, label in enumerate(col_labels):
            self.SetColLabelValue(n, label)
        
        # https://en.wikipedia.org/wiki/List_of_colors_(compact)
        for n in range(rc):
            colors = record["colors"]
            for m in range(3):
                self.SetCellBackgroundColour(n, m, colors[n%2])
        #self.ForceRefresh()
        
        
        self.Bind(wxgrid.EVT_GRID_CELL_CHANGED, self.OnCellChange)
        
    def OnCellChange(self, event):  # Update the content of data with the user edit
        """
            The function responds to a change of the cell value at event.Row, event.Col.
            First, it updates the corresponding data[][] value.
        """
        # print(event.Row, event.Col)  # Show which cell the user changed
        if self.record["editable"] == "No":
            return
            
        if event.Col == 1:
            name = self.GetCellValue(event.Row, 0)
            val = self.GetCellValue(event.Row, 1)
            self.record["display"][event.Row].update({"value": val})
                    
            
            # Update the display
            rc = 0  # row count
            for item in self.record["display"]:
                self.SetCellValue(rc, 0, item["name"])  # Name col
                self.SetCellValue(rc, 1, item["format"].format(item["value"]))  # value col
                self.SetCellValue(rc, 2, item["help"])  # help col
                rc += 1
                
