THRESHOLD = 1000
state = "off"


def occupency(DR1, plugged_sensors):
    """
    Guess whether the bed is occupied
    """
    global state

    plugged_values = {sensor: DR1.pop(sensor) for sensor in plugged_sensors}

    if all(value == 0 for value in DR1.values()):
        if any(value >= THRESHOLD for value in plugged_values.values()):
            state = "on"
        else:
            state = "off"

    return state
