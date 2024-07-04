# Light

![Python workflow badge](https://github.com/earik87/light/actions/workflows/python-app.yml/badge.svg?event=push)

Light is a data acquisition application for THz-TDS Instrument in [Laser Research Group](https://users.metu.edu.tr/eokan/index.html). It is a fork of another great [project](https://github.com/cbuhl/THzInstrumentControl). But, we changed and improved lots of things already. 

Play the video to see how application works. Note that this is in demo mode. So, no hardware is connected.

https://github.com/earik87/light/assets/36437947/27984e98-2990-42b4-97b9-23b0318dfc2a


## Requirements

### Software
- Python 3.8.10
- Pip
- Virtualenv

### Hardware (Not required in demo mode)
- Thorlabs lts150/m
- Lockin SR830.


## Installation

After cloning, create a virtual environment and install the requirements. For Linux and Mac users:

    $ virtualenv venv
    $ source venv/bin/activate
    (venv) $ pip install -r requirements.txt

If you are on Windows, then use the following commands instead:

    $ virtualenv venv
    $ venv\Scripts\activate
    (venv) $ pip install -r requirements.txt

## Running

To run the application, use the following command:

    (venv) $ python3 app/light.py

Note that in our lab pc (windows 7 - 64 bit) we had to downgrade PyQt5-Qt5==5.15.2 version, to be able to pull library. 

## Development
Application is in demo mode by default. This means no hardware is connected, and scan is simulated. To deactivate demo mode and use hardware, comment out the line `activeProfile = 'demo'`. 
Recommended IDE is Visual Studio Code. 
