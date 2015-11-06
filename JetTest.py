#!/usr/bin/env python3

# ############################################################################ #
# JetTest - automate Microsoft Exchange Server Jetstress testing utilizing     #
# the NetJobs and JetEdit tools.                                               #
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
# Usage: JetTest.py [CONFIG_PATH]                                              #
#                                                                              #
# Example: $ JetTest.py config.txt                                             #
# ############################################################################ #

import sys
import re
import os.path
from NetJobs import NetJobs
from JetEdit import JetEdit

path_in = ''
serialNum = 0
config = {
    'maxRuns': None,
    'sharePath': None,
    'jsPath': None,
    'jsExePath': None,
    'mailboxes': None,
    # 'mbStart': None,
    # 'mbStepPass': None,
    # 'mbStepFail': None,
    'iops': None,
    # 'iopsStart': None,
    # 'iopsStepPass': None,
    # 'iopsStepFail': None,
    'duration': None,
    'timeout': None,
    'targets': []
}

verbose = False
currentTestDir = None
currentJetStressConfig = None
currentNetJobsConfig = None
currentMailboxes = None
currentIOPS = None
currentTargetOutPaths = {}
currentTargetConfigPaths = {}
currentResultPass = None

def parseConfig():
    global config
    global lastMailboxes
    global lastIOPS

    try:
        with open(path_in, 'rb') as f:
            targetsBlockReached = False

            for l in f:
                line = l.decode('utf-8').strip()
                # Skip empty lines.
                if not line:
                    continue
                    
                if not targetsBlockReached:
                    tokens = re.split(r' *: *| *', line)
                    numTokens = len(tokens)
                    key = tokens[0].lower()

                    if key == 'sharepath':
                        partial = re.split(r' *: *', line, maxsplit=1)[1]
                        if ((partial.startswith("'") and partial.endswith("'"))
                            or (partial.startswith('"') and partial.endswith('"'))):
                            partial = partial[1:-1]
                        if os.path.exists(partial) and os.path.isdir(partial):
                            config['sharePath'] = partial
                        else:
                            exit('sharepath %s does not exist.' % partial)
                    elif key == 'jetstressconfig':
                        partial = re.split(r' *: *', line, maxsplit=1)[1]
                        if ((partial.startswith("'") and partial.endswith("'"))
                            or (partial.startswith('"') and partial.endswith('"'))):
                            partial = partial[1:-1]
                        if os.path.exists(partial) and os.path.isfile(partial):
                            config['jsPath'] = os.path.abspath(partial)
                        else:
                            exit('jetstressconfig path %s does not exist.' % partial)
                    elif key == 'jetstressexe':
                        partial = re.split(r' *: *', line, maxsplit=1)[1]
                        if ((partial.startswith("'") and partial.endswith("'"))
                            or (partial.startswith('"') and partial.endswith('"'))):
                            partial = partial[1:-1]
                        config['jsExePath'] = partial
                    elif key == 'mailboxes':
                        if config['mailboxes'] == None:
                            config['mailboxes'] = []
                        config['mailboxes'].append(int(tokens[1]))
                        # config['mbStart'] = int(tokens[1])
                        # config['mbStepPass'] = int(tokens[2])
                        # config['mbStepFail'] = int(tokens[3])
                    elif key == 'iops':
                        if config['iops'] == None:
                            config['iops'] = []
                        config['iops'].append(float(tokens[1]))
                        # config['iopsStart'] = float(tokens[1])
                        # config['iopsStepPass'] = float(tokens[2])
                        # config['iopsStepFail'] = float(tokens[3])
                    elif key == 'duration':
                        config['duration'] = int(tokens[1])
                    elif key == 'timeout':
                        config['timeout'] = int(tokens[1])
                    elif key == 'targets':
                        targetsBlockReached = True
                    # elif key == 'maxruns':
                    #     config['maxRuns'] = int(tokens[1])
                    #     if config['maxRuns'] < 1:
                    #         raise Exception('Configuration file invalid. Key maxruns must be > 0.')
                    else:
                        raise Exception('Unable to interpret line: %s.' % line)
                else:
                    if len(config['mailboxes']) != len(config['iops']):
                        exit('Configuration file invalid: number of mailbox configurations does not match number of IOPS.')
                    config['maxRuns'] = len(config['mailboxes'])
                    noneKeys = list(filter(lambda k: config[k] == None, config))
                    if len(noneKeys) > 0:
                        exit('Configuration file invalid: missing fields: %s.'
                             % str(noneKeys))

                    config['targets'].append(line)
    except Exception as e:
        raise e

    for k in config.keys():
        print('%s: %s' % (k, config[k]))

def makeJetstressConfig():
    global currentMailboxes
    global currentIOPS
    global currentJetStressConfig
    global currentTargetConfigPaths

    currentMailboxes = config['mailboxes'][serialNum]
    currentIOPS = config['iops'][serialNum]

    # if currentResultPass == None:
    #     currentMailboxes = config['mbStart']
    #     currentIOPS = config['iopsStart']
    # elif currentResultPass == True:
    #     currentMailboxes += config['mbStepPass']
    #     currentIOPS *= (1.0 + (config['iopsStepPass']/100.0))
    # else:
    #     currentMailboxes -= config['mbStepFail']
    #     currentIOPS *= (1.0 - (config['iopsStepFail']/100.0))

    # Create the config template.
    basename = os.path.basename(path_in)
    serialString = basename + '_{0:04d}_template.jetstressconfig'.format(serialNum)
    jsOutPath = os.path.join(config['sharePath'], currentTestDir, serialString)
    jetEditPath = os.path.abspath(os.path.join('JetEdit', 'JetEdit.py'))
 
    command = ['',  # A quick and dirty hack to make the CLI arguments line up properly.
               'input='+config['jsPath'],
               'output='+jsOutPath,
               'duration='+str(config['duration'])+'m',
               'MailboxCount='+str(currentMailboxes),
               'MailboxIops='+str(currentIOPS)]

    try:
        JetEdit.main(command)
    except Exception as e:
        raise(e)

    # Create separate config files with the output directory customized for each target.
    for target in config['targets']:
        serialString = basename + '_{0:04d}_{1}.jetstressconfig'.format(serialNum, target)
        targetOutPath = os.path.join(config['sharePath'], currentTestDir, target)
        jsOutPath = os.path.join(targetOutPath, serialString)
        # While we're at it, make the output directories.
        os.makedirs(targetOutPath, exist_ok=True)
     
        command = ['',  # A quick and dirty hack to make the CLI arguments line up properly.
                   'input='+config['jsPath'],
                   'output='+jsOutPath,
                   'duration='+str(config['duration'])+'m',
                   'MailboxCount='+str(currentMailboxes),
                   'MailboxIops='+str(currentIOPS),
                   'OutputPath='+targetOutPath]

        currentTargetConfigPaths[target] = jsOutPath

        try:
            JetEdit.main(command)
        except Exception as e:
            raise(e)

    currentJetStressConfig = jsOutPath

def makeNetJobsConfig():
    global currentNetJobsConfig
    global currentTargetOutPaths

    nj_path = os.path.join(currentTestDir, '{0}_{1:04d}.netjobsconfig'.format(path_in, serialNum))
    print('NetJobs config saved as: {}'.format(nj_path))

    try:
        with open(nj_path, 'wb') as f:
            # Test label, timeout/duration.
            f.write(bytes('test_serial_{}:\n'.format(serialNum), 'utf-8'))
            f.write(bytes('-generaltimeout: {}m\n'.format(config['timeout']), 'utf-8'))
            # Target specs.
            for target in config['targets']:
                # The extra set of quotes is necessary to keep NetJobs from stripping the quotes
                # from the file paths.
                jsCommandString = '""{jsExe}" /c "{jsConfig}""'.format(
                    jsExe=config['jsExePath'],
                    jsConfig=currentTargetConfigPaths[target])
                f.write(bytes('{}: {}\n'.format(target, jsCommandString), 'utf-8'))
            f.write(bytes('end', 'utf-8'))
    except Exception as e:
        raise e

    currentNetJobsConfig = nj_path

def runTest():
    global verbose
    try:
        if verbose:
            njargs = ('-l', '-v', currentNetJobsConfig)
        else:
            njargs = ('-l', currentNetJobsConfig)
        NetJobs.main(njargs)
    except Exception as e:
        raise(e)

# def evalResults():
#     global currentResultPass

#     achievedIOPS = {}

#     for target in config['targets']:
#         targetOutPath = currentTargetOutPaths[target]
#         resultPath = getResultPath(targetOutPath)
#         achievedIOPS[target] = None
#         if resultPath == None:
#             raise Exception('Error: no result file found in directory "{}".'.format(
#                 targetOutPath))
#         try:
#             with open(path, 'rb') as f:
#                 for i in range(len(f)):
#                     line = f[i]
#                     if 'Overall Test Result' in line:
#                         if 'Fail' in f[i+1]:
#                             currentResultPass = False
#                             break
#                     elif 'Achieved Transactional I/O per Second' in line:
#                         partial = f[i+1].strip().replace('<td>', '').replace('</td>', '')
#                         achievedIOPS[target] = int(partial)
#         except Exception as e:
#             raise e

#     if currentResultPass == False:
#         return

#     currentResultPass = True

#     # Check to make sure the targets are performing within 40% of each other.
#     maxTarget = max(achievedIOPS, key=achievedIOPS.get)
#     minTarget = min(achievedIOPS, key=achievedIOPS.get)
#     maxIOPS = achievedIOPS[maxTarget]
#     minIOPS = achievedIOPS[minTarget]
#     # Sanity check.
#     if maxIOPS <= 0 or maxIOPS == None:
#         print('WARNING: erroneous maxIOPS reported: {}.'.format(maxIOPS))
#         return

#     percentDelta = minIOPS/maxIOPS * 100

#     if percentDelta <= 60:
#         print('='*80)
#         print('WARNING: target {0} performing significantly worse by {1}%.'
#             .format(minTarget, percentDelta))
#         print('\tBest : {0} || {1} IOPS'.format(maxTarget, maxIOPS))
#         print('\tWorst: {0} || {1} IOPS'.format(minTarget, minIOPS))
#         print('='*80)

# def getResultPath(dir):
#     contents = os.listdir(dir)
#     for name in contents:
#         if re.match('^Performance[^.]*.html$', name) != None:
#             return name
#     return None

#
# Main.
#
def main(argv):
    global verbose
    global path_in
    global js_path
    global serialNum
    global currentTestDir
    global currentResultPass

    argc = len(argv)
    if argc < 2:
        print('Usage: JetTest.py [CONFIG_PATH]')
        exit(1)

    for arg in argv:
        if '-v' in arg:
            verbose = True
        else:
            path_in = arg

    if path_in == None:
        exit('Error: configuration file path not specified.')

    parseConfig()

    # Main loop.
    while serialNum < config['maxRuns']:
        print()
        print('='*80)
        print('Test {} of {}.'.format(serialNum+1, config['maxRuns']))
        print('='*80)
        print()
        # Make the test directory.
        currentTestDir = os.path.join(config['sharePath'], path_in, '{0:04d}'.format(serialNum))
        os.makedirs(currentTestDir, exist_ok=True)
        # Make test configuration files.
        makeJetstressConfig()
        makeNetJobsConfig()
        # Reset current test status.
        currentResultPass = None
        # Start test.
        runTest()
        # evalResults()
        serialNum += 1

    return

# ############################################################################ #
# Execute main.                                                                #
# ############################################################################ #
if __name__ == '__main__':
    main(sys.argv)