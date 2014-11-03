def occupency(DR1, THRESHOLD):
    """
    Method to define if the bed is occupied or not in using one single sensor
    TODO : read the file only one time.
    """
    state = "off"

    while True:
        if(DR1['R1'] == 0 and DR1['R2'] == 0 and DR1['R3'] == 0 and
           DR1['R4'] == 0 and DR1['R5'] == 0 and DR1['R6'] == 0 and
           DR1['R7'] == 0 and DR1['R8'] == 0):
            state = "off"
        elif(DR1['R1'] > THRESHOLD and DR1['R2'] == 0 and DR1['R3'] == 0 and
             DR1['R4'] == 0 and DR1['R5'] == 0 and DR1['R6'] == 0 and
             DR1['R7'] == 0 and DR1['R8'] == 0):
            state = "on"

        yield state
