import json
import time
import zmq
import communication as com


def read_lut(lut_file):
    """
    We assume that only one eMorpho is attached, and that the MCA Data Server is running.
    Here LUT designates a structure containing data for the temperature dependence of
    the operating voltage (ov), the digital gain (dg) and the LED response (led) as a 
    function of temperature.
    Read the lut data file and write the LUT dictionary

    :param lut_file: A json file that has the same dictionary as emorpho_data.fpga_lut.fields
    :return None
    
    """

    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Unique serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here
    
    # Read non-volatile memory
    cmd = {"type": "mca_cmd", "name": "fpga_lut", "dir": "read", "memory": "lut", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    with open(lut_file, "w") as fout:
        fout.write(json.dumps(ret, indent=4))

lut_file = "./data/lut_read.json"
read_lut(lut_file)

