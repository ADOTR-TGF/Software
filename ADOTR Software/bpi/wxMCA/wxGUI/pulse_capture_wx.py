import wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
# from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import json
import init_operation
import graph_ctrl_grid as gcd

class PulseCaptureWindow(wx.Frame): 
    def __init__(self, parent, title): 
        super(HistogramWindow, self).__init__(parent, title = title)
        self.EMORPHO = 0x6001
        self.PMT1K = 0x101
        self.PMT3K = 0x103
        self.SIPM1K = 0x201
        self.SIPM3K = 0x203
        
        panel = wx.Panel(self, size = (700, 1000)) 
        
        init_operation.init_all(self)  # This also calls the operations manager to open communication with the MDS
        
        self.figure, self.axes = plt.subplots(figsize=(4,3))  # figsize is in inch
        #print(self.figure)
        self.canvas = FigureCanvas(panel, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        
        self.cursor_text = wx.StaticText( self, wx.ID_ANY, "X,Y =", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.cursor_text.Wrap( -1 )
        self.canvas.mpl_connect('motion_notify_event', self.onCursorMotion)
        
        self.box_local = wx.BoxSizer(wx.VERTICAL)
        self.box_local.Add(self.canvas, 1, wx.TOP | wx.LEFT )
        self.box_local.Add(self.toolbar, 0, wx.LEFT)
        self.box_local.Add(self.cursor_text,0, wx.RIGHT)
        
        # Make a list of action buttons
        self.button_list = []
        button = wx.Button(panel, id = wx.ID_ANY, label="New", name="start_pulse")
        self.button_list += [button]
        
        button = wx.Button(panel, id = wx.ID_ANY, label="New", name="save_pulse")
        self.button_list += [button]
        
        # Put all buttons in a horizontal sizer
        self.button_box = wx.BoxSizer(wx.HORIZONTAL)
        for button in self.button_list:
            button.Bind(wx.EVT_BUTTON, self.OnClicked)
            self.button_box.Add(button, 0, wx.RIGHT, 10)
        # Add buttonbox to the vertical stack
        self.box_local.Add(self.button_box, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 10)
        
        # Make the editable controls
        # self.graph_ctrl = gcd.StatusPanel(self)
        self.graph_ctrl = gcd.StatusGrid(panel, self)
        self.box_local.Add(self.graph_ctrl, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 10)
        
        #self.Centre() 
        #self.Show()
        #self.toolbar.update()
        self.SetSizer(self.box_local)
        self.box_local.SetSizeHints(self)
        self.Fit()
        

    def OnClicked(self, event): 
        name = event.GetEventObject().GetName()
        getattr(self, name)()  # Call the function that bears the button's name
        
        
    def onCursorMotion(self, event):
        """
            Ideally this event will carry the cursor x/y coordinates in units of the Matplotlib axes.
        """
        
        if event.xdata is None or event.ydata is None:
            pass
        else:
            self.cursor_text.SetLabelText("X,Y = {:.4f}, {:.4f}".format(event.xdata, event.ydata))
            
    def start_pulse(self):
        num_pulses = max(1, float(self.display_ctrl["pulse"]["num_pulses"]["value"]))
        pulse_list = []
        out_file = self.display_ctrl["pulse"]["data"]["file"]["value"]
        for n in range(num_pulses):
            self.om.submit(self.commands["start_trace"])
            while True:
                fpga_results = self.om.submit(self.commands["fpga_results"])[self.om.sn]
                if fpga_results["user"]["trace_done"]:
                    break
            pulse = self.om.submit(self.commands["read_trace"])[self.om.sn]
            if len(pulse_list) < 100:
                pulse_list += [pulse["fields"]["trace"]]
            if num_traces > 10:
                with open(out_file, 'a') as fout:
                    pulse["comment"] = self.display_ctrl["pulse"]["data"]["comment"]["value"]
                    fout.write(json.dumps(pulse)+'\n')
        
        self.pulse = pulse
        dt = 1.0e6/self.adc_sr
        plen = len(pulse["fields"]["trace"])
        x_data = [ n*dt for n in range(plen)]  
        import plot_control as pc
        self.line_plots(x_data, pulse_list, pc.trace_plot_ctrl)
        self.canvas.draw()
        
    def save_pulse(self):
        with open(out_file, 'a') as fout:
            self.pulse["comment"] = self.display_ctrl["pulse"]["data"]["comment"]["value"]
            fout.write(json.dumps(self.pulse)+'\n')
        
    
    def line_plots(self, x_data, y_data, ctrl):
    
        #colors = ["DodgerBlue", "OrangeRed", "Grey"]

        num_lines = len(y_data)
        lps = []
        for n in range(num_lines):
            lps += [self.axes.plot(x_data, y_data[n])]
            # ctrl['line_ctrl']["color"] = colors[n]
            plt.setp(lps[-1], **ctrl['line_ctrl'])

        self.axes.set_xlabel(ctrl['labels']['xlabel'] , **ctrl['labels']['xlabel_ctrl'])
        self.axes.set_ylabel(ctrl['labels']['ylabel'], **ctrl['labels']['ylabel_ctrl'])
        self.axes.set_title(ctrl['labels']['title'], **ctrl['labels']['title_ctrl'])
        self.axes.grid(**ctrl['grid_ctrl'])
        self.axes.set(**ctrl['axis_ctrl'])

        if 0:
            bbox_args = dict(boxstyle="round", pad=0.5, ec=colors[0], fc=(0.9, 0.9, 0.9, 0.9), linewidth=2)  # fill, bounds(l,b,w,h) are ignored
            comment = "Beta"  # Empty string nixes the display 
            self.axes.annotate(comment, fontsize=10,
                        xycoords='axes fraction', xy=(0.65, 0.90), ha="left", va="bottom", bbox=bbox_args)

   
def main():             
    app = wx.App() 
    panel = Mywin(None,  'Histogram')
    panel.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    main()
    
    
"""
Notes:

https://wxpython.org/Phoenix/docs/html/sizers_overview.html#sizers-overview

"""