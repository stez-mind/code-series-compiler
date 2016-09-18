# M-Audio Code Series Preset Compiler

A small pure Python script to generate binary Sysex files for the M-Audio Code Series controller keyboards from a JSON specification.

This is work in progress, does not configure all the parameters yet and has only been tested with the Code25 model. Use it at your own risk - from my trials the Code seemed robust to malformed dumps, but I won't be responsible for bricking your controller ;)

## Instructions

1. Dump the first default preset from your Code and put it inside `data/code25_default_dump.syx`. Compute a MD5 hash on it and check that it's the same as given in that directory README.
2. Edit your JSON preset starting from the given example
3. Run `./gen_code_sysex your_preset.json` to compile it into binary Sysex (use `-h | --help` to see more command line options)
4. Use whatever Sysex utility to flash it to your keyboard

## JSON Preset Syntax

**TODO**: add all the details.
For now, just dig into the file that I hope should be decently self explaining.

The preset is stored as a single dictionary. Top-level fields are:

  * `global` : preset name and number. `name` and `number` subfields are only used for (future) internal purposes.
  * `zones` : keyboard zone definition, as list of zones 1-4
  * `pitch_wheel`
  * `mod_wheel`
  * `pad_x`
  * `pad_y`
  * `pads` : list of 16 pad config maps. The `number` field is not used by the compiler, it's just there for easier manual editing of JSONs. For documentation on the color sequence and meaning of `data?` fields, refer to the CodeSeries User Guide. The possible values for `mode` are:
    - `cc`
    - `program_change`
    - `cc_latch`
    - `note_on`
    - `mmc`
    - `cc_inc`
    - `cc_dec`
    - `program_inc`
    - `program_dec`
  * `buttons` : list of 16 button config maps. Format is the same as for the pads.
  * `encoders` : list of 16 rotary encoder config maps. `mode` field can be either `"cc"` or `"pitch_wheel"`
  * `faders` : list of 20 fader config maps. Format is the same as for encoders


## The MIT License (MIT)
Copyright (c) 2016 Stefano Zambon

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
