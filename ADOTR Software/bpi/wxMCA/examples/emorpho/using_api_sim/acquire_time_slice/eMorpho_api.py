# release public
from __future__ import division
import array
import struct
import time
import eMorpho_data as emd

"""
This is the API layer for communication with a radiation detector with a bpi_usb USB interface.
It exchanges data with the driver layer exclusively via byte arrays.  The write and read function in this file are the 
switchboard where data are interpreted and the data exchange protocol is being enforced.

The data exchange is performed via a data port.  Sending header data to the bpi_usb.COMMAND_EP programs the data port 
and bulk data sent to the bpi_usb.DATA_EP will then be routed to the correct destination.  By the same token, 
preparing a read is also done by first sending data to the data port.  The ARM MCU then prepares the first buffer 
of data before the client sends the USB read command.
"""

"""
    Command structure:
    {
        # serial number or list of serial numbers; if missing or empty list: do all units
        'sn': ['123456789ABCDEF123456789ABCDEF'],  
        'dir': 'read',  # read, short_write,  write, rmw; 
        'memory': 'ram',  # ram or flash (flash = non-volatile memory)
        'type': 'sm_cmd',  # name space of the command
        'name': 'fpga_ctrl',  # name of the command
        'num_items': 16,  # To read a non-default number of items
        'ctrl': [],  # Control data written to mca.command_out; only for FPGA control or action registers 
        'data': []   # Data to be routed via the data endpoints.
    }
    
"""

item_size_dict = {'H': 2, 'I': 4, 'f': 4}  # Bytes per data item, depending on the data_type

# List of command targets
# Objects will support read, short_write, write, rmw as appropriate
# Objects will support cmd['memory']='flash' as appropriate.
make_new_io_obj = {
    'fpga_ctrl': emd.fpga_ctrl,
    'fpga_statistics': emd.fpga_statistics,
    'fpga_results': emd.fpga_results,
    'fpga_histogram': emd.fpga_histogram,
    'fpga_list_mode': emd.fpga_list_mode,
    'fpga_trace': emd.fpga_trace,
    'fpga_user': emd.fpga_user,
    'fpga_weights': emd.fpga_weights,
    'fpga_time_slice': emd.fpga_time_slice,
    'fpga_lm_2b': emd.fpga_lm_2b,
}


def process_cmd(user_cmd, mca_dict):
    """
    A user_cmd is a dictionary with keys as shown above

    :param user_cmd:  A dictionary of command data and controls
    :param mca_dict:  A dictionary of mca objects; keys are the unique, and immutable, serial numbers
    :return: Dictionary of read-back data with serial numbers as the keys

    """
    cmd = {
        # serial number or list of serial numbers; if missing or empty list: do all units
        'dir': 'read',  # read, write;
        'memory': 'ram',  # ram or flash (flash = non-volatile memory)
        'name': 'fpga_ctrl',  # name of the command
        'num_items': 0,  # To read a non-default number of items
        'data': {'registers': [], 'fields': [], 'user': []}   # Data to be routed via the data endpoints.
    }
    cmd.update(user_cmd)  # Update with data from the user command

    # Create a list of mca on which to perform the command
    # user_cmd['sn'] can be missing => perform on all mca
    # user_cmd['sn'] can be a string => perform on that mca
    # user_cmd['sn'] can be an empty list => perform on all mca
    # user_cmd['sn'] can be a list of strings => perform on all mca in the list
    mca_action = {}  # Dictionary of mca on which to perform the command.
    # print("Serial Number:", cmd['sn'], isinstance(str(cmd['sn'].encode("ascii")), str))
    
    if 'sn' not in cmd:  # sn omitted => perform command on all mca devices.
        mca_action = mca_dict
    elif isinstance(cmd['sn'], str) and len(cmd['sn'])>0:  # Single serial number as a string
        mca_action[cmd['sn']] = mca_dict[cmd['sn']]
    elif isinstance(cmd['sn'], list):  # List of multiple serial numbers (must be strings)
        if len(cmd['sn']) == 0:
            mca_action = mca_dict  # sn omitted => perform command on all mca devices.
        else:
            for sn in cmd['sn']:
                mca_action[sn] = mca_dict[sn]
    
    cmd_out_list = [0]*32  # 32 uint16_t integers; ie data_type='H'
    if "ctrl" in cmd:  # user_cmd['ctrl'] are always 16-bit integers
        if isinstance(cmd['ctrl'], list):
            num_ctrl = min(len(cmd['ctrl']), 30)
            ctrl = cmd['ctrl']
            for n in range(num_ctrl):
                cmd_out_list[n+2] = int(ctrl[n]) & 0xFFFF

    data_out_dict = {}
    data_out_list = []
    if cmd['dir'] == "write":  # A write command only takes a list as data
        data_out_list = cmd['data']['registers']
    # A rmw command takes a dictionary with 'user' and 'fields' keys, but no 'registers'
    elif cmd['dir'] == "rmw":
        data_out_dict = cmd['data']

    for sn in mca_action:
        mca_action[sn].cmd = cmd
        mca_action[sn].cmd_out_list = cmd_out_list
        mca_action[sn].data_out_dict = data_out_dict
        mca_action[sn].data_out_list = data_out_list

    in_dict = {}
    for sn in mca_action:
        perform_cmd(mca_action[sn])
        in_dict[sn] = mca_action[sn].data_in_dict

    return in_dict


def perform_cmd(mca):
    """
    Create a local io_obj according to the command name and execute the command.
    :param mca: An mca object describes one eMorpho
    :return: None
    """
    io_obj = make_new_io_obj[mca.cmd["name"]]()
    io_obj.adc_sr = mca.adc_sr
    
    if mca.cmd['memory'] == "ram" and mca.cmd['dir'] == "read":
        read_ram(mca, io_obj)
        return None

    if mca.cmd['memory'] == "flash" and mca.cmd['dir'] == "read":
        read_flash(mca)
        return None

    if mca.cmd['dir'] == 'short_write':  # It is a write command where exactly 32-bytes of data are transmitted
        """Input is mca.data_out_list which is written to the target.  This is not a read-modify-write command
        """
        short_write(mca)
        return None

    if mca.cmd['memory'] == "ram" and mca.cmd['dir'] == "write":
        write_ram(mca, io_obj)
        return None

    if mca.cmd['memory'] == "flash" and mca.cmd['dir'] == "write":
        write_flash(mca)
        return None

    if mca.cmd['dir'] == 'rmw':  # It is a read-modify-write command
        read_modify_write_ram(mca, io_obj)
        return None


def read_ram(mca, io_obj):
    offset = 0
    if "offset" in mca.cmd:
        offset = mca.cmd["offset"]
    # Host omits this, or sets this to zero to get default value for num_items
    if 'num_items' not in mca.cmd or mca.cmd['num_items'] == 0:
        mca.cmd['num_items'] = io_obj.num_items

    # Now read the data and convert to higher level data
    mca._com_p[0] = 0
    mca._com_p[1] = io_obj.cmd_addr
    mca._com_p[2] = mca.cmd['num_items']
    mca._com_p[3] = offset
    mca._com_p[4] = int(1.0e6*(time.time() - mca.start_up_time))
    
    mca.update()
    mca.data_in_list = struct.unpack_from("<{}d".format(mca.cmd['num_items']), mca._host_in)
    mca.data_in_list = [int(d) for d in mca.data_in_list]
    io_obj.registers = mca.data_in_list
    io_obj.registers_2_fields()
    io_obj.fields_2_user()

    mca.data_in_dict = {'registers': io_obj.registers, 'fields': io_obj.fields, 'user': io_obj.user}
    return None


def write_ram(mca, io_obj):
    """
        Write 16-bit data to the simulated device.
        This is not a read-modify-write command
    """
    if 'num_items' not in mca.cmd or mca.cmd['num_items'] == 0:
        mca.cmd['num_items'] = io_obj.num_items
    mca._com_p[0] = 1
    mca._com_p[1] = io_obj.cmd_addr
    mca._com_p[2] = mca.cmd['num_items']
    mca._com_p[3] = 0
    mca._com_p[4] = int(1.0e6*(time.time() - mca.start_up_time))
    struct.pack_into("<{}d".format(mca.cmd['num_items']), mca._host_out, 0, *mca.data_out_list)
    mca.update()
    return None

    
def read_flash(mca):
    mca._com_p[0] = 0
    mca._com_p[1] = 16
    mca._com_p[2] = 17
    mca._com_p[3] = 0
    mca._com_p[4] = int(1.0e6*(time.time() - mca.start_up_time))
    mca.update()
    mca.data_in_list = struct.unpack_from("<17d", mca._host_in)
    mca.data_in_list = [int(d) for d in mca.data_in_list]
    
    ctrl_obj = make_new_io_obj["fpga_ctrl"]()
    ctrl_obj.adc_sr = mca.adc_sr

    # Convert register data to 'fields' and 'user'
    nv_mem_valid = mca.data_in_list[0] == 0x8003
    if nv_mem_valid:
        ctrl_obj.registers = mca.data_in_list[1:17]
        ctrl_obj.registers_2_fields()
        ctrl_obj.fields_2_user()
        mca.data_in_dict = {"registers": mca.data_in_list[1:17], "fields": ctrl_obj.fields, "user": ctrl_obj.user}
    else:
        mca.data_in_dict = {"registers": mca.data_in_list[0:17]}

    return None


def write_flash(mca):
    ctrl_obj = make_new_io_obj["fpga_ctrl"]()
    read_ram(mca, ctrl_obj)

    mca.data_out_list = [0x8003] + ctrl_obj.registers
    mca._com_p[0] = 1
    mca._com_p[1] = 16
    mca._com_p[2] = 17
    mca._com_p[3] = 0
    mca._com_p[4] = int(1.0e6*(time.time() - mca.start_up_time))
    struct.pack_into("<17d", mca._host_out, 0, *mca.data_out_list)
    mca.update()

    return None


def read_modify_write_ram(mca, io_obj):
    """
       Input is mca.data_out_dict.  That dictionary contains the values that should be updated inside the device.
       This is a read-modify-write command:
       Read data from device and create a dictionary,
       Update that dictionary with the user-supplied values,
       Write the data back to the device.
    """

    mca.cmd['num_items'] = io_obj.num_items  # Use the default number to ensure correct conversion to 'fields'
    
    mca._com_p[0] = 0
    mca._com_p[1] = io_obj.cmd_addr
    mca._com_p[2] = mca.cmd['num_items']
    mca._com_p[3] = 0
    mca._com_p[4] = int(1.0e6*(time.time() - mca.start_up_time))
    mca.update()
    mca.data_in_list = struct.unpack_from("<{}d".format(mca.cmd['num_items']), mca._host_in)
    mca.data_in_list = [int(d) for d in mca.data_in_list]
    io_obj.registers = mca.data_in_list
    io_obj.registers_2_fields()
    io_obj.fields_2_user()
        
    # Update the dictionary with the user-supplied data and convert back to an updated list
    if "fields" in mca.data_out_dict:
        io_obj.fields.update(mca.data_out_dict["fields"])
        io_obj.fields_2_user()
        io_obj.fields_2_registers()
    if "user" in mca.data_out_dict:
        io_obj.user.update(mca.data_out_dict["user"])
        io_obj.user_2_fields()
        io_obj.fields_2_registers()

    io_obj.user_2_fields()
    io_obj.fields_2_registers()
    mca.data_out_list = io_obj.registers
    
    # Write data back to the device
    mca._com_p[0] = 1
    mca._com_p[1] = io_obj.cmd_addr
    mca._com_p[2] = mca.cmd['num_items']
    mca._com_p[3] = 0
    mca._com_p[4] = int(1.0e6*(time.time() - mca.start_up_time))
    struct.pack_into("<{}d".format(mca.cmd['num_items']), mca._host_out, 0, *mca.data_out_list)
    mca.update()

    # Report back the state of the eMorpho FPGA controls
    mca.data_in_dict = {'registers': io_obj.registers, 'fields': io_obj.fields, 'user': io_obj.user}
    
    return None
