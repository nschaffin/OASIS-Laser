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
            commandDecoded = command.decode('ascii')
            print("Laser recieved command: {}".format(commandDecoded))
        else:
            raise TypeError('{} is not a byte format'.format(type(command)))

        strip = commandDecoded.split(':', 1)
        strippedCMD = []
        strippedCMD.append(strip[0])            # I can fix this to be shorter prolly, but meh
        strip = strip[1].split('<', 1)
        strippedCMD.append(strip[0])
        strippedCMD.append(strip[1])
        #print("Stripped command: {}".format(strippedCMD))

        # Check for valid command
        if strippedCMD[0] == ';LA' and (strippedCMD[2] == 'CR>' or strippedCMD[2] == 'LF>' or strippedCMD == 'CR><LF>' or strippedCMD == 'LF><CR>'):
            query = strippedCMD[1].find('?')
            if query != -1:                                                 # Query Commands
                queryList = strippedCMD[1].split('?')
                queryCMD = queryList[0]
            
                if queryCMD == 'BC':    # Burst Count
                    self._sendData += '{}\n'.format(str(self._burstCount))

                elif queryCMD == 'BV':  # Bank Voltage
                    self._sendData += '{}\n'.format(str(self._bankVoltage))

                elif queryCMD == 'DT':
                    self._sendData += '{}\n'.format(str(self._diodeTrigger))

                elif queryCMD == 'DC':
                    self._sendData += '{}\n'.format(str(self._diodeCurrent))

                elif queryCMD == 'DC:MIN':
                    self._sendData += '{}\n'.format(str(self._diodeCurrentMIN))

                elif queryCMD == 'DC:MAX':
                    self._sendData += '{}\n'.format(str(self._diodeCurrentMAX))

                elif queryCMD == 'DW':
                    self._sendData += '{}\n'.format(str(self._diodeWidth))

                elif queryCMD == 'DW:MIN':
                    self._sendData += '{}\n'.format(str(self._diodeWidthMIN))

                elif queryCMD == 'DW:MAX':
                    self._sendData += '{}\n'.format(str(self._diodeWidthMAX))

                elif queryCMD == 'EC':
                    self._sendData += '{}\n'.format(str(self._echo))

                elif queryCMD == 'EM':
                    self._sendData += '{}\n'.format(str(self._energyMode))

                elif queryCMD == 'EN':
                    self._sendData += '{}\n'.format(str(self._enable))

                elif queryCMD == 'FL':
                    self._sendData += '{}\n'.format(str(self._fireLaser))

                elif queryCMD == 'FT':
                    self._sendData += '{}\n'.format(str(self._FETtemp))

                elif queryCMD == 'FT:MAX':
                    self._sendData += '{}\n'.format(str(self._FETtempMAX))

                elif queryCMD == 'FV':
                    self._sendData += '{}\n'.format(str(self._FETvolts))

                elif queryCMD == 'ID':
                    self._sendData += '{}\n'.format(str('QC,MicroJewel,00101,1.0-0.0.0.8'))

                elif queryCMD == 'IM':
                    self._sendData += '{}\n'.format(str(self._currentMeasurement))

                elif queryCMD == 'LS':
                    self._sendData += '{}\n'.format(str(self._latchedStatus))

                elif queryCMD == 'PE':
                    self._sendData += '{}\n'.format(str(self._pulsePeriod))

                elif queryCMD == 'PE:MIN':
                    self._sendData += '{}\n'.format(str(self._pulsePeriodMIN))

                elif queryCMD == 'PE:MAX':
                    self._sendData += '{}\n'.format(str(self._pulsePeriodMAX))

                elif queryCMD == 'PM':
                    self._sendData += '{}\n'.format(str(self._pulseMODE))

                elif queryCMD == 'RC':
                    self._sendData += '{}\n'.format(str(self._recallSettings))

                elif queryCMD == 'RR':
                    self._sendData += '{}\n'.format(str(self._repititionRate))

                elif queryCMD == 'RR:MIN':
                    self._sendData += '{}\n'.format(str(self._repititionRateMIN))

                elif queryCMD == 'RR:MAX':
                    self._sendData += '{}\n'.format(str(self._repititionRateMAX))

                elif queryCMD == 'SC':
                    self._sendData += '{}\n'.format(str(self._systemShotCount))

                elif queryCMD == 'SS':
                    self._HPM == '0'
                    decimal = self._packingSSBinary()
                    self._sendBytes(decimal)
                    self._HPM == '1'

                elif queryCMD == 'SV':
                    self._sendData += '{}\n'.format(str(self._saveSettings))

                elif queryCMD == 'TR':
                    self._sendData += '{}\n'.format(str(self._thermistorTemp))

                elif queryCMD == 'TR:MIN':
                    self._sendData += '{}\n'.format(str(self._thermistorTempMIN))

                elif queryCMD == 'TR:MAX':
                    self._sendData += '{}\n'.format(str(self._thermistorTempMAX))

                elif queryCMD == 'UC':
                    self._sendData += '{}\n'.format(str(self._userShotCount))

                else:
                    self._sendBytes('?7')   # Error Code for invalid query command

            elif len(strippedCMD[1].split()) == 2:                          # Action commands
                actionCMD = strippedCMD[1].split()
                if actionCMD[0] == 'BC':
                    self._burstCount = int(actionCMD[1])
                    self._sendBytes('OK<CR>')

                elif actionCMD[0] == 'DC':
                    self._diodeCurrent = int(actionCMD[1])
                    self._sendBytes('OK<CR>')

                elif actionCMD[0] == 'DT':
                    self._diodeTrigger = int(actionCMD[1])
                    self._sendBytes('OK<CR>')

                elif actionCMD[0] == 'DW':
                    self._diodeWidth = int(actionCMD[1])
                    self._sendBytes('OK<CR>')

                elif actionCMD[0] == 'EC':
                    self._echo = int(actionCMD[1])
                    self._sendBytes('OK<CR>')

                elif actionCMD[0] == 'EM':
                    self._energyMode = int(actionCMD[1])
                    self._sendBytes('OK<CR>')

                elif actionCMD[0] == 'EN':              # Arm command
                    if self._RTE == '1':
                        self._enable = int(actionCMD[1])
                        self._LE = str(actionCMD[1])
                        self._RTF = str(actionCMD[1])
                        self._sendBytes('OK<CR>')
                    else:
                        self._sendBytes('?8')

                elif actionCMD[0] == 'FL':              # Fire laser command
                    if self._RTF == '1' and self._HPM == '1' and self._LE == '1' and self._RTE == '1':
                        self._fireLaser = int(actionCMD[1])
                        self._LA = '1'
                        self._sendBytes('OK<CR>')

                elif actionCMD[0] == 'PE':
                    self._pulsePeriod = float(actionCMD[1])
                    self._sendBytes('OK<CR>')

                elif actionCMD[0] == 'PM':
                    self._pulseMODE = int(actionCMD[1])
                    self._sendBytes('OK<CR>')

                elif actionCMD[0] == 'RC':
                    self._recallSettings = int(actionCMD[1])
                    self._sendBytes('OK<CR>')

                elif actionCMD[0] == 'RR':
                    self._repitionRate = float(actionCMD[1])
                    self._sendBytes('OK<CR>')

                elif actionCMD[0] == 'SV':
                    self._saveSettings = int(actionCMD[1])
                    self._sendBytes('OK<CR>')

                elif actionCMD[0] == 'UC':
                    self._userShotCount = int(actionCMD[1])
                    self._sendBytes('OK<CR>')

                else:
                    self._sendBytes('?1')

            elif len(strippedCMD[1].split()) == 1:
                actionCMD = strippedCMD[1].split()
                if actionCMD[0] == 'RS':
                    self._initializeVars()
                    self._sendBytes('OK<CR>')

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
                self._sendData[i+1:]
        return send.encode('ascii')


    def readline(self):                 
        if self._sendData == '':
            return None

        newlineIndex = self._sendData.index("\n")
            
        send = self._sendData[0:newlineIndex]
        self._sendData = self._sendData[newlineIndex+1:]
        return send.encode('ascii')


    def _sendBytes(self, sendValue):
        self._sendData += '{}\n'.format(str(sendValue))
        return None



    def _packingSSBinary(self):  # This grabs all system status values and converts them into a 16 bit decimal
        # Putting all status bits into 16 bit string
        SixteenBit = self._spare + self._spare + self._HPM + self._LPM + self._RTF + self._RTE + self._PF + self._EOT + self._ROT + self._EI + self._reserved + self._reserved + self._DET + self._reserved + self._LA + self._LE
        power = 0
        decimal = 0
        for i in reversed(SixteenBit):       # Converting 16 bit string into 16 bit decimal value
            if i == '1':
                decimal += 2**power
            power += 1
        return decimal



    def __str__(self):
        return "Serial<id=0x8a4c71>, open={}(port='{}', baudrate={})".format(self._isOpen, self.port, self.baudrate)

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
        
        self._pulsePeriod = 0
        self._pulsePeriodMIN = 0
        self._pulsePeriodMAX = 3
        self._pulseMODE = 0     # 0 - Continuous, 1 = single shot, 2 = burst
        self._recallSettings = 0
        self._repititionRate = 1
        self._systemShotCount = 0
        self._saveSettings = 0
        self._thermistorTemp = 0
        self._thermistorTempMIN = 0
        self._thermistorTempMAX = 0
        self._userShotCount = 0


        ### System Status Below ###
        # This goes 15 -> 0 byte order (16 bit decimal value)
        self._spare = '0'       # There are 2 of these
        self._HPM = '1'         # High Power Mode
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

### Error Types ###
class PortError(Exception):
    pass
    
