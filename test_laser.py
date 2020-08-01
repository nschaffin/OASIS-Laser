import unittest
from unittest.mock import Mock
from laser_control import Laser

class TestLaserCommands(unittest.TestCase):

    def test_not_connected(self):
        """Laser object should raise a ConnectionError if __send_command is sent without being connected to a serial device."""
        l = Laser()
        assert l.connected == False
        assert l._ser == None
        with self.assertRaises(ConnectionError):
            l.check_armed()
        with self.assertRaises(ConnectionError): # try two different commands for good measure
            l.get_status()

    def test_device_address(self):
        """The only device address listed in the microjewel manual is 'LA'. Make sure this is set correctly in the code."""
        l = Laser()
        assert l._device_address == "LA"

    def test_arm_command(self):
        """Tests Laser.arm(), should return True because we are feeding it a nominal response, and this should result in serial.write being called with the correct command"""
        serial_mock = Mock()
        serial_mock.read_until = Mock(return_value="OK\r")
        serial_mock.write = Mock() # NOTE: Major difference from pyserial class, does not return the number of bytes written.

        l = Laser()

        # Connect our laser to our mock serial
        l._ser = serial_mock
        l.connected = True

        # Now check the arm command
        assert l.arm() == True
        serial_mock.write.assert_called_once_with(";LA:EN 1\r".encode("ascii"))

    def test_send_command(self):
        """Tests Laser._send_command, feeds in a mock serial object. Checking to make sure that write is called and that it returns the reponse we give it."""
        serial_mock = Mock()

        serial_mock.read_until = Mock(return_value="OK\r")
        serial_mock.write = Mock()

        l = Laser()
        with self.assertRaises(ConnectionError):
            l._send_command("HELLO THERE") # This should throw an exception because we have not connected it to a serial object.
        
        l._ser = serial_mock
        l.connected = True
        assert l._send_command("HELLO WORLD") == "OK\r" # Ensure that we are returning the serial response
        serial_mock.write.assert_called_once_with(";LA:HELLO WORLD\r".encode("ascii")) # Ensure that the correct command format is being used

    def test_diode_trigger_command(self):
        """Tests Laser.set_diode_trigger, feeds in a mock serial object. Makes sure that the correct data is written and that the properties of the class are changed."""
        serial_mock = Mock()

        serial_mock.read_until = Mock(return_value="OK\r")
        serial_mock.write = Mock()

        l = Laser()
        l._ser = serial_mock
        l.connected = True

        with self.assertRaises(ValueError):
            l.set_diode_trigger(6)

        with self.assertRaises(ValueError):
            l.set_diode_trigger("this is not an integer")

        assert l.set_diode_trigger(1)
        serial_mock.write.assert_called_once_with(";LA:DT 1\r".encode("ascii"))
        assert l.diodeTrigger == 1

        serial_mock.read_until = Mock(return_value="?1") # Make sure we return False is the laser returns an error
        serial_mock.write = Mock()
        
        assert not l.set_diode_trigger(0)
        serial_mock.write.assert_called_once_with(";LA:DT 0\r".encode("ascii"))
        assert l.diodeTrigger == 1 # This value should have NOT changed since this command failed.


if __name__ == "__main__":
    unittest.main()