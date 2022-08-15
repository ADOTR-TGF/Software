#include <stdint.h>
#include "Pi3_serial.h"
#include "mca1k_serial_device.h"
#include "mca1k_api.h"
#include "bpi_globals.h"

#include <stdio.h> // For debugging on a device with a file system

void main(){
    /*
        Read the arm_cal from the SiPM-counter.
        Note that arm_cal always resides in non-volatile memory.
        Even if the read command is directed at RAM, the SiPM counter
        will deliver the data stored in its non-volatile memory.
    */
    struct mca_command mca_cmd;
    
    bpi_serial_init();  // Prepare the serial interface communication
    
   
    arm_cal_read(&mca_cmd);  // Replacing one item
    
    {  // Debugging block
        FILE *fout;
        float *fp = (float *)data;
        fout = fopen("./data/arm_cal.txt","w");
        for(uint32_t n=0; n<64; n++){
            fprintf(fout, "%f\n", fp[n]);
        }
        fprintf(fout, "\n");
        fclose(fout);
    }
}
