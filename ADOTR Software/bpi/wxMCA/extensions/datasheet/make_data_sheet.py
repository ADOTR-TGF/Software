import data_sheet
import json

# Please choose the correct setup json file with the same VID as the product for making a data sheet. 
# The product VID can be found from the terminal after starting the MCA server.
# setup json file is located in setup folder.

with open('./setup/setup_0x103.json') as fin:
    setup = json.loads(fin.read())
    
def make_data_sheet():
    DS = data_sheet.DataSheet(setup)
    DS.mca_plot_fit()
    DS.make_data_sheet()      

make_data_sheet();

    #DS.mca_display()  # Display only

