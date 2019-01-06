#!/usr/bin/env python3

import re
import sys
import argparse

FREQ = {
    "0": 0, # This is used for "rest"
    "C3": 130.81, "C3#": 138.59,
    "D3b": 138.59, "D3": 146.83, "D3#": 155.56,
    "E3b": 155.56, "E3": 164.81,
    "F3": 174.61, "F3#": 185.00,
    "G3b": 185.00, "G3": 196.00, "G3#": 207.65,
    "A3b": 207.65, "A3": 220.00, "A3#": 233.08,
    "B3b": 233.08, "B3": 246.94,
    "C4": 261.63, "C4#": 277.18,
    "D4b": 277.18, "D4": 293.66, "D4#": 311.13,
    "E4b": 311.13, "E4": 329.63,
    "F4": 349.23, "F4#": 369.99,
    "G4b": 369.99, "G4": 392.00, "G4#": 415.30,
    "A4b": 415.30, "A4": 440, "A4#": 466.16,
    "B4b": 466.16, "B4": 493.88,
    "C5": 523.25, "C5#": 554.37,
    "D5b": 554.37, "D5": 587.33, "D5#": 622.25,
    "E5b": 622.25, "E5": 659.25,
    "F5": 698.46, "F5#": 739.99,
    "G6b": 739.99, "G5": 783.99, "G5#": 830.61,
    "A5b": 830.61, "A5": 880.00, "A5#": 932.33,
    "B5b": 932.33, "B5": 987.77,
}

parser = argparse.ArgumentParser()
parser.add_argument("sequence_file", help="The music sheet (a text file containig notes and note values pairs)")
parser.add_argument("--steps-per-mm", dest="steps_per_mm", type=int, default=100, help="How many steps per mm does your CNC machine in the X axis")
parser.add_argument("--x-limit", dest="x_limit", type=int, default=100, help="What is the maximum X in mm that you want your CNC machine to reach")
parser.add_argument("--tempo", dest="tempo", type=float, default=1.0, help="Tempo")
parser.add_argument("--output", dest="output", type=str, default=None, help="Write output to a file rather than printing to stdout")
args = parser.parse_args()

if args.output:
    output_file = open(args.output, "w")
    gcode_write = lambda x: output_file.write(x+'\n')
else:
    gcode_write = print

try:
    sequence = open(args.sequence_file, 'r')
except IOError as e:
    if e.errno == 2:
        print("Unable to find the sequence file: %s" % args.sequence_file)
        sys.exit(1)
    else:
        print("Unable to open the sequence file: %s" % args.sequence_file)
        sys.exit(1)

# This is a scaling factor. Multiply this by the desired output frequency, to get the feed rate in mm/min.
# feed_rate = freq * ( 60 / steps_per_mm )
feed_rate_scale = 60.0 / args.steps_per_mm

# Set the CNC machine to incremental mode
gcode_write("G91")

line_counter = 0
current_position = 0
direction_flag = True
for line in sequence.readlines():
    line_counter += 1
    
    if line[0] == "#":
        # Ignore comment line
        continue
    
    line = line.rstrip()
    
    if line == '':
        continue
    
    try:
        m = re.findall("(.*?)\s+(\d/?\d*)(\.?\.?\.?)", line)[0]
        
        note = m[0]
        
        note_value = m[1]
        
        dots = m[2].count(".")
        if dots == 0:
            dot_multiplier = 1
        elif dots == 1:
            dot_multiplier = 1.5
        elif dots == 2:
            dot_multiplier = 1.75
        elif dots == 3:
            dot_multiplier = 1.875
        else:
            print("You can't have more than 3 dots")
            print("Error in line %d (%s)" % (line_counter, line))
    except IndexError as e:
        print("Unable to parse line %d (%s)" % (line_counter, line))
        sys.exit(1)
    
    frequency = FREQ[note]
    
    # ".0" is a little hack here to avoid uglier things, but still allow us to evaluate note_values as floats
    duration = eval(note_value+".0") * dot_multiplier * (1 / (60 * args.tempo))
    
    if frequency == 0:
        # If frequency is 0 we need to execute a rest. This can be done with a dwell command
        
        # Dwel command expects a duration in ms, so that is why we multiply by 1000 here
        gcode_write("G04 P%0.2f" % round(duration * 1000))
    else:
        # Execute a G01 with the right distance and feed_rate, in order to "play" the desired note
        
        feed_rate = int(frequency / feed_rate_scale)
        
        distance = feed_rate * duration
        
        if not direction_flag:
            distance = -distance
        
        # Update the position
        projected_position = current_position + distance
        
        if projected_position > args.x_limit:
            direction_flag = False
            distance = -distance
            projected_position = current_position + distance
        elif projected_position < 0:
            direction_flag = True
            distance = -distance
            projected_position = current_position + distance
        
        gcode_write("G01 X%0.2f F%d" % (distance, feed_rate))
        
        current_position = projected_position

# Return the CNC gantry to the initial position
gcode_write("G00 X%0.2f" % (-current_position))
