#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cloudshell.helpers.scripts.cloudshell_dev_helpers as dev_helpers
from cloudshell.api.cloudshell_api import InputNameValue

from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.workflow.orchestration.setup.default_setup_orchestrator import DefaultSetupWorkflow

import cloudshell.api.cloudshell_api
from datetime import datetime
from ftplib import FTP

# Update this with the current reservation ID
reservation_id = "c6d79cc7-2ab9-4617-a615-3a27b66d02b6"

'''
dev_helpers.attach_to_cloudshell_as('admin', 'admin', 'Global',reservation_id,
                           server_address='localhost', cloudshell_api_port='8029')
'''
DEBUG = False

def restoreConfigs(Sandbox, components):
    # We are passing the resource_name into the function in the components parameter
    resource_name = components

    # Get the path to the FTP directory from the Configuration FTP Repo resource
    ftpServer = Sandbox.components.resources['Configuration FTP Repo']

    # Get the path to the saved directory
    myServ = Sandbox.components.services['SnapshotName']
    for item in myServ.Attributes :
        if item.Name == "SnapshotName.Snapshot_Name":
            saveName = item.Value

    # username from FTP Server resource
    response = Sandbox.automation_api.GetAttributeValue(resourceFullPath='Configuration FTP Repo',
                                      attributeName = 'Ftpserver.ftp_username')
    user = response.Value

    # password from FTP Server resource
    response = Sandbox.automation_api.GetAttributeValue(resourceFullPath='Configuration FTP Repo',
                                      attributeName = 'Ftpserver.ftp_password')
    passwd = response.Value

    ftp_path = Sandbox.automation_api.GetAttributeValue(resourceFullPath='Configuration FTP Repo',
                                                        attributeName='Ftpserver.ftp_dir').Value

    # ensure that the path starts with "/" - if not, add it
    if ftp_path[0] != "/":
        ftp_path = "/"+ftp_path

    ftp_full_path = 'ftp://'+user+':'+passwd+'@'+ftpServer.FullAddress

    full_path = ftp_full_path + ftp_path + '/'+saveName

    # Call the restore command to restore the configurations of the routers

    myList = []
    myList.append(cloudshell.api.cloudshell_api.InputNameValue(Name='path',Value=full_path))
    myList.append(cloudshell.api.cloudshell_api.InputNameValue(Name='configuration_type',Value='running'))
    myList.append(cloudshell.api.cloudshell_api.InputNameValue(Name='restore_method',Value='override'))
    myList.append(cloudshell.api.cloudshell_api.InputNameValue(Name='vrf_management_name',Value=''))

    try:
        response = Sandbox.automation_api.ExecuteCommand(reservationId=Sandbox.id,
                                          targetName=resource_name,
                                          targetType='Resource',
                                          commandName='restore_sandbox',
                                          commandInputs=myList)
        Sandbox.automation_api.WriteMessageToReservationOutput(reservationId=Sandbox.id,message='<div style="color: green; font-weight:bold">Successfully restored '+resource_name+'</div>')
        Sandbox.automation_api.SetResourceLiveStatus(resource_name, "Online" , "Active")

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        Sandbox.automation_api.WriteMessageToReservationOutput(reservationId=Sandbox.id,message='<div style="color: red; font-weight:bold">'+message+'</div>')
        pass


if __name__ == '__main__':
    sandbox = Sandbox()
    DefaultSetupWorkflow().register(sandbox)

    resources = sandbox.components.resources
    for resource_name, resource in sandbox.components.resources.iteritems():
        if "/" in resource_name:
            continue
        if "FTP" in resource_name:
            continue

        sandbox.workflow.add_to_configuration(function=restoreConfigs, components=resource_name)
    sandbox.execute_restore()
