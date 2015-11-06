# JetTest - Jetstress Test Suite README

## License
Copyright (c) 2015 DeepStorage, LLC (deepstorage.net) and Ramon A. Lovato (ramonalovato.com).

See the file LICENSE for copying permission.

Author: Ramon A. Lovato (ramonalovato.com)
For: DeepStorage, LLC (deepstorage.net)

## Introduction

The JetTest is a set of additional command-line tools to facilitate benchmark testing with the Microsoft Exchange Server Jetstress tool. It consists of three components:
- JetEdit: a tool for more easily modifying certain parameters in Jetstress XML configuration files.
- NetJobs: a tool for scheduling jobs on network machines and synchronizing their start times.
- JetTest: a wrapper script that uses the previous two tools to help automate the Jetstress test process.

## Requirements

- Microsoft Exchange Server Jetstress 2013
- Python 3
- n more-or-less-identical Windows Server virtual or physical target machines:
    - Jetstress installed in identical location.
    - Python 3 installed with identical interpreter name/path.
    - Connected to a file share with identical path on all targets and the machine hosting the control center.
    - Windows Firewall DISABLED or set to allow inbound connections on port 16192.
    - NetJobsAgent.py running from cmd.exe (NOT PowerShell).

## Tools

A note on runtime environment--Python maintains two active versions: Python 2 and Python 3. As of this writing, the most recent versions are 2.7.10 and 3.5.0. Python 2 installations are far more common than Python 3, but all scripts included with the test suite require Python 3 and are not compatible with Python 2. Depending on your particular runtime environment and which version(s) of Python you have installed, the name of the Python interpreter could be one of:
- python
- python3
- python3.x, where x is the minor version number

This README assumes a Python 3 interpreter name of "python" in all examples. However, you may need to adjust this for your particular environment.

### JetEdit

JetEdit takes a Jetstress XML configuration file, typically generated using the Jetstress GUI. It allows for easy modification of a few key parameters.

When using NetTest, JetEdit configuration is handled automatically by NetTest. A sample configuration file must be provided.

### NetJobs

NetJobs consists of two components: the control center or client, NetJobs.py; and the agent server, NetJobsAgent.py. NetJobsAgent.py runs as a blocking, CLI-based server, which listens for connections from the control center and runs jobs on its behalf. NetJobs.py takes a configuration file and causes all specified agents to run independent jobs. Please see the NetJobs README for more detailed information.

When running JetTest, NetJobs client configuration is handled automatically by NetTest. However, NetJobsAgent.py must be running on all target machines.

### JetTest

This wrapper script facilitates the automation of Jetstress testing using the previous two tools. NetJobsAgent.py must be running on all target machines, and all target machines must have the same path to Jetstress.exe. All target machines and the controller must also be connected to a public file share with the same path. The share can be stored locally on the controller if desired but must be mapped to the same path as on the target machines using "net use z: \\127.0.0.1", where z: is the drive letter/path for all machines.

JetTest requires a configuration file of the following format (empty lines are ignored):

sharepath: [shared directory path]
jetstressconfig: [Jetstress config template]
jetstressexe: [target machines path to Jetstress.exe]
mailboxes: [mailbox count (positive integer)]
iops: [IOPS count (positive float)]
mailboxes: [mailbox count (positive integer)]
iops: [IOPS count (positive float)]
...
duration: [test duration (in minutes)]
timeout: [test timeout period for NetJobs (in minutes)]
targets:
xxx.xxx.xxx.xxx
xxx.xxx.xxx.xxx
...

*Example:*

sharepath: "Z:\JetTest\share"
jetstressconfig: "sample_config.txt"
jetstressexe: "C:\Program Files\Jetstress\Jetstress.exe"
mailboxes: 1000
iops: 0.5
mailboxes: 2000
iops: 0.25
duration: 120
timeout: 360
targets:
192.168.0.2
192.168.0.3
192.168.0.4



The "mailboxes" and "iops" keys may be repeated an arbitrary number of times, but there must be an equal number of each. Each pair of "mailboxes"/"iops" keys creates an additional test iteration with those parameters. Key-value pairs may be specified in any order, but the targets listing must be the last entry in the final. Any lines read after the "targets" key are automatically assumed to be target addresses.

Assuming a configuration file named "example.txt" and a shared directory of [SHARE], JetTest creates the following directory structure.

[SHARE]\example.txt\XXXX\yyy.yyy.yyy.yyy

Where XXXX is 0000, 0001, ..., maxruns-1 and yyy.yyy.yyy.yyy are the targets, where "maxruns" = the number of "mailboxes/iops" keys.

When using JetTest, the NetJobs configuration is generated and run automatically. A sample Jetstress configuration XML file must be provided as jetstressconfig. We recommend generating the sample XML using the Jetstress GUI.

JetTest attempts to perform maxruns tests using all specified target machines. Each machine must have Jetstress installed in the same location, must have access to the public file share sharepath, and must be running NetJobsAgent.py. JetTest waits for all target machines to complete or time out their current test before continuing to the next.

The duration field is assumed to be in minutes and is passed directly to Jetstress. The timeout field is also assumed to be in minutes and is used by NetJobs to determine when a test has stalled and should be abandoned. Due to the possibility of extreme setup/cleanup times for JetStress, generous timeout values should be used.



This document was last updated on 11/06/15.