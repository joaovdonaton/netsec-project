#
# This file contains the classes and architecture components for the setup mentioned in
# the paper (see README.md)
#

from util import of_type_map
import json

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

        # # temporary thing
        # if sum(msg_type_counts.values()) > 200:
        #     with open('data/2-hosts-200-messages-distribution', 'w') as json_file:
        #         json.dump(msg_type_counts, json_file, indent=4)
            
        #     self.observed_log = []