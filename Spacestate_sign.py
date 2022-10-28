#! /usr/bin/python3

import paho.mqtt.client 
import struct
import socket
import time
import os

from PIL import Image, ImageFont, ImageDraw

class doorPixel():

    client = paho.mqtt.client.Client()

    debugShow = False

    width  = 64
    height = 32
    
    pixelBuffer = []
    rgbMode = struct.pack("<?", 0)
    
    versionBit = struct.pack("<B", 1)
    pixelvlut = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    font = ImageFont.truetype("Comfortaa-Regular.ttf", 12)
    state = False

    def __init__(self):
        self.setup_mqtt()
        self.client.loop_forever()

    def display_debug(self, image):
        import numpy
        import cv2
        image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
        cv2.imshow('nurd sign', image)
        cv2.waitKey(0)

    def send_bufferfull(self, pixelBuffer):
        buffer = self.versionBit + self.rgbMode

        for buf in pixelBuffer:
            buffer += buf

        if len(buffer) >= 1400 and len(buffer) < 1510:
            self.pixelvlut.sendto(buffer, ('esp32-07B018.dhcp.nurd.space', 5004))
            return True

        return False
    
    def show_image(self, image):
        pixelBuffer = []
        for x in range(image.width):
            for y in range(image.height):
                r, g, b = image.getpixel((x, y ))
                pixelBuffer.append(bytes(struct.pack("<2H3B", x, y, r, g, b)))
                if self.send_bufferfull(pixelBuffer):
                        pixelBuffer = []
        
        if self.debugShow:
            self.display_debug(image)


    def spaceopen(self):
        image = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.Draw(image)
        draw.text((10,0), "NURDs\nare in!", font=self.font, alignment="center",fill=(0, 255, 0,)) 
        self.show_image(image)

    def spaceclosed(self):
        image = Image.new("RGB", (self.width, self.height))
        font = ImageFont.truetype("Comfortaa-Regular.ttf", 12)
        draw = ImageDraw.Draw(image)
        draw.text((16,0), "", font=self.font, alignment="center",fill=(255, 0, 0,)) 
        self.show_image(image)

    def doorbell_spaceclosed(self):
        image = Image.new("RGB", (self.width, self.height))
        font = ImageFont.truetype("Comfortaa-Regular.ttf", 12)
        draw = ImageDraw.Draw(image)
        draw.text((16,0), "Er is\nniemand!",font=self.font, alignment="center",fill=(255, 255, 0,)) 
        self.show_image(image)

    def doorbell_wait(self):
        image = Image.new("RGB", (self.width, self.height))
        font = ImageFont.truetype("Comfortaa-Regular.ttf", 10)
        draw = ImageDraw.Draw(image)
        draw.text((1,0), "Een\nmoment", font=self.font, alignment="center",fill=(255, 0, 255,)) 
        self.show_image(image)

    def setup_mqtt(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.connect("mqtt.vm.nurd.space")

    def on_disconnect(self, client, userdata, rc):
        self.setup_mqtt(client)

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("space/state")
        self.client.subscribe("deurbel")

    def on_message(self, client, userdata, msg):

        print(time.ctime(), f'mqtt for {msg.topic}')

        if msg.topic == "space/state":
            self.spacestate = True if msg.payload.decode("utf-8").lower() == "true" else False

            if self.spacestate == True:
                self.spaceopen()
            else:
                self.spaceclosed()

            print(time.ctime(), self.spacestate)

        elif msg.topic == 'deurbel':
            print(time.ctime(), 'Deurbel')

            if self.spacestate == False:
                self.doorbell_spaceclosed()
            
            else:
                self.doorbell_wait()
                time.sleep(10)
    
doorPixel()