import sys
import time
import os
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib
import matplotlib.pyplot as plt
from instruments.lockinAmplifier.sr830 import SR830Demo, SR830
from instruments.nidaq.nidaq import NIDAQ, NIDAQDemo
from instruments.thorlabsStage.lts150m import ThorlabsStageControllerDemo, ThorlabsStageController

# If you do not use demo, then comment this line.
activeProfile = 'demo'


class LightUIWindow(QMainWindow):
    def __init__(self):
        global activeProfile
        super(LightUIWindow, self).__init__()
        loadUi('app/MainWindow.ui', self)
        self.setWindowTitle('THz Scan GUI')

        # Check for os:
        if os.name == 'nt':  # Respond to windows platform
            print('Identified Windows OS')
            portLIA = 'com3'  # Prolific driver
            portStage = 'com4'  # Arduino Uno ID
        elif os.name == 'posix':
            print('Identified Mac OS')
            portLIA = '/dev/tty.usbserial'
            portStage = '/dev/tty.usbmodem1421'
        else:
            print('CRITICAL: Unidentified OS.')

       # Check if application runs in demo mode. Demo mode is bypassing real hardware connection and used for development purposes. 
        if activeProfile == 'demo':
            self.lia = SR830Demo(portLIA, 19200) #SR830 is never set up (for now), so it is always in demo mode.
            self.daq = NIDAQDemo()
            self.stage = ThorlabsStageControllerDemo("45283704")
        else:
            self.lia = SR830Demo(portLIA, 19200) #SR830 is never set up (for now), so it is always in demo mode.
            self.daq = NIDAQ()
            self.stage = ThorlabsStageController("45283704")

        self.lia.openConnection()
        time.sleep(0.25)

        self.stage.openConnection()
        self.stage.home()

        # A hack is needed to start the drop down menus in a sane place.
        self.ddSens.setCurrentIndex(18)
        self.ddTc.setCurrentIndex(7)

        # Define execution control variables
        self.StopRunFlag = False
        self.IsHomedFlag = False
        self.SaveAllFlag = False
        self.SaveOnStop = False

        self.dataX = np.array([])
        self.dataY = np.array([])
        self.dataStep = np.array([])

        ## Set up windows and figures for plotting ##
        # a figure instance to plot on
        self.figure = Figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        # Scale any fonts accordingly.
        if os.name == 'posix':
            matplotlib.rcParams.update({'font.size': 5})

        # Insert the widgets at appropriate places, and replace the placeholder widget.
        self.verticalLayout.insertWidget(0, self.toolbar)
        self.verticalLayout.replaceWidget(self.wplot, self.canvas)

        # Define signals and slots for buttons
        self.btnStart.clicked.connect(self.btnStart_clicked)
        self.btnStop.clicked.connect(self.btnStop_clicked)
        self.btnGoto.clicked.connect(self.btnGoto_clicked)
        self.btnUpdate.clicked.connect(self.btnUpdate_clicked)
        self.cbSaveall.stateChanged.connect(self.update_savestate)

    # Define button functions

    def btnStart_clicked(self):
        try:
            self.lia.demo_measure_reset()  # should be removed when out of dev
        except AttributeError:
            pass

        length_of_scan = int(
            ((self.nStop.value() - self.nStart.value())/self.nStepsize.value()) + 1)
        self.voltage_min = 0
        self.voltage_max = 10
        self.time_min = self.nStart.value()
        self.time_max = self.nStop.value()

        self.update_statusbar('Starting scan')
        self.reset_data_array()
        self.StopRunFlag = False
        # It defaults to the end of the loop where it saves, anyway.
        self.SaveOnStop = False

        self.generate_plot()
        # update step point
        self.PresentPosition = self.nStart.value()
        # goto start of scan range
        self.stage.move(self.PresentPosition)

        # wait for stage controller to arrive

        for i in range(length_of_scan):

            # Check for stop flag
            if self.StopRunFlag == True:
                break

            # Measure data
            voltageValue = self.measureVoltage()

            # append data to dataarray
            self.dataX = np.append(self.dataX, self.PresentPosition)
            self.dataY = np.append(self.dataY, voltageValue)
            self.dataStep = np.append(self.dataStep, self.PresentPosition)

            # Increment the PresentPosition controller variable
            self.PresentPosition = self.PresentPosition + self.nStepsize.value()

            # Execute move start
            self.stage.move(self.PresentPosition)

            # Execute post move wait
            self.interruptable_sleep(self.post_move_wait_time)

            # Update plot
            self.update_plot()

        self.save_data_array()

    def btnStop_clicked(self):
        self.update_statusbar('Stopping scan')
        self.StopRunFlag = True
        if self.SaveOnStop:
            self.save_data_array()
        self.lia.setParameter('I0')

    def btnGoto_clicked(self):
        self.update_statusbar('Starting Goto')
        self.stage.move(self.nPosition.value())
        self.update_statusbar('Goto value reached')

    def btnUpdate_clicked(self):
        self.update_statusbar('Updating Lockin')
        # Update sensitivity
        selected_sens = self.ddSens.currentIndex()
        # print('Sensitivity: '+str(selected_sens))
        self.lia.setSensitivity(selected_sens)
        # Update filter Tcs
        selected_tc = 10-self.ddTc.currentIndex()
        # print('Time constant: '+str(selected_tc))
        self.lia.setTimeConstant(selected_tc)

    # Define update, save and time calc functions
    def measureVoltage(self):
        dataY = []
        for i in range(int(self.nAvg.value())):
            single_measurement = self.daq.measure() #nidaq read
            #single_measurement = self.lia.measure() #SR830 read
            dataY.append(single_measurement)

        return (np.mean(dataY))

    def update_statusbar(self, new_update):
        self.statusBar.setText('Status: '+new_update)

        # As this is an often used function, I will piggy-back on this to ensure
        # the scan time estimate is regularly updated and shown.
        estimated_scan_time = self.estimate_scan_time()
        m, s = divmod(estimated_scan_time, 60)
        h, m = divmod(m, 60)
        self.lblEstduration.setText("%dhrs, %02dmins, %02dsecs" % (h, m, s))

    def update_savestate(self):
        if self.cbSaveall.checkState() == 2:
            self.SaveAllFlag = True
        else:
            self.SaveAllFlag = False
        self.update_statusbar('Saves all: '+str(self.SaveAllFlag))

    def estimate_scan_time(self):
        nStart = self.nStart.value()
        nStop = self.nStop.value()
        nStepsize = self.nStepsize.value()
        nPostmove = self.nPostmove.value()
        nAvg = self.nAvg.value()

        # The integers were easy, now the slightly trickier part;
        # Decoding the time constant from the Tc drop down menu.
        textTc = self.ddTc.currentText()
        multiplier, unit = textTc.split(' ')
        if unit == 's':
            Tc = float(multiplier)
        elif unit == 'ms':
            Tc = float(multiplier) * 1e-3

        self.post_move_wait_time = Tc * (1+nPostmove)

        if activeProfile == 'demo':
            time = ((self.post_move_wait_time * nAvg)+ 0.025) * (nStop-nStart)/nStepsize
        else:
            time = (Tc * (1+nPostmove) * nAvg + nStepsize * 1/120.0) * (nStop-nStart)/nStepsize
            #TODO: 120.0 here is the velocity of stage. Just pull it from stage class.

        return time

    def interruptable_sleep(self, wait_time):
        i = 0
        while not self.StopRunFlag and i < int(wait_time*100):
            time.sleep(0.01)
            i += 1

    def reset_data_array(self):
        self.dataX = np.array([])
        self.dataY = np.array([])
        self.dataStep = np.array([])

    def save_data_array(self):
        # The filename expression will be yyyymmdd-hr-mn-ss.dat
        prefix_string = self.fileprefix.text()
        working_directory = os.path.join(os.getcwd(), '..', 'data/')
        datetime_string = time.strftime('%Y%m%d-%H-%M-%S_')
        fname_string = working_directory+datetime_string+prefix_string+'.csv'

        if self.SaveAllFlag:
            print('Saving file to '+fname_string)
            pd.DataFrame(np.array([self.dataX, self.dataY]).T,
                         columns=['stagePos', 'voltage']).to_csv(fname_string, index=False)

    # Define plotting and plot update functions
    def generate_plot(self):
        self.figure.clear()  # Clear the figure to ensure it's completely reset
        self.ax = self.figure.add_subplot(111)  # Recreate the axes

        # Set axis labels
        self.ax.set_xlabel("Stage Position", fontsize=12)  # Set X-axis label
        self.ax.set_ylabel("Voltage", fontsize=12)         # Set Y-axis label

        # Adjust tick label font size
        # Adjust major tick label font size
        self.ax.tick_params(axis='both', which='major', labelsize=8)
        # Adjust minor tick label font size, if minor ticks are used
        self.ax.tick_params(axis='both', which='minor', labelsize=6)

        # Set the initial axes limits based on the initial scan range
        self.ax.set_xlim(self.nStart.value(), self.nStop.value())
        self.ax.set_ylim(self.voltage_min, self.voltage_max)

        # Plot the initial data
        self.lineX, = self.ax.plot(
            self.dataX, self.dataY, 'r-')  # Adjust as needed

        # Refresh canvas
        self.canvas.draw()

    def update_plot(self):
        # Dynamically adjust the x-axis limits based on the current data range.
        # This could start from your initial point and extend to the last point collected.
        if len(self.dataX) > 1:  # Ensure there are at least two points to define a range
            current_min_x = min(self.dataX)
            current_max_x = max(self.dataX)
            self.ax.set_xlim(current_min_x, current_max_x)
        else:
            # Optional: Set a default or initial range for the x-axis if you prefer
            self.ax.set_xlim(self.nStart.value(),
                             self.nStart.value() + self.nStepsize.value())

        # Dynamically adjust Y-axis limits based on data
        if len(self.dataY) > 0:  # Ensure there's at least one point
            self.ax.set_ylim(min(self.dataY), max(self.dataY))
        else:
            # Optional: Set a default or initial range for the y-axis if you prefer
            self.ax.set_ylim(self.voltage_min, self.voltage_max)

        # Update the data for the line plot
        self.lineX.set_data(self.dataX, self.dataY)

        # Necessary to recompute the graph limits after updating the data
        self.ax.relim()
        self.ax.autoscale_view(True, True, True)

        # Refresh canvas
        self.canvas.draw()
        self.canvas.flush_events()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    lightUIWindow = LightUIWindow()
    lightUIWindow.show()
    sys.exit(app.exec_())