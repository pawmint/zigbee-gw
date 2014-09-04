from datetime import datetime
import pytz
import re
import configparser

from zigbee.sensors import procedure
from zigbee.sensors import callback
from ubigate import logger

SIZEOF_DR1 = 48
FRAGMENT_NUMBER = 3

DEFAULT_ID = None
DEFAULT_OCCUPENCY = 'off'
DEFAULT_FSR = 1
DEFAULT_FSC = 0
DEFAULT_ORDER = None
DEFAULT_THRESHOLD = 500

class Smartbeds(object):
    def __init__(self, gate):
        self.gate = gate
        self.mac_id = DEFAULT_ID
        self.memory = {}
        self.threshold = DEFAULT_THRESHOLD
        self._init_smartbeds()

    def bed_submethod(bedClient, client, userdata, message):
        bedClient.memory = callback.method(userdata, message, bedClient.memory)

    def _init_smartbeds(self):
        """
        Get the configuration of the bed and subscribe to the topic with the method present in the callback.py
        """
        try:
            configbed = configparser.ConfigParser()
            configbed.read('zigbee/sensors/bedconf.txt')
            self.threshold = int(configbed['BEDSENSOR']['THRESHOLD'])
        except:
            logger.warning('Impossible to get the configuration of the bed')

        subscribing_topic = "house/%s/zigbee/sensor/bedsensor/orders" % (self.gate.config.house)
        self.gate.callback_subscribe(str(subscribing_topic), self.bed_submethod)
        logger.info("Sending of the submethod on the topic %s" %str(subscribing_topic))

    def get_date(self):
        """
        This method return the date of the computer regarding of the gate.timezone.
        """
        tz = pytz.timezone(str(self.gate.timezone))
        date = tz.localize(datetime(datetime.now().year,
                           datetime.now().month,
                           datetime.now().day,
                           datetime.now().hour,
                           datetime.now().minute,
                           datetime.now().second,
                           datetime.now().microsecond))
        return date

    def get_ID(self, signal_addr):
        """
        This method formalize and return the mac ID of the bedsensor.
        """

        bed_addr = 0
        for octet in signal_addr:
            bed_addr = (bed_addr*256)+ord(octet)

        bed_ID = 'BED-'+str(bed_addr)
        logger.debug('Address of the Bedproto: %s' % bed_ID)

        return bed_ID

    def new_order(self, bed_ID):
        state = False

        if self.memory[bed_ID].get('order') is not None:
            logger.debug("There is an order: %s" % self.memory[bed_ID].get('order'))
            state = True

        return state


    def get_order(self, bed_ID):
        orderCode = procedure.orderTRAM(self.memory[bed_ID].get('order'))
        return orderCode

    def matches(self, signal):
        """
        The method to check if the signal received is corresponding with the bedsensor patern. If the signal is corresponding, we extract the information corresponding
        """
        #Data FSR 1spl   $ DR1 , ID , R0 R1 R2 R3 R4 R5 R6 R7 \n
        #example: $DR1,\x00\x13\xa2\x00@\xa1N\xba,\x00\x00\x06\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n

        #The other simple possible is $YOP,nb_FSR,nbFSC\n
        #example: $YOP,08,02\n

        #$DR1,\x00\x10\x02\r,\n\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\n

        signal_data = signal['rf_data']
        signal_addr = signal['source_addr']

        logger.debug('Checking the signal "%s" in bedsensor program' % signal_data)


        response_type = None
        response_code = None

        #TO DO put this in procedure
        pattern = (r'^\$(?P<data_type>YOP|DR1).*$\n')
        regexp = re.compile(pattern)
        match = regexp.match(signal_data)

        if match:

            date = self.get_date()
            bed_ID = self.get_ID(signal_addr)
            sample_bits = signal_data.split(",") #Create a list with the parts of the signal

            if match.group('data_type') == 'YOP':

                #Initialization signal
                response_type, response_code, self.memory = procedure.YOPtram(sample_bits, bed_ID, self.memory, date)

            if match.group('data_type') == 'DR1':

                #FSR data signal
                response_type, response_code, self.memory = procedure.DR1tram(sample_bits, bed_ID, self.memory, date, self.threshold, self.gate)

            if self.new_order(bed_ID):
                response_code = self.get_order(bed_ID)
                self.memory[bed_ID]['order'] = None

        else:
            logger.debug('The signal is not matching with the bedsensor patern')

        return response_type, response_code
