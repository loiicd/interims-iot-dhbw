#!/usr/bin/env python3
import smbus
import RPi.GPIO as GPIO
from hbs_operator import HBSOperator
from mqtt_subscriber import MqttSubscriber
from high_bay_storage import HighBayStorage


class IOExtension:
    """ IO extension board for Raspberry Pi """

    def __init__(self, out_a=0, out_b=0):
        self._mcp23017 = (0x20, 0x24, 0x22)
        self._address_map = {
            'IODIRA': 0x00, 'IODIRB': 0x01, 'GPPUA': 0x0c, 'GPPUB': 0x0d,
            'GPIOA': 0x12, 'GPIOB': 0x13, 'GPINTENA': 0x04, 'GPINTENB': 0x05
        }
        self._in_port_map = ((0, 'GPIOA'), (0, 'GPIOB'), (1, 'GPIOA'), (1, 'GPIOB'))
        self._bus = smbus.SMBus(1)
        # enable pullup resistors for input ports for device 0 and 1
        self._bus.write_byte_data(self._mcp23017[0], self._address_map['GPPUA'], 0xff)
        self._bus.write_byte_data(self._mcp23017[0], self._address_map['GPPUB'], 0xff)
        self._bus.write_byte_data(self._mcp23017[1], self._address_map['GPPUA'], 0xff)
        self._bus.write_byte_data(self._mcp23017[1], self._address_map['GPPUB'], 0xff)
        # set port direction to output for device 2
        self._bus.write_byte_data(self._mcp23017[2], self._address_map['IODIRA'], 0x00)
        self._bus.write_byte_data(self._mcp23017[2], self._address_map['IODIRB'], 0x00)
        # initialize output port status
        self._out_a, self._out_b = out_a, out_b
        self._bus.write_byte_data(self._mcp23017[2], self._address_map['GPIOA'], self._out_a)
        self._bus.write_byte_data(self._mcp23017[2], self._address_map['GPIOB'], self._out_b)

        # interrupts
        self._bus.write_byte_data(self._mcp23017[0], self._address_map['GPINTENA'], 0xFF)
        self._bus.write_byte_data(self._mcp23017[0], self._address_map['GPINTENB'], 0xFF)
        self._bus.write_byte_data(self._mcp23017[1], self._address_map['GPINTENA'], 0xFF)
        self._bus.write_byte_data(self._mcp23017[1], self._address_map['GPINTENB'], 0xFF)

        # Init GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.add_event_detect(16, GPIO.RISING, callback=self.interrupt_routine, bouncetime=200)
        GPIO.add_event_detect(7, GPIO.RISING, callback=self.interrupt_routine, bouncetime=200)
        GPIO.add_event_detect(8, GPIO.RISING, callback=self.interrupt_routine, bouncetime=200)
        GPIO.add_event_detect(25, GPIO.RISING, callback=self.interrupt_routine, bouncetime=200)

    def read_port(self, port: int) -> list:
        """ Returns a list of booleans showing the current setting of the input port.
            Select port with an integer range 0 ... 3 """
        if port < 4:
            result = self._bus.read_byte_data(self._mcp23017[self._in_port_map[port][0]],
                                              self._address_map[self._in_port_map[port][1]])
            return [result & (1 << mask) == 0 for mask in range(8)]
        else:
            print("Input port", port, "undefined")
            return None

    def set_port(self, port: int, port_pin: int, value: bool):
        """ Sets a pin at the output port.
            port: 0 ... 1
            port_pin: 0 ... 7
            value: True for high, False for low """
        if port_pin < 8:
            if port == 0:
                if value:
                    self._out_a |= (1 << port_pin)
                else:
                    self._out_a &= ~(1 << port_pin)
                self._bus.write_byte_data(self._mcp23017[2], self._address_map['GPIOA'], self._out_a)
            elif port == 1:
                if value:
                    self._out_b |= (1 << port_pin)
                else:
                    self._out_b &= ~(1 << port_pin)
                self._bus.write_byte_data(self._mcp23017[2], self._address_map['GPIOB'], self._out_b)
            else:
                print("Output port", port, "undefined")
        else:
            print("Output pin", port_pin, "undefined")

    def get_output_port(self) -> tuple:
        """ Returns a tuple with two bytes showing the current setting of the output port. """
        return self._out_a, self._out_b << 8

    def interrupt_routine(self, callback):
        """ Not fully implemented.
        Stops the operator by an interrupt when the target position is reached. """
        op.stop_if_target_reached()


io = IOExtension()
op = HBSOperator(io)
hbs = HighBayStorage(op)
MqttSubscriber(hbs)
