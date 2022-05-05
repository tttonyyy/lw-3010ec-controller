# lw-2010ec-controller
Python module for controlling Topshak/Longwei bench power supplies using USB/serial (Windows)

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
