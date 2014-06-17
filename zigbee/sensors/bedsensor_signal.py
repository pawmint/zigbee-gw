from datetime import datetime
import pytz
import re

from ubigate import logger



def matches(signal, timezone):
    """@todo: Docstring for matches.
    :signal: @todo
    :returns: @todo
    """
    #Data FSR 1spl   $ DR1 , TIME , R0 R1 R2 R3 R4 R5 R6 R7 \n
    #example: $DR1,012345678,0123401234012340123401234012340123401234\n
    #with the number writed in binair in big indian (16 or 32 bit)
     #Data FSC 1spl   $ DC1 , TIME , C1 C2 \n
    #Data FSC Nspl   $ DCN , TIME , DELTA , C0 C1 , ... \n
    #Every simple is concatenated in a buffer without separation
    #example: $DR1,012345A78,0123401234012340123401234012340123401234\n$DC1...\n
    #The other simple possible is $YOP,nb_FSR,nbFSC\n

    logger.debug('Checking the signal "%s" in bedsensor program' % str(signal))


    pattern = (r'^\$(?P<data_type>YOP|DR1).*$\n')

    regexp = re.compile(pattern)

    match = regexp.match(str(signal))

    if match:

        sample_bits = signal.split(",")

        if match.group('data_type') == 'YOP':

            logger.info('The signal matched with the bedsensor initialization patern')

            nb_FSR = int(sample_bits[1])
            nb_FSC = int(sample_bits[2])

            logger.info('The bedsensor is equiped with %s FSR sensors and %s FSC sensors' % (nb_FSR, nb_FSC))
            return None, None

        else:

            logger.info('The signal matched with the bedsensor DR1 data patern')
            logger.debug('The DR1 sample is: %s' %sample_bits)

            """
            It is necessary to put a try because after some time of use, the Arduino bug and send incomplete sample.
            """
            try:
                len(sample_bits) == 3
            except:
                logger.debug('There are more than 3 parts in the sample')
                return None, None

            sensor = 'bedsensor'

            tz = pytz.timezone(str(timezone))
            date = tz.localize(datetime(datetime.now().year,
                               datetime.now().month,
                               datetime.now().day,
                               datetime.now().hour,
                               datetime.now().minute,
                               datetime.now().second,
                               datetime.now().microsecond))

            sample_time = sample_bits[1]
            time = 0
            for octet in sample_time:
                time = ( time * 256 ) + ord( octet )

            sample_data = sample_bits[2]
            DR1 = {}
            i = 0
            for val in ['R1','R2','R3','R4','R5','R6','R7','R8']:
                utf8 = sample_data[i]+sample_data[i+1]
                DR1[val] = 0
                for octet in utf8:
                    DR1[val] = ( DR1[val] * 256 ) + ord( octet )
                i = i+2

            logger.debug('Arduino time: %s, Measures of the FSR: %s, date: %s' % (time, DR1, date.isoformat()))

            data = {'DR1': DR1,
                    'date': date.isoformat()}

            return sensor, data

    else:
        logger.debug('The signal is not matching with the bedsensor patern')

    return None, None
