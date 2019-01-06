# CNCmusic
A script that generates G-code that when executed on a CNC machine sounds like music

usage: cnc_music.py [-h] [--steps-per-mm STEPS_PER_MM] [--x-limit X_LIMIT] [--tempo TEMPO] [--output OUTPUT] sequence_file

By default the script assumes that your CNC machine does 100 steps per mm. It will make the CNC travel up +100mm 
from the starting position. Also by default the generated G-code goes to stdout, but you can use the --output option
to specify an output file.

---

## Sequency file format

The sequenc_file is a text file containing the musical notes that you want to be translated into G-code.

Each line of this text file is a pair of note symbol and note value.

Note symbols are in letter notation (C D E F G A B), followed by an octave number (3, 4, 5) and optionally followed by 
a "b" for flat or # for sharp.

Note value should be one of the following 8, 4, 2, 1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128, 1/256. The value can be 
followed by up to 3 dots for dotted values.

You can use a 0 in place of the note symbol to specify a rest. Of course you still have to enter a note value for the rest.
