#!/usr/bin/env python3
# File:     LW3010EC.py
# Brief:    Power supply controller

from serial.tools.list_ports import comports
from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS
from pymodbus.client import ModbusSerialClient
from pymodbus import pdu
from enum import Enum
from time import sleep
import os
import click

class PSU:
    """
    Basic PSU com port controller
    """

    class Registers(Enum):
        VOLTAGE_WRITE = 0x1000
        CURRENT_WRITE = 0x1001
        VOLTAGE_READ = 0x1002
        CURRENT_READ = 0x1003
        OUTPUT_READ = 0x1004
        CC_CV_OC_READ = 0x1005 # does not seem to be supported
        OUTPUT_WRITE = 0x1006
        ADDRESS_WRITE = 0x1008 # untried

    def __init__(self, com_port=None, slaveId=0x1, debug=False):
        self.debug = debug
        self.com_port = self.find_PSU_com_port( com_port )
        self.pymc = ModbusSerialClient(port=self.com_port, baudrate=9600, timeout=5)
        self.slaveId = slaveId

    def find_PSU_com_port(self, com_port=None):
        """Searches for PSU USB COM port adapter"""
        found_com_port = None

        adapter_ids = {
            "CH340": ("1A86", "7523")
            # add other serial devices here if we find them
            }

        com_ports_list = list(comports())

        if com_port is None:
            # detect PSU in list of ports
            for port in com_ports_list:
                # some adapters don't report VID and PID - these are not supported so don't try and test against them
                if port.vid and port.pid:
                    for adapter in adapter_ids:
                        if ('{:04X}'.format(port.vid), '{:04X}'.format(port.pid)) == adapter_ids[adapter]:
                            if self.debug:
                                print(f'Found supported {port.manufacturer} adapter {adapter} on {port.device}')
                            # assume last com port found, multiple PSUs not supported (yet!)
                            if found_com_port is None or port.device > found_com_port:
                                found_com_port = port.device
        else:
            # check specified port exists on host
            for port in com_ports_list:
                if os.path.realpath(com_port) == port.device:
                    found_com_port = os.path.realpath(com_port)
                if com_port == port.device:
                    found_com_port = port.device

        if found_com_port is None:
            raise OSError('PSU com port adapter not found')

        if self.debug:
            print(f'Assuming PSU on {found_com_port}')

        return found_com_port

    def write(self, address, value):
        rr = self.pymc.write_register(address.value, value, slave=self.slaveId)
        if rr.isError() and self.debug:
            print(address.name, rr.message)

    def read(self, address, len=1):
        rr = self.pymc.read_holding_registers(address.value, len, slave=self.slaveId)

        if not type(rr) is pdu.register_read_message.ReadHoldingRegistersResponse:
            if self.debug:
                print(address.name, rr)
            return None

        if rr.isError():
            if self.debug:
                print(address.name, rr.message)
            return None

        return rr.registers[0]

    @property
    def current(self):
        current = self.read(PSU.Registers.CURRENT_READ)
        if current is None:
            return None
        else:
            return current/100

    @current.setter
    def current(self, amps):
        self.write(PSU.Registers.CURRENT_WRITE, int(round(amps*100)))

    @property
    def voltage(self):
        voltage = self.read(PSU.Registers.VOLTAGE_READ)
        if voltage is None:
            return None
        else:
            return voltage/100

    @voltage.setter
    def voltage(self, volts):
        self.write(PSU.Registers.VOLTAGE_WRITE, int(round(volts*100)))

    @property
    def output(self):
        return False if self.read(PSU.Registers.OUTPUT_READ) == 0 else True

    @output.setter
    def output(self, on):
        self.write(PSU.Registers.OUTPUT_WRITE, int(on))

@click.command()
@click.option('--status', '-s', is_flag=True, default=False, help='Show PSU status after commands applied')
@click.option('--on', is_flag=True, default=False, help='Turn output on')
@click.option('--off', is_flag=True, default=False, help='Turn output off')
@click.option('--voltage', '-v', type=click.FloatRange(0, 30), help='Set voltage in Volts')
@click.option('--current', '-a', type=click.FloatRange(0, 10), help='Set current in Amps')
@click.option('--delay-on', '-d', type=int, help='Delay in seconds applied before enabling output')
@click.option('--debug', is_flag=True, default=False, help='Show internal debug messages')
@click.option('--com-port', type=str, default=None, help='Select com port to use. If omitted will self-detect PSU')
@click.option('--slave-id', type=int, default=1, help='For dual-bank PSUs, select slave to control EG 1 (default) or 2')
@click.option('--scan', is_flag=True, default=False, help='Scan registers for non-zero values')
def psu_cmd(status, on, off, voltage, current, delay_on, debug, com_port, slave_id, scan):
    """
    PSU controller
    
    If both --on and --off are specified, the output will be switched off first, other changes applied and then the output switched on.
    """
    psu = PSU(com_port=com_port, slaveId=slave_id, debug=debug)

    if scan:
        for address in range(0x1001,0x1100):
            class test(Enum):
                REGISTER = address
            result = psu.read(test.REGISTER)
            if(result > 0):
                print('Address', address,':',result)
        exit(0)

    if off:
        psu.output = False
        print('Output disabled')
    
    if voltage:
        psu.voltage = voltage
        print(f"Voltage set to {voltage}V")

    if current:
        psu.current = current
        print(f"Current set to {current}A")

    if on:
        if delay_on:
            sleep(delay_on)
        psu.output = True
        print('Output enabled')
        
    if status:
        sleep(1) # allow PSU to settle for 1 second
        print(f'Output={psu.output}')
        print(f'Voltage={psu.voltage}V')
        print(f'Current={psu.current}A')

if __name__ == '__main__':
    psu_cmd()
