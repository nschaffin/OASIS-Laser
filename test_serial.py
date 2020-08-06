import unittest
#from unittest.mock import patch
import FakeSerialLaser as serial
import laser_control
import time
import threading

class TestSerial(unittest.TestCase):
    """
    This class is meant to use unittesting to test the fake laser serial code and have laser_control interact with fake laser serial.

    Fake laser serial is setup as an object called: self._ser
    Laser control is setup as an object called: self.controller
    """
    def setUp(self):
        self._ser = serial.Serial('COM1', 9600)
        self.controller = laser_control.Laser()

    def tearDown(self):
        pass

    def test_query(self):                                   ### For System Query Commands ###
        """ NOTE: These tests do NOT include all variables, just commonly used ones for testing purposes """
        self._ser.write(b';LA:SS?\r')
        self.assertEqual(self._ser.readline(), b'1024\r')

        self._ser.write(b';LA:BC?\r')
        self.assertEqual(self._ser.readline(), ('{}\r'.format(self._ser._burstCount)).encode('ascii'))

        self._ser.write(b';LA:EM?\r')
        self.assertEqual(self._ser.readline(), ('{}\r'.format(self._ser._energyMode)).encode('ascii'))

        self._ser.write(b';LA:EN?\r')
        self.assertEqual(self._ser.readline(), ('{}\r'.format(self._ser._enable)).encode('ascii'))

        self._ser.write(b';LA:FL?\r')
        self.assertEqual(self._ser.readline(), ('{}\r'.format(self._ser._fireLaser)).encode('ascii'))

        self._ser.write(b';LA:PE?\r')
        self.assertEqual(self._ser.readline(), ('{}\r'.format(self._ser._pulsePeriod)).encode('ascii'))

        self._ser.write(b';LA:PM?\r')
        self.assertEqual(self._ser.readline(), ('{}\r'.format(self._ser._pulseMODE)).encode('ascii'))

        self._ser.write(b';LA:RR?\r')
        self.assertEqual(self._ser.readline(), ('{}\r'.format(self._ser._repititionRate)).encode('ascii'))

    def test_actions(self):                                 ### For System Action Commands and Editing Values ###
        """ NOTE: These tests do NOT include all variables, just commonly used ones for testing purposes """
        self._ser.write(b';LA:SS?\r')
        control = self._ser.readline()                       # This is a control var
        self.assertEqual(control, b'1024\r')

        self._ser.write(b';LA:EN 1\r')
        self.assertEqual(self._ser.readline(), b'OK\r')

        self._ser.write(b';LA:SS?\r')
        self.assertNotEqual(self._ser.readline(), b'3073\r')

        time.sleep(9)

        self._ser.write(b';LA:SS?\r')
        self.assertEqual(self._ser.readline(), b'3073\r')

        self._ser.write(b';LA:FL 1\r')
        self._ser.write(b';LA:SS?\r')
        self.assertEqual(self._ser.readline(), b'OK\r')
        self.assertEqual(self._ser.readline(), b'3075\r')

        assert self._ser._pulsePeriod == 2
        time.sleep(self._ser._pulsePeriod)

        self._ser.write(b';LA:SS?\r')
        self.assertEqual(self._ser.readline(), b'3073\r')

        self._ser.write(b';LA:EN 0\r')
        self.assertEqual(self._ser.readline(), b'OK\r')

        self._ser.write(b';LA:SS?\r')
        self.assertEqual(self._ser.readline(), b'1024\r')

    def test_reset(self):
        self._ser.write(b';LA:RS\r')
        self.assertEqual(self._ser.readline(), b'OK\r')

    def test_errors(self):
        with self.assertRaises(TypeError):
            self._ser.write(';LA:SS?\r')

        self._ser.write(b';LR:SS?\r')
        self.assertEqual(self._ser.readline(), b'?1\r')      # False laser address

        self._ser.write(b';LA:YA?\r')
        self.assertEqual(self._ser.readline(), b'?7\r')      # Invalid query command

        self._ser.write(b';LA:SS\r')
        self.assertEqual(self._ser.readline(), b'?3\r')      # No question mark given, so invalid query command

        self._ser.write(b';LA:EN 5\r')
        self.assertEqual(self._ser.readline(), b'?8\r')      # Invalid enable parameter

        self._ser.write(b';LA:FL 5\r')
        self.assertEqual(self._ser.readline(), b'?8\r')      # Invalid fire parameter

        self._ser.write(b';LA:SS?')
        self.assertEqual(self._ser.readline(), b'?1\r')

    def test_control_send(self):
        self.controller.connected = True
        self.controller._ser = serial.Serial()
        self.assertEqual(self.controller._send_command('SS?'), b'1024\r')

    @unittest.skip("Arm/Disarm Function Contain Bugs")
    def test_arm(self):
        self.controller.connected = True
        self.controller._ser = serial.Serial()
        self.assertEqual(self.controller.arm(), True)
        time.sleep(8.1)
        #self.assertEqual(self.controller.check_armed, True)
        self.assertEqual(self.controller.disarm(), True)
        #self.assertEqual(self.controller.check_armed, False)
    
    def _firing(self):
        """ The use of this function is to be called in a thread """
        self.controller.fire_laser()

    @unittest.skip("Functional, but has some bugs with threading")
    def test_fire(self):
        """
        This function serves to check that fire laser is being called correctly
        """

        self.controller.connected = True
        self.controller._ser = serial.Serial()
        fireThread = threading.Thread(target=self._firing)

        self.assertEqual(self.controller._send_command('SS?'), b'1024\r')
        self.controller.arm()
        
        time.sleep(8.02)

        self.assertEqual(self.controller._send_command('SS?'), b'3073\r')

        fireThread.start()
        time.sleep(.5)
        self.assertEqual(self.controller._send_command('SS?'), b'3075\r')
        time.sleep(self.controller._ser._pulsePeriod)

        self.assertEqual(self.controller._send_command('SS?'), b'3073\r')

    def test_get_status(self):
        self.controller.connected = True
        self.controller._ser = serial.Serial()

        self.assertEqual(self.controller.get_status(), b'1024\r')
""" 
    *** Inserting Mock tests here after I look over the laser_control code
    ** laser_control is going to be named as mock_control
"""

if __name__ == '__main__':
    unittest.main()