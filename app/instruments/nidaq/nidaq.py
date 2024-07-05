import nidaqmx


class NIDAQ():
    def measure(self):
        try:
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan("Dev1/ai5")
                data = task.read()
                print(f"Acquired data: {data:f}")
                return data
                
        except Exception as e:
            print(f"Unexpected error: {e}")