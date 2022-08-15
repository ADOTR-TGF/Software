#!/usr/bin/python3.7

import json

def load_params(filename):
    f=open(filename,"r")
    data = json.load(f)
    print(data['fpga_ctrl']['registers'])
    print(type(data['fpga_ctrl']['registers']))

load_params('../user/emorpho/settings/eRC4183_all_ctrl.json')



 
