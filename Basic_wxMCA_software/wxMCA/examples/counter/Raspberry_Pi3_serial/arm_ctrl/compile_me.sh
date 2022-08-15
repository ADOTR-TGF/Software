#! 
gcc -I "../common/" read_arm_ctrl.c ../common/mca1k_api.c ../common/mca1k_serial_device.c ../common/Pi3_serial.c ../common/bpi_globals.c -O3 -o ./read_arm_ctrl
gcc -I "../common/" write_arm_ctrl.c ../common/mca1k_api.c ../common/mca1k_serial_device.c ../common/Pi3_serial.c ../common/bpi_globals.c -O3 -o ./write_arm_ctrl
