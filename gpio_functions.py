from LCD1602 import CharLCD1602
import Keypad
from flask import Flask, render_template, request, Response, after_this_request, jsonify
from werkzeug.exceptions import HTTPException
from types import SimpleNamespace
import time
import os
from gpiozero import LED, Buzzer, RGBLED
from picamera2 import Picamera2
from random import randint
import cv2
from threading import Thread, Event

arrow = [
    0b00000,
    0b01000,
    0b01100,
    0b01110,
    0b01110,
    0b01100,
    0b01000,
    0b00000,]
replaceable = [
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,]

seven = [
    0b11111,
    0b11111,
    0b00011,
    0b00011,
    0b00110,
    0b00110,
    0b01100,
    0b01100,]
bar = [
    0b00000,
    0b11111,
    0b00000,
    0b11111,
    0b11111,
    0b00000,
    0b11111,
    0b00000,]
cherry = [
    0b00000,
    0b00010,
    0b00100,
    0b01110,
    0b11111,
    0b11111,
    0b01110,
    0b00000,]
bell = [
    0b00000,
    0b00100,
    0b01110,
    0b11111,
    0b11111,
    0b11111,
    0b00100,
    0b00000,]
diamond = [
    0b00000,
    0b00000,
    0b01110,
    0b11111,
    0b11111,
    0b01110,
    0b00100,
    0b00000,]

keys = ['b','u','3','A',
        'l','s','r','B',
        'm','d','p','C',
        'N','0','Y','D']
keypad = Keypad.Keypad(keys,[18,23,24,25],[12,16,20,21],4,4)
keypad.setDebounceTime(50)

lcd1602 = CharLCD1602()
lcd1602.init_lcd()

lcd1602.create_char(0, replaceable)
lcd1602.create_char(1, arrow)

lcd1602.create_char(3, bell)
lcd1602.create_char(4, bar)
lcd1602.create_char(5, cherry)
lcd1602.create_char(6, diamond)
lcd1602.create_char(7, seven)

rgbLED = RGBLED(red=5, green=6, blue=4, active_high=False)
leds = SimpleNamespace(y=LED(17), r=LED(27), g=LED(19), b=LED(22))
buzzer = Buzzer(26)

stop_event = Event()
varibles = {
    "ledR": False,
    "ledG": False,
    "ledB": False,
    "ledY": False,
    "rgbLedR": 0,
    "rgbLedG": 0,
    "rgbLedB": 0,
    "lcd_text": ["", ""]
}
game_vars = {
    "r_val": 0,
    "g_val": 0,
    "b_val": 0,
    "power": 10,
    "state": False,
    "lives": 5,
    "score": 0,
    "muted": False,
    "r1": chr(7),
    "r2": chr(7),
    "r3": chr(7),
    "payout": 10,
    "cost": 1,
    "money": 100,
}

in_menu = False
current_app = None
apps = ["led_control", "rgb_led", "buzzer_toggle", "button_game", "slot-machine", "settings"]
line_index = 0

led_controls = ["A", "B", "C", "D", "b", "N", "l"]
rgb_controls = ["u", "d", "l", "r", "p", "m", "b", "N"]
buzzer_controls = ["r", "s", "Y", "b", "N", "l"]
button_game_controls = ["u", "d", "l", "r", "b", "N"]
slot_machine_controls = ["u", "d", "l", "r", "b", "N"]
settings_controls = ["s", "Y", "r", "b", "N", "l"]
controls = [led_controls, rgb_controls, buzzer_controls, button_game_controls, slot_machine_controls, settings_controls]

lines = [f"{chr(1)}LED Control",
         f"{chr(0)}RGB LED",
         f"{chr(0)}Toggle Buzzer",
         f"{chr(0)}Button Game",
         f"{chr(0)}Slot Machine",
         f"{chr(0)}Settings",
       # f"{chr(0)}Character Limit",
         "",
         ]
led_control_ui = ["A: Yel  B: Red", "C: Grn  D: Blu"]
rgb_pos = 0
rgb_ui = ["R:"+chr(1)+"{r_val} | G:"+chr(0)+"{g_val}", "B:"+chr(0)+"{b_val} | P: X{power}"]
buzzer_ui = ["Buzzer: {state}", ""]
button_game_ui = ["Lives: {lives}", "Score: {score}"]
slot_machine_ui = ["{r1}{r2}{r3} Payout {payout}", "Cost {cost} | ${money}"]
settings_ui = ["Speaker Disabled", "{muted}"]
uis = [led_control_ui, rgb_ui, buzzer_ui, button_game_ui, slot_machine_ui, settings_ui]

def speak_async(tts, server=False):
    if not game_vars["muted"] or server:
        Thread(target=os.system, args=(f"espeak '{tts}'",), daemon=True).start()

def setRGBLED(r_val, g_val, b_val):
    rgbLED.red = r_val / 255
    rgbLED.green = g_val / 255
    rgbLED.blue = b_val / 255
            
def lcd(l1, l2, tts, t):
    global varibles
    lcd1602.clear()
    lcd1602.write(0,0,f'{l1}')
    lcd1602.write(0,1,f'{l2}')
    varibles["lcd_text"] = [l1, l2]
    speak_async(tts)
    time.sleep(t)

def button_press(denied = False):
    if current_app != "buzzer_toggle":
        buzzer.on()
        time.sleep(0.1)
        buzzer.off()
        
        if denied:
            time.sleep(0.1)
            buzzer.on()
            time.sleep(0.1)
            buzzer.off()

def destroy():
    lcd1602.clear()
    rgbLED.off()
    leds.r.off()
    leds.g.off()
    leds.b.off()
    leds.y.off()
    buzzer.off()

lcd(lines[line_index], lines[line_index + 1], "", 0)
def loop():
    global line_index, in_menu, current_app, game_vars, rgb_pos
    while not stop_event.is_set():
        key = keypad.getKey()
        if key != keypad.NULL:
            if not in_menu:
                if key in ['s', 'r', 'Y']:
                    Thread(target=button_press, daemon=True).start()
                elif (key == 'u' and line_index != 0) or (key == 'd' and line_index != len(lines) - 2):
                    Thread(target=button_press, daemon=True).start()
                else:
                    Thread(target=button_press, args=(True,), daemon=True).start()
            elif key not in buzzer_controls and current_app == "buzzer_toggle":
                Thread(target=button_press, args=(True,), daemon=True).start()
            elif key in controls[apps.index(current_app)] and current_app != "buzzer_toggle":
                Thread(target=button_press, daemon=True).start()
            elif current_app != "buzzer_toggle":
                Thread(target=button_press, args=(True,), daemon=True).start()

            if current_app == "led_control":
                if key == 'A':
                    leds.y.toggle()
                    varibles["ledY"] = not varibles["ledY"]
                elif key == 'B':
                    leds.r.toggle()
                    varibles["ledR"] = not varibles["ledR"]
                elif key == 'C':
                    leds.g.toggle()
                    varibles["ledG"] = not varibles["ledG"]
                elif key == 'D':
                    leds.b.toggle()
                    varibles["ledB"] = not varibles["ledB"]
                if key in ['A', 'B', 'C', 'D'] and not game_vars["muted"]:
                    speak_async("Toggling LED")
                
            if current_app == "rgb_led":
                if key == "p":
                    if game_vars["power"] != 100:
                        game_vars["power"] = int(game_vars["power"] * 10)
                        lcd(uis[1][0].format(**game_vars), uis[1][1].format(**game_vars), "Increasing Power" if not game_vars["muted"] else "", 0)
                elif key == "m":
                    if game_vars["power"] != 1:
                        game_vars["power"] = int(game_vars["power"] / 10)
                        lcd(uis[1][0].format(**game_vars), uis[1][1].format(**game_vars), "Decreasing Power" if not game_vars["muted"] else "", 0)
                
                if key == "l":
                    if rgb_pos != 0:
                        rgb_pos -= 1
                        if rgb_pos == 0:
                            rgb_ui[0] = "R:"+chr(1)+"{r_val} | G:"+chr(0)+"{g_val}"
                            rgb_ui[1] = "B:"+chr(0)+"{b_val} | P: X{power}"
                        elif rgb_pos == 1:
                            rgb_ui[0] = "R:"+chr(0)+"{r_val} | G:"+chr(1)+"{g_val}"
                            rgb_ui[1] = "B:"+chr(0)+"{b_val} | P: X{power}"
                        lcd(uis[1][0].format(**game_vars), uis[1][1].format(**game_vars), "Moving Left" if not game_vars["muted"] else "", 0)
                elif key == "r":
                    if rgb_pos != 2:
                        rgb_pos += 1
                        if rgb_pos == 1:
                            rgb_ui[0] = "R:"+chr(0)+"{r_val} | G:"+chr(1)+"{g_val}"
                            rgb_ui[1] = "B:"+chr(0)+"{b_val} | P: X{power}"
                        elif rgb_pos == 2:
                            rgb_ui[0] = "R:"+chr(0)+"{r_val} | G:"+chr(0)+"{g_val}"
                            rgb_ui[1] = "B:"+chr(1)+"{b_val} | P: X{power}"
                        lcd(uis[1][0].format(**game_vars), uis[1][1].format(**game_vars), "Moving Right" if not game_vars["muted"] else "", 0)
                
                if key == "u":
                    if rgb_pos == 0:
                        game_vars["r_val"] = min(255, game_vars["r_val"] + game_vars["power"])
                    elif rgb_pos == 1:
                        game_vars["g_val"] = min(255, game_vars["g_val"] + game_vars["power"])
                    elif rgb_pos == 2:
                        game_vars["b_val"] = min(255, game_vars["b_val"] + game_vars["power"])
                    rgbLED.red = game_vars["r_val"] / 255
                    rgbLED.green = game_vars["g_val"] / 255
                    rgbLED.blue = game_vars["b_val"] / 255
                    lcd(uis[1][0].format(**game_vars), uis[1][1].format(**game_vars), "Increasing Value" if not game_vars["muted"] else "", 0)
                elif key == "d":
                    if rgb_pos == 0:
                        game_vars["r_val"] = max(0, game_vars["r_val"] - game_vars["power"])
                    elif rgb_pos == 1:
                        game_vars["g_val"] = max(0, game_vars["g_val"] - game_vars["power"])
                    elif rgb_pos == 2:
                        game_vars["b_val"] = max(0, game_vars["b_val"] - game_vars["power"])
                    rgbLED.red = game_vars["r_val"] / 255
                    rgbLED.green = game_vars["g_val"] / 255
                    rgbLED.blue = game_vars["b_val"] / 255
                    lcd(uis[1][0].format(**game_vars), uis[1][1].format(**game_vars), "Decreasing Value" if not game_vars["muted"] else "", 0)
                
            if current_app == "buzzer_toggle":
                if key in ['r', 's', 'Y']:
                    game_vars["state"] = not game_vars["state"]
                    if game_vars["state"]:
                        buzzer.on()
                    else:
                        buzzer.off()
                    speak_async("Toggling Buzzer")
                    lcd(uis[2][0].format(**game_vars), uis[2][1].format(**game_vars), "", 0)
                
            if current_app == 'settings':
                if key in ['s', 'Y', 'r']:
                    game_vars["muted"] = not game_vars["muted"]
                    if not game_vars["muted"]:
                        speak_async("unmuting Speaker")
                    lcd(uis[5][0].format(**game_vars), uis[5][1].format(**game_vars), "", 0)
                
            if not in_menu:
                if key == 'd':
                    if line_index + 1 == len(lines) - 1:
                        Thread(target=button_press, args=(True,), daemon=True).start()
                    else:
                        line_index += 1
                        lcd(lines[line_index].replace(chr(0), chr(1)), lines[line_index + 1], "", 0)
                elif key == 'u':
                    if line_index - 1 < 0:
                        Thread(target=button_press, args=(True,), daemon=True).start()
                    else:
                        line_index -= 1
                        lcd(lines[line_index].replace(chr(0), chr(1)), lines[line_index + 1], "", 0)
                elif key in ['r', 's', 'Y']:
                    in_menu = True
                    current_app = apps[line_index]
                    lcd(uis[line_index][0].format(**game_vars), uis[line_index][1].format(**game_vars), "Entering App" if not game_vars["muted"] else "", 0)
                    
            if (in_menu and key in ['b', 'N', 'l'] and current_app != "rgb_led") or (in_menu and key in ['b', 'N'] and current_app == "rgb_led"):
                in_menu = False
                current_app = None
                line_index = 0
                lcd(lines[line_index], lines[line_index + 1], "Exiting App" if not game_vars["muted"] else "", 0)

        time.sleep(0.1)
