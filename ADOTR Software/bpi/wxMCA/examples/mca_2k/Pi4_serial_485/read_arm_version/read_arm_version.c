#include <stdint.h>
#include "Pi3_serial.h"
#include "mca1k_serial_device.h"
#include "mca1k_api.h"
#include "bpi_globals.h"

#include <stdio.h> // For debugging on a device with a file system

void main(){
    struct mca_command mca_cmd;
    bpi_serial_init();  // Prepare the serial interface communication
    // Read the version registers
    arm_version_read(&mca_cmd);
    
    {  // Debugging block
        FILE *fout;
        fout = fopen("./data/arm_version.txt","w");
        for(uint32_t n=0; n<16; n++){
            fprintf(fout, "%u, ", data[n]);
        }
        fprintf(fout, "\n");
        fclose(fout);
    }
    
}
