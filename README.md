# lw-2010ec-controller
Python module for controlling Topshak/Longwei bench power supplies using USB/serial (Windows)

Voltage and current set-points can be changed, and the measured output voltage and current read back.
The output can be turned on and off.

# Example usage

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
