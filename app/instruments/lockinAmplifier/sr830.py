import serial
import numpy as np
from time import sleep
from abc import ABC, abstractmethod


class LockinAmplifierBaseClass(ABC):
    @abstractmethod
    def openConnection(self, port, baudrate):
        pass

    @abstractmethod
    def closeConnection(self):
        pass

    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def measure(self):
        pass

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def setParameter(self):
        pass

    @abstractmethod
    def setTimeConstant(self):
        pass

    @abstractmethod
    def setSensitivity(self):
        pass

    @abstractmethod
    def getTimeConstant(self):
        pass

    @abstractmethod
    def getSensitivity(self):
        pass


class SR830demo(LockinAmplifierBaseClass):
    def __init__(self, port, baudrate):
        self.datasetX = np.sin(np.linspace(0, 10*np.pi, 2500))
        self.datasetY = np.cos(np.linspace(0, 10*np.pi, 2500))
        self.dataN = 0

        self.timeConstant = 0
        self.sensitivity = 0

        thzDemoData = _ThzDemoData()
        self.time = thzDemoData.get_time()
        self.voltage = thzDemoData.get_voltage()
        self.length_of_scan = thzDemoData.get_length_of_scan()
        self.voltage_min, self.voltage_max = thzDemoData.get_min_max_voltage()
        self.time_min, self.time_max = thzDemoData.get_min_max_time()

    def openConnection(self):
        print('DEMO SR830 is connected')

    def closeConnection(self):
        print('DEMO SR830: closing connection')

    def flush(self):
        print('DEMO SR830: flushing serial comms')

    def measure(self) -> tuple:
        measurement = (self.time[self.dataN], self.voltage[self.dataN])
        self.dataN = self.dataN + 1
        sleep(0.00001)
        print("Measurement is: ", measurement)
        return measurement

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

    def setParameter(self, input_string):
        print('DEMO SR830: send '+input_string)

    def demo_measure_reset(self):
        self.dataN = 0

    def query(self, input):
        print('DEMO SR830: Query made with ' +
              str(input)+', returning something')
        return None

    def standard_setup(self):
        print('DEMO SR830: Setting up the standard parameters')

    def send(self):
        print('DEMO SR830: Send')

class SR830:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        if baudrate < 0:
            self.demomode=True
        else:
            self.demomode=False

        #self.ser = self.connect()
        sleep(0.25)

    def connect(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout = 0.03)

    def close(self):
        self.ser.close()

    def flush(self):
        self.ser.flush()

    def send(self, input_string):
        output_string = input_string+'\r'
        #print(output_string.encode())
        self.ser.write(output_string.encode())

    def receive_float(self):
        Nrec = self.ser.read(11)
        # Some error handling is necessary. Mainly when it fails due to changes in the LIA filter parameters.
        try:
            output_value = float(Nrec.decode())
        except ValueError:
            print('Error occured in the float decode')
            output_value = 0.0
            # To flush the buffer, I wait and read, twice.
            print('A:'+str(self.ser.readline()))
            sleep(0.1)
            print('Caught error in float reception')
        return output_value

    def measure(self):
        self.send('QX')
        X = self.receive_float()
        self.send('QY')
        Y = self.receive_float()
        return X,Y

    def set_tc(self, tc):
        TcList = ['T 1,1', #1  ms
                  'T 1,2', #3  ms
                  'T 1,3', #10 ms
                  'T 1,4', #30 ms
                  'T 1,5', #100ms
                  'T 1,6', #300ms
                  'T 1,7', #1   s
                  'T 1,8', #3   s
                  'T 1,9', #10  s
                  'T 1,10',#30  s
                  'T 1,11']#100 s
        self.send(TcList[tc])

    def set_sens(self, sens):
                            # Max scale
        sensList = ['G 4',  # 100 nV
                    'G 5',  # 200 nV
                    'G 6',  # 500 nV
                    'G 7',  # 1   uV
                    'G 8',  # 2   uV
                    'G 9',  # 5   uV
                    'G 10', # 10  uV
                    'G 11', # 20  uV
                    'G 12', # 50  uV
                    'G 13', # 100 uV
                    'G 14', # 200 uV
                    'G 15', # 500 uV
                    'G 16', # 1   mV
                    'G 17', # 2   mV
                    'G 18', # 5   mV
                    'G 19', # 10  mV
                    'G 20', # 20  mV
                    'G 21', # 50  mV
                    'G 22', # 100 mV
                    'G 23', # 200 mV
                    'G 24'] # 500 mV
        self.send(sensList[sens])

    def query(self, query):
        self.send(query)
        output = self.ser.readlines()
        return output

    def check_status_byte(self):
        q = self.query('Y')
        b = str(bin(int(q[0])))
        print(b)
        all_ok = True
        status_bits = ['SB 0: Not used',
                       'SB 1: Command parameter out of range',
                       'SB 2: No reference detected',
                       'SB 3: No phase lock',
                       'SB 4: Signal overload',
                       'SB 5: Auto offset out of range',
                       'SB 6: GPIB SRQ',
                       'SB 7: Illegal command string error']
        #zeropad the binary string with 0s to get an 8 bit string:
        byte = '0'*(8-len(b)+2)+b.split('b')[1]
        for n, bit in enumerate(reversed(byte)):
            if bit == '1':
                all_ok = False
                print(status_bits[n])

        if all_ok == True:
            print('All ok')

        return byte

    def standard_setup(self):
        # Set the character waiting time to 0:
        self.send('W0')
        # Set the band pass filter in
        self.send('B1')
        # Set the post filter to 0.1s
        self.send('T2,1')
        # Disengage both line notch filters.
        self.send('L1,0')
        self.send('L2,0')

class _ThzDemoData:
    def __init__(self):
        
        # Step 1: Read the Data
        with open("app/thz-tds-data.txt", "r") as file:
            data = file.readlines()

        # Step 2: Parse the Data
        self.time = []
        self.voltage = []
        for line in data:
            t, v = line.split()
            self.time.append(float(t))
            self.voltage.append(float(v))

        self.length_of_scan = len(self.time)

    def get_time(self):
        return self.time
    
    def get_voltage(self):
        return self.voltage

    def get_length_of_scan(self):
        return self.length_of_scan
    
    def get_min_max_voltage(self):
        return min(self.voltage), max(self.voltage)

    def get_min_max_time(self):
        return min(self.time), max(self.time)