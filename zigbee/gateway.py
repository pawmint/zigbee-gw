#!/usr/bin/env python

import logging

from zigbee import zigbee_IO

from ubigate import Ubigate
from ubigate import log, logger


def main():
    gate = Ubigate('zigbee-gw',
                   default_file='resources/conf.json.default')
    log.add_logger_file('data.log', logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    logger.info("Starting application")
    logger.info('Timezone: %s' % gate.timezone)
    for gateway in gate.config['gateways']:
        logger.info('Server: %s\n'
                    'Port: %s\n'
                    'Gateway: %s\n' % (gateway['server'],
                                       gateway['port'],
                                       gateway['name']))

    for data in zigbee_IO.run(gate.timezone):
        if data['type'] != 'error':
            try:
                data['house'] = gate.find_house(data['sensor'])
            except KeyError:
                logger.warning("Unknown sensor: %s" % data['sensor'])
            else:
                topic = "/zigbee/sensor/%s/%s" % (data['sensor'], data['type'])
                # topic = "/marmitek/sensor/%s/%s" % (data['sensor'],
                #                                     data['type'])
                gate.push(data['house'], topic, data)


if __name__ == "__main__":
    main()
