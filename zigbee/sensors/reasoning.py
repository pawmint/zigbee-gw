THRESHOLD = 1000
state = "off"


def occupency(DR1):
    """
    Method to define if the bed is occupied or not in using one single sensor
    TODO : read the file only one time.
    """
    global state

    unplugged = dict(DR1)
    r1 = unplugged.pop('R1')
    if r1 < THRESHOLD and all(value == 0 for value in unplugged.values()):
        state = "off"
    elif r1 >= THRESHOLD and all(value == 0 for value in unplugged.values()):
        state = "on"

    return state
