try:
    from Thorlabs.MotionControl.DeviceManagerCLI import *
    from Thorlabs.MotionControl.GenericMotorCLI import *
    from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
    clr.AddReference(
        "C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
    clr.AddReference(
        "C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
    clr.AddReference(
        "C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.IntegratedStepperMotorsCLI.dll")
except ImportError:
    print("Cannot import Thorlabs.MotionControl libraries. Please download Kinesis software and check references to dlls.")
    pass

import os
import decimal  # necessary for real world units
import sys
import clr
import time
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


class ThorlabsStageControllerDemo(ThorlabsStageBaseClass):

    def __init__(self, serialNumber):
        self.serialNumber = serialNumber

    def openConnection(self):
        print('DEMO stagecontroller connecting')

    def initialize(self):
        print('DEMO stagecontroller initialising and homing')

    def move(self, position):
        print('DEMO stagecontroller is ordered to move to ' + str(position))

    def closeConnection(self):
        print('DEMO stageController is disconnecting')


class ThorlabsStageController(ThorlabsStageBaseClass):

    def __init__(self, serialNumber):
        self.serialNumber = serialNumber
        self.device = LongTravelStage.CreateLongTravelStage(self.serialNumber)

    def openConnection(self):
        print('DEMO stagecontroller connecting')

        try:
            DeviceManagerCLI.BuildDeviceList()

            # Connect, begin polling, and enable
            self.device.Connect(self.serialNumber)

            # Ensure that the device settings have been initialized
            if not self.device.IsSettingsInitialized():
                self.device.WaitForSettingsInitialized(
                    10000)  # 10 second timeout
                assert self.device.IsSettingsInitialized() is True

            # Start polling and enable
            self.device.StartPolling(250)  # 250ms polling rate
            time.sleep(25)
            self.device.EnableDevice()
            time.sleep(0.25)  # Wait for device to enable

            # Get Device Information and display description
            device_info = self.device.GetDeviceInfo()
            print(device_info.Description)

            # Load any configuration settings needed by the controller/stage
            motor_config = self.device.LoadMotorConfiguration(
                self.serialNumber)

            # Get Velocity Params
            vel_params = self.device.GetVelocityParams()
            vel_params.MaxVelocity = decimal(50.0)  # This is a bad idea
            self.device.SetVelocityParams(vel_params)

        except Exception as e:
            print(e)

    def initialize(self):
        print('DEMO stagecontroller initialising and homing')
        # Get parameters related to homing/zeroing/other
        home_params = self.device.GetHomingParams()
        print(f'Homing velocity: {home_params.Velocity}\n,'
              f'Homing Direction: {home_params.Direction}')
        home_params.Velocity = decimal(10.0)  # real units, mm/s
        # Set homing params (if changed)
        self.device.SetHomingParams(home_params)

        # Home or Zero the device (if a motor/piezo)
        print("Homing Device")
        self.device.Home(60000)  # 60 second timeout
        print("Done")

    def move(self, position):
        print('DEMO stagecontroller is ordered to move to ' + str(position))
        # Move the device to a new position
        new_pos = decimal(150.0)  # Must be a .NET decimal
        print(f'Moving to {new_pos}')
        self.device.MoveTo(new_pos, 60000)  # 60 second timeout
        print("Done")

    def closeConnection(self):
        # Stop Polling and Disconnect
        self.device.StopPolling()
        self.device.Disconnect()
