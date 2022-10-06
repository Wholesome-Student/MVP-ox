from PIL import Image
from pyzbar.pyzbar import decode, ZBarSymbol

img = Image.open('barcode_qrcode.jpg')

decoded_list = decode(img)

print(type(decoded_list))
# <class 'list'>

print(len(decoded_list))
# 3

print(type(decoded_list[0]))
# <class 'pyzbar.pyzbar.Decoded'>

print(decoded_list[0])
# Decoded(data=b'QR Code Example', type='QRCODE', rect=Rect(left=8, top=6, width=159, height=160), polygon=[Point(x=8, y=66), Point(x=66, y=166), Point(x=167, y=109), Point(x=108, y=6)], quality=1, orientation='UP')

print(decoded_list[1])
# Decoded(data=b'1923055034006', type='EAN13', rect=Rect(left=161, top=217, width=175, height=32), polygon=[Point(x=161, y=229), Point(x=239, y=249), Point(x=330, y=248), Point(x=332, y=242), Point(x=335, y=226), Point(x=336, y=220), Point(x=336, y=218), Point(x=248, y=217), Point(x=165, y=217), Point(x=164, y=219), Point(x=162, y=225)], quality=37, orientation='UP')

print(decoded_list[2])