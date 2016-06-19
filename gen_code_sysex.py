"""gen_code_sysex.py: Generate CODE series Sysex dumps from JSON file"""
__copyright__   = "Copyright (C) 2016 Stefano Zambon"

import os
import array as pyarray
import struct
import argparse
import json

######################
#  Module constants  #
######################

DEFAULT_SYSEX_TEMPLATE = 'data/code25_default_dump.syx'

###########################
#  Preset dump constants  #
###########################

PRESET_NUMBER_OFFSET = 10
PRESET_NAME_OFFSET = 11
PRESET_NAME_LENGTH = 6

ZONES_START_OFFSET = 18
ZONE_STRUCTURE_LEN = 9
PADS_START_OFFSET = 75
PAD_STRUCTURE_LEN = 14
BUTTONS_START_OFFSET = 299
BUTTON_STRUCTURE_LEN = 17
ENCODERS_START_OFFSET = 759
ENCODER_STRUCTURE_LEN = 6
FADERS_START_OFFSET = 639
FADER_STRUCTURE_LEN = 6
WHEELS_START_OFFSET = 53
WHEEL_STRUCTURE_LEN = 5
XYPAD_START_OFFSET = 855
XYPAD_STRUCTURE_LEN = 15

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

CC_CONTROL_MAP = {
    'cc' : 0,
    'pitch_wheel' : 1
}

CC_OFFSETS_MAP = {
    'channel' : 0,
    'mode' : 1,
    'cc' : 2,
    'min_val' : 4,
    'max_val' : 5
}

WHEELS_OFFSETS_MAP = {
    'channel' : 0,
    'mode' : 1,
    'cc' : 2,
    'min_val' : 3,
    'max_val' : 4
}


######################
#  Helper functions  #
######################

def modify_preset_name(dump, name):
    sanitized_name = (name.upper() + ' ' * (PRESET_NAME_LENGTH - len(name)))[:PRESET_NAME_LENGTH]
    dump[PRESET_NAME_OFFSET:PRESET_NAME_OFFSET+PRESET_NAME_LENGTH] = pyarray.array('B', str(sanitized_name))

def modify_zone_data(dump, idx, config):
    offset = ZONES_START_OFFSET + idx * ZONE_STRUCTURE_LEN
    dump[offset] = config['channel']
    dump[offset+1] = config['program']
    dump[offset+2] = config['bank_msb']
    dump[offset+3] = config['bank_lsb']
    dump[offset+4] = config['start_key']
    dump[offset+5] = config['end_key']
    dump[offset+6] = config['octave'] + 5
    dump[offset+7] = config['transpose'] + 12

def modify_pad_data(dump, idx, config,
                    start_offset, structure_len):
    """Modify pad or button structure in binary dump according to given config.

        Input:
            dump          : dump to modify
            idx       : index of pad/button
            config    : dictionary with pad/button paramters
            start_offset  : byte offset of first pad/button
            structure_len : length in bytes of structure for single control
    """

    offset = start_offset + idx * structure_len
    if config['mode'] == 'cc':
        mode_byte = 0
        control_byte = config['cc']
    else:
        mode_byte = 1
        control_byte = PADS_CONTROL_MAP[config['mode']]

    dump[offset] = config['channel']
    dump[offset+1:offset+5] = pyarray.array('B', config['colors'])
    dump[offset+5] = mode_byte
    dump[offset+6] = control_byte
    dump[offset+7] = config['data1']
    dump[offset+8] = config['data2']
    dump[offset+9] = int(not config['data4_active'])
    dump[offset+10] = config['data4']
    dump[offset+11] = int(not config['data5_active'])
    dump[offset+12] = config['data5']
    dump[offset+13] = config['data3']

def modify_cc_control_data(dump, idx, config,
                           start_offset, structure_len, offsets_map):
    offset = start_offset + idx * structure_len
    if config['mode'] == 'cc':
        mode_byte = 0
        control_byte = config['cc']
    elif config['mode'] == 'pitch_wheel':
        mode_byte = 1
        control_byte = 16
    else:
        raise ValueError, "Invalid mode in config entry %s" % config

    dump[offset + offsets_map['channel']] = config['channel']
    dump[offset + offsets_map['mode']] = mode_byte
    dump[offset + offsets_map['cc']] = control_byte
    dump[offset + offsets_map['min_val']] = config['min_val']
    dump[offset + offsets_map['max_val']] = config['max_val']

def create_preset_dump(preset_config_filename,
                    sysex_template_filename=DEFAULT_SYSEX_TEMPLATE):

    with open(preset_config_filename) as infile:
        preset = json.load(infile)
    with open(sysex_template_filename, 'rb') as infile:
        dump = pyarray.array('B', infile.read())

    # Globals
    dump[PRESET_NUMBER_OFFSET] = preset['global']['number']
    modify_preset_name(dump, preset['global']['display_name'])

    # Zones
    for idx, cfg in enumerate(preset['zones']):
        modify_zone_data(dump, idx, cfg)

    # Pads & buttons
    for idx, cfg in enumerate(preset['pads']):
        modify_pad_data(dump, idx, cfg,
                        PADS_START_OFFSET, PAD_STRUCTURE_LEN)
    for idx, cfg in enumerate(preset['buttons']):
        modify_pad_data(dump, idx, cfg,
                        BUTTONS_START_OFFSET, BUTTON_STRUCTURE_LEN)

    # CC-like controls
    modify_cc_control_data(dump, 0, preset['pitch_wheel'],
                           WHEELS_START_OFFSET, WHEEL_STRUCTURE_LEN, WHEELS_OFFSETS_MAP)
    modify_cc_control_data(dump, 1, preset['mod_wheel'],
                           WHEELS_START_OFFSET, WHEEL_STRUCTURE_LEN, WHEELS_OFFSETS_MAP)
    modify_cc_control_data(dump, 0, preset['pad_x'],
                           XYPAD_START_OFFSET, XYPAD_STRUCTURE_LEN, CC_OFFSETS_MAP)
    modify_cc_control_data(dump, 1, preset['pad_y'],
                           XYPAD_START_OFFSET, XYPAD_STRUCTURE_LEN, CC_OFFSETS_MAP)
    for idx, cfg in enumerate(preset['encoders']):
        modify_cc_control_data(dump, idx, cfg,
                               ENCODERS_START_OFFSET, ENCODER_STRUCTURE_LEN, CC_OFFSETS_MAP)
    for idx, cfg in enumerate(preset['faders']):
        modify_cc_control_data(dump, idx, cfg,
                               FADERS_START_OFFSET, FADER_STRUCTURE_LEN, CC_OFFSETS_MAP)

    # Generate dump string from array
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

    new_dump = create_preset_dump(preset_config_filename=preset_filename,
                                  sysex_template_filename=args.template)
    with open(output_filename, 'wb') as outfile:
        outfile.write(new_dump)

