import RPi.GPIO as gpio
from vars import MOTOR1_FORWARD_GPIO, ON, OFF

def setup_gpio():

	gpio.setmode(gpio.BCM)
	gpio.setwarnings(False)

	gpio.setup(MOTOR1_FORWARD_GPIO,gpio.OUT)

	gpio.output(MOTOR1_FORWARD_GPIO,OFF)

