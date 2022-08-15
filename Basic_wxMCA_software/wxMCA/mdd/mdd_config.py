#!/usr/bin/python
#
# version 1.0
suspend = 0  # Set to 1 if you want the MDD to be inactive on the next launch.
mds_present = True  # True or False, 1 or 0

mds_ip = "tcp://localhost:5507"
stabilizer_ip = "tcp://localhost:5508"
monitor_ip = "tcp://localhost:5509"
bridge_ip = "tcp://localhost:5510"

mdd_ip = "tcp://0.0.0.0:5506"
timeout = 10  # seconds
repeat_period = 10  # seconds

# Windows needs an absolute path
mds_win_path = "C:\bpi\wxMCA\mds\run_mds.cmd"

mds_linux_path = "../mds_py_universal/MDS.py"
