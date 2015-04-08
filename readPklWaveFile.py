###############################################
# Functions to read in pickled scope traces
# and perform standard measurements.
# 
# Will calculate: Integrated area, rise time,
# fall time, pulse width, peak voltage and
# the jitter on two signals. 
# 
# Author: Ed Leming
# Date: 17/03/2015
################################################
import calc_utils as calc
import time
import sys
import os

def find_data_filepaths(data_dir, basename):
    """Check the number of data files in a directory"""
    file_names = []
    for i in range(100):
        if os.path.isfile("%s/%s%i.pkl" % (data_dir, basename, i)):
            file_names.append("%s/%s%i.pkl" % (data_dir, basename, i))
    return file_names

if __name__ == "__main__":

    ## File path
    fileName = sys.argv[1]

    # Read data
    x,y = calc.readPickleChannel(fileName, 1)
        
    # Calculate and print parameters / plot        
    calc.printParams(x, y, fileName)
    calc.plot_eg_pulses(x, y, 10, show=True)
