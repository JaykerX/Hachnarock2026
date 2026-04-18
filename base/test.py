import serial
import serial.tools.list_ports
import time
import random

def find_device():
    ports = serial.tools.list_ports.comports()

    for p in ports:
        if "USB" in p.description or "CDC" in p.description:
            print("Found device:", p.device, p.description)
            return p.device

    return None

port = find_device()

if port is None:
    print("No device found")
    exit(1)

ser = serial.Serial(port, 115200, timeout=1)

time.sleep(2)


while True:
    val = random.random()
    msg = f"{val:.3f}\n"

    ser.write(msg.encode())
    #print("Sent:", msg.strip())

    time.sleep(0.05)