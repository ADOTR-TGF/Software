#!/usr/bin/env python
import mca_io
import wx
import MCA_Main

class MCA_Frame(wx.Frame):

    def __init__(self):
        super(MCA_Frame, self).__init__(None, id=wx.ID_ANY)

        self.count=0
    
        self.MCA_IO = mca_io.MCA_IO()
        self.device_list = list(self.MCA_IO.mca)
        self.device_map = {}
        for ind, dev in enumerate(self.device_list):
            self.device_map[dev] = ind

        self.SetTitle('Please select an MCA device.')
        self.SetSize(300, 300)
        self.CenterOnScreen()

        panel = wx.Panel(self, size = (3000, 3000))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.lstbox = wx.ListBox(panel, wx.ID_ANY, size = (300, -1), choices = self.device_list, style = wx.LB_SINGLE)
        self.txtbox = wx.StaticText(panel, style = wx.TE_MULTILINE, size = (300, 50))
        self.txtbox.SetLabelText("In order to make a new selection, please REOPEN wxMCA software. This window will be closed once selection is made.")

        self.sizer.Add(self.lstbox, 0 , wx.TOP | wx.EXPAND, 1)
        self.sizer.Add(self.txtbox, 0, wx.LEFT | wx.EXPAND, 1)
        self.SetSizer(self.sizer)
        self.sizer.SetSizeHints(self)

        self.Bind(wx.EVT_LISTBOX, self.OnList)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        self.SetSizeHints(minW = 300, minH = 300)
        self.Layout()
    
    def OnList(self, event):
        device_name = event.GetEventObject().GetStringSelection()
        self.Destroy()
        MCA_Main.main(self.device_map[device_name])


        

if __name__ == '__main__':
    mca_main = wx.App()
    main_frame = MCA_Frame()
    main_frame.Show()
    mca_main.MainLoop()