# PLEASE READ DISCLAIMER
#
#    This is a sample script for demo and reference purpose only.
#    It is subject to change for content updates without warning.
#
# REQUIREMENTS
#    - Python 2.7 minimum
#    - Python modules: requests
#    - NGPF configuration. (Classic Framework is not supported in ReST)
#    - For ReST API, use Web QuickTest

# DESCRIPTION
#    This sample script demonstrates:
#        - REST API configurations using two back-to-back Ixia ports.
#        - Connecting to Windows IxNetwork API server or Linux API server.
#
#    - Verify for sufficient amount of port licenses before testing.
#    - Verify port ownership.
#    - Load a saved NGPF Quick Test config file.
#    - Reassign Ports:  Exclude calling assignPorts if it's unecessary.
#    - Verify port states.
#    - Apply Quick Test
#    - Start Quick Test
#    - Monitor Quick Test progress
#    - Get stats
#
#    This sample script supports both Windows IxNetwork API server and
#    Linux API server.  If connecting to a Linux API server and the API
#    server is newly installed, it configures the one time global license server settings.
from __future__ import print_function

import ntpath
import shutil
import sys
import os
import traceback
import re
import zipfile
import tempfile
# Include the Ixia ixia in the System Path

# ixnApiPath = os.path.dirname(__file__)+"/ixia"
# sys.path.insert(0, ixnApiPath)
import requests

from ixia.IxNetRestApi import Connect, IxNetRestApiException
from ixia.IxNetRestApiPortMgmt import PortMgmt
from ixia.IxNetRestApiFileMgmt import FileMgmt
from ixia.IxNetRestApiQuickTest import QuickTest
from ixia.IxNetRestApiStatistics import Statistics

API_SERVER_IP = '192.168.51.9'

LICENSE_SERVER_IP = "192.168.51.17"


def extract_file_from_zip(zip_file, file_to_extract):
    zip = zipfile.ZipFile(zip_file, 'r')
    print(zip.namelist())
    file = zip.extract(file_to_extract)
    zip.close()
    return file


def login():
    result = requests.post('https://' + API_SERVER_IP + '/api/v1/auth/session',
                           json={"username": 'admin', "password": 'admin', "rememberMe": "false"}, verify=False)
    return result.json()["apiKey"]


def get_report(session_id, api_key, pdf_path, target_path):
    base_name = ntpath.basename(pdf_path)
    directory = ntpath.dirname(pdf_path)
    headersJson = {"content-type": "application/json", "X-Api-Key": api_key}
    url = session_id + '/ixnetwork/files?filename=%s&absolute=%s' % (
        base_name, directory)
    r = requests.get(url, headers=headersJson, verify=False, stream=True)
    target_path = os.path.join(target_path, 'report.pdf')
    if r.status_code == 200:
        with open(target_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    return target_path


def loadQuickTest(IxVM, quickTestName, configFileName, output_writer, report_attacher=None):
    # Default the API server to either windows or linux.
    osPlatform = 'linux'
    enableDebugTracing = True
    deleteSessionAfterTest = True
    releasePortsWhenDone = False

    output_writer('Preparing Ixia Traffic')

    configFile = extract_file(configFileName)
    report_file = extract_file('report.pdf')

    try:

        # ---------- Preference Settings --------------
        forceTakePortOwnership = True

        quickTestNameToRun = quickTestName
        licenseServer = LICENSE_SERVER_IP
        licenseIsInChassis = False
        licenseModel = 'subscription'

        ixChassisIp = IxVM
        # [chassisIp, cardNumber, slotNumber]
        portList = [[ixChassisIp, '1', '1'],
                    [ixChassisIp, '1', '2']]

        output_writer('Connecting to IxNetwork API')

        ixNetwork = get_ixia_obj(deleteSessionAfterTest, osPlatform)

        # ---------- Preference Settings End --------------

        ixia_ports = PortMgmt(ixNetwork)
        ixia_ports.connectIxChassis(ixChassisIp)

        output_writer('Checking out ports')

        get_ports_ownership(forceTakePortOwnership, portList, ixia_ports)

        output_writer('Configuring license')

        configure_license(ixNetwork, ixia_ports, licenseIsInChassis, licenseModel, licenseServer)

        output_writer('Loading IxNetwork configuration')

        fileMgmtObj = FileMgmt(ixNetwork)
        fileMgmtObj.loadConfigFile(configFile)

        output_writer('Assigning ports')

        ixia_ports.assignPorts(portList, createVports=False)

        output_writer('Validating port state')

        ixia_ports.verifyPortState()

        output_writer('Loading QuickTest ' + quickTestNameToRun)

        quickTestObj = QuickTest(ixNetwork, fileMgmtObj)
        quickTestHandle = quickTestObj.getQuickTestHandleByName(quickTestNameToRun)

        output_writer('Applying QuickTest')

        quickTestObj.applyQuickTest(quickTestHandle)

        output_writer('Starting QuickTest')

        quickTestObj.startQuickTest(quickTestHandle)

        output_writer('Validating QuickTest Initialization')

        quickTestObj.verifyQuickTestInitialization(quickTestHandle, output_writer)

        quickTestObj.monitorQuickTestRunningProgress(quickTestHandle, output_writer=output_writer,
                                                     getProgressInterval=1)

        report_path = quickTestObj.getQuickTestPdf(quickTestHandle)
        api_key = login()

        temp_dir = tempfile.mkdtemp()
        try:
            report_file = get_report(ixNetwork.sessionId, api_key, report_path, temp_dir)
            if report_attacher:
                report_attacher(report_file)
        finally:
            shutil.rmtree(temp_dir)
        # quickTestObj.getQuickTestCsvFiles(quickTestHandle, copyToPath='c:\\Results', csvFile='all')

        # # Copy result files from Windows API server to remote Linux.
        # quickTestObj.getQuickTestPdf(quickTestHandle, copyToLocalPath='/home/hgee', where='remoteLinux',
        #                              renameDestinationFile='rfc2544.pdf', includeTimestamp=True)
        # quickTestObj.getQuickTestCsvFiles(quickTestHandle, copyToPath='/home/hgee', csvFile='all')

        statObj = Statistics(ixNetwork)
        stats = statObj.getStats(viewName='Flow View')
        result_s = ''

        for flowGroup, values in stats.items():
            for value in values:
                result_s += '\n' + value + ' ' + values[value]
            # txPort = values['Tx Port']
            # rxPort = values['Rx Port']
            # rxThroughput = values['Rx Throughput (% Line Rate)']
            # txFrameCount = values['Tx Count (frames)']
            # rxFrameCount = values['Rx Count (frames)']
            # frameLoss = values['Frame Loss (frames)']
            #
            # print('{txPort:15} {rxPort:15} {rxThruPut:10} {txFrames:15} {rxFrames:10} {frameLoss:10}'.format(
            #     txPort=txPort, rxPort=rxPort, rxThruPut=rxThroughput, txFrames=txFrameCount, rxFrames=rxFrameCount, frameLoss=frameLoss))
            #

        if releasePortsWhenDone == True:
            ixia_ports.releasePorts(portList)

        if osPlatform == 'linux':
            ixNetwork.linuxServerStopAndDeleteSession()

        if osPlatform == 'windowsConnectionMgr':
            ixNetwork.deleteSession()

        return result_s

    except (IxNetRestApiException, Exception, KeyboardInterrupt):
        if enableDebugTracing:
            if not bool(re.search('ConnectionError', traceback.format_exc())):
                print('Exception!')
                print('\n%s' % traceback.format_exc())

        if 'mainObj' in locals() and osPlatform == 'linux':
            if deleteSessionAfterTest:
                ixNetwork.linuxServerStopAndDeleteSession()

        if 'mainObj' in locals() and osPlatform in ['windows', 'windowsConnectionMgr']:
            if releasePortsWhenDone and forceTakePortOwnership:
                ixia_ports.releasePorts(portList)

            if osPlatform == 'windowsConnectionMgr':
                if deleteSessionAfterTest:
                    ixNetwork.deleteSession()

        return ''


def extract_file(configFileName):
    if '.zip' in os.path.dirname(__file__):
        configFile = extract_file_from_zip(os.path.dirname(__file__), configFileName)
    else:
        configFile = os.path.join(os.path.dirname(__file__), configFileName)
    return configFile


def configure_license(ixia, ixia_ports, licenseIsInChassis, licenseModel, licenseServer):
    # If the license is activated on the chassis's license server, this variable should be True.
    # Otherwise, if the license is in a remote server or remote chassis, this variable should be False.
    # Configuring license requires releasing all ports even for ports that is not used for this test.
    if licenseIsInChassis == False:
        ixia_ports.releaseAllPorts()
        ixia.configLicenseServerDetails([licenseServer], licenseModel, licenseTier='tier2')


def get_ports_ownership(forceTakePortOwnership, portList, portObj):
    if portObj.arePortsAvailable(portList, raiseException=False) != 0:
        if forceTakePortOwnership == True:
            portObj.releasePorts(portList)
            portObj.clearPortOwnership(portList)
            print("Reserved ports")
        else:
            raise IxNetRestApiException('Ports are owned by another user and forceTakePortOwnership is set to False')


def get_ixia_obj(deleteSessionAfterTest, osPlatform):
    if osPlatform == 'linux':
        mainObj = Connect(apiServerIp=API_SERVER_IP,
                          serverIpPort='443',
                          username='admin',
                          password='admin',
                          deleteSessionAfterTest=deleteSessionAfterTest,
                          verifySslCert=False,
                          serverOs=osPlatform,
                          # generateLogFile='ixiaDebug.log'
                          )
    if osPlatform in ['windows', 'windowsConnectionMgr']:
        mainObj = Connect(apiServerIp=API_SERVER_IP,
                          # serverIpPort='11009',
                          serverIpPort='443',
                          serverOs=osPlatform,
                          deleteSessionAfterTest=deleteSessionAfterTest,
                          # generateLogFile='ixiaDebug.log'
                          )
    return mainObj


if __name__ == '__main__':
    # loadQuickTest(IxVM='192.168.51.11',quickTestName='RFC_TEST',configFileName='config.ixncfg')
    output_logger = lambda message: print(message)
    test = 'rfc2544_frameloss'
    config = 'rfc_2544_frameloss.ixncfg'

    loadQuickTest(IxVM='192.168.51.45', quickTestName=test, configFileName=config,
                  output_writer=output_logger)
    # loadQuickTest(IxVM='192.168.51.42',quickTestName='rfc2544_frameloss',configFileName='rfc_2544_frameloss.ixncfg',
    #                output_writer= output_logger)
