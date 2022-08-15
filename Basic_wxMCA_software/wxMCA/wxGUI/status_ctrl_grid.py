import json
import wx
import wx.grid as wxgrid  # Why can't I use wx.grid directly?

class StatusPanel(wx.Panel):  # Editable data display
    """Panel class to contain frame widgets."""
    def __init__(self, parent, row_format, data):
        super(StatusPanel, self).__init__(parent)
        self.data_ctrl = row_format["source"]
        self.display_ctrl = row_format["self"]
        """Create and populate main sizer."""
        self.stGrid = StatusGrid(self, row_format, data)
        sizer = wx.BoxSizer() # (orientation = wx.VERTICAL or wx.HORIZONTAL)
        sizer.Add(self.stGrid)
        self.SetSizer(sizer)

class StatusGrid(wxgrid.Grid):
    def __init__(self, parent, row_format, data):
        """ 
            parent: is the parent window into which this widget is going to be inserted
            row_format: Names, min_max boundaries and help strings for fields and user data; This may be a subset of all available data
            data: are the actual version or status data read from the MCA
        """
        super(wxgrid.Grid, self).__init__(parent, id=wx.ID_ANY)
        self.data = data
        self.row_format = row_format
        self.parent = parent

        # self.Create(parent, id=wx.ID_ANY)
        self.num_rows = 0
        for key in row_format:
            if key in row_format["displays"]:
                self.num_rows += len(row_format[key])
            
        self.CreateGrid(self.num_rows, 7) # cols: index, name, value, min_val, max_val, help

        rc = 0  # row count
        for tipo in row_format["displays"]:
            for item in row_format[tipo]:
                self.SetCellValue(rc, 0, tipo)  # Show data type ("fields" or "user")
                self.SetCellValue(rc, 1, item["idx"])  # Index col
                self.SetCellValue(rc, 2, item["name"])  # Name col
                self.SetCellValue(rc, 3, str(self.data[tipo][item["name"]]))  # value col
                self.SetCellValue(rc, 4, item["min"])  # min_val col
                self.SetCellValue(rc, 5, item["max"])  # max_val col
                self.SetCellValue(rc, 6, item["help"])  # help col
                rc += 1
            
        self.AutoSize()
        try:
            self.SetCornerLabelValue(parent.data_ctrl)
        except:
            pass
        col_labels = ["Field", "idx", "Name", "Value", "Min", "Max", "Help"]
        for n, label in enumerate(col_labels):
            self.SetColLabelValue(n, label)
        
        # https://en.wikipedia.org/wiki/List_of_colors_(compact)
        for n in range(rc):
            colors = row_format["colors"][self.GetCellValue(n, 0)]
            for m in range(7):
                self.SetCellBackgroundColour(n, m, colors[n%2])
        #self.ForceRefresh()
        
        
        self.Bind(wxgrid.EVT_GRID_CELL_CHANGED, self.OnCellChange)
        
    def OnCellChange(self, event):  # Update the content of data with the user edit
        """
            The function responds to a change of the cell value at event.Row, event.Col.
            First, it updates the corresponding data[][] value.
            Next it seeks to align "fields" and "user" data.
            If the user edits a cell containing "fields" data, it is possible that a "user" data cell needs to change as well.
            In the same manner, editing a "user" cell may require updating a "fields" cell.  Only the mds/mcaxx_data.py file knows.
            So we send a command to the MDS to update fields or user data as needed.
            
            In order to avoid handing down a pointer to the operations manager (self.MCA_IO in the top window), we use GetTopLevelParent
            to reach the main_frame window where the operations manager can be found.  The om communicates with the MDS and thus the MCA.
        """
        # print(event.Row, event.Col)  # Show which cell the user changed
        if self.row_format["editable"] == "No":
            return
            
        if event.Col == 3:
            tipo = self.GetCellValue(event.Row, 0)
            name = self.GetCellValue(event.Row, 2)
            val = float(self.GetCellValue(event.Row, 3))
            self.data[tipo].update({name: val})
                    
            # Align fields and user data
            window = self.GetTopLevelParent()
            if tipo == "fields":
                self.data = window.MCA_IO.submit_command(window.MCA["sn"], {"name": self.row_format["source"], "dir": "fields_to_user", "data": self.data})[window.MCA["sn"]]
            if tipo == "user":
                self.data = window.MCA_IO.submit_command(window.MCA["sn"], {"name": self.row_format["source"], "dir": "user_to_fields", "data": self.data})[window.MCA["sn"]]
            
            # Update the display
            rc = 0  # row count
            for tipo in self.row_format["displays"]:
                for item in self.row_format[tipo]:
                    self.SetCellValue(rc, 0, tipo)  # Show data type ("fields" or "user")
                    self.SetCellValue(rc, 1, item["idx"])  # Index col
                    self.SetCellValue(rc, 2, item["name"])  # Name col
                    self.SetCellValue(rc, 3, str(self.data[tipo][item["name"]]))  # value col
                    self.SetCellValue(rc, 4, item["min"])  # min_val col
                    self.SetCellValue(rc, 5, item["max"])  # max_val col
                    self.SetCellValue(rc, 6, item["help"])  # help col
                    rc += 1
                
