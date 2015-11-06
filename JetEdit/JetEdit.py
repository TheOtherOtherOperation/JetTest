#!/usr/bin/env python3

# ############################################################################ #
# JetEdit - modify Jetstress XML config files.                                 #
#                                                                              #
# Copyright (c) 2015 DeepStorage, LLC (deepstorage.net)                        # 
#     and Ramon A. Lovato (ramonalovato.com).                                  #
#                                                                              #
# See the file LICENSE for copying permission.                                 #
#                                                                              #
# Author: Ramon A. Lovato (ramonalovato.com)                                   #
# For: Deepstorage, LLC (deepstorage.net)                                      #
# Version: 1.0                                                                 #
#                                                                              #
# Usage: JetEdit.py input=[PATH_IN] output=[PATH_OUT] [TAG]=[VALUE]            #
#        [TAG]=[VALUE] [TAG]=[VALUE] ...                                       #
# PATH_IN                                                                      #
#   Relative or absolute path to input configuration file (required).          #
# PATH_OUT                                                                     #
#   Where to create the output configuration file (required).                  #
# TAG                                                                          #
#   Which XML tag you want to change. Any tag not specified will retain its    #
#   input value.                                                               #
# VALUE                                                                        #
#   The new value for the associated tag. The Duration tag may be specified in #
#   the form [VALUE][UNIT] (e.g. '90m' for 90 minutes), where VALUE is a       #
#   positive integer and UNIT is one of 'h', 'm', or 's'. All other tags are   #
#   substituted verbatim.                                                      #
#                                                                              #
# Example: $ JetEdit.py input='oldconfig.xml' output='newconfig.xml'           #
#            Duration=15m MailboxCount=200 MailboxIops=10                      #
# ############################################################################ #

import sys
import re
import xml.etree.ElementTree as ET

TIME_FORMAT_REGEX = '\d+ *[hms]'

path_in = ''
path_out = ''
tags = {
    'MultiHostBreak': '',
    'Duration': '',
    'OutputPath': '',
    'MailboxCount': '',
    'MailboxQuota': '',
    'MailboxIops': ''
}

#
# Evaluate CLI arguments.
#
def eval_args(args):
    global path_in
    global path_out
    global tags

    # Ignore arg[0], since that contains the script name.
    for arg in args[1:]:
        tokens = re.split('=', arg, maxsplit=1)

        # Short-circuits if len(tokens) < 2.
        if len(tokens) < 2 or len(tokens[1]) == 0:
            exit('Argument missing value: ' + arg)
        else:
            key = tokens[0].lower()
            value = tokens[1]
            if (value.startswith('"') and value.endswith('"')) or (value.startswith('\'') and value.endswith('\'')):
                value = value[1:-1]

            valid = False
            for tag in tags.keys():
                if tag.lower() == key:
                    valid = True
                    if tag == 'Duration':
                        tags['Duration'] = eval_duration(value)
                    else:
                        if value.lower() == 'true' or value.lower() == 'false':
                            value = value.lower()
                        tags[tag] = value
                    print('Tag: <%s> = %s' % (tag, tags[tag]))
                    break

            if not valid:
                if key == 'input':
                    path_in = value
                    print('Input path = ' + path_in)
                elif key == 'output':
                    path_out = value
                    print('Output path = ' + path_out)
                else:
                    # Didn't find a match.
                    exit('Invalid argument: ' + arg)


#
# Evaluate duration argument.
#
def eval_duration(duration):
    time_format_regex = re.compile(TIME_FORMAT_REGEX)
    if time_format_regex.match(duration) == None:
        exit('Invalid duration: ' + duration)

    unit = duration[-1] # Last character in string.
    value = int(duration[:-1]) # Everything except last character in string.

    days = 0
    hours = 0
    minutes = 0
    seconds = 0

    if unit is 'h':
        days = int(value / 24)
        hours = value % 24
    elif unit is 'm':
        days = int(value / (24 * 60))
        hours = int(value / 60)
        minutes = value % 60
    else:
        days = int(value / (24 * 60 * 60))
        hours = int(value / (60 * 60))
        minutes = int(value / 60)
        seconds = value % 60
        
    result = 'P0Y0M' + str(days) + 'DT' + str(hours) + 'H' + str(minutes) + 'M' + str(seconds) + 'S'

    return result

#
# Start the main run.
#
def start():
    global path_in
    global path_out

    if path_in == '':
        path_in = ask_for_path('input')
        print('Input path = ' + path_in)
    if path_out == '':
        path_out = ask_for_path('output')
        print('Output path = ' + path_out)

    try:
        tree = ET.parse(path_in)
    except IOError as e:
        exit('Error opening input file "%s": %s' % (path_in, str(e)))

    for key in tags.keys():
        if not tags[key] == '':
            value = tags[key]
            nodes = tree.iter(tag=key)
            for node in nodes:
                print('Changing <%s>%s</%s> --> <%s>%s</%s>' % (node.tag, node.text, node.tag, node.tag, value, node.tag))
                node.text = value

    try:
        tree.write(path_out, encoding=False, xml_declaration=True, method='xml')
        print('New XML file saved as: %s' % path_out)
    except IOError as e:
        exit('Error saving output file "%s": %s' % (path_out, str(e)))

#
# Ask for file path.
#
def ask_for_path(message):
    return input('Please enter the %s file path: ' % message)

#
# Main.
#
def main(argv):
    eval_args(argv)
    start()

    return

# ############################################################################ #
# Execute main.                                                                #
# ############################################################################ #
if __name__ == '__main__':
    main(sys.argv)