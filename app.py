from signalrcore.hub_connection_builder import HubConnectionBuilder
from gpiozero import LED
import RPi.GPIO as GPIO

side = None

def input_with_default(input_text, default_value):
    value = input(input_text.format(default_value))
    return default_value if value is None or value.strip() == "" else value
    
def setLed(s):
    if s == 0:
        redLed.on()
        blueLed.off()
    elif s == 1:
        redLed.off()
        blueLed.on()
    else:
        redLed.off()
        blueLed.off()
    
def red_callback(channel):
    global side
    if side is None:
        print("Red button was pushed!")
        hub_connection.send("SetSide", [0])
        setLed(side)
        side = 0
    
def blue_callback(channel):
    global side
    if side is None:
        print("Blue button was pushed!")
        hub_connection.send("SetSide", [1])
        setLed(side)
        side = 1
        
def onSideChange(s):
    global side
    print(s[0])
    setLed(s[0])
    side = s[0]
    
redLed = LED(18)
blueLed = LED(17)

server_url = input_with_default('Enter your server url(default: {0}): ', "ws://192.168.1.20:8031/familiadaHub")
hub_connection = HubConnectionBuilder()\
    .with_url(server_url, options={"verify_ssl": False}) \
    .with_automatic_reconnect({
            "type": "interval",
            "keep_alive_interval": 10,
            "intervals": [1, 3, 5, 6, 7, 87, 3]
        }).build()

hub_connection.on_open(lambda: print("connection opened and handshake received ready to send messages"))
hub_connection.on_close(lambda: print("connection closed"))

hub_connection.on("OnSetSide", onSideChange)

hub_connection.start()


GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(14,GPIO.RISING,callback=red_callback)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(15,GPIO.RISING,callback=blue_callback)

message = input("Press enter to quit\n\n")

hub_connection.stop()