#include <stdint.h>
#include "Pi3_serial.h"
#include "mca1k_serial_device.h"
#include "mca1k_api.h"
#include "bpi_globals.h"

#include <stdio.h> // For debugging on a device with a file system

void main(){
    struct mca_command mca_cmd;
    float arm_ctrl_reset[64] = {0, 0, 0, 27.0, 1, 0.05, 25.0, 795.64, 0, 328.47, 60, 800, 0x401, 0, 0, 0,
	1.0e-6, 60, 800, 0.1, 0, 40, 100, 100, 60, 1.0e-5, 1.0, 0.015, 23, 10, 1024, 115200,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    bpi_serial_init();  // Prepare the serial interface communication
    
   // Put pattern into data; ie mca_cmd.f_data
    arm_command_defaults(&mca_cmd);
        // Rewrite the patter to fdata
        for(uint32_t n=0; n<64; n++){
            mca_cmd.f_data[n] = arm_ctrl_reset[n];
        }
        arm_ctrl_write(&mca_cmd);
        arm_ctrl_read(&mca_cmd);
        {  // Debugging block
            FILE *fout;
            
            for(uint32_t n=0; n<64; n++){
                fout = fopen("./data/arm_ctrl.txt","a");
                fprintf(fout, "%f\n", mca_cmd.f_data[n]);
                fclose(fout);
            }
        }  
}
