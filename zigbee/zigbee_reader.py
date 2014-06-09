import time
import serial

from ubigate import logger
from zigbee.sensors import pirled_signal

serialport = serial.Serial("/dev/serial/by-id/usb-FTDI_XBIB-U-DEV-if00-port0", 9600, timeout=0.1)

def read_zigbee():
    time.sleep(0.1)
    try:
        line = serialport.readlines(None)
        return line
    except TypeError:
        return None

def gather_data(signal, timezone):
    signal_types = [pirled_signal]

    data = None
    sensor = None

    for checker in signal_types:
        sensor, data = checker.matches(signal, timezone)
        if data is not None:
            break
    return sensor, data


def run(timezone):

#    serialport.write("+++")
#    logger.debug('+++ written')
    while True:
        line = read_zigbee()
        for signal in line:
            logger.debug('Signal received: %s' % signal)
            try:
                sensor, data = gather_data(signal, timezone)
                logger.debug('data received: %s' % data)
                yield sensor, data
            except TypeError:
                pass




