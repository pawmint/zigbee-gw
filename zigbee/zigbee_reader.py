from xbee import XBee
import serial

from ubigate import logger
from zigbee.sensors import bedsensor_signal

PORT = '/dev/serial/by-id/usb-FTDI_XBIB-U-DEV-if00-port0'
BAUD_RATE = 9600
AT_OK = ['OK\r']
API_OK = ['ATAP 02\rOK\r']
NB_ITERATION = 20
NB_TRY = 10

# Open serial port
ser = serial.Serial(PORT, BAUD_RATE)
ser_init = serial.Serial(PORT, BAUD_RATE, timeout=0.1)

# Create API object
xbee = XBee(ser,escaped=True)
import pprint
pprint.pprint(xbee.api_responses)

def initialize_APImode():

    """
    Method to initialise the Xbee module in mode API/level2 => ability to get the emitter address and to choose the destinatory/ and to deal with the bad interpretation of binary data.
    """
    iteration = 0
    response = None

    ser_init.write("+++")

    while iteration < NB_ITERATION:
        iteration = iteration + 1
        response = ser_init.readlines(None)
        if response == AT_OK:
            ser_init.write("ATAP 02\r")
            response = ser_init.readlines(None)
            if response == API_OK:
                logger.info('The Xbee shield is passing into API mode, level 2')
                return True
            else:
                logger.debug('Bad signal received when passing into API mode %s' % response)
        else:
            logger.debug('Bad signal received when passing into AT command mode %s' % response)

    return False


def read_zigbee():
    try:
        response = xbee.wait_read_frame()
        logger.debug('Signal read %s' % response)
        return response
    except TypeError:
        return None

def gather_data(signal, timezone):

    data = None
    sensor = None

    sensor, data = bedsensor_signal.matches(signal, timezone)

    return sensor, data


def run(timezone):

    i = 0
    while i < NB_TRY:
        logger.debug('initialization of API, test %i' % (i+1))
        if initialize_APImode():
            break
        i = i + 1

    if i == NB_TRY:
        logger.error('The program fail to convert the Xbee module in API mode, try to restart')
        yield 'init', 'error'

    while True:
        signal = read_zigbee()
        signal_data = signal['rf_data']
        logger.debug('Data received: %s' % signal_data)
        try:
            sensor, data = gather_data(signal_data, timezone)
            logger.debug('data received: %s' % data)
            yield sensor, data
        except TypeError:
            pass




