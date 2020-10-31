import sys
from time import sleep
from serial import Serial
from ujlaser.lasercontrol import Laser, LaserCommandError

serial_port = "COM3"

if len(sys.argv) > 1:
    serial_port = sys.argv[1]

print("Connecting to serial port " + serial_port)
s = Serial(serial_port, 115200)
running = True
while running:
    cmd = input(";LA:")
    if cmd == "exit" or cmd == "EXIT" or cmd == "quit" or cmd == "CMD":
        break
    r = s.write((";LA:" + cmd + "\r\n").encode("ascii"))
    sleep(0.3)
    if s.in_waiting:
        print(s.read_until())
s.close() 
