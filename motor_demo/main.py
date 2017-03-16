#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
    Super simple program to show off the operation of the Trident motors
"""
import config
import serial
import time

import debug_messages as dm

class CommandWriter:
    """ Writes commands over serial
    Attributes:
    """
    def __init__(self, port='/dev/ttyUSB0', baud_rate=115200):
        """
        Note:
        Args:
            port (optional)(str): The port to send commands to (default: /dev/ttyUSB0)
            baud_rate (optional)(int): The baud rate (default: 115200)
        """
        self.port = port
        self.baud_rate = baud_rate
        self.ser = {}
        self.initialize()
        
    def initialize(self):
        """
        Opens the serial port and sets up communications
        """
        # Try to setup the serial connection
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
        except(OSError, serial.SerialException):
            dm.print_fatal(
                ("Could not open port %s with baud rate: %s" %
                 (self.port, self.baud_rate)))
            exit()
            
    def write_command(self, command_type, args):
        """
        Writes a CRC8 command over the serial line
        """
        command_out = self._create_command(command_type, args)
        self.ser.write(command_out)
        self.ser.flush()
        dm.print_info("Wrote: {0}".format(command_out))
        
    def _create_command(self, command_type, args):
        """Creates a message cockpit expects
        """
        command = command_type + '('
        arg_list = list(args)
        
        if len(arg_list) != 0:
            for index in range(0, (len(arg_list) - 1)):
                command = command + str(arg_list[index]) + ','
            # Add final argument and closing marks
            command = command + str(arg_list[len(arg_list) - 1]) + ");"
        else:
            command = command + ");"
        # Calculate crc on buffer
        crc = self._crc8(command)
        # prepend crc as first byte
        command = chr(crc) + command
        # return buffer
        return command
        
    def _crc8(self, incoming):
        """
        Does crc8 magic
        """
        msg_byte = list(bytearray(incoming))
        check = 0
        for i in msg_byte:
            check = self._add_to_crc(i, check)
        return check
        
    def _add_to_crc(self, b, crc):
        """
        CRC helper function
        """
        b2 = b
        if b < 0:
            b2 = b + 256
        for i in xrange(8):
            odd = ((b2 ^ crc) & 1) == 1
            crc >>= 1
            b2 >>= 1
            if odd:
                crc ^= 0x8C  # This means crc ^= 140
        return crc



def send_high_command(interface):
    """ Sends a high powered throttle command
    """
    level = 100
    command = "throttle"
    
    interface.write_command(command, level)

def send_low_command(interface):
    """Sends a low powered throttle command
    """
    level = 5
    command = "throttle"

    interface.write_command(command, level)

def send_zero_command(interface):
    """Sends a zero command
    """
    level = 0
    command = "throttle"

    interface.write_command(command, level)







if __name__ == '__main__':

    # Serial port access
#    serial_interface = CommandWriter(port=config.default_port, baud_rate=config.default_baud_rate)

    # Loop until done
    is_running = True

    # Send commands at 60 hz
    rate = 16

    # Current time
    current_time = 0

    #send_zero_command(serial_interface)

    # Loop
    while is_running:
        
        # Keep track of the start time for looping, convert to ms
        start = time.time() * 1000

        # Do stuff
        # Beginnning        
        if current_time < 6.0:
            dm.print_info('Slow')
        elif current_time > 6.0 and current_time < 12.0:
            dm.print_info('Fast')
        elif current_time > 12.0 and current_time < 16.0:
            dm.print_info('Slow')
        else:
            dm.print_info('Stop')
     
        # End time, for rate limit, convert to ms
        end = time.time() * 1000
        delta = end - start
        remain = rate - delta

        if remain > 0:
            time.sleep(remain/1000.0)

        current_time = current_time + (remain + delta)/1000.0



