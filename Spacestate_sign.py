from ctypes import alignment
import struct
import socket
import os
from PIL import Image, ImageFont, ImageDraw
import paho.mqtt.client 

mqtt = paho.mqtt.client.Client()

pixelBuffer = []
rgbMode = struct.pack("<?", 0)
versionBit = struct.pack("<B", 1)
pixelvlut = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

font = ImageFont.truetype("Comfortaa-Regular.ttf", 12)

def send_bufferfull(pixelBuffer):
    buffer = versionBit + rgbMode
    for buf in pixelBuffer:
        buffer += buf
    if len(buffer) >= 1400:
        pixelvlut.sendto(buffer, ("esp32-07B018.dhcp.nurd.space.", 5004))
        return True
    return False

def show_image(image):
    pixelBuffer = []
    for x in range(image.width):
        for y in range(image.height):
            r, g, b = image.getpixel((x, y ))
            pixelBuffer.append(bytes(struct.pack("<2H3B", x, y, r, g, b)))
            if send_bufferfull(pixelBuffer):
                    pixelBuffer = []

def open():
    image = Image.new("RGB", (64, 32))
    draw = ImageDraw.Draw(image)
    draw.text((10,0), "NURDs\nare in!", font=font, alignment="center",fill=(0, 255, 0,)) 
    show_image(image)

def closed():
    image = Image.new("RGB", (64, 32))
    draw = ImageDraw.Draw(image)
    draw.text((16,0), "", font=font, alignment="center",fill=(255, 0, 0,)) 
    show_image(image)

def setup_mqtt():
    mqtt.on_connect = on_connect
    mqtt.on_message = on_message
    mqtt.on_disconnect = on_disconnect
    mqtt.connect("mqtt.vm.nurd.space")

def on_disconnect(client, userdata, rc):
    setup_mqtt()

def on_connect(client, userdata, flags, rc):
    mqtt.subscribe("space/state")

def on_message(client, userdata, msg):
    
    if msg.topic == "space/state":
        state = True if msg.payload.decode("utf-8").lower() == "true" else False
        if state==True:
            open()
        else:
            closed()
        print(state)

setup_mqtt()

mqtt.loop_forever()
