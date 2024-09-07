import random
import numpy as np
from time import sleep
from abc import ABC, abstractmethod
from pymeasure.instruments.srs import SR830 as RealSR830
from pymeasure.instruments.resources import list_resources
import pyvisa
from pyvisa.constants import StopBits, Parity

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
        print('DEMO SR830: time constant is set to '+ str(self.timeConstant) + ' second.')

    def setSensitivity(self, sensitivity):
        self.sensitivity = sensitivity
        print('DEMO SR830: sensitivity is set to ' + str(self.sensitivity))

    def getTimeConstant(self):
        return self.timeConstant

    def getSensitivity(self):
        return self.sensitivity


class SR830(LockinAmplifierBaseClass):
    def __init__(self):
        self.instrument = None

    def openConnection(self, port, baudrate):
        # Initialize visa resource manager
        rm = pyvisa.ResourceManager()
        print(rm.list_resources())
        #To understand how this code works, read docs carefully!!!
        #https://pyvisa.readthedocs.io/en/latest/introduction/communication.html#making-sure-the-instrument-understand-the-command
        my_instrument = rm.open_resource('ASRL4::INSTR')
        my_instrument.read_termination = '\r' 
        my_instrument.write_termination = '\n' 
        self.instrument = RealSR830(my_instrument)

        print(my_instrument.query('*IDN?'))
        print("Time constant is", self.instrument.time_constant)
        print("Sensitivity is", self.instrument.sensitivity)
       
    def measure(self) -> float:
        if self.instrument is None:
            raise ConnectionError("Instrument not connected.")
        
        voltage = self.instrument.magnitude
        print("Measurement is: ", voltage)
        return voltage

    def setTimeConstant(self, timeConstant):
        if self.instrument is None:
            raise ConnectionError("Instrument not connected.")
        
        self.instrument.time_constant = timeConstant
        print('Real SR830: time constant is set to ' + str(timeConstant) + ' second.')

    def setSensitivity(self, sensitivity):
        if self.instrument is None:
            raise ConnectionError("Instrument not connected.")
        
        self.instrument.sensitivity = sensitivity
        print('Real SR830: sensitivity is set to ' + str(sensitivity))

    def getTimeConstant(self):
        if self.instrument is None:
            raise ConnectionError("Instrument not connected.")
        
        time_constant = self.instrument.time_constant
        return time_constant

    def getSensitivity(self):
        if self.instrument is None:
            raise ConnectionError("Instrument not connected.")
        
        sensitivity = self.instrument.sensitivity
        return sensitivity