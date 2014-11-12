#!/usr/bin/env python

from zigbee import zigbee_IO

from ubigate import Ubigate
from ubigate import logger


def main():
    gate = Ubigate('zigbee-gw',
                   default_file='resources/conf.json.default')

    logger.info("Starting application")
    logger.debug('Timezone: %s' % gate.timezone)

    for data in zigbee_IO.run(gate):
        if data['type'] != 'error':
            try:
                data['house'] = gate.find_house(data['sensor'])
            except KeyError:
                logger.warning("Unknown sensor: %s" % data['sensor'])
            else:
                topic = "/zigbee/sensor/%s/%s" % (data['sensor'], data['type'])
                gate.push(data['house'], topic, data)


if __name__ == "__main__":
    main()
