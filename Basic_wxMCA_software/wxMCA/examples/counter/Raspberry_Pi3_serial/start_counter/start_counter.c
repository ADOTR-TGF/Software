#include <stdint.h>
#include "Pi3_serial.h"
#include "mca1k_serial_device.h"
#include "mca1k_api.h"
#include "bpi_globals.h"

#include <unistd.h>
#include <stdio.h> // For debugging on a device with a file system

void main(){
    struct mca_command mca_cmd;
    bpi_serial_init();  // Prepare the serial interface communication
    /*
        Perform a read-modify-write command; In this example we restart the counter by 
        issuing a clear statistics command
    */
    replace_idx[0] = AC_RUN_ACTION;
    replace_data[0] = RA_CLEAR_STATS; // cf mca1k_api.h
    arm_ctrl_rmw(&mca_cmd, 1);  // Replacing one item

    sleep(5);  // Wait a few seconds

    arm_status_read(&mca_cmd);

    
    {  // Debugging block
        FILE *fout;
        float *fp = (float *)data;
        fout = fopen("./data/arm_status.txt","w");  // Write the status data to get count rates, etc.
        for(uint32_t n=0; n<64; n++){
            fprintf(fout, "%f\n", fp[n]);
        }
        fprintf(fout, "\n");
        fclose(fout);
    }
    
}
