import threading
import time

class Serial:
    """
    The Serial class is meant to be used inplace of the Serial() call used in laser_control.
    """
    def __init__(self, port=None,baudrate=9600,parity='PARITY_NONE',stopbits='STOPBITS_ONE',timeout=None,xonxoff=False,rtscts=False,write_timeout=None,dsrdtr=False,inter_byte_timeout=None,exclusive=None):
        """
        NOTE: All these 'serial' values passed through the init are just here for placeholding. I cannot literally emulate something such as a baud rate in this emulator.

        This is where all of the placeholder serial commands and the laser variable _initializeVars() function get called to set up all class variables.
        """
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.xonxoff = xonxoff
        self.rtscts = rtscts
        self.write_timeout = write_timeout
        self.dsrdtr = dsrdtr
        self.inter_byte_timeout = inter_byte_timeout
        self.exclusive = exclusive
        self._isOpen = True
        self._initializeVars()
        self._systemShotCount = 0
        
    def isOpen(self):
        """ Checks if fake serial port is open"""
        return self._isOpen

    def open(self):
        """ Opens fake serial port """
        self._isOpen = True
        return None

    def close(self):
        """ Closes fake serial port """
        self._isOpen = False
        return None

    def clearSerial(self):
        """
        This is a debugging only command that is not included in pyserial. The purpose of this function is to clear out a clogged 'RX port' (basically meaning clearing all of the data that our fake serial has recieved)
        """
        self._sendData = ''
        return None


    def write(self, command):
        """
        The write function is meant to do most of the heavy lifting in this class. 
        It is meant to mimic the write function from pyserial, but it has been heavily modified to process incoming laser commands.

        There will be a comment listed around every significant line or lines of code.
        This comment will give a basic understaning of what is occuring in the code, and what laser values the line(s) are modifying.
        """
        # Here I need to implement all of the stuff
        if self._isOpen == False:                                               # You don't have to open the port anymore
            raise PortError('Port Not Opened')
        
        if type(command) == bytes:
            commandDecoded = str((repr(command.decode('ascii')))).replace("u'", "").replace("'", "")      # Lines 62-66 check that the incoming command is indeed in bytes (The u' was something i had to replace since I was getting an issue on mac?)
            print("Laser recieved command: {}".format(commandDecoded))          # If it's in bytes, we will decode the command in ascii and get the raw representation of the ascii string
        else:
            raise TypeError('{} is not a byte format'.format(type(command)))

        strip = commandDecoded.split(':', 1)
        strippedCMD = []
        strippedCMD.append(strip[0])
        try:
            newlineIndex = strip[1].index("\\n")
        except:
            newlineIndex = -1
            
        try:
            carriageReturnIndex = strip[1].index("\\r")                         # Lines 68-95 focus on manipulation of the raw string we just recieved
        except:                                                                 # In this block of code, we extract a list of the following things:
            carriageReturnIndex = -1                                            # strippedCMD = [laser address, command]
        
        if carriageReturnIndex != -1 and newlineIndex == -1:
            strip = strip[1].split("\\r")
            strippedCMD.append(strip[0])
            
        elif carriageReturnIndex == -1 and newlineIndex != -1:
            strip = strip[1].split("\\n")
            strippedCMD.append(strip[0])
            
        elif carriageReturnIndex != -1 and newlineIndex != -1:
            strip = strip[1].replace('\\r', '').replace('\\n', '')
            strippedCMD.append(strip)

        else:
            self._sendBytes('?1')                                   # Command not recognized
            return None

        # Check for valid command
        if strippedCMD[0] == ';LA':                                         # Making sure proper laser address is listed
            query = strippedCMD[1].find('?')
            
            if query != -1:                                                 #---Query Commands-------------------------------------------------------------------------------
                queryList = strippedCMD[1].split('?')
                queryCMD = queryList[0]
            
                if queryCMD == 'BC':                                        # Burst Count - Retursn number of shots to be fired when firing mode is set to burst (default is 10)
                    self._sendBytes(str(self._burstCount))

                elif queryCMD == 'BV':                                      # Bank Voltage - Returns current diode driver bank voltage
                    self._sendBytes(str(self._bankVoltage))

                elif queryCMD == 'DT':                                      # Diode Trigger Mode - Returns trigger value (0 = internal, 1 = external)
                    self._sendBytes(str(self._diodeTrigger))

                elif queryCMD == 'DC':                                      # Diode Current - Returns the amperage value for diode current
                    self._sendBytes(str(self._diodeCurrent))

                elif queryCMD == 'DC:MIN':                                  # Returns Min Diode Current Value
                    self._sendBytes(str(self._diodeCurrentMIN))

                elif queryCMD == 'DC:MAX':                                  # Returns Max Diode Current Value
                    self._sendBytes(str(self._diodeCurrentMAX))

                elif queryCMD == 'DW':                                      # Diode Width - Returns the diode pulse width
                    self._sendBytes(str(self._diodeWidth))

                elif queryCMD == 'DW:MIN':                                  # Min Diode Width
                    self._sendBytes(str(self._diodeWidthMIN))

                elif queryCMD == 'DW:MAX':                                  # Max Diode Width
                    self._sendBytes(str(self._diodeWidthMAX))

                elif queryCMD == 'EC':                                      # Echo (not sure what this does) - Returns if echo characters are on or off (0 = off, 1 = on)
                    self._sendBytes(str(self._echo))

                elif queryCMD == 'EM':                                      # Energy Mode - Current power mode on laser (0 = manual, 1 = low power, 2 = high power)
                    self._sendBytes(str(self._energyMode))

                elif queryCMD == 'EN':                                      # Enable - Returns armed state value (0 = disabled, 1 = enabled)
                    self._sendBytes(str(self._enable))

                elif queryCMD == 'FL':                                      # Fire Laser - Returns laser state value (0 = laser inactive, 1 = laser active)
                    self._sendBytes(str(self._fireLaser))

                elif queryCMD == 'FT':                                      # FET Tempurature - Returns temp. in degrees Celsius
                    self._sendBytes(str(self._FETtemp))

                elif queryCMD == 'FT:MAX':                                  # Returns Max FET Tempurature
                    self._sendBytes(str(self._FETtempMAX))

                elif queryCMD == 'FV':                                      # Returns FET Voltage
                    self._sendBytes(str(self._FETvolts))

                elif queryCMD == 'ID':                                      # Returns connected laser device ID
                    self._sendBytes(str('QC,MicroJewel,00101,1.0-0.0.0.8'))

                elif queryCMD == 'IM':                                      # Returns Diode Current Measurement - in Amps
                    self._sendBytes(str(self._currentMeasurement))

                elif queryCMD == 'LS':                                      # Latched Status - Returns latched system status
                    self._sendBytes(str(self._latchedStatus))

                elif queryCMD == 'PE':                                      # Pulse Period - Returns the current set pulse period
                    self._sendBytes(str(self._pulsePeriod))

                elif queryCMD == 'PE:MIN':                                  # Pulse Period Min - Returns the minimum pulse period allowed
                    self._sendBytes(str(self._pulsePeriodMIN))

                elif queryCMD == 'PE:MAX':                                  # Pulse Period Max - Returns the maximum pulse period allowed
                    self._sendBytes(str(self._pulsePeriodMAX))

                elif queryCMD == 'PM':                                      # Pulse Mode - Returns the current set pulse mode (0 = continuous, 1 = single shot, 2 = burst)
                    self._sendBytes(str(self._pulseMODE))

                elif queryCMD == 'RC':                                      # Recall Settings - Returns settings from user bin 1-6. 0 = recall factory defaults
                    self._sendBytes(str(self._recallSettings))

                elif queryCMD == 'RR':                                      # Repitition Rate - Returns the current repitition rate (default = 1 Hz)
                    self._sendBytes(str(self._repititionRate))

                elif queryCMD == 'RR:MIN':                                  # Repitition Rate Min - Returns minimum allowed repitition rate (1 Hz)
                    self._sendBytes(str(self._repititionRateMIN))

                elif queryCMD == 'RR:MAX':                                  # Repitition Rate Max - Returns maximum allowed repititon rate (5 Hz)
                    self._sendBytes(str(self._repititionRateMAX))

                elif queryCMD == 'SC':                                      # System Shot Count - Returns the number of shots stored on the system since factory build
                    self._sendBytes(str(self._systemShotCount))

                elif queryCMD == 'SS':                                      # System Status - Returns a 16 bit decimal value relaying information on the laser's current state
                    self._HPM == '0'
                    decimal = self._packingSSBinary()
                    self._sendBytes(decimal)
                    self._HPM == '1'

                elif queryCMD == 'SV':                                      # Save Settings - Returns user save settings bin 1-6
                    self._sendBytes(str(self._saveSettings))

                elif queryCMD == 'TR':                                      # Resonator Thermistor Tempurature - Returns temp. in degrees Celsius
                    self._sendBytes(str(self._thermistorTemp))

                elif queryCMD == 'TR:MIN':                                  # Resonator Thermistor Tempurature Min - Returns minimum temp.
                    self._sendBytes(str(self._thermistorTempMIN))

                elif queryCMD == 'TR:MAX':                                  # Resonator Thermistor Tempurature Max - Returns maximum temp.
                    self._sendBytes(str(self._thermistorTempMAX))

                elif queryCMD == 'UC':                                      # User Shot Count - Returns user shot count value
                    self._sendBytes(str(self._userShotCount))

                else:
                    self._sendBytes('?7')                           # Error Code for invalid query command



            elif len(strippedCMD[1].split()) == 2:                          #---Action Commands------------------------------------------------------------------------------
                actionCMD = strippedCMD[1].split()
                if actionCMD[0] == 'BC':                                    # Burst Count - Allows you to edit the laser's burst count
                    if 1 <= int(actionCMD[1]) <= 65535:
                        self._burstCount = int(actionCMD[1])
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?5')                       # Invalid parameter

                elif actionCMD[0] == 'DC':                                  # Diode Current - Allows you to edit the laser's diode current
                    if self._diodeCurrentMIN <= float(actionCMD[1]) <= self._diodeCurrentMAX:
                        self._diodeCurrent = float(actionCMD[1])
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?5')                       # Invalid parameter

                elif actionCMD[0] == 'DT':                                  # Diode Trigger - Allows you to change diode trigger value (0 = internal, 1 = external)
                    if int(actionCMD[1]) == 1 or int(actionCMD[1]) == 0:
                        self._diodeTrigger = int(actionCMD[1])
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?5')                       # Invalid parameter

                elif actionCMD[0] == 'DW':                                  # Diode Width - Allows you to edit the laser's diode width
                    if self._diodeWidthMIN <= int(actionCMD[1]) <= self._diodeWidthMAX:
                        self._diodeWidth = int(actionCMD[1])
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?5')                       # Invalid parameter

                elif actionCMD[0] == 'EC':                                  # Echo - Allows you to change between echo characters on and off (0 = off, 1 = on)
                    if int(actionCMD[1]) == 0 or int(actionCMD[1]) == 1:
                        self._echo = int(actionCMD[1])
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?5')                       # Invalid parameter

                elif actionCMD[0] == 'EM':                                  # Energy Mode - Allows you to change laser energy modes (0 = manual, 1 = low power, 2 = high power)
                    if int(actionCMD[1]) == 0:
                        self._energyMode = int(actionCMD[1])
                        self._HPM = '0'
                        self._LPM = '0'
                        self._sendBytes('OK')
                    elif int(actionCMD[1]) == 1:
                        self._energyMode = int(actionCMD[1])
                        self._LPM = '1'
                        self._HPM = '0'
                        self._sendBytes('OK')
                    elif int(actionCMD[1]) == 2:
                        self._energyMode = int(actionCMD[1])
                        self._LPM = '0'
                        self._HPM = '1'
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?5')                       # Invalid parameter

                elif actionCMD[0] == 'EN':                                  # Enable - Allows you to arm and disarm laser (0 = disarm/disable, 1 = arm/enable)
                    if self._RTE == '1' and actionCMD[1] == '1':
                        self._t2.start()
                        self._sendBytes('OK')
                    elif self._RTE == '0' and actionCMD[1] == '1':
                        self._sendBytes('?8')                       # Command unavailable in current system state
                    elif actionCMD[1] == '0' and self._enable == 1:
                        self._enable = 0
                        self._LE = '0'
                        self._RTF = '0'
                        self._sendBytes('OK')
                    elif actionCMD[1] == '0' and self._enable == 0:
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?8')                       # Command unavailable in current system state

                elif actionCMD[0] == 'FL':                                  # Fire Laser - Allows you to fire and stop firing the laser (0 = stop firing, 1 = fire)
                    if int(actionCMD[1]) == 1 and self._RTF == '1' and (self._energyMode == 0 or self._energyMode == 2) and self._LE == '1' and self._RTE == '1':
                        self._t3.start()
                        self._sendBytes('OK')
                    elif int(actionCMD[1]) == 0:
                        self._LA == '0'
                        self._fireLaser = 0
                    else:
                        self._sendBytes('?8')                       # Command unavailable in current system state
                        
                elif actionCMD[0] == 'PE':                                  # Pulse Period - Allows you to set the laser's pulse period
                    if self._pulsePeriodMIN <= float(actionCMD[1]) <= self._pulsePeriodMAX:
                        self._pulsePeriod = float(actionCMD[1])
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?5')                       # Invalid parameter

                elif actionCMD[0] == 'PM':                                  # Pulse Mode - Allows you to change the laser's pulse mode (0 = continuous, 1 = single shot, 2 = burst)
                    if int(actionCMD[1]) == 0 or int(actionCMD[1]) == 1 or int(actionCMD[1]) == 2: 
                        self._pulseMODE = int(actionCMD[1])
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?5')                       # Invalid parameter

                elif actionCMD[0] == 'RC':                                  # Recall Settings - Allows for changing recall settigns (bin 1-6) (0 = recall factory defaults)
                    if 1 <= int(actionCMD[1]) <= 6:
                        self._recallSettings = int(actionCMD[1])
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?5')                       # Invalid parameter

                elif actionCMD[0] == 'RR':                                  # Repitition Rate - Allows for changing the repitition rate (defaults to 1 Hz)
                    if self._repititionRateMIN <= int(actionCMD[1]) <= self._repititionRateMAX:
                        self._repitionRate = float(actionCMD[1])
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?5')                       # Invalid parameter

                elif actionCMD[0] == 'SV':                                  # Save Settigns - Allows for changing the save settings (bin 1-6)
                    if 1 <= int(actionCMD[1]) <= 6:
                        self._saveSettings = int(actionCMD[1])
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?5')                       # Invalid parameter

                elif actionCMD[0] == 'UC':                                  # User Shot Count - Can be cleared issuing a 0
                    self._userShotCount = int(actionCMD[1])
                    self._sendBytes('OK')

                elif actionCMD[0] == 'BV' or actionCMD [0] == 'DC:MIN' or actionCMD [0] == 'DC:MAX' or actionCMD [0] == 'DW:MIN' or actionCMD [0] == 'DW:MAX' or actionCMD [0] == 'FT' or actionCMD [0] == 'FT:MAX' or actionCMD [0] == 'FV' or actionCMD [0] == 'ID' or actionCMD [0] == 'IM' or actionCMD [0] == 'LS' or actionCMD [0] == 'PE:MIN' or actionCMD [0] == 'PE:MAX' or actionCMD [0] == 'RR:MIN' or actionCMD [0] == 'RR:MAX' or actionCMD [0] == 'SC' or actionCMD [0] == 'SS' or actionCMD [0] == 'TR:MIN' or actionCMD [0] == 'TR:MAX':
                    self._sendBytes('?6')                           # Query only command, query needs a question mark

                else:
                    self._sendBytes('?1')                           # Command not recognized

            elif len(strippedCMD[1].split()) == 1:
                actionCMD = strippedCMD[1].split()
                if actionCMD[0] == 'RS':                                    # Reset - Resets all variables to factory default
                    self._initializeVars()
                    self._sendBytes('OK')

                elif actionCMD[0] == 'BC' or actionCMD[0] == 'DC' or actionCMD[0] == 'DT' or actionCMD[0] == 'DW' or actionCMD[0] == 'EC' or actionCMD[0] == 'EM' or actionCMD[0] == 'EN' or actionCMD[0] == 'FL' or actionCMD[0] == 'PE' or actionCMD[0] == 'PM' or actionCMD[0] == 'RC' or actionCMD[0] == 'RR' or actionCMD[0] == 'SV' or actionCMD[0] == 'UC':
                    self._sendBytes('?5')                           # Invalid parameter
                
                elif actionCMD[0] == '':
                    self._sendBytes('?2')                           # Missing command keyword
                    
                else:
                    self._sendBytes('?3')                           # Invalid command keyword
                
        else:
            if strippedCMD[0] == '':
                self._sendBytes('?2')                               # Missing command keyword
            else: 
                self._sendBytes('?1')                               # Command not recognized
          
        return None


    def read(self, n=1):                    # Needs fixed so it doesn't send \n
        """ This function mocks the pyserial read() function, it takes in the number of bytes that you would like to recieve """
        if self._sendData == '':            # Check if send data is empty
            return None
        
        elif self._sendData == '\n':        # Check if '\n' is all that's left in the sendData string
            self._sendData = ''
            return None
        
        send = ''
        for i in range(n):                  # Going through string character by character
            if len(self._sendData) == 0:    # Break statement
                break
            if self._sendData[i] == '\n':
                self._sendData = self._sendData[i+1:]
            else:
                send += self._sendData[i]
                self._sendData = self._sendData[i+1:]
        return send.encode('ascii')


    def readline(self):                 
        """This function mocks the pyserial readline() fucntion. It reads a singular line of sendData """
        if self._sendData == '':
            return None
        elif self._sendData == '\n':
            self._sendData = ''
            return None

        newlineIndex = self._sendData.index("\n")
            
        send = self._sendData[0:newlineIndex]
        self._sendData = self._sendData[newlineIndex+1:]
        return send.encode('ascii')


    def read_until(self, expected):
        """ This function mocks the pyserial read_until() function. It teads until the provided character is found (until that character's index value) """
        if self._sendData == '':
            return None
        elif self._sendData == '\n':
            self._sendData = ''
            return None

        firstNewLine = self._sendData.index("\n")
        expectedIndex = self._sendData.index(expected)
        
        if firstNewLine < expectedIndex:
            if firstNewLine == 0:
                send = self._sendData[1:expectedIndex+1]
                self._sendData = self._sendData[expectedIndex+1:]
            else:
                send = self._sendData[0:firstNewLine] + self._sendData[firstNewLine+1:expectedIndex]
                self._sendData = self._sendData[expectedIndex+1:]

        else:
            send = self._sendData[0:expectedIndex+1]
            self._sendData = self._sendData[expectedIndex+1:]

        return send.encode('ascii')


    def _sendBytes(self, sendValue):
        """Formats a string into sendData string"""
        self._sendData += '{}\r\n'.format(str(sendValue))   # Places the carriage return along with a newline that I'm using to split off commands (newline's kinda unnecessary but I'm using it anyways )
        return None



    def _packingSSBinary(self):
        """
        This grabs all system status values and converts them into a 16 bit decimal.
        Putting all status bits into 16 bit string.
        """
        SixteenBit = list(self._spare + self._spare + self._HPM + self._LPM + self._RTF + self._RTE + self._PF + self._EOT + self._ROT + self._EI + self._reserved + self._reserved + self._DET + self._reserved + self._LA + self._LE)
        power = 0
        decimal = 0
        for i in reversed(range(len((SixteenBit)))):        # Converting 16 bit string into 16 bit decimal value
            if SixteenBit[i] == '1':
                decimal += 2**power
            power += 1
        return decimal



    def __str__(self):
        return "Serial<id=0x8a4c71>, open={}, port='{}', baudrate={}".format(self._isOpen, self.port, self.baudrate)

    def __repr__(self):
        return self.__str__()                               # Incase for some reason we want the representation of the serial object



    def _initializeVars(self):
        """
        This funciton houses all of our class variables that are laser specific.
        
        These variables are not in the __init__ function since they need to be resetable
        """
        self._sendData = ''
        
        #---Laser Settings------------------------------------------------
        self._burstCount = 10
        self._bankVoltage = 0

        self._diodeCurrent = 0
        self._diodeCurrentMIN = 0
        self._diodeCurrentMAX = 10000000
        self._diodeTrigger = 0
        self._diodeWidth = 0
        self._diodeWidthMIN = 0
        self._diodeWidthMAX = 10000000

        self._echo = 0

        self._energyMode = 2
        self._enable = 0
        self._fireLaser = 0
        self._FETtemp = 0       # Temp in Celsius
        self._FETtempMAX = 10000000
        self._FETvolts = 0      # Voltage
        self._currentMeasurement = 0
        self._latchedStatus = 0
        
        self._pulsePeriod = 0
        self._pulsePeriodMIN = 0
        self._pulsePeriodMAX = 3
        self._pulseMODE = 0     # 0 - Continuous, 1 = single shot, 2 = burst
        self._recallSettings = 0
        self._repititionRate = 1
        self._repititionRateMIN = 1
        self._repititionRateMAX = 5
        self._saveSettings = 0
        self._thermistorTemp = 0
        self._thermistorTempMIN = 0
        self._thermistorTempMAX = 10000000
        self._userShotCount = 0

        self._emergencyStop = False


        ### System Status Below ###
        # This goes 15 -> 0 byte order (16 bit decimal value)
        self._spare = '0'       # There are 2 of these
        self._HPM = '0'         # High Power Mode
        self._LPM = '0'         # Low Power Mode
        self._RTF = '0'         # Ready to Fire
        self._RTE = '1'         # Ready to Enable
        self._PF = '0'          # Power Failure
        self._EOT = '0'         # Electrical Over Temp
        self._ROT = '0'         # Resonator Over Temp
        self._EI = '0'          # External Interlock
        self._reserved = '0'    # Two of these
        self._DET = '0'         # Diode External Trigger
        # Another reserved
        self._LA = '0'          # Laser Active
        self._LE = '0'          # Laser Enabled

        ### Timer Threads ###
        self._t1 = threading.Thread(target=self._warmupTimer)       # Warmup timer thread
        self._t2 = threading.Thread(target=self._armingTimer)       # Arm timer thread
        self._t3 = threading.Thread(target=self._firingTimer)       # Laser Fire timer thread

    ### Threaded Timers ###
    def _warmupTimer(self):
        time.sleep(10)          # This function is unused unless I find a way to simulate the warmup period

    def _armingTimer(self):
        time.sleep(8)           # This function is meant to serve as a fake, threaded timer for 8 seconds which is the amount of time it takes for the laser to arm
        self._enable = 1
        self._LE = '1'
        self._RTF = '1'

    def _firingTimer(self):
        self._fireLaser = 1     # This function is meant to serve as a fake, threaded timer for the pulse period set to simulate the laser firing for that time period
        self._LA = '1'
        if self._pulseMODE == 0:
            time.sleep(self._pulsePeriod)                       # Continuous pulsing
        elif self._pulseMODE == 1:
            time.sleep(1 / self._repitionRate)                  # Single pulse
        elif self._pulseMODE == 2:
            time.sleep(self._burstCount / self._repitionRate)   # Burst pulses
        self._userShotCount += 1
        self._systemShotCount += 1
        self._fireLaser = 0
        self._LA = '0'
    """
    def _emergencyStopChecker(self):
        start = time.time()
        period = 0
        while period < self._pulsePeriod:
            if self._LA == '0':
    """

#---Error Types-----------------------------------------------------------------------------------

class PortError(Exception):     # A custom error that is raised when the port connection is closed
    pass