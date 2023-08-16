How the code works:

An example TGF energy spectrum is read in from the file LgPl_Response

functions:
plastic_pulse() creates a normalized pulse that emulates the output behavior of the plastic detector and electronics.

make_plastic_trace() creates an array of trace samples and times based off the given parameters of count rate and TGF duration etc.. It uses the example TGF energy spectrum as a weighted probability to determine the energy of each count. A 'pulse' is scaled to the particular energy and added to the trace. The time of each count is determined by a lognormal distribution. 

plastic_trace_to_counts() follows the logic of the FPGA in how it determines a pulse and integrates the pulse to output an event energy word and timestamp.  

trace_trigger() emmulates the logic of the FPGA 'save the trace trigger'. this code just puts a red line on the plot where the FPGA would have triggered and saved 700us of trace data.

the arrays on lines 190 'trace' and 194 'trace_time' are the pertinent data to use for machine learning.  

Change the value of countrate on line 21 to get different behavior of the trace. 

For machine learning the number of counts (line 24) and each counts energy (line 92) and the time of each count (line 94) are known values.  Can a machine learning algorithm accurately recreate these values from the trace data (line 190 and 194)? 


