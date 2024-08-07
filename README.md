# Light

![Python workflow badge](https://github.com/earik87/light/actions/workflows/python-app.yml/badge.svg?event=push)

Light is a data acquisition application for THz-TDS Instrument in [Laser Research Group](https://users.metu.edu.tr/eokan/index.html).

Play the video to see how application works. Note that this is in demo mode. So, no hardware is connected.

https://github.com/earik87/light/assets/36437947/27984e98-2990-42b4-97b9-23b0318dfc2a


## Requirements

### Software
- Python 3.8.10
- Pip
- Virtualenv

### Hardware
- Thorlabs lts150/m. 
- NI USB-6361 which is reading from Lockin SR830. Direct connection to SR830 is supported but not tested yet.


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

## Development
Application is in demo mode by default with parameter `DEMO_MODE`. This means no hardware is connected, and scan is simulated. To deactivate demo mode and use hardware, make this constant `False`.
Recommended IDE is Visual Studio Code. 
