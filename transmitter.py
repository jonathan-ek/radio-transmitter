import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    from RPIMock import GPIO


def transmit(payload, sender, rounds=10):
    """
    :param rounds: Number of times to send the signal
    :param sender: GPIO port to send on
    :param payload: Shall be a list of tuples (bit, time)
    :return:
    """
    sender = int(sender)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(sender, GPIO.OUT)
    i = 0
    while i < rounds:
        for p in payload:
            GPIO.output(sender, p[0])
            time.sleep(p[1])
        i += 1

