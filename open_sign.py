import struct
import socket
import os
from PIL import Image

pixelBuffer = []
rgbMode = struct.pack("<?", 0)
versionBit = struct.pack("<B", 1)
pixelvlut = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_bufferfull(pixelBuffer):
    buffer = versionBit + rgbMode
    for buf in pixelBuffer:
        buffer += buf
    if len(buffer) >= 1400:
        pixelvlut.sendto(buffer,  ("10.208.42.134", 5004))
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

# for file in sorted(os.listdir("D:\\dev\\apple"), key=lambda x: int(x.split("_")[-1].split(".")[0])):
#     if file.endswith(".png"):
#         image = Image.open(os.path.join("D:\\dev\\apple", file))
#         image = image.resize((64,32))
#         show_image(image)