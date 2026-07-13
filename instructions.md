# RPi Instruction for RPi Website with Random Games and Functionality

## Instructions
1. Download the source code.
2. Use Python or run `main-server-file`
  - Python
    - Install dependencies
    - Run python file
  - `main-server-file` blob
    - Run file

## Components

- Raspberry Pi (4B+ w/ 4gb ram model used)
- Camera module
- LEDs, buzzer, keypad, speakers, and LCD 1602 modules

## Create venv and Install Python Modules

```
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install Flask gpiozero picamera2 opencv-python werkzeug pyinstaller
```

Run the Python source:

```
python3 server.py
```

## Run Binary on Linux

If you want to use the `main-server-file` binary file, run the command:

```
./main-server-file
```

To rebuild `dist/server` after a fresh clone:

```bash
pyinstaller --onefile --add-data "templates:templates" --add-data "static:static" --collect-submodules picamera2 --collect-submodules gpiozero server.py
```


## Wiring
Wiring not ready yet. Please wait for a future version of this project.

## Video Demonstration [Here](https://youtu.be/fEOe1GjkGv8)
