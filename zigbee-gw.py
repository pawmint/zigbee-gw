#!/usr/bin/env python

import logging

from zigbee import zigbee_reader

from ubigate import Ubigate
from ubigate import log, logger


def main():
    gate = Ubigate('resources/conf.json')
    log.add_logger_file('data.log', logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    logger.info("Starting application")
    logger.info('Server: %s\n'
                'Port: %s\n'
                'Password: %s\n'
                'Gateway: %s\n'
                'Timezone: %s' % (gate.config['server'],
                                  gate.config['port'],
                                  gate.config['password'],
                                  gate.config['gateway'],
                                  gate.timezone))

    for data in zigbee_reader.run(gate.timezone):
        if data['type'] != 'error':
            try:
                data['house'] = gate.find_house(data['sensor'])
            except KeyError:
                logger.warning("Unknown sensor: %s" % data['sensor'])
            else:
                topic = "/zigbee/sensor/%s" % data['sensor']
                # topic = "/marmitek/sensor/%s/%s" % (data['sensor'],
                #                                     data['type'])
                gate.push(data['house'], topic, data)


if __name__ == "__main__":
    main()
