from xbee import XBee
import serial
import time
import importlib
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from ubigate import logger

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

def initialize_APImode():

    """
    Method to initialise the Xbee module in mode API/level2 => ability to get the emitter address and to choose the destinatory/ and to deal with the bad interpretation of binary data.
    """
    iteration = 0
    response = None

    ser_init.write("+++")
    time.sleep(2)

    while iteration < NB_ITERATION:
        iteration = iteration + 1
        response = ser_init.readlines(None)
        logger.info("response 1: %s" %response)
        if response == AT_OK:
            ser_init.write("ATAP 02\r")
            response = ser_init.readlines(None)
            logger.info("response 2: %s" %response)
            if response == AT_OK:
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
        return response
    except TypeError:
        return None

def gather_data(signal, sensors_list):

    data = None
    meta_data = None

#    meta_data, data = bed_signal.matches(signal)
    for sensor in sensors_list:
        meta_data, data = sensor.matches(signal)
        if data is not None:
            break

    return meta_data, data

def import_sensors(gate):
    """
    Method to manage:
    The modules importation of the sensors described in the file 'ressource/conf.ini'.
    The instantiation of the corresponded classes.
    It return a list of the sensors classes instanciated.
    """

    config_sensor = configparser.SafeConfigParser()
    config_sensor.read('resources/conf.ini')
    sensors_info = dict(config_sensor.items("Sensors"))
    sensors_path = list(sensors_info.keys())
    logger.debug("the list of the paths of the sensors: %s" %sensors_path)
    sensors_name = list(sensors_info.values())
    logger.debug("the list of the sensors: %s" %sensors_name)

    sensors_classes = []
    for path, sensor in zip(sensors_path,sensors_name):
        #Import the modules
        module = importlib.import_module(path)
        #Create class objects
        sensor_object = getattr(module, sensor)
        #Instanciate the class objects
        sensors_classes.append(sensor_object(gate))

    return sensors_classes

def run(gate):

    sensors_list = import_sensors(gate)

    i = 0
    while i < NB_TRY:
        logger.debug('initialization of API, test %i' % (i+1))
        if initialize_APImode():
            break
        i = i + 1

    if i == NB_TRY:
        logger.error('The program fail to convert the Xbee module in API mode, try to restart')
        meta_data = {'type': 'error'}
        yield meta_data, None

    while True:
        signal = read_zigbee()
        logger.info('Data received: %s' % signal)
        try:
            meta_data, data = gather_data(signal, sensors_list)
            logger.debug('data received: %s' % data)
#            if data to send with Xbee:
#                send data through Xbee
            #If there is an error and zigbee-gw has to be shut down
            if meta_data['type'] == 'error':
                yield meta_data, None

        except TypeError:
            pass




