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
effects = {}
matchAns = False
playerCount = 0
matchCount = 0

effect_time=5
RING=0
OUKAN=1
BOM=2
HEART=3

with open("camera_cmd.txt", "w") as f:
    pass
with open("error.log", "w") as f:
    pass

ring_img=Image.open('image/particle.png')
oukan_img=Image.open('image/oukan.png')
bom_img=Image.open('image/bom.png')
heart_img=Image.open('image/heart.png')

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
    with open("error.log", "w", encoding="utf-8") as f:
        f.write("カメラを認識していません")
    print("カメラを認識していません")
    sys.exit()
device.__enter__()
q_rgb = device.getOutputQueue("rgb")

frame = None

while True:
    with open("camera_cmd.txt", "r") as f:
        cmd = f.read()
    with open("camera_cmd.txt", "w") as f:
        pass
    try:
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

                    if not matchAns:
                        effects[userInfo['id']]=[RING, effect_time, *code.rect]
                    else:
                        if userInfo['ans'] == ans:
                            effects[userInfo['id']]=[OUKAN, effect_time, *code.rect]
                        else:
                            effects[userInfo['id']]=[BOM, effect_time, *code.rect]
                else:
                    effects[userInfo['id']]=[HEART, effect_time, *code.rect]
            for id in effects:
                ef=effects[id]
                if ef[1]!=0:
                    print(ef)
                    playerCount += 1
                    ef[1]-=1
                    if ef[0]==RING:
                        particle = ring_img
                    elif ef[0]==OUKAN:
                        particle = oukan_img
                        matchCount += 1
                    elif ef[0]==BOM:
                        particle = bom_img
                    elif ef[0]==HEART:
                        particle = heart_img
                    particle = particle.resize((ef[4] * 2, ef[5] * 2))
                    pil_frame.paste(particle, (int(ef[2] - ef[4] / 2), int(ef[3] - ef[5] / 2)), particle)
            
            frame = np.asarray(pil_frame)[:,:,::-1]

            matchCount = 0
            playerCount = 0
            cv2.imshow("MaruVatuPossible", frame)
        
            with open("userInfo.json", "w") as writeJsonFile:
                json.dump(users, writeJsonFile, ensure_ascii=False, indent=2)

        key = cv2.waitKey(1)
        if key!=-1:
            cmd = chr(key)
        if cmd == "q":
            break
        elif cmd == "t":
            matchAns = False
            users = {}
            effects = {}
        elif cmd == "m":
            ans = True
            matchAns = True
        elif cmd == "v":
            ans = False
            matchAns = True
    except RuntimeError as e:
        with open("error.log", "w", encoding="utf-8") as f:
            f.write("カメラが外されました")
        print(e)
        print("カメラが外されました")
        device.__exit__(None, None, None)
        sys.exit()
    except KeyboardInterrupt:
        with open("error.log", "w", encoding="utf-8") as f:
            f.write("-1")
        print("強制終了します")
        device.__exit__(None, None, None)
        sys.exit()
    except Exception as e:
        print(e)
        device.__exit__(None, None, None)
        sys.exit()

"""
except RuntimeError:
print("カメラが認識できません")
sys.exit()
except Exception as error:
print(type(error))
"""