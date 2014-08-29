#!/usr/bin/env python

import logging

from zigbee import zigbee_reader

from ubigate import Ubigate
from ubigate import log, logger

coucou = "I am not a number !"

def on_message(client, userdata, message):
    print("server: " + str(message.payload) + "' on topic '"
        + message.topic + "' with QoS " + str(message.qos) + " Bulbi: " + coucou)

def main():
    gate = Ubigate('resources/conf.ini')
    log.add_logger_file('data.log', logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    logger.info("Starting application")
    logger.info('Server: %s\n'
                'Port: %s\n'
                'Password: %s\n'
                'House: %s\n'
                'Gateway: %s\n'
                'Timezone: %s' % (gate.config.server,
                                  gate.config.port,
                                  gate.config.password,
                                  gate.config.house,
                                  gate.config.gateway,
                                  gate.timezone))

    gate.subscribe("test/callback", on_message)
    #TO DO need to add a regular sync with the brocker to get the information of the callback methods

    # interruption of the program in case of error
    for meta_data, data in zigbee_reader.run(gate):
        if meta_data['type'] == 'error':
            break


if __name__ == "__main__":
    main()
