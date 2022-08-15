import json
import time
import zmq
import communication as com

SPI_BOOT_FPGA = 0

def boot_fpga(config):
    """
    We assume that only one PMT-2000 is attached, and that the MCA Data Server is running.
    We also assume that there is a valid FPGA configuration in the SPI flash memory.
    The PMT-2000 ships with one FPGA configuration ad config=0. Customized software
    may have up to 7 configurations config = 0, .., 6

    :param config
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

    config = min(max(0, config), 6)  # Number of the FPGA configuration (0 through 6 are possible) 
    # Construct command and send; notice the "short_write" direction.
    cmd = {"type": "mca_cmd", "name": "arm_spi", "dir": "short_write", "sn": sn, "ctrl": [SPI_BOOT_FPGA, config]}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')


boot_fpga(file_name="./data/arm_ctrl.json")
