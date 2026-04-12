#
# This file contains the classes and architecture components for the setup mentioned in
# the paper (see README.md)
#

#
# NOTE: this version currently is hardcoded for one switch of id 'of:0000000000000001'
#

from util import of_type_map
import json
import requests
from pprint import pprint
import loxi.of13 as ofp 
import loxi.of13.util as ofputil

class Observer:
    def __init__(self, message_filter):
        '''
        message_filter: a list of the message OF message type (id number) that we want to observe, others are ignored 
        '''
        self.message_filter = message_filter
        self.observed_log = {'of:0000000000000001': []}


    def add_message(self, message, filter_enabled=True):
        '''
        message: one of the loxigen message subclasses (e.g flow_mod)
        filter_enabled: debugging param
        '''
        if not filter_enabled or message.type in self.message_filter:
            norm_msg = self.normalize_message(message)
            if norm_msg is not None:
                self.observed_log['of:0000000000000001'].append(norm_msg)
        
        #print(self.observed_log)


    def normalize_message(self, message):
        '''
        extracing the flow rule selection and instructions is much more
        annoying using the messages because it's buried in loxigen objects
        
        this normalizes the values from the objects into having the same 
        names as the ONOS rest API flows JSON structure
        '''
        selector = []
        for oxm in message.match.oxm_list:
            if isinstance(oxm, ofp.oxm.in_port):
                selector.append({"type": "IN_PORT", "port": oxm.value})
            elif isinstance(oxm, ofp.oxm.eth_dst):
                selector.append({"type": "ETH_DST", "mac": ofputil.pretty_mac(oxm.value)})
            elif isinstance(oxm, ofp.oxm.eth_src):
                selector.append({"type": "ETH_SRC", "mac": ofputil.pretty_mac(oxm.value)})

        treatment = []
        for inst in message.instructions:
            if isinstance(inst, (ofp.instruction.apply_actions, ofp.instruction.write_actions)):
                for act in inst.actions:
                    if isinstance(act, ofp.action.output):
                        treatment.append({"type": "OUTPUT", "port": act.port})

                        # NOTE: this is apparently some special kind of port that refers back to ONOS controller for the switches
                        # we skip if for the same reason we skip org.onosproject.core
                        if act.port == 4294967293:
                            return None

        return {
            'selector': selector,
            'treatment': treatment
        }


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


    def get_log(self):
        return self.observed_log


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

        self.network_view_state = {}

    def fetch_network_state(self):
        resp = requests.get(self.controller_url, auth=(self.username, self.password))

        if resp.status_code == 200:
            flows = resp.json()['flows']


            #print('Flows in controller state:')
            for flow in flows:
                deviceId = flow['deviceId']
                appId = flow['appId']
                selector = flow["selector"]["criteria"]
                treatment = flow["treatment"]["instructions"]

                if deviceId not in self.network_view_state.keys():
                    self.network_view_state[deviceId] = []
                
                # for now I'm skipping all of the org.onosproject.core stuff, it seems like they are not the flow
                # rules we're interesting in using here
                if appId != 'org.onosproject.core':
                    self.network_view_state[deviceId].append({
                        'selector': selector,
                        'treatment': treatment
                    })

                # debug prints
                #print(flow)
                # print(f'[{flow["state"]}] on device \"{flow["deviceId"]}\" installed by app \"{flow["appId"]}\'')
                # print(f'\tSelector Criteria: {flow["selector"]["criteria"]}')
                # print(f'\tTreatment Instruction: {flow["treatment"]["instructions"]}')
                # print()
            
            #pprint(self.network_view_state)

        else:
            raise Exception(f"Failed to get status from SDN Controller REST API: \nat {self.controller_url}")


    def get_network_state(self):
        return self.network_view_state


class Comparator:
    '''
    The comparator object from the paper. Unfortunately they don't go into detail for the comparator algorithm,
    I assume because their paper is more about the architecture. So this is something we can experiment with
    '''
    def __init__(self):
        pass
    
    def compare(self, controller_stub, observer):
        '''
        From the paper, it seems this is meant to be called every time there is a network programming
        attempt (so some kind of flow mod)

        returns:
        - True if the states match
        - False if they don't
        '''
        # get newest state from ONOS 
        controller_stub.fetch_network_state() 
        controller_state = controller_stub.get_network_state()

        # get most recent observer state observed
        flow_mod = observer.get_log()['of:0000000000000001'][-1]

        print('Controller State')
        print(controller_state)
        print('Most recent flow mod')
        print(flow_mod)

        return True