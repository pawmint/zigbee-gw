
from ubigate import logger

def  method(userdata, message, memory):
    """
    Method applied when the server send an order. It write the order in the memory of the bedsensor corresponding.
    """
    logger.info("order received: " + str(message.payload) + "' on topic '"
        + message.topic + "' with QoS " + str(message.qos))
    logger.info("The momory state is: %s" %memory)

    try:
        message_bits = message.payload.split("|")
        order_bedID = message_bits[0]
        order_value = message_bits[1]

        memory[order_bedID]['order'] = order_value
    except IndexError :
        logger.error("The order received is not conform (<BED-ID>|<order>)")
    except KeyError:
        logger.error("The BED-ID given is not registered in the memory")

    return memory
