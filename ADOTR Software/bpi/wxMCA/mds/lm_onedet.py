#!/usr/bin/python3.8
#
from __future__ import division

import json
import zmq
import communication as com
import lm as lm
import sys

# Check to see if the desired SN is there.  Open up a client to the eMorpho
# and get list of connected devices

mds_client = com.zmq_device("tcp://127.0.0.1:5507", "client")  # Communicate with MDS
cmd = {"type": "server_cmd", "name": "hello"}
msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
ret = json.loads(msg)
sn_list = ret['sn_list']
sn = sys.argv[1]
sn_short = sys.argv[2]
if sn not in sn_list:
    sys.exit("Desired serial number "+sn_short+" not found.\n")
    
detlabel = sys.argv[3]
rootdir = sys.argv[4]
num_buffers=int(sys.argv[5])

#PLASTIC, NAI
#set trace trigger values:
snvalues = ['AFD8C28B54525251202020412C2B5FF', 'ACC715C54525251202020412DA5FF']  # *C2B5FF is 455 plastic.  *2DA5FF is 464 Nai.

#If sn is not n snvalues, this will throw an exception and die, which is just as well.
det = snvalues.index(sn)

#these arrays of trace trigger params run across the 5 traces horizontally and the 4 detectors vertically.
#determines pretrigger data
cvalues = [[4096,1024,1024,1024,1024],
           [4096,1024,1024,1024,1024]]

nvalues=[[100,100,100,100,100],
         [30,30,30,30,30]]

#trigger level
mvalues=[[12000,24000,48000,96000,192000],
         [10500,21000,42000,84000,168000]] #NaI traces spend more time above threshold

for i in [0,1,2,3,4]:
    N_field = "xtrn{}".format(i)
    M_field = "xtrm{}".format(i)
    C_field = "xtrc{}".format(i)
    print(det,i)
    print(N_field,nvalues[det][i])
    print(M_field,mvalues[det][i])
    print(C_field,cvalues[det][i])
    
    cmd_set_xtr_ctrl = {"type": "mca_cmd", "name": "fpga_tgf_ctrl", "dir": "rmw", "sn": sn,  
                        "data": {"fields": {N_field: nvalues[det][i],
                                            M_field: mvalues[det][i],
                                            C_field: cvalues[det][i]}}}
    msg = mds_client.send_and_receive(json.dumps(cmd_set_xtr_ctrl).encode('utf-8')).decode('utf-8')  

    
lm.xml22_daq(num_buffers, sn,sn_short,detlabel,rootdir)

#example for a plastic detector:
#python3.7 lm_onedet.py ADD37026323151512020204B2D276FF 269 pla Detector1 20
