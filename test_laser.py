import unittest
from unittest.mock import Mock
from laser_control import Laser, LaserCommandError, LaserStatusResponse

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

    def test_constants(self):
        """Ensures that the constants/enums set for energy modes and pulse modes are correct according to the user manual."""
        assert Laser.MANUAL_ENERGY == 0
        assert Laser.LOW_ENERGY == 1
        assert Laser.HIGH_ENERGY == 2

        assert Laser.CONTINUOUS == 0
        assert Laser.SINGLE_SHOT == 1
        assert Laser.BURST == 2

    def test_send_command(self):
        """Tests Laser._send_command, feeds in a mock serial object. Checking to make sure that write is called and that it returns the reponse we give it."""
        serial_mock = Mock()

        serial_mock.read_until = Mock(return_value=b"OK\r")
        serial_mock.write = Mock()

        l = Laser()
        with self.assertRaises(ConnectionError):
            l._send_command("HELLO THERE") # This should throw an exception because we have not connected it to a serial object.

        l._ser = serial_mock
        l.connected = True
        assert l._send_command("HELLO WORLD") == b"OK\r" # Ensure that we are returning the serial response
        serial_mock.write.assert_called_once_with(";LA:HELLO WORLD\r".encode("ascii")) # Ensure that the correct command format is being used

    def test_arm_command(self):
        """Tests Laser.arm(), should return True because we are feeding it a nominal response, and this should result in serial.write being called with the correct command"""
        serial_mock = Mock()
        serial_mock.read_until = Mock(return_value=b"OK\r")
        serial_mock.write = Mock() # NOTE: Major difference from pyserial class, does not return the number of bytes written.

        l = Laser()

        # Connect our laser to our mock serial
        l._ser = serial_mock
        l.connected = True

        # Now check the arm command
        assert l.arm() == True
        serial_mock.write.assert_called_once_with(";LA:EN 1\r".encode("ascii"))

    def test_disarm_command(self):
        """Tests Laser.disarm(), should return True because we are feeding it a nominal response, and this should result in serial.write being called with the correct command"""
        serial_mock = Mock()
        serial_mock.read_until = Mock(return_value=b"OK\r")
        serial_mock.write = Mock() # NOTE: Major difference from pyserial class, does not return the number of bytes written.

        l = Laser()

        # Connect our laser to our mock serial
        l._ser = serial_mock
        l.connected = True

        # Now check the arm command
        assert l.disarm() == True
        serial_mock.write.assert_called_once_with(";LA:EN 0\r".encode("ascii"))

    def test_status_class(self):
        """Tests to make sure the LaserStatusResponse class parses response strings correctly."""
        s = LaserStatusResponse(b'3075\r') # This example is pulled from the user manual
        assert s.ready_to_enable
        assert s.ready_to_fire
        assert s.laser_enabled
        assert s.laser_active
        assert not s.high_power_mode
        assert not s.low_power_mode
        assert not s.resonator_over_temp
        assert not s.electrical_over_temp
        assert not s.external_interlock

    def test_diode_trigger_command(self):
        """Tests Laser.set_diode_trigger, feeds in a mock serial object. Makes sure that the correct data is written and that the properties of the class are changed."""
        serial_mock = Mock()

        serial_mock.read_until = Mock(return_value=b"OK\r")
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

        serial_mock.read_until = Mock(return_value=b"?1") # Make sure we return False is the laser returns an error
        serial_mock.write = Mock()

        with self.assertRaises(LaserCommandError):
            l.set_diode_trigger(0)

        serial_mock.write.assert_called_once_with(";LA:DT 0\r".encode("ascii"))
        assert l.diodeTrigger == 1 # This value should have NOT changed since this command failed.

    def test_pulse_width_command(self):
        """Tests Laser.set_pulse_width, feeds in a mock serial object. Makes sure that the correct data is written and that the properties of the class are changed."""
        serial_mock = Mock()

        serial_mock.read_until = Mock(return_value=b"OK\r")
        serial_mock.write = Mock()

        l = Laser()
        l._ser = serial_mock
        l.connected = True

        with self.assertRaises(ValueError):
            l.set_pulse_width(0) # Valid values positive, non-zero numbers

        with self.assertRaises(ValueError):
            l.set_pulse_width(-20) # Valid values positive numbers

        with self.assertRaises(ValueError):
            l.set_pulse_width("this is not an integer")

        assert l.set_pulse_width(0.1)
        serial_mock.write.assert_called_once_with(";LA:DW 0.1\r".encode("ascii"))
        assert l.pulseWidth == 0.1

        serial_mock.read_until = Mock(return_value=b"?1") # Make sure we return False is the laser returns an error
        serial_mock.write = Mock()

        with self.assertRaises(LaserCommandError):
            l.set_pulse_width(0.2)

        serial_mock.write.assert_called_once_with(";LA:DW 0.2\r".encode("ascii"))
        assert l.pulseWidth == 0.1 # This value should have NOT changed since this command failed.

    def test_energy_mode_command(self):
        """Tests Laser.set_energy_mode, feeds in a mock serial object. Makes sure that the correct data is written and that the properties of the class are changed."""
        serial_mock = Mock()

        serial_mock.read_until = Mock(return_value=b"OK\r")
        serial_mock.write = Mock()

        l = Laser()
        l._ser = serial_mock
        l.connected = True

        with self.assertRaises(ValueError):
            l.set_energy_mode(4) # Valid values are 0 to 2

        with self.assertRaises(ValueError):
            l.set_energy_mode("this is not an integer")

        assert l.set_energy_mode(1)
        serial_mock.write.assert_called_once_with(";LA:EM 1\r".encode("ascii"))
        assert l.energyMode == 1

        serial_mock.read_until = Mock(return_value=b"?1") # Make sure we return False is the laser returns an error
        serial_mock.write = Mock()

        with self.assertRaises(LaserCommandError):
            l.set_energy_mode(2)

        serial_mock.write.assert_called_once_with(";LA:EM 2\r".encode("ascii"))
        assert l.energyMode == 1 # This value should have NOT changed since this command failed.

    def test_diode_current_command(self):
        """Tests Laser.set_diode_current, feeds in a mock serial object. Makes sure that the correct data is written and that the properties of the class are changed."""
        serial_mock = Mock()

        serial_mock.read_until = Mock(return_value=b"OK\r")
        serial_mock.write = Mock()

        l = Laser()
        l._ser = serial_mock
        l.connected = True

        with self.assertRaises(ValueError):
            l.set_diode_current(0)

        with self.assertRaises(ValueError):
            l.set_diode_current(-5)

        with self.assertRaises(ValueError):
            l.set_diode_current("this is not an integer")

        # Reset the energy mode to test that it gets switched to manual (0)
        l.energyMode = 2

        assert l.set_diode_current(100)
        serial_mock.write.assert_called_once_with(";LA:DC 100\r".encode("ascii"))
        assert l.diodeCurrent == 100
        assert l.energyMode == 0

        serial_mock.read_until = Mock(return_value=b"?1") # Emulate the laser returning a failure code.
        serial_mock.write = Mock()

        # Reset the energy mode to test that it DOES NOT gets switched to manual (0)
        l.energyMode = 2

        with self.assertRaises(LaserCommandError):
            l.set_diode_current(50)
        serial_mock.write.assert_called_once_with(";LA:DC 50\r".encode("ascii"))
        assert l.diodeCurrent == 100 # This value should have NOT changed since this command failed.
        assert l.energyMode == 2 # This also should not have changed because the command failed.


if __name__ == "__main__":
    unittest.main()
