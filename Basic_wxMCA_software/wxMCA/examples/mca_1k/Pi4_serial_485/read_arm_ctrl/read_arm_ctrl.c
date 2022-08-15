#include <stdint.h>
#include "Pi3_serial.h"
#include "mca1k_serial_device.h"
#include "mca1k_api.h"
#include "bpi_globals.h"

#include <stdio.h> // For debugging on a device with a file system

void main(){
    struct mca_command mca_cmd;
    bpi_serial_init();  // Prepare the serial interface communication
    // Read the arm_ctrl registers
    arm_ctrl_read(&mca_cmd);
    
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
