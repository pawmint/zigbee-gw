

THRESHOLD = 1000
STATE = "off"

def occupency(DR1):
    """
    Methode to define if the bed is occupied or not in using one single sensor
    """
    global STATE

    if DR1['R1'] == 0 and DR1['R2'] == 0 and DR1['R3'] == 0 and DR1['R4'] == 0 and DR1['R5'] == 0 and DR1['R6'] == 0 and DR1['R7'] == 0 and DR1['R8'] == 0:
        STATE = "off"
    elif DR1['R1'] > THRESHOLD and DR1['R2'] == 0 and DR1['R3'] == 0 and DR1['R4'] == 0 and DR1['R5'] == 0 and DR1['R6'] == 0 and DR1['R7'] == 0 and DR1['R8'] == 0:
        STATE = "on"

    return STATE

    # for val in ['R1','R2','R3','R4','R5','R6','R7','R8']:
    #     if DR1[val] > THRESHOLD:
    #         return "on"
    # return "off"
