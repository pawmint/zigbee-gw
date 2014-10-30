def occupency(DR1, THRESHOLD):
    """
    Method to define if the bed is occupied or not in using one single sensor
    TODO : read the file only one time.
    """
    if DR1['R1'] == 0 and DR1['R2'] == 0 and DR1['R3'] == 0 and DR1['R4'] == 0 and DR1['R5'] == 0 and DR1['R6'] == 0 and DR1['R7'] == 0 and DR1['R8'] == 0:
        state = "off"
    elif DR1['R1'] > THRESHOLD and DR1['R2'] == 0 and DR1['R3'] == 0 and DR1['R4'] == 0 and DR1['R5'] == 0 and DR1['R6'] == 0 and DR1['R7'] == 0 and DR1['R8'] == 0:
        state = "on"

    return state

    # for val in ['R1','R2','R3','R4','R5','R6','R7','R8']:
    #     if DR1[val] > THRESHOLD:
    #         return "on"
    # return "off"
