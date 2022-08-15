#include <stdint.h>
#include "Pi3_serial.h"
#include "mca1k_serial_device.h"
#include "mca1k_api.h"
#include "bpi_globals.h"

#include <stdio.h> // For debugging on a device with a file system

void main(){
    struct mca_command mca_cmd;
    bpi_serial_init();  // Prepare the serial interface communication
    /*
        Perform a read-modify-write command; In this example we change the operating voltage, 
        which is "cal_ov" at index 7 of the arm_ctrl data array.
    */
    replace_idx[0] = 7;
    replace_data[0] = 33.0f; // New operating voltage
    arm_ctrl_rmw(&mca_cmd, 1);  // Replacing one item
    
    {  // Debugging block
        FILE *fout;
        float *fp = (float *)data;
        fout = fopen("./data/arm_ctrl.txt","w");
        for(uint32_t n=0; n<64; n++){
            fprintf(fout, "%f\n", fp[n]);
        }
        fprintf(fout, "\n");
        fclose(fout);
    }
    
}
