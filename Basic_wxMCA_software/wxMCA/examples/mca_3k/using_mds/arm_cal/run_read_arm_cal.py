import json
import time
import zmq
import communication as com


def read_arm_cal(file_name):
    """
    We assume that only one MCA-3K is attached, and that the mca3k_server is running.
    Read the arm_cal data structure from the MCA-3K.
    Note that lut_mode & 0x1 acts as a lock. If lut_mode & 0x1 == 1 => The user cannot read back the calibration data.
    To check, see out_file = file_name

    :param file_name: Write the calibration lookup tables from this file
    :return: None
    """

    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "hello"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    sn_list = ret['sn_list']
    for sn in sn_list:
        print("Serial number:", sn)
    sn = sn_list[0]  # We only use one attached device here
    
    """ Read arm_cal and store
    Read arm_cal data.  Note that if int(arm_cal[63]) & 0x1 == 1, 
    (ie arm_cal_fields["lut_mode"] & 0x1 ==1) you cannot read back the data.
    On the ARM processor arm_cal is only kept in flash memory, but you do not need to 
    set "memory": "flash"
    """
    cmd = {"type": "mca_cmd", "name": "arm_cal", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    arm_cal = ret[sn]["fields"]
    print(ret[sn]["registers"])
    
    with open(file_name, 'w') as fout:
        fout.write(json.dumps(arm_cal) + ",\n")

# Pick an appropriate calibration file, or provide your own
arm_cal_out_file = "./data/arm_cal.json"
read_arm_cal(arm_cal_out_file)  
