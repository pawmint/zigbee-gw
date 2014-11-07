from datetime import datetime
import pytz

from zigbee.sensors import reasoning
from ubigate import logger

SIZEOF_DR1 = 48

DEFAULT_NB_FSR = 0
DEFAULT_NB_FSC = 0
DEFAULT_OCCUPENCY = ''

current_occupency = DEFAULT_OCCUPENCY


def get_bed_time(sample_id):
    return sum([ord(octet) * pow(256, i)
                for i, octet in enumerate(reversed(sample_id))])


def get_bed_id(signal_addr):
    bed_addr = sum([ord(octet) * pow(256, i)
                    for i, octet in enumerate(reversed(signal_addr))])
    return 'BED-' + str(bed_addr)


def get_DR1(sample_data):
    DR1 = {}
    iterator = iter(sample_data)
    sensors = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8']
    for sensor in sensors:
        try:
            utf8 = next(iterator) + next(iterator)
        except:
            logger.error('There are less than 8 values received')
            return None
        DR1[sensor] = sum([ord(octet) * pow(256, i)
                           for i, octet in enumerate(reversed(utf8))])
    return DR1


def date(timezone):
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
    return date.isoformat()


def parse_dr1(signal_data, signal_addr, timezone):
    global current_occupency

    bed_time, raw_dr1 = signal_data[:]
    dr1 = get_DR1(raw_dr1)
    bed_id = get_bed_id(signal_addr)

    logger.debug('Measures for the bed %s: FSR=%s, date=%s' % (bed_id,
                                                               dr1,
                                                               date(timezone)))

    occupency = reasoning.occupency(dr1)
    if occupency is not current_occupency:
        data = {'sensor': bed_id,
                'type': 'event',
                'value': occupency,
                'signal_time': bed_time,
                'date': date(timezone)}
        current_occupency = occupency
    else:
        data = {'sensor': bed_id,
                'type': 'signal',
                'format': 'DR1',
                'sample': dr1,
                'signal_time': bed_time,
                'date': date(timezone)}
    return data


def matches(signal, timezone):
    """ Check if the signal received matches the bedsensor pattern.
    If the signal matches, we extract the corresponding information
    """
    signal_data = signal['rf_data'].split(',')
    signal_addr = signal['source_addr']
    # Data FSR 1spl   $ DR1 , ID , R0 R1 R2 R3 R4 R5 R6 R7 \n
    # example: $DR1,\x00\x13\xa2\x00@\xa1N\xba,\x00\x00\x06\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n

    # The other simple possible is $YOP,nb_FSR,nbFSC\n
    # example: $YOP,08,02\n

    # $DR1,\x00\x10\x02\r,\n\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\n

    if len(signal_data) != 3:
        return None

    logger.debug('Checking the signal "%s" in bedsensor program' % signal_data)

    if signal_data[0] == '$DR1':
        logger.debug('The signal matches with the bedsensor DR1 data pattern')
        return parse_dr1(signal_data[1:], signal_addr, timezone)
    elif signal_data[0] == '$YOP':
        nb_fsr, nb_fsc = signal_data[1:]
        logger.debug('Number of FSR: %s' % nb_fsr)
        logger.debug('Number of FSC: %s' % nb_fsc)
        return None
    else:
        logger.debug('The signal is not matching with the bedsensor pattern')
        return None
