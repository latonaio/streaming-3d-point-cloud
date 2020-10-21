### Introduction
arena_api is a python wrapper to interact with ArenaSDK. 
This package is built on top of ArenaC API.


### arena_api prerequisites
  - Python >= 3.6
  - ArenaSDK:
    - Windows | 1.0.20.0  <= ArenaSDK <= 1.999.999
    - Linux   | 0.1.27 <= ArenaSDK <= 0.999.999
    - ARM     | 0.1.14  <= ArenaSDK <= 0.999.999
  - Pip packages:
    - Windows :
      pywin32==224 (will be installed automatically on internet connected machine)
  
  - Offline machines only:
    - look at offline_installation_dependencies.zip
    - if a platform specific whl file is missing, it can be found at 
      https://pypi.org/project/<package_name>/#files 

### arena_api installation instructions
  '''pip install arena_api-<>.<>.<>-py3-none-any.whl'''

### Examples prerequisites
  - Make sure arena_api package is installed
  - Some examples require other pip packages which can be
    found in examples/requirements.txt. To install these packages run
      '''pip install -r examples/requirements_win.txt''' for windows platform
      '''pip install -r examples/requirements_lin.txt''' for linux (non arm)
      '''pip install -r examples/requirements_lin_arm32.txt''' for linux on arm 32
      '''pip install -r examples/requirements_lin_arm64.txt''' for linux on arm 64
  - On armhf, opencv-python might need some other dependencies:
    '''sudo apt-get install libatlas-base-dev'''
    '''sudo apt-get install libjasper-dev'''
    '''sudo apt-get install libqtgui4'''
    '''sudo apt-get install python3-pyqt5'''
    '''sudo apt install libqt4-test'''
    '''sudo apt-get install python-opencv'''
    - more on this:
      https://docs.opencv.org/4.2.0/d2/de6/tutorial_py_setup_in_ubuntu.html