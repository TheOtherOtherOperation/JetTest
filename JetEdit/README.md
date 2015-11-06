# JetEdit

## License
Copyright (c) 2015 DeepStorage, LLC (deepstorage.net) and Ramon A. Lovato (ramonalovato.com).

See the file LICENSE for copying permission.

Author: Ramon A. Lovato (ramonalovato.com)
For: DeepStorage, LLC (deepstorage.net)
Version: 1.0

## Instructions

JetEdit takes a Jetstress XML configuration file, typically generated using the Jetstress GUI. It allows for easy modification of the following parameters:
- MultiHostBreak
- Duration
- OutputPath
- MailboxCount
- MailboxQuota
- MailboxIops

Usage: python JetEdit.py input=[PATH_IN] output=[PATH_OUT] [TAG]=[VALUE] [TAG]=[VALUE] [TAG]=[VALUE] ...

Where [TAG] represents one of the above modifiable parameters, and [VALUE] represents a valid value for that tag, [PATH_IN] represents the path to the input file to be modified (the original is left untouched), and [PATH_OUT] represents the path of the output file to generate.

The Duration tag may be specified in the form [VALUE][UNIT] (e.g. '90m' for 90 minutes), where VALUE is a positive integer and UNIT is one of 'h', 'm', or 's'. All other tags are substituted verbatim.

Example: $ python JetEdit.py input='oldconfig.xml' output='newconfig.xml' Duration=15m MailboxCount=200 MailboxIops=10