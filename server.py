from gpio_functions import *

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())

connected = False
app = Flask(__name__)

def genVidFeed():
    while True:
        frame = picam2.capture_array()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ret, jpeg = cv2.imencode('.jpg', frame_rgb)
        if ret:
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/', methods=['GET', 'POST'])
def home():
    global connected, varibles
    if request.method == 'POST':
        if ("speakerSpeak" in request.form) or ("lcdLine1" in request.form) or ("lcdLine2" in request.form):
            message = request.form['speakerSpeak']
            l1 = request.form['lcdLine1']
            l2 = request.form['lcdLine2']
            if l1 == "" and l2 == "":
                speak_async(message, server=True)
            else:
                lcd(l1, l2, message, 0)
        if "ledR" in request.form:
            leds.r.toggle()
            varibles["ledR"] = not varibles["ledR"]
        if "ledG" in request.form:
            leds.g.toggle()
            varibles["ledG"] = not varibles["ledG"]
        if "ledB" in request.form:
            leds.b.toggle()
            varibles["ledB"] = not varibles["ledB"]
        if "ledY" in request.form:
            leds.y.toggle()
            varibles["ledY"] = not varibles["ledY"]
        if "buzzer" in request.form:
            buzzer.toggle()
        if "update" in request.form:
            varibles["rgbLedR"] = int(request.form["rgbLedR"])
            varibles["rgbLedG"] = int(request.form["rgbLedG"])
            varibles["rgbLedB"] = int(request.form["rgbLedB"])
            setRGBLED(varibles["rgbLedR"], varibles["rgbLedG"], varibles["rgbLedB"])
        if "randomize" in request.form:
            varibles["rgbLedR"] = randint(0, 255)
            varibles["rgbLedG"] = randint(0, 255)
            varibles["rgbLedB"] = randint(0, 255)
            setRGBLED(varibles["rgbLedR"], varibles["rgbLedG"], varibles["rgbLedB"])
        return jsonify(varibles)
    
    if not connected:
        # lcd("User Connected", "to the RPi", "A user has connected to the Raspberry Pi", 3)
        connected = True
    return render_template('index.html', data=varibles, chr=chr)

@app.route('/button_game')
def button_game():
    return render_template('button_game.html')

@app.errorhandler(HTTPException)
def handle_http_error(e):
    return render_template('error.html', code=e.code, name=e.name, description=e.description), e.code

@app.route('/video_feed')
def video_feed():
    return Response(genVidFeed(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    gpio_thread = Thread(target=loop, daemon=True)
    gpio_thread.start()
    
    try:
        picam2.configure(picam2.create_video_configuration({"size": (800, 600)}))
        picam2.start()
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        destroy()
        picam2.stop()
        print("Exiting Program...")
