from xbee import XBee
import serial
import time
# import sys
import itertools

from ubigate import logger

from zigbee.sensors import bedsensor_signal


BAUD_RATE = 9600
AT_OK = ['OK\r']
API_OK = ['ATAP 02\rOK\r']
NB_ITERATION = 20
NB_TRY = 10


def init(ser_init):
    for i in itertools.count():
        logger.debug('initialization of API, test %d' % (i + 1))
        if initialize_APImode(ser_init):
            return True

    # logger.error('Failed to turn the Xbee module in API mode, '
    #              'please restart the program')
    # sys.exit(1)


def initialize_APImode(ser_init):
    """
    Initialize the Xbee module in mode API/level2
    API mode gives the ability to get the emitter address, to choose
    the recipient, and to deal with the bad interpretation of binary data.
    """
    response = None

    ser_init.write("+++")
    time.sleep(2)

    for iteration in range(NB_ITERATION):
        response = ser_init.readlines(None)
        logger.debug("response 1: %s" % response)
        if response == AT_OK:
            ser_init.write("ATAP 02\r")
            response = ser_init.readlines(None)
            logger.debug("response 2: %s" % response)
            if response == AT_OK:
                logger.info('The Xbee shield is passing into API mode, '
                            'level 2')
                return True
            else:
                logger.debug('Bad signal received when passing into API '
                             'mode %s' % response)
        else:
            logger.debug('Bad signal received when passing into AT command '
                         'mode %s' % response)

    return False


def read_zigbee(gate):
    # Open serial port
    ser = serial.Serial(gate.config['device'], BAUD_RATE)
    ser_init = serial.Serial(gate.config['device'], BAUD_RATE, timeout=0.1)
    # Create API object
    xbee = XBee(ser, escaped=True)

    init(ser_init)

    while True:
        try:
            response = xbee.wait_read_frame()
            yield response
        except TypeError:
            pass


def run(gate):
    for signal in read_zigbee(gate):
        logger.debug('Message received: %s' % signal)
        try:
            data = bedsensor_signal.matches(signal, gate.timezone)
            if data is not None:
                logger.debug('Data received: %s' % data)
                yield data
        except TypeError:
            pass
