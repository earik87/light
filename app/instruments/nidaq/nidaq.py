from abc import ABC, abstractmethod
import random
from time import sleep

#For MacOS this import will fail, thats why it is in try/catch block to bypass.
try:
    import nidaqmx
except Exception as e:
    print(f"Unexpected error: {e}")

class NIDAQBaseClass(ABC):
    @abstractmethod
    def measure(self):
        pass

class NIDAQ(NIDAQBaseClass):
    def measure(self):
        try:
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan("Dev1/ai5")
                data = task.read()
                print(f"Acquired data: {data:f}")
                return data
                
        except Exception as e:
            print(f"Unexpected error: {e}")

class NIDAQDemo(NIDAQBaseClass):
    def measure(self):
        lower_limit = 0  
        upper_limit = 10 
        random_number = random.uniform(lower_limit, upper_limit)

        sleep(0.00001)
        print("Measurement is: ", random_number)
        return random_number