import unittest
from unittest.mock import Mock
import FakeSerialLaser as fake_serial
import serial
import serial.tools.list_ports
import laser_control
import time
import threading

class TestSerial(unittest.TestCase):
    """
    This class is meant to use unittesting to test the fake laser serial code and have laser_control interact with fake laser serial.

    Fake laser serial is setup as an object called: self._ser
    Laser control is setup as an object called: self.controller

    I hope the names of these functions explain what they're doing, but if some are unclear please lmk and I'll update this with documentation.
    """
    def setUp(self):
        self._ser = fake_serial.Serial('COM1', 9600)
        self.controller = laser_control.Laser()

    def tearDown(self):
        pass
    
    @unittest.skip("Bugs")
    def test_connection(self):
        port_number = 'COM1'
        baud_rate = 115200

        self.controller.connect(port_number, baud_rate)
        assert self.controller._ser is not None
        assert self.controller._ser.port == 'COM1'

    
    #@unittest.skip('skip')
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
        #self.assertEqual(self._ser.readline(), ('{}\r'.format(self._ser._repititionRate)).encode('ascii'))

    #@unittest.skip("I don't know")
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

        self._ser.write(b';LA:PE 2.5\r')
        self._ser.write(b';LA:FL 1\r')
        self._ser.write(b';LA:SS?\r')
        self.assertEqual(self._ser.readline(), b'OK\r')
        self.assertEqual(self._ser.readline(), b'OK\r')
        self.assertEqual(self._ser.readline(), b'3075\r')

        assert self._ser._pulsePeriod == 2.5
        time.sleep(self._ser._pulsePeriod+1)

        self._ser.write(b';LA:SS?\r')
        self.assertEqual(self._ser.readline(), b'3073\r')

        self._ser.write(b';LA:EN 0\r')
        self.assertEqual(self._ser.readline(), b'OK\r')

        self._ser.write(b';LA:SS?\r')
        self.assertEqual(self._ser.readline(), b'1024\r')

    #@unittest.skip('skip')
    def test_reset(self):
        self._ser.write(b';LA:RS\r')
        self.assertEqual(self._ser.readline(), b'OK\r')

    #@unittest.skip('skip')
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

    #@unittest.skip('skip')
    def test_send_command(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()
        self.assertEqual(self.controller._send_command('SS?'), b'1024\r')

    #@unittest.skip("Arm/Disarm Function Contain Bugs")
    def test_arm(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()
        self.assertEqual(self.controller.arm(), True)
        time.sleep(8.1)
        self.assertEqual(self.controller.disarm(), True)

    #@unittest.skip("Comparing to empty string")
    def test_fire(self):
        """
        This function serves to check that fire laser is being called correctly
        """

        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.assertEqual(self.controller._send_command('SS?'), b'1024\r')
        self.controller.arm()
        
        time.sleep(8.02)

        self.assertEqual(self.controller._send_command('SS?'), b'3073\r')
        self.controller.set_pulse_period(1.5)
        self.controller.fire_laser()
        self.assertEqual(self.controller._send_command('SS?'), b'3075\r')
        time.sleep(self.controller._ser._pulsePeriod)

        self.assertEqual(self.controller._send_command('SS?'), b'3073\r')
    
    #@unittest.skip("Newly revised get status")
    def test_get_status(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.assertEqual(self.controller.get_status().__str__(), '1024')

    #@unittest.skip("b'' ")
    def test_fet_temp(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.assertEqual(self.controller.fet_temp_check(), str(self.controller._ser._FETtemp))

    #@unittest.skip("b'' ")
    def test_resonator_temp(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.assertEqual(self.controller.resonator_temp_check(), str(self.controller._ser._thermistorTemp))

    #@unittest.skip("b'' ")
    def test_fet_volatage(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.assertEqual(self.controller.fet_voltage_check(), str(self.controller._ser._FETvolts))

    #@unittest.skip("b'' ")
    def test_diode_current(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.assertEqual(self.controller.diode_current_check(), str(self.controller._ser._diodeCurrent))
    
    #@unittest.skip("Something is not working with emergency stop")
    def test_emergency_stop(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.assertEqual(self.controller._send_command('SS?'), b'1024\r')

        self.assertEqual(self.controller._send_command('EN 1'), b'OK\r')
        time.sleep(9)

        self.assertEqual(self.controller._send_command('PE 2.5'), b'OK\r')
        self.assertEqual(self.controller._send_command('FL 1'), b'OK\r')
        self.assertEqual(self.controller._send_command('SS?'), b'3075\r')

        self.assertEqual(self.controller.emergency_stop(), True)
        self.assertEqual(self.controller._send_command('SS?'), b'3073\r')
    
    #@unittest.skip('skip')
    def test_set_pulseMode(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.assertEqual(self.controller._send_command('PM 2'), b'OK\r')

    #@unittest.skip('skip')
    def test_set_diodeTrigger(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.assertEqual(self.controller.set_diode_trigger(1), True)

    #@unittest.skip('skip')
    def test_bank_voltage_check(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.assertEqual(self.controller.bank_voltage_check(), float(self.controller._ser._bankVoltage))

    #@unittest.skip('skip')
    def test_controller_reset(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.assertTrue(self.controller.laser_reset())
        assert self.controller.pulseMode == self.controller._ser._pulseMODE == 0
        assert self.controller.pulsePeriod == self.controller._ser._pulsePeriod == 0
        assert self.controller.burstCount == self.controller._ser._burstCount == 10
        assert self.controller.diodeCurrent == self.controller._ser._diodeCurrent == .1
        assert self.controller.energyMode == self.controller._ser._energyMode == 0
        assert self.controller.pulseWidth == self.controller._ser._diodeWidth == 10
        assert self.controller.diodeTrigger == self.controller._ser._diodeTrigger == 0
        assert self.controller._device_address == 'LA'

    #@unittest.skip('skip')
    def test_ID(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        response = self.controller.laser_ID_check()
        self.assertIn('MicroJewel', response)

    #@unittest.skip('skip')
    def test_latched_check(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        response = self.controller.latched_status_check()
        self.assertIsInstance(response, str)

    #@unittest.skip('skip')
    def test_pulse_period(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.assertTrue(self.controller.set_pulse_period(1.7))
        assert self.controller.pulsePeriod == self.controller._ser._pulsePeriod == 1.7

        self.controller.set_pulse_period(0)
        assert self.controller.pulsePeriod == self.controller._ser._pulsePeriod == 0
        self.assertIsInstance(self.controller.pulsePeriod, float)

        self.assertTrue(self.controller.set_pulse_period(2.7))
        assert self.controller.pulsePeriod == self.controller._ser._pulsePeriod == 2.7

    #@unittest.skip("On hold till laser_fire is fixed")
    def test_sys_shot_count(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()
        self.controller._ser._systemShotCount = 0

        self.assertEqual(self.controller.system_shot_count_check(), 0)
        self.controller.arm()
        time.sleep(8.02)
        self.controller.set_pulse_period(1.5)
        self.controller.fire_laser()
        time.sleep(self.controller._ser._pulsePeriod)
        self.assertEqual(self.controller.system_shot_count_check(), 1)

    #@unittest.skip('skip')
    def test_burst(self):
        """ This also tests a > 2s burst duration """
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()
        self.controller._kicker_thread_control(0)
        self.assertTrue(self.controller._kicker_active)
        self.assertTrue(self.controller._threads[0].is_alive())

        self.controller.arm()
        time.sleep(8)
        self.controller.set_burst_count(20)
        self.controller.set_rep_rate(5)
        assert self.controller.burstDuration == 4
        self.controller.set_pulse_mode(2)
        assert self.controller.burstCount == self.controller._ser._burstCount
        assert self.controller.repRate == self.controller._ser._repetitionRate == 5
        assert self.controller.pulseMode == self.controller._ser._pulseMODE
        self.assertEqual(self.controller._send_command('SS?'), b'3073\r')
        
        self.controller.fire_laser()
        time.sleep(.2)
        assert self.controller._kicker_status == b'3075\r'
        assert len(self.controller._threads) == 2
        time.sleep(self.controller.burstDuration)
        assert self.controller._kicker_status == None
        assert len(self.controller._threads) == 1
        self.assertTrue(self.controller._threads[0].is_alive())
        time.sleep(2)
        self.controller._kicker_thread_control(1)
        self.assertFalse(self.controller._kicker_active)
        self.assertFalse(self.controller.kicker_thread.is_alive())
        self.assertEqual(len(self.controller._threads), 0)

    #@unittest.skip('skip')
    def test_kicker_control(self):
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.controller._kicker_thread_control(0)
        self.assertTrue(self.controller._kicker_active)
        time.sleep(2)
        self.controller._kicker_thread_control(1)
        self.assertFalse(self.controller._kicker_active)

    #@unittest.skip('no')
    def test_single_shot(self):
        """ This test is meant to have the laser fire for 1 shot, (based off of the rep rate (i'm assuming), so 1s / rep. rate) """
        self.controller.connected = True
        self.controller._ser = fake_serial.Serial()

        self.controller.arm()
        time.sleep(8)
        self.controller.set_rep_rate(1)
        assert self.controller._ser._repetitionRate == 1

        self.controller.set_pulse_mode(1)
        self.controller.fire_laser()
        self.assertTrue(self.controller._threads[0].is_alive())
        time.sleep((1/self.controller.repRate) + .5)
        self.assertFalse(self.controller.fireThread.is_alive())

if __name__ == '__main__':
    unittest.main()