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
import pickle
import utils
import calc_utils as calc
import time
import sys
import os
import numpy as np
import ROOT
import array

def fit_gauss(hist):
    """Fit generic gaussian to histogram"""
    f = ROOT.TF1("f1","gaus")
    f.SetLineColor(1)
    p = hist.Fit(f, "S")

    # Write to canvas
    #stats = c1.GetPrimitive("stats")
    #stats.SetTextColor(1)
    #c1.Modified(); c1.Update()

    return f.GetParameters(), f.GetParErrors()

def print_hist(hist, savename):
    """Function to print histogram to png"""
    c1.Clear()
    hist.Draw("")
    c1.Update()
    stats = c1.GetPrimitive("stats")
    stats.SetTextSize(0.04)
    c1.Modified(); c1.Update()
    c1.Print("%s" % savename, "pdf")

def plot_area(x, y, name):
    """Calc area of pulses"""
    area, areaErr = calc.calcArea(x,y)
    bins = np.arange((area-8*areaErr)*1e9, (area+8*areaErr)*1e9, (areaErr/5)*1e9)
    hist = ROOT.TH1D("%s" % name,"%s" % name, len(bins), bins[0], bins[-1])
    hist.SetTitle("Pulse integral")
    hist.GetXaxis().SetTitle("Integrated area (V.ns)")
    for i in range(len(y[:,0])-1):
        hist.Fill(np.trapz(y[i,:],x)*1e9)
    return hist, area, areaErr

def plot_rise(x, y, name):
    """Calc and plot rise time of pulses"""
    rise, riseErr = calc.calcRise(x,y)
    bins = np.arange((rise-8*riseErr)*1e9, (rise+8*riseErr)*1e9, (riseErr/5.)*1e9)
    hist = ROOT.TH1D("%s" % name,"%s" % name, len(bins), bins[0], bins[-1])
    hist.SetTitle("Rise time")
    hist.GetXaxis().SetTitle("Rise time (ns)")
    f = calc.positive_check(y)
    if f == True:
        for i in range(len(y[:,0])-1):
            m = max(y[i,:])
            lo_thresh = m*0.1
            hi_thresh = m*0.9
            low = calc.interpolate_threshold(x, y[i,:], lo_thresh)
            high = calc.interpolate_threshold(x, y[i,:], hi_thresh)
            hist.Fill((high - low)*1e9)
    else:
        for i in range(len(y[:,0])-1):
            m = min(y[i,:])
            lo_thresh = m*0.1
            hi_thresh = m*0.9
            low = calc.interpolate_threshold(x, y[i,:], lo_thresh, rise=False)
            high = calc.interpolate_threshold(x, y[i,:], hi_thresh, rise=False)
            hist.Fill((high - low)*1e9)
    return hist, rise, riseErr

def plot_fall(x, y, name):
    """Calc and plot fall time of pulses"""
    fall, fallErr = calc.calcFall(x,y)
    bins = np.arange((fall-8*fallErr)*1e9, (fall+8*fallErr)*1e9, (fallErr/5.)*1e9)
    hist = ROOT.TH1D("%s" % name,"%s" % name, len(bins), bins[0], bins[-1])
    hist.SetTitle("Fall time")
    hist.GetXaxis().SetTitle("Fall time (ns)")
    f = calc.positive_check(y)
    if f == True:
        for i in range(len(y[:,0])-1):
            m = max(y[i,:])
            m_index = np.where(y[i,:] == m)[0][0]
            lo_thresh = m*0.1
            hi_thresh = m*0.9
            low = calc.interpolate_threshold(x, y[i,m_index:], lo_thresh, rise=False)
            high = calc.interpolate_threshold(x, y[i,m_index:], hi_thresh, rise=False)
            hist.Fill((low - high)*1e9)
    else:
        for i in range(len(y[:,0])-1):
            m = min(y[i,:])
            m_index = np.where(y[i,:] == m)[0][0]
            lo_thresh = m*0.1
            hi_thresh = m*0.9
            low = calc.interpolate_threshold(x, y[i,m_index:], lo_thresh)
            high = calc.interpolate_threshold(x, y[i,m_index:], hi_thresh)
            hist.Fill((low - high)*1e9)
    return hist, fall, fallErr

def plot_peak(x, y, name):
    """Plot pulse heights for array of pulses"""
    peak, peakErr = calc.calcPeak(x,y)
    bins = np.arange((peak-8*peakErr), (peak+8*peakErr), (peakErr/5.))
    hist = ROOT.TH1D("%s" % name,"%s" % name, len(bins), bins[0], bins[-1])
    hist.SetTitle("Pulse hieght")
    hist.GetXaxis().SetTitle("Pulse height (V)")
    f = calc.positive_check(y)
    if f == True:
        for i in range(len(y[:,0])-1):
            hist.Fill(max(y[i,:]))
    else:
        for i in range(len(y[:,0])-1):
            hist.Fill(min(y[i,:]))
    return hist, peak, peakErr

def plot_jitter(x1, y1, x2, y2, name):
    """Calc and plot jitter of pulse pairs"""
    sep, jitter, jittErr = calc.calcJitter(x1, y1, x2, y2)
    bins = np.arange((sep-8*jitter)*1e9, (sep+8*jitter)*1e9, (jitter/5.)*1e9)
    hist = ROOT.TH1D("%s" % name,"%s" % name, len(bins), bins[0], bins[-1])
    hist.SetTitle("Jitter between signal and trigger out")
    hist.GetXaxis().SetTitle("Pulse separation (ns)")
    p1 = calc.positive_check(y1)
    p2 = calc.positive_check(y2)
    for i in range(len(y1[:,0])-1):
        m1 = calc.calcSinglePeak(p1, y1[i,:])
        m2 = calc.calcSinglePeak(p2, y2[i,:])
        time_1 = calc.interpolate_threshold(x1, y1[i,:], 0.1*m1, rise=p1)
        time_2 = calc.interpolate_threshold(x2, y2[i,:], 0.1*m2, rise=p2)
        hist.Fill((time_1 - time_2)*1e9)
    return hist, jitter, jittErr

def check_dir(dir):
    """Check directory exists. If not, create it"""
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir
        

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
        file_names = calc.find_data_filepaths(basePath, "run_")
        y_tot, count = [], 0

        for fileName in file_names:
            count = count + 1
            plotPath = check_dir("./results/plots/channel_%i/run_%i/" % (ent, count))
            f = ROOT.TFile("%sresults.root" % plotPath, "RECREATE")

            # Read in data file
            x, y = calc.readPickleChannel(fileName, 1)
            y_tot.append(y)

            # Make plots and save 
            area, a_mean, a_Err = plot_area(x, y, "pmt signal")
            area.Write()
            print_hist(area, "%sArea.pdf" % plotPath)
            
            rise, r_mean, r_Err = plot_rise(x, y, "pmt signal")
            rise.Write()
            print_hist(rise, "%sRise.pdf" % plotPath)
            
            fall, f_mean, f_Err = plot_fall(x, y, "pmt signal")
            fall.Write()
            print_hist(fall, "%sFall.pdf" % plotPath)

            peak, p_mean, p_Err = plot_peak(x, y, "pmt signal")
            peak.Write()
            print_hist(peak, "%sPH.pdf" % plotPath)
        ##############################################
        # make containing data from all recorded runs
        ##############################################
        # Make plots and save
        plotPath = check_dir("./results/plots/channel_%i/" % (ent))
        f = ROOT.TFile("%sresults.root" % plotPath, "RECREATE")
        area, a_mean, a_Err = plot_area(x, y, "pmt signal")
        area.Write()
        print_hist(area, "%sArea.pdf" % plotPath)

        rise, r_mean, r_Err = plot_rise(x, y, "pmt signal")
        rise.Write()
        print_hist(rise, "%sRise.pdf" % plotPath)
        
        fall, f_mean, f_Err = plot_fall(x, y, "pmt signal")
        fall.Write()
        print_hist(fall, "%sFall.pdf" % plotPath)

        peak, p_mean, p_Err = plot_peak(x, y, "pmt signal")
        peak.Write()
        print_hist(peak, "%sPH.pdf" % plotPath)
