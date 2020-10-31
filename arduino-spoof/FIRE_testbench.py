import unittest
import sys
from time import sleep
from serial import Serial
from ujlaser.lasercontrol import Laser, LaserCommandError

laser = None
serial_conn = None

class FireTest(unittest.TestCase):
    def test_connection(self):
        global laser
        self.assertEqual(laser.get_laser_ID(), b"QC,MicroJewel,08130,1.0.9")

    def test_arm(self):
        global laser
        self.assertEqual(laser.is_armed(), False)
        laser.arm()
        self.assertEqual(laser.is_armed(), True)
        laser.disarm()
        self.assertEqual(laser.is_armed(), False)

    def test_disarmed_fire(self):
        global laser
        self.assertEqual(laser.is_armed(), False)
        self.assertEqual(laser._send_command("FL 1"), b"?8\r\n")

    def test_armed_fire(self):
        global laser
        i = input("Performing live fire test, continue? [YES/NO]  ")
        if i != "YES":
            print("Response was not YES, skipping...")
            return
        laser.set_pulse_mode(2)
        laser.set_burst_count(10)
        laser.set_rep_rate(2)
        # Laser should be firing for 5 seconds (10x bursts, 2x bursts per second)
        laser.arm()
        self.assertEqual(laser.is_armed(), True)
        laser.fire()
        self.assertEqual(laser.is_firing(), True)

    def test_fire_timing(self):
        pass

if __name__ == "__main__":
    serial_port = "COM3"
    if len(sys.argv) > 1:
        serial_port = sys.argv[1]
        del sys.argv[1]

    print("WARNING")
    print("This program will issue the fire command to the connected serial device!!!")
    print("Exit this program if the actual laser driver is connected!")
    
    done = False
    while not done:
        p = input("Continue connecting to " + serial_port + "? [YES/NO]  ")
        if p != "YES":
            print("You did not enter YES, exiting... (casesensitive)")
            exit()
        else:
            done = True

    serial_conn = Serial(serial_port, 115200)
    laser = Laser()
    laser.connect(serial_conn)
    
    if done:
        unittest.main()
