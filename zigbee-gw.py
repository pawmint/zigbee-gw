#!/usr/bin/env python

import logging

from zigbee import zigbee_IO

from ubigate import Ubigate
from ubigate import log, logger


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


    # interruption of the program in case of error
    for meta_data, data in zigbee_IO.run(gate):
        if meta_data['type'] == 'error':
            break


if __name__ == "__main__":
    main()
