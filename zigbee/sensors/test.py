import pirled_signal
from tzlocal import get_localzone

timezone = get_localzone()
print(timezone)

signal = "['448 - OFF\r\n']"

sensor, data = pirled_signal.matches(signal, timezone)
print('Signal received: sensor:%s, data: %s' % (sensor, data))
