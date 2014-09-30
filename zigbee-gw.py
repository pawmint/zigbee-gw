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
    logger.info('Timezone: %s' % gate.timezone)
    for gateway in gate.config['gateways']:
        logger.info('Server: %s\n'
                    'Port: %s\n'
                    'Password: %s\n'
                    'Gateway: %s\n' % (gateway['server'],
                                       gateway['port'],
                                       gateway['password'],
                                       gateway['name']))

    for data in zigbee_reader.run(gate.timezone):
        if data['type'] != 'error':
            try:
                data['house'] = gate.find_house(data['sensor'])
            except KeyError:
                logger.warning("Unknown sensor: %s" % data['sensor'])
            else:
                topic = "/zigbee/sensor/%s/%s" % (data['sensor'],data['type'])
                # topic = "/marmitek/sensor/%s/%s" % (data['sensor'],
                #                                     data['type'])
                gate.push(data['house'], topic, data)


if __name__ == "__main__":
    main()
