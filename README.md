# Topshak LW-3010EC Bench Power supply control module
Python module for controlling USB connected Topshak/Longwei bench power supplies under Windows and Linux.

It can change the voltage and current set-points as well as measure the momentary output voltage and current.
The output can also be turned on and off.

This module can either be imported into other python code or used directly from the command line, EG:

```
./LW3010EC.py --voltage 12 --current 0.8 --on
Voltage set to 12.0V
Current set to 0.8A
Output enabled
```

# Dependencies

`python -m pip install click pyserial pymodbus`

Tested against Python 3.10.4

# Example usage as a module

```
from LW3010EC import PSU
from time import sleep

psu = PSU()

psu.output = False
psu.voltage = 3.3
psu.current = 0.7
psu.output = True

sleep(2)

print(f'Output={psu.output}')
print(f'Voltage={psu.voltage}V')
print(f'Current={psu.current}A')
```

Expected output:
```
Output=True
Voltage=3.31V
Current=0.0A
```

Both voltage and current are reported as 0.0 when the output is turned off.

Note that when the class is created with `psu = PSU()` there is no need to specify the COM port, it will search for it by device VID/PID.
These power supplies integrate the CH340 USB/serial device, if you have more than one CH340 device you may need to tweak the python.
