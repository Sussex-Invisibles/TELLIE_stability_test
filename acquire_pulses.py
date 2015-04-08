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

    # TELLIE settings
    sc = serial_command.SerialCommand("/dev/tty.usbserial-FTE3C0PG")
    ########################################################
    height = 16383
    fibre_delay = 0
    trigger_delay = 700 #As used in ftb data taking
    pulse_number = 60000 #Just below max allowed by chip
    ########################################################
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
    ###########################################
    scope_chan = 1 # We're using channel 1!
    termination = 50 # Ohms
    trigger = -0.5 # Volts
    y_div_units = 1 # volts
    x_div_units = 4e-9 # seconds
    y_offset = -2.5*y_div_units # offset in y (2.5 divisions up)
    x_offset = +2*x_div_units # offset in x (2 divisions to the left)
    record_length = 1e3 # trace is 1e3 samples long
    half_length = record_length / 2 # For selecting region about trigger point
    ###########################################
    tek_scope.unlock()
    tek_scope.set_horizontal_scale(x_div_units)
    tek_scope.set_horizontal_delay(x_offset) #shift to the left 2 units
    tek_scope.set_channel_y(scope_chan, y_div_units)
    tek_scope.set_display_y(scope_chan, y_div_units, offset=y_offset)
    tek_scope.set_channel_termination(scope_chan, termination)
    tek_scope.set_edge_trigger(trigger, scope_chan, falling=True) # Falling edge trigger 
    tek_scope.set_single_acquisition() # Single signal acquisition mode
    tek_scope.set_record_length(record_length)
    tek_scope.set_data_mode(half_length-50, half_length+50)
    tek_scope.lock()
    tek_scope.begin() # Acquires the pre-amble!

    # Set-up results file
    results = utils.PickleFile(fname, 1)
    results.add_meta_data("timeform_1", tek_scope.get_timeform(1))
    results.add_meta_data("tellie_channel", channel)
    results.add_meta_data("width", IPW)
    results.add_meta_data("rate", 1/(delay*1e-3))
    results.add_meta_data("total_pulses_fired", pulse_number)

    ##########################################################
    # Fire and save data
    ##########################################################
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
