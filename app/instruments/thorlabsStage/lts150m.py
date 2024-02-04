from abc import ABC, abstractmethod
import serial
from time import sleep

class ThorlabsStageBaseClass(ABC):
    @abstractmethod
    def openConnection(self):
        pass

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def closeConnection(self):
        pass

    @abstractmethod
    def waitForMovement(self):
        pass

class ThorlabsStageControllerDemo():
    def __init__(self, port, baudrate):
        print('DEMO stage controller instantiating')

    def openConnection(self):
        print('DEMO stagecontroller connecting')

    def initialize(self):
        print('DEMO stagecontroller initialising and homing')

    def move(self, position):
        print('DEMO stagecontroller is ordered to move to ' + str(position))

    def closeConnection(self):
        pass

    def waitForMovement(self):
        sleep(0.1)

    def read_string(self):
        return 'string'


class ThorlabsStageController():
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate

    def openConnection(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
        sleep(1)

        # run down the buffers initially
        self.ser.write(b'query \r\n')
        garbage = self.__read_string()

        self.ser.write(b'query \r\n')
        output = self.__read_string()

        if output == 'alive\r\n':
            print('Found arduino on port '+self.port)
        else:
            print('Arduino not found.')

    def initialize(self):
        self.ser.flush()
        # Find ud af hvorfor der ikke er endelser paa i Peters udgave.
        self.ser.write(b'init \r\n')
        self.wait_for_done()

    def move(self, x):
        self.ser.write(b'go '+str(int(x)).encode()+'\r\n'.encode())
        # print('move ordered')
        self.wait_for_done()

    def closeConnection(self):
        self.ser.close()

    def waitForMovement(self):
        DONE_FOUND_FLAG = False
        while not DONE_FOUND_FLAG:
            string = ""
            bytes_returned = 1
            while bytes_returned > 0:
                read_char = self.ser.read().decode()
                bytes_returned = len(read_char)
                string += read_char

            if 'done' in string:
                DONE_FOUND_FLAG = True

            sleep(0.1)

    def __read_string(self):
        string = ""
        bytes_returned = 1
        while bytes_returned > 0:
            read_char = self.ser.read()
            bytes_returned = len(read_char)
            string += read_char.decode()
        # print('read_string function: '+string)

        return string