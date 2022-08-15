#!/usr/bin/python
#
# version 1.0
from __future__ import division
import communication as com
import time

def command(cmd):
	client = com.zmq_device("tcp://192.168.8.6:5520",type="client")
	client.send_and_receive('<mdd_cmd cmd="{}"></mdd_cmd>'.format(cmd))
	
command("stop_stabilizer")
#command("stop_mds")
command("start_mds")
#time.sleep(10)
#command("start_stabilizer")

