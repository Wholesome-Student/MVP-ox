import numpy as np
import cv2
import depthai
from PIL import Image
from pyzbar.pyzbar import decode, ZBarSymbol
import json
from json import JSONDecodeError
import mvp_qr
import sys

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

try:
    device = depthai.Device(pipeline)
except RuntimeError:
    print("カメラを認識していません")
    sys.exit()
device.__enter__()
q_rgb = device.getOutputQueue("rgb")

frame = None

while True:
    with open("camera_cmd.txt", "r") as f:
        cmd = f.read()
    try:
        in_rgb = q_rgb.tryGet()
        if in_rgb is not None:
            frame = in_rgb.getCvFrame()
        if frame is not None:

            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGBA)
            frame = Image.fromarray(frame)
            frame = frame.convert('RGBA')
            pil_temp = Image.new('RGBA', frame.size, (255, 255, 255, 0))
            result = cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGBA2BGRA)

            d = decode(result, symbols=[ZBarSymbol.QRCODE])
            try:
                for code in d:
                    userInfo = mvp_qr.qr_decode(code.data.decode("utf-8"))
                    users[userInfo['id']] = userInfo['ans']

                    x, y, w, h = code.rect

                    playerCount += 1

                    if userInfo['ans'] == ans:
                        particle = cv2.imread('image/oukan.png', -1)
                        matchCount += 1
                    else:
                        particle = cv2.imread('image/bom.png', -1)
                    if not matchAns:
                        particle = cv2.imread('image/particle.png', -1)
                    particle = cv2.cvtColor(particle, cv2.COLOR_BGRA2RGBA)
                    particle = Image.fromarray(particle)
                    particle = particle.convert('RGBA')
                    particle = particle.resize((w * 2, h * 2))

                    pil_temp.paste(particle, (int(x - w / 2), int(y - h / 2)), particle)
                    result = Image.alpha_composite(frame, pil_temp)
                    result = cv2.cvtColor(np.asarray(result), cv2.COLOR_RGBA2BGRA)
                    # cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 3)
            except IndexError:
                pass
            result = cv2.cvtColor(np.asarray(result), cv2.COLOR_RGBA2BGRA)
            frame = cv2.cvtColor(np.asarray(result), cv2.COLOR_RGBA2BGRA)

            if matchAns and playerCount != 0:
                cv2.putText(frame, 'rate: ' + str(100 * (matchCount / playerCount)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (255, 255, 0), 2)
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
    except:
        print("カメラが外されました")
        device.__exit__(None, None, None)
        sys.exit()

"""
except RuntimeError:
print("カメラが認識できません")
sys.exit()
except Exception as error:
print(type(error))
"""