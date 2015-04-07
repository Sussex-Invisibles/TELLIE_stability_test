# TELLIE_stability_test
Code to monitor the stability of TELLIE channels using the Tektronix DPO3000 'scope available
underground at SNOLAB. 

### Pre requisits
 - python > 2.5 (you'll need a 32bit install to be compatable with NI VISA!)
 - NI VISA (it is free)
 - PyVISA
 - 'AcquireTek' - acquisition libraries for Tektronix scope (Available at Sussex-Invisables GitHub)
 - 'TELLIE' - Control software for TELLIE (available at Sussex-Invisibles GitHub)

### env.sh
Environment file to be sourced before running any of the python scipts provided here. The paths within the file should be changed to point to the users specific install location for both AcquireTek and TELLIE (see above). 

### acquire_pulses.py
Scipt to set up master mode running of TELLIE for a specific channel. The light output from this channel should be readout by a PMT (one available in TELLIE box underground) and the resulting electronic response coupled into the Tektronix DPO3000 'scope. The scope channel must be set within the script. Digitized pulses will then be 'pickled' (saved to file) with a small header of 'meta data' detailing some of the TELLIE settings of interest. 

### readPklWaveFile.py
Opens up picked wave files and calls a few functions from AcquireTek/calc_utils.py to output the results of some standard measurements to screen.

### rootPlots.py
Creates histograms of parameters measured on pickled data set. Results are saved in both root file format and .pdfs for quick reference. 
