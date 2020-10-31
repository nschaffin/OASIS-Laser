import sys, unittest
from serial import Serial
from ujlaser.lasercontrol import Laser, LaserCommandError

laser = None
serial_conn = None

class TestSpoof(unittest.TestCase):

    def test_default_rep_rate(self):
        global laser
        self.assertEqual(laser.get_repetition_rate(), 5.0)

    def test_set_rep_rate(self):
        global laser, serial_conn
        laser.set_rep_rate(1.2)
        self.assertEqual(laser.get_repetition_rate(), 1.2)
        laser.set_rep_rate(5.0)
        self.assertEqual(laser.get_repetition_rate(), 5.0)
        
        # Testing for invalid parameters
        self.assertEqual(laser._send_command("RR -0.5"), b"?5\r\n")
        self.assertEqual(laser._send_command("RR"), b"?5\r\n")
        self.assertEqual(laser.get_repetition_rate(), 5.0)

    def test_get_rep_rate_range(self):
        global laser, serial_conn
        pass

    def test_default_burst_count(self):
        global laser, serial_conn
        self.assertEqual(laser.get_burst_count(), 31)

    def test_set_burst_count(self):
        global laser, serial_conn
        laser.set_burst_count(2)
        self.assertEqual(laser.get_burst_count(), 2)
        self.assertEqual(laser._send_command("BC -5"), b"?5\r\n")
        self.assertEqual(laser._send_command("BC 0.1"), b"?5\r\n")
        laser.set_burst_count(31)
        self.assertEqual(laser.get_burst_count(), 31)

    def test_default_diode_width(self):
        global laser
        self.assertEqual(laser.get_pulse_width(), 0.00014000)

    def test_set_diode_width(self):
        global laser
        laser.set_pulse_width(0.00020)
        self.assertEqual(laser.get_pulse_width(), 0.000200)
        self.assertEqual(laser._send_command("DW -0.001"), b"?5\r\n")
        self.assertEqual(laser._send_command("DW"), b"?5\r\n")
        laser.set_pulse_width(0.00014000)
        self.assertEqual(laser.get_pulse_width(), 0.00014000)

    def test_default_diode_current(self):
        global laser
        self.assertEqual(laser.get_diode_current(), 0.258) # This is the diode current measurement

    def test_default_fet_voltage(self):
        global laser
        self.assertEqual(laser.get_fet_voltage(), 0.000)

    def test_bad_command(self):
        global laser
        self.assertEqual(laser._send_command("RJ?"), b"?1\r\n")

    def test_missing_query(self):
        global laser
        self.assertEqual(laser._send_command("ID"), b"?6\r\n")
        self.assertEqual(laser._send_command("LS"), b"?6\r\n")
        self.assertEqual(laser._send_command("SS"), b"?6\r\n")
        self.assertEqual(laser._send_command("FV"), b"?6\r\n")
        self.assertEqual(laser._send_command("SC"), b"?5\r\n")
        self.assertEqual(laser._send_command("BV"), b"?6\r\n")
        self.assertEqual(laser._send_command("IM"), b"?6\r\n")

    def test_missing_keyword(self):
        global laser
        #Turns out that the below line is actually accepted by the laser.... weird
        #self.assertEqual(laser._send_command("DW:?"), b"?2\r\n")

        self.assertEqual(laser._send_command("DW:"), b"?5\r\n")
        #TODO: Add all the query commands that have keywords in here

    def test_disconnected_bank_voltage(self):
        global laser
        self.assertEqual(laser.get_bank_voltage(), 0.0)

    def test_diode_trigger(self):
        global laser
        self.assertEqual(laser.get_diode_trigger(), 0)
        laser.set_diode_trigger(1)
        self.assertEqual(laser.get_diode_trigger(), 1)
        laser.set_diode_trigger(0)
        self.assertEqual(laser.get_diode_trigger(), 0)
        self.assertEqual(laser._send_command("DT"), b"?5\r\n")
        self.assertEqual(laser._send_command("DT 3"), b"?5\r\n")
        self.assertEqual(laser._send_command("DT 0.3"), b"?5\r\n")
        self.assertEqual(laser._send_command("DT -1"), b"?5\r\n")
        self.assertEqual(laser.get_diode_trigger(), 0)

    def test_fet_temperature(self):
        global laser
        t = laser.get_fet_temp()
        assert type(t) == float
        assert t > 0 # I'm gonna reasonably assume this is a sane value
        assert t < 130
        self.assertEqual(laser._send_command("FT:MAX?"), b"125.000\r\n")
        self.assertEqual(laser._send_command("FT 1"), b"?6\r\n")
        self.assertEqual(laser._send_command("FT"), b"?6\r\n")
        self.assertEqual(laser._send_command("FT "), b"?6\r\n")
        
    def test_pulse_mode(self):
        global laser
        self.assertEqual(laser.get_pulse_mode(), 0)
        laser.set_pulse_mode(1)
        self.assertEqual(laser.get_pulse_mode(), 1)
        laser.set_pulse_mode(2)
        self.assertEqual(laser.get_pulse_mode(), 2)
        laser.set_pulse_mode(0)
        self.assertEqual(laser.get_pulse_mode(), 0)
        self.assertEqual(laser._send_command("PM"), b"?5\r\n")
        self.assertEqual(laser._send_command("PM "), b"?5\r\n")
        # Don't use the below test case... for some reason it works, but the docs says it shouldn't...
        #self.assertEqual(laser._send_command("PM 3"), b"?5\r\n")
        self.assertEqual(laser._send_command("PM 8"), b"?5\r\n")
        self.assertEqual(laser._send_command("PM 0.8"), b"?5\r\n")
        self.assertEqual(laser.get_pulse_mode(), 0)

if __name__ == "__main__":
    serial_port = "COM2"
    if len(sys.argv) > 1:
        serial_port = sys.argv[1]
        del sys.argv[1]
    
    print("Attempting to connect to serial port " + serial_port)
    serial_conn = Serial(serial_port, 115200)
    if not serial_conn:
        print("Failed to connect to serial port, exiting...")
        exit()

    laser = Laser()
    laser.connect(serial_conn)

    unittest.main()
