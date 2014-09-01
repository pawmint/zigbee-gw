
def occupency(DR1, THRESHOLD):
    """
    Methode to define if the bed is occupied or not in using one single sensor
    TODO : read the file only one time.
    """

    for val in ['R1','R2','R3','R4','R5','R6','R7','R8']:
        if DR1[val] > THRESHOLD:
            return "on"
    return "off"
