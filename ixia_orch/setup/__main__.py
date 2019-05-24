#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cloudshell.helpers.scripts.cloudshell_dev_helpers as dev_helpers
from cloudshell.api.cloudshell_api import InputNameValue
from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.workflow.orchestration.setup.default_setup_orchestrator import DefaultSetupWorkflow
from cloudshell.workflow.orchestration.setup.default_setup_logic import DefaultSetupLogic

TARGET_TYPE_RESOURCE = 'Resource'
REMAP_CHILD_RESOURCES = 'connect_child_resources'

IXVM_CHASSIS_MODEL = "IxVM Virtual Traffic Chassis 2G"
VYOS_MODEL = "Vyos"
RE_AUTOLOAD_MODELS = [IXVM_CHASSIS_MODEL, VYOS_MODEL]
RE_CONNECT_CHILD_RESOURCES_MODELS = [IXVM_CHASSIS_MODEL]


# Update this with the current reservation ID
reservation_id = "5a05a58f-2e60-430d-98df-68685df173fd"
'''
dev_helpers.attach_to_cloudshell_as('admin', 'admin', 'Global',reservation_id,server_address='localhost', cloudshell_api_port='8029')
'''

DEBUG = False

def execute_autoload_on_ixvm(sandbox, components):
    """ Execute autoload on deployed Virtual IxVM Chassis """

    deployed_apps_names = [app.deployed_app.Name for app in components.values()]

    resource_details_cache = {app_name: sandbox.automation_api.GetResourceDetails(app_name) for app_name in
                              deployed_apps_names}

    # execute autoload on the deployed apps after they've got IPs
    for app_name in deployed_apps_names:
        app_resource_details = resource_details_cache[app_name]

        if app_resource_details.ResourceModelName not in RE_AUTOLOAD_MODELS:
            continue

        sandbox.automation_api.WriteMessageToReservationOutput(reservationId=sandbox.id,
                                                               message='Autoload resource {}'.format(app_name))

        sandbox.automation_api.AutoLoad(app_name)

    # execute remap connections on the deployed apps after correct autoload(s)
    # for app_name in deployed_apps_names:
    #     app_resource_details = resource_details_cache[app_name]
    #
    #     if app_resource_details.ResourceModelName not in RE_CONNECT_CHILD_RESOURCES_MODELS:
    #         continue
    #
    #     sandbox.automation_api.WriteMessageToReservationOutput(reservationId=sandbox.id,
    #                                                            message='Connect Child resource on {}'.format(app_name))
    #
    #     sandbox.logger.info("Triggering Connect Child resources command on {}".format(app_name))
    #     sandbox.automation_api.ExecuteCommand(sandbox.id,
    #                                           app_name,
    #                                           TARGET_TYPE_RESOURCE,
    #                                           REMAP_CHILD_RESOURCES, [])

    DefaultSetupLogic.remap_connections(api=Sandbox.automation_api, reservation_id=sandbox.id,
                                        apps_names=deployed_apps_names, logger=sandbox.logger)
    sandbox.logger.info("Triggering 'connect_all_routes_in_reservation' method from the DefaultSetupLogic")
    sandbox.automation_api.WriteMessageToReservationOutput(reservationId=sandbox.id,
                                                           message='Connecting routes in the reservation')

    reservation_details = sandbox.automation_api.GetReservationDetails(sandbox.id)

    DefaultSetupLogic.connect_all_routes_in_reservation(api=sandbox.automation_api,
                                                        reservation_details=reservation_details,
                                                        reservation_id=sandbox.id,
                                                        resource_details_cache=resource_details_cache,
                                                        logger=sandbox.logger)



def loadConfig(Sandbox, components):
    # We are passing the resource_name into the function in the components parameter
    resource_name = components

    resources = Sandbox.components.resources

    # Get the path to the FTP directory from the Configuration FTP Repo resource
    ftpServer = Sandbox.components.resources['Configuration FTP Repo']
    response = Sandbox.automation_api.GetAttributeValue(resourceFullPath='Configuration FTP Repo',
                                      attributeName = 'Ftpserver.ftp_dir')
    ftp_path = response.Value
    # ensure that the path starts with "/" - if not, add it
    if ftp_path[0] != "/":
        ftp_path = "/"+ftp_path


    # username from FTP Server resource
    response = Sandbox.automation_api.GetAttributeValue(resourceFullPath='Configuration FTP Repo',
                                      attributeName = 'Ftpserver.ftp_username')
    user = response.Value

    # password from FTP Server resource
    response = Sandbox.automation_api.GetAttributeValue(resourceFullPath='Configuration FTP Repo',
                                      attributeName = 'Ftpserver.ftp_password')
    passwd = response.Value

    ftp_full_path = 'ftp://'+user+':'+passwd+'@'+ftpServer.FullAddress

    full_path = ftp_full_path+ftp_path

    if "cisco" in resource_name.lower():
        # Use either a pre-defined file or a custom configured file if not BGP, OSPF or CLEAN
        if Sandbox.global_inputs['Router Configuration File Set'] == "BGP":
            routerConfig = full_path+'/cisco_bgp.cfg'
        elif Sandbox.global_inputs['Router Configuration File Set'] == "OSPF":
            routerConfig = full_path+'/cisco_ospf.cfg'
        elif Sandbox.global_inputs['Router Configuration File Set'] == "CLEAN":
            routerConfig = full_path+'/cisco_clean.cfg'
       # else:
        #    routerConfig = full_path+'/'+Sandbox.global_inputs['Cisco Router Configuration File']

    if "juniper" in resource_name.lower():
        # Use either a pre-defined file or a custom configured file if not BGP, OSPF or CLEAN
        if Sandbox.global_inputs['Router Configuration File Set'] == "BGP":
            routerConfig = full_path+'/juniper_bgp.cfg'
        elif Sandbox.global_inputs['Router Configuration File Set'] == "OSPF":
            routerConfig = full_path+'/juniper_ospf.cfg'
        elif Sandbox.global_inputs['Router Configuration File Set'] == "CLEAN":
            routerConfig = full_path+'/juniper_clean.cfg'
        #else:
         #   routerConfig = full_path+'/'+Sandbox.global_inputs['Juniper Router Configuration File']

    myList = []
    myList.append(InputNameValue(Name='path',Value=routerConfig))
    myList.append(InputNameValue(Name='configuration_type',Value='running'))
    myList.append(InputNameValue(Name='restore_method',Value='override'))

    response = Sandbox.automation_api.ExecuteCommand(reservationId=Sandbox.id,
                                              targetName=resource_name,
                                              targetType='Resource',
                                              commandName='restore',
                                              commandInputs=myList)

    Sandbox.automation_api.WriteMessageToReservationOutput(reservationId=Sandbox.id,message='<div style="color: green; font-weight:bold">'+resource_name+' configuration completed</div>')
    Sandbox.automation_api.SetResourceLiveStatus(resource_name, "Online" , "Active")


def connect_l1(sandbox, component):
    for route in sandbox.automation_api.GetReservationDetails(sandbox.id).ReservationDescription.RequestedRoutesInfo:
        sandbox.automation_api.ConnectRoutesInReservation(sandbox.id, [route.Source,route.Target],'bi')

def showGlobalInputs (Sandbox, components):
    # Blueprint Type
    message = "Router Configuration File Set: "+Sandbox.global_inputs['Router Configuration File Set']
    Sandbox.automation_api.WriteMessageToReservationOutput(reservationId=Sandbox.id,message=message)
    
    # Cisco Router Config
   # message = "Cisco Router Configuration File: "+Sandbox.global_inputs['Cisco Router Configuration File']
    #Sandbox.automation_api.WriteMessageToReservationOutput(reservationId=Sandbox.id,message=message)

    # Juniper Router Config
    #message = "Juniper Router Configuration File: "+Sandbox.global_inputs['Juniper Router Configuration File']
    #Sandbox.automation_api.WriteMessageToReservationOutput(reservationId=Sandbox.id,message=message)



if __name__ == '__main__':

    Sandbox = Sandbox()
    DefaultSetupWorkflow().register(Sandbox)  #, enable_configuration=False

    # For each configurable resource, load its config
    if (Sandbox.global_inputs['Router Configuration File Set']).lower() not in ('none'):
        for resource_name, resource in Sandbox.components.resources.iteritems():
            if "/" in resource_name:
                continue
            if "FTP" in resource_name:
                continue
    
            # If not a Cisco or Juniper device, don't load config
            if "cisco" in resource_name.lower() or "juniper" in resource_name.lower():    
                Sandbox.workflow.add_to_configuration(function=loadConfig, components=resource_name)

    Sandbox.workflow.on_provisioning_ended(function=showGlobalInputs, components=Sandbox.components.resources)
    Sandbox.workflow.add_to_connectivity(function=connect_l1,components=None)
    #Sandbox.workflow.on_configuration_ended(function=execute_autoload_on_ixvm, components=Sandbox.components.apps)
    Sandbox.execute_setup()

