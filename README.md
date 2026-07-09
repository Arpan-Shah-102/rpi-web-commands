# RPi Management System

A small Raspberry Pi project that provides a web-based control panel and simple games for hardware components (LEDs, RGB LED, buzzer, keypad, 16x2 LCD) and a Pi Camera live feed.

**Video Demonstration [Here](https://youtu.be/fEOe1GjkGv8)**

**Features**
- **Web UI:** control LEDs, RGB sliders, buzzer, LCD text, and view live camera feed via the web interface.
- **Physical keypad UI:** local menu/apps driven from the attached 4x4 keypad and an LCD.

**NOTE:**
Not all features are ready yet. Some features like the button game and slot machine are not done. I'm also still testing some hardware components to get into the one free GPIO pin remaining on the Pi. A diagram of wiring is also missing. That will be added in the final update.

**Important files**
- [server.py](server.py): Flask web server, routes, and video feed
- [gpio_functions.py](gpio_functions.py): GPIO helpers, device setup, main loop, and hardware UI logic

**Requirements**
- Raspberry Pi (idealy a 4B+ with GPIO access) with a compatible camera and PiCamera2 support.
- Python 3.8+ (3.11 was used on mine).
- System packages: `espeak` (for voice feedback).
- Python packages: `Flask`, `gpiozero`, `picamera2`, `opencv-python`, `werkzeug`.

**Run**

Start the server on the Pi:

```bash
python3 server.py
```

Then open a browser to `http://<raspberry-pi-ip>:5000/` (or `http://raspberrypi.local:5000/`).

The live camera stream is served at `/video_feed` and the Button Game page at `/button_game`.

**Usage notes & troubleshooting**
- The project assumes GPIO pins used in `gpio_functions.py` match your wiring (LEDs, RGB, buzzer, keypad rows/cols).
- `picamera2` requires recent Raspberry Pi OS and camera firmware; consult PiCamera2 docs if the camera does not initialize.
- If the web UI buttons appear unresponsive, check the Flask server logs and ensure the main `loop()` thread (GPIO handling) is running.

**Wiring**

Wiring images will be available on the final version of this project. I don't have anything prepared right now sadly.
