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
import root_utils as ru
import os
import ROOT

def check_dir(dir):
    """Check directory exists. If not, create it"""
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def find_data_filepaths(data_dir, basename):
    """Check the number of data files in a directory"""
    file_names = []
    for i in range(100):
        if os.path.isfile("%s/%s%i.pkl" % (data_dir, basename, i)):
            file_names.append("%s/%s%i.pkl" % (data_dir, basename, i))
    return file_names

if __name__ == "__main__": 

    # ROOT stuff
    ROOT.gROOT.Reset()
    ROOT.gStyle.SetOptStat(1)
    c1 = ROOT.TCanvas("c1")

    # File stuff
    dataPath = "./results/"
    #runs = [1,2,3,4,5]
    channels = [72, 21, 13, 7, 3]
    for ent in channels:
        basePath = "./results/channel_%i" % ent
        file_names = find_data_filepaths(basePath, "run_")
        y_tot, count = [], 0

        for fileName in file_names:
            count = count + 1
            plotPath = check_dir("./results/plots/channel_%i/run_%i/" % (ent, count))
            f = ROOT.TFile("%sresults.root" % plotPath, "RECREATE")

            # Read in data file
            x, y = calc.readPickleChannel(fileName, 1)
            y_tot.append(y)

            # Make plots and save 
            area, a_mean, a_Err = ru.plot_area(x, y, "pmt signal")
            area.Write()
            ru.print_hist(area, "%sArea.pdf" % plotPath, c1)
            
            rise, r_mean, r_Err = ru.plot_rise(x, y, "pmt signal")
            rise.Write()
            ru.print_hist(rise, "%sRise.pdf" % plotPath, c1)
            
            fall, f_mean, f_Err = ru.plot_fall(x, y, "pmt signal")
            fall.Write()
            ru.print_hist(fall, "%sFall.pdf" % plotPath, c1)

            peak, p_mean, p_Err = ru.plot_peak(x, y, "pmt signal")
            peak.Write()
            ru.print_hist(peak, "%sPH.pdf" % plotPath, c1)
        ##############################################
        # make containing data from all recorded runs
        ##############################################
        # Make plots and save
        plotPath = check_dir("./results/plots/channel_%i/" % (ent))
        f = ROOT.TFile("%sresults.root" % plotPath, "RECREATE")
        area, a_mean, a_Err = ru.plot_area(x, y, "pmt signal")
        area.Write()
        ru.print_hist(area, "%sArea.pdf" % plotPath, c1)

        rise, r_mean, r_Err = ru.plot_rise(x, y, "pmt signal")
        rise.Write()
        ru.print_hist(rise, "%sRise.pdf" % plotPath, c1)
        
        fall, f_mean, f_Err = ru.plot_fall(x, y, "pmt signal")
        fall.Write()
        ru.print_hist(fall, "%sFall.pdf" % plotPath, c1)

        peak, p_mean, p_Err = ru.plot_peak(x, y, "pmt signal")
        peak.Write()
        ru.print_hist(peak, "%sPH.pdf" % plotPath, c1)
