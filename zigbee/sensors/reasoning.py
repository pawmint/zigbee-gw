THRESHOLD = 1000
state = "off"


def occupency(DR1):
    """
    Method to define if the bed is occupied or not in using one single sensor
    TODO : read the file only one time.
    """
    global state

    r1 = DR1.pop('R1')
    if r1 < THRESHOLD and all(value == 0 for value in DR1.values()):
        state = "off"
    elif r1 >= THRESHOLD and all(value == 0 for value in DR1.values()):
        state = "on"

    return state
