import json
import time
import zmq
import communication as com


def log_fpga_statistics(file_name="./data/counting_log.json", dwell_time=10, max_lines=1000):
    """
    We assume that only one counter3k is attached, and that the mca3k_server is running.
    Log counting data to a file, one json datum per line.

    :param file_name: Write the resulting fpga_statistics data to this file
    :param dwell_time: Wait time in seconds for each data point
    :param max_lines: Maximum number of lines written to file
    :return: None
    """

    mds_ip = "tcp://127.0.0.1:5507"
    mds_client = com.zmq_device(mds_ip, "client")

    cmd = {"type": "server_cmd", "name": "identify"}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    ret = json.loads(msg)
    print(ret)
    mca_list = ret['mca_id']
    for mca in mca_list:
        sn = list(mca)[0]
        if int(mca[sn],16) == 5:            
            break
    print("Counter S/N {}".format(sn))
    
    # Clear statistics
    cmd = {"type": "mca_cmd", "name": "fpga_action",  "dir": "rmw", "sn": sn, 
           "data": {"fields": {"clear_statistics": 1}, "user":{}}}
    msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
    
    for line_count in range(max_lines):
        # Read statistics and store
        cmd = {"type": "mca_cmd", "name": "fpga_statistics", "dir": "read", "sn": sn}
        msg = mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        
        fpga_statistics = ret[sn]["fields"]['bank_0']
        with open(file_name, 'a') as fout:
            fout.write(json.dumps(fpga_statistics) + "\n")
        
        time.sleep(dwell_time)

log_fpga_statistics(file_name="./data/counting_log.json", dwell_time=10, max_lines=3)

