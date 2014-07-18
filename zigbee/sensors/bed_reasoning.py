

THRESHOLD = 500

def occupency(DR1):
    """
    Methode to define if the bed is occupied or not in using one single sensor
    """

    for val in ['R1','R2','R3','R4','R5','R6','R7','R8']:
        if DR1[val] > THRESHOLD:
            return "on"
    return "off"
