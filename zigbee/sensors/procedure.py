import sys

from ubigate import logger

from zigbee.sensors import reasoning

SIZEOF_DR1 = 48
FRAGMENT_NUMBER = 3

DEFAULT_ID = None
DEFAULT_OCCUPENCY = 'off'
DEFAULT_FSR = 1
DEFAULT_FSC = 0
DEFAULT_ORDER = None
DEFAULT_THRESHOLD = 500

RESPONSE_TYPE = 'response'
RESPONSE_OK = '$OK\n'

# A dictionary to interprete the order from the server
orders_dict = {
    'battery':'$STA\n',
    'nbSensor' : '$STA\n'
}

def integrity(signal):
    if sys.getsizeof(signal) == SIZEOF_DR1:
        logger.debug('The size of the data received is corresponding')
        return True
    logger.error('The size of the data received is not corresponding')
    return False


def new_sensor(bed_ID, memory):

    new = None
    id_list = list(memory.keys())
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


def default_init(bed_ID, memory, date):
    """
    Initialization of a bedsensor without YOP tram
    """
    mac_id = bed_ID
    nb_FSR = DEFAULT_FSR
    nb_FSC = DEFAULT_FSC
    t0 = date.isoformat()
    occupency = DEFAULT_OCCUPENCY
    memory[mac_id] = {
        'nb_FSR' : nb_FSR,
        'nb_FSC' : nb_FSC,
        'occupency' : occupency,
        't0' : t0,
        'order' : DEFAULT_ORDER
    }

    return memory


def formalize_signal(DR1, bed_ID, bed_time, date, format, gate):
    """
    This method formalizes a signal in adding meta data for the server interpretation.
    """
    meta_data = {'type' : 'signal',
                 'sensor': 'bedsensor'}

    logger.info("%s: The bedsensor %s sent %s" % (date.isoformat(), bed_ID, DR1))

    data = {'sensor' : bed_ID,
            'format': format,
            'sample': DR1,
            'signal_time' : bed_time,
            'date': date.isoformat(),
            'house': gate.config.house
            }

    return meta_data, data


def formalize_event(occupency, bed_ID, bed_time, date, gate):
    """
    This method formalizes an event in adding meta data for the server interpretation.
    """
    meta_data = {'type' : 'event',
                 'sensor': 'bedsensor'}

    logger.info("%s: The bedsensor %s occupency is %s" % (date.isoformat(), bed_ID, occupency))

    data = {'sensor' : bed_ID,
            'value': occupency,
            'signal_time' : bed_time,
            'date': date.isoformat(),
            'house': gate.config.house
            }

    return meta_data, data


def publication(meta_data, data, gate):
    topic = "/zigbee/sensor/%s/%s" % (meta_data['sensor'],
                                      meta_data['type'])
    gate.push(topic, data)


def YOPtram(sample_bits, bed_ID, memory, date):
    """
    Initialization of a bedsensor
    """

    if new_sensor(bed_ID, memory):
        logger.info('Initialization of a new bedsensor: %s' %bed_ID)
    else:
        logger.info('Reset the bedsensor: %s' %bed_ID)

    logger.info('The signal matched with the bedsensor initialization patern.')

    mac_id = bed_ID
    nb_FSR = int(sample_bits[1])
    nb_FSC = int(sample_bits[2])
    t0 = date.isoformat()
    occupency = DEFAULT_OCCUPENCY
    memory[mac_id] = {
        'nb_FSR' : nb_FSR,
        'nb_FSC' : nb_FSC,
        'occupency' : occupency,
        't0' : t0,
        'order' : DEFAULT_ORDER
    }

    logger.info('The bedsensor %s is equiped with %s FSR sensors and %s FSC sensors' % (mac_id, nb_FSR, nb_FSC))

    logger.debug('new sensor info:%s' %memory[mac_id])

    return RESPONSE_TYPE, RESPONSE_OK, memory


def DR1tram(sample_bits, bed_ID, memory, date, threshold, gate):

    #if integrity(signal) == False:
    #return None, None

    #If the signal come from an still unknown bedsensor.
    if new_sensor(bed_ID, memory):
        logger.warning('Message reveived by an unknown bedsensor')
        logger.warning('Default instantiation of: %s' %bed_ID)
        memory = default_init(bed_ID, memory, date)
    else:
        logger.debug('The bedsensor is already known')

    logger.info('The signal matchs with the bedsensor DR1 data patern')
    logger.debug('The DR1 sample is: %s' %sample_bits)

    if len(sample_bits) < FRAGMENT_NUMBER: # It is necessary to put a condition because the Arduino sending binary values can send unexpected '/n'.
        logger.error('There are %s fragments, this is less than the %s fragments expected in a sample' % (len(sample_bits), FRAGMENT_NUMBER))
        return None, None, memory

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
            return None, None, memory
        DR1[val] = 0
        for octet in utf8:
            DR1[val] = (DR1[val]*256 )+ord(octet)
        i = i+2

    logger.debug('Measures of the FSR: %s, date: %s' % (DR1, date.isoformat()))

    occupency = reasoning.occupency(DR1, threshold)
    logger.debug('occupency level: %s' %occupency)
    if occupency is not memory[bed_ID].get('occupency'):
        memory[bed_ID]['occupency'] = occupency
        logger.info("Occupency level: %s" % occupency)
        meta_data, data = formalize_event(occupency, bed_ID, bed_time, date, gate)
        publication(meta_data, data, gate)


    meta_data, data = formalize_signal(DR1, bed_ID, bed_time, date, 'DR1', gate)
    publication(meta_data, data, gate)

    return RESPONSE_TYPE, RESPONSE_OK, memory


def orderTRAM(order):
    orderCode = None

    order_list = list(orders_dict.keys())
    logger.debug('list of the orders registered: %s' %order_list)

    if order_list.count(order) == 0:
        logger.warning('The order %s is not known' % order)
    else:
        orderCode = orders_dict.get(order)
        logger.debug('The code %s will be send to the bedsensor' % orderCode)

    return orderCode



