#include <stdint.h>
#include "Pi3_serial.h"
#include "mca1k_serial_device.h"
#include "mca1k_api.h"
#include "bpi_globals.h"

#include <unistd.h>  // sleep(seconds) is defined here
#include <stdio.h> // For debugging on a device with a file system

void main(){
    struct mca_command mca_cmd;
    bpi_serial_init();  // Prepare the serial interface communication
    /*
        Perform a read-modify-write command; In this example we restart the MCA by 
        issuing a clear_statistics and clear_histogram command
    */
    replace_idx[0] = AC_RUN_ACTION;
    replace_data[0] = RA_CLEAR_STATS | RA_CLEAR_HISTO; // cf mca1k_api.h
    
    arm_command_defaults(&mca_cmd);  // Set the mca_cmd default parameters
    mca_cmd.f_data = arm_ctrl;  // Needed only if you want a local copy of arm_ctrl
    arm_ctrl_rmw(&mca_cmd, 1);  // Replacing one item

    sleep(5);  // Wait a few seconds

    arm_command_defaults(&mca_cmd);  // Set the mca_cmd default parameters
    mca_cmd.f_data = arm_status;     // Direct incoming data to the arm_status buffer
    arm_status_read(&mca_cmd);
    
    arm_command_defaults(&mca_cmd);  // Set the mca_cmd default parameters
    mca_cmd.u_data = histo_stats;    // Direct incoming data to the histogram buffer
    arm_histo_read(&mca_cmd);

    
    {  // Debugging block
        FILE *fout;
        
        fout = fopen("./data/histo_status.json","w");  // Write status data and histogramming data.

        fprintf(fout, "{ \"arm_status\": [ " );
        for(uint32_t n=0; n<63; n++){fprintf(fout, "%f, ", arm_status[n]);}
        fprintf(fout, "%f]", arm_status[63]);
        
        fprintf(fout, ", \"histo_stats\": [ ");
        for(uint32_t n=0; n<1039; n++){fprintf(fout, "%u, ", histo_stats[n]);}
        fprintf(fout, "%u]", histo_stats[1039]);
        fprintf(fout, " } \n");
        
        fclose(fout);
    }
    
    
    
}
