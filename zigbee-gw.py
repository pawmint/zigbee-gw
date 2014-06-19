import logging

from zigbee import zigbee_reader

from ubigate import Ubigate
from ubigate import log, logger


def main():
    gate = Ubigate('resources/conf.ini')
    log.add_logger_file('data.log', logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    logger.info("Starting application")
    logger.info('Server: %s\n'
                'Port: %s\n'
                'House: %s\n'
                'Username: %s\n'
                'Timezone: %s' % (gate.config.server,
                                  gate.config.port,
                                  gate.config.house,
                                  gate.config.username,
                                  gate.timezone))

    for sensor, data in zigbee_reader.run(gate.timezone):
        if data is not None:
            topic = "/zigbee/sensor/%s" % sensor
            data['house'] = gate.config.house
            gate.push(topic, data)


if __name__ == "__main__":
    main()
