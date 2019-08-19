from cloudshell.api.cloudshell_api import InputNameValue
from cloudshell.helpers.scripts import cloudshell_scripts_helpers as helper

reservation_id =helper.get_reservation_context_details().id
reservation_details = helper.get_api_session().GetReservationDetails(reservation_id).ReservationDescription
for service in reservation_details.Services:
    print service.ServiceName
    if service.ServiceName=='Ixia IxNetwork Contro  ller Shell 2G':
        helper.get_api_session().ExecuteCommand(helper.get_reservation_context_details().id,
                                                service.Alias,'Service', 'run_quicktest',
                                                [InputNameValue('test_name', 'rfc2544_frameloss'),
                                                 InputNameValue('config_file_name', 'rfc_2544_frameloss.ixncfg')]

                                        )