import json
import time
import zmq
import communication as com


def log_x_temp(file_name, dwell_time=5, number_of_measurements=10):
    """
    We assume that only one SiPM-Morpho is attached, and that the mca3k_server is running.
    Continuously read the current status data from the ARM processor and log the external temperature.

    :param file_name: Write the temperature data to this file.
    :param dwell_time: Time between measurements, in seconds
    :param number_of_measurements: Number of measurements to record
    :return:
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

    with open(file_name, 'w') as fout:
        pass
    for n in range(number_of_measurements):
        time.sleep(dwell_time)
        # Read arm_status
        cmd = {"type": "mca_cmd", "name": "arm_status", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        x_temperature = ret[sn]["fields"]["x_temperature"]
        
        with open(file_name, 'a') as fout:
            fout.write("{:.3f}\n".format(x_temperature))


log_x_temp(file_name="./data/x_temp.csv", dwell_time=5, number_of_measurements=20)