# Light

![Python workflow badge](https://github.com/earik87/light/actions/workflows/python-app.yml/badge.svg)

Light is a data acquisition application for THz-TDS Instrument [in LSG group](https://users.metu.edu.tr/eokan/index.html). It is a fork of another [project](https://github.com/cbuhl/THzInstrumentControl). Why we create a new one? Because the instruments to be controlled are different (lockin SR830 and thorlabs lts150/m). Plus, we will try to use software development practices here as much as possible. 

Note that this project is not in-use, yet and still under-development!

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
