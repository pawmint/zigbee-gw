from datetime import datetime
import pytz
import re
import sys

from zigbee.sensors import bed_reasoning
from ubigate import logger

SIZEOF_DR1 = 48
FRAGMENT_NUMBER = 3

DEFAULT_ID = None
DEFAULT_OCCUPENCY = 'off'

class Bedsensor(object):
    def __init__(self, timezone):
        self.timezone = timezone
        self.mac_id = DEFAULT_ID
        self.memory = {}


    def integrity(self, signal):
        if sys.getsizeof(signal) == SIZEOF_DR1:
            logger.debug('The size of the data received is corresponding')
            return True
        logger.error('The size of the data received is not corresponding')
        return False

    def new_sensor(self, bed_ID):

        new = None
        id_list = list(self.memory.keys())
        logger.debug('list of the bed sensor registered: %s' %id_list)

        if id_list.count(bed_ID) == 0:
            # This is a new bedsensor
            logger.debug('This is a new bedsensor: %s' %bed_ID)
            new = True
        else:
            #The bedsensor was already registered
            logger.debug('This is a registered bedsensor: %s' %bed_ID)
            new = False

        return new

    def get_date(self):
        """
        This method return the date of the computer regarding of the timezone.
        """
        tz = pytz.timezone(str(self.timezone))
        date = tz.localize(datetime(datetime.now().year,
                           datetime.now().month,
                           datetime.now().day,
                           datetime.now().hour,
                           datetime.now().minute,
                           datetime.now().second,
                           datetime.now().microsecond))
        return date

    def formalize(self, DR1, bed_ID, bed_time, date, format):
        """
        This method formalizes the data in adding meta data for the zigbee-gw program and the server interpretation.
        """
        meta_data = {'type' : None,
                     'sensor': 'bedsensor'}

        logger.info("%s: The bedsensor %s sent %s" % (date.isoformat(), bed_ID, DR1))

        occupency = bed_reasoning.occupency(DR1)
        logger.debug('occupency level: %s' %occupency)
        if occupency is not self.memory[bed_ID].get('occupency'):
            self.memory[bed_ID]['occupency'] = occupency
            meta_data['type'] = 'event'
            data = {'sensor' : bed_ID,
                    'value': occupency,
                    'signal_time' : bed_time,
                    'date': date.isoformat()}
            logger.info("Occupency level: %s" % occupency)

        else:
            meta_data['type'] = 'signal'
            data = {'sensor' : bed_ID,
                    'format': format,
                    'sample': DR1,
                    'signal_time' : bed_time,
                    'date': date.isoformat()}
        return meta_data, data

    def initialize(self, sample_bits, bed_ID):
        """
        Initialization of a bedsensor
        """

        logger.info('The signal matched with the bedsensor initialization patern.')

        if self.new_sensor(bed_ID):
            logger.info('Initialization of a new bedsensor: %s' %bed_ID)
        else:
            logger.info('Reset the bedsensor: %s' %bed_ID)

        self.mac_id = bed_ID
        nb_FSR = int(sample_bits[1])
        nb_FSC = int(sample_bits[2])
        t0 = self.get_date().isoformat()
        occupency = DEFAULT_OCCUPENCY
        self.memory[self.mac_id] = {
            'nb_FSR' : nb_FSR,
            'nb_FSC' : nb_FSC,
            'occupency' : occupency,
            't0' : t0
        }

        logger.info('The bedsensor %s is equiped with %s FSR sensors and %s FSC sensors' % (self.mac_id, nb_FSR, nb_FSC))

        logger.debug('new sensor info:%s' %self.memory[self.mac_id])


    def matches(self, signal):

        signal_data = signal['rf_data']
        signal_addr = signal['source_addr']
        """
        The method to check if the signal received is corresponding with the bedsensor patern. If the signal is corresponding, we extract the information corresponding
        """
        #Data FSR 1spl   $ DR1 , ID , R0 R1 R2 R3 R4 R5 R6 R7 \n
        #example: $DR1,\x00\x13\xa2\x00@\xa1N\xba,\x00\x00\x06\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n

        #The other simple possible is $YOP,nb_FSR,nbFSC\n
        #example: $YOP,08,02\n

        #$DR1,\x00\x10\x02\r,\n\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\n

        logger.debug('Checking the signal "%s" in bedsensor program' % signal_data)


        pattern = (r'^\$(?P<data_type>YOP|DR1).*$\n')
        regexp = re.compile(pattern)
        match = regexp.match(signal_data)

        if match:
            date = self.get_date()

            #Get the ID of the bedsensor sending the signal
            bed_addr = 0
            for octet in signal_addr:
                bed_addr = (bed_addr*256)+ord(octet)

            bed_ID = 'BED-'+str(bed_addr)

            logger.debug('Address of the Bedproto: %s' % bed_ID)

            #Create a list with the signal parts
            sample_bits = signal_data.split(",")

            if match.group('data_type') == 'YOP':

                #Initialization signal

                self.initialize(sample_bits, bed_ID)
                return None, None

            else:

                #FSR data signal

#                if integrity(signal) == False:
#                    return None, None

                logger.info('The signal matchs with the bedsensor DR1 data patern')
                logger.debug('The DR1 sample is: %s' %sample_bits)

                if len(sample_bits) < FRAGMENT_NUMBER: # It is necessary to put a condition because the Arduino sending binary values can send unexpected '/n'.
                    logger.error('There are %s fragments, this is less than the %s fragments expected in a sample' % (len(sample_bits), FRAGMENT_NUMBER))
                    return None, None

                #Time of the bedsensor in ms since the initialisation
                #TODO: Associate this value with the real acquisition time in using the t0 value.
                sample_ID = sample_bits[1]
                bed_time = 0
                for octet in sample_ID:
                    bed_time = (bed_time*256)+ord(octet)

                logger.debug('Time of the Bedproto: %s' % bed_time)

                #Get the values of the 8 FSR of DR1 sample
                sample_data = sample_bits[2]
                DR1 = {}
                i = 0
                for val in ['R1','R2','R3','R4','R5','R6','R7','R8']:
                    try:
                        utf8 = sample_data[i]+sample_data[i+1]
                    except:
                        logger.error('There are less than 8 values received')
                        return None, None
                    DR1[val] = 0
                    for octet in utf8:
                        DR1[val] = (DR1[val]*256 )+ord(octet)
                    i = i+2

                logger.debug('Measures of the FSR: %s, date: %s' % (DR1, date.isoformat()))


                return self.formalize(DR1, bed_ID, bed_time, date, match.group('data_type'))

        else:
            logger.debug('The signal is not matching with the bedsensor patern')

            return None, None
