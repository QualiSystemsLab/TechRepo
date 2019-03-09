import requests
import json
import time


class SandboxLibrary(object):

    def __init__(self, cloudshell_url, user, password, domain):
        self.api = cloudshell_url + '/api'
        self.api_v2 = self.api + '/v2'
        self.auth_token = self._login(self.api, user, password, domain)


    def _get_headers(self, auth_token):
        return {'Authorization': auth_token, "Content-Type": "application/json", 'Accept': 'application/json'}

    def _login(self, api, user, password, domain):
        response = requests.put(api + '/login', json={"username": user, "password": password, "domain": domain})

        return "Basic " + response.content[1:-1]

    def _get_component_url(self, api, headers, sandbox_id, resource_name):
        sandbox_components = requests.get(api + '/sandboxes/{sandbox_id}/components'
                                          .format(sandbox_id=sandbox_id), headers=headers)

        components = json.loads(sandbox_components.content)
        component_url = ''

        for component in components:
            if component['name'] == resource_name:
                component_url = component['_links']['self']['href']

        return component_url

    def _start_execution(self, api, headers, component_url, command_name):
        url = api + str(component_url) + '/commands/{command_name}/start'.format(command_name=command_name)
        execution_result = requests.post(url, headers=headers, json={"printOutput": True})
        result_json = json.loads(execution_result.content)
        return str(result_json['_links']['self']['href'])

    def _get_execution_result(self, api, headers, execution_url):
        execution_info = json.loads(requests.get(api + execution_url, headers=headers).content)

        while execution_info['status'] == 'Running':
            time.sleep(2)
            execution_info = json.loads(requests.get(api + execution_url, headers=headers).content)

        return execution_info

    def execute_command(self, sandbox_id, resource_name, command_name):
        headers = self._get_headers(self.auth_token)
        component_url = self._get_component_url(self.api_v2, headers, sandbox_id, resource_name)
        execution_url = self._start_execution(self.api_v2, headers, component_url, command_name)
        return self._get_execution_result(self.api_v2, headers, execution_url)