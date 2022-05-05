# File:     LW3010EC.py
# Brief:    Power supply controller

from serial.tools.list_ports import comports
from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS
from pymodbus.client.sync import ModbusSerialClient
from enum import Enum


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

    def __init__(self, slaveId=0x1, debug=False):
        self.debug = debug
        self.com_port = None
        self.com_port = self.find_PSU_com_port()
        self.pymc = ModbusSerialClient(method='rtu', port=self.com_port, baudrate=9600, timeout=5)
        self.slaveId = slaveId

    def find_PSU_com_port(self):
        """Searches for PSU USB COM port adapter"""

        adapter_ids = {
            "CP2104": ("1A86", "7523")
            # add other serial devices here if we find them
            }

        com_ports_list = list(comports())

        for port in com_ports_list:
            # some adapters don't report VID and PID - these are not supported so don't try and test against them
            if port.vid and port.pid:
                for adapter in adapter_ids:
                    if ('{:04X}'.format(port.vid), '{:04X}'.format(port.pid)) == adapter_ids[adapter]:
                        if self.debug:
                            print(f'Found supported {port.manufacturer} adapter {adapter} on {port.device}')
                        # assume last com port found, multiple PSUs not supported (yet!)
                        if self.com_port is None or port.device > self.com_port:
                            self.com_port = port.device

        if self.com_port is None:
            raise OSError('PSU com port adapter not found')

        if self.debug:
            print(f'Assuming PSU on {self.com_port}')

        return self.com_port

    def write(self, address, value):
        rr = self.pymc.write_register(address.value, value, unit=self.slaveId)
        if rr.isError() and self.debug:
            print(address.name, rr.message)

    def read(self, address, len=1):
        rr = self.pymc.read_holding_registers(address.value, len, unit=self.slaveId)

        if rr.isError():
            if self.debug:
                print(address.name, rr.message)
            return None

        return rr.registers[0]

    def read(self, address, len=1):
        rr = self.pymc.read_holding_registers(address.value, len, unit=self.slaveId)

        if rr.isError():
            if self.debug:
                print(address.name, rr.message)
            return None

        return rr.registers[0]

    @property
    def current(self):
        return self.read(PSU.Registers.CURRENT_READ)/100

    @current.setter
    def current(self, amps):
        self.write(PSU.Registers.CURRENT_WRITE, int(round(amps*100)))

    @property
    def voltage(self):
        return self.read(PSU.Registers.VOLTAGE_READ)/100

    @voltage.setter
    def voltage(self, volts):
        self.write(PSU.Registers.VOLTAGE_WRITE, int(round(volts*100)))

    @property
    def output(self):
        return False if self.read(PSU.Registers.OUTPUT_READ) == 0 else True

    @output.setter
    def output(self, on):
        self.write(PSU.Registers.OUTPUT_WRITE, int(on))


if __name__ == '__main__':
    # if called directly just report current state of PSU without changing anything
    psu = PSU(slaveId=0x1, debug=True)

    print(f'Output={psu.output}')
    print(f'Voltage={psu.voltage}V')
    print(f'Current={psu.current}A')
    
