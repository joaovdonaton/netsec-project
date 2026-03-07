#
# This file contains the classes and architecture components for the setup mentioned in
# the paper (see README.md)
#

from util import of_type_map
import json
import requests

class Observer:
    def __init__(self, message_filter):
        '''
        message_filter: a list of the message OF message type (id number) that we want to observe, others are ignored 
        '''
        self.message_filter = message_filter

        self.observed_log = []

    def add_message(self, message, filter_enabled=True):
        '''
        message: one of the loxigen message subclasses (e.g flow_mod)
        filter_enabled: debugging param
        '''
        if filter_enabled:
            if message.type in self.message_filter:
                self.observed_log.append(message)
        else:
            self.observed_log.append(message)

    def display_stats(self):
        print('Observer Statistics:')

        msg_type_counts = {}
        for msg in self.observed_log:
            type_name = of_type_map[msg.type]
            if type_name not in msg_type_counts:
                msg_type_counts[type_name] = 1
            else:
                msg_type_counts[type_name] += 1
        
        print(f'\t{msg_type_counts}')


class SDNControllerView:
    '''
    This is my version of what the paper refers to as "SDN Controller Stub".
    It is essentially what communicates "northbound" (in this case to the REST API) that the
    SDN Controlle provides. I'm currently only trying ONOS, so this is designed around
    how that works
    '''

    def __init__(self, controller_url, username, password):
        ''''''
        self.controller_url = controller_url
        self.username = username
        self.password = password

    def fetch_network_state(self):
        resp = requests.get(self.controller_url, auth=(self.username, self.password))

        if resp.status_code == 200:
            flows = resp.json()['flows']

            print('Flows in controller state:')
            for flow in flows:
                print(f'[{flow["state"]}] on device \"{flow["deviceId"]}\" installed by app \"{flow["appId"]}\'')
                print(f'\tSelector Criteria: {flow["selector"]["criteria"]}')
                print(f'\tTreatment Instruction: {flow["treatment"]["instructions"]}')

                print()

        else:
            raise Exception(f"Failed to get status from SDN Controller REST API: \nat {self.controller_url}")