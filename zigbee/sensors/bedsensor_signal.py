from datetime import datetime
import pytz
import re
import sys

from zigbee.sensors import bed_reasoning
from ubigate import logger

SIZEOF_DR1 = 48
FRAGMENT_NUMBER = 3

def integrity(signal):
    if sys.getsizeof(signal) == SIZEOF_DR1:
        logger.debug('The size of the data received is corresponding')
        return True
    logger.error('The size of the data received is not corresponding')
    return False

def get_date(timezone):
    """
    This method return the date of the computer regarding of the timezone.
    """
    tz = pytz.timezone(str(timezone))
    date = tz.localize(datetime(datetime.now().year,
                       datetime.now().month,
                       datetime.now().day,
                       datetime.now().hour,
                       datetime.now().minute,
                       datetime.now().second,
                       datetime.now().microsecond))
    return date

def formalize(DR1, bed_ID, date, format):
    """
    This method formalizes the data in adding meta data for the zigbee-gw program and the server interpretation.
    TODO: Add a memory to know the previous occupency state of the bedsensor
    """
    meta_data = {'type' : None,
                 'sensor': 'bedsensor'}

    occupency = bed_reasoning.occupency(DR1)
    if occupency is not None:
        meta_data['type'] = 'event'
        data = {'sensor' : bed_ID,
                'value': occupency,
                'date': date.isoformat()}

    else:
        meta_data['type'] = 'signal'
        data = {'sensor' : bed_ID,
                'format': format,
                'sample': DR1,
                'date': date.isoformat()}
    return meta_data, data

def matches(signal, timezone):
    """
    The method to check if the signal received is corresponding with the bedsensor patern. If the signal is corresponding, we extract the information corresponding
    """
    #Data FSR 1spl   $ DR1 , ID , R0 R1 R2 R3 R4 R5 R6 R7 \n
    #example: $DR1,\x00\x13\xa2\x00@\xa1N\xba,\x00\x00\x06\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n

    #The other simple possible is $YOP,nb_FSR,nbFSC\n
    #example: $YOP,08,02\n

    #$DR1,\x00\x10\x02\r,\n\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\n

    logger.debug('Checking the signal "%s" in bedsensor program' % signal)


    pattern = (r'^\$(?P<data_type>YOP|DR1).*$\n')
    regexp = re.compile(pattern)
    match = regexp.match(signal)

    if match:

        date = get_date(timezone)

        sample_bits = signal.split(",")

        if match.group('data_type') == 'YOP':

            """
            Initialization signal
            TODO: Add a memory to keep this informations
            """

            logger.info('The signal matched with the bedsensor initialization patern')

            nb_FSR = int(sample_bits[1])
            nb_FSC = int(sample_bits[2])

            logger.info('The bedsensor is equiped with %s FSR sensors and %s FSC sensors' % (nb_FSR, nb_FSC))
            return None, None

        else:

            """
            FSR data signal
            """

#            if integrity(signal) == False:
#                return None, None

            logger.info('The signal matchs with the bedsensor DR1 data patern')
            logger.debug('The DR1 sample is: %s' %sample_bits)

            if len(sample_bits) < FRAGMENT_NUMBER: # It is necessary to put a condition because the Arduino sending binary values can send unexpected '/n'.
                logger.error('There are %s fragments, this is less than the %s fragments expected in a sample' % (len(sample_bits), FRAGMENT_NUMBER))
                return None, None

            sample_ID = sample_bits[1]
            bed_mac = 0
            for octet in sample_ID:
                bed_mac = (bed_mac*256)+ord(octet)

            bed_ID = 'BED-'+str(bed_mac)

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


            return formalize(DR1, bed_ID, date, match.group('data_type'))

    else:
        logger.debug('The signal is not matching with the bedsensor patern')

        return None, None
