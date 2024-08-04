import random
import numpy as np
from time import sleep
from abc import ABC, abstractmethod
from pymeasure.instruments.srs import SR830 as RealSR830
import pyvisa

class LockinAmplifierBaseClass(ABC):
    @abstractmethod
    def openConnection(self, port, baudrate):
        pass

    @abstractmethod
    def measure(self):
        pass

    @abstractmethod
    def setTimeConstant(self, timeConstant):
        pass

    @abstractmethod
    def setSensitivity(self, sensitivity):
        pass

    @abstractmethod
    def getTimeConstant(self):
        pass

    @abstractmethod
    def getSensitivity(self):
        pass


class SR830Demo(LockinAmplifierBaseClass):
    def __init__(self):
        self.timeConstant = 0
        self.sensitivity = 0

    def openConnection(self, port, baudrate):
        print('DEMO SR830 is connected')

    def measure(self) -> float:
        lower_limit = 0  
        upper_limit = 10 
        random_number = random.uniform(lower_limit, upper_limit)

        sleep(0.00001)
        print("Measurement is: ", random_number)
        return random_number

    def setTimeConstant(self, timeConstant):
        self.timeConstant = timeConstant
        print('DEMO SR830: time constant is set to '+ str(self.timeConstant))

    def setSensitivity(self, sensitivity):
        self.sensitivity = sensitivity
        print('DEMO SR830: sensitivity is set to ' + str(self.sensitivity))

    def getTimeConstant(self):
        print('DEMO SR830: time constant is set to ' + str(self.timeConstant))

    def getSensitivity(self):
        print('DEMO SR830: sensitivity is set to ' + str(self.sensitivity))


class SR830(LockinAmplifierBaseClass):
    def __init__(self):
        self.instrument = None

    def openConnection(self, port, baudrate):
        # Initialize visa resource manager
        rm = pyvisa.ResourceManager()
        # Open connection to the SR830 using USB to RS232
        self.instrument = RealSR830(rm.open_resource(port, baud_rate=baudrate))
        print('Real SR830 is connected')

    def measure(self) -> float:
        if self.instrument is None:
            raise ConnectionError("Instrument not connected.")
        
        measurement = self.instrument.x
        print("Measurement is: ", measurement)
        return measurement

    def setTimeConstant(self, timeConstant):
        if self.instrument is None:
            raise ConnectionError("Instrument not connected.")
        
        self.instrument.time_constant = timeConstant
        print('Real SR830: time constant is set to ' + str(timeConstant))

    def setSensitivity(self, sensitivity):
        if self.instrument is None:
            raise ConnectionError("Instrument not connected.")
        
        self.instrument.sensitivity = sensitivity
        print('Real SR830: sensitivity is set to ' + str(sensitivity))

    def getTimeConstant(self):
        if self.instrument is None:
            raise ConnectionError("Instrument not connected.")
        
        time_constant = self.instrument.time_constant
        print('Real SR830: time constant is ' + str(time_constant))
        return time_constant

    def getSensitivity(self):
        if self.instrument is None:
            raise ConnectionError("Instrument not connected.")
        
        sensitivity = self.instrument.sensitivity
        print('Real SR830: sensitivity is ' + str(sensitivity))
        return sensitivity