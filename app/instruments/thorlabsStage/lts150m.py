import os
import decimal  # necessary for real world units
import sys
import clr
import time
from abc import ABC, abstractmethod
import serial
from time import sleep

try:

    clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
    clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
    clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.IntegratedStepperMotorsCLI.dll")
    from Thorlabs.MotionControl.DeviceManagerCLI import *
    from Thorlabs.MotionControl.GenericMotorCLI import *
    from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
    from System import Decimal  # necessary for real world units

except AttributeError as e:
    print(f"AttributeError: {e}")
except ImportError as e:
    print(f"ImportError: {e}. Please download Kinesis software and check references to dlls.")
except Exception as e:
    print(f"Unexpected error: {e}")

class ThorlabsStageBaseClass(ABC):
    @abstractmethod
    def openConnection(self):
        pass

    @abstractmethod
    def home(self):
        pass

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def closeConnection(self):
        pass


class ThorlabsStageControllerDemo(ThorlabsStageBaseClass):

    def __init__(self, serialNumber):
        self.serialNumber = serialNumber

    def openConnection(self):
        print('DEMO stagecontroller connected.')

    def home(self):
        print('DEMO stagecontroller homed.')

    def move(self, position):
        print('DEMO stagecontroller is ordered to move to: ' + str(position))

    def closeConnection(self):
        print('DEMO stageController is disconnected.')


class ThorlabsStageController(ThorlabsStageBaseClass):

    def __init__(self, serial_no):
        if not isinstance(serial_no, str) or not serial_no.isnumeric():
            raise ValueError("serial_no must be a string containing only numeric characters.")
        self.serial_no = serial_no

    def openConnection(self):
        DeviceManagerCLI.BuildDeviceList()
        
        # Connect, begin polling, and enable
        self.device = LongTravelStage.CreateLongTravelStage(self.serial_no)
        self.device.Connect(self.serial_no)

        print("stage is connected.")
        
        # Ensure that the device settings have been initialized
        if not self.device.IsSettingsInitialized():
            self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert self.device.IsSettingsInitialized() is True
        print("stage settings have been initialized.")

        # Start polling and enable
        self.device.StartPolling(250)  # 250ms polling rate
        time.sleep(5)  # Try a shorter delay first, then increase if necessary
        self.device.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable
        print("stage is enabled.")

        # Get Device Information and display description
        device_info = self.device.GetDeviceInfo()
        print(device_info.Description)

        # Load any configuration settings needed by the controller/stage.
        # Not sure if this is necessary?
        motor_config = self.device.LoadMotorConfiguration(self.serial_no)

    def home(self):
        # Get parameters related to homing/zeroing/other
        home_params = self.device.GetHomingParams()
        print(f'Homing velocity: {home_params.Velocity}\n,'
                f'Homing Direction: {home_params.Direction}')
        home_params.Velocity = Decimal(10.0)  # real units, mm/s
        # Set homing params (if changed)
        self.device.SetHomingParams(home_params)

        # Home or Zero the device (if a motor/piezo)
        print("Homing Device")
        self.device.Home(60000)  # 60 second timeout
        print("Done")

    def move(self, position):
        print('stagecontroller is ordered to move to ' + str(position))

        # Get Velocity Params
        vel_params = self.device.GetVelocityParams()
        vel_params.MaxVelocity = Decimal(50.0)  # This is a bad idea
        self.device.SetVelocityParams(vel_params)

        # Move the device to a new position
        new_pos = Decimal(150.0)  # Must be a .NET decimal
        print(f'Moving to {new_pos}')
        self.device.MoveTo(new_pos, 60000)  # 60 second timeout
        print("Done")

    def closeConnection(self):
        self.device.StopPolling()
        self.device.Disconnect()
        print('stageController is disconnected.')