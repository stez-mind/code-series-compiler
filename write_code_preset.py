"""write_code_preset.py: Generate CODE series Sysex dumps from JSON file"""
__copyright__   = "Copyright (C) 2016 Stefano Zambon"

import os
import array as pyarray
import struct
import argparse
import json

######################
#  Module constants  #
######################

DEFAULT_SYSEX_TEMPLATE = 'code25_default_dump.syx'

###########################
#  Preset dump constants  #
###########################

PRESET_NUMBER_OFFSET = 10
PRESET_NAME_OFFSET = 11
PRESET_NAME_LENGTH = 6
PADS_START_OFFSET = 75
PAD_DUMP_BYTES_LENGTH = 14

######################
#  Helper functions  #
######################

def modify_preset_name(name, dump):
    sanitized_name = (name.upper() + ' ' * (PRESET_NAME_LENGTH - len(name)))[:PRESET_NAME_LENGTH]
    dump[PRESET_NAME_OFFSET:PRESET_NAME_OFFSET+PRESET_NAME_LENGTH] = pyarray.array('B', str(sanitized_name))

def modify_pad_data(pad_config, dump):
    pad_num = pad_config['number']
    offset = PADS_START_OFFSET + (pad_num-1) * PAD_DUMP_BYTES_LENGTH
    print "Pad %d, start offset: %d" % (pad_num, offset)
    PADS_CONTROL_MAP = {
        'cc' : None,
        'program_change' : 17,
        'cc_latch' : 18,
        'note_on' : 19,
        'mmc' : 21,
        'cc_inc' : 25,
        'cc_dec' : 26,
        'program_inc' : 27,
        'program_dec' : 28
    }
    if pad_config['mode'] == 'cc':
        mode_byte = 0
        control_byte = pad_config['cc']
    else:
        mode_byte = 1
        control_byte = PADS_CONTROL_MAP[pad_config['mode']]

    dump[offset] = pad_config['channel']
    print "Pad %d, channel: %s" % (pad_num, pad_config['channel'])
    dump[offset+1:offset+5] = pyarray.array('B', pad_config['colors'])
    print "Pad %d, colors: %s" % (pad_num, pad_config['colors'])
    dump[offset+5] = mode_byte
    print "Pad %d, mode byte: %s" % (pad_num, mode_byte)
    dump[offset+6] = control_byte
    print "Pad %d, control byte: %s" % (pad_num, control_byte)
    dump[offset+7] = pad_config['data1']
    print "Pad %d, data1: %s" % (pad_num, pad_config['data1'])
    dump[offset+8] = pad_config['data2']
    print "Pad %d, data2: %s" % (pad_num, pad_config['data2'])
    dump[offset+13] = pad_config['data3']
    print "Pad %d, data3: %s" % (pad_num, pad_config['data3'])

def get_preset_dump(preset_config_filename,
                    sysex_template_filename=DEFAULT_SYSEX_TEMPLATE):

    with open(preset_config_filename) as infile:
        preset = json.load(infile)
    with open(sysex_template_filename, 'rb') as infile:
        dump = pyarray.array('B', infile.read())

    # Globals
    dump[PRESET_NUMBER_OFFSET] = preset['number']
    modify_preset_name(preset['display_name'], dump)

    # Pads
    for pad_cfg in preset['pads']:
        modify_pad_data(pad_cfg, dump)

    dump_str = struct.pack('%dB' % len(dump), *dump)
    return dump_str

if __name__ == '__main__':
    # CL arguments parse
    parser = argparse.ArgumentParser()
    parser.add_argument("preset", type=str, nargs=1, help="Input preset config file (.json)")
    parser.add_argument("-o", "--output", type=str, nargs='?', help="Output sysex file")
    parser.add_argument("-t", "--template", default=DEFAULT_SYSEX_TEMPLATE, type=str, help="Specify sysex template file (.syx)")
    args = parser.parse_args()

    preset_filename = args.preset[0]
    if (args.output is None):
        output_filename = os.path.splitext(os.path.basename(preset_filename))[0] + '.syx'
    else:
        output_filename = args.output
    if os.path.isfile(output_filename):
        raise ValueError, "Output file exists"

    new_dump = get_preset_dump(preset_config_filename=preset_filename,
                               sysex_template_filename=args.template)
    with open(output_filename, 'wb') as outfile:
        outfile.write(new_dump)

