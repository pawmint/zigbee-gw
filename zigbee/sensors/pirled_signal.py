from datetime import datetime
import pytz
import re

from ubigate import logger


def matches(signal, timezone):
    """@todo: Docstring for matches.

    :signal: @todo
    :returns: @todo

    """
    # sample matching input: 448 - OFF\r\n
    logger.debug('Checking motion for signal "%s" in pirled program' % str(signal))

    pattern = (r'^(?P<value>\d{3})\s-\s(?P<led>ON|OFF)\r\n$\n*')

    regexp = re.compile(pattern)

    match = regexp.match(str(signal))

    if match:
        logger.info('The signal is matching with the ledpir patern')
        tz = pytz.timezone(str(timezone))

        sensor = 'PIR'

        date = tz.localize(datetime(datetime.now().year,
                               datetime.now().month,
                               datetime.now().day,
                               datetime.now().hour,
                               datetime.now().minute,
                               datetime.now().second,
                               datetime.now().microsecond))

        logger.info('value: "%s", led: "%s", date: "%s"' %
                    (match.group('value'), match.group('led'), date.isoformat()))

        data = {'led': match.group('led'),
                'date': date.isoformat()}
        return sensor, data

    else:
        logger.debug('The signal is not matching with the ledpir patern')

    return None, None
