import json
import time
import zmq
import communication as com


def program_arm_cal(file_name):
    """
    We assume that only one SiPM-Morpho is attached, and that the MCA Data Server is running.
    Upload an arm_cal data structure from file to the SiPM-Morpho.
    You can use lut_mode as a lock. If lut_mode == 1 => the user cannot read back the calibration data.
    To check, see out_file = "./data/arm_cal.json"

    :param file_name: Read the calibration lookup tables from this file
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
    
    with open(file_name, 'r') as fin:
        arm_cal_user_json = fin.read()
    arm_cal_fields = json.loads(arm_cal_user_json)
    
    # Write arm_cal data
    cmd = {"type": "sm_cmd", "name": "arm_cal", "dir": "rmw", "sn": sn,
           "data": {"fields": arm_cal_fields}}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

    # Read back and store
    # Read arm_cal data.  Note that if int(arm_cal[63]) & 0x1 == 1, 
    # (ie arm_cal_fields["lut_mode"] & 0x1 ==1) you cannot read back the data.
    cmd = {"type": "sm_cmd", "name": "arm_cal", "dir": "read", "sn": sn}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    arm_cal = ret[sn]["fields"]
    
    out_file = "./data/arm_cal.json"
    with open(out_file, 'w') as fout:
        fout.write(json.dumps(arm_cal) + ",\n")
    print("Output file: ", out_file)


program_arm_cal(file_name="./data/NaI_SN44.json")
