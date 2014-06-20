from datetime import datetime
import pytz
import re

from ubigate import logger


class BedSensor(object):

    def __init__(self):

        self.t0_buffer = 0
        self.nb_FSR = 0
        self.nb_FSC = 0
        self.ID = 0

    def synchronization(signal):
        """
        Synchronization between the beaglebone and the bedsensor
        when the bedsensor send its first sample.
        """

        pattern = (r'^\$\s(?P<data_type>YOP).*$\n')

        regexp = re.compile(pattern)

        match = regexp.match(str(signal))

        if match:

            # We split the signal into samples (debufferization)
            samples = signal.split("$")

            init_sample = samples[1]
            # We split the first sample of the buffer.
            init_sample_bits = init_sample.split(",")

            if self.ID != 0:
                if self.ID != int(init_sample_bits[x], 16):
                    logger.error('The synchronization is not allowed, another '
                                 'bedsensor is registered on this beaglebone')
                    return False

                else:
                    logger.info('The beaglebone is resynchronizing with the '
                                'bedsensor: %s' % int(init_sample_bits[x], 16))
                    t0_buffer = int(init_sample_bits[x], 16)
                    nb_FSR = int(init_sample_bits[x],16)
                    nb_FSC = int(init_sample_bits[x],16)
                    """
                    TODO: send OK to the bedsensor
                    """
                    return True

            else:

                logger.info('The beaglebone is synchronizing with the bedsensor: %s' % int(init_sample_bits[x], 16))
                sel.ID = int(init_sample_bits[x], 16)
                self.t0_buffer = int(init_sample_bits[x], 16)
                self.nb_FSR = int(init_sample_bits[x],16)
                self.nb_FSC = int(init_sample_bits[x],16)
                """
                TODO: send OK to the bedsensor
                """
            return True
        else:
            return False

    def matches(signal, timezone):
        """@todo: Docstring for matches.

        :signal: @todo
        :returns: @todo

        """
        # Data FSR 1spl   $ DR1 , TIME , R0 R1 R2 R3 R4 R5 R6 R7 \n
        # example: $DR1,012345678,0123401234012340123401234012340123401234\n
        # with the number writed in hexa in big indian
        # Data FSC 1spl   $ DC1 , TIME , C1 C2 \n
        # Data FSC Nspl   $ DCN , TIME , DELTA , C0 C1 , ... \n
        # Every simple is concatenated in a buffer without separation
        # example: $DR1,012345A78,0123401234012340123401234012340123401234\n$DC1...\n

        logger.debug('Checking the signal "%s" in bedsensor' % str(signal))

        if synchronization(signal):
            return None, None

        pattern = (r'^\$\s(?P<data_type>YOP).*$\n')

        regexp = re.compile(pattern)

        match = regexp.match(str(signal))

        if match:

            logger.info('The signal matched with the bedsensor_signal patern')

            # We split the signal into samples (debufferization)
            samples = signal.split("$")
            nb_samples = len(samples) - 1

            init_sample = samples[1]
            # We split the first sample of the buffer.
            init_sample_bits = init_sample.split(",")

            t0_buffer = int(init_sample_bits[x], 16)
            nb_FSR = int(init_sample_bits[x], 16)
            nb_FSC = int(init_sample_bits[x], 16)

            for i in range(2, nb_samples + 1):
                sample_bits = samples[i].split()

                sample_type = sample_bits[0]
                sample_time = sample_bits[1]

                if sample_type == "YOP":
                    logger.error('There is a YOP sample in a wrong position '
                                 'in the buffer reveived')
                elif False:  # sample_type ==
                    pass

        # if match.group('data_type') == 'DR1':
        #     pattern = (r'^\$\s(?P<data_type>DR1|DC1|DCN)\s,'
        #                '\s(?<time>\d{3})\s,'
        #                '\s(?<R0>\d{3})\s,\s(?<R1>\d{3})\s,'
        #                '\s(?<R2>\d{3})\s,\s(?<R3>\d{3})\s,'
        #                '\s(?<R4>\d{3})\s,\s(?<R5>\d{3})\s,'
        #                '\s(?<R6>\d{3})\s,\s(?<R7>\d{3})\s\n$\n')

        # elif match.group('data_type') == 'DC1':
        #     pattern = (r'^\$\s(?P<data_type>DR1|DC1|DCN)\s,'
        #                '\s(?<time>\d{3})\s,'
        #                '\s(?<R0>\d{3})\s,\s(?<R1>\d{3})\s\n$\n')

        # elif match.group('data_type') == 'DCN':
        #     pattern = (r'^\$\s(?P<data_type>DR1|DC1|DCN)\s,'
        #                '\s(?<time>\d{3})\s,'
        #                '\s(?<delta>\d{3})\s,'
        #                '\s(?<R0>\d{3})\s,\s(?<R1>\d{3})\s,'
        #                '\s(?<R2>\d{3})\s,\s(?<R3>\d{3})\s,'
        #                '\s(?<R4>\d{3})\s,\s(?<R5>\d{3})\s,'
        #                '\s(?<R6>\d{3})\s,\s(?<R7>\d{3})\s\n$\n')
        # else:
        #     logger.debug("no pattern for '$ %s' sample in the bedsensor_signal" % match.group('data_type'))
        #     return None, None

        # regexp = re.compile(pattern)

        # match = regexp.match(str(signal))

        # if match:

        #     logger.info('The signal is matching with the %s bedsensor_signal patern' % match.group('data_type'))

        #     tz = pytz.timezone(str(timezone))
        #     sensor = 'PIR'

        #     date = tz.localize(datetime(datetime.now().year,
        #                        datetime.now().month,
        #                        datetime.now().day,
        #                        datetime.now().hour,
        #                        datetime.now().minute,
        #                        datetime.now().second,
        #                        datetime.now().microsecond))

        #     logger.info('value: "%s", led: "%s", date: "%s"' %
        #             (match.group('value'), match.group('led'), date.isoformat()))

        #     data = {'led': match.group('led'),
        #             'date': date.isoformat()}
        #     return sensor, data

    # else:
        # logger.debug('The signal is not matching with the bedsensor_signal patern')

    # return None, None


        return match.group('data_type'), "not yet"
