import array
import json
import time
import zmq
import communication as com

SPI_BOOT_FPGA = 0
SPI_FPGA_ERASE = 1
SPI_FPGA_RESTORE = 2
SPI_USER_ERASE = 3
SPI_HISTO_ERASE = 4
SPI_FLASH_WRITE = 5

"""
    In the PMT-2000 it is possible to update the FPGA configuration by writing a new
    configuration into the SPI flash memory.  There is room for up to 6 configurations,
    numbered from 0 to 5.

    Configuration no. 6 is the default configuration that ships with the PMT-2000.
    It can not be overwritten.  Users can restore this factory default into config=0
    in case they need to.

    The other SPI flash memory areas are the User area and the histogram area.

"""

def erase_fpga(config):
    """
    We assume that only one PMT-2000 is attached, and that the MCA Data Server is running.
    Before loading
    The PMT-2000 ships with one FPGA configuration at config=0. Customized software
    may have up to 6 configurations config = 0, .., 5

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

    config = config % 6  # Number of the FPGA configuration (0 through 5 are possible)
    # Construct command and send; notice the "short_write" direction.
    cmd = {"type": "mca_cmd", "name": "arm_spi_cmd", "dir": "short_write", "sn": sn, "ctrl": [SPI_FPGA_ERASE, config]}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')

def restore_fpga(config):
    """
    We assume that only one PMT-2000 is attached, and that the MCA Data Server is running.

    The PMT-2000 ships with one FPGA configuration at config=0. Customized software
    may have up to 6 configurations config = 0, ... , 5

    The function copies configuration no. config into position 0.

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

    config = config % 6  # Number of the FPGA configuration (0 through 5 are possible)
    # Construct command and send; notice the "short_write" direction.
    cmd = {"type": "mca_cmd", "name": "arm_spi_cmd", "dir": "short_write", "sn": sn, "ctrl": [SPI_FPGA_RESTORE, config]}
    mds_client.send_and_receive(json.dumps(cmd).encode('utf-8')).decode('utf-8')


def write_fpga(fpga_bin_file, config):
    """
    We assume that only one PMT-2000 is attached, and that the MCA Data Server is running.

    The PMT-2000 ships with one FPGA configuration at config=0. Customized software
    may have up to 6 configurations config = 0, ... , 5

    The function copies the content of fpga_bin_file into configuration no. config
    on the SPI-flash on the MCA-2000 PCB.

    :param fpga_bin_file: Data file containing a valid FPGA configuration
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

    config = config % 7  # Number of the FPGA configuration (0 through 6 are possible)

    # Read fpga_configuration
    with open(fpga_bin_file, "rb") as fin:
        fpga_bin = fin.read()
    PL = 256  # page length of the memory
    FL = len(fpga_bin) % PL  # fragment_length
    TL = ((len(fpga_bin)-1) // PL + 1)*PL
    bytes_out = array.array('B', fpga_bin)
    if FL > 0:
        bytes_out.extend([0]*(PL-FL))
        
    with open("./data/test.bin", "wb") as fout:
        fout.write(bytes_out)
    print("Length of config file = ", len(fpga_bin))

    # To check the flash_busy flag
    cmd_check = {"type": "mca_cmd", "name": "arm_status", "dir": "read", "sn": sn}
    if False:    
        # Erase the configuration memory on the MCA-2000 board
        cmd_erase = {"type": "mca_cmd", "name": "arm_spi_cmd", "dir": "short_write", "sn": sn,
                     "ctrl": [SPI_FPGA_ERASE, config]}
        mds_client.send_and_receive(json.dumps(cmd_erase).encode('utf-8')).decode('utf-8')
        while True:
            time.sleep(0.010)
            msg = mds_client.send_and_receive(json.dumps(cmd_check).encode('utf-8')).decode('utf-8')
            ret = json.loads(msg)
            if ret[sn]["user"]["flash_busy"] == 0:
                break

    # Write the FPGA configuration
    
    cmd_to_buffer = {"type": "mca_cmd", "name": "arm_spi_fpga", "dir": "write", "sn": sn}

    num_pages = len(bytes_out)//PL
    for n in range(num_pages):
        registers = bytes_out[n*PL: (n+1)*PL]
        
        cmd_to_buffer["ctrl"] = [(n*PL)%65536, (n*PL)//65536]  # 16-bit words, LSB first
        cmd_to_buffer["data"] = {"registers": list(registers)}
        #if n==0:
        #    print(list(registers))

        mds_client.send_and_receive(json.dumps(cmd_to_buffer).encode('utf-8')).decode('utf-8')
        while True:
            time.sleep(0.010)
            msg = mds_client.send_and_receive(json.dumps(cmd_check).encode('utf-8')).decode('utf-8')
            ret = json.loads(msg)
            if ret[sn]["user"]["flash_busy"] == 0:
                break


def read_spi_mem(out_file, address, num_bytes):
    """
    We assume that only one PMT-2000 is attached, and that the MCA Data Server is running.

    The PMT-2000 has an attached SPI flash memory for FPGA configurations, user data and histogram data.

    :param out_file: Data file to store the read back data
    :param address: Start address in bytes in the SPI flash memory
    :param num_bytes: Number of bytes to read; will be rounded up to integer multiples of 256
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

    PL = 256  # page length of the data buffer in the ARM processor
    num_pages = (num_bytes-1) // PL + 1
    cmd_read = {"type": "mca_cmd", "name": "arm_spi_mem", "dir": "read", "sn": sn}
    
    # Open output file
    fout = open(out_file, "wb")
    for n in range(num_pages):
        cmd_read["ctrl"] = [(address+n*PL)%65536, (address+n*PL)//65536]  # 32-bit address split into two 16-bit words.
        msg = mds_client.send_and_receive(json.dumps(cmd_read).encode('utf-8')).decode('utf-8')
        ret = json.loads(msg)
        fout.write(array.array('B', ret[sn]["registers"]))
        
    fout.close()
    
    

if 1:
    erase_fpga(0)
if 1:
    write_fpga(fpga_bin_file="./data/Morpho_bitmap.bin", config=0)
    time.sleep(2)
read_spi_mem("data/spi_mem.bin", 0*256, 279*256)

