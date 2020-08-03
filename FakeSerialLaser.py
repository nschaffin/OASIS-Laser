import threading
import re
import time

class Serial:
    def __init__(self, port=None,baudrate=9600,parity='PARITY_NONE',stopbits='STOPBITS_ONE',timeout=None,xonxoff=False,rtscts=False,write_timeout=None,dsrdtr=False,inter_byte_timeout=None,exclusive=None):
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
        self._isOpen = False
        self._initializeVars()
        
    def isOpen(self):
        return self._isOpen

    def open(self):
        self._isOpen = True
        return None

    def close(self):
        self._isOpen = False
        return None

    def clearSerial(self):
        self._sendData = ''
        return None


    def write(self, command):
        # Here I need to implement all of the stuff
        if self._isOpen == False:
            raise PortError('Port Not Opened')
        if type(command) == bytes:
            commandDecoded = str(repr(command.decode('ascii'))).strip("'")
            print("Laser recieved command: {}".format(commandDecoded))
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
            carriageReturnIndex = strip[1].index("\\r")
        except:
            carriageReturnIndex = -1
        
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
            print('hi')
            self._sendBytes('?1')
            return None

        # Check for valid command
        if strippedCMD[0] == ';LA':
            query = strippedCMD[1].find('?')
            if query != -1:                                                 # Query Commands
                queryList = strippedCMD[1].split('?')
                queryCMD = queryList[0]
            
                if queryCMD == 'BC':    # Burst Count
                    self._sendBytes(str(self._burstCount))

                elif queryCMD == 'BV':  # Bank Voltage
                    self._sendBytes(str(self._bankVoltage))

                elif queryCMD == 'DT':
                    self._sendBytes(str(self._diodeTrigger))

                elif queryCMD == 'DC':
                    self._sendBytes(str(self._diodeCurrent))

                elif queryCMD == 'DC:MIN':
                    self._sendBytes(str(self._diodeCurrentMIN))

                elif queryCMD == 'DC:MAX':
                    self._sendBytes(str(self._diodeCurrentMAX))

                elif queryCMD == 'DW':
                    self._sendBytes(str(self._diodeWidth))

                elif queryCMD == 'DW:MIN':
                    self._sendBytes(str(self._diodeWidthMIN))

                elif queryCMD == 'DW:MAX':
                    self._sendBytes(str(self._diodeWidthMAX))

                elif queryCMD == 'EC':
                    self._sendBytes(str(self._echo))

                elif queryCMD == 'EM':
                    self._sendBytes(str(self._energyMode))

                elif queryCMD == 'EN':
                    self._sendBytes(str(self._enable))

                elif queryCMD == 'FL':
                    self._sendBytes(str(self._fireLaser))

                elif queryCMD == 'FT':
                    self._sendBytes(str(self._FETtemp))

                elif queryCMD == 'FT:MAX':
                    self._sendBytes(str(self._FETtempMAX))

                elif queryCMD == 'FV':
                    self._sendBytes(str(self._FETvolts))

                elif queryCMD == 'ID':
                    self._sendBytes(str('QC,MicroJewel,00101,1.0-0.0.0.8'))

                elif queryCMD == 'IM':
                    self._sendBytes(str(self._currentMeasurement))

                elif queryCMD == 'LS':
                    self._sendBytes(str(self._latchedStatus))

                elif queryCMD == 'PE':
                    self._sendBytes(str(self._pulsePeriod))

                elif queryCMD == 'PE:MIN':
                    self._sendBytes(str(self._pulsePeriodMIN))

                elif queryCMD == 'PE:MAX':
                    self._sendBytes(str(self._pulsePeriodMAX))

                elif queryCMD == 'PM':
                    self._sendBytes(str(self._pulseMODE))

                elif queryCMD == 'RC':
                    self._sendBytes(str(self._recallSettings))

                elif queryCMD == 'RR':
                    self._sendBytes(str(self._repititionRate))

                elif queryCMD == 'RR:MIN':
                    self._sendBytes(str(self._repititionRateMIN))

                elif queryCMD == 'RR:MAX':
                    self._sendBytes(str(self._repititionRateMAX))

                elif queryCMD == 'SC':
                    self._sendBytes(str(self._systemShotCount))

                elif queryCMD == 'SS':
                    self._HPM == '0'
                    decimal = self._packingSSBinary()
                    self._sendBytes(decimal)
                    self._HPM == '1'

                elif queryCMD == 'SV':
                    self._sendBytes(str(self._saveSettings))

                elif queryCMD == 'TR':
                    self._sendBytes(str(self._thermistorTemp))

                elif queryCMD == 'TR:MIN':
                    self._sendBytes(str(self._thermistorTempMIN))

                elif queryCMD == 'TR:MAX':
                    self._sendBytes(str(self._thermistorTempMAX))

                elif queryCMD == 'UC':
                    self._sendBytes(str(self._userShotCount))

                else:
                    self._sendBytes('?7')   # Error Code for invalid query command

            elif len(strippedCMD[1].split()) == 2:                          # Action commands
                actionCMD = strippedCMD[1].split()
                if actionCMD[0] == 'BC':
                    self._burstCount = int(actionCMD[1])
                    self._sendBytes('OK')

                elif actionCMD[0] == 'DC':
                    self._diodeCurrent = int(actionCMD[1])
                    self._sendBytes('OK')

                elif actionCMD[0] == 'DT':
                    self._diodeTrigger = int(actionCMD[1])
                    self._sendBytes('OK')

                elif actionCMD[0] == 'DW':
                    self._diodeWidth = int(actionCMD[1])
                    self._sendBytes('OK')

                elif actionCMD[0] == 'EC':
                    self._echo = int(actionCMD[1])
                    self._sendBytes('OK')

                elif actionCMD[0] == 'EM':
                    self._energyMode = int(actionCMD[1])
                    self._sendBytes('OK')

                elif actionCMD[0] == 'EN':              # Arm command
                    if self._RTE == '1' and actionCMD[1] == '1':
                        self._t2.start()
                        self._sendBytes('OK')
                    elif self._RTE == '0' and actionCMD[1] == '1':
                        self._sendBytes('?8')
                    elif actionCMD[1] == '0' and self._enable == 1:
                        self._enable = 0
                        self._LE = '0'
                        self._RTF = '0'
                        self._sendBytes('OK')
                    elif actionCMD[1] == '0' and self._enable == 0:
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?8')

                elif actionCMD[0] == 'FL':              # Fire laser command
                    if self._RTF == '1' and (self._energyMode == 0 or self._energyMode == 2) and self._LE == '1' and self._RTE == '1':
                        self._t3.start()
                        self._sendBytes('OK')
                    else:
                        self._sendBytes('?8')
                        
                elif actionCMD[0] == 'PE':
                    self._pulsePeriod = float(actionCMD[1])
                    self._sendBytes('OK')

                elif actionCMD[0] == 'PM':
                    self._pulseMODE = int(actionCMD[1])
                    self._sendBytes('OK')

                elif actionCMD[0] == 'RC':
                    self._recallSettings = int(actionCMD[1])
                    self._sendBytes('OK')

                elif actionCMD[0] == 'RR':
                    self._repitionRate = float(actionCMD[1])
                    self._sendBytes('OK')

                elif actionCMD[0] == 'SV':
                    self._saveSettings = int(actionCMD[1])
                    self._sendBytes('OK')

                elif actionCMD[0] == 'UC':
                    self._userShotCount = int(actionCMD[1])
                    self._sendBytes('OK')

                else:
                    self._sendBytes('?1')

            elif len(strippedCMD[1].split()) == 1:
                actionCMD = strippedCMD[1].split()
                if actionCMD[0] == 'RS':
                    self._initializeVars()
                    self._sendBytes('OK')

                else:
                    self._sendBytes('?1')
                
        else:
            self._sendBytes('?1')
          
        return None


    def read(self, n=1):                    # Needs fixed so it doesn't send \n
        if self._sendData == '':
            return None
        send = ''
        for i in range(n):
            if len(self._sendData) == 0:
                break
            if _sendData[i] == '\n':
                self._sendData = self._sendData[i+1:]
            else:
                send += self._sendData[i]
                self._sendData = self._sendData[i+1:]
        return send.encode('ascii')


    def readline(self):                 
        if self._sendData == '':
            return None

        newlineIndex = self._sendData.index("\n")
            
        send = self._sendData[0:newlineIndex]
        self._sendData = self._sendData[newlineIndex+1:]
        return send.encode('ascii')


    def _sendBytes(self, sendValue):
        self._sendData += '{}\r\n'.format(str(sendValue))
        return None



    def _packingSSBinary(self):  # This grabs all system status values and converts them into a 16 bit decimal
        # Putting all status bits into 16 bit string
        SixteenBit = list(self._spare + self._spare + self._HPM + self._LPM + self._RTF + self._RTE + self._PF + self._EOT + self._ROT + self._EI + self._reserved + self._reserved + self._DET + self._reserved + self._LA + self._LE)
        power = 0
        decimal = 0
        for i in reversed(range(len((SixteenBit)))):       # Converting 16 bit string into 16 bit decimal value
            if SixteenBit[i] == '1':
                decimal += 2**power
            power += 1
        return decimal



    def __str__(self):
        return "Serial<id=0x8a4c71>, open={}, port='{}', baudrate={}".format(self._isOpen, self.port, self.baudrate)

    def __repr__(self):
        return self.__str__()



    def _initializeVars(self):
        #self._recievedData = ""
        self._sendData = ''
        ### Laser Settings ###
        self._burstCount = 10
        self._bankVoltage = 0

        self._diodeCurrent = 0
        self._diodeCurrentMIN = 0
        self._diodeCurrentMAX = 0
        self._diodeTrigger = 0
        self._diodeWidth = 0
        self._diodeWidthMIN = 0
        self._diodeWidthMAX = 0

        self._echo = 0

        self._energyMode = 2
        self._enable = 0
        self._fireLaser = 0
        self._FETtemp = 0       # Temp in Celsius
        self._FETtempMAX = 0
        self._FETvolts = 0      # Voltage
        self._currentMeasurement = 0
        self._latchedStatus = 0
        
        self._pulsePeriod = 2   # Starting pulse period at arbitrary two seconds
        self._pulsePeriodMIN = 0
        self._pulsePeriodMAX = 3
        self._pulseMODE = 0     # 0 - Continuous, 1 = single shot, 2 = burst
        self._recallSettings = 0
        self._repititionRate = 5
        self._systemShotCount = 0
        self._saveSettings = 0
        self._thermistorTemp = 0
        self._thermistorTempMIN = 0
        self._thermistorTempMAX = 0
        self._userShotCount = 0


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
        self._t1 = threading.Thread(target=self._warmupTimer)
        self._t2 = threading.Thread(target=self._armingTimer)
        self._t3 = threading.Thread(target=self._firingTimer)

    ### Threaded Timers ###
    def _warmupTimer(self):
        time.sleep(10)

    def _armingTimer(self):
        time.sleep(8)
        self._enable = 1
        self._LE = '1'
        self._RTF = '1'

    def _firingTimer(self):
        self._fireLaser = 1
        self._LA = '1'
        time.sleep(self._pulsePeriod)
        self._fireLaser = 0
        self._LA = '0'


### Error Types ###
class PortError(Exception):
    pass