import json
import os
import sys
from contextlib import contextmanager

from helpers.rest_api_helper import QualiAPISession
from loadQuickTest import loadQuickTest
from cloudshell.helpers.scripts import cloudshell_scripts_helpers as helper


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def attach_report_to_reservation(reservation_id, filename, api):
    for attachment in api.GetReservationAttachmentsDetails(reservation_id):
        api.DeleteFileFromReservation(reservation_id, attachment)
    api.AttachFileToReservation(reservation_id, filename, filename, True)


if __name__ == '__main__':

    reservation_id = helper.get_reservation_context_details().id
    session = helper.get_api_session()
    IxVM_address = ''
    reservation_details = session.GetReservationDetails(reservation_id)

    for resource in reservation_details.ReservationDescription.Resources:
        resource_name = resource.Name
        if "/" in resource_name:
            continue

        if "IxVM" in resource_name:
            IxVM = resource_name
            IxVM_address = resource.FullAddress

    for resource in reservation_details.ReservationDescription.Apps:
        resource_name = resource.Name
        if "/" in resource_name:
            continue

        if "IxVM" in resource_name:
            IxVM = resource_name
            IxVM_address = resource.FullAddress

    if IxVM_address:
        connectivity = helper.get_connectivity_context_details()
        api = QualiAPISession(connectivity.server_address, connectivity.admin_user, connectivity.admin_pass,
                              domain=helper.get_reservation_context_details().domain)
        test_name = helper.get_user_param('test_name')
        config_name = helper.get_user_param('config_file_name')

        attachreport = lambda filename: attach_report_to_reservation(reservation_id,filename,api)
        output_logger = lambda message: session.WriteMessageToReservationOutput(reservation_id, message)

        with suppress_stdout():
            result = loadQuickTest(IxVM=IxVM_address, quickTestName='rfc2544_frameloss',
                          configFileName='rfc_2544_frameloss.ixncfg',
                          output_writer=output_logger,
                          report_attacher=attachreport)
        print result
