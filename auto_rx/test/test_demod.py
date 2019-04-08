#!/usr/bin/env python
#
#   Run a set of files through a processing and decode chain, and handle the output.
#
#   Copyright (C) 2018  Mark Jessop <vk5qi@rfhead.net>
#   Released under GNU GPL v3 or later
#
#   Refer to the README.md in this directory for instructions on use.
#
import glob
import argparse
import os
import sys
import time
import subprocess


# Dictionary of available processing types.

processing_type = {
    # # RS41 Decoding
    # 'rs41_csdr': {
    #     # Decode a RS41 using a CSDR processing chain to do FM demodulation
    #     # Decimate to 48 khz, filter, then demodulate.
    #     #'demod' : "| csdr fir_decimate_cc 2 0.005 HAMMING 2>/dev/null | csdr bandpass_fir_fft_cc -0.08 0.08 0.05 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",
    #     # Decimate to a 24 kHz channel, demod, then interpolate back up to 48 kHz.
    #     #'demod' : "| csdr fir_decimate_cc 4 0.005 HAMMING 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr rational_resampler_ff 2 1 0.005 HAMMING | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",
    #     # Decimate to a 12 khz channel, filter, demod, then interpolate back up to 48 kHz
    #     'demod' : "| csdr fir_decimate_cc 8 0.005 HAMMING 2>/dev/null | csdr bandpass_fir_fft_cc -0.3 0.3 0.05 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr rational_resampler_ff 4 1 0.005 HAMMING | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",
    #     # Decode using rs41ecc
    #     # Remove --ecc to see how much work the RS decoding is doing!
    #     'decode': "../rs41ecc --ptu --crc --ecc 2>/dev/null",
    #     # Count the number of telemetry lines that have no bit errors
    #     "post_process" : " | grep 00000 | wc -l",
    #     'files' : "./generated/rs41*.bin"
    # },
    # # RS92 Decoding
    # 'rs92_csdr': {
    #     # Decode a RS92 using a CSDR processing chain to do FM demodulation
    #     # Decimate to 48 khz, filter to +/-4.8kHz, then demodulate. - WORKS BEST
    #     'demod' : "| csdr fir_decimate_cc 2 0.005 HAMMING 2>/dev/null | csdr bandpass_fir_fft_cc -0.10 0.10 0.05 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",
    #     # Decimate to a 24 kHz channel, demod, then interpolate back up to 48 kHz.
    #     #'demod' : "| csdr fir_decimate_cc 4 0.005 HAMMING 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr rational_resampler_ff 2 1 0.005 HAMMING | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",
    #     # Decimate to a 12 khz channel, demod, then interpolate back up to 48 kHz.
    #     #'demod' : "| csdr fir_decimate_cc 8 0.005 HAMMING 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr rational_resampler_ff 4 1 0.005 HAMMING | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",
    #     # Decode using rs92ecc
    #     'decode': "../rs92ecc -vx -v --crc --ecc --vel 2>/dev/null",
    #     # Count the number of telemetry lines.
    #     "post_process" : " | grep M2513116 | wc -l",
    #     'files' : "./generated/rs92*.bin"
    # },
    # # DFM Decoding
    # 'dfm_csdr': {
    #     # Decode a DFM using a CSDR processing chain to do FM demodulation
    #     # Decimate to 48 khz, filter to +/-6kHz, then demodulate.
    #     #'demod' : "| csdr fir_decimate_cc 2 0.005 HAMMING 2>/dev/null | csdr bandpass_fir_fft_cc -0.12 0.12 0.05 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",
    #     # Decimate to a 24 kHz channel, demod, then interpolate back up to 48 kHz.
    #     #'demod' : "| csdr fir_decimate_cc 4 0.005 HAMMING 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr rational_resampler_ff 2 1 0.005 HAMMING | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",
    #     # Decimate to a 12 khz channel, demod, then interpolate back up to 48 kHz. - WORKS BEST
    #     'demod' : "| csdr fir_decimate_cc 8 0.005 HAMMING 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr rational_resampler_ff 4 1 0.005 HAMMING | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",
    #     # Decode using rs41ecc
    #     'decode': "../dfm09ecc -vv --ecc --json --dist --auto 2>/dev/null",
    #     # Count the number of telemetry lines.
    #     "post_process" : " | grep frame |  wc -l",
    #     'files' : "./generated/dfm*.bin"
    # },
    # #   M10 Radiosonde decoding.
    # 'm10_csdr': {
    #     # M10 Decoding
    #     # Use a CSDR processing chain to do FM demodulation
    #     # Decimate to 48 khz, filter, then demodulate. - WORKS BEST
    #     'demod' : "| csdr fir_decimate_cc 2 0.005 HAMMING 2>/dev/null | csdr bandpass_fir_fft_cc -0.23 0.23 0.05 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",
    #     # Decimate to a 24 kHz channel, demod, then interpolate back up to 48 kHz.
    #     #'demod' : "| csdr fir_decimate_cc 4 0.005 HAMMING 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr rational_resampler_ff 2 1 0.005 HAMMING | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",
    #     # Decode using rs41ecc
    #     'decode': "../m10 -b -b2 2>/dev/null",
    #     # Count the number of telemetry lines.
    #     "post_process" : "| wc -l",
    #     'files' : "./generated/m10*.bin"
    # },
    # #   rs_detect - Sonde Detection.
    # #   Current approach in auto_rx uses rtl_fm with a 22 khz sample rate (channel bw?) setting,
    # #   then resamples up to 48 khz sampes to feed into rs_detect.
    # #
    # 'rs_detect_csdr': {
    #     # Use a CSDR processing chain to do FM demodulation
    #     # Using a ~22kHz wide filter, and 20 Hz high-pass
    #     # Decimate to 48 khz, filter to ~22 kHz BW, then demod.
    #     # rs_detect seem to like this better than the decimation approach.
    #     #'demod' : "| csdr fir_decimate_cc 2 0.005 HAMMING 2>/dev/null | csdr bandpass_fir_fft_cc -0.23 0.23 0.05 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -t wav - highpass 20 2>/dev/null| ",
    #     # Decimate to 24 khz before passing into the FM demod. This is roughly equivalent to rtl_fm -r 22k
    #     'demod' : "| csdr fir_decimate_cc 4 0.005 HAMMING 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr rational_resampler_ff 2 1 0.005 HAMMING | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -t wav - highpass 20 2>/dev/null| ",
    #     # Decode using rs41ecc
    #     'decode': "../rs_detect -z -t 8 2> /dev/null",
    #     # Grep out the line containing the detected sonde type.
    #     "post_process" : " | grep found",
    #     'files' : "./generated/*.bin"
    # },
    #   dft_detect - Sonde detection using DFT correlation
    #   
    # 'dft_detect_csdr': {
    #     # Use a CSDR processing chain to do FM demodulation
    #     # Filter to 22 khz channel bandwidth, then demodulate.
    #     #'demod' : "| csdr fir_decimate_cc 2 0.005 HAMMING 2>/dev/null | csdr bandpass_fir_fft_cc -0.23 0.23 0.05 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -t wav - 2>/dev/null| ",
    #     # Decimate to a 24 kHz bandwidth, demodulator, then interpolate back up to 48 kHz.
    #     'demod' : "| csdr fir_decimate_cc 4 0.005 HAMMING 2>/dev/null | csdr fmdemod_quadri_cf | csdr limit_ff | csdr rational_resampler_ff 2 1 0.005 HAMMING | csdr convert_f_s16 | sox -t raw -r 48k -e signed-integer -b 16 -c 1 - -r 48000 -t wav - highpass 20 2>/dev/null| ",
    #     # Decode using rs41ecc
    #     'decode': "../dft_detect 2>/dev/null",
    #     # Grep out the line containing the detected sonde type.
    #     "post_process" : " | grep \:",
    #     'files' : "./generated/*.bin"
    # },

    # #
    # # FSK-DEMOD DECODING
    # #
    # # RS41 Decoding
    'rs41_fsk_demod': {
        # Shift up to ~24 khz, and then pass into fsk_demod.
        'demod' : "| csdr shift_addition_cc 0.25 2>/dev/null | csdr convert_f_s16 | ../fsk_demod --cs16 -b 1 -u 45000 --stats=100 2 96000 4800 - - 2>stats.txt | python ./bit_to_samples.py 48000 4800 | sox -t raw -r 48k -e unsigned-integer -b 8 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",

        # Decode using rs41ecc
        'decode': "../rs41ecc --ecc --ptu --crc 2>/dev/null",
        # Count the number of telemetry lines.
        "post_process" : " | grep 00000 | wc -l",
        'files' : "./generated/rs41*"
    },
    # # RS92 Decoding
    'rs92_fsk_demod': {
        # Not currently working - need to resolve segfault in dfk_demod when using 96 kHz Fs ans 2400 Rb
        # Shift up to ~24 khz, and then pass into fsk_demod.
        'demod' : "| csdr shift_addition_cc 0.25 2>/dev/null | csdr convert_f_s16 | ../fsk_demod --cs16 -b 1 -u 45000 --stats=100 2 96000 4800 - - 2>stats.txt | python ./bit_to_samples.py 48000 4800 | sox -t raw -r 48k -e unsigned-integer -b 8 -c 1 - -r 48000 -b 8 -t wav - 2>/dev/null| ",

        # Decode using rs41ecc
        'decode': "../rs92ecc -vx -v --crc --ecc --vel 2>/dev/null",
        # Count the number of telemetry lines.
        "post_process" : " | grep M2513116 | wc -l",
        'files' : "./generated/rs92*"
    },
    'm10_fsk_demod': {
        # Not currently working due to weird baud rate (9614). Doesnt work even with fractional resampling (slow down signal to make it appear to be 9600 baud).
        # Shift up to ~24 khz, and then pass into fsk_demod.
        'demod' : "| csdr shift_addition_cc 0.25 2>/dev/null | csdr convert_f_s16 | ../tsrc - - 1.0016666 -c | ../fsk_demod --cs16 -b 1 -u 45000 --stats=100 2 96160 9616 - - 2>stats.txt | python ./bit_to_samples.py 57696 9616 | sox -t raw -r 57696 -e unsigned-integer -b 8 -c 1 - -r 57696 -b 8 -t wav - 2>/dev/null| ",
        'decode': "../m10 -b -b2 2>/dev/null",
        # Count the number of telemetry lines.
        "post_process" : "| wc -l",
        'files' : "./generated/m10*"
    },

    'dfm_fsk_demod': {
        # cat ./generated/dfm09_96k_float_15.0dB.bin | csdr shift_addition_cc 0.25000 2>/dev/null | csdr convert_f_s16 | 
        #./tsrc - - 1.041666 | ../fsk_demod --cs16 -b 1 -u 45000 2 100000 2500 - - 2>/dev/null | 
        #python ./bit_to_samples.py 50000 2500 | sox -t raw -r 50k -e unsigned-integer -b 8 -c 1 - -r 50000 -b 8 -t wav - 2>/dev/null| 
        #../dfm09ecc -vv --json --dist --auto

        'demod': '| csdr shift_addition_cc 0.25000 2>/dev/null | csdr convert_f_s16 | ../tsrc - - 1.041666 | ../fsk_demod --cs16 -b 1 -u 45000 --stats=100 2 100000 2500 - - 2>stats.txt | python ./bit_to_samples.py 50000 2500 | sox -t raw -r 50k -e unsigned-integer -b 8 -c 1 - -r 50000 -b 8 -t wav - 2>/dev/null| ',
        'decode': '../dfm09ecc -vv --json --dist --auto 2>/dev/null',
        "post_process" : " | grep frame |  wc -l", # ECC
        #"post_process" : "| grep -o '\[OK\]' | wc -l", # No ECC
        'files' : "./generated/dfm*.bin"
    }
}


#
# RTL-FM DECODING - (Baselining of existing decode performance)
#
# NOTE: This requires tsrc (from codec2-dev/unittest) and Viproz's hacked rtl_fm to work.
# Viproz's rtl_fm is available from here: https://github.com/Viproz/rtl-sdr/
# Build this, but do NOT install it. Instead, copy the rtl_fm from build/src to the *this* directory, and re-name it to rtl_fm_stdin
# You still need a RTLSDR connected to be able to run this.
#
# tsrc is available at http://svn.code.sf.net/p/freetel/code/codec2-dev/misc/tsrc.c
# HOWEVER there is a bug which makes it neglect the -c (complex) option.
# Change line 59 to read: int channels = 2;
# and compile with gcc tsrc.c -o tsrc -lm -lsamplerate
# Then copy this file to *this* directory.
#
# The decoder commands for these are generated based on the rtl_fm output sample rate.
# The input samples, which are in complex float IQ format, are shifted in frequency to where rtl_fm
# expects them to be, and are also resampled to match rtl_fm's desired input rate.
#
_sample_fs = 96000.0 # Sample rate of input. Always 96k at the moment.


# RS41
_fm_rate = 15000
# Calculate the necessary conversions
_rtlfm_oversampling = 8.0 # Viproz's hacked rtl_fm oversamples by 8x.
_shift = -2.0*_fm_rate/_sample_fs # rtl_fm tunes 'up' by rate*2, so we need to shift the signal down by this amount.

_resample = (_fm_rate*_rtlfm_oversampling)/_sample_fs

if _resample != 1.0:
    # We will need to resample.
    _resample_command = "csdr convert_f_s16 | ./tsrc - - %.4f | csdr convert_s16_f |" % _resample
    _shift = (-2.0*_fm_rate)/(_sample_fs*_resample)
else:
    _resample_command = ""

_demod_command = "| %s csdr shift_addition_cc %.5f 2>/dev/null | csdr convert_f_u8 |" % (_resample_command, _shift)
_demod_command += " ./rtl_fm_stdin -M fm -f 401000000 -F9 -s %d  2>/dev/null|" % (int(_fm_rate))
_demod_command += " sox -t raw -r %d -e s -b 16 -c 1 - -r 48000 -b 8 -t wav - lowpass 2600 2>/dev/null |" % int(_fm_rate)

processing_type['rs41_rtlfm'] = {
    # Shift signal to -30 kHz, resample to 120 kHz, (8x 15 khz output rate), then convert to u8 before passing into rtl_fm_stdin.
    # Currently using a timeout to kill rtl_fm as it doesnt notice the end of the incoming samples.
    'demod': _demod_command,
    # Decode using rs41ecc
    'decode': "../rs41mod --ptu --crc --ecc2 2>/dev/null",
    # Count the number of telemetry lines.
    "post_process" : " | grep 00000 | wc -l",
    'files' : "./generated/rs41*.bin"
}


# RS92
_fm_rate = 12000
# Calculate the necessary conversions
_rtlfm_oversampling = 8.0 # Viproz's hacked rtl_fm oversamples by 8x.
_shift = -2.0*_fm_rate/_sample_fs # rtl_fm tunes 'up' by rate*2, so we need to shift the signal down by this amount.

_resample = (_fm_rate*_rtlfm_oversampling)/_sample_fs

if _resample != 1.0:
    # We will need to resample.
    _resample_command = "csdr convert_f_s16 | ./tsrc - - %.4f | csdr convert_s16_f |" % _resample
    _shift = (-2.0*_fm_rate)/(_sample_fs*_resample)
else:
    _resample_command = ""

_demod_command = "| %s csdr shift_addition_cc %.5f 2>/dev/null | csdr convert_f_u8 |" % (_resample_command, _shift)
_demod_command += " ./rtl_fm_stdin -M fm -f 401000000 -F9 -s %d  2>/dev/null|" % (int(_fm_rate))
_demod_command += " sox -t raw -r %d -e s -b 16 -c 1 - -r 48000 -b 8 -t wav - highpass 20 2>/dev/null |" % int(_fm_rate)


processing_type['rs92_rtlfm'] = {
    'demod': _demod_command,
    # Decode using rs92ecc
    'decode': "../rs92mod -vx -v --crc --ecc --vel 2>/dev/null",
    #'decode': "../rs92ecc -vx -v --crc --ecc -r --vel 2>/dev/null", # For measuring No-ECC performance
    # Count the number of telemetry lines.
    "post_process" : " | grep M2513116 | wc -l",
    #"post_process" : " | grep \"errors: 0\" | wc -l",
    'files' : "./generated/rs92*.bin" 
}


# RS92-NGP (wider bandwidth)
_fm_rate = 28000
# Calculate the necessary conversions
_rtlfm_oversampling = 8.0 # Viproz's hacked rtl_fm oversamples by 8x.
_shift = -2.0*_fm_rate/_sample_fs # rtl_fm tunes 'up' by rate*2, so we need to shift the signal down by this amount.

_resample = (_fm_rate*_rtlfm_oversampling)/_sample_fs

if _resample != 1.0:
    # We will need to resample.
    _resample_command = "csdr convert_f_s16 | ./tsrc - - %.4f | csdr convert_s16_f |" % _resample
    _shift = (-2.0*_fm_rate)/(_sample_fs*_resample)
else:
    _resample_command = ""

_demod_command = "| %s csdr shift_addition_cc %.5f 2>/dev/null | csdr convert_f_u8 |" % (_resample_command, _shift)
_demod_command += " ./rtl_fm_stdin -M fm -f 401000000 -F9 -s %d  2>/dev/null|" % (int(_fm_rate))
_demod_command += " sox -t raw -r %d -e s -b 16 -c 1 - -r 48000 -b 8 -t wav - highpass 20 2>/dev/null |" % int(_fm_rate)


processing_type['rs92ngp_rtlfm'] = {
    'demod': _demod_command,
    # Decode using rs92ecc
    'decode': "../rs92mod -vx -v --crc --ecc --vel 2>/dev/null",
    #'decode': "../rs92ecc -vx -v --crc --ecc -r --vel 2>/dev/null", # For measuring No-ECC performance
    # Count the number of telemetry lines.
    "post_process" : "| grep P3213708 | wc -l",
    #"post_process" : " | grep \"errors: 0\" | wc -l",
    'files' : "./generated/rsngp*.bin" 
}

# DFM
_fm_rate = 15000 # Match what's in autorx.decode
# Calculate the necessary conversions
_rtlfm_oversampling = 8.0 # Viproz's hacked rtl_fm oversamples by 8x.
_shift = -2.0*_fm_rate/_sample_fs # rtl_fm tunes 'up' by rate*2, so we need to shift the signal down by this amount.

_resample = (_fm_rate*_rtlfm_oversampling)/_sample_fs

if _resample != 1.0:
    # We will need to resample.
    _resample_command = "csdr convert_f_s16 | ./tsrc - - %.4f | csdr convert_s16_f |" % _resample
    _shift = (-2.0*_fm_rate)/(_sample_fs*_resample)
else:
    _resample_command = ""
# For some reason the DFM sample breaks type conversion - multiplying it by 0.9 seems to fix it.
_demod_command = "| csdr gain_ff 0.90 | %s csdr shift_addition_cc %.5f 2>/dev/null | csdr convert_f_u8 |" % (_resample_command, _shift)
_demod_command += " ./rtl_fm_stdin -M fm -f 401000000 -F9 -s %d  2>/dev/null|" % (int(_fm_rate))
_demod_command += " sox -t raw -r %d -e s -b 16 -c 1 - -r 48000 -b 8 -t wav - highpass 20 lowpass 2000 2>/dev/null |" % int(_fm_rate)

processing_type['dfm_rtlfm'] = {
    'demod': _demod_command,
    'decode': "../dfm09mod -vv --json --dist --auto 2>/dev/null", # ECC
    #'decode': "../dfm09ecc -vv --ecc -r --auto 2>/dev/null", # No-ECC
    # Count the number of telemetry lines.
    "post_process" : " | grep frame |  wc -l", # ECC
    #"post_process" : "| grep -o '\[OK\]' | wc -l", # No ECC
    'files' : "./generated/dfm*.bin"
}


# M10
_fm_rate = 22000
# Calculate the necessary conversions
_rtlfm_oversampling = 8.0 # Viproz's hacked rtl_fm oversamples by 8x.
_shift = -2.0*_fm_rate/_sample_fs # rtl_fm tunes 'up' by rate*2, so we need to shift the signal down by this amount.

_resample = (_fm_rate*_rtlfm_oversampling)/_sample_fs

if _resample != 1.0:
    # We will need to resample.
    _resample_command = "csdr convert_f_s16 | ./tsrc - - %.4f | csdr convert_s16_f |" % _resample
    _shift = (-2.0*_fm_rate)/(_sample_fs*_resample)
else:
    _resample_command = ""

_demod_command = "| %s csdr shift_addition_cc %.5f 2>/dev/null | csdr convert_f_u8 |" % (_resample_command, _shift)
_demod_command += " ./rtl_fm_stdin -M fm -f 401000000 -F9 -s %d  2>/dev/null|" % (int(_fm_rate))
_demod_command += " sox -t raw -r %d -e s -b 16 -c 1 - -r 48000 -b 8 -t wav - highpass 20 2>/dev/null |" % int(_fm_rate)

processing_type['m10_rtlfm'] = {
    'demod': _demod_command,
    'decode': "../m10 -b -b2 2>/dev/null",
    # Count the number of telemetry lines.
    "post_process" : "| wc -l",
    'files' : "./generated/m10*.bin"
}

# iMet
_fm_rate = 15000
# Calculate the necessary conversions
_rtlfm_oversampling = 8.0 # Viproz's hacked rtl_fm oversamples by 8x.
_shift = -2.0*_fm_rate/_sample_fs # rtl_fm tunes 'up' by rate*2, so we need to shift the signal down by this amount.

_resample = (_fm_rate*_rtlfm_oversampling)/_sample_fs

if _resample != 1.0:
    # We will need to resample.
    _resample_command = "csdr convert_f_s16 | ./tsrc - - %.4f | csdr convert_s16_f |" % _resample
    _shift = (-2.0*_fm_rate)/(_sample_fs*_resample)
else:
    _resample_command = ""

_demod_command = "| %s csdr shift_addition_cc %.5f 2>/dev/null | csdr convert_f_u8 |" % (_resample_command, _shift)
_demod_command += " ./rtl_fm_stdin -M fm -f 401000000 -F9 -s %d  2>/dev/null|" % (int(_fm_rate))
_demod_command += " sox -t raw -r %d -e s -b 16 -c 1 - -r 48000 -b 8 -t wav - highpass 20 2>/dev/null |" % int(_fm_rate)

processing_type['imet4_rtlfm'] = {
    'demod': _demod_command,
    'decode': "../imet1rs_dft --json 2>/dev/null",
    # Count the number of telemetry lines.
    "post_process" : "| grep frame |  wc -l",
    'files' : "./generated/imet4*.bin"
}

# # RS_Detect
# _fm_rate = 22000
# #_fm_rate = 15000
# # Calculate the necessary conversions
# _rtlfm_oversampling = 8.0 # Viproz's hacked rtl_fm oversamples by 8x.
# _shift = -2.0*_fm_rate/_sample_fs # rtl_fm tunes 'up' by rate*2, so we need to shift the signal down by this amount.

# _resample = (_fm_rate*_rtlfm_oversampling)/_sample_fs

# if _resample != 1.0:
#     # We will need to resample.
#     _resample_command = "csdr convert_f_s16 | ./tsrc - - %.4f | csdr convert_s16_f |" % _resample
#     _shift = (-2.0*_fm_rate)/(_sample_fs*_resample)
# else:
#     _resample_command = ""

# _demod_command = "| %s csdr shift_addition_cc %.5f 2>/dev/null | csdr convert_f_u8 |" % (_resample_command, _shift)
# _demod_command += " ./rtl_fm_stdin -M fm -f 401000000 -F9 -s %d  2>/dev/null|" % (int(_fm_rate))
# _demod_command += " sox -t raw -r %d -e s -b 16 -c 1 - -r 48000 -b 8 -t wav - highpass 20 2>/dev/null |" % int(_fm_rate)

# processing_type['rs_detect_rtlfm'] = {
#     'demod': _demod_command,
#     'decode': "../rs_detect -z -t 8 2> /dev/null",
#     # Grep out the line containing the detected sonde type.
#     "post_process" : " | grep found",
#     'files' : "./generated/*.bin"
# }

# # DFT_Detect
# _fm_rate = 22000
# #_fm_rate = 15000
# # Calculate the necessary conversions
# _rtlfm_oversampling = 8.0 # Viproz's hacked rtl_fm oversamples by 8x.
# _shift = -2.0*_fm_rate/_sample_fs # rtl_fm tunes 'up' by rate*2, so we need to shift the signal down by this amount.

# _resample = (_fm_rate*_rtlfm_oversampling)/_sample_fs

# if _resample != 1.0:
#     # We will need to resample.
#     _resample_command = "csdr convert_f_s16 | ./tsrc - - %.4f | csdr convert_s16_f |" % _resample
#     _shift = (-2.0*_fm_rate)/(_sample_fs*_resample)
# else:
#     _resample_command = ""

# _demod_command = "| %s csdr shift_addition_cc %.5f 2>/dev/null | csdr convert_f_u8 |" % (_resample_command, _shift)
# _demod_command += " ./rtl_fm_stdin -M fm -f 401000000 -F9 -s %d  2>/dev/null|" % (int(_fm_rate))
# _demod_command += " sox -t raw -r %d -e s -b 16 -c 1 - -r 48000 -b 8 -t wav - highpass 20 2>/dev/null |" % int(_fm_rate)

# processing_type['dft_detect_rtlfm'] = {
#     'demod': _demod_command,
#     'decode': "../dft_detect 2>/dev/null",
#     # Grep out the line containing the detected sonde type.
#     "post_process" : " | grep \:",
#     'files' : "./generated/*.bin"
# }



def run_analysis(mode, file_mask=None, shift=0.0, verbose=False, log_output = None):


    _mode = processing_type[mode]

    # If we are not supplied with a file mask, use the defaults.
    if file_mask is None:
        file_mask = _mode['files']

    # Get the list of files.
    _file_list = glob.glob(file_mask)
    if len(_file_list) == 0:
        print("No files found matching supplied path.")
        return

    # Sort the list of files.
    _file_list.sort()

    _first = True

    # Calculate the frequency offset to apply, if defined.
    _shiftcmd = "| csdr shift_addition_cc %.5f 2>/dev/null" % (shift/96000.0)

    if log_output is not None:
        _log = open(log_output,'w')

    # Iterate over the files in the supplied list.
    for _file in _file_list:

        # Generate the command to run.
        _cmd = "cat %s "%_file 

        # Add in an optional frequency error if supplied.
        if shift != 0.0:
            _cmd += _shiftcmd

        # Add on the rest of the demodulation and decoding commands.
        _cmd += _mode['demod'] + _mode['decode'] + _mode['post_process']


        if _first:
            print("Command: %s" % _cmd)
            _first = False

        # Run the command.
        try:
            _start = time.time()
            _output = subprocess.check_output(_cmd, shell=True, stderr=None)
        except:
            _output = "error"

        _runtime = time.time() - _start

        _result = "%s, %s" % (os.path.basename(_file), _output.strip())

        print(_result)
        if log_output is not None:
            _log.write(_result + '\n')

        if verbose:
            print("Runtime: %.1d" % _runtime)

    if log_output is not None:
        _log.close()




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", type=str, default="rs41_csdr", help="Operation mode.")
    parser.add_argument("-f", "--files", type=str, default=None, help="Glob-path to files to run over.")
    parser.add_argument("-v", "--verbose", action='store_true', default=False, help="Show additional debug info.")
    parser.add_argument("--shift", type=float, default=0.0, help="Shift the signal-under test by x Hz. Default is 0.")
    parser.add_argument("--batch", action='store_true', default=False, help="Run all tests, write results to results directory.")
    args = parser.parse_args()

    # Check the mode is valid.
    if args.mode not in processing_type:
        print("Error - invalid operating mode.")
        print("Valid Modes: %s" % str(processing_type.keys()))
        sys.exit(1)


    if args.batch:
        for _mode in processing_type:
            _log_name = "./results/" + _mode + ".txt"
            run_analysis(_mode, file_mask=None, shift=args.shift, verbose=args.verbose, log_output=_log_name)
    else:
        run_analysis(args.mode, args.files, shift=args.shift, verbose=args.verbose)
