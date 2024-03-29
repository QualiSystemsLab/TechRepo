from robot.api import logger
import urllib

import requests
import json
import time


class SandboxLibrary(object):

    def __init__(self, cloudshell_url, user, password, domain):
        self.api = cloudshell_url + '/api'
        self.api_v2 = self.api + '/v2'
        self.auth_token = self._login(self.api, user, password, domain)

    @staticmethod
    def _get_headers(auth_token):
        return {'Authorization': auth_token, "Content-Type": "application/json", 'Accept': 'application/json'}

    @staticmethod
    def _login(api, user, password, domain):
        response = requests.put(api + '/login', json={"username": user, "password": password, "domain": domain})

        return "Basic " + response.text[1:-1]

    @staticmethod
    def _get_component_url(api, headers, sandbox_id, resource_name):
        if resource_name == 'NIL':
            return '/sandboxes/{sandbox_id}'.format(sandbox_id=sandbox_id)
        sandbox_components = requests.get(api + '/sandboxes/{sandbox_id}/components'
                                          .format(sandbox_id=sandbox_id), headers=headers)

        components = json.loads(sandbox_components.content)
        component_url = ''

        for component in components:
            if component['name'] == resource_name:
                component_url = component['_links']['self']['href']

        return component_url

    @staticmethod
    def _start_execution(api, headers, component_url, command_name, params):
        request_json = {"printOutput": True}
        if params:
            request_json['params'] = []
            for param in params:
                request_json['params'].append({"name": param, "value": params[param]})
        command_name = urllib.parse.quote( command_name)
        url = api + str(component_url) + '/commands/{command_name}/start'.format(command_name=command_name)
        logger.console(url)
        execution_result = requests.post(url, headers=headers, json=request_json)
        result_json = json.loads(execution_result.content)

        if execution_result.status_code == 500:
            logger.error(result_json)
            logger.console(result_json)
        else:
            logger.console(result_json)
            return str(result_json['_links']['self']
                       ['href'])

    @staticmethod
    def _get_execution_result(api, headers, execution_url):
        response = requests.get(api + execution_url, headers=headers)
        execution_info = json.loads(response.content)
        if 'status' not in execution_info:
            print('received: ' + response.text)
            raise Exception(response.text)
        while execution_info['status'] == 'Running' or execution_info['status'] == 'Pending':
            time.sleep(2)
            execution_info = json.loads(requests.get(api + execution_url, headers=headers).content)
        return execution_info

    def execute_command(self, sandbox_id, resource_name, command_name, params):

        logger.console(resource_name)
        headers = self._get_headers(self.auth_token)
        component_url = self._get_component_url(self.api_v2, headers, sandbox_id, resource_name)
        execution_url = self._start_execution(self.api_v2, headers, component_url, command_name, params)
        return self._get_execution_result(self.api_v2, headers, execution_url)['output']
