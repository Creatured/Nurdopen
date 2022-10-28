#! /usr/bin/python3

from ctypes import alignment
import struct
import socket
import os
import time
from PIL import Image, ImageFont, ImageDraw
import paho.mqtt.client 

print(time.ctime(), 'START')

mqtt = paho.mqtt.client.Client()

width  = 64
height = 32

pixelBuffer = []
rgbMode = struct.pack("<?", 0)
versionBit = struct.pack("<B", 1)
pixelvlut = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

font = ImageFont.truetype("Comfortaa-Regular.ttf", 12)

def send_bufferfull(pixelBuffer):
    buffer = versionBit + rgbMode

    for buf in pixelBuffer:
        buffer += buf

    if len(buffer) >= 1400 and len(buffer) < 1510:
        pixelvlut.sendto(buffer, ('esp32-07B018.dhcp.nurd.space', 5004))
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
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    draw.text((10,0), "NURDs\nare in!", font=font, alignment="center",fill=(0, 255, 0,)) 
    show_image(image)

def closed():
    image = Image.new("RGB", (width, height))
    font = ImageFont.truetype("Comfortaa-Regular.ttf", 12)
    draw = ImageDraw.Draw(image)
    draw.text((16,0), "", font=font, alignment="center",fill=(255, 0, 0,)) 
    show_image(image)

def dicht():
    image = Image.new("RGB", (width, height))
    font = ImageFont.truetype("Comfortaa-Regular.ttf", 12)
    draw = ImageDraw.Draw(image)
    draw.text((16,0), "Er is\nniemand!", font=font, alignment="center",fill=(255, 0, 0,)) 
    show_image(image)

def moment():
    image = Image.new("RGB", (width, height))
    font = ImageFont.truetype("Comfortaa-Regular.ttf", 12)
    draw = ImageDraw.Draw(image)
    draw.text((16,0), "Momentje", font=font, alignment="center",fill=(255, 0, 255,)) 
    show_image(image)

def setup_mqtt(client):
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.connect("mqtt.vm.nurd.space")

def on_disconnect(client, userdata, rc):
    setup_mqtt(client)

def on_connect(client, userdata, flags, rc):
    client.subscribe("space/state")
    client.subscribe("deurbel")

def on_message(client, userdata, msg):
    if msg.topic == "space/state":
        state = True if msg.payload.decode("utf-8").lower() == "true" else False

        if state == True:
            open()

        else:
            closed()

        print(time.ctime(), state)

    elif msg.topic == 'deurbel':
        print(time.ctime(), 'Deurbel')

        if state == False:
            dicht()
        
        else:
            moment()

setup_mqtt(mqtt)

mqtt.loop_forever()
