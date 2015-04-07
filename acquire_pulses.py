#!/usr/bin/env python
#########################
# acquire_pulses.py 
#
# Script to fire tellie (master mode), and read 
# pmt response pulse at scope. 
#########################
try:
    from pyvisa.vpp43 import visa_library, visa_exceptions
    visa_library.load_library("/Library/Frameworks/Visa.framework/VISA") # Mac specific??
    import visa
except ImportError:
    print "No VISA/pyVISA software installed, cannot use VisaUSB"
import os
import time
import sys
import core.serial_command as serial_command
import common.comms_flags as comms_flags
import scopes
import scope_connections
import readPklWaveFile
import utils

if __name__=="__main__":
    script_time = time.time()

    # Save file
    fname = str(sys.argv[1])
    channel = int(sys.argv[2])
    IPW = int(sys.argv[3])
    delay = float(sys.argv[4]) #delay between pulses (1/rate) [ms]
    #print fname

    # TELLIE settings
    height = 16383
    fibre_delay = 0
    trigger_delay = 700 #As used in ftb data taking
    #pulse_number = 10000 * 50. # 50 is scaling for data rate - we only record ~ 1/50 @ delay=1ms
    pulse_number = 60000

    # Set up serial connection
    sc = serial_command.SerialCommand("/dev/tty.usbserial-FTE3C0PG")
    sc.select_channel(channel)
    sc.set_pulse_width(IPW)
    sc.set_pulse_height(height)
    sc.set_pulse_number(pulse_number)
    sc.set_pulse_delay(delay)
    sc.set_fibre_delay(fibre_delay)
    sc.set_trigger_delay(trigger_delay)

    # Set-up scope
    usb_conn = scope_connections.VisaUSB()
    tek_scope = scopes.Tektronix3000(usb_conn)
    tek_scope.unlock()
    tek_scope.set_single_acquisition() # Single signal acquisition mode
    trigger = -0.2 # Volts
    tek_scope.set_edge_trigger(trigger, 1, False) # Rising edge trigger 
    time.sleep(0.1)
    #tek_scope.set_data_mode(4899, 5049)
    tek_scope.set_data_mode(49949, 50049)
    time.sleep(0.1)
    tek_scope.lock() # Re acquires the preamble  

    # Set-up results file
    results = utils.PickleFile(fname, 1)
    results.set_meta_data("timeform_1", tek_scope.get_timeform(1))
    results.set_meta_data("tellie_channel", channel)
    results.set_meta_data("width", IPW)
    results.set_meta_data("rate", 1/(delay*1e-3))
    results.set_meta_data("total_pulses_fired", pulse_number)
    #print tek_scope._get_preamble
    #results.set_meta_dict(tek_scope._get_preamble(1))       

    # Fire and save data
    time.sleep(0.1)
    run_length = pulse_number*1.05 * delay*1e-3 #[s] Run for slightly longer to avoid losing data
    start = time.time()
    looptime = start
    sc.fire()
    i=0
    print "Acquiring for %1.1f seconds..." % run_length
    while(time.time()-start < run_length):
        check = tek_scope.acquire_time_check()
        if check == True:
            try:
                results.add_data(tek_scope.get_waveform(1), 1)
                i = i + 1
            except Exception, e:
                print "Scope died, acquisition lost..."
                print e
            if i % 100 == 0:
                print "%i events stored, %1.1f seconds remaining" % (i, run_length - (time.time()-start))
                looptime = time.time()
    sc.read_pin(channel) #Stops buffer complaining
    tek_scope.unlock()
    results.save()
    results.close()
    print "########################################"
    print "%i pmt response signals saved to: %s" % (i, fname)
    print "Script took : %1.2f mins"%( (time.time() - script_time)/60 )
