import numpy as np
import cv2
import depthai
from PIL import Image
from pyzbar.pyzbar import decode, ZBarSymbol
import json
import mvp_qr

ans = False
users = {}
matchAns = False
playerCount = 0
matchCount = 0

pipeline = depthai.Pipeline()

cam_rgb = pipeline.create(depthai.node.ColorCamera)
cam_rgb.setPreviewSize(1000, 600)
cam_rgb.setInterleaved(False)

xout_rgb = pipeline.create(depthai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

cam_rgb.setFps(15)

with depthai.Device(pipeline) as device:
    q_rgb = device.getOutputQueue("rgb")

    frame = None

    while True:
        with open("camera_cmd.txt", "r") as f:
            cmd = f.read()
        in_rgb = q_rgb.tryGet()
        if in_rgb is not None:
            frame = in_rgb.getCvFrame()
        if frame is not None:

            pil_frame = Image.fromarray(frame[:,:,::-1])

            d = decode(cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY), symbols=[ZBarSymbol.QRCODE])
            for code in d:
                userInfo = mvp_qr.qr_decode(code.data.decode("utf-8"))
                if userInfo['ans']!=None:
                    users[userInfo['id']] = userInfo['ans']

                    x, y, w, h = code.rect

                    playerCount += 1

                    if not matchAns:
                        particle = Image.open('image/particle.png')
                    else:
                        if userInfo['ans'] == ans:
                            particle = Image.open('image/oukan.png')
                            matchCount += 1
                        else:
                            particle = Image.open('image/bom.png')
                    particle = particle.resize((w * 2, h * 2))

                    pil_frame.paste(particle, (int(x - w / 2), int(y - h / 2)), particle)
            frame = np.asarray(pil_frame)[:,:,::-1]
            
            matchCount = 0
            playerCount = 0
            cv2.imshow("MaruVatuPossible", frame)
        
            with open("userInfo.json", "w") as writeJsonFile:
                json.dump(users, writeJsonFile, ensure_ascii=False, indent=2)

        key = cv2.waitKey(1)
        if cmd == "q":
            break
        elif cmd == "t":
            matchAns = False
            users = {}
        elif cmd == "m":
            ans = True
            matchAns = True
        elif cmd == "v":
            ans = False
            matchAns = True