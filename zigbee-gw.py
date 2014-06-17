import logging

from zigbee import zigbee_reader
#from zigbee import zigbeeReader

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
            gate.push(topic, data)

#    zigbeeReader.run()

if __name__ == "__main__":
    main()
