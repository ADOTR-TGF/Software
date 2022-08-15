#include "mca1k_serial_device.h"
#include "mca1k_api.h"
#include "bpi_globals.h"

#include <stdio.h> // For debugging on a Raspberry Pi

void arm_version_read(struct mca_command *mca_cmd);

struct mca_command mca_cmd;

/*
    Transfer data to the MCA.
    The input structure contains all the necessary information to tell the MCA
    what kind of data are being sent, and if they should be also stored in non-volatile memory.
*/
void mca_write(struct mca_command *mca_cmd){
    mca_cmd -> cmd[0] = (mca_cmd->num_bytes << 16) + (mca_cmd->mem_type << 12) + (mca_cmd->com_address << 4) + mca_cmd->write_type;
    switch(mca_cmd->com_address){
        case ARM_CTRL:
        case ARM_CAL:
            bpi_write_buffer(mca_cmd -> cmd, 64);
            bpi_write_buffer((uint32_t *)(mca_cmd -> f_data), mca_cmd->num_bytes);
            break;
        default:
            break;
    }
}

void mca_read(struct mca_command *mca_cmd){
    mca_cmd -> cmd[0] = (mca_cmd->num_bytes << 16) + (mca_cmd->mem_type << 12) + (mca_cmd->com_address << 4) + mca_cmd->read_type;
    switch(mca_cmd->com_address){
        case ARM_VERSION:
        case ARM_HISTO:
        case ARM_BCK:
        case ARM_DIFF:
            bpi_write_buffer(mca_cmd -> cmd, 64);
            bpi_read_buffer(mca_cmd -> u_data, mca_cmd->num_bytes);
            break;
        case ARM_STATUS:
        case ARM_CTRL:
        case ARM_CAL:
            bpi_write_buffer(mca_cmd -> cmd, 64);
            bpi_read_buffer((uint32_t *)(mca_cmd -> f_data), mca_cmd->num_bytes);
            break;
        default:
            break;
    }
    
}

/*
    Read-modify-write is allowed only for arm_ctrl and arm_cal.
    In both cases, the data are 32-bit float format.
*/
void mca_rmw(struct mca_command *mca_cmd){
    uint32_t proto_com;
    switch(mca_cmd->com_address){
        case ARM_CTRL:
        case ARM_CAL:
            proto_com = (mca_cmd->num_bytes << 16) + (mca_cmd->mem_type << 12) + (mca_cmd->com_address << 4);
            mca_cmd -> cmd[0] = proto_com + mca_cmd->read_type;
            bpi_write_buffer(mca_cmd -> cmd, 64);
            bpi_read_buffer((uint32_t *)(mca_cmd -> f_data), mca_cmd->num_bytes);
            for(uint32_t n=0; n<mca_cmd->replace_num; n++){
                mca_cmd->f_data[mca_cmd->replace_idx[n]] = mca_cmd->replace_f_data[n];
            }
            mca_cmd -> cmd[0] = proto_com + mca_cmd->write_type;
            bpi_write_buffer(mca_cmd -> cmd, 64);
            bpi_write_buffer((uint32_t *)(mca_cmd -> f_data), mca_cmd->num_bytes);
            break;
        default:
            break;
    
    }
}

/*
    This function populates an mca_cmd structure with default values for reading the ARM version registers.
    Other API functions then only change the one or two parameters they need.
    Note that command, data, and replace must be global arrays of sufficient size.  This is especially important when reading histograms, since these are 4160 Byte to 8256 Byte in size if all histogram bins are read.
    
    We keep separate pointers for uint32_t and float data arrays, but by default, they point to the same storage space.  The user can overwrite this behavior in this function without having to change any other code.
*/
void arm_command_defaults(struct mca_command *mca_cmd){
    mca_cmd->cmd = command;
    mca_cmd->read_type = ARM_READ;
    mca_cmd->write_type = ARM_WRITE;
    mca_cmd->com_address = ARM_VERSION;
    mca_cmd->mem_type = MT_RAM;
    mca_cmd->num_bytes = 64;
    mca_cmd->u_data = (uint32_t *)data;
    mca_cmd->f_data = (float *)data;
    mca_cmd->replace_idx = replace_idx;  
    mca_cmd->replace_u_data = (uint32_t *)replace_data;  
    mca_cmd->replace_f_data = (float *)replace_data;  
    mca_cmd->replace_num = 0;  
}

void arm_version_read(struct mca_command *mca_cmd){
    // Set the mca_cmd parameters
    arm_command_defaults(mca_cmd);
    // Read the version registers
    mca_read(mca_cmd); 
}

void arm_status_read(struct mca_command *mca_cmd){
    // Set the mca_cmd parameters
    arm_command_defaults(mca_cmd);
    mca_cmd->com_address = ARM_STATUS;
    mca_cmd->num_bytes = 256;
    // Read the status registers
    mca_read(mca_cmd); 
}

void arm_ctrl_read(struct mca_command *mca_cmd){
    // Set the mca_cmd parameters
    arm_command_defaults(mca_cmd);
    mca_cmd->com_address = ARM_CTRL;
    mca_cmd->num_bytes = 256;
    // Read the control registers
    mca_read(mca_cmd); 
}

void arm_cal_read(struct mca_command *mca_cmd){
    // Set the mca_cmd parameters
    arm_command_defaults(mca_cmd);
    mca_cmd->com_address = ARM_CAL;
    mca_cmd->num_bytes = 256;
    // Read the control registers
    mca_read(mca_cmd); 
}

void arm_histo_read(struct mca_command *mca_cmd){
    // Set the mca_cmd parameters
    arm_command_defaults(mca_cmd);
    mca_cmd->com_address = ARM_HISTO;  // Read bank 2, used to store the sample histogram
    mca_cmd->num_bytes = 4160;  // 16 words of statistics, followed by 1024 MCA bins
    // Read the control registers
    mca_read(mca_cmd); 
}

void arm_histo2k_read(struct mca_command *mca_cmd){
    // Set the mca_cmd parameters
    arm_command_defaults(mca_cmd);
    mca_cmd->com_address = ARM_HISTO;
    mca_cmd->num_bytes = 8256;  // 16 words of statistics, followed by 2048 MCA bins
    // Read the control registers
    mca_read(mca_cmd); 
}

void arm_bck_read(struct mca_command *mca_cmd){
    // Set the mca_cmd parameters
    arm_command_defaults(mca_cmd);
    mca_cmd->com_address = ARM_BCK;  // Read bank 2, used to store a background histogram
    mca_cmd->num_bytes = 4160;  // 16 words of statistics, followed by 2048 MCA bins
    // Read the control registers
    mca_read(mca_cmd); 
}

void arm_diff_read(struct mca_command *mca_cmd){
    // Set the mca_cmd parameters
    arm_command_defaults(mca_cmd);
    mca_cmd->com_address = ARM_DIFF;  // Read sample minus background histogram
    mca_cmd->num_bytes = 4160;  // 16 words of statistics, followed by 2048 MCA bins
    // Read the control registers
    mca_read(mca_cmd); 
}

/* 
    Write and read-modify-write functions
    Data to be written are in data[].
    For read-modify-write, replacement data are in replace_f_data.
    Indices are in replace_idx
    Eg: to replace the operating voltage (index = AC_CAL_OV in arm_ctrl) use
    replace_f_data = {34.5}  // if 34.5V is the new voltage
    replace_idx = {AC_CAL_OV}
*/
void arm_ctrl_write(struct mca_command *mca_cmd){
    // Set the mca_cmd parameters
    arm_command_defaults(mca_cmd);
    mca_cmd->com_address = ARM_CTRL;
    mca_cmd->num_bytes = 256;
    // Write the control registers
    mca_write(mca_cmd); 
}

/*
  User should prepare the contents of
    replace_idx
    replace_data
  before calling this function.
  The above 2 arrays contain the indices and the values for the data to be replaced.
*/
void arm_ctrl_rmw(struct mca_command *mca_cmd, uint32_t num_items){
    // Set the mca_cmd parameters
    arm_command_defaults(mca_cmd);
    mca_cmd->com_address = ARM_CTRL;
    mca_cmd->num_bytes = 256;
    mca_cmd->replace_num = num_items;
    
    // Read-modify-write the control registers
    mca_rmw(mca_cmd); 
}

void arm_cal_write(struct mca_command *mca_cmd){
    // Set the mca_cmd parameters
    arm_command_defaults(mca_cmd);
    mca_cmd->com_address = ARM_CAL;
    mca_cmd->num_bytes = 256;
    // Write the control registers
    mca_write(mca_cmd); 
}

/*
  User should prepare the contents of
    replace_idx
    replace_data
  before calling this function.
  The above 2 arrays contain the indices and the values for the data to be replaced.
*/
void arm_cal_rmw(struct mca_command *mca_cmd, uint32_t num_items){
    // Set the mca_cmd parameters
    arm_command_defaults(mca_cmd);
    mca_cmd->com_address = ARM_CAL;
    mca_cmd->num_bytes = 256;
    mca_cmd->replace_num = num_items;
    
    // Read-modify-write the control registers
    mca_rmw(mca_cmd); 
}


